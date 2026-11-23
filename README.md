# api-gateway-vs-load-balancer

What does an API gateway cost per request, compared with plain nginx doing the
same job? The same small backend sits behind nginx 1.30, Kong Gateway OSS 3.9
and Tyk Gateway OSS 5.16, and the same features are turned on one at a time:
TLS, an API key check, a per-key rate limit, and a header transform. Each step
is timed at a fixed request rate, with the proxy's CPU time read from its
cgroup.

Companion to the DevOps Daily article
[API Gateway or Load Balancer? What Each Gateway Feature Costs, Measured](https://devops-daily.com/posts/api-gateway-vs-load-balancer-what-it-costs).

## Run it

You need Docker with Compose, Python 3.10 or newer, `curl`, `openssl` and
`taskset`, on a Linux x86_64 machine with at least 4 CPUs and cgroup v2. The
recorded runs used a 4 vCPU DigitalOcean droplet (Ubuntu 24.04).

```bash
./scripts/00-setup.sh        # certs, .env, vegeta 12.13.0 (checksum checked), backend image
./scripts/02-up.sh           # fresh containers, the Tyk key, functional checks
python3 scripts/bench.py --rates 1000,2000 --rounds 3 --name main     # about 90 min
python3 scripts/summarize.py results/main-<stamp>
python3 scripts/bench.py --rates 0 --rounds 3 --duration 15 --warmup 5 --name max
python3 scripts/limit_semantics.py
./scripts/break-keepalive.sh
```

## What each file does

| File | What it does |
| --- | --- |
| `compose.yaml` | Backend, nginx, Kong (DB-less), Tyk and its Redis. Host networking, one core each: load generator on core 0, the proxy under test on core 1, backend on core 2, Redis on core 3. |
| `backend/main.go` | A small JSON API. Counts the requests it serves per route and the new connections it accepts, and reports which headers reached it. |
| `nginx/nginx.conf`, `kong/kong.yml`, `tyk/` | The same ladder on each proxy: `/plain`, then TLS, then `/auth`, `/ratelimit`, `/transform`, each adding one feature to the one before. |
| `scripts/verify.py` | Exact checks before anything is timed: 200 with the key, 401 without it, the key stripped before the backend, the headers added and removed, and a 10/s limit that refuses a 50-request burst. |
| `scripts/bench.py` | Fixed-rate runs with vegeta over 64 keepalive connections, shuffled per round. Waits for the rest of the machine to be idle before each run, and fails a run on any non-200, a mismatch between the client's and the backend's counts, a proxy error log line, a starved load generator, or other processes using more than 0.3 cores during it. Failed cells are rerun until each has three passed runs. Every results file is stamped with a hash of the configs, scripts and image IDs. |
| `scripts/summarize.py` | Medians and ranges per cell, and the cost of each feature as the median of paired differences. Refuses mixed stamps. |
| `scripts/limit_semantics.py` | What "10 requests per second" lets through on each proxy, in bursts and at a steady 25/s. |
| `scripts/break-keepalive.sh` | The break: nginx with one inherited-header mistake. Every response is still correct, so `verify.py` passes, but the backend sees a new connection for every request. |

## Results

See [`results/`](results/) for every recorded run and its summary, and the
article for what they mean.

## Limits

One machine, synthetic load, one small response body, one core per proxy, and
loopback networking, so there is no network latency in any number here. The
numbers compare proxies with each other on this machine; they are not
capacity figures for your hardware.

## License

MIT
