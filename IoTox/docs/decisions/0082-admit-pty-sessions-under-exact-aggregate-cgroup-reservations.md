# ADR 0082: Admit PTY sessions under exact aggregate cgroup reservations

- Status: accepted and implemented in rev0031
- Date: 2026-08-19
- Scope: local Ratox PTY admission, production process-factory lifecycle, and private aggregate runtime truth
- Wire effect: none

## Context

rev0030 computes a finite effective cgroup-v2 envelope for every enabled local terminal profile and
proves that policy before network activation. The kernel enforces each admitted session leaf, but
cgroup-v2 limits are intentionally overcommittable: the sum of sibling limits may exceed the resource
available to their parent. A service-level maximum session count therefore does not prevent a set of
heterogeneous profile maxima from multiplying into an administrator-unintended process, memory, or
swap commitment.

The missing control is host-local admission over configured maxima, not a claim that userspace can
preallocate kernel process slots or physical pages. It must preserve the existing authority boundary:
remote Ratox bytes select neither profile nor resource values. It must also fail before any helper,
PTY, cgroup, or process mutation. Capacity may be released only after a partial failure or complete
teardown proves that no charged process/cgroup authority remains; uncertain cleanup must fail closed.

## Decision

1. Add an optional administrator-owned `CgroupAggregateLimits` policy with maximum reserved process
   slots, memory bytes, and swap bytes across live production Ratox PTY sessions. Zero remains a
   meaningful configured swap maximum.
2. Treat the effective post-host/profile-composition `CgroupResourceLimits` as the exact reservation
   vector. Every configured aggregate dimension requires a finite matching per-session maximum, and
   one session must fit on an otherwise empty ledger. Host activation validates this for every enabled
   profile before cgroup recovery or network startup.
3. Require the existing explicit delegated cgroup-v2 root whenever aggregate reservation policy is
   configured. Reject an injected process factory at that boundary: only the production factory can
   couple an admission token to the proved cgroup/process lifecycle.
4. Construct one thread-safe admission controller per production PTY factory. Under one mutex, check
   every configured dimension with subtraction-based overflow-safe arithmetic, reject the whole vector
   atomically when any dimension would exceed its ceiling, and otherwise charge all dimensions and the
   active-reservation count together.
5. Charge after pure profile/root/signal-capability validation but before helper-path validation,
   filesystem opening, encoding, socket or PTY creation, cgroup-leaf creation, or process spawn. A
   capacity rejection therefore produces no process or cgroup side effect.
6. Represent a successful claim as a move-only RAII reservation. A pre-spawn return releases it
   exactly once. After process creation, release only when cleanup proves both direct-child reap and
   exact cgroup removal. A successful `PosixPtyProcess` owns it through recursive descendant death,
   cgroup quiescence and removal, and direct-child reap. If startup rollback or destructor cleanup
   cannot prove that boundary, detach the token while retaining its exact charge and increment a
   saturating stranded-reservation counter. This deliberately rejects later work until daemon restart
   recovery rather than under-accounting a possibly live cgroup.
7. Retain monotone current and peak evidence plus saturating capacity-rejection and stranded-
   reservation counts. Publish only configured dimensions/maxima, current and peak aggregate
   reservations, active reservation counts, and those counts in the owner-private runtime tree. Do not publish profile IDs, payload
   identities, commands, paths, or terminal content.
8. Exclude CPU from this revision. CPU policy is a rational quota/period pair; summing heterogeneous
   ratios into a canonical host-wide reservation requires an explicit scheduling contract rather than
   an approximate scalar conversion.

## Consequences

- Concurrent session admission cannot overrun a configured process, memory, or swap reservation
  ceiling inside one legitimate IoTox host incarnation.
- A profile missing a finite required dimension, or whose single effective maximum exceeds the
  aggregate ceiling, prevents host activation before network exposure.
- Reservation is conservative: an idle session holds its configured maxima, actual kernel usage
  below the maxima does not create unadvertised capacity, and an unproved post-spawn teardown retains
  its full charge until restart recovery.
- Kernel cgroup limits remain the enforcement mechanism after admission. The userspace ledger does not
  reserve physical RAM, guarantee allocation success, predict reclaim, or replace parent cgroup limits.
- The signed host-incarnation lease prevents two legitimate IoTox daemons from owning the same host
  lifecycle at once. A separate privileged co-writer, external process migration, and target-fleet
  resource sizing remain outside this claim. A daemon crash loses the in-memory ledger, so startup
  orphan recovery remains the authority that must clear or reject abandoned leaves before new network
  exposure.
- Per-device I/O throttling, PSI-driven adaptive admission, aggregate CPU bandwidth, dynamic policy
  reload, and cross-daemon distributed reservation remain open work.

## Rejected alternatives

### Rely on the sum of child cgroup limits

Rejected because Linux explicitly permits child limits to be overcommitted. Per-leaf enforcement does
not by itself reject a new sibling whose configured maximum would push the administrator's aggregate
policy over its ceiling.

### Reserve observed usage instead of configured maxima

Rejected because usage is mutable after admission and creates a time-of-check/time-of-use race. It
would also allow several low-usage sessions to enter and then simultaneously grow to their individual
kernel maxima.

### Charge after process spawn

Rejected because capacity exhaustion would then require rollback of a newly created process and cgroup
and could transiently exceed the declared admission policy.

### Count sessions only

Rejected because enabled profiles may have different effective maxima. One session count cannot
represent the process, memory, and swap commitment of a heterogeneous policy set.

### Convert CPU quota to one approximate scalar

Rejected because rounding and period selection would invent scheduling semantics. Exact aggregate CPU
admission needs a separately reviewed policy.
