from dataclasses import replace

from i2p_dht_lab.identity import DhtKeypair
from i2p_dht_lab.mutable import MutableSlotStore, StoreCode
from i2p_dht_lab.mutasync import (
    BlockRef,
    CollectionDescriptor,
    CollectionPolicy,
    FeedEntry,
    FileVersion,
    GardenSyncService,
    HeadKind,
    SnapshotManifest,
    SyncGardenBudget,
    SyncRole,
    WriterGrant,
    capability_id,
    collection_id,
    guess_conflict_strategy,
    head_salt,
    make_roster_head,
    make_snapshot_head,
    make_writer_feed_head,
    mutasync_guardrails,
    plan_sync_garden_services,
)


def test_collection_descriptor_and_capability_ids_are_stable():
    owner = DhtKeypair.from_seed(b"\x90" * 32)
    descriptor = CollectionDescriptor(
        label="ambient-demo",
        root_public_key=owner.public_key_bytes,
        policy=CollectionPolicy.MULTI_WRITER_FEEDS,
        read_capability=capability_id(b"\x01" * 32, SyncRole.READER, b"read-secret"),
    )
    assert descriptor.collection == collection_id(owner.public_key_bytes, "ambient-demo")
    invite = descriptor.public_invite_dict()
    assert invite[b"collection"] == descriptor.collection
    assert invite[b"policy"] == CollectionPolicy.MULTI_WRITER_FEEDS.value
    assert len(invite[b"read_cap"]) == 32


def test_writer_grant_sign_verify_and_tamper_fails():
    owner = DhtKeypair.from_seed(b"\x91" * 32)
    writer = DhtKeypair.from_seed(b"\x92" * 32)
    coll = collection_id(owner.public_key_bytes, "grant-demo")
    grant = WriterGrant.issue(
        owner_keypair=owner,
        collection=coll,
        writer_public_key=writer.public_key_bytes,
        role=SyncRole.WRITER,
        epoch=3,
        label="laptop",
    )
    assert grant.verify()
    assert grant.roster_value()[b"writer"] == writer.public_key_bytes
    assert not replace(grant, epoch=4).verify()


def test_feed_entry_chain_and_mutable_feed_head():
    owner = DhtKeypair.from_seed(b"\x93" * 32)
    writer = DhtKeypair.from_seed(b"\x94" * 32)
    coll = collection_id(owner.public_key_bytes, "feed-demo")
    entry0 = FeedEntry.create(
        writer_keypair=writer,
        collection=coll,
        index=0,
        prev_hash=b"",
        operation={b"put": b"/songs/a.flac", b"block": b"\x01" * 32},
    )
    entry1 = FeedEntry.create(
        writer_keypair=writer,
        collection=coll,
        index=1,
        prev_hash=entry0.entry_hash,
        operation={b"put": b"/songs/b.flac", b"block": b"\x02" * 32},
    )
    assert entry0.verify()
    assert entry1.verify()
    assert entry1.chains_after(entry0)

    head = make_writer_feed_head(writer_keypair=writer, entry=entry1, now=1000)
    assert head.kind == HeadKind.WRITER_FEED_TIP
    assert head.pointer == entry1.entry_hash
    assert head.record.verify()
    assert len(head.record.salt) <= 64

    store = MutableSlotStore.empty()
    assert store.put(head.record, now=1000).code == StoreCode.ACCEPTED_NEW
    stale = make_writer_feed_head(writer_keypair=writer, entry=entry0, now=1001)
    assert store.put(stale.record, now=1001).code == StoreCode.REJECT_STALE_SEQUENCE


def test_snapshot_manifest_root_and_snapshot_head_change_on_file_update():
    owner = DhtKeypair.from_seed(b"\x95" * 32)
    coll = collection_id(owner.public_key_bytes, "snapshot-demo")
    block_a = BlockRef(digest=b"\xaa" * 32, size=131072)
    first = FileVersion(path="music/a.flac", size=131072, mtime_ns=10, blocks=(block_a,))
    manifest1 = SnapshotManifest(collection=coll, version=1, files=(first,))
    assert manifest1.file_count == 1
    assert len(manifest1.root_hash) == 32

    block_b = BlockRef(digest=b"\xbb" * 32, size=131072)
    second = FileVersion(path="music/a.flac", size=131072, mtime_ns=20, blocks=(block_b,))
    manifest2 = SnapshotManifest(collection=coll, version=2, files=(second,), previous_snapshot=manifest1.root_hash)
    assert manifest2.root_hash != manifest1.root_hash

    head = make_snapshot_head(owner_keypair=owner, manifest=manifest2, seq=2, now=1000)
    assert head.pointer == manifest2.root_hash
    assert head.record.value[b"pointer_kind"] == "snapshot_root_hash"
    assert head.record.verify()


def test_roster_head_and_head_salt_are_small():
    owner = DhtKeypair.from_seed(b"\x96" * 32)
    writer = DhtKeypair.from_seed(b"\x97" * 32)
    coll = collection_id(owner.public_key_bytes, "roster-demo")
    grant = WriterGrant.issue(owner_keypair=owner, collection=coll, writer_public_key=writer.public_key_bytes, label="writer")
    salt = head_salt(coll, HeadKind.WRITER_ROSTER)
    assert len(salt) <= 64
    head = make_roster_head(owner_keypair=owner, collection=coll, grants=[grant], seq=1, now=1000)
    assert head.record.kind == "sync.writer_roster"
    assert head.record.verify()


def test_conflict_guess_preserves_both_by_default():
    left = FileVersion(path="notes.txt", size=1, mtime_ns=1, blocks=(BlockRef(b"\x01" * 32, 1),))
    right = FileVersion(path="notes.txt", size=1, mtime_ns=2, blocks=(BlockRef(b"\x02" * 32, 1),))
    conflict = guess_conflict_strategy(left, right)
    assert conflict is not None
    assert conflict.strategy == "preserve_both_conflict_copies"
    assert conflict.user_visible_name().startswith("notes.txt.conflict.")


def test_sync_garden_plan_and_guardrails():
    budget = SyncGardenBudget(
        storage_mb=32768,
        ram_mb=2048,
        upload_kib_s=2048,
        max_watched_heads=50_000,
        max_cached_blocks=2_000_000,
        uptime_hours=20,
    )
    plan = plan_sync_garden_services(budget)
    assert plan.has(GardenSyncService.HEAD_WATCHER)
    assert plan.has(GardenSyncService.BLOCK_CACHE)
    assert plan.has(GardenSyncService.ERASURE_SHARE_KEEPER)
    assert plan.max_metadata_posture == "encrypted-block-and-manifest-cache"
    assert "garden_nodes_may_cache_but_cannot_author_changes" in mutasync_guardrails()
