# Summary de3b51401329efe5

24 passed runs, 0 failed. Medians over rounds; ranges are min to max.

| rate | system | step | runs | p50 ms | p99 ms (range) | CPU ms per 1k req (range) | anon MB | other processes, cores (max) |
|---:|---|---|---:|---:|---|---|---:|---:|
| 1000 | nginx | tls | 3 | 0.397 | 1.21 (1.08 to 2.12) | 146 (137 to 165) | 6 | 0.11 |
| 1000 | nginx | auth | 3 | 0.448 | 1.65 (1.51 to 3.81) | 164 (157 to 169) | 6 | 0.11 |
| 1000 | nginx-broken | tls | 3 | 0.420 | 3.75 (1.14 to 63.09) | 162 (138 to 250) | 6 | 0.05 |
| 1000 | nginx-broken | auth | 3 | 0.399 | 1.10 (1.07 to 1.96) | 145 (141 to 153) | 6 | 0.06 |
| 2000 | nginx | tls | 3 | 0.431 | 3.78 (1.44 to 4.67) | 129 (107 to 136) | 6 | 0.07 |
| 2000 | nginx | auth | 3 | 0.354 | 3.13 (2.14 to 30.54) | 110 (110 to 140) | 6 | 0.04 |
| 2000 | nginx-broken | tls | 3 | 0.392 | 3.10 (2.40 to 4.12) | 125 (108 to 126) | 6 | 0.07 |
| 2000 | nginx-broken | auth | 3 | 0.359 | 1.83 (1.82 to 42.24) | 107 (106 to 201) | 6 | 0.04 |

## What each feature added (difference of cell medians)

| rate | system | feature | runs | CPU ms per 1k (range) | p50 ms | p99 ms |
|---:|---|---|---|---|---:|---:|
| 1000 | nginx | +auth | 3+3 | +19 (-8 to +32) | +0.051 | +0.44 |
| 2000 | nginx | +auth | 3+3 | -19 (-26 to +33) | -0.077 | -0.65 |
| 1000 | nginx-broken | +auth | 3+3 | -17 (-109 to +15) | -0.021 | -2.65 |
| 2000 | nginx-broken | +auth | 3+3 | -18 (-20 to +92) | -0.032 | -1.26 |
