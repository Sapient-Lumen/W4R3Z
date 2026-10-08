# rev0032 — scopeledger-storedebt-samtrace

rev0032 continues the risk-first Python DHT substrate cube by joining three surfaces that were previously adjacent but separable.

The design pressure is:

```text
A scope can pass, a store repair plan can pass, and a SAM-shadow script can pass while the joined boundary is still wrong.
```

New active modules:

```text
src/i2p_dht_lab/scopeledger.py
src/i2p_dht_lab/storedebt.py
src/i2p_dht_lab/samtrace.py
src/i2p_dht_lab/scopefold.py
```

The revision deliberately stays pre-network. No SAM socket is opened and no I2P router is required. The work is local protocol pressure before live latency, partial failure, and router differences hide boundary bugs.
