---
name: logical-commit-split
description: Split a large migration or multi-concern change into logical commits grouped by concern, on a branch whose name encodes the commit story, rather than one giant commit. Use when a change spans multiple distinct concerns (infra + data + UI, baseline + feature + commerce), when the change would be unreviewable as one commit, or when one slice might need to be reverted independently.
---

# Logical Commit Split

One giant migration commit is unreviewable and un-revertable. Splitting by logical concern makes review tractable and lets you revert one slice without rolling back the others.

## When to split

- The change spans multiple distinct concerns (infra + data + UI; baseline + observability + commerce).
- The single-commit diff is too large to review in one pass.
- One slice might need to be reverted independently (a feature flag off, a provider swap rolled back).
- The work items map to a tracker (TECH_DEBT, work_queue) with separable IDs.

Don't split when:
- The change is one concern — splitting fragments a single logical change.
- The slices are tightly coupled — splitting creates broken intermediate states.
- It's a trivial change.

## The split

Group by **concern**, not by file type or by time. A good split reads as a story:

```
1. baseline migration      (the uncommitted fleet migration: api, scripts, specs)
2. observability/data stack (observability, data-ingest, dataset watcher)
3. commercial platform      (commerce, provider-agnostic layer, Medusa default)
```

Each commit:
- Compiles / passes its gate on its own where possible (don't ship a broken intermediate).
- Has a message that names the concern and ties to a tracker item (see `follow-procedure`).
- Is small enough to review in one pass.

## The branch name encodes the story

The branch name is the review's table of contents — a reviewer reads it and knows the scope before opening a file:

```
platform/fleet-baseline-observability-commerce
```

Convention: `<type>/<scope>-<concern>-<concern>-<concern>`. Hyphen-separate the concerns in the order they're committed. Keep it to ≤3 concerns; more means the split is too granular or the branch is doing too much.

## The commit message

Each commit's message follows a structured conventional-commit shape:

```
feat(prod): combined api+worker mode, baked corpora, persistent /data volume
- entrypoint 'all' mode: worker (background) + uvicorn in one container
- baked corpora (build-time, no runtime fetch)
- railway volume add --mount-path /data --service api
```

- **Prefix** — `feat(<scope>):` / `fix(<scope>):` / `chore(<scope>):` — the type and scope of the change.
- **Summary line** — the one-line what.
- **Bullet points** — the concrete changes, each a distinct sub-fact. A reviewer reads the bullets and knows the change shape before opening the diff.

The message is the change's documentation in history — write it for the reviewer who reads the log, not for yourself. Tie it to a tracker item where applicable (see `follow-procedure`).

## Order matters

Commit in dependency order: the thing other slices depend on goes first. Baseline → observability → commerce. A reviewer can read the commits top-to-bottom and the story makes sense.

## Anti-patterns

- **One mega-commit "to keep history clean".** Unreviewable, un-revertable; the opposite of clean.
- **Split by file type** ("all the .py", then "all the .tsx"). Fragments a single logical change across commits.
- **Split by time** ("what I did Monday", "what I did Tuesday"). Reviewers don't care about your calendar.
- **Broken intermediate commits.** Each commit should pass its gate where possible; a bisect-unfriendly history is a tax later.
- **Branch name that doesn't match the commits.** The name is the TOC; if it lies, the reviewer loses trust.

## Pair with

- `pre-commit-hygiene` — run the junk-exclusion + secrets scan before *each* commit, not just the first.
- `respect-the-guard` — the split lands on a branch, not main; the guard is why.
- `follow-procedure` — each commit message ties to a tracker item.
