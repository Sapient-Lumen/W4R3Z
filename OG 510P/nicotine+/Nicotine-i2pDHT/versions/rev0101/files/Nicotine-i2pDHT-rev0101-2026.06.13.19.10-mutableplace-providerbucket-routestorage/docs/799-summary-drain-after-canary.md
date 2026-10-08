# Summary drain after canary

`summarydrain.py` adds a no-network drain marker after the rev0075 summary-send canary.

The drain lane binds:

```text
summary send canary digest
outbox settlement digest
publish fence digest
public ledger digest
redaction GC digest
accepted marker digests
Destination digest
SAM endpoint digest
redacted summary digest
idempotency key
redaction / contradiction memory
```

The drain accepts only when required marker classes are present, sequence links are monotonic, family/path diversity is sufficient, no raw boundary or payload material leaks, and no hard-negative pressure is present.

It explicitly rejects endpoint drift, digest drift, raw leaks, replay, rollback, sequence forks, previous-link mismatch, and contradiction drops.

summary drain
