# rev0062 — ackrepair-liveegress-retryfence

This revision folds the sibling rev0061 `deliveryrepair-liveegress-rollbackprobe` branchlet into the delivered ACK/archive/prune line.

The new risky seam is:

```text
delivery settlement + ack archive + ack prune accepted
    OR
delivery repair + rollback probe + live egress accepted
    ≠ the other path is safe for the same public-edge object
```

The cube now treats terminal ACK settlement and missing-ACK repair as mutually exclusive local permissions at the exact profile/service/scope/request/payload/idempotency boundary.

New active surfaces:

- `src/i2p_dht_lab/deliveryrepair.py`
- `src/i2p_dht_lab/rollbackprobe.py`
- `src/i2p_dht_lab/liveegress.py`
- `src/i2p_dht_lab/ackrepairjoin.py`
- `src/i2p_dht_lab/retryfence.py`
- `src/i2p_dht_lab/repairpruneguard.py`
- `src/i2p_dht_lab/egressrepairfold.py`

Strongest sentence:

```text
A terminal ACK and a retry repair can each be locally plausible; the DHT must not let them both become side-effect permission for the same object.
```

Current nonclaims stay firm: no live I2P/SAM transport, no production DHT, no production retry or publication protocol, no global reputation, no mutable-head consensus, no private retrieval guarantee, no Sybil/anonymity guarantee, and no Nicotine+ patch.
