# Ratox service implementation plan

Status: founding-machine construction complete; optional production activation remains downstream.
Updated 2026-09-01. The frozen wire contract is
`protocol-ratox-v1.md`; this document distinguishes controlled construction activation from the
remaining production-activation gates. `ratox-ssh-status.md` is the concise current product and
SSH-compatibility boundary.

## Outcome and activation rule

The first Ratox service is one explicitly authorized, reconnectable, ordered PTY byte stream. It
uses a locally selected profile, never a remote command line. It preserves each accepted input byte
at most once, fences replaced controllers, reports output-history gaps, and fails closed when
authority, transport, storage, or process state is uncertain.

Feature bit 23 remains absent from every default HELLO. IoTox retains an explicit, default-off
construction activation after R4: the operator must enable Ratox, load a secure owner-only profile
store containing at least one enabled profile and principal binding, select a valid PTY helper or
factory, and pass all bounded-service checks before toxcore starts. Only then is bit 23 frozen into
that process's local HELLO mask. A failure prevents network startup.

This construction gate makes the live dispatcher, R5 controller stream, and R6 restart/fault
qualification testable without pretending that R8 production review exists. Production enablement,
broad operator support, or any future default-on policy still requires a reviewed R8 change together
with reconnect/fault qualification, retained Sandwurm two-node evidence, and focused security review.
A configured node and its peer must both advertise bit 23; one-sided activation never negotiates the
service. The private local
terminal endpoint has an independent default-off gate and does not alter HELLO or remote authority.

## Dependency order

```text
R0 frozen framing and pacing (complete)
 |
 +--> R1 pure session engine -----> R4 agent/transport integration ----+
 |                                  |                                  |
 +--> R2 authority ledger v2 -------+                                  +--> R6 reconnect/fault gates (complete)
 |                                  |                                  |          |
 +--> R3 local PTY/profile adapter --+--> R5 local operator client -----+          v
                                                                    R7 Sandwurm two-node science (complete)
                                                                            |
                                                                            v
                                                                    R8 review and activation
```

R1, R2, and R3 were developed independently; R4 can create a PTY only after all three gates pass.
R5 and R6 are complete at the construction boundary; R5 joins only through a separate private local
gate, while R6 adds a pre-network restart lease and separate-process fault gate. R7 now measures the
complete service rather than diagnostic echoes. R8 remains the production-activation gate, while the
explicit default-off paths exist only for controlled construction and evidence.

## R0 — frozen prerequisites (complete)

Delivered by ADR 0061:

- canonical Ratox 1.0 packet ID, header, registry, and strict codec;
- session/principal/nonce/incarnation/generation attachment identity;
- cumulative input/output positions and explicit output gaps;
- 20 ms admission coalescing with retained SENDQ rejection and bounded backoff;
- transport-independent attachment fence, replay window, and RTT estimator;
- carrier, impairment, and pacing evidence over genuine c-toxcore UDP and forced TCP.

R0 did not implement a receiver state machine, output-history eviction, authority migration, PTY,
local terminal client, or Agent dispatch. R1, R2, and R3 supplied the session, authority, and local
PTY/profile prerequisites. R4 now connects them behind an explicit default-off gate. Sandwurm
two-node complete-service evidence was intentionally absent at the R0 boundary; R7 later supplies
it, while production activation remains absent.

## R1 — transport-independent session engine

Build a library with no toxcore, filesystem, clock-wall-time, terminal, or process dependencies.
Its caller supplies monotonic time and explicit events.

Deliverables:

- [x] `InputReceiver`: stages exactly the next byte range once; repeats the current ACK for wholly old
  input; rejects partial overlap; withholds future gaps; and advances commitment only after an
  explicit whole-frame sink completion.
- [x] `OutputHistory`: assigns positions, retains at most 1 MiB, acknowledges prefixes, and returns
  either an exact suffix or an explicit retained-base/produced-next gap.
- [x] `MessageReplayCache`: exact bounded per-session duplicate-result retention with pre-effect
  result reservations, no ID eviction, explicit in-progress denial, and conflicting-byte rejection.
- [x] `InteractiveSession`: OPEN-equivalent construction plus ATTACH/RESUME/DETACH/CLOSE state,
  one writer, complete token validation, atomic output-position application, monotonically
  increasing generation, terminal partial-input failure, incarnation replacement, exact replay of
  retained terminal results, and denial of fresh terminal-session control effects.
