# Ack prune join boundary

`ackprunejoin.py` is the compact join after settlement and archive.

It exists because cleanup is dangerous after public-edge writes.  A delivered-looking send must not cause important delivery, fence, or hard-negative evidence to disappear unless the settlement and archive agree at the same boundary.

It accepts prune only after:

```text
delivery settlement is accepted and terminal
ack archive is accepted
optional send fence and delivery witness agree
component digests bind
family/path diversity is sufficient
hard-negative count is zero
```

This keeps pruning from becoming evidence laundering.

Needle: ack prune join.
