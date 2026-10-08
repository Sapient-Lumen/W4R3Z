# Research notes — 2026-06-01 rev0023

Research nudges that shaped the revision:

- Kademlia's bucket update rule prefers long-lived responsive contacts over novelty; this keeps route aging and admission pressure from chasing every fresh contact.
- Dynamo-style anti-entropy uses Merkle trees per key range to compare replica state and discover differences cheaply; rev0023 borrows only the range-summary idea, not Dynamo's trust model.
- libp2p/Kad-DHT validator interfaces reinforce that DHT records need type-specific validation before storage/retrieval.
- SAM remains the likely non-Java I2P integration surface, but the cube still keeps SAM behavior shadowed rather than assuming all SAM 3.3 subsession/datagram behavior is available in the bundled-router path.

Design translation:

```text
range roots -> repair hints
validators -> local namespace policy
admission -> local resource wall
transport -> still shadowed
```
