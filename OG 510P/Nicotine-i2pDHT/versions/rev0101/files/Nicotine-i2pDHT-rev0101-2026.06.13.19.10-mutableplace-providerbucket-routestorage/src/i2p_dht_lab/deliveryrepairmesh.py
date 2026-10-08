"""rev0064 delivery-repair mesh after idempotency lineage pressure.

Duplicate delivery is a repair question, not an assertion failure.  This lane
keeps remote delivery witnesses explicit and refuses to let retry publication,
late ACKs, or egress-journal compaction silently choose repair outcome.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable

from .bencode import bencode
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectAction

DELIVERY_REPAIR_MESH_DOMAIN = DOMAIN + b":delivery-repair-mesh-v1:"


class RemoteDeliveryWitnessKind(str, Enum):
    REMOTE_MATCHES_PAYLOAD = "remote_matches_payload"
    REMOTE_DUPLICATE_CONFLICT = "remote_duplicate_conflict"
    REMOTE_ABSENT = "remote_absent"


class DeliveryRepairMeshDecisionKind(str, Enum):
    ACCEPT_NO_REPAIR_NEEDED = "accept_no_repair_needed"
    ACCEPT_RETRY_PUBLICATION_READY = "accept_retry_publication_ready"
    ACCEPT_WITHDRAW_REPAIR_READY = "accept_withdraw_repair_ready"
    ACCEPT_DUPLICATE_BENIGN_WITH_WITNESS = "accept_duplicate_benign_with_witness"
    ACCEPT_REPAIR_REQUIRED_REMOTE_CONFLICT = "accept_repair_required_remote_conflict"
    HOLD_DUPLICATE_DELIVERY_REQUIRES_REMOTE_WITNESS = "hold_duplicate_delivery_requires_remote_witness"
    HOLD_COMPONENT_PENDING = "hold_component_pending"
    HOLD_LOW_WITNESS_DIVERSITY = "hold_low_witness_diversity"
    HOLD_LOW_WITNESS_PATH_DIVERSITY = "hold_low_witness_path_diversity"
    QUARANTINE_COMPONENT_NOT_ACCEPTED = "quarantine_component_not_accepted"
    QUARANTINE_BOUNDARY_DRIFT = "quarantine_boundary_drift"
    QUARANTINE_WITNESS_DIGEST_DRIFT = "quarantine_witness_digest_drift"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"


@dataclass(frozen=True)
class RemoteDeliveryWitness:
    kind: RemoteDeliveryWitnessKind
    sequence: int
    previous_digest: bytes
    action: SideEffectAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    retry_idempotency_key: bytes
    idempotency_mesh_digest: bytes
    retry_publish_digest: bytes
    egress_journal_digest: bytes
    remote_state_digest: bytes
    family_id: str
    path_family_id: str
    hard_negative_count: int = 0

    @property
    def witness_digest(self) -> bytes:
        return sha256(DELIVERY_REPAIR_MESH_DOMAIN + b":witness:" + bencode({
            b"kind": self.kind.value,
            b"seq": self.sequence,
            b"prev": self.previous_digest,
            b"action": SideEffectAction(self.action).value,
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"payload": self.payload_digest,
            b"idem": self.idempotency_key,
            b"retry_idem": self.retry_idempotency_key,
            b"mesh": self.idempotency_mesh_digest,
            b"publish": self.retry_publish_digest,
            b"journal": self.egress_journal_digest,
            b"remote": self.remote_state_digest,
            b"family": self.family_id,
            b"path": self.path_family_id,
            b"hard": self.hard_negative_count,
        }))


@dataclass(frozen=True)
class DeliveryRepairMeshReport:
    decision_kind: DeliveryRepairMeshDecisionKind
    accept: bool
    watch: bool
    repair_required: bool
    retry_publication_ready: bool
    withdraw_repair_ready: bool
    duplicate_benign: bool
    reason: str
    action: SideEffectAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    retry_idempotency_key: bytes
    idempotency_mesh_digest: bytes
    retry_publish_digest: bytes
    egress_journal_digest: bytes
    accepted_witness_digest: bytes
    witness_digests: tuple[bytes, ...]
    family_count: int
    path_family_count: int
    hard_negative_count: int
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _digest(report: Any | None) -> bytes:
    if report is None:
        return ZERO_DIGEST
    for attr in ("report_digest", "accepted_witness_digest", "accepted_marker_digest", "accepted_observation_digest"):
        value = getattr(report, attr, None)
        if isinstance(value, bytes) and len(value) == 32:
            return value
    raise ValueError("component lacks digest")


def _base_report(idempotency_mesh_report: Any, retry_publish_report: Any | None = None, egress_journal_report: Any | None = None) -> Any:
    return idempotency_mesh_report if idempotency_mesh_report is not None else retry_publish_report if retry_publish_report is not None else egress_journal_report


def _boundary(report: Any) -> tuple[Any, ...]:
    return (SideEffectAction(getattr(report, "action")), getattr(report, "profile_id"), getattr(report, "service_name"), getattr(report, "scope_digest"), getattr(report, "request_digest"), getattr(report, "payload_digest"), getattr(report, "idempotency_key"))


def _witness_boundary(witness: RemoteDeliveryWitness) -> tuple[Any, ...]:
    return (SideEffectAction(witness.action), witness.profile_id, witness.service_name, witness.scope_digest, witness.request_digest, witness.payload_digest, witness.idempotency_key)


def make_remote_delivery_witness(*, kind: RemoteDeliveryWitnessKind, sequence: int, idempotency_mesh_report: Any, retry_publish_report: Any | None = None, egress_journal_report: Any | None = None, previous_digest: bytes = ZERO_DIGEST, remote_state_digest: bytes | None = None, family_id: str = "family-a", path_family_id: str = "path-a", hard_negative_count: int = 0) -> RemoteDeliveryWitness:
    base = _base_report(idempotency_mesh_report, retry_publish_report, egress_journal_report)
    return RemoteDeliveryWitness(
        kind=RemoteDeliveryWitnessKind(kind),
        sequence=sequence,
        previous_digest=previous_digest,
        action=SideEffectAction(getattr(base, "action")),
        profile_id=getattr(base, "profile_id"),
        service_name=getattr(base, "service_name"),
        scope_digest=getattr(base, "scope_digest"),
        request_digest=getattr(base, "request_digest"),
        payload_digest=getattr(base, "payload_digest"),
        idempotency_key=getattr(base, "idempotency_key"),
        retry_idempotency_key=getattr(base, "retry_idempotency_key", ZERO_DIGEST),
        idempotency_mesh_digest=_digest(idempotency_mesh_report),
        retry_publish_digest=_digest(retry_publish_report),
        egress_journal_digest=_digest(egress_journal_report),
        remote_state_digest=remote_state_digest if remote_state_digest is not None else getattr(base, "payload_digest"),
        family_id=family_id,
        path_family_id=path_family_id,
        hard_negative_count=hard_negative_count,
    )


def _report(kind: DeliveryRepairMeshDecisionKind, accept: bool, watch: bool, repair_required: bool, retry_ready: bool, withdraw_ready: bool, duplicate_benign: bool, reason: str, *, idempotency_mesh_report: Any, retry_publish_report: Any | None, egress_journal_report: Any | None, witnesses: tuple[RemoteDeliveryWitness, ...], accepted_witness_digest: bytes = ZERO_DIGEST) -> DeliveryRepairMeshReport:
    base = _base_report(idempotency_mesh_report, retry_publish_report, egress_journal_report)
    digests = tuple(w.witness_digest for w in witnesses)
    families = {w.family_id for w in witnesses}
    paths = {w.path_family_id for w in witnesses}
    components = tuple(c for c in (idempotency_mesh_report, retry_publish_report, egress_journal_report) if c is not None)
    hard = sum(int(getattr(c, "hard_negative_count", 0) or 0) for c in components) + sum(w.hard_negative_count for w in witnesses)
    report_digest = sha256(DELIVERY_REPAIR_MESH_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"repair": 1 if repair_required else 0,
        b"retry_ready": 1 if retry_ready else 0,
        b"withdraw_ready": 1 if withdraw_ready else 0,
        b"duplicate_benign": 1 if duplicate_benign else 0,
        b"mesh": _digest(idempotency_mesh_report),
        b"publish": _digest(retry_publish_report),
        b"journal": _digest(egress_journal_report),
        b"witnesses": list(digests),
        b"families": len(families),
        b"paths": len(paths),
        b"hard": hard,
    }))
    return DeliveryRepairMeshReport(kind, accept, watch, repair_required, retry_ready, withdraw_ready, duplicate_benign, reason, SideEffectAction(getattr(base, "action")), getattr(base, "profile_id"), getattr(base, "service_name"), getattr(base, "scope_digest"), getattr(base, "request_digest"), getattr(base, "payload_digest"), getattr(base, "idempotency_key"), getattr(base, "retry_idempotency_key", ZERO_DIGEST), _digest(idempotency_mesh_report), _digest(retry_publish_report), _digest(egress_journal_report), accepted_witness_digest, digests, len(families), len(paths), hard, report_digest)


def assess_delivery_repair_mesh(*, idempotency_mesh_report: Any, retry_publish_report: Any | None = None, egress_journal_report: Any | None = None, remote_witnesses: Iterable[RemoteDeliveryWitness] = (), previous_digest: bytes = ZERO_DIGEST, seen_witness_digests: Iterable[bytes] = (), min_family_count: int = 2, min_path_family_count: int = 2) -> DeliveryRepairMeshReport:
    witnesses = tuple(remote_witnesses)
    components = tuple(c for c in (idempotency_mesh_report, retry_publish_report, egress_journal_report) if c is not None)
    if any(bool(getattr(c, "quarantined", False)) for c in components):
        return _report(DeliveryRepairMeshDecisionKind.QUARANTINE_COMPONENT_NOT_ACCEPTED, False, False, False, False, False, False, "component quarantined", idempotency_mesh_report=idempotency_mesh_report, retry_publish_report=retry_publish_report, egress_journal_report=egress_journal_report, witnesses=witnesses)
    if not (bool(getattr(idempotency_mesh_report, "accept", False)) or bool(getattr(idempotency_mesh_report, "watch", False))):
        return _report(DeliveryRepairMeshDecisionKind.QUARANTINE_COMPONENT_NOT_ACCEPTED, False, False, False, False, False, False, "idempotency mesh neither accepted nor watchful", idempotency_mesh_report=idempotency_mesh_report, retry_publish_report=retry_publish_report, egress_journal_report=egress_journal_report, witnesses=witnesses)
    if any(_boundary(c) != _boundary(idempotency_mesh_report) for c in components):
        return _report(DeliveryRepairMeshDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, False, False, False, False, "component boundary drift", idempotency_mesh_report=idempotency_mesh_report, retry_publish_report=retry_publish_report, egress_journal_report=egress_journal_report, witnesses=witnesses)
    if sum(int(getattr(c, "hard_negative_count", 0) or 0) for c in components):
        return _report(DeliveryRepairMeshDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, False, False, False, False, "component hard-negative pressure", idempotency_mesh_report=idempotency_mesh_report, retry_publish_report=retry_publish_report, egress_journal_report=egress_journal_report, witnesses=witnesses)
    duplicate = bool(getattr(idempotency_mesh_report, "duplicate_delivery_possible", False))
    if not duplicate:
        if bool(getattr(idempotency_mesh_report, "original_lineage_terminal", False)):
            return _report(DeliveryRepairMeshDecisionKind.ACCEPT_NO_REPAIR_NEEDED, True, False, False, False, False, False, "original ACK terminal; retry suppressed", idempotency_mesh_report=idempotency_mesh_report, retry_publish_report=retry_publish_report, egress_journal_report=egress_journal_report, witnesses=witnesses)
        if bool(getattr(idempotency_mesh_report, "withdraw_lineage_terminal", False)):
            return _report(DeliveryRepairMeshDecisionKind.ACCEPT_WITHDRAW_REPAIR_READY, True, False, True, False, True, False, "withdraw repair lineage terminal", idempotency_mesh_report=idempotency_mesh_report, retry_publish_report=retry_publish_report, egress_journal_report=egress_journal_report, witnesses=witnesses)
        if bool(getattr(idempotency_mesh_report, "retry_lineage_terminal", False)) and retry_publish_report is not None and bool(getattr(retry_publish_report, "accept", False)):
            return _report(DeliveryRepairMeshDecisionKind.ACCEPT_RETRY_PUBLICATION_READY, True, False, False, True, False, False, "retry publication ready", idempotency_mesh_report=idempotency_mesh_report, retry_publish_report=retry_publish_report, egress_journal_report=egress_journal_report, witnesses=witnesses)
        return _report(DeliveryRepairMeshDecisionKind.HOLD_COMPONENT_PENDING, False, True, False, False, False, False, "non-duplicate repair line pending", idempotency_mesh_report=idempotency_mesh_report, retry_publish_report=retry_publish_report, egress_journal_report=egress_journal_report, witnesses=witnesses)
    if not witnesses:
        return _report(DeliveryRepairMeshDecisionKind.HOLD_DUPLICATE_DELIVERY_REQUIRES_REMOTE_WITNESS, False, True, False, False, False, False, "duplicate delivery needs remote witness", idempotency_mesh_report=idempotency_mesh_report, retry_publish_report=retry_publish_report, egress_journal_report=egress_journal_report, witnesses=witnesses)
    digests = [w.witness_digest for w in witnesses]
    seen = set(seen_witness_digests)
    if any(d in seen for d in digests) or len(set(digests)) != len(digests):
        return _report(DeliveryRepairMeshDecisionKind.QUARANTINE_REPLAY, False, False, False, False, False, False, "remote witness replay", idempotency_mesh_report=idempotency_mesh_report, retry_publish_report=retry_publish_report, egress_journal_report=egress_journal_report, witnesses=witnesses)
    by_seq: dict[int, set[bytes]] = {}
    for witness in witnesses:
        by_seq.setdefault(witness.sequence, set()).add(witness.witness_digest)
    if any(len(values) > 1 for values in by_seq.values()):
        return _report(DeliveryRepairMeshDecisionKind.QUARANTINE_SEQUENCE_FORK, False, False, False, False, False, False, "same-sequence remote witness fork", idempotency_mesh_report=idempotency_mesh_report, retry_publish_report=retry_publish_report, egress_journal_report=egress_journal_report, witnesses=witnesses)
    ordered = sorted(witnesses, key=lambda w: w.sequence)
    if ordered[0].previous_digest != previous_digest:
        return _report(DeliveryRepairMeshDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, False, False, False, False, False, "previous-link mismatch", idempotency_mesh_report=idempotency_mesh_report, retry_publish_report=retry_publish_report, egress_journal_report=egress_journal_report, witnesses=witnesses)
    if any(_witness_boundary(w) != _boundary(idempotency_mesh_report) for w in witnesses):
        return _report(DeliveryRepairMeshDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, False, False, False, False, "remote witness boundary drift", idempotency_mesh_report=idempotency_mesh_report, retry_publish_report=retry_publish_report, egress_journal_report=egress_journal_report, witnesses=witnesses)
    if any(w.idempotency_mesh_digest != _digest(idempotency_mesh_report) or w.retry_publish_digest != _digest(retry_publish_report) or w.egress_journal_digest != _digest(egress_journal_report) for w in witnesses):
        return _report(DeliveryRepairMeshDecisionKind.QUARANTINE_WITNESS_DIGEST_DRIFT, False, False, False, False, False, False, "witness component digest drift", idempotency_mesh_report=idempotency_mesh_report, retry_publish_report=retry_publish_report, egress_journal_report=egress_journal_report, witnesses=witnesses)
    if sum(w.hard_negative_count for w in witnesses):
        return _report(DeliveryRepairMeshDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, False, False, False, False, "witness hard-negative pressure", idempotency_mesh_report=idempotency_mesh_report, retry_publish_report=retry_publish_report, egress_journal_report=egress_journal_report, witnesses=witnesses)
    if len({w.family_id for w in witnesses}) < min_family_count:
        return _report(DeliveryRepairMeshDecisionKind.HOLD_LOW_WITNESS_DIVERSITY, False, True, False, False, False, False, "low remote witness family diversity", idempotency_mesh_report=idempotency_mesh_report, retry_publish_report=retry_publish_report, egress_journal_report=egress_journal_report, witnesses=witnesses)
    if len({w.path_family_id for w in witnesses}) < min_path_family_count:
        return _report(DeliveryRepairMeshDecisionKind.HOLD_LOW_WITNESS_PATH_DIVERSITY, False, True, False, False, False, False, "low remote witness path diversity", idempotency_mesh_report=idempotency_mesh_report, retry_publish_report=retry_publish_report, egress_journal_report=egress_journal_report, witnesses=witnesses)
    if any(w.kind is RemoteDeliveryWitnessKind.REMOTE_DUPLICATE_CONFLICT for w in witnesses):
        return _report(DeliveryRepairMeshDecisionKind.ACCEPT_REPAIR_REQUIRED_REMOTE_CONFLICT, True, True, True, False, True, False, "remote duplicate conflict requires repair", idempotency_mesh_report=idempotency_mesh_report, retry_publish_report=retry_publish_report, egress_journal_report=egress_journal_report, witnesses=witnesses, accepted_witness_digest=ordered[-1].witness_digest)
    if all(w.kind is RemoteDeliveryWitnessKind.REMOTE_MATCHES_PAYLOAD for w in witnesses):
        return _report(DeliveryRepairMeshDecisionKind.ACCEPT_DUPLICATE_BENIGN_WITH_WITNESS, True, False, False, False, False, True, "duplicate delivery appears benign under remote witnesses", idempotency_mesh_report=idempotency_mesh_report, retry_publish_report=retry_publish_report, egress_journal_report=egress_journal_report, witnesses=witnesses, accepted_witness_digest=ordered[-1].witness_digest)
    return _report(DeliveryRepairMeshDecisionKind.HOLD_DUPLICATE_DELIVERY_REQUIRES_REMOTE_WITNESS, False, True, False, False, False, False, "remote witnesses not decisive", idempotency_mesh_report=idempotency_mesh_report, retry_publish_report=retry_publish_report, egress_journal_report=egress_journal_report, witnesses=witnesses)
