# rev0068 — archivejournal-prunereplay-closureaudit

This revision moves one seam past rev0067.

```text
repair settlement accepted
+ closure archive accepted
+ soft repair prune accepted
    ≠ restart-safe journal
    ≠ replay-safe prune memory
    ≠ audited closure state
```

The new risk-first surfaces are `archivejournal.py`, `prunereplay.py`, and `closureaudit.py`.  They treat cleanup after duplicate-repair settlement as a protocol boundary instead of a storage chore.

The strongest sentence:

```text
A pruned repair trace is not forgotten; it is restart-journaled, replay-checked, and closure-audited until contradiction memory survives the whole path.
```

Current nonclaims remain: no live I2P/SAM transport, no production DHT, no production persistence database, no production prune/replay/audit protocol, no global reputation, no mutable-head consensus, no private retrieval guarantee, no Sybil/anonymity guarantee, and no Nicotine+ patch.
