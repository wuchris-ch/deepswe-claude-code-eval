# DeepSWE background, and what this harness does and does not integrate

## What DeepSWE is

**DeepSWE-Preview** is a 32B-parameter autonomous software-engineering agent released
2025-07-02 by Agentica (UC Berkeley Sky Computing Lab) with Together AI. It is
Qwen3-32B post-trained with pure reinforcement learning (no SFT) using Agentica's
**rLLM** framework and a GRPO-variant algorithm ("GRPO++"), on 4.5K real-world SWE
tasks from the **R2E-Gym-Subset** dataset, with rollouts executed in 512+ parallel
Docker containers.

Reported numbers on SWE-Bench Verified:

| Metric | Score |
|---|---|
| Qwen3-32B baseline | ~23% |
| DeepSWE Pass@1 (avg of 16 runs) | 42.2% |
| Pass@16 (oracle) | 71.0% |
| Hybrid test-time scaling, Best@16 | 59.0% (open-weight SOTA at release) |

Sources:
- Announcement: https://www.together.ai/blog/deepswe
- Model card: https://huggingface.co/agentica-org/DeepSWE-Preview
- Training framework: https://github.com/agentica-project/rllm (archived; successor: rllm-org/rllm)
- Environment framework: https://github.com/R2E-Gym/R2E-Gym (arXiv:2504.07164)
- Dataset: https://huggingface.co/datasets/R2E-Gym/R2E-Gym-Subset

## How DeepSWE is actually evaluated (R2E-Gym), and what this harness mirrors

| R2E-Gym / DeepSWE eval | This harness |
|---|---|
| Task = problem statement + Dockerized repo snapshot | Task = `task.json` prompt + `workspace/` fixture copied to a throwaway sandbox dir |
| Agent loop: bash, search, file-editor, finish tools (max 100 steps) | Claude Code headless (`claude -p`) with its native tools, `--max-turns` capped |
| Hidden golden tests; agent never sees them | `verify/` dir per task, never copied into the sandbox |
| Sparse binary reward: patch passes selected unit tests → 1, else 0 | `resolved` = ALL checks pass (correctness + scope + integrity), plus a fractional `score` |
| Full step-by-step trajectory captured per run | `--output-format stream-json` transcript captured and parsed per run |
| Sampling/instruction config per run | Instruction variants injected via `--append-system-prompt` per run |

The deliberate extension here: R2E-Gym scores only *did the tests pass*. This harness
also scores **scope discipline** (untouched-file and no-stray-file checks) and **test
integrity** (did the agent weaken the tests instead of fixing the bug), which is what
the instruction-variant experiment needs.

## The integration gap (read this before putting anything on a resume)

This project does **not** run the DeepSWE model itself, and does not execute
R2E-Gym/Harbor Docker task images:

1. **Model**: DeepSWE-Preview's published serving path is vLLM with 8-way tensor
   parallelism and 64K context — not runnable on this Mac at full precision.
   Community GGUF/MLX quantizations (e.g. `bartowski/agentica-org_DeepSWE-Preview-GGUF`,
   ~20 GB at Q4_K_M) would run slowly on a 32–64 GB Apple Silicon machine, but
   long agentic trajectories at low tokens/sec were out of scope here.
2. **Environments**: official R2E-Gym evaluation uses per-task Docker images
   (~300–500 MB each, 13 Python repos). This harness substitutes small local task
   fixtures with the same shape (problem statement → sandboxed workspace → hidden
   verification → binary resolve), not the official images.

What this project **is**: a DeepSWE/R2E-Gym-*style* evaluation harness whose agent
under test is **Claude Code in headless mode**, used to A/B real instruction variants
(including a deprecated production CLAUDE.md) and review trajectories.

### Truthful resume wording

Supported by this repo as-is:

> Built an R2E-Gym-style local evaluation harness for long-horizon coding-agent
> behavior, driving Claude Code headless across sandboxed task fixtures with hidden
> verification tests; A/B-tested system-prompt instruction variants (including a
> deprecated production prompt) and reviewed captured trajectories, scoring
> correctness, scope discipline, and test integrity.

NOT supported (don't claim without doing the extra work):

- "Ran/evaluated the DeepSWE model" — requires serving the 32B model (vLLM or a
  GGUF/MLX quant behind an OpenAI-compatible endpoint).
- "Evaluated on SWE-Bench / R2E-Gym benchmark tasks" — requires the official
  Docker task images and datasets.
- Any wording implying access to a proprietary "Pier" agent platform, unless that
  exists elsewhere; this repo demonstrates the Claude Code half.
