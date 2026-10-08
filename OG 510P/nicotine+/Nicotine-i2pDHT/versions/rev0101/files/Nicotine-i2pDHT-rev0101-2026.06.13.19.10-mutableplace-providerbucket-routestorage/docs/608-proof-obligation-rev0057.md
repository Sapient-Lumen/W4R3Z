# Proof obligation — rev0057

The current proof obligation is local and deterministic:

```text
If an effect is unresolved after recovery, then dead-letter memory must exist before retry or reconciliation.
If retry is accepted, it must carry dead-letter memory forward.
If commit/abort is terminal, conflicting dead-letter or journal phase evidence must quarantine.
```

Evidence command:

```bash
PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q tests/test_rev0057_deadletter_retry_reconcile.py
```
