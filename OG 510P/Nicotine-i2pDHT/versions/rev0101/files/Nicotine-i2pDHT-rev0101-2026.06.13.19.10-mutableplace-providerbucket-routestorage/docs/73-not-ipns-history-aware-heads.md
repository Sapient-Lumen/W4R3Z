# Not IPNS: history-aware heads

The design does not aim to clone IPNS.  The useful lesson is the failure pressure: a mutable pointer can be signed, valid, and still not be the value a user should accept.

IPNS records are cryptographically verifiable mutable pointers with fields such as value, validity, sequence, TTL, public key, and signature.  That shape is useful, but not sufficient for this DHT's future power-user needs.  The DHT needs to assume that nodes may return old records, that publishers may fork by accident or compromise, and that lookup paths can be captured or stale.

Source pointers:

- IPNS record specification: https://specs.ipfs.tech/ipns/ipns-record/
- IPNS-over-DHT/PubSub discussion of historic DHT lookup/publish pain: https://discuss.ipfs.tech/t/ipns-over-dht-and-pubsub/18880
- IPNS high-availability discussion noting DHT expiration behavior is independent of IPNS TTL/validity: https://discuss.ipfs.tech/t/ipns-publishing-guidance-for-high-availability/18928

## rev0009 guess

A mutable head should often be history-aware:

```text
head(seq = n)
  pointer = content-addressed manifest/feed/infohash/seedlist/policylist
  prev    = digest(head(seq = n - 1))
  sig     = publisher signature over canonical value
```

The previous-head link is not mandatory for every possible head.  It is a strong mode for high-risk heads: software releases, policy portfolios, seed portfolios, sync rosters, and revocation catalogs.

## Why the previous-head digest matters

A pure sequence number says only:

```text
this signer emitted something numbered 42
```

A previous-head digest says more:

```text
this signer is intentionally advancing from the exact head I already accepted
```

That does not create global consensus.  It gives a client a reason to reject or flag an advance that jumps away from its known history.

## Current behavior

`LocalHeadMemory.observe(..., require_prev=True)` now:

- accepts the first head;
- accepts a sequential advance when `prev` matches the accepted record digest;
- rejects older records as rollback attempts;
- rejects equal-sequence different values as forks;
- rejects advances whose `prev` does not match local memory;
- flags advances that omit `prev` when the caller requires history.

## Open design debt

- Whether previous-head links should be mandatory by namespace.
- How much history a garden should keep per target.
- How to handle legitimate key rotation without making rollback undetectable.
- Whether skipped sequences need checkpoint manifests or witness quorums.
- Whether app heads should include Merkle proof fragments for fast catch-up.
