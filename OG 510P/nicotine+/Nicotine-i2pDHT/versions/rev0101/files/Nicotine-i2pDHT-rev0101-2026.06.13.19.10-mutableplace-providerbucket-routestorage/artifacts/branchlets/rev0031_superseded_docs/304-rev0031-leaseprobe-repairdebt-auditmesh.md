# rev0031 — leaseprobe / repairdebt / auditmesh

rev0031 attacks three joined-boundary risks:

1. A contact lease can become sticky before live probing, egress, and key-crisis pressure agree.
2. Repair triggers can become unbounded outbound work or garden load.
3. The cube can grow surfaces faster than its wake-from-amnesia navigation spine.

New active surfaces:

- `src/i2p_dht_lab/leaseprobe.py`
- `src/i2p_dht_lab/repairdebt.py`
- `src/i2p_dht_lab/auditmesh.py`
- `tests/test_rev0031_leaseprobe_repairdebt_auditmesh.py`

Strongest rule:

```text
Sticky entrances and repair work are side effects; side effects need exact local joins.
```

Nonclaims remain unchanged: no live I2P/SAM transport, no production DHT, no global reputation, no private retrieval guarantee, no mutable-head consensus, no Sybil/anonymity guarantee, and no Nicotine+ patch.
