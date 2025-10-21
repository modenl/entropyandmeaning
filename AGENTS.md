# Repository Guidelines

## Project Structure & Module Organization
- Current: root contains `构建统一的世界观.pdf` (primary artifact).
- Use `docs/` for Markdown notes, changelogs, and citations (e.g., `docs/reading-notes.md`).
- Use `assets/` for images/binaries with descriptive names (e.g., `assets/diagram-v1.png`).
- Use `src/` for code; mirror tests in `tests/` (e.g., `src/data_loader.py`, `tests/test_data_loader.py`).

## Build, Test, and Development Commands
- View PDF: macOS `open 构建统一的世界观.pdf`; Linux `xdg-open 构建统一的世界观.pdf`.
- If a `Makefile` is introduced:
  - `make setup` — install deps and pre-commit hooks.
  - `make test` — run `pytest` in `tests/`.
  - `make lint` — format with `black` and lint with `ruff`.

## Coding Style & Naming Conventions
- Docs: concise Markdown; filenames kebab-case (e.g., `concept-overview.md`).
- Python: 4-space indent, PEP 8; format with `black`, lint with `ruff`; modules snake_case (e.g., `data_loader.py`).
- JSON/YAML: 2-space indent; lowercase, hyphenated keys.

## Testing Guidelines
- Framework: `pytest`.
- Location: `tests/`, mirroring `src/`.
- Naming: `test_*.py`; aim for >80% coverage on new code.
- Run: `pytest` or `make test` (if available).

## Commit & Pull Request Guidelines
- Commits: Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:`); imperative, present tense.
- PRs: include purpose summary, scope of changes, screenshots for visual docs, linked issues, and rationale for large binaries (use Git LFS >10MB).

## Security & Configuration Tips
- Do not commit secrets; add ignores to `.gitignore` as needed.
- Prefer diffable sources; use Git LFS for large assets (>10MB).

## Agent-Specific Instructions
- Keep changes minimal and targeted; do not invent build steps not present.
- Scope: this file applies repo-wide; deeper `AGENTS.md` files override within their subtrees.

