---
name: pre-commit-hygiene
description: Before a large or migration commit, exclude junk (build output, local tool dirs, node_modules) and scan for secrets and sensitive files so they don't enter history. Use before any commit that spans many files or a migration, before `git add`, and whenever the user says "never commit secrets" or "let's push this".
---

# Pre-Commit Hygiene

A big migration commit will vendor junk and may include secrets. Once in history, removing them is a force-push rebase. The cheap guard is *before* `git add`, not after.

## The sequence (run before `git add`)

1. **Size the junk dirs.** Find what's large that shouldn't be committed:
   ```bash
   du -sh .opencode/* .claude/* .next node_modules 2>/dev/null | sort -rh | head
   ```
   Anything large that's tool-local (`.opencode/`, `.claude/`, `.next/`, `node_modules/`, `.turbo/`, `.vercel/`) goes in `.gitignore`, not the commit.

2. **Inspect local settings files.** Local agent/tool settings often hold secrets or machine-specific paths:
   ```bash
   cat .claude/settings.local.json 2>/dev/null | head -20
   ```
   Confirm it's gitignored. If it contains secrets, never stage it.

3. **Check for stray "linked"/artifact paths.** The repo had a stray `{'LINKED'}` entry — scan for similar artifacts that shouldn't be tracked:
   ```bash
   ls -b | grep -i linked
   git status --short | grep -iE 'linked|\.bak|\.local|\.env$|\.env\.'
   ```

4. **Secrets scan across the diff you're about to stage.** Before adding, scan staged-candidate files for secret patterns:
   ```bash
   git diff --no-color | grep -iE 'api[_-]?key|secret|password|token|-----BEGIN .*PRIVATE KEY-----|sk_live_|sk_test_|AKIA[0-9A-Z]{16}'
   ```
   Also scan env files and anything matching `*.env`, `*.local.json`, `credentials*`.

5. **Reach: vuln / anti-pattern scan.** The user asked for this — run a dependency vuln check and a light anti-pattern grep on the changed code:
   ```bash
   pnpm audit --audit-level=high 2>&1 | tail -n 20
   uv run pip-audit 2>&1 | tail -n 20
   ```

6. **Only then `git add`** — staging explicitly, not `git add .` unless every file in the diff has passed the above.

## What to gitignore (not commit)

- Tool-local dirs: `.opencode/`, `.claude/`, `.cursor/` (mostly), `.turbo/`, `.vercel/`, `.next/`, `node_modules/`.
- Local settings: `*.local.json`, `.env*` (except `.env.example`).
- Build output: `dist/`, `build/`, `.output/`, `*.tsbuildinfo`.
- Stray artifacts: `{'LINKED'}`, `*.bak`, `*.log`.

## If secrets are already staged

- `git reset HEAD <file>` to unstage.
- If a secret was committed in a prior commit, do **not** `--amend` if pushed (see commit safety: never force-push to main). Surface it to the user; rotate the secret; plan a history rewrite with explicit user approval.

## Anti-patterns

- **`git add .` on a big migration without scanning.** Vendors `.opencode/` and friends; history bloats; possible secret leak.
- **Scanning after the commit.** The secret is now in history; the cheap window is closed.
- **Committing `.env` "because it's just local".** Local envs get pushed; rotate-then-rebase is painful.
- **`git add -A` to "be safe".** Same risk as `add .` — safety comes from the pre-scan, not the add flag.

## Pair with

- `validate-gate` — tests must be green before the commit; report exact pass/skip/fail counts.
- `follow-procedure` — tie the commit message to a named tracker item ("uncommitted fleet migration, P0 in TECH_DEBT").
- `readiness-report` — the commit closes the readiness report; the report's non-actions tell you what's intentionally *not* in the commit.
- `background-failure-triage` — a failed secrets scan is a stop-the-commit signal, not a backgroundable one.
