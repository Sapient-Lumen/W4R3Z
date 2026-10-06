# Breakglass supplementary adapter side evidence stays payload-anchored when portably carried

**Tier:** B (Cross-cutting breakglass/export boundary)  
**Profiles:** A, B, C, D  
**Pillars:** operability, isolation, supply-chain  
**Patterns:** Bundles, Broker→Lease→Receipt, Adapter→Shadow→Replace

`docs/711` fixed official support handoff to stay authority-first on exact `breakglass.receipt` digests.
`docs/712` then fixed that if richer supplementary breakglass adapter/runtime material travels before a dedicated typed family exists, the portable story stays receipt-first on typed redaction/export/transport proof.
`docs/713` then fixed that those supplementary receipt chains still need the exact `breakglass.receipt` digest in the same portable story.
`docs/714` then fixed that portable supplementary evidence must stay artifactized and off live control locators.

That still leaves one small but expensive seam:
**can the portable story still stop at a receipt-only chain without naming the passive artifact or accepted case object those receipts handled?**

## Accepted boundary

Keep portable supplementary evidence **payload-anchored**.

If richer supplementary breakglass adapter/runtime material travels portably, the archive-facing story should carry:

- exact `breakglass.receipt` digests for typed emergency authority proof,
- typed `redaction.receipt` / `export.receipt` / `transport.receipt` handling proof,
- and at least one exported passive artifact digest or accepted case-object proof for the artifact that actually traveled.

Do **not** stop at a receipt-only chain.
A portable story that proves handling happened but never names the passive artifact/object it handled is incomplete review truth.

## What this means in practice

### Handling proof still does not replace payload identity

Typed handling receipts are still useful and still preferred over ticket prose or raw portal handles.
But they are not the whole answer.
If supplementary breakglass adapter/runtime material travels, keep at least one passive artifact digest or accepted case-object proof in the same portable story.

### `extra[]` should not be receipt-only scrapbook space

`incident.bundle.includes.extra[]` may still carry supplementary evidence digests.
When it carries richer supplementary breakglass adapter/runtime material, do not populate it with only redaction/export/transport receipt digests.
Keep at least one digest or accepted case-object proof that names the passive artifact those receipts governed.

That keeps the archive from proving only process while outsourcing payload identity to case portals or operator memory.

### Payload identity still stays passive and offline-shaped

The payload anchor here is still about **passive exported artifacts** or accepted case-object proof for those artifacts.
It is not permission to reintroduce live control locators, copied entry commands, or other reconnect-capable management surfaces.
The accepted `docs/714` boundary still applies.

## Why this is the right narrow cut

The same evidence/integrity sources already point at the missing piece.
NIST SP 800-86 says forensic procedures should support admissibility by gathering and handling evidence properly, maintaining chain of custody, and preserving integrity, and it describes collection as identifying, labeling, recording, and collecting data while preserving its integrity. RFC 6920 formalizes naming digital objects with hash-based identifiers so the referenced object can be authenticated to the same degree as the reference.

That is exactly the narrow gap this cut closes: portable supplementary handling proof is useful, but it still needs a passive artifact/object identity anchor.

## First spec cut

The implementation cut is intentionally small:

- tighten `incident.bundle.includes.extra[]` and nearby bundle/breakglass docs so portable supplementary evidence cannot be receipt-only
- update the example bundle so the richer breakglass side-evidence trail includes both handling receipts and one passive artifact digest
- add a guardrail that fails if the archive stops saying a passive artifact digest or accepted case-object proof must travel with that supplementary receipt chain

## What this does *not* decide

This cut does **not** decide:

- the future typed family for richer breakglass adapter-side evidence
- the exact accepted-case-object schema for that future family
- same-session joins for richer console/media artifacts
- or which operational systems are approved to host accepted external case objects

It decides only the smaller boundary worth locking now:
**portable supplementary breakglass adapter/runtime evidence must stay payload-anchored, not receipt-only.**

## Related docs

- ADR: `adrs/ADR-0305-breakglass-supplementary-adapter-side-evidence-stays-payload-anchored-when-portably-carried.md`
- authority-first bundle contract: `docs/711-breakglass-adapter-side-evidence-stays-off-first-class-bundle-contract-until-typed-family-exists.md`
- receipt-first supplementary export boundary: `docs/712-breakglass-supplementary-adapter-side-evidence-stays-receipt-first-when-exported.md`
- authority-anchored supplementary handoff: `docs/713-breakglass-supplementary-adapter-side-evidence-stays-authority-anchored-when-portably-carried.md`
- live-locator firewall: `docs/714-breakglass-supplementary-adapter-side-evidence-stays-artifactized-and-off-live-control-locators.md`
- incident bundles: `docs/216-incident-snapshots-and-support-bundles.md`
- support bundle contract: `docs/481-support-bundle-contract-and-timeline-first-handoff.md`
- breakglass workflows: `docs/250-breakglass-and-recovery-workflows.md`
- guardrail: `tools/check_breakglass_adapter_payload_anchor_boundary.py`

## References

- NIST SP 800-86, *Guide to Integrating Forensic Techniques into Incident Response* (evidence integrity, collection, and chain-of-custody guidance): https://csrc.nist.gov/pubs/sp/800/86/final
- RFC 6920, *Naming Things with Hashes* (hash-based object identity / authenticity): https://www.rfc-editor.org/rfc/rfc6920.html
- Dell iDRAC HTML5 virtual console (browser-launched remote-control surface with direct launch / console URL behavior): https://www.dell.com/support/manuals/en-us/idrac9-lifecycle-controller-v5.x-series/idrac9_5.00.00.00_ug/html5-based-virtual-console?guid=guid-d7844cc4-f163-49e5-93f4-1e7f9e926857&lang=en-us
- OpenBMC virtual-media design (browser JavaScript/HTML5 over secure websockets vs BMC-managed remote-image mode): https://github.com/openbmc/docs/blob/master/designs/virtual-media.md

Last updated: 2026-03-23r446
