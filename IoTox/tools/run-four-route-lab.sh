#!/usr/bin/env bash
set -euo pipefail

if [[ ${1:-} == --help ]]; then
    cat <<'HELP'
Usage: tools/run-four-route-lab.sh [--reuse-keys|--fresh-keys] [--prepare-keys]

Starts four independent source-linked Tox route pairs between two logical
IoTox nodes. Every A route shares one stable device identity; every B route
shares another. It transfers a constant total payload through:

  one route / one stream
  one route / four streams
  two routes / two streams
  four routes / four streams

This is a founding-host laboratory, not a product bonding implementation. It
measures whether independent Tox connections escape a per-connection ceiling.
Set IOTOX_FOUR_ROUTE_STREAM_TOTALS to compare each requested total over one
route and evenly over all four routes.

Options:
  --reuse-keys   reuse private route/device baselines (default)
  --fresh-keys   generate all route identities and both device identities now
  --prepare-keys provision or validate the reusable baseline, then exit

Environment:
  IOTOX_BINARY                     source-linked executable
  IOTOX_FOUR_ROUTE_BYTES           total bytes per measured phase (default 8388608)
  IOTOX_FOUR_ROUTE_TRIALS          trials per topology (default 3)
  IOTOX_FOUR_ROUTE_STREAM_TOTALS   comma-separated concurrency sweep, e.g. 8,16,32,64
  IOTOX_FOUR_ROUTE_LATENCY_SAMPLES Ratox read-receipt RTT samples per state (default 0)
  IOTOX_FOUR_ROUTE_LATENCY_ONLY=1  run only idle and one-route bulk latency gate
  IOTOX_FOUR_ROUTE_MAX_ITERATE_MS  cap toxcore owner sleep (default 20)
  IOTOX_FOUR_ROUTE_PROBE_DEADLINE_MS custom-packet RTT deadline (default 250)
  IOTOX_FOUR_ROUTE_LATENCY_SEED    deterministic carrier-order seed (default 151515)
  IOTOX_FOUR_ROUTE_LATENCY_PROFILE report label for the applied path profile
  IOTOX_FOUR_ROUTE_BURST_COUNT     custom probes per reorder/loss burst (default 0)
  IOTOX_FOUR_ROUTE_BURST_SPACING_MS delay between burst sends (default 2)
  IOTOX_FOUR_ROUTE_BURST_PACKET_BYTES sized symmetric probe bytes (default 10)
  IOTOX_FOUR_ROUTE_A_NETNS         optional existing network namespace for A agents
  IOTOX_FOUR_ROUTE_B_NETNS         optional existing network namespace for B agents
  IOTOX_FOUR_ROUTE_TIMEOUT_SECONDS setup/per-phase deadline (default 300)
  IOTOX_FOUR_ROUTE_KEYS            reuse (default) or fresh
  IOTOX_FOUR_ROUTE_KEY_CACHE       private test-only cache directory
  IOTOX_FOUR_ROUTE_WORKDIR         explicit empty work directory
  IOTOX_FOUR_ROUTE_KEEP=1          retain work directory (contains secrets/data)
  IOTOX_FOUR_ROUTE_REPORT          atomic TSV report path
  IOTOX_FOUR_ROUTE_TCP_ONLY=1      disable UDP/discovery/DHT/hole punching

Payload files are sparse zero-filled regular files. Tox encryption removes
wire compressibility; sparse files deliberately reduce source-storage noise.
Never use production identities in this harness or publish its cache/workdir.
HELP
    exit 0
fi

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
# shellcheck disable=SC1091
source "$root/dependencies.lock"

binary=${IOTOX_BINARY:-"$root/dist/standalone/iotox"}
payload_bytes=${IOTOX_FOUR_ROUTE_BYTES:-8388608}
trials=${IOTOX_FOUR_ROUTE_TRIALS:-3}
stream_totals_spec=${IOTOX_FOUR_ROUTE_STREAM_TOTALS:-}
latency_samples=${IOTOX_FOUR_ROUTE_LATENCY_SAMPLES:-0}
latency_only=${IOTOX_FOUR_ROUTE_LATENCY_ONLY:-0}
maximum_iteration_ms=${IOTOX_FOUR_ROUTE_MAX_ITERATE_MS:-20}
probe_deadline_ms=${IOTOX_FOUR_ROUTE_PROBE_DEADLINE_MS:-250}
latency_seed=${IOTOX_FOUR_ROUTE_LATENCY_SEED:-151515}
latency_profile=${IOTOX_FOUR_ROUTE_LATENCY_PROFILE:-uncontrolled}
burst_count=${IOTOX_FOUR_ROUTE_BURST_COUNT:-0}
burst_spacing_ms=${IOTOX_FOUR_ROUTE_BURST_SPACING_MS:-2}
burst_packet_bytes=${IOTOX_FOUR_ROUTE_BURST_PACKET_BYTES:-10}
a_netns=${IOTOX_FOUR_ROUTE_A_NETNS:-}
b_netns=${IOTOX_FOUR_ROUTE_B_NETNS:-}
timeout_seconds=${IOTOX_FOUR_ROUTE_TIMEOUT_SECONDS:-300}
key_mode=${IOTOX_FOUR_ROUTE_KEYS:-reuse}
key_cache=${IOTOX_FOUR_ROUTE_KEY_CACHE:-"$root/.cache/four-route-lab/c-toxcore-$IOTOX_C_TOXCORE_VERSION"}
keep=${IOTOX_FOUR_ROUTE_KEEP:-0}
prepare_keys_only=0

while (($# != 0)); do
    case "$1" in
        --reuse-keys) key_mode=reuse ;;
        --fresh-keys) key_mode=fresh ;;
        --prepare-keys) prepare_keys_only=1 ;;
        *)
            printf 'unknown argument: %s\n' "$1" >&2
            exit 2
            ;;
    esac
    shift
done

case "$key_mode" in
    reuse|fresh) ;;
    *)
        printf 'IOTOX_FOUR_ROUTE_KEYS must be reuse or fresh, got: %s\n' "$key_mode" >&2
        exit 2
        ;;
esac
if [[ "$prepare_keys_only" == 1 && "$key_mode" != reuse ]]; then
    printf '%s\n' '--prepare-keys requires reusable-key mode' >&2
    exit 2
fi
if [[ ! "$payload_bytes" =~ ^[1-9][0-9]*$ ]] ||
   (( payload_bytes < 4096 || payload_bytes > 1073741824 || payload_bytes % 4 != 0 )); then
    printf 'IOTOX_FOUR_ROUTE_BYTES must be divisible by 4 and in 4096..1073741824\n' >&2
    exit 2
fi
if [[ ! "$trials" =~ ^[1-9][0-9]*$ ]] || (( trials > 9 )); then
    printf 'IOTOX_FOUR_ROUTE_TRIALS must be in 1..9\n' >&2
    exit 2
fi
if [[ ! "$timeout_seconds" =~ ^[1-9][0-9]*$ ]]; then
    printf 'IOTOX_FOUR_ROUTE_TIMEOUT_SECONDS must be positive\n' >&2
    exit 2
fi
if [[ ! "$latency_samples" =~ ^[0-9]+$ ]] || (( latency_samples > 10000 )); then
    printf 'IOTOX_FOUR_ROUTE_LATENCY_SAMPLES must be in 0..10000\n' >&2
    exit 2
fi
if [[ "$latency_only" != 0 && "$latency_only" != 1 ]]; then
    printf 'IOTOX_FOUR_ROUTE_LATENCY_ONLY must be 0 or 1\n' >&2
    exit 2
fi
if [[ "$latency_only" == 1 && "$latency_samples" == 0 ]]; then
    printf 'IOTOX_FOUR_ROUTE_LATENCY_ONLY requires positive latency samples\n' >&2
    exit 2
fi
if [[ ! "$maximum_iteration_ms" =~ ^[1-9][0-9]*$ ]] ||
   (( maximum_iteration_ms > 1000 )); then
    printf 'IOTOX_FOUR_ROUTE_MAX_ITERATE_MS must be in 1..1000\n' >&2
    exit 2
fi
if [[ ! "$probe_deadline_ms" =~ ^[1-9][0-9]*$ ]] ||
   (( probe_deadline_ms > 10000 )); then
    printf 'IOTOX_FOUR_ROUTE_PROBE_DEADLINE_MS must be in 1..10000\n' >&2
    exit 2
