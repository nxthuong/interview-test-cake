#!/bin/sh
set -e

### Setup DAG development environment
if ! command -v "uv" &> /dev/null; then
    # Using pip
    python3 -m venv .venv
    . ./.venv/bin/activate
    pip install -r requirements.txt
else
    # Using uv
    uv sync
fi
