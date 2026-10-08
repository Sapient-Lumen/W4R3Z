# Ack archive restart memory

`ackarchive.py` keeps settled delivery evidence sticky across restart.

It tests the danger that a delivered send could be forgotten, rebound to another idempotency payload, or archived under a sequence fork.

The archive lane rejects:

```text
unaccepted settlement
replay
sequence rollback
same-sequence fork
previous-link mismatch
boundary drift
idempotency conflict
hard-negative pressure
low family/path diversity
```

The archive is still local memory, not network truth.

Needle: ack archive.
