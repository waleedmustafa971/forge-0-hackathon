#!/usr/bin/env bash
# Smoke test of the Codespace, run by .github/workflows/codespace.yml after the dev container's own
# setup.sh and start.sh: the backend that start.sh launched must still be serving, and one mock
# investigation of D2 must end in a verified fix after a rejected patch, all in the real sandbox.
set -euo pipefail
cd "$(dirname "$0")/../forge-0"
API=http://127.0.0.1:8010/api
py=backend/.venv/bin/python

curl -fsS --max-time 5 "$API/system/health" > /dev/null \
  || { echo "The backend started by start.sh is not serving" >&2; tail -n 30 data/backend.log >&2; exit 1; }
curl -fsS --max-time 5 -o /dev/null http://127.0.0.1:8010/

repo=$(curl -fsS "$API/repositories" | $py -c 'import json,sys; print(json.load(sys.stdin)[0]["id"])')
inv=$(curl -fsS -X POST "$API/investigations" -H 'content-type: application/json' \
  -d "{\"repository_id\": \"$repo\", \"target_test\": \"charges the customer exactly once when a timed-out request is retried\"}" \
  | $py -c 'import json,sys; print(json.load(sys.stdin)["id"])')
echo "Investigation $inv started"
for _ in $(seq 1 120); do
  status=$(curl -fsS "$API/investigations/$inv" | $py -c 'import json,sys; print(json.load(sys.stdin)["status"])')
  case "$status" in completed|failed|cancelled) break ;; esac
  sleep 5
done
curl -fsS "$API/investigations/$inv" | $py -c '
import json, sys
d = json.load(sys.stdin)
print("status:", d["status"], "| verdict:", d.get("verdict"), "|", (d.get("summary") or {}).get("message"))
sys.exit(0 if d.get("verdict") == "verified_fix" else "expected a verified fix")'
curl -fsS "$API/investigations/$inv/patches" | $py -c '
import json, sys
states = [p["status"] for p in json.load(sys.stdin)]
print("patches:", states)
sys.exit(0 if states[:1] == ["rejected"] and states[-1:] == ["verified"] else "expected a rejected patch, then a verified one")'
echo "Codespace smoke test passed"
