# Settlement fence after delivery

`settlementfence.py` joins summary send canary, summary drain, summary delivery witness, and redaction GC before a future redacted-summary write can be treated as settled.

The fence requires:

```text
send canary ready
summary drain ready
delivery ACK accepted
redaction GC retained
redaction memory carried
contradiction memory carried
exact profile/service/scope/request/payload/idempotency boundary
family and path diversity
```

A delivery witness that is watchful because of missing ACK, useful refusal, NACK, or payload mismatch does not satisfy the fence. The fence exists to make that refusal boring and explicit.

settlement fence
