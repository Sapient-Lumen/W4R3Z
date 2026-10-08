# Finality ledger after reconcile

A reconciled effect is not automatically final. `finalityledger.py` adds signed local finality markers with sequence, previous-marker digest, family/path evidence, component digests, and exact boundary binding.

The ledger has four marker shapes:

```text
terminal_commit
terminal_abort
retry_pending
dead_letter_held
```

The risky case is a valid-looking terminal marker for an effect whose reconcile report still requires retry or dead-letter memory. rev0058 quarantines that as premature terminality. This keeps prepared-only and ambiguous effects sticky after restart.
