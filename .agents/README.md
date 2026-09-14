# Project agent skills

83 curated Agent Skills for professional collaborative development. Cursor loads them from `.agents/skills/`.

These are **not** Hyper-Extract product skills (`hyperextract-skills/` stays the domain pack). This directory is the engineering/collaboration playbook for humans and coding agents working in this repo.

## How to use

1. For a new feature or non-trivial bugfix, start with `/grill-with-docs` (or `/grill-me` if no docs yet).
2. Turn the conversation into a spec with `/to-spec`, then tickets with `/to-tickets`.
3. Implement with `/implement` driving `/tdd`.
4. Review with `/code-review`, then `/finishing-a-development-branch`.
5. If you do not know which skill applies, invoke `/ask-matt` or `using-agent-skills`.

Do not install thousand-skill aggregator dumps. Update the vendored packs with:

```bash
npx skills@latest update
```

## Packs (all MIT unless noted)

| Source | Count | Role |
| --- | --- | --- |
| [mattpocock/skills](https://github.com/mattpocock/skills) | 26 | Default collab pipeline: grill, spec, tickets, TDD, review, triage |
| [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | 25 | Production lifecycle: API, security, git, CI/CD, ADRs, shipping |
| [obra/superpowers](https://github.com/obra/superpowers) | 13 | Branch finish, review request/receive, worktrees, verification |
| [anthropics/skills](https://github.com/anthropics/skills) | 6 | Skill authoring, MCP, docs, frontend, webapp testing, internal comms |
| [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills) | 2 | Writing and web design guidelines |
| [jcdavis131/cursor-agent-skills](https://github.com/jcdavis131/cursor-agent-skills) | 11 | Commit hygiene, convention matching, subagent verification |

Shared Addy Osmani checklists live in `.agents/references/` so lifecycle skills can load them on demand.

Install lockfile: `skills-lock.json` at the repo root (`npx skills experimental_install` restores from it).

## Default pipeline (Matt Pocock)

| Skill | When |
| --- | --- |
| `setup-matt-pocock-skills` | Once per repo (already applied: GitHub issues, default triage labels, single-context docs) |
| `grill-me` / `grill-with-docs` | Before coding: align on the change |
| `to-spec` | Publish the conversation as a spec |
| `to-tickets` | Split into tracer-bullet tickets |
| `implement` + `tdd` | Build the tickets test-first |
| `code-review` | Standards + spec review of the diff |
| `triage` | Move GitHub issues through ready-for-agent / human |
| `handoff` | Compact the session for the next agent |

## Production lifecycle (Addy Osmani)

| Skill | When |
| --- | --- |
| `spec-driven-development` | PRD before a large change |
| `planning-and-task-breakdown` | Spec → atomic tasks |
| `incremental-implementation` | Thin vertical slices |
| `test-driven-development` | Broader TDD guidance (prefer `tdd` for this repo's default loop) |
| `api-and-interface-design` | Public contracts and module boundaries |
| `git-workflow-and-versioning` | Atomic commits, trunk-based habits |
| `ci-cd-and-automation` | Pipelines and quality gates |
| `security-and-hardening` | Auth, secrets, input boundaries |
| `documentation-and-adrs` | Record the *why* |
| `code-review-and-quality` | Five-axis review before merge |
| `shipping-and-launch` | Launch checklist |

## Collaboration / verification (Superpowers)

| Skill | When |
| --- | --- |
| `requesting-code-review` | Ask for a review against the plan |
| `receiving-code-review` | Respond to review comments |
| `finishing-a-development-branch` | Tests green, then PR vs keep/discard |
| `verification-before-completion` | Prove the fix, do not claim it |
| `using-git-worktrees` | Isolated workspace for a change |
| `writing-plans` / `executing-plans` | Detailed plan then batched execution |

## Intentionally not installed

- Thousand-skill aggregators (`sickn33/agentic-awesome-skills`, similar dumps)
- OSINT / pentest / exploit skill packs
- Book-derived rule dumps that may reproduce copyrighted text
- Duplicate Superpowers `test-driven-development` (this repo uses Matt Pocock `tdd` as the default loop)
