# Cooperation benchmark programs should ship a canonical delta receipt for claim-ready compact cards

Once the archive already has a machine-checkable compact card, a scaffold path, a canonical renderer, a claim-readiness lint, and a freeze receipt, one small operational gap still remains: there is still no **single compact object** that says what changed between two retained claim-ready cards and whether the change touched the claim surface or only the surrounding metadata.

That matters because future inheritors often need to answer a narrow question rather than reopen both cards line by line:
**did the evaluated subject, lane contract, metric, or benchmark claim actually change, or did only the notes / label / card id change?**

So the benchmark program should ship one tiny **delta receipt** whenever it compares two claim-ready compact cards.

The compare step should do five things together:

1. re-run schema validation on both cards;
2. re-run the claim-readiness lint on both cards;
3. record the old/new card paths and hashes;
4. emit one deterministic list of changed dotted field paths;
5. classify those path changes into **claim-surface** changes versus **metadata-only** changes.

Why this belongs in the archive:

- `RS-GR-117` says research artefacts benefit from lightweight machine-readable packaging and explicit relations between files, which supports emitting one small structured delta object instead of relying on inheritor memory.
- `RS-GR-119` says an audit trail should let reviewers reconstruct what changed and when, which supports retaining one canonical card-to-card change receipt rather than informal prose about updates.
- `RS-GR-120` says transparency indicators give credit to documentation with update history and versioned releases, which supports keeping card updates legible as first-class retained artefacts rather than as silent overwrites.
- `RS-GR-121` says lifecycle transparency becomes more auditable when governance signals move into machine-checkable contracts, which supports classifying claim-surface changes explicitly instead of burying them in free text.

Keep the delta receipt compact:

- retain only the old/new card identifiers, paths, and hashes;
- list changed field paths rather than copying full field payloads;
- classify the changed paths so inheritors can quickly see whether the benchmark claim moved or only the surrounding metadata moved;
- let the two cards remain the semantic objects and use the receipt as the tiny audit handle between them.

This gives the archive one more important protection without widening it much: once two claim-ready cards both exist, the archive can answer **what changed** in one machine-checkable place instead of forcing every future inheritor to reconstruct the delta by hand.
