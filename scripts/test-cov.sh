#!/usr/bin/env bash

set -e
set -x

COVERAGE_FILE="${COVERAGE_FILE:-coverage/.coverage}"
CONTEXT="${CONTEXT:-default}"

uv run pytest --cov=khulnasoft --cov-context=test --cov-report=term-missing --cov-report=xml tests/ ${@}
