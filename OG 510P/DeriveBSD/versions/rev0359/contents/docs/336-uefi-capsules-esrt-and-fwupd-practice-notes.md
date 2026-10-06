# UEFI capsules + ESRT in practice (fwupd-shaped constraints)

DeriveBSD already treats firmware updates as planned, receipted operations (`fw.update.plan` → `fw.update.receipt`).
This note captures the *boring-but-critical* real-world details for **UEFI capsule updates** so we don't design ourselves into “it staged, so it must be fine” folklore.

Product-shape default now lives in `docs/471-firmware-update-posture-by-profile.md`: this note is substrate and execution detail, not the A/B/C/D policy boundary.

Primary sources worth keeping close:

- UEFI spec: **Firmware Update and Reporting** (ESRT + capsule update status) https://uefi.org/specs/UEFI/2.11/23_Firmware_Update_and_Reporting.html
- fwupd capsule plugin notes (real device quirks, ESRT interactions) https://fwupd.github.io/libfwupdplugin/uefi-capsule-README.html
- Windows guidance (OS-initiated firmware update platform) https://learn.microsoft.com/en-us/windows-hardware/drivers/bringup/windows-uefi-firmware-update-platform

---

## Two core concepts to model explicitly

### 1) `UpdateCapsule` is *not* “update succeeded”

Many platforms implement firmware updates as:

1) OS passes a capsule blob to firmware (`UpdateCapsule` runtime service)
2) firmware persists the intent and/or capsule to non-volatile storage
3) firmware applies the update at early boot
4) firmware reports the outcome later

The OS can only confidently claim **“staged”** until it has rebooted and collected post-state.

DeriveBSD rule:

- **stage != apply**
- `fw.update.receipt` must encode this (e.g. per-target status `staged` vs `applied` vs `postcheck-failed`).

### 2) ESRT is the “contract surface” for capsule-targetable resources

The **EFI System Resource Table (ESRT)** is how firmware exposes which resources are capsule-updatable and how the last attempt went.
The ESRT entry exists for each targetable firmware resource and includes “last attempt” status fields.

DeriveBSD should treat ESRT as:

- the authoritative *inventory id* for capsule targets (class GUID / component id)
- the authoritative *status channel* after reboot

Implication: `fw.device.inventory` components of class `uefi.esrt` should optionally include ESRT-derived fields (last attempt status/version) in a privacy-safe way.

---

## DeriveBSD implementation guidance (day‑0 viable)

### Inventory capture

- Prefer deriving `fw.device.inventory.components[].component_id` from:
  - ESRT firmware class GUID when available
  - otherwise a derived, privacy-safe id (hash of bus path + vendor + model)
- For ESRT components, optionally include:
  - last attempt status code (coarse)
  - last attempt version string
  - last attempt error string if firmware provides one

These fields are both:

- operationally important (“why did it fail?”)
- safe to disclose compared to raw firmware blobs

### Planning constraints (avoid platform-specific brickery)

Real platforms sometimes only support **one staged capsule per boot**.
fwupd’s UEFI capsule plugin documents hardware where scheduling one update hides other ESRT targets until reboot.

DeriveBSD day‑0 default policy should therefore be conservative:

- for `uefi-capsule` targets, default to **one target per plan per reboot**
- require explicit policy override to stage multiple capsule targets in the same window

This can be represented either:

- as a policy rule (“max capsule targets per maintenance window”), or
- as an applier constraint (“split plans by target class”).

### Staging model

For capsule updates that require a reboot, model the operation as a small state machine:

1) **precheck**: collect `fw.inventory.receipt` (digest-first posture snapshot)
2) **stage**: place capsule where firmware expects it (ESP or firmware-defined path)
3) **arm**: set relevant UEFI variables (receipted as `uefi.var.set.receipt`)
4) **reboot**: reboot into firmware update path
5) **postcheck**:
   - read ESRT last attempt status
   - collect fresh `fw.inventory.receipt`
   - emit `fw.update.receipt`

### Receipt discipline (what to include)

A useful `fw.update.receipt` should be able to answer, later:

- *which plan digest did we execute?*
- *which targets were staged vs applied?*
- *what did ESRT report after reboot?*
- *what did the firmware inventory change to?*

Minimum:

- `pre_fw_inventory_digest` and `post_fw_inventory_digest`
- per-target status `staged`/`applied`/`postcheck-failed`
- an evidence pointer with an ESRT summary (coarse) if present

---

## Interaction with health-gated rollback

Firmware rollback is often unavailable or risky.
That means the health gate must treat firmware changes with “do no harm” conservatism:

- firmware updates should run only under a maintenance lease
- staged updates must not be declared “success” until postcheck
- failures should halt promotion of the generation regardless of OS health

See:

- `docs/335-boot-assessment-greenboot-and-health-gated-rollback.md`
- `docs/321-firmware-updates-and-uefi-variables-as-evidence.md`

Last updated: 2026-03-06r200
