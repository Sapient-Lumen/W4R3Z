# rev0067 — repairsettlement-closurearchive-repairprune

rev0067 follows the rev0066 duplicate-closure path into the next local-truth seam:

```text
repair publish ready
+ repair ACK ledger accepted
+ duplicate closure accepted
    ≠ settled repair
    ≠ restart-safe archive
    ≠ safe evidence pruning
```

The strongest sentence in this revision:

```text
Closed duplicate repair is not settled, archived, or prunable until contradiction memory survives each join.
```

New active code:

```text
src/i2p_dht_lab/repairsettlement.py
src/i2p_dht_lab/closurearchive.py
src/i2p_dht_lab/repairprune.py
src/i2p_dht_lab/repairsettlementfold.py
tests/test_rev0067_repairsettlement_archive_prune.py
```

Risk-first additions:

- **repair settlement**: duplicate closure becomes local settlement only if repair publication, repair ACK memory, duplicate closure, remote-witness digest, cooldown digest, contradiction carriage, sequence links, family diversity, and path diversity all agree.
- **closure archive**: settlement is written into restart-sticky archive memory together with contradiction evidence.
- **repair prune**: soft repair-trace pruning is allowed only after settlement and archive agree; proposals that drop settlement, remote witness, cooldown, contradiction, or hard-negative memory quarantine.
- **audit/refactor**: `repairsettlementfold.py` pins rev0067 through current source, tests, docs, fold map, fold registry, surface ledger, and rev0066 `repairpublishfold` predecessor history.

Nonclaims remain firm: no live I2P/SAM transport, no production DHT, no production archive database, no production prune protocol, no global reputation, no mutable-head consensus, no private retrieval guarantee, no Sybil/anonymity guarantee, and no Nicotine+ patch.
