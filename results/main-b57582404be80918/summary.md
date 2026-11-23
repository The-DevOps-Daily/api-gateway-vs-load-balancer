# Summary b57582404be80918

95 passed runs, 19 failed. Medians over rounds; ranges are min to max.

| rate | system | step | runs | p50 ms | p99 ms (range) | CPU ms per 1k req (range) | anon MB | other processes, cores (max) |
|---:|---|---|---:|---:|---|---|---:|---:|
| 1000 | direct | plain | 3 | 0.254 | 2.23 (0.47 to 2.25) | 156 (125 to 158) | 7 | 0.04 |
| 1000 | kong | plain | 3 | 0.434 | 1.26 (1.21 to 1.56) | 217 (206 to 229) | 172 | 0.04 |
| 1000 | kong | tls | 3 | 0.715 | 7.84 (6.17 to 11.79) | 366 (365 to 367) | 172 | 0.17 |
| 1000 | kong | auth | 3 | 0.620 | 2.83 (2.56 to 20.76) | 325 (312 to 345) | 172 | 0.07 |
| 1000 | kong | ratelimit | 3 | 1.115 | 21.44 (14.99 to 57.04) | 798 (754 to 809) | 172 | 0.26 |
| 1000 | kong | transform | 3 | 1.245 | 47.66 (34.69 to 62.67) | 842 (828 to 863) | 172 | 0.11 |
| 1000 | nginx | plain | 3 | 0.482 | 2.45 (1.18 to 4.49) | 183 (146 to 229) | 6 | 0.19 |
| 1000 | nginx | tls | 3 | 0.444 | 2.77 (1.60 to 61.55) | 159 (158 to 202) | 6 | 0.09 |
| 1000 | nginx | auth | 3 | 0.430 | 1.54 (1.27 to 3.38) | 158 (145 to 181) | 6 | 0.02 |
| 1000 | nginx | ratelimit | 3 | 0.493 | 7.41 (0.99 to 13.38) | 211 (143 to 213) | 6 | 0.13 |
| 1000 | nginx | transform | 3 | 0.463 | 2.08 (1.67 to 3.49) | 168 (148 to 179) | 6 | 0.09 |
| 1000 | tyk | plain | 3 | 0.562 | 2.62 (2.41 to 7.75) | 340 (326 to 362) | 79 | 0.12 |
| 1000 | tyk | tls | 3 | 0.599 | 5.72 (3.61 to 7.28) | 363 (362 to 374) | 86 | 0.13 |
| 1000 | tyk | auth | 3 | 0.749 | 42.92 (11.47 to 48.31) | 492 (457 to 521) | 88 | 0.06 |
| 1000 | tyk | ratelimit | 3 | 0.731 | 33.53 (23.87 to 50.25) | 489 (467 to 506) | 92 | 0.12 |
| 1000 | tyk | transform | 3 | 0.805 | 74.41 (40.69 to 79.99) | 545 (534 to 554) | 101 | 0.02 |
| 2000 | direct | plain | 3 | 0.229 | 0.86 (0.51 to 0.94) | 91 (81 to 95) | 6 | 0.08 |
| 2000 | kong | plain | 3 | 0.451 | 2.05 (1.94 to 2.21) | 158 (157 to 166) | 172 | 0.01 |
| 2000 | kong | tls | 3 | 0.559 | 3.39 (2.87 to 4.34) | 199 (197 to 211) | 172 | 0.04 |
| 2000 | kong | auth | 3 | 0.592 | 8.43 (3.44 to 22.95) | 233 (216 to 238) | 172 | 0.02 |
| 2000 | kong | ratelimit | 3 | 1.683 | 47.32 (44.37 to 51.19) | 492 (488 to 493) | 172 | 0.22 |
| 2000 | kong | transform | 3 | 1.780 | 52.79 (48.99 to 53.02) | 495 (495 to 496) | 172 | 0.13 |
| 2000 | nginx | plain | 3 | 0.371 | 2.07 (1.47 to 3.45) | 102 (93 to 119) | 6 | 0.10 |
| 2000 | nginx | tls | 3 | 0.394 | 9.26 (2.76 to 30.80) | 123 (118 to 151) | 6 | 0.07 |
| 2000 | nginx | auth | 3 | 0.421 | 9.91 (3.37 to 44.11) | 131 (129 to 149) | 6 | 0.05 |
| 2000 | nginx | ratelimit | 3 | 0.416 | 2.60 (2.41 to 2.93) | 126 (112 to 127) | 6 | 0.16 |
| 2000 | nginx | transform | 3 | 0.387 | 3.03 (1.58 to 7.93) | 117 (108 to 158) | 6 | 0.15 |
| 2000 | tyk | plain | 3 | 0.614 | 41.80 (36.11 to 43.64) | 279 (276 to 292) | 90 | 0.04 |
| 2000 | tyk | tls | 3 | 0.687 | 45.97 (33.77 to 47.37) | 328 (280 to 345) | 94 | 0.04 |
| 2000 | tyk | auth | 3 | 7.427 | 70.28 (63.83 to 74.59) | 416 (399 to 441) | 117 | 0.10 |
| 2000 | tyk | ratelimit | 2 | 17.359 | 71.42 (71.18 to 71.66) | 439 (435 to 442) | 117 | 0.04 |
| 2000 | tyk | transform | 3 | 22.128 | 80.67 (65.35 to 87.67) | 482 (425 to 483) | 114 | 0.07 |

