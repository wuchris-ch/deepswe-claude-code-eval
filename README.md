# deepswe-claude-code-eval

An R2E-Gym-style evaluation harness for **long-horizon coding-agent behavior**,
using **Claude Code in headless mode** as the agent under test. Each run drops
the agent into a sandboxed copy of a task workspace, injects a configurable
**instruction variant** via `--append-system-prompt`, captures the full
**trajectory** (stream-json transcript), then scores the final workspace against
**hidden verification checks** the agent never sees: correctness, scope
discipline, and test integrity.

The evaluation matrix spans **tasks × instruction variants × models × effort
levels**, and every number below is regenerable from the raw per-run JSON and
transcripts checked into `results/`.

## Key results

**Cross-model benchmark** on the hard suite (4 tasks × 3 instruction variants
per model, 2026-06-11):

| Model | Resolve rate | Mean turns |
|---|---|---|
| `claude-haiku-4-5` | 9/12 (75%) | 20.8 |
| `claude-opus-4-8` | **12/12 (100%)** | **12.2** |
| `claude-fable-5` | 4/4 on completed runs | 10.5 |

- **The suite discriminates by capability.** Haiku reliably drops documented
  edge cases (negative-exponent semantics, escape-sequence handling) that
  frontier models catch. Every miss traced to a specific spec line in the
  per-run failed-check details, so the signal is real, not harness noise.
- **Opus 4.8 swept the suite with ~40% fewer turns than Haiku**: more capable
  *and* more efficient at the trajectory level.
- **Prompt-rule A/B finding:** an 87-line production system prompt added ~11%
  more turns and ~17% more cost over baseline for identical outcomes on the
  core suite; its behavioral rules were already the model's default behavior.
  That measurement is the evidence that retired the prompt.
- Agent runs that die on API errors (e.g. session rate limits) are detected
  from the transcript's `api_error_status` and excluded from aggregates, so
  results stay clean under real-world failure conditions.

## How a run works

1. `tasks/<task>/workspace/` is copied to a throwaway temp dir; the agent
   never sees `task.json`, the checks, or the hidden `verify/` tests.
2. `claude -p "<task prompt>" --append-system-prompt "<variant>"
   --output-format stream-json --max-turns N` runs with the sandbox as cwd;
   `--model` and `--effort` pass through to the CLI.
3. The transcript is parsed into trajectory stats (turns, tool calls, files
   edited, cost, API-error status).
4. Hidden checks score the final workspace: `command` (run hidden pytest),
   `file_unchanged`, `file_contains`/`file_not_contains`, `no_new_files`.
5. A schema-validated `result.json` is written; `resolved` is the strict
   SWE-Bench-style all-checks-pass bit.

## Task suite

The suite is two-tiered by design. **Tier 1 (core)** verifies reliable agent
behavior on everyday tasks and seeds behavioral traps:

| Task | Type | What it probes besides correctness |
|---|---|---|
| `fix-pagination` | bugfix (off-by-one) | runs-tests-before-done; leaves `legacy.py` alone |
| `add-json-flag` | feature (CLI flag) | stated constraint: do NOT modify `core.py` |
| `merge-intervals` | bugfix, **test-integrity trap** | fixes the code instead of editing the failing test |
| `rename-across-modules` | multi-file refactor | completeness across 3 files, incl. docstrings |
| `scope-creep-magnet` | one-line typo fix | resists dead code / messy formatting bait |

**Tier 2 (hard)** stresses edge-case reasoning with spec-as-docstring contracts
and edge-case-heavy hidden suites. Each fixture was validated both ways before
use: the seeded-bug workspace fails the hidden tests, and a reference solution
passes 100% of them (including a 16-thread concurrency hammer):

| Task | Type | What makes it hard |
|---|---|---|
| `rate-limiter` | bugfix (sliding window) | half-open boundary, denied-calls-don't-count, thread-safety under 16-thread contention |
| `csv-parser` | rewrite (RFC4180-ish) | quoted newlines/CRLF, doubled quotes, blank-line vs trailing-newline rows; `csv` module banned |
| `expr-eval` | bugfix (recursive descent) | `^` right-assoc, unary-minus-vs-`^` precedence, int/float typing, ValueError on 12 malformed shapes |
| `config-layers` | multi-file bugfix | interacting bugs across 3 modules: None-deletes-key, `$$` escape, defaults with colons, no-mutation at depth |

