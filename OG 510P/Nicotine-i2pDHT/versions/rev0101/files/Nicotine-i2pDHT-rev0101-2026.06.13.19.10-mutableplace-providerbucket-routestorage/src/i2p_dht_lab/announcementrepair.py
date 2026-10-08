"""Catalog and announcement repair after bridge disable.

When a public bridge is disabled, old announcements and catalogs become an
entrance-capture surface.  rev0042 keeps this as no-network pressure: a service
must show withdrawal of public exposure, a successor catalog if it keeps serving
privately, and no live stale public announcement before repair is accepted.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256

ANNOUNCEMENT_REPAIR_DOMAIN = DOMAIN + b":announcement-repair-v1:"
ZERO_DIGEST = b"\x00" * 32


class RepairSignalKind(str, Enum):
    BRIDGE_DISABLE = "bridge_disable"
    PUBLIC_WITHDRAWAL = "public_withdrawal"
    SUCCESSOR_CATALOG = "successor_catalog"
    PRIVATE_ANNOUNCEMENT = "private_announcement"
    STALE_PUBLIC_ANNOUNCEMENT = "stale_public_announcement"
    TOMBSTONE_SCAN = "tombstone_scan"


class AnnouncementRepairDecisionKind(str, Enum):
    ACCEPT_REPAIR = "accept_repair"
    HOLD_NEEDS_PUBLIC_WITHDRAWAL = "hold_needs_public_withdrawal"
    HOLD_NEEDS_SUCCESSOR_CATALOG = "hold_needs_successor_catalog"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_EXPIRED_OR_FUTURE = "quarantine_expired_or_future"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_SERVICE_DRIFT = "quarantine_service_drift"
    QUARANTINE_STALE_PUBLIC_ANNOUNCEMENT = "quarantine_stale_public_announcement"
    QUARANTINE_SUCCESSOR_ROLLBACK = "quarantine_successor_rollback"
    QUARANTINE_SUCCESSOR_FORK = "quarantine_successor_fork"
    QUARANTINE_HARD_NEGATIVE_PRESENT = "quarantine_hard_negative_present"


@dataclass(frozen=True)
class AnnouncementRepairSignal:
    service_name: str
    scope_digest: bytes
    kind: RepairSignalKind
    sequence: int
    catalog_digest: bytes
    announcement_digest: bytes
    bridge_disable_digest: bytes
    issued_at: int
    expires_at: int
    family_id: str
    signer_public_key: bytes
    hard_negative_clear: bool = True
    public_exposure: bool = False
    signature: bytes = b""

    def __post_init__(self) -> None:
        if not self.service_name or len(self.service_name.encode("utf-8")) > 80:
            raise ValueError("service_name must be short and non-empty")
        if self.sequence < 0:
            raise ValueError("repair signal sequence must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("repair signal expires_at must be after issued_at")
        if not self.family_id:
            raise ValueError("repair family must be non-empty")
        for name, value in (("scope_digest", self.scope_digest), ("catalog_digest", self.catalog_digest), ("announcement_digest", self.announcement_digest), ("bridge_disable_digest", self.bridge_disable_digest), ("signer_public_key", self.signer_public_key)):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if self.signature and len(self.signature) != 64:
            raise ValueError("repair signature must be Ed25519-sized")

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"service": self.service_name,
            b"scope": self.scope_digest,
            b"kind": self.kind.value,
            b"seq": self.sequence,
            b"catalog": self.catalog_digest,
            b"announcement": self.announcement_digest,
            b"bridge_disable": self.bridge_disable_digest,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"family": self.family_id,
            b"signer": self.signer_public_key,
            b"hard_clear": 1 if self.hard_negative_clear else 0,
            b"public": 1 if self.public_exposure else 0,
        }

    @property
    def signal_digest(self) -> bytes:
        return sha256(ANNOUNCEMENT_REPAIR_DOMAIN + b":signal-digest:" + bencode(self.unsigned_bvalue()))

    def signature_payload(self) -> bytes:
        return ANNOUNCEMENT_REPAIR_DOMAIN + b":signal-sig:" + bencode(self.unsigned_bvalue())

    def verifies(self) -> bool:
        return verify_signature(self.signer_public_key, self.signature_payload(), self.signature)


@dataclass(frozen=True)
class AnnouncementRepairPolicy:
    min_families: int = 2
    require_successor_catalog: bool = True
    require_tombstone_scan: bool = True


@dataclass(frozen=True)
class AnnouncementRepairReport:
    decision_kind: AnnouncementRepairDecisionKind
    accept: bool
    reason: str
    service_name: str
    signal_digests: tuple[bytes, ...]
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def make_announcement_repair_signal(
    *,
    keypair: DhtKeypair,
    service_name: str,
    scope_digest: bytes,
    kind: RepairSignalKind,
    sequence: int,
    catalog_digest: bytes,
    announcement_digest: bytes,
    bridge_disable_digest: bytes,
    issued_at: int,
    expires_at: int,
    family_id: str,
    hard_negative_clear: bool = True,
    public_exposure: bool = False,
) -> AnnouncementRepairSignal:
    signal = AnnouncementRepairSignal(service_name=service_name, scope_digest=scope_digest, kind=kind, sequence=sequence, catalog_digest=catalog_digest, announcement_digest=announcement_digest, bridge_disable_digest=bridge_disable_digest, issued_at=issued_at, expires_at=expires_at, family_id=family_id, signer_public_key=keypair.public_key_bytes, hard_negative_clear=hard_negative_clear, public_exposure=public_exposure)
    return replace(signal, signature=keypair.sign(signal.signature_payload()))


def _report(kind: AnnouncementRepairDecisionKind, accept: bool, reason: str, service_name: str, signals: Iterable[AnnouncementRepairSignal]) -> AnnouncementRepairReport:
    signal_tuple = tuple(sorted(signals, key=lambda item: (item.kind.value, item.sequence, item.signal_digest)))
    digests = tuple(sorted(item.signal_digest for item in signal_tuple))
    digest = sha256(ANNOUNCEMENT_REPAIR_DOMAIN + b":report:" + bencode({b"kind": kind.value, b"accept": 1 if accept else 0, b"reason": reason, b"service": service_name, b"signals": list(digests)}))
    return AnnouncementRepairReport(kind, accept, reason, service_name, digests, digest)


def assess_announcement_repair(
    signals: Iterable[AnnouncementRepairSignal],
    *,
    now: int,
    expected_service_name: str,
    expected_scope_digest: bytes,
    bridge_disable_digest: bytes,
    previous_catalog_sequence: int | None = None,
    previously_seen_signals: Iterable[bytes] = (),
    policy: AnnouncementRepairPolicy | None = None,
) -> AnnouncementRepairReport:
    policy = policy or AnnouncementRepairPolicy()
    signal_tuple = tuple(sorted(signals, key=lambda item: (item.kind.value, item.sequence, item.signal_digest)))
    seen = set(previously_seen_signals)
    for signal in signal_tuple:
        if not signal.verifies():
            return _report(AnnouncementRepairDecisionKind.QUARANTINE_BAD_SIGNATURE, False, "bad repair signal signature", expected_service_name, signal_tuple)
        if signal.issued_at > now or signal.expires_at <= now:
            return _report(AnnouncementRepairDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, False, "repair signal expired or future", expected_service_name, signal_tuple)
        if signal.signal_digest in seen:
            return _report(AnnouncementRepairDecisionKind.QUARANTINE_REPLAY, False, "repair signal replay", expected_service_name, signal_tuple)
        if signal.service_name != expected_service_name:
            return _report(AnnouncementRepairDecisionKind.QUARANTINE_SERVICE_DRIFT, False, "repair service drift", expected_service_name, signal_tuple)
        if signal.scope_digest != expected_scope_digest:
            return _report(AnnouncementRepairDecisionKind.QUARANTINE_SCOPE_DRIFT, False, "repair scope drift", expected_service_name, signal_tuple)
        if not signal.hard_negative_clear:
            return _report(AnnouncementRepairDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESENT, False, "repair signal carries hard-negative pressure", expected_service_name, signal_tuple)
    kinds = {signal.kind for signal in signal_tuple}
    if RepairSignalKind.STALE_PUBLIC_ANNOUNCEMENT in kinds or any(signal.public_exposure for signal in signal_tuple if signal.kind is not RepairSignalKind.PUBLIC_WITHDRAWAL):
        return _report(AnnouncementRepairDecisionKind.QUARANTINE_STALE_PUBLIC_ANNOUNCEMENT, False, "stale public announcement still visible", expected_service_name, signal_tuple)
    if RepairSignalKind.BRIDGE_DISABLE not in kinds or not any(signal.bridge_disable_digest == bridge_disable_digest for signal in signal_tuple):
        return _report(AnnouncementRepairDecisionKind.HOLD_NEEDS_PUBLIC_WITHDRAWAL, False, "bridge-disable signal missing", expected_service_name, signal_tuple)
    if RepairSignalKind.PUBLIC_WITHDRAWAL not in kinds:
        return _report(AnnouncementRepairDecisionKind.HOLD_NEEDS_PUBLIC_WITHDRAWAL, False, "public withdrawal missing", expected_service_name, signal_tuple)
    if policy.require_successor_catalog and RepairSignalKind.SUCCESSOR_CATALOG not in kinds:
        return _report(AnnouncementRepairDecisionKind.HOLD_NEEDS_SUCCESSOR_CATALOG, False, "successor catalog missing", expected_service_name, signal_tuple)
    if policy.require_tombstone_scan and RepairSignalKind.TOMBSTONE_SCAN not in kinds:
        return _report(AnnouncementRepairDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESENT, False, "tombstone scan missing", expected_service_name, signal_tuple)
    successor_signals = [signal for signal in signal_tuple if signal.kind is RepairSignalKind.SUCCESSOR_CATALOG]
    seq_to_digest: dict[int, bytes] = {}
    for signal in successor_signals:
        previous = seq_to_digest.setdefault(signal.sequence, signal.catalog_digest)
        if previous != signal.catalog_digest:
            return _report(AnnouncementRepairDecisionKind.QUARANTINE_SUCCESSOR_FORK, False, "same-sequence successor catalog fork", expected_service_name, signal_tuple)
        if previous_catalog_sequence is not None and signal.sequence <= previous_catalog_sequence:
            return _report(AnnouncementRepairDecisionKind.QUARANTINE_SUCCESSOR_ROLLBACK, False, "successor catalog did not advance", expected_service_name, signal_tuple)
    families = {signal.family_id for signal in signal_tuple}
    if len(families) < policy.min_families:
        return _report(AnnouncementRepairDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, "repair evidence lacks family diversity", expected_service_name, signal_tuple)
    return _report(AnnouncementRepairDecisionKind.ACCEPT_REPAIR, True, "bridge disable repaired by withdrawal and successor catalog", expected_service_name, signal_tuple)
