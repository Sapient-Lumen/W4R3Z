# Workstation OCR/searchable sanitized derivatives stay explicit, secondary, and nondefault

**Tier:** B (Base contract boundary)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability, supply-chain  
**Patterns:** Broker→Lease→Receipt, Quarantine→Promote  

`docs/654-workstation-sanitized-inspection-derivatives-stay-inspection-shaped-and-disposable-first.md` already fixed the first post-sanitization trust boundary:
sanitizer success does not silently promote a foreign-derived artifact into ordinary trusted/local persistent-viewer handling.

But one smaller implementation cliff still remained:
**if the sanitizer can optionally reconstruct a searchable/OCR-backed PDF, is that OCR/text-layer output the ordinary default sanitized artifact, or is it a separate explicit derivative with its own evidence and posture?**

This doc makes the next small cut:
**the ordinary sanitized inspection default stays a flat visual derivative; OCR/searchable reconstruction is an explicit secondary derivative, remains inspection-shaped/disposable-first, and does not silently replace the flat sanitized baseline.**

See also:
- ADR: `adrs/ADR-0245-workstation-ocr-searchable-sanitized-derivatives-stay-explicit-secondary-and-nondefault.md`
- sanitization portal: `docs/267-sanitization-portal-and-disposable-sandboxes.md`
- sanitized-derivative boundary: `docs/654-workstation-sanitized-inspection-derivatives-stay-inspection-shaped-and-disposable-first.md`
- anti-laundering boundary: `docs/484-origin-label-authority-and-anti-laundering-boundary.md`
- working-copy lane: `docs/607-workstation-working-copy-receipts-and-edit-route-joins.md`
- schemas/examples: `spec/content.ocr-inspection.plan.schema.json`, `spec/content.ocr-inspection.receipt.schema.json`, `spec/examples/content.ocr-inspection.plan.json`, `spec/examples/content.ocr-inspection.receipt.json`

## Why this needs a hard decision

The render-to-pixels pattern is attractive precisely because it collapses risky active content into a more inspectable visual artifact.
But optional OCR/searchable reconstruction changes two things at once:

- it reintroduces inferred text/semantic structure that did not exist in the flat visual derivative
- and in real systems it can expand where and how more code runs during reconstruction

That does **not** mean OCR is forbidden.
It means the archive should not quietly treat “searchable sanitized PDF” as the same default object as the flat inspection derivative.
If we do, operators lose the ability to answer simple support/forensics questions like:

- was this the plain visual sanitized artifact or a later searchable derivative?
- did policy request OCR explicitly or did some convenience default enable it?
- which derivative was actually viewed, exported, or handed to a human reviewer?

Qubes + Dangerzone again point to the boring answer: safer inspection and richer convenience are separate choices.
DeriveBSD should keep the same split.

## Decision

For sanitization flows that can optionally emit searchable/OCR-backed derivatives:

- the ordinary sanitized inspection default stays a **flat visual derivative**
- searchable/OCR output is an **explicit secondary derivative**, not the implicit default result
- that OCR/searchable derivative still stays **inspection-shaped** and **disposable-first** by default
- OCR/searchable output does **not** silently replace or supersede the flat sanitized derivative in ordinary route/default handling
- the archive does **not** yet treat OCR/searchable derivatives as ordinary editable/trusted-local working-copy sources by default
- any later authoring/promotion/finalization rule for OCR/searchable derivatives remains a separate future boundary

## Practical model

### 1) Keep the flat sanitized derivative as the boring baseline

When a foreign document is sanitized for inspection, the first ordinary result should remain the explainable visual copy.
That gives the archive one stable answer for the baseline inspection artifact and keeps ordinary policy legible.

### 2) OCR/searchable reconstruction is a second explicit act

If a user or policy wants searchable text:

- request it explicitly
- emit a separate typed receipt
- preserve the join back to the same import lineage and sanitized source digest
- keep the derivative class explicit (`ocr-inspection-derivative`)

That keeps OCR from disappearing into generic “safe PDF” folklore.

### 3) Viewing posture still stays disposable-first

The OCR/searchable derivative may be more convenient to search or quote from, but it is still derived from foreign imported content. `docs/657-workstation-ocr-text-egress-stays-explicit-plain-text-single-delivery.md` now fixes the next quote/copy boundary too: when text leaves that lane, the boring baseline remains explicit plain-text single-delivery transfer rather than ambient clipboard/export folklore.
So the ordinary `document_viewing` posture remains disposable-first rather than silently reopening persistent-viewer trust. `docs/656-workstation-ocr-searchable-sanitized-derivatives-stay-out-of-ambient-host-indexes-by-default.md` now fixes the next persistence leak as well: searchable inspection may remain searchable inside that disposable lane, but the derivative does not silently become ambient host/global indexing input.

### 4) Editing remains intentionally out of baseline

The existing typed authoring lane currently names `imported-foreign-original` and `sanitized-inspection-derivative` as the official source classes.
This doc keeps that small on purpose: the archive does **not** yet widen the baseline working-copy source set to include OCR/searchable derivatives.
If later experience shows that explicit OCR-backed authoring is worth standardizing, that should be another deliberate cut.

## Why this is the smallest useful cut

This is not a broad “OCR policy framework.”
It is just enough structure to prevent one likely convenience drift:
turning optional searchable reconstruction into the de facto default sanitized artifact and quietly muddying provenance, attack-surface discussion, and support evidence.

The archive already had most of the ingredients:

- import-first provenance
- disposable inspection
- sanitized derivatives staying inspection-shaped
- explicit working-copy authoring

The missing move was simply to keep OCR/searchable reconstruction **secondary and typed** instead of letting it merge invisibly with the flat sanitized baseline.

## Related docs

- `docs/267-sanitization-portal-and-disposable-sandboxes.md`
- `docs/410-desktop-viability-checklist.md`
- `docs/457-workstation-host-ui-and-appvm-boundary.md`
- `docs/484-origin-label-authority-and-anti-laundering-boundary.md`
- `docs/607-workstation-working-copy-receipts-and-edit-route-joins.md`
- `docs/654-workstation-sanitized-inspection-derivatives-stay-inspection-shaped-and-disposable-first.md`
- `docs/656-workstation-ocr-searchable-sanitized-derivatives-stay-out-of-ambient-host-indexes-by-default.md`
- `spec/content.ocr-inspection.plan.schema.json`
- `spec/content.ocr-inspection.receipt.schema.json`
- `spec/examples/content.ocr-inspection.plan.json`
- `spec/examples/content.ocr-inspection.receipt.json`

Last updated: 2026-03-22r386
