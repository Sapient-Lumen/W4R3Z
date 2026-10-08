# ADR 0169: Retry escrow carries dead-letter memory

Status: accepted in rev0058.

Retry attempts must carry the dead-letter digest that caused them. This prevents retry from erasing unresolved effect history.

Decision: retry escrow tickets bind reconcile, retry quorum, dead-letter, idempotency key, attempt, sequence, and family/path evidence.
