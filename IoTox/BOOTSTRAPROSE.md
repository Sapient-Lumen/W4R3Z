# BOOTSTRAPROSE — IoTox rev0051, “Freshness-Explicit Projection Recovery”

```text
Project:               IoTox
Revision:              rev0051
Version:               0.51.0
Codename:              Freshness-Explicit Projection Recovery
Toxcore target:        0.2.23
Outer linked revision: rev0026
Language:              C++20
Public install:        one executable, iotox
Default network mode:  Tox/native; strict Tox/Tor is construction-enabled and bounded operator-route-qualified; Ratox roles disabled unless --mode self is selected
Current evidence:      859 owned checks; 62 default CTest targets; 12 fuzzers
```

This is the governing wake-from-amnesia entrance. Read it first, then
`README.md`, `docs/product-page.md`, `docs/roadmap.md`, the current ADRs, and
executable evidence. Significant architectural additions also begin with
`docs/architectural-change-intake.md`. Prose never overrides source, tests,
raw logs, or the exact packaged commit.

## 1. Identity and invariant

A correct build reports:

```text
rev0051
IoTox 0.51.0 rev0051 (Freshness-Explicit Projection Recovery)
toxcore-target=0.2.23
```

IoTox remains one installed executable. Internal libraries, test programs, exact provider doubles,
fuzzers, and hidden child roles are build or verification machinery, not public products. The product
invariant remains:

> The outside should be ordinary; the inside must tell the truth.

Friendship is not authority. Transport admission is not remote receipt. An online route is not an
authenticated principal. A local write is not a committed remote effect. A mock is not the public Tox
network. Every boundary preserves these distinctions explicitly.

## 2. Security posture

IoTox is owner-first, capability-gated, bounded, and fail closed. It uses private runtime paths and
Unix sockets, transcript-confirmed online epochs, stable-principal proof, exact-head signed authority,
canonical bounded codecs, immutable retained packets, explicit replay positions, owner-controlled
terminal profiles, a sealed Linux PTY child boundary, and content-free terminal lifecycle evidence.

No device becomes authoritative through an account, friend request, public key alone, socket pathname
alone, or successful send call. Manual mode leaves Ratox disabled by default. Self mode deliberately
turns the Ratox host and same-user terminal controller on by default, but profile binding, current
authority, and host policy still decide whether any shell can be reached.

## 3. Construction through R6

### R1 — Ratox v1 session engine

Packet `0xA2` carries canonical Ratox v1 frames. The pure host state machine enforces complete
attachment identity, cumulative positions, exact duplicate replay, whole-frame input commit, bounded
output retention, explicit gaps, generation fencing, deterministic lifecycle, quotas, and finite work.

### R2 — authority-ledger v2

`interactive.terminal` exists only in authority-ledger v2. A remote Ratox operation must match the
current authenticated principal, online epoch, and authoritative ledger head. Revocation removes
effect authority immediately.

### R3 — sealed profile and PTY boundary

An owner-private profile binds a stable principal to fixed executable, argv, cwd, environment,
identity, limits, dimensions, and shutdown policy. Remote bytes cannot choose those fields. The Linux
child receives an already-open, canonical manifest and proves readiness and final exec through a
private descriptor handoff. This is a constrained process boundary, not a complete sandbox.

### R4 — self-gated live host dispatcher

`--enable-ratox-terminal`, or `--mode self` as the self-machine product mode, validates the profile
store, enabled binding, helper/factory, and signed host-incarnation lane before toxcore starts. Only
then may feature bit 23 be advertised. Incoming Ratox traffic crosses transcript, epoch, principal,
authority, route, replay, and queue gates before any PTY effect.

### R5 — private same-user controller stream

`--enable-ratox-terminal-client`, or `--mode self`, independently publishes
`<runtime>/terminal.sock`. The Linux pathname `SOCK_SEQPACKET` endpoint requires an owner-private
parent, connection-time `SO_PEERCRED`, and
per-record kernel `SCM_CREDENTIALS` in both directions. Supported kernels additionally deliver an
exact `SCM_PIDFD`; malformed/truncated/duplicate ancillary records and injected descriptors are closed
and rejected. The terminal owner process is retained by pidfd, so its exit releases the slot even when
the socket descriptor was inherited or passed elsewhere. No-follow inode checks, close-on-exec/
nonblocking descriptors, and exact socket cleanup remain mandatory. A finite first-OPEN lease prevents
a silent client from holding the only slot.

The active terminal stream is now polled ahead of an independent bounded contender set. Contenders
have individual leases, global and per-process quotas, accept-refill limits, and a finite record-work
budget per cycle. A complete queued first record may be decoded only to return the contender's exact
stream ID; it is never dispatched into the session. Silent or partial contenders therefore cannot
impose a fixed grace wait on active-stream I/O, while active disconnect still wins before successor
admission.

The installed executable exposes `iotox terminal PEER_PUBLIC_KEY_HEX` and
`iotox terminal-resume SESSION_ID_HEX [PEER_PUBLIC_KEY_HEX]`. Output is written before cumulative ACK,
terminal state is restored, resize is propagated, and local escapes are explicit.

Administrative `control.sock` uses the same bidirectional record identity. Instead of serializing the
listener behind one accepted client, it multiplexes a bounded pending set with independent request
leases, global and per-process quotas, accept-refill limits, and a finite ready-request budget per
cycle. Ready records are handled before expired silent peers, and overload replies are nonblocking
best effort. Reachable listeners are preserved, stale socket replacement is device/inode rechecked,
and shutdown unlinks only the inode this server bound. These are process-binding and bounded-
availability controls, not authorization among arbitrary processes sharing the same UID or starvation
freedom against an unlimited coalition of same-UID processes.

### R6 — signed restart fence and separate-process fault gate

An enabled host reserves one device-bound incarnation before constructing Ratox service, local
listener, or transport. The exact 128-byte `IOTXRIN1` record contains the device signing public key,
a nonzero incarnation, its complement, and an Ed25519 signature. The first value is random below the
high bit; every successful successor commits exactly `+1`.

The default lane is `<savedata-parent>/ratox/incarnation.state`. Descriptor-relative no-follow
traversal rejects `..`, links, wrong owner/type/mode/size, and non-private final parents. A same-purpose
0600 lock is held with nonblocking `flock`; post-lock inode identity is revalidated. Commit uses a
private temporary inode, file `fsync`, identity checks, descriptor-retained `renameat`, installed-path
identity verification, directory `fsync`, strict reopen, and signature verification. A contender
cannot advance the record. Runtime status publishes only the incarnation and lease-held fact.

Authentication for the live online epoch is retained separately from current effect authority solely
so a revoked ATTACH/RESUME can receive one explicit replayable denial. It never re-authorizes a PTY
effect. Failed startup remains projected as `phase=failed` after cleanup releases every resource.

