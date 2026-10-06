# Workstation OCR-derived text egress stays explicit, plain-text, and single-delivery by default

**Tier:** B (Base contract boundary)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability, supply-chain  
**Patterns:** Broker→Lease→Receipt, Quarantine→Promote  

`docs/656-workstation-ocr-searchable-sanitized-derivatives-stay-out-of-ambient-host-indexes-by-default.md` already fixed the persistence side of searchable inspection:
local in-view search may stay available, but OCR/searchable sanitized derivatives do not silently become ambient host/global index state or detached text sidecars by default.

One smaller but important ambiguity still remained:
**if a human wants to copy text out of that searchable inspection artifact, does that text quietly become ordinary ambient clipboard/export state, or does it stay on an explicit transfer lane with a boring baseline MIME and evidence join?**

This doc makes the next small cut:
**OCR-derived text egress stays an explicit `ui.datatransfer` act, the baseline transfer payload is plain text, delivery stays single-delivery by default, and transfer receipts may preserve the OCR-inspection source lineage through a typed `content_source` join instead of laundering copied text into generic host clipboard folklore.**

See also:
- ADR: `adrs/ADR-0247-workstation-ocr-text-egress-stays-explicit-plain-text-single-delivery.md`
- data-transfer portal notes: `docs/205-data-transfer-portals-clipboard-and-dnd.md`
- workstation data-transfer floor: `docs/538-workstation-cross-domain-datatransfer-floor.md`
- OCR/searchable derivative boundary: `docs/655-workstation-ocr-searchable-sanitized-derivatives-stay-explicit-secondary-and-nondefault.md`
- OCR/searchable ambient-index boundary: `docs/656-workstation-ocr-searchable-sanitized-derivatives-stay-out-of-ambient-host-indexes-by-default.md`
- single-delivery exhaustion boundary: `docs/660-workstation-single-delivery-datatransfer-grants-stay-one-shot-and-fresh-grant-required.md`
- anti-laundering boundary: `docs/484-origin-label-authority-and-anti-laundering-boundary.md`
- schemas/examples: `spec/content.ocr-inspection.plan.schema.json`, `spec/content.ocr-inspection.receipt.schema.json`, `spec/ui.datatransfer.grant.schema.json`, `spec/ui.datatransfer.receipt.schema.json`, `spec/examples/ui.datatransfer.grant.ocr-inspection-text.json`, `spec/examples/ui.datatransfer.receipt.ocr-inspection-text.json`

## Why this needs a hard decision

Once searchable OCR exists, the next convenience pressure is obvious:
let a user select text and let the system “just copy it.”
But that is not a neutral act.
It turns a bounded inspection affordance into cross-compartment data movement, and it is easy for implementations to quietly smuggle in more than the archive actually meant:

- ambient shared host clipboard state instead of an explicit cross-domain transfer
- richer MIME like HTML/RTF that reintroduces formatting and parser complexity
- durable copied-text folklore with no source join back to the OCR inspection artifact
- or “copy to local notes/editor” convenience that quietly becomes an unofficial authoring/export lane

The archive already paid to keep OCR/searchable inspection secondary, disposable-first, and out of ambient host indexes.
If text egress is left vague, that work immediately starts to unwind.
The smallest useful answer is not “forbid all copy.”
It is to keep copy/export boring, explicit, and provenance-carrying.

## Decision

For text egress sourced from `ocr-inspection-derivative` artifacts:

- the ordinary baseline remains **explicit `ui.datatransfer`**, not ambient clipboard sync
- the ordinary transfer MIME remains **`text/plain;charset=utf-8`**
- **single-delivery** remains the baseline cross-domain posture
- in that ordinary lane, the first successful read-side transfer exhausts the grant and recovery is fresh grant / re-offer required
- rich-text / HTML transfer is **not baseline by default**
- the transfer lane may preserve the OCR-inspection source lineage (`artifact_kind`, `artifact_digest`, `source_class`, and related digests) in the typed grant/receipt
- `docs/658-workstation-datatransfer-evidence-binds-offer-source-and-transfer-subjects-exactly.md`
- `docs/660-workstation-single-delivery-datatransfer-grants-stay-one-shot-and-fresh-grant-required.md`
- `docs/659-workstation-datatransfer-receipts-join-exact-grants-by-digest.md` then fixes the actor pair too: typed transfer evidence now keeps `offer_source_subject` exact while `subject` remains the grant/receipt holder, so copied OCR text can name both the inspection viewer and the destination app without direction folklore. `docs/659-workstation-datatransfer-receipts-join-exact-grants-by-digest.md` then fixes the next portability gap too: receipts now also carry `grant_digest`, so the exact reviewed transfer artifact remains queryable in detached support/export bundles
- this does **not** yet standardize detached text files, rich excerpt packages, or a generic OCR-to-working-copy authoring lane

