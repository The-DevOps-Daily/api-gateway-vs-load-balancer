#!/usr/bin/env bash
# The break: nginx with the proxy_set_header inheritance mistake (see
# nginx/nginx-broken-keepalive.conf). Every response is still correct and
# verify.py would pass, but the backend sees a new connection per request.
# The bench records backend_new_conns, which is how this was caught.
set -euo pipefail
cd "$(dirname "$0")/.."
docker compose --profile break up -d nginx-broken 2>&1 | tail -1
until curl -sk -o /dev/null https://127.0.0.1:8453/plain; do sleep 1; done
python3 scripts/bench.py --systems nginx,nginx-broken --steps tls,auth --rates 1000,2000 --rounds 3 \
  --duration 30 --warmup 10 --name break-keepalive
docker compose --profile break stop nginx-broken 2>&1 | tail -1
