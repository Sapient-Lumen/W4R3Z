# Effect reconciliation boundary

`effectreconcile.py` is the local join after recovery, dead-letter, and retry surfaces have spoken.

It can locally decide:

```text
accept_reconciled_commit
accept_reconciled_abort
accept_retry
accept_keep_dead_letter
hold_component_watch
quarantine_phase_conflict
quarantine_boundary_drift
quarantine_hard_negative_pressure
```

The central rule is that a terminal phase, retry decision, dead-letter memory, and side-effect journal must all bind to the same exact boundary. Commit/abort ambiguity is quarantined. Prepared-only state can remain dead-lettered. Retry can proceed only as retry-with-dead-letter-memory, not as amnesia.
