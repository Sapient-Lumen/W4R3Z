# Next revision pointer — rev0063

Suggested next revision: **rev0064 `retrypublish-idempotencymesh-deliveryrepair`**.

Suggested focus:

```text
retry publication outbox,
retry idempotency lineage,
remote duplicate-delivery witnesses,
and delivery-repair evidence that survives retry settlement.
```

Hard questions:

- When a retry is allowed after late-ACK absence, how is retry publication staged without reusing the original idempotency key?
- How do remote duplicate-delivery witnesses interact with local contradiction journals?
- What evidence is needed to prove a retry was withdrawn rather than delivered?
