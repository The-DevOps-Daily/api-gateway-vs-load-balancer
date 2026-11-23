# Summary de3b51401329efe5

48 passed runs, 0 failed. Medians over rounds; ranges are min to max.

| rate | system | step | runs | p50 ms | p99 ms (range) | CPU ms per 1k req (range) | anon MB | other processes, cores (max) |
|---:|---|---|---:|---:|---|---|---:|---:|
| 0 | direct | plain | 3 | 2.104 | 6.44 (6.39 to 7.50) | 43 (39 to 50) | 8 | 0.05 |
| 0 | kong | plain | 3 | 4.879 | 13.89 (11.96 to 15.40) | 89 (81 to 92) | 175 | 0.04 |
| 0 | kong | tls | 3 | 7.338 | 22.00 (17.38 to 22.87) | 126 (101 to 127) | 176 | 0.03 |
| 0 | kong | auth | 3 | 9.243 | 29.12 (20.15 to 29.75) | 160 (118 to 174) | 175 | 0.03 |
| 0 | kong | ratelimit | 3 | 18.888 | 74.22 (60.24 to 87.12) | 340 (247 to 373) | 175 | 0.07 |
| 0 | kong | transform | 3 | 17.357 | 72.89 (69.73 to 83.60) | 324 (289 to 380) | 175 | 0.03 |
| 0 | nginx | plain | 3 | 2.481 | 7.53 (7.36 to 7.80) | 45 (45 to 47) | 6 | 0.09 |
| 0 | nginx | tls | 3 | 4.086 | 27.19 (23.32 to 47.88) | 152 (92 to 173) | 6 | 0.10 |
| 0 | nginx | auth | 3 | 4.191 | 27.09 (22.21 to 34.29) | 142 (90 to 186) | 6 | 0.06 |
| 0 | nginx | ratelimit | 3 | 4.395 | 25.15 (21.39 to 29.66) | 155 (127 to 164) | 6 | 0.07 |
| 0 | nginx | transform | 3 | 3.818 | 29.27 (20.33 to 29.44) | 159 (90 to 171) | 6 | 0.06 |
| 0 | tyk | plain | 3 | 11.927 | 47.79 (36.63 to 54.02) | 245 (192 to 292) | 103 | 0.09 |
| 0 | tyk | tls | 3 | 12.007 | 48.38 (40.53 to 53.15) | 248 (204 to 264) | 100 | 0.04 |
| 0 | tyk | auth | 3 | 20.148 | 57.83 (55.77 to 63.01) | 338 (321 to 368) | 117 | 0.06 |
| 0 | tyk | ratelimit | 3 | 20.133 | 56.90 (55.84 to 81.62) | 339 (327 to 436) | 115 | 0.06 |
| 0 | tyk | transform | 3 | 21.220 | 76.55 (72.13 to 79.56) | 430 (407 to 450) | 118 | 0.05 |

## What each feature added (difference of cell medians)

| rate | system | feature | runs | CPU ms per 1k (range) | p50 ms | p99 ms |
|---:|---|---|---|---|---:|---:|
| 0 | kong | +tls | 3+3 | +37 (+9 to +47) | +2.459 | +8.12 |
| 0 | kong | +auth | 3+3 | +34 (-10 to +72) | +1.906 | +7.11 |
| 0 | kong | +ratelimit | 3+3 | +179 (+73 to +255) | +9.645 | +45.10 |
| 0 | kong | +transform | 3+3 | -16 (-84 to +133) | -1.531 | -1.33 |
| 0 | nginx | +tls | 3+3 | +106 (+46 to +127) | +1.604 | +19.66 |
| 0 | nginx | +auth | 3+3 | -9 (-83 to +94) | +0.105 | -0.10 |
| 0 | nginx | +ratelimit | 3+3 | +13 (-59 to +74) | +0.204 | -1.94 |
| 0 | nginx | +transform | 3+3 | +4 (-74 to +43) | -0.577 | +4.12 |
| 0 | tyk | +tls | 3+3 | +3 (-88 to +72) | +0.081 | +0.59 |
| 0 | tyk | +auth | 3+3 | +91 (+57 to +163) | +8.140 | +9.46 |
| 0 | tyk | +ratelimit | 3+3 | +0 (-41 to +115) | -0.015 | -0.93 |
| 0 | tyk | +transform | 3+3 | +92 (-29 to +123) | +1.087 | +19.65 |
