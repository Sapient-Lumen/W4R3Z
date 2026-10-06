# Incident bundles carry firmware-inventory-diff proof by digest

**Tier:** B (Cross-cutting evidence boundary)  
**Profiles:** A, B, C, D  
**Pillars:** operability, reproducibility, supply-chain  
**Patterns:** Registry→Diff→Gate, Bundles  

DeriveBSD already decided that `fw.inventory.diff` is the normal review surface for firmware/platform drift.
This doc fixes the smaller but implementation-shaping support/export question the archive still left fuzzy in practice:

**how does the official incident/support bundle contract name the exact `fw.inventory.diff` when firmware/platform drift review actually shaped the story?**

The answer is intentionally narrow.
It is not a new firmware subsystem and not a generic “platform mutation” field.
It is the missing decision to make the existing drift artifact joinable through the official support-handoff contract.

See also:
- ADR: `adrs/ADR-0222-incident-bundles-carry-fw-inventory-diff-proof-by-digest.md`
- drift surface: `docs/428-fw-inventory-diff-as-drift-surface.md`
- firmware lane: `docs/321-firmware-updates-and-uefi-variables-as-evidence.md`
- platform provenance lane: `docs/417-platform-provenance-and-firmware-lifecycle-as-derived-ops.md`
- firmware evidence posture: `docs/621-firmware-inventory-and-mutation-evidence-detail-and-export-posture-by-profile.md`
- firmware-update join: `docs/631-incident-bundles-carry-fw-update-proof-by-digest.md`
- UEFI-variable join: `docs/630-incident-bundles-carry-uefi-var-set-proof-by-digest.md`
- incident bundles: `docs/216-incident-snapshots-and-support-bundles.md`
- support handoff contract: `docs/481-support-bundle-contract-and-timeline-first-handoff.md`

## Why this needs a hard decision

`docs/428-fw-inventory-diff-as-drift-surface.md` already made the review-side cut explicit:

- `fw.inventory.receipt` describes current platform state,
- `fw.inventory.diff` is the routine review surface when two inventory states are compared,
- `fw.update.receipt` remains the authoritative stage/apply mutation proof,
- and `uefi.var.set.receipt` remains the authoritative boot/trust-variable mutation proof.

But the official support/export contract still lagged behind that design in practice.
`incident.bundle` could carry `fw_inventory_digest` for the current snapshot and exact mutation proof through `fw_update_receipt_digests` / `uefi_var_set_receipt_digests`, but it still had no typed place to say which exact `fw.inventory.diff` responders were relying on.

A coherent archive should let support bundles answer all three questions distinctly:

- **what current platform state was captured?**
- **what reviewed firmware/platform drift surface shaped the handoff?**
- **what exact mutation proof, if any, participated?**

## Accepted boundary

### 1) Bundles may carry the exact firmware drift review artifact

Support bundles should not force readers to recompute or guess the important platform-drift comparison out-of-band.

- `fw_inventory_diff_digest` names the exact `fw.inventory.diff` object that belongs to the incident.
- The referenced `fw.inventory.diff` object remains the place that points at the compared inventory-receipt digests, the changed components, and the risk flags.

This keeps the official bundle contract compact while still naming the canonical drift-review proof.

### 2) The official selector is now treated as real

The canonical include surface now carries `firmware_inventory_diff`.
Because `bundle.plan.selection.include` reuses `incident.bundle` include knobs, the same selector works both when planning the bundle and when recording what the final bundle included.

That keeps firmware/platform drift review on the official support-bundle lane instead of buried in `extra`, screenshots, dashboards, or ticket prose.

### 3) Keep snapshot, drift review, and mutation proof separate

This is the design cut worth preserving.
The archive does **not** collapse all firmware/platform evidence into one generic field.

- `fw_inventory_digest` is the typed join for the current inventory snapshot.
- `fw_inventory_diff_digest` is the typed join for the reviewed drift surface.
- `fw_update_receipt_digests` are the typed join for firmware-update stage/apply outcomes.
- `uefi_var_set_receipt_digests` are the typed join for BootOrder, Secure Boot, db/dbx, and capsule-intent mutation.

That keeps “what the platform looks like now,” “what changed across two snapshots,” and “what exact mutation ran” separately explainable.

### 4) Include drift proof when it materially shaped the story

The rule is intentionally conditional.
The archive does **not** require every incident bundle to include every possible `fw.inventory.diff`.
Instead, bundles should carry `fw_inventory_diff_digest` when the reviewed firmware/platform drift materially participated in or shaped the incident/support story.

Examples:

- a fleet incident needs to prove the exact reviewed Secure Boot/trust-root drift surface that triggered a gate or investigation,
- a workstation support case needs to show the one bounded before/after firmware comparison the user approved for export,
- a general-purpose install needs to tie a post-upgrade problem to one explicit inventory diff instead of a support engineer recomputing it from raw helper output,
- or an appliance/factory handoff needs to prove what reviewed platform drift justified escalation during an audit or incident window.

### 5) Portal diffs and screenshots remain side aids, not official truth

This boundary does not promote updater dashboards, screenshots, or manually assembled before/after notes into the official bundle truth model.
Those aids may still exist as auxiliary review material, but the default support-handoff join stays digest-first:

- exact `fw.inventory.diff` digest,
- with the diff itself carrying the compared inventory receipts and risk flags,
- and optional mutation-proof joins pointing at the exact receipts that explain why that drift occurred.

That keeps human review aids and official support/export truth separate.

## Practical meaning by product shape

### A / secure fleet host

Fleet incidents can now prove which exact reviewed firmware/platform drift surface shaped a maintenance or regression handoff instead of normalizing dashboard diffs or shell comparison output as the official evidence.

### B / secure workstation

Workstation support handoff can now export one exact `fw.inventory.diff` when the user or support flow needs the before/after review surface, instead of making support infer it from screenshots or prose.

### C / general-purpose OS

C keeps compatibility adapters real.
This boundary keeps the Derive-managed firmware/platform drift story explicit in bundles without pretending every foreign vendor comparison tool inherits the full authority model.

### D / appliance / factory / regulatory

Production and audit lanes can now answer what reviewed firmware/platform drift shaped the incident handoff without collapsing the story into ad-hoc reports, screenshots, or ticket notes.

## Guardrail

- `tools/check_fw_inventory_diff_bundle_contract.py`

The guardrail checks that the official bundle selector and metadata surfaces keep `fw.inventory.diff` proof explicit, that the canonical bundle example binds the real `fw.inventory.diff` example digest, and that the relevant docs keep teaching the same firmware/support-bundle story.

## What remains open

This doc does **not** fix:

- the exact UI for previewing firmware/platform drift before export,
- whether every bundle template enables the drift selector by default,
- whether future support handoffs should carry more than one `fw.inventory.diff`,
- or richer export paths for vendor-specific comparison reports.

The expensive hard decision is smaller:
DeriveBSD incident bundles no longer get to mention firmware/platform drift only in prose while hand-waving the exact `fw.inventory.diff` review artifact.

Last updated: 2026-03-21r362
