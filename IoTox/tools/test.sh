#!/usr/bin/env bash
set -euo pipefail

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
preset=${1:-gcc-debug}
cd "$root"
cmake --preset "$preset"
cmake --build --preset "$preset" --parallel

case "$preset" in
    clang-asan-ubsan)
        ASAN_OPTIONS=detect_leaks=1:halt_on_error=1 \
        UBSAN_OPTIONS=halt_on_error=1 \
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
