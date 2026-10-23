# AGENTS.md

## Project Overview

Python SDK for KhulnaSoft providing blob storage, runtime caching, OIDC token handling, and FastAPI integrations.

## Commands

- Install dependencies: `uv sync`
- Run tests: `bash scripts/test.sh`
- Run lint: `bash scripts/lint.sh`
- Run format: `bash scripts/format.sh`
- Run coverage: `bash scripts/test-cov.sh`
- Run HTML coverage: `bash scripts/test-cov-html.sh`
- Run pre-commit: `uv run pre-commit run --all-files`

## Code Style

- Python 3.10+ with modern typing (`X | Y` syntax).
- Line length: 100.
- Ruff for lint and format; mypy for type checking.

## Testing

- Unit tests: `tests/` (run via `scripts/test.sh`).
- Integration tests: `tests/integration/` (require credentials; skipped without them).
- Example tests: `tests/test_examples.py` (skip when credentials are missing).

## CI/CD

- Workflows: `.github/workflows/ci.yml`, `pre-commit.yml`, `redistribute.yml`, `detect-conflicts.yml`.
- Dependabot: `.github/dependabot.yml`.
- Pre-commit config: `.pre-commit-config.yaml`.

## Notes

- Use `uv` for Python environment and dependency management.
- Prefer `scripts/` shell scripts for repeated tasks.
