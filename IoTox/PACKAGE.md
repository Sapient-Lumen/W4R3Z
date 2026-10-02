# IoTox repository package contract

Status: current clean-tree repository-datacube contract. Updated 2026-10-01.

**Source revision:** rev0051
**Version:** 0.51.0
**Codename:** Freshness-Explicit Projection Recovery
**Ordinary release channel:** founder-preview unless a stable evidence manifest
passes the explicit stable gate.

## Current seed archive name

```text
IoTox-seed-repository-datacube-YYYY.MM.DD.HH.MM.SS-COMMIT.zip
```

The timestamp is America/New_York local time and `COMMIT` is the represented
clean source commit prefix. The seed ZIP expands to exactly one
commit-addressed top-level directory containing `CHATGPT_START_HERE.md`,
checksums and file index, the exact tracked repository, a cloneable Git bundle
with one exact source-snapshot commit, available same-commit standalone
distribution, and selected validation evidence. It omits local history and
nested founding cubes by default so the artifact is small enough and clean
enough for public/GitHub review.

Build and verify from a clean committed tree:

```sh
tools/iotox-repo.sh release-plan founder-preview
tools/iotox-repo.sh release-check founder-preview --iotox /path/to/iotox
tools/iotox-repo.sh datacube --seed
tools/make-repository-datacube.sh --verify \
  DR0Pbox/IoTox-seed-repository-datacube-YYYY.MM.DD.HH.MM.SS-COMMIT.zip
sha256sum -c \
  DR0Pbox/IoTox-seed-repository-datacube-YYYY.MM.DD.HH.MM.SS-COMMIT.zip.sha256
```

Use `tools/iotox-repo.sh datacube --public` only when a reviewer specifically
wants the public profile's automatic history behavior. Use the seed profile for
the first official public repository seed.

Use `tools/iotox-repo.sh datacube --conversation` only when the recipient needs
the richer internal conversation/recovery handoff. That profile may admit
unchanged founding cubes under the same strict 128,000,000-byte ceiling.
Historical `IoTox-rev####-...zip` handoff names count delivered conversation
snapshots; they are provenance, not the default public package contract.

## Full upload archive name

```text
IoTox-upload-repository-datacube-YYYY.MM.DD.HH.MM.SS-COMMIT.zip
```

Use this profile when the ZIP itself should be the full repository handoff to
carry private provenance elsewhere. It is not the recommended first public
GitHub seed. It keeps the same clean-tree, checksum, verifier, unsafe-path,
symlink, and secret-scan rules as the seed/public profiles, but it defaults to:

- full reachable Git history in `git/IoTox.bundle`;
- no default ZIP size ceiling;
- no nested founding cubes unless explicitly requested.

Build it with:

```sh
tools/iotox-repo.sh release-check founder-preview --iotox /path/to/iotox
tools/iotox-repo.sh datacube --upload
tools/make-repository-datacube.sh --verify \
  DR0Pbox/IoTox-upload-repository-datacube-YYYY.MM.DD.HH.MM.SS-COMMIT.zip
```

## Included construction

The tracked flake also defines an optional `iotox-rescue-toolbox` deployment payload: separately
pinned static oksh 7.9 and Toybox 0.8.14 plus their notices and provenance. It is not linked into the
one IoTox product executable, not counted in the product source SBOM, and not embedded in the
repository datacube unless a future package contract explicitly adds the built closure. ADR 0287 and
`docs/ratox-rescue-toolbox.md` own that distinction.

The source retains rev0031's exact process/memory/swap reservation ledger, rev0030 profile-scoped
cgroup budgets, rev0029 controller-enforced per-session resource policy, rev0028 boot/process-
incarnation recovery, process-pinned local IPC, Ratox replay/authority/session fencing, capability
sealing, argument-aware baseline seccomp, and strict MDWE/Landlock construction.

rev0032 added an optional administrator-owned aggregate CPU bandwidth ceiling above every effective
per-session `cpu.max` policy. The aggregate ceiling is one exact quota/period ratio; an omitted period
selects 100,000 microseconds. Every enabled profile must carry a finite effective CPU quota, fit once
on an idle ledger, and map to an integral quota at the selected accounting period. Comparison uses
continued-fraction arithmetic and normalization divides by the period GCD before checked
multiplication. No floating point, overflowing cross-product, or hidden floor/ceiling/nearest rounding
is accepted.

