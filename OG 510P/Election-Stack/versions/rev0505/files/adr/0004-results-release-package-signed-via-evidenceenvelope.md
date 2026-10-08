# ADR 0004: ResultsReleasePackage signed via EvidenceEnvelope (avoid signature layering)

**Track:** Shared (cross-cutting)


- Status: **Accepted**
- Date: **2026-02-27**

## Context
Track A results publishing depends on small, content‑addressed artifacts (CRO / ENRUpdate / RRP) and strict ordering (PBB + witness checkpoints; `236`).

However, early RRP sketches allowed an **inner signature field** (`package_signature`) while the archive already defines a canonical signing wrapper (`EvidenceEnvelope`; `173`–`176`). This creates ambiguity:
- which bytes are the “official signed object”,
- whether the PBB `RESULTS` leaf commits to the signed bytes, and
- how keys/rotations are audited.

## Decision
1) RRPs are published as `EvidenceEnvelope` payloads using a dedicated envelope kind:
- `kind: hfv.results.release_package`
- `payload_schema: schemas/ResultsReleasePackage.json`

2) The PBB `RESULTS` leaf commits to the **RRP payload digest** (RFC8785‑JCS), which must match the envelope `payload_digest` (`236`, `238`).

3) `ResultsReleasePackage.package_signature` is deprecated for Track A publication. It may exist for legacy pipelines, but verifiers MUST NOT treat it as sufficient without a valid envelope signature (`238`).

## Consequences
- Schema relaxation: `package_signature` is no longer required in `ResultsReleasePackage.json`.
- Registry update: new envelope kind `hfv.results.release_package`.
- Interop tripwire: results hash vectors add a “no inner signature” leaf example (`artifacts/test-vectors/results_hash_vectors.json`).
