# ADR 0089: admit new PTY sessions with cgroup PSI hysteresis

- Status: accepted and implemented in rev0038
- Date: 2026-08-19
- Scope: host-local Ratox PTY admission before aggregate reservation and process mutation

## Context

rev0031 and rev0032 prevent configured per-session envelopes from exceeding one exact aggregate
reservation vector. rev0035 retains completed-session CPU, memory, and I/O Pressure Stall Information
(PSI) totals but deliberately keeps that historical evidence outside admission. Those controls answer
whether a requested envelope fits configured capacity; they do not answer whether the delegated host
subtree is already experiencing current contention when a new interactive PTY is requested.

Linux PSI exposes recent ten-, sixty-, and three-hundred-second pressure trends plus cumulative stall
time for CPU, memory, and I/O. Kernel documentation explicitly identifies load shedding as one valid
userspace response. A safe host gate still needs exact parsing, a stable cgroup identity, hysteresis,
clear failure semantics, bounded state, and an admission ordering that cannot consume aggregate
capacity or create a process before the pressure decision is complete.

## Decision

1. Add an optional host-local pressure-admission policy. It is disabled by default and is never
   serialized into a terminal profile, Ratox packet, authority record, or remote capability choice.
2. Accept independent exact thresholds for delegated-root CPU `some avg10`, memory `full avg10`, and
   I/O `full avg10`. Represent every percentage as an unsigned integer basis-point value in
   `0..10000`, where one unit is `0.01%`; do not use binary floating point.
3. Apply one configured hysteresis width to every enabled metric. Hysteresis requires at least one
   threshold and may not exceed any enabled threshold.
4. Close the gate only when an enabled observation is strictly greater than its maximum. Once closed,
   reopen only when every enabled observation is less than or equal to
   `maximum - hysteresis`. Equality at the close boundary remains admitted; equality at the reopen
   boundary reopens. A zero-width policy is valid and still retains explicit latch state.
5. Construct the controller during production PTY-factory activation under the signed host lease and
   before resource-policy probe leaves, orphan-recovery mutation, listener exposure, or network
   service. Require one normalized absolute non-root cgroup-v2 path, the established daemon-owned
   delegation boundary, `cgroup.pressure=1`, and every configured PSI file. Pin the exact root and PSI
   control files by descriptor.
6. Parse complete LF-terminated canonical PSI records. Require `some` for every sampled resource and
   additionally require `full` for configured memory and I/O decisions. Require exactly two decimal
   percentage digits, reject duplicate or missing mandatory keys/classes, reject values above
   `100.00`, retain exact `avg10` basis points, and continue grammar-validating future numeric fields
   without assigning them admission semantics.
7. Check `cgroup.pressure=1` both before and after the configured PSI reads, then preflight one complete
   descriptor-pinned sample at controller construction. A missing, disabled,
   unreadable, malformed, or unsupported capability aborts host activation. High but valid pressure
   does not abort startup; the first real PTY admission applies the threshold and latch decision.
8. On each PTY spawn, sample pressure before aggregate reservation, cgroup-leaf creation, PTY/helper
   creation, or any other mutable spawn work. A pressure rejection therefore consumes no aggregate
   reservation and creates no child process or session cgroup.
9. Serialize sampling and state transition under one controller mutex. Any read, parse, accounting,
   or semantic failure rejects the request and latches the gate closed. Classify the live request as
   local `unavailable` rather than a peer protocol error while retaining the original typed local
   failure in private status. Only a later complete valid sample satisfying all reopen thresholds can
   reopen it.
10. Retain saturation-safe counts for checks, admissions, rejections, sampling failures, close
    transitions, and reopen transitions, last-sample validity and its typed local error class, plus the
    most recent valid configured observations. Project
    them only into owner-private runtime status without profile, principal, command, path, payload,
    process, peer, or terminal-content labels.
11. Add exact parser/evaluator boundaries, malformed input, zero/full-range threshold, CLI, Agent,
    runtime projection, startup failure, no-mutation failure, GCC/Clang, and dedicated private-cgroup
    process coverage. The process route must disable `cgroup.pressure`, prove fail-closed latching,
    restore it, prove one exact reopen, and serialize a concurrent valid-admission burst when the
    construction host exposes per-cgroup PSI.

## Consequences

- A host can reject new interactive work when the exact delegated subtree is already experiencing a
  configured recent CPU, memory, or I/O pressure trend.
- Hysteresis prevents a closed gate from reopening merely because one sample oscillates immediately
  below the close threshold.
- Descriptor pinning prevents ordinary pathname substitution after activation from redirecting the
  controller to a different cgroup or PSI file.
- Startup capability validation prevents a configured gate from silently degrading to an always-open
  policy.
- Fail-closed sampling makes loss or corruption of the pressure signal visible as rejection rather
  than success.
- Pressure and aggregate-capacity decisions remain distinct: pressure is sampled first, then the
  existing exact aggregate vector is reserved atomically.
- Runtime counters disclose policy behavior without creating per-session operational telemetry.

## Retained nonclaims

- `avg10` is a rolling recent trend, not a forecast, instantaneous utilization, free-capacity
  measurement, queue-depth bound, latency guarantee, throughput guarantee, or proof that one more
  session would cause failure.
- Sequential reads of CPU, memory, and I/O PSI are not one atomic kernel snapshot. The gate makes one
  bounded synchronous decision from the complete sequence it observed.
- CPU `some` and memory/I/O `full` are policy choices, not universal defaults. Safe thresholds and
  hysteresis require workload- and deployment-specific qualification.
- The gate does not install PSI trigger file descriptors, continuously monitor pressure, preempt or
  kill existing sessions, migrate work, change cgroup ceilings, or persist latch/counters across
  daemon restart.
- The most recent projected observation is the last valid complete sample. A later sampling failure
  sets last-sample validity false, retains its typed local error class, increments `sampling-failures`,
  and closes the gate without fabricating replacement metric values.
- Descriptor and ownership checks do not exclude a privileged cgroup co-writer. A sufficiently
  privileged actor can alter kernel policy or accounting and is outside this local daemon boundary.
- Construction-host compilation and skipped capability-aware process routes do not establish target
  fleet support, threshold fitness, independent security review, or production readiness.

## Rejected alternatives

### Use floating-point percentages

Rejected because admission boundaries must be locale-independent and exact. The kernel emits two
fractional digits, so integer basis points preserve the complete decision value without rounding.

### Close and reopen at the same threshold without a latch

Rejected because repeated samples near one boundary can flap admission state and amplify request
bursts. Explicit hysteresis makes the reopening condition strictly more conservative when configured.

### Treat a sampling failure as an open gate

Rejected because missing or malformed pressure evidence is not evidence of low pressure. Fail-open
behavior would silently disable configured load shedding exactly when the signal is least trustworthy.

### Fail Agent startup whenever the current sample exceeds a threshold

Rejected because a transient valid pressure trend is an admission condition, not a capability or
configuration defect. Startup validates that the signal can be trusted; live requests apply policy.

### Reserve aggregate capacity before sampling PSI

Rejected because a pressure-rejected request would temporarily consume scarce configured capacity and
could contend with otherwise admissible requests. The pressure decision must precede every reservation
and process/cgroup mutation.

### Put pressure thresholds in remotely selected profiles

Rejected because delegated-root PSI is host state and host capacity policy. A remote profile must not
choose the host's load-shedding threshold or infer host-wide operational state.
