# Diagrams

**Track:** Shared (cross-cutting)


## End-to-end flow (Mermaid)

```mermaid
sequenceDiagram
  participant V as Voter Client
  participant N as PBB Node
  participant W as Witnesses
  participant T as Trustees

  V->>V: Build ballot, encrypt C, ZK proof π
  V->>N: Submit {C, π, credential proof}
  N->>N: Verify eligibility + revocation + π
  N->>W: Publish STH / gossip
  N-->>V: Receipt (index + inclusion proof + STH)
  W->>W: Cross-check STHs, detect equivocation
  N->>T: Close election; provide ciphertext set
  T->>T: Mixnet or homomorphic tally + threshold decrypt
  T-->>W: Publish proofs
  W-->>V: Anyone verifies inclusion + tally
```