- [x] `SessionDirectory`: at most two live sessions per principal and eight per device, with atomic
  reservation/release, configured sequence-origin propagation, and no partial OPEN side effect.
- [x] bounded structured events for lifecycle and denial facts; terminal content never enters an
  event and close records final cumulative positions before wiping stream memory.

Deterministic acceptance gates:

- exhaustively split 1..2,152 input bytes across every packet boundary and replay each prefix,
  suffix, duplicate, partial overlap, future gap, old generation, and old incarnation;
- kill/replace the modeled controller before and after every INPUT and ACK transition;
- inject every partial-sink completion and error boundary; no later input may interleave with a
  staged frame, ACK advances only after its complete sink commit, and a failed partial commit makes
  the incarnation terminal rather than replaying uncertain bytes;
- cross the 64 KiB input and 1 MiB output limits at exact boundary, boundary+1, ACK, and eviction;
- prove generation/incarnation overflow, quota exhaustion, message-ID duplication, and internal
  callback failure have no partial state transition;
- property-test state invariants and add focused fuzz targets for frame-plus-session sequences.

Exit: complete. A deterministic model proves byte, control replay, attachment, incarnation,
lifecycle, event, and quota behavior without a socket or PTY. R2, R3, and the default-off R4
integration and the R5 private controller stream are also complete; R6 and R7 have since completed,
leaving operational R8 qualification.

## R2 — authority-ledger v2 migration (complete)

Add `interactive.terminal` at durable bit 7 without reinterpreting an existing signature or
silently widening an existing principal.

Delivered by ADR 0063 and `protocol-authority-v2.md`:

- [x] a distinct v2 file header, record discriminator, signature/digest domains, capability mask,
  format-aware role ceilings, signed migration action, v1 read compatibility, and an explicit
  local rollback-guard versus coordinated-snapshot boundary;
- [x] exact non-widening migration: all v1 principals retain their existing masks and only a later
  explicit v2 grant may add `interactive.terminal`;
- [x] permanent compatibility semantics where `all`, `all-v1`, and `kAllCapabilities` remain bits
  0–6 while `all-v2` is the explicit terminal-inclusive opt-in;
- [x] mixed signed-history replay, strict header/history agreement, unknown-bit rejection, one-way
  format progression, sequence/epoch exhaustion checks, and restart recovery;
- [x] a private 192-byte committed/pending head guard that detects ledger-only rollback, deletion,
  and fork, adopts valid legacy v1 state, rejects unguarded v2, and reconciles the two exact
  interrupted atomic-replace states;
- [x] RecallRoot client verification that daemon-prepared action, role, capabilities, principals,
  time fields, and migration format exactly match the requested ceremony before signing;
- [x] negotiated feature bit 24, v2 challenge/proof format binding, independent proof signature
  domain, and refusal of unnegotiated or downgraded authority rounds;
- [x] local and remote RecallRoot migration ceremonies, exact-head mutation preparation/application,
  proof invalidation, idempotent duplicate acknowledgement, delegation/revocation, exact-capability
  succession, and process-level CLI coverage.

Exit: complete. A transcript-confirmed remote principal can prove explicitly granted bit 7 under v2,
while every v1 ledger and every non-terminal principal remains denied. This phase creates no PTY,
process, Ratox dispatcher, or feature-bit-23 advertisement.

## R3 — local PTY and profile adapter (complete)

Keep process creation behind a narrow interface so lifecycle tests use a deterministic fake.

The profile contract is local-only and immutable for one OPEN attempt. It names a fixed argument
vector, working directory, environment allowlist, terminal type, dimensions policy, UID/GID policy,
resource limits, local confinement tier, and optional profile-scoped cgroup budget. Profile v4 has
no remote profile selector: local policy resolves at most one enabled profile for the proven principal,
and missing or ambiguous policy denies OPEN. The wire carries only the profile-independent v1 OPEN
fields; it cannot supply a profile name, argv, shell text, paths, environment, identities, limits, or
confinement choice. Existing canonical v1/v2/v3 records remain readable; v1 maps to `compatibility`, v1/v2 map to an
empty cgroup budget, v3 maps to no `memory.high`, and newly encoded profiles default to `baseline`.

Delivered by ADRs 0064, 0071, 0081, 0082, 0083, and 0084 plus `terminal-profile-v4.md`:

