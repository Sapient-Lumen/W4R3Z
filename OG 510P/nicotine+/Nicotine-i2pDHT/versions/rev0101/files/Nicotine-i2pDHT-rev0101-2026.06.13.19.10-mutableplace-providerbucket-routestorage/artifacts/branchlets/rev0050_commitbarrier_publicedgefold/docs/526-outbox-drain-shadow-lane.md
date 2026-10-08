# Outbox drain shadow lane

The outbox drain lane sits after commit barrier acceptance but before live network writes.

It models the future publisher's last local receipt:

- accepted commit report digest
- accepted outbox report digest
- accepted egress report digest
- accepted scope-journal report digest
- public payload digest
- idempotency key
- public effect digest
- drain intent: refresh, withdraw, repair
- sequence and previous drain digest
- family and path-family hints

The drain lane is still no-network. It emits local evidence that the future sender may have permission to drain an idempotent side effect. It does not provide exactly-once semantics, does not open SAM, and does not update a DHT.

The main risk is laundering: one accepted commit, one accepted egress report, or one signed outbox entry must not become a repeatable hidden publish loop. The tests therefore pin replay, sequence fork, component drift, watch debt, and idempotency conflict behavior.