The deterministic R6 evidence crosses the real daemon, private controller stream, owner thread, mock
Tox transport, packet `0xA2`, profile resolver, native PTY helper, reconnect, controller replacement,
SENDQ retry, signed revocation, explicit denial, daemon replacement, and stale-session refusal. The
source-controlled restart process gate separately proves lifetime lease exclusion, failed-start truth,
clean release, and exact successor `+1`.

## 4. R7 observability and evidence boundary

The transport owner records exact-at-the-gate queue distributions for interactive, control, and bulk
commands. Runtime status publishes p50/p95/p99 bounds and exactness flags, the >=2 ms count, coherent
typed sensitive-send outcomes, separate controller/host retained-head streak and age, and monotonic
Ratox lifecycle time. None of those records contain terminal bytes.

`tools/prepare-ratox-r7.py` and `tools/analyze-ratox-r7.py` implement the ADR 0071 v2 chain. A
balanced SHA-256/Fisher-Yates schedule reconstructs every route/load trial and token. Evidence retains
raw controller-local and host-local timestamps and derives only same-clock intervals. Host events join
one exact INPUT admission, whole-frame PTY commit, and OUTPUT append through content-free message,
byte-span, and event coordinates.

Canonical digests bind schedule, samples, and the exact retained route/bulk observation files. Two
distinct ephemeral Ed25519 capture keys sign role-separated payloads containing the same unsigned run;
signing checks the local Linux boot ID and key consistency, while sealing and analysis verify both
signatures. The analyzer still rejects missing cells, undersampling, unsafe files, malformed canonical
records, reordered timestamps/events, overlapping spans, and altered auxiliary evidence. A PASS is a
bound evidence gate, not remote attestation or proof that physical metadata is truthful.

Sanitizer presets split the 859-check owned registry into sixteen deterministic shards. The ordinary
default remains one process so ordering and contamination regressions remain visible.

## 5. Terminal capability and kernel-confinement boundary

Canonical profile v5 retains the confinement, hard-budget, and soft-memory fields from v4 and adds
one exact block-device I/O policy:

```text
confinement=compatibility|baseline|strict
cgroup-pids-max=none|u64
cgroup-memory-high-bytes=none|u64
cgroup-memory-max-bytes=none|u64
cgroup-swap-max-bytes=none|u64
cgroup-cpu-quota-us=none|u64
cgroup-cpu-period-us=none|u64
cgroup-io-device=none|u32:u32
cgroup-io-rbps=none|u64
cgroup-io-wbps=none|u64
cgroup-io-riops=none|u64
cgroup-io-wiops=none|u64
```

The encoder always emits v5. Canonical v1 through v4 records remain accepted; v1 maps to
`compatibility`, v1/v2 map to an empty profile cgroup budget, v3 leaves `memory.high` absent, and
v1-v4 leave I/O policy absent. They are never silently strengthened. New in-memory profiles default
to `baseline`.

Every mode receives the common process floor:

```text
runtime capability-ceiling discovery with a finite review bound
ambient capability clear and readback across that runtime ceiling
zero effective, permitted, and inheritable sets before final exec
privileged securebits lock and complete bounding-set removal when CAP_SETPCAP is available
fail-closed refusal of a privileged context that cannot establish the required seal
no_new_privs, helper-handoff nondumpability, exact identity, rlimits, core disablement
parent-death rearm, umask(077), inventory-proved descriptor closure, readiness and final-fexecve proof
```

Baseline adds an architecture-checked classic-BPF seccomp deny filter. It terminates architecture
confusion, rejects x32 on x86-64, and returns `EPERM` for a reviewed bounded set of high-risk process,
kernel, mount/namespace, module, keyring, privileged-I/O, host-identity, and time-mutation interfaces.
rev0023 added syscall-argument inspection; rev0024 retains it: the reviewed terminal/console mutation ioctl set is denied,
legacy `clone` namespace bits are denied on the architecture-correct flags argument, and `clone3`
returns `ENOSYS` so libc can use the inspected legacy path. After helper setup, `setsid`, controlling-
terminal detach/reassignment, and parent-death-signal mutation are denied. Ordinary ioctl validation,
real fork, and post-filter thread creation remain executable evidence. All unnamed syscalls and ioctl
requests remain allowed; this is not a complete allowlist.

Strict adds verified `PR_MDWE_REFUSE_EXEC_GAIN` and a no-downgrade Landlock ABI 10 domain. Ordinary
mutation is granted only beneath the already-open non-root working directory. Device-node creation,
external TCP/UDP, external pathname/abstract Unix sockets, and external signals are denied. The
portable enforcement oracle separates allowed in-tree mutation from denied out-of-tree
create/truncate/unlink and TCP/UDP bind/connect/send. Read and execute rights are not handled.
Unsupported or externally blocked MDWE, Landlock, or seccomp rejects
the spawn at a named stage; strict never falls back.

The local build environment's outer syscall policy reports Landlock unavailable, so retained strict
evidence here is the named fail-closed branch. The same process oracle contains the enforcement branch
for a qualified ABI-10 host, but this revision does not claim that branch was reached locally.

Baseline and strict preflight `pidfd_open`, `pidfd_send_signal`, readable procfs identity, and readable
procfs inventory, then require a retained close-on-exec child pidfd. rev0024 verifies that inventory is
an actual procfs mount, opens each numeric process directory without following links, and binds every
candidate to its reported PID, fixed session, live state, and field-22 start time. After pidfd
acquisition it re-reads those witnesses through the same pinned directory before signaling through
`pidfd_send_signal`. Once KILL begins, three consecutive complete empty inventories are required before
the still-waitable leader is reaped. Any live member resets the quiescence count. A bounded fork-churn
oracle covers descendants created into separate process groups during teardown, while a direct zombie
oracle proves that one or two empty scans cannot release the session-ID pin.

The baseline filter also denies payload acquisition/use of the reviewed process-handle interfaces:
`pidfd_open`, `pidfd_send_signal`, `process_madvise`, and `process_mrelease`. When the explicit host gate
is enabled, the long-lived Agent process becomes non-dumpable and receives hard/soft core limits of
zero before device state is constructed. Compatibility alone retains the historical process-group
path.

rev0025 optionally replaces KILL convergence with one explicit delegated cgroup-v2 lifecycle unit.
`--ratox-cgroup-root` must name a normalized non-root daemon-owned delegation with the required
migration and kernel-control permissions. Every enabled profile must be baseline/strict with a
non-root exact UID distinct from the daemon and cleared supplementary groups. The supervisor creates
one underscore-prefixed inode-pinned domain leaf, attaches the still-waitable helper before releasing
its manifest, writes `cgroup.kill` for explicit KILL and natural-leader cleanup, waits for recursive
`cgroup.events: populated 0`, removes the exact leaf, and only then reaps the leader. Configured
failure never silently returns to procfs. Empty configuration retains the rev0024 behavior.

## 6. Activation examples

