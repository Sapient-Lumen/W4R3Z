#!/usr/bin/env bash
set -euo pipefail

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
build=${IOTOX_COVERAGE_BUILD_DIR:-"$root/build/gcc-coverage"}
report=${IOTOX_COVERAGE_REPORT_DIR:-"$root/build/coverage-report"}
jobs=${IOTOX_JOBS:-2}
minimum=${IOTOX_COVERAGE_MINIMUM:-70}
gcov_executable=${IOTOX_GCOV_EXECUTABLE:-gcov}

if ! command -v gcovr >/dev/null 2>&1; then
    printf '%s\n' 'gcovr is required to produce the coverage report' >&2
    exit 2
fi
if [[ "$gcov_executable" == */* ]]; then
    if [[ ! -x "$gcov_executable" ]]; then
        printf 'IOTOX_GCOV_EXECUTABLE is not executable: %s\n' "$gcov_executable" >&2
        exit 2
    fi
elif ! command -v "$gcov_executable" >/dev/null 2>&1; then
    printf 'gcov matching the coverage compiler is required: %s\n' "$gcov_executable" >&2
    exit 2
fi
if [[ ! "$jobs" =~ ^[1-9][0-9]*$ ]]; then
    printf 'IOTOX_JOBS must be a positive integer: %s\n' "$jobs" >&2
    exit 2
fi
if [[ ! "$minimum" =~ ^([0-9]|[1-9][0-9]|100)$ ]]; then
    printf 'IOTOX_COVERAGE_MINIMUM must be an integer from 0 through 100: %s\n' "$minimum" >&2
    exit 2
fi

cmake --preset gcc-coverage
if ! grep -Fxq 'IOTOX_ENABLE_COVERAGE:BOOL=ON' "$build/CMakeCache.txt"; then
    printf '%s\n' 'coverage instrumentation is disabled in the configured build cache' >&2
    exit 2
fi
cmake --build --preset gcc-coverage --parallel "$jobs"

# Nix keeps runtime libraries outside the global loader path. Honor pkg-config
# when present while remaining a no-op on conventional distributions.
if command -v pkg-config >/dev/null 2>&1 && pkg-config --exists libsodium; then
    sodium_libdir=$(pkg-config --variable=libdir libsodium)
    export LD_LIBRARY_PATH="$sodium_libdir${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
fi
ctest --preset gcc-coverage --output-on-failure

mkdir -p "$report"
gcovr "$build" \
    --root "$root" \
    --gcov-executable "$gcov_executable" \
    --filter "$root/src/" \
    --filter "$root/include/" \
    --exclude-unreachable-branches \
    --gcov-ignore-parse-errors negative_hits.warn_once_per_file \
    --gcov-ignore-parse-errors suspicious_hits.warn_once_per_file \
    --print-summary \
    --fail-under-line "$minimum" \
    --xml-pretty \
    --xml "$report/coverage.xml" \
    --html-details "$report/index.html"

printf 'coverage-report=%s\n' "$report/index.html"
