# Settlement store branch join

`settlementstore.py` joins the spoken rev0058 finality/prune branch with the alternate rev0058 settlement/tombstone branch.

The store accepts only when:

- finality and settlement agree on terminal versus retry/dead-letter hold,
- finality, settlement, attestation, tombstone repair, prune guard, and retry escrow bind to the same profile/service/scope/request/payload/idempotency boundary,
- retry-held state carries retry escrow,
- terminal state does not carry pending prune or hard-negative pressure,
- component family/path diversity is high enough.

The store is deliberately not a database. It is a local judgment report that says the branch merge is coherent enough to carry forward.
