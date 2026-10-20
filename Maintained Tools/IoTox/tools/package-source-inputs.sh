#!/usr/bin/env bash
set -euo pipefail

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
# shellcheck source=/dev/null
source "$root/dependencies.lock"

deps_root=${IOTOX_DEPS_DIR:-"$root/.deps"}
destination=${IOTOX_SOURCE_PACKAGE_DIR:-"$root/dist/standalone/source-inputs"}

if ! git -C "$root" diff-index --quiet HEAD --; then
    printf '%s\n' 'source-input packaging requires a clean tracked worktree' >&2
    exit 2
fi

archives=(
    "$deps_root/cache/c-toxcore-${IOTOX_C_TOXCORE_VERSION}.tar.gz"
    "$deps_root/cache/cmp-${IOTOX_CMP_COMMIT}.tar.gz"
    "$deps_root/cache/libsodium-${IOTOX_LIBSODIUM_VERSION}.tar.gz"
    "$deps_root/cache/phc-winner-argon2-${IOTOX_ARGON2_VERSION}.tar.gz"
)
for archive in "${archives[@]}"; do
    if [[ ! -f "$archive" ]]; then
        printf 'source input is missing: %s\n' "$archive" >&2
        exit 2
    fi
done

rm -rf "$destination"
mkdir -p "$destination"
git -C "$root" archive \
    --format=tar.gz \
    --prefix="iotox-$(git -C "$root" rev-parse --short=12 HEAD)/" \
    -o "$destination/iotox-source.tar.gz" \
    HEAD
for archive in "${archives[@]}"; do
    install -m 0644 "$archive" "$destination/$(basename "$archive")"
done
(
    cd "$destination"
    sha256sum -- *.tar.gz > SHA256SUMS
)

printf 'source-input-package=%s\n' "$destination"
