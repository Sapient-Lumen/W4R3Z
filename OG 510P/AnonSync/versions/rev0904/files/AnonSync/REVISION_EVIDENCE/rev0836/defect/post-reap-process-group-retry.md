# Defect: process-group authority survived exact leader reap

## Parent behavior

Rev0835 correctly changed both test-process owners to observe the exact leader
with `waitid(P_PID, ..., WNOWAIT)`, terminate remaining group members while the
leader was still waitable, and then reap that leader. The captured-output paths,
however, split that terminal transition across wrapper state:

- the inherited owner set `leader_ = -1` after reap but kept `process_group_`
  until every capture descriptor reached EOF;
- the self-exec owner copied `child_` into a local `process_group`, reaped the
  child, set `child_ = -1`, and retained the copied group number while draining;
- a later timeout, poll error, read error, or output-budget failure entered the
  catch path and could issue another `kill(-pgid, SIGKILL)`.

At that point the exact leader had already been reaped. The strongest evidence
that pinned the numeric identity was gone, so the later negative-PID signal was
not authorized by the owner state. The parent tests still passed because they
proved descendant cleanup, not that every post-reap failure path had lost the
ability to signal.

`parent-post-reap-numeric-authority-witness.json` binds the exact rev0835 parent
files and records the relevant control-flow needles.

## Correction

Rev0836 introduces one move-only `TestProcessTopologyOwner`. It owns the exact
leader and optional top-level group together. `try_complete_exit_or_throw()` is
one indivisible owner transition:

1. observe the exact leader using `waitid(P_PID, ..., WEXITED | WNOHANG |
   WNOWAIT)`;
2. while that exact leader remains waitable, signal the owned group;
3. reap that exact leader with `waitpid(leader, ..., 0)`; and
4. clear both numeric identifiers before returning the completed status.

The capture wrappers no longer cache or retain a process-group number. Any
later output-drain failure can close descriptors, but `terminate_and_reap` sees
an inactive topology owner and cannot issue a stale group signal.

## Executable proof

The deterministic linker-wrap oracle scripts `waitid`, `kill`, and `waitpid`
and proves, among other branches, that exact completion clears authority before
return and that later cleanup performs zero lifecycle syscalls. Linux integration
tests additionally keep an escaped descriptor writer alive after the leader is
reaped, force the drain timeout path, and prove that the escaped process is not
signaled by stale group authority.
