# Python surface — rev0066

Active modules:

```text
src/i2p_dht_lab/repairpublishgate.py
src/i2p_dht_lab/repairackledger.py
src/i2p_dht_lab/duplicateclosure.py
src/i2p_dht_lab/repairpublishfold.py
```

Active tests:

```text
tests/test_rev0066_repairpublish_ackclosure.py
```

The tests cover happy-path repair publication / ACK / closure, released cooldown blocking repair, digest drift, ACK diversity, NACK/mixed holding behavior, contradiction-memory preservation, and current fold audit visibility.
