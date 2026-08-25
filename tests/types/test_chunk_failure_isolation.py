"""Per-chunk extractor failures must not abort graph-family parse/feed_text.

Graph/Hypergraph override BaseAutoType._extract_data(); this matrix covers the
isolation that the base class already had and the graph family was missing.
#69 only filters None merge inputs — these tests cover exceptions at invoke/batch.
"""

import logging
from typing import Any

import pytest
from ontomem.merger import MergeStrategy
from pydantic import BaseModel, Field

from hyperextract.types import AutoGraph, AutoHypergraph, AutoTemporalGraph
from tests.mocks import MockChatModel, MockEmbeddings

SECRET_TEXT = "SECRET_USER_TEXT_9f3c1a_DO_NOT_LOG"
OK_CHUNK = "Apple was founded by Steve Jobs in Cupertino."
FAIL_CHUNK = f"Rate-limited chunk containing {SECRET_TEXT}."
FAIL_ERROR = TimeoutError("rate limited")


class Entity(BaseModel):
    name: str
    type: str
    properties: dict = Field(default_factory=dict)


class Relation(BaseModel):
    source: str
    target: str
    relation_type: str


class HyperRelation(BaseModel):
    participants: list[str]
    relation_type: str


class TemporalRelation(BaseModel):
    source: str
    target: str
    relation_type: str
    year: str = ""


APPLE = Entity(name="Apple", type="ORGANIZATION", properties={})
STEVE = Entity(name="Steve Jobs", type="PERSON", properties={})
FOUNDED = Relation(source="Apple", target="Steve Jobs", relation_type="founded_by")
FOUNDED_HYPER = HyperRelation(
    participants=["Apple", "Steve Jobs"], relation_type="founded_by"
)
FOUNDED_TEMPORAL = TemporalRelation(
    source="Apple",
    target="Steve Jobs",
    relation_type="founded_by",
    year="1976",
)


class RecordingExtractor:
    """Mock runnable: each call returns the next preset value or raises it."""

    def __init__(self, results: list):
        self.results = list(results)
        self.payloads: list[Any] = []
        self._offset = 0

    def _next(self, payload):
        self.payloads.append(payload)
        if self._offset >= len(self.results):
            raise AssertionError("unexpected extra extractor call")
        item = self.results[self._offset]
        self._offset += 1
        if isinstance(item, Exception):
            raise item
        return item

    def invoke(self, payload, config=None):
        return self._next(payload)

    def batch(self, inputs, config=None, return_exceptions=False, **kwargs):
        out = []
        for inp in inputs:
            try:
                out.append(self._next(inp))
            except Exception as exc:
                if return_exceptions:
                    out.append(exc)
                else:
                    raise
        return out


def _force_batch_chunks(graph, chunks: list[str]) -> str:
    """Route extraction through the multi-chunk batch path with fixed splits."""
    graph.text_splitter.split_text = lambda _text: list(chunks)
    return "x" * (graph.chunk_size + 1)


class _LogCapture(logging.Handler):
    def __init__(self):
        super().__init__()
        self.messages: list[str] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.messages.append(record.getMessage())


@pytest.fixture
def isolation_logs():
    handler = _LogCapture()
    handler.setLevel(logging.WARNING)
    names = (
        "hyperextract.types.base",
        "hyperextract.types.graph",
        "hyperextract.types.hypergraph",
        "hyperextract.types.temporal_graph",
    )
    loggers = [logging.getLogger(name) for name in names]
    previous = [(logger, logger.level) for logger in loggers]
    for logger in loggers:
        logger.addHandler(handler)
        logger.setLevel(logging.WARNING)
    try:
        yield handler
    finally:
        for logger, level in previous:
            logger.removeHandler(handler)
            logger.setLevel(level)


def _assert_isolated_logs(
    handler: _LogCapture, *, chunk_index: int, secret: str = SECRET_TEXT
):
    text = "\n".join(handler.messages)
    assert f"chunk_index={chunk_index}" in text
    assert "error_type=TimeoutError" in text
    assert secret not in text


def _make_graph(*, extraction_mode: str) -> AutoGraph:
    return AutoGraph(
        node_schema=Entity,
        edge_schema=Relation,
        node_key_extractor=lambda x: x.name,
        edge_key_extractor=lambda x: f"{x.source}-{x.relation_type}-{x.target}",
        nodes_in_edge_extractor=lambda x: (x.source, x.target),
        llm_client=MockChatModel(),
        embedder=MockEmbeddings(),
        extraction_mode=extraction_mode,
        node_strategy_or_merger=MergeStrategy.KEEP_EXISTING,
        edge_strategy_or_merger=MergeStrategy.KEEP_EXISTING,
    )


