# Lineagefold audit/refactor

rev0026 adds `lineagefold.py`, a small current-revision navigation audit. Its job is boring and valuable: make sure the current risky surfaces are reachable from code, tests, docs, public pointers, and the active surface ledger.

Checked surfaces:

- `src/i2p_dht_lab/lineagewindow.py`
- `src/i2p_dht_lab/claimbundle.py`
- `src/i2p_dht_lab/workmeter.py`
- `src/i2p_dht_lab/lineagefold.py`
- `tests/test_rev0026_lineagebundle_workmeter.py`
- `docs/240-rev0026-lineagebundle-workmeter-fold.md`
- `docs/241-lineage-window-gap-pressure.md`
- `docs/242-claim-bundle-type-pressure.md`
- `docs/243-work-meter-garden-contribution-pressure.md`
- `docs/244-lineagefold-audit-refactor.md`

This does not delete older fold modules. It keeps current-revision navigation visible while preserving wake-from-amnesia history.
