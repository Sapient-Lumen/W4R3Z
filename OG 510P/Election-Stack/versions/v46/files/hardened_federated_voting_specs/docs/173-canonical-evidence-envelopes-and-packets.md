# 173 — Canonical Evidence Envelopes & Packets

**Track:** Shared

## Goal
Make the archive's *evidence objects* durable, portable, and machine-checkable across:
- independent verifiers,
- third‑party monitors,
- mirrors/archives,
- and long time horizons (court timelines, recounts, history).

This is an anti-drift layer: it prevents “format entropy” from slowly breaking verification, and it makes selective disclosure harder because evidence is easy to mirror and re-check.

## Design principles
1. **Content addressing first:** all evidence bytes are named by `sha256` so mirrors can prove integrity without trusting hosting.
2. **Envelope separation:** the *same* payload can be re-used in different contexts without re-signing the payload itself.
3. **Minimal mandatory metadata:** just enough to support replay protection, provenance, and verification at scale.
4. **No privacy surprises:** public packets MUST avoid per‑voter identifiers; sensitive lanes use redaction policies and separate access control.

## Canonical objects
This pack defines three normative schema objects:

- **EvidencePointer** (`schemas/EvidencePointer.json`)
  - references bytes by hash, media type, and (optional) retrieval hints.
- **EvidenceEnvelope** (`schemas/EvidenceEnvelope.json`)
  - a signed wrapper that binds:
    - what the payload *is* (kind + schema),
    - who issued it,
    - when,
    - and what subject it concerns.
- **EvidenceBundleManifest** (`schemas/EvidenceBundleManifest.json`)
  - a signed index of all objects in a bundle (public evidence packet).

### EvidencePointer (normative)
Use when the payload is stored separately (e.g., large JSON, PDF excerpt, a binary artifact).

Rules:
- `digest` MUST be `sha256:<hex>`.
- `uri` is optional and non-authoritative (mirrors can host different URIs).

### EvidenceEnvelope (normative)
Fields you should expect in every envelope:
- `envelope_version` (semver)
- `kind` (string; namespaced, e.g., `hfv.enr.snapshot`, `hfv.inspection.suppression_report`)
- `track` (A / B / C / Shared label)
- `issued_at` (RFC3339)
- `issuer` (stable id + public key reference)
- `subject` (election id, jurisdiction id, device id, etc.)
- `payload_schema` (URI/id of the JSON schema for the payload)
- `payload_inline` (inline object) OR `payload_pointer` (`EvidencePointer`) (exactly one)
- `payload_digest` (digest of RFC8785-JCS canonicalized payload bytes)
- `signatures` (one or more signatures over the envelope header + payload_digest)

**Canonicalization:** All payload digests and envelope signing inputs use **RFC 8785 (JCS)** canonical JSON.

**Signing input:** Signers MUST compute `tbs_digest` over the canonicalized *to‑be‑signed* envelope object (the envelope with `signatures` omitted). See `docs/176`.

Rules:
- Envelopes MUST be verifiable without network access if the referenced bytes are present in the bundle.
- `payload_digest` MUST match the canonical form used by verifiers in this archive (see `docs/14-receipts-and-state-machine.md`).
- Multi-signature envelopes are encouraged for high-stakes artifacts (e.g., outages, revocations, close elections).

### EvidenceBundleManifest (normative)
A bundle manifest is the “table of contents” for a public evidence packet.

Rules:
- The manifest MUST enumerate every file in the bundle that is intended for verification.
- Bundles MUST include `MANIFEST.sha256` at the repo root **and** a bundle-local manifest (this schema).
- A bundle may contain:
  - raw documents (markdown, PDFs, images) referenced by digest, and/or
  - JSON envelopes referenced by digest.
- The manifest is itself signed and should be mirrored.

## Canonical packet layout (recommended)
This layout is not strictly required, but tools in `tools/` assume it:

```
evidence_packets/<packet_id>/
  manifest.json
  objects/
    sha256-<hex>.json
    sha256-<hex>.bin
  notes/
    README.md
```

## Tooling
- `tools/evidence_packager.py` builds a packet directory from a list of artifacts and produces:
  - `manifest.json` (EvidenceBundleManifest)
  - a content-addressed `objects/` store

This tool is intentionally boring: it is meant to be forked and re-implemented by independent verifiers.

## Relationship to other docs
- Retention policy: `docs/98-evidence-bundle-provenance-and-retention.md`
- Public inspections + suppression proofs: `docs/146–149`
- North Star endorsement/reference transparency: `docs/169` and `docs/175`


## Kind registry (API surface)
Evidence envelopes use a small, registered set of `kind` values so verifiers do not need to chase
endless string drift.

- Registry: `artifacts/registries/envelope-kinds.csv`
- Policy: `178-envelope-kind-registry.md`
- Verifier surface: `179-evidence-api-surface.md`
