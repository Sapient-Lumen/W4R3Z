# Revocation-head pressure

Revocation heads are mutable heads. Therefore they can be rolled back.

## Risk

A grant may be valid before a revocation head appears. If an attacker replays an older revocation head that omits the grant, a naive evaluator might allow the grant again.

## Implemented

`revocation_pressure.py` adds local memory for revocation authorities:

```text
highest seen sequence per authority
accepted head hash
same-sequence fork hashes
cumulative union of revoked grant hashes
```

The crucial behavior:

```text
observe latest head revoking grant
observe older valid head that omits grant
memory still treats grant as revoked
```

## Guess

Revocation in an eventually consistent DHT cannot be instant or perfect. But local monotonic memory and tombstone preservation are cheap and necessary. Gardens can help by preserving revocation heads and stale-head evidence, but they cannot author revocations unless delegated to do so.
