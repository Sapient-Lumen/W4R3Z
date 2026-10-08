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

## Versioning and compatibility (semver)

`EvidenceEnvelope.envelope_version` uses **semver** and defines the verifier’s interoperability contract.

Verifier rules:
- A verifier MUST reject envelopes whose **major** version it does not support.
- A verifier SHOULD accept the same major version with higher **minor/patch** versions unless it relies on fields that are missing or has an explicit safety reason to fail closed.
- A verifier MUST treat unknown `kind` values as “unknown kind” failures (publishable), not as “success”.

Maintainer rules (what a bump means):
- **Patch**: editorial changes; clarifications; tightening validation; examples/tools updates; *no* change to canonicalization, digesting, or required fields.
- **Minor**: additive, backwards-compatible changes (new optional fields, new optional attachments, new kinds marked `experimental`, new receipt profiles).
- **Major**: any breaking change (field removal/rename, changed digest/signing inputs, canonicalization changes, or semantics that would make old verifiers mis-verify).

Pack note: the archive `VERSION` is a release label for this repository. It is not the wire format version; envelope/payload versions can remain stable across many pack releases.

## Canonical packet layout (recommended)
This layout is not strictly required, but tools in `tools/` assume it:

```
evidence_packets/<packet_id>/
  manifest.json
  envelopes/
    <name>.envelope.json   # human-friendly envelope copies (see also objects/)
  objects/
    sha256-<hex>.<ext>     # content-addressed payloads/envelopes/attachments
  notes/
    README.md
```

Notes:
- Reference verifiers (e.g., `tools/observer_verify_packet.py`) read envelopes from `envelopes/`.
- The *canonical* bytes are still the content-addressed entries under `objects/` (as indexed by `manifest.json`).

## Tooling
- `tools/evidence_packager.py` builds a packet directory from a list of artifacts and produces:
  - `manifest.json` (EvidenceBundleManifest)
  - a content-addressed `objects/` store

This tool is intentionally boring: it is meant to be forked and re-implemented by independent verifiers.

### Publishable packet preflight (recommended)

For packets intended to be **publicly shareable** (cards, parity snapshots, liveness beacons, dispute bundles), run both:

One-command convenience (recommended):
- Structural integrity + conservative publication hygiene lint:
  - `python3 tools/observer_verify_packet.py <packet_dir> --lint-public`

Or run the two steps separately:
- `python3 tools/observer_verify_packet.py <packet_dir>`
- `python3 tools/public_artifact_lint.py --packet <packet_dir>`

The linter is deliberately conservative; it is a drift firewall, not a substitute for the redaction checklist (`DOC:docs/189...`).

Optional (recommended for dispute bundles + mirroring):
- Generate a **publishable public fingerprint** digest over the bounded packet surfaces:
  - One-command (recommended when available):
    - `python3 tools/observer_verify_packet.py <packet_dir> --lint-public --public-fingerprint --public-fingerprint-out public-fingerprint.json --public-fingerprint-stable`
  - Or generate directly:
    - `python3 tools/public_fingerprint_report.py <packet_dir> --write-default --stable`

- Verify a shipped fingerprint file matches the packet bytes (useful when reviewing mirrored bundles):
  - `python3 tools/observer_verify_packet.py <packet_dir> --lint-public --verify-public-fingerprint`

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
