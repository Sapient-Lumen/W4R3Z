# AnonSync rev0843 research notes

Accessed 2026-07-19. These primary or project-authoritative sources informed the
implementation and audit; citation does not imply that AnonSync implements every
mechanism described.

## Positional descriptor reads

Linux `pread(2)` reads at an explicit offset from the start of the file and does
not change the file offset. The manual also notes its value when multiple threads
perform I/O on the same descriptor without being affected by offset changes.
Rev0843 uses that semantic to freeze a borrowed descriptor from byte zero without
consuming the caller's shared offset.

- Linux man-pages, `pread(2)`:
  https://man7.org/linux/man-pages/man2/pread.2.html
- POSIX Issue 7 `read`/`pread` family (historical stable specification):
  https://pubs.opengroup.org/onlinepubs/9699919799/functions/read.html

## Open files and removed names

`unlink(2)` removes a name. When the final name is removed while a process still
holds the file open, the object remains accessible until the last descriptor is
closed. Readable bytes therefore do not prove that a current namespace name still
selects the object. Rev0843 rejects a pre-observation `st_nlink == 0` and requires
link-count stability across the freeze.

- Linux man-pages, `unlink(2)`:
  https://man7.org/linux/man-pages/man2/unlink.2.html
- POSIX `fstat(3p)` open-file observation:
  https://man7.org/linux/man-pages/man3/fstat.3p.html

## Namespace confinement remains separate

`pread` and `fstat` bind I/O to an opened object but do not constrain how parent
path components were resolved. Linux `openat2(2)` supplies explicit resolution
policies for a future directory-descriptor owner. The current cloud host reports
Linux 4.4, predating `openat2`; rev0843 therefore makes no runtime claim for it.

- Linux man-pages, `openat2(2)`:
  https://man7.org/linux/man-pages/man2/openat2.2.html
- Linux kernel path lookup documentation:
  https://docs.kernel.org/filesystems/path-lookup.html

## Directory-entry durability remains open

Synchronizing file contents does not necessarily synchronize the directory entry
that names the file. Journal creation, ledger rename, journal unlink, and each
containing-directory sync need to be one modeled crash protocol.

- Linux man-pages, `fsync(2)`:
  https://man7.org/linux/man-pages/man2/fsync.2.html
- SQLite atomic commit assumptions:
  https://www.sqlite.org/atomiccommit.html

## Speculation

The descriptor owner is a useful seam for a disposable hostile-input worker: a
parent can resolve and open under trusted directory authority, pass only a sealed
descriptor, retain lifetime supervision, and accept a bounded response. This is
still only one layer; resource limits, namespaces, syscall filtering, filesystem
policy, deadlines, and protocol validation remain necessary.
