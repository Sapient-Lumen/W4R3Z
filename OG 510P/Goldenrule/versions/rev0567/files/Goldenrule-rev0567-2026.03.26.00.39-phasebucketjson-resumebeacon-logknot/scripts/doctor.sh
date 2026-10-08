#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUST_EXEC="$ROOT/tools/rust_exec.sh"

fail=0

echo "[doctor] cwd=$ROOT"
echo "[doctor] TZ=${TZ:-unset}"
echo "[doctor] LANG=${LANG:-unset}"
echo "[doctor] LC_ALL=${LC_ALL:-unset}"

check_bin() {
  local b="$1"
  local install_hint="$2"
  if command -v "$b" >/dev/null 2>&1; then
    echo "[ok] $b=$(command -v "$b")"
  else
    echo "[fail] missing $b - $install_hint"
    fail=1
  fi
}

check_bin python3 "install Python 3.11+"
check_bin git "install git"
check_bin bash "install bash"

if "$RUST_EXEC" cargo --version >/dev/null 2>&1; then
  echo "[ok] cargo=$($RUST_EXEC cargo --version | head -n1)"
else
  echo "[fail] cargo unavailable (native or junest fallback)."
  echo "       run: /run/sandworm/toolroot/bin/junest setup"
  fail=1
fi

if "$RUST_EXEC" rustc --version >/dev/null 2>&1; then
  echo "[ok] rustc=$($RUST_EXEC rustc --version | head -n1)"
else
  echo "[warn] rustc direct probe failed; cargo may still function via wrapper"
fi

if [[ -f "$ROOT/rust-toolchain.toml" ]]; then
  echo "[ok] rust-toolchain.toml present"
else
  echo "[warn] missing rust-toolchain.toml"
fi

if [[ -f "$ROOT/pyproject.toml" ]]; then
  echo "[ok] pyproject.toml present"
else
  echo "[warn] missing pyproject.toml"
fi

if [[ "$fail" -ne 0 ]]; then
  echo "[doctor] FAILED"
  exit 1
fi

echo "[doctor] OK"
