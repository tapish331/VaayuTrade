## What
- [ ] Baseline tooling & conventions
- [ ] commitlint + husky (commit-msg) installed

## Why
Establish consistent contributor workflow (editorconfig, gitignore, Conventional Commits, templates).

## Test Plan
- Ran `npm ci` (or `npm i`) in repo root, then `npx husky install`
- Verified conventional message passes locally: `git commit -m "feat(repo): tooling baseline"`
- Confirmed `.editorconfig` applies and `.gitignore` excludes expected files

## Checklist
- [ ] Conventional commit
- [ ] No secrets/keys in diff
- [ ] Docs updated if needed
