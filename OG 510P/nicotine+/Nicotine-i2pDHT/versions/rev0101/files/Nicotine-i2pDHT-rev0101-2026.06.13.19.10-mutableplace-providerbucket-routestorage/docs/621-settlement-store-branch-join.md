# Settlement store branch join

`settlementstore.py` is the first current surface that forces the two rev0058 ideas to agree.

The finality lineage says whether an effect is terminal, retry-pending, or dead-letter-held. The folded settlement branchlet says whether a post-reconcile observation has enough attestation memory to become sticky local state. Either can be valid alone and still unsafe together.

The store rejects:

- finality terminal while settlement is retry-held or dead-letter-held,
- retry-held settlement without retry escrow carry,
- terminal state with pending prune pressure,
- terminal state with hard-negative pressure,
- boundary drift across scope, request, payload, or idempotency key,
- low component family/path diversity.

Accepting the store does not mean global truth. It means one local node has enough exact-boundary evidence to carry the state forward.


needle: settlement store

Needle: settlement store.
