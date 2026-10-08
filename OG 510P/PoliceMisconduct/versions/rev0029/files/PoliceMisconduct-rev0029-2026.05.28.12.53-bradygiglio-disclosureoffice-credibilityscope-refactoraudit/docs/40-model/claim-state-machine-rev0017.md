# Claim state machine — rev0017

The lifecycle state machine separates four ideas that earlier revisions repeatedly defended in local ledgers:

1. Source custody: where the record came from and whether it has been preserved.
2. Extraction permission: whether content can be summarized, named-entity scanned, or atomized.
3. Claim review: whether an extracted atom can support a private corpus claim.
4. Display review: whether anything can be shown publicly, to whom, and with what correction path.

The high-risk transitions are deliberately receipt-based. In particular, nothing may jump directly from source row, document label, URL target, payload envelope, official news item, motion, settlement, or name-only candidate into a public claim.

This state machine does not replace existing ledgers. It is an overlay that lets future sessions ask: what lifecycle state am I touching, and what would be required to move it?
