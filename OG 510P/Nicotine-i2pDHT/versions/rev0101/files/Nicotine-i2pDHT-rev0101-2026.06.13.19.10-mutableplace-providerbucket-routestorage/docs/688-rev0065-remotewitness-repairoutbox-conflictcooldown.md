# rev0065 — remotewitness-repairoutbox-conflictcooldown

rev0065 follows the public-edge retry/ACK line one step deeper:

```text
retry publication staged
+ idempotency mesh accepted or watchful
+ delivery repair mesh saw remote duplicate evidence
    ≠ remote witness memory is safe across rounds
    ≠ repair publication may be staged
    ≠ repeated duplicate conflict may spam retry/repair work
```

The strongest sentence in this revision:

```text
Remote duplicate evidence is not a resend button; it is sticky local memory until ledger, outbox, and cooldown agree at one exact boundary.
```

New active Python surfaces:

```text
src/i2p_dht_lab/remotewitnessledger.py
src/i2p_dht_lab/repairoutbox.py
src/i2p_dht_lab/conflictcooldown.py
src/i2p_dht_lab/remoterepairfold.py
tests/test_rev0065_remotewitness_repairoutbox_conflictcooldown.py
```

## Risk-first focus

1. Remote witness replay across rounds.
2. Repair-outbox staging after a remote duplicate conflict.
3. Conflict cooldown for repeated duplicate evidence.
4. Audit/refactor of the public-edge ACK/retry/repair lineage.

## Nonclaim

This is still a no-network cube. There is no live I2P/SAM transport, no production DHT, no production remote-witness protocol, no production public repair outbox, no production cooldown scheduler, no global reputation, no mutable-head consensus, no private retrieval guarantee, no Sybil/anonymity guarantee, and no Nicotine+ patch.
