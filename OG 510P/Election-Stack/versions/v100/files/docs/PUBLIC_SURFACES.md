# Public surfaces index
This document is a compact index of the archive’s **public surfaces**: small identifiers and schemas that external implementers may depend on.
If you change any of these in a way that could break consumers, prefer an ADR + a migration story.

| Surface | Canonical source | Digest | Human view | Notes |
|---|---|---|---|---|
| Envelope kinds (kind → schema) | `artifacts/registries/envelope-kinds.csv` | `sha256:191ce8b89311…` | docs/EVIDENCE_OBJECT_CATALOG.md (generated), docs/178-envelope-kind-registry.md | Treat as a stable API surface; add via ADR when semantics change. (18 entries.) |
| Required attachments per kind | `artifacts/registries/envelope-attachment-requirements.csv` | `sha256:42ef26da7c28…` | docs/EVIDENCE_OBJECT_CATALOG.md (generated), docs/180-receipts-and-gossip-attachments.md | Anti-selective-disclosure firewall; changes can be breaking. (18 entries.) |
| Receipt profiles | `artifacts/registries/receipt-profiles.csv` | `sha256:315aeba9765f…` | docs/182-receipt-profiles-and-mappings.md, docs/185-receipt-semantics-tiers.md | Profile IDs are public strings; keep small and stable. (7 entries.) |
| Publishable verifier problem codes | `artifacts/registries/verifier-problem-codes.csv` | `sha256:2727e20a0b22…` | docs/VERIFIER_PROBLEM_CODES.md (generated), docs/193-publishable-verifier-reports.md | Designed for cross-verifier comparability; registry is strict + sorted. (42 entries.) |
| Official communication channel IDs | `artifacts/registries/official-channels.csv` | `sha256:5d8695da948e…` | docs/186-incident-communications-as-evidence.md, artifacts/checklists/official-communications-channels-hardening-checklist.md | Channel IDs appear in PublicNotice payloads; changes require migrations. (8 entries.) |
| Publication trigger vocabulary | `artifacts/registries/publication-triggers.csv` | `sha256:89e8d592492c…` | docs/184-publication-trigger-vocabulary.md | Used for incident comms + compliance coverage; keep IDs stable. (8 entries.) |
| EvidenceEnvelope schema | `schemas/EvidenceEnvelope.json` | `sha256:0fd31edb64d3…` | docs/173-canonical-evidence-envelopes-and-packets.md, docs/176-canonicalization-and-signing-rules-for-evidence-envelopes.md | Envelope header semantics; versioned by envelope_version. |
| PacketVerificationReport schema | `schemas/PacketVerificationReport.json` | `sha256:dc99fc01dd1b…` | docs/193-publishable-verifier-reports.md | Packet-scoped publishable verifier output. |
| VerifierReport schema | `schemas/VerifierReport.json` | `sha256:5fed7097e267…` | docs/193-publishable-verifier-reports.md | Implementation-scoped verifier identity + conformance claims. |
| External source lockfile IDs | `evidence/lock/external-sources.toml` | `sha256:dcabec0c0d44…` | docs/191-external-source-lockfile-playbook.md | Cite, don’t bloat; pinned sources are treated as normative references. |

## Full digests

Full sha256 digests for canonical sources listed above (computed from file bytes at generation time; also present in `MANIFEST.sha256`).

- `artifacts/registries/envelope-kinds.csv` — `sha256:191ce8b8931139edbfc20634b526e96a1d646ac61f71b6aa3ed9e28c0f0d98cb`
- `artifacts/registries/envelope-attachment-requirements.csv` — `sha256:42ef26da7c28b9c954bf9f819c64abd53c8b549031a1c0fe6831bee193bb6536`
- `artifacts/registries/receipt-profiles.csv` — `sha256:315aeba9765fc35492afaea3068569cb8a62d4482d3e000d57748b17cc7536e4`
- `artifacts/registries/verifier-problem-codes.csv` — `sha256:2727e20a0b22da683387aafadff751cce2c579affa925ab10af34b965b6b629d`
- `artifacts/registries/official-channels.csv` — `sha256:5d8695da948efd5eef9b83e95782e0cc05b8465bdab1a5ea43deea6d7979250d`
- `artifacts/registries/publication-triggers.csv` — `sha256:89e8d592492c9512477d5916323907a4cdd6c76781623aed7929fa7e205b14e7`
- `schemas/EvidenceEnvelope.json` — `sha256:0fd31edb64d30f8ca5691c820cabcaf4fe0e105b69559daa41399856a44d0f4c`
- `schemas/PacketVerificationReport.json` — `sha256:dc99fc01dd1bbe198db98c994e7424588674cdcde0e0c981be5e0353197e4e4b`
- `schemas/VerifierReport.json` — `sha256:5fed7097e2674311883b0e2c1ee465176b95cfb77e3518b6bfd59e6fdbb58288`
- `evidence/lock/external-sources.toml` — `sha256:dcabec0c0d4443bd4bdc85ef3978912d6cf9fd4c4c859120555319b3337faa05`
