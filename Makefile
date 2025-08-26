.PHONY: build hooks tree check

build:
	@echo "Task 01 placeholder build: OK"

hooks:
	pre-commit install

tree:
	@find . -maxdepth 3 -type d | sort

check:
	@pre-commit run --all-files || true
