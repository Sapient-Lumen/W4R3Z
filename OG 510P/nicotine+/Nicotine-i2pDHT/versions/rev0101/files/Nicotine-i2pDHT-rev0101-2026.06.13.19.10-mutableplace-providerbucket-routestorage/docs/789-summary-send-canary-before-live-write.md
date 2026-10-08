# Summary send canary before live write

`summarysendcanary.py` models a no-network canary after outbox settlement. It is not a live send.

The canary binds outboxsettlement, publish fence, publicledger, redactiongc, summarysettlement lineage, redacted-summary digest, and contradiction memory at one exact boundary.

Keywords: summary send canary, summarysendcanary, outboxsettlement, publicledger, redactiongc, summarysettlement.
