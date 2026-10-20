#!/usr/bin/env bash
set -euo pipefail

if [[ ${1:-} == --help ]]; then
    cat <<'HELP'
Usage: tools/run-ratox-pacing-lab.sh

Sweeps Ratox research bursts across pacing intervals and packet sizes under
the controlled adversity profile. Each cell reuses the safe two-namespace
impairment laboratory and retains its complete report, qdisc counters, seeds,
and hashes. UDP uses a larger finite bulk transfer so the complete burst stays
inside the measured bulk interval; TCP is already relay/impairment limited.

Environment:
  IOTOX_BINARY                    source-linked standalone executable
  IOTOX_PACING_SPACINGS_MS        comma list (default 2,5,10,20,40)
  IOTOX_PACING_PACKET_BYTES       comma list (default 64,1200)
  IOTOX_PACING_MODES              comma list (default udp,tcp)
  IOTOX_PACING_PROFILE            impairment profile (default adversity)
  IOTOX_PACING_BURST_COUNT        packets per carrier/state (default 64)
  IOTOX_PACING_DEADLINE_MS        final response window (default 2500)
  IOTOX_PACING_UDP_BYTES          finite bulk bytes (default 16777216)
  IOTOX_PACING_TCP_BYTES          finite bulk bytes (default 4194304)
  IOTOX_PACING_REPORT_DIR         private output directory

The tool never attaches a qdisc to a host or physical interface. The nested
laboratory owns exact namespace, veth, bridge, and NAT cleanup.
HELP
    exit 0
fi

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
binary=${IOTOX_BINARY:-"$root/dist/standalone/iotox"}
spacings_spec=${IOTOX_PACING_SPACINGS_MS:-2,5,10,20,40}
sizes_spec=${IOTOX_PACING_PACKET_BYTES:-64,1200}
modes_spec=${IOTOX_PACING_MODES:-udp,tcp}
profile=${IOTOX_PACING_PROFILE:-adversity}
burst_count=${IOTOX_PACING_BURST_COUNT:-64}
deadline_ms=${IOTOX_PACING_DEADLINE_MS:-2500}
udp_bytes=${IOTOX_PACING_UDP_BYTES:-16777216}
tcp_bytes=${IOTOX_PACING_TCP_BYTES:-4194304}
report_dir=${IOTOX_PACING_REPORT_DIR:-"$root/build/ratox-pacing-lab"}

[[ -x "$binary" ]] || { printf 'source-linked binary not found: %s\n' "$binary" >&2; exit 2; }
[[ "$spacings_spec" =~ ^[0-9]+(,[0-9]+)*$ ]] || exit 2
[[ "$sizes_spec" =~ ^[0-9]+(,[0-9]+)*$ ]] || exit 2
[[ "$modes_spec" =~ ^(udp|tcp)(,(udp|tcp))*$ ]] || exit 2
[[ "$profile" =~ ^(baseline|delay40|adversity|constrained)$ ]] || exit 2
for value_name in burst_count deadline_ms udp_bytes tcp_bytes; do
    value=${!value_name}
    [[ "$value" =~ ^[1-9][0-9]*$ ]] || exit 2
done
(( burst_count <= 128 && deadline_ms <= 10000 )) || exit 2
(( udp_bytes >= 4096 && udp_bytes % 4 == 0 )) || exit 2
(( tcp_bytes >= 4096 && tcp_bytes % 4 == 0 )) || exit 2

IFS=, read -r -a spacings <<<"$spacings_spec"
IFS=, read -r -a sizes <<<"$sizes_spec"
IFS=, read -r -a modes <<<"$modes_spec"
for spacing in "${spacings[@]}"; do
    (( spacing <= 1000 )) || exit 2
done
for size in "${sizes[@]}"; do
    (( size >= 10 && size <= 1200 )) || exit 2
done

install -d -m 0700 "$report_dir"
exec 9>"$report_dir/.pacing-lock"
chmod 0600 "$report_dir/.pacing-lock"
flock -n 9 || { printf 'another pacing lab owns %s\n' "$report_dir" >&2; exit 2; }

