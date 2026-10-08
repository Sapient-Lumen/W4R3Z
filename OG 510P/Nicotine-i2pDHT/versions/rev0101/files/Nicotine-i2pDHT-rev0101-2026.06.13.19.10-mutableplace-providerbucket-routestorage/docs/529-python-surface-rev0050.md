# Python surface — rev0050

New modules:

```text
src/i2p_dht_lab/outboxdrain.py
src/i2p_dht_lab/samcanary.py
src/i2p_dht_lab/compactjoin.py
src/i2p_dht_lab/drainfold.py
```

New tests:

```text
tests/test_rev0050_outboxdrain_samcanary_compactjoin.py
```

The implementation remains deterministic, local, no-network, and toy-signed. It is designed to pin invariants before live SAM/I2P transport exists.
