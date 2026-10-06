# ADR-0228: Incident bundles carry PKI issuance proof by digest

Date: 2026-03-21
Status: Accepted

## Context

DeriveBSD already treats PKI and workload identity as typed evidence instead of a sidecar problem.
`docs/228-pki-and-identity-lifecycle-as-evidence.md` already established the PKI lane:

- `pki-trust-bundle` is the canonical reviewed trust-root set,
- `pki.trust.bundle.apply.receipt` proves what trust view was actually served,
- `pki-issue-plan` describes desired issuance/renewal intent,
- and `pki-issue-receipt` records issued / renewed / failed / revoked / installed outcomes.

The official incident/support-bundle contract still lagged behind that design in practice.
`incident.bundle` already had the `pki_issue_receipts` selector and `pki_issue_receipt_digests` metadata field, but the archive still did not explicitly treat that join as official support-handoff proof when identity issuance, certificate renewal, failed install, or revocation materially shaped the incident.
Canonical `bundle.plan` examples also failed to exercise the existing selector, which left the PKI issuance lane looking half-real even though the schema already had the right field.

That omission is expensive because it blurs three distinct questions:

- what trust roots were reviewed,
- what trust view was actually served,
- and which exact issuance / renewal / install / revoke actions materially participated.

Without an explicit join, support falls back to ACME control-plane screenshots, CA dashboards, or ad hoc shell notes instead of a typed answer about exact PKI actions.

## Decision

**Incident/support bundles may carry PKI issuance proof by typed digest join.**

1. **Treat the existing PKI issuance selector + metadata field as official support-handoff surfaces.**
   - `pki_issue_receipts` / `pki_issue_receipt_digests` identify the exact `pki-issue-receipt` objects proving issuance / renewal / install / revoke outcomes that materially shaped the incident.

2. **Keep reviewed trust roots, served trust view, and issuance actions distinct.**
   - `pki_trust_bundle_digest` answers what canonical trust roots were reviewed.
   - `pki_trust_bundle_apply_receipt_digests` answer what runtime trust view was actually served.
   - `pki_issue_receipt_digests` answer which exact issuance / renewal / install / revoke actions participated.
   - This ADR does not collapse PKI evidence into one generic certificate-debug field.

3. **Keep the support-handoff lane metadata-first.**
   - `pki-issue-receipt` remains a metadata object: issuer/provider, request id, serial, validity window, chain digests, status, and step correlation.
   - This ADR does not bless PEM dumps, private-key material, or CA control-plane screenshots as ordinary support-bundle truth.

4. **Make the shared bundle-plan include surface real for PKI issuance too.**
   - `spec/incident.bundle.schema.json#/$defs/include_knobs` already carries `pki_issue_receipts`.
   - `bundle.plan.selection.include` must exercise that selector when issuance/renewal/install outcomes materially shaped the incident/support story.

5. **Use the PKI issuance join when it materially shapes the story.**
   - Bundles should include `pki_issue_receipt_digests` when a new certificate, failed renewal, revoked identity, or install failure materially participated in the incident.
   - Bundles do not need to carry every historical issuance receipt.

## Consequences

- Official support handoff can now explain exact PKI actions without teaching support to trust CA dashboards, ACME logs, or ticket prose.
- Canonical bundle examples become mechanically checkable instead of placeholder-shaped for the PKI issuance lane.
- The archive keeps a narrow boundary: no new PKI subsystem, no certificate-byte export requirement, and no promotion of provider-private debug output into routine support truth.

## Alternatives considered

- **Leave PKI issuance joins implicit in prose.** Rejected: the schema already has the right surfaces, but implementers still need the archive to say they are official support-handoff truth.
- **Rely on `pki_trust_bundle_digest` plus `pki_trust_bundle_apply_receipt_digests` alone.** Rejected: reviewed trust roots and served trust view are not the same thing as the exact issuance / renewal / revoke actions that happened.
- **Add a generic `certificate_debug` field.** Rejected for now: it widens the routine handoff contract and fights the typed PKI lane.
- **Let CA dashboards or screenshots explain issuance state.** Rejected: that recreates implementation-private folklore and weakens explainability across A–D.

## Status

Accepted and wired through the canonical bundle examples, the PKI/support-bundle docs, and archive hygiene checks.
