# Risk register — rev0049

Active risks:

- outbox staging might be mistaken for completed publication
- idempotency keys might hide payload/effect drift
- audit-gap repair might launder stale public records into refreshes
- hard-negative evidence might be compacted away before repair planning
- watch debt might become invisible queue state
- family/path diversity remains a weak local pressure tool, not Sybil resistance

Deliberate nonclaims remain unchanged: no live SAM/I2P, no production DHT, no production public bridge protocol, no mutable-head consensus, no global ban list, no global reputation, no private retrieval guarantee, and no Sybil/anonymity guarantee.
