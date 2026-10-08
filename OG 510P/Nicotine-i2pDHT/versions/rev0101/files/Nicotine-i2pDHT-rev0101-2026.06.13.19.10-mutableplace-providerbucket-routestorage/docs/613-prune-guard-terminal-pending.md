# Prune guard for terminal and pending effects

Evidence deletion is a protocol boundary. `pruneguard.py` distinguishes terminal soft-prune from pending hold.

Terminal commit/abort may allow soft evidence to be compacted, but not:

```text
accepted finality marker
hard negatives
idempotency conflict evidence
```

Pending retry or held dead-letter state must retain:

```text
dead-letter report
retry escrow report, when present
accepted pending finality marker
```

This keeps local storage pressure from erasing the exact evidence needed for safe restart and retry.
