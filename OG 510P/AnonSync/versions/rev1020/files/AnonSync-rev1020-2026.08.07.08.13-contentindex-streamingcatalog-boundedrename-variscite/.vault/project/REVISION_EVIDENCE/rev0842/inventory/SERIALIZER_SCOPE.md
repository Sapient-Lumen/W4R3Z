# AnonSync rev0842 serializer scope

Rev0842 classifies and freezes three additional durable/security-relevant byte domains and factors their shared locale-free primitives. It does **not** classify every serializer in the repository.

## Newly owned boundaries

- **shared frozen publication primitives** — `src/persistence/frozen_publication_primitives.hpp`: typed bounded locale-free leaf.
- **local JSONL replay row and journal** — `src/persistence/local_jsonl_replay_publication.cpp`: frozen owner; canonical load/re-encode; legacy bytes retained on injective subset.
- **SQLite snapshot manifest v2** — `src/persistence/sqlite_snapshot_manifest_publication.cpp`: 16-field frozen owner; digest/signature/JSON bind one value.
- **effect transition durable record** — `src/persistence/effect_transition_record_material.cpp`: frozen owner; exact JSON counters; legacy material retained on injective subset.
- **effect transition intent** — `src/persistence/effect_transition_intent_publication.cpp`: uses shared primitives; current v3 unchanged.
- **bounded document read** — `src/sync_bounded_regular_file.cpp`: single-link variant reused by manifest/trust/request/config readers.

## Remaining stream sites

- `src/sync_domain_selftests.cpp`: 13 `ostringstream` constructions.
- `src/reporting_selftests.cpp`: 9 `ostringstream` constructions.
- `src/sync_operator_cli.cpp`: 8 `ostringstream` constructions.
- `src/runner.cpp`: 5 `ostringstream` constructions.
- `src/persistence/sqlite_replay_ledger_reset_documents.cpp`: 3 `ostringstream` constructions.
- `src/sqlite_replay_ledger.cpp`: 3 `ostringstream` constructions.
- `src/json_codec_crypto.cpp`: 2 `ostringstream` constructions.
- `src/sync_daemon_heartbeat_document.cpp`: 2 `ostringstream` constructions.
- `src/persistence/canonical_projection_verifier.cpp`: 1 `ostringstream` constructions.
- `src/persistence/sqlite_replay_ledger_reset_receipt_protocol.cpp`: 1 `ostringstream` constructions.
- `src/persistence/sqlite_snapshot_seal.cpp`: 1 `ostringstream` constructions.
- `src/reporting.cpp`: 1 `ostringstream` constructions.
- `src/sync_atomic_file_publication.cpp`: 1 `ostringstream` constructions.
- `src/sync_domain.cpp`: 1 `ostringstream` constructions.
- `src/sync_sqlite_support.cpp`: 1 `ostringstream` constructions.

Many remaining sites are diagnostics or selftest fixture emitters; each machine-facing site still requires individual classification. A blind global replacement would conflate human reports with signed or durable bytes.
