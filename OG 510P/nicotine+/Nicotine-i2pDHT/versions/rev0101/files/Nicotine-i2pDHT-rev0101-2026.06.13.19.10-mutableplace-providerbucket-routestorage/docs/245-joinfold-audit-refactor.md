# Joinfold audit/refactor

`src/i2p_dht_lab/joinfold.py` audits the current rev0026 joined-boundary path.

It checks that code, tests, docs, public pointers, head registry entries, and active surface-ledger entries all point at the current joined surfaces:

- `schedjoin.py`,
- `custodygc.py`,
- `partitionwitness.py`,
- `transportshadow.py`,
- `joinfold.py`.

This is a refactor lane, not a feature lane. It keeps the live path visible without deleting historical branchlets.
