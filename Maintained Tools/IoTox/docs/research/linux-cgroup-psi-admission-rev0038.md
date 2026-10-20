# Linux cgroup PSI admission — applied review for rev0038

## Sources reviewed

Primary sources retrieved and rechecked 2026-08-19 America/New_York:

- Linux kernel, *PSI — Pressure Stall Information*:
  https://docs.kernel.org/accounting/psi.html
- Linux kernel, *Control Group v2*:
  https://docs.kernel.org/admin-guide/cgroup-v2.html
- Linux source, `kernel/sched/psi.c`:
  https://github.com/torvalds/linux/blob/master/kernel/sched/psi.c

The documentation is the semantic authority for userspace interfaces. Current kernel source was read
to confirm the emitted PSI grammar and current CPU/full handling, not to create an undocumented ABI.

## Source findings applied

### PSI is a contention signal intended to support load shedding

Linux documents PSI as a measure of productive time lost to CPU, memory, or I/O resource contention.
It explicitly names dynamic load shedding, migration, pausing, and killing lower-priority work as
possible userspace responses. rev0038 applies only the narrowest of those choices: refuse creation of a
new Ratox PTY. It does not migrate, pause, reprioritize, or kill existing work.

### Per-cgroup interfaces use the standard PSI record

On a cgroup-v2 system with PSI support, cgroups expose `cpu.pressure`, `memory.pressure`, and
`io.pressure` records using rows of the form:

```text
some avg10=0.00 avg60=0.00 avg300=0.00 total=0
full avg10=0.00 avg60=0.00 avg300=0.00 total=0
```

`some` measures intervals in which at least one task is stalled. `full` measures intervals in which all
non-idle tasks are stalled simultaneously. The averages are percentages over recent ten-, sixty-, and
three-hundred-second windows; `total` is cumulative microseconds.

Applied construction:

- parse all mandatory current fields with a bounded canonical grammar;
- convert the exact two-digit percentages directly to integer basis points;
- retain `avg10` only for the admission decision while continuing to validate `avg60`, `avg300`, and
  `total` as part of the complete record;
- require CPU `some` for CPU admission;
- require memory and I/O `full` for memory/I/O admission;
- reject missing, duplicate, malformed, overflowing, unterminated, or oversized evidence;
- accept unrelated future numeric fields/classes only after canonical grammar validation and assign
  them no current admission meaning.

### Ten-second averages are recent trends, not instantaneous capacity

The documented averages summarize recent windows. rev0038 therefore treats them only as a policy
signal at one admission instant. It does not call them utilization, remaining capacity, a forecast, a
service-level objective, or a guarantee that pressure will remain below a threshold after admission.
The existing aggregate cgroup ledger remains the exact configured-capacity gate; PSI is an independent
current-contention gate.

### `cgroup.pressure` controls per-cgroup PSI accounting

The cgroup-v2 core interface `cgroup.pressure` accepts `0` or `1`, defaults to `1`, and disables PSI
accounting for that cgroup when set to `0`. Its setting is not hierarchical.

Applied construction:

- construct the controller under the signed host lease before resource-policy probes, orphan-recovery
  mutation, listener activation, or network exposure;
- pin the exact delegated root, its `cgroup.pressure` file, and every configured PSI file by descriptor;
- require the exact canonical enabled record `1\n` during startup preflight and both before and after
  every configured admission sample;
- fail host activation if configured PSI capability is unavailable or disabled;
- fail an admission closed and latch the gate if accounting later becomes disabled or unreadable;
- return local `unavailable` for the live request while retaining the original typed local sampling
  cause in owner-private status;
- reopen only after accounting is enabled and one complete valid sample satisfies every configured
  reopen boundary.

### Cgroup identity and controller delegation are separate concerns

Per-cgroup PSI observation belongs to the cgroup-v2 hierarchy and does not itself require IoTox to
enable the CPU, memory, or I/O resource controllers in `cgroup.subtree_control`. rev0038 therefore
requires the PSI files themselves, not an unrelated resource-controller policy. Existing resource
ceilings continue to validate their own controller availability independently.

The controller still reuses the established IoTox delegated-root boundary: normalized absolute
non-root path, cgroup-v2 filesystem identity, daemon-owned directory/control files, no symlink
traversal, and descriptor pinning. This binds observations to the same host subtree used for session
cgroups without claiming protection against a privileged co-writer.

## Admission state machine

For each configured metric `x`, maximum `M`, and common hysteresis `H`:

```text
open -> closed     when any x > M
open -> open       when every x <= M
closed -> open     when every x <= M - H
closed -> closed   otherwise
sample failure     reject and force/retain closed
```

Configuration requires `0 <= H <= M` for every enabled metric. Comparisons are exact unsigned integer
basis-point comparisons. Threshold equality is admitted while open; reopen-boundary equality reopens.
A valid high-pressure startup sample does not prevent Agent startup because it is live state rather
than a capability defect. The first real request applies the state machine.

## Ordering and evidence boundary

rev0038 samples the descriptor-pinned delegated-root PSI records synchronously and under one controller
mutex. The complete pressure decision occurs before:

1. aggregate process/memory/swap/CPU reservation;
2. session-cgroup leaf creation;
3. PTY or helper process creation;
4. payload attachment or manifest release.

A rejected or failed sample therefore leaves aggregate accounting and process/cgroup state unchanged.
Successful pressure admission does not bypass any later profile resolution, aggregate reservation,
resource-policy, PTY, confinement, attachment, or supervision check.

Owner-private runtime status publishes configuration flags and thresholds, latch state, saturating
check/admit/reject/failure/transition counts, last-sample validity, the typed local sampling-error
class, and the last valid configured observations. A failed sample does not erase the preceding valid
observation, but it is explicitly marked invalid for the current decision. The live admission result is
normalized to local `unavailable`; the private snapshot preserves the more specific bounded cause. It
does not publish per-session labels, payload identity, profile identity, command, path, peer, process,
device, terminal bytes, or error strings.

## Qualification boundary

rev0038 adds:

- exact valid and malformed PSI percentage parsing;
- zero, equality, full-range, close, latch, and reopen evaluator boundaries;
- missing-observation failure;
- policy validation and CLI range/root rejection;
- Agent startup validation and private runtime projection;
- production factory preflight failure before spawn mutation;
- GCC and Clang builds and direct suites;
- one dedicated private-cgroup process route that, where PSI exists, opens the real kernel interfaces,
  accepts a low-pressure sample, writes `cgroup.pressure=0`, proves fail-closed latching, typed
  last-sample evidence, and exact counters, restores `1`, proves one reopen, serializes a concurrent
  valid-admission burst with exact totals, and proves startup preflight refuses disabled accounting.

The 2026-08-19 construction host runs Linux 6.18.35 but does not expose `/proc/pressure` or
per-cgroup `cgroup.pressure`. The dedicated route therefore returns its named code-77 capability skip.
No synthetic positive kernel PSI-admission result is claimed. Parser, state-machine, integration, and
compiler evidence remain valid; live target support remains unqualified on this host.

## Explicit limitations

rev0038 does not implement:

- PSI trigger registration or `poll`/`epoll` monitoring;
- one atomic cross-resource kernel snapshot;
- continuous sampling, histories, percentiles, forecasting, or adaptive thresholds;
- default threshold selection or workload-specific tuning;
- preemption, migration, reprioritization, pausing, or killing of existing sessions;
- pressure-latch persistence across restart;
- remote/profile control of host pressure policy;
- privileged cgroup co-writer exclusion;
- target-fleet kernel/delegation qualification, external audit, or production activation.
