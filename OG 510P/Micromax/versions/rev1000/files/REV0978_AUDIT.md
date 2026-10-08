# Rev0978 audit — completion means drained and reaped

## Highest-risk findings

Two finite owners on ordinary product paths could declare the wrong result:

- filesystem workers joined before their result queue was drained, so a large
  successful read/list result filled the queue pipe, kept the child alive, and
  was misreported as a timeout; and
- bounded subprocess capture returned after the direct child exited even when a
  background descendant retained stdout/stderr, leaving blocked daemon reader
  threads and an unowned process.

The first failure affected editor open/recovery/help plus `ed.fs-read`,
`ed.fs-list`, metadata, and completion paths. The second affected the shared
argv/shell owner used by `ed.shell`, external clipboard tools, and bounded browser
launch.

## Substantive correction

All bounded contained-filesystem worker families now use one receive-before-join
collector with finite receive time, short reap grace, terminate/kill fallback,
and queue/process-handle cleanup on success, timeout, crash, and broken IPC.
Large real editor/hostcall payload regressions prove the corrected ordering.

Shared subprocess capture now treats pipe EOF as part of completion. After a
direct child stops, lingering I/O threads trigger owned process-group cleanup
and, on Linux, exact capture-pipe holder discovery through `/proc/<pid>/fd`.
TERM/KILL escalation is finite and targets stable holder identities, not their
whole process groups. Linux uses pidfds when available and revalidates both pipe
ownership and process start time before the numeric fallback. Stdio-detached
background work—including a same-group sibling of a pipe holder—is preserved
because it owns no Micromax descriptor.

## Audit/refactor

- deleted five duplicated filesystem start/join/get/cleanup variants in favor of
  one lifecycle owner;
- folded the older special-case batched-stat drain loop into the same owner;
- named process-capture threads and replaced per-thread fixed waits with one
  absolute drain deadline;
- tightened already-exited process-group escalation so same-group descendants
  are not mistaken for a complete tree;
- removed collateral process-group signaling from Linux exact-holder cleanup,
  preserving redirected siblings beside a leaking pipe owner;
- uses pidfd-stable signaling where Python and the kernel support it, with a
  narrower start-time-and-pipe revalidation fallback on older Linux; and
- extended structural audit checks for receive-before-join, abnormal IPC release,
  exact-pipe cleanup, and detached-job preservation; and
- corrected the generated handoff so current audit/changelog/test evidence is
  included while the oldest root evidence triplet rotates to history at the fixed
  64-document ceiling.

## Waste corrected

The linked rev0977 tree could spend a full timeout on work that had already
succeeded, repeatedly spawn replacement filesystem workers after false failures,
and accumulate reader threads/processes after apparently successful shell or
clipboard commands. Rev0978 removes those false retries and makes capture-resource
completion an explicit postcondition of the existing bounded process owner.

## Residual risk

No claim is made for preemptible `Process.start()`/`Popen`, Windows Job Objects,
non-Linux escaped-session pipe discovery, atomic numeric-PID fallback, total
memory, syscalls, native crashes, or hostile-code isolation. A Queue receive that
has already entered an incomplete/corrupt frame is also not made asynchronously
preemptible by this ordering fix. `/proc` scanning is exceptional best-effort
cleanup, not a process registry. See
`docs/935-process-capture-pipe-ownership.md`.
