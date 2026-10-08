# Python surface — rev0042

New modules:

```text
src/i2p_dht_lab/multiservice.py
src/i2p_dht_lab/profilecooldown.py
src/i2p_dht_lab/operatorkey.py
src/i2p_dht_lab/announcementrepair.py
src/i2p_dht_lab/controlplanefold.py
```

New tests:

```text
tests/test_rev0042_multiservice_cooldown_keyoperator.py
```

The code remains a deterministic toy lab. It signs small bencoded claims with Ed25519 keys and applies local pressure rules. It does not implement live I2P, live DHT traffic, durable databases, or production key management.
