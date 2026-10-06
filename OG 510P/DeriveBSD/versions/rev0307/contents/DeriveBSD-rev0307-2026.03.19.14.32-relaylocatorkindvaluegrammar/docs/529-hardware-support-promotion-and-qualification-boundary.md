# Hardware support promotion and qualification boundary

**Tier:** B (Base contract boundary)  
**Profiles:** A, B, C, D  
**Pillars:** supply-chain, operability  
**Patterns:** Registry→Diff→Gate, Plan→Apply→Receipt

`docs/528-hardware-support-matrix-and-bundled-admission-boundary.md` fixed where supported-hardware claims live.
This doc makes the next small hard decision:
**`hw.support.matrix` entries must say how far they were qualified, which target span that proof covers, and non-fully-supported entries must also publish typed `conditions[]` instead of hiding caveats in prose.**

See also:
- ADR: `adrs/ADR-0119-hardware-support-promotion-and-qualification-boundary.md`
- support-catalog boundary: `docs/528-hardware-support-matrix-and-bundled-admission-boundary.md`
- hardware compatibility posture: `docs/479-hardware-compatibility-posture-by-profile.md`
- hardware compatibility preflight: `docs/320-hardware-compatibility-gates-and-safe-upgrades.md`
- workstation trusted-UI floor: `docs/410-desktop-viability-checklist.md`
- support catalog shape: `spec/hw.support.matrix.schema.json`
- conditions / limitations boundary: `docs/534-hardware-support-conditions-and-known-limitations-boundary.md`
- qualification receipt boundary: `docs/530-hardware-support-qualification-receipt-boundary.md`
- qualification profile boundary: `docs/531-hardware-support-qualification-profile-boundary.md`
- qualification freshness boundary: `docs/532-hardware-support-qualification-freshness-boundary.md`
- qualification status boundary: `docs/533-hardware-support-qualification-status-boundary.md`

## Why this needs a hard decision

A typed support matrix is already better than spreadsheets.
But a typed catalog can still drift into theater if `supported` means whatever the last engineer hoped it meant.

That ambiguity is expensive in exactly the product shapes DeriveBSD cares about:

- **A** needs to know whether a hardware class is just in canary or genuinely promoted before using it as a rollout cohort.
- **B** needs a defensible story for trusted-display / trusted-input / boot-storage support before asking a human to accept a risky generation switch.
- **C** benefits from the extra structure but must keep broad-compatibility override lanes viable.
- **D** needs offline support/admission bundles whose claims survive audits and rebuilds.

The failure mode is not theoretical.
Real ecosystems publish support catalogs, per-release compatibility policies, and hardware gating programs because “works on my lab bench” is not enough for a durable platform story.

## Accepted boundary

Across all profiles:

- `hw.support.matrix` remains the catalog artifact for hardware support/admission claims,
- positive entries in that catalog now carry a typed `qualification` summary,
- that summary now points at `qualification.receipt_digest` rather than assuming ticket systems or lab notes carry the real proof,
- that summary now also points at `qualification.profile_digest` so the receipt is anchored to a typed qualification standard rather than a lab-specific playlist,
- and that receipt must now remain an `accepted` receipt to back a current positive support claim,
- and non-current receipt lifecycle is now explicit through `decision.status`, `status_effective_at`, `reason_code`, and `replacement_receipt_digest`.
- `hw.compat.report` still joins live inventory to the matrix for target-specific gating,
- and the qualification summary stays metadata-only rather than becoming runtime authority.

The new rule is simple:
**support promotion must be reviewable in the artifact itself.**

## Minimal v0 contract worth implementing

### Qualification stages

`hw.support.matrix.entries[].qualification.stage` now uses a small ladder:

- `lab-validated`
- `canary-observed`
- `release-qualified`
- `field-sustained`

That is enough to separate “we booted it in the lab,” “we are letting canaries touch it,” and “this is honestly part of the release support story.”

### Level → stage mapping

The support label is no longer free-floating:

- `canary-only` means `canary-observed`
- `supported` means `release-qualified` or `field-sustained`
- `conditional` means at least `lab-validated`
- `maintenance-only` means a previously qualified platform that is still supportable in a narrow lane

This is intentionally narrow.
It does not build a giant certification bureaucracy; it just prevents support labels from decoupling from evidence maturity.