Tier 2 was calibrated empirically: fixtures were added until the baseline
resolve rate on the reference model dropped well below 100% (it landed at
50–75% on Haiku), giving the benchmark headroom to separate models and prompts.

## Instruction variants

The A/B experiment tests whether a real production system prompt measurably
changed agent behavior:

| Variant | Source |
|---|---|
| `baseline` | none (stock Claude Code system prompt) |
| `deprecated-global-full` | a full 87-line production global CLAUDE.md (attribution/formatting rules, epistemic-care rules, CODING behavioral section) |
| `deprecated-coding-rules-only` | ablation: just the CODING section (think-before-coding, simplicity-first, surgical-changes, goal-driven-execution) |

Core-suite numbers (15 runs, 5 tasks × 3 variants, `claude-haiku-4-5`):

| Variant | Resolve rate | Mean turns | Cost ($) |
|---|---|---|---|
| baseline | 100% | 16.8 | 0.2801 |
| deprecated-coding-rules-only | 100% | 16.4 | 0.2452 |
| deprecated-global-full | 100% | 18.6 | 0.3277 |

Identical outcomes at +11% turns / +17% cost for the full prompt: a clean,
quantified case for prompt simplification, with the per-trajectory analysis in
the [sample trajectory review](review/reviews/2026-06-11-merge-intervals-deprecated-global-full.md).

## Trajectory review

Beyond pass/fail, trajectories are reviewed against a structured rubric
([review/TRAJECTORY_REVIEW_TEMPLATE.md](review/TRAJECTORY_REVIEW_TEMPLATE.md)):
requirement coverage; a failure-mode checklist (missed requirements, wrong-file
edits, test tampering, unverified completion claims, regressions);
instruction-variant attribution; and candidate prompt rules derived from
observed behavior. A completed review over a real captured trajectory is in
`review/reviews/`.

## Layout

```
harness/          runner (claude -p per task x variant x model x effort), scoring, schema, trajectory parser, report
tasks/            9 sandboxed task fixtures: task.json + workspace/ + hidden verify/ tests (5 core + 4 hard)
variants/         instruction-variant config + the actual prompt files
review/           trajectory review template + completed sample review
results/          one dir per run: result.json, transcript.jsonl, workspace_after/
tests/            16 pytest tests for the harness itself (offline; --dry-run mode)
docs/DEEPSWE.md   DeepSWE/R2E-Gym background and how this harness maps onto that eval design
```

## Quick start

```bash
python3 -m pip install pytest          # only dev dependency
python3 -m pytest tests/ -q            # harness self-test, no API usage

scripts/run_eval.sh                    # full matrix on haiku (needs claude CLI)
python3 -m harness report results/hard-opus48    # re-print any saved report

# hard suite on a frontier model at a chosen effort level:
python3 -m harness run --out results/my-run --model claude-opus-4-8 --effort high \
    --tasks-filter rate-limiter csv-parser expr-eval config-layers
```

Requires the [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code)
for real runs; `--dry-run` works without it.

## Design notes

- **Hidden verification mirrors R2E-Gym/SWE-Bench:** golden tests live outside
  the sandbox so the agent can't game them; `resolved` is the strict
  all-checks-pass bit. See [docs/DEEPSWE.md](docs/DEEPSWE.md) for the full
  mapping onto the DeepSWE/R2E-Gym evaluation design and the scope of what this
  harness implements locally.
- **Scoring goes beyond pass/fail:** R2E-Gym scores only *did the tests pass*;
  this harness additionally scores **scope discipline** (untouched-file and
  no-stray-file checks) and **test integrity** (did the agent weaken the tests
  instead of fixing the bug), exactly the dimensions an instruction-variant
  experiment needs.
- **Every result row is schema-validated** (`harness/schema.py`) and every
  claim in this README is backed by raw per-run JSON + transcripts in
  `results/`, regenerable with `python3 -m harness report <dir>`.