def _make_hypergraph(*, extraction_mode: str) -> AutoHypergraph:
    return AutoHypergraph(
        node_schema=Entity,
        edge_schema=HyperRelation,
        node_key_extractor=lambda x: x.name,
        edge_key_extractor=lambda x: f"{x.relation_type}_{sorted(x.participants)}",
        nodes_in_edge_extractor=lambda x: tuple(x.participants),
        llm_client=MockChatModel(),
        embedder=MockEmbeddings(),
        extraction_mode=extraction_mode,
        node_strategy_or_merger=MergeStrategy.KEEP_EXISTING,
        edge_strategy_or_merger=MergeStrategy.KEEP_EXISTING,
    )


def _make_temporal(*, extraction_mode: str) -> AutoTemporalGraph:
    return AutoTemporalGraph(
        node_schema=Entity,
        edge_schema=TemporalRelation,
        node_key_extractor=lambda x: x.name,
        edge_key_extractor=lambda x: f"{x.source}|{x.relation_type}|{x.target}",
        time_in_edge_extractor=lambda x: x.year or "",
        nodes_in_edge_extractor=lambda x: (x.source, x.target),
        llm_client=MockChatModel(),
        embedder=MockEmbeddings(),
        observation_time="2024-01-15",
        extraction_mode=extraction_mode,
        node_strategy_or_merger=MergeStrategy.KEEP_EXISTING,
        edge_strategy_or_merger=MergeStrategy.KEEP_EXISTING,
    )


def test_autograph_one_stage_invoke_failure_returns_empty(isolation_logs):
    graph = _make_graph(extraction_mode="one_stage")
    graph.data_extractor = RecordingExtractor([FAIL_ERROR])

    result = graph.parse(SECRET_TEXT)

    assert result.empty()
    assert result.nodes == []
    assert result.edges == []
    _assert_isolated_logs(isolation_logs, chunk_index=0)


def test_autograph_one_stage_batch_keeps_successful_chunk(isolation_logs):
    graph = _make_graph(extraction_mode="one_stage")
    success = graph.graph_schema(nodes=[APPLE, STEVE], edges=[FOUNDED])
    graph.data_extractor = RecordingExtractor([success, FAIL_ERROR])
    text = _force_batch_chunks(graph, [OK_CHUNK, FAIL_CHUNK])

    result = graph.parse(text)

    assert {n.name for n in result.nodes} == {"Apple", "Steve Jobs"}
    assert len(result.edges) == 1
    _assert_isolated_logs(isolation_logs, chunk_index=1)


def test_autograph_one_stage_batch_all_fail_returns_empty(isolation_logs):
    graph = _make_graph(extraction_mode="one_stage")
    graph.data_extractor = RecordingExtractor([FAIL_ERROR, FAIL_ERROR])
    text = _force_batch_chunks(graph, [FAIL_CHUNK, FAIL_CHUNK])

    result = graph.parse(text)

    joined = "\n".join(isolation_logs.messages)
    assert result.empty()
    assert "chunk_index=0" in joined
    assert "chunk_index=1" in joined
    assert SECRET_TEXT not in joined


def test_autograph_two_stage_skips_edges_when_nodes_fail(isolation_logs):
    graph = _make_graph(extraction_mode="two_stage")
    nodes_ok = graph.node_list_schema(items=[APPLE, STEVE])
    edges_ok = graph.edge_list_schema(items=[FOUNDED])
    node_extractor = RecordingExtractor([nodes_ok, FAIL_ERROR])
    edge_extractor = RecordingExtractor([edges_ok])
    graph.node_extractor = node_extractor
    graph.edge_extractor = edge_extractor
    text = _force_batch_chunks(graph, [OK_CHUNK, FAIL_CHUNK])

    result = graph.parse(text)

    assert {n.name for n in result.nodes} == {"Apple", "Steve Jobs"}
    assert len(result.edges) == 1
    assert len(edge_extractor.payloads) == 1
    assert FAIL_CHUNK not in edge_extractor.payloads[0]["source_text"]
    assert "reason=node_extract_failed" in "\n".join(isolation_logs.messages)
    _assert_isolated_logs(isolation_logs, chunk_index=1)


def test_autograph_two_stage_keeps_nodes_when_edges_fail(isolation_logs):
    graph = _make_graph(extraction_mode="two_stage")
    nodes_ok = graph.node_list_schema(items=[APPLE, STEVE])
    nodes_other = graph.node_list_schema(
        items=[Entity(name="Cupertino", type="LOCATION", properties={})]
    )
    edges_ok = graph.edge_list_schema(items=[FOUNDED])
    graph.node_extractor = RecordingExtractor([nodes_ok, nodes_other])
    graph.edge_extractor = RecordingExtractor([edges_ok, FAIL_ERROR])
    text = _force_batch_chunks(graph, [OK_CHUNK, FAIL_CHUNK])

    result = graph.parse(text)

    assert {n.name for n in result.nodes} == {"Apple", "Steve Jobs", "Cupertino"}
    assert len(result.edges) == 1
    _assert_isolated_logs(isolation_logs, chunk_index=1)