fi
if [[ ! "$latency_seed" =~ ^[0-9]+$ ]] || (( latency_seed > 2147483647 )); then
    printf 'IOTOX_FOUR_ROUTE_LATENCY_SEED must be in 0..2147483647\n' >&2
    exit 2
fi
if [[ ! "$latency_profile" =~ ^[A-Za-z0-9._-]{1,64}$ ]]; then
    printf 'IOTOX_FOUR_ROUTE_LATENCY_PROFILE must be a safe 1..64 byte label\n' >&2
    exit 2
fi
if [[ ! "$burst_count" =~ ^[0-9]+$ ]] || (( burst_count > 128 )); then
    printf 'IOTOX_FOUR_ROUTE_BURST_COUNT must be in 0..128\n' >&2
    exit 2
fi
if [[ ! "$burst_spacing_ms" =~ ^[0-9]+$ ]] ||
   (( burst_spacing_ms > 1000 )); then
    printf 'IOTOX_FOUR_ROUTE_BURST_SPACING_MS must be in 0..1000\n' >&2
    exit 2
fi
if [[ ! "$burst_packet_bytes" =~ ^[0-9]+$ ]] ||
   (( burst_packet_bytes < 10 || burst_packet_bytes > 1200 )); then
    printf 'IOTOX_FOUR_ROUTE_BURST_PACKET_BYTES must be in 10..1200\n' >&2
    exit 2
fi
for netns in "$a_netns" "$b_netns"; do
    if [[ -n "$netns" && ! "$netns" =~ ^[A-Za-z0-9._-]{1,64}$ ]]; then
        printf 'network namespace has an unsafe name: %s\n' "$netns" >&2
        exit 2
    fi
done
if [[ -n "$a_netns" || -n "$b_netns" ]]; then
    [[ -n "$a_netns" && -n "$b_netns" && "$a_netns" != "$b_netns" ]] || {
        printf 'A/B network namespaces must both be set and distinct\n' >&2
        exit 2
    }
    command -v sudo >/dev/null 2>&1 && command -v ip >/dev/null 2>&1 &&
        command -v setpriv >/dev/null 2>&1 && sudo -n true || {
        printf 'network namespace launch requires noninteractive sudo, ip, and setpriv\n' >&2
        exit 2
    }
    for netns in "$a_netns" "$b_netns"; do
        sudo -n ip netns list | awk '{print $1}' | grep -Fxq "$netns" || {
            printf 'network namespace does not exist: %s\n' "$netns" >&2
            exit 2
        }
    done
fi

declare -a stream_totals=()
active_transfer_limit=32
if [[ -n "$stream_totals_spec" ]]; then
    [[ "$stream_totals_spec" =~ ^[1-9][0-9]*(,[1-9][0-9]*)*$ ]] || {
        printf 'IOTOX_FOUR_ROUTE_STREAM_TOTALS must be a comma-separated positive-integer list\n' >&2
        exit 2
    }
    IFS=, read -r -a stream_totals <<<"$stream_totals_spec"
    declare -A seen_stream_totals=()
    for total in "${stream_totals[@]}"; do
        (( total <= 256 )) || {
            printf 'stream total exceeds c-toxcore file-pipe limit 256: %s\n' "$total" >&2
            exit 2
        }
        (( total % 4 == 0 )) || {
            printf 'stream total must be divisible over four routes: %s\n' "$total" >&2
            exit 2
        }
        (( payload_bytes % total == 0 && payload_bytes / total >= 4096 )) || {
            printf 'payload must divide into at least 4096 bytes for stream total %s\n' "$total" >&2
            exit 2
        }
        [[ -z ${seen_stream_totals[$total]+present} ]] || {
            printf 'duplicate stream total: %s\n' "$total" >&2
            exit 2
        }
        seen_stream_totals[$total]=1
        (( total > active_transfer_limit )) && active_transfer_limit=$total
    done
fi

mkdir -p "$root/build"
command -v flock >/dev/null 2>&1 || {
    printf '%s\n' 'flock is required to serialize the four-route laboratory' >&2
    exit 2
}
exec 9>"$root/build/.four-route-lab.lock"
if ! flock -n 9; then
    printf '%s\n' 'another four-route laboratory run already owns the host fixture' >&2
    exit 75
fi

if [[ -n ${IOTOX_FOUR_ROUTE_WORKDIR:-} ]]; then
    work=$IOTOX_FOUR_ROUTE_WORKDIR
    if [[ -e "$work" ]]; then
        [[ -d "$work" && ! -L "$work" && -z $(find "$work" -mindepth 1 -maxdepth 1 -print -quit) ]] || {
            printf 'explicit four-route work directory must be an empty real directory: %s\n' "$work" >&2
            exit 2
        }
        chmod 0700 "$work"
    else
        install -d -m 0700 "$work"
    fi
else
    work=$(mktemp -d)
fi

report=${IOTOX_FOUR_ROUTE_REPORT:-"$root/build/four-route-lab/four-route-lab-$(date +%Y%m%dT%H%M%S).tsv"}
if [[ -e "$report" || -L "$report" ]]; then
    printf 'four-route report already exists: %s\n' "$report" >&2
    exit 2
fi
install -d -m 0700 "$(dirname "$report")"
report_stage=$(mktemp "$(dirname "$report")/.four-route-report.XXXXXX")
chmod 0600 "$report_stage"

declare -a a_pid=()
declare -a b_pid=()
declare -a a_metric_pid=()
declare -a b_metric_pid=()
declare -a a_runtime=()
declare -a b_runtime=()
declare -a a_state=()
declare -a b_state=()
declare -a a_identity=()
declare -a b_identity=()
declare -a a_address=()
declare -a b_address=()
declare -a a_key=()
declare -a b_key=()
declare -a samples_one=()
declare -a samples_one_four=()
declare -a samples_two=()
declare -a samples_four=()
declare -A sweep_samples=()
declare -A sweep_data_samples=()

provision_pid=
provision_workspace=
publish_workspace=
cache_digest_before=
run_sequence=0
latency_bulk_pending=1

record() {
    printf '%s\n' "$*"
    printf '%s\n' "$*" >>"$report_stage"
}

fail() {
    printf 'four-route-lab=fail detail=%s\n' "$*" >&2
    find "$work" -type f -name '*.log' -print 2>/dev/null | sort | while IFS= read -r log; do
        printf '\n--- %s (tail) ---\n' "$log" >&2
        tail -n 120 "$log" >&2
    done
    exit 1
}

cleanup() {
    if [[ -n "$provision_pid" ]] && kill -0 "$provision_pid" 2>/dev/null; then
        kill "$provision_pid" 2>/dev/null || true
        wait "$provision_pid" 2>/dev/null || true
    fi
    # A namespace launch has a root setns/sudo parent waiting on the actual
    # unprivileged daemon. Ask every reachable daemon to stop first so failure
    # cleanup does not strand the child while waiting on its wrapper.
    for runtime in "${a_runtime[@]}" "${b_runtime[@]}"; do
        if [[ -n "$runtime" && -S "$runtime/control.sock" ]]; then
            "$binary" --runtime "$runtime" --timeout-ms 1000 stop \
                >/dev/null 2>&1 || true
        fi
    done
    for pid in "${a_pid[@]}" "${b_pid[@]}"; do
        if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
            kill "$pid" 2>/dev/null || true
            wait "$pid" 2>/dev/null || true
        fi
    done
    if [[ -n "$provision_workspace" && -d "$provision_workspace" ]]; then
        rm -rf "$provision_workspace"
    fi
    if [[ -n "$publish_workspace" && -d "$publish_workspace" ]]; then
        rm -rf "$publish_workspace"
    fi
    if [[ -n "$report_stage" && -f "$report_stage" ]]; then
        rm -f "$report_stage"
    fi
    if [[ "$keep" != 1 && -z ${IOTOX_FOUR_ROUTE_WORKDIR:-} ]]; then
        rm -rf "$work"
    else
        printf 'four-route-workdir=%s\n' "$work"
    fi
}
trap cleanup EXIT

field() {
    local name=$1
    sed -n "s/^${name}=//p" | head -n 1
}

