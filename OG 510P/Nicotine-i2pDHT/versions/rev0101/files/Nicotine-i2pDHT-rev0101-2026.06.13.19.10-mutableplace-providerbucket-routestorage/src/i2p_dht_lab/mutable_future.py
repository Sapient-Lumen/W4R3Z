
"""Open questions and mutable-head dreams for the I2P DHT lab.

The DHT's core claim is no longer merely "store mutable values".  The deeper
claim is that small, signed mutable heads can become a durable control plane for
entrance portfolios, policy capsules, garden catalogs, sync rosters, software
update channels, mutable torrents, and local-first collaboration systems.

This module keeps the guesses executable without pretending they are production
protocols.  It models two concrete mutable-head families:

* seed portfolios: compact, signed lists of entrance/contact-card references;
* policy portfolios: compact, signed lists of subjective policy capsule refs.

It also models a head-observation cache for the two ugly mutability problems:
rollback/staleness and equivocation/forks.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .governance import PolicyCapsule
from .identity import DhtKeypair
from .ids import DOMAIN, key_id, sha256
from .mutable import MAX_SALT_BYTES, MAX_VALUE_BYTES, MutableRecord
from .sovereignty import ContactCard

FUTURE_DOMAIN = DOMAIN + b":mutable-future-v1:"
MAX_PORTFOLIO_ENTRIES = 48
MAX_POLICY_POINTERS = 256


class QuestionPressure(str, Enum):
    FOUNDATION = "foundation"
    SECURITY = "security"
    PERFORMANCE = "performance"
    GOVERNANCE = "governance"
    PRIVACY = "privacy"
    PRODUCT = "product"


class MutableDreamKind(str, Enum):
    SEED_PORTFOLIO = "seed_portfolio"
    POLICY_PORTFOLIO = "policy_portfolio"
    GARDEN_CATALOG = "garden_catalog"
    MUTABLE_TORRENT = "mutable_torrent"
    FLOSS_SYNC = "floss_sync"
    WRITER_ROSTER = "writer_roster"
    SOFTWARE_UPDATE = "software_update"
    ROOM_OR_GROUP_HEAD = "room_or_group_head"
    SEARCH_INDEX_HEAD = "search_index_head"
    TRANSPARENCY_WITNESS = "transparency_witness"
    WAKE_COURIER = "wake_courier"
    CAPABILITY_REVOCATION = "capability_revocation"


class HeadAlertKind(str, Enum):
    OK = "ok"
    STALE_OR_ROLLBACK = "stale_or_rollback"
    SAME_SEQUENCE_FORK = "same_sequence_fork"
    ADVANCED = "advanced"
    EXPIRED_OR_EMPTY = "expired_or_empty"


@dataclass(frozen=True)
class OpenQuestion:
    slug: str
    pressure: QuestionPressure
    question: str
    current_guess: str
    why_it_matters: str
    next_test_hint: str


@dataclass(frozen=True)
class MutableDream:
    kind: MutableDreamKind
    summary: str
    primitive: str
    why_mutability_matters: str
    garden_help: str
    danger: str


def open_question_register() -> tuple[OpenQuestion, ...]:
    """Return the rev0008 question ledger in executable form."""
    return (
        OpenQuestion(
            "identity_binding",
            QuestionPressure.FOUNDATION,
            "Should node identity be bound to the I2P Destination, a DHT Ed25519 key, or a delegated pair?",
            "Use Destination + DHT key binding for routing, but allow delegated writer keys for mutable slots.",
            "Hard binding reduces cheap node-id grinding; delegated writer keys keep app data portable across routers.",
            "Simulate destination rotation and key delegation without losing mutable heads.",
        ),
        OpenQuestion(
            "mutable_format",
            QuestionPressure.FOUNDATION,
            "Should values be bencoded, DAG-CBOR-like, or pluggable canonical codecs?",
            "Keep bencode for BEP44/BEP46-compatible heads; reserve codec tags for richer app manifests.",
            "Mutable signatures are only as deterministic as their canonical encoding.",
            "Generate cross-codec test vectors and reject ambiguous encodings.",
        ),
        OpenQuestion(
            "stale_head_memory",
            QuestionPressure.SECURITY,
            "How should clients remember the highest sequence they have seen without creating global consensus?",
            "Local monotonic memory plus garden witness receipts, never global truth.",
            "Rollback is the most ordinary mutability attack: a valid old signature can still be harmful.",
            "Feed stale heads and same-seq forks through local/garden caches under churn.",
        ),
        OpenQuestion(
            "same_seq_equivocation",
            QuestionPressure.SECURITY,
            "What happens when a publisher signs two different values at the same sequence?",
            "The slot store rejects equal-seq different values locally; garden witnesses should preserve fork evidence.",
            "Equivocation can partition users without breaking signatures.",
            "Build same-sequence fork transcript fixtures and witness receipts.",
        ),
        OpenQuestion(
            "seed_authority_shape",
            QuestionPressure.GOVERNANCE,
            "How many seed/policy authorities should a default client know?",
            "Default portfolio should be multi-headed: maintainer, community gardens, user-imported friends, cached last-good.",
            "One seed head becomes the central entrance we were trying to pay down.",
            "Run bootstrap simulations with one, three, and many seed heads under capture.",
        ),
        OpenQuestion(
            "metadata_mode_ladder",
            QuestionPressure.PRIVACY,
            "How explicit must metadata tradeoffs be for connective/search/helper modes?",
            "Expose mode ladder and make garden/search/bridge helper roles separate, named, and reversible.",
            "Power users may choose connectivity over privacy, but silent escalation would be betrayal.",
            "Map each mutable dream to visible metadata posture and opt-in threshold.",
        ),
        OpenQuestion(
            "provider_sweep_budget",
            QuestionPressure.PERFORMANCE,
            "How should provider reannounce, mutable-head republish, and garden sweeping be scheduled over I2P latency?",
            "Region sweep plus hot-key/sloppy replicas, with explicit refusal receipts under overload.",
            "Naive per-key reproviding will strand high-volume users and overload generous gardens.",
            "Measure fake-I2P latency and throughput budgets before live SAM work.",
        ),
        OpenQuestion(
            "capability_revocation",
            QuestionPressure.SECURITY,
            "Can capability delegation be useful without making revocation brittle offline?",
            "Use short-lived delegated capabilities plus mutable revocation heads and tombstone witnesses.",
            "A FLOSS sync/control layer needs delegation, but revocation is a distributed-systems tax.",
            "Model UCAN-like grants with DHT-hosted revocation heads and stale-cache behavior.",
        ),
        OpenQuestion(
            "garden_non_authority",
            QuestionPressure.GOVERNANCE,
            "How do garden nodes provide enormous value without becoming truth authorities?",
            "Make garden outputs receipts, hints, caches, witnesses, and service offers; require cross-checks for risky answers.",
            "Supernodes are good when they give capacity; bad when clients are forced to believe them.",
            "Simulate garden capture and compare single-garden vs diversified portfolio lookups.",
        ),
    )


def dream_register() -> tuple[MutableDream, ...]:
    """Return the rev0008 mutability dream ledger."""
    return (
        MutableDream(MutableDreamKind.SEED_PORTFOLIO, "Rotating entrance lists", "mutable head -> contact-card hashes", "Entrances can heal after churn without classic servers.", "Seed gates curate fresh diverse contact cards.", "A captured seed head can bias bootstrap unless portfolios are diverse."),
        MutableDream(MutableDreamKind.POLICY_PORTFOLIO, "Scoped subjective refusal lists", "mutable head -> policy capsule hashes", "Maintainers/gardens can update official defaults without changing DHT truth.", "Gardens mirror and witness policy evolution.", "Policy can become de facto central if users cannot replace it."),
        MutableDream(MutableDreamKind.GARDEN_CATALOG, "Current services and budgets", "mutable head -> signed service catalog", "A garden can change capacity/refusal semantics over time.", "Leaves know what work to ask from which garden.", "Attackers can lure users with fake capacity unless offers are locally measured."),
        MutableDream(MutableDreamKind.MUTABLE_TORRENT, "BEP46-like changing torrent heads", "public key + salt -> current infohash", "A stable name can point at changing content-addressed releases.", "Gardens cache recent heads and provider regions.", "Old valid heads can be replayed without monotonic memory."),
        MutableDream(MutableDreamKind.FLOSS_SYNC, "Open Resilio/Syncthing-shaped control plane", "collection root -> roster + feed tips + snapshot roots", "Folders, manifests, and feeds need stable names that advance.", "Gardens watch heads, cache blocks, preserve tombstones.", "Conflict/revocation rules are app-level and cannot be handwaved by the DHT."),
        MutableDream(MutableDreamKind.WRITER_ROSTER, "Multiwriter group membership", "owner head -> writer grants", "Readers need to discover who may write now.", "Roster witnesses preserve old epochs and detect rollbacks.", "Membership leaks social graph unless salted/private discovery is used."),
        MutableDream(MutableDreamKind.SOFTWARE_UPDATE, "Auditable update channels", "project key -> release manifest hash", "A project needs a stable update name with signed moving releases.", "Gardens mirror manifests and witness monotonic release history.", "Update keys become high-value targets; transparency/witnessing matters."),
        MutableDream(MutableDreamKind.ROOM_OR_GROUP_HEAD, "Private/public room directories", "group key -> invite/epoch/rendezvous pointers", "Groups need changing rendezvous without central rooms.", "Invite bridges and wake couriers help intermittent members.", "Discovery metadata can reveal group existence and membership timing."),
        MutableDream(MutableDreamKind.SEARCH_INDEX_HEAD, "Curated provider-index shards", "index key -> shard manifests", "Search indexes need curation and expiration, not just immutable blobs.", "Region gardeners keep hot shards alive and report poison.", "False-provider and censorship games become salient."),
        MutableDream(MutableDreamKind.TRANSPARENCY_WITNESS, "Small witness checkpoints", "log key -> latest signed tree/head", "Users can notice split views and rollback over time.", "Gardens preserve receipts and cross-sign observations.", "Transparency logs can become heavy or accidentally central."),
        MutableDream(MutableDreamKind.WAKE_COURIER, "Sleeping-node mailboxes", "node key -> wake/rendezvous hints", "Intermittent nodes need tiny moving hints without always being online.", "Gardens store bounded wake envelopes and useful refusals.", "Mailboxes are metadata-rich if not carefully scoped."),
        MutableDream(MutableDreamKind.CAPABILITY_REVOCATION, "Delegation and revocation heads", "capability issuer -> grant/revoke epochs", "Delegated writers/gardens need revocable authority.", "Tombstone keepers preserve revocations after churn.", "Offline revocation is intrinsically stale-prone."),
    )


def slot_salt(kind: MutableDreamKind | str, label: str) -> bytes:
    raw_kind = kind.value if isinstance(kind, MutableDreamKind) else kind
    salt = f"{raw_kind}:{label}".encode("utf-8")
    if len(salt) <= MAX_SALT_BYTES:
        return salt
    return salt[:40] + b":" + sha256(salt)[:23]


@dataclass(frozen=True)
class SeedPortfolioEntry:
    card_hash: bytes
    node_id: bytes
    channel: str
    capabilities: tuple[str, ...]
    issued_at: int
    expires_at: int
    weight: int = 1

    @classmethod
    def from_card(cls, card: ContactCard, *, channel: str, weight: int = 1) -> "SeedPortfolioEntry":
        if not card.verify(now=card.issued_at):
            raise ValueError("cannot add invalid contact card to seed portfolio")
        return cls(
            card_hash=card.card_hash,
            node_id=card.node_id,
            channel=channel,
            capabilities=tuple(sorted(card.capabilities)),
            issued_at=card.issued_at,
            expires_at=card.expires_at,
            weight=weight,
        )

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"card": self.card_hash,
            b"node": self.node_id,
            b"channel": self.channel,
            b"caps": tuple(cap.encode("utf-8") for cap in self.capabilities),
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"weight": self.weight,
        }

    @property
    def is_gardenish(self) -> bool:
        return "garden" in self.capabilities or "seed_gate" in self.capabilities


@dataclass(frozen=True)
class SeedPortfolio:
    label: str
    sequence: int
    issued_at: int
    expires_at: int
    entries: tuple[SeedPortfolioEntry, ...]
    previous_head_hash: bytes = b""
    note: str = ""

    @classmethod
    def from_cards(
        cls,
        *,
        label: str,
        sequence: int,
        cards: Iterable[ContactCard],
        channel: str,
        issued_at: int,
        ttl: int = 24 * 3600,
        previous_head_hash: bytes = b"",
        note: str = "",
        limit: int = MAX_PORTFOLIO_ENTRIES,
    ) -> "SeedPortfolio":
        entries = tuple(
            SeedPortfolioEntry.from_card(card, channel=card.bootstrap_hints.get("channel", channel))
            for card in list(cards)[:limit]
        )
        return cls(label, sequence, issued_at, issued_at + ttl, entries, previous_head_hash, note)

    def bvalue(self) -> dict[bytes, BValue]:
        if len(self.entries) > MAX_PORTFOLIO_ENTRIES:
            raise ValueError("too many seed portfolio entries")
        return {
            b"kind": b"seed_portfolio",
            b"label": self.label,
            b"seq": self.sequence,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"prev": self.previous_head_hash,
            b"note": self.note,
            b"entries": tuple(entry.bvalue() for entry in self.entries),
        }

    @property
    def digest(self) -> bytes:
        return sha256(FUTURE_DOMAIN + b":seed-portfolio:" + bencode(self.bvalue()))

    @property
    def diversity_score(self) -> int:
        channels = {entry.channel for entry in self.entries}
        gardens = sum(1 for entry in self.entries if entry.is_gardenish)
        # Deliberately simple: a portfolio with all one channel should not look healthy.
        return len(channels) * 3 + min(gardens, 8) + min(len(self.entries), 16)

    def head_value(self) -> dict[bytes, BValue]:
        """Return a mutable-head-sized value.

        Full portfolios can exceed BEP44's small mutable value budget.  When the
        manifest is too large, the mutable head becomes a compact pointer to the
        manifest digest.  That is the desired pattern: small moving heads, bulkier
        signed manifests elsewhere.
        """
        full = self.bvalue()
        if len(bencode(full)) <= MAX_VALUE_BYTES:
            merged = dict(full)
            merged[b"inline"] = 1
            return merged
        channels = tuple(sorted({entry.channel.encode("utf-8") for entry in self.entries}))
        gardens = sum(1 for entry in self.entries if entry.is_gardenish)
        return {
            b"kind": b"seed_portfolio_pointer",
            b"label": self.label,
            b"seq": self.sequence,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"prev": self.previous_head_hash,
            b"manifest_digest": self.digest,
            b"entry_count": len(self.entries),
            b"channels": channels,
            b"gardens": gardens,
            b"note": self.note,
        }

    def make_head(self, keypair: DhtKeypair, *, now: int | None = None) -> MutableRecord:
        return MutableRecord.create(
            keypair=keypair,
            seq=self.sequence,
            value=self.head_value(),
            salt=slot_salt(MutableDreamKind.SEED_PORTFOLIO, self.label),
            kind="future.seed_portfolio",
            now=now or self.issued_at,
            ttl=max(1, self.expires_at - self.issued_at),
        )


@dataclass(frozen=True)
class PolicyPointer:
    capsule_hash: bytes
    authority_public_key: bytes
    authority_name: str
    sequence: int
    scope_hint: str = "advisory"

    @classmethod
    def from_capsule(cls, capsule: PolicyCapsule, *, scope_hint: str = "advisory") -> "PolicyPointer":
        return cls(
            capsule_hash=capsule.capsule_hash,
            authority_public_key=capsule.authority_public_key,
            authority_name=capsule.authority_name,
            sequence=capsule.sequence,
            scope_hint=scope_hint,
        )

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"hash": self.capsule_hash,
            b"authority_key": self.authority_public_key,
            b"authority_name": self.authority_name,
            b"seq": self.sequence,
            b"scope": self.scope_hint,
        }


@dataclass(frozen=True)
class PolicyPortfolio:
    label: str
    sequence: int
    issued_at: int
    expires_at: int
    pointers: tuple[PolicyPointer, ...]
    previous_head_hash: bytes = b""

    def bvalue(self) -> dict[bytes, BValue]:
        if len(self.pointers) > MAX_POLICY_POINTERS:
            raise ValueError("too many policy pointers")
        return {
            b"kind": b"policy_portfolio",
            b"label": self.label,
            b"seq": self.sequence,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"prev": self.previous_head_hash,
            b"pointers": tuple(pointer.bvalue() for pointer in self.pointers),
        }

    @property
    def digest(self) -> bytes:
        return sha256(FUTURE_DOMAIN + b":policy-portfolio:" + bencode(self.bvalue()))

    def head_value(self) -> dict[bytes, BValue]:
        full = self.bvalue()
        if len(bencode(full)) <= MAX_VALUE_BYTES:
            merged = dict(full)
            merged[b"inline"] = 1
            return merged
        authorities = tuple(sorted({pointer.authority_name.encode("utf-8") for pointer in self.pointers}))
        return {
            b"kind": b"policy_portfolio_pointer",
            b"label": self.label,
            b"seq": self.sequence,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"prev": self.previous_head_hash,
            b"manifest_digest": self.digest,
            b"pointer_count": len(self.pointers),
            b"authorities": authorities,
        }

    def make_head(self, keypair: DhtKeypair, *, now: int | None = None) -> MutableRecord:
        return MutableRecord.create(
            keypair=keypair,
            seq=self.sequence,
            value=self.head_value(),
            salt=slot_salt(MutableDreamKind.POLICY_PORTFOLIO, self.label),
            kind="future.policy_portfolio",
            now=now or self.issued_at,
            ttl=max(1, self.expires_at - self.issued_at),
        )


@dataclass(frozen=True)
class HeadObservation:
    target_hex: str
    seq: int
    value_digest: bytes
    source_node_id: bytes
    observed_at: int
    signer_public_key: bytes = b""

    @classmethod
    def from_record(cls, record: MutableRecord, *, source_node_id: bytes, observed_at: int) -> "HeadObservation":
        return cls(
            target_hex=record.target_hex,
            seq=record.seq,
            value_digest=sha256(record.encoded_value),
            source_node_id=source_node_id,
            observed_at=observed_at,
            signer_public_key=record.public_key,
        )


@dataclass(frozen=True)
class HeadHealth:
    kind: HeadAlertKind
    max_seq: int | None
    distinct_value_digests_at_max: int
    stale_sources: tuple[bytes, ...]
    fork_sources: tuple[bytes, ...]
    reason: str

    @property
    def healthy(self) -> bool:
        return self.kind in {HeadAlertKind.OK, HeadAlertKind.ADVANCED}


def analyze_head_observations(
    observations: Iterable[HeadObservation],
    *,
    known_seq: int | None = None,
    known_digest: bytes | None = None,
) -> HeadHealth:
    """Classify local observations of one mutable target.

    This is not consensus.  It is a local early-warning device that says when a
    client or garden should distrust a lookup result and ask more paths.
    """
    obs = tuple(observations)
    if not obs:
        return HeadHealth(HeadAlertKind.EXPIRED_OR_EMPTY, known_seq, 0, (), (), "no_observations")
    max_seq = max(o.seq for o in obs)
    stale = tuple(o.source_node_id for o in obs if known_seq is not None and o.seq < known_seq)
    at_max = [o for o in obs if o.seq == max_seq]
    digests = {o.value_digest for o in at_max}
    fork_sources: tuple[bytes, ...] = ()
    if len(digests) > 1:
        fork_sources = tuple(o.source_node_id for o in at_max)
        return HeadHealth(HeadAlertKind.SAME_SEQUENCE_FORK, max_seq, len(digests), stale, fork_sources, "same_sequence_different_values")
    if known_seq is not None:
        if max_seq < known_seq:
            return HeadHealth(HeadAlertKind.STALE_OR_ROLLBACK, max_seq, len(digests), stale or tuple(o.source_node_id for o in obs), (), "all_observed_heads_older_than_known")
        if max_seq == known_seq and known_digest is not None and digests and next(iter(digests)) != known_digest:
            return HeadHealth(HeadAlertKind.SAME_SEQUENCE_FORK, max_seq, len(digests) + 1, stale, tuple(o.source_node_id for o in at_max), "observed_same_sequence_conflicts_with_known_digest")
        if max_seq > known_seq:
            return HeadHealth(HeadAlertKind.ADVANCED, max_seq, len(digests), stale, (), "observed_newer_head")
    if stale:
        return HeadHealth(HeadAlertKind.STALE_OR_ROLLBACK, max_seq, len(digests), stale, (), "some_sources_returned_older_than_known")
    return HeadHealth(HeadAlertKind.OK, max_seq, len(digests), (), (), "observations_consistent")
