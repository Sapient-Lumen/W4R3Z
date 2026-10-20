#!/usr/bin/env bash
set -euo pipefail

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
# shellcheck source=/dev/null
source "$root/dependencies.lock"

deps_root=${IOTOX_DEPS_DIR:-"$root/.deps"}
cache="$deps_root/cache"
sources="$deps_root/src"
mkdir -p "$cache" "$sources"

download() {
    local url=$1
    local destination=$2
    local temporary="${destination}.part.$$"
    rm -f "$temporary"
    if command -v curl >/dev/null 2>&1; then
        curl --fail --location --proto '=https' --tlsv1.2 \
            --retry 3 --retry-delay 1 --output "$temporary" "$url"
    elif command -v wget >/dev/null 2>&1; then
        wget --https-only --tries=3 --output-document="$temporary" "$url"
    else
        printf '%s\n' 'fetch requires curl or wget' >&2
        exit 2
    fi
    mv "$temporary" "$destination"
}

fetch_verified() {
    local label=$1
    local url=$2
    local expected=$3
    local destination=$4

    if [[ ! -f "$destination" ]] || \
       [[ $(sha256sum "$destination" | awk '{print $1}') != "$expected" ]]; then
        rm -f "$destination"
        printf 'fetching %s from %s\n' "$label" "$url"
        download "$url" "$destination"
    fi
    printf '%s  %s\n' "$expected" "$destination" | sha256sum --check --status
    printf 'verified %s sha256=%s\n' "$label" "$expected"
}

safe_extract() {
    local archive=$1
    local destination=$2
    local marker=$3

    if [[ -f "$destination/$marker" ]]; then
        return
    fi
    rm -rf "$destination"
    mkdir -p "$destination"
    if tar -tf "$archive" | grep -Eq '(^/|(^|/)\.\.(/|$))'; then
        printf 'refusing unsafe archive paths in %s\n' "$archive" >&2
        exit 3
    fi
    tar -xf "$archive" --strip-components=1 -C "$destination"
    if [[ ! -f "$destination/$marker" ]]; then
        printf 'archive %s did not produce expected %s\n' "$archive" "$marker" >&2
        exit 3
    fi
}

sodium_archive="$cache/libsodium-${IOTOX_LIBSODIUM_VERSION}.tar.gz"
toxcore_archive="$cache/c-toxcore-${IOTOX_C_TOXCORE_VERSION}.tar.gz"
argon2_archive="$cache/phc-winner-argon2-${IOTOX_ARGON2_VERSION}.tar.gz"
cmp_archive="$cache/cmp-${IOTOX_CMP_COMMIT}.tar.gz"

fetch_verified \
    "libsodium ${IOTOX_LIBSODIUM_VERSION}" \
    "$IOTOX_LIBSODIUM_URL" \
    "$IOTOX_LIBSODIUM_SHA256" \
    "$sodium_archive"
fetch_verified \
    "c-toxcore ${IOTOX_C_TOXCORE_VERSION}" \
    "$IOTOX_C_TOXCORE_URL" \
    "$IOTOX_C_TOXCORE_SHA256" \
    "$toxcore_archive"
fetch_verified \
    "Argon2 ${IOTOX_ARGON2_VERSION}" \
    "$IOTOX_ARGON2_URL" \
    "$IOTOX_ARGON2_SHA256" \
    "$argon2_archive"
fetch_verified \
    "c-toxcore cmp submodule ${IOTOX_CMP_COMMIT}" \
    "$IOTOX_CMP_URL" \
    "$IOTOX_CMP_SHA256" \
    "$cmp_archive"

safe_extract \
    "$sodium_archive" \
    "$sources/libsodium-${IOTOX_LIBSODIUM_VERSION}" \
    configure
safe_extract \
    "$toxcore_archive" \
    "$sources/c-toxcore-${IOTOX_C_TOXCORE_VERSION}" \
    CMakeLists.txt
safe_extract \
    "$cmp_archive" \
    "$sources/c-toxcore-${IOTOX_C_TOXCORE_VERSION}/third_party/cmp" \
    cmp.c
safe_extract \
    "$argon2_archive" \
    "$sources/phc-winner-argon2-${IOTOX_ARGON2_VERSION}" \
    Makefile

cat <<REPORT
dependencies-root=$deps_root
libsodium-source=$sources/libsodium-${IOTOX_LIBSODIUM_VERSION}
c-toxcore-source=$sources/c-toxcore-${IOTOX_C_TOXCORE_VERSION}
c-toxcore-cmp-submodule=$IOTOX_CMP_COMMIT
argon2-source=$sources/phc-winner-argon2-${IOTOX_ARGON2_VERSION}
verification=sha256-pinned-immutable-release-artifacts
REPORT
