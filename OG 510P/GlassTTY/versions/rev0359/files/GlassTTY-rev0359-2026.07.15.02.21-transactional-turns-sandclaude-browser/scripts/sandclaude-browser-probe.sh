#!/usr/bin/env bash
set -Eeuo pipefail

ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)
last=''
for ((attempt = 0; attempt < 120; attempt++)); do
  if last=$("$ROOT/glassttyd" ping 2>&1); then
    printf '%s\n' "$last"
    exit 0
  fi
  sleep 0.1
done

printf 'GlassTTY browser bundle did not establish its broker: %s\n' "$last" >&2
exit 1
