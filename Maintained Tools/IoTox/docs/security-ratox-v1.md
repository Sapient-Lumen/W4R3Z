# Ratox v1 focused security model

Status: live default-off R8 construction threat model. Updated 2026-09-01. R1 session controls,
R2 authority, R3 profiles/processes, R4 Agent dispatch, R5 controller, the first R6 restart/fault
contract, R7 observability, and the rev0039 capability, confinement, supervision, local-IPC,
cgroup-recovery, resource-budget, aggregate-admission, PSI-admission/trigger, memory-throttle, and
kernel-outcome boundary are implemented. Genuine two-guest Sandwurm R7 direct-UDP/forced-TCP
latency, interference, impairment, total-loss/resume, daemon-replacement, and guest-restart evidence
is retained. Independent review, named deployment qualification, and production activation remain
incomplete. This narrows the repository-wide `threat-model-draft.md` to the frozen Ratox
protocol and reachable construction service. It is not an audit or production-readiness claim.

## Assets and promises

Ratox must protect:

- **input integrity:** each accepted byte reaches the intended current PTY at most once and in order;
- **attachment exclusivity:** only the current authorized controller generation may affect a session;
- **process identity:** delayed traffic cannot target a replacement process or reused session;
- **output truth:** reconnect returns an exact retained suffix or an explicit gap, never invented
  continuity;
- **authority separation:** friendship, Tox identity, text, files, or other capabilities never imply
  terminal access;
- **content privacy:** terminal bytes are not copied into runtime projections, ordinary audit logs,
  diagnostics, crash messages, or command journals;
- **local control:** only the owning local user may configure profiles or attach a local client;
- **availability bounds:** peers cannot create unbounded sessions, replay, output, queues, processes,
  audit records, or CPU work.

Tox and the local host remain trusted for their stated cryptographic and operating-system
properties. Ratox does not claim to contain a malicious program intentionally launched by an
authorized local profile, hide traffic metadata from relays, or make a compromised device safe.

## Trust boundaries

```text
untrusted network packet
  -> c-toxcore callback dedicated to packet 0xA2
  -> current transcript-confirmed online epoch
  -> bilateral ratox-interactive-v1 negotiation
  -> authenticated stable principal and exact-head interactive.terminal authority
  -> strict Ratox decoder and attachment/session state machine
  -> fixed local profile resolution
  -> bounded PTY adapter
  -> locally configured child process

local terminal client (R5)
  -> same-user private streaming endpoint with finite OPEN lease, bounded contenders, and detach-ACK drain
  -> local client framing and escape handling
  -> Agent/session state machine
```

Every arrow is a validation boundary. No downstream component may rely on the previous component
having sanitized terminal content; bytes remain opaque.

## Threat/control table

