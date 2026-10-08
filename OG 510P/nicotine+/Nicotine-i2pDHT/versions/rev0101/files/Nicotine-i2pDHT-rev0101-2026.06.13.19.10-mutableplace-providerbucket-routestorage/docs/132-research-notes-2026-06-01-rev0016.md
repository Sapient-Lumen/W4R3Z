# Research notes — 2026-06-01 rev0016

The research posture did not change the cube into a standards clone. It sharpened three warnings.

## SAM

SAM v3.3 adds primary/subsession support that can combine streaming, datagrams, and raw subsessions on one destination. That is attractive for a future DHT, but it should stay a shadowed assumption until the bundle-first i2pd path is tested. The cube therefore keeps streaming-first transcript families and a datagram-primary negative test.

## Provider reprovide and garden batching

Provider records are not content truth. They are routing pointers that need validation, expiration, and republishing. Reprovide Sweep remains a useful garden-node clue because batching by XOR keyspace region can reduce repeated lookup/connection storms for large provider sets.

## I2P floodfill lessons

I2P’s own network database docs and threat model remain the right warning for garden nodes: capacity tiers are useful, but hostile or unreliable high-capacity nodes can still return bad/no answers or capture part of a keyspace. Garden nodes should therefore give capacity, receipts, repair contacts, and useful refusal — not authority.

## Imported into rev0016 code

```text
SAM transcript families before live transport
route-gossip repair before routing-table trust
repeated-round replay memory before accepting cached evidence
provider-surface migration before deleting history
```
