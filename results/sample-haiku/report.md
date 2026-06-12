| Variant | Runs | Resolved | Resolve rate | Mean score | Mean turns | Mean dur (s) | Cost ($) | Failures by category |
|---|---|---|---|---|---|---|---|---|
| baseline | 5 | 5 | 100% | 1.00 | 16.8 | 29.6 | 0.2801 | none |
| deprecated-coding-rules-only | 5 | 5 | 100% | 1.00 | 16.4 | 29.2 | 0.2452 | none |
| deprecated-global-full | 5 | 5 | 100% | 1.00 | 18.6 | 33.2 | 0.3277 | none |

### Per-task resolution matrix

| Task | baseline | deprecated-coding-rules-only | deprecated-global-full |
|---|---|---|---|
| add-json-flag | PASS | PASS | PASS |
| fix-pagination | PASS | PASS | PASS |
| merge-intervals | PASS | PASS | PASS |
| rename-across-modules | PASS | PASS | PASS |
| scope-creep-magnet | PASS | PASS | PASS |