| Threat | Required control | Failure evidence |
|---|---|---|
| Friend sends Ratox without authority | confirmed directional proof of `interactive.terminal` | denied, no PTY |
| v1 ledger interpreted as granting bit 7 | explicit signed v2 migration; no widening | migration denied |
| Header or record attempts v2 downgrade | replayed format transition, independent domains, header/history equality | protocol error |
| Session carries unnegotiated v2 authority | transcript-bound feature bit 24 and explicit v2 payload marker | unsupported, no mutation |
| Ledger alone is rolled back, deleted, or forked | private committed/pending `IOTOXAG2` head guard | protocol error, no mutation |
| Ledger and guard are restored as one older pair | external or hardware monotonic witness | explicit nonclaim |
| Old controller races new controller | nonce + strictly increasing generation on every frame | stale generation |
| Delayed packet reaches replacement PTY | nonzero incarnation changes on process replacement | stale incarnation |
| Duplicate control executes twice | reserve exact route-scoped request and result capacity before effect; never evict IDs | replay result or deny before effect |
| Stale or parallel route replays an owning-route control | domain + friend number + online epoch prefix every live-session replay key; validate attachment before effect; cancel rejected reservations | protocol error, no effect, no retained slot |
| Unauthorized peer probes absent ATTACH/RESUME | authorize before distinguishing absence; retain the denial exactly | denied, no existence disclosure |
| Authority head changes between authorization and PTY effect | serialize signed head mutation with Ratox receive and bounded service progress | new head reconciled before effect or old-head cycle completes first |
| Fresh control enters a terminal session | only retained/pending IDs survive failure or close; new IDs cannot reserve | closed/terminal denial |
| Duplicate/replayed INPUT | exact next-byte receiver and cumulative ACK | duplicate ACK, no write |
| Partial overlap hides different bytes | reject partial overlap as protocol error | session protocol error |
| Missing INPUT is skipped | future range withheld; sender replays retained prefix | current ACK repeated |
| PTY accepts only part of INPUT | stage one frame; ACK only on whole completion; no interleaving | close failed incarnation |
| Output eviction looks continuous | retained base plus mandatory `OUTPUT_GAP` | explicit gap |
| SENDQ rejection loses a response | exact outbound packet remains owned until toxcore accepts it | retained queue and event counter |
| Transport command/event heap storage retains terminal bytes | shared wiping owner-command payload on send; exception-safe event-vector wipe after ingress metadata projection | transport adapter tests plus sanitizer matrix |
| Retained success crosses a later revocation | persist an authority-required fence with the packet and exact replay; revalidate friend/epoch/principal before send | route purge and authority-revocation close |
| Peer exhausts memory/processes | fixed per-session, per-principal, per-device, and queue quotas | resource exhausted |
| Peer supplies executable/path/env | OPEN has no such fields; local profile is authoritative | unsupported/denied |
| Payload injects bytes through terminal ioctl | argument-aware seccomp denies `TIOCSTI` and reviewed console/VT mutations | `EPERM` before fd validation |
| Payload creates a namespace through clone flags | inspect legacy clone flags; force clone3 to `ENOSYS` fallback; deny unshare/setns | `EPERM`, no namespace creation |
| Payload acquires a new process handle | deny pidfd open/signal and reviewed pidfd memory interfaces in baseline/strict | `EPERM` before ordinary validation |
| PID is reused between session inventory and signaling | pin `/proc/<pid>`, compare reported PID/session/start time after pidfd acquisition, signal only through pidfd | vanished/mismatch, no redirected signal |
| One empty procfs pass releases the session-ID pin | retain waitable leader and require three consecutive complete empty inventories | first and second empty passes remain unreaped |
| Descendant forks or migration race final PTY teardown | optional supervisor-owned cgroup-v2 leaf; attach blocked helper before manifest; final `cgroup.kill`; wait recursive `populated=0` | fail closed before target, or empty exact leaf before leader reap |
| Daemon crash leaves a populated delegated PTY subtree | boot ID + PID + procfs start time in the leaf name; signed host lease serializes recovery; pidfd/procfs proof precedes bounded recursive kill | exact live owner preserved, proven stale owner reclaimed, ambiguous legacy owner blocks startup |
| Payload controls its own kill boundary | exact non-root identity distinct from daemon, cleared supplementary groups, supervisor-owned non-writable delegation and controls | activation/spawn denied |
| Local profile attempts to weaken the host cgroup ceiling | monotone scalar minimum plus exact lower CPU ratio; host representation wins equal ratios | host ceiling remains effective or profile tightens it |
| Two profiles share one payload uid but carry different budgets | preflight distinct `(identity, effective budget)` pairs after host lease and recompute at spawn | every exact controller policy is proved before network exposure |
| Simultaneous profile maxima multiply into host overcommit | resolve exact process/memory/swap/CPU charges, reject nonintegral CPU normalization, atomically reserve the complete vector before mutable spawn work, and retain the token through complete cgroup teardown | typed policy/capacity failure with no helper, PTY, cgroup, or process side effect |
| A new PTY is admitted while the delegated host subtree is already under sustained pressure | descriptor-pinned CPU `some avg10`, memory `full avg10`, and I/O `full avg10` policy; exact basis-point comparison; mutexed hysteresis gate before aggregate reservation or mutable spawn work | resource exhausted with no reservation, helper, PTY, leaf, or process side effect |
| A configured continuous PSI observer stops, loses a source, or reports a cumulative stall trip | one independently opened trigger descriptor per resource, bounded poll/eventfd monitor, atomic pending-state transfer, minimum-window hold, and fail-closed monitor-health latch | local `unavailable`; no new aggregate reservation, helper, PTY, leaf, or process mutation |
| PSI accounting is disabled, disappears, or becomes malformed after activation | controller construction under the signed host lease before recovery/network mutation, exact `cgroup.pressure=1` proof before and after configured reads, complete canonical sample parsing, and fail-closed latch until one valid sample satisfies every reopen threshold | startup refusal or local `unavailable`; bounded owner-private status retains last-sample validity, original typed cause, and close/reopen/failure counters |
| Enabled host exposes ordinary same-UID dump/core behavior while holding secrets | set and verify nondumpability plus hard/soft zero core limits before Agent construction | startup fails before device state |
| Terminal bytes inject logs or paths | content-free structured audit; no content rendering | bounded event only |
| Different local UID attaches to R5 stream | mode-0600 endpoint, private parent, path/inode checks, `SO_PEERCRED` | denied before OPEN |
| A connected descriptor is inherited or passed to another process | require per-record `SCM_CREDENTIALS`, optional exact `SCM_PIDFD`, and equality with the connection peer in both directions | mismatched sender rejected before decode/dispatch |
| A sender injects descriptors or malformed ancillary data | fixed control ceiling, `MSG_CMSG_CLOEXEC`, close every received right, reject truncation/duplicates/unknown controls | no descriptor retained; record rejected |
| Original terminal owner exits while another process keeps the socket description | retain exact owner pidfd and poll exit beside socket readiness | release slot without accepting successor-process impersonation |
| Silent same-UID client reserves the sole terminal slot | finite first-OPEN steady-clock lease; no publication before committed OPEN | typed timeout, successor admitted |
| Silent same-UID client reserves administrative control processing | bounded multiplexed pending set with independent leases and ready-before-expiry service | timed-out peer closes while unrelated ready request completes |
| One process occupies every local pending descriptor | separate global/per-process quotas plus finite admission refills | excess peer receives best-effort resource-exhausted response |
| Busy-close races contender OPEN | active descriptor terminal event is handled before contender work; pre-OPEN ERROR is connection-scoped | successor is admitted after dead owner release, not denied for stale ownership |
| Losing contender reaches Agent effects | decode first record only for response identity; never dispatch | exactly one OPEN handler call |
| Server closes before final detach ACK commits | bounded ACK-only close phase after DETACH; output remains render-before-ACK | exact cumulative ACK reaches handler before release |
| Detach drain spins, exceeds its I/O lease, or denies a valid successor | omit listener from drain polling; apply one absolute deadline to packet sends; keep successor in kernel backlog | bounded release without stale busy result |
| Post-detach packet starts a fresh effect | accept only exact-stream OUTPUT_ACK after DETACH and reject before dispatch | no PING/input/resize/close handler effect |
| Client crash leaves raw terminal | scoped termios restore and signal/exit handlers | process tests and cleanup paths |
| One route loses its exact-head proof | fence only sessions owned by that friend/epoch; do not rewrite ownership from rejected traffic | route-scoped authority close |
| Principal is durably revoked | reconcile the signed ledger by stable principal, including detached sessions and other epochs | principal-wide authority close |
| Tox friend number is reused | resolve live handle through stable key/session identity | identity mismatch |
| Daemon restart reuses old state | fresh incarnation or explicit durable-supervisor protocol | not found/new incarnation |
| Malformed frame causes side effect | canonical decode and state validation precede mutation | protocol error |
| Exit/close race gives two outcomes | one terminal transition and duplicate result cache | repeated same result |