- [x] strict canonical profile and binding records in an exact owner-only tree, opened component by
  component without symlinks, with single-link files, bounded counts/bytes, atomic registry
  replacement, and generation-bound resolution;
- [x] fixed argv/cwd/terminal/dimensions/identity/limit policy, exact environment construction from
  fixed entries plus a small inherited allowlist, and rejection of loader/shell startup variables;
- [x] a narrow nonblocking `PtyProcess` interface and deterministic fake-backed controller with
  64 KiB call bounds, output drain after close, observe-before-signal, HUP/TERM/KILL escalation,
  kill-reap timeout, exact snapshots, and backend-contract failure handling;
- [x] a Linux `posix_spawn` one-binary child path with high collision-proof handoff descriptors,
  canonical manifest, PTY allocation, session/controlling-terminal/foreground setup, descriptor-
  based target and cwd, rlimits, exact identity, `PR_SET_NO_NEW_PRIVS`, `umask(077)`, two-pass descriptor
  inventory/proof, and final `fexecve`;
- [x] explicit startup truth: the reviewed hidden child emits a fixed readiness record immediately
  before final exec; only readiness plus close-on-exec EOF succeeds, while structured stage/errno
  records, premature EOF, wrong helper, and timeout fail closed and reap the child;
- [x] test-only local fixtures for exact cwd/environment/window/limits/session/descriptors, binary
  NUL/high-byte echo, resize clamps, HUP exit, HUP/TERM/KILL forced shutdown, insecure executable,
  impossible limits, helper-readiness rejection, capability state, baseline seccomp, high inherited
  descriptor closure, session-wide descendant teardown, and strict success-or-named-fail-closed behavior;
- [x] runtime capability-ceiling discovery, zero active/ambient capability verification, privileged
  securebits and full bounding-set sealing, nondumpability, default baseline seccomp, and opt-in
  fail-closed MDWE plus Landlock ABI 10 strict confinement;
- [x] optional exact aggregate process/memory/swap and rational CPU reservations over effective
  profile maxima, with all-profile startup fit and representability validation, atomic pre-mutation
  charging, RAII rollback, teardown-coupled proved release, conservative complete-charge stranding on
  unproved cleanup, and owner-private quota/period/current/peak/rejection/stranding evidence.
- [x] canonical profile v4 and host `memory.high` throttles with monotone composition and cross-layer
  clamp, plus protected zero-baseline PID/memory/CPU records and one-shot teardown outcomes accumulated
  as saturating owner-private content-free counters.
- [x] canonical profile v5 exact-device read/write BPS and IOPS ceilings with same-device
  host/profile composition, semantic `io.max` readback, protected zero-baseline `io.stat`, and
  teardown-time saturating owner-private I/O totals.
- [x] protected optional `cpu.pressure`, `memory.pressure`, and `io.pressure` outcome capture for
  every session leaf, with exact enabled/zero-baseline proof, bounded PSI parsing, optional `full`,
  post-quiescence absolute microseconds, saturation, and explicit owner-private capability counts.

No default profile implies “run whatever the peer asks.” The peer cannot select the profile or
supply argv, shell text, paths, environment, identity, limits, or confinement tier. The implementation
claims the exact common capability floor, baseline seccomp/lifecycle/session boundary, and strict
MDWE/Landlock ABI 10 policy described by profile v5 and ADRs 0072/0073. The optional cgroup envelope
adds administrator and profile-scoped process, memory, swap, CPU, and exact-device I/O ceilings with monotone exact
composition. Optional aggregate process/memory/swap and exactly normalized average-CPU admission conservatively
reserves those configured maxima across live production sessions. Unproved post-spawn teardown strands
its complete charge until restart recovery rather than reopening capacity. It does not claim created
namespaces, aggregate I/O reservation, storage latency/queue-depth control, live PSI-trigger/admission or memory-high feedback policy, synchronized periods or parent/burst CPU enforcement,
physical preallocation, cross-daemon capacity, mount
isolation, a complete syscall allowlist, read/execute confinement, proof against unknown future
session escapes, or daemon-restart PTY survival.

Exit: complete. Local fake and native tests drive a fixed helper through the adapter with exact
bytes, startup proof, and lifecycle truth. rev0018 now reaches this adapter only through R4's explicit
pre-network activation and exact live authority gate.

