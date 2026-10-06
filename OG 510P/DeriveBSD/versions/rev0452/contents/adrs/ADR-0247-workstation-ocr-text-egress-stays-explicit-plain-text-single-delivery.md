# ADR-0247: Workstation OCR-derived text egress stays explicit, plain-text, and single-delivery by default

Date: 2026-03-22
Status: Accepted

## Context

`adrs/ADR-0245-workstation-ocr-searchable-sanitized-derivatives-stay-explicit-secondary-and-nondefault.md` already fixed the first OCR/searchability boundary:

- the flat visual sanitized derivative remains the boring default
- OCR/searchable reconstruction is explicit and secondary
- OCR/searchable derivatives remain inspection-shaped and disposable-first
- OCR/searchable derivatives are not baseline working-copy sources yet

`adrs/ADR-0246-workstation-ocr-searchable-sanitized-derivatives-stay-out-of-ambient-host-indexes-by-default.md` then fixed the next persistence boundary:

- local search may stay inside the inspection lane
- ambient host/global indexing is forbidden by default
- detached text sidecars are not emitted by default

That still leaves one practical ambiguity:
**when a user copies OCR-derived text out of a searchable inspection artifact, is that copy path just ambient clipboard convenience, or is it still an explicit cross-domain transfer act with a boring baseline payload and evidence join?**

Qubes’ inter-qube clipboard keeps transfer explicit, plain-text-focused, and clears the inter-qube clipboard after delivery, while its security docs also warn that copy from less-trusted to more-trusted domains remains a real transfer risk. That is the right shape here too.

## Decision

1. **OCR-derived text egress stays on the existing explicit data-transfer lane.**
   - Copying text out of `ocr-inspection-derivative` artifacts does not silently create an ambient shared clipboard path.
   - The ordinary lane remains `ui.datatransfer` with visible brokered transfer semantics.

2. **Plain text is the boring baseline payload.**
   - The default transfer MIME is `text/plain;charset=utf-8`.
   - Rich HTML/RTF excerpt transfer is not baseline by default.

3. **Single-delivery remains the ordinary posture.**
   - OCR-derived text transfer inherits the workstation baseline `delivery_mode = single-delivery` unless a future exception lane exists.
   - “Copied once” should not quietly become compartment-spanning clipboard history.

4. **Transfers may preserve OCR source lineage.**
   - When the broker knows the payload came from an OCR inspection derivative, the typed grant/receipt may preserve the source artifact join (`artifact_kind`, `artifact_digest`, `source_class`, and related digests).
   - Copied OCR text should not become provenance-free host folklore.

5. **Detached text/export authoring remains future work.**
   - This ADR does not standardize detached `.txt` exports, rich excerpt packages, or an OCR-derived working-copy lane.
   - It only keeps the ordinary copy path from silently becoming one of those things.

## Consequences

### What this locks now

- Searchable inspection remains useful for bounded copy/quote workflows.
- OCR-derived text transfer stays explicit rather than ambient.
- The default payload stays the smallest practical one: plain text.
- Support/export/forensics can keep copied OCR text joined back to the inspection artifact that produced it.

### What stays intentionally open

This ADR does **not** decide:

- detached extracted-text files as a first-class export lane
- rich-text/HTML excerpt packages
- OCR-derived authoring or working-copy promotion
- policy for broader multi-delivery clipboard/history exceptions

## Why this is the smallest viable cut

The archive already paid for the expensive parts: OCR is explicit, secondary, disposable-first, and not ambiently indexed.
The missing move was simply to keep OCR-derived text egress from bypassing the already-accepted explicit transfer floor.
That keeps the workstation story coherent without inventing another subsystem.

## Wiring

- new boundary doc: `docs/657-workstation-ocr-text-egress-stays-explicit-plain-text-single-delivery.md`
- data-transfer floor: `docs/538-workstation-cross-domain-datatransfer-floor.md`
- data-transfer portal: `docs/205-data-transfer-portals-clipboard-and-dnd.md`
- OCR/searchable boundaries: `docs/655-workstation-ocr-searchable-sanitized-derivatives-stay-explicit-secondary-and-nondefault.md`, `docs/656-workstation-ocr-searchable-sanitized-derivatives-stay-out-of-ambient-host-indexes-by-default.md`
- anti-laundering boundary: `docs/484-origin-label-authority-and-anti-laundering-boundary.md`
- typed schemas/examples: `spec/content.ocr-inspection.plan.schema.json`, `spec/content.ocr-inspection.receipt.schema.json`, `spec/ui.datatransfer.grant.schema.json`, `spec/ui.datatransfer.receipt.schema.json`, `spec/examples/ui.datatransfer.grant.ocr-inspection-text.json`, `spec/examples/ui.datatransfer.receipt.ocr-inspection-text.json`
