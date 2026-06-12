| Variant | Runs | Resolved | Resolve rate | Mean score | Mean turns | Mean dur (s) | Cost ($) | Failures by category |
|---|---|---|---|---|---|---|---|---|
| baseline | 4 | 4 | 100% | 1.00 | 13.5 | 73.2 | 1.6613 | none |
| deprecated-coding-rules-only | 4 | 4 | 100% | 1.00 | 12.2 | 83.2 | 1.6698 | none |
| deprecated-global-full | 4 | 4 | 100% | 1.00 | 11.0 | 72.0 | 1.8008 | none |

### Per-task resolution matrix

| Task | baseline | deprecated-coding-rules-only | deprecated-global-full |
|---|---|---|---|
| config-layers | PASS | PASS | PASS |
| csv-parser | PASS | PASS | PASS |
| expr-eval | PASS | PASS | PASS |
| rate-limiter | PASS | PASS | PASS |