Self-machine Agent:

```sh
iotox run \
  --mode self \
  --state /absolute/device.toxsave \
  --runtime /absolute/private-runtime \
  --ratox-profile-store /absolute/owner-private-profile-store \
  --ratox-helper /absolute/path/to/iotox
```

Self mode is the default-on Ratox product path for machines the owner treats as their own swarm. It
enables both the host dispatcher and the same-user controller. It does not install profiles, choose a
remote shell, grant `interactive.terminal`, enable sudo, or turn friendship into authority.

Manual host only:

```sh
iotox run \
  --state /absolute/device.toxsave \
  --runtime /absolute/private-runtime \
  --enable-ratox-terminal \
  --ratox-profile-store /absolute/owner-private-profile-store \
  --ratox-helper /absolute/path/to/iotox
```

An explicit alternative durable lane may be supplied with
`--ratox-incarnation-state /absolute/private/incarnation.state`.

An administrator-provided exclusive cgroup-v2 subtree may be selected with:

```text
--ratox-cgroup-root /absolute/delegated/cgroup-v2/subtree
```

The administrator-owned host ceiling provides `--ratox-cgroup-pids-max`,
`--ratox-cgroup-memory-high-bytes`, `--ratox-cgroup-memory-max-bytes`, `--ratox-cgroup-swap-max-bytes`,
`--ratox-cgroup-cpu-quota-us`, `--ratox-cgroup-cpu-period-us`, `--ratox-cgroup-io-device`, and
read/write BPS and IOPS options. Requested controllers must be available and active at the delegated
root. rev0037 retains composition of those command-line values with each enabled profile's v5 budget. Scalar maxima
select the smaller configured value; CPU selects the lower exact `quota/period` ratio; I/O requires the
same exact device then selects each lower rate. Agent startup applies and exactly reads back every
distinct `(payload identity, effective budget)` policy in a disposable leaf before the PTY factory or
network activates; a real session recomputes and repeats that proof before attaching the blocked
helper. Zero swap forbids swap; memory values are page aligned; the effective `memory.high` never
exceeds `memory.max`; and complete `io.max` semantics must read back exactly.

rev0032 retains `--ratox-cgroup-aggregate-pids-max`,
`--ratox-cgroup-aggregate-memory-max-bytes`, and
`--ratox-cgroup-aggregate-swap-max-bytes`, and adds
`--ratox-cgroup-aggregate-cpu-quota-us` plus
`--ratox-cgroup-aggregate-cpu-period-us`. Each configured aggregate dimension requires a finite
matching effective limit in every enabled profile and must fit once at activation. CPU ratios are
compared exactly and normalized to the selected accounting period with GCD reduction; a fractional
quota-microsecond result is rejected rather than rounded. The production factory atomically reserves
the complete composed process/memory/swap/CPU vector before any helper-path, PTY, cgroup-leaf, or
spawn mutation. A move-only token rolls back pre-spawn and proved-cleanup failures and remains held
through recursive cgroup quiescence, exact leaf removal, and leader reap. Unproved post-spawn cleanup
strands the complete charge until restart recovery. This is conservative configured-maximum average-
bandwidth accounting, not physical preallocation, parent-cgroup CPU enforcement, synchronized period
boundaries, or PSI-driven admission.

rev0033 retains bounded, content-free kernel outcomes after recursive `populated 0` and before exact
leaf removal. It prefers `pids.events.local` and `memory.events.local`, accepts a childless
hierarchical fallback only when a local interface is unsupported, and reads `cpu.stat` only for
CPU-limited sessions. Completed and incomplete outcome counts, PID-limit hits, memory high/max/OOM
events and kills, and CPU usage/throttling counters are saturating and owner-private. Missing or
malformed telemetry never blocks cleanup and is never reported as a complete observation.

rev0034 adds protected `io.stat` for I/O-limited sessions. New leaves require a zero known-counter
baseline. After recursive quiescence, saturating read/write/discard byte and operation totals are
captured before exact removal and added to the same unlabeled owner-private outcome state. The exact
numeric device is never published. `io.max` is a rate limit, not aggregate media reservation,
deterministic latency, or automatic topology discovery.

rev0035 adds protected optional `cpu.pressure`, `memory.pressure`, and `io.pressure` interfaces for
every delegated session leaf, independent of configured ceilings. A present `cgroup.pressure` control
must report accounting enabled. Fresh leaves require zero cumulative `some` and optional `full`
microsecond totals; after recursive quiescence the same bounded parser captures final absolute totals
before exact removal. Owner-private status aggregates each resource with separate interface/full-class
availability counts and saturating arithmetic. Rolling averages are validated but not retained. This
is completed-session outcome evidence, not live pressure monitoring, trigger registration, causal
attribution, or adaptive admission.

rev0036 adds protected independently optional `pids.peak`, `memory.peak`, and `memory.swap.peak`
descriptors for every delegated session leaf. Available records must begin at canonical zero and are
read after quiescence as exact optional lifetime high-water marks. `cpu.stat` is attempted for every
session, including those without quota policy; usage/user/system are mandatory, while bandwidth and
burst fields are accepted only as complete nested tuples. Private status adds explicit capability
counts, saturation-safe peak sums/maxima, and CPU work/throttle/burst totals. These are completed-
session observations, not simultaneous demand, working sets, live sampling, or admission policy.

rev0037 adds protected `memory.stat`, `memory.swap.events`, `cgroup.stat.local`, and `irq.pressure`
records. Memory work and swap-event interfaces become mandatory when their linked memory or swap
policy is active; newer local-freeze and IRQ-pressure capabilities remain independently optional.
Fresh leaves require exact zero baselines for retained counters. After recursive quiescence, one
all-or-nothing capture retains page faults, major faults, reclaim scan/steal pages, swap-in/out pages,
swap high/max/fail events, local frozen microseconds, and IRQ `full` stall microseconds. Capability
counts distinguish unsupported interfaces from observed zero. No IRQ `some` class is fabricated, and
none of these completed-session totals is treated as causal attribution or adaptive policy input.

Under systemd this must come from a service or scope with `Delegate=` and one manager. rev0028 names
each leaf with the canonical boot ID, daemon PID, procfs field-22 start time, and local sequence. Before
the PTY factory or network service activates, startup pins every reserved leaf and owner process,
preserves exact live incarnations, and reclaims only identities proven stale. Recovery is bounded,
preflight-first, recursive through `cgroup.kill` plus `cgroup.events: populated 0`, and fail closed for
populated legacy PID-only leaves or malformed evidence.

The dedicated process oracles mount a fresh cgroup-v2 hierarchy in isolated user, mount, and
cgroup namespaces. Lifecycle recovery, memory/PID policy, and CPU policy are independent routes. On
a host that delegates the controller, the resource routes prove exact readback plus live PID rejection,
`memory.high` pressure, and CPU throttling before retaining one-shot teardown outcomes. A missing
preactivated controller is a named skip, not positive evidence. This is local-kernel evidence, not
fleet qualification.

