#!/usr/bin/env python3
"""Fixed-rate runs over every system and step, in a shuffled order per round.

For each run: warm up, reset the backend counters, then send a fixed rate for
a fixed time with vegeta (open loop, so a slow proxy cannot slow the sender
down and hide its own latency). Records client latency, the proxy's CPU time
from its cgroup, its memory, the CPU used on its core by anything else, and
the backend's own count of requests and new connections.

A run fails, and is kept with the reason, when any request is not a 200,
when the backend served a different number of requests than the client got
back, when the proxy logged an error, or when the load generator was short
of CPU.

usage: bench.py --rates 1000,2000 --rounds 3 [--duration 30] [--warmup 10]
       bench.py --rates 0 --name max     # rate 0: as fast as 64 connections go
"""
import argparse
import fcntl
import hashlib
import json
import os
import random
import resource
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
from targets import BREAK_SYSTEMS, KEY, SYSTEMS, route_of  # noqa: E402

ALL = {**SYSTEMS, **BREAK_SYSTEMS}

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VEGETA = os.path.join(ROOT, "tools", "vegeta")
LOADGEN_CPU = "0"
PROXY_CPU = 1
# A fixed pool of keepalive connections, like a fleet of app servers with
# connection pools. Without a cap, vegeta opens a new connection (and a TLS
# handshake) whenever latency rises, and one hiccup snowballs into a collapse.
CONNS = 64

STAMPED = [
    "compose.yaml", "backend/main.go", "backend/Dockerfile", "nginx/nginx.conf",
    "nginx/nginx-broken-keepalive.conf", "kong/kong.yml", "tyk/tyk.conf",
    "scripts/targets.py", "scripts/bench.py", "scripts/verify.py", "scripts/01-tyk-key.sh",
] + sorted("tyk/apps/" + f for f in os.listdir(os.path.join(ROOT, "tyk/apps")))
IMAGES = ["gwbench-backend:local", "nginx:1.30.7-alpine", "kong:3.9.5",
          "tykio/tyk-gateway:v5.16.0", "redis:8.8.4-alpine"]


def sh(*cmd):
    return subprocess.run(cmd, check=True, capture_output=True, text=True).stdout.strip()


def stamp():
    h = hashlib.sha256()
    for f in STAMPED:
        h.update(f.encode())
        with open(os.path.join(ROOT, f), "rb") as fh:
            h.update(fh.read())
    images = {i: sh("docker", "image", "inspect", "-f", "{{.Id}}", i) for i in IMAGES}
    for i in IMAGES:
        h.update(images[i].encode())
    return h.hexdigest()[:16], images


def container_ids():
    out = {}
    for svc in ["backend", "nginx", "kong", "redis", "tyk", "nginx-broken"]:
        out[svc] = sh("docker", "compose", "-f", os.path.join(ROOT, "compose.yaml"), "ps", "-q", svc)
    return out


def cg(cid, f):
    with open(f"/sys/fs/cgroup/system.slice/docker-{cid}.scope/{f}") as fh:
        return fh.read()


def cpu_usec(cid):
    for line in cg(cid, "cpu.stat").splitlines():
        k, v = line.split()
        if k == "usage_usec":
            return int(v)


def mem(cid):
    stat = dict(l.split() for l in cg(cid, "memory.stat").splitlines())
    return {"current_mb": int(cg(cid, "memory.current")) / 2**20,
            "anon_mb": int(stat["anon"]) / 2**20}


def percpu():
    """Busy and steal jiffies per CPU from /proc/stat."""
    out = {}
    with open("/proc/stat") as fh:
        for line in fh:
            if line.startswith("cpu") and line[3].isdigit():
                p = line.split()
                vals = list(map(int, p[1:]))
                idle = vals[3] + vals[4]
                out[int(p[0][3:])] = {"busy": sum(vals[:8]) - idle, "steal": vals[7], "total": sum(vals[:8])}
    return out


def backend(path):
    return json.loads(sh("curl", "-fsS", f"http://127.0.0.1:9000{path}") or "null")


