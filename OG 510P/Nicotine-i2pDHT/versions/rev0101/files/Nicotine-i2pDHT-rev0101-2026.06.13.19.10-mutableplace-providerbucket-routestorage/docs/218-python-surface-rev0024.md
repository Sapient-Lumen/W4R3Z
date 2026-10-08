# Python surface — rev0024

New modules:

```text
src/i2p_dht_lab/policyepoch.py
src/i2p_dht_lab/rangemerkle.py
src/i2p_dht_lab/queueforge.py
src/i2p_dht_lab/policyfold.py
```

New tests:

```text
tests/test_rev0024_policyepoch_rangemerkle_queueforge.py
```

Extended audit surface:

```text
src/i2p_dht_lab/surfaceledger.py
scripts/evidence/run_cube_audit.py
scripts/evidence/check_surfaces.py
```

The new code is deterministic and local. It does not open sockets, call SAM, or implement production storage.
