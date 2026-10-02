# ADR 0085: Add exact-device I/O ceilings and retain kernel I/O accounting

- Status: accepted and implemented in rev0034
- Date: 2026-08-19
- Scope: canonical local terminal policy, host/profile composition, delegated cgroup-v2 enforcement,
  PTY teardown outcomes, and private runtime truth
- Wire effect: none

## Context

rev0029 established fail-closed per-session `pids.max`, memory, swap, and `cpu.max` controls in one
administrator-delegated cgroup-v2 subtree. rev0030 made those limits profile-scoped beneath a host
ceiling; rev0031 and rev0032 added conservative aggregate admission for process, memory, swap, and
exact average CPU bandwidth. rev0033 added `memory.high` and retained content-free PID, memory, and CPU
kernel outcomes after proved quiescence.

Terminal workloads can still consume unbounded block-device bandwidth and IOPS. Linux cgroup v2
exposes `io.max`, a nested-keyed per-device BPS/IOPS limit, and `io.stat`, a nested-keyed per-device
accounting record. The interfaces have ordering freedom and device-specific semantics that differ
from the existing flat-keyed controllers.

The policy boundary must prevent a profile from redirecting an administrator's ceiling to another
device, must not infer identity through mutable paths or aliases, and must fail before helper execution
when the delegated controller does not retain the exact policy. Outcome accounting must remain
content-free and bounded. It must not turn rate limits into a false aggregate-reservation claim or
pretend that buffered-write attribution, latency, or storage topology is universally qualified.

## Decision

1. Add `CgroupIoDevice { uint32 major, uint32 minor }` and four optional positive rate ceilings to
   `CgroupResourceLimits`: read/write bytes per second and read/write operations per second.
2. Treat the five I/O fields as one unit. A device requires at least one ceiling and any ceiling
   requires a device. Reject `0:0`, noncanonical device text, values outside `uint32`, zero ceilings,
   and ceilings above `INT64_MAX`.
3. Emit canonical `iotox-terminal-profile-v5` with ordered `cgroup-io-device`, `cgroup-io-rbps`,
   `cgroup-io-wbps`, `cgroup-io-riops`, and `cgroup-io-wiops` fields. Continue exact canonical decoding
   of v1-v4 and migrate them with no invented I/O policy.
4. Add host CLI options mirroring those five fields. They remain local administrator policy and are
   not represented in the Ratox protocol.
5. Compose host and profile I/O policy only when both name the same exact numeric device. If one side
   is absent, inherit the other. For a matching device, select the lower configured value independently
   for each of the four ceilings. Reject a cross-layer device mismatch before host activation.
6. Request `io` whenever an effective I/O policy exists. Require the controller to be both available
   and activated in the delegated root before leaf creation proceeds.
7. Write one complete `io.max` line for the exact device, using explicit `max` for every absent
   dimension. Parse the readback semantically because device lines and nested keys are unordered.
   Require exactly one retained device line and exact equality for all four standard values before the
   blocked helper may execute. Apply the same path in startup preflight and production creation.
8. Parse `io.max` and `io.stat` as bounded LF-terminated nested-key records. Reject malformed spacing,
   noncanonical or overflowing decimals, duplicate device lines, duplicate keys, and missing required
   standard fields. Accept well-formed future fields. For `io.max`, `max` represents absence and zero
   finite standard ceilings are invalid. For `io.stat`, require read/write bytes and operations on each
   nonempty line; accept the discard byte/operation counters only as a complete pair and map an absent pair to zero.
9. Open a protected read-only `io.stat` descriptor before attachment and require the fresh leaf's
   known counters to be zero. After recursive `populated=0`, sum all device lines with saturating
   arithmetic before descriptor reset and exact inode removal.
10. Add six I/O fields to one-shot `CgroupSessionOutcome`, factory aggregate state, Agent snapshots,
    and owner-private runtime status. Record only complete outcomes. Any statistics read/parse failure
    contributes one incomplete outcome and no partial counters, while proved-empty cleanup may still
    complete.
11. Keep aggregate admission unchanged. `io.max` is an overcommittable rate limit, not an advance
    allocation of physical service; no aggregate I/O reservation is inferred from per-session maxima.
12. Add a capability-aware live process oracle. On a suitable delegated host it discovers a genuine
    written device from `io.stat`, verifies exact `io.max` retention, performs synchronous I/O, and
    requires nonzero teardown accounting. Missing namespaces, preactivated `io`, or attributable
    block I/O returns named skip code 77 rather than a synthetic pass.

## Consequences

- A local host or profile can bound one reviewed block device by direction and unit before payload
  execution.
- A profile cannot union devices with or redirect a host ceiling; disagreement keeps the service
  offline.
- Semantic readback tolerates documented kernel ordering freedom without accepting duplicate or
  incomplete policy.
- Completed-session status gains cumulative content-free read/write/discard byte and operation totals
  without per-device, per-profile, path, command, peer, or terminal labels.
- Numeric device identity is stable only within the qualified deployment topology. Administrators
  must requalify after device-number or backing-stack changes.
- Kernel `io.max` allows temporary bursts. The feature does not guarantee latency, completion time,
  or queue depth.
- Buffered writeback attribution is mediated by filesystem and inode ownership. Shared inodes or
  filesystems without cgroup writeback support can prevent exact workload attribution.
- Privileged co-writers remain outside the trust boundary. The delegated subtree must have one
  manager.

## Rejected alternatives

### Accept a filesystem path instead of `MAJOR:MINOR`

Rejected because paths can be aliases, mounts can be rebound, and layered filesystems may not name the
actual device consumed by `io.max`. The kernel interface's numeric identity is the canonical policy
input; deployment tooling may map reviewed topology to that tuple outside the profile format.

### Union different host and profile devices

Rejected because a profile would be able to add or redirect controlled media. Monotone composition is
well-defined only for one matching device in v5.

### Write only configured `io.max` subkeys

Rejected for IoTox's fresh-leaf proof. A complete line with explicit `max` values produces a fully
specified semantic state and lets readback prove every standard dimension rather than relying on
implicit defaults.

### Compare `io.max` byte-for-byte

Rejected because Linux nested-keyed records do not promise device-line or subkey ordering. IoTox
parses a bounded semantic representation and compares exact values.

### Count only the configured device in `io.stat`

Rejected because a session may generate I/O on other devices through executable loading, logging,
filesystem layers, or unexpected paths. Whole-leaf totals are more truthful and remain content-free.
The configured device is a control target, not a claim that all session I/O reaches only that device.

### Treat summed `io.max` values as aggregate reserved bandwidth

Rejected because cgroup-v2 limits may be overcommitted and do not reserve physical media service.
Aggregate I/O admission requires an explicit capacity and topology model that rev0034 does not have.

### Assert throughput or latency from a timed smoke test

Rejected because temporary bursts, caching, writeback, scheduler behavior, and storage stacks make a
portable timing oracle misleading. The live route proves kernel policy retention and attributed
accounting; target-specific performance qualification remains separate.

### Publish device-labelled session histories

Rejected because labels and histories widen retained metadata and cardinality. Owner-private
cumulative unlabeled totals are sufficient for the current operational truth boundary.
