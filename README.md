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
./scripts/00-setup.sh        # certs, .env, vegeta 12.13.0 (checksum checked), images
./scripts/02-up.sh           # fresh containers, the Tyk key, functional checks
python3 scripts/bench.py --rates 1000,2000 --rounds 3 --name main     # about 90 min on a quiet machine
python3 scripts/summarize.py results/main-<stamp>
python3 scripts/lag.py results/main-<stamp>                           # send lag (coordinated omission check)
./scripts/run-extras.sh      # limit semantics, Kong patch, keepalive break, max mode, Tyk on two cores
./scripts/break-keepalive-1.28.sh
```

## What each file does

| File | What it does |
| --- | --- |
| `compose.yaml` | Backend, nginx, Kong (DB-less), Tyk and its Redis. Host networking, each part pinned to one vCPU: load generator on 0, the proxy under test on 1, backend on 2, Redis on 3. |
| `backend/main.go` | A small JSON API. Counts the requests it serves per route and the new connections it accepts, and reports which headers reached it. |
| `nginx/nginx.conf`, `kong/kong.yml`, `tyk/` | The same ladder on each proxy: `/plain`, then TLS, then `/auth`, `/ratelimit`, `/transform`, each adding one feature to the one before. |
| `scripts/verify.py` | Exact checks before anything is timed: 200 with the key, 401 without it (403 for a wrong key on Tyk), the key stripped before the backend, the headers added and removed, and a 10/s limit that lets some of 50 concurrent requests through and refuses most. |
| `scripts/bench.py` | Fixed-rate runs with vegeta, at most 64 requests and connections in flight, in a shuffled order per round. Waits for the rest of the machine to be idle before each run. Fails a run on any non-200, a mismatch between the client's and the backend's counts, a proxy error log line (TLS handshake aborts by the client are counted, not failed), a starved load generator, fewer than 99% of the scheduled requests sent, or other processes using more than 0.3 cores during it. Failed cells are rerun, up to six rounds, until each has three passed runs. Every results directory is stamped with a hash of the configs, scripts and image IDs. |
| `scripts/summarize.py` | Medians and ranges per cell, and the cost of each feature as the difference between cell medians, with the widest range the runs allow. Refuses mixed stamps. |
| `scripts/lag.py` | How late vegeta sent each request against its schedule, and the latency with that lag added back. |
| `scripts/limit_semantics.py` | What "10 requests per second" lets through on each proxy, in bursts of 50 and at a steady 25/s. |
| `scripts/explain-kong-timer.sh`, `compose.explain.yaml` | Copies Kong 3.9.5's rate-limiting handler out of the image, changes one condition so the `local` policy counts inline instead of in a timer per request, and times both. The patched file is generated, not committed. |
| `scripts/break-keepalive.sh`, `scripts/break-keepalive-1.28.sh` | The break: an nginx config with the `proxy_set_header` inheritance mistake, on nginx 1.30.7 (where it no longer breaks anything) and on 1.28.3 (where it opens a backend connection per request). |
| `scripts/tyk-two-cores.sh`, `compose.tyk2.yaml` | Tyk's plain and full-ladder steps again with two cores. |

## Results

Every recorded run is in [`results/`](results/), including the failed and
discarded ones; see [`results/README.md`](results/README.md) for which commit
produced which directory. The article explains what the numbers mean.

## Limits

One machine, synthetic load, one small GET response, one hot key, one core per
proxy (two for the Tyk variant), and loopback networking, so no request crossed
a real network. The vCPUs are virtual, and the host may place two of them on
one physical core. The numbers compare the proxies with each other on this
machine; they are not capacity figures for your hardware.

## License

MIT
