# Rev0861 audit

## Question

Can a caller treat checkpoint-sidecar recovery evidence as one authoritative
value when its rows were read on different SQLite connections or in separate
autocommit snapshots?

## Findings

### 1. Snapshot splicing

The former path selected claimed workorder paths, then opened a second database
connection and issued independent schema, apply-intent, manifest-header, chunk,
and lineage reads. SQLite WAL readers see a stable snapshot only for the
lifetime of one read transaction. Separate autocommit statements may therefore
observe different committed generations. The old code could assemble a result
that never existed atomically.

Rev0861 opens one read-only FULLMUTEX owner, begins one deferred typed
transaction, makes claimed-path selection the first data read, and passes one
copied `SyncSqliteTransactionAuthority` through all nested loaders. The
transaction commits only after the complete staged value is valid.

### 2. Unbounded frontier materialization

The old claimed-path vector had no aggregate row or byte admission. The new
owner validates positive limits, queries at most `max_paths + 1`, accounts each
path before retention, and rejects the sentinel row. It owns one reusable typed
statement and resets and clears bindings on both success and exception.

This bounds returned rows and copied bytes. It does not by itself bound every
SQLite VM step required to produce a `DISTINCT` frontier; that remaining
performance authority is explicitly not claimed.

### 3. Collation is identity policy

A durable column may declare `NOCASE`. Without an explicit expression
collation, session, worker, lease, work-state, path, and manifest joins could
merge byte-distinct principals or objects. Rev0861 uses `COLLATE BINARY` on all
security-relevant equality and ordering expressions in the snapshot path. The
focused corpus creates a hostile `NOCASE` schema and proves that case variants
are excluded while byte-distinct paths remain distinct.

### 4. Namespace and schema inventory

Every durable table in this path is explicitly `main`-qualified, so a TEMP
shadow cannot redirect evidence. Table inventory is read once inside the
snapshot and reused; the former per-path schema probes are removed. Schema
version and copied schema text consume the shared metadata budget.

### 5. Nested resource authority

Public recovery limits independently cap claimed paths, claimed-path bytes,
manifest chunks, manifest lineage rows, and total copied metadata. Nested
loaders use exact storage-class decoders, cardinality sentinels, contiguous
indices, and one `SyncManifestResourceBudget`. Budget exhaustion precedes
filesystem mutation and result publication.

### 6. Sticky publication

Previously, an exception after some fields were assigned could return a
caller-visible half-hydrated object while the final loaded flag remained false.
Rev0861 builds a local pending result, commits the read transaction, then moves
it into the caller output. A compile-time assertion requires that result move
assignment be nonthrowing. Failure leaves only the initialized request identity
and the explicit transport-payload-not-required fact.

## Refactor result

The claimed-path persistence loop is now a separately compiled capability with
an exact database generation and typed transaction authority. The integration
coordinates one snapshot and bounded nested loaders rather than owning an
unbounded frontier statement. The 69-check source audit rejects reintroduction
of extra opens, extra commits, unqualified durable tables, inherited
collations, repeated schema probes, partial publication, absent limits, or
missing package enforcement.

## Mechanical and executable proof

- `tools/audit_sync_sqlite_sidecar_snapshot.py`: 69/69 checks.
- `anonsync_sync_sqlite_sidecar_claimed_path_snapshot_test`: 27/27 checks.
- Integrated domain model: 607/607 checks, including aggregate limit failures
  and caller-visible sticky-result assertions.
- WAL regression: a writer commits after the first reader step; the open read
  transaction retains the old generation, while a new transaction observes the
  new generation.

## Remaining exposure

Output cardinality is not a complete CPU budget. The `DISTINCT` frontier needs
an attested supporting index or a typed progress-handler/time budget tied to the
same connection generation. Other purpose-specific readers still need the same
single-snapshot classification. Hostile persistence interpretation remains in
the principal process, and the product-defining distributed operation algebra
and privacy/key plane remain incomplete.
