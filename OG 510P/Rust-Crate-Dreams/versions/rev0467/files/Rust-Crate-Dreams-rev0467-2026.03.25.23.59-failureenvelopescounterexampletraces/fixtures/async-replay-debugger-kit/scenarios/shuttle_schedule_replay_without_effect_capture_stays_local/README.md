# Shuttle schedule replay without effect capture stays local

This scenario captures a failing async/concurrency test reproduced from a Shuttle seed or saved schedule.
The important truth is that schedule authority can be strong while external effects are still outside the replay contract.

What the receipts should prove:

- that the schedule basis is deterministic and local,
- that nondeterministic effects not captured remain explicitly live or manual-review-only,
- and that the fidelity claim stays bounded accordingly.
