# settlementfold audit/refactor

`settlementfold.py` is the rev0058 current fold audit. It checks that the settlement lane, attestation pack, tombstone repair, tests, docs, public surface, head registry, and version all point to rev0058.

The audit also preserves the rev0057 predecessor line by checking that `reconcilefold.py` still exposes `audit_reconcile_fold`.

This turn's refactor aim is modest but important: the post-reconcile line is now visible as one path instead of being scattered across recovery, retry, dead-letter, and cleanup surfaces.
