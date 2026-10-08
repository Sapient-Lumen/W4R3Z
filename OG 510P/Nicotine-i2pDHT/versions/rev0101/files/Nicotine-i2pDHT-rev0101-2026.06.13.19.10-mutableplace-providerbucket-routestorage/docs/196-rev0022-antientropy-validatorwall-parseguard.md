# rev0022 — antientropy / validatorwall / parseguard

rev0022 keeps the cube in risk-first DHT design.  It does not add live I2P/SAM transport.  It asks what will break first when signed frames, mutable summaries, and arbitrary payload bytes arrive from a noisy anonymous network.

The main rule added here:

```text
Signed bytes are not yet typed, fresh, scoped, or safe to parse.
```

New surfaces:

- `parseguard.py` — strict, bounded, canonical bdecode for cube wire fixtures.
- `validatorwall.py` — a semantic wall between signed wire frames and future DHT handlers.
- `antientropy.py` — signed short-lived summaries for mutable heads, tombstones, provider ledgers, and custody facts.
- `surfaceindex.py` — audit/refactor lane that checks current-revision navigation without deleting history.

The cube now tests malformed bencode, unsorted dictionaries, duplicate keys, depth/size limits, role/kind confusion, body-digest mismatches, request-id conflicts, anti-entropy fork evidence, tombstone-first reconciliation, source-family monoculture, expired summaries, and rollback mesh pressure.

Nonclaims remain firm: no production parser, no production validator, no production anti-entropy protocol, no consensus, no private retrieval guarantee, no Sybil/anonymity guarantee, and no application patch.
