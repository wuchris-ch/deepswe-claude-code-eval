# deepswe-claude-code-eval

A local, R2E-Gym-style evaluation harness for **long-horizon coding-agent behavior**,
using **Claude Code in headless mode** as the agent under test. Each run drops the
agent into a sandboxed copy of a task workspace, injects a configurable
**instruction variant** via `--append-system-prompt`, captures the full
**trajectory** (stream-json transcript), then scores the final workspace against
**hidden verification checks** the agent never sees — correctness, scope
discipline, and test integrity.

The instruction variants are real: the experiment A/B-tests a **deprecated
production global CLAUDE.md** (and an ablation of just its CODING rules) against a
no-instructions baseline, to measure whether those prompt rules actually changed
agent behavior. See [docs/DEEPSWE.md](docs/DEEPSWE.md) for how this relates to
DeepSWE/R2E-Gym and exactly what is and is not integrated.

## Layout

```
harness/          runner (claude -p per task x variant x model x effort), scoring, schema, trajectory parser, report
tasks/            9 sandboxed task fixtures: task.json + workspace/ + hidden verify/ tests (5 core + 4 hard)
variants/         instruction-variant config + the actual prompt files
review/           trajectory review template + completed sample review
results/          one dir per run: result.json, transcript.jsonl, workspace_after/
tests/            16 pytest tests for the harness itself (offline; --dry-run mode)
docs/DEEPSWE.md   DeepSWE/R2E-Gym background, integration gap, truthful resume wording
```

## Quick start

```bash
python3 -m pip install pytest          # only dev dependency
python3 -m pytest tests/ -q            # harness self-test, no API usage

scripts/run_eval.sh                    # full matrix on haiku (needs claude CLI)
python3 -m harness report results/sample-haiku   # re-print a saved report

# hard suite only, on a frontier model at a chosen effort level:
python3 -m harness run --out results/my-run --model claude-opus-4-8 --effort high \
    --tasks-filter rate-limiter csv-parser expr-eval config-layers
```

Requires the [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) for
real runs; `--dry-run` works without it.

## How a run works

1. `tasks/<task>/workspace/` is copied to a throwaway temp dir (the agent never
   sees `task.json`, the checks, or `verify/`).
2. `claude -p "<task prompt>" --append-system-prompt "<variant>" --output-format
   stream-json --max-turns N` runs with the sandbox as cwd. `--model` and
   `--effort` pass through to the CLI, so the matrix extends to
   tasks × variants × models × effort levels.
3. The transcript is parsed into trajectory stats (turns, tool calls, files
   edited, cost).
4. Hidden checks score the final workspace: `command` (run hidden pytest),
   `file_unchanged`, `file_contains`/`file_not_contains`, `no_new_files`.
5. A schema-validated `result.json` is written; `resolved` is the strict
   SWE-Bench-style all-checks-pass bit.

## Task fixtures

| Task | Type | What it probes besides correctness |
|---|---|---|
| `fix-pagination` | bugfix (off-by-one) | runs-tests-before-done; leaves `legacy.py` alone |
| `add-json-flag` | feature (CLI flag) | stated constraint: do NOT modify `core.py` |
| `merge-intervals` | bugfix, **test-integrity trap** | fixes the code instead of editing the failing test |
| `rename-across-modules` | multi-file refactor | completeness across 3 files, incl. docstrings |
| `scope-creep-magnet` | one-line typo fix | resists dead code / messy formatting bait |

Harder fixtures (added to break the ceiling effect below — spec-as-docstring
contracts with edge-case-heavy hidden suites):

| Task | Type | What makes it hard |
|---|---|---|
| `rate-limiter` | bugfix (sliding window) | half-open boundary, denied-calls-don't-count, thread-safety hammer (16 threads) |
| `csv-parser` | rewrite (RFC4180-ish) | quoted newlines/CRLF, doubled quotes, blank-line vs trailing-newline rows; `csv` module banned |
| `expr-eval` | bugfix (recursive descent) | `^` right-assoc, unary-minus-vs-`^` precedence, int/float typing, ValueError on 12 malformed shapes |
| `config-layers` | multi-file bugfix | interacting bugs across 3 modules: None-deletes-key, `$$` escape, defaults with colons, no-mutation at depth |

## Instruction variants

| Variant | Source |
|---|---|
| `baseline` | none — stock Claude Code system prompt |
| `deprecated-global-full` | Chris's full deprecated global CLAUDE.md (87 lines: attribution/formatting rules, epistemic-care rules, CODING behavioral section), recovered from `~/.claude/backups/` |
| `deprecated-coding-rules-only` | ablation: just the CODING section (think-before-coding, simplicity-first, surgical-changes, goal-driven-execution) |

Known confound, by design choice: the runner does not isolate `CLAUDE_CONFIG_DIR`
(to keep CLI auth intact), so the user-level `~/.claude/CLAUDE.md` is constant
background for **all** variants. At measurement time it contained only skill
triggers and no behavioral rules, so the variant deltas remain attributable to the
injected prompts.

## Results: hard suite across models (2026-06-11)

The 4 hard fixtures were built specifically to break the ceiling effect seen on
the core suite (below). Each model ran the full hard-task × 3-variant matrix;
raw runs in `results/hard-haiku/`, `results/hard-opus48/`, `results/hard-fable5/`.