## R4 — agent and transport integration (complete in rev0018)

Join R1–R3 on the toxcore owner thread while preserving existing session and authority gates.

Inbound order is fixed:

```text
custom-lossless callback
 -> packet ID/version/canonical decode
 -> confirmed IoTox feature/session lookup
 -> transport-key to stable-device binding
 -> current directional authority proof with bit 7
 -> session/principal/attachment validation
 -> duplicate/state transition
 -> PTY side effect
 -> paced response/ACK
```

Delivered by ADR 0065 and the rev0018 Agent/service tests:

- [x] explicit pre-network activation with secure whole-store load, enabled profile/binding checks,
  valid bounded service limits, and absolute helper or injected process factory;
- [x] immutable runtime HELLO selection where bit 23 is omitted by default and added only after the
  explicit activation request; bilateral negotiation remains mandatory per online epoch;
- [x] dedicated packet-`0xA2` dispatch through transcript confirmation, current online epoch,
  authenticated stable principal, and exact current `interactive.terminal` authority;
- [x] a transport-independent coordinator joining R1 sessions, R3 profile resolution, PTY lifecycle,
  bounded result replay, whole-frame input commitment, output replay/gaps, and session quotas;
- [x] retained outbound packets: successful toxcore admission pops the exact packet, retryable
  `SENDQ`/not-connected rejection retains it, and stale or terminal route failure detaches it;
- [x] transport-offline detachment, exact authority-revocation shutdown, finite Agent shutdown drain,
  and round-robin bounded service so one busy PTY cannot starve another;
- [x] private status counters and a rotating content-free `ratox-events` journal that excludes
  terminal bytes, argv, environment, cwd, profile IDs, paths, and error strings.

Friend number remains a live lookup handle and is never durable session identity. Current telemetry
covers queue/replay/session/process occupancy and lifecycle facts; end-to-end R7 latency and local
render telemetry remain later phases.

Input side effects use a two-step boundary. The session engine first validates and stages one exact
next range. The PTY adapter may consume it through multiple nonblocking writes, but no later frame
can interleave. Only whole-frame completion advances next-expected and permits an ACK. If the PTY
fails after a partial write, the attachment closes and that incarnation becomes terminal; uncertain
bytes are never replayed into a replacement process.

Exit: complete for the current R4 boundary. Unit/integration fixtures exercise coordinator
lifecycle, bounded fairness, replay and authority closure. An exact mock peer independently advertises
bit 23, completes the live Agent session/authority path, injects a canonical OPEN, receives the denial
result, and proves a v1-authorized owner cannot spawn a PTY. Activation-without-store fails before
transport startup, and one-sided advertisement never negotiates the feature. Separate-process
controller replacement and complete two-Agent PTY lifecycle remain R6 evidence rather than an R4
claim.

## R5 — local operator client (complete in rev0019; fault-hardened in rev0020)

rev0019 added an explicit `iotox terminal` and `iotox terminal-resume` mode over a private same-user
local endpoint. rev0020 bounds incomplete admission and makes real-CLI contention deterministic. The
local stream is a separately versioned canonical protocol; terminal bytes never travel through the
control request/response protocol or public runtime files.

Delivered by ADRs 0066–0067 and the rev0019–rev0020 client/socket/process tests:

- [x] independent `--enable-ratox-terminal-client` activation; the endpoint is absent by default and
  does not advertise bit 23 or grant any remote capability;
- [x] private real-parent `AF_UNIX` `SOCK_SEQPACKET` listener, owner-only pathname, same-UID
  `SO_PEERCRED` admission, one live controller, bounded multiplexed contenders, nonblocking
  close-on-exec descriptors, exact stale-socket reclamation, and inode/device-checked unlink on
  shutdown;
- [x] fixed 32-byte local header, exact type/payload invariants, 16 KiB bound, typed errors, and
  dedicated OPEN/INPUT/RESIZE/DETACH/CLOSE/OUTPUT_ACK/PING plus server result/output records;
- [x] pure controller state machine with exact friend/online-epoch/principal route binding, bounded
  input and output replay, immutable packets until transport admission, duplicate/overlap checks,
  explicit gaps, route loss, resume, and terminal outcomes;
