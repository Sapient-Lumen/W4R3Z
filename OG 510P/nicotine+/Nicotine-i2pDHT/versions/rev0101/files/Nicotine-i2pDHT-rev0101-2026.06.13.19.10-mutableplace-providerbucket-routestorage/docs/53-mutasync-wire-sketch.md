# Mutable sync wire sketch

This is not final wire format.  It is a transcript-shaped guess for future tests.

## Publish writer roster

```text
PUT_MUTABLE
  target = H(owner_pubkey, salt=sync1/writer_roster/<collection>)
  seq    = roster_epoch
  value  = {
    kind: writer_roster,
    collection: <32 bytes>,
    pointer_kind: writer_roster_digest,
    pointer: H(roster-manifest-or-inline-grants),
    epoch: roster_epoch
  }
  sig = Sign(owner_key, seq || value || salt)
```

## Publish writer feed tip

```text
PUT_MUTABLE
  target = H(writer_pubkey, salt=sync1/writer_feed_tip/<collection>/<writer>)
  seq    = feed_index
  value  = {
    kind: writer_feed_tip,
    collection: <32 bytes>,
    writer: <32 bytes>,
    pointer_kind: feed_entry_hash,
    pointer: H(feed_entry_n),
    epoch: roster_epoch
  }
  sig = Sign(writer_key, seq || value || salt)
```

## Publish snapshot root

```text
PUT_MUTABLE
  target = H(owner_pubkey, salt=sync1/snapshot_root/<collection>)
  seq    = snapshot_version
  value  = {
    kind: snapshot_root,
    collection: <32 bytes>,
    pointer_kind: snapshot_root_hash,
    pointer: H(snapshot_manifest),
    epoch: roster_epoch
  }
```

## Advertise encrypted block provider

```text
PUT_PROVIDER
  namespace = sync.block
  key       = H(encrypted_block)
  provider  = garden_or_leaf_node_id
  hints     = {
    collection_hint: optional truncated tag,
    codec: raw|erasure-share|manifest,
    max_streams: n
  }
  sig = Sign(provider_key, provider_payload)
```

## Ask a garden for diff hints

```text
SYNC_DIFF_HINT_REQUEST
  collection = <32 bytes>
  known_snapshot = <32 bytes or empty>
  wanted_prefix = encrypted/path/prefix/or/public-path-prefix
  budget = max entries / max bytes

SYNC_DIFF_HINT_RESPONSE
  signed_by_garden
  not authoritative
  contains manifest roots, feed ranges, or prefix buckets
```

## Principle

Every response that accelerates sync is treated as a hint until the client validates signed heads, feed signatures, block hashes, and capabilities.
