# Rev0954 research notes

Consulted 2026-07-30.

## Linux inode timestamp semantics

- https://man7.org/linux/man-pages/man7/inode.7.html

Linux documents that ordinary file writes update modification and change time,
and inode metadata changes update change time. Exact device/inode/mode/link/owner/
group/size/mtime/ctime observations are therefore useful conservative nomination
fences for immutable digest-named payloads. They are not permanent byte-integrity
proofs: privileged or same-UID interference and some storage faults sit outside
the cooperative writer-lease model.

## Linux fs-verity

- https://docs.kernel.org/filesystems/fsverity.html

The kernel's fs-verity facility builds a Merkle tree for a file, marks it read-
only, verifies reads, and exposes a measurement digest. Copied or restored files
do not automatically retain verity state, and deployment is filesystem- and
platform-specific. It is a possible future qualified optimization, not a portable
substitute for AnonSync's SHA-256 content identity or a reason to overclaim the
metadata checkpoint.

## Syncthing indexing and rescans

- https://docs.syncthing.net/users/syncing.html
- https://docs.syncthing.net/users/config.html
- https://docs.syncthing.net/specs/bep-v1.html

Syncthing retains an index database, uses filesystem metadata to decide what must
be rehashed during rescans, combines watcher notifications with periodic scans,
and separates full indexes from monotonic index updates. Rev0954 is intentionally
narrower: it accelerates exact unchanged payload verification across restart but
is not a general namespace/change-sequence index, a watcher replacement, or an
integrity scrub.

## Inference

A useful restart checkpoint and a useful integrity scrub have different budgets
and failure semantics. The former may conservatively nominate exact metadata for
reuse while the authoritative scanner still enumerates every object. The latter
must eventually reread every byte and therefore needs both byte and entry limits,
durable fair continuation, and a defined response to corruption. Combining them
behind a one-entry-per-pass knob would hide unbounded I/O and restart starvation.
