#!/usr/bin/env bash
set -euo pipefail

if [[ ${1:-} == --help ]]; then
    cat <<'HELP'
Usage: tools/run-ratox-latency-lab.sh [--reuse-keys|--fresh-keys]

Runs the next genuine-provider latency gate twice: observed direct UDP and
forced TCP-only. Each mode measures daemon-monotonic Ratox text-to-read-receipt
RTT plus fixed lossless/lossy custom-packet echo RTT while idle and during one
active finite-file transfer. The underlying
four-route fixture verifies all eight route directions even though latency is
sampled on route zero.

Environment:
  IOTOX_BINARY                    source-linked executable
  IOTOX_RATOX_LATENCY_SAMPLES     samples per state (default 40)
  IOTOX_RATOX_LATENCY_BYTES       bulk payload bytes (default 67108864)
  IOTOX_RATOX_LATENCY_REPORT_DIR  output directory
  IOTOX_FOUR_ROUTE_MAX_ITERATE_MS owner sleep cap under test (default 20)
  IOTOX_FOUR_ROUTE_PROBE_DEADLINE_MS custom-packet deadline (default 250)
  IOTOX_FOUR_ROUTE_KEY_CACHE      private reusable test identity cache

This gate compares candidate Ratox carriers. It does not claim
keypress-to-render latency or qualify a future lossy terminal protocol.
HELP
    exit 0
fi

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
key_option=--reuse-keys
if (($# != 0)); then
    case "$1" in
        --reuse-keys|--fresh-keys) key_option=$1 ;;
        *)
            printf 'unknown argument: %s\n' "$1" >&2
            exit 2
            ;;
    esac
    shift
fi
if (($# != 0)); then
    printf '%s\n' 'too many arguments' >&2
    exit 2
fi

samples=${IOTOX_RATOX_LATENCY_SAMPLES:-40}
payload_bytes=${IOTOX_RATOX_LATENCY_BYTES:-67108864}
report_dir=${IOTOX_RATOX_LATENCY_REPORT_DIR:-"$root/build/ratox-latency-lab"}
stamp=$(date +%Y%m%dT%H%M%S)
install -d -m 0700 "$report_dir"

run_mode() {
    local mode=$1
    local tcp_only=$2
    local report="$report_dir/ratox-latency-$mode-$stamp.tsv"
    IOTOX_FOUR_ROUTE_BYTES="$payload_bytes" \
    IOTOX_FOUR_ROUTE_TRIALS=1 \
    IOTOX_FOUR_ROUTE_LATENCY_SAMPLES="$samples" \
    IOTOX_FOUR_ROUTE_LATENCY_ONLY=1 \
    IOTOX_FOUR_ROUTE_TCP_ONLY="$tcp_only" \
    IOTOX_FOUR_ROUTE_REPORT="$report" \
        "$root/tools/run-four-route-lab.sh" "$key_option"
}

run_mode udp 0
run_mode tcp 1
printf 'ratox-latency-lab=pass samples-per-state=%s payload-bytes=%s\n' \
    "$samples" "$payload_bytes"
