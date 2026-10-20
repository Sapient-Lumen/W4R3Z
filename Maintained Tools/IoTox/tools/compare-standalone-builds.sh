#!/usr/bin/env bash
set -euo pipefail

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
baseline=${IOTOX_REPRO_BASELINE_DIR:-}
jobs=${IOTOX_JOBS:-2}

if ! git -C "$root" diff-index --quiet HEAD --; then
    printf '%s\n' \
        'reproducible comparison requires a clean tracked worktree' >&2
    exit 2
fi

source_commit=$(git -C "$root" rev-parse HEAD)
source_date_epoch=$(git -C "$root" log -1 --format=%ct)
temporary=$(mktemp -d "${TMPDIR:-/tmp}/iotox-reproducible.XXXXXXXX")
trap 'rm -rf "$temporary"' EXIT

build_distribution() {
    local name=$1
    local destination="$temporary/$name/dist"
    if ! IOTOX_STANDALONE_BUILD_DIR="$temporary/$name/build" \
         IOTOX_DIST_DIR="$destination" \
         IOTOX_SOURCE_COMMIT="$source_commit" \
         SOURCE_DATE_EPOCH="$source_date_epoch" \
         IOTOX_JOBS="$jobs" \
             "$root/tools/build-standalone.sh" >/dev/null; then
        printf 'reproducible comparison build failed: %s\n' "$name" >&2
        return 1
    fi
    printf '%s\n' "$destination"
}

if [[ -n "$baseline" ]]; then
    baseline=$(realpath "$baseline")
    "$root/tools/verify-standalone.sh" \
        "$baseline/iotox" "$baseline/iotox.spdx.json" >/dev/null
    if ! grep -Fqx "source-commit=$source_commit" \
        "$baseline/build-info.txt"; then
        printf '%s\n' \
            'baseline distribution does not bind the current commit' >&2
        exit 2
    fi
    baseline_mode=prebuilt-current-commit
else
    baseline=$(build_distribution first)
    baseline_mode=fresh-empty-build-directory
fi
candidate=$(build_distribution second)

files=(
    iotox
    iotox.spdx.json
    build-info.txt
    verification.txt
    THIRD_PARTY.md
)
for relative in "${files[@]}"; do
    if ! cmp -s "$baseline/$relative" "$candidate/$relative"; then
        printf 'reproducible comparison mismatch: %s\n' "$relative" >&2
        exit 1
    fi
done
if ! diff -qr "$baseline/licenses" "$candidate/licenses" >/dev/null; then
    printf '%s\n' 'reproducible comparison mismatch: licenses/' >&2
    exit 1
fi

binary_sha256=$(sha256sum "$candidate/iotox" | awk '{print $1}')
sbom_sha256=$(sha256sum "$candidate/iotox.spdx.json" | awk '{print $1}')
cat <<REPORT
schema=iotox.reproducible-standalone.v1
source-commit=$source_commit
source-date-epoch=$source_date_epoch
baseline=$baseline_mode
candidate=fresh-empty-build-directory
binary-sha256=$binary_sha256
spdx-sbom-sha256=$sbom_sha256
comparison=byte-identical
scope=same-host-same-toolchain-distinct-product-build-roots
REPORT
