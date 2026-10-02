# ADR 0223: Freeze private-prefix file resume below synchronization

Status: accepted construction prerequisite, 2026-08-28.

Amended by ADR 0224: the upper-protocol entrance also accepts an exact empty private partial at
offset zero without issuing a Tox seek. Ordinary `receive_to_path` behavior is unchanged.

## Context

Whole-object reassignment currently fences the lost route, discards its attempt-scoped staging,
allocates fresh attempt/FileId identities, and requests the complete immutable object again. That is
safe, but it turns a late route loss into nearly a full-object latency penalty. c-toxcore exposes
`tox_file_seek`, so a replacement transfer can request only the missing suffix. The old prefix is
not independently authenticated, however, and the ordinary safe receiver owns a disposable hidden
temporary that it deletes on every terminal failure.

The synchronization scheduler is not yet allowed to reuse such a prefix. First the transport layer
needs an ownership contract that cannot delete a caller-retained partial or silently publish
unauthenticated bytes.

## Decision

- Add `FileTransferManager::receive_to_path_from_offset`. ADR 0224 permits zero only for an existing
  exact empty caller-owned partial; ordinary fresh and empty-file receives continue through
  `receive_to_path` unchanged.
- Require an absolute existing regular file whose opened and inspected identities match, with one
  link, effective-user ownership, exact mode `0600`, and size exactly equal to the nonzero requested
  offset. Require the offset to be strictly below the finite offered size.
- Keep the offer locally paused while calling c-toxcore seek, then resume through the existing
  bounded carrier window. The accepted record starts at the requested position.
- Treat the prefix as caller-owned. Cancellation, peer loss, manager stop, seek failure, malformed
  completion, and ordinary write failure close the transfer but do not unlink it. If a positional
  write partially fails, truncate back to the last fully accounted callback boundary when possible.
- On complete receipt, revalidate that the named path still resolves to the opened private inode,
  fsync the inode, and leave it in place. Path substitution fails closed and neither the substituted
  path nor the displaced completed inode is published by this API.
- Require the upper protocol to authenticate the complete immutable digest before publication and
  to remove or quarantine an unusable prefix explicitly. Prefix length is progress, not trust.

The mock provider now honors nonzero receive positions. Owned tests prove suffix-only completion,
mode and zero-offset refusal, preservation across authoritative peer loss and manager shutdown, and
destination-substitution refusal at completion.

## Consequences

This removes the lowest transport obstacle to byte-efficient immutable-object reassignment without
changing Tox framing, sync-wire-v1, signed HEADs, FileId correlation, or attempt fencing. It does not
yet make synchronization resumable: the scheduler must durably carry exact verified progress from
the fenced attempt into a fresh attempt, bind a new FileId and carrier, and still hash the full object
before commit. Cross-process recovery and genuine two-guest route-loss qualification remain open.

Arbitrary received files and mutable command payloads do not gain resume semantics. This primitive
is intentionally narrow enough for a digest-authenticated upper layer.
