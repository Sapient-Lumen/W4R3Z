# Risk register rev0071

Open risks:

```text
Recipient receipts may be treated as authority instead of local evidence.
Import markers may accidentally widen scope or leak raw boundary material.
Summary lineage can become public metadata if not redacted aggressively.
Contradiction memory can be dropped during handoff/import/summary transitions.
Family/path diversity remains a lab hint, not a solved independence oracle.
```

Local mitigations added:

```text
exact-boundary joins
previous-linked receipt/import/summary entries
raw leak flags
component digest binding
contradiction-carriage checks
hard-negative pressure checks
fold/audit visibility
```
