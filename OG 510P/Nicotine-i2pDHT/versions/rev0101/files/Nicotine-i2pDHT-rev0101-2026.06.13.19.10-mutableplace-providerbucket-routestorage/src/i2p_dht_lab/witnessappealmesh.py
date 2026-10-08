"""Witness-appeal mesh for watched public-bridge decisions.

rev0047 folds the useful branchlet idea that *watch* is a real protocol state,
not a soft comment.  A public bridge ledger can be locally accepted while still
carrying watch pressure from subjective policy, moderation, redress, egress, or
shadow-fire.  This module models the next local question: what typed evidence is
enough to proceed with that proof debt visible?

The answer is deliberately modest.  Appeal observations are signed local facts,
not global reputation and not DHT truth.  They can support a watched local
publication boundary only when they bind to the exact bridge-ledger, moderation,
redress, scope, request, and path/family surface.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .bridgeledger import BridgeLedgerAction, BridgeLedgerReport
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .moderationquarantine import ModerationQuarantineReport, ZERO_DIGEST
from .redresslane import RedressReport

WITNESS_APPEAL_MESH_DOMAIN = DOMAIN + b":witness-appeal-mesh-v1:"


class AppealMeshObservationKind(str, Enum):
    POLICY_WATCH = "policy_watch"
    BRIDGE_LEDGER_WATCH = "bridge_ledger_watch"
    REDRESS_PRIVACY_SCAN = "redress_privacy_scan"
    HARD_NEGATIVE_SCAN = "hard_negative_scan"
    STALE_PUBLIC_SCAN = "stale_public_scan"
    OPERATOR_CONTEXT = "operator_context"


class WitnessAppealMeshDecisionKind(str, Enum):
    ACCEPT_NOT_NEEDED = "accept_not_needed"
    ACCEPT_APPEAL_MESH = "accept_appeal_mesh"
    ACCEPT_WITH_WATCH = "accept_with_watch"
    HOLD_BRIDGE_LEDGER_NOT_ACCEPTED = "hold_bridge_ledger_not_accepted"
    HOLD_MISSING_OBSERVATION = "hold_missing_observation"
    HOLD_OBSERVATION_NOT_ACCEPTED = "hold_observation_not_accepted"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    QUARANTINE_BRIDGE_LEDGER = "quarantine_bridge_ledger"
    QUARANTINE_MODERATION = "quarantine_moderation"
    QUARANTINE_REDRESS = "quarantine_redress"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_EXPIRED_OR_FUTURE = "quarantine_expired_or_future"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_PROFILE_DRIFT = "quarantine_profile_drift"
    QUARANTINE_SERVICE_DRIFT = "quarantine_service_drift"
    QUARANTINE_ACTION_DRIFT = "quarantine_action_drift"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_REQUEST_DRIFT = "quarantine_request_drift"
    QUARANTINE_COMPONENT_DIGEST_DRIFT = "quarantine_component_digest_drift"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"


@dataclass(frozen=True)
class AppealMeshObservation:
    kind: AppealMeshObservationKind
    action: BridgeLedgerAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    bridge_ledger_digest: bytes
    moderation_digest: bytes
    redress_digest: bytes
    evidence_digest: bytes
    sequence: int
    previous_observation_digest: bytes
    accepted: bool
    watch: bool
    issued_at: int
    expires_at: int
    family_id: str
    path_family: str
    signer_public_key: bytes
    signature: bytes = b""

    def __post_init__(self) -> None:
        object.__setattr__(self, "kind", AppealMeshObservationKind(self.kind))
        object.__setattr__(self, "action", BridgeLedgerAction(self.action))
        if not self.profile_id or not self.service_name or not self.family_id or not self.path_family:
            raise ValueError("appeal observation needs profile/service/family/path")
        if self.sequence < 0:
            raise ValueError("sequence must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("expires_at must be greater than issued_at")
        for name, value in (
            ("scope_digest", self.scope_digest),
            ("request_digest", self.request_digest),
            ("bridge_ledger_digest", self.bridge_ledger_digest),
            ("moderation_digest", self.moderation_digest),
            ("redress_digest", self.redress_digest),
            ("evidence_digest", self.evidence_digest),
            ("previous_observation_digest", self.previous_observation_digest),
            ("signer_public_key", self.signer_public_key),
        ):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if self.signature and len(self.signature) != 64:
            raise ValueError("signature must be Ed25519-sized")

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"kind": self.kind.value,
            b"action": self.action.value,
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"bridge": self.bridge_ledger_digest,
            b"moderation": self.moderation_digest,
            b"redress": self.redress_digest,
            b"evidence": self.evidence_digest,
            b"seq": self.sequence,
            b"prev": self.previous_observation_digest,
            b"accepted": 1 if self.accepted else 0,
            b"watch": 1 if self.watch else 0,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"family": self.family_id,
            b"path_family": self.path_family,
            b"signer": self.signer_public_key,
        }

    def signature_payload(self) -> bytes:
        return WITNESS_APPEAL_MESH_DOMAIN + b":observation-sig:" + bencode(self.unsigned_bvalue())

    @property
    def observation_core_digest(self) -> bytes:
        return sha256(WITNESS_APPEAL_MESH_DOMAIN + b":observation-core:" + bencode(self.unsigned_bvalue()))

    @property
    def observation_digest(self) -> bytes:
        return sha256(WITNESS_APPEAL_MESH_DOMAIN + b":observation-digest:" + self.signature_payload() + self.signature)

    def verifies(self) -> bool:
        return verify_signature(self.signer_public_key, self.signature_payload(), self.signature)


@dataclass(frozen=True)
class WitnessAppealMeshReport:
    decision_kind: WitnessAppealMeshDecisionKind
    accept: bool
    watch: bool
    reason: str
    profile_id: str
    service_name: str
    action: BridgeLedgerAction
    scope_digest: bytes
    request_digest: bytes
    bridge_ledger_digest: bytes
    moderation_digest: bytes
    redress_digest: bytes
    accepted_observation_digests: tuple[bytes, ...]
    family_count: int
    path_family_count: int
    highest_sequence: int
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def make_appeal_mesh_observation(
    *,
    keypair: DhtKeypair,
    kind: AppealMeshObservationKind,
    action: BridgeLedgerAction,
    profile_id: str,
    service_name: str,
    scope_digest: bytes,
    request_digest: bytes,
    bridge_ledger_digest: bytes,
    moderation_digest: bytes,
    redress_digest: bytes = ZERO_DIGEST,
    evidence_digest: bytes,
    sequence: int,
    previous_observation_digest: bytes = ZERO_DIGEST,
    accepted: bool = True,
    watch: bool = False,
    issued_at: int,
    expires_at: int,
    family_id: str,
    path_family: str,
) -> AppealMeshObservation:
    observation = AppealMeshObservation(kind, action, profile_id, service_name, scope_digest, request_digest, bridge_ledger_digest, moderation_digest, redress_digest, evidence_digest, sequence, previous_observation_digest, accepted, watch, issued_at, expires_at, family_id, path_family, keypair.public_key_bytes)
    return replace(observation, signature=keypair.sign(observation.signature_payload()))


def _report(
    kind: WitnessAppealMeshDecisionKind,
    accept: bool,
    watch: bool,
    reason: str,
    *,
    profile_id: str,
    service_name: str,
    action: BridgeLedgerAction,
    scope_digest: bytes,
    request_digest: bytes,
    bridge_ledger_digest: bytes,
    moderation_digest: bytes,
    redress_digest: bytes,
    observations: Iterable[AppealMeshObservation] = (),
    family_count: int = 0,
    path_family_count: int = 0,
    highest_sequence: int = -1,
) -> WitnessAppealMeshReport:
    obs_tuple = tuple(sorted(observations, key=lambda item: (item.sequence, item.observation_digest)))
    digests = tuple(obs.observation_digest for obs in obs_tuple if accept)
    digest = sha256(WITNESS_APPEAL_MESH_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"reason": reason,
        b"profile": profile_id,
        b"service": service_name,
        b"action": action.value,
        b"scope": scope_digest,
        b"request": request_digest,
        b"bridge": bridge_ledger_digest,
        b"moderation": moderation_digest,
        b"redress": redress_digest,
        b"observations": list(digests),
        b"families": family_count,
        b"paths": path_family_count,
        b"highest": highest_sequence,
    }))
    return WitnessAppealMeshReport(kind, accept, watch, reason, profile_id, service_name, action, scope_digest, request_digest, bridge_ledger_digest, moderation_digest, redress_digest, digests, family_count, path_family_count, highest_sequence, digest)


def assess_witness_appeal_mesh(
    observations: Iterable[AppealMeshObservation],
    *,
    bridge_ledger: BridgeLedgerReport,
    moderation: ModerationQuarantineReport,
    redress: RedressReport | None,
    now: int,
    action: BridgeLedgerAction,
    expected_profile_id: str,
    expected_service_name: str,
    expected_scope_digest: bytes,
    expected_request_digest: bytes,
    required_kinds: Iterable[AppealMeshObservationKind] | None = None,
    previous_sequence: int | None = None,
    previously_seen_observations: Iterable[bytes] = (),
    live_hard_negative_digests: Iterable[bytes] = (),
    min_family_diversity: int = 3,
    min_path_diversity: int = 2,
) -> WitnessAppealMeshReport:
    action = BridgeLedgerAction(action)
    redress_digest = redress.report_digest if redress is not None else ZERO_DIGEST
    if bridge_ledger.quarantined:
        return _report(WitnessAppealMeshDecisionKind.QUARANTINE_BRIDGE_LEDGER, False, bridge_ledger.watch, "bridge ledger is quarantined", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, bridge_ledger_digest=bridge_ledger.report_digest, moderation_digest=moderation.report_digest, redress_digest=redress_digest)
    if not bridge_ledger.accept:
        return _report(WitnessAppealMeshDecisionKind.HOLD_BRIDGE_LEDGER_NOT_ACCEPTED, False, bridge_ledger.watch, "bridge ledger not accepted", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, bridge_ledger_digest=bridge_ledger.report_digest, moderation_digest=moderation.report_digest, redress_digest=redress_digest)
    if moderation.quarantined:
        return _report(WitnessAppealMeshDecisionKind.QUARANTINE_MODERATION, False, moderation.watch, "moderation lane quarantined", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, bridge_ledger_digest=bridge_ledger.report_digest, moderation_digest=moderation.report_digest, redress_digest=redress_digest)
    if redress is not None and redress.quarantined:
        return _report(WitnessAppealMeshDecisionKind.QUARANTINE_REDRESS, False, redress.watch, "redress lane quarantined", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, bridge_ledger_digest=bridge_ledger.report_digest, moderation_digest=moderation.report_digest, redress_digest=redress_digest)
    if tuple(live_hard_negative_digests):
        return _report(WitnessAppealMeshDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, True, "live hard negative blocks appeal mesh", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, bridge_ledger_digest=bridge_ledger.report_digest, moderation_digest=moderation.report_digest, redress_digest=redress_digest)
    needs_appeal = bridge_ledger.watch or moderation.watch or (redress.watch if redress is not None else False)
    required = tuple(required_kinds or (
        AppealMeshObservationKind.POLICY_WATCH,
        AppealMeshObservationKind.HARD_NEGATIVE_SCAN,
        AppealMeshObservationKind.STALE_PUBLIC_SCAN,
    )) if needs_appeal else ()
    obs_tuple = tuple(sorted(observations, key=lambda item: (item.sequence, item.observation_digest)))
    if not needs_appeal and not obs_tuple:
        return _report(WitnessAppealMeshDecisionKind.ACCEPT_NOT_NEEDED, True, False, "appeal mesh not needed for clear bridge ledger", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, bridge_ledger_digest=bridge_ledger.report_digest, moderation_digest=moderation.report_digest, redress_digest=redress_digest)
    seen = set(previously_seen_observations)
    fork_guard: dict[int, bytes] = {}
    families: set[str] = set()
    paths: set[str] = set()
    highest = -1
    for obs in obs_tuple:
        if not obs.verifies():
            return _report(WitnessAppealMeshDecisionKind.QUARANTINE_BAD_SIGNATURE, False, True, "bad appeal observation signature", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, bridge_ledger_digest=bridge_ledger.report_digest, moderation_digest=moderation.report_digest, redress_digest=redress_digest, observations=obs_tuple)
        if obs.issued_at > now or obs.expires_at <= now:
            return _report(WitnessAppealMeshDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, False, True, "appeal observation expired or future", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, bridge_ledger_digest=bridge_ledger.report_digest, moderation_digest=moderation.report_digest, redress_digest=redress_digest, observations=obs_tuple)
        if obs.observation_digest in seen:
            return _report(WitnessAppealMeshDecisionKind.QUARANTINE_REPLAY, False, True, "appeal observation replay", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, bridge_ledger_digest=bridge_ledger.report_digest, moderation_digest=moderation.report_digest, redress_digest=redress_digest, observations=obs_tuple)
        if obs.profile_id != expected_profile_id:
            return _report(WitnessAppealMeshDecisionKind.QUARANTINE_PROFILE_DRIFT, False, True, "appeal profile drift", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, bridge_ledger_digest=bridge_ledger.report_digest, moderation_digest=moderation.report_digest, redress_digest=redress_digest, observations=obs_tuple)
        if obs.service_name != expected_service_name:
            return _report(WitnessAppealMeshDecisionKind.QUARANTINE_SERVICE_DRIFT, False, True, "appeal service drift", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, bridge_ledger_digest=bridge_ledger.report_digest, moderation_digest=moderation.report_digest, redress_digest=redress_digest, observations=obs_tuple)
        if obs.action is not action:
            return _report(WitnessAppealMeshDecisionKind.QUARANTINE_ACTION_DRIFT, False, True, "appeal action drift", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, bridge_ledger_digest=bridge_ledger.report_digest, moderation_digest=moderation.report_digest, redress_digest=redress_digest, observations=obs_tuple)
        if obs.scope_digest != expected_scope_digest:
            return _report(WitnessAppealMeshDecisionKind.QUARANTINE_SCOPE_DRIFT, False, True, "appeal scope drift", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, bridge_ledger_digest=bridge_ledger.report_digest, moderation_digest=moderation.report_digest, redress_digest=redress_digest, observations=obs_tuple)
        if obs.request_digest != expected_request_digest:
            return _report(WitnessAppealMeshDecisionKind.QUARANTINE_REQUEST_DRIFT, False, True, "appeal request drift", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, bridge_ledger_digest=bridge_ledger.report_digest, moderation_digest=moderation.report_digest, redress_digest=redress_digest, observations=obs_tuple)
        if obs.bridge_ledger_digest != bridge_ledger.report_digest or obs.moderation_digest != moderation.report_digest or obs.redress_digest != redress_digest:
            return _report(WitnessAppealMeshDecisionKind.QUARANTINE_COMPONENT_DIGEST_DRIFT, False, True, "appeal component digest drift", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, bridge_ledger_digest=bridge_ledger.report_digest, moderation_digest=moderation.report_digest, redress_digest=redress_digest, observations=obs_tuple)
        if previous_sequence is not None and obs.sequence < previous_sequence:
            return _report(WitnessAppealMeshDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, True, "appeal observation rollback", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, bridge_ledger_digest=bridge_ledger.report_digest, moderation_digest=moderation.report_digest, redress_digest=redress_digest, observations=obs_tuple)
        prior = fork_guard.get(obs.sequence)
        if prior is not None and prior != obs.observation_core_digest:
            return _report(WitnessAppealMeshDecisionKind.QUARANTINE_SEQUENCE_FORK, False, True, "same-sequence appeal observation fork", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, bridge_ledger_digest=bridge_ledger.report_digest, moderation_digest=moderation.report_digest, redress_digest=redress_digest, observations=obs_tuple)
        fork_guard[obs.sequence] = obs.observation_core_digest
        families.add(obs.family_id)
        paths.add(obs.path_family)
        highest = max(highest, obs.sequence)
    if any(not obs.accepted for obs in obs_tuple):
        return _report(WitnessAppealMeshDecisionKind.HOLD_OBSERVATION_NOT_ACCEPTED, False, True, "appeal observation not accepted", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, bridge_ledger_digest=bridge_ledger.report_digest, moderation_digest=moderation.report_digest, redress_digest=redress_digest, observations=obs_tuple, family_count=len(families), path_family_count=len(paths), highest_sequence=highest)
    missing = set(required) - {obs.kind for obs in obs_tuple}
    if missing:
        return _report(WitnessAppealMeshDecisionKind.HOLD_MISSING_OBSERVATION, False, True, "appeal mesh missing required observation", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, bridge_ledger_digest=bridge_ledger.report_digest, moderation_digest=moderation.report_digest, redress_digest=redress_digest, observations=obs_tuple, family_count=len(families), path_family_count=len(paths), highest_sequence=highest)
    if len(families) < min_family_diversity:
        return _report(WitnessAppealMeshDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, "appeal mesh lacks family diversity", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, bridge_ledger_digest=bridge_ledger.report_digest, moderation_digest=moderation.report_digest, redress_digest=redress_digest, observations=obs_tuple, family_count=len(families), path_family_count=len(paths), highest_sequence=highest)
    if len(paths) < min_path_diversity:
        return _report(WitnessAppealMeshDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, "appeal mesh lacks path diversity", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, bridge_ledger_digest=bridge_ledger.report_digest, moderation_digest=moderation.report_digest, redress_digest=redress_digest, observations=obs_tuple, family_count=len(families), path_family_count=len(paths), highest_sequence=highest)
    watch = bridge_ledger.watch or moderation.watch or (redress.watch if redress is not None else False) or any(obs.watch for obs in obs_tuple)
    kind = WitnessAppealMeshDecisionKind.ACCEPT_WITH_WATCH if watch else WitnessAppealMeshDecisionKind.ACCEPT_APPEAL_MESH
    return _report(kind, True, watch, "witness appeal mesh accepted as local watched evidence", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, bridge_ledger_digest=bridge_ledger.report_digest, moderation_digest=moderation.report_digest, redress_digest=redress_digest, observations=obs_tuple, family_count=len(families), path_family_count=len(paths), highest_sequence=highest)