The production POSIX factory resolves process, memory, swap, and CPU into one canonical charge and
atomically claims the whole vector before helper-path validation, filesystem opening, PTY/socket
creation, cgroup-leaf creation, or process spawn. Concurrent claims serialize under one overflow-safe
ledger. A move-only RAII token releases a pre-spawn or proved-cleanup failure exactly once and remains
owned by a successful PTY through recursive descendant death, cgroup quiescence and exact removal,
and leader reap. If post-spawn cleanup cannot prove both leader reap and exact leaf removal, the token
strands its complete charge so later admission remains conservatively fail closed until restart
recovery. Capacity exhaustion is returned as typed `resource_exhausted`; malformed, missing,
oversized, or nonrepresentable policy is `invalid_argument`.

Owner-private runtime status records configured dimensions and maxima, the CPU accounting period,
current and peak active reservations, current and peak process/memory/swap/normalized-CPU totals, a
saturating capacity-rejection count, and a saturating stranded-reservation count. It contains no
profile IDs, payload identities, commands, paths, or terminal bytes.

The package includes semantic policy validation, a bounded exact-rational lattice checked against an
independent integer oracle, atomic accounting, move-only rollback, fail-closed stranded-charge tests,
deterministic concurrent process/CPU saturation, Agent pre-network rejection tests, production-
factory reservation-before-mutation and rollback evidence, CLI validation, runtime rendering checks,
and the existing real-kernel cgroup lifecycle/recovery and resource-controller process oracles.
Qualification records preserve named skips rather than fabricating positive controller evidence.

rev0033 adds canonical profile v4 with an optional page-aligned `memory.high` throttle composed
monotonically beneath host policy and clamped under the effective hard maximum. It retains bounded,
content-free local PID and memory event counters plus CPU usage/throttle counters after proved
recursive quiescence and before exact leaf removal. Unknown future keys are tolerated, duplicate or
noncanonical values fail closed, unavailable telemetry is counted as incomplete, and aggregate totals
saturate rather than wrap. The build also locks CMake, `REVISION`, and executable identity together.

rev0034 adds canonical profile v5 with one exact numeric block-device identity and independent
read/write BPS and IOPS ceilings. Host and profile layers must name the same device and compose each
rate by monotone minimum. Startup probes and production leaves activate the delegated `io` controller,
write one complete `io.max` line, and require semantic unordered readback before helper attachment.
Protected `io.stat` begins at a proved zero baseline and contributes saturating read/write/discard
bytes and operation totals after recursive quiescence and before exact removal. The totals remain
content-free and unlabeled; the device identity is not published.

rev0035 adds protected optional `cpu.pressure`, `memory.pressure`, and `io.pressure` interfaces for
every delegated session leaf, independent of configured resource ceilings. A present
`cgroup.pressure` control must report accounting enabled. The bounded parser validates canonical
`some` fields, optional `full`, rolling percentages, keyed uniqueness, termination, and size while
retaining only absolute cumulative microseconds. Fresh leaves require zero observed totals; final
values are captured after recursive quiescence and before exact removal. CPU, memory, and I/O
`some`/`full` totals aggregate independently with saturating arithmetic and explicit capability counts.
A failed PSI or controller observation marks the whole one-shot outcome incomplete and contributes no
partial totals. Profile v5 and the Ratox wire remain unchanged.

rev0036 adds protected independently optional `pids.peak`, `memory.peak`, and `memory.swap.peak`
descriptors, exact fresh-leaf zero validation, and post-quiescence lifetime high-water marks. It also
attempts `cpu.stat` for sessions without configured CPU quota, retaining mandatory usage/user/system
work and complete optional bandwidth and burst tuples. Private aggregates add explicit capability
counts, saturation-safe peak sums/maxima, and CPU work/throttle/burst totals. The outcomes remain
content-free observations rather than simultaneous capacity, working-set, or adaptive-policy claims.

rev0037 adds protected pre-attachment `memory.stat`, `memory.swap.events`,
`cgroup.stat.local`, and `irq.pressure` evidence. It requires exact zero baselines and retains final
page faults, major faults, complete optional scan/reclaim and swap-in/out tuples, swap high/max/fail
events, freezer microseconds, and current-kernel IRQ `full` microseconds only after recursive
quiescence and before exact removal. Interface and tuple capability counts remain explicit; every
counter saturates; a single protected read or parse failure suppresses the entire session outcome.
The construction host positively qualifies page-fault and freezer evidence where supported but does
not expose `irq.pressure`, so no positive live IRQ result is claimed.

