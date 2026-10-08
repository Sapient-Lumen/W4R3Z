# Summary receipt after lineage

A redacted summary lineage is still only local evidence.  It is not recipient receipt.

`summaryreceipt.py` adds `SummaryReceiptEntry` and `SummaryReceiptReport`.  Entries bind the summary-lineage digest, accepted summary entry, handoff-import digest, handoff-receipt digest, closure-handoff digest, exact boundary, family/path hints, redaction state, contradiction memory, and optional refusal.

Receipt refusal is deliberately watchful:

```text
summary refused -> watch, not accept
summary ACKs from diverse families -> accepted receipt
```

The risky failures tested first are raw leak, same-sequence fork, replay, previous-link mismatch, digest drift, contradiction drop, hard-negative pressure, and low family/path diversity.

summary receipt audit needle.
