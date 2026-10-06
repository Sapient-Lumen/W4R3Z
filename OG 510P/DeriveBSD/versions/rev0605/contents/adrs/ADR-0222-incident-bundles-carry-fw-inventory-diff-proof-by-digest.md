# ADR-0222: Incident bundles carry firmware-inventory-diff proof by digest

- Status: Accepted
- Date: 2026-03-21

## Context

`docs/428-fw-inventory-diff-as-drift-surface.md`, `docs/321-firmware-updates-and-uefi-variables-as-evidence.md`, and `docs/621-firmware-inventory-and-mutation-evidence-detail-and-export-posture-by-profile.md` already fixed the review side of the firmware lane:

- `fw.inventory.receipt` is the routine snapshot of current platform state,
- `fw.inventory.diff` is the routine review surface when firmware/platform state is compared,
- `fw.update.receipt` is authoritative for staged/applied firmware-update outcomes,
- and `uefi.var.set.receipt` remains the separate authoritative lane for BootOrder, Secure Boot, db/dbx, and capsule-intent mutation.

The official incident/support-bundle contract still lagged behind that decision.
`incident.bundle` could carry the current `fw_inventory_digest`, plus exact mutation proof through `fw_update_receipt_digests` and `uefi_var_set_receipt_digests`, but it still had no typed way to say **which exact `fw.inventory.diff` shaped the support handoff** when the incident was about platform drift.

That omission is expensive because it quietly blurs three different questions back together:

- what platform state the bundle captured now (`fw.inventory.receipt`),
- what staged/applied mutation ran (`fw.update.receipt` / `uefi.var.set.receipt`),
- and what reviewed drift surface responders were actually looking at (`fw.inventory.diff`).

Without an explicit join, responders fall back to prose, screenshots, dashboard diffs, or manually comparing inventory receipts outside the bundle.
That re-opens the exact entropy the archive already paid to close elsewhere.

We do **not** need a generic “firmware evidence blob” or a second drift subsystem.
We need the existing support-handoff contract to name the exact bounded drift review artifact when that artifact materially shaped the incident story.

## Decision

**Incident/support bundles may carry firmware-inventory-diff proof by typed digest join.**

Specifically:

1. Keep current-state and drift-review artifacts distinct.
   - `fw_inventory_digest` continues to point at the current `fw.inventory.receipt` snapshot.
   - `fw_inventory_diff_digest` points at the reviewed `fw.inventory.diff` artifact when firmware/platform drift materially shaped the incident/support story.

2. Keep the selector real.
   - `spec/incident.bundle.schema.json#/$defs/include_knobs` now carries `firmware_inventory_diff`.
   - `bundle.plan.selection.include` must exercise that selector when the support handoff needs the reviewed drift surface, not just the current inventory snapshot.

3. Keep drift review distinct from mutation proof.
   - `fw_inventory_diff_digest` is the typed join for the reviewed drift surface.
   - `fw_update_receipt_digests` remain the typed join for staged/applied firmware-update outcomes.
   - `uefi_var_set_receipt_digests` remain the typed join for BootOrder, Secure Boot, db/dbx, and capsule-intent mutation.
   - This avoids re-collapsing “what changed,” “what review surface compared it,” and “what exact mutation ran” into one generic firmware field.

4. Keep the rule conditional and narrow.
   - Bundles should include `fw_inventory_diff_digest` when a reviewed firmware/platform diff materially participated in the incident/support story.
   - This does not mean every bundle must always include every historical or possible firmware diff.

5. Keep ad-hoc external diffing as side workflow, not official truth.
   - This ADR does not bless screenshots, portal comparisons, or manually produced diffs as the canonical support-handoff proof.
   - Those remain auxiliary review aids unless they produce or reference the typed `fw.inventory.diff` object.

## Consequences

- Support bundles can now answer **what current firmware/platform state was captured** and **which exact reviewed drift surface shaped the handoff**.
- Firmware/platform drift stays on the same digest-first evidence graph as updates, trust-root mutation, and other operational proof.
- The official support handoff no longer forces responders to infer the “important diff” from prose or to recompute it out-of-band.
- `bundle.plan` / `incident.bundle` remain the one official bundle-selection and metadata contract for this drift-review lane too.

## What this does not decide

This ADR does **not** decide:

- the final UI for previewing firmware drift before export,
- whether every bundle template enables the drift selector by default,
- whether bundles should include multiple firmware diffs in future,
- or richer raw export paths for platform-specific vendor comparison reports.

It only makes the already-existing drift review artifact (`fw.inventory.diff`) joinable through the official incident/support-bundle contract.
