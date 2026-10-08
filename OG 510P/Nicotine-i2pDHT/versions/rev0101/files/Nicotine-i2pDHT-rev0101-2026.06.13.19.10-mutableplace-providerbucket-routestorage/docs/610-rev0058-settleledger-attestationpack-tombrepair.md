# rev0058 — settleledger-attestationpack-tombrepair

rev0058 continues the no-network I2P DHT design cube after rev0057's dead-letter / retry-quorum / effect-reconcile seam.

The risk this turn is deceptively mundane:

```text
effect reconcile accepted
+ dead-letter / retry evidence accepted
+ recovery memory accepted
    ≠ locally settled state
    ≠ safe compaction of hard negatives
    ≠ safe forgetting of unresolved retry/dead-letter memory
```

New surfaces:

- `settlementlane.py` — signed settlement entries after effect reconciliation.
- `attestationpack.py` — typed report-digest packs that carry evidence without becoming an oracle.
- `tombstonerepair.py` — post-settlement tombstone / revocation repair pressure.
- `settlementfold.py` — current-revision audit/refactor fold preserving the rev0057 `reconcilefold` predecessor.

Strong sentence:

> A reconciled effect is not settled until attestations, sticky settlement memory, and tombstone repair agree at the exact boundary.

The settlement lane deliberately treats retry as sticky watch state. A retry settlement is accepted only when it keeps dead-letter memory alive; a retry that drops dead-letter memory is quarantined.

Current proof path:

```text
tests/test_rev0058_settlement_attestation_tombrepair.py
src/i2p_dht_lab/attestationpack.py
src/i2p_dht_lab/settlementlane.py
src/i2p_dht_lab/tombstonerepair.py
src/i2p_dht_lab/settlementfold.py
```

Nonclaims remain unchanged: no live I2P/SAM transport, no production DHT, no production settlement database, no production attestation protocol, no production tombstone repair protocol, no global reputation, no mutable-head consensus, no private retrieval guarantee, no Sybil/anonymity guarantee, and no Nicotine+ patch.
