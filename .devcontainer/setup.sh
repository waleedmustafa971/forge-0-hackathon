#!/usr/bin/env bash
# Codespaces, once: assemble FORGE-0 into ./forge-0, install it and build the dashboard and the
# sandbox images. Takes about 5 minutes.
set -euo pipefail
cd "$(dirname "$0")/.."

[ -d forge-0 ] || python assemble.py --out forge-0
cd forge-0
[ -f .env ] || cp .env.example .env

python -m venv backend/.venv
backend/.venv/bin/pip install -q --upgrade pip
backend/.venv/bin/pip install -q -e ./backend

(cd frontend && npm ci --no-audit --no-fund && npm run build)

for _ in $(seq 1 60); do docker info > /dev/null 2>&1 && break; sleep 2; done
docker pull -q node:24-alpine
docker build -q -t forge0/sandbox-python:3.12 backend/sandbox/images/python
echo "FORGE-0 is installed in ./forge-0"
