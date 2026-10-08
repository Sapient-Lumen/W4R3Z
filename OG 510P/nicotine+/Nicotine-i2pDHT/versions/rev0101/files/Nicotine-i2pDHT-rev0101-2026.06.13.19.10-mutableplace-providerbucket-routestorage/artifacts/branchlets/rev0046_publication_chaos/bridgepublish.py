"""Public bridge publication ledger.

rev0046 treats public publication as its own risk boundary after shadow-fire.
A shadow-fire report says a side effect is locally allowed; it does not say the
public exposure payload is redacted, fresh, scoped, sequenced, or safe to keep
alive.  This module models the signed publication capsule and the local checks
before a future mutable head, seed portfolio, or public bridge catalog is
refreshed.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .ids import DOMAIN, sha256
from .identity import DhtKeypair, verify_signature
from .shadowfire import ShadowFireAction, ShadowFireReport

BRIDGE_PUBLISH_DOMAIN = DOMAIN + b":bridge-publish-v1:"
ZERO_DIGEST = b"\x00" * 32


class BridgePublishAction(str, Enum):
    PUBLIC_REFRESH = "public_refresh"
    PUBLIC_WITHDRAW = "public_withdraw"
    PUBLIC_REPAIR = "public_repair"


class ExposureClass(str, Enum):
    DIGEST_ONLY = "digest_only"
    PUBLIC_BRIDGE_TOKEN = "public_bridge_token"
    WITHDRAWAL_ONLY = "withdrawal_only"


class BridgePublishDecisionKind(str, Enum):
    ACCEPT_PUBLICATION = "accept_publication"
    ACCEPT_WITH_WATCH = "accept_with_watch"
    HOLD_SHADOW_FIRE_NOT_ACCEPTED = "hold_shadow_fire_not_accepted"
    HOLD_SHADOW_FIRE_WATCH = "hold_shadow_fire_watch"
    HOLD_WITHDRAWAL_PAYLOAD = "hold_withdrawal_payload"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_EXPIRED = "quarantine_expired"
    QUARANTINE_FUTURE = "quarantine_future"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_ROLLBACK = "quarantine_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_PROFILE_DRIFT = "quarantine_profile_drift"
    QUARANTINE_SERVICE_DRIFT = "quarantine_service_drift"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_REQUEST_DRIFT = "quarantine_request_drift"
    QUARANTINE_ACTION_DRIFT = "quarantine_action_drift"
    QUARANTINE_EPOCH_DRIFT = "quarantine_epoch_drift"
    QUARANTINE_FIRE_DIGEST_DRIFT = "quarantine_fire_digest_drift"
    QUARANTINE_RAW_EXPOSURE = "quarantine_raw_exposure"
    QUARANTINE_HARD_NEGATIVE = "quarantine_hard_negative"
    QUARANTINE_STALE_PUBLIC_REPLAY = "quarantine_stale_public_replay"


SHADOW_TO_PUBLICATION_ACTION = {
    ShadowFireAction.PUBLIC_BRIDGE_REFRESH: BridgePublishAction.PUBLIC_REFRESH,
    ShadowFireAction.PUBLIC_BRIDGE_WITHDRAW: BridgePublishAction.PUBLIC_WITHDRAW,
    ShadowFireAction.PUBLIC_BRIDGE_REPAIR: BridgePublishAction.PUBLIC_REPAIR,
}


@dataclass(frozen=True)
class BridgePublication:
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    action: BridgePublishAction
    exposure_class: ExposureClass
    epoch_digest: bytes
    shadow_fire_digest: bytes
    key_chain_digest: bytes
    public_contact_digest: bytes
    catalog_digest: bytes
    sequence: int
    previous_publication_digest: bytes
    issued_at: int
    expires_at: int
    family_id: str
    path_family: str
    signer_public_key: bytes
    redaction_label: str = "redacted-token-digest"
    signature: bytes = b""

    def __post_init__(self) -> None:
        object.__setattr__(self, "action", BridgePublishAction(self.action))
        object.__setattr__(self, "exposure_class", ExposureClass(self.exposure_class))
        if not self.profile_id or len(self.profile_id.encode("utf-8")) > 80:
            raise ValueError("profile_id must be short and non-empty")
        if not self.service_name or len(self.service_name.encode("utf-8")) > 96:
            raise ValueError("service_name must be short and non-empty")
        for name, value in (
            ("scope_digest", self.scope_digest),
            ("request_digest", self.request_digest),
            ("epoch_digest", self.epoch_digest),
            ("shadow_fire_digest", self.shadow_fire_digest),
            ("key_chain_digest", self.key_chain_digest),
            ("public_contact_digest", self.public_contact_digest),
            ("catalog_digest", self.catalog_digest),
            ("previous_publication_digest", self.previous_publication_digest),
        ):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if len(self.signer_public_key) != 32:
            raise ValueError("signer public key must be 32 bytes")
        if self.sequence < 0:
            raise ValueError("sequence must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("expires_at must be greater than issued_at")
        if not self.family_id or not self.path_family:
            raise ValueError("family_id and path_family must be non-empty")
        if not self.redaction_label or len(self.redaction_label.encode("utf-8")) > 96:
            raise ValueError("redaction_label must be short and non-empty")

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"action": self.action.value,
            b"exposure": self.exposure_class.value,
            b"epoch": self.epoch_digest,
            b"fire": self.shadow_fire_digest,
            b"key": self.key_chain_digest,
            b"contact": self.public_contact_digest,
            b"catalog": self.catalog_digest,
            b"seq": self.sequence,
            b"prev": self.previous_publication_digest,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"family": self.family_id,
            b"path_family": self.path_family,
            b"signer": self.signer_public_key,
            b"redaction": self.redaction_label,
        }

    def payload(self) -> bytes:
        return BRIDGE_PUBLISH_DOMAIN + b":publication:" + bencode(self.unsigned_bvalue())

    @property
    def publication_digest(self) -> bytes:
        return sha256(BRIDGE_PUBLISH_DOMAIN + b":digest:" + self.payload() + self.signature)

    def verify(self) -> bool:
        return verify_signature(self.signer_public_key, self.payload(), self.signature)

    def with_signature(self, signature: bytes) -> "BridgePublication":
        return replace(self, signature=signature)


@dataclass(frozen=True)
class BridgePublicationReport:
    decision_kind: BridgePublishDecisionKind
    accepted: bool
    reason: str
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    action: BridgePublishAction
    publication_digest: bytes
    sequence: int
    previous_publication_digest: bytes
    exposure_class: ExposureClass
    family_id: str
    path_family: str
    watch: bool
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def make_bridge_publication(
    *,
    keypair: DhtKeypair,
    profile_id: str,
    service_name: str,
    scope_digest: bytes,
    request_digest: bytes,
    action: BridgePublishAction,
    exposure_class: ExposureClass,
    epoch_digest: bytes,
    shadow_fire_digest: bytes,
    key_chain_digest: bytes,
    public_contact_digest: bytes,
    catalog_digest: bytes,
    sequence: int,
    previous_publication_digest: bytes,
    issued_at: int,
    expires_at: int,
    family_id: str,
    path_family: str,
    redaction_label: str = "redacted-token-digest",
) -> BridgePublication:
    capsule = BridgePublication(profile_id, service_name, scope_digest, request_digest, action, exposure_class, epoch_digest, shadow_fire_digest, key_chain_digest, public_contact_digest, catalog_digest, sequence, previous_publication_digest, issued_at, expires_at, family_id, path_family, keypair.public_key_bytes, redaction_label)
    return capsule.with_signature(keypair.sign(capsule.payload()))


def _report(kind: BridgePublishDecisionKind, accepted: bool, reason: str, publication: BridgePublication, *, watch: bool = False) -> BridgePublicationReport:
    digest = sha256(BRIDGE_PUBLISH_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accepted": 1 if accepted else 0,
        b"reason": reason,
        b"publication": publication.publication_digest,
        b"seq": publication.sequence,
        b"prev": publication.previous_publication_digest,
        b"profile": publication.profile_id,
        b"service": publication.service_name,
        b"scope": publication.scope_digest,
        b"request": publication.request_digest,
        b"action": publication.action.value,
        b"exposure": publication.exposure_class.value,
        b"family": publication.family_id,
        b"path_family": publication.path_family,
        b"watch": 1 if watch else 0,
    }))
    return BridgePublicationReport(kind, accepted, reason, publication.profile_id, publication.service_name, publication.scope_digest, publication.request_digest, publication.action, publication.publication_digest, publication.sequence, publication.previous_publication_digest, publication.exposure_class, publication.family_id, publication.path_family, watch, digest)


def assess_bridge_publication(
    publication: BridgePublication,
    *,
    shadow_fire: ShadowFireReport,
    now: int,
    expected_profile_id: str,
    expected_service_name: str,
    expected_scope_digest: bytes,
    expected_request_digest: bytes,
    last_sequence: int | None = None,
    last_publication_digest: bytes | None = None,
    previously_seen_publication_digests: Iterable[bytes] = (),
    stale_public_announcement_digests: Iterable[bytes] = (),
    hard_negative_digests: Iterable[bytes] = (),
    allow_watch: bool = False,
    allow_public_token_exposure: bool = True,
) -> BridgePublicationReport:
    if len(expected_scope_digest) != 32 or len(expected_request_digest) != 32:
        raise ValueError("expected digests must be 32 bytes")
    if not publication.verify():
        return _report(BridgePublishDecisionKind.QUARANTINE_BAD_SIGNATURE, False, "bad publication signature", publication)
    if publication.issued_at > now:
        return _report(BridgePublishDecisionKind.QUARANTINE_FUTURE, False, "publication issued in the future", publication)
    if publication.expires_at <= now:
        return _report(BridgePublishDecisionKind.QUARANTINE_EXPIRED, False, "publication expired", publication)
    if publication.publication_digest in set(previously_seen_publication_digests):
        return _report(BridgePublishDecisionKind.QUARANTINE_REPLAY, False, "publication replay", publication)
    if hard_negative_digests:
        return _report(BridgePublishDecisionKind.QUARANTINE_HARD_NEGATIVE, False, "hard-negative pressure before public publication", publication)
    if stale_public_announcement_digests:
        return _report(BridgePublishDecisionKind.QUARANTINE_STALE_PUBLIC_REPLAY, False, "stale public announcement replay before publication", publication)
    if publication.profile_id != expected_profile_id or shadow_fire.profile_id != expected_profile_id:
        return _report(BridgePublishDecisionKind.QUARANTINE_PROFILE_DRIFT, False, "profile drift across publication boundary", publication)
    if publication.service_name != expected_service_name or shadow_fire.service_name != expected_service_name:
        return _report(BridgePublishDecisionKind.QUARANTINE_SERVICE_DRIFT, False, "service drift across publication boundary", publication)
    if publication.scope_digest != expected_scope_digest or shadow_fire.scope_digest != expected_scope_digest:
        return _report(BridgePublishDecisionKind.QUARANTINE_SCOPE_DRIFT, False, "scope drift across publication boundary", publication)
    if publication.request_digest != expected_request_digest or shadow_fire.request_digest != expected_request_digest:
        return _report(BridgePublishDecisionKind.QUARANTINE_REQUEST_DRIFT, False, "request drift across publication boundary", publication)
    expected_action = SHADOW_TO_PUBLICATION_ACTION[shadow_fire.action]
    if publication.action is not expected_action:
        return _report(BridgePublishDecisionKind.QUARANTINE_ACTION_DRIFT, False, "shadow-fire action and publication action disagree", publication)
    if publication.epoch_digest != shadow_fire.epoch_digest:
        return _report(BridgePublishDecisionKind.QUARANTINE_EPOCH_DRIFT, False, "epoch digest drift across publication boundary", publication)
    if publication.shadow_fire_digest != shadow_fire.report_digest or publication.key_chain_digest != shadow_fire.key_chain_digest:
        return _report(BridgePublishDecisionKind.QUARANTINE_FIRE_DIGEST_DRIFT, False, "shadow-fire digest or key-chain digest drift", publication)
    if not shadow_fire.accepted:
        return _report(BridgePublishDecisionKind.HOLD_SHADOW_FIRE_NOT_ACCEPTED, False, "shadow-fire did not accept side effect", publication)
    if shadow_fire.watch and not allow_watch:
        return _report(BridgePublishDecisionKind.HOLD_SHADOW_FIRE_WATCH, False, "shadow-fire accepted only with watch", publication, watch=True)
    if publication.action is BridgePublishAction.PUBLIC_WITHDRAW and publication.exposure_class is not ExposureClass.WITHDRAWAL_ONLY:
        return _report(BridgePublishDecisionKind.HOLD_WITHDRAWAL_PAYLOAD, False, "withdrawals must not carry live bridge exposure", publication)
    if publication.exposure_class is ExposureClass.PUBLIC_BRIDGE_TOKEN and not allow_public_token_exposure:
        return _report(BridgePublishDecisionKind.QUARANTINE_RAW_EXPOSURE, False, "public token exposure disabled for this path", publication)
    lowered = publication.redaction_label.lower()
    if ".b32.i2p" in lowered or "destination=" in lowered or "privkey" in lowered or "raw" in lowered:
        return _report(BridgePublishDecisionKind.QUARANTINE_RAW_EXPOSURE, False, "redaction label appears to contain raw exposure material", publication)
    if last_sequence is not None:
        if publication.sequence < last_sequence:
            return _report(BridgePublishDecisionKind.QUARANTINE_ROLLBACK, False, "publication sequence rollback", publication)
        if publication.sequence == last_sequence:
            if last_publication_digest is not None and publication.publication_digest != last_publication_digest:
                return _report(BridgePublishDecisionKind.QUARANTINE_SEQUENCE_FORK, False, "same-sequence publication fork", publication)
            return _report(BridgePublishDecisionKind.QUARANTINE_REPLAY, False, "same-sequence publication replay", publication)
        if publication.sequence > last_sequence + 1:
            return _report(BridgePublishDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, "publication sequence gap", publication)
        if last_publication_digest is not None and publication.previous_publication_digest != last_publication_digest:
            return _report(BridgePublishDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, "publication previous digest mismatch", publication)
    watch = shadow_fire.watch
    return _report(BridgePublishDecisionKind.ACCEPT_WITH_WATCH if watch else BridgePublishDecisionKind.ACCEPT_PUBLICATION, True, "bridge publication accepted locally", publication, watch=watch)
