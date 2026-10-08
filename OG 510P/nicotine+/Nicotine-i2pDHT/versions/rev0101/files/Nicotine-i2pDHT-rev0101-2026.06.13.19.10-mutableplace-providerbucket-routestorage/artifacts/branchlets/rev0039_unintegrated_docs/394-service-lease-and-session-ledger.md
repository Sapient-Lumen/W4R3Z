# service lease and session ledger

`servicelease.py` creates short-lived, signed toy service leases bound to continuity, catalog, caller, scope, object, request, and budget. `sessionledger.py` checks repeated service windows for replay, overspend, active withdrawal, hard negatives, family diversity, and refusal-only loops.

The risk is that a valid service once can become accidental indefinite permission. rev0039 makes repeated service use explicit and budgeted.
