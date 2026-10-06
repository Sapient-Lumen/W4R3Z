# ADR-0069: Hardware compatibility posture by profile

Date: 2026-03-06
Status: Accepted

## Context

DeriveBSD already has the raw ingredients for a coherent hardware-safety lane:
`docs/319-hardware-inventory-and-driver-binding-as-evidence.md` and
`docs/320-hardware-compatibility-gates-and-safe-upgrades.md` define privacy-safe inventory receipts,
compatibility reports, and the idea that upgrades should not switch generations blind.

What the archive still lacked was a **product-default boundary** for how strong those checks are by default.
Without that boundary, the same inventory and preflight vocabulary drifts into contradictory expectations:

- fleet hosts either block remote-brick risk or quietly treat `hw.compat.report` as advisory theater,
- workstations either become too rigid for real hardware diversity or too casual about display/input/storage regressions,
- general-purpose installs cannot tell whether preflight is preferred or merely aspirational,
- and factory/regulatory images claim supported-hardware posture while still relying on best-effort live discovery.

## Decision

DeriveBSD will treat **hardware compatibility posture** as a first-class, profile-shaped default captured in
`spec/examples/product.profiles.json` under `hardware_compatibility` and guarded by `tools/check_product_profiles.py`.

This posture covers the default handling of:

- when `hw.inventory.receipt` must be refreshed before switch/install/recovery decisions,
- whether `hw.compat.report` findings are blocking, warning-first, or admission-shaped,
- whether hardware-class cohorting / allowlists are part of the default product contract,
- and whether overrides require breakglass, trusted UI, or explicit admin action.

The default values are:

- **A / `fleet_host`**: `preflight-blocking-cohort-aware-breakglass`
- **B / `workstation`**: `boot-floor-blocking-trusted-ui-consent`
- **C / `general_os`**: `preflight-preferred-explicit-override`
- **D / `appliance_factory`**: `admission-first-allowlist-bundled`

## Meaning by profile

### A) Secure fleet host (`fleet_host`)

- A fresh hardware inventory + compatibility preflight is part of the normal switch path.
- Boot-critical and remote-management-floor failures block the switch unless breakglass says otherwise.
- Cohorting by stable hardware-class summaries is part of the default rollout story.

### B) Secure workstation (`workstation`)

- Boot/display/input/storage floor regressions block by default.
- Warnings remain trusted-UI-visible and require explicit user consent plus a verified recovery path.
- The workstation should not silently cross a compatibility warning boundary that strands the user locally.

### C) General-purpose OS (`general_os`)

- Compatibility preflight is preferred and should stay explainable/receipted by default.
- Explicit local override remains viable for labs, older hardware, and compatibility exploration.
- C keeps broad viability without silently redefining stricter fleet/workstation/factory posture.

### D) Appliance factory / regulatory (`appliance_factory`)

- Production support claims are admission-first and tied to approved hardware classes / support matrices.
- Offline bundles and reset media must carry the hardware-support story with them.
- “Best effort, maybe this controller works” is not the production default.

## Consequences

### Positive

- The archive now has a stable answer to “is hardware preflight advisory or blocking?” across A–D.
- Fleet rollouts can treat hardware class as a first-class cohorting axis instead of relying on folklore.
- Factory/regulatory support claims now match the archive’s offline-bundle / approved-hardware posture.

### Negative / trade-offs

- This adds one more stable profile knob that must remain small and guardrailed.
- Exact reason-code vocabulary, support-matrix format, and probe cadence remain implementation work.
- Workstation/general-OS users will still need humane explanations when compatibility gates say no.

## Non-goals

This ADR does **not** decide:

- the exact `hw.compat.report` reason-code taxonomy,
- the exact hardware-class canonicalization algorithm,
- the exact support-matrix artifact format for vendor or factory programs,
- or the exact split between kernel/firmware driver checks and higher-level support policy.

Those remain implementation work or future RFC/ADR material.

## Why this shape

The coherence win is not “block everything everywhere” and it is not “warn and pray.”
It is deciding that:

- A defaults to blocking preflight for boot-critical + remote-management-floor failures with cohort-aware rollout and explicit breakglass,
- B defaults to blocking local-brick failures and showing warnings in trusted UI with consent + recovery readiness,
- C defaults to explainable preferred preflight while preserving explicit override,
- D defaults to approved-hardware admission and bundle-carried support claims.

That is enough to guide future specs and coding without prematurely freezing the inventory collector,
compatibility reason-code set, or support-matrix representation.
