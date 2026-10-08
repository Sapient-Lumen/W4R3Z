"""Effect-seal replay across restart generations.

rev0056 treats an accepted effect seal as sticky local state that must survive
multiple restart generations without being reinterpreted.  A committed effect
cannot quietly come back as aborted, an aborted effect cannot quietly become a
commit, and a later generation cannot replay an old seal observation as fresh
truth.  This remains a no-network toy lane: it signs compact observations and
checks local monotonic memory before a recovery mesh may advance.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Any, Iterable

from .bencode import BValue, bencode
from .effectseal import EffectSealDecisionKind
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectAction, SideEffectPhase

SEAL_REPLAY_DOMAIN = DOMAIN + b":seal-replay-v1:"


class SealReplayDecisionKind(str, Enum):
    ACCEPT_REPLAY_COMMITTED = "accept_replay_committed"
    ACCEPT_REPLAY_ABORTED = "accept_replay_aborted"
    ACCEPT_WITH_WATCH = "accept_with_watch"
    HOLD_COMPONENT_WATCH = "hold_component_watch"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    EMPTY_NO_OBSERVATIONS = "empty_no_observations"
    QUARANTINE_COMPONENT_NOT_ACCEPTED = "quarantine_component_not_accepted"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_EXPIRED_OR_FUTURE = "quarantine_expired_or_future"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_GENERATION_ROLLBACK = "quarantine_generation_rollback"
    QUARANTINE_GENERATION_FORK = "quarantine_generation_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_PROFILE_DRIFT = "quarantine_profile_drift"
    QUARANTINE_SERVICE_DRIFT = "quarantine_service_drift"
    QUARANTINE_ACTION_DRIFT = "quarantine_action_drift"
    QUARANTINE_PHASE_DRIFT = "quarantine_phase_drift"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_REQUEST_DRIFT = "quarantine_request_drift"
    QUARANTINE_PAYLOAD_DRIFT = "quarantine_payload_drift"
    QUARANTINE_IDEMPOTENCY_DRIFT = "quarantine_idempotency_drift"
    QUARANTINE_COMPONENT_DIGEST_DRIFT = "quarantine_component_digest_drift"
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"


@dataclass(frozen=True)
class SealReplayObservation:
    generation: int
    action: SideEffectAction
    final_phase: SideEffectPhase
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    effect_seal_digest: bytes
    restart_chaos_digest: bytes
    side_effect_journal_digest: bytes
    previous_observation_digest: bytes
    hard_negative_count: int
    issued_at: int
    expires_at: int
    family_id: str
    path_family: str
    signer_public_key: bytes
    signature: bytes = b""

    def __post_init__(self) -> None:
        object.__setattr__(self, "action", SideEffectAction(self.action))
        object.__setattr__(self, "final_phase", SideEffectPhase(self.final_phase))
        if self.generation < 0 or self.hard_negative_count < 0:
            raise ValueError("generation and hard_negative_count must be non-negative")
        if not self.profile_id or not self.service_name or not self.family_id or not self.path_family:
            raise ValueError("seal replay observation needs profile/service/family/path")
        if self.expires_at <= self.issued_at:
            raise ValueError("expires_at must follow issued_at")
        for name, value in (
            ("scope_digest", self.scope_digest),
            ("request_digest", self.request_digest),
            ("payload_digest", self.payload_digest),
            ("idempotency_key", self.idempotency_key),
            ("effect_seal_digest", self.effect_seal_digest),
            ("restart_chaos_digest", self.restart_chaos_digest),
            ("side_effect_journal_digest", self.side_effect_journal_digest),
            ("previous_observation_digest", self.previous_observation_digest),
            ("signer_public_key", self.signer_public_key),
        ):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if self.signature and len(self.signature) != 64:
            raise ValueError("signature must be empty or Ed25519-sized")

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"generation": self.generation,
            b"action": self.action.value,
            b"phase": self.final_phase.value,
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"payload": self.payload_digest,
            b"idem": self.idempotency_key,
            b"effect_seal": self.effect_seal_digest,
            b"restart": self.restart_chaos_digest,
            b"journal": self.side_effect_journal_digest,
            b"prev": self.previous_observation_digest,
            b"hard": self.hard_negative_count,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"family": self.family_id,
            b"path_family": self.path_family,
            b"signer": self.signer_public_key,
        }

    def signature_payload(self) -> bytes:
        return SEAL_REPLAY_DOMAIN + b":observation-sig:" + bencode(self.unsigned_bvalue())

    @property
    def observation_core_digest(self) -> bytes:
        return sha256(SEAL_REPLAY_DOMAIN + b":observation-core:" + bencode(self.unsigned_bvalue()))

    @property
    def observation_digest(self) -> bytes:
        return sha256(SEAL_REPLAY_DOMAIN + b":observation-digest:" + self.signature_payload() + self.signature)

    def verifies(self) -> bool:
        return verify_signature(self.signer_public_key, self.signature_payload(), self.signature)

    def live(self, now: int) -> bool:
        return self.issued_at <= now < self.expires_at


@dataclass(frozen=True)
class SealReplayReport:
    decision_kind: SealReplayDecisionKind
    accept: bool
    watch: bool
    reason: str
    action: SideEffectAction
    final_phase: SideEffectPhase | None
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    accepted_observation_digest: bytes
    observation_digests: tuple[bytes, ...]
    component_digests: tuple[bytes, ...]
    highest_generation: int
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


def make_seal_replay_observation(
    *,
    keypair: DhtKeypair,
    effect_seal_report: Any,
    restart_chaos_report: Any,
    side_effect_journal_report: Any,
    generation: int,
    previous_observation_digest: bytes = ZERO_DIGEST,
    issued_at: int,
    expires_at: int,
    hard_negative_count: int = 0,
    family_id: str,
    path_family: str,
) -> SealReplayObservation:
    unsigned = SealReplayObservation(
        generation=generation,
        action=getattr(effect_seal_report, "action"),
        final_phase=getattr(effect_seal_report, "final_phase"),
        profile_id=getattr(effect_seal_report, "profile_id"),
        service_name=getattr(effect_seal_report, "service_name"),
        scope_digest=getattr(effect_seal_report, "scope_digest"),
        request_digest=getattr(effect_seal_report, "request_digest"),
        payload_digest=getattr(effect_seal_report, "payload_digest"),
        idempotency_key=getattr(effect_seal_report, "idempotency_key"),
        effect_seal_digest=_digest(effect_seal_report),
        restart_chaos_digest=_digest(restart_chaos_report),
        side_effect_journal_digest=_digest(side_effect_journal_report),
        previous_observation_digest=previous_observation_digest,
        hard_negative_count=hard_negative_count,
        issued_at=issued_at,
        expires_at=expires_at,
        family_id=family_id,
        path_family=path_family,
        signer_public_key=keypair.public_key_bytes,
    )
    return replace(unsigned, signature=keypair.sign(unsigned.signature_payload()))


def assess_seal_replay(
    observations: Iterable[SealReplayObservation],
    *,
    effect_seal_report: Any,
    restart_chaos_report: Any,
    side_effect_journal_report: Any,
    now: int,
    previous_seen_observation_digests: Iterable[bytes] = (),
    highest_seen_generation: int | None = None,
    allow_component_watch: bool = False,
    min_family_count: int = 2,
    min_path_family_count: int = 2,
) -> SealReplayReport:
    obs_t = tuple(observations)
    action = SideEffectAction(getattr(effect_seal_report, "action"))
    final_phase = getattr(effect_seal_report, "final_phase", None)
    final_phase = SideEffectPhase(final_phase) if final_phase is not None else None
    profile_id = getattr(effect_seal_report, "profile_id")
    service_name = getattr(effect_seal_report, "service_name")
    scope_digest = getattr(effect_seal_report, "scope_digest")
    request_digest = getattr(effect_seal_report, "request_digest")
    payload_digest = getattr(effect_seal_report, "payload_digest")
    idempotency_key = getattr(effect_seal_report, "idempotency_key")
    component_digests = (_digest(effect_seal_report), _digest(restart_chaos_report), _digest(side_effect_journal_report))
    common = dict(action=action, final_phase=final_phase, profile_id=profile_id, service_name=service_name, scope_digest=scope_digest, request_digest=request_digest, payload_digest=payload_digest, idempotency_key=idempotency_key, component_digests=component_digests)
    if not obs_t:
        return _report(SealReplayDecisionKind.EMPTY_NO_OBSERVATIONS, False, False, "seal replay needs observations", observations=obs_t, **common)
    for component in (effect_seal_report, restart_chaos_report, side_effect_journal_report):
        if not _accept(component) or _quarantined(component):
            return _report(SealReplayDecisionKind.QUARANTINE_COMPONENT_NOT_ACCEPTED, False, False, "component did not accept", observations=obs_t, **common)
    if any(_watch(component) for component in (effect_seal_report, restart_chaos_report, side_effect_journal_report)) and not allow_component_watch:
        return _report(SealReplayDecisionKind.HOLD_COMPONENT_WATCH, False, True, "component watch pressure must be carried", observations=obs_t, **common)
    restart_phase = getattr(restart_chaos_report, "final_phase", None)
    journal_phase = getattr(side_effect_journal_report, "final_phase", None)
    if final_phase is not None:
        for observed_phase in (restart_phase, journal_phase):
            if observed_phase is not None and SideEffectPhase(observed_phase) is not final_phase:
                return _report(SealReplayDecisionKind.QUARANTINE_PHASE_DRIFT, False, False, "component phase drift", observations=obs_t, **common)

    seen = set(previous_seen_observation_digests)
    by_generation: dict[int, SealReplayObservation] = {}
    for obs in obs_t:
        if not obs.verifies():
            return _report(SealReplayDecisionKind.QUARANTINE_BAD_SIGNATURE, False, False, "bad seal replay signature", observations=obs_t, **common)
        if not obs.live(now):
            return _report(SealReplayDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, False, False, "expired or future seal replay observation", observations=obs_t, **common)
        if obs.observation_digest in seen:
            return _report(SealReplayDecisionKind.QUARANTINE_REPLAY, False, False, "replayed seal replay observation", observations=obs_t, **common)
        if highest_seen_generation is not None and obs.generation < highest_seen_generation:
            return _report(SealReplayDecisionKind.QUARANTINE_GENERATION_ROLLBACK, False, False, "generation rollback", observations=obs_t, **common)
        prior = by_generation.get(obs.generation)
        if prior is not None and prior.observation_core_digest != obs.observation_core_digest:
            return _report(SealReplayDecisionKind.QUARANTINE_GENERATION_FORK, False, False, "same-generation seal replay fork", observations=obs_t, **common)
        by_generation[obs.generation] = obs
        if obs.profile_id != profile_id:
            return _report(SealReplayDecisionKind.QUARANTINE_PROFILE_DRIFT, False, False, "profile drift", observations=obs_t, **common)
        if obs.service_name != service_name:
            return _report(SealReplayDecisionKind.QUARANTINE_SERVICE_DRIFT, False, False, "service drift", observations=obs_t, **common)
        if obs.action is not action:
            return _report(SealReplayDecisionKind.QUARANTINE_ACTION_DRIFT, False, False, "action drift", observations=obs_t, **common)
        if final_phase is not None and obs.final_phase is not final_phase:
            return _report(SealReplayDecisionKind.QUARANTINE_PHASE_DRIFT, False, False, "phase drift", observations=obs_t, **common)
        if obs.scope_digest != scope_digest:
            return _report(SealReplayDecisionKind.QUARANTINE_SCOPE_DRIFT, False, False, "scope drift", observations=obs_t, **common)
        if obs.request_digest != request_digest:
            return _report(SealReplayDecisionKind.QUARANTINE_REQUEST_DRIFT, False, False, "request drift", observations=obs_t, **common)
        if obs.payload_digest != payload_digest:
            return _report(SealReplayDecisionKind.QUARANTINE_PAYLOAD_DRIFT, False, False, "payload drift", observations=obs_t, **common)
        if obs.idempotency_key != idempotency_key:
            return _report(SealReplayDecisionKind.QUARANTINE_IDEMPOTENCY_DRIFT, False, False, "idempotency drift", observations=obs_t, **common)
        if (obs.effect_seal_digest, obs.restart_chaos_digest, obs.side_effect_journal_digest) != component_digests:
            return _report(SealReplayDecisionKind.QUARANTINE_COMPONENT_DIGEST_DRIFT, False, False, "component digest drift", observations=obs_t, **common)
        if obs.hard_negative_count:
            return _report(SealReplayDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, "hard negatives block seal replay", observations=obs_t, **common)
    ordered = sorted(by_generation.values(), key=lambda item: item.generation)
    for left, right in zip(ordered, ordered[1:]):
        if right.generation == left.generation + 1 and right.previous_observation_digest != left.observation_digest:
            return _report(SealReplayDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, False, "seal replay previous-link mismatch", observations=obs_t, **common)
    if len({obs.family_id for obs in obs_t}) < min_family_count:
        return _report(SealReplayDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, "seal replay needs family diversity", observations=obs_t, **common)
    if len({obs.path_family for obs in obs_t}) < min_path_family_count:
        return _report(SealReplayDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, "seal replay needs path diversity", observations=obs_t, **common)
    accepted = ordered[-1]
    if any(_watch(component) for component in (effect_seal_report, restart_chaos_report, side_effect_journal_report)):
        return _report(SealReplayDecisionKind.ACCEPT_WITH_WATCH, True, True, "seal replay accepted with watch", observations=obs_t, accepted=accepted, **common)
    if final_phase is SideEffectPhase.ABORT:
        return _report(SealReplayDecisionKind.ACCEPT_REPLAY_ABORTED, True, False, "seal replay accepted aborted effect", observations=obs_t, accepted=accepted, **common)
    return _report(SealReplayDecisionKind.ACCEPT_REPLAY_COMMITTED, True, False, "seal replay accepted committed effect", observations=obs_t, accepted=accepted, **common)


def _report(kind: SealReplayDecisionKind, accept: bool, watch: bool, reason: str, *, action: SideEffectAction, final_phase: SideEffectPhase | None, profile_id: str, service_name: str, scope_digest: bytes, request_digest: bytes, payload_digest: bytes, idempotency_key: bytes, component_digests: tuple[bytes, ...], observations: Iterable[SealReplayObservation], accepted: SealReplayObservation | None = None) -> SealReplayReport:
    obs_t = tuple(observations)
    digests = tuple(obs.observation_digest for obs in obs_t)
    families = {obs.family_id for obs in obs_t}
    paths = {obs.path_family for obs in obs_t}
    highest = max((obs.generation for obs in obs_t), default=-1)
    hard = sum(obs.hard_negative_count for obs in obs_t)
    accepted_digest = accepted.observation_digest if accepted else ZERO_DIGEST
    digest = sha256(SEAL_REPLAY_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"reason": reason,
        b"action": action.value,
        b"phase": final_phase.value if final_phase else b"none",
        b"profile": profile_id,
        b"service": service_name,
        b"scope": scope_digest,
        b"request": request_digest,
        b"payload": payload_digest,
        b"idem": idempotency_key,
        b"accepted": accepted_digest,
        b"observations": list(digests),
        b"components": list(component_digests),
        b"highest": highest,
        b"families": len(families),
        b"paths": len(paths),
        b"hard": hard,
    }))
    return SealReplayReport(kind, accept, watch, reason, action, final_phase, profile_id, service_name, scope_digest, request_digest, payload_digest, idempotency_key, accepted_digest, digests, component_digests, highest, len(families), len(paths), hard, digest)