- [x] raw mode only for an interactive TTY, unconditional restoration through RAII/signal handling,
  `SIGWINCH` forwarding, ordered stdin/stdout, beginning-of-line `~.`, `~d`, `~~`, and `~?` escapes,
  and scripted stdin/stdout without a false TTY claim;
- [x] Agent-level proof that the socket is default-off, owner-only when enabled, cannot bypass the
  live friend/session/authority route map, returns a typed local denial, and unlinks on stop.
- [x] finite 1 ms..60 s first-`OPEN` lease (5 s default), typed silent-client timeout, no
  publication or disconnect callback before a committed `OPEN`, and immediate successor admission;
- [x] bounded four-contender consume-and-deny batches with a shared 20 ms first-record window, exact
  busy ID when available, no losing-packet dispatch, and connection-scoped pre-OPEN errors;
- [x] active descriptor data/death processed before listener contention, so a queued replacement is
  admitted after the previous controller closes instead of receiving a stale busy result;
- [x] bounded two-phase `DETACH`: final output drains before `DETACHED`, only exact cumulative
  `OUTPUT_ACK` is admitted afterward, packet sends share one absolute 1 ms..5 s deadline, and queued
  successors remain in the kernel backlog until release;
- [x] real one-binary process proof for one winner, typed loser, abrupt local-controller death,
  replacement resume, retained/final output-before-ACK, exact cumulative ACK committed before release,
  clean detach, and explicit empty-restart `not_found`.

Exit: complete at the R5 construction boundary. One binary can open, detach, resume, and close a
bounded test-gated session; a client crash releases the connection and cannot transfer access to a
different local UID. rev0020 now proves local separate-process controller replacement and explicit
empty-server restart failure, but remote route/revocation/storage and real-Agent/PTY restart fault
qualification remain R6 rather than inferred R5 claims.

## R6 — reconnect, restart, and fault qualification (first contract complete in rev0020)

rev0020 joins deterministic state-machine gates with a separate real-process boundary across the
Agent, private local terminal socket, exact toxcore double, and native PTY helper.

Delivered by ADR 0068, `tests/test_ratox_restart_process.cpp`,
`tests/test_terminal_controller_process.cpp`, the Agent/service unit gates, and retained full-path R6
oracle evidence:

- [x] durable signed host incarnation reserved and strictly re-read before transport/listener startup,
  with lifetime lock exclusion, exact increment, corruption/identity/symlink/contention/exhaustion
  refusal, descriptor-relative commit, synchronized newly created hierarchy entries, explicit
  enabled-service reservation, and runtime lease observability;
- [x] finite first-OPEN admission, bounded non-dispatching contender denial, exact typed stream-bound
  loser outcomes, active-controller death handling, and replacement resume through the real CLI;
- [x] exact Ratox packet retention across injected SENDQ rejection and byte-exact PTY input/output;
- [x] local controller crash/replacement with a higher attachment generation, plus one winning stream
  and explicit denial of a simultaneous controller;
- [x] friend deletion, complete mock epoch-state erasure, re-add, and valid same-principal resume;
- [x] signed live authority revocation, process reap, retained-authority purge, and one explicit
  replayable denied RESUME that cannot authorize a PTY effect;
- [x] daemon replacement with old-session `not found`, a fresh host carrying exactly the prior durable
  incarnation plus one, and strict state-file ownership/mode/link/extent inspection.

Required outcomes retained by the combined R1–R6 evidence:

- transport disconnect detaches but does not replace a live PTY; a valid RESUME replays the exact
  retained suffix and fences the former attachment;
- stale INPUT, RESIZE, CLOSE, ACK, and delayed results cannot affect the winner;
- input replay never silently evicts; output eviction always produces `OUTPUT_GAP`;
- authority revocation closes the attachment and makes resume explicitly denied;
- storage full, SENDQ rejection, queue saturation, local-client death, toxcore reconnect, and
  orderly shutdown have explicit bounded outcomes.

Daemon restart has two distinct, testable semantics. The first release may terminate the PTY and
return `not found` after restart, but must never imply that the old process survived or reuse its
incarnation. PTY survival across daemon restart requires a separately supervised child and durable
session journal plus a crash-safe input-commit protocol with that supervisor. If implemented later,
it is a new milestone, not an inference from transport resume.

