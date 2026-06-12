#!/usr/bin/env bash
# Run the full task x variant eval matrix through Claude Code headless mode.
# Usage: scripts/run_eval.sh [model]   (default: haiku)
set -euo pipefail
cd "$(dirname "$0")/.."

MODEL="${1:-haiku}"
OUT="results/$(date +%Y%m%d-%H%M%S)-${MODEL}"

command -v claude >/dev/null || { echo "claude CLI not found; install Claude Code first" >&2; exit 1; }

python3 -m harness run --out "$OUT" --model "$MODEL"
echo
echo "results: $OUT"
