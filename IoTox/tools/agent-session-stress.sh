#!/usr/bin/env bash
set -euo pipefail

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
mkdir -p "$root/build"
exec 9>"$root/build/.agent-stress.lock"
if ! flock -n 9; then
    printf '%s\n' "another IoTox Agent stress run already owns $root/build/.agent-stress.lock" >&2
    exit 75
fi

preset=${1:-gcc-debug}
build=${IOTOX_BUILD_DIR:-"$root/build/$preset"}
runs=${IOTOX_AGENT_STRESS_RUNS:-100}
revision=$(tr -d '[:space:]' < "$root/REVISION")
log=${IOTOX_AGENT_STRESS_LOG:-"/mnt/data/iotox-${revision}-agent-stress-final.log"}
exit_file=${IOTOX_AGENT_STRESS_EXIT:-"/mnt/data/iotox-${revision}-agent-stress-final.exit"}
target='ratox successor agent exposes files and structured local control over mock toxcore'

if [[ ! "$runs" =~ ^[1-9][0-9]*$ ]] || (( runs > 999 )); then
    printf 'IOTOX_AGENT_STRESS_RUNS must be an integer from 1 through 999: %s\n' "$runs" >&2
    exit 2
fi

required=(
    "$build/iotox_tests"
    "$build/libtoxcore-iotox-mock.so"
    "$build/libargon2-iotox-mock.so"
    "$root/third_party/eff_large_wordlist_2016-07-18.txt"
)
for path in "${required[@]}"; do
    if [[ ! -f "$path" ]]; then
        printf 'agent stress input is missing: %s\n' "$path" >&2
        exit 2
    fi
done

if command -v pkg-config >/dev/null 2>&1 && pkg-config --exists libsodium; then
    sodium_libdir=$(pkg-config --variable=libdir libsodium)
    export LD_LIBRARY_PATH="$sodium_libdir${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
fi

log_dir=$(dirname "$log")
mkdir -p "$log_dir" "$(dirname "$exit_file")"
work=$(mktemp -d)
log_stage=$(mktemp "$log_dir/.iotox-agent-stress.XXXXXX")
cleanup() {
    rm -rf "$work"
    rm -f "$log_stage"
}
trap cleanup EXIT
: > "$log_stage"
rm -f "$exit_file"

run_test() {
    "$build/iotox_tests" \
        --mock-toxcore "$build/libtoxcore-iotox-mock.so" \
        --mock-argon2 "$build/libargon2-iotox-mock.so" \
        --wordlist "$root/third_party/eff_large_wordlist_2016-07-18.txt" \
        "$@"
}

# Discover the linked registry index from a complete passing run. Translation-unit
# initialization order is a build fact, so the tool must not freeze a guessed shard number.
if ! run_test > "$work/full.log" 2>&1; then
    cat "$work/full.log" >&2
    printf '%s\n' 1 > "$exit_file"
    exit 1
fi

summary=$(tail -n 1 "$work/full.log")
if [[ ! "$summary" =~ ^tests=([0-9]+)[[:space:]]selected=([0-9]+)[[:space:]]shard=0/1[[:space:]]failures=0$ ]]; then
    printf 'unable to read a complete passing registry summary: %s\n' "$summary" >&2
    printf '%s\n' 1 > "$exit_file"
    exit 1
fi
registered=${BASH_REMATCH[1]}
selected=${BASH_REMATCH[2]}
if [[ "$registered" != "$selected" || "$registered" == 0 ]]; then
    printf 'registry discovery was incomplete: tests=%s selected=%s\n' "$registered" "$selected" >&2
    printf '%s\n' 1 > "$exit_file"
    exit 1
fi

shard_index=$(awk -v target="PASS $target" '
    /^PASS / {
        if ($0 == target) {
            print pass_index
            found = 1
            exit
        }
        ++pass_index
    }
    END {
        if (!found) {
            exit 1
        }
    }
' "$work/full.log") || {
    printf 'target Agent test is absent from the linked registry: %s\n' "$target" >&2
    printf '%s\n' 1 > "$exit_file"
    exit 1
}

for ((run = 1; run <= runs; ++run)); do
    one="$work/run-$run.log"
    if run_test --shard-index "$shard_index" --shard-count "$registered" > "$one" 2>&1 \
        && grep -Fxq "PASS $target" "$one" \
        && grep -Fxq "tests=$registered selected=1 shard=$shard_index/$registered failures=0" "$one"; then
        printf 'run=%03d PASS agent-shard online-epoch=1 hello-send-attempts=2\n' \
            "$run" >> "$log_stage"
    else
        printf 'run=%03d FAIL agent-shard shard=%s/%s\n' \
            "$run" "$shard_index" "$registered" >> "$log_stage"
        cat "$one" >> "$log_stage"
        chmod 0600 "$log_stage"
        mv -f "$log_stage" "$log"
        printf '%s\n' 1 > "$exit_file"
        cat "$log" >&2
        exit 1
    fi
done

summary_line="agent-session-stress=$runs/$runs passed shard=$shard_index/$registered"
printf '%s\n' "$summary_line" >> "$log_stage"

pass_lines=$(grep -cE '^run=[0-9]{3} PASS ' "$log_stage" || true)
summary_lines=$(grep -Fxc "$summary_line" "$log_stage" || true)
if [[ "$pass_lines" != "$runs" ]] || \
   ! diff -u \
       <(seq 1 "$runs" | awk '{printf "%03d\n", $1}') \
       <(awk '/^run=[0-9][0-9][0-9] PASS / {sub(/^run=/, "", $1); print $1}' \
           "$log_stage") >/dev/null || \
   [[ "$summary_lines" != 1 ]] || \
   [[ "$(tail -n 1 "$log_stage")" != "$summary_line" ]]; then
    printf '%s\n' \
        'Agent stress self-validation failed; refusing to publish a green transcript' >&2
    chmod 0600 "$log_stage"
    mv -f "$log_stage" "$log"
    printf '%s\n' 1 > "$exit_file"
    exit 1
fi

chmod 0600 "$log_stage"
mv -f "$log_stage" "$log"
printf '%s\n' 0 > "$exit_file"
cat "$log"
