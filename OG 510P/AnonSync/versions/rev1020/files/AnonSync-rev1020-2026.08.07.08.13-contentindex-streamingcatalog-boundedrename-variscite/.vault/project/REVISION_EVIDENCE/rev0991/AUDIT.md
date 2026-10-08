# Rev0991 audit

## Defect

The normal prepared local-file publication path rebuilt the complete retained replica model during both preparation and commit. At a 4,096-file scan segment and 10,000 retained operations, that shape admitted 8,192 complete projections and 81,920,000 prior operation-row decodes.

## Correction

Schema v8 adds a canonical operation-path index, exact counts, and fixed-width counted commutative witnesses. Normal local publication now reads the target-path history and active causal heads, then incrementally updates durable metadata under one re-proved writer cutpoint. Unrelated progress may continue; same-path, local-chain, policy, schema, or causal-head drift fails closed. A rare future-ID reverse dependency uses the complete-model fallback.

## Adjacent audit/refactor

An exact retry could previously report `AlreadyPublished` after a same-dot fork quarantined the operation and compromised the local actor. Rev0991 requires the retained operation to remain active and the actor uncompromised. The fixed-width arithmetic regression also covers exact 256-bit carry and borrow.

## Nonclaims

The additive witness is structural acceleration, not authentication authority or a cryptographic set commitment. Complexity is O(history-of-that-path + active causal heads), not constant memory. Complete reconstruction remains authoritative, multi-terabyte RSS remains unqualified, and rev0990 is absent from lineage.
