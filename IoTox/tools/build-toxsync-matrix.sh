#!/usr/bin/env bash
set -euo pipefail

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
source_root="$root/components/toxsync"

jobs=${IOTOX_MATRIX_JOBS:-2}
clean=${IOTOX_MATRIX_CLEAN:-1}
if [[ ! "$jobs" =~ ^[1-9][0-9]*$ ]]; then
    printf 'IOTOX_MATRIX_JOBS must be a positive integer: %s\n' "$jobs" >&2
    exit 2
fi

presets=(
    gcc-debug
    gcc-release
    gcc-portable-release
    clang-debug
    clang-asan-ubsan
    clang-tsan
)
fuzz_build="$source_root/build/clang-fuzz"

if [[ "$clean" == 1 ]]; then
    for preset in "${presets[@]}"; do
        rm -rf "$source_root/build/$preset"
    done
    rm -rf "$fuzz_build"
fi

for preset in "${presets[@]}"; do
    printf '==> toxsync configure: %s\n' "$preset"
    cmake --preset "$preset" -S "$source_root"
    printf '==> toxsync build: %s\n' "$preset"
    cmake --build "$source_root/build/$preset" --parallel "$jobs"
    printf '==> toxsync test: %s\n' "$preset"
    case "$preset" in
        clang-asan-ubsan)
            ASAN_OPTIONS=detect_leaks=1:halt_on_error=1 \
            UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1 \
                ctest --test-dir "$source_root/build/$preset" --output-on-failure
            ;;
        clang-tsan)
            TSAN_OPTIONS=halt_on_error=1:second_deadlock_stack=1 \
                ctest --test-dir "$source_root/build/$preset" --output-on-failure
            ;;
        *)
            ctest --test-dir "$source_root/build/$preset" --output-on-failure
            ;;
    esac
done

printf '%s\n' '==> toxsync configure: clang-fuzz'
cmake -S "$source_root" -B "$fuzz_build" -G Ninja \
    -DCMAKE_BUILD_TYPE=Debug \
    -DCMAKE_CXX_COMPILER=clang++ \
    -DBUILD_TESTING=OFF \
    -DTOXSYNC_BUILD_CLI=OFF \
    -DTOXSYNC_BUILD_TESTS=OFF \
    -DTOXSYNC_BUILD_BENCHMARK=OFF \
    -DTOXSYNC_BUILD_FUZZER=ON \
    -DTOXSYNC_WARNINGS_AS_ERRORS=ON
cmake --build "$fuzz_build" --parallel "$jobs" --target \
    toxsync_wire_fuzzer toxsync_metadata_fuzzer toxsync_files_fuzzer

fuzz_runs=${TOXSYNC_FUZZ_RUNS:-5000}
if [[ ! "$fuzz_runs" =~ ^[1-9][0-9]*$ ]]; then
    printf 'TOXSYNC_FUZZ_RUNS must be a positive integer: %s\n' "$fuzz_runs" >&2
    exit 2
fi
mkdir -p \
    "$fuzz_build/corpus/wire" \
    "$fuzz_build/corpus/metadata" \
    "$fuzz_build/corpus/files" \
    "$fuzz_build/artifacts/wire" \
    "$fuzz_build/artifacts/metadata" \
    "$fuzz_build/artifacts/files"

ASAN_OPTIONS=${ASAN_OPTIONS:-detect_leaks=1:halt_on_error=1} \
UBSAN_OPTIONS=${UBSAN_OPTIONS:-halt_on_error=1:print_stacktrace=1} \
    "$fuzz_build/toxsync_wire_fuzzer" \
        "$fuzz_build/corpus/wire" \
        -runs="$fuzz_runs" \
        -max_len=1024 \
        -artifact_prefix="$fuzz_build/artifacts/wire/"
ASAN_OPTIONS=${ASAN_OPTIONS:-detect_leaks=1:halt_on_error=1} \
UBSAN_OPTIONS=${UBSAN_OPTIONS:-halt_on_error=1:print_stacktrace=1} \
    "$fuzz_build/toxsync_metadata_fuzzer" \
        "$fuzz_build/corpus/metadata" \
        -runs="$fuzz_runs" \
        -max_len=65536 \
        -artifact_prefix="$fuzz_build/artifacts/metadata/"
ASAN_OPTIONS=${ASAN_OPTIONS:-detect_leaks=1:halt_on_error=1} \
UBSAN_OPTIONS=${UBSAN_OPTIONS:-halt_on_error=1:print_stacktrace=1} \
    "$fuzz_build/toxsync_files_fuzzer" \
        "$fuzz_build/corpus/files" \
        -runs="$fuzz_runs" \
        -max_len=65536 \
        -artifact_prefix="$fuzz_build/artifacts/files/"

printf '%s\n' 'toxsync-source-matrix=pass'
