# IoTox command protocol v1

**Revision:** rev0041 construction line
**Maturity:** read operations and `profile.status.set` are established construction surfaces.
`update.stage` is unit/process/restart verified and network-verified between two genuine
source-linked peers over direct UDP and forced TCP. It stages one inert inactive slot; it does not
authorize apply, restart, health confirmation, executable installation, or a target-hardware claim.

This document freezes the first machine-operation records carried inside the IoTox 41-byte
lossless custom-packet frame. Multi-byte integers are big-endian. Reserved bytes must be zero.
Decoders reject trailing bytes, unknown versions, unsupported operations, inconsistent body sizes,
and payloads beyond the negotiated frame ceiling.

## 1. Admission order

A peer-originated command is considered only after:

1. Tox reports the friend connected;
2. both canonical HELLO records are frozen and compatible;
3. both peers confirm the exact transcript and negotiation result;
4. both negotiated `durable_commands_v1` for the durable path;
5. the local verifier accepts a transcript-bound proof from an active ledger principal;
6. that principal's current capability mask covers the exact operation.

`update.stage` additionally requires bilateral `signed-ota-v1`, the locally configured update
construction, and one exact current accepted synchronization HEAD. A peer that did not negotiate
the feature receives `unsupported`; no update effect or durable incoming record is created.

Friendship, connectivity, compatibility, confirmation, and transport queue acceptance do not grant
an application capability.

## 2. Durable envelope rules

For a durable `COMMAND`:

```text
frame.type              command
frame.flags             0
frame.message_id        nonzero sender-chosen command id
frame.correlation_id    0
frame.sequence          persistent nonzero sender epoch
frame.expiry_unix_ms    0 or absolute deadline for read-only operations
```

The receiver's durable key is:

```text
sender Tox public key + frame.sequence + frame.message_id
```

The receiver does not use toxcore friend number or the current online epoch as durable identity.

For its receipt and result:

```text
frame.sequence          exact request sender epoch
frame.correlation_id    exact request message id
frame.message_id        new nonzero artifact id
```

A sender must not rotate the sender epoch or message id merely because toxcore rejected a send with
retryable local `SENDQ`/not-connected pressure. It retries the exact canonical frame.

Legacy peers that did not negotiate `durable_commands_v1` use sequence zero and process-local
behavior. That path exists for compatibility research and rejects every mutating operation.

## 3. `COMMAND` request: `ICQ1`

Fixed payload length: 8 bytes. Full current frame length: 49 bytes.

```text
0..3   magic "ICQ1"
4      payload format version = 1
5      operation
6      operation argument
7      reserved = 0
```

The frozen operation table is:

| Value | Name | Byte 6 | Required capability | Restart policy |
|---:|---|---|---|---|
| 1 | `device.describe` | 0 | `read.telemetry` | read-only re-execution |
| 2 | `system.summary` | 0 | `read.telemetry` | read-only re-execution |
| 3 | `profile.status.set` | 0 available, 1 away, 2 busy | `write.settings` | idempotent desired-state reapplication |

Unknown values, a nonzero byte 6 on either read, a status value above 2, or a nonzero byte 7 are
malformed. Operation 3 occupies advertised-operation bit 2. Existing protocol-v1 peers that do not
implement it reject the unknown operation without changing the fixed `ICQ1` shape.

### 3.1 `update.stage` request: `ICQ2`

Fixed payload length: 40 bytes. Full current frame length: 81 bytes.

```text
0..3    magic "ICQ2"
4       payload format version = 2
5       operation = 4 (`update.stage`)
6..7    reserved = 0
8..39   exact current accepted synchronization HEAD record
```

The HEAD must be nonzero. Operation 4 occupies advertised-operation bit 3 and requires
`install.firmware`. It uses a distinct fixed request because the existing 8-byte `ICQ1` record is
frozen. It requires `expiry_unix_ms = 0`.

