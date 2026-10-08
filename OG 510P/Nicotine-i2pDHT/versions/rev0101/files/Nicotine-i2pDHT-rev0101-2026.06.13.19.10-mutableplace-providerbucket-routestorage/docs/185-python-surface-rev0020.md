# Python surface — rev0020

New modules:

```text
src/i2p_dht_lab/epochgate.py
src/i2p_dht_lab/repairmarket.py
src/i2p_dht_lab/wirecanon.py
src/i2p_dht_lab/surfacefold.py
```

New tests:

```text
tests/test_rev0020_epochgate_repairmarket_wirecanon.py
```

Extended audit/evidence surfaces:

```text
src/i2p_dht_lab/surfaceledger.py
scripts/evidence/check_surfaces.py
scripts/evidence/run_micro_simulation.py
scripts/evidence/run_cube_audit.py
```

The new code remains deterministic and local.  It does not open sockets, contact I2P, or implement production routing/storage.
