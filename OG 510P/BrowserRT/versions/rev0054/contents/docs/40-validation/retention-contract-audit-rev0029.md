# Retention contract audit rev0029

Revision: rev0029

Manifest id:

```txt
facility:retention-contract-audit
```

Tool:

```txt
tools/retention_contract_audit.mjs
```

Artifact:

```txt
artifacts/audit/REV0044-RETENTION-CONTRACT-AUDIT.json
```

## Purpose

This audit/factor checks that the retained-ref compaction proof is not floating alone. It verifies source, types, runtime boot surface, proof artifact, docs, manifest, impact map, surface inventory, research registry, and non-claim surfaces.

## Checks

- `PersistedSpillMailbox` exposes `compact()`.
- Source tracks retained refs and live refs.
- `compact-delete` is journaled and replayed.
- The proof artifact is current and passed.
- Manifest and impact map include proof and audit tasks.
- Surface inventory has the retention/compaction surface.
- The research registry remembers Redis, Kafka, NATS JetStream, and RocksDB retention/compaction pressure.
- Future-session docs carry the fake-provider boundary and non-claims.
- Broad release remains browser-light.

## Why this belongs

Future sessions will inherit less context. This audit gives them an office-respect surface: retention/compaction is useful, earned, and still fake-provider-only.

This audit is explicitly a coherence guard: it checks that source, proof artifact, manifest, inventory, handoff docs, and non-claim surfaces tell the same retention/compaction story.


## Rev0028 carry-forward note

This is a current-revision carry-forward audit document for `retention`. It keeps the source, docs, manifest, impact map, surface inventory, proof artifact, and non-claim boundaries visible while rev0029 adds storage-lane model and retry surfaces.
