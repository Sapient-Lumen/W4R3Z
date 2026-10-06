# ADR-0220: Incident bundles carry UEFI-var-set proof by digest

- Status: Accepted
- Date: 2026-03-21

## Context

`docs/321-firmware-updates-and-uefi-variables-as-evidence.md` and `docs/621-firmware-inventory-and-mutation-evidence-detail-and-export-posture-by-profile.md` already made the firmware lane explicit:

- `fw.inventory.receipt` and `fw.inventory.diff` are the routine inventory/review surfaces,
- `fw.update.receipt` is authoritative for firmware-update mutation,
- and `uefi.var.set.receipt` is authoritative for BootOrder, Secure Boot, db/dbx, and capsule-intent variable mutation.

The official incident/support-bundle contract still lagged behind that decision.
`incident.bundle` could already carry `fw_update_receipt_digests`, but it still had no typed place for the exact `uefi.var.set.receipt` digest itself.

That omission is expensive because it quietly re-opens the exact folklore boundary the archive already paid to close:

- support handoff can say that firmware or trust-root mutation mattered without naming the exact bounded `uefi.var.set.receipt`,
- responders fall back to raw efivar dumps, helper stdout, screenshots, or ticket notes,
- Secure Boot/db/dbx and BootOrder mutation get flattened into a generic “firmware changed” story,
- and the support/export contract drifts away from the archive’s digest-first mutation model.

We do **not** need a new firmware subsystem.
We need the official incident-bundle selector and metadata surfaces to carry the typed `uefi.var.set.receipt` join by digest.

## Decision

**Incident/support bundles may carry UEFI-variable mutation proof by typed digest joins.**

Specifically:

1. Extend the canonical bundle include-knob surface.
   - `spec/incident.bundle.schema.json#/$defs/include_knobs` must carry `uefi_var_set_receipts`.
   - Because `bundle.plan.selection.include` reuses that shape, official bundle planning inherits the same selector automatically.

2. Extend the canonical bundle metadata surface.
   - `incident.bundle.includes` must carry `uefi_var_set_receipt_digests`.
   - These digests point at `uefi.var.set.receipt` objects, not raw efivar blobs, helper stdout, or ticket prose.

3. Keep UEFI-variable mutation proof distinct from firmware-update proof.
   - `fw_update_receipt_digests` remain the typed join for firmware-update apply/stage outcomes.
   - `uefi_var_set_receipt_digests` identify the exact bounded `uefi.var.set.receipt` object(s) that belong to the incident.
   - This avoids a generic “firmware mutation” catch-all that would blur trust-root mutation, BootOrder drift, and ordinary firmware updates back together.

4. Keep the rule conditional and narrow.
   - Incident bundles should include `uefi_var_set_receipt_digests` when BootOrder, Secure Boot, db/dbx, capsule-intent, or other UEFI-variable mutation materially participated in the incident/support story.
   - This does not mean every bundle must always include every historical UEFI-variable write.

5. Keep stronger raw platform material separate.
   - This ADR does not promote raw efivar dumps, raw Secure Boot databases, or helper-private logs into the official bundle truth model.
   - Those remain explicit stronger side evidence under separate policy/approval/export rules.

## Consequences

- Support bundles can now answer **whether UEFI-variable mutation participated** and **which exact `uefi.var.set.receipt` bounded it**.
- Secure Boot trust-root changes, BootOrder edits, and capsule-intent writes remain explainable in the same digest-first evidence graph as the rest of the system.
- The official support handoff now stays aligned with the already-decided firmware evidence posture instead of partially undoing it.
- `bundle.plan` / `incident.bundle` remain the one official bundle-selection and metadata contract for this firmware-side mutation lane too.

## What this does not decide

This ADR does **not** decide:

- the final UI for previewing UEFI-variable mutation participation before export,
- whether every bundle template enables the selector by default,
- richer export paths for raw efivars or raw Secure Boot blobs,
- or the final helper stack for producing parsed summaries.

It only fixes the missing typed join between the already-decided `uefi.var.set.receipt` artifact and the already-decided incident/support bundle contract.
