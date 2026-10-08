# Python surface — rev0057

New modules:

- `deadletter.py`
- `retryquorum.py`
- `effectreconcile.py`
- `reconcilefold.py`

New tests:

- `tests/test_rev0057_deadletter_retry_reconcile.py`

The tests pin prepared-only dead-letter acceptance, missing budget quarantine, replay/fork detection, phase drift detection, retry quorum acceptance, useful-refusal backoff, effect retry, terminal commit reconciliation, boundary drift, and current fold visibility.
