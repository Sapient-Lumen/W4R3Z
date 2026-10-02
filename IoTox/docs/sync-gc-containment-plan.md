# Synchronization GC containment plan

Status: quarantine-only collector implemented and Sandwurm-qualified; purge remains absent.

## Qualification substrate decision

Collector correctness remains a local filesystem problem, so ordinary unit/process development uses
disposable namespace roots. The project decision is nevertheless to run every destructive
quarantine/GC acceptance fixture inside the Sandwurm Cloud Hypervisor guest before enabling it. Host
snapshots are recovery protection, not permission to point a collector at ambient host paths.

The 2026-08-24 `sync-file-repair` Sandwurm gate now runs the collector independently in both source-
linked guests after signed convergence. Each guest proves a real bind mount over `objects` is refused,
plants two sentinels outside the namespace root, dry-runs one 32 KiB unreachable object without
mutation, moves that exact inode into quarantine, synchronizes both directories, preserves every
sentinel and live object, and observes an empty exact retry. The local `sandworm` Bubblewrap path is
not an acceptance dependency.

## Construction boundary

1. No collector accepts a caller-supplied deletion pathname. It accepts a validated namespace policy
   and reconstructs one digest-named object beneath its already-open private `objects` directory.
2. Planning is always non-destructive. Execution requires a fresh stored reachability pass whose
   transaction is still held, whose rollback guard is coherent, and whose missing/mismatched sets are
   empty.
3. The first executable form quarantines by descriptor-relative no-replace rename into a private
   namespace-local directory. It does not unlink. A later purge is a separate explicit operation.
4. Every candidate is reopened without following links and must still match the planned device,
   inode, owner, mode, link count, kind, digest-derived name, and size immediately before rename.
5. Directory descriptors and Linux `openat2`/`renameat2` beneath/no-symlink constraints are preferred;
   unsupported kernels fail closed rather than falling back to path traversal.
6. The object directory and quarantine must be on the same filesystem. Cross-device movement, mount
   boundaries, symlinks, hard links, unexpected entries, and directory replacement abort the pass.
7. Cancellation is checked between objects. Each completed rename and both parent directories are
   synchronized before it is reported. The result records exact moved objects/bytes and failures.
8. Tests create a unique disposable root beneath a configured workspace scratch directory, plant
   sentinel files outside it, and prove those sentinels are unchanged after every successful and
   refused run. Tests never point collection at the checkout, home directory, `/tmp`, or `/`.

## Rollback limitation

The local signed guard detects isolated rollback but not restoration of one complete coherent older
guard plus every matching root. Therefore quarantine may be implemented and tested now, but automatic
purge remains disabled until IoTox adopts an external owner/replica witness, a hardware monotonic
counter, or an explicit operator policy that accepts this availability risk. Host snapshots are
excellent recovery protection; they are not protocol evidence available to the device.

## Ordered gates

- [x] Freeze a dry-run collection request/result and descriptor-pinned candidate identity.
- [x] Implement quarantine-only execution with no arbitrary paths and no unlink operation.
- [x] Prove symlink/escape, inode substitution, hard-link, real mount, cancellation, and post-rename
  directory-sync failure behavior with exact moved/durable accounting.
- [x] Run the destructive fixture in both Sandwurm guests with outside-root sentinels.
- [x] Decide explicitly that no purge entrance exists until an independent monotonic witness or a
  separately accepted operator-risk policy exists (ADR 0149).
- [x] Re-run the fixture inside the accepted S3 signed convergence/repair scenario.

The remaining work is deliberately a different milestone: design an independent rollback witness,
then review and qualify a purge protocol. Quarantine growth is therefore operator-visible retained
state, not an implicit queue for later automatic deletion.
