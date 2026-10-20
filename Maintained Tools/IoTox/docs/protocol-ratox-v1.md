# Ratox interactive framing v1

Status: frozen framing and failure semantics; parser, pure R1 session model, default-off live R4
Agent/PTy dispatch, R5 controller stream, and the first deterministic-provider R6 restart/fault
contract are implemented. Production/default advertisement remains disabled, and genuine two-host
qualification remains R7 evidence. Date: 2026-08-17.

Ratox v1 is a separately authorized ordered terminal-byte protocol carried only by paced
c-toxcore custom-lossless packets. It does not reuse human Tox messages, IoTox command frames,
files, diagnostic probes, or custom-lossy packets. Its custom packet ID is `0xA2`; negotiation
feature bit 23 is named `ratox-interactive-v1` and is advertised only after explicit secure
pre-network activation; ordinary/default construction keeps it clear.

## Packet boundary

Every v1 packet is 124..1,200 bytes. Integers are unsigned big-endian unless stated otherwise.
The fixed header is:

| Offset | Bytes | Field | v1 rule |
|---:|---:|---|---|
| 0 | 1 | packet ID | `0xA2` |
| 1 | 1 | major | `1` |
| 2 | 1 | minor | `0` |
| 3 | 1 | frame type | 1..17 below |
| 4 | 1 | flags | zero; no v1 flag is assigned |
| 5 | 1 | header bytes | `124` |
| 6 | 2 | payload bytes | exact trailing byte count, at most 1,076 |
| 8 | 8 | message ID | nonzero; never reused by one sender in a session |
| 16 | 8 | correlation ID | request message ID on result frames, otherwise zero; `EXIT_STATUS` may correlate a close |
| 24 | 16 | session ID | nonzero random stable session identity |
| 40 | 32 | controller principal | nonzero authority-ledger signing principal |
| 72 | 16 | attachment nonce | nonzero and fresh for each OPEN/ATTACH/RESUME attempt |
| 88 | 8 | terminal incarnation | zero on OPEN and denied OPEN_RESULT; changes when the PTY/process is replaced |
| 96 | 8 | attachment generation | zero on OPEN/ATTACH and their denied result; nonzero on acceptance and attached traffic |
| 104 | 8 | byte sequence | first byte position on INPUT/OUTPUT; retained base on OUTPUT_GAP |
| 112 | 8 | cumulative ACK | next expected byte; may be piggybacked on INPUT/OUTPUT |
| 120 | 4 | reserved | zero |

Unknown major/minor versions, types, flags, header sizes, reserved bytes, noncanonical lengths,
impossible attachment states, and invalid stream positions are rejected before side effects.

## Frame registry and payloads

| ID | Type | Payload |
|---:|---|---|
| 1 | `OPEN` | 12-byte open parameters |
| 2 | `OPEN_RESULT` | 12-byte result and accepted parameters |
| 3 | `ATTACH` | next input and output positions, two u64 values |
| 4 | `ATTACH_RESULT` | result u16, reserved u16, next input, output base, output next (three u64) |
| 5 | `DETACH` | empty |
| 6 | `INPUT` | 1..1,076 opaque PTY input bytes |
| 7 | `INPUT_ACK` | empty; cumulative position is in the header ACK |
| 8 | `OUTPUT` | 1..1,076 opaque PTY output bytes |
| 9 | `OUTPUT_ACK` | empty; cumulative position is in the header ACK |
| 10 | `RESIZE` | columns u16, rows u16; both nonzero |
| 11 | `PING` | empty |
| 12 | `PONG` | empty; correlation names the PING |
| 13 | `CLOSE` | reason u16 |
| 14 | `EXIT_STATUS` | kind u8, core-dump u8, signal u16, signed exit code i32 |
| 15 | `RESUME` | same two positions as ATTACH |
| 16 | `RESUME_RESULT` | same 28-byte shape as ATTACH_RESULT |
| 17 | `OUTPUT_GAP` | empty; sequence is retained base and ACK is produced output next |

`OPEN` bytes are mode u8 (`1` = ordered PTY byte stream), encoding u8 (`0` = opaque), columns u16,
rows u16, reserved u16 zero, and requested feature bits u32. No feature bit is assigned in v1.
`OPEN_RESULT` is result u16, accepted mode u8, accepted encoding u8, columns u16, rows u16, and
accepted feature bits u32. Result values are 0 success, 1 denied, 2 unsupported, 3 busy, 4 not
found, 5 invalid, 6 resource exhausted, 7 unavailable, and 8 internal failure. A non-success
result has no side effect and carries zero accepted parameters.

