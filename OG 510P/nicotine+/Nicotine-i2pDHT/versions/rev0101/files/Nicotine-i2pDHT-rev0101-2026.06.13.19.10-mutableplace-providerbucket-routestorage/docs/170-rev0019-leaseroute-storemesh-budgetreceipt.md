# rev0019 — leaseroute-storemesh-budgetreceipt

rev0019 keeps the cube in risk-first DHT design space and joins surfaces that were previously tested alone.

## Core guess

```text
Helpful contribution surfaces become capture surfaces when they are accepted in isolation.
```

The new work attacks four seams:

1. **Lease-bound route gossip**: route repair must be backed by fresh, monotonic, purpose-scoped contact leases.
2. **Store mesh**: sibling store acks must be judged across mutable heads, tombstones, provider claims, and useful refusals.
3. **Garden budget receipts**: a giving supernode should explain throttling/reordering/refusal with signed local evidence.
4. **Repeated-round ledger**: liveness budget, provider proofs, and witness cache summaries must agree across rounds before local acceptance.

This revision also retains and audits the parallel rev0019 store-flight/lease-quorum/read-repair branchlet instead of deleting it. That branchlet is useful: it pressures actual garden STORE admission, storage leases, and read repair. The new surfaces are complementary.

## Still not claimed

No live I2P/SAM transport. No production DHT. No production STORE protocol. No private retrieval guarantee. No global reputation. No Sybil or anonymity guarantee. No application integration.
