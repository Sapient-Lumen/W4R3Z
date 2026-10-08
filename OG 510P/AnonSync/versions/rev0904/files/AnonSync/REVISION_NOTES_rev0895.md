# AnonSync rev0895 revision notes

## Mission increment

Rev0895 converts the newer causal replica stack from a set of strongly tested libraries into a separately invokable one-shot product spine. The revision adds the missing production TLS client, a non-self-test `anonsync_replica` executable, and a process-level proof that composes durable payload publication, causal SQLite claim/dispatch, mutual TLS/SPKI authorization, receiver filesystem publication, terminal receipt, and sender settlement across two independent processes.

## C++ implementation

### Production TLS client

Added `src/sync_replica_file_tls_client.hpp` and `.cpp`:

- move-only retained client `SSL_CTX` owner;
- numeric-only IPv4/unscoped-IPv6 endpoint parsing;
- exact nonblocking and close-on-exec socket creation/reproof;
- absolute-deadline connect using readiness plus `SO_ERROR`;
- bounded TLS 1.3 `SSL_connect` state machine;
- verified peer SPKI and exact actor policy before any SQLite claim;
- at-most-one durable payload-backed dispatch;
- guarded request-prefix frontier and bounded request/receipt continuations;
- exact receipt application; and
- subordinate bounded TLS shutdown plus unconditional single close.

The implementation was added to the existing file-TLS product library rather than creating another one-file static archive.

### Product executable

Added `src/anonsync_replica.cpp` with commands:

- `certificate-spki`
- `enqueue-file`
- `membership-publish`
- `send-one`
- `serve-one`

The executable links no self-test implementation library. It requires absolute filesystem/database/credential paths, numeric endpoints, bounded inputs, and emits one JSON result to stdout.

### Explicit operator-trusted clock profile

Added `SyncReplicaOperatorTrustedClockProfile` and `make_operator_trusted_sync_replica_outbox_clock_source_or_throw` for environments where synchronization evidence is externally owned but hidden from the process. Selection requires a canonical authority ID and nonzero bounded claimed uncertainty. Samples bind boot identity, best-available calling-thread time-namespace material, bracketed realtime/boottime, and the existing drift/quarantine/recovery state machine.

The normal system source remains the default and fail-closed. Operator trust is an explicit deployment assertion, not a measurement, attestation, or automatic fallback.

## Integration defects found by the product process proof

- Fixed fresh membership bootstrap by publishing against the anchored coordinator's reconciled genesis/current target instead of requiring existing current authority.
- Fixed invalid request-frame sizing by deriving protocol-reviewed non-payload headroom rather than adding a guessed 1 MiB.
- Added an explicit container clock trust surface because the correct default source cannot mint leases when host synchronization evidence is unavailable.
- Preserved the receiver's refusal to invent missing parent directories; the test provisions the parent and records causal directory semantics as missing work.

## Tests and audit maintenance

Added `tools/test_anonsync_replica_cli.py`, registered on Linux, to generate credentials and prove a complete two-process transfer with exact bytes and terminal settlement.

Extended the real TLS transport test with the production client path and extended the outbox clock test with invalid and valid operator-trusted profiles.

The first complete registry run found three lexical-audit failures caused by legitimate new production consumers and by an audit selecting the first `observe_or_throw` method after a second clock source was introduced. The audits were corrected to:

- target the named Linux system clock class rather than the first matching method;
- explicitly verify the new operator-trusted profile and CLI selection;
- include `anonsync_replica` as a reviewed bounded-file reader consumer; and
- include its typed SQLite busy-timeout gateway call.

No runtime assertion was weakened. The sanitizer target inventory was also corrected so the production TLS client/server library and `anonsync_replica` are compiled and linked with ASan/UBSan in the focused sanitizer lane; previously that nominal lane would have skipped the new product code.

The release verifier now scopes additional rev0895 integrity checks to this and later packages: README heading, gate revision, artifact revision, canonical declared package filename, and actual ZIP basename must agree. Older sealed parents remain verifiable under the policy in force for their revision.

## Documentation and architecture assessment

Added:

- `MISSION_PRODUCT_SPINE_ASSESSMENT_rev0895.md`
- `PRODUCT_SPINE_TLS_CLIENT_AUDIT_rev0895.md`

The assessment identifies the mission as authority-preserving convergence, documents the prior assurance/product inversion, ranks missing runtime/filesystem/GC/privacy work, records build/evidence waste, and compares current design with Syncthing BEP, Willow Confidential Sync, Noise, MLS, local-first work, SLSA, and SQLite's current patch release.

## Dependency note

The tree still vendors SQLite 3.53.3. SQLite 3.53.4 was released 2026-07-24 and fixes problems remaining in 3.53.0–3.53.3. The official archive and source hashes were recorded, but this cloudtainer could not acquire archive media through its available download paths. Rev0895 does not claim an SQLite upgrade. Exact official acquisition, hash verification, pin updates, and complete database validation are immediate follow-up work.

## Validation

Final sealed validation records the exact compiler lanes, registered test count, focused checks, source audits, package verification, and nonclaims in `REVISION_EVIDENCE/rev0895/validation/VALIDATION_SUMMARY.json` and `RELEASE_GATE.json`.

## Explicit nonclaims

Rev0895 does not provide a daemon, continuous scheduling, discovery, NAT traversal, directory creation semantics, tombstones, rename/symlink convergence, chunking/resume, reachability, GC, indexed performance, automatic clock recovery, cross-resource atomicity, exactly-once delivery, at-rest encryption, capability-private sync, anonymity, unlinkability, endpoint hiding, traffic-analysis resistance, Windows runtime coverage, external signed build provenance, or formal proof.

## Next milestone

Build the durable operational loop around the one-shot owners, add status and explicit clock recovery, and define causal directory/tombstone semantics. In parallel, acquire SQLite 3.53.4 and design reachability/GC plus a separate indexed catalog that is continuously checked against the full-scan oracle.
