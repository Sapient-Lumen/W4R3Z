# Rev0979 audit handoff

## Scope

Rev0979 persists one deletion-free retention mark from the exact writer-fenced physical-payload observation introduced in rev0978. The mark is evidence for later policy work, not collection authority. No owner command, trusted-clock proof, collection quarantine, reclaim, rename, or unlink is added.

## Primary correction

The fixed-width checksum-framed record binds the immutable payload-store identity and exact identity-inode observation, a same-lineage monotonic SQLite source generation, causal/evidence/pin/visible/payload/transient digests, the complete unreferenced-candidate set, and bounded grace and future collection count/byte frontiers. The folder owner moves the exact retained writer-fenced snapshot into publication; it does not perform another complete payload-root observation. A final SQLite reproof rejects same-lineage digest ABA such as pin removal followed by restoration.

## Adjacent audit and refactor

The source audit found that post-failure reconciliation could throw while attempting to inspect a possibly committed mark and thereby replace the atomic publisher's primary exception. The catch path now treats that inspection as best effort and always rethrows the original publication exception unless exact committed bytes are successfully reobserved. A structural check binds this exception-provenance contract.

The cloudtainer audit also found self-restarting mutable-source validators, an in-tree build cache, shared-cache writers, and source-divergent retention prototypes. Those processes and artifacts were removed or quarantined. Final GCC and Clang authority came from byte-reconciled clean source copies on neutral process paths; every interrupted or source-unbound result was excluded.

## Authority boundary

The mark's generation is same-lineage source freshness, not external database anti-rollback authority. The supplied Unix time is historical operator evidence, not trusted elapsed-time proof. A later collector must treat every mark as stale until it reacquires writer and exact-inode fences, completely reobserves causal and transient roots, rehashes current bytes, stages collection-specific quarantine, survives restart, and re-proves every root before unlink.
