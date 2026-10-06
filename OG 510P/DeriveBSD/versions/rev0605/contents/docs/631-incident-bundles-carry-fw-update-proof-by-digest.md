# Incident bundles carry firmware-update proof by digest

**Tier:** B (Cross-cutting evidence boundary)  
**Profiles:** A, B, C, D  
**Pillars:** operability, reproducibility, supply-chain  
**Patterns:** Plan→Apply→Receipt, Bundles, Capsule  

DeriveBSD already decided that firmware updates are a typed evidence lane and that `fw.update.receipt` is the bounded stage/apply envelope.
This doc fixes the smaller but implementation-shaping support/export question the archive still left fuzzy in practice:

**how does the official incident/support bundle contract name the exact `fw.update.receipt` when a staged or applied firmware update actually participated in the story?**

The answer is intentionally narrow.
It is not a new firmware subsystem and not a new product-profile key.
It is the missing decision to make the existing `firmware_update_receipts` / `fw_update_receipt_digests` join real, canonical, and enforced.

See also:
- ADR: `adrs/ADR-0221-incident-bundles-carry-fw-update-proof-by-digest.md`
- firmware lane: `docs/321-firmware-updates-and-uefi-variables-as-evidence.md`
- platform provenance lane: `docs/417-platform-provenance-and-firmware-lifecycle-as-derived-ops.md`
- firmware evidence posture: `docs/621-firmware-inventory-and-mutation-evidence-detail-and-export-posture-by-profile.md`
- UEFI-variable join: `docs/630-incident-bundles-carry-uefi-var-set-proof-by-digest.md`
- incident bundles: `docs/216-incident-snapshots-and-support-bundles.md`
- support handoff contract: `docs/481-support-bundle-contract-and-timeline-first-handoff.md`

## Why this needs a hard decision

`docs/321-firmware-updates-and-uefi-variables-as-evidence.md` already fixed the core firmware-side mutation story:

- `fw.inventory.receipt` and `fw.inventory.diff` describe platform state and drift,
- `fw.update.receipt` is authoritative for staged/applied firmware-update outcomes,
- and `uefi.var.set.receipt` stays authoritative for BootOrder, Secure Boot, db/dbx, and capsule-intent mutation.

But the official support/export contract still lagged behind that decision in practice.
The schema had room for `firmware_update_receipts` and `fw_update_receipt_digests`, but the archive still had not locked them as the official support-handoff join.
The canonical examples did not bind the real `fw.update.receipt` digest, and the surrounding docs still left firmware-update participation easy to retell through updater dashboards, helper stdout, or ticket prose.

A coherent archive should let support bundles answer both:

- **did a firmware update materially participate?**
- **which exact bounded `fw.update.receipt` was it?**

## Accepted boundary

### 1) Bundles carry the exact firmware-update receipt

Support bundles should not force readers to reconstruct staged or applied firmware work from side evidence.

- `fw_update_receipt_digests` name the exact `fw.update.receipt` object(s) that belong to the incident.
- The referenced `fw.update.receipt` object remains the place that points at the plan digest, pre/post inventory digests, evidence digests, and per-target outcome status.

This keeps the official bundle contract compact while still naming the canonical firmware-update proof.

### 2) The official selector is now treated as real

The canonical include surface already carries `firmware_update_receipts`.
Because `bundle.plan.selection.include` reuses `incident.bundle` include knobs, the same selector works both when planning a bundle and when recording what the final bundle included.

That keeps firmware-update participation on the official support-bundle lane instead of in `extra`, updater dashboards, vendor job pages, or ticket prose.

### 3) Keep firmware-update and UEFI-variable proof separate

This is the design cut worth preserving.
The archive does **not** collapse all platform mutation into one generic “firmware mutation” field.

- `fw_update_receipt_digests` are the typed join for firmware-update stage/apply outcomes.
- `uefi_var_set_receipt_digests` are the typed join for BootOrder, Secure Boot, db/dbx, and capsule-intent mutation.

That keeps “firmware update ran” separate from “trust roots or boot variables changed,” which matters for both forensics and implementation.

### 4) Include firmware-update proof when it materially shaped the story

The rule is intentionally conditional.
The archive does **not** require every incident bundle to include every historical `fw.update.receipt`.
Instead, bundles should carry `fw.update.receipt` digests when staged or applied firmware-update outcomes materially participated in or shaped the incident/support story.

Examples:

- a fleet incident happened immediately after a staged capsule apply and the handoff needs to prove which exact firmware-update receipt bounded the transition,
- a workstation support case needs to show that a trusted-UI firmware update was only staged, not yet confirmed applied,
- a general-purpose install used a Derive-managed firmware lane and the bundle should tie a post-reboot failure to one exact `fw.update.receipt`,
- or an appliance/factory handoff needs to prove what production firmware-update step actually ran during the incident window.

### 5) updater dashboards and raw capsule bytes remain stronger side evidence

This boundary does not promote updater dashboards, helper stdout, raw capsule bytes, or vendor-private traces into the official bundle truth model.
Those artifacts may still exist as explicit stronger/debugging evidence, but the default support-bundle join stays digest-first:

- exact `fw.update.receipt` digest,
- with the receipt itself carrying the typed stage/apply outcome and evidence digests,
- and optional event/export joins pointing at the same mutation proof.

That keeps raw platform material and support/export truth separate.

## Practical meaning by product shape

### A / secure fleet host

Fleet incidents can now prove which exact staged/applied firmware update participated in a failure or maintenance story without normalizing updater dashboards or helper logs as the truth surface.

### B / secure workstation

Workstation support handoff can now export one exact `fw.update.receipt` instead of making support reconstruct a trusted-UI firmware flow from screenshots or prose alone.

### C / general-purpose OS

C keeps compatibility adapters real.
This boundary keeps the Derive-managed firmware-update story explicit in bundles without pretending every foreign vendor tool inherits the full authority model.

### D / appliance / factory / regulatory

Production and audit lanes can now answer whether an approved firmware update participated in the incident window without collapsing the story into raw capsule blobs or updater folklore.

## Guardrail

- `tools/check_fw_update_bundle_contract.py`

The guardrail checks that the official bundle selector and metadata surfaces keep `fw.update.receipt` proof explicit, that the canonical bundle example binds the real `fw.update.receipt` example digest, and that the relevant docs keep teaching the same firmware/support-bundle story.

## What remains open

This doc does **not** fix:

- the exact UI for previewing firmware-update participation before export,
- whether every bundle template enables the selector by default,
- the richer export path for raw capsule bytes or raw updater logs,
- or the final staging/apply helper stack.

The expensive hard decision is smaller:
DeriveBSD incident bundles no longer get to mention firmware updates only in prose while hand-waving the exact `fw.update.receipt` envelope.

Last updated: 2026-03-21r361