A durable outgoing request is committed to the signed local command store before the first toxcore
send. A valid incoming request is committed before any application receipt is sent.

## 4. `ACKNOWLEDGEMENT` receipt: `ICA1`

Fixed payload length: 8 bytes. Full current frame length: 49 bytes.

```text
0..3   magic "ICA1"
4      receipt format version = 1
5      stage
6..7   reserved = 0
```

Stages are:

```text
1 received
2 admitted
3 started
```

rev0010 sends only `received`. The other stage values are reserved in the frozen codec so later
revisions can add truthful progress receipts without changing the payload shape.

`received` means:

```text
the exact request and exact receipt are committed in the receiver's durable store
```

It does not mean:

```text
the principal was authorized
the command started
the command completed
the result reached the sender
```

A receipt is application evidence, separate from c-toxcore accepting a packet into its local send
queue.

## 5. `COMMAND_RESULT`: `ICR1`

Header length: 16 bytes followed by exactly `body_length` bytes.

```text
0..3    magic "ICR1"
4       result format version = 1
5       operation
6       outcome
7       reserved = 0
8..11   body length
12..15  reserved = 0
16..    body
```

Outcomes:

```text
0 succeeded
1 denied
2 malformed
3 unsupported
4 expired
5 conflict
6 internal-error
```

A failed result has an empty body. A successful `device.describe` result has exactly the 64-byte
`IDD1` body below; a successful `system.summary` result has exactly the 40-byte `ISS1` body below;
a successful `profile.status.set` result has exactly the 8-byte `IPS1` body below; and a successful
`update.stage` result has exactly the 80-byte `IUS1` body below.

The receiver commits the exact terminal result before asking toxcore to send it. An exact duplicate
request replays the frozen receipt and terminal result. Different canonical bytes reusing the same
durable key receive a conflict result and do not mutate the original record.

## 6. `device.describe` result body: `IDD1`

Fixed length: 64 bytes. Successful full result frame length: 121 bytes.

```text
0..3    magic "IDD1"
4       body format version = 1
5       reserved = 0
6..7    revision number
8..9    semantic version major
10..11  semantic version minor
12..13  semantic version patch
14      negotiated protocol major
15      negotiated protocol minor
16..47  stable Ed25519 device principal
48..55  implemented feature mask
56..63  offered operation mask
```

A sender accepts a successful description only when:

- the protocol version equals the current confirmed session;
- the device principal equals the verifier device in the peer's accepted challenge;
- the result correlates to the exact durable request identity;
- it is the first canonical result or a byte-identical duplicate.

## 7. `system.summary` result body: `ISS1`

Fixed length: 40 bytes. Integers are unsigned big-endian.

```text
0..3    magic "ISS1"
4       body format version = 1
5       health: 0 unknown, 1 healthy, 2 degraded
6..7    validity flags: memory=1, load=2, process-count=4
8..11   uptime in whole minutes
12..15  total memory in 64 MiB buckets
16..19  available memory in 64 MiB buckets
20..23  one-minute load in milli units, quantized to multiples of 100
24..27  process count
28..39  reserved = 0
```

Available memory cannot exceed total memory; load is bounded at 1,000,000 and process count at
10,000,000. The body never contains host names, users, addresses, machine identifiers, mounts,
process names, command lines, kernel versions, or free-form provider strings. ADR 0051 owns this
privacy contract.

A non-identical second receipt or result for the same correlation is a protocol conflict.

## 8. `profile.status.set` result body: `IPS1`

Fixed length: 8 bytes. Successful full result frame length: 65 bytes.

```text
0..3   magic "IPS1"
4      body format version = 1
5      desired status: 0 available, 1 away, 2 busy
6      provider-observed status: 0 available, 1 away, 2 busy
7      reserved = 0
```

