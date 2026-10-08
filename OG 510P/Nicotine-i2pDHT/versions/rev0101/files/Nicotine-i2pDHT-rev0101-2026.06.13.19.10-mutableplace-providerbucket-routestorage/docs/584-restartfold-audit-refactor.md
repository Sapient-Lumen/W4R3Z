# restartfold audit/refactor

`restartfold.py` pins rev0055's active surfaces through source, tests, docs, public pointers, fold map, fold registry, and surface ledger.

It also preserves rev0054 `replayfold` as predecessor history. This keeps the cube from silently advancing into a new seam while forgetting the replay/quench/fuzz-ledger lane it depends on.

Audit targets:

- `src/i2p_dht_lab/restartchaos.py`
- `src/i2p_dht_lab/effectseal.py`
- `src/i2p_dht_lab/fuzzshrink.py`
- `src/i2p_dht_lab/restartfold.py`
- `tests/test_rev0055_restartchaos_effectseal_fuzzshrink.py`
- docs `580` through `584`
