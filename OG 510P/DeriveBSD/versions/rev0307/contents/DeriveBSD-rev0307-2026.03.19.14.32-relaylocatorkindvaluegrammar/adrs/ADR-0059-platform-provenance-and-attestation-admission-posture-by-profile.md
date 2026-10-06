# ADR-0059: Platform provenance and attestation-admission posture by profile

- **Status:** Accepted
- **Date:** 2026-03-06

## Context

DeriveBSD already has a serious **measured-boot / attestation lane** on paper:
`docs/176-measured-boot-attestation.md` makes measurement evidence first-class,
`docs/226-platform-posture-and-attestation-results-as-evidence.md` defines typed receipts,
`docs/388-remote-attestation-admission-and-enrollment.md` turns attestation into admission policy,
and `docs/440-attestation-admission-policy-diff-as-review-surface.md` makes weakening drift reviewable.

What the archive still lacked was the **product-shape default** for platform provenance.
Without that, the archive quietly allows incompatible stories to coexist:

- **A** may collect measurements forever without clearly gating secrets, identity, or rollout on them.
- **B** may either ignore measured posture entirely or accidentally turn remote verifier reachability into a surprise requirement for ordinary local use.
- **C** cannot tell whether attestation is a real optional lane or a hidden expectation.
- **D** may retain evidence but fail to say whether production enrollment, maintenance access, or secret release should actually depend on measured posture.

We do **not** need to choose one verifier stack, one PCR policy set, or one attestation service here.
We do need a stable, checkable answer to:

- when measured posture is merely exportable evidence vs a default gate for sensitive admissions,
- where retained measured posture is part of production/factory governance,
- how workstation/local usability differs from fleet/factory admission strictness,
- and how optional attestation lanes stay optional for general-purpose installations.

## Decision

We define platform provenance as a **profile-shaped default** and thread it into `spec/examples/product.profiles.json` under the stable `platform_provenance` knob.

Cross-profile guardrail:
- measured posture must be **receipted and explainable**, not reduced to raw PCR/quote folklore,
- any admission gate must point at typed requirements/policies rather than “the verifier said so,”
- weaker or missing attestation must not silently redefine stricter A/D defaults,
- and B/C must remain viable on systems or workflows where remote-attestation infrastructure is absent.

### A) `fleet_host`

Default posture: `measured-receipted-and-sensitive-gating`

- Fleet hosts treat measured platform posture as receipted evidence by default.
- Sensitive admissions such as identity issuance, secret release, rollout, or recovery may gate on that posture.
- The gate is policy-shaped and non-ambient; the operator UX is receipts/reasons, not raw TPM ritual.

### B) `workstation`

Default posture: `measured-exportable-user-visible`

- Workstations keep measured posture visible/exportable for the user, support, and verification flows.
- Default attestation gating is limited to sensitive operations rather than ordinary local use.
- A missing verifier path must not silently turn the workstation into a broken or locked-out product shape.

### C) `general_os`

Default posture: `optional-exportable-explicit-gates`

- Measured posture remains optional and exportable.
- Deployments may define explicit gates where they want them.
- General-purpose viability must not silently depend on TPM/vTPM or remote verifier infrastructure.

### D) `appliance_factory`

Default posture: `measured-retained-and-production-gating`

- Factory/regulatory shapes retain measured posture by default.
- Production enrollment, maintenance access, secret release, or equivalent sensitive admissions may depend on that posture.
- Weakening those gates is a review event, not a quiet operational shortcut.

## Consequences

- Product profiles now carry a stable `platform_provenance` default.
- `tools/check_product_profiles.py` must enforce this boundary so the archive cannot silently drift back into attestation theater, workstation breakage-by-surprise, or production evidence-without-gating.
- Risk item 52 narrows from “should we decide the default?” to implementation detail: exact sensitive-action sets, verdict vocabulary, enrollment lifecycle, reference-value variance policy, and workstation UX.

## Non-goals

- Choosing one verifier/registrar/enrollment implementation.
- Freezing one PCR/event-log variance policy for all hardware classes.
- Making TPM/vTPM remote attestation mandatory for every installation.
- Finalizing the exact degraded/waived verdict taxonomy here.