A successful body is canonical only when desired equals observed. The receiver performs the real
c-toxcore profile mutation on the transport owner thread, persists tox savedata before that call
returns, reads the provider state back, and only then commits `IPS1` plus the terminal command result.
The provider surfaces atomic savedata failure to the Agent. An effect, persistence, or readback error
leaves the durable lifecycle at `started` and commits no terminal result, because the local effect is
then uncertain and the exact bounded desired value is the only safe recovery input.
The evidence proves convergence at that readback instant. It does not prove that the result reached
the sender or that some later authorized/local mutation did not change presence again.

Presence is transport presentation state. It is not IoTox identity, authorization, physical
actuation, or a safety signal. The operation requires the narrower existing `write.settings`
capability; `actuate` is neither required nor implied.

## 9. `update.stage` result body: `IUS1`

Fixed length: 80 bytes. Successful full result frame length: 137 bytes.

```text
0..3    magic "IUS1"
4       body format version = 1
5       already-staged flag: 0 first stage, 1 exact inactive state already existed
6..7    reserved = 0
8..15   verified release sequence
16..47  exact accepted synchronization HEAD from `ICQ2`
48..79  verified signed-update manifest record
```

The sequence, accepted HEAD, and manifest record must all be nonzero. The accepted HEAD must equal
the request. The flag describes the update store's idempotent staging result; it is not a transport
duplicate flag. An exact duplicate durable command replays the already committed `ICR1` bytes.

The receiver serializes update mutation, reopens the locally configured range-v1 namespace, and
requires `ICQ2` to name its exact current accepted HEAD. It re-verifies the artifact and signed
bundle under owner-private update policy, copies only inert payload bytes to a digest-named
mode-`0400` inactive slot, and commits stable-device-signed staged state. A different or stale HEAD
returns `conflict`. Construction or storage failure returns `internal-error`. Neither outcome
weakens the accepted HEAD or update policy.

Feature bit 20 is advertised only when the local update construction opened successfully. A HELLO
that advertises it without `durable-commands-v1`, `state-sync-v1`, and `state-sync-ranges-v1` is
invalid. Execution also requires the bit in the confirmed shared feature set and a current
transcript-bound `install.firmware` proof under the active ownership epoch.

Successful remote staging grants no `update-apply`, restart, health-token, `update-confirm`,
executable, bootloader, or device-local path authority. Those local effect boundaries remain
separate.

## 10. Local durable lifecycle

The wire protocol does not expose the complete local lifecycle, but implementations need an
unambiguous crash model.

Outgoing:

```text
reserved
    request bytes committed before send
locally-queued
    toxcore accepted the exact packet into its local queue
succeeded|failed|expired
    terminal result committed
```

Incoming:

```text
received
    request and RECEIVED receipt committed
admitted
    current authority decision and ledger head committed
started
    execution start committed
succeeded|failed|expired
    terminal result committed before send
```

Receipt/result delivery state is recorded independently because a command can be terminal locally
while its result is still pending transport.

## 11. Restart and duplicate behavior

On reconnect or restart:

- scans outgoing nonterminal restart-safe records and reuses exact request bytes;
- reconstructs the live peer-description projection from durable state;
- resumes read-only incoming records when session and authority are available;
- may reapply only the exact frozen `profile.status.set` desired value or exact frozen
  `update.stage` HEAD after `STARTED`, because each declares idempotent desired-state recovery;
- resends pending/failure-marked frozen receipt/result artifacts;
- replays terminal evidence on exact duplicate requests;
- keeps the local sender epoch stable.

An admitted or started effect is resumed only after the same stable principal proves current
authority under the same ownership epoch. A revoked principal, a substituted principal on the same
Tox key, or an ownership transition holds the unfinished record and performs no new effect. Later
same-epoch ledger heads are allowed only after fresh exact-head proof still grants the operation.

The crash window is explicit: death after the provider effect but before savedata or result commit
can lose provider persistence and leave lifecycle `started`; recovery may therefore apply the same
desired status again. It never invents a new desired value or command identity. The
separate-process gate stops inside the provider in that exact window, kills the daemon, restarts it,
and proves one recovery reapplication followed by converged evidence.

