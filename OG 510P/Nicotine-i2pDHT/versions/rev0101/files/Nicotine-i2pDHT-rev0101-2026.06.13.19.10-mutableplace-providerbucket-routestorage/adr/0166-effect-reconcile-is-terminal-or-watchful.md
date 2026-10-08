# ADR 0166 — Effect reconcile is terminal or watchful

Status: accepted in rev0057.

Reconciliation may accept terminal commit/abort, accept retry with dead-letter memory, or keep dead-letter watch. Commit/abort phase conflicts quarantine.

This keeps local side-effect truth monotonic without pretending to solve distributed consensus.
