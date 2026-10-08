"""Mutable sync control-plane guesses for a DHT living above I2P.

This module is not a file-sync implementation.  It is a small executable
algebra for the DHT records that a future FLOSS Resilio/Syncthing/Hypercore-like
system could build on: collection identities, writer grants, append-only feeds,
small snapshot manifests, mutable heads, and garden-node sync service planning.

The DHT should remain a control plane.  Blocks and file contents travel through
separate block-exchange streams or garden caches; the DHT stores only compact,
validated, signed pointers and provider announcements.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .mutable import MutableRecord

MAX_SYNC_HEAD_VALUE_BYTES = 1000
MAX_FEED_ENTRY_BYTES = 4096
MAX_MANIFEST_VALUE_BYTES = 32_768
SYNC_DOMAIN = DOMAIN + b":mutasync-v1:"


class SyncRole(str, Enum):
    OWNER = "owner"
    WRITER = "writer"
    READER = "reader"
    PROVIDER = "provider"
    GARDEN_STEWARD = "garden_steward"


class CollectionPolicy(str, Enum):
    SINGLE_WRITER = "single_writer"
    DELEGATED_WRITERS = "delegated_writers"
    MULTI_WRITER_FEEDS = "multi_writer_feeds"
    APP_CRDT = "app_crdt"


class HeadKind(str, Enum):
    WRITER_ROSTER = "writer_roster"
    WRITER_FEED_TIP = "writer_feed_tip"
    SNAPSHOT_ROOT = "snapshot_root"
    MUTABLE_TORRENT = "mutable_torrent"
    GARDEN_CATALOG = "garden_catalog"


class GardenSyncService(str, Enum):
    HEAD_WATCHER = "head_watcher"
    ROSTER_WITNESS = "roster_witness"
    FEED_RELAY = "feed_relay"
    BLOCK_CACHE = "block_cache"
    SNAPSHOT_MIRROR = "snapshot_mirror"
    DIFF_HINTER = "diff_hinter"
    ERASURE_SHARE_KEEPER = "erasure_share_keeper"
    TOMBSTONE_KEEPER = "tombstone_keeper"
    WAKE_RENDEZVOUS = "wake_rendezvous"


def collection_id(root_public_key: bytes, label: str, *, policy: CollectionPolicy = CollectionPolicy.MULTI_WRITER_FEEDS) -> bytes:
    if len(root_public_key) != 32:
        raise ValueError("root_public_key must be 32 bytes")
    if not label:
        raise ValueError("label must not be empty")
    return sha256(SYNC_DOMAIN + b"collection:" + policy.value.encode("ascii") + b":" + root_public_key + b":" + label.encode("utf-8"))


def capability_id(collection: bytes, role: SyncRole, secret_material: bytes) -> bytes:
    if len(collection) != 32:
        raise ValueError("collection id must be 32 bytes")
    if not secret_material:
        raise ValueError("secret_material must not be empty")
    return sha256(SYNC_DOMAIN + b"capability:" + collection + b":" + role.value.encode("ascii") + b":" + secret_material)


def _short_tag(raw: bytes, size: int = 16) -> bytes:
    return raw[:size]


def head_salt(collection: bytes, kind: HeadKind, *, writer_public_key: bytes = b"", shard: bytes = b"") -> bytes:
    """Return a <=64-byte BEP44-style salt for a sync mutable head.

    We intentionally use short binary tags, not long user labels, because BEP44
    caps salts at 64 bytes.  The salt is only an address namespace; the record
    value still carries enough context to validate intent.
    """
    if len(collection) != 32:
        raise ValueError("collection id must be 32 bytes")
    if writer_public_key and len(writer_public_key) != 32:
        raise ValueError("writer_public_key must be 32 bytes when present")
    if len(shard) > 8:
        raise ValueError("shard tag must be <= 8 bytes")
    kind_tag = kind.value.encode("ascii")[:18]
    salt = b"sync1/" + kind_tag + b"/" + _short_tag(collection)
    if writer_public_key:
        salt += b"/" + _short_tag(writer_public_key)
    if shard:
        salt += b"/" + shard
    if len(salt) > 64:
        raise AssertionError("internal salt builder exceeded BEP44 limit")
    return salt


@dataclass(frozen=True)
class CollectionDescriptor:
    """Small share/root descriptor that can appear in invite files."""

    label: str
    root_public_key: bytes
    policy: CollectionPolicy = CollectionPolicy.MULTI_WRITER_FEEDS
    read_capability: bytes | None = None
    write_capability: bytes | None = None

    @property
    def collection(self) -> bytes:
        return collection_id(self.root_public_key, self.label, policy=self.policy)

    def public_invite_dict(self) -> dict[bytes, BValue]:
        payload: dict[bytes, BValue] = {
            b"label": self.label,
            b"root": self.root_public_key,
            b"policy": self.policy.value,
            b"collection": self.collection,
        }
        if self.read_capability is not None:
            payload[b"read_cap"] = self.read_capability
        return payload


@dataclass(frozen=True)
class WriterGrant:
    collection: bytes
    owner_public_key: bytes
    writer_public_key: bytes
    role: SyncRole
    epoch: int
    label: str = ""
    expires_at: int | None = None
    signature: bytes = b""

    def unsigned_payload(self) -> bytes:
        if len(self.collection) != 32:
            raise ValueError("collection must be 32 bytes")
        if len(self.owner_public_key) != 32 or len(self.writer_public_key) != 32:
            raise ValueError("public keys must be 32 bytes")
        if self.epoch < 0:
            raise ValueError("epoch must be non-negative")
        payload: dict[bytes, BValue] = {
            b"collection": self.collection,
            b"owner": self.owner_public_key,
            b"writer": self.writer_public_key,
            b"role": self.role.value,
            b"epoch": self.epoch,
            b"label": self.label,
        }
        if self.expires_at is not None:
            payload[b"expires_at"] = self.expires_at
        return SYNC_DOMAIN + b"writer-grant:" + bencode(payload)

    @classmethod
    def issue(
        cls,
        *,
        owner_keypair: DhtKeypair,
        collection: bytes,
        writer_public_key: bytes,
        role: SyncRole = SyncRole.WRITER,
        epoch: int = 0,
        label: str = "",
        expires_at: int | None = None,
    ) -> "WriterGrant":
        grant = cls(
            collection=collection,
            owner_public_key=owner_keypair.public_key_bytes,
            writer_public_key=writer_public_key,
            role=role,
            epoch=epoch,
            label=label,
            expires_at=expires_at,
        )
        return replace(grant, signature=owner_keypair.sign(grant.unsigned_payload()))

    def verify(self) -> bool:
        return verify_signature(self.owner_public_key, self.unsigned_payload(), self.signature)

    def roster_value(self) -> dict[bytes, BValue]:
        return {
            b"owner": self.owner_public_key,
            b"writer": self.writer_public_key,
            b"role": self.role.value,
            b"epoch": self.epoch,
            b"label": self.label,
            b"sig": self.signature,
        }


@dataclass(frozen=True)
class FeedEntry:
    collection: bytes
    writer_public_key: bytes
    index: int
    prev_hash: bytes
    operation: BValue
    signature: bytes = b""

    def unsigned_payload(self) -> bytes:
        if len(self.collection) != 32:
            raise ValueError("collection must be 32 bytes")
        if len(self.writer_public_key) != 32:
            raise ValueError("writer_public_key must be 32 bytes")
        if self.index < 0:
            raise ValueError("index must be non-negative")
        if self.index == 0 and self.prev_hash != b"":
            raise ValueError("genesis entry prev_hash must be empty")
        if self.index > 0 and len(self.prev_hash) != 32:
            raise ValueError("non-genesis prev_hash must be 32 bytes")
        payload = bencode({
            b"collection": self.collection,
            b"writer": self.writer_public_key,
            b"index": self.index,
            b"prev": self.prev_hash,
            b"op": self.operation,
        })
        if len(payload) > MAX_FEED_ENTRY_BYTES:
            raise ValueError("feed entry payload too large")
        return SYNC_DOMAIN + b"feed-entry:" + payload

    @classmethod
    def create(
        cls,
        *,
        writer_keypair: DhtKeypair,
        collection: bytes,
        index: int,
        prev_hash: bytes,
        operation: BValue,
    ) -> "FeedEntry":
        entry = cls(
            collection=collection,
            writer_public_key=writer_keypair.public_key_bytes,
            index=index,
            prev_hash=prev_hash,
            operation=operation,
        )
        return replace(entry, signature=writer_keypair.sign(entry.unsigned_payload()))

    @property
    def entry_hash(self) -> bytes:
        return sha256(SYNC_DOMAIN + b"feed-entry-hash:" + self.unsigned_payload() + self.signature)

    def verify(self) -> bool:
        return verify_signature(self.writer_public_key, self.unsigned_payload(), self.signature)

    def chains_after(self, previous: "FeedEntry") -> bool:
        return self.index == previous.index + 1 and self.prev_hash == previous.entry_hash and self.collection == previous.collection


@dataclass(frozen=True)
class BlockRef:
    digest: bytes
    size: int
    codec: str = "raw"

    def as_value(self) -> dict[bytes, BValue]:
        if len(self.digest) != 32:
            raise ValueError("block digest must be 32 bytes")
        if self.size < 0:
            raise ValueError("block size must be non-negative")
        return {b"digest": self.digest, b"size": self.size, b"codec": self.codec}


@dataclass(frozen=True)
class FileVersion:
    path: str
    size: int
    mtime_ns: int
    blocks: tuple[BlockRef, ...]
    deleted: bool = False
    mode: int = 0o644

    def as_value(self) -> dict[bytes, BValue]:
        if not self.path:
            raise ValueError("path must not be empty")
        if self.size < 0:
            raise ValueError("size must be non-negative")
        return {
            b"path": self.path,
            b"size": self.size,
            b"mtime_ns": self.mtime_ns,
            b"deleted": 1 if self.deleted else 0,
            b"mode": self.mode,
            b"blocks": [block.as_value() for block in self.blocks],
        }

    @property
    def version_hash(self) -> bytes:
        return sha256(SYNC_DOMAIN + b"file-version:" + bencode(self.as_value()))


@dataclass(frozen=True)
class SnapshotManifest:
    collection: bytes
    version: int
    files: tuple[FileVersion, ...]
    previous_snapshot: bytes = b""

    def as_value(self) -> dict[bytes, BValue]:
        if len(self.collection) != 32:
            raise ValueError("collection must be 32 bytes")
        if self.version < 0:
            raise ValueError("version must be non-negative")
        if self.previous_snapshot and len(self.previous_snapshot) != 32:
            raise ValueError("previous_snapshot must be empty or 32 bytes")
        files = sorted(self.files, key=lambda item: item.path)
        value = {
            b"collection": self.collection,
            b"version": self.version,
            b"previous": self.previous_snapshot,
            b"files": [file.as_value() for file in files],
        }
        if len(bencode(value)) > MAX_MANIFEST_VALUE_BYTES:
            raise ValueError("snapshot manifest too large for prototype manifest record")
        return value

    @property
    def root_hash(self) -> bytes:
        return sha256(SYNC_DOMAIN + b"snapshot-root:" + bencode(self.as_value()))

    @property
    def file_count(self) -> int:
        return len(self.files)


@dataclass(frozen=True)
class SyncMutableHead:
    kind: HeadKind
    collection: bytes
    pointer: bytes
    pointer_kind: str
    seq: int
    publisher_public_key: bytes
    record: MutableRecord

    @property
    def target_hex(self) -> str:
        return self.record.target_hex

    def verify(self) -> bool:
        return self.record.verify()


def make_sync_head_record(
    *,
    keypair: DhtKeypair,
    kind: HeadKind,
    collection: bytes,
    pointer: bytes,
    pointer_kind: str,
    seq: int,
    now: int,
    writer_public_key: bytes = b"",
    epoch: int = 0,
    ttl: int = 2 * 60 * 60,
) -> SyncMutableHead:
    if len(collection) != 32:
        raise ValueError("collection must be 32 bytes")
    if not pointer:
        raise ValueError("pointer must not be empty")
    value: dict[bytes, BValue] = {
        b"kind": kind.value,
        b"collection": collection,
        b"pointer": pointer,
        b"pointer_kind": pointer_kind,
        b"epoch": epoch,
    }
    if writer_public_key:
        value[b"writer"] = writer_public_key
    if len(bencode(value)) > MAX_SYNC_HEAD_VALUE_BYTES:
        raise ValueError("sync head value too large for mutable DHT slot")
    salt = head_salt(collection, kind, writer_public_key=writer_public_key)
    record = MutableRecord.create(
        keypair=keypair,
        seq=seq,
        value=value,
        salt=salt,
        kind=f"sync.{kind.value}",
        now=now,
        ttl=ttl,
    )
    return SyncMutableHead(
        kind=kind,
        collection=collection,
        pointer=pointer,
        pointer_kind=pointer_kind,
        seq=seq,
        publisher_public_key=keypair.public_key_bytes,
        record=record,
    )


def make_writer_feed_head(*, writer_keypair: DhtKeypair, entry: FeedEntry, now: int) -> SyncMutableHead:
    return make_sync_head_record(
        keypair=writer_keypair,
        kind=HeadKind.WRITER_FEED_TIP,
        collection=entry.collection,
        pointer=entry.entry_hash,
        pointer_kind="feed_entry_hash",
        seq=entry.index,
        now=now,
        writer_public_key=writer_keypair.public_key_bytes,
    )


def make_snapshot_head(*, owner_keypair: DhtKeypair, manifest: SnapshotManifest, seq: int, now: int) -> SyncMutableHead:
    return make_sync_head_record(
        keypair=owner_keypair,
        kind=HeadKind.SNAPSHOT_ROOT,
        collection=manifest.collection,
        pointer=manifest.root_hash,
        pointer_kind="snapshot_root_hash",
        seq=seq,
        now=now,
    )


def make_roster_head(*, owner_keypair: DhtKeypair, collection: bytes, grants: Iterable[WriterGrant], seq: int, now: int) -> SyncMutableHead:
    grant_values = []
    for grant in grants:
        if not grant.verify():
            raise ValueError("cannot publish roster containing invalid writer grant")
        grant_values.append(grant.roster_value())
    # The roster head is intentionally only a compact head. Large rosters should
    # point to a manifest or feed of grants; this direct form is useful for tiny groups/tests.
    value = bencode({b"grants": grant_values})
    pointer = sha256(SYNC_DOMAIN + b"roster-direct:" + value)
    return make_sync_head_record(
        keypair=owner_keypair,
        kind=HeadKind.WRITER_ROSTER,
        collection=collection,
        pointer=pointer,
        pointer_kind="writer_roster_digest",
        seq=seq,
        now=now,
    )


@dataclass(frozen=True)
class SyncConflictGuess:
    path: str
    left_hash: bytes
    right_hash: bytes
    strategy: str

    def user_visible_name(self) -> str:
        return f"{self.path}.conflict.{self.left_hash.hex()[:8]}.{self.right_hash.hex()[:8]}"


def guess_conflict_strategy(left: FileVersion, right: FileVersion) -> SyncConflictGuess | None:
    if left.path != right.path:
        return None
    if left.version_hash == right.version_hash:
        return None
    if left.deleted and not right.deleted:
        strategy = "preserve_right_and_tombstone_left"
    elif right.deleted and not left.deleted:
        strategy = "preserve_left_and_tombstone_right"
    else:
        strategy = "preserve_both_conflict_copies"
    return SyncConflictGuess(left.path, left.version_hash, right.version_hash, strategy)


@dataclass(frozen=True)
class SyncGardenBudget:
    storage_mb: int
    ram_mb: int
    upload_kib_s: int
    max_watched_heads: int
    max_cached_blocks: int
    uptime_hours: int


@dataclass(frozen=True)
class SyncGardenPlan:
    services: tuple[GardenSyncService, ...]
    reasons: tuple[str, ...]
    max_metadata_posture: str

    def has(self, service: GardenSyncService) -> bool:
        return service in self.services


def plan_sync_garden_services(budget: SyncGardenBudget) -> SyncGardenPlan:
    services: list[GardenSyncService] = []
    reasons: list[str] = []
    metadata = "head-only"

    if budget.max_watched_heads >= 100 and budget.ram_mb >= 256:
        services.append(GardenSyncService.HEAD_WATCHER)
        services.append(GardenSyncService.ROSTER_WITNESS)
        reasons.append("can watch mutable sync heads and roster changes")

    if budget.upload_kib_s >= 256 and budget.uptime_hours >= 8:
        services.append(GardenSyncService.FEED_RELAY)
        services.append(GardenSyncService.WAKE_RENDEZVOUS)
        reasons.append("has enough upload and uptime to reconnect intermittent peers")

    if budget.storage_mb >= 1024 and budget.max_cached_blocks >= 1000:
        services.append(GardenSyncService.BLOCK_CACHE)
        services.append(GardenSyncService.SNAPSHOT_MIRROR)
        metadata = "encrypted-block-and-manifest-cache"
        reasons.append("can cache encrypted blocks and compact snapshot manifests")

    if budget.storage_mb >= 16_384 and budget.uptime_hours >= 16:
        services.append(GardenSyncService.ERASURE_SHARE_KEEPER)
        services.append(GardenSyncService.TOMBSTONE_KEEPER)
        reasons.append("can hold longer-lived shares and deletion history")

    if budget.ram_mb >= 1024 and budget.upload_kib_s >= 1024:
        services.append(GardenSyncService.DIFF_HINTER)
        reasons.append("can compute coarse diff hints without becoming source of truth")

    # Preserve order while removing duplicates.
    unique = tuple(dict.fromkeys(services))
    return SyncGardenPlan(unique, tuple(reasons), metadata)


def mutasync_guardrails() -> tuple[str, ...]:
    return (
        "dht_is_control_plane_not_file_store",
        "mutable_heads_are_signed_not_voted",
        "multiwriter_sync_uses_per_writer_feeds_not_shared_write_slot",
        "garden_nodes_may_cache_but_cannot_author_changes",
        "readers_can_provide_blocks_without_write_authority",
        "conflicts_are_preserved_not_silently_resolved",
        "large_manifests_live_as_content_addressed_blocks_not_mutable_values",
    )
