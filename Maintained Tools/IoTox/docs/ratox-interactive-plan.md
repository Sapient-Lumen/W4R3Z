# Ratox and reconnectable-interactive plan

Updated 2026-08-27. This is the implementation order for latency-sensitive Ratox work and the
later Eternal Terminal/Mosh-style remote session. R0–R7 are constructed and the founding-machine
two-guest campaign is complete through bounded impairment, total route loss, detached-PTY retention,
and exact resume. Optional production-support review R8 is outside repository completion; no
production-readiness claim follows from the default-off construction.

The phase-by-phase execution contract is `ratox-service-implementation-plan.md`; the focused
service security analysis is `security-ratox-v1.md`. This document owns product shape
and scientific targets. The service plan owns dependencies, deliverables, and activation gates.

## Product order

1. Finish the Ratox successor as the ordinary local face of one truthful IoTox agent.
2. Qualify one low-latency Tox carrier without weakening command, authority, or file semantics.
3. Add a separately negotiated, capability-gated interactive session protocol.
4. Add reconnect and roaming only after attachment fencing, replay bounds, and terminal lifecycle
   survive process tests and genuine two-host faults.

Human Tox text remains useful for chat. It is not the terminal byte carrier: a read receipt is a Tox
message acknowledgement, not a remote PTY acknowledgement, and the genuine-provider gate found
large carrier-specific idle tails.

## Decisions already supported by evidence

| Concern | Current decision |
|---|---|
| Reliable terminal carrier | Tox custom-lossless, 20 ms base pacing, SENDQ backoff |
| Lossy packets | Optional only for sequenced replaceable state with snapshot/resync semantics |
| Human text | Chat and compatibility only |
| Files and OTA | Bulk lane, never terminal framing |
| Owner scheduling | interactive/control/bulk weighted 8:4:1; at most 16 commands before `tox_iterate` |
| Idle iteration | cap provider-requested sleep at 20 ms; expose requested/effective values |
| Reconnect input | cumulative byte sequence with explicit ACK and bounded unacknowledged replay |
| Controller handoff | session ID + incarnation + principal + nonce + monotonically increasing generation |
| Heartbeat miss | warning-only; no carrier/session mutation |
| Authoritative route loss | typed local `unavailable`; retain the bounded remote PTY detached |
| Reconnect | require a higher authenticated epoch before explicit exact-session resume |
| Route migration | unqualified; never infer it from one-route recovery |

The corrected 40-sample founding-host gate found direct-UDP custom-lossless/custom-lossy idle
medians of 20.532/20.545 ms and bulk medians of 11.960/12.484 ms, with no deadline misses. Lossy
delivered no material advantage. Forced TCP was path-bound: custom-lossless missed 2/40 idle
deadlines versus 24/40 for lossy; both degraded during bulk. See the rev0015 latency report for the
complete boundary.

The controlled namespace/netem gate supersedes the idea of one unconditional carrier. At 2 ms
burst spacing beside UDP bulk, delayed lossless admitted 51/64 and returned 39 by 2.5 seconds;
lossy admitted all 64 and returned 35 with 67 reorder inversions. Under adverse TCP bulk, lossless
admitted 3/64 and lossy 34/64, with no reordering because both shared the relay TCP stream. ADR
0060 therefore keeps indispensable control/input sparse and lossless, requires pacing/coalescing,
and permits lossy only for explicitly replaceable output state.

The 20-cell adversity pacing gate crossed 2/5/10/20/40 ms with 64-byte and full 1,200-byte
packets. Twenty milliseconds was the first direct-UDP interval with 64/64 success for both sizes
and the only interval whose four UDP/TCP size cells were all clean. TCP remained non-monotonic
across public-relay epochs, so 20 ms is a base rather than a guarantee: SENDQ rejection retains the
whole offer and doubles through a 320 ms ceiling. See the rev0015 pacing report and ADR 0061.

## Implemented v1 protocol shape and remaining evolution

### Stable identity and session lifetime

An interactive session needs identifiers that survive transport reconnection without letting a
delayed controller write into a new process:

