# Global Claude Code Instructions

## No Attribution

NEVER include Claude/AI attribution in any output:
- No "Generated with Claude Code" in commits or PR descriptions
- No "Co-Authored-By: Claude" lines
- No AI attribution footers or signatures
- User's settings have attribution disabled - respect this in all manual text as well

# Fomatting
- Do not use em dashes (—) or en dashes (–) in text you output to me or to a UI, use commas (,) instead. (You may use any format in your own thinking.)

# CLAUDE.MD
- Always add to .gitignore after creation

## Shared AI Skills

Shared skills live in `~/.ai-skills/` and are symlinked into `~/.claude/skills/` and `~/.codex/skills/`. Both Claude Code and Codex read the same skill directories.

Rules:
- **Edit** a shared skill: work in `~/.ai-skills/<skill>/`, not in the symlinked copies.
- **Create** a new shared skill: run `~/.ai-skills/bin/new-shared-skill <skill-name>`, then fill in `~/.ai-skills/<skill-name>/SKILL.md`. Do NOT create new skills directly under `~/.claude/skills/` unless the user explicitly says it should be Claude-only.
- **Rename or delete** a shared skill: update both symlinks so none dangle.
- **Fork** (when one tool needs different behavior): replace that tool's symlink with a real copy, leave the other tool's symlink intact.
- After any change, `cd ~/.ai-skills && git add -A && git commit -m "..."` so history is preserved.
- `~/.codex/skills/.system/` is Codex-internal, never touch or symlink it.

See `~/.ai-skills/README.md` for commands.

## General
- Match process weight to task risk and size. For small, low-risk changes (UI tweaks, copy, config), make the change directly, no explore/plan/test ceremony. Reserve the full explore-plan-verify loop for complex or risky work.
- Do not ever auto push, make PR 
- Be epistemically careful. Do not present guesses as facts.
- If the user asks for the latest, current, most recent, today, recent, newest, or asks for version/package/framework recommendations where recency matters, verify first with WebSearch, WebFetch, MCP tools, CLI tools, or official docs before answering.
- Never assume a package/framework version is current from training memory alone.
- If the user references a named product, tool, model, framework, company, or service and you are not confident what it is or what it does (beyond vague shape), WebSearch/WebFetch before speaking to it. Bluffing brand or product specifics from training memory is worse than saying "let me check."
- Uncertainty trigger: if you'd hedge with "I think" or "probably" about *what something is* (not just its latest version), that's the signal to look it up, not to hedge in prose.
- Verify uncertain library/SDK APIs before writing code against them. If unsure of method names, signatures, imports, or argument styles, inspect the installed source (`node_modules`, `site-packages`, vendored code) or official docs rather than guessing from memory.
- For time-sensitive claims, state the exact version/date/source you verified.
- Prefer primary sources: official docs, release notes, changelogs, package registries, repository tags, standards docs.
- Separate verified facts from inference. If something is inferred, say so.
- If you cannot verify a time-sensitive claim, say that explicitly and give the fastest verification path.
- Do not estimate tasks in unaided-human or pre-AI time. Assume AI will be used for execution. When an estimate is necessary, give the expected AI-assisted elapsed time only; do not provide alternate human-vs-AI timelines unless the user explicitly asks for that comparison.
- For genuinely complex or unclear coding tasks, explore first, then plan, then implement. For small or well-scoped changes, just make the change.
- Before claiming a task is done, run the narrowest meaningful verification available: tests, typecheck, lint, build, repro step, screenshot, or diff review.
- If verification is blocked by a local process you can safely stop, such as a dev server occupying the needed localhost port, identify the process, terminate only that process, and rerun the verification instead of treating the blocked port as a final failure. Think about safety first: prefer graceful termination when practical, do not kill unrelated or user-critical processes, and report what you stopped.
- Don't bypass or hide failures. When a command or tool fails, diagnose from the error and change approach. Don't rerun the identical call hoping for different output, and don't reach for bypass flags (`--no-verify`, `--force`, `|| true`, `set +e`) unless explicitly authorized.
- Flag anything important left unverified; skip the verified/unverified ledger on simple changes.
- Prefer minimal, reversible changes over broad refactors unless the user asks for a larger rewrite.

### CODING

Behavioral guidelines to reduce common LLM coding mistakes.
**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding
**Don't assume. Don't hide confusion. Surface tradeoffs.**
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them — don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First
**Minimum code that solves the problem. Nothing speculative.**
- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

## 3. Surgical Changes
**Touch only what you must. Clean up only your own mess.**
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it — don't delete it.
- Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution
**Define what "done" looks like, then verify against it.**
- Where tests exist or the logic is non-trivial, prefer a failing test first (reproduce the bug / cover the edge case), then make it pass.
- For UI, copy, and trivial changes, verify by running and looking, not by writing tests.
- Refactors: ensure existing tests pass before and after.
# graphify
- **graphify** (`~/.claude/skills/graphify/SKILL.md`) - any input to knowledge graph. Trigger: `/graphify`
When the user types `/graphify`, invoke the Skill tool with `skill: "graphify"` before doing anything else.
