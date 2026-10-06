# Breakglass adapter side evidence stays off first-class bundle contract until typed family exists

**Tier:** B (Cross-cutting support/export boundary)  
**Profiles:** A, B, C, D  
**Pillars:** operability, isolation, reproducibility  
**Patterns:** Bundles, Broker→Lease→Receipt, Adapter→Shadow→Replace

`docs/629` already fixed the first-class support-handoff answer for emergency authority:
`incident.bundle.includes.breakglass_receipt_digests` is where official bundles prove that breakglass participated.

`docs/710` then fixed the nearby receipt boundary:
rich BMC / KVM / SOL / virtual-media launch/runtime detail stays out of the baseline `breakglass.receipt` and remains redacted side evidence.

This page fixes the next implementation shortcut before it lands:
**should official support bundles now mint first-class fields for that richer adapter/runtime detail anyway?**

## Accepted boundary

No.

Official breakglass support handoff stays **authority-first**:

- `breakglass_receipt_digests` remains the typed bundle proof that emergency authority participated
- richer adapter/runtime material may travel only as **supplementary side evidence** for now
- and no new first-class `incident.bundle` fields are minted for that material until a dedicated typed artifact family exists
- if that supplementary material travels, keep the portable archive story receipt-first on typed export/redaction/transport receipts rather than raw attachment handles
- and keep that supplementary receipt chain authority-anchored to exact `breakglass.receipt` proof in the same portable story instead of letting it float alone (`docs/713-breakglass-supplementary-adapter-side-evidence-stays-authority-anchored-when-portably-carried.md`)

## What this means in practice

### The official proof stays exact and portable

If emergency access mattered to the incident, the bundle should still answer that question through exact `breakglass.receipt` digests.
That remains the portable answer across A/B/C/D.

### Supplementary adapter evidence is allowed, but it is not the contract

Some investigations may still need richer material, for example:

- BMC / virtual-console launch diagnostics
- SOL / serial-console runtime detail
- virtual-media session/runtime state
- screenshots, crash videos, or similar adapter-specific operator artifacts

Before a dedicated typed family exists, that material may appear only as:

- `incident.bundle.includes.extra[]` evidence digests, and/or
- explicit external case attachments under stronger support/export policy

When it does travel, prefer receipt-first on typed export/redaction/transport receipts instead of treating raw attachment ids, portal object handles, or ticket prose as the archive-facing truth surface (`docs/712-breakglass-supplementary-adapter-side-evidence-stays-receipt-first-when-exported.md`).

That makes the material usable without pretending the archive already standardized a portable cross-vendor schema for it.

### `extra[]` is not an escape hatch for authority truth

The key boring rule is:
`includes.extra[]` can supplement the incident, but it does **not** replace `breakglass_receipt_digests`.

If a bundle can only explain breakglass participation by pointing at `extra[]`, screenshots, or ticket prose, it has drifted away from the archive's typed support-handoff contract.

## Why this is the right narrow cut

The primary management sources already separate these surfaces instead of flattening them.
Redfish models serial console, graphical console, and virtual-media-related properties separately, and recent Redfish release history calls out `ConsoleEntryCommand`, `HotKeySequenceDisplay`, `SerialConsole`, `GraphicalConsole`, `VirtualMediaConfig`, and `VirtualMedia` as distinct surfaces rather than one generic OOB blob.
OpenBMC documents virtual media as a separate facility with proxy and legacy modes, while Dell documents that virtual media can be accessed with or without virtual console.

That is exactly the situation where DeriveBSD should resist standardizing a premature first-class bundle schema for adapter/runtime detail.
The authority receipt is already portable; the richer runtime material is still adapter-specific and policy-sensitive.

## First spec cut

The implementation cut is intentionally small:

- keep `incident.bundle.includes.breakglass_receipt_digests` as the first-class official handoff proof
- tighten `incident.bundle.includes.extra[]` descriptions so it is clearly supplementary evidence rather than a substitute for typed contract fields
- teach the breakglass/support docs that richer adapter/runtime material can ride only as supplementary evidence or external case attachments for now
- add a guardrail that fails if the archive starts promising first-class breakglass adapter bundle fields before the dedicated typed family exists

## What this does *not* decide

This cut does **not** decide:

- the exact artifact schema for future adapter-side-evidence objects
- the review UI for that richer material
- whether such artifacts should later gain first-class typed joins in support bundles
- or which product shapes would include them by default

It decides only the smaller implementation boundary worth locking now:
**official support truth remains authority-first, and richer breakglass adapter/runtime material stays supplementary until it earns its own typed family.**

## Related docs

- ADR: `adrs/ADR-0301-breakglass-adapter-side-evidence-stays-off-first-class-bundle-contract-until-typed-family-exists.md`
- breakglass proof in bundles: `docs/629-incident-bundles-carry-breakglass-proof-by-digest.md`
- adapter-thin baseline receipt: `docs/710-breakglass-adapter-details-stay-redacted-side-evidence-and-off-baseline-receipt.md`
- incident bundles: `docs/216-incident-snapshots-and-support-bundles.md`
- bundle plans: `docs/253-bundle-plans-and-deterministic-exports.md`
- support handoff contract: `docs/481-support-bundle-contract-and-timeline-first-handoff.md`
- guardrail: `tools/check_breakglass_adapter_bundle_boundary.py`

## References

- DMTF Redfish Release History (`ConsoleEntryCommand`, `HotKeySequenceDisplay`, `SerialConsole`, `GraphicalConsole`, `VirtualMediaConfig`, `VirtualMedia`): https://redfish.dmtf.org/schemas/Redfish_Release_History.pdf
- OpenBMC virtual-media design (proxy vs legacy modes; separate virtual-media facility): https://github.com/openbmc/docs/blob/master/designs/virtual-media.md
- Dell iDRAC Virtual Media (virtual media may be accessed with or without virtual console): https://www.dell.com/support/manuals/en-us/poweredge-r570/idrac10_1.20.xx_ug/accessing-virtual-media?guid=guid-4fecffb2-11ac-48e8-950c-6bd6def97338&lang=en-us

Last updated: 2026-03-23r444
