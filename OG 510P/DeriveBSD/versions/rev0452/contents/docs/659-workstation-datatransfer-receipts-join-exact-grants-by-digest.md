# Workstation data-transfer receipts join exact grants by digest

**Tier:** B (Base contract boundary)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Quarantine→Promote

`docs/538-workstation-cross-domain-datatransfer-floor.md` already fixed the workstation transfer posture: ordinary cross-domain clipboard/file movement is explicit, directional, and single-delivery by default rather than an ambient shared clipboard. `docs/658-workstation-datatransfer-evidence-binds-offer-source-and-transfer-subjects-exactly.md` then fixed the actor side of that same lane by making `ui.datatransfer.*` artifacts name both the exact `offer_source_subject` and the current `subject`.

One small but expensive evidence gap still remained:
**the receipt could name the actors and the offer id, but it still did not point back to the exact `ui.datatransfer.grant` artifact whose policy/MIME/expiry constraints made the transfer legitimate.**

This doc makes the next narrow cut:
**`ui.datatransfer.receipt` now carries exact `grant_digest`, so support/export/forensics can join a transfer back to the exact reviewed grant artifact instead of reconstructing policy from `offer_id`, `lease_id`, or broker memory.**

See also:
- ADR: `adrs/ADR-0249-workstation-datatransfer-receipts-join-exact-grants-by-digest.md`
- data-transfer floor: `docs/538-workstation-cross-domain-datatransfer-floor.md`
- data-transfer actor exactness: `docs/658-workstation-datatransfer-evidence-binds-offer-source-and-transfer-subjects-exactly.md`
- OCR text egress boundary: `docs/657-workstation-ocr-text-egress-stays-explicit-plain-text-single-delivery.md`
- portal notes: `docs/205-data-transfer-portals-clipboard-and-dnd.md`
- schemas/examples: `spec/ui.datatransfer.grant.schema.json`, `spec/ui.datatransfer.receipt.schema.json`, `spec/examples/ui.datatransfer.grant.json`, `spec/examples/ui.datatransfer.receipt.json`, `spec/examples/ui.datatransfer.grant.ocr-inspection-text.json`, `spec/examples/ui.datatransfer.receipt.ocr-inspection-text.json`

## Why this needs a hard decision

The archive keeps choosing **exact digests over reconstruction folklore** almost everywhere else:

- route receipts point back to the exact import receipt
- edit routes point back to the exact working-copy receipt
- candidate supersession points back to the exact earlier candidate receipt
- post-breakglass ordinary authority points back to the exact relevant breakglass receipt

The transfer lane had not finished that move yet.
If a receipt only says `lease_id` plus `offer_id`, detached tooling still has to guess which grant artifact actually governed the transfer:

- did the source create a newer grant for the same offer id?
- which MIME set / max-bytes / foreground rule / expiry constraint was the one actually consumed?
- was the transfer under the ordinary single-delivery lane or a later explicit exception?

That is too much reconstruction for a lane that is supposed to be boring, explicit, and supportable.

## Accepted baseline

For the ordinary workstation lane:

- `ui.datatransfer.receipt` carries exact `grant_digest`
- that digest points to the exact `ui.datatransfer.grant` artifact whose reviewed constraints governed the transfer
- `offer_id` and `lease_id` still remain useful operational correlates, but they are no longer the portable source of truth
- detached tooling should answer policy questions from the joined grant artifact, not from broker-side reconstruction

## What this buys

### 1) Portable transfer policy evidence

A support bundle can now answer not only *who offered data to whom*, but also *which exact grant artifact allowed it*.
That keeps MIME limits, size limits, TTL posture, and foreground/expiry rules portable instead of hidden in broker logs.

### 2) Cleaner multi-delivery and retry stories

Even if a future explicit exception lane allows `delivery_mode = multi-delivery`, every receipt can still point back to the same exact grant artifact rather than relying on `offer_id` reuse folklore.
We do **not** need to settle the full multi-delivery subsystem now in order to make receipts exact today.
`docs/660-workstation-single-delivery-datatransfer-grants-stay-one-shot-and-fresh-grant-required.md` now fixes the ordinary recovery side too: `grant_exhausted = true` is the boring one-shot answer, and later recovery is fresh grant / re-offer required rather than replay folklore.

### 3) OCR excerpt transfer stays provenance-carrying all the way down

The last OCR cut already kept copied OCR text on the explicit transfer lane and allowed `content_source` joins.
This doc keeps the next join exact too:

- `content_source` can still name the OCR-inspection artifact that produced the text
- `offer_source_subject` can still name the inspection viewer that offered it
- `subject` can still name the receiving notes/editor app
- and `grant_digest` can now also name the exact reviewed transfer artifact that authorized the crossing

That is a much better support/export story than “a quote was pasted at some point.”

## Why this is the smallest useful cut

This does **not** invent a richer clipboard protocol, grant database, or replay subsystem.
It only makes the existing transfer artifacts follow the same exact-join discipline the archive already uses elsewhere.

The transfer lane already had:

- explicit grants and receipts
- exact actor pair (`offer_source_subject`, `subject`)
- typed MIME/size/TTL posture
- optional content provenance joins for OCR-derived text

The missing move was simply to keep the receipt joinable back to the exact grant artifact by digest.

## Related docs

- `docs/205-data-transfer-portals-clipboard-and-dnd.md`
- `docs/457-workstation-host-ui-and-appvm-boundary.md`
- `docs/484-origin-label-authority-and-anti-laundering-boundary.md`
- `docs/538-workstation-cross-domain-datatransfer-floor.md`
- `docs/657-workstation-ocr-text-egress-stays-explicit-plain-text-single-delivery.md`
- `docs/658-workstation-datatransfer-evidence-binds-offer-source-and-transfer-subjects-exactly.md`
- `docs/660-workstation-single-delivery-datatransfer-grants-stay-one-shot-and-fresh-grant-required.md`
- `spec/ui.datatransfer.grant.schema.json`
- `spec/ui.datatransfer.receipt.schema.json`


And now that receipts join exact grant artifacts, those grants also have to carry exact lifetime: `docs/661-workstation-datatransfer-grants-carry-exact-effective-until-and-late-delivery-fails-closed.md` keeps the consumed artifact publishing explicit `effective_until` so detached support/export can answer both **which grant** and **until when** without broker folklore.

Last updated: 2026-03-22r391
