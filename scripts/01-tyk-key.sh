#!/usr/bin/env bash
# Create the bench API key in Tyk. nginx and Kong read theirs from config files;
# Tyk keeps keys in Redis and takes them through its control API.
set -euo pipefail
cd "$(dirname "$0")/.."
hdr=$(mktemp)
trap 'rm -f "$hdr"' EXIT
# The secret goes in a header file, not on the command line where ps can see it.
printf 'x-tyk-authorization: %s\n' "$(grep '^TYK_GW_SECRET=' .env | cut -d= -f2-)" > "$hdr"

apis=""
for a in plain tls auth ratelimit transform rlcheck; do
  apis="$apis\"$a\":{\"api_id\":\"$a\",\"api_name\":\"$a\",\"versions\":[\"Default\"]},"
done
body="{\"org_id\":\"bench\",\"rate\":100000,\"per\":1,\"allowance\":100000,\"quota_max\":-1,\"expires\":0,\"access_rights\":{${apis%,}}}"

curl -fsS -H @"$hdr" -H 'Content-Type: application/json' \
  -X POST "http://127.0.0.1:28080/tyk/keys/bench-key-1" -d "$body"
echo
