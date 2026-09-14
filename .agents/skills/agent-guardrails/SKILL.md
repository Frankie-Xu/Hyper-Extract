---
name: agent-guardrails
description: Give every autonomous agent three guardrails — a per-team allowlist (what it can do), bounded loops (can't run forever), and full transcripts (auditable). Use when building an autonomous agent, a recurring agent loop, or any agent that runs without per-step human approval.
---

# Agent Guardrails

An autonomous agent without guardrails can run forever, do things it shouldn't, and leave no trail. Three guardrails make autonomy safe: allowlist, bounded loops, full transcripts.

## The three guardrails

### 1. Per-team allowlist (what it can do)

Each agent/team has an explicit allowlist of permitted actions. Anything not on the list is denied. The allowlist is the positive scope; pair it with an explicit "never touches" list (see `lane-discipline`):

- Data team: inventory datasets, run the dataset-builder tick, add new sources (additive-only).
- R&D team: snapshot the queue, review telemetry, rank next experiments. **Never touches training code.**
- Operations team: blockers report, platform health, Operator digest.

The allowlist is enforced in code (a tool/permission boundary), not just documented. An agent that "shouldn't touch training code" must be unable to, not merely asked not to.

### 2. Bounded loops (can't run forever)

A recurring agent (`--loop 1440`) must have a bound so a bug or a stuck condition can't make it run forever:

- A max-iterations cap per run.
- A per-iteration timeout (see `diagnose-before-retry`'s `timeout` idiom).
- A max wall-clock per loop.
- A stop condition (a queue empty, a budget exhausted, a kill signal).

Bounded loops also make a runaway cost visible — a loop that's been running 4× its expected iterations is a signal, not a silent drain.

### 3. Full transcripts (auditable)

Every run produces a full transcript in a fixed location, appended per run (a living run log):

- `knowledge/teams/<team>.md` — append-per-run, OKF-shaped.
- The transcript records: what the deterministic core did, what the LLM suggested, what was surfaced.
- A fixed dir makes collection trivial; append-per-run keeps history and makes trends visible.

Without transcripts, a misbehaving agent is invisible — you can't diagnose what it did wrong. With transcripts, every run is auditable after the fact.

## Why all three

- Allowlist without bounded loops → the agent does allowed things forever.
- Bounded loops without allowlist → the agent stops on time but did something forbidden.
- Transcripts without the other two → you can audit the damage after it's done.
- All three → the agent does permitted things for a bounded time and leaves a trail.

## Anti-patterns

- **"It's an internal agent, it can do anything."** Internal agents still drift; allowlists catch it.
- **Unbounded loop.** "Run forever" sounds fine until a bug makes it cost 1000× the budget.
- **No transcript.** "We'll add logging later." You won't; and the first incident is un-auditable.
- **Allowlist documented but not enforced.** The agent "shouldn't" touch X but can. Should → must.
- **Transcripts in a per-run file with no fixed dir.** Collection is a hunt; trends are invisible.

## Pair with

- `deterministic-core-llm-judgment` — the deterministic core is what makes bounded loops safe (it does its work and stops; it doesn't freewheel on LLM token budget).
- `lane-discipline` — the "never touches" list is the negative scope that pairs with the allowlist.
- `sme-fanout` — the per-team OKF run log is the output contract applied to recurring runs.
- `respect-the-guard` — agent guardrails are guards you enforce, not bypass.
