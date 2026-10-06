# Incident bundles carry PKI issuance proof by digest

**Tier:** B (Cross-cutting evidence boundary)  
**Profiles:** A, B, C, D  
**Pillars:** operability, supply-chain, isolation  
**Patterns:** Plan→Apply→Receipt, Bundles  

DeriveBSD already decided that PKI and workload identity should be explicit, receipted, and reviewable.
This doc fixes the smaller but implementation-shaping support/export question the archive still left fuzzy in practice:

**how does the official incident/support bundle contract name the exact issuance / renewal / install / revoke actions that materially shaped the incident?**

The answer is intentionally narrow.
It is not a new PKI subsystem, not a certificate dump, and not a permission slip to ship private keys or renderer-specific debug output.
It is the missing decision to make the existing `pki-issue-receipt` join real through the official support-handoff contract.

See also:
- ADR: `adrs/ADR-0228-incident-bundles-carry-pki-issuance-proof-by-digest.md`
- PKI lifecycle lane: `docs/228-pki-and-identity-lifecycle-as-evidence.md`
- trust-view apply proof: `docs/622-trust-bundle-apply-receipts-bind-canonical-bundles-to-runtime-views.md`
- trust-view support-handoff join: `docs/624-incident-bundles-carry-trust-bundle-apply-proof-by-digest.md`
- incident bundles: `docs/216-incident-snapshots-and-support-bundles.md`
- support handoff contract: `docs/481-support-bundle-contract-and-timeline-first-handoff.md`
- bundle plans: `docs/253-bundle-plans-and-deterministic-exports.md`
- evidence spine: `docs/229-evidence-spine-overview.md`

## Why this needs a hard decision

The PKI lane already existed:

- `pki-trust-bundle` keeps reviewed trust roots explicit,
- `pki.trust.bundle.apply.receipt` proves what trust view was actually served,
- `pki-issue-plan` keeps desired issuance/renewal intent explicit,
- and `pki-issue-receipt` records what issuance / renewal / install / revoke action actually happened.

But the official support/export contract still lagged behind that design in practice.
`incident.bundle` could already carry `pki_issue_receipt_digests`, but the archive still did not explicitly teach that support handoff should use that typed join when identity issuance or renewal materially shaped the incident.
Canonical bundle plans also failed to exercise the existing selector, which left the PKI issuance story weaker than the schema.

A coherent archive should let support bundles answer three different questions distinctly:

- **what trust roots were reviewed?**
- **what trust view was actually served?**
- **what exact issuance / renewal / install / revoke actions materially participated?**

## Accepted boundary

### 1) Bundles may carry exact PKI issuance proof

Support bundles should not force readers to infer certificate activity from CA dashboards, ACME logs, or ticket prose.

- `pki_issue_receipt_digests` name the exact `pki-issue-receipt` objects that materially belong to the incident.
- The referenced receipts remain metadata-first and answer which issuer/provider path ran, which request id or order id correlated, which serial / validity window / chain digests resulted, and whether the action issued, renewed, failed, installed, or revoked.

That keeps exact PKI action proof on the official support contract without teaching the bundle to carry certificate/private-key dumps.

### 2) Keep trust roots, served trust view, and issuance actions separate

This is the design cut worth preserving.
The archive does **not** collapse all PKI evidence into one generic certificate-debug field.

- `pki_trust_bundle_digest` is the typed join for reviewed canonical trust roots.
- `pki_trust_bundle_apply_receipt_digests` are the typed joins for what trust view was actually served.
- `pki_issue_receipt_digests` are the typed joins for exact issuance / renewal / install / revoke actions.

That keeps “what roots were approved?”, “what trust view was live?”, and “what certificate action happened?” separately explainable.

### 3) The official selector is now treated as real

The canonical include surface already carries `pki_issue_receipts`.
Because `bundle.plan.selection.include` reuses `incident.bundle` include knobs, the same selector applies both when planning a support bundle and when recording what the final bundle included.

That means official support-bundle planning can stop treating PKI issuance as prose-only.
`bundle.plan` should use `pki_issue_receipts` when the incident is identity/credential-shaped.

### 4) PKI evidence stays metadata-first on the routine handoff lane

This boundary does not promote PEM dumps, private-key material, ACME account state, or CA control-plane screenshots into the official bundle truth model.
The bundle contract remains metadata-first:

- exact `pki_trust_bundle_digest` for reviewed trust roots,
- exact `pki_trust_bundle_apply_receipt_digests` for served trust-view proof,
- exact `pki_issue_receipt_digests` for the participating issuance/renewal/install/revoke actions,
- no routine certificate-byte or private-key export lane hidden inside support collection.

That keeps the PKI lane usable across A–D without degrading the isolation story.

## Practical meaning by product shape

### A / secure fleet host

Fleet incidents can now prove which exact certificate issuance or renewal action happened to a workload or host without normalizing ACME logs or CA dashboards into support truth.

### B / secure workstation

Workstation support handoff can now export exact `pki-issue-receipt` proof when a brokered app/service identity changed, failed to renew, or installed incorrectly, without shipping raw certificate/private-key material.

### C / general-purpose OS

C keeps compatibility adapters possible, but the Derive-managed support story now has a typed answer for exact PKI actions instead of generic control-plane screenshots or shell archaeology.

### D / appliance / factory / regulatory

Production and audit lanes can now show exact issuance / renewal / revoke evidence during an incident window without turning support bundles into raw certificate archives.

## Guardrail

- `tools/check_pki_issue_bundle_contract.py`

The guardrail checks that the official bundle selector and metadata surfaces keep PKI issuance proof explicit, that canonical bundle examples bind the real `pki-issue-receipt` digest, and that the relevant docs keep teaching the same PKI/support-bundle story.

## What remains open

This doc does **not** fix:

- the exact default bundle templates for every certificate/identity incident class,
- whether future support handoffs should also join richer `pki-event` summaries directly,
- how many recent PKI issue receipts bundle templates should keep by default,
- or broader provider-specific debug export lanes.

The expensive hard decision is smaller:
DeriveBSD incident bundles no longer get to mention issuance, renewal, install failure, or revocation only in prose while hand-waving the exact `pki-issue-receipt` proof.

Last updated: 2026-03-21r368
