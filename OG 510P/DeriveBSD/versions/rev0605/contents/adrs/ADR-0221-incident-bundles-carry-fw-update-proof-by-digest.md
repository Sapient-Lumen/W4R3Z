# ADR-0221: Incident bundles carry firmware-update proof by digest

- Status: Accepted
- Date: 2026-03-21

## Context

`docs/321-firmware-updates-and-uefi-variables-as-evidence.md`, `docs/417-platform-provenance-and-firmware-lifecycle-as-derived-ops.md`, and `docs/621-firmware-inventory-and-mutation-evidence-detail-and-export-posture-by-profile.md` already fixed the core firmware lane:

- `fw.inventory.receipt` and `fw.inventory.diff` are the routine inventory/review surfaces,
- `fw.update.receipt` is authoritative for staged/applied firmware-update outcomes,
- and `uefi.var.set.receipt` remains the separate authoritative lane for BootOrder, Secure Boot, db/dbx, and capsule-intent mutation.

The official incident/support-bundle contract still lagged behind that decision in practice.
The schema already had `firmware_update_receipts` plus `fw_update_receipt_digests`, but the archive still had not treated them as a real typed support-handoff boundary:

- the canonical bundle examples did not bind the real `fw.update.receipt` digest,
- `bundle.plan` did not exercise the selector on the shared include surface,
- and the surrounding docs did not teach when support handoff should carry the exact bounded firmware-update proof.

That omission is expensive because it quietly re-opens the exact folklore boundary the archive already paid to close:

- support handoff can say that a firmware update mattered without naming the exact bounded `fw.update.receipt`,
- responders fall back to updater dashboards, helper stdout, vendor job pages, or ticket notes,
- staged-versus-applied firmware outcomes drift back into implementation-private tooling,
- and the support/export contract stops matching the archive's digest-first mutation model.

We do **not** need a new firmware subsystem or a generic “platform mutation” catch-all.
We need the existing incident-bundle selector and metadata surfaces to become the real typed join for exact `fw.update.receipt` participation.

## Decision

**Incident/support bundles may carry firmware-update proof by typed digest joins.**

Specifically:

1. Keep the canonical bundle selector real.
   - `spec/incident.bundle.schema.json#/$defs/include_knobs` already carries `firmware_update_receipts`.
   - `bundle.plan.selection.include` must exercise that shared selector when staged/applied firmware-update outcomes materially participated in the incident/support story.

2. Keep the canonical bundle metadata surface real.
   - `incident.bundle.includes` already carries `fw_update_receipt_digests`.
   - These digests point at `fw.update.receipt` objects, not updater dashboards, helper stdout, raw capsule bytes, or ticket prose.

3. Keep firmware-update proof distinct from UEFI-variable proof.
   - `fw_update_receipt_digests` remain the typed join for firmware-update stage/apply outcomes.
   - `uefi_var_set_receipt_digests` remain the typed join for BootOrder, Secure Boot, db/dbx, and capsule-intent mutation.
   - This avoids a generic firmware-mutation field that would blur update outcomes, trust-root changes, and boot-variable drift back together.

4. Keep the rule conditional and narrow.
   - Incident bundles should include `fw_update_receipt_digests` when a staged or applied firmware update materially participated in the incident/support story.
   - This does not mean every bundle must always include every historical firmware update receipt.

5. Keep stronger raw platform material separate.
   - This ADR does not promote raw capsule payloads, helper-private logs, updater dashboards, or vendor-private traces into the official bundle truth model.
   - Those remain explicit stronger side evidence under separate policy/approval/export rules.

## Consequences

- Support bundles can now answer **whether a firmware update participated** and **which exact `fw.update.receipt` bounded it**.
- Staged-versus-applied firmware outcomes stay explainable in the same digest-first evidence graph as the rest of the system.
- The official support handoff now stays aligned with the already-decided firmware evidence posture instead of partially undoing it.
- `bundle.plan` / `incident.bundle` remain the one official bundle-selection and metadata contract for this firmware-update lane too.

## What this does not decide

This ADR does **not** decide:

- the final UI for previewing firmware-update participation before export,
- whether every bundle template enables the selector by default,
- richer export paths for raw capsule bytes or raw updater logs,
- or the final helper stack for staging/applying firmware.

It only makes the already-existing typed join between `fw.update.receipt` and the incident/support bundle contract real and enforced.
