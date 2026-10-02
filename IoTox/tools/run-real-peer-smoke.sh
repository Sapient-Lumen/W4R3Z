#!/usr/bin/env bash
set -euo pipefail

if [[ ${1:-} == --help ]]; then
    cat <<'HELP'
Usage: tools/run-real-peer-smoke.sh [--reuse-keys|--fresh-keys] [--prepare-keys]

Runs two source-linked IoTox peers over configured native Tox bootstrap/relay
routes. By default it copies an immutable pair of test-only Tox/device identity
baselines into otherwise disposable profiles. It proves friendship, confirmed
session, fresh-controller RecallRoot re-entry and self-delegation, owner
revocation and epoch transition, mutual signed read authority, live text,
durable device.describe, and identity/evidence reload.

Options:
  --reuse-keys   reuse the private test baseline (default)
  --fresh-keys   generate both Tox/device identities from scratch
  --prepare-keys provision or validate the reusable baseline, then exit

Environment:
  IOTOX_BINARY                    source-linked executable
  IOTOX_REAL_PEER_SBOM            optional explicit SPDX path
  IOTOX_REAL_PEER_TIMEOUT_SECONDS total network deadline (default 240)
  IOTOX_REAL_PEER_WORKDIR         explicit disposable work directory
  IOTOX_REAL_PEER_KEEP=1          retain the work directory (contains secrets)
  IOTOX_REAL_PEER_TCP_ONLY=1      disable UDP/discovery/DHT/hole punching
  IOTOX_REAL_PEER_NETWORK         tox/native (default), tox/tor, or
                                  tox/i2p (tox/i2p-construction is an alias)
  IOTOX_REAL_PEER_SOCKS5_PROXY    numeric proxy for a strict routed mode
  IOTOX_REAL_PEER_BOOTSTRAP       exact HOST:PORT:KEY routed bootstrap record
  IOTOX_REAL_PEER_TCP_RELAY       exact HOST:PORT:KEY routed relay record
  IOTOX_REAL_PEER_BOOTSTRAPS      comma-separated routed bootstrap records;
                                  overrides the singular variable
  IOTOX_REAL_PEER_TCP_RELAYS      comma-separated routed relay records;
                                  overrides the singular variable
  IOTOX_REAL_PEER_KEYS            reuse (default) or fresh
  IOTOX_REAL_PEER_KEY_CACHE       private test-only baseline directory

This revision includes finite-file completion and removal/re-add. Relay-only
and fault-injection gates still require controlled infrastructure. The cache
and retained work directory contain private keys: never point the cache at a
live/production profile and never publish either directory.
HELP
    exit 0
fi

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
# shellcheck disable=SC1091
source "$root/dependencies.lock"
binary=${IOTOX_BINARY:-"$root/dist/standalone/iotox"}
timeout_seconds=${IOTOX_REAL_PEER_TIMEOUT_SECONDS:-240}
key_mode=${IOTOX_REAL_PEER_KEYS:-reuse}
key_cache=${IOTOX_REAL_PEER_KEY_CACHE:-"$root/.cache/real-peer-keys/c-toxcore-$IOTOX_C_TOXCORE_VERSION"}
peer_network=${IOTOX_REAL_PEER_NETWORK:-tox/native}
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
        printf 'IOTOX_REAL_PEER_KEYS must be reuse or fresh, got: %s\n' "$key_mode" >&2
        exit 2
        ;;
esac
case "$peer_network" in
    tox/native|native|tox) peer_network=tox/native ;;
    tox/tor|tox/i2p|tox/i2p-construction) ;;
    *)
        printf 'unsupported IOTOX_REAL_PEER_NETWORK: %s\n' "$peer_network" >&2
        exit 2
        ;;
esac
if [[ "$peer_network" != tox/native && "$key_mode" != fresh ]]; then
    printf '%s\n' 'strict routed real-peer runs require --fresh-keys to preserve route identity separation' >&2
    exit 2
fi
if [[ "$prepare_keys_only" == 1 && "$key_mode" != reuse ]]; then
    printf '%s\n' '--prepare-keys requires reusable-key mode' >&2
    exit 2
fi

work=${IOTOX_REAL_PEER_WORKDIR:-$(mktemp -d)}
keep=${IOTOX_REAL_PEER_KEEP:-0}
a_pid=
b_pid=
provision_pid=
provision_workspace=
publish_workspace=
cache_run_fd=
cache_digest_before=