Route proof freshness is not the same fact as durable authority. A missing/stale proof on one
friend/epoch may reflect proof refresh or route churn; it closes only sessions whose last successful
attachment was owned by that exact route. A signed-ledger revocation is reconciled separately by
stable principal and reaches detached sessions. Rejected packets never update the recorded authority
route. Live-session replay identity also includes the authenticated route, so byte-identical traffic
from another route cannot inherit a successful PONG or empty-control outcome.

Exact-head authorization is also ordered with the effect it authorizes. Local signed appends and
accepted remote owner mutations share an Agent-level boundary with Ratox receive, bounded PTY
progress, and transport admission. Retained packets distinguish authority-bound results and stream
traffic from explicit unauthorized admission denials. That dependency survives replay, so a cached
success cannot be reclassified as a harmless denial when the current proof disappears.

## Process and profile risks

A PTY is a powerful local execution surface even when the network protocol is correct. Profiles are
therefore local configuration, not authority records and not wire data. Profile v3 has no remote
selector; local policy resolves at most one enabled profile for the proven principal or denies OPEN.
Canonical v1 records remain readable as the explicitly named `compatibility` tier. R3 plus the rev0025
R8 hardening freeze and test:

- exact fixed argv and descriptor-opened ELF executable resolution without shell expansion;
- owner-only no-follow profile-store, executable, helper, and working-directory handling;
- exact environment construction from fixed values plus a small inherited allowlist;
- UID/GID, supplementary groups, `umask(077)`, soft resource limits, core disablement, nondumpability,
  and two-pass inventory-proved descriptor closure;
