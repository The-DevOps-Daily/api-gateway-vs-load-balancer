# Recorded results

Each directory is one `bench.py` invocation: `meta.json` (stamp, image IDs,
arguments, host), `runs.jsonl` (every run, passed and failed, with the reason),
and `summary.md` / `summary.json` from `scripts/summarize.py`. `lag.json` is
from `scripts/lag.py`. The raw vegeta files are not committed (2.4 GB for the
main run alone).

The stamp is a hash of the configs, scripts and image IDs at the time of the
run. The code changed between runs, so each directory matches a commit:

| Directory | What | Commit |
| --- | --- | --- |
| `main-b57582404be80918` | The main ladder, 1,000 and 2,000 requests/s, all proxies | a5463fd |
| `explain-kong-timer-de3b51401329efe5` | Kong stock vs rate-limit handler patched to count inline | 291541f |
| `break-keepalive-de3b51401329efe5` | nginx 1.30.7, correct vs broken `proxy_set_header` config | 291541f |
| `max-de3b51401329efe5` | As fast as 64 requests in flight go, every proxy and step | 291541f |
| `limit-semantics.json`, `limit-semantics-kong-inline.json` | What a 10/s limit lets through | 291541f |
| `break-keepalive-1.28-7e81865a8157dadd` | The broken config on nginx 1.28.3 | bf8b060 |
| `tyk-two-cores-93f5d68a8a9258be` | Tyk plain and full ladder with two cores | 431a4bc |

The `*.log` files are the console output of those runs. `summarize.py` and
`lag.py` are analysis only; their output here was produced with the latest
commit.

## Discarded

- `discarded/main-2b5a36dd71a1ba6c`, `main-run2.log`: an earlier main run,
  stopped and restarted after a harness fix (3 s pause after the warm-up, so
  Tyk's log lines about the warm-up client's dropped connections fall outside
  the measured window).
- `discarded/main-eeca50983dd4a08c`, `main-run3.log`: stopped and restarted to
  count TLS handshake aborts by the client separately instead of failing the
  run on them.
- Two attempts before those, and the smoke tests that found the connection-cap
  problem, were deleted when the harness was restarted and are not here. They
  ran while another job used one to two cores of the same machine.
- `discarded/tyk-two-cores-de3b51401329efe5-interrupted`: interrupted after six
  runs, when the stack was restarted by hand for the next test.