fail() {
    printf 'real-peer-smoke=fail detail=%s\n' "$*" >&2
    for log in "$work"/*.log; do
        [[ -f "$log" ]] && { printf '\n--- %s ---\n' "$log" >&2; cat "$log" >&2; }
    done
    exit 1
}

cleanup() {
    for pid in "$provision_pid" "$a_pid" "$b_pid"; do
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
    if [[ "$keep" != 1 && -z ${IOTOX_REAL_PEER_WORKDIR:-} ]]; then
        rm -rf "$work"
    else
        printf 'real-peer-workdir=%s\n' "$work"
    fi
}
trap cleanup EXIT

field() {
    local name=$1
    sed -n "s/^${name}=//p" | head -n 1
}

control_with_phrase() {
    local phrase=$1
    local runtime=$2
    shift 2
    printf '%s\n' "$phrase" | "$binary" --runtime "$runtime" "$@"
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
        fail "reusable key generation is not an owned 0700 directory: $current"
    local entries
    entries=$(cd "$current" && find . -mindepth 1 -maxdepth 2 -printf '%P\n' | LC_ALL=C sort)
    [[ "$entries" == $'a\na/device.identity\na/device.toxsave\nb\nb/device.identity\nb/device.toxsave' ]] ||
        fail "reusable key generation must contain exactly two key-only baselines: $current"
    for label in a b; do
        private_directory_is_safe "$current/$label" ||
            fail "reusable peer directory is not owned 0700: $current/$label"
        for name in device.toxsave device.identity; do
            private_file_is_safe "$current/$label/$name" ||
                fail "reusable key file must be owned, nonempty, nonsymlink 0600: $current/$label/$name"
        done
    done
    ! cmp -s "$current/a/device.toxsave" "$current/b/device.toxsave" ||
        fail 'reusable peers cannot share one Tox savedata identity'
    ! cmp -s "$current/a/device.identity" "$current/b/device.identity" ||
        fail 'reusable peers cannot share one stable device identity'
}

provision_peer_baseline() {
    local label=$1
    local directory=$2
    local runtime="$directory/run"
    local log="$directory/provision.log"
    local state="$directory/device.toxsave"
    local identity="$directory/device.identity"
    local args=(
        run
        --runtime "$runtime"
        --state "$state"
        --identity "$identity"
        --authority-ledger "$directory/authority.ledger"
        --command-store "$directory/commands.store"
        --run-ms 30000
    )
    if [[ ${IOTOX_REAL_PEER_TCP_ONLY:-0} == 1 ]]; then
        args+=(--native-tcp-only)
    fi

    install -d -m 0700 "$directory"
    "$binary" "${args[@]}" >"$log" 2>&1 &
    provision_pid=$!
    local provision_deadline=$((SECONDS + 20))
    while (( SECONDS < provision_deadline )) && [[ ! -S "$runtime/control.sock" ]]; do
        kill -0 "$provision_pid" 2>/dev/null ||
            fail "reusable peer $label exited while creating its baseline"
        sleep 0.05
    done
    [[ -S "$runtime/control.sock" ]] ||
        fail "reusable peer $label did not expose its provisioning control socket"
    "$binary" --runtime "$runtime" stop >/dev/null
    wait "$provision_pid" || fail "reusable peer $label did not stop cleanly"
    provision_pid=
    private_file_is_safe "$state" ||
        fail "reusable peer $label did not create private Tox savedata"
    private_file_is_safe "$identity" ||
        fail "reusable peer $label did not create a private device identity"
}

prepare_reusable_baseline() {
    command -v flock >/dev/null 2>&1 ||
        fail 'flock is required to serialize reusable test identities'
    if [[ -e "$key_cache" || -L "$key_cache" ]]; then
        private_directory_is_safe "$key_cache" ||
            fail "reusable key cache must be an owned nonsymlink 0700 directory: $key_cache"
    else
        install -d -m 0700 "$key_cache"
    fi

    local prepare_fd
    exec {prepare_fd}>"$key_cache/.prepare.lock"
    chmod 0600 "$key_cache/.prepare.lock"
    flock "$prepare_fd"

    local current="$key_cache/current"
    if [[ -e "$current" || -L "$current" ]]; then
        validate_cached_baseline "$current"
    else
        provision_workspace=$(mktemp -d "$key_cache/.provision.XXXXXX")
        chmod 0700 "$provision_workspace"
        provision_peer_baseline a "$provision_workspace/a"
        provision_peer_baseline b "$provision_workspace/b"

        publish_workspace=$(mktemp -d "$key_cache/.publish.XXXXXX")
        chmod 0700 "$publish_workspace"
        install -d -m 0700 "$publish_workspace/a" "$publish_workspace/b"
        for label in a b; do
            install -m 0600 "$provision_workspace/$label/device.toxsave" \
                "$publish_workspace/$label/device.toxsave"
            install -m 0600 "$provision_workspace/$label/device.identity" \
                "$publish_workspace/$label/device.identity"
        done
        validate_cached_baseline "$publish_workspace"
        mv -- "$publish_workspace" "$current"
        publish_workspace=
        rm -rf "$provision_workspace"
        provision_workspace=
    fi
    flock -u "$prepare_fd"
    exec {prepare_fd}>&-
    validate_cached_baseline "$current"
}

cached_baseline_digest() {
    (
        cd "$key_cache/current"
        sha256sum a/device.toxsave a/device.identity \
            b/device.toxsave b/device.identity
    ) | sha256sum | cut -d' ' -f1
}

[[ -x "$binary" ]] || {
    printf 'source-linked binary not found: %s\n' "$binary" >&2
    printf '%s\n' 'run tools/build-standalone.sh first, or set IOTOX_BINARY' >&2
    exit 2
}
sbom=${IOTOX_REAL_PEER_SBOM:-}
if [[ -z "$sbom" ]]; then
    binary_prefix=$(cd "$(dirname "$binary")/.." && pwd)
    if [[ -f "$binary_prefix/share/doc/iotox/iotox.spdx.json" ]]; then
        sbom="$binary_prefix/share/doc/iotox/iotox.spdx.json"
    else
        sbom="$(dirname "$binary")/iotox.spdx.json"
    fi
fi
"$root/tools/verify-standalone.sh" "$binary" "$sbom" >/dev/null

if [[ "$key_mode" == reuse ]]; then
    prepare_reusable_baseline
    if [[ "$prepare_keys_only" == 1 ]]; then
        cat <<REPORT
real-peer-key-cache=ready
key-mode=reuse
provider-version=$IOTOX_C_TOXCORE_VERSION
key-cache=$key_cache
REPORT
        exit 0
    fi
    exec {cache_run_fd}>"$key_cache/.run.lock"
    chmod 0600 "$key_cache/.run.lock"
    if ! flock -n "$cache_run_fd"; then
        fail "reusable test identities are already active: $key_cache"
    fi
    cache_digest_before=$(cached_baseline_digest)
fi

mkdir -p "$work/a" "$work/b"
a_runtime="$work/a/run"
b_runtime="$work/b/run"
a_state="$work/a/device.toxsave"
b_state="$work/b/device.toxsave"
a_identity="$work/a/device.identity"
b_identity="$work/b/device.identity"
a_authority="$work/a/authority.ledger"
b_authority="$work/b/authority.ledger"
a_commands="$work/a/commands.store"
b_commands="$work/b/commands.store"
a_log="$work/a.log"
b_log="$work/b.log"

if [[ "$key_mode" == reuse ]]; then
    install -m 0600 "$key_cache/current/a/device.toxsave" "$a_state"
    install -m 0600 "$key_cache/current/a/device.identity" "$a_identity"
    install -m 0600 "$key_cache/current/b/device.toxsave" "$b_state"
    install -m 0600 "$key_cache/current/b/device.identity" "$b_identity"
fi

agent_args_a=(
    run
    --runtime "$a_runtime"
    --state "$a_state"
    --identity "$a_identity"
    --authority-ledger "$a_authority"
    --command-store "$a_commands"
)
agent_args_b=(
    run
    --runtime "$b_runtime"
    --state "$b_state"
    --identity "$b_identity"
    --authority-ledger "$b_authority"
    --command-store "$b_commands"
)
if [[ ${IOTOX_REAL_PEER_TCP_ONLY:-0} == 1 ]]; then
    agent_args_a+=(--native-tcp-only)
    agent_args_b+=(--native-tcp-only)
fi
if [[ "$peer_network" != tox/native ]]; then
    : "${IOTOX_REAL_PEER_SOCKS5_PROXY:?strict routed mode requires IOTOX_REAL_PEER_SOCKS5_PROXY}"
    bootstrap_csv=${IOTOX_REAL_PEER_BOOTSTRAPS:-${IOTOX_REAL_PEER_BOOTSTRAP:-}}
    relay_csv=${IOTOX_REAL_PEER_TCP_RELAYS:-${IOTOX_REAL_PEER_TCP_RELAY:-}}
    [[ -n "$bootstrap_csv" ]] || fail 'strict routed mode requires IOTOX_REAL_PEER_BOOTSTRAP(S)'
    [[ -n "$relay_csv" ]] || fail 'strict routed mode requires IOTOX_REAL_PEER_TCP_RELAY(S)'
    IFS=, read -r -a bootstrap_records <<<"$bootstrap_csv"
    IFS=, read -r -a relay_records <<<"$relay_csv"
    if [[ "$peer_network" == tox/i2p || \
          "$peer_network" == tox/i2p-construction ]]; then
        (( ${#bootstrap_records[@]} >= 3 )) || fail 'fresh I2P requires at least three bootstrap records'
        (( ${#relay_records[@]} >= 3 )) || fail 'fresh I2P requires at least three TCP relay records'
    fi
    routed_args=(
        --network "$peer_network"
        --socks5-proxy "$IOTOX_REAL_PEER_SOCKS5_PROXY"
    )
    for record in "${bootstrap_records[@]}"; do
        [[ -n "$record" ]] || fail 'routed bootstrap records may not be empty'
        routed_args+=(--bootstrap "$record")
    done
    for record in "${relay_records[@]}"; do
        [[ -n "$record" ]] || fail 'routed relay records may not be empty'
        routed_args+=(--tcp-relay "$record")
    done
    agent_args_a+=("${routed_args[@]}")
    agent_args_b+=("${routed_args[@]}")
fi

started_unix_ms=$(date +%s%3N)
"$binary" "${agent_args_a[@]}" >"$a_log" 2>&1 &
a_pid=$!
"$binary" "${agent_args_b[@]}" >"$b_log" 2>&1 &
b_pid=$!

deadline=$((SECONDS + timeout_seconds))
wait_for() {
    local description=$1
    shift
    while (( SECONDS < deadline )); do
        "$@" && return 0
        [[ -z "$a_pid" ]] || kill -0 "$a_pid" 2>/dev/null || fail 'peer A exited'
        [[ -z "$b_pid" ]] || kill -0 "$b_pid" 2>/dev/null || fail 'peer B exited'
        sleep 0.1
    done
    fail "timeout waiting for $description"
}

wait_for 'both local control sockets' bash -c \
    '[[ -S "$1" && -S "$2" ]]' _ "$a_runtime/control.sock" "$b_runtime/control.sock"

[[ -z $("$binary" --runtime "$a_runtime" peers) &&
   -z $("$binary" --runtime "$b_runtime" peers) &&
   -z $("$binary" --runtime "$a_runtime" requests) &&
   -z $("$binary" --runtime "$b_runtime" requests) ]] ||
    fail 'identity baseline contains friendship/request state; use test-only clean savedata'

a_address=$("$binary" --runtime "$a_runtime" address | tr -d '\n')
b_address=$("$binary" --runtime "$b_runtime" address | tr -d '\n')
[[ ${#a_address} -eq 76 && ${#b_address} -eq 76 ]] || fail 'invalid Tox address length'
a_key=${a_address:0:64}
b_key=${b_address:0:64}
[[ "$a_key" != "$b_key" ]] || fail 'two agents unexpectedly share one Tox identity'

a_identity_text=$("$binary" --runtime "$a_runtime" identity)
b_identity_text=$("$binary" --runtime "$b_runtime" identity)
a_device_principal=$(printf '%s' "$a_identity_text" | field device-public-key)
b_device_principal=$(printf '%s' "$b_identity_text" | field device-public-key)
[[ ${#a_device_principal} -eq 64 && ${#b_device_principal} -eq 64 ]] || \
    fail 'stable device principals were not available'
[[ "$a_device_principal" != "$b_device_principal" ]] || \
    fail 'two agents unexpectedly share one stable device principal'

# Fixed phrases are test-fixture material only. They exercise the permanent
# RecallRoot contract without passing a phrase in argv or writing it to disk.
a_phrase='abacus abdomen abdominal abide abiding ability ablaze able'
b_phrase='abnormal abrasion abrasive abreast abridge abroad abruptly absence'
b_successor_phrase='absentee absently absinthe absolute absolve abstain abstract absurd'
b_owner_public=$(control_with_phrase "$b_phrase" "$a_runtime" \
    recall-owner-public-key-stdin | field owner-public-key)
b_successor_public=$(control_with_phrase "$b_successor_phrase" "$a_runtime" \
    recall-owner-public-key-stdin | field owner-public-key)
[[ ${#b_owner_public} -eq 64 && ${#b_successor_public} -eq 64 && \
   "$b_owner_public" != "$b_successor_public" ]] || \
    fail 'distinct current and successor RecallRoot owner keys were not derived'
control_with_phrase "$a_phrase" "$a_runtime" \
    authority-bootstrap-recall-stdin >/dev/null
control_with_phrase "$b_phrase" "$b_runtime" \
    authority-bootstrap-recall-stdin >/dev/null
control_with_phrase "$a_phrase" "$a_runtime" \
    authority-grant-recall-stdin "$b_device_principal" automation \
    read.telemetry >/dev/null

"$binary" --runtime "$a_runtime" transport-peer-request \
    "$b_address" 'IoTox source-linked real-peer smoke' >/dev/null
wait_for 'friend request at peer B' bash -c \
    '"$1" --runtime "$2" requests 2>/dev/null | grep -q "$3"' \
    _ "$binary" "$b_runtime" "$a_key"
"$binary" --runtime "$b_runtime" request-accept "$a_key" >/dev/null

wait_for 'confirmed IoTox session at peer A' bash -c \
    '"$1" --runtime "$2" session "$3" 2>/dev/null | grep -q "^state=confirmed$"' \
    _ "$binary" "$a_runtime" "$b_key"
wait_for 'confirmed IoTox session at peer B' bash -c \
    '"$1" --runtime "$2" session "$3" 2>/dev/null | grep -q "^state=confirmed$"' \
    _ "$binary" "$b_runtime" "$a_key"
wait_for 'pre-enrolled stable principal at peer A' bash -c \
    'out=$("$1" --runtime "$2" authority-session "$3" 2>/dev/null) && grep -q "^remote-authorized=1$" <<<"$out" && grep -q "^claimant-state=proof-sent$" <<<"$out"' \
    _ "$binary" "$a_runtime" "$b_key"
wait_for 'fresh controller device denial at peer B' bash -c \
    'out=$("$1" --runtime "$2" authority-session "$3" 2>/dev/null) && grep -q "^remote-authorized=0$" <<<"$out" && grep -q "^verifier-state=denied$" <<<"$out" && grep -q "^peer-proof-candidate-count=1$" <<<"$out"' \
    _ "$binary" "$b_runtime" "$a_key"

# Reconstruct A's owner only in the short-lived CLI process. The ordinary A
# device proof has already been denied by B; the authority protocol permits
# exactly one explicit recovery replacement and keeps authorized proofs frozen.
control_with_phrase "$b_phrase" "$a_runtime" \
    authority-prove-recall-stdin "$b_key" >/dev/null
wait_for 'recalled owner authorized at peer B' bash -c \
    'out=$("$1" --runtime "$2" authority-session "$3" 2>/dev/null) && grep -q "^remote-authorized=1$" <<<"$out" && grep -q "^remote-role=owner$" <<<"$out" && grep -q "^peer-proof-candidate-count=2$" <<<"$out"' \
    _ "$binary" "$b_runtime" "$a_key"

# Owner creation is categorically outside self-delegation. Prove that the
# client-side ceremony rejects it before any record reaches the network.
if control_with_phrase "$b_phrase" "$a_runtime" \
    authority-delegate-self-recall-stdin "$b_key" owner all \
    >/dev/null 2>&1; then
    fail 'remote self-delegation unexpectedly permitted an owner grant'
fi

control_with_phrase "$b_phrase" "$a_runtime" \
    authority-delegate-self-recall-stdin "$b_key" automation \
    read.telemetry >/dev/null
wait_for 'remote self-delegation applied at peer B' bash -c \
    'out=$("$1" --runtime "$2" authority-delegation "$3" 2>/dev/null) && grep -q "^state=result-received$" <<<"$out" && grep -q "^outcome=applied$" <<<"$out" && grep -q "^authority-sequence=2$" <<<"$out"' \
    _ "$binary" "$a_runtime" "$b_key"
wait_for 'delegated controller becomes ordinary authorized principal' bash -c \
    'out=$("$1" --runtime "$2" authority-session "$3" 2>/dev/null) && grep -q "^remote-authorized=1$" <<<"$out" && grep -q "^remote-role=automation$" <<<"$out" && grep -q "^remote-principal=$4$" <<<"$out"' \
    _ "$binary" "$b_runtime" "$a_key" "$a_device_principal"

# Requeue the exact frozen signed record. The receiver recognizes its current
# ledger tail without appending a third record, even though the first append
# invalidated the owner's old authority round.
"$binary" --runtime "$a_runtime" authority-delegation-retry "$b_key" >/dev/null
wait_for 'exact duplicate delegation result' bash -c \
    'out=$("$1" --runtime "$2" authority-delegation "$3" 2>/dev/null) && grep -q "^state=result-received$" <<<"$out" && grep -q "^outcome=exact-duplicate$" <<<"$out" && grep -q "^authority-sequence=2$" <<<"$out"' \
    _ "$binary" "$a_runtime" "$b_key"
[[ $("$binary" --runtime "$b_runtime" authority | field sequence) == 2 ]] || \
    fail 'exact duplicate changed the receiver authority sequence'
initial_ready_unix_ms=$(date +%s%3N)
initial_convergence_ms=$((initial_ready_unix_ms - started_unix_ms))

message="real-toxcore-hello-$RANDOM-$RANDOM"
"$binary" --runtime "$a_runtime" message "$b_key" "$message" >/dev/null
wait_for 'message journal at peer B' bash -c \
    '[[ -f "$1" ]] && grep -Fq "$2" "$1"' \
    _ "$b_runtime/peers/$a_key/messages" "$message"

# Exercise the product command entrance, not only chat. The request must be
# committed before transport, acknowledged by the receiver, completed under
# the independent authority ledger, and queryable by durable identity.
"$binary" --runtime "$a_runtime" command "$b_key" device.describe >/dev/null
wait_for 'durable device.describe result at peer A' bash -c \
    'out=$("$1" --runtime "$2" peer-description "$3" 2>/dev/null) && grep -q "^state=succeeded$" <<<"$out" && grep -q "^receipt-stage=received$" <<<"$out" && grep -q "^sender-epoch=[1-9][0-9]*$" <<<"$out"' \
    _ "$binary" "$a_runtime" "$b_key"

description=$("$binary" --runtime "$a_runtime" peer-description "$b_key")
sender_epoch=$(printf '%s' "$description" | field sender-epoch)
request_message_id=$(printf '%s' "$description" | field request-message-id)
[[ "$sender_epoch" =~ ^[1-9][0-9]*$ ]] || fail 'durable sender epoch is invalid'
[[ "$request_message_id" =~ ^[1-9][0-9]*$ ]] || fail 'durable request message id is invalid'
command_record=$("$binary" --runtime "$a_runtime" command-record outgoing \
    "$b_key" "$sender_epoch" "$request_message_id")
grep -q '^lifecycle=succeeded$' <<<"$command_record" || \
    fail 'outgoing durable command did not become terminal success'
grep -q '^receipt-delivery=observed$' <<<"$command_record" || \
    fail 'outgoing durable command did not retain the peer receipt'
grep -q '^result-delivery=observed$' <<<"$command_record" || \
    fail 'outgoing durable command did not retain the peer result'
[[ -f "$a_runtime/commands/outgoing/$b_key/$sender_epoch-$request_message_id/request.frame" ]] || \
    fail 'ratox-style command projection is missing the exact request frame'

summary_issue=$("$binary" --runtime "$a_runtime" command "$b_key" system.summary)
summary_epoch=$(printf '%s' "$summary_issue" | field sender-epoch)
summary_message_id=$(printf '%s' "$summary_issue" | field message-id)
[[ "$summary_epoch" =~ ^[1-9][0-9]*$ && "$summary_message_id" =~ ^[1-9][0-9]*$ ]] || \
    fail 'system.summary did not reserve a durable identity'
summary_result="$a_runtime/commands/outgoing/$b_key/$summary_epoch-$summary_message_id/result"
wait_for 'typed system.summary result at peer A' bash -c \
    '[[ -f "$1" ]] && grep -q "^operation=system.summary$" "$1" && grep -q "^outcome=succeeded$" "$1" && grep -q "^health=" "$1"' \
    _ "$summary_result"

# Transfer exact finite bytes through genuine toxcore callbacks. Incoming
# offers remain paused until the receiver chooses a private destination.
file_source="$work/genuine-source.bin"
file_destination="$work/genuine-received.bin"
printf 'IoTox genuine finite file\nline two\000tail' >"$file_source"
"$binary" --runtime "$a_runtime" file-send "$b_key" "$file_source" >/dev/null
wait_for 'paused incoming finite-file offer at peer B' bash -c \
    '"$1" --runtime "$2" files 2>/dev/null | grep -q "direction=incoming state=offered"' \
    _ "$binary" "$b_runtime"
b_files=$("$binary" --runtime "$b_runtime" files)
incoming_file_number=$(printf '%s\n' "$b_files" | sed -n \
    's/.*direction=incoming state=offered[^\n]*file-number=\([0-9][0-9]*\).*/\1/p' | head -n 1)
[[ "$incoming_file_number" =~ ^[0-9]+$ ]] || fail 'incoming file number was not projected'
"$binary" --runtime "$b_runtime" file-receive "$a_key" \
    "$incoming_file_number" "$file_destination" >/dev/null
wait_for 'exact finite-file completion at peer B' bash -c \
    '[[ -f "$1" ]] && cmp -s "$1" "$2"' _ "$file_source" "$file_destination"
wait_for 'both finite transfers leave the live set' bash -c \
    '[[ -z $("$1" --runtime "$2" files 2>/dev/null) && -z $("$1" --runtime "$3" files 2>/dev/null) ]]' \
    _ "$binary" "$a_runtime" "$b_runtime"

# Elevate the already delegated controller into one explicit owner
# administration proof, revoke its ordinary device principal, and replay the
# exact signed revocation. The receiver must retain one sequence transition.
control_with_phrase "$b_phrase" "$a_runtime" \
    authority-prove-recall-stdin "$b_key" >/dev/null
wait_for 'delegated controller owner administration proof' bash -c \
    'out=$("$1" --runtime "$2" authority-session "$3" 2>/dev/null) && grep -q "^remote-authorized=1$" <<<"$out" && grep -q "^remote-role=owner$" <<<"$out" && grep -q "^peer-proof-candidate-count=2$" <<<"$out"' \
    _ "$binary" "$b_runtime" "$a_key"
control_with_phrase "$b_phrase" "$a_runtime" \
    authority-revoke-remote-recall-stdin "$b_key" \
    "$a_device_principal" >/dev/null
wait_for 'remote delegated-controller revocation applied' bash -c \
    'out=$("$1" --runtime "$2" authority-delegation "$3" 2>/dev/null) && grep -q "^state=result-received$" <<<"$out" && grep -q "^outcome=applied$" <<<"$out" && grep -q "^authority-sequence=3$" <<<"$out"' \
    _ "$binary" "$a_runtime" "$b_key"
wait_for 'delegated controller is inactive at receiver' bash -c \
    '"$1" --runtime "$2" principals 2>/dev/null | grep -q "^public-key=$3 active=0 role=none capabilities=none last-sequence=3$"' \
    _ "$binary" "$b_runtime" "$a_device_principal"
"$binary" --runtime "$a_runtime" authority-delegation-retry "$b_key" >/dev/null
wait_for 'exact duplicate revocation result' bash -c \
    'out=$("$1" --runtime "$2" authority-delegation "$3" 2>/dev/null) && grep -q "^outcome=exact-duplicate$" <<<"$out" && grep -q "^authority-sequence=3$" <<<"$out"' \
    _ "$binary" "$a_runtime" "$b_key"
[[ $("$binary" --runtime "$b_runtime" authority | field sequence) == 3 ]] || \
    fail 'exact duplicate revocation changed the receiver authority sequence'

# Stop one genuine peer process without removing friendship, then require a
# higher online epoch, a fresh transcript, and fresh authority proof after the
# same savedata and stable device identity return.
pre_reconnect_session=$("$binary" --runtime "$a_runtime" session "$b_key")
pre_reconnect_epoch=$(printf '%s' "$pre_reconnect_session" | field online-epoch)
reconnect_started_unix_ms=$(date +%s%3N)
"$binary" --runtime "$b_runtime" stop >/dev/null
wait "$b_pid"
b_pid=
wait_for 'peer A observes genuine disconnect' bash -c \
    '! "$1" --runtime "$2" session "$3" 2>/dev/null | grep -q "^state=confirmed$"' \
    _ "$binary" "$a_runtime" "$b_key"
b_reconnect_log="$work/b-reconnect.log"
"$binary" "${agent_args_b[@]}" >"$b_reconnect_log" 2>&1 &
b_pid=$!
wait_for 'peer B reconnect control socket' bash -c \
    '[[ -S "$1" ]]' _ "$b_runtime/control.sock"
[[ $("$binary" --runtime "$b_runtime" address | tr -d '\n') == "$b_address" ]] || \
    fail 'peer B Tox identity changed across reconnect'
reloaded_principals=$("$binary" --runtime "$b_runtime" principals)
grep -q "^public-key=$a_device_principal active=0 role=none capabilities=none last-sequence=3$" \
    <<<"$reloaded_principals" || \
    fail 'receiver did not replay the controller revocation across restart'
wait_for 'fresh confirmed session after genuine process reconnect' bash -c \
    'out=$("$1" --runtime "$2" session "$3" 2>/dev/null) && grep -q "^state=confirmed$" <<<"$out" && epoch=$(sed -n "s/^online-epoch=//p" <<<"$out") && [[ "$epoch" -gt "$4" ]]' \
    _ "$binary" "$a_runtime" "$b_key" "$pre_reconnect_epoch"
wait_for 'revoked controller denial after genuine process reconnect' bash -c \
    'out=$("$1" --runtime "$2" authority-session "$3" 2>/dev/null) && grep -q "^remote-authorized=0$" <<<"$out" && grep -q "^verifier-state=denied$" <<<"$out" && grep -q "^peer-proof-candidate-count=1$" <<<"$out"' \
    _ "$binary" "$b_runtime" "$a_key"
control_with_phrase "$b_phrase" "$a_runtime" \
    authority-prove-recall-stdin "$b_key" >/dev/null
wait_for 'recalled owner re-entry after receiver restart' bash -c \
    'out=$("$1" --runtime "$2" authority-session "$3" 2>/dev/null) && grep -q "^remote-authorized=1$" <<<"$out" && grep -q "^remote-role=owner$" <<<"$out"' \
    _ "$binary" "$b_runtime" "$a_key"
control_with_phrase "$b_phrase" "$a_runtime" \
    authority-delegate-self-recall-stdin "$b_key" automation \
    read.telemetry >/dev/null
wait_for 'controller re-delegation after receiver restart' bash -c \
    'out=$("$1" --runtime "$2" authority-delegation "$3" 2>/dev/null) && grep -q "^outcome=applied$" <<<"$out" && grep -q "^authority-sequence=4$" <<<"$out"' \
    _ "$binary" "$a_runtime" "$b_key"
wait_for 'fresh ordinary authority proof after re-delegation' bash -c \
    'out=$("$1" --runtime "$2" authority-session "$3" 2>/dev/null) && grep -q "^remote-authorized=1$" <<<"$out" && grep -q "^remote-role=automation$" <<<"$out"' \
    _ "$binary" "$b_runtime" "$a_key"
reconnect_ready_unix_ms=$(date +%s%3N)
reconnect_convergence_ms=$((reconnect_ready_unix_ms - reconnect_started_unix_ms))

# Make an explicit constitutional cut. The current owner nominates a distinct
# successor at sequence 5; after that mutation invalidates proofs, the successor
# proves possession and signs epoch 2 sequence 1. Exact replay cannot advance
# the epoch twice, and every old-epoch principal disappears from live authority.
control_with_phrase "$b_phrase" "$a_runtime" \
    authority-prove-recall-stdin "$b_key" >/dev/null
wait_for 'current owner proof before successor nomination' bash -c \
    'out=$("$1" --runtime "$2" authority-session "$3" 2>/dev/null) && grep -q "^remote-authorized=1$" <<<"$out" && grep -q "^remote-principal=$4$" <<<"$out" && grep -q "^remote-role=owner$" <<<"$out"' \
    _ "$binary" "$b_runtime" "$a_key" "$b_owner_public"
control_with_phrase "$b_phrase" "$a_runtime" \
    authority-nominate-successor-remote-recall-stdin "$b_key" \
    "$b_successor_public" >/dev/null
wait_for 'successor owner nomination applied at peer B' bash -c \
    'out=$("$1" --runtime "$2" authority-delegation "$3" 2>/dev/null) && grep -q "^outcome=applied$" <<<"$out" && grep -q "^authority-epoch=1$" <<<"$out" && grep -q "^authority-sequence=5$" <<<"$out"' \
    _ "$binary" "$a_runtime" "$b_key"
"$binary" --runtime "$a_runtime" authority-delegation-retry "$b_key" >/dev/null
wait_for 'exact duplicate successor nomination result' bash -c \
    'out=$("$1" --runtime "$2" authority-delegation "$3" 2>/dev/null) && grep -q "^outcome=exact-duplicate$" <<<"$out" && grep -q "^authority-epoch=1$" <<<"$out" && grep -q "^authority-sequence=5$" <<<"$out"' \
    _ "$binary" "$a_runtime" "$b_key"
wait_for 'controller proof refresh after successor nomination' bash -c \
    'out=$("$1" --runtime "$2" authority-session "$3" 2>/dev/null) && grep -q "^remote-authorized=1$" <<<"$out" && grep -q "^remote-role=automation$" <<<"$out"' \
    _ "$binary" "$b_runtime" "$a_key"
control_with_phrase "$b_successor_phrase" "$a_runtime" \
    authority-prove-recall-stdin "$b_key" >/dev/null
wait_for 'nominated successor possession proof' bash -c \
    'out=$("$1" --runtime "$2" authority-session "$3" 2>/dev/null) && grep -q "^remote-authorized=1$" <<<"$out" && grep -q "^remote-principal=$4$" <<<"$out" && grep -q "^remote-role=owner$" <<<"$out"' \
    _ "$binary" "$b_runtime" "$a_key" "$b_successor_public"
control_with_phrase "$b_successor_phrase" "$a_runtime" \
    authority-transition-remote-recall-stdin "$b_key" >/dev/null
wait_for 'ownership epoch transition applied at peer B' bash -c \
    'out=$("$1" --runtime "$2" authority-delegation "$3" 2>/dev/null) && grep -q "^outcome=applied$" <<<"$out" && grep -q "^authority-epoch=2$" <<<"$out" && grep -q "^authority-sequence=1$" <<<"$out"' \
    _ "$binary" "$a_runtime" "$b_key"
"$binary" --runtime "$a_runtime" authority-delegation-retry "$b_key" >/dev/null
wait_for 'exact duplicate ownership epoch transition result' bash -c \
    'out=$("$1" --runtime "$2" authority-delegation "$3" 2>/dev/null) && grep -q "^outcome=exact-duplicate$" <<<"$out" && grep -q "^authority-epoch=2$" <<<"$out" && grep -q "^authority-sequence=1$" <<<"$out"' \
    _ "$binary" "$a_runtime" "$b_key"
[[ $("$binary" --runtime "$b_runtime" authority | field ownership-epoch) == 2 && \
   $("$binary" --runtime "$b_runtime" authority | field sequence) == 1 ]] || \
    fail 'ownership transition did not freeze epoch 2 sequence 1'
wait_for 'old-epoch controller denied after transition' bash -c \
    'out=$("$1" --runtime "$2" authority-session "$3" 2>/dev/null) && grep -q "^remote-authorized=0$" <<<"$out" && grep -q "^verifier-state=denied$" <<<"$out"' \
    _ "$binary" "$b_runtime" "$a_key"

# Re-enter only with the successor phrase, delegate this controller in epoch 2,
# then prove that the old phrase is a valid signature from a principal that no
# longer exists in live authority.
control_with_phrase "$b_successor_phrase" "$a_runtime" \
    authority-prove-recall-stdin "$b_key" >/dev/null
wait_for 'successor owner re-entry in epoch 2' bash -c \
    'out=$("$1" --runtime "$2" authority-session "$3" 2>/dev/null) && grep -q "^remote-authorized=1$" <<<"$out" && grep -q "^remote-principal=$4$" <<<"$out" && grep -q "^remote-role=owner$" <<<"$out"' \
    _ "$binary" "$b_runtime" "$a_key" "$b_successor_public"
control_with_phrase "$b_successor_phrase" "$a_runtime" \
    authority-delegate-self-recall-stdin "$b_key" automation \
    read.telemetry >/dev/null
wait_for 'controller delegated in epoch 2' bash -c \
    'out=$("$1" --runtime "$2" authority-delegation "$3" 2>/dev/null) && grep -q "^outcome=applied$" <<<"$out" && grep -q "^authority-epoch=2$" <<<"$out" && grep -q "^authority-sequence=2$" <<<"$out"' \
    _ "$binary" "$a_runtime" "$b_key"
wait_for 'epoch 2 controller proof becomes authorized' bash -c \
    'out=$("$1" --runtime "$2" authority-session "$3" 2>/dev/null) && grep -q "^remote-authorized=1$" <<<"$out" && grep -q "^remote-role=automation$" <<<"$out"' \
    _ "$binary" "$b_runtime" "$a_key"
control_with_phrase "$b_phrase" "$a_runtime" \
    authority-prove-recall-stdin "$b_key" >/dev/null
wait_for 'retired owner phrase denied in epoch 2' bash -c \
    'out=$("$1" --runtime "$2" authority-session "$3" 2>/dev/null) && grep -q "^remote-authorized=0$" <<<"$out" && grep -q "^verifier-state=denied$" <<<"$out" && grep -q "^remote-principal=$4$" <<<"$out" && grep -q "^peer-proof-candidate-count=2$" <<<"$out"' \
    _ "$binary" "$b_runtime" "$a_key" "$b_owner_public"

# Replay the transitioned ledger in a fresh receiver process before continuing
# with the transport-removal gate.
pre_epoch_restart_session=$("$binary" --runtime "$a_runtime" session "$b_key")
pre_epoch_restart_online=$(printf '%s' "$pre_epoch_restart_session" | field online-epoch)
"$binary" --runtime "$b_runtime" stop >/dev/null
wait "$b_pid"
b_pid=
wait_for 'peer A observes epoch-verification disconnect' bash -c \
    '! "$1" --runtime "$2" session "$3" 2>/dev/null | grep -q "^state=confirmed$"' \
    _ "$binary" "$a_runtime" "$b_key"
b_epoch_log="$work/b-epoch-restart.log"
"$binary" "${agent_args_b[@]}" >"$b_epoch_log" 2>&1 &
b_pid=$!
wait_for 'epoch-transition receiver control socket' bash -c \
    '[[ -S "$1" ]]' _ "$b_runtime/control.sock"
[[ $("$binary" --runtime "$b_runtime" authority | field ownership-epoch) == 2 && \
   $("$binary" --runtime "$b_runtime" authority | field sequence) == 2 ]] || \
    fail 'receiver did not replay epoch 2 sequence 2 after restart'
epoch_principals=$("$binary" --runtime "$b_runtime" principals)
grep -q "^public-key=$b_successor_public active=1 role=owner" \
    <<<"$epoch_principals" || fail 'successor owner missing after epoch restart'
! grep -q "^public-key=$b_owner_public " <<<"$epoch_principals" || \
    fail 'retired owner remained in the live epoch principal set'
wait_for 'fresh confirmed session after epoch receiver restart' bash -c \
    'out=$("$1" --runtime "$2" session "$3" 2>/dev/null) && grep -q "^state=confirmed$" <<<"$out" && epoch=$(sed -n "s/^online-epoch=//p" <<<"$out") && [[ "$epoch" -gt "$4" ]]' \
    _ "$binary" "$a_runtime" "$b_key" "$pre_epoch_restart_online"
wait_for 'epoch 2 controller authorization after receiver restart' bash -c \
    'out=$("$1" --runtime "$2" authority-session "$3" 2>/dev/null) && grep -q "^remote-authorized=1$" <<<"$out" && grep -q "^remote-role=automation$" <<<"$out"' \
    _ "$binary" "$b_runtime" "$a_key"

# Friendship is transport inventory, not authority. Remove both endpoints,
# then re-request and prove that the stable authority relationship rebinds to
# a fresh confirmed online epoch without changing either principal.
"$binary" --runtime "$a_runtime" transport-peer-remove "$b_key" >/dev/null
"$binary" --runtime "$b_runtime" transport-peer-remove "$a_key" >/dev/null
wait_for 'peer projections withdrawn after removal' bash -c \
    '[[ ! -e "$1/peers/$3" && ! -e "$2/peers/$4" ]]' \
    _ "$a_runtime" "$b_runtime" "$b_key" "$a_key"
"$binary" --runtime "$a_runtime" transport-peer-request \
    "$b_address" 'IoTox genuine re-add' >/dev/null
wait_for 're-add request at peer B' bash -c \
    '"$1" --runtime "$2" requests 2>/dev/null | grep -q "$3"' \
    _ "$binary" "$b_runtime" "$a_key"
"$binary" --runtime "$b_runtime" request-accept "$a_key" >/dev/null
wait_for 'confirmed re-added IoTox session' bash -c \
    '"$1" --runtime "$2" session "$3" 2>/dev/null | grep -q "^state=confirmed$"' \
    _ "$binary" "$a_runtime" "$b_key"
wait_for 're-added stable authority proof' bash -c \
    'out=$("$1" --runtime "$2" authority-session "$3" 2>/dev/null) && grep -q "^remote-authorized=1$" <<<"$out" && grep -q "^claimant-state=proof-sent$" <<<"$out"' \
    _ "$binary" "$a_runtime" "$b_key"

# These are host observations, not protocol guarantees. Protocol journal bytes
# are an application-frame proxy and intentionally are not called wire bytes.
a_rss_kib=$(awk '/^VmRSS:/ {print $2}' "/proc/$a_pid/status")
b_rss_kib=$(awk '/^VmRSS:/ {print $2}' "/proc/$b_pid/status")
a_context_switches=$(awk '/^(voluntary|nonvoluntary)_ctxt_switches:/ {sum += $2} END {print sum + 0}' "/proc/$a_pid/status")
b_context_switches=$(awk '/^(voluntary|nonvoluntary)_ctxt_switches:/ {sum += $2} END {print sum + 0}' "/proc/$b_pid/status")
a_cpu_ticks=$(awk '{print $14 + $15}' "/proc/$a_pid/stat")
b_cpu_ticks=$(awk '{print $14 + $15}' "/proc/$b_pid/stat")
a_open_fds=$(find "/proc/$a_pid/fd" -mindepth 1 -maxdepth 1 | wc -l)
b_open_fds=$(find "/proc/$b_pid/fd" -mindepth 1 -maxdepth 1 | wc -l)
protocol_journal_bytes=$(find "$a_runtime/peers" "$b_runtime/peers" \
    -type f -name protocol -printf '%s\n' 2>/dev/null | awk '{sum += $1} END {print sum + 0}')
persistent_state_bytes=$(stat -c '%s' "$a_state")
persistent_state_bytes=$((persistent_state_bytes + $(stat -c '%s' "$b_state")))

"$binary" --runtime "$a_runtime" stop >/dev/null
wait "$a_pid"
a_pid=
"$binary" --runtime "$b_runtime" stop >/dev/null
wait "$b_pid"
b_pid=
for path in "$a_state" "$b_state" "$a_identity" "$b_identity" \
            "$a_authority" "$b_authority" "$a_commands" "$b_commands"; do
    [[ -s "$path" ]] || fail "persistent state missing: $path"
    [[ $(stat -c '%a' "$path") == 600 ]] || fail "persistent state mode is not 0600: $path"
done

restart_log="$work/a-restart.log"
"$binary" "${agent_args_a[@]}" --run-ms 10000 >"$restart_log" 2>&1 &
a_pid=$!
deadline=$((SECONDS + 20))
while (( SECONDS < deadline )) && [[ ! -S "$a_runtime/control.sock" ]]; do
    kill -0 "$a_pid" 2>/dev/null || fail 'peer A restart exited'
    sleep 0.05
done
[[ -S "$a_runtime/control.sock" ]] || fail 'peer A restart control socket missing'
restart_address=$("$binary" --runtime "$a_runtime" address | tr -d '\n')
[[ "$restart_address" == "$a_address" ]] || fail 'peer A Tox identity changed after restart'
restart_identity=$("$binary" --runtime "$a_runtime" identity | field device-public-key)
[[ "$restart_identity" == "$a_device_principal" ]] || \
    fail 'peer A stable device identity changed after restart'
restored_record=$("$binary" --runtime "$a_runtime" command-record outgoing \
    "$b_key" "$sender_epoch" "$request_message_id")
[[ "$restored_record" == "$command_record" ]] || \
    fail 'durable command evidence changed across restart'
"$binary" --runtime "$a_runtime" stop >/dev/null
wait "$a_pid"
a_pid=

if [[ "$key_mode" == reuse ]]; then
    [[ $(cached_baseline_digest) == "$cache_digest_before" ]] ||
        fail 'reusable key baseline changed during an isolated smoke run'
    key_lifecycle=reused-immutable-clean-baseline
else
    key_lifecycle=fresh-generated-disposable
fi

cat <<REPORT
real-peer-smoke=pass
binary=$binary
key-mode=$key_mode
key-lifecycle=$key_lifecycle
peer-a-public-key-sha256=$(printf '%s' "$a_key" | sha256sum | cut -d' ' -f1)
peer-b-public-key-sha256=$(printf '%s' "$b_key" | sha256sum | cut -d' ' -f1)
session=canonical-hello-transcript-confirmed-both-directions
authority=stable-principal-proof-and-read-telemetry-grant-both-directions
owner-reentry=denied-device-then-recalled-owner-proof
self-delegation=owner-role-denied-applied-exact-duplicate
remote-revocation=applied-exact-duplicate-and-inactive-after-restart
delegation-restart=revoked-controller-recalled-and-redelegated-at-sequence-4
ownership-epoch=successor-nominated-transitioned-exact-duplicate-replayed-at-epoch-2
phrase-compromise-cut=old-owner-denied-successor-reentered-and-redelegated
transport-mode=$peer_network
message=delivered-to-peer-journal
command=device.describe-received-succeeded-and-durably-reloaded
summary=system.summary-received-succeeded-and-typed
file=finite-exact-bytes-completed
friendship=removed-both-directions-and-readded-with-fresh-session-proof
reconnect=process-restart-fresh-session-and-authority-proof
initial-convergence-ms=$initial_convergence_ms
reconnect-convergence-ms=$reconnect_convergence_ms
peer-a-rss-kib=$a_rss_kib
peer-b-rss-kib=$b_rss_kib
peer-a-cpu-ticks=$a_cpu_ticks
peer-b-cpu-ticks=$b_cpu_ticks
peer-a-context-switches=$a_context_switches
peer-b-context-switches=$b_context_switches
peer-a-open-fds=$a_open_fds
peer-b-open-fds=$b_open_fds
protocol-journal-bytes-proxy=$protocol_journal_bytes
persistent-tox-savedata-bytes=$persistent_state_bytes
restart-identity=tox-and-stable-device-preserved
workdir=$work
REPORT
