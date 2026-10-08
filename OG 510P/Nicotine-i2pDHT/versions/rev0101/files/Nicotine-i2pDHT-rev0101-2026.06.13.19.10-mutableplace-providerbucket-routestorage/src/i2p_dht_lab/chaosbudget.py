"""Chaos budget after effect sealing and recovery.

rev0056 adds a local budget lane for expensive post-effect work: restart
replays, retry probes, cleanup, fuzz shrink checks, and future canary rehearsals.
A sealed effect plus accepted recovery does not authorize unbounded chaos work or
metadata spend.
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

CHAOS_BUDGET_DOMAIN = DOMAIN + b":chaos-budget-v1:"


class ChaosLane(str, Enum):
    RESTART_REPLAY = "restart_replay"
    EFFECT_RECOVERY = "effect_recovery"
    SAFE_CLEANUP = "safe_cleanup"
    FUZZ_SHRINK = "fuzz_shrink"
    RETRY_PROBE = "retry_probe"
    DEAD_LETTER = "dead_letter"
    SAM_CANARY = "sam_canary"


class ChaosBudgetDecisionKind(str, Enum):
    ACCEPT_BUDGET = "accept_budget"
    ACCEPT_WITH_WATCH = "accept_with_watch"
    EMPTY_NO_GRANTS = "empty_no_grants"
    HOLD_RECOVERY_MESH = "hold_recovery_mesh"
    HOLD_SAFE_CLEANUP = "hold_safe_cleanup"
    HOLD_COMPONENT_WATCH = "hold_component_watch"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    HOLD_PROTECTED_RESERVE_LOW = "hold_protected_reserve_low"
    HOLD_RETRY_WITHOUT_WATCH = "hold_retry_without_watch"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_EXPIRED_OR_FUTURE = "quarantine_expired_or_future"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_PROFILE_DRIFT = "quarantine_profile_drift"
    QUARANTINE_SERVICE_DRIFT = "quarantine_service_drift"
    QUARANTINE_ACTION_DRIFT = "quarantine_action_drift"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_REQUEST_DRIFT = "quarantine_request_drift"
    QUARANTINE_PAYLOAD_DRIFT = "quarantine_payload_drift"
    QUARANTINE_IDEMPOTENCY_DRIFT = "quarantine_idempotency_drift"
    QUARANTINE_COMPONENT_DIGEST_DRIFT = "quarantine_component_digest_drift"
    QUARANTINE_TOTAL_BUDGET_EXCEEDED = "quarantine_total_budget_exceeded"
    QUARANTINE_RAW_KEY_BUDGET_EXCEEDED = "quarantine_raw_key_budget_exceeded"
    QUARANTINE_LANE_CAP_EXCEEDED = "quarantine_lane_cap_exceeded"
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"


@dataclass(frozen=True)
class ChaosBudgetGrant:
    lane: ChaosLane
    action: SideEffectAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    effect_seal_digest: bytes
    recovery_mesh_digest: bytes
    safe_cleanup_digest: bytes
    restart_chaos_digest: bytes
    fuzz_shrink_digest: bytes
    budget_units: int
    raw_key_units: int
    decoy_units: int
    protected_reserve_units: int
    hard_negative_count: int
    sequence: int
    previous_grant_digest: bytes
    issued_at: int
    expires_at: int
    family_id: str
    path_family: str
    signer_public_key: bytes
    signature: bytes = b""

    def __post_init__(self) -> None:
        object.__setattr__(self, "lane", ChaosLane(self.lane))
        object.__setattr__(self, "action", SideEffectAction(self.action))
        if not self.profile_id or not self.service_name or not self.family_id or not self.path_family:
            raise ValueError("chaos budget grant needs profile/service/family/path")
        if min(self.budget_units, self.raw_key_units, self.decoy_units, self.protected_reserve_units, self.hard_negative_count, self.sequence) < 0:
            raise ValueError("budget counts and sequence must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("expires_at must follow issued_at")
        for name, value in (
            ("scope_digest", self.scope_digest),
            ("request_digest", self.request_digest),
            ("payload_digest", self.payload_digest),
            ("idempotency_key", self.idempotency_key),
            ("effect_seal_digest", self.effect_seal_digest),
            ("recovery_mesh_digest", self.recovery_mesh_digest),
            ("safe_cleanup_digest", self.safe_cleanup_digest),
            ("restart_chaos_digest", self.restart_chaos_digest),
            ("fuzz_shrink_digest", self.fuzz_shrink_digest),
            ("previous_grant_digest", self.previous_grant_digest),
            ("signer_public_key", self.signer_public_key),
        ):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if self.signature and len(self.signature) != 64:
            raise ValueError("signature must be empty or Ed25519-sized")

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"lane": self.lane.value,
            b"action": self.action.value,
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"payload": self.payload_digest,
            b"idem": self.idempotency_key,
            b"effect_seal": self.effect_seal_digest,
            b"recovery": self.recovery_mesh_digest,
            b"cleanup": self.safe_cleanup_digest,
            b"restart": self.restart_chaos_digest,
            b"fuzz_shrink": self.fuzz_shrink_digest,
            b"budget": self.budget_units,
            b"raw": self.raw_key_units,
            b"decoy": self.decoy_units,
            b"reserve": self.protected_reserve_units,
            b"hard": self.hard_negative_count,
            b"seq": self.sequence,
            b"prev": self.previous_grant_digest,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"family": self.family_id,
            b"path_family": self.path_family,
            b"signer": self.signer_public_key,
        }

    def signature_payload(self) -> bytes:
        return CHAOS_BUDGET_DOMAIN + b":grant-sig:" + bencode(self.unsigned_bvalue())

    @property
    def grant_core_digest(self) -> bytes:
        return sha256(CHAOS_BUDGET_DOMAIN + b":grant-core:" + bencode(self.unsigned_bvalue()))

    @property
    def grant_digest(self) -> bytes:
        return sha256(CHAOS_BUDGET_DOMAIN + b":grant-digest:" + self.signature_payload() + self.signature)

    def verifies(self) -> bool:
        return verify_signature(self.signer_public_key, self.signature_payload(), self.signature)

    def live(self, now: int) -> bool:
        return self.issued_at <= now < self.expires_at


@dataclass(frozen=True)
class ChaosBudgetReport:
    decision_kind: ChaosBudgetDecisionKind
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
    accepted_grant_digest: bytes
    grant_digests: tuple[bytes, ...]
    component_digests: tuple[bytes, ...]
    lanes: tuple[ChaosLane, ...]
    total_budget_units: int
    total_raw_key_units: int
    total_decoy_units: int
    minimum_protected_reserve_units: int
    highest_sequence: int
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
    for attr in ("report_digest", "transcript_digest", "canary_digest"):
        value = getattr(report, attr, None)
        if isinstance(value, bytes) and len(value) == 32:
            return value
    raise ValueError("component lacks 32-byte digest")


def _accept(report: Any | None) -> bool:
    return bool(getattr(report, "accept", False)) if report is not None else False


def _watch(report: Any | None) -> bool:
    return bool(getattr(report, "watch", False)) if report is not None else False


def _quarantined(report: Any | None) -> bool:
    return bool(getattr(report, "quarantined", False)) if report is not None else False


def make_chaos_budget_grant(
    *,
    keypair: DhtKeypair,
    lane: ChaosLane,
    effect_seal_report: Any,
    recovery_mesh_report: Any,
    safe_cleanup_report: Any,
    restart_chaos_report: Any,
    fuzz_shrink_report: Any,
    budget_units: int,
    raw_key_units: int = 0,
    decoy_units: int = 0,
    protected_reserve_units: int = 0,
    hard_negative_count: int = 0,
    sequence: int,
    previous_grant_digest: bytes = ZERO_DIGEST,
    issued_at: int,
    expires_at: int,
    family_id: str,
    path_family: str,
) -> ChaosBudgetGrant:
    unsigned = ChaosBudgetGrant(
        lane=lane,
        action=SideEffectAction(getattr(effect_seal_report, "action")),
        profile_id=getattr(effect_seal_report, "profile_id"),
        service_name=getattr(effect_seal_report, "service_name"),
        scope_digest=getattr(effect_seal_report, "scope_digest"),
        request_digest=getattr(effect_seal_report, "request_digest"),
        payload_digest=getattr(effect_seal_report, "payload_digest"),
        idempotency_key=getattr(effect_seal_report, "idempotency_key"),
        effect_seal_digest=_digest(effect_seal_report),
        recovery_mesh_digest=_digest(recovery_mesh_report),
        safe_cleanup_digest=_digest(safe_cleanup_report),
        restart_chaos_digest=_digest(restart_chaos_report),
        fuzz_shrink_digest=_digest(fuzz_shrink_report),
        budget_units=budget_units,
        raw_key_units=raw_key_units,
        decoy_units=decoy_units,
        protected_reserve_units=protected_reserve_units,
        hard_negative_count=hard_negative_count,
        sequence=sequence,
        previous_grant_digest=previous_grant_digest,
        issued_at=issued_at,
        expires_at=expires_at,
        family_id=family_id,
        path_family=path_family,
        signer_public_key=keypair.public_key_bytes,
    )
    return replace(unsigned, signature=keypair.sign(unsigned.signature_payload()))


def assess_chaos_budget(
    grants: Iterable[ChaosBudgetGrant],
    *,
    effect_seal_report: Any,
    recovery_mesh_report: Any,
    safe_cleanup_report: Any,
    restart_chaos_report: Any,
    fuzz_shrink_report: Any,
    now: int,
    previous_seen_grant_digests: Iterable[bytes] = (),
    highest_seen_sequence: int | None = None,
    total_budget_cap: int = 100,
    raw_key_budget_cap: int = 2,
    lane_caps: dict[ChaosLane, int] | None = None,
    min_protected_reserve_units: int = 1,
    min_family_count: int = 2,
    min_path_family_count: int = 2,
    allow_component_watch: bool = False,
) -> ChaosBudgetReport:
    grant_t = tuple(grants)
    action = SideEffectAction(getattr(effect_seal_report, "action"))
    profile_id = getattr(effect_seal_report, "profile_id")
    service_name = getattr(effect_seal_report, "service_name")
    scope_digest = getattr(effect_seal_report, "scope_digest")
    request_digest = getattr(effect_seal_report, "request_digest")
    payload_digest = getattr(effect_seal_report, "payload_digest")
    idempotency_key = getattr(effect_seal_report, "idempotency_key")
    components = (effect_seal_report, recovery_mesh_report, safe_cleanup_report, restart_chaos_report, fuzz_shrink_report)
    component_digests = tuple(_digest(component) for component in components)
    common = dict(action=action, profile_id=profile_id, service_name=service_name, scope_digest=scope_digest, request_digest=request_digest, payload_digest=payload_digest, idempotency_key=idempotency_key, component_digests=component_digests)
    if not grant_t:
        return _report(ChaosBudgetDecisionKind.EMPTY_NO_GRANTS, False, False, "chaos budget needs grants", grants=grant_t, **common)
    if not _accept(recovery_mesh_report) or _quarantined(recovery_mesh_report):
        return _report(ChaosBudgetDecisionKind.HOLD_RECOVERY_MESH, False, True, "recovery mesh not accepted", grants=grant_t, **common)
    if not _accept(safe_cleanup_report) or _quarantined(safe_cleanup_report):
        return _report(ChaosBudgetDecisionKind.HOLD_SAFE_CLEANUP, False, True, "safe cleanup not accepted", grants=grant_t, **common)
    if any(_quarantined(component) for component in components):
        return _report(ChaosBudgetDecisionKind.QUARANTINE_COMPONENT_DIGEST_DRIFT, False, False, "component quarantined", grants=grant_t, **common)
    if any(_watch(component) for component in components) and not allow_component_watch:
        return _report(ChaosBudgetDecisionKind.HOLD_COMPONENT_WATCH, False, True, "component watch pressure must be carried", grants=grant_t, **common)

    caps = lane_caps or {
        ChaosLane.RESTART_REPLAY: 40,
        ChaosLane.EFFECT_RECOVERY: 20,
        ChaosLane.SAFE_CLEANUP: 20,
        ChaosLane.FUZZ_SHRINK: 20,
        ChaosLane.RETRY_PROBE: 12,
        ChaosLane.DEAD_LETTER: 8,
        ChaosLane.SAM_CANARY: 10,
    }
    seen = set(previous_seen_grant_digests)
    by_sequence: dict[int, ChaosBudgetGrant] = {}
    by_lane: dict[ChaosLane, int] = {}
    for grant in grant_t:
        if not grant.verifies():
            return _report(ChaosBudgetDecisionKind.QUARANTINE_BAD_SIGNATURE, False, False, "bad chaos budget signature", grants=grant_t, **common)
        if not grant.live(now):
            return _report(ChaosBudgetDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, False, False, "expired or future budget grant", grants=grant_t, **common)
        if grant.grant_digest in seen:
            return _report(ChaosBudgetDecisionKind.QUARANTINE_REPLAY, False, False, "replayed budget grant", grants=grant_t, **common)
        if highest_seen_sequence is not None and grant.sequence < highest_seen_sequence:
            return _report(ChaosBudgetDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, False, "budget sequence rollback", grants=grant_t, **common)
        prior = by_sequence.get(grant.sequence)
        if prior is not None and prior.grant_core_digest != grant.grant_core_digest:
            return _report(ChaosBudgetDecisionKind.QUARANTINE_SEQUENCE_FORK, False, False, "same-sequence budget fork", grants=grant_t, **common)
        by_sequence[grant.sequence] = grant
        by_lane[grant.lane] = by_lane.get(grant.lane, 0) + grant.budget_units
        if grant.profile_id != profile_id:
            return _report(ChaosBudgetDecisionKind.QUARANTINE_PROFILE_DRIFT, False, False, "profile drift", grants=grant_t, **common)
        if grant.service_name != service_name:
            return _report(ChaosBudgetDecisionKind.QUARANTINE_SERVICE_DRIFT, False, False, "service drift", grants=grant_t, **common)
        if grant.action is not action:
            return _report(ChaosBudgetDecisionKind.QUARANTINE_ACTION_DRIFT, False, False, "action drift", grants=grant_t, **common)
        if grant.scope_digest != scope_digest:
            return _report(ChaosBudgetDecisionKind.QUARANTINE_SCOPE_DRIFT, False, False, "scope drift", grants=grant_t, **common)
        if grant.request_digest != request_digest:
            return _report(ChaosBudgetDecisionKind.QUARANTINE_REQUEST_DRIFT, False, False, "request drift", grants=grant_t, **common)
        if grant.payload_digest != payload_digest:
            return _report(ChaosBudgetDecisionKind.QUARANTINE_PAYLOAD_DRIFT, False, False, "payload drift", grants=grant_t, **common)
        if grant.idempotency_key != idempotency_key:
            return _report(ChaosBudgetDecisionKind.QUARANTINE_IDEMPOTENCY_DRIFT, False, False, "idempotency drift", grants=grant_t, **common)
        if (grant.effect_seal_digest, grant.recovery_mesh_digest, grant.safe_cleanup_digest, grant.restart_chaos_digest, grant.fuzz_shrink_digest) != component_digests:
            return _report(ChaosBudgetDecisionKind.QUARANTINE_COMPONENT_DIGEST_DRIFT, False, False, "component digest drift", grants=grant_t, **common)
        if grant.hard_negative_count:
            return _report(ChaosBudgetDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, "hard negatives block chaos budget", grants=grant_t, **common)
    ordered = sorted(by_sequence.values(), key=lambda item: item.sequence)
    for left, right in zip(ordered, ordered[1:]):
        if right.sequence == left.sequence + 1 and right.previous_grant_digest != left.grant_digest:
            return _report(ChaosBudgetDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, False, "budget previous-link mismatch", grants=grant_t, **common)
    total = sum(grant.budget_units for grant in grant_t)
    raw = sum(grant.raw_key_units for grant in grant_t)
    reserve = min((grant.protected_reserve_units for grant in grant_t), default=0)
    if total > total_budget_cap:
        return _report(ChaosBudgetDecisionKind.QUARANTINE_TOTAL_BUDGET_EXCEEDED, False, False, "total chaos budget exceeded", grants=grant_t, **common)
    if raw > raw_key_budget_cap:
        return _report(ChaosBudgetDecisionKind.QUARANTINE_RAW_KEY_BUDGET_EXCEEDED, False, False, "raw-key chaos budget exceeded", grants=grant_t, **common)
    for lane, used in by_lane.items():
        if used > caps.get(lane, total_budget_cap):
            return _report(ChaosBudgetDecisionKind.QUARANTINE_LANE_CAP_EXCEEDED, False, False, "lane budget cap exceeded", grants=grant_t, **common)
    if reserve < min_protected_reserve_units:
        return _report(ChaosBudgetDecisionKind.HOLD_PROTECTED_RESERVE_LOW, False, True, "protected reserve too low", grants=grant_t, **common)
    recovery_outcome = getattr(recovery_mesh_report, "outcome", None)
    recovery_outcome_value = getattr(recovery_outcome, "value", recovery_outcome)
    if ChaosLane.RETRY_PROBE in by_lane and not (_watch(recovery_mesh_report) or recovery_outcome_value == "retry_needed"):
        # Retrying after a stable committed/aborted recovery is suspicious unless an upstream watch carries it.
        return _report(ChaosBudgetDecisionKind.HOLD_RETRY_WITHOUT_WATCH, False, True, "retry budget without recovery watch", grants=grant_t, **common)
    families = {grant.family_id for grant in grant_t}
    paths = {grant.path_family for grant in grant_t}
    if len(families) < min_family_count:
        return _report(ChaosBudgetDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, "chaos budget needs family diversity", grants=grant_t, **common)
    if len(paths) < min_path_family_count:
        return _report(ChaosBudgetDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, "chaos budget needs path diversity", grants=grant_t, **common)
    if any(_watch(component) for component in components):
        return _report(ChaosBudgetDecisionKind.ACCEPT_WITH_WATCH, True, True, "chaos budget accepted with watch", grants=grant_t, accepted=ordered[-1], **common)
    return _report(ChaosBudgetDecisionKind.ACCEPT_BUDGET, True, False, "chaos budget accepted", grants=grant_t, accepted=ordered[-1], **common)


def _report(kind: ChaosBudgetDecisionKind, accept: bool, watch: bool, reason: str, *, action: SideEffectAction, profile_id: str, service_name: str, scope_digest: bytes, request_digest: bytes, payload_digest: bytes, idempotency_key: bytes, component_digests: tuple[bytes, ...], grants: Iterable[ChaosBudgetGrant], accepted: ChaosBudgetGrant | None = None) -> ChaosBudgetReport:
    grant_t = tuple(grants)
    digests = tuple(grant.grant_digest for grant in grant_t)
    lanes = tuple(sorted({grant.lane for grant in grant_t}, key=lambda lane: lane.value))
    total = sum(grant.budget_units for grant in grant_t)
    raw = sum(grant.raw_key_units for grant in grant_t)
    decoy = sum(grant.decoy_units for grant in grant_t)
    reserve = min((grant.protected_reserve_units for grant in grant_t), default=0)
    highest = max((grant.sequence for grant in grant_t), default=-1)
    families = {grant.family_id for grant in grant_t}
    paths = {grant.path_family for grant in grant_t}
    hard = sum(grant.hard_negative_count for grant in grant_t)
    accepted_digest = accepted.grant_digest if accepted else ZERO_DIGEST
    digest = sha256(CHAOS_BUDGET_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"reason": reason,
        b"action": action.value,
        b"profile": profile_id,
        b"service": service_name,
        b"scope": scope_digest,
        b"request": request_digest,
        b"payload": payload_digest,
        b"idem": idempotency_key,
        b"accepted": accepted_digest,
        b"grants": list(digests),
        b"components": list(component_digests),
        b"lanes": [lane.value for lane in lanes],
        b"total": total,
        b"raw": raw,
        b"decoy": decoy,
        b"reserve": reserve,
        b"highest": highest,
        b"families": len(families),
        b"paths": len(paths),
        b"hard": hard,
    }))
    return ChaosBudgetReport(kind, accept, watch, reason, action, profile_id, service_name, scope_digest, request_digest, payload_digest, idempotency_key, accepted_digest, digests, component_digests, lanes, total, raw, decoy, reserve, highest, len(families), len(paths), hard, digest)
