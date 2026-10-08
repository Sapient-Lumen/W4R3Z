# Research notes — rev0835

Research used current primary Linux interface documentation retrieved on
2026-07-18.

## Raw fork is an exception, not the process-launch default

Linux `fork(2)` documents that a multithreaded child contains only the calling
thread while copied mutex and condition-variable states remain, and that the
child may safely call only async-signal-safe functions until `execve()`.
`pthread_atfork(3)` further says that restoring arbitrary application/library
state is generally too difficult to be practicable.

Sources:
- https://man7.org/linux/man-pages/man2/fork.2.html
- https://man7.org/linux/man-pages/man3/pthread_atfork.3.html

Design consequence: use pinned self-exec for any campaign that does not need
inherited state. Keep raw-fork callbacks test-only, inventory-bound, and as
small as the inherited fact permits.

## Preserve leader identity through group cleanup

Linux `waitid(2)` defines `WNOWAIT` to leave a terminated child waitable so a
later wait can retrieve it again. Rev0835 uses that property as an identity
seal: observe terminal leader status without reaping, terminate remaining owned
group members while the leader PID is still pinned by the zombie, then reap the
exact leader.

Source: https://man7.org/linux/man-pages/man2/waitid.2.html

This supports the corrected local topology, but it is not universal process-tree
containment. Process groups are cooperative namespace structure; a hostile
child can attempt to escape them.

## pidfds are the next single-task identity primitive

Linux `pidfd_open(2)` returns a descriptor referring to a task. The documentation
notes conditions under which opening a child after fork remains race-safe and
recommends creating the child with `CLONE_PIDFD` when asynchronous reaping can
interfere. `pidfd_send_signal(2)` explains that a pidfd avoids the recycled-PID
race of PID-based signaling. `clone3(CLONE_PIDFD)` can return the pidfd as part
of child creation.

Sources:
- https://man7.org/linux/man-pages/man2/pidfd_open.2.html
- https://man7.org/linux/man-pages/man2/pidfd_send_signal.2.html
- https://man7.org/linux/man-pages/man2/clone3.2.html

Inference: a future Linux owner should prototype feature-detected
`clone3(CLONE_PIDFD)` or a carefully constrained `pidfd_open()` path for exact
leader ownership. A pidfd names one task; descendant/group authority still needs
an explicit model and executable escape/cleanup tests.

## Parent-death signals require a separate contract

Linux `PR_SET_PDEATHSIG` defines the parent as the thread that created the child,
not the lifetime of the whole multithreaded process. The setting is cleared for
a child of fork and by several credential transitions.

Source: https://man7.org/linux/man-pages/man2/pr_set_pdeathsig.2const.html

Design consequence: do not silently add `PR_SET_PDEATHSIG` as a universal
cleanup fix. Parent death, creator-thread death, subreaper adoption, credential
changes, and helper policy need a named contract and independent tests.
