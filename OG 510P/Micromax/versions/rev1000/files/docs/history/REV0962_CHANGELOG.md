# Micromax revision 0962

## Outcome

Rev0962 closes the riskiest unfinished save-recovery evidence gap. Save attempts
can now be killed in a fresh process at named checkpoint, document-commit,
permission, directory-sync, and journal-retirement boundaries; restart from the
same state root produces an asserted document/journal classification.

## Product changes

- Made every atomic temp that receives unsaved document bytes owner-only from
  inode creation, not after payload exposure.
- Preserved ordinary new-file mode without thread-unsafe umask mutation by using
  an empty mode probe; restored the intended mode only after atomic commit.
- Synchronized the committed inode again after permission restoration, then
  synchronized the containing directory where supported.
- Exposed separate file and directory synchronization witnesses for document
  writes, recovery checkpoint publication, and checkpoint retirement.
- Kept unsupported directory sync honest as a false witness while propagating
  real I/O, permission, and media errors.
- Added real `os._exit` crash points through checkpoint, atomic/direct document
  writes, and journal dismissal.

## Audit/refactor changes

- Replaced three duplicated file-worker join/queue paths with one drain-before-
  join collector.
- Closed queue and process resources on success, timeout, receive failure,
  abnormal child exit, and process-start failure paths; fully consumed results
  join the feeder, while incomplete/corrupt receive paths cancel that join so
  teardown cannot block on a killed producer's partial frame.
- Made worker liveness probing best-effort so a broken process object cannot mask
  the original failure or queue cleanup.
- Removed the false implication that one requested `fsync` proves both file and
  namespace synchronization.

## Honest boundary

The matrix proves observed restart behavior after process death on this
cloudtainer's overlayfs and tmpfs roots. It does not prove behavior under power
loss, volatile hardware caches, every mount mode, remote filesystems, or
Windows. A crash between replacement and mode restoration can leave a committed
file owner-only; that is a deliberate confidentiality-first failure mode and is
now documented rather than hidden.
