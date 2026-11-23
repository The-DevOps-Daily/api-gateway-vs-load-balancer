#!/usr/bin/env bash
# Everything after the main run, in the order it was recorded.
set -euo pipefail
cd "$(dirname "$0")/.."
./scripts/02-up.sh
[ -f results/limit-semantics.json ] || python3 scripts/limit_semantics.py
./scripts/explain-kong-timer.sh
./scripts/02-up.sh
./scripts/break-keepalive.sh
./scripts/02-up.sh
python3 scripts/bench.py --rates 0 --rounds 3 --duration 15 --warmup 5 --name max
./scripts/tyk-two-cores.sh
echo EXTRAS-DONE
