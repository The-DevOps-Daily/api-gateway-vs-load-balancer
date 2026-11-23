# Summary 7e81865a8157dadd

12 passed runs, 0 failed. Medians over rounds; ranges are min to max.

| rate | system | step | runs | p50 ms | p99 ms (range) | CPU ms per 1k req (range) | anon MB | other processes, cores (max) |
|---:|---|---|---:|---:|---|---|---:|---:|
| 1000 | nginx128-broken | tls | 3 | 0.471 | 2.38 (1.33 to 2.55) | 167 (156 to 169) | 6 | -0.01 |
| 1000 | nginx128-broken | auth | 3 | 0.567 | 1.88 (1.59 to 2.11) | 244 (220 to 262) | 6 | 0.06 |
| 2000 | nginx128-broken | tls | 3 | 0.430 | 3.14 (1.45 to 4.24) | 127 (103 to 131) | 6 | 0.07 |
| 2000 | nginx128-broken | auth | 3 | 0.587 | 20.68 (3.11 to 34.59) | 213 (205 to 223) | 6 | 0.06 |

## What each feature added (difference of cell medians)

| rate | system | feature | runs | CPU ms per 1k (range) | p50 ms | p99 ms |
|---:|---|---|---|---|---:|---:|
| 1000 | nginx128-broken | +auth | 3+3 | +76 (+51 to +106) | +0.095 | -0.51 |
| 2000 | nginx128-broken | +auth | 3+3 | +86 (+74 to +121) | +0.158 | +17.53 |
