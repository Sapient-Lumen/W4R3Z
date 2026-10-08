# Python surface — rev0021

New modules:

```text
src/i2p_dht_lab/epochsplit.py
src/i2p_dht_lab/storewire.py
src/i2p_dht_lab/repairreplay.py
```

Extended modules:

```text
src/i2p_dht_lab/surfacefold.py
src/i2p_dht_lab/surfaceledger.py
```

New tests:

```text
tests/test_rev0021_epochsplit_storewire_repairreplay.py
```

The tests cover linked diverse epoch advances, fork and previous-link split quarantine, stale replay against local memory, store/custody wire role binding, frame tamper detection, repair offer replay, sequence rollback, useful refusal pacing, and current-revision audit navigation.
