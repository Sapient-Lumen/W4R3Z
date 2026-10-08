# Sustained synchronous-I/O validation note

One combined stress command ran the 442-check protocol/crash-frontier executable
25 consecutive times and then began repeated reset tests. All 25 protocol runs
passed (11,050 checks) and the first two reset runs passed before the outer
20-minute cloud command invocation was terminated. During the long run the
cloud overlay showed severe synchronous-I/O pressure around forked SQLite reset,
WAL/journal cleanup, and directory synchronization.

The reset executable was then run separately 12 consecutive times and passed
all 12, with each completed iteration reporting 68 checks. The ordinary frozen
source CTest ranges and focused compiler/sanitizer gates also passed.

This evidence does not prove a product deadlock and does not justify ignoring an
unbounded process wait. Existing CTest timeouts remain 60 seconds for reset and
120 seconds for the crash-frontier test. A future exec-based child harness
should add parent-side monotonic deadlines, forced termination, descriptor/state
dumps, and less ambiguous attribution when the kernel blocks in synchronous
I/O. This release claims only the completed iterations.
