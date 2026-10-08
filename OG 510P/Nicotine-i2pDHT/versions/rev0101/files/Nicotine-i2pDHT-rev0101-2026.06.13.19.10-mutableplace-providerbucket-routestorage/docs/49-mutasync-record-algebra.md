# Mutable sync record algebra

The DHT's sync-supporting record algebra should be tiny and composable.

## 1. Collection descriptor

A collection is a share, folder, archive, feed group, mutable torrent family, or app namespace.

```text
collection_id = SHA256(domain || root_public_key || policy || label)
```

The descriptor is not necessarily secret.  A future encrypted sync app may have separate read/write capabilities.  The DHT can safely reason about opaque collection ids while accepting that metadata posture varies by mode.

## 2. Writer grants

A root/owner key signs grants for writers, readers, providers, and garden stewards.

```text
owner_key signs:
  collection_id
  writer_public_key
  role
  epoch
  optional expiry
```

Storage nodes do not need to understand the whole application.  They only need to verify the grant's signature when the grant appears in a roster record or when a validator policy asks for it.

## 3. Per-writer feeds

Each writer has an append-only feed:

```text
entry_0 = sign(writer_key, collection || index=0 || prev='' || operation)
entry_1 = sign(writer_key, collection || index=1 || prev=hash(entry_0) || operation)
...
```

The DHT stores the current tip as a mutable head.  The feed body can be fetched through peers, garden caches, or content-addressed block providers.

This avoids a single shared mutable write slot for a multiwriter folder.  It also makes offline operation natural: each writer can continue its own log and reconciliation can happen later.

## 4. Snapshot manifests

Feeds are excellent for history; snapshots are excellent for catch-up.  A snapshot manifest summarizes a collection state:

```text
path
size
mtime-ish logical timestamp
block refs
mode/deleted bit
```

The DHT's mutable snapshot head points to a manifest root hash.  Very small manifests can be inline in prototype records, but real manifests should be content-addressed blocks.

## 5. Mutable heads

All live names become mutable heads:

```text
writer feed tip    -> latest feed entry hash
snapshot root      -> latest manifest root
writer roster      -> grant list digest or roster manifest root
mutable torrent    -> latest infohash
garden catalog     -> service catalog digest
```

The mutable head payload should stay under the BEP44-style small-value ceiling.  This cube uses 1000 bytes as the conservative prototype threshold inherited from the BEP44 model.

## 6. Provider records

Provider records answer:

```text
who can provide block X?
who can provide feed segment Y?
who can mirror manifest root Z?
who watches collection C?
```

Provider records are signed by the provider.  Garden nodes may publish provider records for encrypted blocks or feed segments they cache, but that does not grant write authority.

## 7. Garden service records

Garden sync services are not magic.  They are offers:

```text
I can watch up to N heads.
I can cache M encrypted blocks.
I can hold tombstones for T days.
I can relay feed segments.
I can witness roster rollbacks.
```

The DHT can store signed service offers and local nodes can select gardens based on their own observed usefulness.

## Consequence

The DHT does not need one monolithic sync protocol.  It needs validators for small signed records, a good lookup/replication strategy, and garden-aware republishing.  Sync protocols can then compose these records.
