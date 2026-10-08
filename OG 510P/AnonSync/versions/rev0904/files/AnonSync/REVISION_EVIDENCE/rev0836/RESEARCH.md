# Research notes — AnonSync rev0836

## Exact observation without early identity release

POSIX `waitid()` with `P_PID` selects one exact child. `WNOHANG` makes the
observation nonblocking, and `WNOWAIT` keeps a reported child in a waitable
state so a later wait can reap it. Linux additionally documents the portable
`WNOHANG` pattern used here: zero `si_pid` before the call and treat a remaining
zero as “no waitable child.”

Sources:

- https://pubs.opengroup.org/onlinepubs/9699919799/functions/waitid.html
- https://man7.org/linux/man-pages/man2/wait.2.html
- https://man7.org/linux/man-pages/man3/waitid.3p.html

Rev0836 uses that sequence to keep the exact leader unreaped while the
leader-equal process-group number is used. This is a Linux test-runtime
ownership argument, not a claim that a raw integer is a generally portable
capability.

## Why pidfds are the stronger future primitive

A PID file descriptor is a stable kernel reference to a process and avoids the
classic numeric-PID reuse race. Linux documents `pidfd_send_signal()` and, since
Linux 6.9, `PIDFD_SIGNAL_PROCESS_GROUP` for signaling the process group of a
pidfd-referenced leader.

Source:

- https://man7.org/linux/man-pages/man2/pidfd_send_signal.2.html

The cloudtainer used for rev0836 runs Linux 4.4.0, so neither `pidfd_open()` nor
the Linux 6.9 process-group signaling flag is available. The current WNOWAIT
owner is therefore a constrained compatibility implementation. A future Linux
backend should prefer pidfd acquisition at spawn, exact pidfd polling/waiting,
and group signaling through a pidfd when the runtime kernel supports the full
required set. Feature detection must be behavioral and fail closed; a header
constant alone is not runtime support.

## Why process groups are not complete topology containment

A cooperative descendant can create a new session or process group before
cleanup. Process-group ownership therefore cannot prove containment of hostile
or arbitrary descendants. Linux cgroup v2 exposes `cgroup.kill`; kernel
documentation states that writing `1` kills the cgroup tree, handles concurrent
forks, and is protected against migrations. That is a materially stronger
workload-topology primitive when the caller has a delegated cgroup subtree.

Source:

- https://docs.kernel.org/admin-guide/cgroup-v2.html

The current cloudtainer does not provide the required delegated cgroup
administration, so rev0836 does not claim cgroup containment. A future worker
supervisor could combine pidfd leader identity with a delegated cgroup for
whole-tree resource ceilings and teardown.

## Design inference

The project’s recurring pattern is that an observation must not outlive the
identity evidence that authorizes the next operation. For process lifecycle,
that suggests a typed transition capability rather than exposing PID/PGID
integers or separate “observe” and “complete” methods. Rev0836 is a small
instance of that broader design: the status result is emitted only after the
owner has consumed every numeric authority that could otherwise escape into a
later error path.
