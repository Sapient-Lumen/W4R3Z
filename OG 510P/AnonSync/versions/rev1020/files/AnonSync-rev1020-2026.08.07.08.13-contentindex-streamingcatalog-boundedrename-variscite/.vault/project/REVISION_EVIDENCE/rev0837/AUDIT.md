# Audit — AnonSync rev0837

## Boundary under review

The daemon heartbeat and recovery-workflow readers shared a hidden helper inside
`src/sync_domain.cpp`. The name promised a bounded regular-file read, but the
implementation treated the first `fstat().st_size` as the complete length. It
allocated exactly that many bytes, stopped when they were filled, and never
proved EOF or re-inspected the opened object.

The exact rev0836 helper therefore accepted a three-byte prefix while a scripted
fourth byte remained unread. It also opened without `O_NONBLOCK`, so a path
raced to a FIFO could block in `open()` before `fstat()` had a chance to reject
its type. The included behavior witnesses record both outcomes: prefix
acceptance and a no-writer FIFO blocking past a one-second external bound.

The Windows branch had a separate pathname-authority split: it inspected the
path with `symlink_status()` and `file_size()`, then delegated to another path
open. That was neither one opened-object observation nor a bounded read.

## Refactor and correction

Rev0837 extracts one dependency-free invariant owner:
`read_sync_bounded_regular_file_no_symlink_or_throw()`. Both production callers
include its 21-line header and link one 351-line compiled leaf. The old hidden
helper and the CLI's cross-translation-unit forward declaration are gone.
`sync_domain.cpp` falls from 15,257 to 15,202 lines; `sync_operator_cli.cpp`
falls from 1,431 to 1,428.

On POSIX the owner opens with `O_NOFOLLOW`, `O_NONBLOCK`, close-on-exec, and
`O_NOCTTY`; binds observations to that descriptor; rejects non-regular objects;
reads until EOF with a one-byte ceiling sentinel; retries `EINTR`; compares
identity, size, mtime, and ctime before and after; and makes close failure
visible without replacing an earlier read/inspection failure.

On Windows it uses one `CreateFileW` handle opened with
`FILE_FLAG_OPEN_REPARSE_POINT`, rejects reparse/directory/device objects, reads
through EOF, and compares handle identity, size, last-write time, and attributes
before and after. Both platforms reject an embedded NUL before the operating
system can observe a shorter pathname than C++ validated.

CMake compiles the leaf outside the core source aggregation, links it privately
into the core, and fails configuration if either focused proof regains a core
link dependency. The runtime and deterministic syscall tests each expose only
two first-party translation units: the leaf and that proof.

## New proof surface

- live filesystem contract: **12/12**, including exact ceiling edges, missing
  files, directories, final-component symlinks, embedded NUL, and a FIFO
  liveness bound;
- deterministic Linux syscall oracle: **25/25**, including EOF, growth,
  pre/post metadata drift, `EINTR`, read error, close error, error precedence,
  exact open flags, and cleanup ownership;
- source/dependency audit: **21/21**;
- repeated focused campaign: **740/740 checks** over twenty iterations;
- Clang 17 focused compile/runtime: **37/37**; and
- GCC 14.2 ASan/UBSan focused runtime: **37/37**, with leak detection disabled.

The immutable zero-work final build passed all **127/127** registered tests in
non-overlapping CTest ranges, cross-checked against the exact `ctest -N`
inventory. The active source patch replays exactly across **220/220**
active files.

## Claim boundary

`O_NOFOLLOW` protects only the final POSIX path component. Ancestors are not yet
anchored to a trusted directory descriptor. `O_NONBLOCK` prevents FIFO-open
blocking but does not guarantee a wall-clock bound for regular files on FUSE,
remote, or failing storage. Pre/post metadata equality is a strong consistency
screen, not a cryptographic filesystem snapshot against a privileged writer
that can restore metadata. Windows code was source-reviewed but neither built
nor executed because this cloudtainer has no Windows or MinGW toolchain.

This revision does not prove arbitrary crash-cut completeness, hostile-worker
sandboxing, distributed convergence, confidentiality, anonymity, metadata
hiding, key lifecycle, or secure erasure.
