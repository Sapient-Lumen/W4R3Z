# ADR-0056: Export boundary posture by profile

- **Status:** Accepted
- **Date:** 2026-03-06

## Context

DeriveBSD already has the pieces for a credible **export boundary**:
`docs/251-export-policies-and-support-bundle-portal.md` makes export an explicit policy + receipt lane,
`docs/433-export-policy-diff-as-review-surface.md` makes drift reviewable,
`docs/195-deterministic-redaction-transforms.md` narrows deterministic privacy controls,
and the recent A–D profile work already fixes recovery, remote assistance, key use, and data-at-rest defaults.

What the archive still lacked was the **product-shape default** for evidence leaving the system.
Without that, different deployments quietly normalize incompatible and dangerous habits:

- A quietly treats vendor/support upload as an ad-hoc oncall action with weak ticket/encryption discipline.
- B has a user-facing export portal, but no stable default for recipient visibility, redaction, or remembered authority.
- C cannot tell whether explicit adapter fallback is acceptable or whether all exports must be purely Derive-managed.
- D risks turning factory/regulatory evidence sharing into undocumented "email the tarball" practice or permanent broad export exceptions.

We do **not** need to freeze one ticketing system, one transport backend, or one transparency log here.
We do need a stable, checkable answer to:

- which product shapes may export evidence interactively,
- when ticket ids, encryption, redaction, or two-person integrity are the default rather than an optional footnote,
- which shapes allow adapter-shaped handoff,
- and which shapes treat raw-blob or broad-recipient expansion as exceptional review events.

## Decision

We define export-boundary posture as a **profile-shaped default** and thread it into `spec/examples/product.profiles.json` under the stable `evidence_exports` knob.

Cross-profile guardrail:
- Export remains a separately governed lane: selection, transform, recipient, and transport are explicit rather than ambient follow-up behavior.
- Raw blob export (coredumps, memory images, wide trace payloads) is **not** a first-class default in any profile.
- External-recipient handoff should be encrypted and receipted by default.
- Any remembered authority must land in a lease or durable policy object rather than becoming a silent ambient exception.

### A) `fleet_host`

Default posture: `brokered-ticketed-encrypted-external-two-person`

- Fleet evidence export is brokered and ticket-shaped by default.
- Encryption is expected for external recipients.
- Boundary expansion (new external recipient class, consent relaxation, raw blob enablement) should require stronger review, typically two-person integrity.
- The host itself does not rely on ad-hoc interactive "send logs now" behavior as the authority model.

### B) `workstation`

Default posture: `user-mediated-redacted-recipient-visible-encrypted-external`

- Evidence export is allowed through a visible trusted-UI path.
- Recipient identity/class and redaction posture should be visible to the human before bytes leave.
- External export should be encrypted by default.
- Remembered support/export authority must still land in a lease or durable policy object rather than an invisible background exception.

### C) `general_os`

Default posture: `brokered-preferred-ticketed-explicit-adapter-fallback`

- Derive-managed export policy/receipt lanes are preferred.
- Compatibility with classic support tooling is allowed only as an explicit adapter-shaped fallback.
- Ticketing, encryption, and redaction remain the expected posture for Derive-managed lanes even when fallback exists.

### D) `appliance_factory`

Default posture: `minimal-redacted-encrypted-two-person-transparency-required`

- Factory/regulatory export should prefer minimal, redacted evidence by default.
- External or cross-boundary export should be encrypted, ticketed/case-bound, and normally require two-person integrity.
- Transparency logging of the export act is required by default in the highest-assurance/exported-evidence lanes.
- Raw blob convenience export is out of bounds unless explicitly approved as a narrow maintenance exception.

## Consequences

- Product profiles now carry a stable `evidence_exports` default.
- `tools/check_product_profiles.py` must enforce this boundary so the archive cannot silently drift back toward ambient support uploads, invisible remembered export authority, or factory evidence handoff by folklore.
- Risk item 51 narrows from a product-default question to implementation detail: diff risk-flag vocabulary, approval thresholds by change class, transport-independent ticket semantics, and privacy-safe transparency metadata.

## Non-goals

- Choosing one ticketing system, attachment API, or upload backend.
- Freezing the exact transparency-log implementation for all profiles.
- Defining every export artifact class, retention budget, or redaction transform here.
