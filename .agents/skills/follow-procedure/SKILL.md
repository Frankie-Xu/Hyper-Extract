---
name: follow-procedure
description: When a documented, named procedure exists for the decision at hand (a dataviz palette procedure, a commit-message convention, a deploy checklist, a spec, an ADR), cite it by name and follow it rather than improvising. Use whenever a written procedure, spec, checklist, ADR, or convention applies to the current decision — especially in spec-driven repos.
---

# Follow Procedure

If a decision has already been made and written down, reusing it beats re-litigating it. A named procedure is auditable and consistent; an ad-hoc choice is neither.

## The move

1. **Recognize the decision is procedural.** Palette, commit format, deploy steps, error-response shape, naming, migration order, eval-gate thresholds — these are exactly the decisions someone has probably already written down.
2. **Find the procedure.** Search the repo: `docs/`, `specs/`, `docs/adr/`, `docs/wiki/`, `AGENTS.md`, `.cursor/rules/`, `CLAUDE.md`, `memory/`. Look for a name like "dataviz procedure", "deploy checklist", "ADR-002", "spec 0008".
3. **Cite it by name.** In your response: "Validating the chart palette per the dataviz procedure" — name + that you're following it. This makes the choice auditable and tells the user which document to override if they disagree.
4. **Follow it.** Don't silently deviate. If a step doesn't fit the current case, say which step and why you're diverging.
5. **If no procedure exists**, say so and either propose one (for repeat decisions) or just decide (for one-offs).

## When to NOT improvise even though you "know better"

- The procedure is more conservative than you'd like. Following it preserves consistency; the right fix is to update the procedure, not skip it.
- The procedure is slightly out of date. Follow the spirit, note the staleness, propose an update.
- You're under time pressure. Procedures exist precisely to short-circuit re-deliberation under pressure.

## Mark findings done in the tracker via a script

When a tracked item (a review finding, a task) is fixed, mark it done in the tracker via a script — load the JSON, find by id, set status + claimedBy + notes:

```python
import json
d = json.load(open('config/work_queue.json', encoding='utf-8'))
for t in d['tasks']:
    if t.get('id') == 'REV-909':
        t['status'] = 'done'
        t['claimedBy'] = 'claude'
        t['notes'] = 'atomic temp+rename save; cross-process lock still open'
json.dump(d, open('config/work_queue.json', 'w', encoding='utf-8'), indent=2)
```

- **status='done'** — the finding is resolved.
- **claimedBy** — who resolved it (agent name).
- **notes** — record both the fix *and* the remaining gap (see `document-non-action`). A finding marked "done" with a documented remaining limitation is honest; "done" with a hidden gap is not.

The tracker is the source of truth for finding status; a fix that isn't recorded in the tracker is invisible to the next agent.

## When it's fine to decide without a procedure

- Genuine one-off with no recurrence.
- Decision clearly below the bar where writing it down pays off.
- User explicitly overrides.

## Anti-patterns

- **Silent deviation.** The worst outcome — you look like you followed the procedure but didn't, and the next contributor can't tell why.
- **Re-deliberating every time.** A procedure that's re-litigated on every use isn't a procedure.
- **Citing a procedure you didn't actually read.** Open it, confirm it says what you think, then cite.

## Pair with

- `match-conventions` — conventions are the implicit version of procedures; procedures are the explicit version of conventions.
