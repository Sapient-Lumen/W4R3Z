# rev0063 — lateack-retrysettle-egressjournal

This revision follows the rev0062 ACK/repair split into the next risky seam:

```text
retry fence accepted
+ missing ACK repair path exists
+ live egress says retry/withdraw is ready
    ≠ late original ACK is harmless
    ≠ retry result is settled
    ≠ withdraw repair is terminal
    ≠ egress journal may compact contradictions
```

The main rule is:

> A late ACK, retry settlement, withdraw repair, and egress journal compaction are separate local permissions; none may erase the others.

Active surfaces:

```text
src/i2p_dht_lab/lateack.py
src/i2p_dht_lab/retrysettlement.py
src/i2p_dht_lab/withdrawrepair.py
src/i2p_dht_lab/egressjournal.py
src/i2p_dht_lab/lateackfold.py
tests/test_rev0063_lateack_retrysettle_egressjournal.py
```

The strongest behavior added is conservative: if a late original ACK appears after a retry fence, the retry path must either explicitly abort by late ACK or preserve contradiction evidence. A retry-delivered marker cannot silently coexist with a late original ACK.

Current nonclaims remain: no live I2P/SAM transport, no production DHT, no production retry publication protocol, no production egress database, no global reputation, no mutable-head consensus, no private retrieval guarantee, no Sybil/anonymity guarantee, and no Nicotine+ patch.
