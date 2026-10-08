# Record algebra and mutability

The DHT should have a small record vocabulary from day zero.

## Immutable records

Content-addressed records:

```text
target = SHA256(domain || namespace || canonical_payload)
```

Useful for small manifests, contact snapshots, bootstrap hints, and validator
metadata. Not for large files.

## Provider records

Provider records say: "node X can provide content/service/key Y". They are
signed by the provider key and expire quickly. Storage nodes validate signatures
but do not need to understand future application semantics.

## Mutable records

Mutable records follow the BEP44/BEP46 shape:

```text
public_key: 32-byte Ed25519 key
salt: optional <=64 bytes
seq: monotonic int64
value: <=1000-byte canonical bencoded value
signature: Ed25519 over salt/seq/value payload
```

Native DHT target:

```text
i2p_target = SHA256(domain || public_key || salt)
```

Compatibility facet:

```text
bt_target = SHA1(public_key || salt)
```

## Why mutable slots are core

A DHT without mutability can find static things. A DHT with signed mutable slots
can host living pointers: torrent heads, release channels, provider manifests,
friend feeds, room topics, update channels, reputation anchors, and directory
roots.

## Validators

The core DHT validates universal properties: size, signature, expiry, monotonic
sequence, target match. Consumer namespaces add deeper validators later.
