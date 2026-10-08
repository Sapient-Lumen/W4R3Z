# Subprocess save crash matrix, private temps, and sync witnesses (rev0962)

## Executive judgment

The highest-risk unfinished Micromax path was not another policy registry. It
was the moment a dirty buffer crosses from private recovery state into the real
document namespace. Earlier tests injected exceptions inside one Python process;
those tests still ran `finally` blocks and could therefore make failure safer
than abrupt process death.

Rev0962 turns that transaction into executable process-death evidence. A fresh
interpreter checkpoints exact bytes, writes the document, and is terminated with
`os._exit(86)` at named boundaries. A second interpreter opens the same state
root and verifies the visible document, retained journal payload, permissions,
and recovery classification. The matrix covers atomic and direct writes on the
cloudtainer's overlay filesystem and on tmpfs.

This is evidence for the tested Linux/POSIX process-crash model. It is not a
universal sudden-power-loss, controller-cache, remote-filesystem, Windows, or
all-mount-options guarantee.

## What was severely wrong

### Payload temps were not private from birth

Atomic save temps previously used the ordinary destination create mode. If the
process died after writing the temp but before replacement or cleanup, exact
unsaved bytes could remain under a discoverable `.micromax-*.tmp` name with
permissions suitable for the eventual document rather than for private working
state.

The writer now creates the inode that will receive document bytes as `0600` and
keeps its file descriptor open through commit. For a new destination it first
creates and deletes an **empty** `0666` mode probe, which observes the directory's
ordinary umask/default-ACL result without changing the process umask and without
ever placing document data in the probe. The committed inode receives the final
mode only after namespace replacement, then the file is synchronized again.

This intentionally chooses confidentiality over temporary availability: a kill
in the tiny post-replace/pre-mode-restore window can leave the committed target
owner-only. It cannot leave the unsaved precommit temp broadly readable.

### One `fsync` request was being mistaken for several completed facts

A requested `fsync=True` did not say whether file data/metadata actually reached
the synchronization call, nor whether the containing directory entry was
synchronized. The Linux `fsync(2)` documentation explicitly says a file fsync
does not necessarily persist its directory entry; the directory needs its own
fsync.

`FileWriteResult` now reports `file_synced` and `directory_synced` separately.
The recovery journal reports the same narrow witnesses for checkpoint
publication and checkpoint retirement. Explicit unsupported-operation errors
produce a false directory witness; real permission/media/I/O errors propagate
instead of being silently converted into success.

### Bounded file workers joined before draining their result

Parent creation, freshness capture, and atomic write workers repeated slightly
different process/queue teardown. They joined the child before consuming its
`multiprocessing.Queue` result and did not close every queue/process resource on
all start, timeout, broken-result, or abnormal-exit paths.

One collector now drains before join, terminates abnormal workers, performs
write-temp cleanup where applicable, closes the queue and process object, and
treats liveness probing itself as fallible. A fully received result joins the
local feeder deterministically. A failed/incomplete receive first calls
`cancel_join_thread()` and then closes the queue, because a terminated producer
can leave the transport corrupted and feeder joining must not become the new
hang. Focused tests pin success, receive failure, join failure, non-exiting child,
start failure, and teardown rather than relying on eventual garbage collection.

## Transaction stages now exercised

Checkpoint stages:

1. private checkpoint temp created;
2. checkpoint temp file synchronized;
3. before and after journal replacement;
4. checkpoint directory synchronized.

Atomic document stages:

1. private document temp created;
2. document temp synchronized;
3. before and after replacement;
4. final mode restored;
5. committed file metadata synchronized;
6. document directory synchronized.

Retirement stages:

1. before dismissal;
2. after journal unlink;
3. after journal-directory synchronization.

Direct-write evidence also kills the process immediately after truncation and
after file synchronization. The former must retain exact recovery payload while
classifying the disk target as changed; the latter must classify the committed
bytes as already persisted.

## Observed filesystem matrix on 2026-07-17

The same 13-test process-death matrix passed with pytest temporary roots on:

- `/mnt/data` — Linux `overlay` filesystem: **13 passed**;
- `/dev/shm` — Linux `tmpfs`: **13 passed**.

The ordinary in-process recovery, permission, synchronization-error, symlink,
freshness, timeout, and cleanup slices also passed. Exact commands and scoped
counts are recorded in `docs/history/REV0962_TESTS.md`.

## Research that changed the implementation

- Python `multiprocessing` documentation warns that joining a process before its
  queued items are consumed can deadlock, that terminating a queue producer can
  corrupt the transport, and that `cancel_join_thread()` permits exit without
  waiting for an unflushable feeder. The collector therefore drains before join
  and uses feeder cancellation only after an incomplete receive.
  <https://docs.python.org/3/library/multiprocessing.html>
- Python `os` documentation: buffered file objects must be flushed before
  `os.fsync`, and `os.replace` is the replacement primitive exposed by Python.
  <https://docs.python.org/3/library/os.html>
- Linux `fsync(2)`: synchronizing a file does not necessarily synchronize the
  directory entry; an explicit directory fsync is needed.
  <https://man7.org/linux/man-pages/man2/fsync.2.html>
- Pillai et al., *All File Systems Are Not Created Equal* (OSDI 2014):
  application crash protocols depend on filesystem-specific persistence
  properties, so evidence must name the filesystems actually exercised.
  <https://www.usenix.org/conference/osdi14/technical-sessions/presentation/pillai>

These sources support ordering and scoping choices; they do not convert a test
matrix into a proof about every storage stack.

## Residual risk and next correction

- A real kill can leave private checkpoint or document temp files behind. They
  no longer disclose group/world-readable payload bytes, but repeated crashes
  can still waste disk. Automatic cross-process deletion would be unsafe without
  ownership/lease evidence; the next cleanup step should be a bounded,
  inspectable stale-temp inventory with conservative ownership checks.
- The post-replace owner-only window can permanently narrow a committed file's
  mode after a crash. A future recovery record could retain the intended final
  mode and offer an explicit fingerprint-verified repair; startup discovery
  should remain read-only.
- The matrix does not issue power cuts, bypass volatile storage caches, or cover
  ext4/xfs/btrfs/APFS/NTFS/network filesystems. A release claim should add
  controlled VM/power-loss testing on each declared platform rather than infer
  those guarantees from overlayfs and tmpfs.
- Direct writes remain inherently able to expose an empty or partial target if
  killed after truncate. Recovery protects the user's exact buffer, not the
  direct-write target's atomicity.
