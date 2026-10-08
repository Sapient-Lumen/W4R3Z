"""Sovereignty entrance records for an I2P DHT.

This module models the future application-facing doorway: a normal client can
publish or hand peers a compact, signed contact card containing an I2P
Destination, a DHT public key, a node id, and a few bootstrap hints.  The card
is deliberately app-generic, but it was born from the observation that a large
legacy P2P network can become a resilience ramp if every willing client becomes
an entrance distributor instead of depending forever on central entrances.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Iterable

from .bencode import bencode
from .identity import DhtKeypair, NodeIdentity, verify_signature
from .ids import DOMAIN, key_id

MAX_CAPABILITIES = 32
MAX_HINT_BYTES = 768
MAX_CONTEXT_BYTES = 256
CONTACT_CARD_DOMAIN = DOMAIN + b":sovereign-contact-card-v1:"


class EntranceChannel(str, Enum):
    """Ways an already-running social/client network can leak entrances."""

    DIRECT_INVITE = "direct_invite"
    BUDDY_EXCHANGE = "buddy_exchange"
    ROOM_GOSSIP = "room_gossip"
    SEARCH_RESULT_HINT = "search_result_hint"
    CENTRAL_SERVER_SIDELOAD = "central_server_sideload"
    PUBLIC_SEED_LIST = "public_seed_list"
    GARDEN_SEED_GATE = "garden_seed_gate"
    CACHED_LAST_GOOD = "cached_last_good"


class ParticipationMode(str, Enum):
    OFF = "off"
    CLASSIC_ONLY = "classic_only"
    HYBRID_ENTRANCE = "hybrid_entrance"
    I2P_ONLY = "i2p_only"
    GARDEN = "garden"


class MetadataPosture(str, Enum):
    MINIMAL = "minimal"
    CONNECTIVE = "connective"
    INDEX_HELPER = "index_helper"
    BRIDGE_HELPER = "bridge_helper"


@dataclass(frozen=True)
class ContactCard:
    """Signed entrance card.

    The signer is the DHT public key carried in the card.  The I2P Destination is
    transport reachability; the DHT public key is application identity; the node
    id is recomputed from the identity to prevent arbitrary node-id selection.
    """

    destination: str
    public_key: bytes
    node_id: bytes
    work_nonce: bytes
    issued_at: int
    expires_at: int
    capabilities: tuple[str, ...] = ()
    context: str = "generic-i2p-dht"
    bootstrap_hints: dict[str, str] = field(default_factory=dict)
    previous_card_hash: bytes = b""
    signature: bytes = b""

    @classmethod
    def create(
        cls,
        *,
        identity: NodeIdentity,
        keypair: DhtKeypair,
        issued_at: int | None = None,
        ttl: int = 48 * 60 * 60,
        capabilities: Iterable[str] = (),
        context: str = "generic-i2p-dht",
        bootstrap_hints: dict[str, str] | None = None,
        previous_card_hash: bytes = b"",
    ) -> "ContactCard":
        if keypair.public_key_bytes != identity.public_key:
            raise ValueError("keypair does not match identity public key")
        if issued_at is None:
            issued_at = int(time.time())
        card = cls(
            destination=identity.destination,
            public_key=identity.public_key,
            node_id=identity.node_id,
            work_nonce=identity.work_nonce,
            issued_at=issued_at,
            expires_at=issued_at + ttl,
            capabilities=tuple(sorted(set(capabilities))),
            context=context,
            bootstrap_hints=dict(bootstrap_hints or {}),
            previous_card_hash=previous_card_hash,
        )
        return replace(card, signature=keypair.sign(card.unsigned_payload()))

    def unsigned_payload(self) -> bytes:
        if len(self.capabilities) > MAX_CAPABILITIES:
            raise ValueError("too many contact-card capabilities")
        hints = {key.encode("utf-8"): value.encode("utf-8") for key, value in self.bootstrap_hints.items()}
        payload = {
            b"destination": self.destination.encode("utf-8"),
            b"public_key": self.public_key,
            b"node_id": self.node_id,
            b"work_nonce": self.work_nonce,
            b"issued_at": self.issued_at,
            b"expires_at": self.expires_at,
            b"capabilities": tuple(cap.encode("utf-8") for cap in self.capabilities),
            b"context": self.context.encode("utf-8"),
            b"bootstrap_hints": hints,
            b"previous_card_hash": self.previous_card_hash,
        }
        encoded = CONTACT_CARD_DOMAIN + bencode(payload)
        if len(encoded) > MAX_HINT_BYTES + 512:
            raise ValueError("contact-card payload too large")
        return encoded

    @property
    def card_hash(self) -> bytes:
        return key_id("contact-card", self.unsigned_payload() + self.signature)

    @property
    def target(self) -> bytes:
        return key_id("contact-card-target", self.node_id)

    @property
    def age_bound_seconds(self) -> int:
        return max(0, self.expires_at - self.issued_at)

    def is_expired(self, *, now: int | None = None) -> bool:
        if now is None:
            now = int(time.time())
        return now >= self.expires_at

    def verify(self, *, now: int | None = None, max_ttl: int = 7 * 24 * 3600) -> bool:
        if len(self.public_key) != 32 or len(self.node_id) != 32:
            return False
        recomputed = NodeIdentity(self.destination, self.public_key, self.work_nonce).node_id
        if recomputed != self.node_id:
            return False
        if self.issued_at < 0 or self.expires_at <= self.issued_at or self.age_bound_seconds > max_ttl:
            return False
        if self.is_expired(now=now):
            return False
        if len(bencode({k.encode(): v.encode() for k, v in self.bootstrap_hints.items()})) > MAX_HINT_BYTES:
            return False
        if len(self.context.encode("utf-8")) > MAX_CONTEXT_BYTES:
            return False
        return verify_signature(self.public_key, self.unsigned_payload(), self.signature)

    def has_capability(self, capability: str) -> bool:
        return capability in self.capabilities


@dataclass(frozen=True)
class EntrancePolicy:
    """Local policy for how aggressively a client should distribute entrances."""

    mode: ParticipationMode
    metadata_posture: MetadataPosture = MetadataPosture.MINIMAL
    max_room_gossip_per_hour: int = 2
    max_search_hint_per_hour: int = 6
    require_user_visible_opt_in: bool = True
    allow_central_side_load: bool = True
    allow_i2p_only_start: bool = False

    def allowed_channels(self) -> tuple[EntranceChannel, ...]:
        if self.mode in {ParticipationMode.OFF, ParticipationMode.CLASSIC_ONLY}:
            return ()
        channels = {EntranceChannel.DIRECT_INVITE, EntranceChannel.CACHED_LAST_GOOD, EntranceChannel.GARDEN_SEED_GATE}
        if self.mode in {ParticipationMode.HYBRID_ENTRANCE, ParticipationMode.GARDEN}:
            channels.update({EntranceChannel.BUDDY_EXCHANGE, EntranceChannel.ROOM_GOSSIP})
            if self.allow_central_side_load:
                channels.add(EntranceChannel.CENTRAL_SERVER_SIDELOAD)
            if self.metadata_posture in {MetadataPosture.CONNECTIVE, MetadataPosture.INDEX_HELPER, MetadataPosture.BRIDGE_HELPER}:
                channels.add(EntranceChannel.SEARCH_RESULT_HINT)
        if self.mode is ParticipationMode.I2P_ONLY:
            channels.update({EntranceChannel.PUBLIC_SEED_LIST, EntranceChannel.DIRECT_INVITE})
        if self.mode is ParticipationMode.GARDEN:
            channels.add(EntranceChannel.PUBLIC_SEED_LIST)
        return tuple(sorted(channels, key=lambda c: c.value))


@dataclass(frozen=True)
class EntranceReadiness:
    ready: bool
    reason: str
    distinct_contacts: int
    distinct_gardens: int
    distinct_channels: int
    freshest_age_seconds: int | None


def assess_i2p_only_readiness(
    cards: Iterable[ContactCard],
    *,
    now: int,
    min_contacts: int = 16,
    min_gardens: int = 2,
    min_channels: int = 3,
    max_freshest_age_seconds: int = 36 * 3600,
) -> EntranceReadiness:
    """Decide whether default-off I2P-only startup is sane for this local cache."""

    valid = [card for card in cards if card.verify(now=now)]
    node_ids = {card.node_id for card in valid}
    gardens = {card.node_id for card in valid if card.has_capability("garden") or card.has_capability("seed_gate")}
    channels = {
        value
        for card in valid
        for key, value in card.bootstrap_hints.items()
        if key in {"channel", "entrance_channel"}
    }
    freshest = min((now - card.issued_at for card in valid), default=None)

    if len(node_ids) < min_contacts:
        return EntranceReadiness(False, "too_few_distinct_contacts", len(node_ids), len(gardens), len(channels), freshest)
    if len(gardens) < min_gardens:
        return EntranceReadiness(False, "too_few_garden_entrances", len(node_ids), len(gardens), len(channels), freshest)
    if len(channels) < min_channels:
        return EntranceReadiness(False, "too_few_entrance_channels", len(node_ids), len(gardens), len(channels), freshest)
    if freshest is None or freshest > max_freshest_age_seconds:
        return EntranceReadiness(False, "cache_stale", len(node_ids), len(gardens), len(channels), freshest)
    return EntranceReadiness(True, "ready_for_i2p_only_start", len(node_ids), len(gardens), len(channels), freshest)


@dataclass(frozen=True)
class EntranceReceipt:
    channel: EntranceChannel
    target_node_id: bytes
    accepted: bool
    reason: str
    at: int


class EntranceCache:
    """Small local cache that favors fresh, diverse, signed entrance cards."""

    def __init__(self, *, max_cards: int = 512) -> None:
        if max_cards < 1:
            raise ValueError("max_cards must be positive")
        self.max_cards = max_cards
        self._cards: dict[bytes, ContactCard] = {}
        self.receipts: list[EntranceReceipt] = []

    @property
    def cards(self) -> tuple[ContactCard, ...]:
        return tuple(sorted(self._cards.values(), key=lambda c: (c.expires_at, c.node_id), reverse=True))

    def add(self, card: ContactCard, *, channel: EntranceChannel, now: int) -> EntranceReceipt:
        if not card.verify(now=now):
            receipt = EntranceReceipt(channel, card.node_id, False, "invalid_contact_card", now)
            self.receipts.append(receipt)
            return receipt
        old = self._cards.get(card.node_id)
        if old is not None and old.issued_at > card.issued_at:
            receipt = EntranceReceipt(channel, card.node_id, False, "older_than_cached_card", now)
            self.receipts.append(receipt)
            return receipt
        self._cards[card.node_id] = card
        if len(self._cards) > self.max_cards:
            ordered = sorted(self._cards.values(), key=lambda c: (c.expires_at, c.issued_at), reverse=True)
            self._cards = {card.node_id: card for card in ordered[: self.max_cards]}
        receipt = EntranceReceipt(channel, card.node_id, True, "accepted", now)
        self.receipts.append(receipt)
        return receipt

    def bootstrap_portfolio(self, *, now: int, limit: int = 64) -> tuple[ContactCard, ...]:
        valid = [card for card in self.cards if card.verify(now=now)]
        garden_first = sorted(
            valid,
            key=lambda card: (
                not (card.has_capability("garden") or card.has_capability("seed_gate")),
                -(card.issued_at),
                card.node_id,
            ),
        )
        return tuple(garden_first[:limit])
