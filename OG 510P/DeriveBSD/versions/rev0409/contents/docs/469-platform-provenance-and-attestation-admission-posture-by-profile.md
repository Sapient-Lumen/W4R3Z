# Platform provenance and attestation-admission posture by profile

**Tier:** B (Base)  
**Profiles:** A, B, C, D  
**Pillars:** supply-chain, isolation, operability  
**Patterns:** Registry→Diff→Gate, Plan→Apply→Receipt  

DeriveBSD already knows how to **measure** and how to **receipt** platform posture.
What this doc decides is narrower and more important for coherence:
**what is the default platform-provenance / attestation-admission posture in each product shape?**

This is intentionally **not** a verifier-stack doc.
It is a product-default decision.

See also:
- ADR: `adrs/ADR-0059-platform-provenance-and-attestation-admission-posture-by-profile.md`
- platform posture as evidence: `docs/226-platform-posture-and-attestation-results-as-evidence.md`
- remote attestation admission lane: `docs/388-remote-attestation-admission-and-enrollment.md`
- admission drift review surface: `docs/440-attestation-admission-policy-diff-as-review-surface.md`
- product profiles: `docs/411-product-profiles-as-compilation-target.md`

## Why this needs a hard decision

Every system that avoids deciding its attestation posture eventually decides it through drift:

- measurements are collected but nothing depends on them,
- workstations unexpectedly depend on remote verifier reachability,
- general-purpose installs acquire an implicit TPM/vTPM requirement nobody meant to impose,
- and factory/regulated deployments retain evidence without saying which admissions are actually blocked when posture is weak.

DeriveBSD already says evidence, admission, secrets, and identity matter.
That only means anything if the archive fixes the **default authority model for measured posture** instead of leaving it to vendor dashboards and local folklore.

## Product-shape defaults

| Profile | `platform_provenance` default | Practical meaning |
|---|---|---|
| A (`fleet_host`) | `measured-receipted-and-sensitive-gating` | Measured posture is receipted and can gate sensitive admissions such as identity issuance, secret release, rollout, or recovery. |
| B (`workstation`) | `measured-exportable-user-visible` | Measured posture is visible/exportable and can inform sensitive-operation gates, but ordinary local use does not silently depend on remote verifier infrastructure. |
| C (`general_os`) | `optional-exportable-explicit-gates` | Measured posture remains optional/exportable; deployments may add explicit gates where they want them. |
| D (`appliance_factory`) | `measured-retained-and-production-gating` | Measured posture is retained and can gate production enrollment, maintenance access, or sensitive release by default. |

These values live in `spec/examples/product.profiles.json` and are guarded by `tools/check_product_profiles.py`.

## Cross-profile invariants

Regardless of profile:

A cohort-scoped reference authoring baseline now applies across profiles: routine `attestation.reference` objects start at `scope.kind = cohort` and `boot.variance.mode = manifest-replay-first`, while deployment- or host-shaped references stay explicit exceptions.
`attestation.reference.exception` now keeps those exceptions timeboxed and approval-shaped, so rollout windows and host containment remain reviewable artifacts instead of verifier-side folklore. Renewals now form a digest-linked renewal trail too: each successor artifact mints a new digest and explicitly supersedes the prior exception digest instead of depending on backend row ordering. Selection stays exact-digest-pinned as well: selector overlap or a latest matching row must not quietly decide which reference admission actually used.
Attester identity provenance is explicit too: when a receipt names an AK handle, it should also carry the exact attester-provision receipt digest, so A/B/C/D do not need registrar archaeology to explain why that attester identity was trusted. Authoritative action receipts now pin the exact decision tuple **and** `attestation_receipt_verdict`, so fleets/workstations/general OS/factory flows can prove the exact pinned verifier outcome instead of recovering it through backend archaeology or hidden policy-service state. Degraded admission stays requirement-shaped too: `attestation.requirement.min_verdict = degraded` is the sole portable way to allow degraded posture in v0, and there is no hidden degraded-waiver lane. Ordinary authority also stays fail-closed on rejected posture: successful secret delivery or workload identity issuance cannot quietly carry `rejected`, and breakglass remains the explicit emergency lane for reviewed rejected-posture recovery. Breakglass remains explicit rather than sticky ordinary authority: after a breakglass session, later ordinary secret/identity lanes require a fresh `attestation.receipt` issued after the relevant breakglass receipt `created_at`. That post-breakglass ordinary story is time-ordered too: the pinned `attestation.receipt.created_at` must be strictly later than the relevant breakglass receipt `created_at`, and the later ordinary receipt must not predate the pinned `attestation.receipt.created_at`.
A strict-PCR exception posture remains available for tightly controlled platforms, but it must stay visibly exceptional rather than becoming the quiet default.

