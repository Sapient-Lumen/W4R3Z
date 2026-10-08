"""Tombstone repair pressure after settlement.

rev0058 refuses to let a settled public-edge effect quietly clean away hard
negative memory.  Tombstone repair observations are small signed local reports:
they say whether tombstones/revocations were carried, repaired, or contradicted
by resurrection-like positive evidence.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Any, Iterable

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectAction

TOMBSTONE_REPAIR_DOMAIN = DOMAIN + b":tombstone-repair-v1:"


class TombstoneRepairKind(str, Enum):
    TOMBSTONE_CARRIED = "tombstone_carried"
    REVOCATION_CARRIED = "revocation_carried"
    REPAIR_PUBLISHED = "repair_published"
    RESURRECTION_BLOCKED = "resurrection_blocked"
    SOFT_NONE = "soft_none"


class TombstoneRepairDecisionKind(str, Enum):
    ACCEPT_REPAIR_COVERAGE = "accept_repair_coverage"
    ACCEPT_NO_LIVE_TOMBSTONES = "accept_no_live_tombstones"
    HOLD_MISSING_REPAIR = "hold_missing_repair"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_EXPIRED_OR_FUTURE = "quarantine_expired_or_future"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_BOUNDARY_DRIFT = "quarantine_boundary_drift"
    QUARANTINE_COMPONENT_DIGEST_DRIFT = "quarantine_component_digest_drift"
    QUARANTINE_RESURRECTION_PRESSURE = "quarantine_resurrection_pressure"


@dataclass(frozen=True)
class TombstoneRepairEntry:
    repair_kind: TombstoneRepairKind
    action: SideEffectAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    settlement_digest: bytes
    tombstone_digest: bytes
    repair_subject_digest: bytes
    live_tombstone_count: int
    carried_tombstone_count: int
    resurrection_count: int
    sequence: int
    previous_entry_digest: bytes
    issued_at: int
    expires_at: int
    family_id: str
    path_family: str
    signer_public_key: bytes
    signature: bytes = b""

    def __post_init__(self) -> None:
        object.__setattr__(self, "repair_kind", TombstoneRepairKind(self.repair_kind))
        object.__setattr__(self, "action", SideEffectAction(self.action))
        if not self.profile_id or not self.service_name or not self.family_id or not self.path_family:
            raise ValueError("tombstone repair entry needs profile/service/family/path")
        if min(self.live_tombstone_count, self.carried_tombstone_count, self.resurrection_count, self.sequence, self.issued_at, self.expires_at) < 0:
            raise ValueError("tombstone repair counts/times must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("tombstone repair expires_at must follow issued_at")
        for name, value in (
            ("scope_digest", self.scope_digest),
            ("request_digest", self.request_digest),
            ("payload_digest", self.payload_digest),
            ("idempotency_key", self.idempotency_key),
            ("settlement_digest", self.settlement_digest),
            ("tombstone_digest", self.tombstone_digest),
            ("repair_subject_digest", self.repair_subject_digest),
            ("previous_entry_digest", self.previous_entry_digest),
            ("signer_public_key", self.signer_public_key),
        ):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if self.signature and len(self.signature) != 64:
            raise ValueError("signature must be empty or Ed25519-sized")

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"kind": self.repair_kind.value,
            b"action": self.action.value,
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"payload": self.payload_digest,
            b"idem": self.idempotency_key,
            b"settlement": self.settlement_digest,
            b"tombstone": self.tombstone_digest,
            b"subject": self.repair_subject_digest,
            b"live": self.live_tombstone_count,
            b"carried": self.carried_tombstone_count,
            b"resurrect": self.resurrection_count,
            b"seq": self.sequence,
            b"prev": self.previous_entry_digest,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"family": self.family_id,
            b"path_family": self.path_family,
            b"signer": self.signer_public_key,
        }

    def signature_payload(self) -> bytes:
        return TOMBSTONE_REPAIR_DOMAIN + b":entry-sig:" + bencode(self.unsigned_bvalue())

    @property
    def entry_core_digest(self) -> bytes:
        return sha256(TOMBSTONE_REPAIR_DOMAIN + b":entry-core:" + bencode(self.unsigned_bvalue()))

    @property
    def entry_digest(self) -> bytes:
        return sha256(TOMBSTONE_REPAIR_DOMAIN + b":entry-digest:" + self.signature_payload() + self.signature)

    def verifies(self) -> bool:
        return verify_signature(self.signer_public_key, self.signature_payload(), self.signature)

    def live(self, now: int) -> bool:
        return self.issued_at <= now < self.expires_at


@dataclass(frozen=True)
class TombstoneRepairReport:
    decision_kind: TombstoneRepairDecisionKind
    accept: bool
    watch: bool
    reason: str
    action: SideEffectAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    accepted_entry_digest: bytes
    entry_digests: tuple[bytes, ...]
    settlement_digest: bytes
    live_tombstone_count: int
    carried_tombstone_count: int
    resurrection_count: int
    highest_sequence: int
    family_count: int
    path_family_count: int
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _digest(report: Any | None) -> bytes:
    if report is None:
        return ZERO_DIGEST
    for attr in ("report_digest", "entry_digest"):
        value = getattr(report, attr, None)
        if isinstance(value, bytes) and len(value) == 32:
            return value
    raise ValueError("component lacks digest")


def make_tombstone_repair_entry(
    *,
    keypair: DhtKeypair,
    repair_kind: TombstoneRepairKind,
    settlement_report: Any,
    tombstone_digest: bytes,
    repair_subject_digest: bytes,
    live_tombstone_count: int,
    carried_tombstone_count: int,
    resurrection_count: int = 0,
    sequence: int,
    previous_entry_digest: bytes = ZERO_DIGEST,
    issued_at: int,
    expires_at: int,
    family_id: str,
    path_family: str,
) -> TombstoneRepairEntry:
    unsigned = TombstoneRepairEntry(
        repair_kind=repair_kind,
        action=SideEffectAction(getattr(settlement_report, "action")),
        profile_id=getattr(settlement_report, "profile_id"),
        service_name=getattr(settlement_report, "service_name"),
        scope_digest=getattr(settlement_report, "scope_digest"),
        request_digest=getattr(settlement_report, "request_digest"),
        payload_digest=getattr(settlement_report, "payload_digest"),
        idempotency_key=getattr(settlement_report, "idempotency_key"),
        settlement_digest=_digest(settlement_report),
        tombstone_digest=tombstone_digest,
        repair_subject_digest=repair_subject_digest,
        live_tombstone_count=live_tombstone_count,
        carried_tombstone_count=carried_tombstone_count,
        resurrection_count=resurrection_count,
        sequence=sequence,
        previous_entry_digest=previous_entry_digest,
        issued_at=issued_at,
        expires_at=expires_at,
        family_id=family_id,
        path_family=path_family,
        signer_public_key=keypair.public_key_bytes,
    )
    return replace(unsigned, signature=keypair.sign(unsigned.signature_payload()))


def assess_tombstone_repair(
    entries: Iterable[TombstoneRepairEntry],
    *,
    settlement_report: Any,
    expected_live_tombstone_count: int,
    now: int,
    previous_highest_sequence: int = -1,
    previous_seen_entry_digests: Iterable[bytes] = (),
    min_family_count: int = 2,
    min_path_family_count: int = 2,
) -> TombstoneRepairReport:
    entry_tuple = tuple(entries)
    action = SideEffectAction(getattr(settlement_report, "action"))
    profile_id = getattr(settlement_report, "profile_id")
    service_name = getattr(settlement_report, "service_name")
    scope_digest = getattr(settlement_report, "scope_digest")
    request_digest = getattr(settlement_report, "request_digest")
    payload_digest = getattr(settlement_report, "payload_digest")
    idempotency_key = getattr(settlement_report, "idempotency_key")
    settlement_digest = _digest(settlement_report)
    common = dict(action=action, profile_id=profile_id, service_name=service_name, scope_digest=scope_digest, request_digest=request_digest, payload_digest=payload_digest, idempotency_key=idempotency_key, settlement_digest=settlement_digest)
    if expected_live_tombstone_count < 0:
        raise ValueError("expected_live_tombstone_count must be non-negative")
    if expected_live_tombstone_count == 0 and not entry_tuple:
        return _report(TombstoneRepairDecisionKind.ACCEPT_NO_LIVE_TOMBSTONES, True, False, "no live tombstones require repair", accepted_entry_digest=ZERO_DIGEST, entry_digests=(), live_tombstone_count=0, carried_tombstone_count=0, resurrection_count=0, highest_sequence=previous_highest_sequence, family_count=0, path_family_count=0, **common)
    if expected_live_tombstone_count > 0 and not entry_tuple:
        return _report(TombstoneRepairDecisionKind.HOLD_MISSING_REPAIR, False, True, "live tombstones need repair evidence", accepted_entry_digest=ZERO_DIGEST, entry_digests=(), live_tombstone_count=expected_live_tombstone_count, carried_tombstone_count=0, resurrection_count=0, highest_sequence=previous_highest_sequence, family_count=0, path_family_count=0, **common)
    valid: list[TombstoneRepairEntry] = []
    seen = set(previous_seen_entry_digests)
    for entry in entry_tuple:
        if not entry.verifies():
            return _entry_report(TombstoneRepairDecisionKind.QUARANTINE_BAD_SIGNATURE, False, False, "bad repair signature", entry_tuple, valid, expected_live_tombstone_count, **common)
        if not entry.live(now):
            return _entry_report(TombstoneRepairDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, False, False, "repair entry expired or from future", entry_tuple, valid, expected_live_tombstone_count, **common)
        if entry.entry_digest in seen:
            return _entry_report(TombstoneRepairDecisionKind.QUARANTINE_REPLAY, False, False, "repair entry replay", entry_tuple, valid, expected_live_tombstone_count, **common)
        if entry.sequence <= previous_highest_sequence:
            return _entry_report(TombstoneRepairDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, False, "repair sequence rollback", entry_tuple, valid, expected_live_tombstone_count, **common)
        if entry.action is not action or entry.profile_id != profile_id or entry.service_name != service_name:
            return _entry_report(TombstoneRepairDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, "action/profile/service drift", entry_tuple, valid, expected_live_tombstone_count, **common)
        if entry.scope_digest != scope_digest or entry.request_digest != request_digest or entry.payload_digest != payload_digest or entry.idempotency_key != idempotency_key:
            return _entry_report(TombstoneRepairDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, "scope/request/payload/idempotency drift", entry_tuple, valid, expected_live_tombstone_count, **common)
        if entry.settlement_digest != settlement_digest:
            return _entry_report(TombstoneRepairDecisionKind.QUARANTINE_COMPONENT_DIGEST_DRIFT, False, False, "settlement digest drift", entry_tuple, valid, expected_live_tombstone_count, **common)
        valid.append(entry)
    ordered = sorted(valid, key=lambda e: e.sequence)
    by_seq: dict[int, bytes] = {}
    for entry in ordered:
        prior = by_seq.get(entry.sequence)
        if prior is not None and prior != entry.entry_core_digest:
            return _entry_report(TombstoneRepairDecisionKind.QUARANTINE_SEQUENCE_FORK, False, False, "same-sequence repair fork", entry_tuple, valid, expected_live_tombstone_count, **common)
        by_seq[entry.sequence] = entry.entry_core_digest
    for prev, nxt in zip(ordered, ordered[1:]):
        if nxt.previous_entry_digest != prev.entry_digest:
            return _entry_report(TombstoneRepairDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, False, "repair previous-link mismatch", entry_tuple, valid, expected_live_tombstone_count, **common)
    resurrection_count = sum(entry.resurrection_count for entry in valid)
    if resurrection_count:
        return _entry_report(TombstoneRepairDecisionKind.QUARANTINE_RESURRECTION_PRESSURE, False, False, "resurrection pressure conflicts with tombstone repair", entry_tuple, valid, expected_live_tombstone_count, **common)
    families = {entry.family_id for entry in valid}
    paths = {entry.path_family for entry in valid}
    if len(families) < min_family_count:
        return _entry_report(TombstoneRepairDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, "low repair family diversity", entry_tuple, valid, expected_live_tombstone_count, **common)
    if len(paths) < min_path_family_count:
        return _entry_report(TombstoneRepairDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, "low repair path diversity", entry_tuple, valid, expected_live_tombstone_count, **common)
    carried = sum(entry.carried_tombstone_count for entry in valid)
    if carried < expected_live_tombstone_count:
        return _entry_report(TombstoneRepairDecisionKind.HOLD_MISSING_REPAIR, False, True, "not all live tombstones carried", entry_tuple, valid, expected_live_tombstone_count, **common)
    return _entry_report(TombstoneRepairDecisionKind.ACCEPT_REPAIR_COVERAGE, True, False, "tombstone repair coverage accepted", entry_tuple, valid, expected_live_tombstone_count, **common)


def _entry_report(kind: TombstoneRepairDecisionKind, accept: bool, watch: bool, reason: str, all_entries: tuple[TombstoneRepairEntry, ...], valid: list[TombstoneRepairEntry], expected_live_tombstone_count: int, *, action: SideEffectAction, profile_id: str, service_name: str, scope_digest: bytes, request_digest: bytes, payload_digest: bytes, idempotency_key: bytes, settlement_digest: bytes) -> TombstoneRepairReport:
    entry_digests = tuple(entry.entry_digest for entry in valid)
    return _report(kind, accept, watch, reason, action=action, profile_id=profile_id, service_name=service_name, scope_digest=scope_digest, request_digest=request_digest, payload_digest=payload_digest, idempotency_key=idempotency_key, settlement_digest=settlement_digest, accepted_entry_digest=entry_digests[-1] if accept and entry_digests else ZERO_DIGEST, entry_digests=entry_digests, live_tombstone_count=expected_live_tombstone_count, carried_tombstone_count=sum(e.carried_tombstone_count for e in valid), resurrection_count=sum(e.resurrection_count for e in valid), highest_sequence=max((e.sequence for e in valid), default=-1), family_count=len({e.family_id for e in valid}), path_family_count=len({e.path_family for e in valid}))


def _report(kind: TombstoneRepairDecisionKind, accept: bool, watch: bool, reason: str, *, action: SideEffectAction, profile_id: str, service_name: str, scope_digest: bytes, request_digest: bytes, payload_digest: bytes, idempotency_key: bytes, settlement_digest: bytes, accepted_entry_digest: bytes, entry_digests: tuple[bytes, ...], live_tombstone_count: int, carried_tombstone_count: int, resurrection_count: int, highest_sequence: int, family_count: int, path_family_count: int) -> TombstoneRepairReport:
    body = {
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"reason": reason,
        b"action": SideEffectAction(action).value,
        b"profile": profile_id,
        b"service": service_name,
        b"scope": scope_digest,
        b"request": request_digest,
        b"payload": payload_digest,
        b"idem": idempotency_key,
        b"settlement": settlement_digest,
        b"accepted": accepted_entry_digest,
        b"entries": list(entry_digests),
        b"live": live_tombstone_count,
        b"carried": carried_tombstone_count,
        b"resurrect": resurrection_count,
        b"highest": highest_sequence,
        b"families": family_count,
        b"paths": path_family_count,
    }
    return TombstoneRepairReport(kind, accept, watch, reason, SideEffectAction(action), profile_id, service_name, scope_digest, request_digest, payload_digest, idempotency_key, accepted_entry_digest, entry_digests, settlement_digest, live_tombstone_count, carried_tombstone_count, resurrection_count, highest_sequence, family_count, path_family_count, sha256(TOMBSTONE_REPAIR_DOMAIN + b":report:" + bencode(body)))
