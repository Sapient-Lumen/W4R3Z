# AnonSync rev0835 — inherited owner, WNOWAIT seal, fresh-image reclassification

## Executive result

Rev0835 reduces the active raw-fork surface from 15 calls in eight test
translation units to one call in one test-only owner. The remaining call is not
a generic process-launch mechanism: it exists solely for probes whose subject
is application authority inherited through an ordinary fork.

The revision also corrects a lifecycle defect shared by the fresh-image and
inherited owners. A successful top-level leader could previously be reaped
before group cleanup. Once reaped, the owner had released the strongest local
PID identity evidence while descendants could still be alive. Both owners now
observe the leader without reaping, terminate the still-bound group, and reap
the exact leader only after that cleanup transition.

## What changed

### One owner for inherited-state probes

`tests/inherited_test_process.{hpp,cpp}` defines a move-only test capability that
jointly owns:

- the exact child leader PID;
- the top-level process group;
- an optional close-on-exec capture pipe;
- a monotonic timeout;
- a bounded output budget;
- kill and exact-reap authority; and
- the rule for relinquishing numeric authority on `ECHILD`.

Only this implementation contains `::fork()`. Thirteen spawn sites across seven
consumers use it. Top-level children establish a process group, while nested
inherited probes intentionally remain in that group. Timeout, overflow,
exception, destructor, read, poll, and wait failures consume process and
descriptor authority before reporting failure.

The runtime oracle covers move transfer, exact status, callback exception,
invalid return, exact binary capture, overflow, wait-mode mismatch, timeout,
destructor cleanup, external reap, nested group topology, and successful-leader
descendant cleanup. It passes **20/20** checks.

### Successful exit no longer strands descendants

Both process owners use Linux `waitid(P_PID, ..., WEXITED | WNOHANG |
WNOWAIT)` to distinguish a waitable leader without reaping it. While that zombie
still pins leader identity, the owner sends `SIGKILL` to the owned group and
then performs the exact leader reap. `ECHILD` clears PID/group authority before
throwing, so a later numeric reuse cannot be signaled by cleanup.

Deterministic Linux tests temporarily become child subreapers, create a
successful leader with a deliberately lingering descendant, and prove that the
exact descendant becomes waitable with `SIGKILL`. The self-exec owner now passes
**35/35** checks.

### Fresh-state campaigns are fresh images

Two tests were described as inherited-state probes even though their databases
and SQLite state were created only after the fork. They now enter versioned,
pinned self-exec helper modes:

- SQLite connection-affinity fail-stop: **10** isolated scenarios; and
- owner-generation borrow/close races: **32** isolated workers.

This removes inherited allocator, mutex, SQLite, and C++ runtime state from
campaigns that never needed it. True inherited-capability probes remain on the
new inherited owner.

### Typed evidence rather than capability bytes

`SyncProcessIncarnation` deliberately rejects arbitrary bitwise construction and
is not trivially copyable. The lineage test no longer writes that object's raw
representation to a pipe. It exports only a fixed-layout,
trivially-copyable `{kernel_pid, lineage_generation}` observation and verifies
those facts against the live child and expected lineage algebra.

### Build-graph and audit closure

CMake adds a dependency-free test-support library, a runtime contract test, and
a structural audit. All seven inherited consumers link the owner explicitly.
POSIX-only headers, aliases, targets, and tests are platform-guarded.

The raw-fork audit now fails unless production has zero calls, tests have exactly
one implementation call, the 13 inherited spawn sites match the exact inventory,
and all seven fresh-state campaigns use self-exec. Dependent audits were updated
to verify the shared ownership boundary rather than demand local fork/wait
choreography.

## Validation

- parent archive: `AnonSync-rev0834-2026.07.18.09.18-captureowner-pipefrontier-forkexceptioncull-allocatorfreshimage.zip`;
- parent SHA-256:
  `f24b4424813a2163d7724a487d108f8a69bdb09259940a65d34b610bfe65d067`;
- parent ZIP verifier: **25/25**;
- parent directory verifier: **21/21**;
- active source delta: **23 files**, **2,485 insertions**, **602 deletions**;
- patch replay: **211/211 active files**, zero mismatches;
- GCC 14.2 C++20 Debug build with `-O0 -g0`: all targets passed;
- CTest inventory: **122**;
- final bounded complete gate: **122/122**;
- focused direct runtime: **491/491 checks**;
- owner and migrated-caller stress: **90/90 executions**;
- nine changed/dependent source audits: **277/277 checks**; and
- GCC 14.2 ASan/UBSan: **9/9 focused tests**, `detect_leaks=0`.

The final complete CTest gate was intentionally partitioned. No single
uninterrupted 122-test invocation is claimed. The sanitizer result is focused,
not project-wide, and leak detection is not claimed.

## Research-grounded decisions

Linux documents that a multithreaded child after `fork()` may call only
async-signal-safe functions until `execve()`, and that restoring arbitrary
library state with `pthread_atfork()` is generally impracticable. That is why
self-exec remains the default for fresh-state campaigns and the raw-fork callback
is a narrow, test-only exception.

Linux `waitid(..., WNOWAIT)` leaves a terminated child waitable so its exact
identity remains pinned for a later reap. This is the basis for group cleanup
before leader reaping. Linux pidfds can provide a stable reference to one task
and avoid recycled-PID signal races; `clone3(CLONE_PIDFD)` is a plausible future
owner improvement, but one pidfd does not by itself define descendant-group
ownership.

`PR_SET_PDEATHSIG` is not adopted here. Linux defines its parent as the creating
thread, not necessarily the lifetime of the entire parent process; it is also
cleared on fork and in several credential transitions. A deliberate parent-death
contract needs separate design and tests.

## Claim boundary and next work

This revision improves test process ownership and removes avoidable inherited
runtime state. It does not make arbitrary C++ safe after fork, prevent a hostile
child from escaping its group, or provide a sandbox.

The highest-return next process work is a Linux pidfd experiment that keeps
feature detection and process-group semantics explicit. The larger mission
still needs an executable convergence algebra, a crash-cut protocol oracle,
disposable hostile-database interpretation, and a complete privacy/key-lifecycle
specification.
