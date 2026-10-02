#!/usr/bin/env bash
set -euo pipefail

binary=${1:-}
if [[ -z "$binary" || ! -x "$binary" ]]; then
    printf 'usage: %s /path/to/iotox [/path/to/iotox.spdx.json]\n' "$0" >&2
    exit 2
fi
root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
sbom=${2:-"$(dirname "$binary")/iotox.spdx.json"}

"$binary" --version
"$binary" bootstrap-seeds >/dev/null

if command -v nm >/dev/null 2>&1; then
    if nm -u "$binary" 2>/dev/null | grep -Eq '[[:space:]]tox_[A-Za-z0-9_]+$'; then
        printf '%s\n' 'standalone verification failed: unresolved toxcore symbols remain' >&2
        nm -u "$binary" | grep -E '[[:space:]]tox_[A-Za-z0-9_]+$' >&2 || true
        exit 1
    fi
fi

if command -v ldd >/dev/null 2>&1; then
    dependencies=$(ldd "$binary" 2>&1 || true)
    printf '%s\n' "$dependencies"
    if grep -Eiq 'libtoxcore|libsodium|libargon2' <<<"$dependencies"; then
        printf '%s\n' 'standalone verification failed: toxcore, libsodium, or Argon2 is still a runtime shared-library dependency' >&2
        exit 1
    fi
fi

if command -v readelf >/dev/null 2>&1; then
    readelf -d "$binary" 2>/dev/null | sed -n '/NEEDED/p' || true
fi

if [[ ! -f "$sbom" ]]; then
    printf 'standalone verification failed: SPDX SBOM is missing: %s\n' \
        "$sbom" >&2
    exit 1
fi
python3 "$root/tools/generate-sbom.py" verify \
    --root "$root" --binary "$binary" --sbom "$sbom"

printf '%s\n' 'standalone-linked-toxcore-libsodium-argon2=pass'
printf '%s\n' 'standalone-spdx-sbom=pass'
