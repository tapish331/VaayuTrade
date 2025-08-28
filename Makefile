.PHONY: bootstrap py.install js.install fmt lint py.lint js.lint py.fmt js.fmt check versions

bootstrap: versions py.install js.install
	@echo "Bootstrap complete."

versions:
	@echo "== Tool versions ==" && \
	python3 --version && \
	( poetry --version || echo "poetry not found" ) && \
	node --version && \
	( corepack --version || echo "corepack not found" ) && \
	( pnpm --version || echo "pnpm not found (will be prepared via corepack)" ) && \
	echo "===================="

py.install:
	@echo "== Python setup =="
	@python3 -m pip install -q --user pipx || true
	@pipx ensurepath || true
	@pipx install poetry || true
	@poetry env use 3.11
	@poetry lock --no-update
	@poetry install --no-root
	@echo "Python deps installed."

js.install:
	@echo "== Node setup =="
	@corepack enable || true
	@corepack prepare pnpm@9.9.0 --activate || true
	@pnpm install --frozen-lockfile=false
	@pnpm run prepare || true
	@echo "Node deps installed."

fmt: py.fmt js.fmt

lint: py.lint js.lint

py.lint:
        @poetry run ruff check .
        @poetry run black --check .
        @poetry run mypy . || true

js.lint:
	@ESLINT_USE_FLAT_CONFIG=false pnpm eslint .

py.fmt:
	@poetry run ruff format .
	@poetry run black .

js.fmt:
        @pnpm prettier -w .

check:
        @echo "Running repo checks..."
        @make lint

db.up:
        @alembic -c infra/db/alembic.ini upgrade head

db.down:
        @alembic -c infra/db/alembic.ini downgrade base

db.revise:
        @alembic -c infra/db/alembic.ini revision -m "$(m)"
