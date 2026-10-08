"""Protocol negotiation pressure before live I2P/SAM side effects.

A future DHT node will need to decide whether another node speaks the same
wire/version/features before spending SAM streams, metadata budget, or sticky
peer-state.  rev0033 turns that into a local signed pressure surface instead
of treating negotiation as a friendly prelude.

This is not a production handshake.  It is a deterministic seam for downgrade,
policy-digest, feature, replay, fork, and stale-offer tests.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256

NEGOTIATION_DOMAIN = DOMAIN + b":negotiation-lane-v1:"
ZERO_DIGEST = b"\x00" * 32


class NegotiationDecisionKind(str, Enum):
    ACCEPT_NEGOTIATION = "accept_negotiation"
    ACCEPT_WITH_WATCH = "accept_with_watch"
    HOLD_NO_SHARED_VERSION = "hold_no_shared_version"
    HOLD_NO_SHARED_FEATURES = "hold_no_shared_features"
    QUARANTINE_BAD_OFFER_SIGNATURE = "quarantine_bad_offer_signature"
    QUARANTINE_BAD_SELECTION_SIGNATURE = "quarantine_bad_selection_signature"
    QUARANTINE_EXPIRED_OFFER = "quarantine_expired_offer"
    QUARANTINE_EXPIRED_SELECTION = "quarantine_expired_selection"
    QUARANTINE_REPLAYED_OFFER = "quarantine_replayed_offer"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_POLICY_DIGEST_MISMATCH = "quarantine_policy_digest_mismatch"
    QUARANTINE_REQUIRED_FEATURE_MISSING = "quarantine_required_feature_missing"
    QUARANTINE_FORBIDDEN_FEATURE = "quarantine_forbidden_feature"
    QUARANTINE_DOWNGRADE = "quarantine_downgrade"
    QUARANTINE_SELECTION_OFFER_MISMATCH = "quarantine_selection_offer_mismatch"
    QUARANTINE_SELECTION_VERSION_MISMATCH = "quarantine_selection_version_mismatch"
    QUARANTINE_SELECTION_FEATURE_MISMATCH = "quarantine_selection_feature_mismatch"
    QUARANTINE_FRAME_BUDGET_TOO_SMALL = "quarantine_frame_budget_too_small"


@dataclass(frozen=True)
class NegotiationPolicy:
    min_version: int = 1
    max_version: int = 1
    required_features: tuple[str, ...] = ()
    forbidden_features: tuple[str, ...] = ()
    min_frame_bytes: int = 1024
    require_highest_shared_version: bool = True
    allow_watch_without_selection: bool = False

    def validate(self) -> None:
        if self.min_version <= 0 or self.max_version < self.min_version:
            raise ValueError("negotiation version window is invalid")
        if self.min_frame_bytes <= 0:
            raise ValueError("min_frame_bytes must be positive")


@dataclass(frozen=True)
class ProtocolOffer:
    actor_public_key: bytes
    node_id: bytes
    source_family: str
    path_family: str
    versions: tuple[int, ...]
    features: tuple[str, ...]
    required_features: tuple[str, ...]
    namespace_policy_digest: bytes
    max_frame_bytes: int
    sequence: int
    issued_at: int
    expires_at: int
    signature: bytes = b""

    def __post_init__(self) -> None:
        for name, value in (("actor_public_key", self.actor_public_key), ("node_id", self.node_id), ("namespace_policy_digest", self.namespace_policy_digest)):
            if len(value) != 32:
                raise ValueError(f"protocol offer {name} must be 32 bytes")
        if not self.source_family or not self.path_family:
            raise ValueError("protocol offer requires source/path families")
        if not self.versions or any(v <= 0 for v in self.versions):
            raise ValueError("protocol offer needs positive versions")
        if len(set(self.versions)) != len(self.versions):
            raise ValueError("protocol offer versions must be unique")
        if not self.features:
            raise ValueError("protocol offer needs at least one feature")
        if not set(self.required_features).issubset(set(self.features)):
            raise ValueError("required features must be included in feature set")
        if self.max_frame_bytes <= 0 or self.sequence < 0:
            raise ValueError("protocol offer frame budget/sequence must be positive/non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("protocol offer expiry must follow issue time")
        if self.signature and len(self.signature) != 64:
            raise ValueError("protocol offer signature must be empty or 64 bytes")

    @classmethod
    def create(
        cls,
        *,
        keypair: DhtKeypair,
        node_id: bytes,
        source_family: str,
        path_family: str,
        versions: Iterable[int],
        features: Iterable[str],
        required_features: Iterable[str],
        namespace_policy_digest: bytes,
        max_frame_bytes: int,
        sequence: int,
        issued_at: int,
        ttl: int,
    ) -> "ProtocolOffer":
        if ttl <= 0:
            raise ValueError("protocol offer ttl must be positive")
        unsigned = cls(
            actor_public_key=keypair.public_key_bytes,
            node_id=node_id,
            source_family=source_family,
            path_family=path_family,
            versions=tuple(sorted(set(versions))),
            features=tuple(sorted(set(features))),
            required_features=tuple(sorted(set(required_features))),
            namespace_policy_digest=namespace_policy_digest,
            max_frame_bytes=max_frame_bytes,
            sequence=sequence,
            issued_at=issued_at,
            expires_at=issued_at + ttl,
        )
        return replace(unsigned, signature=keypair.sign(unsigned.unsigned_payload()))

    def live(self, *, now: int) -> bool:
        return self.issued_at <= now < self.expires_at

    @property
    def offer_digest(self) -> bytes:
        return sha256(NEGOTIATION_DOMAIN + b":offer:" + self.unsigned_payload() + self.signature)

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"actor": self.actor_public_key,
            b"node": self.node_id,
            b"source_family": self.source_family,
            b"path_family": self.path_family,
            b"versions": list(self.versions),
            b"features": list(self.features),
            b"required_features": list(self.required_features),
            b"policy": self.namespace_policy_digest,
            b"max_frame_bytes": self.max_frame_bytes,
            b"sequence": self.sequence,
            b"issued_at": self.issued_at,
            b"expires_at": self.expires_at,
        }

    def unsigned_payload(self) -> bytes:
        return NEGOTIATION_DOMAIN + b":offer-unsigned:" + bencode(self.unsigned_bvalue())

    def verify(self) -> bool:
        return verify_signature(self.actor_public_key, self.unsigned_payload(), self.signature)


@dataclass(frozen=True)
class ProtocolSelection:
    selector_public_key: bytes
    request_id: bytes
    local_offer_digest: bytes
    remote_offer_digest: bytes
    chosen_version: int
    chosen_features: tuple[str, ...]
    namespace_policy_digest: bytes
    sequence: int
    issued_at: int
    expires_at: int
    signature: bytes = b""

    def __post_init__(self) -> None:
        for name, value in (
            ("selector_public_key", self.selector_public_key),
            ("request_id", self.request_id),
            ("local_offer_digest", self.local_offer_digest),
            ("remote_offer_digest", self.remote_offer_digest),
            ("namespace_policy_digest", self.namespace_policy_digest),
        ):
            if len(value) != 32:
                raise ValueError(f"protocol selection {name} must be 32 bytes")
        if self.chosen_version <= 0 or self.sequence < 0:
            raise ValueError("protocol selection version/sequence must be positive/non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("protocol selection expiry must follow issue time")
        if self.signature and len(self.signature) != 64:
            raise ValueError("protocol selection signature must be empty or 64 bytes")

    @classmethod
    def create(
        cls,
        *,
        keypair: DhtKeypair,
        request_id: bytes,
        local_offer: ProtocolOffer,
        remote_offer: ProtocolOffer,
        chosen_version: int,
        chosen_features: Iterable[str],
        sequence: int,
        issued_at: int,
        ttl: int,
    ) -> "ProtocolSelection":
        if ttl <= 0:
            raise ValueError("protocol selection ttl must be positive")
        unsigned = cls(
            selector_public_key=keypair.public_key_bytes,
            request_id=request_id,
            local_offer_digest=local_offer.offer_digest,
            remote_offer_digest=remote_offer.offer_digest,
            chosen_version=chosen_version,
            chosen_features=tuple(sorted(set(chosen_features))),
            namespace_policy_digest=local_offer.namespace_policy_digest,
            sequence=sequence,
            issued_at=issued_at,
            expires_at=issued_at + ttl,
        )
        return replace(unsigned, signature=keypair.sign(unsigned.unsigned_payload()))

    def live(self, *, now: int) -> bool:
        return self.issued_at <= now < self.expires_at

    @property
    def selection_digest(self) -> bytes:
        return sha256(NEGOTIATION_DOMAIN + b":selection:" + self.unsigned_payload() + self.signature)

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"selector": self.selector_public_key,
            b"request": self.request_id,
            b"local_offer": self.local_offer_digest,
            b"remote_offer": self.remote_offer_digest,
            b"version": self.chosen_version,
            b"features": list(self.chosen_features),
            b"policy": self.namespace_policy_digest,
            b"sequence": self.sequence,
            b"issued_at": self.issued_at,
            b"expires_at": self.expires_at,
        }

    def unsigned_payload(self) -> bytes:
        return NEGOTIATION_DOMAIN + b":selection-unsigned:" + bencode(self.unsigned_bvalue())

    def verify(self) -> bool:
        return verify_signature(self.selector_public_key, self.unsigned_payload(), self.signature)


@dataclass(frozen=True)
class NegotiationReport:
    decision_kind: NegotiationDecisionKind
    accept: bool
    reason: str
    chosen_version: int
    chosen_features: tuple[str, ...]
    offer_digests: tuple[bytes, ...]
    selection_digest: bytes
    source_families: tuple[str, ...]
    path_families: tuple[str, ...]
    pressure_digests: tuple[bytes, ...]
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _report(
    kind: NegotiationDecisionKind,
    accept: bool,
    reason: str,
    offers: tuple[ProtocolOffer, ...],
    *,
    selection: ProtocolSelection | None = None,
    chosen_version: int = 0,
    chosen_features: Iterable[str] = (),
    pressures: Iterable[bytes] = (),
) -> NegotiationReport:
    offer_digests = tuple(sorted({offer.offer_digest for offer in offers}))
    source_families = tuple(sorted({offer.source_family for offer in offers}))
    path_families = tuple(sorted({offer.path_family for offer in offers}))
    feature_t = tuple(sorted(set(chosen_features)))
    pressure_t = tuple(sorted(set(pressures)))
    selection_digest = ZERO_DIGEST if selection is None else selection.selection_digest
    digest = sha256(NEGOTIATION_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"reason": reason,
        b"version": chosen_version,
        b"features": list(feature_t),
        b"offers": list(offer_digests),
        b"selection": selection_digest,
        b"sources": list(source_families),
        b"paths": list(path_families),
        b"pressures": list(pressure_t),
    }))
    return NegotiationReport(kind, accept, reason, chosen_version, feature_t, offer_digests, selection_digest, source_families, path_families, pressure_t, digest)


def assess_protocol_negotiation(
    local_offer: ProtocolOffer,
    remote_offer: ProtocolOffer,
    *,
    now: int,
    selection: ProtocolSelection | None = None,
    policy: NegotiationPolicy | None = None,
) -> NegotiationReport:
    policy = policy or NegotiationPolicy()
    policy.validate()
    offers = (local_offer, remote_offer)

    for offer in offers:
        if not offer.verify():
            return _report(NegotiationDecisionKind.QUARANTINE_BAD_OFFER_SIGNATURE, False, "bad offer signature", offers, pressures=(offer.offer_digest,))
        if not offer.live(now=now):
            return _report(NegotiationDecisionKind.QUARANTINE_EXPIRED_OFFER, False, "expired offer", offers, pressures=(offer.offer_digest,))
    if local_offer.offer_digest == remote_offer.offer_digest:
        return _report(NegotiationDecisionKind.QUARANTINE_REPLAYED_OFFER, False, "same signed offer replayed as both sides", offers, pressures=(local_offer.offer_digest,))
    if local_offer.actor_public_key == remote_offer.actor_public_key and local_offer.sequence == remote_offer.sequence and local_offer.offer_digest != remote_offer.offer_digest:
        return _report(NegotiationDecisionKind.QUARANTINE_SEQUENCE_FORK, False, "same actor sequence has different offer digest", offers, pressures=(local_offer.offer_digest, remote_offer.offer_digest))
    if local_offer.namespace_policy_digest != remote_offer.namespace_policy_digest:
        return _report(NegotiationDecisionKind.QUARANTINE_POLICY_DIGEST_MISMATCH, False, "namespace policy digests differ", offers)
    if min(local_offer.max_frame_bytes, remote_offer.max_frame_bytes) < policy.min_frame_bytes:
        return _report(NegotiationDecisionKind.QUARANTINE_FRAME_BUDGET_TOO_SMALL, False, "negotiated frame budget too small", offers)

    shared_versions = sorted(v for v in set(local_offer.versions).intersection(remote_offer.versions) if policy.min_version <= v <= policy.max_version)
    if not shared_versions:
        return _report(NegotiationDecisionKind.HOLD_NO_SHARED_VERSION, False, "no shared protocol version", offers)
    expected_version = shared_versions[-1]

    available_features = set(local_offer.features).intersection(remote_offer.features)
    required = set(policy.required_features).union(local_offer.required_features).union(remote_offer.required_features)
    forbidden = set(policy.forbidden_features)
    if not available_features:
        return _report(NegotiationDecisionKind.HOLD_NO_SHARED_FEATURES, False, "no shared feature set", offers, chosen_version=expected_version)
    missing = required.difference(available_features)
    if missing:
        pressure = tuple(sha256(NEGOTIATION_DOMAIN + b":missing-feature:" + item.encode("utf-8")) for item in sorted(missing))
        return _report(NegotiationDecisionKind.QUARANTINE_REQUIRED_FEATURE_MISSING, False, "required feature missing", offers, chosen_version=expected_version, pressures=pressure)
    if forbidden.intersection(available_features):
        pressure = tuple(sha256(NEGOTIATION_DOMAIN + b":forbidden-feature:" + item.encode("utf-8")) for item in sorted(forbidden.intersection(available_features)))
        return _report(NegotiationDecisionKind.QUARANTINE_FORBIDDEN_FEATURE, False, "forbidden feature negotiated", offers, chosen_version=expected_version, pressures=pressure)

    default_features = tuple(sorted(required if required else available_features))
    if selection is None:
        if policy.allow_watch_without_selection:
            return _report(NegotiationDecisionKind.ACCEPT_WITH_WATCH, True, "shared features/version but no signed selection", offers, chosen_version=expected_version, chosen_features=default_features)
        return _report(NegotiationDecisionKind.ACCEPT_NEGOTIATION, True, "shared features/version", offers, chosen_version=expected_version, chosen_features=default_features)

    if not selection.verify():
        return _report(NegotiationDecisionKind.QUARANTINE_BAD_SELECTION_SIGNATURE, False, "bad selection signature", offers, selection=selection, chosen_version=expected_version, pressures=(selection.selection_digest,))
    if not selection.live(now=now):
        return _report(NegotiationDecisionKind.QUARANTINE_EXPIRED_SELECTION, False, "expired selection", offers, selection=selection, chosen_version=expected_version, pressures=(selection.selection_digest,))
    if selection.local_offer_digest != local_offer.offer_digest or selection.remote_offer_digest != remote_offer.offer_digest:
        return _report(NegotiationDecisionKind.QUARANTINE_SELECTION_OFFER_MISMATCH, False, "selection is not bound to these offers", offers, selection=selection, chosen_version=expected_version)
    if selection.namespace_policy_digest != local_offer.namespace_policy_digest:
        return _report(NegotiationDecisionKind.QUARANTINE_POLICY_DIGEST_MISMATCH, False, "selection policy digest mismatch", offers, selection=selection, chosen_version=expected_version)
    if policy.require_highest_shared_version and selection.chosen_version != expected_version:
        return _report(NegotiationDecisionKind.QUARANTINE_DOWNGRADE, False, "selection chose a lower version than highest shared", offers, selection=selection, chosen_version=selection.chosen_version, chosen_features=selection.chosen_features)
    if selection.chosen_version not in shared_versions:
        return _report(NegotiationDecisionKind.QUARANTINE_SELECTION_VERSION_MISMATCH, False, "selection chose an unshared version", offers, selection=selection, chosen_version=selection.chosen_version, chosen_features=selection.chosen_features)
    chosen = set(selection.chosen_features)
    if not required.issubset(chosen) or not chosen.issubset(available_features):
        return _report(NegotiationDecisionKind.QUARANTINE_SELECTION_FEATURE_MISMATCH, False, "selection feature set is not required-subset/available-subset", offers, selection=selection, chosen_version=selection.chosen_version, chosen_features=selection.chosen_features)
    return _report(NegotiationDecisionKind.ACCEPT_NEGOTIATION, True, "signed selection accepted", offers, selection=selection, chosen_version=selection.chosen_version, chosen_features=selection.chosen_features)