Controller only:

```sh
iotox run \
  --state /absolute/device.toxsave \
  --runtime /absolute/private-runtime \
  --enable-ratox-terminal-client
```

Both roles may run in one Agent. Outside `--mode self`, neither role is enabled by upgrade or default
configuration.

## 7. M7 signed-update construction boundary

rev0045 retains rev0044's `signed-update-bundle-v1`: a canonical 320-byte Ed25519 manifest precedes one payload
that remains inert throughout delivery/staging and binds its digest, byte count, namespace, target,
sequence, version, kind, and release
signer. Owner-private policy pins the acceptable namespace, target, storage root, payload ceiling,
health timeout, and sorted release keys. Sync may deliver the artifact, but neither sync acceptance
nor ordinary activation grants update authority.

The default-off Agent stages only an independently reverified payload into an immutable mode-`0400`
inactive slot. Stable-device-signed state commits before the exact `current` symlink changes. Only a
later durable Agent incarnation may confirm the one-use health token; timeout, a second restart, or
an interrupted transition deterministically rolls back to the last confirmed slot. Invalid slots,
state, and tokens fail closed. Both state-first apply and pointer-first rollback crash windows are
recovered. The eight-slot hot store fails closed when full and never deletes rollback material.

Policy v2 records a positive signer-policy epoch and bounded revoked-signer set. Explicit release-
role identities are created no-clobber and cannot be loaded as device identities; reviewable policy
rotation uses an overlap epoch before retirement. Local `update-gc dry-run|quarantine` protects the
signed confirmed and live candidate slots and moves only historical payloads into a strict bounded
recovery directory. Partial moves resume safely, and no purge path exists.

Same-user controls expose signer create/show, policy template/lint/rotation, no-clobber bundle
creation, status, stage, apply, confirm, and recoverable slot quarantine. Remote durable
`update.stage` names only one exact accepted HEAD and requires bilateral
feature bit 20 plus current `install.firmware` authority. It inherits signed command replay, quotas,
restart recovery, pre-first-send cancellation, and audit. It cannot apply, restart, obtain a health
token, confirm, select a path, or execute bytes. Direct-UDP and forced-TCP Sandwurm cells qualify one
exact 4 MiB remote stage, local restart, health confirmation, and selected-slot digest between two
simultaneous guests. ADRs 0184–0186 and `docs/protocol-command-v1.md` freeze the boundary.

Policy v3 and signed kind 2 now name only `linux-service-v1`; v1/v2 remain byte-compatible opaque
policy. A matching, separately enabled Agent rehashes the selected mode-`0400` slot into a sealed
anonymous executable image, enters it through the exact parent-death/no-new-privileges IoTox helper,
and admits health only after `IOTOXSR1 || release-sequence-u64be` from the same live process.
Confirmation still requires the one-use local token. Candidate exec/readiness/exit failure signs
rollback and relaunches the prior confirmed service through the complete sealed path. Remote peers
still cannot apply, restart, select the helper, obtain the token, or confirm. ADR 0189 and
`docs/update-linux-service-v1.md` freeze this construction boundary.

## 8. M8 strict routed-privacy construction

`--network tox/tor` is now an explicit, non-default route. It requires exactly one numeric
`--socks5-proxy`, at least one explicit numeric bootstrap record, and at least one explicit numeric
TCP relay. Route selection itself suppresses the compiled native node catalogs and forces c-toxcore
UDP, local discovery, DHT announcements, hole punching, and native DNS off. Hostnames, missing
records, a SOCKS option under `tox/native`, and signed auxiliary members that require UDP all fail
before durable/runtime mutation. There is no native fallback.

c-toxcore 0.2.23 still needs `tox_bootstrap()` in TCP-only mode to install onion path nodes; with
UDP disabled that call does not execute its DHT datagram branch. The pinned SOCKS5 implementation
encodes relay destinations as numeric IPv4/IPv6 addresses, not proxy-resolved names. These source
facts are why numeric bootstrap and relay records are both required.

The source-linked local construction gate uses the pinned c-toxcore bootstrap/TCP-relay fixture and
an allowlisted numeric-only SOCKS5 forwarder. It observes `Tox/Tor` plus TCP self-connectivity, no
IoTox UDP socket, no direct IoTox-to-relay TCP socket, explicit offline state when SOCKS disappears,
and same-endpoint recovery. The forwarder is intentionally not Tor. The Sandwurm gate separately
proves two-IoTox application traffic and TAP containment through that generic boundary.

The opt-in operator gate then binds an actual Tor 0.4.8.11 daemon, its normalized loopback policy,
one current public numeric Tox relay, a successful stream on initial/recovered three-hop circuits,
Tor-owned public sockets, and IoTox-only loopback TCP with zero UDP/direct fallback across a held
outage. It uses explicit `SafeSocks 0` because c-toxcore sends numeric SOCKS destinations while IoTox
itself prohibits hostnames and native DNS. This is one host/relay/Tor/time route sample, not
anonymity. Accepted compact proof `pair.2mycvy9n` separately places two exact Tor auxiliaries on
distinct three-hop circuits and reaches private-v2 readiness in one converged sync topology.
Accepted compact proof `pair.lzsyitvy` then binds the complete signed-tree job to the exact Tor
member with zero reassignment and independently verified Tor/control plus TAP evidence. Accepted
compact proof `pair.iompvehf` additionally kills only that Tor process after positive object
progress and binds one loss, native reassignment, real carrier return, zero IoTox worker restarts,
and zero unexpected-context TAP packets. The repeated operator sample observes local refusal in
34 ms while the authoritative carrier remains TCP, then c-toxcore offline after 76.990 seconds.
Accepted compact proof `pair.2waqdpgk` closes the distinct ADR 0206 Ratox primary-route follow-on:
after initial PTY progress the host kills only client Tor, observes heartbeat warning before
authoritative offline, retains the detached device PTY, and explicitly resumes the same
session/incarnation after exact Tor restart. Three authenticated Tor phases, zero IoTox daemon
restarts, and TCP-only guest TAP containment independently reverify. Route identity separation, long-running
multi-relay/exit qualification, and I2P remain later gates.

`iotox route-health [FRIEND]` is a separate content-free observation. It preserves the exact
c-toxcore carrier label, optionally connects only to the configured local SOCKS listener, and may
add the already transcript-gated lossless peer echo. It never turns listener reachability into an
upstream claim and cannot advance a protocol session epoch. `route-health-watch [FRIEND]` strictly
parses repeated reports into independent process-local boundary/application latches with bounded
three-failure/two-recovery defaults. The terminal separately samples one byte-identical frozen-v1
Ratox PING identity per attachment; three missed one-second deadlines warn but cannot detach, resume,
relabel, or advance an epoch. Actual SOCKS-target/Tor-control observation and impaired-route recovery
policy remain open. `docs/networks.md` and ADRs 0190/0191/0192/0193/0194 freeze the exact claims.

