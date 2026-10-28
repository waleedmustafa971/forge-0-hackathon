#!/usr/bin/env bash
# Codespaces, on every start: serve FORGE-0's API and dashboard on port 8010, or say why not.
# With a META_API_KEY Codespaces secret it runs on Muse Spark 1.3, otherwise on the mock provider.
set -euo pipefail
cd "$(dirname "$0")/.."
[ -d forge-0 ] || { echo "FORGE-0 is not installed (setup.sh did not finish): run bash .devcontainer/setup.sh" >&2; exit 1; }
cd forge-0
mkdir -p data
LOG=data/backend.log
PIDFILE=data/backend.pid
URL=http://127.0.0.1:8010

fail() {
  echo "FORGE-0 did not start: $1" >&2
  if [ -f "$LOG" ]; then tail -n 30 "$LOG" >&2; fi
  exit 1
}
health() { curl -fsS --max-time 5 "$URL/api/system/health" 2> /dev/null; }

# One backend only: reuse a healthy one, replace one that stopped answering.
if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2> /dev/null; then
  if health > /dev/null; then echo "FORGE-0 is already running on port 8010"; exit 0; fi
  kill "$(cat "$PIDFILE")" 2> /dev/null || true
  sleep 2
fi

for _ in $(seq 1 60); do timeout 5 docker info > /dev/null 2>&1 && break; sleep 2; done
timeout 5 docker info > /dev/null 2>&1 || fail "the Docker daemon is not reachable"
[ -f frontend/dist/index.html ] || fail "the dashboard is not built (frontend/dist/index.html is missing)"

export SERVE_FRONTEND_DIR=frontend/dist
export DATABASE_URL="sqlite:///$PWD/data/forge0.db"  # no database server needed
export WORKER_THREADS=1 SANDBOX_MAX_CONCURRENT=1 LOG_FORMAT=text
if [ -n "${META_API_KEY:-}" ]; then export AI_PROVIDER=meta; fi

# setsid: lifecycle commands may kill their process group when they finish.
setsid nohup backend/.venv/bin/uvicorn api.main:app --app-dir backend --host 127.0.0.1 --port 8010 \
  --no-access-log > "$LOG" 2>&1 &
echo $! > "$PIDFILE"

status=""
for _ in $(seq 1 90); do
  kill -0 "$(cat "$PIDFILE")" 2> /dev/null || fail "the backend exited"
  if status=$(health); then break; fi
  sleep 1
done
[ -n "$status" ] || fail "the API did not answer within 90 s"
echo "$status" | backend/.venv/bin/python -c '
import json, sys
d = json.load(sys.stdin)
bad = [k + ": " + str(d[k].get("detail")) for k in ("database", "sandbox") if not d[k]["ok"]]
sys.exit("unhealthy (" + "; ".join(bad) + ")" if bad else 0)' || fail "the health check reported a problem"
curl -fsS --max-time 5 -o /dev/null "$URL/" || fail "the dashboard page did not load"
asset=$(grep -o 'assets/[^"]*\.js' frontend/dist/index.html | head -n 1)
curl -fsS --max-time 5 -o /dev/null "$URL/$asset" || fail "the dashboard script $asset did not load"
echo "FORGE-0 is running on port 8010 (provider: ${AI_PROVIDER:-mock}). Log: forge-0/$LOG"
