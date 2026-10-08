# Publishdryrunfold audit/refactor

`publishdryrunfold.py` pins rev0049's current path:

- `publishdryrun.py`
- `witnesscompact.py`
- `scopejournal.py`
- `publishdryrunfold.py`
- `tests/test_rev0049_publishdryrun_witnesscompact_scopejournal.py`
- docs `514` through `518`

It preserves rev0048 `shadowauditfold` as predecessor history.  The audit also checks that `PUBLIC_SURFACE.json`, `HEAD_REGISTRY.json`, `docs/00-index.md`, fold map, fold registry, and surface ledger know the new revision words.
