# Update-delivery and release posture by profile

**Tier:** B (Base)  
**Profiles:** A, B, C, D  
**Pillars:** supply-chain, operability, reproducibility  
**Patterns:** Registry→Diff→Gate, Plan→Apply→Receipt  

DeriveBSD already has serious update primitives.
What this doc decides is narrower and more important for coherence:
**what is the default update-delivery and release-finalization posture in each product shape?**

This is intentionally **not** an updater-daemon or GUI doc.
It is a product-default decision.

See also:
- ADR: `adrs/ADR-0062-update-delivery-and-release-posture-by-profile.md`
- channel metadata: `docs/61-channel-metadata-tuf-inspired.md`
- health-gated updates: `docs/112-health-gated-updates.md`
- staged rollouts: `docs/177-fleet-coordinated-rollouts.md`, `docs/258-staged-rollouts-and-cohorts.md`
- offline bundles and mirror kits: `docs/138-offline-signed-update-bundles.md`, `docs/273-airgap-mirror-kits-and-sneakernet-updates.md`
- product profiles: `docs/411-product-profiles-as-compilation-target.md`

## Why this needs a hard decision

Systems that avoid deciding update posture eventually decide it through drift:

- fleets accumulate opaque always-on host updater authority because rollout policy never becomes a first-class artifact,
- workstations discover updates safely but still surprise the human with background apply/reboot behavior,
- general-purpose installs quietly inherit dependencies on health-gate controllers or rollout services they never asked for,
- and factory/regulatory images claim air-gap discipline while production success still depends on live channels instead of approved offline carriers.

DeriveBSD already says updates must be signed, planned, receipted, and explainable.
That only becomes coherent if the archive fixes the **default authority model for delivery + finalization** instead of leaving it to whichever agent, GUI, or mirror workflow shows up first.

## Product-shape defaults

| Profile | `updates` default | Practical meaning |
|---|---|---|
| A (`fleet_host`) | `health-gated` | Fleet updates are rollout-shaped operations: signed channels remain byte authority, while cohorts/assignments/windows/finalization stay policy-derived and receipted. |
| B (`workstation`) | `health-gated` | Update discovery may background safely, but apply/finalization stays trusted-UI-visible, deferrable, and health/rollback-aware rather than silently reboot-driven. |
| C (`general_os`) | `transactional` | Atomic apply/rollback remains the baseline; stronger rollout, health-gate, or offline-delivery lanes stay available without becoming hidden requirements. |
| D (`appliance_factory`) | `offline-bundles` | Approved offline bundles or mirror kits with quarantine→promote import are the default production delivery path, with retained receipts and controlled windows. |

These values already live in `spec/examples/product.profiles.json` and are now guarded by `tools/check_product_profiles.py`.

## Cross-profile invariants

Regardless of profile:

- signed channel metadata and anti-rollback/freshness rules stay authoritative for byte authenticity
- offer/assignment/finalization decisions remain separately explainable and receipted rather than fused into one opaque updater
- `staged` or `applied` is never treated as `healthy` success without the profile-appropriate commit signal
- when health-gated finalization materially shapes a support case, official support handoff carries `boot_bless_receipt_digests` as the typed health-gated finalization proof instead of loader counters or status text
- offline carriers are only carriers; local verification and quarantine→promote remain the trust boundary
- weaker compatibility lanes in C do not silently redefine stricter A/B/D defaults

## What this fixes by profile

### A) Secure fleet host (`fleet_host`)

Default: `health-gated`

- Fleet hosts treat updates as staged rollout operations, not local convenience clicks.
- Cohorts, maintenance windows, reboot coordination, and post-boot health gates are normal rather than optional extras.
- Director-like explicit assignment may exist, but it narrows *offer* authority; it does not replace signed channel metadata as byte authority.

### B) Secure workstation (`workstation`)

Default: `health-gated`

- Workstations can background discovery or non-disruptive staging, but apply and reboot finalization must stay visible in the trusted UI.
- Rollback/health consequences should be understandable to a non-expert user.
- Silent unattended host-generation apply or reboot is out of bounds as the workstation baseline.

### C) General-purpose OS (`general_os`)

Default: `transactional`

- General-purpose installs keep atomic switch/rollback as the baseline update story.
- Health gates, rollout graphs, assignment services, and offline bundle lanes remain optional Derive features rather than hidden prerequisites for viability.
- Central coordinators and compatibility update tools stay adapter-shaped or explicitly chosen.

### D) Appliance/factory/regulatory (`appliance_factory`)

Default: `offline-bundles`

- Factory/regulatory posture assumes approved offline bundles or mirror kits with quarantine→promote import.
- Production success should not depend on live upstream channel reachability.
- Controlled windows, retained receipts, and local approval policy are the expected update path, with online channels serving staging and preparation rather than production trust.

## What this does **not** decide yet

This doc does **not** freeze:

- the exact update agent or UX surface,
- the final mirror-kit/bundle envelope,
- the full key-rotation ceremony,
- or the exact source-retention/archive budget for every deployment.

Those remain implementation details or future RFC/ADR material.

## Why this is worth locking now

This decision keeps all four product shapes viable **without forks** while collapsing a recurring ambiguity:

- A gets rollout-safe automation without trusting one opaque updater,
- B gets humane visibility and consent around disruptive finalization,
- C keeps broad viability without coordinator theater,
- D gets a real offline happy path instead of “we’ll script it later.”

That is enough of a boundary to guide specs and future coding without prematurely freezing the agent stack.

Last updated: 2026-03-21r363
