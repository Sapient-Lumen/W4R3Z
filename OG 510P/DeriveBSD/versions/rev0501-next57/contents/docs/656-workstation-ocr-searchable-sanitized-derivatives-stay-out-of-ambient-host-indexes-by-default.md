# Workstation OCR/searchable sanitized derivatives stay out of ambient host indexes by default

**Tier:** B (Base contract boundary)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability, supply-chain  
**Patterns:** Broker→Lease→Receipt, Quarantine→Promote

`docs/655-workstation-ocr-searchable-sanitized-derivatives-stay-explicit-secondary-and-nondefault.md` already fixed the first OCR/searchability boundary:
OCR/searchable reconstruction is explicit, secondary, and still inspection-shaped/disposable-first by default.

One smaller but important ambiguity remained:
**once that OCR/searchable derivative exists, may the host quietly enroll it in ambient/global search indexes or emit detached text sidecars by default, or does searchability stay local to the inspection lane until some later explicit act exists?**

This doc makes the next small cut:
**local search inside the disposable inspection lane may remain available, but OCR/searchable sanitized derivatives stay out of ambient host/global indexes by default, and detached text sidecars are not emitted implicitly.**

See also:
- ADR: `adrs/ADR-0246-workstation-ocr-searchable-sanitized-derivatives-stay-out-of-ambient-host-indexes-by-default.md`
- sanitization portal: `docs/267-sanitization-portal-and-disposable-sandboxes.md`
- OCR/searchable derivative boundary: `docs/655-workstation-ocr-searchable-sanitized-derivatives-stay-explicit-secondary-and-nondefault.md`
- query/index substrate: `docs/293-attribute-indexed-metadata-and-live-queries.md`
- anti-laundering boundary: `docs/484-origin-label-authority-and-anti-laundering-boundary.md`
- schemas/examples: `spec/content.ocr-inspection.plan.schema.json`, `spec/content.ocr-inspection.receipt.schema.json`, `spec/examples/content.ocr-inspection.plan.json`, `spec/examples/content.ocr-inspection.receipt.json`

## Why this needs a hard decision

Once OCR/searchable reconstruction exists, convenience pressure shifts from “should OCR exist?” to “should it just show up everywhere search already works?”
That sounds harmless, but ambient indexing changes the posture again:

- text from foreign-derived content can become long-lived host search state
- detached text caches or sidecars can outlive the disposable inspection lane
- support/export tooling can lose the ability to distinguish “user searched inside the disposable viewer” from “the host enrolled this foreign-derived text into an ambient corpus”

That is a different trust and privacy question than merely allowing Ctrl-F inside a disposable viewer.
If the archive leaves it blurry, implementations will quietly let searchable inspection drift into ambient corpus-building.
That would undercut the disposable-first story precisely where the archive just paid to make it coherent.

## Decision

For OCR/searchable sanitized inspection derivatives:

- **local viewer search may remain available** inside the disposable inspection lane
- **ambient host/global indexing is forbidden by default**
- **detached text sidecars are not emitted by default**
- the existence of an OCR/searchable derivative does **not** by itself enroll that derivative into any host-global search corpus or metadata index
- any later text-export, indexing, promotion, or authoring lane remains a **separate future boundary**

## Practical model

### 1) Searchability is allowed to stay local to the inspection lane

The point of OCR/searchable reconstruction is that a human may need to find a term or quote within the inspection artifact.
That is compatible with the disposable-first posture as long as the search stays bounded to the same inspection environment.

### 2) Ambient host indexing is a different act

A host-global index is not just a viewer convenience.
It is a persistent derived corpus with its own privacy, provenance, and export consequences.
So the archive should not treat “searchable PDF exists” as permission to auto-enroll that derivative in ambient search services.

### 3) Detached text should not appear by default

A searchable layer inside the PDF is already one derived representation.
Automatically emitting a parallel `.txt` sidecar or similar detached extraction would create another more copyable/searchable artifact without an explicit decision. `docs/657-workstation-ocr-text-egress-stays-explicit-plain-text-single-delivery.md` now fixes the next narrower convenience drift too: when text does leave the searchable inspection lane, the boring baseline is still an explicit plain-text single-delivery data-transfer act rather than ambient clipboard/export state.
That should stay off by default until a later explicit act says otherwise.

### 4) Query/index work stays metadata-first

`docs/293-attribute-indexed-metadata-and-live-queries.md` already keeps the baseline query substrate on blessed metadata classes rather than arbitrary body text.
This doc narrows the workstation follow-on: OCR/searchable text from foreign-derived inspection artifacts is not baseline ambient index fodder just because it exists.

## Why this is the smallest useful cut

This is not a full-text search subsystem design.
It just prevents one likely convenience regression:
letting explicit searchable inspection quietly become ambient long-lived host corpus state.

That small distinction preserves:

- disposable-first inspection
- anti-laundering provenance discipline
- clearer support/export answers
- room for a later explicit text-export or indexing act if it proves worthwhile

## Related docs

- `docs/267-sanitization-portal-and-disposable-sandboxes.md`
- `docs/293-attribute-indexed-metadata-and-live-queries.md`
- `docs/410-desktop-viability-checklist.md`
- `docs/457-workstation-host-ui-and-appvm-boundary.md`
- `docs/484-origin-label-authority-and-anti-laundering-boundary.md`
- `docs/655-workstation-ocr-searchable-sanitized-derivatives-stay-explicit-secondary-and-nondefault.md`
- `spec/content.ocr-inspection.plan.schema.json`
- `spec/content.ocr-inspection.receipt.schema.json`
- `spec/examples/content.ocr-inspection.plan.json`
- `spec/examples/content.ocr-inspection.receipt.json`

Last updated: 2026-03-22r387