def vegeta(url, rate, duration, out_path):
    target = json.dumps({"method": "GET", "url": url, "header": {"apikey": [KEY]}}) + "\n"
    cmd = ["taskset", "-c", LOADGEN_CPU, VEGETA, "attack", "-format=json", f"-rate={rate}",
           f"-duration={duration}s", "-http2=false", "-keepalive=true",
           f"-workers={CONNS}", f"-max-workers={CONNS}", f"-connections={CONNS}",
           f"-max-connections={CONNS}", "-timeout=10s",
           f"-root-certs={os.path.join(ROOT, 'certs', 'server.crt')}", f"-output={out_path}"]
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    t0 = time.time()
    subprocess.run(cmd, input=target, text=True, check=True)
    wall = time.time() - t0
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    cpu = (after.ru_utime - before.ru_utime) + (after.ru_stime - before.ru_stime)
    return wall, cpu


def decode(bin_path):
    """Latency (ns) and status of every request, from vegeta's own records."""
    p = subprocess.run([VEGETA, "encode", "--to", "json", bin_path], check=True,
                       capture_output=True, text=True)
    lat, codes, errors = [], {}, 0
    for line in p.stdout.splitlines():
        r = json.loads(line)
        codes[r["code"]] = codes.get(r["code"], 0) + 1
        if r["error"]:
            errors += 1
        lat.append(r["latency"])
    return lat, codes, errors


