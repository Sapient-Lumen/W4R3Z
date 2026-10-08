# Tombstone/cache resurrection pressure

Mutable systems need deletion and revocation memory. Without tombstones, stale caches can resurrect old provider records, old mutable heads, revoked grants, deleted sync entries, or withdrawn service offers.

`TombstoneRecord` is a signed toy record:

```text
target_commitment
kind: provider_withdrawn | mutable_deleted | key_compromised | grant_revoked
issuer public key
issuer family
sequence
issued_at / expires_at
optional subject digest
reason
signature
```

`TombstoneCache` verifies records, keeps live records by target, detects same-issuer same-sequence tombstone forks, and compares live tombstones against witness-cache claims such as `provider_true` or `mutable_latest`.

The central rev0017 pressure test:

```text
live tombstone + cached alive/provider evidence => block resurrection pressure
```

A tombstone is still only evidence. It does not prove global deletion. It does force a local client/garden to treat stale “alive” evidence as risky rather than convenient.
