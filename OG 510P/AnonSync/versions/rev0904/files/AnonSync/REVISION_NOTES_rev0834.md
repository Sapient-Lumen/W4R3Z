# AnonSync rev0834 — capture owner, pipe frontier, raw-fork exception removal

## Executive result

Rev0834 removes the last reviewed non-inheritance raw-`fork()` bridge from the
active C++ test tree. The SQLite transaction allocator-fault campaign now uses
the common pinned fresh-image process owner and receives worker evidence through
a bounded, concurrent stdout/stderr capture protocol.

The core correction is an ownership correction: process termination, child
status, stdout bytes, stderr bytes, pipe EOF, byte budgets, and deadline are no
longer independent observations assembled by the caller. They are consumed as
one move-only capability, and every exceptional path disposes of that complete
capability before reporting failure.

## What changed

### Capture-capable fresh-image owner

`SelfExecTestProcess` now optionally owns two close-on-exec capture pipes in
addition to the child PID/process group.

- `pipe2(O_CLOEXEC)` creates race-free close-on-exec endpoints.
- Endpoint descriptors are promoted above the standard/pinned descriptor range.
- Spawn file actions duplicate only the child write ends onto stdout/stderr,
  then apply the existing close-from fence.
- Only parent read ends receive `O_NONBLOCK`; child writes retain ordinary
  blocking backpressure.
- `wait_for_exact_exit_with_output()` drains stdout and stderr concurrently,
  checks the leader with `waitpid(WNOHANG)`, and uses one steady-clock deadline.
- Each stream has an explicit caller budget plus a 16 MiB hard ceiling.
- Completion requires a reaped leader and EOF on both streams.
- Timeout, output overflow, read/poll/wait failure, and allocation failure kill
  the process group, reap any owned leader, close both descriptors, and then
  throw.
- Exact-status mismatch includes bounded escaped stdout/stderr context after
  all authority has already been consumed.
- Plain and capture waits reject the wrong owner mode without consuming it.

### Executable capture oracle

The dedicated owner test grew from 11 to 31 checks. It now proves:

- PID plus both descriptor owners transfer together under move construction;
- exact stdout and stderr remain separate;
- a child can write the actual pipe capacity plus 4 KiB to each stream and
  complete without deadlock;
- output bytes remain exact through that frontier;
- overflow and timeout synchronously kill/reap and close descriptors;
- plain/capture API mismatch fails closed and remains recoverable; and
- the parent descriptor count is unchanged after the complete capture corpus.

### Allocator campaign migration

The allocator campaign no longer has local raw `fork`, pipe, `dup2`, exec, read,
close, or `waitpid` choreography. Each of its 318 workers is launched with the
versioned helper instruction
`--anonsync-sqlite-transaction-allocator-fault-worker-v1`, verifies the pinned
fresh-image boundary before argument parsing or SQLite initialization, and
returns separately bounded stdout/stderr evidence through the common owner.
Unexpected stderr is rejected.

The fault frontier remains **642 checks, 318 isolated workers, and 312 injected
cutpoints** over one-shot and sticky allocator failure modes.

## Audit and refactor result

Four changed-boundary audits pass **245/245**:

- raw-fork boundary: **9/9**;
- self-exec process owner: **35/35**;
- SQLite transaction allocator fault campaign: **101/101**; and
- SQLite transaction-stack authority: **100/100**.

The exact raw-fork inventory is now:

- production calls: **0**;
- test calls: **15**;
- test translation units: **8**;
- inherited-state or process-lineage probes: **15**;
- reviewed fork-exec bridges: **0**; and
- fresh-image migrated campaigns: **5**.

The structural audits also bind CMake linkage, helper versioning, child-boundary
ordering, blocking child/nonblocking parent pipe semantics, `dup2` before
close-from ordering, concurrent stream draining, the monotonic deadline, byte
ceilings, EOF requirements, failure cleanup, and the runtime over-capacity
oracle.

## Validation

- rev0833 parent archive SHA-256:
  `2d08478acfa8f34e3336a8141cb73bd39348b7e6c04eb39b5514c1b45a15209a`;
- parent ZIP verifier: **25/25**;
- parent directory verifier: **21/21**;
- active source delta: **9 files**, **915 insertions**, **243 deletions**;
- patch replay: **207/207 active files**, zero mismatches;
- GCC 14.2 Debug all-target build: passed;
- final dependency closure: `ninja: no work to do.`;
- CTest inventory: **120**;
- post-closure bounded CTest gate: **120/120**;
- focused direct runtime: **673/673 checks**;
- focused CTest: **2/2**;
- self-exec stress: **50/50** executions;
- allocator stress: **10/10** complete campaigns;
- Clang 17 `-Werror` focused build and runtime: passed; and
- Clang 17 ASan/UBSan focused build and runtime: passed with
  `detect_leaks=0`.

## Research-grounded decisions

POSIX spawn file actions define ordered descriptor duplication in the child
before the new process image begins. Linux `pipe2(O_CLOEXEC)` atomically applies
close-on-exec to both endpoints; because `O_NONBLOCK` supplied to `pipe2()` would
apply to both open file descriptions, rev0834 deliberately sets nonblocking
mode only on parent read ends after creation. Linux `poll()` reports readiness,
hangup, errors, and invalid descriptors, and a pipe hangup does not imply EOF
until buffered bytes are consumed. The implementation therefore drains before
and after polling and accepts completion only after read returns zero on both
streams.

## Claim boundary and next work

The capture owner is test infrastructure, not a hostile worker sandbox. It has
no pidfd, parent-death signal, namespaces, seccomp, Landlock, credential change,
or kernel resource limits. A deliberately escaping or privilege-changing child
is outside the current contract.

The next high-return process audit is the remaining 15 inheritance-specific raw
fork calls. Raw inheritance may be semantically necessary, but blocking parent
pipe/read/wait choreography is not. A reusable bounded inherited-process owner
should be extracted where it can preserve the exact inherited-state fact under
test. Separately, the larger mission still needs an executable convergence
algebra, crash-cut protocol oracle, hostile-database worker isolation, and an
explicit confidentiality/anonymity/key-lifecycle design.
