#!/usr/bin/env bash
# Regenerate both sets twice, under two hash seeds, and fail unless the two runs give the same bytes and neither
# prints a WARNING or ERROR. A set whose run exits 1 because anchors moved is run once more, as the generator asks.
# Leaves the working tree as the second run wrote it; `git diff -- diagrams` then shows what the change moved.
#
#     .claude/skills/drawing-posters/scripts/determinism.sh [R3 F7 ...]
set -uo pipefail
cd "$(git rev-parse --show-toplevel)"
gen() {  # seed, then the generator's arguments
  local seed=$1; shift
  local out status
  out=$(PYTHONHASHSEED=$seed uv run python diagrams/gen-diagrams.py "$@" 2>&1); status=$?
  if [ $status -ne 0 ] && grep -q '^NOTE ' <<<"$out"; then
    out=$(PYTHONHASHSEED=$seed uv run python diagrams/gen-diagrams.py "$@" 2>&1); status=$?
  fi
  if grep -E 'WARNING|ERROR' <<<"$out"; then echo "determinism: seed $seed, $*: the build is not clean"; exit 1; fi
  [ $status -eq 0 ] || { echo "$out"; echo "determinism: seed $seed, $*: exit $status"; exit 1; }
}
snap=$(mktemp -d)
for seed in 0 1; do
  gen "$seed" "$@"
  gen "$seed" --map "$@"
  mkdir -p "$snap/$seed"
  cp diagrams/*.svg diagrams/manifest.json "$snap/$seed/"
  mkdir -p "$snap/$seed/map" && cp diagrams/map/*.svg diagrams/map/manifest.json "$snap/$seed/map/"
done
if diff -rq "$snap/0" "$snap/1"; then
  echo "determinism: both sets are byte-identical under PYTHONHASHSEED 0 and 1"
  rm -rf "$snap"
else
  echo "determinism: the runs differ (kept in $snap): sort by count then name, never by set or dict order"
  exit 1
fi
