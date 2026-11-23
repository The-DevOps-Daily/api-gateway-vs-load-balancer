#!/usr/bin/env bash
# The break: nginx with the proxy_set_header inheritance mistake (see
# nginx/nginx-broken-keepalive.conf), on nginx 1.30.7 next to the correct
# config. The bench records backend_new_conns for every run. On 1.30 the
# broken config keeps its upstream connections; break-keepalive-1.28.sh shows
# the same file on 1.28, where it does not.
set -euo pipefail
cd "$(dirname "$0")/.."
docker compose --profile break up -d nginx-broken 2>&1 | tail -1
for i in $(seq 1 60); do curl -sk -o /dev/null https://127.0.0.1:8453/plain && break; sleep 1; done
python3 scripts/bench.py --systems nginx,nginx-broken --steps tls,auth --rates 1000,2000 --rounds 3 \
  --duration 30 --warmup 10 --name break-keepalive
docker compose --profile break stop nginx-broken 2>&1 | tail -1
