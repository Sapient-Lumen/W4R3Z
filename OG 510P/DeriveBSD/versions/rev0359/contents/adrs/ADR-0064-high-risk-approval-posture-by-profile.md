# ADR-0064: High-risk approval posture by profile

Date: 2026-03-06
Status: Accepted

## Context

DeriveBSD already has the pieces for strong approvals:
`docs/107-two-person-integrity.md`, `docs/256-consent-ux-contract.md`,
`docs/260-release-authority-policy-and-key-management.md`, and
`docs/288-multiparty-approvals-and-separation-of-duties.md` all describe
thresholds, digest binding, and separation of duties.

What the archive still lacked was a **product-default boundary**.
Without that boundary, “quorum” drifts into one of two failure modes:

- **too weak** for fleet/factory shared-trust mutations because approvals remain a social process,
- **too strong** for workstation/general-purpose use because personal-risk actions inherit enterprise ceremony and become bypass bait.

That ambiguity is expensive because it leaks into release authority, breakglass,
network exposure changes, evidence export exceptions, and trust-root/key-rotation work.

## Decision

DeriveBSD will treat **high-risk approval posture** as a first-class,
profile-shaped default captured in `spec/examples/product.profiles.json`
under `high_risk_approvals` and guarded by `tools/check_product_profiles.py`.

This posture applies to **shared-trust or boundary-expanding mutations**, such as:

- release publish / halt / resume authority,
- trust-root and key-rotation ceremonies,
- destructive breakglass or reset authority,
- exposure or export policy expansions that widen blast radius,
- other plan/policy/artifact changes where requester-self-approval would be unsafe.

The default values are:

- **A / `fleet_host`**: `digest-bound-role-separated-quorum`
- **B / `workstation`**: `trusted-ui-user-consent-first`
- **C / `general_os`**: `single-principal-default-explicit-quorum-lane`
- **D / `appliance_factory`**: `offline-oob-role-separated-quorum`

## Meaning by profile

### A) Secure fleet host (`fleet_host`)

- High-risk shared-trust mutations require digest-bound approvals from **distinct principals** by default.
- “Approve the plan/policy/artifact digest, not the idea” is baseline behavior.
- Requester self-approval for publish, trust-root mutation, or destructive breakglass is out of bounds by default.

### B) Secure workstation (`workstation`)

- The ordinary authority model is **trusted-UI user consent** for personal-risk actions.
- Workstation UX must not force enterprise-style quorum friction onto local install, update, export, or firmware actions that primarily affect the human holding the device.
- Shared-trust / organization-wide mutations, if enabled, live in an explicit admin lane rather than piggybacking on ordinary app/user prompts.

### C) General-purpose OS (`general_os`)

- Classic single-principal local admin remains viable by default.
- Quorum / separation-of-duties workflows remain available, but only as explicit policy or adapter lanes.
- Ordinary local install/update/admin paths must not acquire a hidden dependency on a central approver service.

### D) Appliance factory / regulatory (`appliance_factory`)

- Production/manufacturing shared-trust mutations are digest-bound, role-separated, and quorum-shaped by default.
- Offline or out-of-band approval paths must remain workable because regulated/air-gapped environments cannot depend on live SaaS reviewers.
- Self-approval or same-principal decide+ship for production-mutating operations is out of bounds.

## Consequences

### Positive

- The archive can now distinguish **user consent** from **organizational quorum** without collapsing them into one fuzzy prompt surface.
- Fleet/factory release, trust-root, and breakglass lanes now have a stable default authority model.
- Workstation/general-purpose viability stays intact because high-risk approval posture does not silently impose enterprise ceremonies everywhere.

### Negative / trade-offs

- This introduces one more stable product-profile knob, so the archive must keep it small and guardrailed.
- Some docs that previously said “approval” generically now need to be read through this profile default.
- Exact threshold counts, approver groups, and envelope formats remain open implementation work.

## Non-goals

This ADR does **not** decide:

- exact threshold numbers or role names,
- exact offline approval transport or hardware token workflow,
- exact GUI/TUI wording,
- or a full workflow engine.

Those remain implementation-level or future RFC/ADR material.

## Why this shape

The coherence win is **not** “quorum everywhere.”
It is making the hard product decision that:

- A/D default to digest-bound, distinct-principal approvals for shared-trust mutations,
- B defaults to trusted-UI user consent for personal-risk actions,
- C keeps single-principal viability unless stronger workflows are explicitly chosen.

That collapses a real ambiguity without inventing a new subsystem.
