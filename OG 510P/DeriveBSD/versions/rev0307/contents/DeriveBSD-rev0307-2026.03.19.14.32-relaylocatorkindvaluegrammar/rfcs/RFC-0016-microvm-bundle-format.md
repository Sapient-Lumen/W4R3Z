# RFC-0016: MicroVM bundle directory format

- Status: draft
- Author(s): (add names)
- Created: 2026-02-23
- Last updated: 2026-02-23

## Summary
Standardize the microVM bundle directory structure and integrity root (`bundle.json`).

## Proposal (v1)
- Bundle contains `bundle.json`, `runtime.manifest.json`, image payload, and attestations.
- `bundle.json` lists file digests; `bundle_digest = sha256(bundle.json bytes)`.
- Provenance attestation binds the image + manifest digests via in-toto Statement in DSSE envelope.

## Open questions
- Support zfs refs as first-class payload (text ref + expected digest)
- Chunked downloads / streaming verification for large payloads
