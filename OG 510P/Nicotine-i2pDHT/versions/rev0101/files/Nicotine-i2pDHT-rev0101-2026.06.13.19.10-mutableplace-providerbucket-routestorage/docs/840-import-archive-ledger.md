# Import archive ledger

Import archive ledger turns accepted summary import settlement into restart-sticky local memory.

It deliberately remains separate from import settlement. Settlement says the import is locally terminal. Archive says the terminal state survived into durable evidence with redaction and contradiction memory intact.

Required classes:

```text
import_settlement
retention_audit
import_gate
archive_state
redaction_memory
contradiction_memory
```

The archive ledger rejects raw leaks, digest drift, dropped contradiction memory, dropped redaction memory, hard negatives, and weak family/path diversity.
