# Python surface — rev0018 combined

New or expanded rev0018 surfaces:

```text
src/i2p_dht_lab/livenessbudget.py
src/i2p_dht_lab/tombmesh.py
src/i2p_dht_lab/provider_compat.py
src/i2p_dht_lab/providerwrap.py
src/i2p_dht_lab/contactlease.py
src/i2p_dht_lab/siblingbroadcast.py
src/i2p_dht_lab/keyspacecartography.py
src/i2p_dht_lab/surfaceaudit.py
src/i2p_dht_lab/siblingcast.py
src/i2p_dht_lab/sweepaudit.py
src/i2p_dht_lab/surfaceledger.py
```

Tests:

```text
tests/test_rev0018_liveness_tombmesh_providerwrap.py
tests/test_rev0018_sibling_cartography_surfaceaudit.py
tests/test_rev0018_contactlease_siblingcast_sweepaudit.py
```

The rev0018 test count at packaging time is recorded in `artifacts/process/rev0018_local_verification.json`. The expected packaging lane for this cube is currently `pytest: 188 passed`.