Exit: complete for the first deterministic-provider R6 contract. Transport reconnect, controller
replacement, queue pressure, revocation, and restart fencing are process-qualified; daemon restart
intentionally terminates the PTY, returns `not found` for the lost local session, preserves failed
startup evidence, and cannot reuse the former host incarnation. Storage-full/power-cut hardware
qualification and durable child supervision remain later work. Sandwurm two-node qualification is
closed by R7 below rather than retroactively treated as an R6 claim.

## R7 — Sandwurm two-node latency and interference science (complete)

Use two sibling Sandwurm Cloud Hypervisor guests on the founding machine, reusable test identities by
default, the pinned source-linked provider, and separate direct-UDP and forced-TCP phases. A dedicated
Sandwurm network/relay guest or host-owned network service supplies controlled routing and impairment.
Record keypress injection at the client, PTY observation, output observation, and local render using
monotonic clocks; report per-leg and end-to-end latency.

Run idle and beside 1/8/16/32/64 bulk streams, randomized by phase, for at least 1,000 keypresses per
cell. Retain route observation, SENDQ rejection, pacing, owner-queue wait, RTT, reconnect convergence,
CPU, RSS, descriptors, context switches, and available power data.

The first clean post-measurement-boundary direct-UDP idle cell delivered 1,000/1,000 but rendered at
p50 62.107 ms, p95 83.115 ms, and p99 86.936 ms while owner queue p99 remained 0.511 ms. Disposable
5 ms transport-only and combined transport/service diagnostics localized the tail to toxcore's
bounded iteration sleep plus the Agent's independent 20 ms Ratox service sleep. ADR 0156 implements
demand-driven 5 ms defaults only while an attachment or controller transition is live, immediate
local service wakes, idle restoration, runtime policy truth, and process-incarnation-fenced resource
intervals. The combined diagnostic reached p95 32.000 ms and p99 47.643 ms, but it is not accepted
qualification evidence; the later clean exact-commit route/load cells supply that requirement.

The completed campaign accepts 1,000-sample idle and 1/8/16/32-stream load cells on the qualified
route classes, freezes 32 accepted transfers as the single-Agent ceiling, and proves a protected
Ratox route beside 24 streams. Larger cells remain recorded failures rather than weakened passes.
ADRs 0196 and 0197 then close the route-fault slice: one authenticated session survives bounded
delay/loss without mutation; complete loss produces a warning-only heartbeat miss, authoritative
controller detachment with a live remote PTY, and explicit exact-session resume after a higher
authenticated epoch on direct UDP, forced TCP, and strict generic SOCKS. Automatic migration and
actual-Tor terminal behavior is not inferred. ADR 0206's distinct process-loss and explicit-resume
cell is accepted as compact proof `pair.2waqdpgk`. ADR 0207 accepts compact proof
`pair.k8o54n2v` for a 120-sample paced
continuous-process cell with exact client/device Tor circuit replacement and no process restart.
Live attempts observed both attachment loss and no error, so post-replacement PONG continuity and
exact higher-epoch resume are the only accepted branches; the accepted run exercises both. Route
diversity, adversarial proxies, and production support remain open.
ADR 0208's second-record repetition keeps both application checkpoints continuous despite two Tor
stream reopenings, proving that the Tor transition label is not a shortcut around the frozen
provider/PING/explicit-resume lifecycle.

Direct-route release targets are p95 <= 50 ms, p99 <= 100 ms, zero misses at 250 ms, zero lost or
duplicated accepted input, and owner interactive queue p99 < 2 ms. Forced TCP is reported as a
separate path class rather than mislabeled direct-route success.

Run a dedicated authenticated Tox-route experiment only if a bulk cell misses the latency target
while owner interactive queue p99 remains below 2 ms. Adopt the extra route only if it restores the
target reproducibly across randomized repetitions and its identity binding, fallback, resource,
disconnect, and restart costs are acceptable. Otherwise keep one route and address the measured
layer that actually queues.

Exit: complete-service latency, bounded impairment, and exact one-route reconnect claims are
supported by retained Sandwurm two-node evidence. Production support remains an R8 decision.

## R8 — security review and activation

Before production advertisement or any broader enablement:

