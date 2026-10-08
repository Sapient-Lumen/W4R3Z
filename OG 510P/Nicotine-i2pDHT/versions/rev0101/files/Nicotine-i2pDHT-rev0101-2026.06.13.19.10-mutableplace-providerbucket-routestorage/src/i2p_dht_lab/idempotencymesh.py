"""rev0064 idempotency mesh for original/retry/withdraw delivery lineages.

The DHT must not pretend that idempotency keys make duplicate publication safe.
This lane joins late ACKs, retry settlement, retry publication staging, and the
egress journal into a local lineage assessment that can accept simple cases,
hold duplicate-delivery contradictions, or quarantine key/payload drift.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable

from .bencode import bencode
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectAction

IDEMPOTENCY_MESH_DOMAIN = DOMAIN + b":idempotency-mesh-v1:"


class IdempotencyObservationKind(str, Enum):
    ORIGINAL_ACK = "original_ack"
    RETRY_SETTLEMENT = "retry_settlement"
    RETRY_PUBLICATION = "retry_publication"
    WITHDRAW_REPAIR = "withdraw_repair"
    CONTRADICTION = "contradiction"


class IdempotencyMeshDecisionKind(str, Enum):
    ACCEPT_ORIGINAL_ACK_SUPPRESSED_RETRY = "accept_original_ack_suppressed_retry"
    ACCEPT_RETRY_ONLY_LINEAGE = "accept_retry_only_lineage"
    ACCEPT_WITHDRAW_REPAIR_LINEAGE = "accept_withdraw_repair_lineage"
    HOLD_DUPLICATE_DELIVERY_INVESTIGATION = "hold_duplicate_delivery_investigation"
    HOLD_LINEAGE_PENDING = "hold_lineage_pending"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    QUARANTINE_COMPONENT_NOT_ACCEPTED = "quarantine_component_not_accepted"
    QUARANTINE_BOUNDARY_DRIFT = "quarantine_boundary_drift"
    QUARANTINE_KEY_OR_PAYLOAD_DRIFT = "quarantine_key_or_payload_drift"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_DROPPED_CONTRADICTION = "quarantine_dropped_contradiction"
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"


@dataclass(frozen=True)
class IdempotencyObservation:
    kind: IdempotencyObservationKind
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
    late_ack_digest: bytes
    retry_settlement_digest: bytes
    retry_publish_digest: bytes
    egress_journal_digest: bytes
    family_id: str
    path_family_id: str
    hard_negative_count: int = 0

    @property
    def observation_digest(self) -> bytes:
        return sha256(IDEMPOTENCY_MESH_DOMAIN + b":obs:" + bencode({
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
            b"late_ack": self.late_ack_digest,
            b"settlement": self.retry_settlement_digest,
            b"publish": self.retry_publish_digest,
            b"journal": self.egress_journal_digest,
            b"family": self.family_id,
            b"path": self.path_family_id,
            b"hard": self.hard_negative_count,
        }))


@dataclass(frozen=True)
class IdempotencyMeshReport:
    decision_kind: IdempotencyMeshDecisionKind
    accept: bool
    watch: bool
    duplicate_delivery_possible: bool
    retry_lineage_terminal: bool
    original_lineage_terminal: bool
    withdraw_lineage_terminal: bool
    reason: str
    action: SideEffectAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    retry_idempotency_key: bytes
    late_ack_digest: bytes
    retry_settlement_digest: bytes
    retry_publish_digest: bytes
    egress_journal_digest: bytes
    accepted_observation_digest: bytes
    observation_digests: tuple[bytes, ...]
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
    for attr in ("report_digest", "accepted_marker_digest", "accepted_observation_digest", "accepted_entry_digest"):
        value = getattr(report, attr, None)
        if isinstance(value, bytes) and len(value) == 32:
            return value
    raise ValueError("component lacks digest")


def _base_report(*reports: Any | None) -> Any:
    for report in reports:
        if report is not None:
            return report
    raise ValueError("idempotency mesh needs at least one component")


def _boundary(report: Any) -> tuple[Any, ...]:
    return (SideEffectAction(getattr(report, "action")), getattr(report, "profile_id"), getattr(report, "service_name"), getattr(report, "scope_digest"), getattr(report, "request_digest"), getattr(report, "payload_digest"), getattr(report, "idempotency_key"))


def _obs_boundary(obs: IdempotencyObservation) -> tuple[Any, ...]:
    return (SideEffectAction(obs.action), obs.profile_id, obs.service_name, obs.scope_digest, obs.request_digest, obs.payload_digest, obs.idempotency_key)


def make_idempotency_observation(*, kind: IdempotencyObservationKind, sequence: int, base_report: Any, late_ack_report: Any | None = None, retry_settlement_report: Any | None = None, retry_publish_report: Any | None = None, egress_journal_report: Any | None = None, previous_digest: bytes = ZERO_DIGEST, family_id: str = "family-a", path_family_id: str = "path-a", hard_negative_count: int = 0) -> IdempotencyObservation:
    return IdempotencyObservation(
        kind=IdempotencyObservationKind(kind),
        sequence=sequence,
        previous_digest=previous_digest,
        action=SideEffectAction(getattr(base_report, "action")),
        profile_id=getattr(base_report, "profile_id"),
        service_name=getattr(base_report, "service_name"),
        scope_digest=getattr(base_report, "scope_digest"),
        request_digest=getattr(base_report, "request_digest"),
        payload_digest=getattr(base_report, "payload_digest"),
        idempotency_key=getattr(base_report, "idempotency_key"),
        retry_idempotency_key=getattr(base_report, "retry_idempotency_key", ZERO_DIGEST),
        late_ack_digest=_digest(late_ack_report),
        retry_settlement_digest=_digest(retry_settlement_report),
        retry_publish_digest=_digest(retry_publish_report),
        egress_journal_digest=_digest(egress_journal_report),
        family_id=family_id,
        path_family_id=path_family_id,
        hard_negative_count=hard_negative_count,
    )


def _report(kind: IdempotencyMeshDecisionKind, accept: bool, watch: bool, duplicate: bool, retry_terminal: bool, original_terminal: bool, withdraw_terminal: bool, reason: str, *, late_ack_report: Any | None, retry_settlement_report: Any | None, retry_publish_report: Any | None, egress_journal_report: Any | None, observations: tuple[IdempotencyObservation, ...], accepted_observation_digest: bytes = ZERO_DIGEST) -> IdempotencyMeshReport:
    base = _base_report(retry_settlement_report, late_ack_report, retry_publish_report, egress_journal_report)
    digests = tuple(obs.observation_digest for obs in observations)
    families = {obs.family_id for obs in observations}
    paths = {obs.path_family_id for obs in observations}
    components = tuple(c for c in (late_ack_report, retry_settlement_report, retry_publish_report, egress_journal_report) if c is not None)
    hard = sum(int(getattr(c, "hard_negative_count", 0) or 0) for c in components) + sum(obs.hard_negative_count for obs in observations)
    report_digest = sha256(IDEMPOTENCY_MESH_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"duplicate": 1 if duplicate else 0,
        b"retry_terminal": 1 if retry_terminal else 0,
        b"original_terminal": 1 if original_terminal else 0,
        b"withdraw_terminal": 1 if withdraw_terminal else 0,
        b"late_ack": _digest(late_ack_report),
        b"settlement": _digest(retry_settlement_report),
        b"publish": _digest(retry_publish_report),
        b"journal": _digest(egress_journal_report),
        b"obs": list(digests),
        b"families": len(families),
        b"paths": len(paths),
        b"hard": hard,
    }))
    return IdempotencyMeshReport(kind, accept, watch, duplicate, retry_terminal, original_terminal, withdraw_terminal, reason, SideEffectAction(getattr(base, "action")), getattr(base, "profile_id"), getattr(base, "service_name"), getattr(base, "scope_digest"), getattr(base, "request_digest"), getattr(base, "payload_digest"), getattr(base, "idempotency_key"), getattr(base, "retry_idempotency_key", ZERO_DIGEST), _digest(late_ack_report), _digest(retry_settlement_report), _digest(retry_publish_report), _digest(egress_journal_report), accepted_observation_digest, digests, len(families), len(paths), hard, report_digest)


def assess_idempotency_mesh(*, late_ack_report: Any | None = None, retry_settlement_report: Any | None = None, retry_publish_report: Any | None = None, egress_journal_report: Any | None = None, observations: Iterable[IdempotencyObservation] = (), previous_digest: bytes = ZERO_DIGEST, seen_observation_digests: Iterable[bytes] = (), min_family_count: int = 2, min_path_family_count: int = 2) -> IdempotencyMeshReport:
    obs_tuple = tuple(observations)
    components = tuple(c for c in (late_ack_report, retry_settlement_report, retry_publish_report, egress_journal_report) if c is not None)
    if not components:
        raise ValueError("idempotency mesh needs at least one component report")
    if any(bool(getattr(c, "quarantined", False)) for c in components):
        return _report(IdempotencyMeshDecisionKind.QUARANTINE_COMPONENT_NOT_ACCEPTED, False, False, False, False, False, False, "component quarantined", late_ack_report=late_ack_report, retry_settlement_report=retry_settlement_report, retry_publish_report=retry_publish_report, egress_journal_report=egress_journal_report, observations=obs_tuple)
    if retry_settlement_report is not None and not (bool(getattr(retry_settlement_report, "accept", False)) or bool(getattr(retry_settlement_report, "watch", False))):
        return _report(IdempotencyMeshDecisionKind.QUARANTINE_COMPONENT_NOT_ACCEPTED, False, False, False, False, False, False, "retry settlement neither accepted nor watchful", late_ack_report=late_ack_report, retry_settlement_report=retry_settlement_report, retry_publish_report=retry_publish_report, egress_journal_report=egress_journal_report, observations=obs_tuple)
    if egress_journal_report is not None and not bool(getattr(egress_journal_report, "accept", False)):
        return _report(IdempotencyMeshDecisionKind.QUARANTINE_COMPONENT_NOT_ACCEPTED, False, False, False, False, False, False, "egress journal not accepted", late_ack_report=late_ack_report, retry_settlement_report=retry_settlement_report, retry_publish_report=retry_publish_report, egress_journal_report=egress_journal_report, observations=obs_tuple)
    if retry_publish_report is not None and bool(getattr(retry_publish_report, "quarantined", False)):
        return _report(IdempotencyMeshDecisionKind.QUARANTINE_COMPONENT_NOT_ACCEPTED, False, False, False, False, False, False, "retry publication quarantined", late_ack_report=late_ack_report, retry_settlement_report=retry_settlement_report, retry_publish_report=retry_publish_report, egress_journal_report=egress_journal_report, observations=obs_tuple)
    if any(_boundary(c) != _boundary(components[0]) for c in components):
        return _report(IdempotencyMeshDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, False, False, False, False, "component boundary drift", late_ack_report=late_ack_report, retry_settlement_report=retry_settlement_report, retry_publish_report=retry_publish_report, egress_journal_report=egress_journal_report, observations=obs_tuple)
    if sum(int(getattr(c, "hard_negative_count", 0) or 0) for c in components):
        return _report(IdempotencyMeshDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, False, False, False, False, "component hard-negative pressure", late_ack_report=late_ack_report, retry_settlement_report=retry_settlement_report, retry_publish_report=retry_publish_report, egress_journal_report=egress_journal_report, observations=obs_tuple)
    if not obs_tuple:
        return _report(IdempotencyMeshDecisionKind.HOLD_LINEAGE_PENDING, False, True, False, False, False, False, "idempotency observations pending", late_ack_report=late_ack_report, retry_settlement_report=retry_settlement_report, retry_publish_report=retry_publish_report, egress_journal_report=egress_journal_report, observations=obs_tuple)
    digests = [obs.observation_digest for obs in obs_tuple]
    seen = set(seen_observation_digests)
    if any(d in seen for d in digests) or len(set(digests)) != len(digests):
        return _report(IdempotencyMeshDecisionKind.QUARANTINE_REPLAY, False, False, False, False, False, False, "observation replay", late_ack_report=late_ack_report, retry_settlement_report=retry_settlement_report, retry_publish_report=retry_publish_report, egress_journal_report=egress_journal_report, observations=obs_tuple)
    by_seq: dict[int, set[bytes]] = {}
    for obs in obs_tuple:
        by_seq.setdefault(obs.sequence, set()).add(obs.observation_digest)
    if any(len(values) > 1 for values in by_seq.values()):
        return _report(IdempotencyMeshDecisionKind.QUARANTINE_SEQUENCE_FORK, False, False, False, False, False, False, "same-sequence idempotency fork", late_ack_report=late_ack_report, retry_settlement_report=retry_settlement_report, retry_publish_report=retry_publish_report, egress_journal_report=egress_journal_report, observations=obs_tuple)
    ordered = sorted(obs_tuple, key=lambda obs: obs.sequence)
    if ordered[0].previous_digest != previous_digest:
        return _report(IdempotencyMeshDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, False, False, False, False, False, "previous-link mismatch", late_ack_report=late_ack_report, retry_settlement_report=retry_settlement_report, retry_publish_report=retry_publish_report, egress_journal_report=egress_journal_report, observations=obs_tuple)
    if any(_obs_boundary(obs) != _boundary(components[0]) for obs in obs_tuple):
        return _report(IdempotencyMeshDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, False, False, False, False, "observation boundary drift", late_ack_report=late_ack_report, retry_settlement_report=retry_settlement_report, retry_publish_report=retry_publish_report, egress_journal_report=egress_journal_report, observations=obs_tuple)
    if any(obs.payload_digest != getattr(components[0], "payload_digest") or obs.idempotency_key != getattr(components[0], "idempotency_key") for obs in obs_tuple):
        return _report(IdempotencyMeshDecisionKind.QUARANTINE_KEY_OR_PAYLOAD_DRIFT, False, False, False, False, False, False, "observation key or payload drift", late_ack_report=late_ack_report, retry_settlement_report=retry_settlement_report, retry_publish_report=retry_publish_report, egress_journal_report=egress_journal_report, observations=obs_tuple)
    if any(obs.late_ack_digest != _digest(late_ack_report) or obs.retry_settlement_digest != _digest(retry_settlement_report) or obs.retry_publish_digest != _digest(retry_publish_report) or obs.egress_journal_digest != _digest(egress_journal_report) for obs in obs_tuple):
        return _report(IdempotencyMeshDecisionKind.QUARANTINE_KEY_OR_PAYLOAD_DRIFT, False, False, False, False, False, False, "observation component digest drift", late_ack_report=late_ack_report, retry_settlement_report=retry_settlement_report, retry_publish_report=retry_publish_report, egress_journal_report=egress_journal_report, observations=obs_tuple)
    if sum(obs.hard_negative_count for obs in obs_tuple):
        return _report(IdempotencyMeshDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, False, False, False, False, "observation hard-negative pressure", late_ack_report=late_ack_report, retry_settlement_report=retry_settlement_report, retry_publish_report=retry_publish_report, egress_journal_report=egress_journal_report, observations=obs_tuple)
    if len({obs.family_id for obs in obs_tuple}) < min_family_count:
        return _report(IdempotencyMeshDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, False, False, False, False, "low idempotency family diversity", late_ack_report=late_ack_report, retry_settlement_report=retry_settlement_report, retry_publish_report=retry_publish_report, egress_journal_report=egress_journal_report, observations=obs_tuple)
    if len({obs.path_family_id for obs in obs_tuple}) < min_path_family_count:
        return _report(IdempotencyMeshDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, False, False, False, False, "low idempotency path diversity", late_ack_report=late_ack_report, retry_settlement_report=retry_settlement_report, retry_publish_report=retry_publish_report, egress_journal_report=egress_journal_report, observations=obs_tuple)
    late_present = bool(getattr(late_ack_report, "late_ack_present", False)) if late_ack_report is not None else False
    retry_terminal = bool(getattr(retry_settlement_report, "retry_terminal", False)) if retry_settlement_report is not None else False
    aborted_by_late_ack = bool(getattr(retry_settlement_report, "aborted_by_late_ack", False)) if retry_settlement_report is not None else False
    withdraw_terminal = bool(getattr(retry_settlement_report, "withdraw_terminal", False)) if retry_settlement_report is not None else False
    contradiction_retained = bool(getattr(egress_journal_report, "contradiction_retained", False)) if egress_journal_report is not None else False
    if late_present and retry_terminal:
        if not contradiction_retained:
            return _report(IdempotencyMeshDecisionKind.QUARANTINE_DROPPED_CONTRADICTION, False, False, True, True, True, False, "late ACK/retry contradiction not retained", late_ack_report=late_ack_report, retry_settlement_report=retry_settlement_report, retry_publish_report=retry_publish_report, egress_journal_report=egress_journal_report, observations=obs_tuple)
        return _report(IdempotencyMeshDecisionKind.HOLD_DUPLICATE_DELIVERY_INVESTIGATION, False, True, True, True, True, False, "late ACK and retry terminal both observed", late_ack_report=late_ack_report, retry_settlement_report=retry_settlement_report, retry_publish_report=retry_publish_report, egress_journal_report=egress_journal_report, observations=obs_tuple)
    if late_present and aborted_by_late_ack:
        return _report(IdempotencyMeshDecisionKind.ACCEPT_ORIGINAL_ACK_SUPPRESSED_RETRY, True, False, False, False, True, False, "original late ACK suppresses retry", late_ack_report=late_ack_report, retry_settlement_report=retry_settlement_report, retry_publish_report=retry_publish_report, egress_journal_report=egress_journal_report, observations=obs_tuple, accepted_observation_digest=ordered[-1].observation_digest)
    if retry_terminal:
        return _report(IdempotencyMeshDecisionKind.ACCEPT_RETRY_ONLY_LINEAGE, True, False, False, True, False, False, "retry-only lineage accepted", late_ack_report=late_ack_report, retry_settlement_report=retry_settlement_report, retry_publish_report=retry_publish_report, egress_journal_report=egress_journal_report, observations=obs_tuple, accepted_observation_digest=ordered[-1].observation_digest)
    if withdraw_terminal:
        return _report(IdempotencyMeshDecisionKind.ACCEPT_WITHDRAW_REPAIR_LINEAGE, True, False, False, False, False, True, "withdraw repair lineage accepted", late_ack_report=late_ack_report, retry_settlement_report=retry_settlement_report, retry_publish_report=retry_publish_report, egress_journal_report=egress_journal_report, observations=obs_tuple, accepted_observation_digest=ordered[-1].observation_digest)
    return _report(IdempotencyMeshDecisionKind.HOLD_LINEAGE_PENDING, False, True, False, False, False, False, "idempotency lineage pending", late_ack_report=late_ack_report, retry_settlement_report=retry_settlement_report, retry_publish_report=retry_publish_report, egress_journal_report=egress_journal_report, observations=obs_tuple)