private_directory_is_safe() {
    local path=$1
    [[ -d "$path" && ! -L "$path" ]] &&
        [[ $(stat -c '%u' -- "$path") == "$(id -u)" ]] &&
        [[ $(stat -c '%a' -- "$path") == 700 ]]
}

private_file_is_safe() {
    local path=$1
    [[ -f "$path" && ! -L "$path" && -s "$path" ]] &&
        [[ $(stat -c '%u' -- "$path") == "$(id -u)" ]] &&
        [[ $(stat -c '%a' -- "$path") == 600 ]]
}

validate_cached_baseline() {
    local current=$1
    private_directory_is_safe "$current" ||
        fail "four-route cache generation is not an owned 0700 directory: $current"
    local expected=$'a0.toxsave\na1.toxsave\na2.toxsave\na3.toxsave\nb0.toxsave\nb1.toxsave\nb2.toxsave\nb3.toxsave\nnode-a.identity\nnode-b.identity'
    local entries
    entries=$(cd "$current" && find . -mindepth 1 -maxdepth 1 -printf '%P\n' | LC_ALL=C sort)
    [[ "$entries" == "$expected" ]] ||
        fail "four-route cache must contain exactly eight route states and two device identities: $current"
    local name
    for name in a0.toxsave a1.toxsave a2.toxsave a3.toxsave \
                b0.toxsave b1.toxsave b2.toxsave b3.toxsave \
                node-a.identity node-b.identity; do
        private_file_is_safe "$current/$name" ||
            fail "four-route cache file must be owned, nonempty, nonsymlink 0600: $current/$name"
    done
    ! cmp -s "$current/node-a.identity" "$current/node-b.identity" ||
        fail 'the two logical laboratory nodes cannot share one device identity'
    local distinct_states
    distinct_states=$(sha256sum "$current"/*.toxsave | awk '{print $1}' | sort -u | wc -l)
    [[ "$distinct_states" == 8 ]] ||
        fail 'the four-route cache does not contain eight distinct savedata files'
}

provision_peer_baseline() {
    local label=$1
    local directory=$2
    local runtime="$directory/run"
    local log="$directory/provision.log"
    local args=(
        run
        --runtime "$runtime"
        --state "$directory/device.toxsave"
        --identity "$directory/device.identity"
        --authority-ledger "$directory/authority.ledger"
        --command-store "$directory/commands.store"
        --run-ms 30000
    )
    if [[ ${IOTOX_FOUR_ROUTE_TCP_ONLY:-0} == 1 ]]; then
        args+=(--native-tcp-only)
    fi
    install -d -m 0700 "$directory"
    "$binary" "${args[@]}" >"$log" 2>&1 &
    provision_pid=$!
    local provision_deadline=$((SECONDS + 20))
    while (( SECONDS < provision_deadline )) && [[ ! -S "$runtime/control.sock" ]]; do
        kill -0 "$provision_pid" 2>/dev/null ||
            fail "route $label exited during baseline provisioning"
        sleep 0.05
    done
    [[ -S "$runtime/control.sock" ]] ||
        fail "route $label did not expose its provisioning control socket"
    "$binary" --runtime "$runtime" stop >/dev/null
    wait "$provision_pid" || fail "route $label did not stop cleanly after provisioning"
    provision_pid=
    private_file_is_safe "$directory/device.toxsave" ||
        fail "route $label did not create private Tox savedata"
    private_file_is_safe "$directory/device.identity" ||
        fail "route $label did not create a private device identity"
}

prepare_reusable_baseline() {
    if [[ -e "$key_cache" || -L "$key_cache" ]]; then
        private_directory_is_safe "$key_cache" ||
            fail "four-route key cache must be an owned nonsymlink 0700 directory: $key_cache"
    else
        install -d -m 0700 "$key_cache"
    fi
    exec 7>"$key_cache/.prepare.lock"
    chmod 0600 "$key_cache/.prepare.lock"
    flock 7

    local current="$key_cache/current"
    if [[ -e "$current" || -L "$current" ]]; then
        validate_cached_baseline "$current"
    else
        provision_workspace=$(mktemp -d "$key_cache/.provision.XXXXXX")
        chmod 0700 "$provision_workspace"
        provision_peer_baseline a0 "$provision_workspace/a0"
        provision_peer_baseline b0 "$provision_workspace/b0"
        install -m 0600 "$provision_workspace/a0/device.identity" \
            "$provision_workspace/node-a.identity"
        install -m 0600 "$provision_workspace/b0/device.identity" \
            "$provision_workspace/node-b.identity"
        local lane
        for lane in 1 2 3; do
            install -d -m 0700 "$provision_workspace/a$lane" "$provision_workspace/b$lane"
            install -m 0600 "$provision_workspace/node-a.identity" \
                "$provision_workspace/a$lane/device.identity"
            install -m 0600 "$provision_workspace/node-b.identity" \
                "$provision_workspace/b$lane/device.identity"
            provision_peer_baseline "a$lane" "$provision_workspace/a$lane"
            provision_peer_baseline "b$lane" "$provision_workspace/b$lane"
        done

        publish_workspace=$(mktemp -d "$key_cache/.publish.XXXXXX")
        chmod 0700 "$publish_workspace"
        install -m 0600 "$provision_workspace/node-a.identity" \
            "$publish_workspace/node-a.identity"
        install -m 0600 "$provision_workspace/node-b.identity" \
            "$publish_workspace/node-b.identity"
        for lane in 0 1 2 3; do
            install -m 0600 "$provision_workspace/a$lane/device.toxsave" \
                "$publish_workspace/a$lane.toxsave"
            install -m 0600 "$provision_workspace/b$lane/device.toxsave" \
                "$publish_workspace/b$lane.toxsave"
        done
        validate_cached_baseline "$publish_workspace"
        mv -- "$publish_workspace" "$current"
        publish_workspace=
        rm -rf "$provision_workspace"
        provision_workspace=
    fi
    flock -u 7
    exec 7>&-
    validate_cached_baseline "$current"
}

cached_baseline_digest() {
    (
        cd "$key_cache/current"
        sha256sum a0.toxsave a1.toxsave a2.toxsave a3.toxsave \
            b0.toxsave b1.toxsave b2.toxsave b3.toxsave \
            node-a.identity node-b.identity
    ) | sha256sum | cut -d' ' -f1
}

[[ -x "$binary" ]] || {
    printf 'source-linked binary not found: %s\n' "$binary" >&2
    exit 2
}
"$root/tools/verify-standalone.sh" "$binary" >/dev/null

if [[ "$key_mode" == reuse ]]; then
    prepare_reusable_baseline
    if [[ "$prepare_keys_only" == 1 ]]; then
        record "four-route-key-cache=ready"
        record "key-mode=reuse"
        record "provider-version=$IOTOX_C_TOXCORE_VERSION"
        record "route-count=4"
        mv -- "$report_stage" "$report"
        report_stage=
        printf 'report=%s\n' "$report"
        exit 0
    fi
    exec 8>"$key_cache/.run.lock"
    chmod 0600 "$key_cache/.run.lock"
    if ! flock -n 8; then
        fail "four-route test identities are already active: $key_cache"
    fi
    cache_digest_before=$(cached_baseline_digest)
fi

materialize_route_files() {
    local lane
    for lane in 0 1 2 3; do
        install -d -m 0700 "$work/a$lane" "$work/b$lane"
        a_runtime[$lane]="$work/a$lane/run"
        b_runtime[$lane]="$work/b$lane/run"
        a_state[$lane]="$work/a$lane/device.toxsave"
        b_state[$lane]="$work/b$lane/device.toxsave"
        a_identity[$lane]="$work/a$lane/device.identity"
        b_identity[$lane]="$work/b$lane/device.identity"
    done
    if [[ "$key_mode" == reuse ]]; then
        for lane in 0 1 2 3; do
            install -m 0600 "$key_cache/current/a$lane.toxsave" "${a_state[$lane]}"
            install -m 0600 "$key_cache/current/b$lane.toxsave" "${b_state[$lane]}"
            install -m 0600 "$key_cache/current/node-a.identity" "${a_identity[$lane]}"
            install -m 0600 "$key_cache/current/node-b.identity" "${b_identity[$lane]}"
        done
        return
    fi

    provision_peer_baseline fresh-a0 "$work/fresh-a0"
    provision_peer_baseline fresh-b0 "$work/fresh-b0"
    install -m 0600 "$work/fresh-a0/device.toxsave" "${a_state[0]}"
    install -m 0600 "$work/fresh-b0/device.toxsave" "${b_state[0]}"
    for lane in 0 1 2 3; do
        install -m 0600 "$work/fresh-a0/device.identity" "${a_identity[$lane]}"
        install -m 0600 "$work/fresh-b0/device.identity" "${b_identity[$lane]}"
    done
}

all_agents_alive() {
    local pid
    for pid in "${a_pid[@]}" "${b_pid[@]}"; do
        [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null || return 1
    done
}

wait_for() {
    local description=$1
    shift
    local wait_deadline=$((SECONDS + timeout_seconds))
    while (( SECONDS < wait_deadline )); do
        "$@" && return 0
        all_agents_alive || fail "an agent exited while waiting for $description"
        sleep 0.1
    done
    fail "timeout waiting for $description"
}

materialize_route_files

lab_uid=$(id -u)
lab_gid=$(id -g)
launch_agent() {
    local netns=$1
    shift
    if [[ -z "$netns" ]]; then
        exec "$binary" "$@"
    fi
    exec sudo -n ip netns exec "$netns" setpriv \
        --reuid "$lab_uid" --regid "$lab_gid" --init-groups -- \
        "$binary" "$@"
}

lane_sockets_ready() {
    local lane=$1
    [[ -S "${a_runtime[$lane]}/control.sock" &&
       -S "${b_runtime[$lane]}/control.sock" ]]
}

for lane in 0 1 2 3; do
    a_args=(
        run --runtime "${a_runtime[$lane]}" --state "${a_state[$lane]}"
        --identity "${a_identity[$lane]}"
        --authority-ledger "$work/a$lane/authority.ledger"
        --command-store "$work/a$lane/commands.store"
        --max-file-bytes "$payload_bytes"
        --max-active-sends "$active_transfer_limit"
        --max-active-receives "$active_transfer_limit"
        --max-pending-file-offers "$active_transfer_limit"
        --max-iterate-ms "$maximum_iteration_ms"
    )
    b_args=(
        run --runtime "${b_runtime[$lane]}" --state "${b_state[$lane]}"
        --identity "${b_identity[$lane]}"
        --authority-ledger "$work/b$lane/authority.ledger"
        --command-store "$work/b$lane/commands.store"
        --max-file-bytes "$payload_bytes"
        --max-active-sends "$active_transfer_limit"
        --max-active-receives "$active_transfer_limit"
        --max-pending-file-offers "$active_transfer_limit"
        --max-iterate-ms "$maximum_iteration_ms"
    )
    if [[ ${IOTOX_FOUR_ROUTE_TCP_ONLY:-0} == 1 ]]; then
        a_args+=(--native-tcp-only)
        b_args+=(--native-tcp-only)
    fi
    launch_agent "$a_netns" "${a_args[@]}" >"$work/a$lane.log" 2>&1 &
    a_pid[$lane]=$!
    launch_agent "$b_netns" "${b_args[@]}" >"$work/b$lane.log" 2>&1 &
    b_pid[$lane]=$!
    # toxcore discovers a free UDP port during construction. Starting several
    # owners concurrently in one network namespace creates a bind-selection
    # race; make each lane own its port before constructing the next lane.
    wait_for "lane $lane control sockets" lane_sockets_ready "$lane"
done

sockets_ready() {
    local lane
    for lane in 0 1 2 3; do
        [[ -S "${a_runtime[$lane]}/control.sock" &&
           -S "${b_runtime[$lane]}/control.sock" ]] || return 1
    done
}
wait_for 'all eight control sockets' sockets_ready

resolve_namespace_agent_pid() {
    local netns=$1 runtime=$2 pid cmdline
    while IFS= read -r pid; do
        [[ "$pid" =~ ^[1-9][0-9]*$ ]] || continue
        cmdline=$(sudo -n cat "/proc/$pid/cmdline" 2>/dev/null | tr '\0' '\n') ||
            continue
        if grep -Fxq -- "$runtime" <<<"$cmdline"; then
            printf '%s\n' "$pid"
            return 0
        fi
    done < <(sudo -n ip netns pids "$netns")
    return 1
}

for lane in 0 1 2 3; do
    if [[ -n "$a_netns" ]]; then
        a_metric_pid[$lane]=$(resolve_namespace_agent_pid \
            "$a_netns" "${a_runtime[$lane]}") ||
            fail "unable to resolve namespace process for A lane $lane"
        b_metric_pid[$lane]=$(resolve_namespace_agent_pid \
            "$b_netns" "${b_runtime[$lane]}") ||
            fail "unable to resolve namespace process for B lane $lane"
    else
        a_metric_pid[$lane]=${a_pid[$lane]}
        b_metric_pid[$lane]=${b_pid[$lane]}
    fi
done

declare -A route_addresses=()
node_a_device=
node_b_device=
for lane in 0 1 2 3; do
    a_address[$lane]=$("$binary" --runtime "${a_runtime[$lane]}" address | tr -d '\n')
    b_address[$lane]=$("$binary" --runtime "${b_runtime[$lane]}" address | tr -d '\n')
    [[ ${#a_address[$lane]} == 76 && ${#b_address[$lane]} == 76 ]] ||
        fail "lane $lane returned an invalid Tox address"
    a_key[$lane]=${a_address[$lane]:0:64}
    b_key[$lane]=${b_address[$lane]:0:64}
    route_addresses["${a_key[$lane]}"]=1
    route_addresses["${b_key[$lane]}"]=1
    current_a_device=$("$binary" --runtime "${a_runtime[$lane]}" identity | field device-public-key)
    current_b_device=$("$binary" --runtime "${b_runtime[$lane]}" identity | field device-public-key)
    if [[ "$lane" == 0 ]]; then
        node_a_device=$current_a_device
        node_b_device=$current_b_device
    fi
    [[ "$current_a_device" == "$node_a_device" && "$current_b_device" == "$node_b_device" ]] ||
        fail "lane $lane is not bound to the shared logical-node identities"
    [[ -z $("$binary" --runtime "${a_runtime[$lane]}" peers) &&
       -z $("$binary" --runtime "${b_runtime[$lane]}" peers) &&
       -z $("$binary" --runtime "${a_runtime[$lane]}" requests) &&
       -z $("$binary" --runtime "${b_runtime[$lane]}" requests) ]] ||
        fail "lane $lane baseline contains friendship/request state"
done
[[ ${#route_addresses[@]} == 8 ]] || fail 'the laboratory requires eight distinct Tox route keys'
[[ "$node_a_device" != "$node_b_device" ]] || fail 'logical nodes A and B share one device key'

for lane in 0 1 2 3; do
    "$binary" --runtime "${a_runtime[$lane]}" transport-peer-request \
        "${b_address[$lane]}" "IoTox four-route laboratory lane $lane" >/dev/null
    "$binary" --runtime "${b_runtime[$lane]}" transport-peer-request \
        "${a_address[$lane]}" "IoTox four-route laboratory lane $lane" >/dev/null
done

friend_records_ready() {
    local lane
    for lane in 0 1 2 3; do
        "$binary" --runtime "${a_runtime[$lane]}" peers 2>/dev/null |
            grep -q "${b_key[$lane]}" || return 1
        "$binary" --runtime "${b_runtime[$lane]}" peers 2>/dev/null |
            grep -q "${a_key[$lane]}" || return 1
    done
}
wait_for 'four bilateral friend records' friend_records_ready

sessions_ready() {
    local lane
    for lane in 0 1 2 3; do
        "$binary" --runtime "${a_runtime[$lane]}" session "${b_key[$lane]}" 2>/dev/null |
            grep -q '^state=confirmed$' || return 1
        "$binary" --runtime "${b_runtime[$lane]}" session "${a_key[$lane]}" 2>/dev/null |
            grep -q '^state=confirmed$' || return 1
    done
}
wait_for 'four confirmed bidirectional IoTox sessions' sessions_ready

route_connection_for() {
    local runtime=$1
    local key=$2
    "$binary" --runtime "$runtime" peers 2>/dev/null |
        awk -v key="$key" '$0 ~ "public-key=" key {for (i=1;i<=NF;i++) if ($i ~ /^connection=/) {sub(/^connection=/,"",$i); print $i; exit}}'
}

expected_connection=udp
if [[ ${IOTOX_FOUR_ROUTE_TCP_ONLY:-0} == 1 ]]; then
    expected_connection=tcp
fi
connections_ready() {
    local lane a_connection b_connection
    for lane in 0 1 2 3; do
        a_connection=$(route_connection_for "${a_runtime[$lane]}" "${b_key[$lane]}")
        b_connection=$(route_connection_for "${b_runtime[$lane]}" "${a_key[$lane]}")
        [[ "$a_connection" == "$expected_connection" &&
           "$b_connection" == "$expected_connection" ]] || return 1
    done
}
wait_for "all routes to report $expected_connection" connections_ready

record $'schema\tiotox-four-route-lab-v2'
record $'four-route-lab\trunning'
record $'provider\tc-toxcore-'"$IOTOX_C_TOXCORE_VERSION"
record $'key-mode\t'"$key_mode"
record $'transport-mode\t'"$([[ ${IOTOX_FOUR_ROUTE_TCP_ONLY:-0} == 1 ]] && printf tcp-only || printf udp-and-tcp)"
record $'required-observed-connection\t'"$expected_connection"
record $'payload-kind\tsparse-zero-filled-regular-file'
record $'payload-bytes-per-phase\t'"$payload_bytes"
record $'trials-per-topology\t'"$trials"
record $'stream-totals\t'"${stream_totals_spec:-standard-1x2x4}"
record $'active-transfer-limit-per-agent\t'"$active_transfer_limit"
record $'latency-samples-per-state\t'"$latency_samples"
record $'maximum-iteration-interval-ms\t'"$maximum_iteration_ms"
record $'custom-probe-deadline-ms\t'"$probe_deadline_ms"
record $'latency-profile\t'"$latency_profile"
record $'latency-order-seed\t'"$latency_seed"
record $'burst-count-per-carrier-state\t'"$burst_count"
record $'burst-spacing-ms\t'"$burst_spacing_ms"
record $'burst-packet-bytes\t'"$burst_packet_bytes"
record $'endpoint-topology\t'"$([[ -n "$a_netns" ]] && printf 'isolated-network-namespaces' || printf 'host-network')"
record $'latency-carriers\tratox-normal-text-read-receipt,custom-lossless-echo,custom-lossy-echo'
record $'latency-clock\tdaemon-monotonic-steady-clock'
record $'latency-meaning\tlocal-text-admission-through-remote-tox-observation-and-local-receipt-callback'
record $'provider-file-pipe-limit-per-friend\t256'
record $'node-a-device-public-key-sha256\t'"$(printf '%s' "$node_a_device" | sha256sum | cut -d' ' -f1)"
record $'node-b-device-public-key-sha256\t'"$(printf '%s' "$node_b_device" | sha256sum | cut -d' ' -f1)"
for lane in 0 1 2 3; do
    route_kind=$(route_connection_for "${a_runtime[$lane]}" "${b_key[$lane]}")
    record $'route\t'"$lane"$'\tconnection\t'"${route_kind:-unknown}"$'\ta-public-key-sha256\t'"$(printf '%s' "${a_key[$lane]}" | sha256sum | cut -d' ' -f1)"$'\tb-public-key-sha256\t'"$(printf '%s' "${b_key[$lane]}" | sha256sum | cut -d' ' -f1)"
done
record $'phase\ttrial\troutes\tstreams\tbytes\telapsed-ms\tbytes-per-second\tdata-window-ms\tdata-bytes-per-second\toffer-setup-ms\treceive-admission-ms\tcpu-ticks\tcontext-switches\trchar-bytes\twchar-bytes\ttransport-events\tdropped-events\thost-net-rx-plus-tx-bytes\tcompletion-ms'

collect_latency_samples() {
    local state=$1
    local count=$2
    local output=$3
    : >"$output"
    local sample carrier label response rtt_us timeout_ms selector order
    local state_offset=0
    [[ "$state" == bulk ]] && state_offset=12345
    local -a permutations=(
        'text lossless lossy'
        'text lossy lossless'
        'lossless text lossy'
        'lossless lossy text'
        'lossy text lossless'
        'lossy lossless text'
    )
    # The prior fixed order let a slow text receipt change the provider cadence
    # seen by the following custom samples. Select one of all six permutations
    # deterministically for each sample/state so the exact run is reproducible.
    for ((sample = 1; sample <= count; ++sample)); do
        selector=$((
            (latency_seed + sample * 1103515245 + state_offset) % 6
        ))
        order=${permutations[$selector]}
        printf 'latency-order\t%s\t%s\t%s\n' \
            "$state" "$sample" "${order// /,}" >>"$output"
        for carrier in $order; do
            label="$carrier-$state"
            # The client assigns three quarters of its local deadline to the
            # daemon-side probe. Ceil(4*d/3) maps back to exactly d.
            timeout_ms=$(( (probe_deadline_ms * 4 + 2) / 3 ))
            if [[ "$carrier" == text ]]; then
                if ! response=$("$binary" --runtime "${a_runtime[0]}" \
                    --timeout-ms "$timeout_ms" message-probe "${b_key[0]}" \
                    "IoTox latency $state sample $sample" 2>/dev/null); then
                    printf 'latency-drop\t%s\t%s\tdeadline-us\t%s\n' \
                        "$label" "$sample" "$((probe_deadline_ms * 1000))" \
                        >>"$output"
                    continue
                fi
            else
                if ! response=$("$binary" --runtime "${a_runtime[0]}" \
                    --timeout-ms "$timeout_ms" packet-probe "${b_key[0]}" \
                    "$carrier" 2>/dev/null); then
                    printf 'latency-drop\t%s\t%s\tdeadline-us\t%s\n' \
                        "$label" "$sample" "$((probe_deadline_ms * 1000))" \
                        >>"$output"
                    continue
                fi
            fi
            rtt_us=$(printf '%s' "$response" | field rtt-us)
            [[ "$rtt_us" =~ ^[0-9]+$ ]] || return 1
            printf 'latency-sample\t%s\t%s\t%s\n' \
                "$label" "$sample" "$rtt_us" >>"$output"
        done
    done

    if (( burst_count != 0 )); then
        local burst_timeout_ms=$((
            probe_deadline_ms + burst_spacing_ms * (burst_count - 1) + 500
        ))
        local first_carrier=lossless second_carrier=lossy line
        if (( (latency_seed + state_offset) % 2 != 0 )); then
            first_carrier=lossy
            second_carrier=lossless
        fi
        for carrier in "$first_carrier" "$second_carrier"; do
            label="$carrier-$state"
            printf 'burst-order\t%s\t%s\n' "$state" "$carrier" >>"$output"
            if ! response=$("$binary" --runtime "${a_runtime[0]}" \
                --timeout-ms "$burst_timeout_ms" packet-probe-burst \
                "${b_key[0]}" "$carrier" "$burst_count" \
                "$burst_spacing_ms" "$probe_deadline_ms" \
                "$burst_packet_bytes" 2>/dev/null); then
                printf 'burst-error\t%s\trequest-failed\n' "$label" >>"$output"
                continue
            fi
            while IFS= read -r line; do
                [[ "$line" == burst-probe$'\t'* ]] || return 1
                printf 'burst-sample\t%s\t%s\n' \
                    "$label" "${line#burst-probe$'\t'}" >>"$output"
            done <<<"$response"
        done
    fi
}

append_latency_samples() {
    local input=$1
    local line
    while IFS= read -r line; do
        record "$line"
    done <"$input"
}

latency_order_statistic() {
    local label=$1
    local percentile=$2
    local -a values=()
    mapfile -t values < <(
        awk -F '\t' -v label="$label" \
            '$1 == "latency-sample" && $2 == label {print $4}' \
            "$report_stage" | sort -n
    )
    local count=${#values[@]}
    (( count != 0 )) || return 1
    local rank=$(( (count * percentile + 99) / 100 ))
    (( rank < 1 )) && rank=1
    printf '%s\n' "${values[$((rank - 1))]}"
}

burst_order_statistic() {
    local label=$1
    local percentile=$2
    local -a values=()
    mapfile -t values < <(
        awk -F '\t' -v label="$label" \
            '$1 == "burst-sample" && $2 == label && $8 != "miss" {print $8}' \
            "$report_stage" | sort -n
    )
    local count=${#values[@]}
    (( count != 0 )) || return 1
    local rank=$(( (count * percentile + 99) / 100 ))
    (( rank < 1 )) && rank=1
    printf '%s\n' "${values[$((rank - 1))]}"
}

burst_reorder_inversions() {
    local label=$1
    awk -F '\t' -v label="$label" '
        $1 == "burst-sample" && $2 == label && $8 != "miss" {
            count++
            ordinal[count] = $4 + 0
            rank[count] = $10 + 0
        }
        END {
            inversions = 0
            for (i = 1; i <= count; ++i) {
                for (j = i + 1; j <= count; ++j) {
                    if (ordinal[i] < ordinal[j] && rank[i] > rank[j]) {
                        inversions++
                    }
                }
            }
            print inversions + 0
        }
    ' "$report_stage"
}

process_metric_sum() {
    local metric=$1
    local sum=0
    local pid value
    for pid in "${a_metric_pid[@]}" "${b_metric_pid[@]}"; do
        case "$metric" in
            cpu)
                value=$(awk '{print $14 + $15}' "/proc/$pid/stat")
                ;;
            context)
                value=$(awk '/^(voluntary|nonvoluntary)_ctxt_switches:/ {sum += $2} END {print sum + 0}' "/proc/$pid/status")
                ;;
            rchar|wchar)
                if [[ -n "$a_netns" ]]; then
                    # setns requires privilege and the subsequent setuid marks
                    # the process nondumpable. The originating user can still
                    # read stat/status, but Linux correctly protects proc/io;
                    # use the already-required noninteractive sudo boundary.
                    value=$(sudo -n awk -v key="$metric:" \
                        '$1 == key {print $2}' "/proc/$pid/io")
                else
                    value=$(awk -v key="$metric:" \
                        '$1 == key {print $2}' "/proc/$pid/io")
                fi
                ;;
            *) return 2 ;;
        esac
        sum=$((sum + value))
    done
    printf '%s\n' "$sum"
}

transport_event_sum() {
    local sum=0 lane status a_events b_events
    for lane in 0 1 2 3; do
        status=$("$binary" --runtime "${a_runtime[$lane]}" status)
        a_events=$(printf '%s' "$status" | field event-count)
        status=$("$binary" --runtime "${b_runtime[$lane]}" status)
        b_events=$(printf '%s' "$status" | field event-count)
        sum=$((sum + a_events + b_events))
    done
    printf '%s\n' "$sum"
}

dropped_event_sum() {
    local sum=0 lane status a_dropped b_dropped
    for lane in 0 1 2 3; do
        status=$("$binary" --runtime "${a_runtime[$lane]}" status)
        a_dropped=$(printf '%s' "$status" | field dropped-event-count)
        status=$("$binary" --runtime "${b_runtime[$lane]}" status)
        b_dropped=$(printf '%s' "$status" | field dropped-event-count)
        sum=$((sum + a_dropped + b_dropped))
    done
    printf '%s\n' "$sum"
}

host_network_bytes() {
    awk 'NR > 2 {receive += $2; transmit += $10} END {printf "%.0f\n", receive + transmit}' /proc/net/dev
}

transport_iteration_sum() {
    local sum=0 lane status iterations
    for lane in 0 1 2 3; do
        status=$("$binary" --runtime "${a_runtime[$lane]}" status)
        iterations=$(printf '%s' "$status" | field transport-iteration-count)
        sum=$((sum + iterations))
        status=$("$binary" --runtime "${b_runtime[$lane]}" status)
        iterations=$(printf '%s' "$status" | field transport-iteration-count)
        sum=$((sum + iterations))
    done
    printf '%s\n' "$sum"
}

if (( latency_samples != 0 )); then
    idle_latency="$work/latency-idle.tsv"
    idle_cpu_before=$(process_metric_sum cpu)
    idle_context_before=$(process_metric_sum context)
    idle_iterations_before=$(transport_iteration_sum)
    idle_started_ms=$(date +%s%3N)
    collect_latency_samples idle "$latency_samples" "$idle_latency" ||
        fail 'idle Ratox read-receipt latency sampling failed'
    idle_ended_ms=$(date +%s%3N)
    idle_iterations_after=$(transport_iteration_sum)
    idle_context_after=$(process_metric_sum context)
    idle_cpu_after=$(process_metric_sum cpu)
    append_latency_samples "$idle_latency"
    record $'latency-idle-window\tsamples\t'"$latency_samples"$'\telapsed-ms\t'"$((idle_ended_ms - idle_started_ms))"$'\tcpu-ticks\t'"$((idle_cpu_after - idle_cpu_before))"$'\tcontext-switches\t'"$((idle_context_after - idle_context_before))"$'\ttox-iterations\t'"$((idle_iterations_after - idle_iterations_before))"
fi

offer_number_for() {
    local lane=$1
    local filename=$2
    local output line
    output=$("$binary" --runtime "${b_runtime[$lane]}" files 2>/dev/null) || return 1
    while IFS= read -r line; do
        if [[ "$line" == *'direction=incoming state=offered'* &&
              "$line" == *"filename=$filename"* ]]; then
            sed -n 's/.*file-number=\([0-9][0-9]*\).*/\1/p' <<<"$line"
            return 0
        fi
    done <<<"$output"
    return 1
}

run_phase() {
    local phase=$1
    local trial=$2
    local route_count=$3
    local streams_per_route=$4
    local task_count=$((route_count * streams_per_route))
    local shard_bytes=$((payload_bytes / task_count))
    local phase_tag="t${trial}-${phase}-$run_sequence"
    run_sequence=$((run_sequence + 1))

    local -a task_lane=()
    local -a source=()
    local -a destination=()
    local -a filename=()
    local -a file_number=()
    local -a completed=()
    local -a completion_ms=()
    local route stream task=0
    install -d -m 0700 "$work/payload"
    for ((route = 0; route < route_count; ++route)); do
        for ((stream = 0; stream < streams_per_route; ++stream)); do
            task_lane[$task]=$route
            source[$task]="$work/payload/$phase_tag-r$route-s$stream.src"
            destination[$task]="$work/payload/$phase_tag-r$route-s$stream.dst"
            filename[$task]=$(basename "${source[$task]}")
            truncate -s "$shard_bytes" "${source[$task]}"
            chmod 0600 "${source[$task]}"
            completed[$task]=0
            completion_ms[$task]=0
            task=$((task + 1))
        done
    done

    local cpu_before context_before rchar_before wchar_before events_before dropped_before net_before
    cpu_before=$(process_metric_sum cpu)
    context_before=$(process_metric_sum context)
    rchar_before=$(process_metric_sum rchar)
    wchar_before=$(process_metric_sum wchar)
    events_before=$(transport_event_sum)
    dropped_before=$(dropped_event_sum)
    net_before=$(host_network_bytes)
    local started_ms
    started_ms=$(date +%s%3N)

    local -a command_pids=()
    # Admit at most one control client per route at a time. The experiment is
    # about simultaneous Tox files, not the Unix listen backlog shared by a
    # burst of short-lived CLI processes.
    for ((stream = 0; stream < streams_per_route; ++stream)); do
        command_pids=()
        for ((route = 0; route < route_count; ++route)); do
            task=$((route * streams_per_route + stream))
            "$binary" --runtime "${a_runtime[$route]}" file-send \
                "${b_key[$route]}" "${source[$task]}" \
                >"$work/$phase_tag-send-$task.log" 2>&1 &
            command_pids[$route]=$!
        done
        for ((route = 0; route < route_count; ++route)); do
            task=$((route * streams_per_route + stream))
            wait "${command_pids[$route]}" ||
                fail "$phase trial $trial file-send $task failed"
        done
    done

    local phase_deadline=$((SECONDS + timeout_seconds))
    for ((task = 0; task < task_count; ++task)); do
        route=${task_lane[$task]}
        while (( SECONDS < phase_deadline )); do
            number=$(offer_number_for "$route" "${filename[$task]}" || true)
            if [[ "$number" =~ ^[0-9]+$ ]]; then
                file_number[$task]=$number
                break
            fi
            all_agents_alive || fail "an agent exited while waiting for $phase offers"
            sleep 0.02
        done
        [[ ${file_number[$task]:-} =~ ^[0-9]+$ ]] ||
            fail "$phase trial $trial did not expose offer $task"
    done

    local offer_ready_ms
    offer_ready_ms=$(date +%s%3N)
    command_pids=()
    for ((stream = 0; stream < streams_per_route; ++stream)); do
        command_pids=()
        for ((route = 0; route < route_count; ++route)); do
            task=$((route * streams_per_route + stream))
            "$binary" --runtime "${b_runtime[$route]}" file-receive \
                "${a_key[$route]}" "${file_number[$task]}" "${destination[$task]}" \
                >"$work/$phase_tag-receive-$task.log" 2>&1 &
            command_pids[$route]=$!
        done
        for ((route = 0; route < route_count; ++route)); do
            task=$((route * streams_per_route + stream))
            wait "${command_pids[$route]}" ||
                fail "$phase trial $trial file-receive $task failed"
        done
    done
    local admission_ended_ms
    admission_ended_ms=$(date +%s%3N)

    local latency_pid= latency_output=
    if (( latency_samples != 0 && latency_bulk_pending == 1 )); then
        latency_bulk_pending=0
        latency_output="$work/latency-bulk.tsv"
        collect_latency_samples bulk "$latency_samples" "$latency_output" &
        latency_pid=$!
    fi

    local remaining=$task_count now_ms size
    while (( SECONDS < phase_deadline && remaining != 0 )); do
        for ((task = 0; task < task_count; ++task)); do
            [[ ${completed[$task]} == 0 ]] || continue
            if [[ -f "${destination[$task]}" ]]; then
                size=$(stat -c '%s' -- "${destination[$task]}")
                if [[ "$size" == "$shard_bytes" ]]; then
                    now_ms=$(date +%s%3N)
                    completion_ms[$task]=$((now_ms - started_ms))
                    completed[$task]=1
                    remaining=$((remaining - 1))
                fi
            fi
        done
        (( remaining == 0 )) && break
        all_agents_alive || fail "an agent exited during $phase trial $trial"
        sleep 0.02
    done
    (( remaining == 0 )) || fail "$phase trial $trial transfer deadline expired"

    # Freeze transfer timing and process/host counters when the last payload
    # reaches its destination. Latency sampling is an overlapping observer and
    # may intentionally continue after a fast transfer; waiting for it must not
    # inflate the transfer's elapsed or throughput result.
    local ended_ms
    ended_ms=$(date +%s%3N)
    local cpu_after context_after rchar_after wchar_after events_after dropped_after net_after
    cpu_after=$(process_metric_sum cpu)
    context_after=$(process_metric_sum context)
    rchar_after=$(process_metric_sum rchar)
    wchar_after=$(process_metric_sum wchar)
    net_after=$(host_network_bytes)
    events_after=$(transport_event_sum)
    dropped_after=$(dropped_event_sum)

    if [[ -n "$latency_pid" ]]; then
        wait "$latency_pid" || fail 'bulk Ratox read-receipt latency sampling failed'
        append_latency_samples "$latency_output"
    fi
    local elapsed_ms=$((ended_ms - started_ms))
    local data_window_ms=$((ended_ms - offer_ready_ms))
    local offer_setup_ms=$((offer_ready_ms - started_ms))
    local receive_admission_ms=$((admission_ended_ms - offer_ready_ms))

    for ((task = 0; task < task_count; ++task)); do
        cmp -s "${source[$task]}" "${destination[$task]}" ||
            fail "$phase trial $trial payload $task differs"
    done

    local cleanup_deadline=$((SECONDS + 20)) all_empty
    while (( SECONDS < cleanup_deadline )); do
        all_empty=1
        for ((route = 0; route < route_count; ++route)); do
            if [[ -n $("$binary" --runtime "${a_runtime[$route]}" files 2>/dev/null) ||
                  -n $("$binary" --runtime "${b_runtime[$route]}" files 2>/dev/null) ]]; then
                all_empty=0
                break
            fi
        done
        [[ "$all_empty" == 1 ]] && break
        sleep 0.02
    done
    [[ "$all_empty" == 1 ]] || fail "$phase trial $trial live transfer cleanup did not converge"

    local bytes_per_second=$((payload_bytes * 1000 / elapsed_ms))
    local data_bytes_per_second=$((payload_bytes * 1000 / data_window_ms))
    local completions
    completions=$(IFS=,; printf '%s' "${completion_ms[*]}")

    record "$phase"$'\t'"$trial"$'\t'"$route_count"$'\t'"$task_count"$'\t'"$payload_bytes"$'\t'"$elapsed_ms"$'\t'"$bytes_per_second"$'\t'"$data_window_ms"$'\t'"$data_bytes_per_second"$'\t'"$offer_setup_ms"$'\t'"$receive_admission_ms"$'\t'"$((cpu_after - cpu_before))"$'\t'"$((context_after - context_before))"$'\t'"$((rchar_after - rchar_before))"$'\t'"$((wchar_after - wchar_before))"$'\t'"$((events_after - events_before))"$'\t'"$((dropped_after - dropped_before))"$'\t'"$((net_after - net_before))"$'\t'"$completions"

    case "$phase" in
        one-route-one-stream) samples_one+=("$elapsed_ms") ;;
        one-route-four-streams) samples_one_four+=("$elapsed_ms") ;;
        two-routes) samples_two+=("$elapsed_ms") ;;
        four-routes) samples_four+=("$elapsed_ms") ;;
        *)
            sweep_samples[$phase]="${sweep_samples[$phase]-}$elapsed_ms "
            sweep_data_samples[$phase]="${sweep_data_samples[$phase]-}$data_window_ms "
            ;;
    esac

    for ((task = 0; task < task_count; ++task)); do
        rm -f -- "${source[$task]}" "${destination[$task]}"
    done
}

