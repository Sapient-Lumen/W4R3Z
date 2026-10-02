# ADR 0140: Bound directory-projection crash recovery

Date: 2026-08-24

Status: accepted

## Context

ADR 0139 made a materialized directory a derived, retryable projection of durable signed activation
truth. It recovered canonical unpack staging below `materialized-trees/revisions`, but one crash
window remained: the process creates a temporary relative `current` symlink before atomically
renaming it. Termination between those syscalls leaves `.current.part.PID.SEQUENCE`. A retry could
still switch `current`, but it did not collect the abandoned pointer. Repeated interruption could
therefore grow derived state without bound.

Testing only a returned I/O error is insufficient here because ordinary stack unwinding runs cleanup
destructors. The qualification gate must terminate a separate process at the real post-effect
boundary and let a fresh process reconcile the resulting filesystem.

## Decision

Directory projection exposes eight named, injected post-effect checkpoints: unpack complete, frozen
staging complete, revision rename, revision-directory fsync, pointer creation, pointer rename,
activation-directory fsync, and stale-projection pruning. Production leaves the checkpoint callback
empty. The seam changes no on-disk format and grants no runtime control surface.

Before projection work, IoTox completely classifies the top level of `materialized-trees`. Only the
owner directory `revisions`, an owner symlink named `current`, and owner symlinks named exactly
`.current.part.PID.SEQUENCE` are admissible. A temporary target must be a canonical relative
`revisions/GENERATION-RECORD` path. Any ambiguity refuses the operation before the first unlink.
Pointer candidates are bounded by the namespace object ceiling. Revision cleanup admits that bound
plus the one complete predecessor required during an atomic switch. Excess state returns
`resource_exhausted` before cleanup mutation.

After complete classification, canonical pointer temporaries are unlinked and the activation
directory is fsynced. The existing revision cleanup applies the same classify-before-mutate rule to
abandoned unpack trees.

The process oracle first installs generation 1, then terminates a child with `_exit` at each of the
eight generation-2 checkpoints. Before pointer rename, an observer must see the complete generation-1
tree. At and after pointer rename, it must see the complete generation-2 tree. A fresh child must then
retry the exact revision and leave one canonical revision, one `current` pointer, and no staging or
pointer temporary.

## Consequences

Projection interruption is now process-verified across every explicit local boundary, including the
window that previously leaked pointer temporaries. Exact retry remains the only recovery action;
signed activation state remains authoritative and no cleanup decision can advance or roll it back.

This does not simulate an abrupt power cut below `fsync`, storage firmware behavior, ENOSPC at every
write, read-only remount, general allocation failure, or provider queue exhaustion. It does not make
derived projection state a rollback witness. Those resource and real-filesystem cells remain in the
M5B fault matrix.
