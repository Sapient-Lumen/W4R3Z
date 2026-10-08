# Riskfold audit/refactor

rev0025 adds `riskfold.py`, a tiny current-revision audit for the joined risk surfaces:

- `capgate.py`,
- `evidencegc.py`,
- `splitmerge.py`,
- `riskfold.py`,
- `tests/test_rev0025_capgate_evidence_splitmerge.py`,
- docs `231` through `235`,
- public-surface and head-registry pointers,
- active surface-ledger entries.

This audit is deliberately boring. The point is to stop the cube from accumulating valuable but orphaned pressure surfaces. If a future revision moves or supersedes these modules, the fold should either follow the new path or mark the old one as historical rather than silently losing it.