`iotox route-target-health` adds one deliberate upstream sample for Tox/Tor. The Agent chooses only
the first numeric relay already frozen in its validated route, completes SOCKS5 CONNECT without
application bytes, and emits content-free stage/result evidence. It accepts no target and is not
part of the persistent watch. Success is one TCP admission—not a Tox handshake, circuit identity, or
anonymity claim (ADR 0194).

## 9. Nonclaims and next gates

rev0038 added one optional host-local admission gate over descriptor-pinned delegated-root PSI. Exact
integer basis-point maxima may be configured for CPU `some avg10`, memory `full avg10`, and I/O
`full avg10`, with one common hysteresis width. The controller is constructed under the signed host
lease before resource probes, orphan recovery, listener activation, or networking. It requires
`cgroup.pressure=1` before and after every complete configured sample and evaluates under one mutex
before aggregate reservation, cgroup creation, PTY creation, or helper spawn. Any read, parse, or
accounting failure returns local unavailability and latches closed; owner-private status preserves
last-sample validity, the bounded typed local cause, counters, and the previous complete valid values.
A valid high-pressure preflight is capability evidence rather than an activation failure; the first
real request applies policy. Sequential cross-resource reads are not atomic, and no threshold is
claimed generally safe.

rev0039 layers a continuous kernel-trigger tripwire onto that synchronous gate. Each configured PSI
resource owns one `O_RDWR|O_NONBLOCK` descriptor and one canonical NUL-terminated trigger record. A
dedicated monitor polls `POLLPRI`, transfers typed events through bounded atomics, latches admission
closed for at least one configured tracking window, and requires the complete rev0038 avg10
hysteresis sample before reopening. Monitor setup, poll, source-loss, or handoff failures fail closed;
owner-private status exposes health, hold time, typed failure, per-resource events, total failures,
and trigger-caused close transitions. The monitor is descriptor-pinned to the exact delegated root,
starts before orphan recovery or listener/network mutation, and shuts down through an `eventfd` wake
before any monitored descriptor closes. It does not preempt or kill an already admitted session.

rev0051 does not claim:

```text
live PTY or controller-state survival across daemon restart
rollback resistance against an equivalent owner or coordinated storage snapshot
complete snapshot freshness without a configured independently operated rollback witness
descriptor/mapping safety after final exchanged-old-tree validation or across remount/restart
power-cut durability qualification beyond the retained paired workspace and v4 object-pipeline whole-VMM cuts
remote update apply/restart/confirm or fleet rollout
bootloader or representative-hardware update integration
physical service-manager/cgroup, recovery-media, power-cut, flash-wear, secure-boot, or hardware-witness qualification
destructive slot collection
more than one simultaneous local terminal controller
public-network or two-physical-host Ratox qualification
Tor/I2P anonymity, censorship resistance, public routed-mode reliability, or long-running/diverse actual-Tor qualification beyond the retained bounded samples
production-default Ratox or a production security audit
filesystem read secrecy or an executable-path allowlist
mount, PID, user, network, or cgroup namespaces
aggregate I/O reservation, storage latency/queue-depth control, persistent PSI histories, adaptive threshold tuning, synchronized CPU periods, parent CPU enforcement, or fleet-wide resource sizing
protection from root or another same-UID writer violating delegation
authorization between arbitrary processes sharing one UID
starvation freedom against an unlimited coalition of hostile same-UID processes
preemption of a handler callback that blocks after admission
container, VM, or complete sandbox isolation
hardware remote attestation or truth of externally supplied physical metadata
```

The exact provider double does not prove bootstrap, NAT traversal, relay, or genuine-peer behavior.
The attested R7 chain binds schedule, raw same-clock samples, exact host coordinates, auxiliary files,
and two capture roles; it does not substitute for the physical-host experiment. The next terminal gate
is an ABI-10 host run of the strict enforcement branch plus target-specific compatibility inventories;
the next service gate remains the retained two-physical-host R7 matrix.

## 10. Build and evidence

```sh
cmake --preset gcc-debug
cmake --build --preset gcc-debug --parallel 2
ctest --preset gcc-debug --output-on-failure
./build/gcc-debug/iotox --version
```

The default suite has 62 CTest targets. The direct registry has 859 fixture-aware checks. Twelve
fuzzers cover frame, session, local control, terminal protocol, command, terminal profile, kernel
cgroup records, signed update bundles/policies, authority, Ratox frame, interactive state, and
interactive service.

Current evidence:

```text
artifacts/rev0045/
artifacts/rev0039/
artifacts/rev0038/
artifacts/rev0037/
artifacts/rev0035/
artifacts/rev0034/
artifacts/rev0033/
artifacts/reports/validation-summary.txt
docs/testing.md
docs/evidence/2026-08-27-operator-tor-public-route.md
docs/research/cloudtainer-build-report-rev0039.md
docs/research/linux-cgroup-psi-trigger-tripwire-rev0039.md
docs/research/cloudtainer-build-report-rev0038.md
docs/research/linux-cgroup-psi-admission-rev0038.md
docs/research/cloudtainer-build-report-rev0037.md
docs/research/memory-work-swap-irq-freeze-kernel-accounting-rev0037.md
docs/research/peak-resource-kernel-accounting-rev0036.md
docs/research/cloudtainer-build-report-rev0035.md
docs/research/pressure-stall-kernel-accounting-rev0035.md
docs/research/cloudtainer-build-report-rev0033.md
docs/research/io-bandwidth-kernel-accounting-rev0034.md
docs/research/memory-high-kernel-outcome-telemetry-rev0033.md
docs/research/cloudtainer-build-report-rev0032.md
docs/research/exact-rational-cpu-reservation-admission-rev0032.md
docs/research/cloudtainer-build-report-rev0031.md
docs/research/aggregate-cgroup-reservation-admission-rev0031.md
docs/research/cloudtainer-build-report-rev0030.md
docs/research/profile-scoped-cgroup-budget-ceilings-rev0030.md
docs/research/controller-enforced-cgroup-resource-budgets-rev0029.md
docs/research/cloudtainer-build-report-rev0028.md
docs/research/boot-bound-cgroup-orphan-recovery-rev0028.md
docs/research/cloudtainer-build-report-rev0027.md
docs/research/bounded-local-ipc-admission-rev0027.md
docs/research/process-pinned-local-ipc-lifetimes-rev0027.md
docs/research/cloudtainer-build-report-rev0026.md
docs/research/message-bound-local-ipc-hardening-rev0026.md
docs/research/delegated-cgroup-session-containment-rev0025.md
docs/research/terminal-process-domain-hardening-rev0024.md
docs/research/terminal-session-containment-rev0023.md
docs/research/ratox-r7-attested-evidence-chain-rev0022.md
docs/research/terminal-confinement-rev0022.md
docs/research/cloudtainer-build-report-rev0020.md
docs/research/ratox-restart-fence-rev0020.md
```

