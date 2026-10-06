# Workstation single-delivery data-transfer grants stay one-shot and fresh-grant-required

**Tier:** B (Base contract boundary)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Quarantine→Promote  

`docs/538-workstation-cross-domain-datatransfer-floor.md` already fixed the ordinary workstation data-transfer posture: cross-domain clipboard/file movement is explicit, directional, and single-delivery by default instead of an ambient shared clipboard. `docs/658-workstation-datatransfer-evidence-binds-offer-source-and-transfer-subjects-exactly.md` then made the actor pair exact, and `docs/659-workstation-datatransfer-receipts-join-exact-grants-by-digest.md` made the consumed grant artifact exact too.

One small but still expensive contract gap remained:
**the archive said `single-delivery` was the boring default, but it still left too much room for replay folklore about what happens after the first successful read-side transfer.**

This doc makes the next narrow cut:
**for the ordinary workstation lane, `delivery_mode = single-delivery` means the first successful read-side transfer exhausts the grant, and ordinary recovery is a fresh explicit grant / re-offer rather than replay, clipboard-history resurrection, or broker-side re-delivery folklore.**

See also:
- ADR: `adrs/ADR-0250-workstation-single-delivery-datatransfer-grants-stay-one-shot-and-fresh-grant-required.md`
- data-transfer floor: `docs/538-workstation-cross-domain-datatransfer-floor.md`
- portal notes: `docs/205-data-transfer-portals-clipboard-and-dnd.md`
- OCR text-egress boundary: `docs/657-workstation-ocr-text-egress-stays-explicit-plain-text-single-delivery.md`
- exact actor and grant joins: `docs/658-workstation-datatransfer-evidence-binds-offer-source-and-transfer-subjects-exactly.md`, `docs/659-workstation-datatransfer-receipts-join-exact-grants-by-digest.md`
- schemas/examples: `spec/ui.datatransfer.grant.schema.json`, `spec/ui.datatransfer.receipt.schema.json`, `spec/examples/ui.datatransfer.grant.json`, `spec/examples/ui.datatransfer.receipt.json`, `spec/examples/ui.datatransfer.grant.ocr-inspection-text.json`, `spec/examples/ui.datatransfer.receipt.ocr-inspection-text.json`

## Why this needs a hard decision

Without a tighter rule, "single-delivery" still leaves too much room for convenience drift:

- a broker may quietly replay the same grant if the receiving app says paste failed,
- a host clipboard history feature may resurrect a supposedly spent cross-domain offer,
- or support tooling may have to guess whether another transfer under the same `offer_id` was legitimate or already outside the ordinary lane.

That would re-open exactly the kind of hidden ambient behavior the workstation archive has been trying to squeeze out.

## Accepted baseline

For the ordinary workstation lane:

- `delivery_mode = single-delivery` means **one successful read-side delivery** under that exact grant artifact
- the first successful read-side transfer **exhausts the grant**
- successful ordinary read-side receipts must therefore carry `grant_exhausted = true`
- if the user wants to try again after the first successful delivery, the boring path is **fresh explicit grant / re-offer required**
- implementations should not treat clipboard history, broker replay, or stale offer reuse as equivalent to a fresh grant

This keeps recovery honest: if the destination app lost the pasted text after receipt-minting time, the right recovery story is to **copy again** or otherwise mint a **fresh reviewed transfer grant**, not to pretend the original one was still alive.

## What this buys

### 1) Single-delivery stops being folklore

`single-delivery` now has one boring operational meaning instead of a family of convenience interpretations.
Detached tooling can read `grant_exhausted = true` and know the ordinary lane is finished.

### 2) OCR/searchable inspection egress stays bounded all the way through

The OCR text-egress lane was already explicit, plain-text, and single-delivery by default.
This doc fixes the next support/recovery interpretation too:
**quoted OCR text does not get a hidden replay lane just because the source artifact stayed open.**

### 3) A smaller future exception lane

A future explicit multi-delivery or clipboard-history exception may still be worth designing.
But it now has to be visibly different from the ordinary lane instead of hiding behind the same `single-delivery` label.

## What is explicitly not baseline

The ordinary workstation lane does **not** treat these as equivalent to a fresh explicit grant:

- reusing a spent single-delivery grant after the first successful read-side transfer
- resurrecting a spent transfer from host clipboard history
- re-delivering a spent transfer from broker-only state because the receiving app later reports failure
- inferring "probably the same paste" from `offer_id` alone

## Related docs

- `docs/205-data-transfer-portals-clipboard-and-dnd.md`
- `docs/410-desktop-viability-checklist.md`
- `docs/457-workstation-host-ui-and-appvm-boundary.md`
- `docs/484-origin-label-authority-and-anti-laundering-boundary.md`
- `docs/538-workstation-cross-domain-datatransfer-floor.md`
- `docs/657-workstation-ocr-text-egress-stays-explicit-plain-text-single-delivery.md`
- `docs/658-workstation-datatransfer-evidence-binds-offer-source-and-transfer-subjects-exactly.md`
- `docs/659-workstation-datatransfer-receipts-join-exact-grants-by-digest.md`
- `spec/ui.datatransfer.grant.schema.json`
- `spec/ui.datatransfer.receipt.schema.json`


This now has the matching lifetime boundary too: `docs/661-workstation-datatransfer-grants-carry-exact-effective-until-and-late-delivery-fails-closed.md` keeps unused ordinary authority from drifting past timeout through broker grace periods by requiring exact `effective_until` and fail-closed late delivery. `docs/662-workstation-datatransfer-renewals-stay-successor-grants-and-predecessor-digest-linked.md` then fixes the matching reviewed-retry continuity boundary: when the human or policy really does approve a retry, the result is a fresh successor-shaped grant with explicit predecessor digest, `renewal_posture`, and no in-place mutation of the spent grant.

Last updated: 2026-03-22r392
