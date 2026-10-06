# Workstation sanitized inspection derivatives stay inspection-shaped and disposable-first

**Tier:** B (Base contract boundary)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability, supply-chain  
**Patterns:** Broker→Lease→Receipt, Quarantine→Promote  

`docs/606-workstation-imported-foreign-documents-stay-view-first.md` already fixed the first mutation floor: imported foreign originals stay **view-first**, and editing requires an explicit working-copy step.
`docs/653-workstation-imported-foreign-document-viewing-stays-disposable-first.md` then fixed the ordinary viewer-lifetime floor for those imported originals: the baseline inspection lane is **disposable-first** rather than a remembered persistent reader default.

But one practical ambiguity still remained after those cuts:
**once the system has produced a sanitized or converted inspection derivative from that same foreign import, does that result become an ordinary trusted/local document for persistent viewing by default, or does it stay an inspection-shaped object until a later explicit authoring/promotion act occurs?**

This doc makes the next narrow cut:
**sanitized inspection derivatives stay inspection-shaped and disposable-first by default; sanitizer success is not implicit trust-promotion into a remembered persistent viewer or ambient trusted-local document class.**

See also:
- ADR: `adrs/ADR-0244-workstation-sanitized-inspection-derivatives-stay-inspection-shaped-and-disposable-first.md`
- imported-original view-first boundary: `docs/606-workstation-imported-foreign-documents-stay-view-first.md`
- imported-original disposable-viewing boundary: `docs/653-workstation-imported-foreign-document-viewing-stays-disposable-first.md`
- sanitization portal: `docs/267-sanitization-portal-and-disposable-sandboxes.md`
- anti-laundering boundary: `docs/484-origin-label-authority-and-anti-laundering-boundary.md`
- working-copy lane: `docs/607-workstation-working-copy-receipts-and-edit-route-joins.md`
- host/AppVM boundary: `docs/457-workstation-host-ui-and-appvm-boundary.md`
- desktop viability: `docs/410-desktop-viability-checklist.md`
- OCR/searchable follow-on: `docs/655-workstation-ocr-searchable-sanitized-derivatives-stay-explicit-secondary-and-nondefault.md`

## Why this needs a hard decision

Without this cut, the archive still leaves a laundering-shaped loophole:

- the system imports risky foreign bytes,
- runs a sanitize/convert pipeline,
- produces an inspection derivative,
- and then quietly treats that derivative as an ordinary persistent-viewer document simply because the sanitizer succeeded.

That sounds convenient, but it smuggles two different claims together:

- **the derivative is safer to inspect than the original**, and
- **the derivative now deserves trusted/local handling semantics by default**.

Those are not the same claim.
If the archive does not say so clearly, implementations will eventually collapse “sanitized” into “fully promoted”, and the provenance / quarantine story will get laundered precisely at the point where humans stop thinking about the original risk.

Qubes and Dangerzone both teach an important lesson: sanitization is a useful inspection tool, not a magic proof that the result should inherit every ordinary desktop convenience by default. Even Microsoft Protected View makes the same broader point from another angle: safer viewing posture and ordinary editing/trust posture are separate decisions. DeriveBSD should keep the smaller, more explainable split.  

## Decision

For sanitized or converted derivatives produced from foreign imported documents:

- the derivative stays an **inspection-shaped** object, not an implicitly promoted trusted/local document
- the ordinary route for that derivative on `document_viewing` remains **disposable-first**
- remembered persistent `document_viewing` targets do **not** silently win for that derivative just because the sanitizer succeeded
- editing still requires an explicit `content.working-copy.plan` / `content.working-copy.receipt` step
- any later persistent-viewing-by-default or trusted-local posture needs a **separate explicit boundary** (future promotion/finalization/adapter work), not sanitizer success alone

This keeps “safer to inspect” distinct from “ordinary trusted/local document now”.

## Practical model

### 1) Sanitized derivatives stay joined to the original import story

A sanitized inspection derivative is still part of the same evidence chain:

- the foreign import is still the first authoritative intake act
- the derivative is still explainable as an inspection-oriented result of that intake path
- support/export surfaces should still be able to point back to the authoritative origin / import evidence

This means the archive should keep talking about `sanitized-inspection-derivative`, not letting the object disappear into generic “local document” prose.

### 2) Viewing posture stays disposable-first

For the ordinary review path:

