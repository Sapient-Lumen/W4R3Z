# Workstation data-transfer evidence binds offer-source and transfer subject exactly

**Tier:** B (Base contract boundary)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability, supply-chain  
**Patterns:** Broker→Lease→Receipt, Quarantine→Promote

`docs/538-workstation-cross-domain-datatransfer-floor.md` already fixed the workstation clipboard/file-transfer posture:
ordinary cross-domain movement is explicit, directional, and single-delivery by default rather than an ambient shared clipboard.
`docs/657-workstation-ocr-text-egress-stays-explicit-plain-text-single-delivery.md` then fixed one narrower follow-on:
OCR-derived text copied out of searchable foreign inspection still leaves on that same explicit transfer lane, and the payload may preserve a provenance join through `ui.datatransfer.*.content_source`.

One small but consequential evidence gap still remained:
**the archive says support/export should be able to answer which compartment offered the data and which compartment accepted it, but the typed `ui.datatransfer.*` artifacts did not name the offer-side subject explicitly.**

This doc makes the next small cut:
**`ui.datatransfer.grant` and `ui.datatransfer.receipt` now carry exact `offer_source_subject`, while `subject` stays the exact grant/receipt holder, so ordinary transfer evidence can name both sides without reopening broker-side folklore or direction-dependent guesswork. `docs/659-workstation-datatransfer-receipts-join-exact-grants-by-digest.md` then fixes the next exactness gap too: the receipt must also point back to the exact grant artifact through `grant_digest`, so detached tooling can answer which reviewed transfer rule governed the crossing.**

See also:
- ADR: `adrs/ADR-0248-workstation-datatransfer-evidence-binds-offer-source-and-transfer-subject-exactly.md`
- data-transfer portal notes: `docs/205-data-transfer-portals-clipboard-and-dnd.md`
- workstation data-transfer floor: `docs/538-workstation-cross-domain-datatransfer-floor.md`
- OCR text-egress boundary: `docs/657-workstation-ocr-text-egress-stays-explicit-plain-text-single-delivery.md`
- host/AppVM boundary: `docs/457-workstation-host-ui-and-appvm-boundary.md`
- anti-laundering boundary: `docs/484-origin-label-authority-and-anti-laundering-boundary.md`
- schemas/examples: `spec/ui.datatransfer.grant.schema.json`, `spec/ui.datatransfer.receipt.schema.json`, `spec/examples/ui.datatransfer.grant.json`, `spec/examples/ui.datatransfer.receipt.json`, `spec/examples/ui.datatransfer.grant.ocr-inspection-text.json`, `spec/examples/ui.datatransfer.receipt.ocr-inspection-text.json`

## Why this needs a hard decision

The archive already chose explicit transfer.
That only really pays off if the evidence can answer who crossed what boundary.
Without an exact offer-side subject in the typed artifact, implementations drift toward weaker substitutes:

- consulting ephemeral broker state to recover who created the offer
- inferring the source from direction plus stale UI context
- assuming the current `subject` means the same thing for every transfer phase
- or relying on support notes/screenshots when the interesting question is "who offered this data to whom?"

That is too much hidden state for a lane that is supposed to be explainable and queryable.
The fix should stay small and typed.

## Decision

For `ui.datatransfer.grant` and `ui.datatransfer.receipt`:

- `subject` remains the exact holder of the grant/receipt
- `offer_source_subject` names the exact subject that created or exposed the offer
- the pair is always explicit in typed evidence instead of being reconstructed from direction-specific folklore
- for `direction = read`, the ordinary case is `offer_source_subject != subject`
- for `direction = write`, `offer_source_subject` ordinarily equals `subject` because the source is creating the offer

This keeps the lane compact without inventing a new transfer-management subsystem. In other words, subject remains the exact holder of the grant/receipt, while `offer_source_subject` names the offer-side peer.

## Practical meaning

### 1) Read-side transfer receipts can finally answer both sides directly

For the ordinary clipboard/paste case:

- `offer_source_subject` says who offered/exported the data
- `subject` says who consumed/accepted it
- `offer_id` plus `lease_id` still bind the exact offer/grant instance

That means support/export surfaces can answer the exact two-party question directly from the receipt.

### 2) Write-side grants stay self-describing too

When a subject is only creating an offer, the archive should not make readers guess whether the source side was omitted because it was unknown or because it happened to equal the holder.
Requiring `offer_source_subject` even there keeps the artifact mechanically uniform.

### 3) OCR-derived text transfer gets a cleaner evidence story

The last OCR cut already kept copied OCR text on the explicit plain-text single-delivery lane.
This doc makes the exact actor pair visible too:

- the searchable inspection viewer can remain the explicit `offer_source_subject`
- the note/editor/destination app can remain the exact `subject`
- `content_source` can still preserve which receipted OCR-inspection artifact the copied text came from

So copied excerpts no longer need direction folklore to explain both *which artifact* and *which compartments* were involved.

## Why this is the smallest useful cut

This does **not** create a new clipboard manager protocol, policy language, or quote/export subsystem.
It only fixes the typed evidence so the archive's existing transfer story becomes mechanically true.

The workstation lane already had:

- explicit brokered transfer
- `offer_id`, `lease_id`, MIME, and delivery posture
- OCR/content provenance joins where needed

The missing move was simply to carry the offer-side subject explicitly.

## Related docs

- `docs/205-data-transfer-portals-clipboard-and-dnd.md`
- `docs/410-desktop-viability-checklist.md`
- `docs/457-workstation-host-ui-and-appvm-boundary.md`
- `docs/484-origin-label-authority-and-anti-laundering-boundary.md`
- `docs/538-workstation-cross-domain-datatransfer-floor.md`
- `docs/657-workstation-ocr-text-egress-stays-explicit-plain-text-single-delivery.md`
- `spec/ui.datatransfer.grant.schema.json`
- `spec/ui.datatransfer.receipt.schema.json`
- `spec/examples/ui.datatransfer.grant.json`
- `spec/examples/ui.datatransfer.receipt.json`
- `spec/examples/ui.datatransfer.grant.ocr-inspection-text.json`
- `spec/examples/ui.datatransfer.receipt.ocr-inspection-text.json`
- `docs/659-workstation-datatransfer-receipts-join-exact-grants-by-digest.md`

Last updated: 2026-03-22r389
