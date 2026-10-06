# Breakglass supplementary adapter side evidence stays artifactized and off live control locators

**Tier:** B (Cross-cutting breakglass/export boundary)  
**Profiles:** A, B, C, D  
**Pillars:** operability, isolation, supply-chain  
**Patterns:** Bundles, Broker→Lease→Receipt, Adapter→Shadow→Replace

`docs/711` fixed official support handoff to stay authority-first on exact `breakglass.receipt` digests.
`docs/712` then fixed that if richer supplementary breakglass adapter/runtime material travels before a dedicated typed family exists, the portable story stays receipt-first on typed redaction/export/transport proof instead of raw attachment folklore.
`docs/713` then fixed that those supplementary receipt chains still need the exact `breakglass.receipt` digest in the same portable story.

That still leaves one small but expensive seam:
**can the portable story still carry live control entry hints such as console URLs, copied `ConsoleEntryCommand` values, `WebSocketEndpoint` strings, image locators, or session tokens?**

## Accepted boundary

Keep portable supplementary evidence **artifactized**.

If richer supplementary breakglass adapter/runtime material travels portably, the archive-facing story should point at:

- exact `breakglass.receipt` digests for typed emergency authority proof,
- typed `redaction.receipt` / `export.receipt` / `transport.receipt` handling proof,
- and exported artifact digests or accepted case-object proof where the stronger handoff lane already has them.

Do **not** let live control locators ride in that same portable story.
Console URLs, copied `ConsoleEntryCommand` values, `WebSocketEndpoint` strings, virtual-media image locators, and session ids/tokens are operational reconnect detail, not portable review truth.

## What this means in practice

### Portable supplementary evidence stays offline-shaped

The same bundle or handoff may still carry supplementary breakglass adapter/runtime material.
But what travels should be the exported artifact and its typed handling proof — not the active browser endpoint, shell entry command, or vendor console hint that happened to exist while the artifact was gathered.

### `extra[]` is not a place for live control surfaces

`incident.bundle.includes.extra[]` may still carry supplementary evidence digests.
It is **not** where the archive should stash live console URLs, copied `ConsoleEntryCommand` strings, `WebSocketEndpoint` values, virtual-media image locators, or session tokens.

Those values are too active, too vendor/runtime-shaped, and too unstable to act like portable evidence identity.
If later review needs the artifact, the archive-facing answer should be the typed receipt chain and the exported artifact it governed.

### Operational re-entry is separate from portable review

Support teams may still need fresh live-session coordination during an incident.
That remains an operational channel concern.
The archive should not preserve those reconnect hints as part of the portable evidence story.
If a fresh session is needed later, obtain it through the management surface or a new reviewed approval path rather than replaying an old locator leaked from the earlier emergency session.

## Why this is the right narrow cut

The primary sources already describe these values as control-entry surfaces, not durable evidence identity.
DMTF’s Redfish console/virtual-media material describes `ConsoleEntryCommand` as connection arguments for entering a console. Intel’s OpenBMC Redfish API specification exposes `WebSocketEndpoint` as the endpoint socket name/location for virtual-media interaction. Dell’s iDRAC security guidance likewise describes virtual console as a browser-launched remote-control facility.

That is exactly the situation where DeriveBSD should keep the portable story on exported artifacts and typed handling receipts rather than on active entrypoints or reconnect hints.

## First spec cut

The implementation cut is intentionally small:

- tighten `incident.bundle.includes.extra[]` and nearby bundle/breakglass docs so portable supplementary evidence stays artifactized
- teach the archive that live control locators are not acceptable portable truth for supplementary breakglass adapter/runtime material
- add a guardrail that fails if the archive drifts toward console URLs, `ConsoleEntryCommand`, `WebSocketEndpoint`, image locators, or session tokens as portable supplementary evidence

## What this does *not* decide

This cut does **not** decide:

- the future typed family for richer breakglass adapter-side evidence
- same-session or same-console joins for that future family
- whether any product profile should later suppress these supplementary exports entirely
- or which operational channels are approved for live reconnect coordination

It decides only the smaller boundary worth locking now:
**portable supplementary breakglass adapter/runtime evidence stays artifactized and off live control locators.**

## Related docs

- ADR: `adrs/ADR-0304-breakglass-supplementary-adapter-side-evidence-stays-artifactized-and-off-live-control-locators.md`
- authority-first bundle contract: `docs/711-breakglass-adapter-side-evidence-stays-off-first-class-bundle-contract-until-typed-family-exists.md`
- receipt-first supplementary export boundary: `docs/712-breakglass-supplementary-adapter-side-evidence-stays-receipt-first-when-exported.md`
- authority-anchored supplementary handoff: `docs/713-breakglass-supplementary-adapter-side-evidence-stays-authority-anchored-when-portably-carried.md`
- incident bundles: `docs/216-incident-snapshots-and-support-bundles.md`
- support bundle contract: `docs/481-support-bundle-contract-and-timeline-first-handoff.md`
- export policies / receipts: `docs/251-export-policies-and-support-bundle-portal.md`
- breakglass workflows: `docs/250-breakglass-and-recovery-workflows.md`
- guardrail: `tools/check_breakglass_adapter_live_locator_boundary.py`

## References

- DMTF Redfish console/virtual-media material (`ConsoleEntryCommand` as scripted connection arguments): https://www.dmtf.org/sites/default/files/Redfish_Serial_Console_Enhancements_05-2020_WIP.pdf
- Intel® Server System OpenBMC Redfish API specification (`WebSocketEndpoint` for virtual-media interaction): https://www.intel.com/content/dam/support/us/en/documents/server-products/intel-server-obmc-redfish-interface.pdf
- Dell iDRAC virtual-console / virtual-media security guidance (browser-launched remote-control surface): https://www.dell.com/support/manuals/en-us/idrac9-lifecycle-controller-v5.x-series/idrac9_security_configuration_guide/virtual-console-and-virtual-media-security?guid=guid-fb3786a6-81eb-47b7-8a39-d69d5df1fcb1&lang=en-us

Last updated: 2026-03-23r445
