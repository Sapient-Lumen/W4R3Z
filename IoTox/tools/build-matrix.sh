#!/usr/bin/env bash
set -euo pipefail

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$root"

revision=$(tr -d '[:space:]' < "$root/REVISION")
fuzzer_log=${IOTOX_FUZZ_LOG:-/mnt/data/iotox-${revision}-fuzzer-smoke-final.log}
static_analyzer_log=${IOTOX_STATIC_ANALYZER_LOG:-/mnt/data/iotox-${revision}-focused-static-analysis-final.log}

mkdir -p "$root/build"
exec 9>"$root/build/.matrix.lock"
if ! flock -n 9; then
    printf "%s\n" "another IoTox build matrix already owns $root/build/.matrix.lock" >&2
    exit 75
fi

clean=${IOTOX_MATRIX_CLEAN:-1}
jobs=${IOTOX_MATRIX_JOBS:-2}
if [[ ! "$jobs" =~ ^[1-9][0-9]*$ ]]; then
    printf 'IOTOX_MATRIX_JOBS must be a positive integer: %s\n' "$jobs" >&2
    exit 2
fi
if [[ "$clean" == 1 ]]; then
    rm -rf \
        build/gcc-debug \
        build/gcc-release \
        build/clang-debug \
        build/clang-asan-ubsan \
        build/gcc-tsan \
        build/gcc-linked-argon2 \
        build/clang-fuzz \
        build/mutorr-preservation \
        components/toxsync/build/gcc-debug \
        components/toxsync/build/gcc-release \
        components/toxsync/build/gcc-portable-release \
        components/toxsync/build/clang-debug \
        components/toxsync/build/clang-asan-ubsan \
        components/toxsync/build/clang-fuzz
fi

for preset in gcc-debug gcc-release clang-debug clang-asan-ubsan gcc-tsan; do
    echo "==> configure: $preset"
    cmake --preset "$preset"
    echo "==> build: $preset"
    cmake --build --preset "$preset" --parallel "$jobs"
    echo "==> test: $preset"
    case "$preset" in
        clang-asan-ubsan)
            ASAN_OPTIONS=detect_leaks=1:halt_on_error=1 \
            UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1 \
                ctest --preset "$preset"
            ;;
        gcc-tsan)
            TSAN_OPTIONS=halt_on_error=1:second_deadlock_stack=1 \
                ctest --preset "$preset"
            ;;
        *)
            ctest --preset "$preset"
            ;;
    esac
done

echo "==> focused static analysis: critical admission and pressure units"
IOTOX_STATIC_ANALYZER_COMPILE_COMMANDS="$root/build/clang-debug/compile_commands.json" \
    ./tools/focused-static-analysis.py |& tee "$static_analyzer_log"

echo "==> fuzz smoke: canonical source seeds copied into build-local corpora"
IOTOX_FUZZ_RUNS=${IOTOX_FUZZ_RUNS:-5000} \
IOTOX_FUZZ_JOBS="$jobs" \
    ./tools/fuzz-smoke.sh |& tee "$fuzzer_log"

echo "==> preserved toxsync component matrix"
IOTOX_MATRIX_JOBS="$jobs" IOTOX_MATRIX_CLEAN=0 \
    ./tools/build-toxsync-matrix.sh

echo "==> configure: gcc-linked-argon2"
argon2_library=${IOTOX_SYSTEM_ARGON2_LIBRARY:-}
if [[ -z "$argon2_library" && -n "${LD_LIBRARY_PATH:-}" ]]; then
    IFS=: read -r -a iotox_library_paths <<<"$LD_LIBRARY_PATH"
    for iotox_library_path in "${iotox_library_paths[@]}"; do
        for iotox_argon2_name in libargon2.so libargon2.so.1; do
            if [[ -f "$iotox_library_path/$iotox_argon2_name" ]]; then
                argon2_library="$iotox_library_path/$iotox_argon2_name"
                break 2
            fi
        done
    done
fi
if [[ -z "$argon2_library" ]] && command -v ldconfig >/dev/null 2>&1; then
    argon2_library=$(ldconfig -p 2>/dev/null | awk '/libargon2\.so(\.1)? / {print $NF; exit}')
fi
if [[ -z "$argon2_library" || ! -f "$argon2_library" ]]; then
    printf '%s\n' 'system libargon2 was not found; set IOTOX_SYSTEM_ARGON2_LIBRARY for this required evidence lane' >&2
    exit 2
fi
cmake -S . -B build/gcc-linked-argon2 -G Ninja \
    -DCMAKE_BUILD_TYPE=Debug \
    -DCMAKE_CXX_COMPILER=g++ \
    -DBUILD_TESTING=ON \
    -DIOTOX_WARNINGS_AS_ERRORS=ON \
    -DIOTOX_ARGON2_LIBRARY="$argon2_library"
echo "==> build: gcc-linked-argon2"
cmake --build build/gcc-linked-argon2 --parallel "$jobs"
echo "==> test: gcc-linked-argon2"
ctest --test-dir build/gcc-linked-argon2 --output-on-failure

echo "==> preservation build: Mutorr incubator"
cmake -S . -B build/mutorr-preservation -G Ninja \
    -DCMAKE_BUILD_TYPE=Debug \
    -DIOTOX_WARNINGS_AS_ERRORS=ON \
    -DIOTOX_BUILD_MUTORR_RESEARCH=ON \
    -DIOTOX_BUILD_RESEARCH_LAB=ON \
    -DIOTOX_BUILD_BENCHMARK=ON
cmake --build build/mutorr-preservation --parallel "$jobs"
ctest --test-dir build/mutorr-preservation --output-on-failure

printf '%s\n' 'final-source-matrix=pass'