if [[ "$latency_only" == 1 ]]; then
    run_phase latency-bulk 1 1 1
elif (( ${#stream_totals[@]} == 0 )); then
    for ((trial = 1; trial <= trials; ++trial)); do
        case $((trial % 3)) in
            1)
                run_phase one-route-one-stream "$trial" 1 1
                run_phase two-routes "$trial" 2 1
                run_phase four-routes "$trial" 4 1
                run_phase one-route-four-streams "$trial" 1 4
                ;;
            2)
                run_phase four-routes "$trial" 4 1
                run_phase one-route-four-streams "$trial" 1 4
                run_phase two-routes "$trial" 2 1
                run_phase one-route-one-stream "$trial" 1 1
                ;;
            0)
                run_phase two-routes "$trial" 2 1
                run_phase one-route-one-stream "$trial" 1 1
                run_phase one-route-four-streams "$trial" 1 4
                run_phase four-routes "$trial" 4 1
                ;;
        esac
    done
else
    for ((trial = 1; trial <= trials; ++trial)); do
        declare -a ordered_totals=()
        if (( trial % 2 == 1 )); then
            ordered_totals=("${stream_totals[@]}")
        else
            for ((index = ${#stream_totals[@]} - 1; index >= 0; --index)); do
                ordered_totals+=("${stream_totals[$index]}")
            done
        fi
        index=0
        for total in "${ordered_totals[@]}"; do
            one_phase="one-route-${total}-streams"
            four_phase="four-routes-${total}-streams"
            if (( (trial + index) % 2 == 0 )); then
                run_phase "$one_phase" "$trial" 1 "$total"
                run_phase "$four_phase" "$trial" 4 "$((total / 4))"
            else
                run_phase "$four_phase" "$trial" 4 "$((total / 4))"
                run_phase "$one_phase" "$trial" 1 "$total"
            fi
            index=$((index + 1))
        done
    done
fi

if (( latency_samples != 0 )); then
    for latency_label in text-idle lossless-idle lossy-idle \
                         text-bulk lossless-bulk lossy-bulk; do
        latency_successes=$(awk -F '\t' -v label="$latency_label" \
            '$1 == "latency-sample" && $2 == label {count++} END {print count + 0}' \
            "$report_stage")
        latency_drops=$(awk -F '\t' -v label="$latency_label" \
            '$1 == "latency-drop" && $2 == label {count++} END {print count + 0}' \
            "$report_stage")
        if (( latency_successes == 0 )); then
            record $'latency-summary\t'"$latency_label"$'\tsuccess\t0\tdropped\t'"$latency_drops"
            continue
        fi
        latency_min=$(latency_order_statistic "$latency_label" 1)
        latency_median=$(latency_order_statistic "$latency_label" 50)
        latency_p95=$(latency_order_statistic "$latency_label" 95)
        latency_p99=$(latency_order_statistic "$latency_label" 99)
        latency_max=$(latency_order_statistic "$latency_label" 100)
        record $'latency-summary\t'"$latency_label"$'\tsuccess\t'"$latency_successes"$'\tdropped\t'"$latency_drops"$'\tmin-us\t'"$latency_min"$'\tmedian-us\t'"$latency_median"$'\tp95-us\t'"$latency_p95"$'\tp99-us\t'"$latency_p99"$'\tmax-us\t'"$latency_max"
    done
    if (( burst_count != 0 )); then
        for latency_label in lossless-idle lossy-idle \
                             lossless-bulk lossy-bulk; do
            burst_attempts=$(awk -F '\t' -v label="$latency_label" \
                '$1 == "burst-sample" && $2 == label {count++} END {print count + 0}' \
                "$report_stage")
            burst_successes=$(awk -F '\t' -v label="$latency_label" \
                '$1 == "burst-sample" && $2 == label && $8 != "miss" {count++} END {print count + 0}' \
                "$report_stage")
            burst_errors=$(awk -F '\t' -v label="$latency_label" \
                '$1 == "burst-error" && $2 == label {count++} END {print count + 0}' \
                "$report_stage")
            burst_duplicates=$(awk -F '\t' -v label="$latency_label" \
                '$1 == "burst-sample" && $2 == label && $12 > 1 {extra += $12 - 1} END {print extra + 0}' \
                "$report_stage")
            burst_rejected=$(awk -F '\t' -v label="$latency_label" \
                '$1 == "burst-sample" && $2 == label && $14 != "ok" {count++} END {print count + 0}' \
                "$report_stage")
            burst_misses=$(awk -F '\t' -v label="$latency_label" \
                '$1 == "burst-sample" && $2 == label && $8 == "miss" && $14 == "ok" {count++} END {print count + 0}' \
                "$report_stage")
            burst_inversions=$(burst_reorder_inversions "$latency_label")
            if (( burst_successes == 0 )); then
                record $'burst-summary\t'"$latency_label"$'\tattempted\t'"$burst_attempts"$'\tsuccess\t0\tpath-missed\t'"$burst_misses"$'\tlocal-rejected\t'"$burst_rejected"$'\trequest-errors\t'"$burst_errors"$'\tduplicate-extra\t'"$burst_duplicates"$'\treorder-inversions\t'"$burst_inversions"
                continue
            fi
            burst_median=$(burst_order_statistic "$latency_label" 50)
            burst_p95=$(burst_order_statistic "$latency_label" 95)
            burst_max=$(burst_order_statistic "$latency_label" 100)
            record $'burst-summary\t'"$latency_label"$'\tattempted\t'"$burst_attempts"$'\tsuccess\t'"$burst_successes"$'\tpath-missed\t'"$burst_misses"$'\tlocal-rejected\t'"$burst_rejected"$'\trequest-errors\t'"$burst_errors"$'\tduplicate-extra\t'"$burst_duplicates"$'\treorder-inversions\t'"$burst_inversions"$'\tmedian-us\t'"$burst_median"$'\tp95-us\t'"$burst_p95"$'\tmax-us\t'"$burst_max"
        done
    fi
    sender_status=$("$binary" --runtime "${a_runtime[0]}" status)
    record $'latency-sender-interactive-max-queue-wait-us\t'"$(printf '%s' "$sender_status" | field transport-interactive-max-queue-wait-us)"
    record $'latency-sender-bulk-max-queue-wait-us\t'"$(printf '%s' "$sender_status" | field transport-bulk-max-queue-wait-us)"
    record $'latency-sender-requested-iteration-ms\t'"$(printf '%s' "$sender_status" | field transport-requested-iteration-ms)"
    record $'latency-sender-effective-iteration-ms\t'"$(printf '%s' "$sender_status" | field transport-effective-iteration-ms)"
fi

median() {
    local -a sorted=()
    mapfile -t sorted < <(printf '%s\n' "$@" | sort -n)
    local count=${#sorted[@]}
    if (( count % 2 == 1 )); then
        printf '%s\n' "${sorted[$((count / 2))]}"
    else
        printf '%s\n' "$(( (sorted[count / 2 - 1] + sorted[count / 2]) / 2 ))"
    fi
}

if [[ "$latency_only" == 1 ]]; then
    interpretation=ratox-read-receipt-latency-gate-complete-compare-idle-bulk-and-transport-modes
elif (( ${#stream_totals[@]} == 0 )); then
    median_one=$(median "${samples_one[@]}")
    median_one_four=$(median "${samples_one_four[@]}")
    median_two=$(median "${samples_two[@]}")
    median_four=$(median "${samples_four[@]}")
    speedup_one_four_x100=$((median_one * 100 / median_one_four))
    speedup_two_x100=$((median_one * 100 / median_two))
    speedup_four_x100=$((median_one * 100 / median_four))
    efficiency_two_percent=$((median_one * 100 / (median_two * 2)))
    efficiency_four_percent=$((median_one * 100 / (median_four * 4)))

    record $'median\tone-route-one-stream\t'"$median_one"
    record $'median\tone-route-four-streams\t'"$median_one_four"
    record $'median\ttwo-routes\t'"$median_two"
    record $'median\tfour-routes\t'"$median_four"
    record $'speedup-x100\tone-route-four-streams\t'"$speedup_one_four_x100"
    record $'speedup-x100\ttwo-routes\t'"$speedup_two_x100"
    record $'speedup-x100\tfour-routes\t'"$speedup_four_x100"
    record $'parallel-efficiency-percent\ttwo-routes\t'"$efficiency_two_percent"
    record $'parallel-efficiency-percent\tfour-routes\t'"$efficiency_four_percent"

    if (( speedup_four_x100 >= 150 && speedup_one_four_x100 < 130 )); then
        interpretation=independent-route-scaling-observed-per-connection-ceiling-is-a-candidate
    elif (( speedup_four_x100 < 125 )); then
        interpretation=four-routes-did-not-escape-the-shared-host-or-path-ceiling
    else
        interpretation=mixed-scaling-more-controlled-trials-required
    fi
else
    for total in "${stream_totals[@]}"; do
        one_phase="one-route-${total}-streams"
        four_phase="four-routes-${total}-streams"
        read -r -a one_values <<<"${sweep_samples[$one_phase]}"
        read -r -a four_values <<<"${sweep_samples[$four_phase]}"
        read -r -a one_data_values <<<"${sweep_data_samples[$one_phase]}"
        read -r -a four_data_values <<<"${sweep_data_samples[$four_phase]}"
        median_one=$(median "${one_values[@]}")
        median_four=$(median "${four_values[@]}")
        median_one_data=$(median "${one_data_values[@]}")
        median_four_data=$(median "${four_data_values[@]}")
        route_speedup_x100=$((median_one * 100 / median_four))
        data_route_speedup_x100=$((median_one_data * 100 / median_four_data))
        record $'median\t'"$one_phase"$'\t'"$median_one"
        record $'median\t'"$four_phase"$'\t'"$median_four"
        record $'route-distribution-speedup-x100\t'"$total"$'\t'"$route_speedup_x100"
        record $'median-data-window\t'"$one_phase"$'\t'"$median_one_data"
        record $'median-data-window\t'"$four_phase"$'\t'"$median_four_data"
        record $'data-route-distribution-speedup-x100\t'"$total"$'\t'"$data_route_speedup_x100"
    done
    interpretation=concurrency-sweep-complete-compare-route-distribution-per-stream-total
fi
record $'interpretation\t'"$interpretation"

for lane in 0 1 2 3; do
    "$binary" --runtime "${a_runtime[$lane]}" stop >/dev/null &
    stop_a=$!
    "$binary" --runtime "${b_runtime[$lane]}" stop >/dev/null &
    stop_b=$!
    wait "$stop_a"
    wait "$stop_b"
    wait "${a_pid[$lane]}"
    wait "${b_pid[$lane]}"
    a_pid[$lane]=
    b_pid[$lane]=
done

if [[ "$key_mode" == reuse ]]; then
    [[ $(cached_baseline_digest) == "$cache_digest_before" ]] ||
        fail 'four-route reusable baseline changed during the laboratory run'
fi

record $'four-route-lab\tpass'
mv -- "$report_stage" "$report"
report_stage=
printf 'report=%s\n' "$report"
