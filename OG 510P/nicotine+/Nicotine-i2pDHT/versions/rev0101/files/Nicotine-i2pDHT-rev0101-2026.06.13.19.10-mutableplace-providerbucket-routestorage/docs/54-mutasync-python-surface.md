# rev0006 Python surface

`src/i2p_dht_lab/mutasync.py` adds executable scaffolding for the mutable sync control plane.

## Core functions

```text
collection_id(root_public_key, label, policy)
capability_id(collection, role, secret_material)
head_salt(collection, kind, writer_public_key=b'', shard=b'')
make_sync_head_record(...)
make_writer_feed_head(...)
make_snapshot_head(...)
make_roster_head(...)
```

## Core records

```text
CollectionDescriptor
WriterGrant
FeedEntry
BlockRef
FileVersion
SnapshotManifest
SyncMutableHead
```

## Garden planning

```text
SyncGardenBudget
SyncGardenPlan
plan_sync_garden_services(...)
```

## Tests

`tests/test_mutasync.py` exercises:

- stable collection/capability ids;
- signed writer grants;
- tamper rejection;
- feed-entry chaining;
- mutable feed heads;
- snapshot-root changes;
- roster-head salt bounds;
- conflict preservation;
- garden sync service planning.

## Design limitation

The module uses direct Python dataclasses and bencoding.  It is intentionally not final wire format, not storage format, and not a sync engine.
