# Rev0978 audit handoff

## Scope

Rev0978 remains deletion-free. It closes two prerequisites for future storage retention without claiming a collector: independently opened owners over one exact durable payload store now share a bounded same-process live-capability scope, and retention planning keeps the store-global writer fence through physical observation, exact-inode candidate probes, final database comparison, rooted reproof, and the terminal capability cutpoint.

## Primary correction

The live-capability registry is now brokered by the exact descriptor-attested root and immutable store identity. Snapshots, opened payload descriptors, targeted accessors, and mutation batches from every same-process owner in that scope appear in one canonical set. Final owner and capability release destroys the non-durable scope; reopening creates a new incarnation. Exact snapshot handoff remains owner-local and still requires the issuing verification cache and integrity epoch.

The retention planner constructs and sorts its immutable causal projection before the exclusive interval, then retains the exact global exclusive lease through physical merge and at most 1,024 exact-inode nonblocking exclusive probes. It publishes a process-interval deletion-free mark, a separate restart-stable candidate witness, and a page digest. None is reclaim authority.

## Adjacent audit and refactor

The independent deletion-free-mark oracle had omitted the inode-lease protocol field already bound by production. It now verifies the actual production digest instead of accepting a weakened oracle. The local control regression now uses the project’s strict JSON parser rather than ad hoc field extraction. A standalone unsealed durable-mark codec with no persistence owner, policy consumer, recovery path, or collection operation was removed rather than retained as ceremonial architecture.

Validation authority excludes duplicate shared-tree launchers, interrupted monolithic wrappers, stale or source-divergent runs, and generated Python bytecode. The exact binary-aware patch reconstructed all 15 changed active files and the complete 570-file active projection byte-for-byte and by mode.

## Authority boundary

The result does not bind copied transport buffers, every active receiver/publication/mutation lifetime, other-process work before exact-inode open, noncooperating writers, policy, grace, quota or ENOSPC behavior, durable mark intent, collection quarantine, restart reobservation, reclaim, or unlink. Advisory locks remain a cooperative Linux boundary and require live qualification on remote filesystems.
