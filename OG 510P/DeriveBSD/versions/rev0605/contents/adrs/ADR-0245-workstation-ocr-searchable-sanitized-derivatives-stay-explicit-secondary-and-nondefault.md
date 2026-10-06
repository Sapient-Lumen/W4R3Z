# ADR-0245: Workstation OCR/searchable sanitized derivatives stay explicit, secondary, and nondefault

Date: 2026-03-22
Status: Accepted

## Context

`adrs/ADR-0244-workstation-sanitized-inspection-derivatives-stay-inspection-shaped-and-disposable-first.md` already fixed the first post-sanitization trust boundary:

- sanitized inspection derivatives remain inspection-shaped by default
- ordinary viewing of sanitized inspection derivatives stays disposable-first
- and sanitizer success is not implicit trust-promotion

That still leaves one smaller but practical ambiguity:
**if the sanitization tool can optionally rebuild a searchable/OCR-backed PDF, is that searchable output the ordinary sanitized default, or is it a separate explicit derivative with its own posture and evidence?**

Real systems such as Dangerzone make this ambiguity concrete:

- the primary safety story is render-to-pixels and rebuild a flat readable result
- OCR is optional and creates a searchable text layer
- and the OCR path has been treated as additional attack-surface worth reviewing in its own right

If the archive leaves this blurry, implementations will quietly collapse the two outputs together and support tooling will lose the ability to answer whether a viewed/exported artifact was the plain visual derivative or a later OCR-backed one.

## Decision

1. **The ordinary sanitized inspection default remains the flat visual derivative.**
   - Flat visual sanitized output is the boring baseline inspection artifact.
   - Searchable/OCR-backed output is not implicitly assumed or auto-selected as the only official sanitized result.

2. **OCR/searchable reconstruction is an explicit secondary derivative.**
   - If policy or a user wants searchable text, that request should be explicit.
   - The resulting artifact should have its own typed receipt/evidence rather than disappearing into generic “sanitized PDF” prose.

3. **OCR/searchable derivatives remain inspection-shaped and disposable-first.**
   - They do not inherit ordinary persistent-viewer trust by default.
   - They do not silently replace the flat visual derivative in routing/default posture.

4. **OCR/searchable derivatives are not baseline working-copy sources yet.**
   - The official working-copy lane remains intentionally narrow.
   - If later experience justifies OCR-backed authoring as a first-class lane, that requires a separate explicit boundary.

## Consequences

### What this locks now

- The archive gets one stable default answer: sanitized inspection means flat visual by default.
- OCR/searchable convenience stays available as a typed second step rather than ambient policy drift.
- Support/export/forensics surfaces can distinguish the flat sanitized derivative from the OCR-backed derivative.
- The workstation story remains coherent: import → flat sanitized inspection → optional OCR inspection derivative → explicit future authoring/promotion boundary if ever needed.

### What stays intentionally open

This ADR does **not** decide:

- a broad OCR policy framework for every content class
- whether OCR/searchable derivatives should later support explicit working-copy issuance
- what a future promotion/finalization lane for searchable derivatives would look like
- language packs, OCR model distribution, or user-facing OCR UX details beyond the explicit/nondefault posture

## Why this is the smallest viable cut

The archive already had the bigger trust story.
The missing move was just to stop optional OCR/searchable reconstruction from silently becoming part of the default sanitized baseline.
That single distinction improves provenance, evidence quality, and implementation discipline without inventing a large new subsystem.

## Wiring

- portal/sanitization framing: `docs/267-sanitization-portal-and-disposable-sandboxes.md`
- sanitized-derivative trust boundary: `docs/654-workstation-sanitized-inspection-derivatives-stay-inspection-shaped-and-disposable-first.md`
- new OCR/searchable derivative boundary doc: `docs/655-workstation-ocr-searchable-sanitized-derivatives-stay-explicit-secondary-and-nondefault.md`
- anti-laundering boundary: `docs/484-origin-label-authority-and-anti-laundering-boundary.md`
- working-copy lane: `docs/607-workstation-working-copy-receipts-and-edit-route-joins.md`
- typed examples: `spec/content.ocr-inspection.plan.schema.json`, `spec/content.ocr-inspection.receipt.schema.json`
