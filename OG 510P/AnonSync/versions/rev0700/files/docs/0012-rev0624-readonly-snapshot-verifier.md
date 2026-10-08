# Rev0624 — dedicated read-only SQLite snapshot verifier

## Risk addressed

The remaining restore/snapshot verifier seam was architectural rather than cosmetic: untrusted SQLite snapshot candidates were still being evaluated through the same mutable SQLite/WAL backend loader used for active persistence. That made candidate verification depend on a broad writer-capable object, not a narrow verifier. It also risked creating lock/write-gate sidecars while evaluating a database that should be treated as hostile input.

## Change

Rev0624 adds a dedicated read-only verifier for SQLite snapshots and routes these call sites through it:

- snapshot backup verification;
- signed snapshot-manifest verification;
- restore source verification;
- restore staged temporary database verification;
- restored destination verification.

The verifier:

- rejects SQLite-family symlink sidecars before opening;
- opens with SQLite read-only flags, including `SQLITE_OPEN_NOFOLLOW` when available;
- applies a defensive profile using `SQLITE_DBCONFIG_DEFENSIVE`, `SQLITE_DBCONFIG_TRUSTED_SCHEMA`, conservative SQLite limits, `PRAGMA query_only=ON`, `PRAGMA trusted_schema=OFF`, and `PRAGMA foreign_keys=ON` where available;
- requires `PRAGMA integrity_check` to return `ok`;
- allows only `metadata`, `ledger_entries`, `backend_profile`, and the async event identity unique index;
- rejects unexpected views, triggers, virtual tables, malformed index definitions, duplicate schema objects, and wrong table columns;
- validates the backend profile and recomputes every ledger entry hash before trusting line count or head hash.

## Audit/refactor result

The high-level refactor is small but meaningful: snapshot verification is now a standalone read-only trust boundary instead of a side effect of constructing the mutable backend loader. The selftest verifies that a valid backup snapshot can be verified without mutable sidecars and that a snapshot with an injected unexpected view is rejected.

## Remaining ceiling

This does not make SQLite storage tamper-proof, distributed, or externally durable. It also does not solve the effect-idempotency boundary between an authorized decision and downstream side effects. Those remain higher-level protocol and deployment work.
