# ADR-0246: Workstation OCR/searchable sanitized derivatives stay out of ambient host indexes by default

Date: 2026-03-22
Status: Accepted

## Context

`adrs/ADR-0245-workstation-ocr-searchable-sanitized-derivatives-stay-explicit-secondary-and-nondefault.md` already fixed the first OCR/searchability boundary:

- the flat visual sanitized derivative remains the boring default
- OCR/searchable reconstruction is explicit and secondary
- OCR/searchable derivatives remain inspection-shaped and disposable-first
- OCR/searchable derivatives are not baseline working-copy sources yet

That still leaves one practical ambiguity:
**once an OCR/searchable derivative exists, may the host quietly index it into ambient/global search surfaces or emit detached extracted-text artifacts by default?**

Real systems help motivate the split:
- Qubes keeps risky document handling on disposable/open-in-VM lanes
- Dangerzone treats OCR as an optional follow-on to the safer visual reconstruction path

Those lessons point to a smaller implementation rule too:
local search inside the inspection lane is one thing, but ambient host indexing is a different trust/privacy/export act.

## Decision

1. **Local search may stay inside the inspection lane.**
   - Search/find inside the disposable viewer is compatible with the inspection posture.
   - Searchability does not have to mean host-global persistence.

2. **Ambient host/global indexing is forbidden by default.**
   - Merely creating an OCR/searchable derivative does not auto-enroll it into host-global search/index services.
   - A searchable inspection artifact remains bounded to the inspection lane unless a later explicit act says otherwise.

3. **Detached text sidecars are not emitted by default.**
   - The archive does not silently mint `.txt` or equivalent extracted-text companions for OCR/searchable inspection artifacts.
   - More copyable detached text remains a separate future boundary.

4. **Future text-export/indexing lanes remain explicit future work.**
   - This ADR does not standardize a generic full-text search subsystem.
   - It only prevents convenience drift from turning searchable inspection into ambient corpus state.

## Consequences

### What this locks now

- OCR/searchable inspection remains useful for bounded in-view search.
- The host does not quietly accumulate foreign-derived text into ambient indexes by default.
- Support/export/forensics can still distinguish searchable inspection from explicit later indexing/export.
- The query/index substrate stays metadata-first rather than silently expanding into body-text capture.

### What stays intentionally open

This ADR does **not** decide:

- a generic body-text indexing service
- explicit quote/excerpt export workflows
- whether some future trusted/local or finalized artifacts may enroll in broader search surfaces
- OCR model/language-pack distribution or broader viewer UX

## Why this is the smallest viable cut

The archive already paid for the hard part: searchable OCR is explicit, secondary, and still disposable-first.
The missing move was simply to stop that convenience from quietly turning into ambient host search/index persistence.
That keeps the workstation story coherent without inventing a new subsystem.

## Wiring

- OCR/searchable derivative boundary: `docs/655-workstation-ocr-searchable-sanitized-derivatives-stay-explicit-secondary-and-nondefault.md`
- new ambient-indexing boundary doc: `docs/656-workstation-ocr-searchable-sanitized-derivatives-stay-out-of-ambient-host-indexes-by-default.md`
- sanitization portal: `docs/267-sanitization-portal-and-disposable-sandboxes.md`
- query/index substrate: `docs/293-attribute-indexed-metadata-and-live-queries.md`
- anti-laundering boundary: `docs/484-origin-label-authority-and-anti-laundering-boundary.md`
- typed examples: `spec/content.ocr-inspection.plan.schema.json`, `spec/content.ocr-inspection.receipt.schema.json`
