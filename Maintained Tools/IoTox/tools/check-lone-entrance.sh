#!/usr/bin/env bash
set -euo pipefail

datacube=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
root=$(cd "$datacube/.." && pwd)

mapfile -t ordinary < <(find "$root" -mindepth 1 -maxdepth 1 \
    ! -name '.*' -printf '%f\n' | sort)

if [[ ${#ordinary[@]} -ne 1 || "${ordinary[0]:-}" != BOOTSTRAPROSE.md ]]; then
    printf '%s\n' 'lone-entrance invariant failed; ordinary root entries:' >&2
    printf '  %s\n' "${ordinary[@]:-<none>}" >&2
    exit 1
fi

[[ -d "$root/.datacube" ]]
[[ -f "$root/BOOTSTRAPROSE.md" ]]
[[ -f "$root/.datacube/CMakeLists.txt" ]]
printf '%s\n' 'lone-entrance=pass'