- runtime capability-ceiling discovery; zero ambient/effective/permitted/inheritable verification;
  and, for privileged launches, locked securebits plus a verified empty capability bounding set;
- a default architecture-checked seccomp hazardous-interface deny floor with reviewed ioctl-request
  and clone namespace-flag inspection, plus clone3-to-legacy fallback that preserves ordinary fork/threads;
- an opt-in strict tier that fails closed unless MDWE and Landlock ABI 10 are installed, permits
  ordinary mutation only below the already-open non-root cwd, grants no TCP/UDP port, and scopes
  pathname/abstract Unix sockets plus external signals;
- `posix_spawn` into the reviewed one-binary hidden child, avoiding post-fork C++ application code;
- readiness plus close-on-exec EOF, finite startup timeout, named security stages,
  signal/resize/close escalation, required baseline/strict pidfd/genuine-procfs support, pinned
  PID/session/start-time revalidation, repeated-quiescence session-wide HUP/TERM/KILL sweeps, exact
  child reap, parent-death handling, and bounded Agent shutdown drain;
- baseline/strict payload denial of pidfd open/signal plus reviewed process-memory pidfd interfaces;
- optional supervisor-owned cgroup-v2 leaf creation, blocked-helper attachment before manifest release,
  final `cgroup.kill`, recursive `populated=0` completion, exact inode-checked removal, and boot/process-
  incarnation-bound startup reclamation under the durable host lease;
- optional administrator-owned host and profile-scoped `pids.max`, `memory.max`,
  `memory.swap.max`, `memory.oom.group=1`, and `cpu.max` policy, with monotone host/profile composition,
  available-and-active controller proof, exact `(identity, effective budget)` preflight before orphan
  recovery/network activation, exact read-back, and application before helper attachment;
- optional administrator-owned aggregate process, memory, swap, and exact-average-CPU reservation
  maxima; all enabled profiles must expose finite matching effective maxima, fit once, and map CPU
  exactly to the selected accounting period, the production factory atomically charges the complete
  vector before mutable spawn work, move-only RAII rolls back every pre-spawn or proved-cleanup
  failure, the token remains charged through cgroup quiescence/removal and direct-child reap, and
  unproved post-spawn teardown strands rather than releases the complete charge;
