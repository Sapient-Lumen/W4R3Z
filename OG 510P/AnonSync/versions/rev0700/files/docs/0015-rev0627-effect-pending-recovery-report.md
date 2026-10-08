# Rev0627 effect pending recovery report

Rev0627 addresses the next local crash-boundary gap left after rev0626.

Rev0625 reserved every accepted decision as a prepared effect. Rev0626 added an append-only SQLite/WAL transition chain for terminal states (`applied`, `failed`, `compensated`). The remaining practical recovery problem was discoverability: after a crash, a worker or operator had to inspect SQLite directly to find prepared effects that did not yet have terminal transition evidence.

Rev0627 adds a narrow recovery surface instead of a broader registry:

```bash
anonsync_core --ledger ledger.sqlite --ledger-effect-pending-report pending-effects.json
```

The command opens the SQLite/WAL ledger read-only, applies the untrusted snapshot verifier profile, checks the exact schema allowlist, verifies the decision hash chain, verifies the effect transition hash chain, and only then emits a JSON report of prepared effects with no terminal transition row.

The report intentionally excludes JWT `jti` values and includes only recovery-routing material: ledger sequence, case id, kind, operation id, verified contract digest, action, CloudEvents identity when present, and `effect_idempotency_key`.

## Fixed in rev0627

- Added `anonsync-sqlite-effect-pending-report-v1`.
- Added `--ledger-effect-pending-report`.
- Added `--selftest-ledger-sqlite-effect-pending-recovery`.
- Refactored the read-only snapshot verifier into a single-open helper that can be reused by the report command without a verify-then-query reopen gap.
- The verifier stats now expose effect transition line count and head hash.
- Capability metadata advances to v22 and records that pending-effect reports are SQLite/WAL-only local recovery evidence.

## Still not fixed

The pending report is not a downstream worker, not distributed consensus, not delivery proof, not downstream transaction custody, and not exactly-once semantics across services. It gives a future reconciler a safe local list of prepared-but-not-terminal work.
