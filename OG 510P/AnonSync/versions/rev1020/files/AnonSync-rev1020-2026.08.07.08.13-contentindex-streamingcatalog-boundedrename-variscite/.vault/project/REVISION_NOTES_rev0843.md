# AnonSync rev0843

## Mission increment

A pathname is only one way to select an object, and a file descriptor is only a
borrowed observation until its lifetime, offset, object identity, topology, byte
ceiling, and metadata stability are made explicit. Rev0843 extracts that proof
from the pathname adapter into a reusable C++ owner.

## Delivered

- Added `FrozenSyncPosixRegularFileSnapshot`, a dependency-light owner for one
  exact bounded observation of a caller-owned POSIX descriptor.
- Replaced shared-offset `read(2)` with `pread(2)` from byte zero. The owner never
  calls `close(2)` or `lseek(2)`, preserving the caller's descriptor ownership and
  shared file offset on success and rejection.
- Centralized byte-limit policy for the pathname adapter and descriptor owner,
  including positive limits, `size_t`, `std::string::max_size()`, and POSIX
  `off_t` frontiers.
- Retained the one-byte EOF sentinel rather than trusting the initial `st_size`
  as a read length.
- Bound the frozen observation to pre/post `fstat(2)` identity, size, link count,
  modification time, and change time.
- Made namespace topology policy explicit: ordinary observations allow a stable
  named hard-linked object; authority-bearing observations require exactly one
  link; an already unlinked open descriptor is rejected.
- Reduced `sync_bounded_regular_file.cpp` by moving the POSIX observation state
  machine into its own 158-line translation unit.
- Expanded the live filesystem corpus from 15 to 27 checks and the deterministic
  syscall corpus from 25 to 26 checks. The direct corpus proves byte-zero reads,
  offset preservation, caller ownership after success and failure, hard-link
  policy, unlinked-open rejection, and invalid-descriptor behavior.
- Upgraded the structural audit to 23 obligations and pinned the new owner,
  shared limits, tests, and audit in the release verifier.

## Audit interpretation

This is primarily a boundary refactor, not a claim that the old pathname-only
callers returned wrong bytes in ordinary single-threaded operation: those callers
opened a fresh descriptor whose offset began at zero. The old implementation did,
however, combine pathname acquisition, descriptor lifetime, mutable-offset I/O,
metadata proof, and cleanup in one function. That shape could not be safely reused
by a future directory-descriptor namespace owner or by code borrowing an existing
descriptor. Rev0843 separates those authorities and makes the reusable primitive
safe against shared-offset interference.

The extraction also closes two quieter fail-closed gaps. Limits beyond string or
positional-offset capacity now fail under the caller's labeled contract instead
of escaping as implementation-specific allocation/offset behavior, and an
already-unlinked open inode cannot be mistaken for current namespace evidence.

## Validation

The exact validation record is in
`REVISION_EVIDENCE/rev0843/validation/VALIDATION_SUMMARY.json`.

## Scope limits

Rev0843 does not claim all-component path confinement, a retained directory
handle, `openat2(2)` resolution policy, protection against a caller concurrently
closing and reusing the borrowed descriptor number, Windows runtime coverage,
arbitrary power-loss completeness, distributed convergence, payload
confidentiality, anonymity, metadata hiding, forward secrecy, post-compromise
recovery, hostile-parser isolation, or secure erasure.
