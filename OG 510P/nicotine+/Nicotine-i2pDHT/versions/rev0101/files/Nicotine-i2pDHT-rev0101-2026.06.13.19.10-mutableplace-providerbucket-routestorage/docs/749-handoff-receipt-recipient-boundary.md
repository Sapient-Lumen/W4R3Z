# Handoff receipt recipient boundary

`handoffreceipt.py` treats a prepared closure handoff as only an outbound observation. A recipient still needs scoped receipt memory.

Risk checks now include:

```text
pending closure handoff
missing required audience
import refusal as watch pressure
raw boundary / payload leakage
component digest drift
boundary drift
sequence rollback
same-sequence fork
previous-link mismatch
contradiction memory drop
hard-negative pressure
low family/path diversity
```

The important design guess is that recipient acknowledgement is useful but not authoritative. A garden or operator can say it saw a redacted handoff; that does not become DHT truth, import permission, publication permission, or global reputation.


Audit needle: handoff receipt.
