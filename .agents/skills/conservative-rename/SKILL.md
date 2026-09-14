---
name: conservative-rename
description: When applying a brand or name rename across a codebase, replaces paths and ids only — never blanket word replaces — and cleans up unused imports in the same phase. Use when rebranding sites, agents, or products where the old name could appear in unrelated prose (hub, cursor, control).
---

# Conservative Rename

A blanket word replace on a rename over-replaces — "cursor" the agent name vs "cursor" the CSS/UX term; "hub" the site vs "hub" the generic word; "control" the site vs "control" the variable. The result is corrupted prose, broken identifiers, and false matches. Restrict the replace to the structured references; leave the prose to a human pass.

## The rule

> Replace paths and ids only; no blanket word replaces.

- **Paths** — `apps/sites/research-rag/` → `apps/sites/research/`, import paths, file paths in config.
- **Ids** — `siteId: "research-rag"` → `siteId: "research"`, registry keys, fleet ids, spec ids.
- **Identifiers** — variable/type names that are unambiguously the renamed entity (`ResearchRagClient` → `ResearchClient`).

Do NOT blanket-replace:
- Prose in docs/comments that *might* refer to the entity — review each occurrence; some may be the generic word.
- Substrings inside other words ("hub" inside "hubspot", "control" inside "controller").
- User-facing copy — brand copy changes are a product decision per-occurrence, not a find-replace.

## The sequence

1. **Structural renames first** — paths, ids, identifiers (the structured references). These are safe because they're unambiguous.
2. **Clean up now-unused imports** — a rename leaves imports that referenced the old name now-unused. Clean them in the same phase so the diff is complete and the build stays green:
   > "Cleaning the now-unused imports in the storefront page."
3. **Copy/metadata alignment (Phase 6)** — the user-facing copy and the metadata fields, reviewed per-occurrence, not blanket-replaced.
4. **Docs/memory brand alignment (Phase 7)** — conservative patterns on docs: paths and ids only; prose reviewed per-occurrence.

## Why conservative

- **False matches are silent.** A blanket replace that hits "cursor" in a CSS context doesn't error — it ships a wrong doc. Conservative patterns make the replace set auditable.
- **Prose needs judgment.** "The hub of the fleet" may or may not rename when the site "hub" renames — a human decides, a regex can't.
- **Revertability.** A conservative, structured replace is easy to review and revert. A blanket replace that touched 500 files is not.
- **Diffs stay reviewable.** A path/id replace diff shows the structural change clearly; a blanket-replace diff is noise.

## Anti-patterns

- **`sed -i 's/old/new/g'` across the repo.** The classic foot-gun — over-replaces, no review, hard to revert.
- **Leaving unused imports "for the linter".** Fragments the rename across phases; the rename phase should leave a green build.
- **Renaming prose without review.** Brand copy is a product decision; a find-replace isn't a brand decision.
- **Substring matches.** `s/hub/hubspot/g` would be a disaster; scope the match to whole identifiers/paths.

## Pair with

- `metadata-align` — the rename's alignment phases (copy/metadata, docs/memory) are `metadata-align` applied to a rebrand.
- `match-conventions` — after a rename, mirror the new naming in sibling files.
- `respect-the-guard` — a blanket replace is a guard you don't bypass; the conservative pattern is the legitimate path.
- `logical-commit-split` — structural renames, import cleanup, and copy alignment are separate logical commits.
