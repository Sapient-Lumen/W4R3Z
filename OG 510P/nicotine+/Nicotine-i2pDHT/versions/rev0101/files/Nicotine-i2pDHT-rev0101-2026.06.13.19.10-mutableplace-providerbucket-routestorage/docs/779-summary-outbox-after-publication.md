# Summary outbox after publication

`summaryoutbox.py` stages redacted summary work into a no-network local outbox after summary publication, redaction witness, and import-prune audit reports agree.

It checks:

- exact profile/service/scope/request/payload/idempotency boundary
- component digest binding
- accepted intent / redaction receipt / import-prune marker binding
- raw boundary and raw payload leak rejection
- contradiction memory carry
- previous-link sequencing
- replay, rollback, and fork pressure
- family and path diversity

The outbox is not a send.  It is only local staging evidence.

summary outbox lower-case audit needle.