```text
stable device principal
interactive session ID (random 128-bit)
terminal incarnation (increments when the remote PTY/process is replaced)
authorized controller principal
attachment nonce (fresh per attach)
attachment generation (strictly increasing)
```

Every input, resize, ACK, detach, and resume record names the complete current attachment. A new
attach fences every packet from the old generation. Tox friend number is never part of durable
session identity.

### Reliable control lane

Custom-lossless control records carry:

```text
OPEN / OPEN_RESULT
ATTACH / ATTACH_RESULT
DETACH
INPUT_ACK
OUTPUT_ACK
RESIZE
PING / PONG
CLOSE / EXIT_STATUS
RESUME / RESUME_RESULT
```

These records require a transcript-confirmed IoTox session and a new explicit authority capability.
Opening a shell is not implied by friendship, text access, `read.telemetry`, or file permission.

### Input and output modes

The first mode is a conservative ordered byte stream above custom-lossless packets:

- input bytes have a cumulative sequence and are delivered to the PTY at most once;
- ACK releases the retained prefix;
- unacknowledged input is never silently evicted; a full replay window applies backpressure;
- output has an independent sequence so reconnect can request a bounded retained suffix;
- a history gap is explicit and forces a snapshot/reset decision.

A later screen-state mode may transmit replaceable terminal state rather than replay every output
byte. It must define emulator version, dimensions, UTF-8/control parsing, snapshot identity, delta
base, and resynchronization. Lossy delivery is eligible only for state that is explicitly
superseded by a newer complete state; authority, input commitment, attach, close, and exit status
remain reliable.

### Initial bounds and latency targets

These are the frozen v1 bounds and current implementation targets:

| Item | Starting target |
|---|---:|
| owner wake cap | 20 ms |
| input/output coalescing base | 20 ms; rejection doubles to at most 320 ms |
| interactive packet / payload | at most 1,200 / 1,076 bytes |
| unacknowledged input replay | 64 KiB per session |
| retained output replay | 1 MiB per session, with explicit gap |
| direct-UDP idle custom-lossless | p95 <= 50 ms, p99 <= 100 ms |
| custom probe deadline gate | zero misses at 250 ms on qualified direct route |
| owner interactive queue | p99 < 2 ms under qualified bulk load |

The 1,200-byte packet ceiling leaves room below c-toxcore's 1,373-byte custom-packet maximum. The
complete attachment header leaves 1,076 payload bytes. ADR 0061 freezes packet ID `0xA2`, framing
version 1.0, the default-off negotiation bit, and strict type/payload invariants.

## Scientific gates

- [x] Build attachment fencing, bounded cumulative replay, and monotonic RTT estimation as
  transport-independent primitives.
- [x] Separate interactive/control/bulk owner work, bound per-iteration service, and project queue
  and iteration evidence.
- [x] Compare text/read-receipt, custom-lossless echo, and custom-lossy echo over observed UDP and
  forced TCP with the pinned genuine provider, idle and during bulk.
- [x] Apply controlled delay, loss, duplication, reordering, and queue pressure. Compare reliable
  head-of-line behavior with replaceable lossy state; do not infer this from a zero-loss host run.
- [x] Sweep paced/coalesced emission intervals and freeze congestion response before terminal wire
  framing; a local toxcore send rejection must remain distinct from a path miss.
- [x] Freeze canonical Ratox 1.0 framing, its default-off feature and authority reservations,
  quotas, local-profile-only OPEN policy, and audit/lifecycle semantics in ADR 0061.
- [x] Build the R3 local PTY/profile loop and R4 coordinator with fixed framing, at-most-once input,
  resize/exit/lifecycle bounds, replay, default-off Agent dispatch, and exact authority-denial tests.
- [x] Build R5 as a separate private local stream: canonical terminal protocol, owner-only
  `SOCK_SEQPACKET` endpoint, same-UID peer credential gate, bounded controller replay/state machine,
  and one-binary open/resume client with raw-mode restoration, resize, detach, close, and scripted I/O.
- [x] Kill and replace controller connections across reconnect, replacement, SENDQ, revocation,
  restart, input, and ACK boundaries; prove stale generations cannot write and bounded replay remains exact.