- [x] construct the focused capability/process-confinement review in `security-ratox-v1.md`, profile
  v5, ADRs 0072/0073/0074/0075/0076/0077/0078/0079/0080/0081/0082/0083/0084/0085/0086/0087/0088/0089/0090, and the rev0039 native oracles, including argument-aware
  terminal/namespace fences, descriptor proof, procfd-pinned identity, repeated-quiescence teardown,
  payload process-handle denial, enabled-host dump/core sealing, and optional delegated-cgroup
  leaf/attach/kill/populated ownership, boot/process-incarnation crash recovery under the signed host
  lease, controller-availability/activation proof, pre-recovery exact `(identity, effective budget)` resource preflight,
  pre-attachment pids/memory-high/memory/swap/CPU and exact-device I/O read-back, pre-recovery delegated-root PSI controller construction, exact basis-point hysteresis admission before aggregate reservation or spawn mutation, dedicated kernel PSI trigger descriptors, bounded eventfd-controlled notification monitoring, quiet-window closure, fail-closed monitor/source failure, typed private sample/trigger evidence, protected zero-baseline controller, optional PSI, lifetime-peak, quota-independent CPU, memory-work, swap-event, local-freeze, and IRQ-pressure outcome files,
  teardown-time PID/memory/CPU/I/O counters, all-profile aggregate fit and exact CPU representability proof, atomic pre-mutation process/memory/swap/CPU reservation, proved-cleanup
  rollback on every failed spawn path, teardown-coupled release, fail-closed complete-charge stranding
  on unproved post-spawn cleanup, owner-private quota/period/current/peak/rejection/stranding evidence, plus bidirectional per-record local credentials, optional pidfds,
  ancillary rejection, terminal process-lifetime fencing, bounded multiplexed administrative and
  contender admission, independent leases, per-process/global quotas, and finite accept/work budgets;
  retain independent audit, callback isolation, hostile multi-process coalition stress, and target
  qualification as separate gates;
- complete review of authority migration, local client, audit privacy, denial-of-service limits,
  supportable kernel inventory, and deployment policy;
- pass the full compiler/sanitizer matrix, all fuzzers, long reconnect/PTY soaks, process-leak checks,
  genuine UDP/TCP lifecycle, and R7 latency gate;
- document operator setup, capability grant/revoke, profile configuration, recovery, limitations,
  and emergency disable;
- make feature enablement reversible and default it off for upgrades until an operator configures a
  profile and explicitly grants terminal authority;
- update protocol/status docs and create one ADR that records the evidence and enables feature bit
  23 in the implementation mask.

Exit: Ratox may be presented as a production-supported feature only by builds and deployments that
can serve the frozen contract and carry retained R6–R8 evidence, including successful strict-host
qualification when that tier is claimed. The construction gates remain explicit, reversible, and
default off.

## Immediate work queue

1. [x] Implement and test R1 `InputReceiver` and `OutputHistory` without changing Agent behavior.
2. [x] Add fail-closed `MessageReplayCache` reservation/commit, the pure `InteractiveSession` state
   machine, bounded lifecycle evidence, directory quotas, and exhaustive attachment/input boundaries.
3. [x] Freeze and implement the authority-ledger v2 migration, exact non-widening capability
   semantics, negotiated proof format, remote ceremonies, downgrade tests, and restart fixtures.
4. [x] Freeze the local profile schema and PTY adapter interface, prove the deterministic fake, and
   complete the native Linux process boundary without changing Agent behavior.
5. [x] Join completed R1–R3 in R4 through the staged whole-frame PTY write boundary, preserving
   authority, attachment, disconnect, revocation, retained-send, bounded-fairness, and shutdown
   fences behind a pre-network default-off gate.
6. [x] Build R5's private local streaming protocol, owner-only same-user endpoint, bounded
   controller engine, and one-binary open/resume UX.
7. [x] Build R6's separate-process reconnect, controller-replacement, queue-pressure, revocation,
   and daemon-restart fixtures, backed by a signed pre-network host-incarnation lease.
8. [x] Run R7 Sandwurm two-node complete-service science using active-only cadence, retained two-role
   process-resource intervals, the complete stream/load matrix, bounded impairment, and exact
   total-loss/detached-PTY/resume cells.
9. Optional downstream R8: qualify the cgroup lifecycle/resource/aggregate-admission/PSI trigger/
   outcome envelope under named deployment kernels/service managers and complete independent
   operational review before any production-support claim or broader enablement. ADR 0277 keeps
   this outside repository completion.

This ordering keeps the next commits reviewable and keeps the reachable construction surface behind
explicit local policy, bilateral negotiation, and exact authority while the remaining evidence is
built.
