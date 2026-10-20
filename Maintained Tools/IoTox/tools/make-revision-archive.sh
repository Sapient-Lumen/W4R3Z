#!/usr/bin/env bash
set -euo pipefail

datacube=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
entrance=$(cd "$datacube/.." && pwd)
revision=${1:-$(tr -d '\n' < "$datacube/REVISION")}
timestamp=${2:-$(TZ=America/New_York date +%Y.%m.%d.%H.%M)}
summary=${3:-ordinary-root-request-exact-address-just-werx}
output_dir=${4:-"$entrance/.."}
filename="IoTox-${revision}-${timestamp}-${summary}.zip"

if [[ ! "$revision" =~ ^rev[0-9]{4}$ ]]; then
    printf 'invalid revision: %s\n' "$revision" >&2
    exit 2
fi
if [[ ! "$timestamp" =~ ^[0-9]{4}\.[0-9]{2}\.[0-9]{2}\.[0-9]{2}\.[0-9]{2}$ ]]; then
    printf 'invalid timestamp: %s\n' "$timestamp" >&2
    exit 2
fi
if [[ ! "$summary" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]]; then
    printf 'summary must be lowercase hyphenated words: %s\n' "$summary" >&2
    exit 2
fi

"$datacube/tools/check-lone-entrance.sh" >/dev/null
mkdir -p "$output_dir"
stage=$(mktemp -d)
trap 'rm -rf "$stage"' EXIT
mkdir -p "$stage/IoTox/.datacube"
cp "$entrance/BOOTSTRAPROSE.md" "$stage/IoTox/BOOTSTRAPROSE.md"
if [[ -f "$entrance/.gitignore" ]]; then
    cp "$entrance/.gitignore" "$stage/IoTox/.gitignore"
fi

(
    cd "$datacube"
    tar \
        --exclude='./.git' \
        --exclude='./build' \
        --exclude='./build-*' \
        --exclude='./.deps' \
        --exclude='./dist' \
        --exclude='./*.toxsave' \
        --exclude='./**/*.toxsave' \
        --exclude='./*.identity' \
        --exclude='./**/*.identity' \
        --exclude='./*.ledger' \
        --exclude='./**/*.ledger' \
        --exclude='./*.store' \
        --exclude='./**/*.store' \
        --exclude='./authority.plist' \
        --exclude='./**/__pycache__' \
        --exclude='./**/*.pyc' \
        --exclude='./.DS_Store' \
        -cf - .
) | (
    cd "$stage/IoTox/.datacube"
    tar -xf -
)

mapfile -t ordinary < <(find "$stage/IoTox" -mindepth 1 -maxdepth 1 \
    ! -name '.*' -printf '%f\n' | sort)
[[ ${#ordinary[@]} -eq 1 && "${ordinary[0]}" == BOOTSTRAPROSE.md ]]

rm -f "$output_dir/$filename"
(
    cd "$stage"
    zip -q -r "$output_dir/$filename" IoTox
)
printf '%s\n' "$output_dir/$filename"