## 11. Governing decisions

```text
docs/decisions/0064-seal-local-terminal-profiles-behind-fork-safe-pty-adapter.md
docs/decisions/0065-gate-live-ratox-dispatch-before-network.md
docs/decisions/0066-separate-private-terminal-controller-stream.md
docs/decisions/0067-bound-local-controller-admission-and-contention.md
docs/decisions/0068-reserve-signed-ratox-host-incarnation-before-network.md
docs/decisions/0069-measure-queue-tails-and-typed-ratox-send-outcomes.md
docs/decisions/0070-qualify-ratox-r7-with-bounded-fail-closed-evidence.md
docs/decisions/0071-bind-ratox-r7-to-attested-raw-evidence.md
docs/decisions/0072-seal-terminal-capabilities-and-add-tiered-kernel-confinement.md
docs/decisions/0073-fence-terminal-lifecycle-and-contain-pty-sessions.md
docs/decisions/0074-pin-session-identities-and-seal-terminal-process-domain.md
docs/decisions/0075-own-hardened-pty-lifecycles-with-delegated-cgroup-v2.md
docs/decisions/0076-bind-local-seqpacket-records-to-kernel-sender-evidence.md
docs/decisions/0077-bound-and-multiplex-local-seqpacket-admission.md
docs/decisions/0078-pin-local-seqpacket-connections-to-peer-process-lifetimes.md
docs/decisions/0079-bind-delegated-cgroup-lifecycles-to-boot-and-process-incarnations.md
docs/decisions/0080-enforce-global-pty-resource-budgets-in-delegated-cgroups.md
docs/decisions/0081-compose-profile-cgroup-budgets-under-host-ceilings.md
docs/decisions/0082-admit-pty-sessions-under-exact-aggregate-cgroup-reservations.md
docs/decisions/0083-admit-exact-rational-aggregate-cpu-bandwidth.md
docs/decisions/0084-add-memory-throttle-and-retain-kernel-session-outcomes.md
docs/decisions/0085-add-device-io-ceilings-and-retain-kernel-io-accounting.md
docs/decisions/0086-retain-cgroup-pressure-stall-outcomes.md
docs/decisions/0087-retain-cgroup-lifetime-peaks-and-complete-cpu-work.md
docs/decisions/0088-retain-memory-work-swap-freeze-and-irq-outcomes.md
docs/decisions/0089-admit-new-pty-sessions-with-cgroup-psi-hysteresis.md
docs/decisions/0090-latch-ratox-admission-with-continuous-cgroup-psi-triggers.md
docs/decisions/0183-freeze-application-restart-and-qualify-route-throughput.md
docs/decisions/0184-separate-update-intent-from-sync-delivery.md
docs/decisions/0185-qualify-the-signed-update-slot-lifecycle.md
docs/decisions/0186-authorize-remote-update-staging-through-durable-commands.md
docs/decisions/0187-freeze-release-signer-revocation-policy.md
docs/decisions/0188-operate-release-keys-and-quarantine-update-slots.md
docs/decisions/0189-freeze-linux-service-deployment-adapter.md
docs/decisions/0190-freeze-strict-tox-tor-route.md
docs/decisions/0191-qualify-operator-tor-public-route.md
docs/decisions/0192-separate-auxiliary-route-health.md
docs/decisions/0193-bound-persistent-route-and-ratox-heartbeats.md
docs/decisions/0194-probe-only-the-configured-socks-target.md
docs/ratox-r7-evidence-v2.md
docs/protocol-signed-update-bundle-v1.md
docs/update-linux-service-v1.md
docs/protocol-ratox-v1.md
docs/terminal-profile-v4.md
docs/terminal-profile-v5.md
docs/terminal-profile-v6.md
docs/terminal-profile-v3.md
docs/terminal-profile-v1.md
docs/terminal-client-v1.md
docs/security-ratox-v1.md
docs/ratox-ssh-status.md
docs/self-mode.md
docs/ratox-rescue-toolbox.md
docs/research/sources.md
```

Historical revision reports describe their own commits and must not be silently rewritten.

## 11.5. Everyday synchronization and bounded shared history

rev0051 retains the immutable one-writer synchronization and signed update delivery lines, and adds
an ordinary bounded read-write directory surface. Every node chooses its own absolute worktree,
creates the same `tree-v2` namespace with `sync-create ... read-write`, and runs a bilateral
RecallRoot-bound `sync-share ... read-write` for every other writer. Tox friendship is not authority:
each share binds the current application transcript to one stable device principal and grants only
the exact sync capabilities and namespace memberships.

Per-file CAS, independent signed writer branches, causal observations, tombstones, deterministic
projection, and provenance-bearing conflict files preserve concurrent offline values. Signed
workspace state distinguishes received data from what the user actually saw. A full mesh may contain
at most 16 writers and 16 candidates per path; local automation stores at most 15 remote stable
principals with independent retry clocks.

ADR 0275 bounds lifecycle without adding destructive purge. Negotiated format-2 checkpoints are
conflict-free authenticated history floors. Exact-record pins, signed workspace roots, and current
branches guard recoverable GC. `sync-gc ... quarantine` only moves authenticated unreachable objects
into private quarantine and `sync-restore` reauthenticates them. A terminal writer cutoff must be
applied independently on every survivor and does not replace general authority revocation. Quiet
remote convergence does not author acknowledgement-only branches.

The accepted claim is same-computer Sandwurm/KVM construction plus owned deterministic evidence.
The accelerated 24-cycle lifecycle cell also proves remote checkpoint propagation, recoverable
quarantine/restore, matching cutoff on both survivors, and refused retired-writer re-entry; see
`docs/evidence/2026-09-01-sandwurm-sync-three-writer-lifecycle.md`. A preceding constrained cell's
intermittent pending exchange remains an explicit availability observation, with bounded harness
watchdog/restart recovery wired but not exercised by the accepted retry.
ADRs 0278 and 0280--0281 close the local selective-sync, private owner-mode, named crash/fork/
conflict, 16-candidate, and 4,096-file gates. ADRs 0282--0283 repair the finite publisher-session
defect exposed by the incumbent campaign and accept a 240-cycle, 7,200,096-ms networkless IoTox/
Resilio shadow with twelve alternating Agent restarts and 356 replay-window evictions. This closes
the founding-machine roadmap. Physical power cuts, dishonest storage, case-folding, symlinks, rich
metadata, tree-v2 range/auxiliary/parallel transfer, encryption at rest, and permanent purge remain unsupported. Sync is
not backup; important data must retain an independent copy. ADR 0284 and
`docs/sync-trust-graduation.md` freeze the operator checklist and the engineering gates required
before a precious-data recommendation.

