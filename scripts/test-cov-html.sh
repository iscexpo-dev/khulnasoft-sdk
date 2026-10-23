#!/usr/bin/env bash

set -e
set -x

uv run pytest --cov=khulnasoft --cov-report=term-missing --cov-report=html tests/ ${@}
