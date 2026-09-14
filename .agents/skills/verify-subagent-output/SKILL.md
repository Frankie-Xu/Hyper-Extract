---
name: verify-subagent-output
description: After parallel subagents (SME reviewers, research agents, task agents) return, spot-check their output against the named contract/standard before synthesizing or marking the task done. Use whenever you dispatched subagents and they've returned artifacts — especially before treating their output as ground truth in a synthesis or a "done" report.
---

# Verify Subagent Output

Subagent output is the most trusted-yet-unverified thing in an agent loop. You dispatched it; it returned prose; you're tempted to trust it. Don't — spot-check first.

## Why this matters

- SMEs drift from the contract — they skip a section, add an unrequested one, or pad.
- Subagents can claim evidence they didn't actually gather ("verified against the spec" without opening the spec).
- A synthesis built on unverified subagent output inherits every gap.
- A "done" report built on it misleads the user.

## The spot-check

You don't re-do the subagent's work. You check **conformance + substance**:

1. **Conformance to the contract.** Each returned file has the agreed sections, in the agreed shape, at the agreed length. Missing section = drift.
2. **Conformance to the named standard.** If output is supposed to be "OKF-conformant" or "ADRs" or "spec-0008-shaped", check the shape against that standard by name.
3. **Substance, not just shape.** At least one non-trivial claim per section that a careful reader would accept as evidence the SME actually did the work — not filler. "Security was reviewed" is filler; "authn boundary at `app/auth.py:42` is missing a workspace check" is substance.
4. **A sample, not all.** For 5 SMEs, spot-check 1–2 in depth and skim the rest. Full re-verification defeats the fan-out.

## The report

State the result as a one-line verdict that names the standard:

```
Bundle is fully OKF-conformant with five substantive reviews.
```

Or, if drift found:

```
OKF bundle: 4/5 conformant; security review missing the Risk section — sent back for completion.
```

## When to send back vs. fix yourself

- **Send back** (re-dispatch the subagent with the specific gap) when the gap is large or in the SME's domain.
- **Fix yourself** when the gap is a missing boilerplate section you can write in one line.

## When NOT to verify

- The subagent's output is purely advisory and won't feed a synthesis or a "done" claim.
- The cost of the spot-check exceeds the cost of being wrong (rare — usually the spot-check is cheap).

## Pair with

- `sme-fanout` — verification is the step between "all SMEs returned" and "synthesize".
- `validate-gate` — same ethos: cheap gate before declaring done.
- `follow-procedure` — the named standard you check against is the procedure.
