#!/usr/bin/env python3
"""Check that every step does what it claims before anything is timed.

Each check needs an exact status and exact headers. A benchmark of an auth
step that lets every request through, or a rate limit that never refuses,
would measure nothing, so the bench refuses to run until this passes.
"""
import concurrent.futures as cf
import http.client
import json
import os
import ssl
import sys
import time
import urllib.parse

sys.path.insert(0, os.path.dirname(__file__))
from targets import KEY, STEPS, SYSTEMS, route_of  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CTX = ssl.create_default_context(cafile=os.path.join(ROOT, "certs", "server.crt"))

# Status for a request with a wrong key. Tyk answers 403, the others 401.
WRONG_KEY_STATUS = {"nginx": 401, "kong": 401, "tyk": 403}


def get(url, key=KEY):
    u = urllib.parse.urlsplit(url)
    if u.scheme == "https":
        c = http.client.HTTPSConnection(u.hostname, u.port, context=CTX, timeout=5)
    else:
        c = http.client.HTTPConnection(u.hostname, u.port, timeout=5)
    headers = {"apikey": key} if key else {}
    c.request("GET", u.path, headers=headers)
    r = c.getresponse()
    body = r.read()
    hdrs = {k.lower(): v for k, v in r.getheaders()}
    c.close()
    return r.status, hdrs, body


def backend(path):
    c = http.client.HTTPConnection("127.0.0.1", 9000, timeout=5)
    c.request("GET", path)
    r = c.getresponse()
    body = r.read()
    c.close()
    return json.loads(body) if body else None


def main():
    failures = []

    def check(cond, msg):
        print(("ok   " if cond else "FAIL ") + msg)
        if not cond:
            failures.append(msg)

    for name, sysdef in SYSTEMS.items():
        for step, url in sysdef["steps"].items():
            label = f"{name}/{step}"
            status, hdrs, body = get(url)
            check(status == 200, f"{label}: valid key gives 200 (got {status})")
            if status != 200:
                continue
            data = json.loads(body)
            check(data.get("route") == route_of(url), f"{label}: backend saw route {route_of(url)}")
            i = STEPS.index(step)
            has_auth = i >= STEPS.index("auth")
            is_tx = step == "transform"
            check(data["api_key_forwarded"] == (not has_auth),
                  f"{label}: key forwarded to backend = {not has_auth}")
            check(("x-internal-debug" in hdrs) == (not is_tx),
                  f"{label}: X-Internal-Debug present = {not is_tx}")
            check((data["tag"] == "gw-bench") == is_tx, f"{label}: X-Request-Tag added = {is_tx}")
            check(("x-gateway" in hdrs) == is_tx, f"{label}: X-Gateway added = {is_tx}")
            if has_auth:
                s, _, _ = get(url, key=None)
                check(s == 401, f"{label}: no key gives 401 (got {s})")
                s, _, _ = get(url, key="wrong-key")
                exp = WRONG_KEY_STATUS[name]
                check(s == exp, f"{label}: wrong key gives {exp} (got {s})")

        if "rlcheck" in sysdef:
            url = sysdef["rlcheck"]
            time.sleep(2)  # let a previous run's burst drain from the limiter
            backend("/__reset")
            with cf.ThreadPoolExecutor(50) as ex:
                codes = list(ex.map(lambda _: get(url)[0], range(50)))
            ok = codes.count(200)
            limited = codes.count(429)
            served = (backend("/__count") or {}).get("rlcheck", 0)
            check(ok + limited == 50, f"{name}/rlcheck: only 200 or 429 in a 50-request burst ({sorted(set(codes))})")
            check(1 <= ok <= 25 and limited >= 25, f"{name}/rlcheck: limit of 10/s refuses most of the burst ({ok} passed, {limited} refused)")
            check(served == ok, f"{name}/rlcheck: backend served exactly the {ok} passed requests (saw {served})")

    print()
    if failures:
        print(f"{len(failures)} check(s) failed")
        sys.exit(1)
    print("all checks passed")


if __name__ == "__main__":
    main()
