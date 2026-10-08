# rev0024 — policyepoch / rangemerkle / queueforge

This revision pushes three risky guesses into executable Python before live I2P/SAM transport exists:

1. namespace policy rollout needs mutable epoch heads, not just signed policy blobs;
2. range anti-entropy needs proof-sized repair fixtures, not only compact roots;
3. garden admission needs queue scheduling under latency/overload, not only batch admission.

The rule added here is:

```text
Mutable policy, repair evidence, and queued capacity all need local memory before they become useful.
```

No global policy authority is introduced. A policy epoch head is an observation by a local authority the node chose to follow. It must still pass local rollback, fork, previous-link, digest-binding, and source-family pressure.

Range Merkle fixtures are deliberately small. They are not a storage engine, not a production Merkle protocol, and not a claim that roots decide truth. They let the cube test exact repair proofs and tombstone-first repair pressure instead of stopping at “root changed.”

Queue forge is likewise deliberately small. It tests that head-watch, witness-query, and seed-gate work can survive bulk provider floods and that useful refusal remains signed capacity evidence rather than silent failure.
