# bhyve backend mapping: runtime manifest → bhyve_config

DeriveBSD runtime manifests are backend-agnostic. bhyve has a documented configuration model (`bhyve_config(5)`).
We need a deterministic mapping to keep launch behavior testable and auditable.

## Inputs
- `runtime.manifest.json` (canonical JSON digest per ADR-0022 (ADR-0005 is superseded))
- bundle metadata (bundle digest)
- policy constraints (network/storage/resource ceilings)

## Outputs
- generated bhyve_config (diffable)
- launch invocation using those settings
- audit record:
  - artifact_digest
  - manifest_digest
  - config_digest
  - instance_id

## Debugging
bhyve supports emitting a configuration dump of effective settings:
- `-o config.dump=1`
Capture this in repro capsules and conformance tests.

See RFC-0021 and `docs/44-backend-conformance-tests.md`.
Last updated: 2026-02-23

## Image building pointer

Disk image determinism notes live in `docs/78-deterministic-image-building.md` (RFC-0051).
