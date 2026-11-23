#!/usr/bin/env bash
# Why Kong's rate limit costs so much: for the local policy, Kong 3.9's
# rate-limiting handler counts each request in a new ngx.timer.at(0, ...)
# timer. This copies the handler out of the image, changes one condition so
# the local policy counts inline, and times both side by side.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p kong/patched results
docker run --rm --entrypoint cat kong:3.9.5 \
  /usr/local/share/lua/5.1/kong/plugins/rate-limiting/handler.lua > kong/patched/handler.orig.lua
old='  if conf.sync_rate ~= SYNC_RATE_REALTIME and conf.policy == "redis" then'
new='  if conf.policy == "local" or (conf.sync_rate ~= SYNC_RATE_REALTIME and conf.policy == "redis") then'
grep -qxF "$old" kong/patched/handler.orig.lua
python3 - "$old" "$new" <<'PY'
import sys
src = open("kong/patched/handler.orig.lua").read()
assert src.count(sys.argv[1]) == 1
open("kong/patched/handler.lua", "w").write(src.replace(sys.argv[1], sys.argv[2]))
PY
diff kong/patched/handler.orig.lua kong/patched/handler.lua > results/explain-kong-timer.diff || true
sha256sum kong/patched/handler.lua >> results/explain-kong-timer.diff

docker compose -f compose.yaml -f compose.explain.yaml --profile explain up -d kong-inline 2>&1 | tail -1
for i in $(seq 1 60); do curl -sk -o /dev/null https://127.0.0.1:18543/plain && break; sleep 1; done
curl -sk -o /dev/null https://127.0.0.1:18543/plain || { docker logs gwbench-kong-inline-1 2>&1 | tail -5; exit 1; }
python3 scripts/limit_semantics.py --systems kong,kong-inline --out results/limit-semantics-kong-inline.json
python3 scripts/bench.py --systems kong,kong-inline --steps auth,ratelimit --rates 1000,2000 \
  --rounds 3 --duration 30 --warmup 10 --name explain-kong-timer
docker compose -f compose.yaml -f compose.explain.yaml --profile explain stop kong-inline 2>&1 | tail -1
