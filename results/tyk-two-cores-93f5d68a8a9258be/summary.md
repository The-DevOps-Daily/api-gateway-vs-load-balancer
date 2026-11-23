# Summary 93f5d68a8a9258be

12 passed runs, 0 failed. Medians over rounds; ranges are min to max.

| rate | system | step | runs | p50 ms | p99 ms (range) | CPU ms per 1k req (range) | anon MB | other processes, cores (max) |
|---:|---|---|---:|---:|---|---|---:|---:|
| 1000 | tyk | plain | 3 | 0.815 | 2.72 (2.72 to 5.47) | 557 (514 to 595) | 77 | 0.06 |
| 1000 | tyk | transform | 3 | 0.904 | 6.41 (4.89 to 6.83) | 703 (633 to 720) | 79 | 0.05 |
| 2000 | tyk | plain | 3 | 0.578 | 2.32 (2.13 to 2.69) | 356 (347 to 357) | 79 | -0.05 |
| 2000 | tyk | transform | 3 | 0.941 | 36.95 (22.04 to 43.99) | 599 (523 to 622) | 91 | 0.09 |

## What each feature added (difference of cell medians)

| rate | system | feature | runs | CPU ms per 1k (range) | p50 ms | p99 ms |
|---:|---|---|---|---|---:|---:|
