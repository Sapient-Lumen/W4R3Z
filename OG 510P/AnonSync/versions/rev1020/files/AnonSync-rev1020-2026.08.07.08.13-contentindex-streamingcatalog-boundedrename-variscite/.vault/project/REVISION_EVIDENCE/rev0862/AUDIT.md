# Rev0862 audit

## Question

Does bounding the rows and bytes returned by checkpoint-sidecar hydration also
bound the SQLite work that produces those values?

## Finding: output budgets were not execution budgets

Rev0861 correctly bounded retained paths, rows, chunks, lineage, and copied
metadata. Its `SELECT DISTINCT ... ORDER BY` could nevertheless scan and sort a
large duplicate-heavy durable relation before yielding a tiny frontier. The
caller owned the output but not the persistence engine's internal work.

Rev0862 installs the existing reviewed SQLite progress-handler capability once
for the complete read transaction. A purpose-specific adapter freezes the exact
database pointer and owner generation, admits only the execution dimensions
needed by this path, and requires both transaction and budget authority before
SQL execution and final result publication.

## Finding: generic interruption needed typed recovery

SQLite reports a nonzero progress callback as `SQLITE_INTERRUPT`. Treating that
as an ordinary database error discards whether the callback-count or elapsed-
time policy failed and loses the observed/limit evidence. Every unexpected
`sqlite3_step` result now asks the budget to publish its sticky typed failure
before generic SQLite error translation.

## Finding: callback lifetime is part of transaction safety

An exhausted callback left attached during rollback could interrupt cleanup.
The transaction is therefore declared before the budget. On success the budget
is explicitly detached before commit. On failure stack unwinding destroys and
detaches the budget before the transaction guard rolls back.

## Finding: detach had to revoke authority

The first adapter shape retained its frozen pointer and generation after
`detach()`. A live transaction could therefore reuse that object after callback
removal and execute without a budget. Rev0862 adds one-way attached state,
process/thread fencing before the state diagnosis, and a direct live-
transaction regression. Detached authority is permanently dead.

## Finding: audit execution carried ambient state

Most Python audit CTests still allowed site initialization and bytecode writes.
All 50 registered Python audit commands now use `-B -S`. Four audits that
introspect CMake were updated to require the full contract. Exact replay also
found and removed one ignored stale `__pycache__`; the package verifier rejects
its reintroduction.

## Refactor result

The integration coordinates one exact read transaction and one separately
linked execution capability. It no longer owns callback policy, callback
installation, raw interruption interpretation, or per-query timer logic. The
generic owner's hot callback performs one fail-stop execution fence and then
reads sticky state directly, avoiding duplicate process/thread checks on every
progress invocation.

## Mechanical and executable proof

- `tools/audit_sync_sqlite_sidecar_snapshot.py`: 94/94 checks.
- `anonsync_sync_sqlite_sidecar_claimed_path_snapshot_test`: 35/35 checks.
- Integrated domain model: 609/609 checks.
- Duplicate-heavy VM-step exhaustion reports the exact callback-limit type and
  count; a fresh budget then reuses the same statement and transaction.
- Elapsed-time expiry reports the elapsed-limit type; a fresh budget succeeds.
- Wrong-generation, revoked, stale, and foreign authorities are distinct.
- 100 focused executions and 100 audit executions passed without variation.
- All 49 registered audits pass under `python -B -S`.

## Remaining exposure

The progress callback cadence is approximate, not a hard real-time scheduler.
Blocking outside callback opportunities is not bounded by this owner. Other
SQLite readers need explicit classification and migration. Hostile SQLite and
document interpretation remain in the principal process. The distributed
operation algebra and the privacy/device/key plane remain incomplete.