def pct(sorted_vals, q):
    # Nearest-rank percentile.
    if not sorted_vals:
        return None
    k = max(0, min(len(sorted_vals) - 1, int(-(-q * len(sorted_vals) // 1)) - 1))
    return sorted_vals[k]


def error_lines(container, since):
    logs = subprocess.run(["docker", "logs", "--since", since, container],
                          capture_output=True, text=True)
    text = logs.stdout + logs.stderr
    bad = [l for l in text.splitlines()
           if any(w in l.lower() for w in ("error", "[crit]", "[alert]", "upstream", "timeout"))]
    return bad


def ours_usec(ids):
    return sum(cpu_usec(i) for i in ids.values() if i)


def host_busy_s():
    hz = os.sysconf("SC_CLK_TCK")
    return sum(v["busy"] for v in percpu().values()) / hz


def wait_for_quiet(ids, args):
    """The box is shared. Start a run only when everything that is not ours
    has used less than --quiet cores over a 5 s sample."""
    waited = 0
    while True:
        h0, o0 = host_busy_s(), ours_usec(ids)
        time.sleep(5)
        foreign = (host_busy_s() - h0 - (ours_usec(ids) - o0) / 1e6) / 5
        if foreign <= args.quiet or waited >= args.max_wait:
            return round(foreign, 3), waited
        waited += 5


def one_run(system, step, url, rate, args, ids, raw_dir, round_no):
    containers = ALL[system]["containers"]
    route = route_of(url)
    pre_foreign, waited = wait_for_quiet(ids, args)
    # Warm-up at the same rate, not timed.
    vegeta(url, rate, args.warmup, os.path.join(raw_dir, "warmup.bin"))
    # When the warm-up client exits, Tyk logs "TLS handshake error ... reset by
    # peer" for the connections it drops, up to a second later. Let those land
    # before the window whose logs are checked.
    time.sleep(3)
    backend("/__reset")
    since = f"{time.time():.3f}"
    cpu0 = {c: cpu_usec(ids[c]) for c in containers}
    be0 = cpu_usec(ids["backend"])
    all0, host0 = ours_usec(ids), host_busy_s()
    pc0 = percpu()
    bin_path = os.path.join(raw_dir, f"r{round_no}-{system}-{step}-{rate}.bin")
    wall, gen_cpu = vegeta(url, rate, args.duration, bin_path)
    cpu1 = {c: cpu_usec(ids[c]) for c in containers}
    be1 = cpu_usec(ids["backend"])
    all1, host1 = ours_usec(ids), host_busy_s()
    pc1 = percpu()
    until = f"{time.time():.3f}"
    host_foreign = (host1 - host0 - (all1 - all0) / 1e6 - gen_cpu) / wall
    counts = backend("/__count")
    lat, codes, errors = decode(bin_path)
    lat.sort()
    n = len(lat)
    ok = codes.get(200, 0)

    proxy_cpu_s = {c: (cpu1[c] - cpu0[c]) / 1e6 for c in containers}
    core = {k: {m: pc1[k][m] - pc0[k][m] for m in ("busy", "steal", "total")} for k in pc1}
    hz = os.sysconf("SC_CLK_TCK")
    own_on_core = proxy_cpu_s[containers[0]] if system != "direct" else 0
    foreign_on_proxy_core = max(0.0, core[PROXY_CPU]["busy"] / hz - own_on_core)

    reasons, bound = [], []
    if host_foreign > args.max_foreign:
        reasons.append(f"contended: other processes used {host_foreign:.2f} cores during the run")
    if rate and n < 0.99 * rate * args.duration:
        reasons.append(f"could not sustain {rate}/s: sent {n} of {rate * args.duration}")
    if ok != n or errors:
        reasons.append(f"non-200 or errors: {codes}, errors={errors}")
    if counts.get(route, 0) != ok:
        reasons.append(f"backend served {counts.get(route, 0)}, client got {ok} 200s")
    if gen_cpu / wall > 0.85:
        msg = f"load generator used {gen_cpu / wall:.2f} of its core"
        # At a fixed rate a starved sender means bad timing. In max mode it
        # means the number is a floor for the proxy, not its ceiling.
        (bound if rate == 0 else reasons).append(msg)
    if rate == 0 and system != "direct" and (be1 - be0) / 1e6 / wall > 0.85:
        bound.append("backend core saturated")
    handshake_aborts = 0
    if system != "direct":
        bad = []
        for c in containers:
            bad += error_lines(ids[c], since)
        # Go's TLS server logs a client that hangs up mid-handshake. That is the
        # client dropping a connection it was opening, not a failed request (the
        # counts above already prove every request), so it is counted, not failed.
        aborts = [l for l in bad if "TLS handshake error" in l and ("EOF" in l or "reset by peer" in l)]
        handshake_aborts = len(aborts)
        bad = [l for l in bad if l not in aborts]
        if bad:
            reasons.append(f"{len(bad)} error log lines, first: {bad[0][:200]}")

    rec = {
        "round": round_no, "system": system, "step": step, "rate": rate, "url": url,
        "window": [since, until], "waited_for_quiet_s": waited,
        "foreign_cores_before": pre_foreign, "foreign_cores_during": round(host_foreign, 3),
        "requests": n, "ok": ok, "codes": codes, "errors": errors,
        "wall_s": round(wall, 3),
        "throughput_rps": round(n / args.duration, 1),
        "backend_cpu_frac": round((be1 - be0) / 1e6 / wall, 3),
        "bound_by": bound,
        "latency_ms": {q: pct(lat, v) / 1e6 for q, v in
                       (("p50", 0.50), ("p90", 0.90), ("p99", 0.99), ("p999", 0.999), ("max", 1.0))},
        "mean_ms": sum(lat) / n / 1e6 if n else None,
        "cpu_s": proxy_cpu_s,
        "cpu_ms_per_1k": {c: proxy_cpu_s[c] * 1000 / (n / 1000) for c in containers} if n else None,
        "mem": {c: mem(ids[c]) for c in containers},
        "backend_new_conns": counts.get("__new_conns"),
        "tls_handshake_aborts_logged": handshake_aborts,
        "loadgen_cpu_frac": round(gen_cpu / wall, 3),
        "foreign_cpu_on_proxy_core_frac": round(foreign_on_proxy_core / wall, 3),
        "steal_frac_all_cores": round(sum(c["steal"] for c in core.values()) / max(1, sum(c["total"] for c in core.values())), 4),
        "host_busy_frac": {k: round(v["busy"] / max(1, v["total"]), 3) for k, v in core.items()},
        "loadavg": open("/proc/loadavg").read().split()[:3],
        "pass": not reasons, "fail_reasons": reasons,
    }
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rates", default="1000,3000")
    ap.add_argument("--rounds", type=int, default=3, help="passed runs wanted per cell")
    ap.add_argument("--max-rounds", type=int, default=6)
    ap.add_argument("--quiet", type=float, default=0.15, help="max foreign cores before a run")
    ap.add_argument("--max-foreign", type=float, default=0.3, help="max foreign cores during a run")
    ap.add_argument("--max-wait", type=int, default=3600)
    ap.add_argument("--duration", type=int, default=30)
    ap.add_argument("--warmup", type=int, default=10)
    ap.add_argument("--systems", default=",".join(SYSTEMS))
    ap.add_argument("--steps", default="", help="comma list; default all")
    ap.add_argument("--seed", type=int, default=66)
    ap.add_argument("--name", default="main")
    args = ap.parse_args()

    st, images = stamp()
    out_dir = os.path.join(ROOT, "results", f"{args.name}-{st}")
    raw_dir = os.path.join(ROOT, "results", "raw", f"{args.name}-{st}")
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(raw_dir, exist_ok=True)
    lock = open(os.path.join(out_dir, ".lock"), "w")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        sys.exit("another bench run is writing to this results directory")

    if subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "verify.py")],
                      capture_output=True).returncode != 0:
        sys.exit("verify.py failed: fix the stack before timing it")

    ids = container_ids()
    meta = {"stamp": st, "images": images, "args": vars(args),
            "host": {"nproc": os.cpu_count(), "kernel": os.uname().release,
                     "cpu": next(l.split(":", 1)[1].strip() for l in open("/proc/cpuinfo") if l.startswith("model name"))},
            "started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    with open(os.path.join(out_dir, "meta.json"), "w") as fh:
        json.dump(meta, fh, indent=2)

    rates = [int(r) for r in args.rates.split(",")]
    systems = args.systems.split(",")
    jobs = [(s, step, url, rate) for s in systems for step, url in ALL[s]["steps"].items() for rate in rates]
    if args.steps:
        jobs = [j for j in jobs if j[1] in args.steps.split(",")]
    rng = random.Random(args.seed)
    runs_path = os.path.join(out_dir, "runs.jsonl")
    passed = {}
    for rnd in range(1, args.max_rounds + 1):
        # Every round runs the cells that still lack --rounds passed runs, in a
        # new shuffled order, so a contended run is replaced, not averaged in.
        order = [j for j in jobs if passed.get(j, 0) < args.rounds]
        if not order:
            break
        rng.shuffle(order)
        for i, (s, step, url, rate) in enumerate(order, 1):
            rec = one_run(s, step, url, rate, args, ids, raw_dir, rnd)
            rec["stamp"] = st
            if rec["pass"]:
                passed[(s, step, url, rate)] = passed.get((s, step, url, rate), 0) + 1
            with open(runs_path, "a") as fh:
                fh.write(json.dumps(rec) + "\n")
            lm = rec["latency_ms"]
            cpu = rec["cpu_ms_per_1k"]
            print(f"r{rnd} {i:>2}/{len(order)} {s:>6} {step:<9} {rate:>5}/s {rec['throughput_rps']:>7.0f} done "
                  f"p50 {lm['p50']:.3f} p99 {lm['p99']:.3f} ms "
                  f"cpu/1k {', '.join(f'{k} {v:.0f}ms' for k, v in cpu.items())} "
                  f"foreign {rec['foreign_cores_during']:.2f} (waited {rec['waited_for_quiet_s']}s) "
                  f"{'ok' if rec['pass'] else 'FAIL ' + '; '.join(rec['fail_reasons'])}"
                  f"{' bound: ' + ', '.join(rec['bound_by']) if rec['bound_by'] else ''}", flush=True)
    os.remove(os.path.join(raw_dir, "warmup.bin"))


if __name__ == "__main__":
    main()
