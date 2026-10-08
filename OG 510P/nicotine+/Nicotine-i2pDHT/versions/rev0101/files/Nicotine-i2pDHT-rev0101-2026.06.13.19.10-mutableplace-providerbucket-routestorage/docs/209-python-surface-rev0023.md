# Python surface — rev0023

New modules:

```text
src/i2p_dht_lab/rangesketch.py
src/i2p_dht_lab/admissionwall.py
src/i2p_dht_lab/namespaceregistry.py
src/i2p_dht_lab/namespacefold.py
```

New tests:

```text
tests/test_rev0023_rangesketch_admission_namespace.py
```

Extended surfaces:

```text
src/i2p_dht_lab/surfaceledger.py
scripts/evidence/check_surfaces.py
scripts/evidence/run_micro_simulation.py
scripts/evidence/run_cube_audit.py
scripts/ci/run_python_cloudtainer_lane.sh
pyproject.toml
VERSION
```

The active test surface now exercises range sketch repair, namespace dispatch policy, admission budgets, and namespace-fold audit hygiene.
