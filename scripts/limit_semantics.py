#!/usr/bin/env python3
"""What "10 requests per second" lets through on each proxy.

The /rlcheck route has a limit of 10 per second on all three. Two tests:
  burst:  50 requests at once, five times, 3 s apart
  steady: 25 requests per second for 20 s (vegeta)
Writes results/limit-semantics.json (or --out).
"""
import argparse
import concurrent.futures as cf
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
from targets import BREAK_SYSTEMS, KEY, SYSTEMS  # noqa: E402
from verify import backend, get  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VEGETA = os.path.join(ROOT, "tools", "vegeta")

ap = argparse.ArgumentParser()
ap.add_argument("--systems", default="nginx,kong,tyk")
ap.add_argument("--out", default=os.path.join(ROOT, "results", "limit-semantics.json"))
args = ap.parse_args()
ALL = {**SYSTEMS, **BREAK_SYSTEMS}

out = {}
for name in args.systems.split(","):
    sysdef = ALL[name]
    url = sysdef["rlcheck"]
    time.sleep(3)
    bursts = []
    for _ in range(5):
        backend("/__reset")
        with cf.ThreadPoolExecutor(50) as ex:
            codes = list(ex.map(lambda _: get(url)[0], range(50)))
        bursts.append({"passed": codes.count(200), "refused": codes.count(429),
                       "other": len(codes) - codes.count(200) - codes.count(429),
                       "backend_served": backend("/__count").get("rlcheck", 0)})
        time.sleep(3)

    backend("/__reset")
    target = json.dumps({"method": "GET", "url": url, "header": {"apikey": [KEY]}}) + "\n"
    attack = subprocess.run([VEGETA, "attack", "-format=json", "-rate=25", "-duration=20s",
                             "-http2=false", f"-root-certs={os.path.join(ROOT, 'certs', 'server.crt')}"],
                            input=target.encode(), capture_output=True, check=True)
    rep = subprocess.run([VEGETA, "report", "-type=json"], input=attack.stdout,
                         capture_output=True, check=True)
    r = json.loads(rep.stdout)
    steady = {"sent": r["requests"], "status_codes": r["status_codes"],
              "passed_per_s": r["status_codes"].get("200", 0) / 20,
              "backend_served": backend("/__count").get("rlcheck", 0)}
    out[name] = {"burst_of_50": bursts, "steady_25_per_s_for_20s": steady}
    print(name, "bursts passed:", [b["passed"] for b in bursts],
          "| steady:", steady["status_codes"], f"= {steady['passed_per_s']:.2f}/s passed")

json.dump(out, open(args.out, "w"), indent=2)
