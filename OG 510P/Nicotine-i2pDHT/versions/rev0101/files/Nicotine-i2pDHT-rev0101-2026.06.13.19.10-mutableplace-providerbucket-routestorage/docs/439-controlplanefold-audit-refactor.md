# Controlplanefold audit/refactor

rev0042 adds `controlplanefold.py` to keep the new control-plane surfaces visible from public pointers, docs, fold map, fold registry, and the active surface ledger. It preserves rev0041 `controlfold` as predecessor history.

This is also a small refactor direction: future folds should become more declarative. The current one-off fold modules remain useful regression anchors, but rev0042's fold path keeps the active module/test/doc set small and explicit.

Checked current paths:

- `src/i2p_dht_lab/multiservice.py`
- `src/i2p_dht_lab/profilecooldown.py`
- `src/i2p_dht_lab/operatorkey.py`
- `src/i2p_dht_lab/announcementrepair.py`
- `src/i2p_dht_lab/controlplanefold.py`
- `tests/test_rev0042_multiservice_cooldown_keyoperator.py`
- docs 434 through 439
