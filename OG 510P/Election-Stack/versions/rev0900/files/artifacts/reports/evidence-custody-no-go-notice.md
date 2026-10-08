# Evidence custody/provenance no-go notice

Archive version: `v900`  
Release date: `2026-06-18`  

**No-go for live pilot use or public release of local evidence until custody/provenance records exist. Synthetic-only. This is not live election evidence, not authorization, not chain-of-custody certification, not an admissibility opinion, and not legal advice.**

## Decision

`NO_GO_LIVE_PILOT_CUSTODY_PROVENANCE_INCOMPLETE`

The archive can verify synthetic packet bytes, but live evidence handling also needs capture authorization, collector attribution, tool/version/time-source records, transfer digests, access logs, public/private separation, incident freeze records, source-review custody, chain-gap exceptions, and retention/disposition records.

## Current custody state

- Policies: `14`.
- Blocking policies: `14`.
- Missing local custody records: `14`.
- Release-gate families: `7`.

## Promotion condition

Regenerate this pack with jurisdiction-specific custody records, named owners, transfer/access logs, reviewer approvals, and documented exceptions. Live promotion remains no-go until every applicable row is closed or an accountable local exception is recorded.

## First actions

- `ECP-001` / `capture_scope_authorization` — Record who authorized collection, what surfaces are in scope, and what data is excluded before capture.
- `ECP-002` / `collector_identity_and_role` — Bind each collector to a role, affiliation/COI note, training status, and equipment-owner record.
- `ECP-003` / `capture_environment_and_tooling` — Record tool/archive version, time source, vantage point, and capture limitations while minimizing private identifiers.
- `ECP-004` / `digest_manifest_and_payload_lineage` — Preserve payload, manifest, report, and command lineage for every packet or derivative.
- `ECP-005` / `custody_transfer_handoff` — Record from/to custodian, timestamp, storage medium, and pre/post transfer digests for every handoff.
- `ECP-006` / `access_log_and_review_window` — Record who accessed evidence, why, when, and whether private fields were visible.
- `ECP-007` / `sealed_or_sensitive_material` — Separate sealed/private fields from public derivatives and document withholding reasons.
- `ECP-008` / `public_derivative_lineage` — Link public summaries, quickstarts, screenshots, and bulletins to source evidence, redaction rule, and correction pointer.
- `ECP-009` / `incident_evidence_freeze` — Freeze incident evidence before interpretation and attach a safe public sentence plus non-claims.
- `ECP-010` / `offline_drill_transcript_custody` — Preserve offline drill transcript digest, ZIP digest, verifier role, machine description, and manifest result.
- `ECP-011` / `source_review_and_pin_custody` — Record source-review reviewer, date, pin/demotion reason, and affected artifacts.
- `ECP-012` / `chain_gap_exception_and_dissent` — Make chain gaps, exceptions, reviewer dissent, owners, and expiry dates visible before relying on evidence.
- `ECP-013` / `retention_disposition_and_destruction` — Record disposition action, retention rule, digest, owner, legal hold, and date.
- `ECP-014` / `custody_provenance_gate` — Keep live promotion no-go until every applicable custody row has local records or documented exceptions.

## Boundary

Evidence custody/provenance support only; not live election evidence, not live-pilot authorization, not chain-of-custody certification, not public-records authorization, not admissibility opinion, not outcome proof, not proof of intent or fraud, and not legal advice.
