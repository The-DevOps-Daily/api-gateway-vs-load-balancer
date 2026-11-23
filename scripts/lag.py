#!/usr/bin/env python3
"""How late did vegeta send each request?

bench.py caps vegeta at 64 requests in flight. When all 64 are waiting on a
slow proxy, the next request is sent late, and the time it spent waiting to be
sent is not in its latency (coordinated omission). This reads the raw results
of a run, compares each request's send time with its scheduled time
(first send + seq / rate), and reports the lag and the latency with the lag
added back.

usage: lag.py results/<name>-<stamp>    (needs results/raw/<name>-<stamp>/)
Writes results/<name>-<stamp>/lag.json.
"""
import json
import os
import statistics as stats
import subprocess
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VEGETA = os.path.join(ROOT, "tools", "vegeta")
out_dir = sys.argv[1].rstrip("/")
raw_dir = os.path.join(ROOT, "results", "raw", os.path.basename(out_dir))


def pct(v, q):
    k = max(0, min(len(v) - 1, int(-(-q * len(v) // 1)) - 1))
    return v[k]


def ts_ns(s):
    # RFC 3339 in UTC with up to nanoseconds, e.g. 2026-11-23T18:40:41.123456789Z
    if not s.endswith("Z"):
        raise ValueError(f"expected a UTC timestamp, got {s}")
    base, _, frac = s[:-1].partition(".")
    sec = datetime.strptime(base, "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc).timestamp()
    return int(sec) * 10**9 + int((frac or "0").ljust(9, "0")[:9])


runs = [json.loads(l) for l in open(os.path.join(out_dir, "runs.jsonl"))]
res = []
for r in runs:
    if not r["pass"] or not r["rate"]:
        continue
    path = os.path.join(raw_dir, f"r{r['round']}-{r['system']}-{r['step']}-{r['rate']}.bin")
    p = subprocess.run([VEGETA, "encode", "--to", "json", path], capture_output=True, text=True, check=True)
    rows = [json.loads(l) for l in p.stdout.splitlines()]
    rows.sort(key=lambda x: x["seq"])
    t0 = ts_ns(rows[0]["timestamp"])
    period = 1e9 / r["rate"]
    lag = sorted(max(0.0, ts_ns(x["timestamp"]) - (t0 + x["seq"] * period)) for x in rows)
    corrected = sorted(max(0.0, ts_ns(x["timestamp"]) - (t0 + x["seq"] * period)) + x["latency"] for x in rows)
    res.append({"round": r["round"], "system": r["system"], "step": r["step"], "rate": r["rate"],
                "lag_ms": {"p50": pct(lag, 0.5) / 1e6, "p99": pct(lag, 0.99) / 1e6, "max": lag[-1] / 1e6},
                "corrected_ms": {"p50": pct(corrected, 0.5) / 1e6, "p99": pct(corrected, 0.99) / 1e6},
                "measured_p99_ms": r["latency_ms"]["p99"]})
    print(f"{r['system']:>12} {r['step']:<9} {r['rate']:>5} r{r['round']} lag p99 {res[-1]['lag_ms']['p99']:7.2f} "
          f"max {res[-1]['lag_ms']['max']:7.2f} ms | p99 {r['latency_ms']['p99']:6.2f} -> corrected {res[-1]['corrected_ms']['p99']:6.2f} ms",
          flush=True)

cells = {}
for x in res:
    cells.setdefault((x["system"], x["step"], x["rate"]), []).append(x)
summary = [{"system": s, "step": st, "rate": rt, "n": len(v),
            "lag_p99_ms": stats.median(x["lag_ms"]["p99"] for x in v),
            "lag_max_ms": max(x["lag_ms"]["max"] for x in v),
            "p99_ms": stats.median(x["measured_p99_ms"] for x in v),
            "corrected_p50_ms": stats.median(x["corrected_ms"]["p50"] for x in v),
            "corrected_p99_ms": stats.median(x["corrected_ms"]["p99"] for x in v)}
           for (s, st, rt), v in sorted(cells.items())]
json.dump({"runs": res, "cells": summary}, open(os.path.join(out_dir, "lag.json"), "w"), indent=2)
