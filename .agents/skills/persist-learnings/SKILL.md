---
name: persist-learnings
description: During wait windows (long installs, builds, tests, deploys), save durable session learnings to memory files so the next session inherits them. Treat memory as a first-class session artifact, not optional notes. Use whenever a wait window opens and you have fresh, reusable learnings in context — a gotcha, a working command, a corrected assumption, a decision rationale.
---

# Persist Learnings

A session that only edits code leaves the next session to re-derive the same lessons. A session that writes memory files compounds. Learnings saved at the *end* of a session are often lost to context pressure; learnings saved *mid-wait* survive.

## When to persist

The trigger is a **wait window** — an install, build, test, deploy, or any long op that has blocked your foreground lane. You have loaded context and idle wall-clock; that's the moment.

Persist when:
- A long op is in flight and you have fresh learnings in context.
- You just corrected an assumption you'd otherwise re-make next session.
- You discovered a working command / flag combo worth recording (e.g. `pnpm install --prefer-offline --reporter=append-only`).
- You made a decision with a non-obvious rationale.
- You hit a gotcha that cost time.

Don't persist when:
- The wait is short (< ~30s) — not enough to write meaningfully.
- The learning is one-off / not reusable.
- You're under a time pressure that the wait isn't the cause of.

## Where to persist

Follow the repo's memory convention. Common locations:
- `memory/` — project memory files (people, projects, glossary, gotchas).
- `docs/wiki/` — durable wiki entries.
- `docs/adr/` — architecture decision records (for decisions, not gotchas).
- `CLAUDE.md` / `AGENTS.md` — agent-facing conventions.
- A personal `~/.cursor/notes/` if the learning is yours, not the project's.

Pick the location the next session will actually read. A learning in a file no one opens is wasted.

## How to write a memory entry

- **One fact per entry.** A memory file with 30 mixed facts is grep-able but not readable.
- **Lead with the reusable rule**, then the evidence. Not the reverse.
- **Date it** if it's time-sensitive (a workaround that will be obsolete when X upgrades).
- **Link the source** — the command, the file, the spec that backs the rule.

Bad: "Today I had trouble with pnpm. It was silent. I killed it and restarted with a reporter and it worked. The PID was 3380."
Good: "When `pnpm install` goes silent for 90s+, kill by PID and restart with `--reporter=append-only 2>&1 | tail -n 15`. Track PIDs at launch so the kill is targeted."

## Anti-patterns

- **Persist at session end only.** Context pressure makes the end the worst time.
- **Write prose, not rules.** A memory entry that's a story doesn't get reused.
- **Write to a file no one reads.** Match the repo's memory convention.
- **Persist every triviality.** A memory dir full of noise gets ignored; signal gets lost.

## The handoff note — the paste-into-fresh-session form

The highest-leverage persistent artifact is a handoff note designed to be paste-able into a fresh session. `HANDOFF.md` opens with a dated session-continuation block:

- **Dated** — when this state was captured.
- **Live state** — what's deployed, what's running, what's the current head.
- **The exact gate-command sequence** — the 4 commands a fresh session runs to verify state (e.g. build, test, migrate-check, smoke).
- **Ordered follow-ups** — the next actions in priority order.

This is the session-to-session bridge. A memory file is read when someone looks for it; a handoff note is read at the start of the next session by default. Optimize it for paste: one block, complete enough that a fresh session can resume without re-deriving the state.

## Pair with

- `fill-the-wait` — persisting learnings is one of the highest-value fill tasks.
- `cost-transparency` — a 17m wait is a 17m persist window; a 30s wait isn't.
- `follow-procedure` — a procedure that's discovered mid-session should be persisted so the next session can follow it.
