.PHONY:
.SILENT:

init:
	uv sync
	uv run pre-commit install

check:
	uv lock
	uv run pre-commit run --all-files

run:
	uvx marimo edit notebook.py