- [x] Run the complete terminal service between the two Sandwurm guests through direct UDP and
  forced TCP relay, record keypress-to-render and reconnect convergence, and include
  CPU/RSS/context-switch evidence. The founding-machine VM topology is the project qualification
  target; a second physical machine is not a release gate.
- [x] Run terminal traffic beside 1/8/16/32/64 bulk streams and multiple Tox routes. If bulk still
  causes head-of-line delay below the owner queue, evaluate a dedicated authenticated Tox route.
- [x] Separate carrier, heartbeat, PTY progress, and visible stall under seeded bounded impairment;
  keep partial impairment warning-only (ADR 0196).
- [x] Qualify bilateral 100% loss, typed controller detachment, live remote-PTY retention, higher-
  epoch recovery, and exact generation-two resume on direct UDP, forced TCP, and strict generic
  SOCKS (ADR 0197).
- [ ] Fuzz every new frame, soak PTY lifecycle/reconnect, and complete a protocol/threat review
  before advertising the feature.

## Current execution point

R0 through R7 are complete at the current construction boundary:

1. R0 froze framing, admission pacing, carrier selection, and controlled impairment evidence.
2. R1 implements receiver-side at-most-once input, bounded output history, exact replay,
   attachment/incarnation lifecycle, content-free events, and quotas.
3. R2 implements an explicit signed authority-ledger v2 migration and bit-7 grant without widening
   any v1 principal.
4. R3 implements owner-only fixed local profiles and the sealed PTY process boundary.
5. R4 connects those layers to live Agent packet `0xA2` dispatch behind an explicit pre-network gate,
   bilateral feature negotiation, and exact current authority. Default configurations advertise no
   Ratox feature.
6. R5 adds a separately enabled same-user `terminal.sock`, canonical local records, a bounded pure
   controller state machine, exact route/principal/epoch binding, and one-binary open/resume UX. It
   neither grants host authority nor makes a remote session reachable without every R4 gate.
7. R6 adds a signed pre-network incarnation lease plus separate-process reconnect, controller
   replacement, queue pressure, revocation denial, and restart fencing.
8. R7 measures complete-service latency beside 1/8/16/32/64 bulk streams, freezes 32 accepted
   transfers as the single-Agent ceiling, qualifies a protected terminal beside 24 streams, and
   closes bounded-impairment plus exact total-loss/resume behavior between Sandwurm guests.
9. R8 governs any optional future production-support activation decision; it is not a founding-
   machine repository gate.

The optional Ratox production frontier is R8 review beyond ADR 0207's accepted duration/circuit-
churn soak and ADR 0206's accepted actual-Tor terminal cell. The accepted cell kills only client Tor
after initial PTY progress and proves the
frozen heartbeat/offline/detach/explicit-resume lifecycle with three Tor phases and TCP-only
containment as compact proof `pair.2waqdpgk`. The new cell keeps both Tor processes alive while one
120-sample session crosses exact client/device application-circuit replacement. Live science observed
both carrier-loss and no-error attempts; the gate now requires post-replacement PONG with unchanged
epoch/generation or exact loss plus explicit higher-epoch resume, with exact
session/incarnation/PTY/byte continuity. Compact proof `pair.k8o54n2v` exercises both branches with
all 120 samples and unchanged processes. ADR 0208's `pair.9cx0jels` repeats the gate through a
second public record; both Tor streams reopen while Ratox remains continuous. The
explicit host and controller enable flags exist to exercise the qualified construction, not to imply
production support, complete roaming, daemon-restart PTY survival, or broad public-network
qualification.

## Things deliberately not implemented yet

The diagnostic sized packet echo and bounded burst are not terminal protocol, are not advertised,
carry no user data, and exist only to measure c-toxcore carrier behavior. IoTox implements a
one-binary `iotox terminal`/`terminal-resume` client over a private local endpoint and the remote PTY
service when both peers negotiate bit 23 and the remote principal has exact bit-7 authority. It still
has no terminal emulator or screen-state protocol, multi-controller policy, roaming claim, route
bonding, durable controller/session state across daemon restart, PTY restart survival, automatic
route migration, lossy application reliability layer, or production activation.
