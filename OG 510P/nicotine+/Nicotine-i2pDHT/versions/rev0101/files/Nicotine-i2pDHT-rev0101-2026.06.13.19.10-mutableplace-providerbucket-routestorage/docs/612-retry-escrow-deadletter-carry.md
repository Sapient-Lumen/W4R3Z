# Retry escrow and dead-letter carry

Retry is not a rerun button. `retryescrow.py` requires a retry ticket to bind:

```text
reconcile digest
retry quorum digest
dead-letter digest
carried dead-letter digest
idempotency key
exact scope/request/payload
attempt number
sequence + previous ticket
family/path diversity
```

The carried dead-letter digest is the important part. A retry attempt must remember what unresolved effect caused it. That prevents retry from becoming cleanup by another name.
