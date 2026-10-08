# Export receipt restart memory

`exportreceipt.py` records signed-ish toy receipts for redacted audit export bundles.  A receipt carries the same action/profile/service/scope/request/payload/idempotency boundary as the export report, plus the accepted export bundle digest, closure-seal digest, retention-proof digest, redacted receipt digest, family/path hints, and contradiction carriage.

The lane rejects raw boundary or raw payload leakage, replay, same-sequence forks, previous-link mismatch, component-digest drift, low diversity, and dropped contradiction memory.  A receipt is not global truth; it is local evidence that the redacted export crossed a local review boundary.

Needle: export receipt.
