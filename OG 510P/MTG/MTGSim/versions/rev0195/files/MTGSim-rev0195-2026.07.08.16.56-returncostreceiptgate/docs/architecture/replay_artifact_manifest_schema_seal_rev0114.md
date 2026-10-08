# rev0114 replay artifact manifest schema seal

## Purpose

`ReplayArtifactManifest.v1` already had a header and `bundle_hash`, but the manifest schema itself was still implicit in those two places. That left a future manifest-layout migration vulnerable to being reported as a generic bundle-hash or unsupported-format issue.

rev0114 promotes the manifest protocol to `ReplayArtifactManifest.v2` and carries explicit `manifest_schema=` evidence in the serialized manifest payload. The goal is not to change snapshot or trace replay semantics; it is to make the trust wrapper around those artifacts self-describing and schema-auditable.

## New evidence surface

- `kReplayArtifactManifestSchemaVersion` is the supported manifest schema constant.
- `ReplayArtifactManifest::schema_version` is included in the manifest payload hash.
- `serialize_replay_artifact_manifest(...)` writes `MTGSim.ReplayArtifactManifest.v2` plus `manifest_schema=2`.
- `parse_replay_artifact_manifest(...)` accepts historical v1 manifests for parse diagnostics, but v2 manifests must declare exactly one nonzero `manifest_schema=` field.
- `verify_replay_artifact_bundle(...)` returns `ManifestSchemaMismatch` before snapshot parsing or trace replay when the manifest-declared schema is unsupported.

## Replay semantics

A v2 manifest with `manifest_schema=2` says that its `bundle_hash` was computed over the v2 manifest contract, including the schema value itself. A self-consistent manifest that declares a future schema can still parse, but verification rejects it before any StateCore mutation. That keeps manifest-schema drift separate from ordinary artifact tampering.

## Audit hook

`test_replay_artifact_manifest_schema_seal_rejects_schema_drift_before_replay` mutates a manifest to a self-consistent unsupported schema and confirms verification reports `ManifestSchemaMismatch` with zero replay attempts. The datacube audit probes the constant, text field, parser/verify path, CLI output, rule ledger, and this document so the manifest trust boundary remains visible.