`update.stage` recovery adopts an already committed exact staged state and emits `IUS1` with the
already-staged flag. It never applies the candidate. No other mutation is restart-safe. A physical
operation must supply its own effect identity,
idempotency, reservation, cancellation, compensation, expiry, and power-cut contract before it can
enter this recovery path.

## 12. Expiry and clocks

The outer frame contains `expiry_unix_ms`, and the current receiver can return `expired`. This is
not yet a safe physical-effect deadline because many IoT devices boot without trustworthy wall
clock.

Before expiry governs an effect, IoTox must define at least:

```text
issued-at and/or relative TTL semantics
clock-quality evidence
sender and receiver restart epochs
maximum accepted skew
replay windows
behavior when time moves backward
```

`profile.status.set` and `update.stage` require `expiry_unix_ms = 0`; both local admission and remote
envelope validation reject an expiring mutation. This avoids reporting expiry after a pre-crash
effect may already have happened. Read-only commands retain the existing trusted-wall-clock TTL
behavior.

## 13. Size budget

c-toxcore 0.2.23 documents a maximum custom-packet size of 1,373 bytes. The IoTox outer frame uses
41 bytes, leaving 1,332 payload bytes.

Current records:

```text
COMMAND device.describe       49 bytes total
COMMAND profile.status.set    49 bytes total
COMMAND update.stage          81 bytes total
ACKNOWLEDGEMENT received      49 bytes total
COMMAND_RESULT denied         57 bytes total
COMMAND_RESULT profile status 65 bytes total
COMMAND_RESULT system summary 97 bytes total
COMMAND_RESULT describe       121 bytes total
COMMAND_RESULT update stage   137 bytes total
```

Large configuration, diagnostics, and firmware do not belong in fragmented command payloads. They
should use Tox file transfer plus a signed manifest and durable command reference.

## 14. Local command entrances

The wire protocol is unchanged by either local adapter. The structured form is:

```text
iotox command FRIEND device.describe [PRIORITY [TTL_MS]]
iotox command FRIEND system.summary [PRIORITY [TTL_MS]]
iotox command FRIEND profile.status.set available|away|busy [PRIORITY]
iotox command FRIEND update.stage HEAD_RECORD_HEX [PRIORITY]
```

Local control extends `command-issue` with one bounded desired-status byte for operation 3 and one
exact 32-byte HEAD for operation 4. The older no-argument forms remain valid for reads. A missing,
extra, or invalid status or 64-hex HEAD is rejected before socket submission; a TTL on either
mutation is rejected by Agent admission.

A complete FIFO record contains printable ASCII followed by LF. The accepted grammar is exactly:

```text
device.describe
system.summary
profile.status.set available|away|busy
update.stage HEAD_RECORD_HEX
```

There is no quoting, escaping, or free-form argument tail.

The ordinary `command-cancel` contract is unchanged. It may cancel an outgoing `update.stage` only
while its durable record is reserved with zero committed send attempts. After any attempt, remote
observation cannot be disproved, so cancellation is refused. Store limits remain 256 unfinished
records globally, 32 per peer/direction, 256 KiB canonical bytes per peer/direction, and the
absolute 1,024-record/8 MiB ceiling. No unfinished record is evicted for an update.

The adapter performs no wire encoding until the ordinary record has passed the same operation
registry and durable outgoing reservation used by the structured client. The resulting canonical
`COMMAND` frame, sender epoch, and message id are therefore identical in kind regardless of local
ingress.

```text
FIFO write success
    != durable admission
    != toxcore enqueue
    != remote RECEIVED
    != authority admission
    != STARTED
    != terminal result
```

An admitted transient `command-events` line publishes the durable key. The signed command store is
the authority for exact frame and lifecycle. See `ratox-command-fifo-v1.md` and ADR 0040.
