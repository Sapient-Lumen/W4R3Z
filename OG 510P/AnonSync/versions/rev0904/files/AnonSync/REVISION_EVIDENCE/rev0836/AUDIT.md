# Audit — AnonSync rev0836

## Boundary under review

Rev0835 established the right order for successful process-topology completion:
observe the exact leader with `WNOWAIT`, kill surviving group members while the
leader remains waitable, then reap that leader. The rev0836 audit followed the
capture wrappers beyond that successful transition and found a stale-authority
escape.

Both captured-output implementations could retain a numeric process-group value
after the exact leader had been reaped. If a descriptor remained open and a
later drain timeout, read error, poll error, or byte-budget failure occurred,
the catch path could issue another `kill(-pgid, SIGKILL)`. The owner no longer
held the exact leader evidence that justified using that number. Rev0835’s
integration tests passed because they proved descendant removal, not the
absence of a signal after reap.

## Refactor and correction

Rev0836 adds a move-only, test-only `TestProcessTopologyOwner` with one compiled
implementation. It owns exact leader and optional top-level group together.
`try_complete_exit_or_throw()` combines observation and completion in one
transition, clears both identifiers before returning status, and treats
`ECHILD` as authority relinquishment before propagation. Destructive cleanup
consumes member state before its first syscall.

The inherited and self-exec wrappers now own capture descriptors plus the
common topology owner; neither wrapper contains a direct `kill`, `waitid`, or
`waitpid` call. All nine direct lifecycle syscall sites are in the one leaf
implementation. CMake prevents that target from gaining dependencies or
entering the production runtime graph.

## New proof surface

A linker-wrap syscall-script oracle executes 12 scenarios and 24 assertions,
including pending observation, exact completion, no signal after completed
return, leader-only completion, `EINTR`, `ESRCH`, foreign `si_pid`, observation
`ECHILD`, hard observation failure, group-signal `EPERM`, final-wait `ECHILD`,
impossible blocking-wait return, consume-before-syscall cleanup, and exact move
transfer.

Linux integration tests add escaped post-reap descriptor writers for both
wrappers. They force output-drain timeout after the exact leader has completed
and prove the escaped process remains alive until the fixture explicitly
cleans it. Every intentionally infinite hostile descendant now arms an
independent 15-second fail-safe alarm.

## Measured result

- active implementation projection: **215 files**, **16,741,290 bytes**;
- source delta: **16 files**, **1,818 insertions**, **440 deletions**;
- direct lifecycle syscall sites: **9**, all in one compiled owner;
- wrapper lifecycle syscall sites: **0**;
- focused deterministic/integration runtime: **85/85 checks**;
- repeated process-owner campaign: **60/60 executions**;
- changed/dependent structural audits: **193/193 checks**;
- registered source-audit gate: **36/36 tests**;
- full CTest gate: **124/124 in one uninterrupted invocation**;
- GCC 14.2 ASan/UBSan focused runtime: **3/3 targets, 85/85 checks**;
- Clang 17 independent build/runtime: **3/3 targets, 85/85 checks**; and
- final dependency closure: **zero compile or link steps**.

The source patch replays exactly from the sealed rev0835 parent to all 215
active files.

## Claim boundary

This revision hardens test infrastructure. It does not make arbitrary post-fork
C++ safe, prevent process-group/session escape, provide pidfd or cgroup
containment on this Linux 4.4 cloudtainer, bound every possible blocking reap,
or prove production convergence, crash completeness, confidentiality,
anonymity, metadata hiding, or key lifecycle.
