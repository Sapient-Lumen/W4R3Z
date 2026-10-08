# Rev0819 research notes

Research informed the authority boundary but is not represented as a universal
portability or durability claim.

- POSIX/Linux `unlink` and `unlinkat` remove a directory entry identified by a
  pathname at the time of the deletion call. Their interfaces carry no
  expected-device/inode argument. Therefore `fstatat(name)` followed by
  `unlinkat(name)` is observation followed by an unconditional name operation,
  not a conditional delete:
  <https://pubs.opengroup.org/onlinepubs/9699919799/functions/unlink.html>
  and <https://man7.org/linux/man-pages/man2/unlink.2.html>
- `ftruncate` operates on the object denoted by an already-open descriptor. It
  is suitable for best-effort payload sanitation without re-resolving a mutable
  path: <https://man7.org/linux/man-pages/man2/ftruncate.2.html>
- `fsync` likewise acts on an open descriptor. Syncing a file and syncing its
  containing directory are distinct durability steps:
  <https://man7.org/linux/man-pages/man2/fsync.2.html>
- `renameat` binds source and destination lookup to directory descriptors and
  remains the namespace publication point in this implementation:
  <https://man7.org/linux/man-pages/man2/rename.2.html>
- `openat2` can constrain path resolution, but those controls do not create an
  expected-inode form of unlink. It can strengthen a future Linux-specific
  reaper's lookup phase without solving deletion authority by itself:
  <https://man7.org/linux/man-pages/man2/openat2.2.html>
- `linkat` can create directory entries for an already-open object in some
  designs, but it is not an atomic compare-and-unlink primitive:
  <https://man7.org/linux/man-pages/man2/link.2.html>

## Speculation: an authority-bound residue reaper

A future reaper should be a separate protocol owner, not a delayed call to the
publisher's old cleanup routine. A plausible design would use a versioned,
private temp namespace and require evidence for directory identity, process
incarnation or expired lease, artifact type, private mode, link count, naming
schema, age, and non-membership in any live publication transaction. It should
open and revalidate the exact artifact, quarantine it under coordinated
namespace authority, and only then delete. A recognizable prefix or stale
mtime alone is not authority. The reaper should expose retained/quarantined/
deleted outcomes and be exercised under name replacement, hard-link, symlink,
restart, clock-skew, and concurrent-publisher traces.
