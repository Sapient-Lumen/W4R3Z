# Capability grants and revocation heads

rev0009 adds `capgrant.py` because garden service, bridge service, sync service, and policy publication need bounded delegation before they need application polish.

The guiding rule:

```text
capabilities delegate service authority; they do not define identity or DHT truth
```

## Capability grant shape

A `CapabilityGrant` signs:

```text
issuer public key
subject public key
verbs
resource
audience
issued_at / not_before / expires_at
caveats
parent_hash
nonce
```

The new verb vocabulary includes:

```text
watch_head
witness_head
reprovide_region
seed_gate
bridge_query
cache_block
hold_wake_record
write_feed
read_collection
publish_policy
```

The shape is intentionally UCAN-adjacent but not UCAN-compatible. The cube is testing semantics first: scoping, expiry, audience binding, resource narrowing, and revocation.

## Revocation head shape

A `RevocationHead` signs a sequence-numbered set of revoked grant hashes. It can also be wrapped into the existing generic `MutableRecord` primitive with `make_revocation_mutable_head()`.

That makes revocation a first-class mutable-head use case:

```text
publisher key + salt -> current revocation head
```

This is not instant revocation. A DHT cannot promise offline clients learn immediately. The goal is visible, signed, refreshable revocation that gardens can cache and witness.

## What tests now cover

- Exact grants allow the intended verb/resource/audience.
- Wrong resource, wrong audience, and wrong verb are denied.
- A revocation head denies a previously valid grant.
- The revocation head can be wrapped as a signed mutable record.

## Unresolved design bets

- Whether revocation heads should be per-authority, per-collection, per-garden, or per-resource-region.
- Whether delegation chains should be encoded compactly in DHT records or resolved through provider records.
- Whether gardens should refuse expired/revoked capabilities softly, with signed refusal receipts.
- Whether forked revocation heads should be treated more like policy-head forks or software-update-channel forks.

## Strong current guess

Revocation should be treated as a moving pointer to evidence, not as magical deletion. A grant that was valid yesterday may still be replayed by a stale node. The receiving client must evaluate grant validity at request time, check known revocation heads, and keep local monotonic memory for the revocation head itself.
