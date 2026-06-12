| Variant | Runs | Resolved | Resolve rate | Mean score | Mean turns | Mean dur (s) | Cost ($) | Failures by category |
|---|---|---|---|---|---|---|---|---|
| baseline | 4 | 3 | 75% | 0.96 | 18.0 | 98.4 | 0.5194 | correctness:1 |
| deprecated-coding-rules-only | 4 | 3 | 75% | 0.96 | 22.8 | 70.0 | 0.4147 | correctness:1 |
| deprecated-global-full | 4 | 3 | 75% | 0.96 | 21.8 | 99.8 | 0.5462 | correctness:1 |

### Per-task resolution matrix

| Task | baseline | deprecated-coding-rules-only | deprecated-global-full |
|---|---|---|---|
| config-layers | 0.86 | PASS | PASS |
| csv-parser | PASS | PASS | PASS |
| expr-eval | PASS | 0.83 | 0.83 |
| rate-limiter | PASS | PASS | PASS |
