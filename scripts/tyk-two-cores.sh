#!/usr/bin/env bash
# Tyk warns that one CPU is too few for production. The main run gives every
# proxy one core; this reruns Tyk's plain and full-ladder steps with two, to
# see how much of its tail latency comes from that.
set -euo pipefail
cd "$(dirname "$0")/.."
docker compose -f compose.yaml -f compose.tyk2.yaml up -d --force-recreate --wait tyk redis 2>&1 | tail -1
until curl -s -o /dev/null http://127.0.0.1:28080/; do sleep 1; done
./scripts/01-tyk-key.sh > /dev/null
python3 scripts/verify.py | tail -1
python3 scripts/bench.py --systems tyk --steps plain,transform --rates 1000,2000 \
  --rounds 3 --duration 30 --warmup 10 --name tyk-two-cores
docker compose up -d --force-recreate --wait tyk redis 2>&1 | tail -1
./scripts/01-tyk-key.sh > /dev/null
