# Python surface — rev0025

New modules:

```text
src/i2p_dht_lab/capgate.py
src/i2p_dht_lab/evidencegc.py
src/i2p_dht_lab/splitmerge.py
src/i2p_dht_lab/riskfold.py
```

New tests:

```text
tests/test_rev0025_capgate_evidence_splitmerge.py
```

Updated active ledgers/scripts:

```text
src/i2p_dht_lab/surfaceledger.py
scripts/evidence/check_surfaces.py
scripts/evidence/run_cube_audit.py
scripts/evidence/run_micro_simulation.py
scripts/ci/run_python_cloudtainer_lane.sh
```

The new Python surface intentionally connects previously separate risk boundaries instead of creating another isolated speculative branchlet.
