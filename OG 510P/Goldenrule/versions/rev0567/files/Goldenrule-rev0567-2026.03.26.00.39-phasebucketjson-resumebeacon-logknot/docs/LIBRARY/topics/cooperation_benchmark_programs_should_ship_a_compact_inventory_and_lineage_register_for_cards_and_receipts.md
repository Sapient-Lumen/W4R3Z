# Cooperation benchmark programs should ship a compact inventory and lineage register for cards and receipts

Once the archive already has a schema-backed cooperation card, a scaffold path, a canonical renderer, a readiness lint, a freeze receipt, and a delta receipt, one further operational gap remains: future inheritors still need one place to answer **which compact cards exist, which are claim-ready, which are latest, and which receipts bind or update them**.

Keep that answer in one tiny generated register rather than in memory or in scattered prose.

## What to retain

For every retained cooperation card family, publish one compact inventory that records:

1. each schema-valid card id and path;
2. whether the card is claim-ready under the standing lint;
3. whether the card has at least one freeze receipt;
4. predecessor / successor links implied by retained delta receipts;
5. the latest-known claim-ready card ids; and
6. any orphan receipts that no longer resolve to retained cards.

## Why this matters

Freeze receipts bind one claim-ready card to one rendered review surface.
Delta receipts say what changed between two claim-ready cards.
But once the archive accumulates multiple cards and receipts, inheritors still need a compact **searchable register** over those objects.
Otherwise even a disciplined compact-card program drifts back toward manual archaeology: “which card was latest?”, “was this one frozen?”, “does this receipt still point at a retained card?”, and “did this branch have a successor?”

A generated inventory is the smallest durable fix because it reuses the standing card, lint, freeze, and delta artifacts instead of widening them.
