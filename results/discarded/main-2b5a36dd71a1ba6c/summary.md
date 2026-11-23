# Summary 2b5a36dd71a1ba6c

5 passed runs, 1 failed. Medians over rounds; ranges are min to max.

| rate | system | step | runs | p50 ms | p99 ms (range) | CPU ms per 1k req (range) | anon MB | other processes, cores (max) |
|---:|---|---|---:|---:|---|---|---:|---:|
| 1000 | kong | transform | 1 | 1.100 | 62.46 (62.46 to 62.46) | 801 (801 to 801) | 170 | 0.01 |
| 1000 | nginx | transform | 1 | 0.393 | 1.33 (1.33 to 1.33) | 142 (142 to 142) | 6 | -0.04 |
| 1000 | tyk | plain | 1 | 0.610 | 7.28 (7.28 to 7.28) | 373 (373 to 373) | 82 | 0.05 |
| 2000 | tyk | plain | 1 | 0.603 | 24.14 (24.14 to 24.14) | 276 (276 to 276) | 90 | -0.02 |
| 2000 | tyk | auth | 1 | 1.089 | 65.64 (65.64 to 65.64) | 392 (392 to 392) | 114 | -0.01 |

## What each feature added (difference of cell medians)

| rate | system | feature | runs | CPU ms per 1k (range) | p50 ms | p99 ms |
|---:|---|---|---|---|---:|---:|

## Failed runs (left out)

- round 1 tyk/ratelimit at 2000/s: 9 error log lines, first: 2026/11/23 18:34:21 http: TLS handshake error from 127.0.0.1:54235: read tcp 127.0.0.1:28443->127.0.0.1:54235: read: connection reset by peer
