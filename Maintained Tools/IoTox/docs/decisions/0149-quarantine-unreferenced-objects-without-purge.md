# ADR 0149: Quarantine unreferenced objects without purge

Date: 2026-08-24

Status: accepted

## Context

IoTox can authenticate current publication, acceptance, activation, and retention roots and bind
them to one signed committed/pending rollback guard. It still cannot detect coordinated restoration
of a complete older guard plus every matching root. A mark-only reachability result is therefore
useful evidence but is not permanent deletion authority.

The immutable store nevertheless needs a bounded operator action for clearly unreachable bytes. The
action must remain safe when invoked from the ordinary local control socket, under same-user path
substitution, cancellation, directory-sync failure, and a kernel mount boundary.

## Decision

- Add local-control v1.32 operation 77 and `sync-gc NAMESPACE dry-run|quarantine`. Do not define
  `apply`, `purge`, an unlink mode, or a remotely invocable GC operation.
- Accept only a validated installed namespace policy and the device's stable signing key. No API
  accepts an object path. Reconstruct every filename from its validated kind and digest.
- Acquire one namespace transaction, authenticate all persisted roots and the rollback guard, and
  capture the complete strict object inventory through directory descriptors. Freeze device, inode,
  owner, group, link count, mode, kind, digest-derived name, and size for every entry.
- Retain a descriptor for the namespace root in the transaction token and bind the token to that
  root's device/inode. Refuse a substituted root, transaction directory, or lock path.
- A dry run returns rooted/candidate counts and bytes and performs no quarantine-directory creation.
- Quarantine only when missing and mismatched live-root sets are empty. Re-capture and compare the
  complete inventory before the first effect, require Linux `openat2` beneath/no-symlink/no-mount
  resolution, reopen each candidate and compare its frozen identity immediately before effect, and
  use `renameat2(RENAME_NOREPLACE)` into private same-filesystem `gc-quarantine`.
- Never unlink. Synchronize the root after first quarantine creation and synchronize both source and
  quarantine directories after each rename. Report moved objects/bytes separately from objects/bytes
  whose two directory fsyncs completed. Cancellation returns the exact durable prefix.
- Treat malformed entries, links, mount crossings, destination collisions, identity substitution,
  root inconsistency, and unsupported kernel primitives as terminal refusal.
- Keep quarantine on exact retry. A later purge requires a separate ADR and either an independent
  monotonic witness or an explicit accepted operator policy for coordinated rollback risk.

## Consequences

IoTox can now reclaim active object-store quota into namespace-local quarantine without pretending
the bytes are permanently disposable. The operation is local, explicit, content-free in its normal
response, repeatable, and cannot target ambient caller paths. Partial mutation remains auditable:
post-rename durability failure reports what moved and what became durable instead of claiming an
all-or-nothing transaction.

Quarantine consumes filesystem space and has no automatic expiry. This decision does not prove that
a quarantined object can never become live after coordinated rollback, authorize deletion from
quarantine, compact retained roots, provide a hardware monotonic counter, survive abrupt power loss
at every filesystem boundary, or qualify filesystems and kernels outside the named gates.