Non-fully-supported publication now also needs typed `conditions[]` with stable `condition_id`, `reason_code`, and `required_posture`, so `conditional` / `canary-only` / `maintenance-only` stops meaning “see notes.” Positive support publication also needs typed `target_binding`; for workstation trusted-UI floor claims, `same-release-train-and-boot-manifest` is usually the honest answer when boot/display/input trust depends on the exact boot path. That keeps support maturity tied to a concrete `release-train` story instead of a timeless compatibility badge.

### Verified roles

`qualification.verified_roles` records which roles were actually rechecked during promotion.
That matters because “supported” is much less interesting than *supported for what?*

Examples:

- B may care about `trusted-display`, `trusted-input`, and `boot-storage`
- A may care about `primary-network` and `boot-storage`
- D may care about `boot-storage`, `primary-network`, `usb-quarantine`, and offline recovery

If those roles were not part of the qualification story, the matrix should not pretend otherwise.

### Evidence floor

`qualification.evidence_floor` is a small controlled vocabulary:

- `boot`
- `generation-switch`
- `rollback-or-recovery`
- `trusted-ui-basic`
- `network-basic`
- `device-mediation-basic`
- `suspend-resume`

This is not trying to encode whole test plans.
It only answers the high-leverage question: **what basic floor was revalidated before this entry was promoted?**

The archive now also expects that summary to be backed by `qualification.receipt_digest`, pointing at a typed `hw.support.qualification.receipt` object that can travel with support bundles and preflight explanations. The receipt is now in turn anchored by `qualification.profile_digest`, pointing at a typed `hw.support.qualification.profile` that defines the required checks. That same typed profile now also defines freshness, while the receipt carries the concrete `fresh_until` bound and `reverify_on` trigger list so `last_verified_at` does not silently stand in for a freshness policy.

## The hard decision for B and D

The archive now takes a stronger stance for trusted-UI and bundled-support claims:

- if a matrix entry claims `trusted-display` or `trusted-input`, qualification must include `trusted-ui-basic`
- if a matrix entry claims `boot-storage`, qualification must include `boot`
- if a matrix entry claims `primary-network` or `maintenance-network`, qualification must include `network-basic`
- if a B or D entry claims trusted-UI/boot floor roles, qualification must include `rollback-or-recovery`
- when `last_verified_at` ages past the typed freshness policy, `hw.compat.report` should surface `qualification-stale` rather than silently treating the promotion summary as fresh support

This is the courage cut.
It means some attractive hardware classes will stay `conditional` or `canary-only` until recovery and trusted-UI basics are really checked.
That is better than pretending a workstation or appliance is supported because the kernel happened to bind drivers.

## Product-shape fit

### A) Secure fleet host

- promoted cohorts become more honest: `canary-only` and `supported` are no longer interchangeable words
- rollout graphs and support cohorts can treat matrix entries as maturity-bearing facts rather than oral tradition
- fresh inventory still matters; the matrix does not replace live preflight
- `last_verified_at` is a summary timestamp, not the whole freshness rule; the real freshness answer now lives in the profile/receipt pair (`fresh_until`, `reverify_on`)

### B) Secure workstation

- trusted-UI support claims become defendable instead of aspirational
- humans can be shown that a risky switch is relying on a `conditional` or `canary-only` class rather than a fully release-qualified one
- recovery expectations stop being implied by tone of voice

### C) General-purpose OS

- C can still use the matrix as advisory metadata
- explicit local override stays viable
- the qualification ladder helps without forcing broad-compat users into a vendor-style certification regime

### D) Appliance factory / regulatory

- support/admission bundles can now say both *which class is allowed* and *what qualification floor backs that claim*
- offline review becomes stronger because the bundle no longer depends on ticket history to explain support maturity

## What this does **not** decide yet

This doc does **not** freeze:

- the final review UI for promotion diffs,
- the exact structure of all underlying qualification receipts,
- how every vendor or partner workflow feeds the matrix,
- or the full lifecycle/deprecation story for hardware classes that age out.

Those remain future spec or RFC work.
The important move now is smaller:
support promotion is no longer folklore.

## Why this is the right next revision

This compounds the previous matrix boundary without inventing a new subsystem.
The archive now knows:

- where support claims live,
- how they join live hardware facts,
- and what minimum maturity story must accompany a positive support label.

That is enough to keep future hardware/workstation/factory specs honest while still leaving room to learn.

Last updated: 2026-03-17r264