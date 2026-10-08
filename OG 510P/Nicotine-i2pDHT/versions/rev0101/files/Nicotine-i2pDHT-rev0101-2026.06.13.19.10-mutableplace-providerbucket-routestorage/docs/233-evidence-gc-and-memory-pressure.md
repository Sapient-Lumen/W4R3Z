# Evidence GC and memory pressure

The DHT design keeps saying that witnesses, tombstones, provider proofs, route attestations, useful refusals, forks, and rollbacks are evidence rather than truth. rev0025 adds the missing counterweight: evidence is also storage pressure.

`evidencegc.py` classifies evidence as soft, hard, or pinned:

```text
soft evidence:       provider_true, mutable_latest, route_attestation, useful_refusal, custody_proof
hard evidence:       provider_false, mutable_stale, mutable_fork, tombstone, capability_revocation
pinned evidence:     mutable_fork, tombstone, capability_revocation
```

The local GC pass prefers keeping hard negative evidence, especially tombstones, forks, and revocations. It drops expired soft evidence, caps repeated family evidence, quarantines same-scope/same-sequence digest conflicts, and applies a byte budget.

This is not deletion consensus. A tombstone is not global truth. But forgetting a tombstone or fork too early creates rollback/resurrection risk, while keeping every old observation forever creates a denial-of-memory surface. The prototype now tests that tension directly.