ADR 0294 adds bounded retained-history inventory, provenance-aware diff/conflict inspection, and an
exact-token forward restore that authors only a higher local generation. ADR 0295 adds the first
sparse-custody vertical slice: recipient-local prefix rules keep the full signed metadata graph while
selected-only transfer, repair, GC, and pull status report partial custody. The policy-bound
projection marker makes on-demand widening preserve formerly unprojected absence until selected bytes
arrive. A sparse node and its pins are not a complete backup. ADR 0296 closes the immediately
following source-availability correctness gate.

ADR 0296 closes that correctness gate without reopening peer framing. One primary source freezes the
signed frontier; the existing exact object result serves as authenticated availability evidence, and
bounded complementary primary-lane sources can satisfy a missing immutable digest. This is serial
recovery, not range/auxiliary striping, and it still does not turn sparse custody into backup.

ADRs 0329--0331 add bounded exact-object lanes, batch their completed file commits, and cache one
strictly verified CAS inventory for the lifetime of each pull. The cache never becomes durable
truth: the complete store is digest- and quota-revalidated under the final branch/projection
transaction, with cached mutation refused and independently verified additive objects permitted.
Status and capacity receipts expose batch and full-scan counts. Peer framing and signed tree-v2
semantics are unchanged.

ADR 0332 adds one real two-boot Sandwurm storage slice without widening that product protocol. The
host kills the exact task-owned Cloud Hypervisor process after the corrected v2 observer binds raw
workspace phase byte 2 (`pending-exchange`); a second kernel boots a reflink of the crash disk,
admits only exact prior or completed projections before Agent restart, preserves node identities,
then converges and repairs all writers. The phase-reversed v1 predecessor is withdrawn and rejected.
This is one virtual workspace-exchange linearization, not the complete cut matrix, physical or
dishonest storage, backup independence, or precious-data approval.

ADR 0333 closes the paired post-exchange linearization. The accepted cut observes pending byte 2
while the visible marker names the pending manifest and the old active projection remains staged;
after reboot all three views are completed and that journal/marker/stage tuple recovers exactly.
Together the two runs cover both workspace directory-exchange sides, not other transaction families.

ADR 0334 closes two earlier object-pipeline cuts. Source-linked v4 run `1e05ayp9` freezes the Agent
at the real generic receive temporary and run `jtiyspp_` freezes it at the CAS install temporary;
the host then kills only the exact task-owned VMM. Both crash disks reboot under a second kernel,
admit `[completed, completed, prior]` before recovery, leave no temporary after startup, install the
exact 32-MiB object, preserve identities, converge three writers, and pass repair. The independently
verified compact proofs remain under `.sandwurm/exports/sync-power-cut/`. Metadata-publication
qualification, record corruption, dishonest storage, physical power, and independent backup remain
open at that v4 boundary.

ADR 0335 constructs the next semantic layer without changing the tree-v2 wire or signed bytes.
Proof v5 independently binds the fully written manifest temporary, immutable branch-record
temporary, and mutable branch-pointer temporary before their rename syscalls enter the kernel. An
external qualification-only ptrace delay identifies the exact stopped sync worker; a process-group
fence stops every Agent thread before the host kills the exact VMM. Offline inspection requires the
corresponding absent/absent/prior, exact/absent/prior, or exact/exact/prior metadata prefix and permits
only an absent-or-exact selected temporary. All three source-linked campaigns
pass. ADR 0336 also closes the three post-rename/pre-directory-fsync sides
with strict proof-v6 old-or-new directory outcomes.

ADR 0337 makes present byte-invalid signed tree-v2 metadata fail closed. Agent
startup and `sync-repair` authenticate current pointer, exact immutable
record and manifest, workspace, and maintenance state before effects or a
verified result. Neither path rewrites, quarantines, or treats corrupt signed
bytes as absent. Recovery requires externally supplied byte-exact originals.
The dedicated networkless KVM/ext4 construction flips one last bit in each
family, requires live protocol-error and cold-start refusal with exact byte
retention, restores the original with file and parent barriers, then demands
identity/worktree preservation and three-writer convergence. Source-linked
run `mixJ9VUp` passes all five cells in 26.429 seconds from commit `08e4179`;
its strict content-free proof is
`.sandwurm/exports/sync-metadata-corruption/run.mixJ9VUp`. See
`docs/evidence/2026-09-08-sync-tree-v2-metadata-corruption.md`. This is not
automatic recovery, valid-old rollback detection, backup provenance, physical
power, or dishonest-storage evidence.

ADR 0338 closes a narrower writable-projection loss window. After the real
directory exchange IoTox validates the obsolete staged projection as well as
the visible target, including an exact bidirectional preserved-unselected
closure. Deterministic seams cover held descriptor writes both after the final
source scan and after exchange but before validation; either leaves the stage
and signed pending workspace for operator recovery instead of being discarded.
Current or explicitly authenticated-prior
projection markers are required for an established worktree; marker mismatch
cannot hide a selected deletion. This is bounded detection, not general
descriptor safety: a write after final old-tree validation starts, writable
mappings, hostile same-UID writers, and markerless legacy recovery remain
open.

ADR 0339 separates integrity from freshness. `sync-repair` renders
`rollback-witness=0|1`, and direct tests retain valid-old branch, workspace,
and maintenance records with matching old local guards while a current
external witness refuses live and cold replay unchanged. Its receipt-v2
Sandwurm construction stops every Agent task, writes all five corrupt
metadata roots sequentially while they are co-resident, resumes once, then
requires first-error repair refusal, ordered cold-start peeling, exact
restoration, and convergence. The code, rehearsal, strict verifier, and
backward v1 replay are checked. Source-linked KVM/ext4 run `MG27auOK` at
commit `2be7a2a` qualifies v2 and retains strict compact proof
`.sandwurm/exports/sync-metadata-corruption/run.MG27auOK`. The accepted
`mixJ9VUp` compact proof is rev0050/v1 historical single-family evidence and
must not be misrepresented as v2 qualification.

ADR 0297 turns those local truths into a fixed signed health record. `sync-health` refreshes exact
selected coverage, frontier/workspace convergence, worktree cleanliness, conflicts, cutoffs,
automation failure streaks, active-store headroom, and last source exhaustion, or verifies the
cached restart-surviving observation. Sparse selected custody can be green while still saying
partial. The record is tamper evident but has no rollback witness and never certifies a backup.

ADR 0298 joins those records to the content-free support bundle only after locally verifying them.
Redacted diagnostics v2 exposes anonymous health/custody/fault totals and explicitly counts absent or
invalid records; it exports no namespace name, path, commitment, key, content digest, or stable slot.
The outer bundle remains an inspectable integrity wrapper, not authorship, attestation, a rollback
witness, or backup proof.

