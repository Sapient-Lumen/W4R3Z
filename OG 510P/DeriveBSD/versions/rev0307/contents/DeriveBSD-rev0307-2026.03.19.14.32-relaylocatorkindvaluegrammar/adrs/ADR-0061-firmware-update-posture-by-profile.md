# ADR-0061: Firmware-update posture by profile

- **Status:** Accepted
- **Date:** 2026-03-06

## Context

DeriveBSD already has a serious firmware lane on paper:
`docs/221-firmware-updates-as-artifacts.md` treats firmware as change material,
`docs/321-firmware-updates-and-uefi-variables-as-evidence.md` makes firmware and UEFI mutation receipted,
`docs/336-uefi-capsules-esrt-and-fwupd-practice-notes.md` captures the capsule/ESRT substrate,
and `docs/417-platform-provenance-and-firmware-lifecycle-as-derived-ops.md` threads firmware into the broader platform-provenance workflow.

What the archive still lacked was the **product-shape default** for firmware updates.
Without that, incompatible stories quietly coexist:

- **A** may want fleet-safe staged updates, but still drift toward ambient vendor updater authority.
- **B** may either spring silent BIOS/dbx changes on users or make workstation-safe firmware hygiene so annoying that nobody uses it.
- **C** cannot tell whether firmware management is a real lane or a hidden requirement.
- **D** may claim regulated/offline posture while still depending on live vendor reachability or convenience flashing in production.

We do **not** need to choose one updater stack, one capsule helper, or one OEM workflow here.
We do need a stable, checkable answer to:

- when firmware updates are policy-gated fleet operations vs user-mediated workstation actions,
- where interactive consent is required instead of silent apply,
- how general-purpose installations keep broad compatibility without silently weakening stricter defaults,
- and where offline-staged firmware becomes part of the default factory/regulatory posture.

## Decision

We define firmware updates as a **profile-shaped default** and thread them into `spec/examples/product.profiles.json` under the stable `firmware_updates` knob.

Cross-profile guardrail:
- firmware and UEFI mutation stay **planned, receipted, and reviewable**,
- `stage` is never treated as `applied` success,
- Secure Boot trust-root changes (`PK/KEK/db/dbx`) and comparable boot-trust mutations require stronger review than ordinary device firmware by default,
- and update tooling remains a bounded authority lane rather than an ambient always-privileged background service.

### A) `fleet_host`

Default posture: `policy-gated`

- Fleet firmware updates are policy-gated maintenance operations.
- Cohort-aware preflight, staged rollout, and post-reboot receipts matter more than interactive prompts.
- Ambient vendor updater behavior is out of bounds as the default fleet story.

### B) `workstation`

Default posture: `interactive-consent`

- Workstations should surface firmware/device/trust-root changes in the trusted UI.
- Applying firmware requires explicit user-mediated consent by default.
- Background discovery is fine; silent unattended firmware apply is not the workstation baseline.

### C) `general_os`

Default posture: `user-choice`

- Firmware handling remains available, but it is not a hidden product requirement.
- Derive-managed or fwupd-shaped lanes are preferred where present.
- Classic vendor tooling may exist, but only as explicit adapters rather than silent ambient mutation.

### D) `appliance_factory`

Default posture: `offline-staged`

- Factory/regulatory shapes use approved offline-staged firmware artifacts by default.
- Production workflows should not depend on live vendor reachability.
- Trust-root and platform-firmware changes belong in review-heavy maintenance windows with retained receipts.

## Consequences

- Product profiles now treat `firmware_updates` as a stable compilation-target surface, not an incidental convenience knob.
- `tools/check_product_profiles.py` must enforce this boundary so the archive cannot silently drift back toward silent workstation firmware changes, fleet updater folklore, or online-only factory firmware workflows.
- Risk item 44 narrows from “what is the default?” to implementation detail: exact helper stack, class-specific approval policy, bundle formats, downgrade policy, and failure taxonomy.

## Non-goals

- Choosing one firmware transport stack or one companion EFI helper.
- Freezing the final approval matrix for every firmware/device class.
- Defining the full failure/status vocabulary beyond the existing plan/receipt discipline.
- Eliminating explicit compatibility adapters for vendor tooling on day 0.
