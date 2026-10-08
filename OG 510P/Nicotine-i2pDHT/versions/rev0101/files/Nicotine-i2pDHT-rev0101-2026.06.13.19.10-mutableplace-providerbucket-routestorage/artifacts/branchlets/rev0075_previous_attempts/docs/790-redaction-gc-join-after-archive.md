# rev0075 — Redaction GC join after archive

The folded redaction GC branch keeps redacted-summary memory, public-ledger memory, and contradiction memory tied to the same exact boundary. Redaction GC is treated as a pressure surface after archive/fence evidence, not as cleanup.

This document also records the sibling branchlet folded forward from rev0074: summarysettlement, publicledger, and redactiongc. Those surfaces are used by rev0075's outbox settlement and summary send canary tests.

Audit needles: redactiongc, redaction GC, summarysettlement, publicledger, outboxsettlement, summarysendcanary.
