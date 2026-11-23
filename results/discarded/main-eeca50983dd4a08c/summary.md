# Summary eeca50983dd4a08c

2 passed runs, 1 failed. Medians over rounds; ranges are min to max.

| rate | system | step | runs | p50 ms | p99 ms (range) | CPU ms per 1k req (range) | anon MB | other processes, cores (max) |
|---:|---|---|---:|---:|---|---|---:|---:|
| 1000 | kong | transform | 1 | 1.101 | 58.65 (58.65 to 58.65) | 803 (803 to 803) | 174 | 0.08 |
| 2000 | tyk | plain | 1 | 0.639 | 32.43 (32.43 to 32.43) | 295 (295 to 295) | 85 | -0.02 |

## What each feature added (difference of cell medians)

| rate | system | feature | runs | CPU ms per 1k (range) | p50 ms | p99 ms |
|---:|---|---|---|---|---:|---:|

## Failed runs (left out)

- round 1 tyk/auth at 2000/s: 3 error log lines, first: 2026/11/23 18:38:53 http: TLS handshake error from 127.0.0.1:57179: EOF
