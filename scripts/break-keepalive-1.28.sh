#!/usr/bin/env bash
# The same break on nginx 1.28. Before 1.29.7, nginx sent "Connection: close"
# upstream unless told otherwise, so the /auth location of the broken config
# (its own proxy_set_header, no Connection "") opens a backend connection per
# request, while /plain in the same file (no proxy_set_header of its own)
# keeps its connections.
set -euo pipefail
cd "$(dirname "$0")/.."
docker compose -f compose.yaml -f compose.nginx128.yaml --profile break128 up -d nginx128-broken 2>&1 | tail -1
for i in $(seq 1 60); do curl -sk -o /dev/null https://127.0.0.1:8453/plain && break; sleep 1; done
python3 scripts/bench.py --systems nginx128-broken --steps tls,auth --rates 1000,2000 --rounds 3 \
  --duration 30 --warmup 10 --name break-keepalive-1.28
docker compose -f compose.yaml -f compose.nginx128.yaml --profile break128 stop nginx128-broken 2>&1 | tail -1
