# Breakglass supplementary adapter side evidence stays authority anchored when portably carried

**Tier:** B (Cross-cutting breakglass/export boundary)  
**Profiles:** A, B, C, D  
**Pillars:** operability, isolation, supply-chain  
**Patterns:** Bundles, Broker→Lease→Receipt, Adapter→Shadow→Replace

`docs/711` fixed official support handoff to stay authority-first on exact `breakglass.receipt` digests.
`docs/712` then fixed that if richer supplementary breakglass adapter/runtime material travels before a dedicated typed family exists, the portable story stays receipt-first on typed redaction/export/transport proof rather than raw case-attachment folklore.

That still leaves one small but expensive interpretation seam:
**can those supplementary receipt chains stand on their own, or must they remain anchored to the exact breakglass authority proof that makes them about emergency access in the first place?**

## Accepted boundary

Keep them **authority-anchored**.

If richer supplementary breakglass adapter/runtime material travels portably, the same bundle or support handoff should also carry the exact `breakglass_receipt_digests` that describe the governing emergency session. `extra[]` is not enough on its own. extra[] is not enough on its own.

The portable story is therefore:

- `breakglass.receipt` digests for typed emergency authority proof
- supplementary `redaction.receipt` / `export.receipt` / `transport.receipt` evidence when richer adapter/runtime artifacts also had to travel
- optional external attachments or case objects as operational detail, not portable authority

The supplementary receipt chain is useful, but it does **not** self-authenticate breakglass authority by itself.

## What this means in practice

### `extra[]` is not enough on its own

If `incident.bundle.includes.extra[]` carries supplementary breakglass adapter/runtime material or the receipt digests that describe its handling, keep at least one exact `breakglass_receipt_digests` entry in the same portable story.

Do not force later review to guess whether an upload/export trail came from:

- a real breakglass session,
- ordinary troubleshooting,
- or the wrong machine and time window entirely.

### External case attachments still stay second-class

A case system may still hold screenshots, console traces, crash videos, virtual-media diagnostics, or vendor-specific runtime exports.
But those are operational attachments, not the portable truth surface.

If that material matters enough to reference portably, the archive-facing answer remains:

1. the exact `breakglass.receipt` digest naming the emergency session,
2. then the typed redaction/export/transport receipt chain that explains how the richer side evidence moved.

### This does not widen the first-class bundle contract

This page does **not** add new first-class `incident.bundle` fields for breakglass adapter/runtime evidence.
It simply prevents the already-accepted supplementary lane from floating free of the authority record that makes it interpretable.

## Why this is the right narrow cut

The primary management sources already separate these surfaces.
Redfish models `VirtualMedia`, `SerialConsole`, `GraphicalConsole`, `AccountService`, and `SessionService` as distinct resources/properties rather than as one self-proving emergency-access artifact. NIST SP 800-86 likewise emphasizes preserving evidence integrity and chain of custody when evidence is gathered, handled, and transported.

That is exactly the situation where DeriveBSD should keep the portable support/export story anchored on the typed `breakglass.receipt` authority record and treat the richer redaction/export/transport proof as supplementary handling evidence, not as self-authenticating emergency authority.

## First spec cut

The implementation cut is intentionally small:

- tighten `incident.bundle.includes.extra[]` language so supplementary breakglass adapter/runtime evidence stays authority-anchored when it travels
- teach support/breakglass docs that receipt-first export proof still needs the matching `breakglass.receipt` digest in the same portable story
- add a guardrail that fails if the archive drifts toward orphan supplementary receipt chains pretending to prove breakglass participation on their own

## What this does *not* decide

This cut does **not** decide:

- the future typed family for breakglass adapter/runtime side evidence
- exact same-session or same-console joins for that future family
- whether screenshots/videos/runtime bundles deserve their own schema family
- or which case systems/export adapters are mandatory

It decides only the smaller support/export boundary worth locking now:
**supplementary breakglass adapter/runtime material may travel, but it must stay anchored to the exact breakglass authority proof that makes it part of an emergency-access story at all.**

## Related docs

- ADR: `adrs/ADR-0303-breakglass-supplementary-adapter-side-evidence-stays-authority-anchored-when-portably-carried.md`
- breakglass proof in bundles: `docs/629-incident-bundles-carry-breakglass-proof-by-digest.md`
- authority-first bundle contract: `docs/711-breakglass-adapter-side-evidence-stays-off-first-class-bundle-contract-until-typed-family-exists.md`
- receipt-first supplementary export boundary: `docs/712-breakglass-supplementary-adapter-side-evidence-stays-receipt-first-when-exported.md`
- incident bundles: `docs/216-incident-snapshots-and-support-bundles.md`
- support bundle contract: `docs/481-support-bundle-contract-and-timeline-first-handoff.md`
- export policies / receipts: `docs/251-export-policies-and-support-bundle-portal.md`
- breakglass workflows: `docs/250-breakglass-and-recovery-workflows.md`
- guardrail: `tools/check_breakglass_adapter_anchor_boundary.py`

## References

- DMTF Redfish Resource and Schema Guide (`VirtualMedia`, `AccountService`, `SessionService`, `SerialConsole`, `GraphicalConsole` as separate resource/property surfaces): https://redfish.dmtf.org/schemas/v1/DSP2046_2025.2.html
- NIST SP 800-86, *Guide to Integrating Forensic Techniques into Incident Response* (integrity + chain-of-custody guidance): https://csrc.nist.gov/pubs/sp/800/86/final

Last updated: 2026-03-23r444
