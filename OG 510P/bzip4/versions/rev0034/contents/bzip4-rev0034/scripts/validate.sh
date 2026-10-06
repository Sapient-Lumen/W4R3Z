#!/bin/sh
set -eu
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
build=${1:-"${TMPDIR:-/tmp}/bzip4-rev0034-release-build"}
cmake -S "$root" -B "$build" -G Ninja \
  -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON
cmake --build "$build" -j2
ctest --test-dir "$build" --output-on-failure
"$build/bzip4_release_audit" "$root"