- optional administrator-owned delegated-root PSI admission using exact CPU `some avg10`, memory
  `full avg10`, and I/O `full avg10` maxima plus a common basis-point hysteresis margin; controller
  construction occurs under the signed host lease before resource probes, orphan recovery, listener,
  or network mutation; descriptor-pinned files prove `cgroup.pressure=1` before and after configured
  reads; every new production PTY samples under one mutex before aggregate reservation or mutable spawn
  work; any read/parse/capability failure returns local unavailability and latches closed, with the
  original typed local cause retained privately; optional per-resource PSI triggers use separate
  read/write descriptors and one bounded monitor, close between admissions, hold through at least one
  tracking window, and fail closed on monitor loss; reopening requires every configured metric to be at
  or below its exact lower threshold;
- protected optional per-cgroup CPU, memory, and I/O PSI descriptors opened before attachment,
  canonical zero-baseline proof, exact enabled-state proof when `cgroup.pressure` exists, and one-shot
  post-quiescence absolute stall totals accumulated with saturation and explicit capability counts;
- enabled-host nondumpability and irreversible zero core limits before Agent construction.

No created namespace, aggregate I/O reservation, persistent PSI history service, atomic
cross-resource PSI snapshot, automatic pressure-threshold tuning, existing-session preemption,
synchronized-period or parent/burst CPU enforcement, physical resource preallocation, cross-daemon
distributed capacity, mount isolation, container, VM, complete syscall allowlist, read/execute
confinement, or proof against unknown future session-escape interfaces is claimed. The optional
delegated-cgroup path assumes one
trusted local writer and does not silently downgrade when requested. `compatibility` intentionally
omits both that path and the IoTox seccomp/Landlock policies while retaining the common
capability/credential floor; `strict` never silently becomes compatibility or baseline.

“Authorized terminal” means authorized to use the configured local profile. The selected tier and
retained evidence must be named; none of the tiers alone establishes a complete sandbox.

## Protocol and state-machine risks

The custom-lossless carrier preserves provider order while connected, but Ratox correctness must not
depend on reconnect ordering, callback identity, or a Tox friend number remaining stable. The
session engine owns input/output sequence spaces and the attachment fence. It must be tested with
events duplicated, delayed, replayed, split at every byte boundary, and delivered after disconnect,
reattach, process replacement, authority revocation, and quota failure.

Message IDs provide bounded result deduplication only. They do not authorize a request and do not
replace cumulative byte positions. An ACK is a statement about PTY commitment/consumption as defined
by the state machine, not merely successful c-toxcore admission.

PTY commitment is whole-frame but cannot make a process side effect transactional with a daemon
crash. A partial sink error closes the incarnation and forbids replay into its replacement. The
initial restart contract terminates the PTY, so an unacknowledged frame is not replayed into a
possibly surviving process. Any future process-survival design needs a supervisor participating in
a separately reviewed crash-safe input-commit protocol.

## Availability and congestion

Control and input are indispensable lossless data. A peer can still induce queue pressure or forced
TCP head-of-line delay. Required bounds are:

- 64 KiB unacknowledged input per session;
- 1 MiB retained output per session;
- two live sessions per principal and eight per device;
- at most 1,076 payload bytes per packet;
- 20 ms base admission pacing, 320 ms ceiling, retained rejection;
- bounded duplicate cache, audit journal, pending responses, and per-iteration service;
- round-robin global PTY service budgets so a continuously ready session cannot monopolize progress;
- bounded administrative and terminal-contender pending sets, per-process/global quotas, independent
  leases, finite admission refills, and finite ready-record work per cycle;
- at most 32 retained Ratox transport sends per Agent cycle.

When a bound is reached, the system backpressures or returns an explicit or best-effort local error.
It never silently
drops accepted input or claims complete output. A dedicated Tox route is not a security control by
itself; it must authenticate to the same stable device and cannot bypass authority or attachment
state. Local admission bounds do not preempt a synchronous callback that blocks after admission and
do not establish starvation freedom against an unlimited coalition of same-UID processes.

## Privacy and audit

