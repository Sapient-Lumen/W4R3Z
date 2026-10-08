# Next revision pointer — rev0049

Suggested rev0050 direction:

```text
commitjournal-rollbackprobe-outboxdrain
```

Possible focus:

- join public outbox to restart journal/checkpoint lanes
- model drain/commit receipts without live networking
- add rollback probes for public records that outlive withdrawal
- compact audit-gap evidence without dropping negative witnesses
- continue fold registry consolidation
