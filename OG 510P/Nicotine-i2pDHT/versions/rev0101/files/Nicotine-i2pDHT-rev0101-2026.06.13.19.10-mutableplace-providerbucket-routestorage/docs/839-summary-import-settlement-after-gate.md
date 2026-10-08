# Summary import settlement after gate

Summary import settlement is the first local marker that says a redacted summary import became terminal local state.

Inputs:

```text
summary_export_receipt_report
summary_import_gate_report
export_retention_audit_report
settlement marker chain
```

The lane rejects:

```text
receipt pending
import gate pending
retention audit pending
import not ready
boundary drift
digest drift
raw boundary or payload leaks
redaction drops
contradiction drops
hard-negative pressure
replay / rollback / sequence fork / previous-link mismatch
low family or path diversity
```

It accepts only when the receipt, import gate, retention audit, and settlement marker chain all bind to the same action/profile/service/scope/request/payload/idempotency boundary.
