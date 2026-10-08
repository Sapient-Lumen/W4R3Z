# rev0009 — risk-first mutability

The design goal for this revision is to stop merely admiring mutability and start testing the pieces most likely to betray users.

The user correction is accepted directly: IPNS is not the template.  IPNS is a teacher because it shows the hard shape of the problem: a cryptographically valid mutable pointer is not enough when users need the actual latest pointer, need rollback memory, and need delivery paths that do not depend on one fragile routing mechanism.

## What this cube now tests first

1. **Rollback:** a valid old signed mutable record returns after a client already accepted a newer one.
2. **Same-sequence fork:** the same publisher signs two different values with the same sequence.
3. **Missing history link:** an advancing head does not point back at the locally accepted head.
4. **Capability delegation:** a garden or helper can act for a publisher without becoming the publisher.
5. **Revocation:** a valid grant can become unusable when a signed revocation head is known.
6. **Chaos lookup:** stale, forked, empty, and honest responders appear in one fake lookup transcript.

## The big guess

```text
latest-enough = signature-valid
              + monotonic local memory
              + optional previous-head linkage
              + disjoint lookup pressure
              + witnessable evidence
              + expiry/revocation discipline
```

This is not consensus.  It is survival discipline for eventual consistency.

## Code added

- `src/i2p_dht_lab/headlog.py`
- `src/i2p_dht_lab/capability.py`
- `src/i2p_dht_lab/chaos.py`
- `tests/test_headlog_capability_chaos.py`

## Nonclaim

The cube still does not solve global latestness.  It starts making stale/forked/latest ambiguity explicit, testable, and witnessable.
