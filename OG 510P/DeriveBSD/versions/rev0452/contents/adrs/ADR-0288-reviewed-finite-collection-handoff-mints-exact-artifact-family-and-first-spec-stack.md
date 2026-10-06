# ADR-0288: Reviewed finite-collection handoff mints exact artifact family and first spec stack

- Status: Accepted
- Date: 2026-03-23

## Context

`ADR-0262` already fixed that any richer workstation transfer lane must mint a **distinct artifact family** instead of widening ordinary `ui.datatransfer.*`, and `ADR-0263` through `ADR-0287` already narrowed the first richer queue into one implementation-shaped reviewed finite-collection handoff lane.

That leaves one practical ambiguity that is now more expensive than useful:
**the archive still says this lane must be distinct-family, manifest-first, read-only only, fresh-rooted, and receipt-rich, but it still does not name the exact artifact family or the minimum first spec stack that implementers should build.**

At this point the remaining uncertainty is not healthy flexibility.
It is a drift vector:
- one implementation could try to keep bolting fields onto ordinary `ui.datatransfer.*`,
- another could invent a broker-local manifest artifact outside the portable archive surface,
- and a third could make result-root evidence or selected-root state implicit even though the archive already rejected those ambiguities.

## Decision

For the first richer reviewed finite-collection handoff lane, the accepted distinct artifact family is:

- `ui.collection.handoff.grant`
- `ui.collection.handoff.manifest`
- `ui.collection.handoff.receipt`

This first spec stack is the minimum portable floor for the lane:

1. `ui.collection.handoff.grant`
   - names the exact source side (`offer_source_subject`) and receiving side (`subject`),
   - stays **read-only** in the first cut,
   - stays **single-retrieve-autostop** in the first cut,
   - joins the reviewed set by exact `collection_digest`,
   - and carries exact lifetime bounds (`effective_until`, optional closed-world constraints, signature).

2. `ui.collection.handoff.manifest`
   - is the authoritative manifest-first review/export surface,
   - carries the explicit selected-root set,
   - carries the ancestor-closed canonical member manifest,
   - and publishes the authoritative compact identity as `collection_digest = sha256(utf8(JCS(authoritative_manifest)))`.

3. `ui.collection.handoff.receipt`
   - joins back to the exact grant artifact through `grant_digest`,
   - joins back to the authoritative reviewed set through `collection_digest`,
   - carries the exact created fresh result root through an authoritative receiver-local opaque handle,
   - and keeps any human-facing path/display text advisory and retrieve-frozen rather than authoritative.

This family is still the first richer **B/C/D** lane fixed by `ADR-0277`; it is not an A / fleet-host baseline.

The following remain explicitly out of scope for this family and must return only as later explicit RFC/ADR work:
- write-enabled receive,
- bookmark-like reopen or repeated retrieve after success,
- sender-directed destination placement,
- top-level reviewed alias/disambiguation state,
- richer filesystem metadata preservation,
- and any A-specific operator file-ferry surface.

## Consequences

- The archive now has one exact richer family to implement instead of an RFC that still hides its final nouns.
- Ordinary `ui.datatransfer.*` stays boring and frozen.
- The reviewed finite-collection lane now has a minimal portable spec stack that can be linted, exemplified, and discussed without reopening already-set boundaries.
- Future widening pressure has a smaller target: if it does not fit inside `ui.collection.handoff.grant` / `manifest` / `receipt` as accepted here, it is later-lane work rather than “just one more field.”

## Alternatives considered

- **Keep the family name provisional longer:** rejected because the queue is already precise enough that lack of names is now just hidden drift.
- **Reuse ordinary `ui.datatransfer.*` with collection fields:** rejected by `ADR-0262` and because it would erase the frozen ordinary baseline.
- **Make the first stack grant + receipt only and keep the manifest broker-local:** rejected because manifest-first membership is already an accepted portable review/export surface, not backend folklore.
- **Add writable receive now:** rejected because `ADR-0267` already pushed that mutation pressure into later explicit work.

## Related

- `adrs/ADR-0262-workstation-richer-datatransfer-lanes-mint-distinct-artifact-families.md`
- `adrs/ADR-0263-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md`
- `adrs/ADR-0277-workstation-finite-collection-handoff-stays-profiled-to-b-c-d-and-not-a-fleet-host-baseline.md`
- `adrs/ADR-0281-workstation-finite-collection-handoff-receipts-pin-the-exact-created-fresh-root.md`
- `adrs/ADR-0287-reviewed-finite-collection-handoff-current-contract-stack-stays-canonical-and-pointer-backed.md`
- `docs/698-reviewed-finite-collection-handoff-mints-exact-artifact-family-and-first-spec-stack.md`
- `rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md`
- `spec/ui.collection.handoff.grant.schema.json`
- `spec/ui.collection.handoff.manifest.schema.json`
- `spec/ui.collection.handoff.receipt.schema.json`
