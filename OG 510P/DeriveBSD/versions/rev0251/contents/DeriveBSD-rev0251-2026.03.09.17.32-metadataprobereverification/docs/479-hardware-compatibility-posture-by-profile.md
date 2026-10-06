# Hardware compatibility posture by profile

**Tier:** B (Base)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Registry→Diff→Gate, Plan→Apply→Receipt  

DeriveBSD already has privacy-safe hardware inventory receipts and typed compatibility reports.
What this doc decides is narrower and more important for coherence:
**when hardware preflight is blocking, when it is warning-first, and when approved hardware support becomes part of the product contract.**

This is intentionally **not** a full device-manager or driver-stack spec.
It is a product-default decision.

See also:
- ADR: `adrs/ADR-0069-hardware-compatibility-posture-by-profile.md`
- inventory lane: `docs/319-hardware-inventory-and-driver-binding-as-evidence.md`
- preflight/gate lane: `docs/320-hardware-compatibility-gates-and-safe-upgrades.md`
- update gating: `docs/112-health-gated-updates.md`
- authority budgets: `docs/298-authority-budgets-and-permission-drift-alarms.md`
- product profiles: `docs/411-product-profiles-as-compilation-target.md`

## Why this needs a hard decision

The archive already says hardware facts should be typed, privacy-safe, and usable for preflight.
Without a profile-shaped default, the same lane still drifts in practice:

- fleet operators cannot tell whether `hw.compat.report` is genuinely blocking or just a nice-to-have,
- workstation users cannot tell whether a warning means “unsafe to switch” or merely “good luck,”
- general-purpose installs cannot tell whether preflight is preferred or optional ceremony,
- and factory/regulatory deployments cannot make honest support claims about approved hardware.

Hardware compatibility posture is too close to remote bricks, supportability, and privacy to leave as implied local custom.
The archive needs a stable answer for **when inventories refresh, when findings block, and when support matrices are mandatory.**

## Scope of this knob

`hardware_compatibility` covers the default handling of:

- required refresh of `hw.inventory.receipt` before switch/install/recovery decisions that depend on hardware truth
- whether `hw.compat.report` is blocking, warning-first, or admission-shaped by default
- whether hardware-class cohorting / allowlists are part of the product contract
- whether overrides require breakglass, trusted UI, or explicit admin action

It does **not** decide every reason code, probe detail, or support-matrix schema.

## Product-shape defaults

| Profile | `hardware_compatibility` default | Practical meaning |
|---|---|---|
| A (`fleet_host`) | `preflight-blocking-cohort-aware-breakglass` | Fresh inventory + compatibility preflight is part of the normal switch path; boot-critical or remote-management-floor failures block unless explicit breakglass says otherwise, and hardware-class cohorting is part of rollout hygiene. |
| B (`workstation`) | `boot-floor-blocking-trusted-ui-consent` | Boot/display/input/storage floor failures block by default; warnings remain trusted-UI-visible and require explicit user consent plus a verified recovery path. |
| C (`general_os`) | `preflight-preferred-explicit-override` | Compatibility preflight is preferred and receipted by default, but explicit local override remains viable for labs, unusual hardware, and compatibility exploration. |
| D (`appliance_factory`) | `admission-first-allowlist-bundled` | Production support claims are admission-first and tied to approved hardware classes/support matrices; offline bundles and reset media carry the support story with them. |

These values live in `spec/examples/product.profiles.json` and are guarded by `tools/check_product_profiles.py`.

## Cross-profile invariants

Regardless of profile:

- any switch/install/recovery path that relies on hardware truth must refresh inventory first
- compatibility findings must be **receipted** and explainable
- boot-critical and authority-expanding mismatches should be reviewable as typed findings, not dmesg folklore
- support bundles should default to inventory digests / privacy-safe summaries rather than raw serial sprawl
- hardware-class cohorting or support claims must be based on stable summaries, not ad-hoc hostname spreadsheets

## What this fixes by profile

### A) Secure fleet host (`fleet_host`)

Default: `preflight-blocking-cohort-aware-breakglass`

- Fleet hosts should not switch generations blind and then hope boot assessment rescues them.
- The default is blocking preflight for storage/network/boot-critical failures, with explicit breakglass when operators knowingly accept risk.
- Hardware-class cohorting becomes part of the normal rollout story rather than a bespoke fleet side database.

### B) Secure workstation (`workstation`)

Default: `boot-floor-blocking-trusted-ui-consent`

- Users need clear trusted-UI explanations when a generation risks breaking display, input, storage, or ordinary boot.
- The safety valve is not hidden policy servers; it is visible warnings, explicit consent, and a verified local recovery path.
- This keeps workstation ergonomics real without normalizing “the laptop black-screened after reboot” as acceptable collateral damage.

### C) General-purpose OS (`general_os`)

Default: `preflight-preferred-explicit-override`

- General-purpose viability requires room for odd hardware, labs, and explicit local override.
- Preflight remains preferred because it gives users a reviewable summary of likely failures before the switch.
- Compatibility fallback stays explicit rather than silently redefining stricter A/B/D defaults.

### D) Appliance factory / regulatory (`appliance_factory`)

Default: `admission-first-allowlist-bundled`

- Production hardware support should be declared, not guessed live in the field.
- Offline bundles, recovery media, and reset workflows should carry support-matrix facts with them.
- Approved-hardware admission is a better match for regulatory/factory claims than “best effort on whatever was plugged in.”

## What this does **not** decide yet

This doc does **not** freeze:

- the exact `hw.compat.report` reason-code vocabulary
- the exact hardware-class digest or canonicalization algorithm
- the exact support-matrix / approved-hardware artifact format
- the exact policy language for “known-bad module/firmware version” findings

Those remain implementation details or future RFC/ADR material.

## Why this is worth locking now

This decision collapses a recurring ambiguity without inventing a new subsystem:

- A gets blocking preflight for remote-brick risk plus cohort-aware rollout,
- B gets trusted-UI-visible blocking/warning semantics with recovery readiness,
- C keeps preflight preferred without killing explicit local override,
- D gets honest approved-hardware support posture for production/offline bundles.

That is enough to guide future specs and coding while keeping collectors, reason codes, and support matrices replaceable.

## Design cue from current systems

A few ecosystem lessons are durable:

- FreeBSD exposes device topology and unattached-device matching through simple inspection tools, which is useful raw material but not yet a product policy
- systemd’s hardware database shows that modalias-like identifiers can be normalized into reviewable properties rather than shell folklore
- fwupd’s hardware-ID story shows that support/update targeting often needs stable hardware-class identifiers without depending on raw serials
- Fuchsia’s driver binding model is a useful reminder that match/bind decisions are explicit logic, not mystical kernel vibes

DeriveBSD should steal those lessons while keeping inventory privacy, support claims, preflight strength, and override ceremonies explicit.

Last updated: 2026-03-06r208
