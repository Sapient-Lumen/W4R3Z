# rev0009 — hardest guesses first

Codename: `forkwatch-capgrant-chaosloom`.

This revision stops merely naming the right DHT dreams and starts pushing the riskiest ones into executable Python. The core stance is still speculative and DHT-first: no live SAM/I2P transport, no production security, no application integration. The difference is that the hard guesses now have tests.

## The hard guesses chosen first

1. Mutable heads will be attacked by staleness, rollback, split views, and same-sequence forks. Signature validity is necessary but not enough.
2. Garden nodes need receipts and bounded service contracts, not vague trust.
3. Capability delegation and revocation must exist before sync, bridge, or garden service layers become serious.
4. Seed portfolios can be captured if entrances are not diversified by channel, garden source, cache, and social path.
5. A fake adversarial transport is more valuable right now than a fragile live transport demo.

## New executable surfaces

- `src/i2p_dht_lab/forkwatch.py`: local mutable-head memory, same-sequence fork detection, rollback/stale detection, signed witness receipts, and deterministic best-record selection.
- `src/i2p_dht_lab/capgrant.py`: scoped delegated capabilities, audience/resource checks, revocation heads, and a mutable revocation-head wrapper.
- `src/i2p_dht_lab/chaos.py`: fake replica replies with honest/stale/fork/silent/empty behaviors, lookup transcripts, witness receipts, and seed-capture reports.
- `tests/test_forkwatch_capgrant_chaos.py`: the new pressure lane for these guesses.

The previous `headlog.py` and `capability.py` experiments remain in place and still pass. rev0009 adds a second, more record-native fork/watch surface rather than pretending the first sketch is final.

## Current thesis

Mutable records need two layers of defense:

```text
record validation
  verifies signature, size, salt, sequence shape, expiry

history validation
  remembers highest seen sequence
  detects same-sequence forks
  detects valid-but-stale rollback attempts
  emits witness receipts as evidence
```

The first layer is pure cryptography and shape. The second layer is local memory plus evidence. There is no global consensus claim.

## Why this matters

A future DHT above I2P will have high latency, churn, intermittent publishers, garden caches, opportunistic bridges, and policy/seed heads. Under those conditions, “valid signed record” and “safe latest record” are different concepts. The DHT must be born with this distinction or it will eventually reproduce the mutability pain that made IPNS frustrating.

## Nonclaims

- No live network behavior is measured.
- No Byzantine consensus is implemented.
- No global transparency log is implemented.
- No UCAN-compatible token format is implemented.
- No production revocation semantics are claimed.
- No metadata-safety, Sybil-resistance, or anonymity guarantee is claimed.
