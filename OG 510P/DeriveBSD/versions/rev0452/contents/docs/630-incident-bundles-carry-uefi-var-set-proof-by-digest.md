# Incident bundles carry UEFI-var-set proof by digest

**Tier:** B (Cross-cutting evidence boundary)  
**Profiles:** A, B, C, D  
**Pillars:** operability, supply-chain, reproducibility  
**Patterns:** Plan→Apply→Receipt, Bundles, Capsule  

DeriveBSD already decided that UEFI-variable mutation is a typed evidence lane and that `uefi.var.set.receipt` is the bounded mutation envelope.
This doc fixes the smaller but implementation-shaping support/export question the archive still left open:

**how does the official incident/support bundle contract name the exact `uefi.var.set.receipt` when Secure Boot, BootOrder, or capsule-intent mutation actually participated in the story?**

The answer is intentionally narrow.
It is not a new firmware subsystem and not a new product-profile key.
It is the missing digest join between the existing `uefi.var.set.receipt` artifact and the existing support-bundle contract.

See also:
- ADR: `adrs/ADR-0220-incident-bundles-carry-uefi-var-set-proof-by-digest.md`
- firmware lane: `docs/321-firmware-updates-and-uefi-variables-as-evidence.md`
- platform provenance lane: `docs/417-platform-provenance-and-firmware-lifecycle-as-derived-ops.md`
- firmware evidence posture: `docs/621-firmware-inventory-and-mutation-evidence-detail-and-export-posture-by-profile.md`
- incident bundles: `docs/216-incident-snapshots-and-support-bundles.md`
- support handoff contract: `docs/481-support-bundle-contract-and-timeline-first-handoff.md`

## Why this needs a hard decision

`docs/321-firmware-updates-and-uefi-variables-as-evidence.md` already fixed the core firmware-side mutation story:

- `fw.inventory.receipt` and `fw.inventory.diff` describe platform state and drift,
- `fw.update.receipt` is authoritative for firmware-update mutation,
- and `uefi.var.set.receipt` is authoritative for BootOrder, Secure Boot, db/dbx, and capsule-intent mutation.

But the official support/export contract still lagged behind that decision.
`incident.bundle` already had room for the firmware inventory digest and `fw_update_receipt_digests`, but not for the exact `uefi.var.set.receipt` digest itself.

That is expensive because it quietly pushes responders back toward raw efivar dumps, helper stdout, screenshots, or ticket notes right after the archive had already paid to define a better answer.

A coherent archive should let support bundles answer both:

- **did UEFI-variable mutation participate?**
- **which exact bounded `uefi.var.set.receipt` was it?**

## Accepted boundary

### 1) Bundles carry the exact UEFI-variable mutation receipt

Support bundles should not force readers to reconstruct Secure Boot, BootOrder, or capsule-intent changes from side evidence.

- `uefi_var_set_receipt_digests` name the exact `uefi.var.set.receipt` object(s) that belong to the incident.
- The referenced `uefi.var.set.receipt` object remains the place that points at the exact variable operations and old/new payload digests.

This keeps the official bundle contract compact while still naming the canonical mutation receipt.

### 2) The official selector is now typed

The canonical include surface now carries `uefi_var_set_receipts`.
Because `bundle.plan.selection.include` reuses `incident.bundle` include knobs, the same selector works both when planning a bundle and when recording what the final bundle included.

That keeps UEFI-variable mutation on the official support-bundle lane instead of in `extra`, raw export side channels, or ticket prose.

### 3) Keep firmware-update and UEFI-variable proof separate

This is the hard design cut worth preserving.
The archive does **not** collapse all platform mutation into one generic “firmware mutation” field.

- `fw_update_receipt_digests` remain the typed join for firmware-update apply outcomes.
- `uefi_var_set_receipt_digests` are the typed join for BootOrder, Secure Boot, db/dbx, and capsule-intent mutation.

That keeps trust-root changes and boot-variable drift explainable without laundering them into generic firmware-update folklore.

### 4) Include UEFI-variable proof when it materially shaped the story

The rule is intentionally conditional.
The archive does **not** require every incident bundle to include every historical `uefi.var.set.receipt`.
Instead, bundles should carry `uefi.var.set.receipt` digests when UEFI-variable mutation materially participated in or shaped the incident/support story.

Examples:

- a fleet issue involved Secure Boot/db/dbx rollout state and the handoff needs to prove which exact trust-root mutation ran,
- a workstation incident needs to prove that a BootOrder or Secure Boot change happened in a user-visible trusted-UI flow,
- a general-purpose install used a Derive-managed capsule-intent or boot-variable change alongside a firmware update and the bundle should tie that act to one exact receipt,
- or an appliance/factory handoff needs to prove whether a production trust-root or boot-path mutation participated in the incident window.

### 5) raw efivar dumps remain stronger side evidence

This boundary does not promote raw efivar dumps, raw Secure Boot databases, or helper-private logs into the official bundle truth model.
Those artifacts may still exist as explicit stronger/debugging evidence, but the default support-bundle join stays digest-first:

- exact `uefi.var.set.receipt` digest,
- with the receipt itself carrying the typed variable operations and old/new value digests,
- and optional event/export joins pointing at the same mutation proof.

That keeps raw platform material and support/export truth separate.

## Practical meaning by product shape

### A / secure fleet host

Fleet incidents can now prove which exact Secure Boot, db/dbx, BootOrder, or capsule-intent mutation participated in a failure or maintenance story without normalizing raw efivar dumps as the truth surface.

### B / secure workstation

Workstation support handoff can now export one exact `uefi.var.set.receipt` instead of making support reconstruct a trusted-UI firmware/trust-root act from screenshots or prose alone.

### C / general-purpose OS

C keeps compatibility adapters real.
This boundary keeps the Derive-managed UEFI-variable story explicit in bundles without pretending every foreign helper inherits the full authority model.

### D / appliance / factory / regulatory

Production and audit lanes can now answer whether an approved UEFI trust-root or boot-variable mutation participated in the incident window without collapsing the story into raw platform blobs or bench folklore.

## Guardrail

- `tools/check_uefi_var_set_bundle_contract.py`

The guardrail checks that the official bundle selector and metadata surfaces carry `uefi.var.set.receipt` proof explicitly, that the canonical bundle example binds the real `uefi.var.set.receipt` example digest, and that the relevant docs keep teaching the same firmware/support-bundle story.

## What remains open

This doc does **not** fix:

- the exact UI for previewing UEFI-variable participation before export,
- whether every bundle template enables the selector by default,
- the richer export path for raw efivars or raw Secure Boot database blobs,
- or the final parsing/reporting surface for human-readable Secure Boot summaries.

The expensive hard decision is smaller:
DeriveBSD incident bundles no longer get to mention Secure Boot, BootOrder, or capsule-intent mutation only in prose while hand-waving the exact `uefi.var.set.receipt` envelope.

Last updated: 2026-03-21r360
