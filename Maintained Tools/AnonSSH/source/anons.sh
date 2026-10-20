#!/usr/bin/env bash
set -euo pipefail

if command -v anonssh >/dev/null 2>&1; then
  exec anonssh "$@"
fi

root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
package="$(nix-build "$root/default.nix" --no-out-link)"
if ! "$package/bin/anonssh" check-i2p-bootstrap \
  --corpus "$root/bootstrap/i2p" >/dev/null 2>&1; then
  printf '%s\n' \
    'warning: bundled I2P bootstrap corpus failed validation; verified network reseed remains enabled' >&2
fi
exec "$package/bin/anonssh" "$@"