run_id=$(date -u +%Y%m%dT%H%M%SZ)-$(printf '%05x' "$(( (BASHPID ^ $(date +%s)) & 1048575 ))")
manifest="$report_dir/pacing-$run_id.tsv"
stage="$manifest.stage"
: >"$stage"
chmod 0600 "$stage"
cleanup() { rm -f -- "$stage"; }
trap cleanup EXIT INT TERM
record() { printf '%s\n' "$1" >>"$stage"; }

record $'schema\tiotox-ratox-pacing-matrix-v1'
record $'run-id\t'"$run_id"
record $'binary-sha256\t'"$(sha256sum "$binary" | cut -d' ' -f1)"
record $'spacings-ms\t'"$spacings_spec"
record $'packet-bytes\t'"$sizes_spec"
record $'modes\t'"$modes_spec"
record $'profile\t'"$profile"
record $'burst-count\t'"$burst_count"
record $'deadline-ms\t'"$deadline_ms"

for mode in "${modes[@]}"; do
    payload_bytes=$udp_bytes
    [[ "$mode" != tcp ]] || payload_bytes=$tcp_bytes
    for size in "${sizes[@]}"; do
        for spacing in "${spacings[@]}"; do
            cell="$report_dir/$run_id-$mode-b${size}-s${spacing}"
            install -d -m 0700 "$cell"
            printf 'pacing mode=%s bytes=%s spacing-ms=%s\n' "$mode" "$size" "$spacing"
            IOTOX_BINARY="$binary" \
            IOTOX_IMPAIRMENT_PROFILES="$profile" \
            IOTOX_IMPAIRMENT_MODES="$mode" \
            IOTOX_IMPAIRMENT_SAMPLES=1 \
            IOTOX_IMPAIRMENT_BURST_COUNT="$burst_count" \
            IOTOX_IMPAIRMENT_BURST_SPACING_MS="$spacing" \
            IOTOX_IMPAIRMENT_BURST_PACKET_BYTES="$size" \
            IOTOX_IMPAIRMENT_DEADLINE_MS="$deadline_ms" \
            IOTOX_IMPAIRMENT_BYTES="$payload_bytes" \
            IOTOX_IMPAIRMENT_CONSTRAINED_BYTES="$payload_bytes" \
            IOTOX_IMPAIRMENT_TIMEOUT_SECONDS=600 \
            IOTOX_IMPAIRMENT_REPORT_DIR="$cell" \
                "$root/tools/run-ratox-impairment-lab.sh"
            inner_manifest=$(find "$cell" -maxdepth 1 -type f -name 'matrix-*.tsv' -print)
            [[ -n "$inner_manifest" && $(printf '%s\n' "$inner_manifest" | wc -l) == 1 ]] || exit 1
            inner_report=$(find "$cell" -maxdepth 1 -type f -name "*-$mode-$profile.tsv" -print)
            [[ -n "$inner_report" && $(printf '%s\n' "$inner_report" | wc -l) == 1 ]] || exit 1
            record $'cell\t'"$mode"$'\tpacket-bytes\t'"$size"$'\tspacing-ms\t'"$spacing"$'\tpayload-bytes\t'"$payload_bytes"$'\tmanifest\t'"${inner_manifest#"$report_dir/"}"$'\tmanifest-sha256\t'"$(sha256sum "$inner_manifest" | cut -d' ' -f1)"$'\treport\t'"${inner_report#"$report_dir/"}"$'\treport-sha256\t'"$(sha256sum "$inner_report" | cut -d' ' -f1)"
            while IFS= read -r summary; do
                record $'result\t'"$mode"$'\tpacket-bytes\t'"$size"$'\tspacing-ms\t'"$spacing"$'\t'"$summary"
            done < <(awk -F '\t' '$1 == "burst-summary" && $2 ~ /-bulk$/ {print}' "$inner_report")
        done
    done
done

record $'matrix\tpass'
mv -- "$stage" "$manifest"
trap - EXIT INT TERM
printf 'manifest=%s\n' "$manifest"
