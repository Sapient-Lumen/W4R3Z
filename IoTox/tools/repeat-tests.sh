#!/usr/bin/env bash
set -euo pipefail

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
preset=${1:-gcc-debug}
runs=${2:-${IOTOX_REPEAT_RUNS:-10}}
pattern=${3:-${IOTOX_REPEAT_PATTERN:-iotox\.}}

if [[ ! "$runs" =~ ^[1-9][0-9]*$ ]]; then
    printf 'repeat count must be a positive integer: %s\n' "$runs" >&2
    exit 2
fi
if [[ ! -f "$root/build/$preset/CTestTestfile.cmake" ]]; then
    printf 'build preset first; CTest tree is missing: %s\n' "$root/build/$preset" >&2
    exit 2
fi

if command -v pkg-config >/dev/null 2>&1 && pkg-config --exists libsodium; then
    sodium_libdir=$(pkg-config --variable=libdir libsodium)
    export LD_LIBRARY_PATH="$sodium_libdir${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
fi

ctest \
    --test-dir "$root/build/$preset" \
    --repeat "until-fail:$runs" \
    --tests-regex "$pattern" \
    --output-on-failure
