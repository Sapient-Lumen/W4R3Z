# Research notes — rev0834

Research was limited to primary interface specifications and directly informed
the capture-owner design.

## POSIX spawn file actions

The Open Group POSIX.1-2024 specification states that
`posix_spawn_file_actions_adddup2()` adds a `dup2()` action applied in the child
process as part of spawn processing. This supports the ordered topology used
here: duplicate the pinned executable to descriptor 3, duplicate capture write
ends to descriptors 1 and 2, then execute the Linux close-from action.

Source: https://pubs.opengroup.org/onlinepubs/9799919799.2024edition/functions/posix_spawn_file_actions_adddup2.html

POSIX `posix_spawn()` creates the child from the specified process image and
applies the configured spawn attributes/file actions around that transition.

Source: https://pubs.opengroup.org/onlinepubs/9799919799/functions/posix_spawn.html

## Linux pipe semantics

Linux `pipe2(O_CLOEXEC)` sets close-on-exec on both returned descriptors. The
manual also states that `O_NONBLOCK` passed to `pipe2()` sets nonblocking status
on both new open file descriptions. Rev0834 therefore creates the pipe with only
`O_CLOEXEC`, then sets `O_NONBLOCK` exclusively on the parent read endpoint so
child writes retain ordinary backpressure.

Source: https://man7.org/linux/man-pages/man2/pipe.2.html

## Linux poll and EOF semantics

Linux `poll()` multiplexes readiness over descriptor arrays and reports
`POLLERR`, `POLLHUP`, and `POLLNVAL` through `revents`. The manual explicitly
notes that hangup on a pipe does not imply immediate EOF: subsequent reads return
zero only after outstanding buffered data is consumed. Rev0834 therefore drains
each nonblocking descriptor before polling and again on every loop, and closes a
stream owner only when `read()` returns zero.

Source: https://man7.org/linux/man-pages/man2/poll.2.html

## Linux wait semantics

`waitpid(..., WNOHANG)` provides a nonblocking leader observation, allowing pipe
draining and child-exit checks to share one monotonic deadline instead of
serializing a blocking read and a blocking wait.

Source: https://man7.org/linux/man-pages/man2/wait.2.html

## Inference and remaining gap

These interfaces support bounded evidence collection, not hostile process
containment. A child that escapes its process group, changes privilege, consumes
unbounded resources outside the two streams, or survives parent death is beyond
this owner. pidfds, parent-death policy, resource limits, namespaces, seccomp,
and Landlock remain separate future layers.
