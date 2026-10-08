# Interoperability plan

The cube should remain simple now but exportable later.

## Do not over-adopt yet

Do not convert the working poem corpus to TEI, RO-Crate, DataCite, C2PA, or WACZ wholesale before the first poem exists. The current cube borrows patterns, not full compliance burdens.

## Keep future export possible

Maintain enough line/stanza metadata that a later poem can export to TEI-style verse structures. TEI P5 verse guidance distinguishes verse lines and line groups such as stanzas; this is useful for poem export and formal verification.

Maintain enough selector metadata that source and quote receipts can later map to Web Annotation-style TextQuoteSelector/TextPositionSelector patterns.

Maintain enough machine-readable metadata, stable identifiers, and qualified references to remain compatible with FAIR-inspired archive practice.

## Near-term practice

- Keep Markdown as the authoring format.
- Store poem metadata in JSON.
- Record line counts, stanza breaks, form IDs, source IDs, and verification receipts.
- Add richer export only after at least one poem shows what the export must preserve.