rev0038 adds a default-off host-local pressure-admission controller over the exact delegated root.
It accepts independent CPU `some avg10`, memory `full avg10`, and I/O `full avg10` maxima as canonical
integer basis points plus one common hysteresis width. The complete PSI parser retains exact rolling
values without floating point while preserving rev0035 cumulative outcome semantics. A gate closes
only above a maximum and reopens only when every enabled metric is at or below
`maximum-hysteresis`. Read, parse, capability, or `cgroup.pressure` accounting failure rejects and
latches closed until a later complete valid sample satisfies every reopen boundary.

The production factory verifies cgroup-v2 identity and daemon ownership, pins the root and configured
PSI controls, checks `cgroup.pressure=1` before and after configured reads, and preflights one complete
sample under the signed host lease before resource-policy probes, orphan recovery, or Agent
listener/network exposure. Every live
pressure sample occurs under one mutex before aggregate reservation, cgroup/PTY/helper creation, or
other spawn mutation. Private runtime status exposes only configuration flags, exact thresholds, latch
state, saturation-safe admission/failure/transition counts, last-sample validity and typed local error
class, and the last valid configured observations.
Profiles and the Ratox wire remain unchanged. The direct registry contains 356 checks and the default
CTest surface contains nineteen routes, including a dedicated real-kernel PSI route. This construction
host lacks per-cgroup PSI, so that route records a named capability skip and no positive kernel
pressure-admission result is claimed.

rev0039 layers continuous kernel PSI trigger notification onto that synchronous gate. Each enabled
CPU `some`, memory `full`, or I/O `full` trigger owns a distinct descriptor and canonical
NUL-terminated `<some|full> <stall_us> <window_us>` record. One bounded monitor polls `POLLPRI`,
atomically publishes typed events, closes admission for at least one configured tracking window, and
requires the complete rev0038 avg10 hysteresis sample before reopening. Setup, poll, source-loss, and
event-handoff failures permanently fail closed for that controller. `eventfd` provides bounded
shutdown before trigger descriptors close. Owner-private runtime status adds monitor health, active
hold and remaining time, typed failure, total/per-resource events, monitor failures,
trigger-caused close transitions, and hold-specific rejections without exposing terminal or peer
content. Trigger windows are portable 2,000,000-microsecond quanta in 2..10 seconds, and the exact
NUL-terminated record is produced by a typed directly tested encoder. Profiles and the Ratox wire
remain unchanged. The direct registry contains 359 checks. This construction host can compile
and exercise the policy/state/runtime surface but lacks per-cgroup `cgroup.pressure`, so live trigger
registration remains an explicit capability skip rather than positive event-delivery evidence.

rev0043 separates release intent from synchronization delivery. One canonical release-signed
manifest binds an inert payload, while owner-private policy pins acceptable release keys and local
limits. Staging requires an accepted sync HEAD but independently verifies the release signature and
payload before copying it into a mode-`0400` inactive slot. Stable-device-signed lifecycle state
commits before the exact current pointer changes; only a later Agent incarnation may confirm health.
Expiry, a second restart, or either interrupted pointer/state ordering rolls back to the last
confirmed release; invalid slot/state/token evidence fails closed. The bounded eight-slot hot store
never silently deletes rollback material. Policy v2 adds a positive signer-policy epoch plus bounded
revoked release keys, rejecting future bundles from retired signers without changing the bundle
manifest or retroactively reinterpreting staged/confirmed state. No-clobber signer creation/public
inspection and canonical policy-rotation output define the owner-local overlap/retirement ceremony.
Explicit dry-run/recoverable quarantine protects signed confirmed/candidate slots, bounds retained
custody to 256 files, resumes partial moves, and adds no purge path.

rev0045 retains rev0044's policy-v3 kind binding and default-off `linux-service-v1` consumer. It rehashes one
selected mode-`0400` slot into a sealed anonymous image, executes only that descriptor through the
exact no-new-privileges parent-death IoTox helper, and requires a sequence-bound readiness record
before local confirmation. Candidate exec/readiness/exit failure signs rollback and relaunches the
prior confirmed service. Historical opaque policy/state remain inert and byte-compatible. Physical
service-manager/cgroup, recovery-media, power-cut, wear, secure-boot, and hardware-witness gates stay
explicitly open.

