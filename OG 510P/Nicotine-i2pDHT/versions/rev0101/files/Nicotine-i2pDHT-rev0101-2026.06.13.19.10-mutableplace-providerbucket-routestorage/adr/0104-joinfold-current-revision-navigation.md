# ADR 0104 — joinfold current revision navigation

Decision: rev0026 adds a current-surface audit rather than trusting prose pointers.

Reason: the cube intentionally keeps historical branchlets. Without a fold audit, the live path can drift or disappear.

Consequence: `joinfold.py` checks current code, tests, docs, public pointers, and active surface-ledger entries.
