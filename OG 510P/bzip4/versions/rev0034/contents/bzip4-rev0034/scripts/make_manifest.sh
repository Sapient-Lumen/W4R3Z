#!/bin/sh
set -eu
root=${1:-.}
cd "$root"
temporary=MANIFEST.sha256.tmp
trap 'rm -f "$temporary"' EXIT HUP INT TERM
find . \
  \( -type d \( -name .git -o -name .svn -o -name __pycache__ -o -name .pytest_cache \
      -o -path './build' -o -path './build-*' -o -path './cmake-build-*' \
      -o -name CMakeFiles \) -prune \) \
  -o \( -type f ! -path './MANIFEST.sha256' ! -path './MANIFEST.sha256.tmp' -print \) \
  | LC_ALL=C sort \
  | sed 's#^./##' \
  | while IFS= read -r path; do
      digest=$(sha256sum -- "$path" | awk '{print $1}')
      printf '%s  %s\n' "$digest" "$path"
    done > "$temporary"
mv -f "$temporary" MANIFEST.sha256
trap - EXIT HUP INT TERM