- newly produced sanitized inspection derivatives still route to `document_viewing`
- that route should stay **policy-pinned** to a disposable viewer target
- missing disposable-viewer support still fails closed or requires a separately typed stronger path

The derivative may be easier to render safely than the original, but that is not enough reason to reopen long-lived persistent-viewer convenience as the default story.

### 3) Mutation posture stays explicit

Sanitized inspection derivatives are still **not** authoring workspaces.
If a user wants to change content, the next official step remains:

- explicit working-copy issuance through `content.working-copy.plan`
- explicit working-copy evidence through `content.working-copy.receipt`
- and then ordinary `document_editing` on that writable copy

That is why `content.working-copy.*.source.source_class = sanitized-inspection-derivative` remains important.
It tells the archive that the writable artifact came from an inspection derivative, not from ambient trusted/local state.

## What this means for provenance and anti-laundering

The origin-label / anti-laundering boundary already says provenance authority lives in `content.origin` plus typed import receipts, not in whatever the current path or app happens to imply.
This doc applies that principle to workstation document handling:

- sanitizer success does **not** erase foreign origin lineage by default
- sanitizer success does **not** implicitly clear the result into persistent viewer trust
- and sanitizer success does **not** make the derivative an ambient editing target

This is the small move that prevents “sanitized” from quietly becoming a synonym for “ordinary local now”.

## What is explicitly not baseline

The ordinary workstation sanitized-derivative lane does **not** require:

- auto-promotion of sanitized output into a persistent viewer by default
- treating sanitizer success as implicit trust-promotion
- treating sanitized derivatives as ambient `document_editing` targets
- forgetting the original import lineage once an inspection derivative exists
- widening the role vocabulary beyond `document_viewing` / `document_editing`

## Product-shape fit (A–D without forks)

- **A / secure fleet host:** support/maintenance documents can still use sanitize-first inspection without teaching that every sanitized result is now a long-lived ordinary document.
- **B / secure workstation:** the boring story stays coherent: import → disposable inspect → optional sanitized disposable inspect → explicit working copy if mutation is intended.
- **C / general-purpose OS:** compatibility pressure can still exist later, but the official Derive-managed lane stays explainable and does not silently normalize provenance laundering.
- **D / appliance factory / regulatory:** converted procedures, reports, and inbound paperwork remain auditable because sanitize output is still an inspection artifact unless a later explicit step promotes it.

## What remains intentionally open

This doc does **not** settle:

- whether some future narrow sanitized classes deserve explicit promotion into persistent viewing
- what the typed promotion/finalization artifact should be for that later move
- profile-`C` compatibility adapters for broader in-place workflows
- media/IDE/design-tool role families

Those are future RFC/ADR topics. `docs/655-workstation-ocr-searchable-sanitized-derivatives-stay-explicit-secondary-and-nondefault.md` now narrows one of those follow-ons already: optional OCR/searchable reconstruction should stay an explicit secondary derivative, with the flat visual derivative / sanitized artifact remaining the boring baseline.

## Related docs

- `docs/267-sanitization-portal-and-disposable-sandboxes.md`
- `docs/410-desktop-viability-checklist.md`
- `docs/457-workstation-host-ui-and-appvm-boundary.md`
- `docs/484-origin-label-authority-and-anti-laundering-boundary.md`
- `docs/540-workstation-role-bound-intent-targets-and-chooser-floor.md`
- `docs/541-workstation-role-slot-bindings-as-typed-state-boundary.md`
- `docs/605-workstation-file-open-import-and-bounded-document-roles.md`
- `docs/606-workstation-imported-foreign-documents-stay-view-first.md`
- `docs/607-workstation-working-copy-receipts-and-edit-route-joins.md`
- `docs/653-workstation-imported-foreign-document-viewing-stays-disposable-first.md`
- `docs/655-workstation-ocr-searchable-sanitized-derivatives-stay-explicit-secondary-and-nondefault.md`
- `spec/content.working-copy.plan.schema.json`
- `spec/content.working-copy.receipt.schema.json`
- `spec/examples/content.working-copy.plan.json`
- `spec/examples/content.working-copy.receipt.json`
- `spec/examples/intent.request.document-view.sanitized-inspection.json`
- `spec/examples/intent.route.receipt.document-view.sanitized-inspection.json`

Last updated: 2026-03-22r385
