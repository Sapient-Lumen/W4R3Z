# Retry fence restart memory

`retryfence.py` turns a retry/withdraw-ready join into signed, previous-linked local memory.

A retry fence marker binds:

```text
profile/service/scope/request/payload
original idempotency key
retry idempotency key
ack-repair join digest
live-egress digest
delivery-repair digest
rollback-probe digest
sequence / previous digest
family / path family
```

Terminal ACK paths do not become retry permission. They produce a terminal hold instead.

The riskiest failure avoided here is a restart or retry scheduler treating "repair path accepted" as a reusable send token without carrying the exact evidence chain.
