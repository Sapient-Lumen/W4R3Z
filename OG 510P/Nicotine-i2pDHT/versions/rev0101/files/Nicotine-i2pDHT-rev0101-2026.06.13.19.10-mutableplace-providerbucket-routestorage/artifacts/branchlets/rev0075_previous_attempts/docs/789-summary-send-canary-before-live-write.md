# rev0075 — Summary send canary before live write

The summary send canary is a no-network boundary before any future redacted public-summary write. It joins outbox settlement, publish fence, public ledger, and redaction GC evidence. The summary send canary is not a live send and does not claim SAM/I2P transport readiness.

Risk-first rules:

- raw boundary and raw payload material are quarantined;
- contradiction memory must be carried by every marker;
- public-ledger and redaction-GC digests must remain bound to the outbox settlement;
- a canary-ready report is still only local permission for a later live-send boundary.

Audit needles: summarysendcanary, summary send canary, outboxsettlement, publicledger, redactiongc, summarysendfold.