rev0045 additionally construction-enables `Tox/Tor` behind one explicit numeric SOCKS5 endpoint.
The route forces TCP-only c-toxcore, disables local discovery, DHT announcements, hole punching,
UDP, native DNS, and compiled native node catalogs, and accepts only explicit numeric bootstrap and
TCP-relay records. Source-linked loopback qualification proves SOCKS-only connection, route loss,
and same-endpoint recovery. Its allowlisted forwarder is lab plumbing, not Tor. A separate retained
operator gate binds an exact Tor 0.4.8.11 build/configuration, one public numeric Tox relay, initial
and recovered three-hop circuits, Tor-owned public sockets, and no IoTox UDP/direct fallback across
a held outage. A separate accepted Sandwurm proof binds two independently keyed Tor auxiliaries to
distinct three-hop circuits and private-v2 readiness in a two-IoTox sync topology. A second accepted
proof binds the complete signed-tree job to the exact Tor member with zero reassignment and strict
Tor/control plus TAP containment. A third accepted proof kills only that Tor process after positive
object progress and binds one loss, native reassignment, real carrier return, and zero IoTox worker
restarts. These package bounded route claims, not anonymity, public reliability, or long-duration/
multi-relay behavior. Accepted compact proof `pair.2waqdpgk` separately binds an actual-Tor Ratox
process loss to heartbeat-before-offline behavior, one detached host PTY, explicit exact-session
generation-2 resume after Tor returns, zero IoTox daemon restarts, three authenticated Tor phases,
and TCP-only guest TAP containment (ADR 0206). The content-free
`route-health [FRIEND]` read keeps exact
carrier truth, local SOCKS-listener reachability, and optional confirmed-peer response separate; it
does not package an upstream monitor or automatic recovery policy. `route-health-watch [FRIEND]`
adds strict report parsing and independent bounded process-local boundary/application latches. The
separate terminal heartbeat reuses one exact frozen-v1 Ratox PING identity per attachment and warns
after three one-second misses without detaching or changing carrier/session truth (ADR 0193). The
retained operator sample measures local refusal after 35 ms and provider offline after 74.602
seconds without collapsing those states. The same receipt now binds exact configured-target
success to authenticated Tor-control circuit evidence. Persistent/fleet target monitoring and
impaired-route terminal policy remain open.

Explicit `route-target-health` adds one complete SOCKS5 CONNECT only to the first numeric relay in
the already validated Tox/Tor route. The request carries no endpoint, the result exposes only
content-free stage/health/RTT/reply evidence, and the high-rate watch never calls it. The
whole-binary strict-forwarder gate separates target success, target refusal, and proxy refusal while
carrier truth remains TCP. This is configured-target reachability, not a Tox handshake or anonymity
claim. The distinct operator gate binds it to one Tor circuit only when authenticated control and
process/socket evidence agree (ADRs 0194/0195).

The package includes canonical bundle/policy and lifecycle tests, abrupt/interrupted process cases,
a real-Agent publication-to-rollback fixture, a dedicated hostile-input fuzzer, and compact verified
two-guest Sandwurm evidence over direct UDP (`pair.pwpgv4si`) and forced TCP (`pair.rntpawny`). The
service cells prove process/Agent interruption and confirmed recovery inside VMs, not abrupt VMM or
host power loss; exact bindings are in
`docs/evidence/2026-08-27-sandwurm-linux-service-update.md`. Feature bit 20 exposes only
authority-gated exact-HEAD remote staging through the signed command journal. Remote
apply/restart/confirm, bootloader or physical power-cut qualification, hardware anti-rollback, and
production OTA remain unclaimed.

