# Obligation debt and proof-carrying local decisions

A local accept-with-watch decision should leave debt. Examples:

- provider semantic proof still owed
- mutable-head witness still owed
- route liveness still owed
- tombstone repair still owed
- custody challenge still owed

`ProofObligation` records what remains to be proven. `ProofEvidence` clears it only when kind, scope, object, subject, freshness, and source/path diversity line up. Missing proof before due is a hold; missing proof after due becomes quarantine pressure.

This is not global consensus. It is a local ledger of promises the node made to itself.
