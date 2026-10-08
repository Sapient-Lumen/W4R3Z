# C++ core revision rev0767

Rev0767 establishes a typed, exact peer-ingress SQLite schema authority boundary.

## New invariant owners

- `src/sync_peer_ingress_schema_sql.hpp` contains the eleven plain-`CREATE` reviewed objects.
- `src/sync_sqlite_schema_identity.cpp/.hpp` produces a length-framed lexical identity for DDL.
- `src/sync_peer_ingress_schema.cpp/.hpp` owns bootstrap, markers, exact manifest verification, cohost dependency checks, authorizer fencing, and handle/generation-bound attestation.

## Lifecycle rule

Opening a connection does not authorize its later statements. Every peer-ingress operation first establishes its own read or write transaction snapshot, then calls the schema-attestation verifier. Existing marked databases are inspected with `BEGIN`; only empty bootstrap and exact legacy migration escalate to `BEGIN IMMEDIATE` and re-inspect.

## Failure rule

Partial schema, wrong marker pair, trigger/view, temp object, attached database, virtual/shadow table, arbitrary cohost object, cross-domain foreign key, changed schema generation, or capability/handle mismatch fails before domain mutation. No `CREATE ... IF NOT EXISTS` is used for active peer-ingress bootstrap.

## Validation

- ordinary CTest: 40/40
- ASan+UBSan CTest (`detect_leaks=0`): 40/40
- schema attestation: 48/0
- payload/runtime: 38/0
- domain: 588/0
- lifecycle: 49/0
- retention integrity: pass
