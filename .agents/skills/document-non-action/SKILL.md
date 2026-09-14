---
name: document-non-action
description: When you deliberately choose not to do something that looks like it would be part of the task, state the non-action and its rationale explicitly so it isn't read as an oversight. Use whenever you skip a plausible-looking step on purpose — a file you didn't edit, a feature you didn't wire, an existing issue you didn't rework, a test you didn't add — because of a real constraint or a lane/spec boundary.
---

# Document Non-Action

A missing piece is usually read as an oversight. Stating "I deliberately didn't do X *because* Y" converts a presumed gap into a documented decision the user can ratify or override. The non-action is the decision.

## Why this matters

- Reviewers scan for gaps. A gap they have to flag costs them a turn and costs you a "yes I knew about that" reply.
- A non-action with a rationale is often a *better* decision than the action would have been (scope, lane, measurement integrity, spec-missing). That reasoning is valuable and should survive the session.
- The user can't ratify a decision they can't see. Silent non-actions become silent defaults.

## The shape

One line, three parts:

```
I deliberately did not <action> — <rationale>; <follow-up>.
```

Examples from practice:

```
I deliberately did not wire observability into the hill-climb loop —
per-step logging inside a time-budgeted training loop would perturb
measured results; it needs a small spec.

I didn't rework existing auth without your sign-off — the /v1/trace
RLS bypass is a pre-existing endpoint (SEC-003) and is yours to approve.
```

- **`<action>`** — the specific thing you didn't do (concrete, not "I didn't finish").
- **`<rationale>`** — the real reason: measurement integrity, lane boundary, missing spec, prod-safety, user-decision-required. Not "ran out of time".
- **`<follow-up>`** — what would unblock it: a spec, a sign-off, a separate task, an issue ID.

## Where to put it

- In the `readiness-report` list — non-actions belong in the handoff, not hidden.
- In a memory/ADR file if the rationale is durable (a decision that should outlive the session).
- In a code comment at the relevant site if a future contributor might re-add the thing ("// observability intentionally not wired here — see ADR-00X").
- In the board as a `◻` with a `⚠` if it's a deferred task, not a permanent decision.

## When NOT to document non-action

- The thing you didn't do was never plausible (you didn't "not deploy to Mars" — don't document it).
- The rationale is just "didn't get to it" — that's a TODO, not a non-action; put it on the board.
- It was a small, obvious skip that no one would flag.

## The placeholder-pending-decision variant

A deferred decision often shows up as a placeholder value in code/data, not as a skipped action. Document it the same way — name the owner and the next step:

```
// Price is a placeholder pending Operator pricing decision — adjust in admin.
```

A placeholder with no note is read as "the price is $X". A placeholder with a note is read as "the price is $X *for now*, the Operator decides, adjust here". The note converts a forgotten value into a deferred decision. Applies to any pending value: prices, thresholds, default config, copy that needs brand sign-off.

## Anti-patterns

- **Silent skip.** The gap gets flagged; you reply "yes I knew"; wasted turns.
- **Rationale as excuse.** "Didn't have time" is not a non-action rationale; it's a TODO.
- **Documenting every plausible skip.** Inflates the report; the signal non-actions get lost.
- **No follow-up.** A non-action with no unblock path is just a permanent gap; say whether it needs a spec, a sign-off, or a separate task.

## Pair with

- `readiness-report` — non-actions belong in the handoff list.
- `lane-discipline` — "not my lane" is one of the strongest non-action rationales.
- `persist-learnings` — a durable non-action rationale belongs in an ADR or memory file.
