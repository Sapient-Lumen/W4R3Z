# Cooperation benchmark programs should ship a freeze receipt for claim-ready compact cards

Once the archive already has a machine-checkable compact card, a scaffold path, a canonical renderer, and a claim-readiness lint, one small operational gap remains: there is still no **single compact receipt** that binds the exact claim-ready JSON card to the exact canonical rendered view that future inheritors read.

That matters because a card can drift after review, a rendered markdown summary can go stale, or a future session can cite the human-readable view without an equally compact proof of which structured object generated it.

So the benchmark program should ship one tiny **freeze receipt** for every claim-ready compact card it intends to retain or cite.

The freeze step should do four things together:

1. re-run schema validation on the JSON card;
2. re-run the claim-readiness lint;
3. regenerate the canonical markdown render;
4. emit one compact receipt carrying stable paths plus hashes for the card, the rendered view, the governing schema, and the local freeze tool.

Why this belongs in the archive:

- `RS-GR-111` says benchmark documentation should follow a standardized structure, which supports turning the final card state into one citeable publication object rather than leaving provenance split across ad hoc files.
- `RS-GR-114` says machine-actionable metadata should stay easy for software systems to reuse, which points toward a tiny deterministic freeze receipt rather than manual inheritor bookkeeping.
- `RS-GR-117` says research artefacts benefit from lightweight packaging with machine-readable metadata and explicit relations between the constituent files, which supports binding the card and its derivative human-readable view together.
- `RS-GR-118` says checksum manifests are useful for detecting stale or damaged transferred payloads, which supports carrying compact card / render / schema / tool hashes inside a freeze receipt.

Keep the freeze receipt compact:

- include only the minimum identifying fields plus the relevant hashes;
- treat the rendered markdown as derivative rather than primary;
- let the JSON card remain the publication object that carries the semantic fields;
- use the receipt as the small provenance handle future inheritors can diff, cite, or audit.

This gives the archive one more important protection without widening it much: a claim-ready card is no longer just valid and reviewed, it is also **frozen to a specific rendered view and specific local toolchain state**.
