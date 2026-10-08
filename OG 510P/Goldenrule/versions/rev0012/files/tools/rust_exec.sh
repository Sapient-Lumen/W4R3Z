#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ $# -eq 0 ]]; then
  echo "usage: tools/rust_exec.sh <command> [args...]" >&2
  exit 2
fi

if command -v cargo >/dev/null 2>&1 && command -v rustc >/dev/null 2>&1; then
  cd "$ROOT"
  exec "$@"
fi

JUNEST_BIN="${JUNEST_BIN:-/run/sandworm/toolroot/bin/junest}"
JUNEST_HOME="${SW_JUNEST_HOME:-$ROOT/.sandworm/toolroot/junest-home}"

if [[ ! -x "$JUNEST_BIN" ]]; then
  echo "rust_exec: junest not found at $JUNEST_BIN" >&2
  exit 127
fi

if [[ ! -d "$JUNEST_HOME" ]]; then
  echo "rust_exec: junest home not found at $JUNEST_HOME; attempting setup" >&2
  mkdir -p "$(dirname "$JUNEST_HOME")"
  if ! env SW_JUNEST_HOME="$JUNEST_HOME" "$JUNEST_BIN" setup >/dev/null 2>&1; then
    echo "rust_exec: failed to initialize junest home at $JUNEST_HOME" >&2
    echo "run: env SW_JUNEST_HOME=$JUNEST_HOME $JUNEST_BIN setup" >&2
    exit 127
  fi
fi

if ! env SW_JUNEST_HOME="$JUNEST_HOME" "$JUNEST_BIN" ns -f -- sh -lc "command -v cargo >/dev/null 2>&1 && command -v rustc >/dev/null 2>&1"; then
  echo "rust_exec: rust toolchain missing in junest; attempting install" >&2
  if ! env SW_JUNEST_HOME="$JUNEST_HOME" "$JUNEST_BIN" ns -f -- sh -lc "pacman -Syy --noconfirm >/dev/null 2>&1 && pacman -Sy --noconfirm archlinux-keyring >/dev/null 2>&1 && pacman -Syu --noconfirm >/dev/null 2>&1 && pacman -S --noconfirm rust >/dev/null 2>&1"; then
    echo "rust_exec: failed to install rust in junest home at $JUNEST_HOME" >&2
    echo "run: env SW_JUNEST_HOME=$JUNEST_HOME $JUNEST_BIN ns -f -- pacman -Syy && ... pacman -S rust" >&2
    exit 127
  fi
fi

if ! env SW_JUNEST_HOME="$JUNEST_HOME" "$JUNEST_BIN" ns -f -- sh -lc "cargo --version >/dev/null 2>&1 && rustc --version >/dev/null 2>&1"; then
  echo "rust_exec: rust toolchain runtime broken in junest; attempting full upgrade" >&2
  if ! env SW_JUNEST_HOME="$JUNEST_HOME" "$JUNEST_BIN" ns -f -- sh -lc "pacman -Syu --noconfirm >/dev/null 2>&1"; then
    echo "rust_exec: junest upgrade failed for $JUNEST_HOME" >&2
    exit 127
  fi
fi

quoted=()
for a in "$@"; do
  quoted+=("$(printf '%q' "$a")")
done
cmd="${quoted[*]}"
root_q="$(printf '%q' "$ROOT")"

# Use Junest namespace mode with a bind mount of the workspace so Cargo can
# resolve workspace-relative paths consistently.
exec env SW_JUNEST_HOME="$JUNEST_HOME" \
  "$JUNEST_BIN" ns -f -b "--bind $ROOT $ROOT" -- sh -lc "cd $root_q && unset LD_PRELOAD && export LD_LIBRARY_PATH=/usr/lib:/usr/lib64:/usr/lib32 && $cmd"
