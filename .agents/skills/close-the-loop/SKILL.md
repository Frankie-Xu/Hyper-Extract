---
name: close-the-loop
description: When a multi-step user request is fully complete, deliver an explicit "closes the full request chain" summary that recaps the whole arc against the original ask, cites the commit SHA, separates any deferred "small notes for later" (with time estimates + doc pointers) from the win, and names the next action. Use when a long or multi-part request reaches full completion — not at intermediate milestones.
---

# Close The Loop

After a long multi-step request, the user wants to know the *whole* arc is closed, not just that the last step ran. A closure that names the chain end-to-end confirms completeness against the original ask; a closure that just says "done" leaves the user re-deriving whether everything actually shipped.

## The shape

```
That closes the full request chain: <step 1> (<commit SHA>), <step 2>,
<step 3>, and now <final step>.

Two small notes for later:
- <deferred item 1> — <time estimate> via <doc pointer> whenever you're ready.
- <deferred item 2>.

Next action: <the one thing to do next, if any>.
```

## Required elements

1. **"Closes the full request chain"** — name the arc end-to-end, in the order the user asked for it. This is the completeness check: every part of the original ask is accounted for.
2. **Cite the commit SHA** — `(c229ebc)` next to the push/merge. The SHA is the auditable anchor; `git show <sha>` verifies exactly what landed. A closure without a SHA is a claim; with a SHA it's a checkable fact.
3. **Separate "closed" from "small notes for later"** — don't mix loose ends into the win. A "Two small notes for later" section keeps the win clear and the follow-ups visible (see `document-non-action`).
4. **Time estimate + doc pointer on each deferred note** — "15 minutes via `services/commerce/README.md` whenever you're ready." The estimate lets the user budget; the doc pointer lets them pick it up without re-deriving; "whenever you're ready" signals it's not blocking.
5. **Name the next action** — the one thing to do next, if any. Not a list; one action.

## Narrate the end-to-end funnel, not just the code arc

For a business-layer change, the closure confirms the funnel is wired end to end, not just that the code compiles. Walk every path and where it terminates:

> "The full funnel, end to end: model-gateway's free check → store credits; cert-service certification → store checkout; research-portal → design-partner seat; finance-tool → waitlist → future premium notes — every path terminating in the live Medusa backend or the leads file, and consented interactions flowing into the data-ingest inbox for the R&D flywheel."

Each path names its origin, its terminus (Medusa / leads file), and (where relevant) its data flow into the R&D flywheel. A closure that says "the sites are built" without confirming where each path terminates hides a broken funnel; the end-to-end narration proves the funnel is wired.

## Prove one complete end-to-end path before declaring a fleet live

For a fleet/backend going live, don't try to verify every path. Prove ONE complete path end-to-end through the live system, which validates the wiring:

> "The fleet is on live data. One end-to-end proof through a public site's BFF, then closing out."

A single concrete path (public site → BFF → api → key → response) exercises every link in the chain. If it works, the wiring is sound; if it fails, you have one specific failure to diagnose (see `diagnose-before-retry`) rather than a vague "something's broken". Then close out. Verifying every path is expensive and unnecessary — one complete e2e proof is the confidence signal.

## When to close the loop

- A multi-step request reaches full completion (all parts done).
- A deferred tool-gap item gets resolved (the `gh` install completed → push the repo metadata → close the loop).
- A merge/deploy lands and the post-merge alignment is done.

Do NOT close at intermediate milestones — that's `progress-board` / `recap-on-long-session`.

## Anti-patterns

- **"Done!"** with no chain recap — the user re-derives whether everything shipped.
- **No commit SHA.** Unauditable; trust me bro.
- **Loose ends mixed into the win.** "Merged, pushed, docs aligned, oh and Medusa still needs Postgres" — muddies the win and buries the follow-up.
- **Deferred note with no time estimate or doc pointer.** The user can't budget or find it later.
- **Closing at every milestone.** Inflates the signal; the real closure gets ignored.

## Pair with

- `recap-on-long-session` — the recap is periodic status; the closure is end-of-request completion. Different cadences.
- `readiness-report` — the readiness report precedes the closure; the closure follows once the user's inputs are resolved.
- `document-non-action` — the "small notes for later" are documented non-actions or deferred items.
- `metadata-align` — the closure often names the docs/registry alignment as one of the chain steps.
