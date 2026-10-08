# ADR 0033 — Local head memory and garden witness receipts

Accepted for rev0009. Clients and gardens keep local mutable-head memory. Gardens may sign receipts for rollback, fork, previous-link mismatch, or missing-previous observations.

Consequences: receipts are evidence, not consensus, and can be ignored by clients that do not trust the witness.
