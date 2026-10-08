# AnonSync rev0839 deep audit

## Heart of the mission

AnonSync is an evidence-authorized convergence engine. A returned PID, parsed document,
wall-clock timeout, durable row, syscall, signature, or successful commit is an
observation. The invariant owner must bind the exact identity, generation, process life,
policy, bytes, namespace object, and durability evidence required for a transition
before it can authorize mutation. Then the authorized transitions must be given an
explicit convergence algebra.

Rev0839 applies that rule to daemon takeover. A stale heartbeat alone is not proof that
the daemon is dead, and a PID is not a process incarnation.

## Severe parent defect

The sealed rev0838 document serialized a numeric PID but neither daemon preflight
nor operator status re-observed it. After the stale deadline and durable owner expiry,
preflight admitted re-entry even if the exact original process still existed. This can
happen during a long scheduler pause, overload, filesystem stall, or partial failure.
The parent also duplicated lifecycle policy in two consumers, making drift likely.

The exact parent slices are preserved under `defect/`. This was not merely missing
telemetry: the unused PID created the appearance of process evidence without placing it
in the authorization decision.

## C++ correction

A new dependency-light leaf owns `SyncProcessIdentityObservation` and a six-way typed
comparison result. Linux observations bind PID, boot UUID, and `/proc/<pid>/stat` field
22. The parser finds the final `)` around `comm`, bounds reads at 4096 bytes, rejects
embedded NUL and malformed canonical values, treats zombie/dead states as not running,
and uses nonblocking no-follow close-on-exec descriptors. A pidfd is opened and polled
before and after proc reads when available. Windows uses process creation FILETIME from
`GetProcessTimes`; unsupported platforms emit an explicit unavailable format.

The leaf is explicitly observational. A document writer can forge all of these fields.
Only the separately verified durable owner generation remains mutation authority.

Heartbeat schema v2 requires the nested process-incarnation object and exact equality
between top-level and nested PIDs. V1 remains decodable only as legacy PID-only evidence;
a non-final legacy document fails closed and requests operator attention. V1 cannot
smuggle v2 fields.

A shared `evaluate_sync_daemon_heartbeat_lifecycle_or_throw` now owns both daemon
preflight and operator status. Its meaningful outcomes are:

| Document and evidence | Decision |
|---|---|
| Exact final/released owner evidence | Permit new start |
| Non-final legacy PID-only | Block; operator attention |
| Unsupported, indeterminate, or invalid process observation | Block; operator attention |
| Missing stale horizon or scheduler clock | Block |
| Fresh, exact live process, live owner | Healthy existing daemon; block second start |
| Stale, but owner still live | Block; operator attention |
| Stale, owner expired, but exact process still live | Block; operator attention |
| Stale, owner expired, process gone or incarnation mismatched | Permit re-entry |

Heartbeat publication captures the current process identity on the first write and
requires every later write to match it. This catches an inherited/forked writer trying
to continue a parent daemon's heartbeat result object.

## Refactor and build-graph audit

The process observation is a separate static leaf rather than another helper embedded
in the 15,285-line domain translation unit. A source audit proves one compiled owner,
no core back-edge, call-site parity, bounded proc parsing, no raw PID-only kill checks,
shared lifecycle evaluator use, and focused target ownership.

The sanitizer lane exposed a genuine CMake defect during this revision: new objects were
compiled with ASan/UBSan, but their focused executable was omitted from the list that
links sanitizer runtimes. The resulting undefined sanitizer symbols were correctly
treated as a failed gate. CMake was fixed and the audit gained a permanent
`focused_sanitizer_compile_link_parity` invariant. The clean sanitizer lane then linked
and passed 70/70 with leak detection enabled.

One wasteful test dependency was also removed: the non-forking process-observation test
no longer links the inherited-process wrapper. Its focused graph now contains only the
leaf and its test.

## Cloudtainer correction

Old orphaned revision streams repeatedly compiled abandoned trees and attempted to
publish conflicting artifacts. Their results are not included. The authoritative source
and build were frozen by active-projection digest, stale groups and paths were
quarantined, and the final 131 tests were counted only from exact successful,
non-overlapping ranges. This is why the validation summary does not claim one
uninterrupted CTest invocation.

## Evidence

- Parent package: directory **21/21**, ZIP **25/25**.
- Active source patch replay: **PASS**, 229 files, zero mismatches.
- Active source delta: **15 files**, **1,996 insertions**, **102 deletions**.
- Focused process identity: **15/15**.
- Focused heartbeat lifecycle: **55/55**.
- Domain integration: **602/602**.
- Focused repeat: **700/700**.
- Process source audit: **27/27**.
- Heartbeat source audit: **29/29**.
- Related regression audits: **21/21** and **13/13**.
- Clang 17 `-Werror`: **70/70**.
- GCC 14 ASan+UBSan with leak detection: **70/70**.
- Complete final CTest inventory: **131/131**.

## What remains missing

Process observation is unauthenticated and can be forged for denial of service. The
cloudtainer kernel returned `ENOSYS` for `pidfd_open`, so the runtime result covers the
explicit procfs fallback, not pidfd behavior. The Windows branch is source-reviewed but
not compiled or executed. Wall-clock staleness remains a suspicion mechanism. No full
project sanitizer or full Release all-target gate is claimed.

The larger mission remains open: authenticated lifecycle evidence, cross-resource
crash-cut completeness, a disposable hostile-database worker, executable convergence
semantics, payload confidentiality, anonymity and metadata-leakage analysis, device/key
lifecycle, forward secrecy, post-compromise recovery, and secure erasure.
