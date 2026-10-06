# Descriptor-pinned input audit

rev0022 consolidates file identity, exact positional reading, and direct
workspace filling in `PinnedFile`. The codec CLI and datacube ZIP preflight use
the same audited primitive instead of maintaining separate path-based readers.

## Open and read contract

- Resolve the path once with `open(O_RDONLY|O_CLOEXEC|O_NOFOLLOW)`.
- Require a regular file and a nonnegative initial size.
- Retain device, inode, size, mtime, and ctime as the initial fingerprint.
- Read only inside the initial size boundary with `pread`, retrying EINTR and
  requiring exact progress.
- `read_into` fills caller-owned storage directly and throws before I/O when a
  requested range crosses the pinned size boundary.
- Re-stat the retained descriptor after range-backed codec work, whole-file
  reads, or ZIP preflight.

In-place writes, truncation, or growth ordinarily alter the descriptor
fingerprint and are rejected. Replacing the pathname after open does not
redirect reads: the object continues to read the original inode. Such a path
replacement is intentionally not reported as mutation of that opened inode;
callers interested in pathname continuity need a stronger directory-entry
policy in addition to descriptor pinning.

`O_NOFOLLOW` rejects a symlink in the final path component. Parent-directory
symlinks can still be resolved during open, after which the descriptor is
stable. The primitive does not authenticate file authorship or prevent an
adversary from modifying the already-open inode while reads are in flight. It
detects ordinary fingerprint drift and refuses to publish derived codec output.

## Codec publication refactor

Compression and decompression now pass `read_into` as a `RangeReader`; one block
or payload is filled directly into codec workspace. Output remains in an
uncommitted `AtomicFileWriter` until the complete codec call succeeds and
`require_unchanged()` verifies the input fingerprint. A mutation regression
proves that failure preserves an existing destination and removes the private
temporary.

## Cube preflight boundary

The ZIP parser consumes `PinnedFile` directly and appends a fatal
`source_changed` issue when the descriptor fingerprint differs after structural
inspection. This preserves bounded central/local reconciliation while sharing
the same input-lifetime primitive as the codec.