def test_autograph_two_stage_single_chunk_failure_returns_empty(isolation_logs):
    graph = _make_graph(extraction_mode="two_stage")
    graph.node_extractor = RecordingExtractor([FAIL_ERROR])
    graph.edge_extractor = RecordingExtractor([])

    result = graph.parse(SECRET_TEXT)

    assert result.empty()
    assert graph.edge_extractor.payloads == []
    _assert_isolated_logs(isolation_logs, chunk_index=0)


def test_autohypergraph_one_stage_batch_keeps_successful_chunk(isolation_logs):
    graph = _make_hypergraph(extraction_mode="one_stage")
    success = graph.graph_schema(nodes=[APPLE, STEVE], edges=[FOUNDED_HYPER])
    graph.data_extractor = RecordingExtractor([success, FAIL_ERROR])
    text = _force_batch_chunks(graph, [OK_CHUNK, FAIL_CHUNK])

    result = graph.parse(text)

    assert {n.name for n in result.nodes} == {"Apple", "Steve Jobs"}
    assert len(result.edges) == 1
    _assert_isolated_logs(isolation_logs, chunk_index=1)


def test_autohypergraph_one_stage_invoke_failure_returns_empty(isolation_logs):
    graph = _make_hypergraph(extraction_mode="one_stage")
    graph.data_extractor = RecordingExtractor([FAIL_ERROR])

    result = graph.parse(SECRET_TEXT)

    assert result.empty()
    _assert_isolated_logs(isolation_logs, chunk_index=0)


def test_autohypergraph_two_stage_skips_edges_when_nodes_fail(isolation_logs):
    graph = _make_hypergraph(extraction_mode="two_stage")
    nodes_ok = graph.node_list_schema(items=[APPLE, STEVE])
    edges_ok = graph.edge_list_schema(items=[FOUNDED_HYPER])
    edge_extractor = RecordingExtractor([edges_ok])
    graph.node_extractor = RecordingExtractor([nodes_ok, FAIL_ERROR])
    graph.edge_extractor = edge_extractor
    text = _force_batch_chunks(graph, [OK_CHUNK, FAIL_CHUNK])

    result = graph.parse(text)

    assert {n.name for n in result.nodes} == {"Apple", "Steve Jobs"}
    assert len(result.edges) == 1
    assert len(edge_extractor.payloads) == 1
    _assert_isolated_logs(isolation_logs, chunk_index=1)


def test_temporal_one_stage_batch_keeps_chunk_and_observation_time(isolation_logs):
    graph = _make_temporal(extraction_mode="one_stage")
    success = graph.graph_schema(nodes=[APPLE, STEVE], edges=[FOUNDED_TEMPORAL])
    extractor = RecordingExtractor([success, FAIL_ERROR])
    graph.data_extractor = extractor
    text = _force_batch_chunks(graph, [OK_CHUNK, FAIL_CHUNK])

    result = graph.parse(text)

    assert {n.name for n in result.nodes} == {"Apple", "Steve Jobs"}
    assert len(result.edges) == 1
    assert extractor.payloads[0]["observation_time"] == "2024-01-15"
    assert extractor.payloads[1]["observation_time"] == "2024-01-15"
    _assert_isolated_logs(isolation_logs, chunk_index=1)


def test_temporal_two_stage_edge_payload_includes_observation_time(isolation_logs):
    graph = _make_temporal(extraction_mode="two_stage")
    nodes_ok = graph.node_list_schema(items=[APPLE, STEVE])
    edges_ok = graph.edge_list_schema(items=[FOUNDED_TEMPORAL])
    edge_extractor = RecordingExtractor([edges_ok])
    graph.node_extractor = RecordingExtractor([nodes_ok, FAIL_ERROR])
    graph.edge_extractor = edge_extractor
    text = _force_batch_chunks(graph, [OK_CHUNK, FAIL_CHUNK])

    result = graph.parse(text)

    assert {n.name for n in result.nodes} == {"Apple", "Steve Jobs"}
    assert len(result.edges) == 1
    assert len(edge_extractor.payloads) == 1
    assert edge_extractor.payloads[0]["observation_time"] == "2024-01-15"
    assert "Apple" in edge_extractor.payloads[0]["known_nodes"]
    _assert_isolated_logs(isolation_logs, chunk_index=1)
