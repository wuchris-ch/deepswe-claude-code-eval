| Variant | Runs | Resolved | Resolve rate | Mean score | Mean turns | Mean dur (s) | Cost ($) | Failures by category |
|---|---|---|---|---|---|---|---|---|
| baseline | 2 | 2 | 100% | 1.00 | 11.0 | 102.1 | 1.7227 | none |
| deprecated-coding-rules-only | 1 | 1 | 100% | 1.00 | 10.0 | 45.6 | 0.5294 | none |
| deprecated-global-full | 1 | 1 | 100% | 1.00 | 10.0 | 48.4 | 0.8883 | none |

### Per-task resolution matrix

| Task | baseline | deprecated-coding-rules-only | deprecated-global-full |
|---|---|---|---|
| csv-parser | PASS | — | — |
| rate-limiter | PASS | PASS | PASS |