## Practical model

### 1) In-view search stays local; egress stays explicit

Searching inside the disposable inspection viewer is still a local inspection affordance.
The moment text crosses compartments or lands in another app, that becomes a transfer act and should use the existing broker/receipt lane instead of an ambient clipboard fiction.

### 2) Plain text is the boring baseline

The archive should prefer the smallest transfer shape that keeps quoting and lookup viable.
For OCR-derived text that means plain text by default, not HTML/RTF or other richer payloads that recreate formatting, hidden metadata, or larger parser surfaces in the destination.

### 3) Single-delivery stays the boring posture

The same reason the workstation floor rejected an ambient shared clipboard still applies here.
One explicit recipient should receive one explicit copied text payload unless policy opens a richer exception lane.

### 4) Preserve provenance when text leaves the lane

A copied quote or excerpt should not become an evidence orphan.
If the transfer broker knows the payload came from an OCR inspection derivative, the grant/receipt may preserve that source lineage through `ui.datatransfer.*.content_source` so support/export/forensics can still answer which inspection artifact produced the copied text. The typed transfer artifacts may also carry exact transferred payload identity through `offer.payload_digest` and `summary.payload_digest`, so detached export can prove which exact copied text crossed instead of treating regenerated OCR output as “close enough.” `docs/658-workstation-datatransfer-evidence-binds-offer-source-and-transfer-subjects-exactly.md` now keeps the same evidence lane actor-exact too: `offer_source_subject` can name the inspection viewer while `subject` names the receiving note/editor app. `docs/659-workstation-datatransfer-receipts-join-exact-grants-by-digest.md` then keeps the policy join exact too: `grant_digest` can name the exact transfer grant artifact instead of leaving detached export to reconstruct the rule set from broker state. `docs/665-workstation-successor-datatransfer-grants-stay-exact-payload-bound-and-no-semantic-equivalence-rebinding.md` uses that same payload digest to keep reviewed successor continuity bound to the same exact transferred payload rather than semantic-equivalence folklore.
`docs/660-workstation-single-delivery-datatransfer-grants-stay-one-shot-and-fresh-grant-required.md` then fixes the next recovery interpretation too: once that ordinary OCR-text transfer succeeds, the grant is spent and later recovery is fresh grant / re-offer required rather than clipboard-history or broker replay folklore. `docs/662-workstation-datatransfer-renewals-stay-successor-grants-and-predecessor-digest-linked.md` then fixes the matching reviewed continuity seam too: any explicit retry stays a new grant story and carries `renewal_posture` instead of quietly mutating the earlier OCR-text transfer grant in place.

## Why this is the smallest useful cut

This is not a whole “secure quote workflow” subsystem.
It only keeps the next likely convenience drift from collapsing inspection into ambient authoring/export behavior.

The archive already had the pieces:

- explicit cross-domain data transfer
- single-delivery defaults
- OCR/searchable inspection as an explicit secondary derivative
- no ambient host indexing for foreign-derived searchable text

The missing move was just to say that **copying OCR-derived text is still a transfer act**, and that the boring baseline should stay **plain-text, single-delivery, and evidence-carrying**.

## Related docs

- `docs/205-data-transfer-portals-clipboard-and-dnd.md`
- `docs/267-sanitization-portal-and-disposable-sandboxes.md`
- `docs/410-desktop-viability-checklist.md`
- `docs/457-workstation-host-ui-and-appvm-boundary.md`
- `docs/484-origin-label-authority-and-anti-laundering-boundary.md`
- `docs/538-workstation-cross-domain-datatransfer-floor.md`
- `docs/655-workstation-ocr-searchable-sanitized-derivatives-stay-explicit-secondary-and-nondefault.md`
- `docs/656-workstation-ocr-searchable-sanitized-derivatives-stay-out-of-ambient-host-indexes-by-default.md`
- `spec/content.ocr-inspection.plan.schema.json`
- `spec/content.ocr-inspection.receipt.schema.json`
- `spec/ui.datatransfer.grant.schema.json`
- `spec/ui.datatransfer.receipt.schema.json`
- `spec/examples/ui.datatransfer.grant.ocr-inspection-text.json`
- `spec/examples/ui.datatransfer.receipt.ocr-inspection-text.json`
- `docs/658-workstation-datatransfer-evidence-binds-offer-source-and-transfer-subjects-exactly.md`


This lane now inherits the same exact lifetime rule too: `docs/661-workstation-datatransfer-grants-carry-exact-effective-until-and-late-delivery-fails-closed.md` keeps OCR-derived text transfer bounded by explicit `effective_until`, so copied inspection text does not ride on stale broker grace-period folklore.

Last updated: 2026-03-22r395
