"""The ladder: the same five steps on every proxy, plus the backend on its own.

plain      HTTP, proxy only
tls        + TLS 1.3 from the client (keepalive, so mostly record encryption)
auth       + API key check, key stripped before the backend
ratelimit  + per-key rate limit (set far above the test rate: bookkeeping only)
transform  + add a request header, strip a response header, add a response header
"""

KEY = "bench-key-1"
STEPS = ["plain", "tls", "auth", "ratelimit", "transform"]

SYSTEMS = {
    "direct": {
        "containers": ["backend"],
        "steps": {"plain": "http://127.0.0.1:9000/plain"},
    },
    "nginx": {
        "containers": ["nginx"],
        "steps": {
            "plain": "http://127.0.0.1:8080/plain",
            "tls": "https://127.0.0.1:8443/plain",
            "auth": "https://127.0.0.1:8443/auth",
            "ratelimit": "https://127.0.0.1:8443/ratelimit",
            "transform": "https://127.0.0.1:8443/transform",
        },
        "rlcheck": "https://127.0.0.1:8443/rlcheck",
    },
    "kong": {
        "containers": ["kong"],
        "steps": {
            "plain": "http://127.0.0.1:18000/plain",
            "tls": "https://127.0.0.1:18443/plain",
            "auth": "https://127.0.0.1:18443/auth",
            "ratelimit": "https://127.0.0.1:18443/ratelimit",
            "transform": "https://127.0.0.1:18443/transform",
        },
        "rlcheck": "https://127.0.0.1:18443/rlcheck",
    },
    "tyk": {
        # Tyk keeps keys and rate-limit state in Redis, so Redis is part of its cost.
        "containers": ["tyk", "redis"],
        "steps": {
            "plain": "http://127.0.0.1:28080/plain",
            "tls": "https://127.0.0.1:28443/tls",
            "auth": "https://127.0.0.1:28443/auth",
            "ratelimit": "https://127.0.0.1:28443/ratelimit",
            "transform": "https://127.0.0.1:28443/transform",
        },
        "rlcheck": "https://127.0.0.1:28443/rlcheck",
    },
}

# Started only by scripts/break-keepalive.sh (compose profile "break").
BREAK_SYSTEMS = {
    "nginx-broken": {
        "containers": ["nginx-broken"],
        "steps": {
            "tls": "https://127.0.0.1:8453/plain",
            "auth": "https://127.0.0.1:8453/auth",
        },
    },
}


def route_of(url):
    return url.split("/", 3)[3].split("/")[0]
