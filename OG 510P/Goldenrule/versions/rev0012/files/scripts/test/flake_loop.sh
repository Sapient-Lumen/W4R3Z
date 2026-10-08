#!/usr/bin/env bash
set -euo pipefail

N="${1:-5}"
MODE="${2:-quick}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
OUT="$ROOT/artifacts/timing/flake_${MODE}.json"
mkdir -p "$ROOT/artifacts/timing"

pass_count=0
for ((i=1; i<=N; i++)); do
  if "$ROOT/scripts/test/run_harness.sh" "$MODE"; then
    pass_count=$((pass_count + 1))
  fi
done

cat > "$OUT" <<JSON
{
  "mode": "$MODE",
  "iterations": $N,
  "passes": $pass_count,
  "failures": $((N - pass_count))
}
JSON

echo "flake: mode=$MODE pass=$pass_count/$N artifact=$OUT"
