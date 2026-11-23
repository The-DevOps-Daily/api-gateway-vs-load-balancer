# Summary de3b51401329efe5

6 passed runs, 0 failed. Medians over rounds; ranges are min to max.

| rate | system | step | runs | p50 ms | p99 ms (range) | CPU ms per 1k req (range) | anon MB | other processes, cores (max) |
|---:|---|---|---:|---:|---|---|---:|---:|
| 1000 | tyk | plain | 2 | 0.808 | 3.75 (3.10 to 4.41) | 557 (541 to 573) | 81 | 0.12 |
| 1000 | tyk | transform | 2 | 0.925 | 6.51 (4.26 to 8.76) | 709 (638 to 780) | 84 | 0.05 |
| 2000 | tyk | plain | 1 | 0.787 | 31.35 (31.35 to 31.35) | 471 (471 to 471) | 87 | 0.14 |
| 2000 | tyk | transform | 1 | 0.685 | 15.22 (15.22 to 15.22) | 513 (513 to 513) | 90 | 0.00 |

## What each feature added (difference of cell medians)

| rate | system | feature | runs | CPU ms per 1k (range) | p50 ms | p99 ms |
|---:|---|---|---|---|---:|---:|
