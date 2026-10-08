# Python surface — rev0019

Active rev0019 modules:

```text
src/i2p_dht_lab/storeflight.py
src/i2p_dht_lab/leasequorum.py
src/i2p_dht_lab/leaseroute.py
src/i2p_dht_lab/storemesh.py
src/i2p_dht_lab/budgetreceipt.py
src/i2p_dht_lab/roundledger.py
src/i2p_dht_lab/storecontract.py
src/i2p_dht_lab/custodyaudit.py
src/i2p_dht_lab/storerepair.py
src/i2p_dht_lab/surfaceclean.py
src/i2p_dht_lab/surfaceledger.py
```

Active rev0019 tests:

```text
tests/test_rev0019_storeflight_leasequorum_surfaceclean.py
tests/test_rev0019_leaseroute_storemesh_budgetreceipt.py
tests/test_rev0019_custodylease_storeflight.py
```

Updated active support:

```text
scripts/evidence/check_surfaces.py
scripts/evidence/run_micro_simulation.py
scripts/evidence/run_cube_audit.py
```

The implementation remains deterministic and offline. It is designed to make bad local acceptance rules executable before a live I2P transport hides them behind latency and churn.

Additional risk-first modules added in the same revision:

```text
src/i2p_dht_lab/storagelease.py
src/i2p_dht_lab/readrepair.py
```

Additional tests:

```text
tests/test_rev0019_storeflight_leasequorum_readrepair.py
```

Supporting docs:

```text
docs/178-storage-lease-quorum-addendum.md
docs/179-read-repair-store-pressure.md
```