| Model | Resolve rate | Mean turns | What it missed |
|---|---|---|---|
| `claude-haiku-4-5` | 9/12 (75%) | 20.8 | negative-exponent semantics (`2^-2`), the `$$` escape — both stated verbatim in the spec docstrings |
| `claude-opus-4-8` | **12/12 (100%)** | 12.2 | nothing — and with the fewest turns |
| `claude-fable-5` | 4/4 (partial) | 10.5 | nothing in completed runs; 8 runs hit an API session limit and are quarantined in `results/hard-fable5/invalid-rate-limited/` |

Takeaways:

- **The suite now discriminates by model.** Haiku reliably drops edge cases that
  frontier models catch; its misses are real documented-spec items, not harness
  noise (verified per-run in the failed-check details).
- **Opus 4.8 resolves the suite at the ceiling with ~40% fewer turns than
  haiku** — better *and* cheaper per outcome at the trajectory level, though
  ~3.4× the dollar cost for this matrix.
- **Prompt variants still don't separate on resolve rate** at either end —
  consistent with the core-suite finding that the deprecated prompt's rules are
  already default behavior. Separating variants on frontier models needs a
  third difficulty tier (multi-bug repos, longer horizons).
- Runs that die on an API error (e.g. 429 session limits) are now detected via
  the transcript's `api_error_status` and flagged so they can't silently
  pollute aggregates — the Fable column above is honest about that.

## Results (core suite, sample run)

15 runs (5 tasks × 3 variants), model `haiku`, 2026-06-11, total cost ≈ $0.85.
Raw per-run JSON + transcripts in [results/sample-haiku/](results/sample-haiku/);
regenerate the table with `python3 -m harness report results/sample-haiku`.

| Variant | Runs | Resolved | Resolve rate | Mean score | Mean turns | Mean dur (s) | Cost ($) |
|---|---|---|---|---|---|---|---|
| baseline | 5 | 5 | 100% | 1.00 | 16.8 | 29.6 | 0.2801 |
| deprecated-coding-rules-only | 5 | 5 | 100% | 1.00 | 16.4 | 29.2 | 0.2452 |
| deprecated-global-full | 5 | 5 | 100% | 1.00 | 18.6 | 33.2 | 0.3277 |

All 15 runs resolved (per-task matrix in `results/sample-haiku/report.md`), so on
this 5-task suite the variants show **no quality difference — a ceiling effect**:
the tasks are within the model's comfortable range, and none of the seeded traps
(test tampering, scope creep, stated do-not-touch constraints) caught any variant.

What the numbers *do* show: the 87-line deprecated prompt added ~11% more turns
and ~17% more cost than baseline for identical outcomes, while its CODING-section
ablation was marginally the cheapest. The honest takeaway (detailed in the
[sample trajectory review](review/reviews/2026-06-11-merge-intervals-deprecated-global-full.md)):
the deprecated global prompt's behavioral rules were already the model's default
behavior on tasks of this size — overhead without lift. Separating the variants on
resolve rate would need harder, longer-horizon tasks (or a weaker model), which is
the designed next step: add fixtures until baseline drops below ~70%.

## Trajectory review

`review/TRAJECTORY_REVIEW_TEMPLATE.md` is the structured rubric (requirement
coverage, failure-mode checklist: missed requirements, wrong-file edits, test
tampering, unverified completion claims, regressions; instruction-variant
attribution; candidate prompt rules). A completed example over a real captured
trajectory is in `review/reviews/`.

## Proof table: resume claim → evidence

Resume bullet under test:
*"Ran DeepSWE-style evals through Claude Code, injecting custom instruction
variants and evaluating long-horizon coding-agent behavior on sandboxed tasks;
reviewed trajectories and converted failures into tighter prompt rules."*

| Claim fragment | Evidence | Verify with |
|---|---|---|
| Evaluation harness for coding-agent behavior | [harness/runner.py](harness/runner.py), [harness/scoring.py](harness/scoring.py), [harness/schema.py](harness/schema.py) | `python3 -m pytest tests/ -q` (16 tests) |
| Sandboxed software tasks | [tasks/](tasks/) — 9 fixtures, hidden `verify/` tests, temp-dir sandboxing in [harness/runner.py](harness/runner.py) | `python3 -m harness run --dry-run --out /tmp/d` |
| Driven through Claude Code (headless) | `build_agent_cmd()` in [harness/runner.py](harness/runner.py); per-run `transcript.jsonl` in [results/sample-haiku/](results/sample-haiku/) | `scripts/run_eval.sh` |
| Instruction variants injected | [variants/variants.json](variants/variants.json), [variants/deprecated-global-full.md](variants/deprecated-global-full.md) (real deprecated prompt) | inspect any two runs of the same task |
| Long-horizon behavior measured | turns/tool-calls/files-edited per run via [harness/trajectory.py](harness/trajectory.py); scope+integrity checks beyond pass/fail | `python3 -m harness report results/sample-haiku` |
| Scoring schema | `RESULT_SCHEMA` in [harness/schema.py](harness/schema.py), validated on every run | [tests/test_schema.py](tests/test_schema.py) |
| Trajectory review | [review/TRAJECTORY_REVIEW_TEMPLATE.md](review/TRAJECTORY_REVIEW_TEMPLATE.md) + completed sample in [review/reviews/](review/reviews/) | read it against the referenced transcript |
| Actual numbers | results table above; raw per-run JSON in [results/sample-haiku/](results/sample-haiku/) | `python3 -m harness report results/sample-haiku` |
| **DeepSWE/Pier integration itself** | **NOT integrated** — documented gap | [docs/DEEPSWE.md](docs/DEEPSWE.md) incl. truthful resume wording |
