#!/usr/bin/env python3
"""Summarize one bench run directory into results/<dir>/summary.{json,md}.

Refuses a file with mixed or missing stamps. Failed runs are listed and left
out; the table shows how many passed runs each cell rests on. Feature costs
are differences between cell medians, with the widest range the runs allow.

usage: summarize.py results/<name>-<stamp>
"""
import json
import os
import statistics as st
import sys

sys.path.insert(0, os.path.dirname(__file__))
from targets import STEPS  # noqa: E402

d = sys.argv[1]
runs = [json.loads(l) for l in open(os.path.join(d, "runs.jsonl"))]
meta = json.load(open(os.path.join(d, "meta.json")))
stamps = {r.get("stamp") for r in runs}
if stamps != {meta["stamp"]}:
    sys.exit(f"refusing: stamps in runs.jsonl {stamps} do not match meta {meta['stamp']}")

failed = [r for r in runs if not r["pass"]]
ok = [r for r in runs if r["pass"]]


def total_cpu(r):
    return sum(r["cpu_ms_per_1k"].values())


def total_mem(r):
    return sum(m["anon_mb"] for m in r["mem"].values())


cells = {}
for r in ok:
    cells.setdefault((r["system"], r["step"], r["rate"]), []).append(r)

rows = []
for (system, step, rate), rs in sorted(cells.items(), key=lambda kv: (kv[0][2], kv[0][0], STEPS.index(kv[0][1]))):
    rows.append({
        "system": system, "step": step, "rate": rate, "n": len(rs),
        "p50_ms": st.median(r["latency_ms"]["p50"] for r in rs),
        "p99_ms": st.median(r["latency_ms"]["p99"] for r in rs),
        "p99_ms_range": [min(r["latency_ms"]["p99"] for r in rs), max(r["latency_ms"]["p99"] for r in rs)],
        "cpu_ms_per_1k": st.median(total_cpu(r) for r in rs),
        "cpu_ms_per_1k_range": [min(total_cpu(r) for r in rs), max(total_cpu(r) for r in rs)],
        "cpu_by_container": {c: st.median(r["cpu_ms_per_1k"][c] for r in rs) for c in rs[0]["cpu_ms_per_1k"]},
        "anon_mem_mb": st.median(total_mem(r) for r in rs),
        "foreign_cpu_max": max(r["foreign_cores_during"] for r in rs),
        "backend_new_conns_max": max(r["backend_new_conns"] for r in rs),
    })

# Per-feature cost: the difference between the medians of two cells (a step and
# the one below it, same system and rate). Runs are not paired: failed runs are
# refilled in later rounds, so a step's runs need not share rounds with the
# step below. The range is the widest the difference could be from the runs:
# (min of the step - max of the one below) to (max - min).
deltas = []
for system in sorted({r["system"] for r in ok}):
    for rate in sorted({r["rate"] for r in ok}):
        for i in range(1, len(STEPS)):
            a = cells.get((system, STEPS[i - 1], rate))
            b = cells.get((system, STEPS[i], rate))
            if not a or not b:
                continue
            ca, cb = [total_cpu(r) for r in a], [total_cpu(r) for r in b]
            deltas.append({
                "system": system, "rate": rate, "feature": STEPS[i], "runs": [len(a), len(b)],
                "cpu_ms_per_1k": st.median(cb) - st.median(ca),
                "cpu_range": [min(cb) - max(ca), max(cb) - min(ca)],
                "p50_ms": st.median(r["latency_ms"]["p50"] for r in b) - st.median(r["latency_ms"]["p50"] for r in a),
                "p99_ms": st.median(r["latency_ms"]["p99"] for r in b) - st.median(r["latency_ms"]["p99"] for r in a),
            })

out = {"stamp": meta["stamp"], "meta": meta, "rows": rows, "feature_deltas": deltas,
       "failed": [{k: r[k] for k in ("round", "system", "step", "rate", "fail_reasons")} for r in failed]}
json.dump(out, open(os.path.join(d, "summary.json"), "w"), indent=2)

md = [f"# Summary {meta['stamp']}", "",
      f"{len(ok)} passed runs, {len(failed)} failed. Medians over rounds; ranges are min to max.", "",
      "| rate | system | step | runs | p50 ms | p99 ms (range) | CPU ms per 1k req (range) | anon MB | other processes, cores (max) |",
      "|---:|---|---|---:|---:|---|---|---:|---:|"]
for r in rows:
    md.append(f"| {r['rate']} | {r['system']} | {r['step']} | {r['n']} | {r['p50_ms']:.3f} | "
              f"{r['p99_ms']:.2f} ({r['p99_ms_range'][0]:.2f} to {r['p99_ms_range'][1]:.2f}) | "
              f"{r['cpu_ms_per_1k']:.0f} ({r['cpu_ms_per_1k_range'][0]:.0f} to {r['cpu_ms_per_1k_range'][1]:.0f}) | "
              f"{r['anon_mem_mb']:.0f} | {r['foreign_cpu_max']:.2f} |")
md += ["", "## What each feature added (difference of cell medians)", "",
       "| rate | system | feature | runs | CPU ms per 1k (range) | p50 ms | p99 ms |", "|---:|---|---|---|---|---:|---:|"]
for x in deltas:
    md.append(f"| {x['rate']} | {x['system']} | +{x['feature']} | {x['runs'][0]}+{x['runs'][1]} | {x['cpu_ms_per_1k']:+.0f} "
              f"({x['cpu_range'][0]:+.0f} to {x['cpu_range'][1]:+.0f}) | {x['p50_ms']:+.3f} | {x['p99_ms']:+.2f} |")
if failed:
    md += ["", "## Failed runs (left out)", ""]
    for r in failed:
        md.append(f"- round {r['round']} {r['system']}/{r['step']} at {r['rate']}/s: {'; '.join(r['fail_reasons'])[:300]}")
open(os.path.join(d, "summary.md"), "w").write("\n".join(md) + "\n")
print("\n".join(md))
