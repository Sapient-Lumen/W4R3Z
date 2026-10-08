# Handoff import redacted state

`handoffimport.py` adds the import boundary after recipient receipt.

The required import marker classes are:

```text
handoff_receipt_marker
closure_handoff_marker
contradiction_memory
redacted_summary_memory
local_recipient_state
```

The import lane keeps the same exact action/profile/service/scope/request/payload/idempotency boundary as the receipt lane. It explicitly rejects raw leakage, component digest drift, sequence forks, previous-link mismatch, contradiction drops, and hard-negative pressure.

The design point is simple: importing redacted closure evidence is a state mutation. It should be previous-linked and restart-visible, not a side effect hidden behind an export handoff success.


Audit needle: handoff import.
