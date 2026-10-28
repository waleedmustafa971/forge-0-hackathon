#!/usr/bin/env bash
# Codespaces, once: assemble FORGE-0 into ./forge-0, install it and build the dashboard and the
# sandbox images. Safe to run again; it stops at the first step that fails.
set -euo pipefail
cd "$(dirname "$0")/.."

if [ ! -d forge-0 ]; then
  rm -rf .forge-0.partial  # left by an interrupted earlier attempt; forge-0/ exists only once verified
  python assemble.py --out forge-0
fi
cd forge-0
[ -f .env ] || cp .env.example .env

python -m venv backend/.venv
backend/.venv/bin/pip install -q --upgrade pip
backend/.venv/bin/pip install -q -e ./backend

(cd frontend && npm ci --no-audit --no-fund && npm run build)

bash ../.devcontainer/docker-up.sh
docker pull -q node:24-alpine
docker build -q -t forge0/sandbox-python:3.12 backend/sandbox/images/python
echo "FORGE-0 is installed in ./forge-0"