Close reasons are 0 normal, 1 controller request, 2 authority revoked, 3 protocol violation, and 4
resource exhaustion. Exit kinds are 0 exited, 1 signalled, and 2 unknown. Unassigned values and
nonzero reserved fields are protocol errors in the implemented decoder.

## Delivery and reconnect invariants

Input and output use independent cumulative byte spaces beginning at 1. Sequence names the first
payload byte; ACK names the next expected byte. Addition is checked for overflow.

- INPUT exactly at the next expected position is written once and advances the position.
- A wholly old INPUT is a duplicate: it is not written and the current ACK is repeated.
- A partial overlap is a protocol error. A future INPUT gap is not written; the current ACK is
  repeated so the sender can replay from retained bytes.
- Receiver commitment is whole-frame: an exact-next INPUT is staged, the live PTY sink may consume
  it through partial nonblocking writes, and ACK advances only after the complete payload commits.
  No later INPUT may interleave. A terminal failure after a partial write closes that incarnation;
  uncertain bytes are never replayed into a replacement process.
- Unacknowledged input is retained up to 64 KiB and then backpressures local input. It is never
  silently evicted.
- Output is retained up to 1 MiB. Eviction advances the retained base; a reconnect asking before
  that base receives `OUTPUT_GAP` before any available suffix.
- A new accepted attachment increments generation and immediately fences every prior controller
  packet, including delayed INPUT and CLOSE.
- Replacing the PTY/process increments incarnation. No generation from an old incarnation can
  affect the replacement.

The first service release explicitly terminates sessions on daemon restart. Before networking, each
enabled host durably reserves a signed device-bound incarnation greater than the prior reservation.
The old incarnation is unavailable and RESUME returns not found; the protocol makes no process-survival or
cross-daemon exactly-once claim. Surviving PTYs would require a separately frozen supervisor and
crash-safe commit protocol.

Message IDs support result correlation and exact bounded duplicate suppression; they do not
replace byte-sequence checks. Before any control side effect, the receiver reserves the canonical
request and bounded result capacity. An exact committed duplicate replays its result, an exact
in-progress duplicate is unavailable, and conflicting bytes under one ID are a protocol error.
Retained IDs are never evicted in v1; entry or byte exhaustion refuses new work before side effects.
After a session becomes failed or closed, already retained duplicates remain replayable and an
already reserved terminal result may finish recording, but every fresh control ID is denied before
effect.

`INPUT` and `OUTPUT_ACK` are stream-coordinate operations rather than arbitrary control effects.
INPUT duplicates are decided by the exact byte interval above. OUTPUT_ACK is cumulative and uses one
attachment-local `(message ID, next-output)` high-water fence: an exact latest repeat succeeds;
conflicting, backward, non-advancing, out-of-range, or wrong-generation acknowledgements fail.
Neither operation consumes one permanent exact-control replay entry per byte. Resize, ping, detach,
close, attach, and resume retain the never-evicted exact-result rule. ADR 0154 records this bounded
long-session correction without changing the Ratox 1.0 frame encoding.

Periodic attachment liveness therefore reuses one byte-identical PING and message ID for the life of
that attachment. Repeated local requests coalesce while it awaits transport acceptance; afterward
the sender may submit the same exact record again and the host replays the correlated cached PONG.
Detach, route loss, exit, failure, and a new resumed generation discard the prior heartbeat identity.
This bounds healthy indefinite sampling to one exact-control replay entry per attachment. A fresh
PING ID per interval is not conforming IoTox client behavior because it would deterministically
consume the finite never-evicted replay store (ADR 0193). No wire encoding or receiver replay rule
changes.
Tox friend numbers are never durable identity.

## Authority, lifecycle, and bounds

Opening or attaching requires a transcript-confirmed IoTox session and the separately named
`interactive.terminal` capability, reserved as authority bit 7. The existing authority-ledger v1
intentionally rejects that bit. A signed ledger-v2 migration must land before the service can be
enabled; friendship, text access, telemetry, actuation, files, or owner-queue access never imply
terminal authority.

The initial local policy admits at most two live sessions per authorized principal and eight per
device, one attached writer per session, a 64 KiB unacknowledged-input window, and a 1 MiB retained
output window. V1 carries no profile selector. Local policy resolves at most one enabled
program/profile for the proven principal; missing or ambiguous policy denies OPEN. The packet
carries no profile name, command, working directory, environment, UID, or arbitrary executable
path. PTY creation, resize, signal, detach,
authority revocation, exit, replay gap, quota denial, and internal failure must each append bounded
audit evidence without terminal contents.

Control and input remain lossless and admission-aware. A local c-toxcore SENDQ rejection means the
frame was not sent and must be paced/retried from retained state. No v1 state may be silently moved
to lossy delivery. Replaceable screen-state transport requires a later negotiated protocol.
