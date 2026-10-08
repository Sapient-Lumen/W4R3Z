"""Crash-cut restart chaos lane for the no-network public edge.

rev0055 treats restart as an adversarial schedule, not as a boring replay of
already accepted reports.  Handler replay, side-effect journal state, handler
quench windows, and fuzz-ledger coverage may all be valid on their own while a
crash cut leaves only a prepared side effect, drifts component digests, or loses
watch pressure.  This module keeps that joined restart evidence signed,
previous-linked, and exact-boundary scoped before sticky post-restart state can
advance.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Any, Iterable

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectPhase

RESTART_CHAOS_DOMAIN = DOMAIN + b":restart-chaos-v1:"


class RestartCutLane(str, Enum):
    HANDLER_REPLAY = "handler_replay"
    SIDE_EFFECT_JOURNAL = "side_effect_journal"
    HANDLER_QUENCH = "handler_quench"
    FUZZ_LEDGER = "fuzz_ledger"


class RestartChaosDecisionKind(str, Enum):
    ACCEPT_RESTART_COMMITTED = "accept_restart_committed"
    ACCEPT_RESTART_ABORTED = "accept_restart_aborted"
    ACCEPT_WITH_WATCH = "accept_with_watch"
    EMPTY_NO_CUTS = "empty_no_cuts"
    HOLD_MISSING_LANES = "hold_missing_lanes"
    HOLD_PREPARE_ONLY = "hold_prepare_only"
    HOLD_COMPONENT_WATCH = "hold_component_watch"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    QUARANTINE_COMPONENT_NOT_ACCEPTED = "quarantine_component_not_accepted"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_EXPIRED_OR_FUTURE = "quarantine_expired_or_future"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_PROFILE_DRIFT = "quarantine_profile_drift"
    QUARANTINE_SERVICE_DRIFT = "quarantine_service_drift"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_REQUEST_DRIFT = "quarantine_request_drift"
    QUARANTINE_COMPONENT_DIGEST_DRIFT = "quarantine_component_digest_drift"
    QUARANTINE_PHASE_DRIFT = "quarantine_phase_drift"
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"


@dataclass(frozen=True)
class RestartChaosCut:
    lane: RestartCutLane
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    component_report_digest: bytes
    phase: str
    sequence: int
    previous_cut_digest: bytes
    issued_at: int
    expires_at: int
    hard_negative_count: int
    family_id: str
    path_family: str
    signer_public_key: bytes
    signature: bytes = b""

    def __post_init__(self) -> None:
        object.__setattr__(self, "lane", RestartCutLane(self.lane))
        if not self.profile_id or not self.service_name or not self.phase or not self.family_id or not self.path_family:
            raise ValueError("restart chaos cut requires profile/service/phase/family/path")
        if self.sequence < 0 or self.hard_negative_count < 0:
            raise ValueError("sequence and hard_negative_count must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("expires_at must follow issued_at")
        for name, value in (
            ("scope_digest", self.scope_digest),
            ("request_digest", self.request_digest),
            ("component_report_digest", self.component_report_digest),
            ("previous_cut_digest", self.previous_cut_digest),
            ("signer_public_key", self.signer_public_key),
        ):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if self.signature and len(self.signature) != 64:
            raise ValueError("signature must be empty or Ed25519-sized")

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"lane": self.lane.value,
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"component": self.component_report_digest,
            b"phase": self.phase,
            b"seq": self.sequence,
            b"prev": self.previous_cut_digest,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"hard": self.hard_negative_count,
            b"family": self.family_id,
            b"path_family": self.path_family,
            b"signer": self.signer_public_key,
        }

    def signature_payload(self) -> bytes:
        return RESTART_CHAOS_DOMAIN + b":cut-sig:" + bencode(self.unsigned_bvalue())

    @property
    def cut_core_digest(self) -> bytes:
        return sha256(RESTART_CHAOS_DOMAIN + b":cut-core:" + bencode(self.unsigned_bvalue()))

    @property
    def cut_digest(self) -> bytes:
        return sha256(RESTART_CHAOS_DOMAIN + b":cut-digest:" + self.signature_payload() + self.signature)

    def verifies(self) -> bool:
        return verify_signature(self.signer_public_key, self.signature_payload(), self.signature)

    def live(self, now: int) -> bool:
        return self.issued_at <= now < self.expires_at


@dataclass(frozen=True)
class RestartChaosReport:
    decision_kind: RestartChaosDecisionKind
    accept: bool
    watch: bool
    reason: str
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    required_lanes: tuple[RestartCutLane, ...]
    observed_lanes: tuple[RestartCutLane, ...]
    accepted_cut_digest: bytes
    cut_digests: tuple[bytes, ...]
    component_digests: tuple[bytes, ...]
    highest_sequence: int
    final_phase: SideEffectPhase | None
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
    raise ValueError("component report lacks a 32-byte digest")


def _accept(report: Any | None) -> bool:
    return bool(getattr(report, "accept", False)) if report is not None else False


def _watch(report: Any | None) -> bool:
    return bool(getattr(report, "watch", False)) if report is not None else False


def _quarantined(report: Any | None) -> bool:
    return bool(getattr(report, "quarantined", False)) if report is not None else False


def _phase(report: Any | None) -> str:
    value = getattr(report, "final_phase", None)
    if value is None:
        return "none"
    return SideEffectPhase(value).value


def make_restart_chaos_cut(
    *,
    keypair: DhtKeypair,
    lane: RestartCutLane,
    profile_id: str,
    service_name: str,
    scope_digest: bytes,
    request_digest: bytes,
    component_report: Any,
    phase: str | SideEffectPhase | None = None,
    sequence: int,
    previous_cut_digest: bytes = ZERO_DIGEST,
    issued_at: int,
    expires_at: int,
    hard_negative_count: int = 0,
    family_id: str,
    path_family: str,
) -> RestartChaosCut:
    phase_value = SideEffectPhase(phase).value if phase in tuple(item.value for item in SideEffectPhase) or isinstance(phase, SideEffectPhase) else (phase or _phase(component_report))
    unsigned = RestartChaosCut(
        lane=lane,
        profile_id=profile_id,
        service_name=service_name,
        scope_digest=scope_digest,
        request_digest=request_digest,
        component_report_digest=_digest(component_report),
        phase=phase_value,
        sequence=sequence,
        previous_cut_digest=previous_cut_digest,
        issued_at=issued_at,
        expires_at=expires_at,
        hard_negative_count=hard_negative_count,
        family_id=family_id,
        path_family=path_family,
        signer_public_key=keypair.public_key_bytes,
    )
    return replace(unsigned, signature=keypair.sign(unsigned.signature_payload()))


def assess_restart_chaos(
    cuts: Iterable[RestartChaosCut],
    *,
    handler_replay_report: Any,
    side_effect_journal_report: Any,
    handler_quench_report: Any,
    fuzz_ledger_report: Any,
    now: int,
    expected_profile_id: str,
    expected_service_name: str,
    expected_scope_digest: bytes,
    expected_request_digest: bytes,
    required_lanes: Iterable[RestartCutLane] = (RestartCutLane.HANDLER_REPLAY, RestartCutLane.SIDE_EFFECT_JOURNAL, RestartCutLane.HANDLER_QUENCH, RestartCutLane.FUZZ_LEDGER),
    previous_seen_cut_digests: Iterable[bytes] = (),
    highest_seen_sequence: int | None = None,
    allow_component_watch: bool = False,
    min_family_count: int = 2,
    min_path_family_count: int = 2,
) -> RestartChaosReport:
    cut_t = tuple(cuts)
    required = tuple(RestartCutLane(item) for item in required_lanes)
    components: dict[RestartCutLane, Any] = {
        RestartCutLane.HANDLER_REPLAY: handler_replay_report,
        RestartCutLane.SIDE_EFFECT_JOURNAL: side_effect_journal_report,
        RestartCutLane.HANDLER_QUENCH: handler_quench_report,
        RestartCutLane.FUZZ_LEDGER: fuzz_ledger_report,
    }
    component_digests = tuple(_digest(components.get(lane)) for lane in required)
    common = dict(profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, required_lanes=required, component_digests=component_digests)
    if not cut_t:
        return _report(RestartChaosDecisionKind.EMPTY_NO_CUTS, False, False, "restart chaos needs cuts", cuts=cut_t, **common)
    for lane in required:
        component = components.get(lane)
        if not _accept(component) or _quarantined(component):
            return _report(RestartChaosDecisionKind.QUARANTINE_COMPONENT_NOT_ACCEPTED, False, False, f"required component {lane.value} did not accept", cuts=cut_t, **common)
    if any(_watch(components.get(lane)) for lane in required) and not allow_component_watch:
        return _report(RestartChaosDecisionKind.HOLD_COMPONENT_WATCH, False, True, "component watch pressure must be carried through restart chaos", cuts=cut_t, **common)

    final_phase = getattr(side_effect_journal_report, "final_phase", None)
    final = SideEffectPhase(final_phase) if final_phase is not None else None
    if final is SideEffectPhase.PREPARE:
        return _report(RestartChaosDecisionKind.HOLD_PREPARE_ONLY, False, True, "prepared side effect needs commit or abort before restart acceptance", cuts=cut_t, **common)

    seen = set(previous_seen_cut_digests)
    by_sequence: dict[int, RestartChaosCut] = {}
    by_lane: dict[RestartCutLane, RestartChaosCut] = {}
    for cut in cut_t:
        if not cut.verifies():
            return _report(RestartChaosDecisionKind.QUARANTINE_BAD_SIGNATURE, False, False, "bad restart cut signature", cuts=cut_t, **common)
        if not cut.live(now):
            return _report(RestartChaosDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, False, False, "expired or future restart cut", cuts=cut_t, **common)
        if cut.cut_digest in seen:
            return _report(RestartChaosDecisionKind.QUARANTINE_REPLAY, False, False, "replayed restart cut", cuts=cut_t, **common)
        if highest_seen_sequence is not None and cut.sequence < highest_seen_sequence:
            return _report(RestartChaosDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, False, "restart cut sequence rollback", cuts=cut_t, **common)
        prior = by_sequence.get(cut.sequence)
        if prior is not None and prior.cut_core_digest != cut.cut_core_digest:
            return _report(RestartChaosDecisionKind.QUARANTINE_SEQUENCE_FORK, False, False, "same-sequence restart cut fork", cuts=cut_t, **common)
        by_sequence[cut.sequence] = cut
        by_lane[cut.lane] = cut
        if cut.profile_id != expected_profile_id:
            return _report(RestartChaosDecisionKind.QUARANTINE_PROFILE_DRIFT, False, False, "profile drift", cuts=cut_t, **common)
        if cut.service_name != expected_service_name:
            return _report(RestartChaosDecisionKind.QUARANTINE_SERVICE_DRIFT, False, False, "service drift", cuts=cut_t, **common)
        if cut.scope_digest != expected_scope_digest:
            return _report(RestartChaosDecisionKind.QUARANTINE_SCOPE_DRIFT, False, False, "scope drift", cuts=cut_t, **common)
        if cut.request_digest != expected_request_digest:
            return _report(RestartChaosDecisionKind.QUARANTINE_REQUEST_DRIFT, False, False, "request drift", cuts=cut_t, **common)
        if cut.component_report_digest != _digest(components.get(cut.lane)):
            return _report(RestartChaosDecisionKind.QUARANTINE_COMPONENT_DIGEST_DRIFT, False, False, "component digest drift", cuts=cut_t, **common)
        if cut.hard_negative_count:
            return _report(RestartChaosDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, "restart cut carries hard negative pressure", cuts=cut_t, **common)
        if cut.lane is RestartCutLane.SIDE_EFFECT_JOURNAL and final is not None and cut.phase != final.value:
            return _report(RestartChaosDecisionKind.QUARANTINE_PHASE_DRIFT, False, False, "side-effect final phase drift", cuts=cut_t, **common)
    missing = tuple(lane for lane in required if lane not in by_lane)
    if missing:
        return _report(RestartChaosDecisionKind.HOLD_MISSING_LANES, False, True, "restart chaos missing required lanes", cuts=cut_t, **common)
    ordered = sorted(by_sequence.values(), key=lambda item: item.sequence)
    for left, right in zip(ordered, ordered[1:]):
        if right.sequence == left.sequence + 1 and right.previous_cut_digest != left.cut_digest:
            return _report(RestartChaosDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, False, "restart cut previous-link mismatch", cuts=cut_t, **common)
    families = {cut.family_id for cut in cut_t}
    paths = {cut.path_family for cut in cut_t}
    if len(families) < min_family_count:
        return _report(RestartChaosDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, "restart chaos needs family diversity", cuts=cut_t, **common)
    if len(paths) < min_path_family_count:
        return _report(RestartChaosDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, "restart chaos needs path diversity", cuts=cut_t, **common)
    accepted = ordered[-1]
    if final is SideEffectPhase.ABORT:
        return _report(RestartChaosDecisionKind.ACCEPT_RESTART_ABORTED, True, False, "restart chaos accepted aborted side effect", cuts=cut_t, accepted=accepted, **common)
    return _report(RestartChaosDecisionKind.ACCEPT_RESTART_COMMITTED, True, False, "restart chaos accepted committed side effect", cuts=cut_t, accepted=accepted, **common)


def _report(kind: RestartChaosDecisionKind, accept: bool, watch: bool, reason: str, *, profile_id: str, service_name: str, scope_digest: bytes, request_digest: bytes, required_lanes: tuple[RestartCutLane, ...], component_digests: tuple[bytes, ...], cuts: Iterable[RestartChaosCut], accepted: RestartChaosCut | None = None) -> RestartChaosReport:
    cut_t = tuple(cuts)
    digests = tuple(cut.cut_digest for cut in cut_t)
    observed = tuple(sorted({cut.lane for cut in cut_t}, key=lambda item: item.value))
    highest = max((cut.sequence for cut in cut_t), default=-1)
    families = {cut.family_id for cut in cut_t}
    paths = {cut.path_family for cut in cut_t}
    hard = sum(cut.hard_negative_count for cut in cut_t)
    accepted_digest = accepted.cut_digest if accepted else ZERO_DIGEST
    final_phase = None
    for cut in cut_t:
        if cut.lane is RestartCutLane.SIDE_EFFECT_JOURNAL and cut.phase in tuple(item.value for item in SideEffectPhase):
            final_phase = SideEffectPhase(cut.phase)
    digest = sha256(RESTART_CHAOS_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"reason": reason,
        b"profile": profile_id,
        b"service": service_name,
        b"scope": scope_digest,
        b"request": request_digest,
        b"required": [lane.value for lane in required_lanes],
        b"observed": [lane.value for lane in observed],
        b"accepted": accepted_digest,
        b"cuts": list(digests),
        b"components": list(component_digests),
        b"highest": highest,
        b"phase": final_phase.value if final_phase else "none",
        b"families": len(families),
        b"paths": len(paths),
        b"hard": hard,
    }))
    return RestartChaosReport(kind, accept, watch, reason, profile_id, service_name, scope_digest, request_digest, required_lanes, observed, accepted_digest, digests, component_digests, highest, final_phase, len(families), len(paths), hard, digest)