## What each feature added (difference of cell medians)

| rate | system | feature | runs | CPU ms per 1k (range) | p50 ms | p99 ms |
|---:|---|---|---|---|---:|---:|
| 1000 | kong | +tls | 3+3 | +150 (+136 to +161) | +0.281 | +6.59 |
| 1000 | kong | +auth | 3+3 | -41 (-55 to -20) | -0.095 | -5.01 |
| 1000 | kong | +ratelimit | 3+3 | +473 (+409 to +496) | +0.495 | +18.61 |
| 1000 | kong | +transform | 3+3 | +44 (+19 to +109) | +0.130 | +26.22 |
| 2000 | kong | +tls | 3+3 | +40 (+31 to +54) | +0.108 | +1.34 |
| 2000 | kong | +auth | 3+3 | +34 (+5 to +41) | +0.032 | +5.04 |
| 2000 | kong | +ratelimit | 3+3 | +259 (+250 to +277) | +1.092 | +38.89 |
| 2000 | kong | +transform | 3+3 | +3 (+2 to +8) | +0.097 | +5.47 |
| 1000 | nginx | +tls | 3+3 | -24 (-72 to +56) | -0.038 | +0.32 |
| 1000 | nginx | +auth | 3+3 | -1 (-57 to +24) | -0.014 | -1.23 |
| 1000 | nginx | +ratelimit | 3+3 | +54 (-39 to +68) | +0.062 | +5.87 |
| 1000 | nginx | +transform | 3+3 | -43 (-65 to +37) | -0.029 | -5.33 |
| 2000 | nginx | +tls | 3+3 | +21 (-1 to +58) | +0.023 | +7.19 |
| 2000 | nginx | +auth | 3+3 | +8 (-23 to +31) | +0.027 | +0.65 |
| 2000 | nginx | +ratelimit | 3+3 | -6 (-37 to -2) | -0.004 | -7.31 |
| 2000 | nginx | +transform | 3+3 | -9 (-19 to +46) | -0.029 | +0.42 |
| 1000 | tyk | +tls | 3+3 | +23 (-1 to +48) | +0.037 | +3.10 |
| 1000 | tyk | +auth | 3+3 | +129 (+83 to +160) | +0.150 | +37.19 |
| 1000 | tyk | +ratelimit | 3+3 | -3 (-55 to +49) | -0.018 | -9.38 |
| 1000 | tyk | +transform | 3+3 | +57 (+28 to +87) | +0.074 | +40.88 |
| 2000 | tyk | +tls | 3+3 | +48 (-12 to +69) | +0.073 | +4.17 |
| 2000 | tyk | +auth | 3+3 | +88 (+54 to +162) | +6.740 | +24.31 |
| 2000 | tyk | +ratelimit | 3+2 | +22 (-6 to +43) | +9.932 | +1.14 |
| 2000 | tyk | +transform | 2+3 | +43 (-17 to +48) | +4.770 | +9.25 |

## Failed runs (left out)

- round 1 tyk/ratelimit at 2000/s: could not sustain 2000/s: sent 58309 of 60000
- round 1 nginx/transform at 2000/s: could not sustain 2000/s: sent 55613 of 60000
- round 2 direct/plain at 1000/s: contended: other processes used 1.47 cores during the run
- round 2 tyk/transform at 2000/s: contended: other processes used 0.49 cores during the run
- round 2 tyk/ratelimit at 2000/s: could not sustain 2000/s: sent 59332 of 60000
- round 2 nginx/tls at 1000/s: contended: other processes used 0.44 cores during the run
- round 2 kong/plain at 1000/s: contended: other processes used 0.85 cores during the run
- round 2 tyk/auth at 1000/s: contended: other processes used 0.92 cores during the run
- round 2 tyk/transform at 1000/s: contended: other processes used 1.43 cores during the run
- round 2 tyk/auth at 2000/s: contended: other processes used 0.73 cores during the run
- round 2 kong/ratelimit at 2000/s: contended: other processes used 0.96 cores during the run
- round 3 tyk/tls at 1000/s: contended: other processes used 0.92 cores during the run
- round 3 nginx/transform at 2000/s: contended: other processes used 0.49 cores during the run
- round 3 kong/plain at 2000/s: contended: other processes used 0.30 cores during the run
- round 4 kong/ratelimit at 2000/s: contended: other processes used 1.13 cores during the run
- round 5 nginx/transform at 2000/s: contended: other processes used 1.12 cores during the run
- round 5 kong/ratelimit at 2000/s: contended: other processes used 0.64 cores during the run
- round 5 tyk/ratelimit at 2000/s: contended: other processes used 0.61 cores during the run
- round 6 tyk/ratelimit at 2000/s: contended: other processes used 1.22 cores during the run
