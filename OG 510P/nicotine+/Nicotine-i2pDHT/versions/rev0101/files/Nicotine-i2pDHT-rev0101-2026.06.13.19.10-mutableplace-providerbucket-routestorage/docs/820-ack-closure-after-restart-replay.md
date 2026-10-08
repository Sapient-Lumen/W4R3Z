# ACK closure after restart replay

`ackclosure.py` closes the local redacted-summary ACK path only after these component reports agree:

```text
summaryackledger
deliveryarchive
summaryprunefence
summaryreplay
```

ACK closure is intentionally later than ACK settlement. Settlement says the ACK path was plausible; closure says enough restart-safe evidence has survived to treat the local path as terminal for subsequent export-fence work.

The closure rejects replay, digest drift, boundary drift, sequence rollback/fork, previous-link mismatch, hard-negative pressure, redaction drops, and contradiction drops.
