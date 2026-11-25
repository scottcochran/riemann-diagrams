#!/usr/bin/env bash
# Run .lake/build/bin/deps (lake build deps, beside this script) once per compiled module, its parts in the order Lean writes them
# (.olean, .olean.server, .olean.private): one process each, since the parts of different modules can claim
# the same address. Arguments go to xargs NUL-separated, because module names may contain quotes
# (HypothesesZ'). Usage: run-deps.sh <oleans dir> <out dir> [module path ...]
set -euo pipefail
oleans=$1; out=$2; shift 2
exe="$(cd "$(dirname "$0")" && pwd)/.lake/build/bin/deps"
mkdir -p "$out"
list() { if [ "$#" -gt 0 ]; then printf '%s\n' "$@"; else find "$oleans" -name '*.olean' | sort; fi; }
list "$@" | while IFS= read -r f; do
  rel=${f#"$oleans"/}
  printf '%s\0%s\0' "$f" "$out/${rel//\//.}.jsonl"
done | xargs -0 -n 2 -P 8 sh -c '
  f=$1; o=$2; set -- "$f"
  [ -f "$f.server" ] && set -- "$@" "$f.server"
  [ -f "$f.private" ] && set -- "$@" "$f.private"
  "'"$exe"'" "$@" > "$o" 2> "$o.err" || echo "FAILED $f"' sh
