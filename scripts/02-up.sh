#!/usr/bin/env bash
# Fresh containers (so memory numbers start from a clean process), the Tyk key,
# then the functional checks.
set -euo pipefail
cd "$(dirname "$0")/.."
docker compose up -d --force-recreate --wait 2>&1 | tail -1
for port in 9000 8080 18000 28080; do
  until curl -s -o /dev/null "http://127.0.0.1:$port/"; do sleep 1; done
done
./scripts/01-tyk-key.sh > /dev/null
python3 scripts/verify.py | tail -1
