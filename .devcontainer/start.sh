#!/usr/bin/env bash
# Codespaces, on every start: serve FORGE-0's API and dashboard on port 8010.
# With a META_API_KEY Codespaces secret it runs on Muse Spark 1.3, otherwise on the mock provider.
set -euo pipefail
cd "$(dirname "$0")/../forge-0"
mkdir -p data

for _ in $(seq 1 60); do docker info > /dev/null 2>&1 && break; sleep 2; done

export SERVE_FRONTEND_DIR=frontend/dist
export DATABASE_URL="sqlite:///$PWD/data/forge0.db"  # no database server needed
export WORKER_THREADS=1 SANDBOX_MAX_CONCURRENT=1 LOG_FORMAT=text
if [ -n "${META_API_KEY:-}" ]; then export AI_PROVIDER=meta; fi

cd backend
# setsid: lifecycle commands may kill their process group when they finish.
setsid nohup .venv/bin/uvicorn api.main:app --host 127.0.0.1 --port 8010 --no-access-log \
  > ../data/backend.log 2>&1 &
for _ in $(seq 1 60); do
  curl -fs http://127.0.0.1:8010/api/system/health > /dev/null 2>&1 && break
  sleep 1
done
echo "FORGE-0 is running on port 8010 (provider: ${AI_PROVIDER:-mock}). Log: forge-0/data/backend.log"
