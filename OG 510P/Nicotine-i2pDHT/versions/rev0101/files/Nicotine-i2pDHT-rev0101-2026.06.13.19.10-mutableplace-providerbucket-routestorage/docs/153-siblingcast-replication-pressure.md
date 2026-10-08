# Siblingcast replication pressure

A DHT store operation should not be accepted merely because one fast path returned success. rev0018 adds a sibling-broadcast pressure surface inspired by S/Kademlia's reliable sibling broadcast idea: store near the target, but evaluate acknowledgements across path/family diversity.

The new surface models:

```text
SiblingCandidate
SiblingBroadcastPlan
SiblingAck
SiblingCastReport
```

The store round can end in:

```text
stored_diverse
continue_needs_acks
continue_needs_families
continue_timeout_pressure
continue_refusal_pressure
quarantine_contradiction
quarantine_bad_signature
```

A sibling acknowledgement is not truth. It is evidence that a chosen storage peer claims to hold the exact record digest at a sequence. Same-node same-sequence digest conflicts are quarantine evidence. Useful refusals remain useful capacity evidence, but they do not count as stored replicas.

The local rule:

```text
Replication success needs exact digest acknowledgements from diverse siblings.
```
