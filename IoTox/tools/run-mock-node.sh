#!/usr/bin/env bash
set -euo pipefail

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
preset=${1:-gcc-debug}
build_dir=${IOTOX_BUILD_DIR:-"$root/build/$preset"}
work=$(mktemp -d)
node_pid=
cleanup() {
    if [[ -n "${node_pid:-}" ]] && kill -0 "$node_pid" 2>/dev/null; then
        kill "$node_pid" 2>/dev/null || true
        wait "$node_pid" 2>/dev/null || true
    fi
    rm -rf "$work"
}
trap cleanup EXIT

if [[ ${IOTOX_SKIP_BUILD:-0} != 1 ]]; then
    cmake --preset "$preset" -S "$root"
    # Build the configured tree by absolute path so this fixture works from any caller cwd.
    cmake --build "$build_dir" --parallel
fi

for required in iotox libtoxcore-iotox-mock.so; do
    if [[ ! -f "$build_dir/$required" ]]; then
        printf 'required mock-node input is missing: %s\n' "$build_dir/$required" >&2
        exit 2
    fi
done

version_output=$("$build_dir/iotox" --version)
read -r expected_project expected_version expected_revision trailing <<<"$version_output"
if [[ $expected_project != IoTox || -z $expected_version ||
      ! $expected_revision =~ ^rev([0-9]+)$ || -n ${trailing:-} ]]; then
    printf 'invalid IoTox --version identity: %s\n' "$version_output" >&2
    exit 2