The rev0020 `ratox-events` journal contains only an ordinal, lifecycle kind, typed error code,
friend routing handle, online epoch, session/principal identifiers, frame type, incarnation,
generation, and cumulative sequence positions. Owner-private aggregate status publishes only
configured process/memory/swap/CPU maxima, the CPU accounting period, exact current and peak
reservations, active-token counts, rejected-admission counts, and stranded-reservation counts. The journal deliberately excludes input/output bytes, argv, environment, cwd, paths, profile
IDs, error strings, command history, and recovery material. The current identifiers are not hashed;
filesystem privacy relies on the private runtime-tree boundary and rotation, so export/redaction policy
remains a later operational decision.

The same owner-private boundary publishes only the configured PSI basis-point maxima and hysteresis,
trigger window/stall policy, the gate latch, monitor health and active/remaining hold, saturating sample/
admission/failure/transition and total/per-resource trigger counters, typed sampling/monitor error
classes, and the last complete valid configured `avg10` observation. A failed sample
is marked invalid without erasing the preceding valid observation. It publishes no PSI file paths,
profile labels, process identifiers, terminal content, error strings, or partial failed sample.

Terminal content remains visible to the endpoint processes and their local users, and traffic timing
and volume may be visible to network infrastructure. The first release makes no terminal-content
forward-secrecy claim beyond the selected Tox session and no anonymity claim.

## Security gates before production support or broader activation

- strict codec fuzzing plus stateful frame-sequence fuzzing;
- exhaustive at-most-once and stale-generation tests at every input/ACK boundary;
- capability migration, delegation, revocation, RecallRoot, ownership-transition, and rollback tests;
- local endpoint connection/record credentials, pidfd lifetime, ancillary injection, symlink,
  replacement, silent-admission, bounded multiplexing, per-process quotas, active-stream latency,
  typed-contention, detach-ACK, and multi-client races;
- PTY descriptor, child, signal, output-pressure, storage, and shutdown fault injection;
- PSI capability, trigger registration/delivery, disabled-accounting, malformed-sample, threshold,
  hysteresis, hold, monitor-failure, latch, and concurrent admission qualification on kernels that expose
  per-cgroup PSI;
- sanitizer, ThreadSanitizer, long reconnect/attach/exit soak, and process/descriptor leak checks;
- two-host direct UDP and forced TCP lifecycle and latency evidence;
- manual review of the protocol, authority migration, profile schema, process boundary, and audit
  fields before Ratox is described as production-supported beyond the bounded self-mode/manual
  construction gates.

## Open security decisions

ADR 0063 resolves the authority-ledger v2 migration and in-history downgrade behavior. ADR 0064
resolves local profile grammar and the current Linux process boundary. ADR 0065 resolves the default-
off live Agent gate, exact dispatch order, retained outbound semantics, round-robin coordinator, and
content-free runtime journal. ADR 0066 resolves the separate R5 controller stream; ADR 0067 resolves
finite pre-OPEN admission, bounded typed contention, and bounded post-DETACH ACK commitment. ADR 0068
resolves the signed pre-network host-incarnation reservation and crash-durable hierarchy commit. ADRs
0072 through 0090 resolve the current terminal capability, argument, procfd identity, host-seal,
delegated-cgroup lifecycle/recovery/resource/aggregate-admission/outcome telemetry, and message-bound
local-seqpacket, PSI-admission, and continuous PSI-trigger boundary. None claims
detection of restoring an older complete authority snapshot without an external witness.

Remaining decisions are:

1. Whether PTY survival across daemon restart justifies a separately supervised durable child and
   new crash-safe journal; the current resolved behavior intentionally terminates it and returns
   `not_found`.
2. Audit retention, identifier hashing/redaction, and operator export policy.
3. Additional deployment confinement and the minimum supported Linux/kernel/service-manager set.
4. Independent security/operational review and the R8 production-support activation decision.

Defaults remain disabled and fail closed. The explicit rev0039 enable flags are construction/testing
surfaces, not resolution of the remaining operational R8 gates.