rev0051 packages the ordinary synchronization surface through bounded full-mesh `tree-v2` and its
recoverable lifecycle. Every writer chooses its own path and receives authority only through a
bilateral RecallRoot ceremony. Per-file CAS, signed branches, visible-frontier workspace journals,
causal tombstones, and provenance-bearing conflicts preserve concurrent offline values. Negotiated
format-2 checkpoints bound authenticated graph history; exact-record pins and signed workspace roots
guard quarantine-only GC; restore reauthenticates every object. Exact terminal writer cutoffs are
owner-local per survivor and do not imply general authority revocation. Quiet convergence no longer
authors acknowledgement-only branches. ADRs 0278 and 0280--0283 close the founding selective-sync,
finite adversarial/scale, and two-hour incumbent-shadow gates. There is no permanent purge.
ADRs 0329--0331 bound parallel exact-object lanes, batch file commits, and reduce full CAS hashing to
pull-scoped initial/final scans while retaining strict final quota and mutation checks before any
branch or projection effect.
ADR 0332 additionally retains one corrected source-linked, two-boot Sandwurm qualification: an exact
task-owned VMM disk cut at raw signed pending phase byte 2 exposes only prior/completed projections
before identity-preserving convergence. ADR 0333 retains the paired post-exchange result with all
views completed and the pending journal, marker, and old stage recovered exactly. Its phase-reversed
v1 predecessor is withdrawn. ADR 0334 makes receive/CAS temporary cleanup durable and retains two
source-linked strict v4 object-pipeline VMM passes. Run `1e05ayp9` cuts the real partial generic
transport temporary; run `jtiyspp_` cuts the partial CAS install copy. Both exact compact proofs
verify independently and recover without residue to the same three-writer successor. ADR 0335 adds
strict v5 construction for the manifest, immutable-record, and mutable-pointer pre-rename prefixes,
with external worker-thread fencing and exact second-boot prefix inspection; all three
source-linked cells pass. ADR 0336 separately closes each adjacent
post-rename/pre-directory-fsync cell. ADR 0337 authenticates current branch,
immutable record/manifest, workspace, and maintenance metadata at both startup
and `sync-repair`, retains byte-invalid signed records unchanged, and
qualifies the exact external-restoration KVM gate in source-linked run
`mixJ9VUp` at commit `08e4179`. Its five families refuse live repair and cold
startup without mutation, restore exact originals, preserve identity/worktree,
converge to `[3,3,3]`, and retain strict compact proof
`.sandwurm/exports/sync-metadata-corruption/run.mixJ9VUp`. ADR 0339 adds
direct valid-old witness refusal and a co-resident-corruption v2 construction;
source-linked KVM/ext4 run `MG27auOK` qualifies it and retains compact proof
`.sandwurm/exports/sync-metadata-corruption/run.MG27auOK`. Projection descriptor writes
are retained through ADR 0338's deterministic pre- and post-exchange
validation checks; a write after final old-tree validation begins remains
open. Other durable families, physical
power loss, dishonest-storage,
case-folding, symlink, rich-metadata, sparse-fetch,
encrypted-at-rest, backup, and unrestricted sole-copy claims remain excluded.

The aggregate CPU ledger accounts configured average bandwidth. It does not align independent period
boundaries, enforce a parent `cpu.max`, reserve processor time, model burst concurrency, guarantee
latency or throughput, or cover CPU weight/burst, real-time/deadline policy, cpusets, aggregate I/O reservation,
storage latency/queue-depth control, persistent PSI histories, adaptive pressure thresholds, atomic cross-resource PSI snapshots, pressure-based preemption of existing sessions, continuous peak/fault/reclaim/freeze monitoring, or outcome-adaptive admission, cross-daemon distributed capacity, privileged co-writers, namespace/container
isolation, target-fleet qualification, independent audit, or production readiness.

## Excluded and prohibited material

The repository snapshot excludes untracked build trees, dependency work directories, caches, and
runtime state. The datacube must contain no live `.toxsave`, RecallRoot phrase, private key, device
identity, authority ledger, command/profile/runtime store, socket, FIFO, journal, received file, core
dump, unrelated host log, unsafe archive path, or symlink entry. Pinned dependency archives are
permitted only in a checksummed standalone source-input package after `dependencies.lock`
verification.

## Construction and verification

Build only from a clean commit:

```sh
git diff --check
git status --short
tools/iotox-repo.sh release-check founder-preview --iotox /path/to/iotox
IOTOX_DATACUBE_TIMESTAMP="$(TZ=America/New_York date +%Y.%m.%d.%H.%M.%S)" \
  ./tools/iotox-repo.sh datacube --seed /mnt/data
./tools/make-repository-datacube.sh --verify \
  /mnt/data/IoTox-seed-repository-datacube-TIMESTAMP-COMMIT.zip
unzip -tq /mnt/data/IoTox-seed-repository-datacube-TIMESTAMP-COMMIT.zip
```

After copying to the linked outer basename, run the same verifier again against that exact file. The
embedded `repository/REVISION` must be `rev0051`, datacube metadata must name the packaged Git commit,
and the final linked response must contain exactly one link whose visible text is the complete archive
filename.
