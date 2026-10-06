# Firmware-update posture by profile

**Tier:** B (Base)  
**Profiles:** A, B, C, D  
**Pillars:** supply-chain, operability, reproducibility  
**Patterns:** Registry→Diff→Gate, Plan→Apply→Receipt  

DeriveBSD already knows how to **plan**, **stage**, and **receipt** firmware-shaped changes.
What this doc decides is narrower and more important for coherence:
**what is the default firmware-update posture in each product shape?**

This is intentionally **not** an updater-stack doc.
It is a product-default decision.

See also:
- ADR: `adrs/ADR-0061-firmware-update-posture-by-profile.md`
- firmware lane: `docs/321-firmware-updates-and-uefi-variables-as-evidence.md`
- capsule/ESRT practice notes: `docs/336-uefi-capsules-esrt-and-fwupd-practice-notes.md`
- platform provenance + firmware lifecycle: `docs/417-platform-provenance-and-firmware-lifecycle-as-derived-ops.md`
- product profiles: `docs/411-product-profiles-as-compilation-target.md`

## Why this needs a hard decision

Systems that avoid deciding firmware posture eventually decide it through drift:

- fleet hosts acquire ambient vendor updater authority because “maintenance later” never becomes real,
- workstations surprise users with silent BIOS/dbx changes or push them to unsafe manual tooling,
- general-purpose installs gain a hidden dependency on one updater stack,
- and factory/regulatory images quietly depend on live vendor reachability despite claiming offline control.

DeriveBSD already says platform drift must be planned, receipted, and explainable.
That only becomes coherent if the archive fixes the **default authority model for firmware mutation** instead of leaving it to OEM tools, desktop helpers, and hand-waved maintenance folklore.

## Product-shape defaults

| Profile | `firmware_updates` default | Practical meaning |
|---|---|---|
| A (`fleet_host`) | `policy-gated` | Firmware changes are maintenance-shaped, policy-gated fleet operations with cohort-aware preflight and post-reboot receipts. |
| B (`workstation`) | `interactive-consent` | Firmware apply requires explicit trusted-UI consent; discovery/explanation can be backgrounded, but silent apply is not the baseline. |
| C (`general_os`) | `user-choice` | Firmware handling stays available without becoming a hidden requirement; Derive-managed or fwupd-shaped lanes are preferred, vendor tooling stays adapter-shaped. |
| D (`appliance_factory`) | `offline-staged` | Production/factory firmware flows use approved offline-staged artifacts, review-heavy maintenance windows, and retained receipts by default. |

These values live in `spec/examples/product.profiles.json` and are guarded by `tools/check_product_profiles.py`.

## Cross-profile invariants

Regardless of profile:

- firmware and UEFI mutation stay planned, receipted, and reviewable rather than ambient background privilege
- `stage` is never treated as `applied` success; post-reboot confirmation matters
- Secure Boot trust-root changes and comparable boot-trust mutations require stronger review than ordinary device firmware by default
- weaker compatibility lanes in C do not silently redefine stricter A/B/D defaults
- inventory, preflight, and failure explanations matter because firmware incidents are only tolerable when operators can answer what changed and why

## What this fixes by profile

### A) Secure fleet host (`fleet_host`)

Default: `policy-gated`

- Fleet hosts treat firmware changes as a policy and rollout problem, not a popup problem.
- Cohort-aware preflight and maintenance authority matter more than interactive consent.
- Firmware mutation should land in health/promotion gates with post-reboot evidence before a generation is considered good.

### B) Secure workstation (`workstation`)

Default: `interactive-consent`

- Workstations should explain vendor/device/risk in the trusted UI before apply.
- User presence and power-safety checks matter because the person holding the device bears the blast radius.
- Background scanning or advisories are fine; unattended apply of firmware or Secure Boot trust-root changes is not the default B story.

### C) General-purpose OS (`general_os`)

Default: `user-choice`

- Firmware management is a real lane, but not an ambient product obligation.
- Prefer Derive-managed or fwupd-shaped flows where available because they keep evidence and policy coherent.
- Compatibility fallbacks for classic vendor tools remain possible, but must be explicit adapters rather than invisible privilege.

### D) Appliance factory / regulatory (`appliance_factory`)

Default: `offline-staged`

- Factory/regulatory posture assumes approved staged artifacts, mirror kits, or other offline-controlled delivery.
- Production images should not rely on reaching vendor services at apply time.
- Trust-root, platform-firmware, and BMC-class changes belong in review-heavy maintenance workflows with retained receipts and deterministic evidence export.

## What this does *not* decide

Still open:

- exact helper stack (`fwupd`, custom workers, companion EFI app, BMC adapters, etc.)
- final approval matrices by component class (system firmware, dbx, SSD, NIC, BMC, downgrade)
- exact UI wording and repair flow on B
- the long-term bundle/mirror format for D
- the full status/failure taxonomy beyond the current plan/receipt discipline

That work stays implementation-level.
This doc only fixes the product-default boundary so the archive can keep converging without drifting.

## Design cue from current systems

A few lessons are stable:

- firmware becomes tractable when inventory, delivery, and post-reboot confirmation are distinct stages
- user-facing systems need explicit consent because “security update” does not erase the blast radius of a bad flash
- regulated/offline systems need staged artifacts and retained evidence because convenience reachability is not a compliance story
- general-purpose systems stay viable when the managed lane is preferred but adapters remain explicit and killable

DeriveBSD should steal those lessons while keeping the helper stack replaceable.

Last updated: 2026-03-06r200
