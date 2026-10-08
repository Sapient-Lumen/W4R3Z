# Witness cache aging

`witnesscache.py` answers a risky question left open by batch witness analysis:

```text
What happens after a garden or client hears evidence over time?
```

The answer in rev0015 is intentionally local and conservative.

A receipt can be:

- cryptographically valid;
- fresh enough to count;
- stale but still useful as history;
- duplicated by repeated gossip;
- monocultured inside one family;
- self-contradictory for one witness/target.

The cache stores `WitnessReceipt` objects from `probewitness.py`, but it treats duplicate receipt hashes as freshness refreshes, not extra votes.  It computes a simple deterministic weight: full weight during a short window, then linear decay to zero.  Family caps apply before summary decisions.

Decision kinds:

```text
preserve_diverse_evidence
continue_insufficient_weight
continue_insufficient_diversity
quarantine_contradiction
empty
```

The cache does not decide truth.  It tells the caller whether local signed evidence remains worth preserving/escalating, whether more paths are needed, or whether a target view should be quarantined because a witness contradicted itself.

## Why this matters

Long-lived DHT clients and garden nodes will accumulate partial observations.  Without aging, stale witness receipts become sticky folklore.  Without dedupe, gossip amplifies one receipt into fake consensus.  Without family caps, a garden family can become a local monoculture.  Without contradiction quarantine, a fast malicious witness can poison every later decision.
