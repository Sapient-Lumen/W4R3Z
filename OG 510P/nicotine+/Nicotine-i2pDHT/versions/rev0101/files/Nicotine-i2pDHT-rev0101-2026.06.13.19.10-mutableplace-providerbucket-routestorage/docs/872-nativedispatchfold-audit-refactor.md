# nativedispatchfold audit/refactor

`nativedispatchfold.py` is the rev0083 current-path fold. It checks that runtime drift, dispatch seal, native source audit, tests, docs, fold map, fold registry, active surface ledger, and the rev0082 nativeparity predecessor remain visible.

This is the audit/refactor lane for the revision. It does not delete historical surfaces; it pins the new native runtime boundary so future revisions do not hide native-selection drift behind old parity tests.
