# Python surface — rev0052

New modules:

```text
src/i2p_dht_lab/backpressuremesh.py
src/i2p_dht_lab/liveadapter.py
src/i2p_dht_lab/profileedge.py
src/i2p_dht_lab/edgefold.py
```

New tests:

```text
tests/test_rev0052_liveadapter_backpressure_profileedge.py
```

The tests cover bidirectional acceptance, bulk-shed pressure, raw-key budget rejection, hard-negative rejection, protected-reserve starvation, backpressure-mode mismatch, live-adapter component drift, profile generation rollback, profile-edge budget overflow, and fold audit visibility.
