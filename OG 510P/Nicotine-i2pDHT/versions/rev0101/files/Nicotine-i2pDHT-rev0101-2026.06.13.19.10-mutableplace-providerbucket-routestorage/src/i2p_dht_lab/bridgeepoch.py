"""Public bridge epoch windows and stale-announcement pressure.

A public bridge is one of the riskiest garden roles: it is useful precisely
because it creates an entrance for others, but that entrance can also become a
sticky stale rumor after the operator disables it, rotates keys, or repairs a
catalog.  rev0045 treats public bridge state as an epoch lane rather than a
boolean.

The lane is intentionally local and no-network.  It signs small epoch notices,
checks monotonic/previous-link pressure, and refuses to let stale public
announcements survive a close/withdraw epoch without an accepted repair report.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .announcementrepair import AnnouncementRepairReport
from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256

BRIDGE_EPOCH_DOMAIN = DOMAIN + b":bridge-epoch-v1:"
ZERO_DIGEST = b"\x00" * 32


class BridgeEpochAction(str, Enum):
    OPEN_PUBLIC = "open_public"
    RENEW_PUBLIC = "renew_public"
    CLOSE_PUBLIC = "close_public"
    WITHDRAW_PUBLIC = "withdraw_public"


class BridgeEpochDecisionKind(str, Enum):
    ACCEPT_EPOCH = "accept_epoch"
    ACCEPT_CLOSE_WITH_REPAIR = "accept_close_with_repair"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_NEEDS_REPAIR = "hold_needs_repair"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_EXPIRED_OR_FUTURE = "quarantine_expired_or_future"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_PROFILE_DRIFT = "quarantine_profile_drift"
    QUARANTINE_SERVICE_DRIFT = "quarantine_service_drift"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_REQUEST_DRIFT = "quarantine_request_drift"
    QUARANTINE_CATALOG_DRIFT = "quarantine_catalog_drift"
    QUARANTINE_ANNOUNCEMENT_DRIFT = "quarantine_announcement_drift"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_STALE_PUBLIC_REPLAY = "quarantine_stale_public_replay"
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"


@dataclass(frozen=True)
class BridgeEpochNotice:
    profile_id: str
    service_name: str
    action: BridgeEpochAction
    sequence: int
    previous_epoch_digest: bytes
    scope_digest: bytes
    request_digest: bytes
    catalog_digest: bytes
    announcement_digest: bytes
    control_receipt_digest: bytes
    issued_at: int
    expires_at: int
    family_id: str
    path_family: str
    signer_public_key: bytes
    public_exposure: bool
    hard_negative_clear: bool = True
    signature: bytes = b""

    def __post_init__(self) -> None:
        if not self.profile_id or len(self.profile_id.encode("utf-8")) > 80:
            raise ValueError("profile_id must be short and non-empty")
        if not self.service_name or len(self.service_name.encode("utf-8")) > 80:
            raise ValueError("service_name must be short and non-empty")
        if self.sequence < 0:
            raise ValueError("epoch sequence must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("epoch notice expires_at must be after issued_at")
        if not self.family_id or not self.path_family:
            raise ValueError("family_id and path_family must be non-empty")
        for name, value in (
            ("previous_epoch_digest", self.previous_epoch_digest),
            ("scope_digest", self.scope_digest),
            ("request_digest", self.request_digest),
            ("catalog_digest", self.catalog_digest),
            ("announcement_digest", self.announcement_digest),
            ("control_receipt_digest", self.control_receipt_digest),
            ("signer_public_key", self.signer_public_key),
        ):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if self.signature and len(self.signature) != 64:
            raise ValueError("signature must be Ed25519-sized")
        object.__setattr__(self, "action", BridgeEpochAction(self.action))

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"action": self.action.value,
            b"seq": self.sequence,
            b"prev": self.previous_epoch_digest,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"catalog": self.catalog_digest,
            b"announcement": self.announcement_digest,
            b"control_receipt": self.control_receipt_digest,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"family": self.family_id,
            b"path_family": self.path_family,
            b"signer": self.signer_public_key,
            b"public": 1 if self.public_exposure else 0,
            b"hard_clear": 1 if self.hard_negative_clear else 0,
        }

    def signature_payload(self) -> bytes:
        return BRIDGE_EPOCH_DOMAIN + b":notice-sig:" + bencode(self.unsigned_bvalue())

    @property
    def epoch_core_digest(self) -> bytes:
        """Digest of the bridge epoch claim, excluding witness family/signer noise."""
        return sha256(BRIDGE_EPOCH_DOMAIN + b":epoch-core:" + bencode({
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"action": self.action.value,
            b"seq": self.sequence,
            b"prev": self.previous_epoch_digest,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"catalog": self.catalog_digest,
            b"announcement": self.announcement_digest,
            b"control_receipt": self.control_receipt_digest,
            b"public": 1 if self.public_exposure else 0,
            b"hard_clear": 1 if self.hard_negative_clear else 0,
        }))

    @property
    def notice_digest(self) -> bytes:
        return sha256(BRIDGE_EPOCH_DOMAIN + b":notice-digest:" + bencode(self.unsigned_bvalue()))

    def verifies(self) -> bool:
        return verify_signature(self.signer_public_key, self.signature_payload(), self.signature)


@dataclass(frozen=True)
class BridgeEpochReport:
    decision_kind: BridgeEpochDecisionKind
    accept: bool
    reason: str
    profile_id: str
    service_name: str
    action: BridgeEpochAction | None
    highest_sequence: int
    accepted_epoch_digest: bytes
    notice_digests: tuple[bytes, ...]
    family_count: int
    path_family_count: int
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")

    @property
    def public_open(self) -> bool:
        return self.action in (BridgeEpochAction.OPEN_PUBLIC, BridgeEpochAction.RENEW_PUBLIC) and self.accept


def make_bridge_epoch_notice(
    *,
    keypair: DhtKeypair,
    profile_id: str,
    service_name: str,
    action: BridgeEpochAction,
    sequence: int,
    previous_epoch_digest: bytes,
    scope_digest: bytes,
    request_digest: bytes,
    catalog_digest: bytes,
    announcement_digest: bytes,
    control_receipt_digest: bytes,
    issued_at: int,
    expires_at: int,
    family_id: str,
    path_family: str,
    public_exposure: bool,
    hard_negative_clear: bool = True,
) -> BridgeEpochNotice:
    notice = BridgeEpochNotice(
        profile_id=profile_id,
        service_name=service_name,
        action=action,
        sequence=sequence,
        previous_epoch_digest=previous_epoch_digest,
        scope_digest=scope_digest,
        request_digest=request_digest,
        catalog_digest=catalog_digest,
        announcement_digest=announcement_digest,
        control_receipt_digest=control_receipt_digest,
        issued_at=issued_at,
        expires_at=expires_at,
        family_id=family_id,
        path_family=path_family,
        signer_public_key=keypair.public_key_bytes,
        public_exposure=public_exposure,
        hard_negative_clear=hard_negative_clear,
    )
    return replace(notice, signature=keypair.sign(notice.signature_payload()))


def _report(
    kind: BridgeEpochDecisionKind,
    accept: bool,
    reason: str,
    *,
    profile_id: str,
    service_name: str,
    notices: Iterable[BridgeEpochNotice],
    selected: BridgeEpochNotice | None = None,
    family_count: int = 0,
    path_family_count: int = 0,
) -> BridgeEpochReport:
    notice_tuple = tuple(sorted(notices, key=lambda item: (item.sequence, item.notice_digest)))
    digests = tuple(sorted(item.notice_digest for item in notice_tuple))
    action = selected.action if selected is not None else None
    highest = selected.sequence if selected is not None else -1
    accepted = selected.notice_digest if selected is not None and accept else ZERO_DIGEST
    digest = sha256(BRIDGE_EPOCH_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"reason": reason,
        b"profile": profile_id,
        b"service": service_name,
        b"action": action.value if action is not None else b"none",
        b"highest": highest,
        b"accepted": accepted,
        b"notices": list(digests),
        b"families": family_count,
        b"paths": path_family_count,
    }))
    return BridgeEpochReport(kind, accept, reason, profile_id, service_name, action, highest, accepted, digests, family_count, path_family_count, digest)


def assess_bridge_epoch(
    notices: Iterable[BridgeEpochNotice],
    *,
    now: int,
    expected_profile_id: str,
    expected_service_name: str,
    expected_scope_digest: bytes,
    expected_request_digest: bytes,
    expected_catalog_digest: bytes,
    expected_announcement_digest: bytes,
    previous_sequence: int | None = None,
    previous_epoch_digest: bytes | None = None,
    previously_seen_notices: Iterable[bytes] = (),
    min_family_diversity: int = 2,
    require_repair_for_close: bool = False,
    repair_report: AnnouncementRepairReport | None = None,
) -> BridgeEpochReport:
    if len(expected_scope_digest) != 32 or len(expected_request_digest) != 32:
        raise ValueError("expected scope/request digests must be 32 bytes")
    if len(expected_catalog_digest) != 32 or len(expected_announcement_digest) != 32:
        raise ValueError("expected catalog/announcement digests must be 32 bytes")
    notice_tuple = tuple(sorted(notices, key=lambda item: (item.sequence, item.notice_digest)))
    seen = set(previously_seen_notices)
    families: set[str] = set()
    paths: set[str] = set()
    fork_guard: dict[int, bytes] = {}
    latest: BridgeEpochNotice | None = None
    for notice in notice_tuple:
        if not notice.verifies():
            return _report(BridgeEpochDecisionKind.QUARANTINE_BAD_SIGNATURE, False, "bad bridge epoch signature", profile_id=expected_profile_id, service_name=expected_service_name, notices=notice_tuple)
        if notice.issued_at > now or notice.expires_at <= now:
            return _report(BridgeEpochDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, False, "bridge epoch expired or future", profile_id=expected_profile_id, service_name=expected_service_name, notices=notice_tuple)
        if notice.notice_digest in seen:
            return _report(BridgeEpochDecisionKind.QUARANTINE_REPLAY, False, "bridge epoch replay", profile_id=expected_profile_id, service_name=expected_service_name, notices=notice_tuple)
        if notice.profile_id != expected_profile_id:
            return _report(BridgeEpochDecisionKind.QUARANTINE_PROFILE_DRIFT, False, "bridge epoch profile drift", profile_id=expected_profile_id, service_name=expected_service_name, notices=notice_tuple)
        if notice.service_name != expected_service_name:
            return _report(BridgeEpochDecisionKind.QUARANTINE_SERVICE_DRIFT, False, "bridge epoch service drift", profile_id=expected_profile_id, service_name=expected_service_name, notices=notice_tuple)
        if notice.scope_digest != expected_scope_digest:
            return _report(BridgeEpochDecisionKind.QUARANTINE_SCOPE_DRIFT, False, "bridge epoch scope drift", profile_id=expected_profile_id, service_name=expected_service_name, notices=notice_tuple)
        if notice.request_digest != expected_request_digest:
            return _report(BridgeEpochDecisionKind.QUARANTINE_REQUEST_DRIFT, False, "bridge epoch request drift", profile_id=expected_profile_id, service_name=expected_service_name, notices=notice_tuple)
        if notice.catalog_digest != expected_catalog_digest:
            return _report(BridgeEpochDecisionKind.QUARANTINE_CATALOG_DRIFT, False, "bridge epoch catalog drift", profile_id=expected_profile_id, service_name=expected_service_name, notices=notice_tuple)
        if notice.announcement_digest != expected_announcement_digest:
            return _report(BridgeEpochDecisionKind.QUARANTINE_ANNOUNCEMENT_DRIFT, False, "bridge epoch announcement drift", profile_id=expected_profile_id, service_name=expected_service_name, notices=notice_tuple)
        if not notice.hard_negative_clear:
            return _report(BridgeEpochDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, "hard-negative pressure on bridge epoch", profile_id=expected_profile_id, service_name=expected_service_name, notices=notice_tuple)
        prior = fork_guard.get(notice.sequence)
        if prior is not None and prior != notice.epoch_core_digest:
            return _report(BridgeEpochDecisionKind.QUARANTINE_SEQUENCE_FORK, False, "same-sequence bridge epoch fork", profile_id=expected_profile_id, service_name=expected_service_name, notices=notice_tuple)
        fork_guard[notice.sequence] = notice.epoch_core_digest
        if previous_sequence is not None and notice.sequence < previous_sequence:
            return _report(BridgeEpochDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, "bridge epoch rollback", profile_id=expected_profile_id, service_name=expected_service_name, notices=notice_tuple)
        families.add(notice.family_id)
        paths.add(notice.path_family)
        if latest is None or notice.sequence > latest.sequence:
            latest = notice
    if latest is None:
        return _report(BridgeEpochDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, "no bridge epoch notices", profile_id=expected_profile_id, service_name=expected_service_name, notices=notice_tuple)
    if previous_sequence is not None and latest.sequence > previous_sequence and previous_epoch_digest is not None and latest.previous_epoch_digest != previous_epoch_digest:
        return _report(BridgeEpochDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, "bridge epoch previous-link mismatch", profile_id=expected_profile_id, service_name=expected_service_name, notices=notice_tuple, selected=latest, family_count=len(families), path_family_count=len(paths))
    if latest.action in (BridgeEpochAction.CLOSE_PUBLIC, BridgeEpochAction.WITHDRAW_PUBLIC) and latest.public_exposure:
        return _report(BridgeEpochDecisionKind.QUARANTINE_STALE_PUBLIC_REPLAY, False, "close/withdraw epoch still exposes public announcement", profile_id=expected_profile_id, service_name=expected_service_name, notices=notice_tuple, selected=latest, family_count=len(families), path_family_count=len(paths))
    if latest.action in (BridgeEpochAction.OPEN_PUBLIC, BridgeEpochAction.RENEW_PUBLIC) and not latest.public_exposure:
        return _report(BridgeEpochDecisionKind.QUARANTINE_STALE_PUBLIC_REPLAY, False, "open/renew epoch lacks public exposure binding", profile_id=expected_profile_id, service_name=expected_service_name, notices=notice_tuple, selected=latest, family_count=len(families), path_family_count=len(paths))
    if len(families) < min_family_diversity:
        return _report(BridgeEpochDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, "bridge epoch lacks family diversity", profile_id=expected_profile_id, service_name=expected_service_name, notices=notice_tuple, selected=latest, family_count=len(families), path_family_count=len(paths))
    if latest.action in (BridgeEpochAction.CLOSE_PUBLIC, BridgeEpochAction.WITHDRAW_PUBLIC) and require_repair_for_close:
        if repair_report is None or not repair_report.accept:
            return _report(BridgeEpochDecisionKind.HOLD_NEEDS_REPAIR, False, "close/withdraw epoch needs announcement repair", profile_id=expected_profile_id, service_name=expected_service_name, notices=notice_tuple, selected=latest, family_count=len(families), path_family_count=len(paths))
        return _report(BridgeEpochDecisionKind.ACCEPT_CLOSE_WITH_REPAIR, True, "bridge close/withdraw accepted with repair evidence", profile_id=expected_profile_id, service_name=expected_service_name, notices=notice_tuple, selected=latest, family_count=len(families), path_family_count=len(paths))
    return _report(BridgeEpochDecisionKind.ACCEPT_EPOCH, True, "bridge epoch accepted", profile_id=expected_profile_id, service_name=expected_service_name, notices=notice_tuple, selected=latest, family_count=len(families), path_family_count=len(paths))