fi
expected_revision_number=$((10#${BASH_REMATCH[1]}))

runtime="$work/run"
state="$work/state/device.toxsave"
log="$work/iotox-run.log"
key=000102030405060708090A0B0C0D0E0F101112131415161718191A1B1C1D1E1F

authority_audit="$work/mock-authority-audit.log"
IOTOX_MOCK_INCOMING_FRIEND_REQUEST='please-add-this-device' \
IOTOX_MOCK_HELLO_SENDQ_FAILURES=1 \
IOTOX_MOCK_CONFIRMATION_SENDQ_FAILURES=1 \
IOTOX_MOCK_AUTHORITY_CHALLENGE_SENDQ_FAILURES=1 \
IOTOX_MOCK_AUTHORITY_PROOF_SENDQ_FAILURES=1 \
IOTOX_MOCK_COMMAND_SENDQ_FAILURES=1 \
IOTOX_MOCK_COMMAND_RESULT_SENDQ_FAILURES_PER_REQUEST=1 \
IOTOX_MOCK_AUTHORITY_AUDIT="$authority_audit" \
"$build_dir/iotox" run \
    --library "$build_dir/libtoxcore-iotox-mock.so" \
    --runtime "$runtime" \
    --state "$state" \
    --bootstrap "bootstrap.test:33445:$key" \
    --tcp-relay "relay.test:443:$key" \
    --run-ms 60000 >"$log" 2>&1 &
node_pid=$!

for _ in $(seq 1 500); do
    [[ -S "$runtime/control.sock" ]] && break
    kill -0 "$node_pid" 2>/dev/null || {
        cat "$log" >&2
        exit 1
    }
    sleep 0.01
done
[[ -S "$runtime/control.sock" ]]

"$build_dir/iotox" --runtime "$runtime" ping
"$build_dir/iotox" --runtime "$runtime" status
"$build_dir/iotox" --runtime "$runtime" identity
"$build_dir/iotox" --runtime "$runtime" authority

# Establish the sovereign local constitution before asking the mock peer to
# prove a principal.  This fixed phrase exists only inside the disposable
# fixture; production operators should use recall-generate and protect the
# output as their permanent owner secret.
recall_phrase='abacus abdomen abdominal abide abiding ability ablaze able'
owner_public_key=$(printf '%s\n' "$recall_phrase" | \
    "$build_dir/iotox" --runtime "$runtime" \
        authority-bootstrap-recall-stdin | \
    sed -n 's/^owner-public-key=//p')
[[ ${#owner_public_key} -eq 64 ]]
mock_authority_public_key=D75A980182B10AB7D54BFED3C964073A0EE172F3DAA62325AF021A68F707511A
printf '%s\n' "$recall_phrase" | \
    "$build_dir/iotox" --runtime "$runtime" \
        authority-grant-recall-stdin "$mock_authority_public_key" \
        automation read.telemetry,write.settings,actuate
"$build_dir/iotox" --runtime "$runtime" authority | grep -q '^sequence=2$'
"$build_dir/iotox" --runtime "$runtime" principals | \
    grep -q "public-key=$mock_authority_public_key active=1 role=automation"

# The mock injects one incoming request from public key A7...A7. The request
# remains a transport-only live inbox record until the operator accepts or
# rejects it; this fixture rejects it and verifies no peer was created.
request_peer=A7A7A7A7A7A7A7A7A7A7A7A7A7A7A7A7A7A7A7A7A7A7A7A7A7A7A7A7A7A7A7A7
for _ in $(seq 1 500); do
    if "$build_dir/iotox" --runtime "$runtime" requests | \
        grep -q "public-key=$request_peer"; then
        break
    fi
    kill -0 "$node_pid" 2>/dev/null || {
        cat "$log" >&2
        exit 1
    }
    sleep 0.01
done
"$build_dir/iotox" --runtime "$runtime" requests | \
    grep -q 'message=please-add-this-device'
request_reject_fifo="$runtime/requests/$request_peer/reject"
[[ -p "$request_reject_fifo" ]]
printf '%s\n' reject > "$request_reject_fifo"
# FIFO write success is only kernel admission. Poll the semantic projection
# until the Agent has consumed the exact decision and withdrawn the request.
request_rejected=0
for _ in $(seq 1 500); do
    if ! "$build_dir/iotox" --runtime "$runtime" requests | \
        grep -q "public-key=$request_peer"; then
        request_rejected=1
        break
    fi
    kill -0 "$node_pid" 2>/dev/null || {
        cat "$log" >&2
        exit 1
    }
    sleep 0.01
done
[[ $request_rejected -eq 1 ]]
grep -q 'source=local-fifo operation=request-reject' \
    "$runtime/friend-events"

peer=4242424242424242424242424242424242424242424242424242424242424242
"$build_dir/iotox" --runtime "$runtime" transport-peer-accept "$peer"

# Friend acceptance is not connection establishment. Wait for toxcore's online
# callback and IoTox's automatic HELLO-and-confirmation negotiation before
# exercising an explicit byte-identical retry.
for _ in $(seq 1 500); do
    if [[ -f "$runtime/peers/$peer/session" ]] &&
       grep -q 'state=confirmed' "$runtime/peers/$peer/session"; then
        break
    fi
    kill -0 "$node_pid" 2>/dev/null || {
        cat "$log" >&2
        exit 1
    }
    sleep 0.01
done
grep -q 'state=confirmed' "$runtime/peers/$peer/session"

printf '%s' 'IoTox Mock Node' | \
    "$build_dir/iotox" --runtime "$runtime" profile-name-stdin
"$build_dir/iotox" --runtime "$runtime" profile-status-message \
    one binary speaks
printf 'operator\0message\n' | \
    "$build_dir/iotox" --runtime "$runtime" action-stdin "$peer"

# Exercise the literal ratox-successor human lane as an ordinary shell write.
# The structured action above consumes valid message id zero; this normal FIFO
# write must preserve the next id and expose local ingress separately from the
# outgoing/incoming/read-receipt transport journal.
message_fifo="$runtime/peers/$peer/message"
message_events="$runtime/peers/$peer/message-events"
for _ in $(seq 1 500); do
    [[ -p "$message_fifo" && -f "$runtime/peers/$peer/message.help" ]] && break
    kill -0 "$node_pid" 2>/dev/null || {
        cat "$log" >&2
        exit 1
    }
    sleep 0.01
done
[[ -p "$message_fifo" ]]
printf '%s\n' ratox-writes > "$message_fifo"

"$build_dir/iotox" --runtime "$runtime" typing "$peer" on

# Adding an online peer starts the IoTox session automatically. Wait for the
# canonical HELLO and mutual confirmation to traverse the real owner thread, callback queue,
# decoder, session registry, local control server, and private runtime tree.
for _ in $(seq 1 500); do
    if [[ -f "$runtime/peers/$peer/session" ]] &&
       grep -q '^state=confirmed$' "$runtime/peers/$peer/session"; then
        break
    fi
    kill -0 "$node_pid" 2>/dev/null || {
        cat "$log" >&2
        exit 1
    }
    sleep 0.01
done
grep -q 'kind=lossless-packet' "$runtime/events"
for _ in $(seq 1 500); do
    [[ -f "$runtime/peers/$peer/messages" && -f "$runtime/peers/$peer/protocol" ]] && break
    sleep 0.01
done
"$build_dir/iotox" --runtime "$runtime" sessions
"$build_dir/iotox" --runtime "$runtime" session "$peer"
"$build_dir/iotox" --runtime "$runtime" peer-session "$peer"
"$build_dir/iotox" --runtime "$runtime" peer-messages "$peer"
"$build_dir/iotox" --runtime "$runtime" peer-protocol "$peer"
grep -q '^hello-sent=1$' "$runtime/peers/$peer/session"
grep -q '^hello-received=1$' "$runtime/peers/$peer/session"
grep -q '^confirmation-sent=1$' "$runtime/peers/$peer/session"
grep -q '^confirmation-received=1$' "$runtime/peers/$peer/session"
grep -q '^hello-send-attempts=2$' "$runtime/peers/$peer/session"
grep -q '^confirmation-send-attempts=2$' "$runtime/peers/$peer/session"
! grep -q '^last-hello-send-error=' "$runtime/peers/$peer/session"
! grep -q '^last-confirmation-send-error=' "$runtime/peers/$peer/session"
grep -q '^application-ready=1$' "$runtime/peers/$peer/session"
grep -q '^authorization=separate-authority-session$' "$runtime/peers/$peer/session"
grep -q 'direction=outgoing kind=action message-id=0' "$runtime/peers/$peer/messages"
for _ in $(seq 1 500); do
    if [[ -f "$message_events" ]] &&
       grep -q 'kind=normal disposition=accepted error-code=0 message-id=1' "$message_events" &&
       grep -q 'body=ratox-writes' "$message_events" &&
       grep -q 'direction=outgoing kind=normal message-id=1' "$runtime/peers/$peer/messages" &&
       grep -q 'direction=incoming kind=normal' "$runtime/peers/$peer/messages" &&
       grep -q 'direction=receipt kind=normal message-id=1' "$runtime/peers/$peer/messages"; then
        break
    fi
    kill -0 "$node_pid" 2>/dev/null || {
        cat "$log" >&2
        exit 1
    }
    sleep 0.01
done
grep -q 'kind=normal disposition=accepted error-code=0 message-id=1' "$message_events"
"$build_dir/iotox" --runtime "$runtime" peer-message-events "$peer" |
    grep -q 'kind=normal disposition=accepted'
grep -q 'direction=outgoing protocol=1.0 type=hello' "$runtime/peers/$peer/protocol"
grep -q 'direction=incoming protocol=1.0 type=hello' "$runtime/peers/$peer/protocol"
grep -q 'direction=outgoing protocol=1.0 type=capabilities' "$runtime/peers/$peer/protocol"
grep -q 'direction=incoming protocol=1.0 type=capabilities' "$runtime/peers/$peer/protocol"

# Each side proves a stable application principal after transcript confirmation.
# The agent answers the peer challenge with its stable device identity automatically;
# RecallRoot re-entry is an explicit owner ceremony, not the day-to-day device claimant.
device_public_key=$("$build_dir/iotox" --runtime "$runtime" identity | \
    sed -n 's/^device-public-key=//p')
[[ ${#device_public_key} -eq 64 ]]
for _ in $(seq 1 1000); do
    authority_state=$("$build_dir/iotox" --runtime "$runtime" authority-session "$peer")
    if grep -q '^verifier-state=authorized$' <<<"$authority_state" &&
       grep -q '^claimant-state=proof-sent$' <<<"$authority_state" &&
       grep -q '^challenge-send-attempts=2$' <<<"$authority_state" &&
       grep -q '^proof-send-attempts=2$' <<<"$authority_state"; then
        break
    fi
    kill -0 "$node_pid" 2>/dev/null || {
        cat "$log" >&2
        exit 1
    }
    sleep 0.01
done
grep -q '^remote-authorized=1$' <<<"$authority_state"
grep -q "^remote-principal=$mock_authority_public_key$" <<<"$authority_state"
grep -q '^remote-role=automation$' <<<"$authority_state"
grep -q '^remote-capabilities=read.telemetry,write.settings,actuate$' <<<"$authority_state"
grep -q "^local-claimant-principal=$device_public_key$" <<<"$authority_state"
grep -q '^challenge-send-attempts=2$' <<<"$authority_state"
grep -q '^proof-send-attempts=2$' <<<"$authority_state"
! grep -q '^last-challenge-send-error=' <<<"$authority_state"
! grep -q '^last-proof-send-error=' <<<"$authority_state"
grep -q "agent-proof-verified principal=$device_public_key" "$authority_audit"
grep -q 'direction=outgoing protocol=1.0 type=authority-challenge' "$runtime/peers/$peer/protocol"
grep -q 'direction=incoming protocol=1.0 type=authority-proof' "$runtime/peers/$peer/protocol"
grep -q 'direction=incoming protocol=1.0 type=authority-challenge' "$runtime/peers/$peer/protocol"
grep -q 'direction=outgoing protocol=1.0 type=authority-proof' "$runtime/peers/$peer/protocol"

# The exact peer asks once before its principal is admitted and once afterward.
# IoTox must deny the former, complete the latter, and retry the same frozen
# COMMAND_RESULT after one injected toxcore SENDQ response.
peer_operation_complete=0
for _ in $(seq 1 1000); do
    if grep -q 'preauthority-device-describe-denied' "$authority_audit" &&
       grep -q "authorized-device-describe-succeeded principal=$device_public_key revision=$expected_revision_number" "$authority_audit" &&
       grep -q 'authorized-device-describe-duplicate-replayed-exact' "$authority_audit" &&
       [[ $(grep -c 'command-result-sendq correlation=' "$authority_audit" || true) -ge 2 ]]; then
        peer_operation_complete=1
        break
    fi
    kill -0 "$node_pid" 2>/dev/null || {
        cat "$log" >&2
        cat "$authority_audit" >&2 || true
        exit 1
    }
    sleep 0.01
done
[[ $peer_operation_complete -eq 1 ]]
grep -q 'direction=incoming protocol=1.0 type=command' "$runtime/peers/$peer/protocol"
grep -q 'direction=outgoing protocol=1.0 type=command-result' "$runtime/peers/$peer/protocol"

# The operator now uses the literal ratox-successor surface: one ordinary,
# newline-terminated write to the private per-peer FIFO. The adapter must not
# become a second queue. It has succeeded only after command-events names a
# nonzero durable identity created by the same signed command store used by the
# structured control client. Admission is recorded as reserved; the later
# device-description projection proves the injected first SENDQ and exact retry.
command_fifo="$runtime/peers/$peer/command"
command_events="$runtime/peers/$peer/command-events"
for _ in $(seq 1 500); do
    [[ -p "$command_fifo" && -f "$runtime/peers/$peer/command.help" ]] && break
    kill -0 "$node_pid" 2>/dev/null || {
        cat "$log" >&2
        exit 1
    }
    sleep 0.01
done
[[ -p "$command_fifo" ]]
grep -q '^operation=device.describe$' "$runtime/peers/$peer/command.help"
printf '%s\n' device.describe > "$command_fifo"

fifo_admitted=0
for _ in $(seq 1 1000); do
    if [[ -f "$command_events" ]] &&
       grep -q 'operation=device.describe' "$command_events" &&
       grep -q 'disposition=admitted' "$command_events" &&
       grep -q 'error-code=0' "$command_events" &&
       grep -q 'state=reserved' "$command_events" &&
       grep -Eq 'sender-epoch=[1-9][0-9]*' "$command_events" &&
       grep -Eq 'message-id=[1-9][0-9]*' "$command_events"; then
        fifo_admitted=1
        break
    fi
    kill -0 "$node_pid" 2>/dev/null || {
        cat "$log" >&2
        cat "$command_events" >&2 || true
        exit 1
    }
    sleep 0.01
done
[[ $fifo_admitted -eq 1 ]]
for _ in $(seq 1 1000); do
    peer_description=$("$build_dir/iotox" --runtime "$runtime" peer-description "$peer")
    if grep -q '^state=succeeded$' <<<"$peer_description" &&
       grep -q '^send-attempts=2$' <<<"$peer_description"; then
        break
    fi
    kill -0 "$node_pid" 2>/dev/null || {
        cat "$log" >&2
        exit 1
    }
    sleep 0.01
done
grep -q "^device-principal=$mock_authority_public_key$" <<<"$peer_description"
grep -q "^version=$expected_version$" <<<"$peer_description"
grep -q "^revision=$expected_revision$" <<<"$peer_description"
grep -q '^protocol=1.0$' <<<"$peer_description"
grep -q 'mock-device-describe-response-sent' "$authority_audit"
# The control reply and the ratox-style runtime projection are published by
# adjacent agent steps, not one atomic filesystem transaction. Poll the
# observation surface rather than assuming it is already caught up when the
# structured reply arrives.
description_projection="$runtime/peers/$peer/iotox/description"
description_projected=0
for _ in $(seq 1 1000); do
    if [[ -f "$description_projection/state" &&
          -f "$description_projection/send-attempts" &&
          -f "$description_projection/device-principal" ]] &&
       grep -q '^succeeded$' "$description_projection/state" &&
       grep -q '^2$' "$description_projection/send-attempts" &&
       grep -q "^$mock_authority_public_key$" \
           "$description_projection/device-principal"; then
        description_projected=1
        break
    fi
    kill -0 "$node_pid" 2>/dev/null || {
        cat "$log" >&2
        exit 1
    }
    sleep 0.01
done
[[ $description_projected -eq 1 ]]
fifo_status=$("$build_dir/iotox" --runtime "$runtime" status)
grep -q '^command-fifo-running=1$' <<<"$fifo_status"
grep -q '^command-fifo-count=1$' <<<"$fifo_status"
grep -q '^command-fifo-record-count=1$' <<<"$fifo_status"
grep -q '^command-fifo-rejected-count=0$' <<<"$fifo_status"
grep -q '^text-fifo-running=1$' <<<"$fifo_status"
grep -q '^message-fifo-count=1$' <<<"$fifo_status"
grep -q '^action-fifo-count=1$' <<<"$fifo_status"
grep -q '^text-fifo-record-count=1$' <<<"$fifo_status"
grep -q '^text-fifo-rejected-count=0$' <<<"$fifo_status"
grep -q '^file-fifo-running=1$' <<<"$fifo_status"
grep -q '^file-send-fifo-count=1$' <<<"$fifo_status"
grep -q '^file-receive-fifo-count=1$' <<<"$fifo_status"
grep -q '^file-control-fifo-count=1$' <<<"$fifo_status"

# Operators may explicitly retry the same frozen HELLO and confirmation.
# Byte-identical retries are idempotent for the online epoch.
"$build_dir/iotox" --runtime "$runtime" hello "$peer"
"$build_dir/iotox" --runtime "$runtime" confirm "$peer"
sleep 0.05
grep -q '^state=confirmed$' "$runtime/peers/$peer/session"

# The process-wide ratox successor entrance is the ordinary root `request`
# FIFO. Run it only after the main peer has consumed the fixture's deliberate
# one-shot SENDQ failures. A malformed complete record must remain observable
# as keyless; the exact address<TAB>message record must create a public-key
# selected peer through tox_friend_add and the shared Agent operation.
[[ -p "$runtime/request" ]]
grep -q '^maximum-record-bytes=998 ' "$runtime/request.help"
printf '%s\n' too-short > "$runtime/request"
requested_peer=C5C5C5C5C5C5C5C5C5C5C5C5C5C5C5C5C5C5C5C5C5C5C5C5C5C5C5C5C5C5C5C5
requested_address=${requested_peer}010203040206
printf '%s\t%s\n' "$requested_address" mock-root-request > "$runtime/request"
requested_peer_directory="$runtime/peers/$requested_peer"
root_request_committed=0
for _ in $(seq 1 500); do
    current_status=$("$build_dir/iotox" --runtime "$runtime" status)
    if [[ -d "$requested_peer_directory" ]] &&
       grep -q "source=local-fifo operation=request-send public-key=$requested_peer disposition=requested" "$runtime/friend-events" &&
       grep -q 'source=local-fifo operation=request-send public-key=unknown disposition=rejected' "$runtime/friend-events" &&
       grep -q 'not evidence of remote receipt or acceptance' "$runtime/friend-events" &&
       grep -q '^request-send-fifo-count=1$' <<<"$current_status"; then
        root_request_committed=1
        break
    fi
    kill -0 "$node_pid" 2>/dev/null || {
        cat "$log" >&2
        cat "$runtime/friend-events" >&2 || true
        exit 1
    }
    sleep 0.01
done
[[ $root_request_committed -eq 1 ]]
[[ -p "$requested_peer_directory/remove" ]]
printf '%s\n' remove > "$requested_peer_directory/remove"
for _ in $(seq 1 500); do
    [[ ! -e "$requested_peer_directory" ]] && break
    kill -0 "$node_pid" 2>/dev/null || {
        cat "$log" >&2
        exit 1
    }
    sleep 0.01
done
[[ ! -e "$requested_peer_directory" ]]

# The final lifecycle mutation is also the ordinary ratox-style file, not a
# second product or numeric friend-handle command. The public-key directory is
# withdrawn only after the key-bound toxcore owner-thread operation succeeds.
peer_remove_fifo="$runtime/peers/$peer/remove"
[[ -p "$peer_remove_fifo" ]]
printf '%s\n' remove > "$peer_remove_fifo"
for _ in $(seq 1 500); do
    [[ ! -e "$runtime/peers/$peer" ]] && break
    kill -0 "$node_pid" 2>/dev/null || {
        cat "$log" >&2
        exit 1
    }
    sleep 0.01
done
[[ ! -e "$runtime/peers/$peer" ]]

# Runtime withdrawal and friendship-journal publication are adjacent agent
# effects, not one filesystem transaction. The peer directory may disappear
# immediately before the best-effort append becomes visible. Poll the stronger
# semantic observation instead of treating directory absence as journal
# completion or FIFO write(2) success as acceptance.
friend_lifecycle_observed=0
for _ in $(seq 1 500); do
    if grep -q 'source=local-fifo operation=request-reject' "$runtime/friend-events" &&
       grep -q 'source=local-fifo operation=request-send' "$runtime/friend-events" &&
       grep -q 'source=local-fifo operation=peer-remove' "$runtime/friend-events" &&
       grep -q 'IoTox authority is unchanged' "$runtime/friend-events"; then
        friend_lifecycle_observed=1
        break
    fi
    kill -0 "$node_pid" 2>/dev/null || {
        cat "$log" >&2
        cat "$runtime/friend-events" >&2 || true
        exit 1
    }
    sleep 0.01
done
[[ $friend_lifecycle_observed -eq 1 ]]

"$build_dir/iotox" --runtime "$runtime" stop
wait "$node_pid"
node_pid=

first_address=$(sed -n 's/^address=//p' "$log" | head -n1)
[[ ${#first_address} -eq 76 ]]
[[ -s "$state" ]]
[[ $(stat -c '%a' "$state") == 600 ]]
grep -q 'kind=lossless-packet' "$runtime/events"
grep -q 'kind=bootstrap' "$runtime/events"
grep -q 'kind=tcp-relay' "$runtime/events"

second_log="$work/iotox-run-restart.log"
"$build_dir/iotox" run \
    --library "$build_dir/libtoxcore-iotox-mock.so" \
    --runtime "$runtime" \
    --state "$state" \
    --run-ms 30000 >"$second_log" 2>&1 &
node_pid=$!
for _ in $(seq 1 500); do
    [[ -S "$runtime/control.sock" ]] && break
    kill -0 "$node_pid" 2>/dev/null || {
        cat "$second_log" >&2
        exit 1
    }
    sleep 0.01
done
second_address=$("$build_dir/iotox" --runtime "$runtime" address | tr -d '\n')
[[ "$second_address" == "$first_address" ]]
"$build_dir/iotox" --runtime "$runtime" stop
wait "$node_pid"
node_pid=

cat "$log"
cat "$second_log"
printf '%s\n' 'mock-node-lifecycle=pass'
