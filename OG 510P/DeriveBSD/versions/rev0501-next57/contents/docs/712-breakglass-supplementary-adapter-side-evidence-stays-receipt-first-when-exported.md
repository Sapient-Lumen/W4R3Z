# Breakglass supplementary adapter side evidence stays receipt-first when exported

**Tier:** B (Cross-cutting breakglass/export boundary)  
**Profiles:** A, B, C, D  
**Pillars:** operability, isolation, supply-chain  
**Patterns:** Bundles, Broker→Lease→Receipt, Adapter→Shadow→Replace

`docs/710` fixed the baseline breakglass receipt to stay adapter-thin.
`docs/711` then fixed official support handoff to stay authority-first on exact `breakglass.receipt` digests.

That still leaves one small but expensive export ambiguity:
**if richer BMC / KVM / SOL / virtual-media runtime material has to travel before a dedicated typed family exists, what should the archive point at?**

## Accepted boundary

Keep it **receipt-first**.

If supplementary breakglass adapter/runtime material is exported or referenced portably before a dedicated typed family exists, the portable archive surface should point at the typed proof chain for that act:

- `redaction.receipt` when sanitization materially shaped the artifact
- `export.receipt` for the governed export act
- `transport.receipt` and `transport.acceptance.receipt` when the stronger handoff lane emitted them

The raw attachment, portal object id, visible upload handle, or ticket prose may still exist operationally, but it is not the portable truth surface. Even this receipt-first chain still needs the governing `breakglass.receipt` digest in the same portable story; receipt-first handling proof does not self-authenticate emergency authority (`docs/713-breakglass-supplementary-adapter-side-evidence-stays-authority-anchored-when-portably-carried.md`).

## What this means in practice

### Authority proof still stays where it already belongs

Official incident/support handoff still proves emergency authority participation through exact `breakglass_receipt_digests`.
This page does not widen that first-class bundle contract.

### Supplementary runtime material may still travel

Sometimes a case still needs richer side evidence, for example:

- virtual-console launch/runtime diagnostics
- SOL / serial runtime traces
- virtual-media session/runtime state
- screenshots, crash videos, or similar operator artifacts

Before a dedicated typed family exists, that material may still travel — but the portable archive answer should be the typed export/redaction receipts describing how it was handled, not the raw external handle by itself.

### `extra[]` should prefer receipt digests over attachment folklore

If `incident.bundle.includes.extra[]` carries anything about this richer breakglass adapter/runtime material, prefer the matching receipt evidence digests.
That keeps detached review on the archive’s ordinary export discipline instead of making later readers depend on whichever case system or portal happened to hold the blob.

## Why this is the right narrow cut

The primary management sources already separate these runtime surfaces and treat them as security-sensitive operational features rather than portable authority records.
Redfish documents `ConsoleEntryCommand`, `HotKeySequenceDisplay`, `SerialConsole`, `GraphicalConsole`, `VirtualMediaConfig`, and `VirtualMedia` as distinct properties rather than one generic OOB fact surface.
OpenBMC’s virtual-media design also separates browser-proxied and BMC-managed modes and exposes a `WebSocketEndpoint` / image / connection model specific to that facility.
Dell’s iDRAC security guidance similarly treats virtual console and virtual media as distinct features with their own encryption and redirection settings.

That is exactly the situation where DeriveBSD should keep the archive-facing truth on ordinary typed redaction/export/transport receipts rather than on whatever raw case attachment or vendor handle happened to be created along the way.

## First spec cut

The implementation cut is intentionally small:

- tighten `incident.bundle.includes.extra[]` so the preferred portable surface for richer breakglass adapter/runtime material is receipt-first
- teach breakglass/support docs that supplementary adapter/runtime exports should point at typed redaction/export/transport proof when available
- add a guardrail that fails if the archive drifts back toward raw attachment handles or ticket prose as the portable truth surface for this material

## What this does *not* decide

This cut does **not** decide:

- the exact future artifact family for breakglass adapter-side evidence
- whether screenshots/videos/log bundles deserve their own typed schemas
- whether future richer adapter-side-evidence artifacts should gain first-class bundle fields
- or which case systems/export adapters are mandatory

It decides only the smaller export boundary worth locking now:
**supplementary breakglass adapter/runtime material stays second-class, and when it travels the portable archive answer is the typed receipt chain rather than the raw external handle.**

## Related docs

- ADR: `adrs/ADR-0302-breakglass-supplementary-adapter-side-evidence-stays-receipt-first-when-exported.md`
- breakglass proof in bundles: `docs/629-incident-bundles-carry-breakglass-proof-by-digest.md`
- adapter-thin baseline receipt: `docs/710-breakglass-adapter-details-stay-redacted-side-evidence-and-off-baseline-receipt.md`
- authority-first bundle contract: `docs/711-breakglass-adapter-side-evidence-stays-off-first-class-bundle-contract-until-typed-family-exists.md`
- authority-anchored supplementary handoff: `docs/713-breakglass-supplementary-adapter-side-evidence-stays-authority-anchored-when-portably-carried.md`
- incident bundles: `docs/216-incident-snapshots-and-support-bundles.md`
- bundle plans: `docs/253-bundle-plans-and-deterministic-exports.md`
- export policy / receipts: `docs/251-export-policies-and-support-bundle-portal.md`
- support handoff contract: `docs/481-support-bundle-contract-and-timeline-first-handoff.md`
- guardrail: `tools/check_breakglass_adapter_export_receipt_boundary.py`

## References

- DMTF Redfish Release History (`ConsoleEntryCommand`, `HotKeySequenceDisplay`, `SerialConsole`, `GraphicalConsole`, `VirtualMediaConfig`, `VirtualMedia`): https://redfish.dmtf.org/schemas/Redfish_Release_History.pdf
- OpenBMC virtual-media design (proxy vs legacy modes; `WebSocketEndpoint`; browser path vs BMC-managed image mounting): https://github.com/openbmc/docs/blob/master/designs/virtual-media.md
- Dell iDRAC virtual-console / virtual-media security guidance (separate encryption / redirection posture): https://www.dell.com/support/manuals/en-us/idrac9-lifecycle-controller-v5.x-series/idrac9_security_configuration_guide/virtual-console-and-virtual-media-security?guid=guid-fb3786a6-81eb-47b7-8a39-d69d5df1fcb1&lang=en-us

Last updated: 2026-03-23r444
