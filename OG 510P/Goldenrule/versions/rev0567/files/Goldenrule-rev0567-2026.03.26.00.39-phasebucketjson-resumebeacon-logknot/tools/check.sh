#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
RUST_EXEC="$ROOT/tools/rust_exec.sh"

echo "[check] cargo fmt --check"
"$RUST_EXEC" cargo fmt --check

echo "[check] cargo test -p gr_engine"
"$RUST_EXEC" cargo test -p gr_engine

echo "[check] python -m compileall -q grlab"
python3 -m compileall -q grlab

echo "[check] python -m unittest discover -s grlab/tests"
python3 -m unittest discover -s grlab/tests

echo "[check] ok"