ADR 0299 adds the other closed diagnostics join. The explicit administrator probe still live-tests
pidfd/seccomp/MDWE/Landlock and reports local sudo/cgroup detail; the running Agent reuses it in
passive/no-fork mode and exports only normalized grades, masks, and counts. Paths, raw controller
text, kernel text, and environment remain absent, and an availability grade is not child-confinement
or sudo-policy evidence.

The owner-local Ratox surface now also has a self-machine product entrance: `--mode self` makes the
host dispatcher and same-user controller default-on for owned machines while preserving the same
profile, binding, authority, and sudo gates. ADR 0383 adds the native self-swarm roster:
`iotox self-swarm` creates, joins, retires, inspects, verifies, plans, grants, and revokes
owner-signed self-machine membership without making Tox friendship authoritative. The Ratox surface
authors and binds canonical profiles, lists/closes the one retained controller session, supports
batch attachment, probes live host capabilities, and generates real non-root account shells. Profile
v6 freezes supplementary groups and denies privilege gain by default; a separate `--allow-sudo`
compatibility profile delegates elevation only to host policy (ADRs 0285--0286). ADR 0287 adds a
separately built optional static rescue payload: oksh 7.9 plus
Toybox 0.8.14, with Toybox's pending shell excluded. The explicit disabled rescue profile is
baseline/non-root and toolbox-first; the VM gate crosses that exact payload through the production
PTY with no host tools in PATH. It is prepared fallback, not automatic failover or a second product
binary. See `docs/ratox-ssh-status.md`, `docs/self-mode.md`, and
`docs/ratox-rescue-toolbox.md`.

## 12. Packaging contract

Build the repository datacube only from a clean committed tree:

```sh
IOTOX_DATACUBE_TIMESTAMP="$(TZ=America/New_York date +%Y.%m.%d.%H.%M.%S)" \
  ./tools/make-repository-datacube.sh /mnt/data
```

The linked outer revision is `rev0026`:

```text
IoTox-rev0026-YYYY.MM.DD.HH.MM-strict-routed-privacy-boundary.zip
```

The archive must remain below 128,000,000 bytes, contain one safe top-level directory, no symlink
entries, a complete Git bundle, exact SHA-256 metadata, and `repository/REVISION` equal to `rev0051`.
The renamed linked archive must be verified again.

## 13. Handoff truth

```text
version/revision:       0.51.0 / rev0051
codename:               Freshness-Explicit Projection Recovery
toxcore target:         0.2.23
outer linked revision:  rev0026
owned registry:         859 checks
default CTest surface:  62 targets
fuzz topology:          12 targets
self activation:        --mode self
manual host activation: --enable-ratox-terminal
manual controller:      --enable-ratox-terminal-client
local endpoint:         <runtime>/terminal.sock
membership roster:      iotox self-swarm v1
profile encoder:        iotox-terminal-profile-v7
profile default:        baseline
strict minimum:         MDWE plus Landlock ABI 10
cgroup activation:      --ratox-cgroup-root (optional, explicit delegation)
next construction:      compacted 24-hour proof, independent backup custody, then lying-storage cuts
```

The supported claim is narrow: rev0051 preserves the authenticated, authorized, replay-bounded
host/controller, signed restart fence, attested R7 evidence chain, argument-aware baseline seccomp,
strict mutation/network/IPC profile, descriptor closure, procfs identity pinning, and payload/host
process-handle reductions. It now also binds each local request and response to kernel sender
credentials, optionally pidfds, and terminal process lifetime while rejecting ancillary capability
injection. It also multiplexes bounded local administrative admissions and terminal contenders with
independent leases, per-process/global quotas, finite accept/refill and record-work budgets, and
active-stream-first terminal service. With an explicit valid delegation it additionally owns one cgroup-v2 leaf
per hardened PTY, attaches before manifest release, uses kernel subtree KILL, requires recursive empty
state, and removes the exact leaf before reap. It now also recovers crash-abandoned versioned leaves
only after boot/process-incarnation proof, while populated PID-only legacy leaves stop startup rather
than authorize a reuse-unsafe kill. rev0030 additionally carries local profile-specific pids, memory,
swap, and CPU budgets in canonical v3 records, composes them monotonically beneath the host ceiling,
preflights each distinct identity/effective-budget pair, and recomputes the result at production
spawn. rev0032 additionally reserves the configured process, memory, swap, and exactly normalized CPU
bandwidth maxima atomically across live production PTYs, rejects capacity or nonrepresentable ratios
before mutation, rolls back every proved-cleanup partial spawn, retains the complete charge through
complete teardown, and strands rather than releases it when post-spawn teardown cannot prove both reap
and exact leaf removal. It publishes owner-private current/peak/rejection/stranding evidence together
with the aggregate CPU accounting period. rev0033 additionally carries a monotone soft memory
throttle in canonical v4 profiles, verifies exact `memory.high` readback, and retains bounded local
kernel outcome counters after proved teardown. rev0034 carries same-device monotone BPS/IOPS policy in
canonical v5, semantically verifies `io.max`, and retains bounded `io.stat` totals while distinguishing
incomplete observations. rev0035 additionally retains bounded absolute CPU, memory, and I/O PSI
microseconds with explicit capability counts after proved quiescence, while leaving profile v5 and
admission policy unchanged. rev0036 additionally retains zero-baseline PID, memory, and swap lifetime peaks
plus quota-independent usage/user/system CPU work and complete optional bandwidth/burst tuples, with
explicit capability counts and saturation-safe private projection. rev0037 additionally retains
bounded memory-work, swap-event, local-freeze, and IRQ-full pressure outcomes through protected
pre-attachment descriptors and one post-quiescence all-or-nothing capture, while preserving explicit
unsupported-versus-zero capability evidence. rev0038 additionally constructs a descriptor-pinned PSI
admission controller before recovery/network mutation and applies exact hysteresis before aggregate or
spawn mutation, with fail-closed local-unavailable responses and typed content-free private evidence.
rev0039 additionally owns one dedicated kernel PSI trigger descriptor per configured metric, polls
continuous trigger events in a bounded monitor, atomically latches admission closed through at least
one tracking window, requires the complete avg10 hysteresis sample before reopening, fails closed on
monitor/source failure, and publishes typed content-free event, health, hold, and failure evidence.
rev0040 additionally separates signed release intent from immutable sync delivery, stages only
reverified inert bytes, signs the durable device lifecycle, fences confirmation to a later Agent
incarnation, and deterministically rolls incomplete or unhealthy candidates back. rev0041 adds one
exact-HEAD, `install.firmware`-authorized remote staging operation through the existing signed durable
command journal while keeping apply, restart, health confirmation, and execution local.
Without explicit delegation it preserves rev0024 supervision and rejects
every effective resource budget or aggregate reservation policy.
It is not a production remote shell, restart-persistent PTY service, read-secret sandbox,
hardware-attestation system, public-network qualification, namespace container, resource accountant,
defense against a privileged competing writer, or proof against every future
kernel escape interface.
