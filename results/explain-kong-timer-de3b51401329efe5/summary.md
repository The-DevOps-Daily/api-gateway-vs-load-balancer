# Summary de3b51401329efe5

24 passed runs, 0 failed. Medians over rounds; ranges are min to max.

| rate | system | step | runs | p50 ms | p99 ms (range) | CPU ms per 1k req (range) | anon MB | other processes, cores (max) |
|---:|---|---|---:|---:|---|---|---:|---:|
| 1000 | kong | auth | 3 | 0.593 | 2.53 (2.50 to 3.48) | 310 (306 to 340) | 170 | 0.11 |
| 1000 | kong | ratelimit | 3 | 1.074 | 19.28 (9.26 to 28.75) | 739 (712 to 741) | 171 | 0.12 |
| 1000 | kong-inline | auth | 3 | 0.590 | 2.66 (2.13 to 4.19) | 308 (287 to 339) | 169 | 0.12 |
| 1000 | kong-inline | ratelimit | 3 | 0.594 | 3.66 (2.75 to 18.60) | 326 (317 to 376) | 169 | -0.08 |
| 2000 | kong | auth | 3 | 0.543 | 3.07 (3.07 to 11.27) | 210 (210 to 234) | 171 | 0.02 |
| 2000 | kong | ratelimit | 3 | 1.583 | 46.79 (43.92 to 66.55) | 480 (479 to 482) | 171 | 0.08 |
| 2000 | kong-inline | auth | 3 | 0.588 | 4.26 (3.13 to 13.33) | 216 (201 to 237) | 170 | 0.04 |
| 2000 | kong-inline | ratelimit | 3 | 0.641 | 38.86 (15.62 to 43.06) | 275 (243 to 288) | 170 | 0.01 |

## What each feature added (difference of cell medians)

| rate | system | feature | runs | CPU ms per 1k (range) | p50 ms | p99 ms |
|---:|---|---|---|---|---:|---:|
| 1000 | kong | +ratelimit | 3+3 | +429 (+372 to +435) | +0.481 | +16.75 |
| 2000 | kong | +ratelimit | 3+3 | +270 (+245 to +272) | +1.040 | +43.71 |
| 1000 | kong-inline | +ratelimit | 3+3 | +18 (-22 to +89) | +0.004 | +1.01 |
| 2000 | kong-inline | +ratelimit | 3+3 | +59 (+6 to +87) | +0.053 | +34.60 |
