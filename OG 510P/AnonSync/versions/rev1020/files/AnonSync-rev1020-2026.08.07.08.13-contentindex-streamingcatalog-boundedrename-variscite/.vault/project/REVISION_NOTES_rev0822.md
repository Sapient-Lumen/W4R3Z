# AnonSync rev0822 revision notes

## Mission-level result

AnonSync is an **evidence-authorized convergence engine**. A successful syscall, open, query, signature, callback, pointer lookup, transaction, backup, or rename is an observation. It becomes transition authority only when the invariant owner binds the exact bytes, identity, generation, process incarnation, lifetime, policy, relationship, resource budget, and durability evidence required for that transition.

Rev0822 applies that rule to live replay-ledger backup. A source database handle authorizes one consistent private capture. A verified resident image authorizes exact publication. It does not authorize deletion, direct writable opening, or later cleanup of an unrelated destination SQLite family; and equality of row counts does not establish durable ledger identity.

## Parent defect and differential

Rev0821 deleted the destination main/WAL/SHM/journal family, created parent directories before source verification, opened the final pathname read/write, copied directly into it, canonicalized there, reopened the path, and accepted it when loaded entry count matched.

The exact same adversarial test changes only the durable `ledger_instance_id` to another syntactically valid value. Rev0821 publishes it and exits 2. Rev0822 verifies the private resident image against the live identity, rejects before creating the requested destination directory, and passes 36/36.

## Private live capture and exact publication

`SealedSqliteSnapshot::capture_database()` now accepts an already-open full-mutex, autocommit source. It rejects policy/geometry errors before any private destination open, copies through SQLite's online backup API into `:memory:` on the pinned VFS, disables trusted schema, keeps temp storage in memory, and runs private `VACUUM` to produce standalone rollback-journal 1/1 bytes.

The seal preflights serialized extent, directly adopts SQLite's allocation with `sqlite3_free`, binds exact geometry and SHA-256, and owns no cleanup pathname. One resident image feeds logical verification and capability-bound atomic publication.

Backup compares durable entry count, decision count/head, `ledger_instance_id`, transition count/head, and outbox state. A complete-gate failure caught an attempted comparison between durable transition rows and a session-local success counter that resets after reopen. Rev0822 removes that telemetry from authorization and adds a structural prohibition against reintroducing it.

Destination sidecars are rejection evidence, not deletion authority. Parent directory creation occurs only after source evidence passes. Publication uses the typed atomic owner and post-publication sidecar races are classified as effectful failures.

## Validation

- parent lineage: ZIP 25/25 and directory 21/21;
- one uninterrupted complete CTest gate: 101/101;
- source audits: 276/276;
- focused repeat: 75/75 executions, 3,450/3,450 checks;
- GCC 14 and Clang 17 `-Werror`: 4/4 changed C++ translation units each;
- scoped Clang 17 ASan/UBSan: 3/3 focused production paths;
- 8192-byte nondefault page capture: passed;
- source patch replay: 12/12 changed active files byte-exact.

## Highest-priority next work

The sole remaining `unlink_sqlite_family()` caller is `load(reset=true)`. Reset should become an explicit administrative transition carrying expected prior ledger identity, owner generation, namespace proof, and durable receipt rather than an ordinary boolean load option.

The live-copy preflight/postcheck does not yet prove that concurrent source growth cannot transiently exceed memory policy during `sqlite3_backup_step(-1)`. Add a verified destination page ceiling or bounded-step protocol and a concurrent-growth oracle.

The long-lived process still interprets hostile SQLite artifacts; same-UID directory writers can race point-in-time namespace checks. No Windows, arbitrary power-loss, full-project sanitizer, leak-sanitizer, distributed convergence, confidentiality, anonymity, metadata-hiding, key-lifecycle, or secure-erasure property is claimed.

Full evidence is under `REVISION_EVIDENCE/rev0822/`.
