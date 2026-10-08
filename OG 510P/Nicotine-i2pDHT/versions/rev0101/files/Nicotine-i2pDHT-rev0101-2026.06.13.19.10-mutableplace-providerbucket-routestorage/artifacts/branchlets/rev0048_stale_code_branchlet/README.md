# rev0048 stale code/test branchlet

This folder preserves two alternate rev0048 sketches that used incompatible APIs:

- `shadowauditfold.py` / `bridgeshadowfold.py` / `bridgeauditfold.py`
- old `test_rev0048_*` files expecting checkpoint-style audit quorum and `make_bridge_shadow_step`

The canonical active rev0048 surface is now:

- `src/i2p_dht_lab/bridgeshadow.py`
- `src/i2p_dht_lab/auditquorum.py`
- `src/i2p_dht_lab/redressgc.py`
- `src/i2p_dht_lab/bridgegovernancefold.py`
- `tests/test_rev0048_bridge_shadow_audit_redressgc.py`

These stale files remain wake-from-amnesia artifacts only.
