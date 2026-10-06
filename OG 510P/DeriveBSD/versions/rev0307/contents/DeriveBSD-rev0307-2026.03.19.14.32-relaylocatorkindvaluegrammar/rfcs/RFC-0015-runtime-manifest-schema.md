# RFC-0015: Runtime manifest schema + digest rules

- Status: draft
- Author(s): (add names)
- Created: 2026-02-23
- Last updated: 2026-02-23

## Summary
Define `runtime.manifest.json` schema for microVMs and how to compute `manifest_digest`.

## Proposal (v1)
- Manifest is JSON, canonicalized via RFC 8785 (JCS).
- `manifest_digest = sha256(JCS(manifest))`
- Fields cover: resources, devices, storage, networking attachments, injection channels, secrets contract, observability, update strategy.

## Rationale
Stable digests enable:
- policy decisions at plan/run time
- audit logs that are replayable
- provenance binding between runtime + image

## Open questions
- JSON vs CBOR for v2
- How to version schema without breaking old artifacts
