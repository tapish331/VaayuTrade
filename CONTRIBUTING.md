# Contributing

- Use **Conventional Commits** (e.g., `feat(traderd): add scheduler`).
- After cloning, install tooling in repo root:
  ```bash
  npm ci || npm i
  npx husky install
  pre-commit install
  ```

* Commit messages are validated by **commitlint** via Husky `commit-msg` hook.
