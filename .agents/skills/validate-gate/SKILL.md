---
name: validate-gate
description: Run the cheapest non-trivial correctness gate for the change type — install (offline-preferring) + typecheck for frontend, smoke-import + targeted tests for Python — before declaring a task done. Use after any code edit, before marking a task complete, and before moving to the next board item.
---

# Validate Gate

"Done" means the cheapest meaningful correctness gate passed — not "I finished typing". The gate is cheap, so skipping it has no upside.

## Per-stack gate

### TypeScript / Next.js / frontend

```bash
CI=true pnpm --filter <pkg> build 2>&1 | tail -n 10
```

- `CI=true` — force CI-equivalent behavior (fail on warnings, no interactive, stricter). Running it locally gives you CI-equivalent signal before pushing.
- `--filter <pkg>` — build only the affected package(s), not the whole monorepo (see `affected-tests`).
- Tail the output — a passing build should be a few lines, not a wall.

If the area has a lint config the project cares about, add `pnpm --filter <pkg> lint` after typecheck.

### Python

```bash
uv run --no-sync python -c "import sys; sys.path.insert(0, 'packages/<pkg>'); import <pkg>; print('imports ok)"
uv run --no-sync python -m pytest packages/<pkg>/tests -q 2>&1 | tail -n 6
```

See `smoke-import` and `affected-tests` for the rationale.

### Cross-stack

A change that touches both: run both gates. They're independent commands — batch them in parallel.

## When to run which

- Edited TS → install + typecheck (the affected package).
- Edited Python → smoke-import + affected tests.
- Edited a shared client consumed by both → run both gates.
- Edited only docs/config with no code surface → no gate needed; say so.
- Edited test fixtures or conftest → run the wider test set, not just the affected package.

## Tail discipline

Always tail the gate output. A passing gate that floods context with 200 lines of green is a tax on every subsequent turn. `tail -n 6` / `Select-Object -Last 6` for tests, `tail -n 10` for typecheck.

## "Done" rule

A task moves to `done` only when:
1. The artifact exists.
2. The validate gate for its stack passed (or you explicitly state why the gate was skipped and why that's acceptable).

"I finished writing the file" is not done. "Typecheck passed" is done.

## Reporting test results — exact counts, not "tests pass"

```
40 passed, 7 skipped, zero failures (7 skips are RLS-auth tests — conftest marker when test key absent).
```

- Exact passed / skipped / failed counts; name skip reasons.
- Green with unstated skips is dishonest; green with named skips is auditable.

## Thin corpus — gate honesty

- **State corpus size + source** with every gate result ("200 pairs from real arXiv corpus").
- **Thin data → unproven**, not proof — downgrade the claim when pairs are below threshold.
- **Prefer fail-closed gates** (`sufficientEvalPairs`) over post-hoc disclaimers.
- **Structural fix beats caution** — the gate should reject insufficient corpora, not silently pass.

## Anti-patterns

- Skipping the gate because "it's a small change" — small changes break typecheck too.
- Running the full monorepo typecheck/test on every edit — slow, noisy, trains you to skip the gate.
- Not tailing — the gate's output tax makes you reluctant to run it next time.
- Marking done on green dots without reading the actual assertion line — a tail of "1 failed" hidden in a green-looking summary.
