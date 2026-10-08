"""Witness appeal lane for watch-required public bridge decisions.

Subjective policy may require watch instead of deny/allow.  rev0046 models the
next local question: what evidence is enough to spend outbound bridge egress
while preserving proof debt?  Appeals are signed observations.  They are not a
quorum, not global reputation, and not a way to override hard negatives.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .shadowfire import ShadowFireAction, ShadowFireReport

WITNESS_APPEAL_DOMAIN = DOMAIN + b":witness-appeal-v1:"
ZERO_DIGEST = b"\x00" * 32


class AppealObservationKind(str, Enum):
    POLICY_WATCH = "policy_watch"
    INDEPENDENT_WITNESS = "independent_witness"
    NO_STALE_PUBLIC = "no_stale_public"
    HARD_NEGATIVE_SCAN = "hard_negative_scan"
    EGRESS_BUDGET_SCAN = "egress_budget_scan"
    OPERATOR_CONTEXT = "operator_context"


class WitnessAppealDecisionKind(str, Enum):
    ACCEPT_WITNESS_APPEAL = "accept_witness_appeal"
    ACCEPT_WITH_WATCH = "accept_with_watch"
    HOLD_NOT_NEEDED = "hold_not_needed"
    HOLD_MISSING_OBSERVATION = "hold_missing_observation"
    HOLD_OBSERVATION_NOT_ACCEPTED = "hold_observation_not_accepted"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_EXPIRED_OR_FUTURE = "quarantine_expired_or_future"
    QUARANTINE_PROFILE_DRIFT = "quarantine_profile_drift"
    QUARANTINE_ACTION_DRIFT = "quarantine_action_drift"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_REQUEST_DRIFT = "quarantine_request_drift"
    QUARANTINE_SHADOW_DRIFT = "quarantine_shadow_drift"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_HARD_NEGATIVE = "quarantine_hard_negative"


@dataclass(frozen=True)
class AppealObservation:
    kind: AppealObservationKind
    profile_id: str
    service_name: str
    action: ShadowFireAction
    scope_digest: bytes
    request_digest: bytes
    shadow_fire_digest: bytes
    evidence_digest: bytes
    sequence: int
    accepted: bool
    watch: bool
    issued_at: int
    expires_at: int
    signer_public_key: bytes
    family_id: str
    path_family: str
    signature: bytes = b""

    def __post_init__(self) -> None:
        object.__setattr__(self, "kind", AppealObservationKind(self.kind))
        object.__setattr__(self, "action", ShadowFireAction(self.action))
        for name, value in (
            ("scope_digest", self.scope_digest),
            ("request_digest", self.request_digest),
            ("shadow_fire_digest", self.shadow_fire_digest),
            ("evidence_digest", self.evidence_digest),
        ):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if len(self.signer_public_key) != 32:
            raise ValueError("signer public key must be 32 bytes")
        if self.sequence < 0:
            raise ValueError("sequence must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("expires_at must be greater than issued_at")
        if not self.profile_id or not self.service_name or not self.family_id or not self.path_family:
            raise ValueError("appeal observation needs profile/service/family hints")

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"kind": self.kind.value,
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"action": self.action.value,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"shadow": self.shadow_fire_digest,
            b"evidence": self.evidence_digest,
            b"seq": self.sequence,
            b"accepted": 1 if self.accepted else 0,
            b"watch": 1 if self.watch else 0,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"signer": self.signer_public_key,
            b"family": self.family_id,
            b"path_family": self.path_family,
        }

    def payload(self) -> bytes:
        return WITNESS_APPEAL_DOMAIN + b":observation:" + bencode(self.unsigned_bvalue())

    @property
    def observation_digest(self) -> bytes:
        return sha256(WITNESS_APPEAL_DOMAIN + b":observation-digest:" + self.payload() + self.signature)

    def verify(self) -> bool:
        return verify_signature(self.signer_public_key, self.payload(), self.signature)

    def with_signature(self, signature: bytes) -> "AppealObservation":
        return replace(self, signature=signature)


@dataclass(frozen=True)
class WitnessAppealReport:
    decision_kind: WitnessAppealDecisionKind
    accepted: bool
    watch: bool
    reason: str
    profile_id: str
    service_name: str
    action: ShadowFireAction
    scope_digest: bytes
    request_digest: bytes
    shadow_fire_digest: bytes
    accepted_observation_digests: tuple[bytes, ...]
    family_count: int
    path_family_count: int
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def make_appeal_observation(
    *,
    keypair: DhtKeypair,
    kind: AppealObservationKind,
    profile_id: str,
    service_name: str,
    action: ShadowFireAction,
    scope_digest: bytes,
    request_digest: bytes,
    shadow_fire_digest: bytes,
    evidence_digest: bytes,
    sequence: int,
    accepted: bool,
    issued_at: int,
    expires_at: int,
    family_id: str,
    path_family: str,
    watch: bool = False,
) -> AppealObservation:
    observation = AppealObservation(
        kind=kind,
        profile_id=profile_id,
        service_name=service_name,
        action=action,
        scope_digest=scope_digest,
        request_digest=request_digest,
        shadow_fire_digest=shadow_fire_digest,
        evidence_digest=evidence_digest,
        sequence=sequence,
        accepted=accepted,
        watch=watch,
        issued_at=issued_at,
        expires_at=expires_at,
        signer_public_key=keypair.public_key_bytes,
        family_id=family_id,
        path_family=path_family,
    )
    return observation.with_signature(keypair.sign(observation.payload()))


def _report(
    kind: WitnessAppealDecisionKind,
    *,
    accepted: bool,
    watch: bool,
    reason: str,
    profile_id: str,
    service_name: str,
    action: ShadowFireAction,
    scope_digest: bytes,
    request_digest: bytes,
    shadow_fire_digest: bytes,
    observations: Iterable[AppealObservation] = (),
) -> WitnessAppealReport:
    obs_tuple = tuple(observations)
    digests = tuple(obs.observation_digest for obs in obs_tuple)
    families = tuple(sorted({obs.family_id for obs in obs_tuple}))
    paths = tuple(sorted({obs.path_family for obs in obs_tuple}))
    digest = sha256(WITNESS_APPEAL_DOMAIN + b":report:" + bencode({
        b"decision": kind.value,
        b"accepted": 1 if accepted else 0,
        b"watch": 1 if watch else 0,
        b"reason": reason,
        b"profile": profile_id,
        b"service": service_name,
        b"action": action.value,
        b"scope": scope_digest,
        b"request": request_digest,
        b"shadow": shadow_fire_digest,
        b"observations": list(digests),
        b"families": list(families),
        b"paths": list(paths),
    }))
    return WitnessAppealReport(kind, accepted, watch, reason, profile_id, service_name, action, scope_digest, request_digest, shadow_fire_digest, digests, len(families), len(paths), digest)


def assess_witness_appeal(
    observations: Iterable[AppealObservation],
    *,
    shadow_fire: ShadowFireReport,
    now: int,
    expected_profile_id: str,
    expected_service_name: str,
    expected_action: ShadowFireAction,
    expected_scope_digest: bytes,
    expected_request_digest: bytes,
    required_kinds: Iterable[AppealObservationKind] = (
        AppealObservationKind.POLICY_WATCH,
        AppealObservationKind.INDEPENDENT_WITNESS,
        AppealObservationKind.NO_STALE_PUBLIC,
        AppealObservationKind.HARD_NEGATIVE_SCAN,
        AppealObservationKind.EGRESS_BUDGET_SCAN,
    ),
    min_family_diversity: int = 3,
    min_path_diversity: int = 2,
    allow_watch: bool = False,
    previously_seen_observation_digests: Iterable[bytes] = (),
) -> WitnessAppealReport:
    expected_action = ShadowFireAction(expected_action)
    required = frozenset(AppealObservationKind(kind) for kind in required_kinds)
    obs_tuple = tuple(observations)
    if not shadow_fire.watch:
        return _report(WitnessAppealDecisionKind.HOLD_NOT_NEEDED, False, False, "shadow-fire did not require watch appeal", profile_id=expected_profile_id, service_name=expected_service_name, action=expected_action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, shadow_fire_digest=shadow_fire.report_digest, observations=obs_tuple)
    seen = set(previously_seen_observation_digests)
    valid: list[AppealObservation] = []
    by_kind_seq: dict[tuple[AppealObservationKind, int], bytes] = {}
    for obs in obs_tuple:
        if not obs.verify():
            return _report(WitnessAppealDecisionKind.QUARANTINE_BAD_SIGNATURE, accepted=False, watch=False, reason="bad observation signature", profile_id=expected_profile_id, service_name=expected_service_name, action=expected_action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, shadow_fire_digest=shadow_fire.report_digest, observations=(obs,))
        if obs.observation_digest in seen:
            return _report(WitnessAppealDecisionKind.QUARANTINE_REPLAY, accepted=False, watch=False, reason="appeal observation replay", profile_id=expected_profile_id, service_name=expected_service_name, action=expected_action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, shadow_fire_digest=shadow_fire.report_digest, observations=(obs,))
        if not (obs.issued_at <= now < obs.expires_at):
            return _report(WitnessAppealDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, accepted=False, watch=False, reason="appeal observation expired or future", profile_id=expected_profile_id, service_name=expected_service_name, action=expected_action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, shadow_fire_digest=shadow_fire.report_digest, observations=(obs,))
        if obs.profile_id != expected_profile_id or obs.service_name != expected_service_name:
            return _report(WitnessAppealDecisionKind.QUARANTINE_PROFILE_DRIFT, accepted=False, watch=False, reason="appeal profile/service drift", profile_id=expected_profile_id, service_name=expected_service_name, action=expected_action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, shadow_fire_digest=shadow_fire.report_digest, observations=(obs,))
        if obs.action is not expected_action:
            return _report(WitnessAppealDecisionKind.QUARANTINE_ACTION_DRIFT, accepted=False, watch=False, reason="appeal action drift", profile_id=expected_profile_id, service_name=expected_service_name, action=expected_action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, shadow_fire_digest=shadow_fire.report_digest, observations=(obs,))
        if obs.scope_digest != expected_scope_digest:
            return _report(WitnessAppealDecisionKind.QUARANTINE_SCOPE_DRIFT, accepted=False, watch=False, reason="appeal scope drift", profile_id=expected_profile_id, service_name=expected_service_name, action=expected_action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, shadow_fire_digest=shadow_fire.report_digest, observations=(obs,))
        if obs.request_digest != expected_request_digest:
            return _report(WitnessAppealDecisionKind.QUARANTINE_REQUEST_DRIFT, accepted=False, watch=False, reason="appeal request drift", profile_id=expected_profile_id, service_name=expected_service_name, action=expected_action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, shadow_fire_digest=shadow_fire.report_digest, observations=(obs,))
        if obs.shadow_fire_digest != shadow_fire.report_digest:
            return _report(WitnessAppealDecisionKind.QUARANTINE_SHADOW_DRIFT, accepted=False, watch=False, reason="appeal shadow-fire digest drift", profile_id=expected_profile_id, service_name=expected_service_name, action=expected_action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, shadow_fire_digest=shadow_fire.report_digest, observations=(obs,))
        prev = by_kind_seq.get((obs.kind, obs.sequence))
        if prev is not None and prev != obs.evidence_digest:
            return _report(WitnessAppealDecisionKind.QUARANTINE_SEQUENCE_FORK, accepted=False, watch=False, reason="appeal same-kind sequence fork", profile_id=expected_profile_id, service_name=expected_service_name, action=expected_action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, shadow_fire_digest=shadow_fire.report_digest, observations=obs_tuple)
        by_kind_seq[(obs.kind, obs.sequence)] = obs.evidence_digest
        valid.append(obs)
    if any(obs.kind is AppealObservationKind.HARD_NEGATIVE_SCAN and not obs.accepted for obs in valid):
        return _report(WitnessAppealDecisionKind.QUARANTINE_HARD_NEGATIVE, accepted=False, watch=False, reason="hard-negative scan refused appeal", profile_id=expected_profile_id, service_name=expected_service_name, action=expected_action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, shadow_fire_digest=shadow_fire.report_digest, observations=valid)
    if any(not obs.accepted for obs in valid):
        return _report(WitnessAppealDecisionKind.HOLD_OBSERVATION_NOT_ACCEPTED, accepted=False, watch=False, reason="appeal contains non-accepted observation", profile_id=expected_profile_id, service_name=expected_service_name, action=expected_action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, shadow_fire_digest=shadow_fire.report_digest, observations=valid)
    kinds = {obs.kind for obs in valid if obs.accepted}
    missing = required - kinds
    if missing:
        return _report(WitnessAppealDecisionKind.HOLD_MISSING_OBSERVATION, accepted=False, watch=False, reason="missing appeal observation kinds: " + ",".join(sorted(kind.value for kind in missing)), profile_id=expected_profile_id, service_name=expected_service_name, action=expected_action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, shadow_fire_digest=shadow_fire.report_digest, observations=valid)
    family_count = len({obs.family_id for obs in valid})
    path_count = len({obs.path_family for obs in valid})
    if family_count < min_family_diversity:
        return _report(WitnessAppealDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, accepted=False, watch=False, reason="appeal lacks witness family diversity", profile_id=expected_profile_id, service_name=expected_service_name, action=expected_action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, shadow_fire_digest=shadow_fire.report_digest, observations=valid)
    if path_count < min_path_diversity:
        return _report(WitnessAppealDecisionKind.HOLD_LOW_PATH_DIVERSITY, accepted=False, watch=False, reason="appeal lacks witness path diversity", profile_id=expected_profile_id, service_name=expected_service_name, action=expected_action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, shadow_fire_digest=shadow_fire.report_digest, observations=valid)
    watch = any(obs.watch for obs in valid)
    if watch and not allow_watch:
        return _report(WitnessAppealDecisionKind.ACCEPT_WITH_WATCH, accepted=True, watch=True, reason="appeal accepted but carries watch debt", profile_id=expected_profile_id, service_name=expected_service_name, action=expected_action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, shadow_fire_digest=shadow_fire.report_digest, observations=valid)
    return _report(WitnessAppealDecisionKind.ACCEPT_WITNESS_APPEAL, accepted=True, watch=watch, reason="watch-required shadow fire has diverse appeal evidence", profile_id=expected_profile_id, service_name=expected_service_name, action=expected_action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, shadow_fire_digest=shadow_fire.report_digest, observations=valid)
