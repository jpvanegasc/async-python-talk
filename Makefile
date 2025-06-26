.PHONY:
.SILENT:

init:
	uv sync
	uv run pre-commit install

check:
	uv lock
	uv run pre-commit run --all-files

run:
	uv run marimo edit notebook.py