- measured posture must be receipted and explainable rather than reduced to raw PCR folklore
- admission rules must point at typed requirement/policy artifacts
- weakening attestation gates must be reviewable through diff surfaces
- stricter profiles are not silently weakened by looser compatibility defaults elsewhere
- local/product usability and admission strictness are separate decisions, not accidental side effects

## What this fixes by profile

### A) Secure fleet host (`fleet_host`)

Default: `measured-receipted-and-sensitive-gating`

- Fleet hosts treat platform provenance as an operational gate, not a compliance checkbox.
- Identity issuance, secret release, rollout, or recovery can require fresh measured posture by default.
- Operators should see verifier receipts/reasons, not be expected to manually interpret raw quotes or PCR tables.

### B) Secure workstation (`workstation`)

Default: `measured-exportable-user-visible`

- Workstations should make measured posture visible/exportable in the trusted UI and support flows.
- Attestation can gate sensitive operations, but it should not become an ambient dependency for ordinary local use.
- This keeps “platform posture matters” compatible with real workstation viability.

### C) General-purpose OS (`general_os`)

Default: `optional-exportable-explicit-gates`

- Measured posture is a real lane, but not a hidden requirement.
- Explicit deployment-specific gates are fine; implicit baseline dependence is not.
- This keeps DeriveBSD viable on broader hardware and operator habits without silently weakening stricter A/B/D defaults.

### D) Appliance factory / regulatory (`appliance_factory`)

Default: `measured-retained-and-production-gating`

- Production and factory workflows retain measured posture by default.
- Sensitive admissions like enrollment, maintenance access, or secret release can depend on that posture.
- Operational waivers belong in reviewable policy and evidence, not in undocumented exception handling.

## What this does *not* decide

Still open:

- which actions are in the default “sensitive admission” set for each profile
- the final degraded/waived verdict vocabulary
- exact verifier/registrar/enrollment topology
- exact reviewer/quorum topology and renewal UX for timeboxed attestation exceptions
- workstation UI wording and escalation behavior when posture is missing or stale

That work stays implementation-level.
This doc only fixes the product-default boundary so the archive can keep converging without drifting.

## Design cue from current systems

A few lessons are stable:

- measured boot becomes operationally meaningful when it feeds a receipt and an admission policy
- retained event logs and reference values matter because operators need explanations, not just binary pass/fail
- human-facing systems need visibility/exportability without turning remote attestation into a surprise boot-time or login-time dependency
- production/factory systems benefit from stronger gating defaults because their whole value proposition is controlled admission and durable evidence

DeriveBSD should steal those lessons while keeping the verifier stack replaceable.

The post-breakglass join is exact and same-host bound too: when breakglass materially shaped later ordinary authority, `relevant_breakglass_receipt_digest` keeps A/B/C/D from having to guess which breakglass session mattered, from normalizing “latest breakglass” folklore, or from permitting cross-host join folklore. The joined breakglass receipt must name the same host as the pinned attestation receipt, and the time-ordered post-breakglass chain keeps freshness portable instead of backend-reconstructed.
Last updated: 2026-03-21r382
