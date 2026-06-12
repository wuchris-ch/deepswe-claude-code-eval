# Trajectory review — <task-id> / <variant-id> / <run-id>

Reviewer:
Date:
Transcript: `results/<run>/<run-id>/transcript.jsonl`
Final workspace: `results/<run>/<run-id>/workspace_after/`
Result: `results/<run>/<run-id>/result.json`

## 1. Outcome summary

| Field | Value |
|---|---|
| Resolved (all checks) | yes / no |
| Score | |
| Turns / tool calls | |
| Duration / cost | |
| Failed checks | |

## 2. Requirement coverage

For each requirement stated or implied in the task prompt:

| Requirement | Addressed? | Evidence (turn #, file) |
|---|---|---|
| | | |

## 3. Failure-mode checklist

Mark any observed, with the turn number where it happens:

- [ ] **Missed requirement** — part of the prompt never acted on
- [ ] **Wrong-file edit** — edited a file unrelated to the task
- [ ] **Scope creep** — "improved" code it was not asked to touch
- [ ] **Test tampering** — weakened/edited tests instead of fixing the code
- [ ] **Unverified claim of completion** — said done without running checks
- [ ] **Skipped verification** — never ran the test suite despite being told to
- [ ] **Regression** — fixed the target but broke something that passed before
- [ ] **Hallucinated API/file** — referenced code that does not exist
- [ ] **Loop/thrash** — repeated near-identical attempts without new information
- [ ] **Premature stop** — hit max-turns or gave up with work remaining

## 4. Turn-by-turn notes (interesting turns only)

| Turn | Tool | What happened | Assessment |
|---|---|---|---|
| | | | |

## 5. Instruction-variant attribution

Did the injected instructions visibly change behavior (e.g. ran tests before
finishing, refused to touch unrelated files, asked-vs-assumed)? Quote the
instruction line and the trajectory moment that follows it — or note that the
behavior is indistinguishable from baseline.

## 6. Verdict and rule candidates

- Verdict: correct / correct-but-sloppy / incorrect / incomplete
- Root cause (one sentence):
- Prompt/workflow rule this failure suggests (candidate for the instruction file):
