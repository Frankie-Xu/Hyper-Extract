---
name: match-conventions
description: Read one or two sibling files in the same area before writing a new file, so the new file matches the codebase's existing imports, component shape, data-fetching style, and folder structure. Use before creating any new file in an existing area of the codebase — a new page, component, route handler, test, service module, or config — especially when a similar file already exists nearby.
---

# Match Conventions

A new file written from scratch invents its own conventions. A new file written after reading a sibling lands as if the same author wrote both. The second is what you want.

## The move

Before authoring a new file:

1. **Find a sibling.** The closest existing file that does something similar — same layer (page/component/route/test), same area, same framework. A new page in `apps/sites/<site>/app/<route>/page.tsx` → look at another page in the same site. A new service module → look at a sibling module in `services/<svc>/app/services/`.
2. **Read it.** A head is enough for big files (`head -30` / first 30 lines); full read for small ones. You're looking for:
   - import style and ordering,
   - the component / function shape (server vs client component, default export vs named, hooks used),
   - how it talks to data (API client import path, fetch pattern, polling interval convention),
   - folder structure and co-location (components in `../components/`, types in `../lib/types`),
   - error/loading states and how they're rendered.
3. **Mirror it.** Use the same import paths, the same component shape, the same naming. Don't introduce a new pattern because it's "better" — consistency beats local optimization.
4. **Only diverge when the new file's needs genuinely differ**, and say why in the file if you do.

## Cheap version

If you can't find a perfect sibling, read the closest two and synthesize. Two examples are usually enough to infer the convention.

## What this prevents

- A new page that imports `axios` when the site uses a local `lib/api` client.
- A new component that's a server component when the area is all `"use client"`.
- A new test that uses `pytest.fixture` when the suite uses a shared `conftest`.
- A new module that exports a default when the area uses named exports.
- **A new site/module that skips the boring hygiene files** (`.gitignore`, `.env.example`, `tsconfig.json`, `pyproject.toml`) — include whatever a sibling has, written as a deliberate first artifact, not an afterthought.

Each of these is a review-comment you can prevent by reading one sibling first.

## When to skip

- Genuinely first-of-its-kind file with no sibling (a brand new area). Then you're setting the convention — pick deliberately and document it.
- The user explicitly asked for a specific different pattern.

## Pair with

- `smoke-import` — after mirroring conventions, smoke-import to confirm the wiring is sound.
- `affected-tests` — run the sibling's tests to confirm the shared shape still holds.
