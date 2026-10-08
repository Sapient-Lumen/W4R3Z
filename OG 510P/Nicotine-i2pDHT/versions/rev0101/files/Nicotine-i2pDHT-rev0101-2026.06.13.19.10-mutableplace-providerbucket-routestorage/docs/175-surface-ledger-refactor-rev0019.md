# rev0019 — surface-ledger refactor

rev0019 refactors the active surface ledger so it can include current risk-first modules without duplicating historical `surfaceledger.py` entries. The ledger now exposes `rev0018_entries()`, `rev0019_entries()`, and `active_entries()`.

The active rev0019 entries pin these surfaces to tests and docs:

- `leaseroute.py`
- `storemesh.py`
- `budgetreceipt.py`
- `roundledger.py`
- `surfaceledger.py`

The point is not bureaucratic neatness. It is wake-from-amnesia hygiene: every active module should have a test and a doc, while historical duplicate surfaces can remain mapped instead of silently deleted.
