"""Repeated public-bridge chaos pressure.

A single bridge egress report can look locally acceptable.  The nastier bugs show
up across restarts and windows: repeated stale-public announcements, appeal-free
watch debt, family-captured egress, or the same public refresh replayed until it
looks normal.  This module keeps those cross-window observations typed.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .bridgeegress import BridgeEgressReport
from .ids import DOMAIN, sha256
from .shadowfire import ShadowFireAction
from .witnessappeal import WitnessAppealReport

BRIDGE_CHAOS_DOMAIN = DOMAIN + b":bridge-chaos-v1:"
ZERO_DIGEST = b"\x00" * 32


class BridgeChaosObservationKind(str, Enum):
    EGRESS_REPORT = "egress_report"
    WITNESS_APPEAL = "witness_appeal"
    STALE_PUBLIC_ANNOUNCEMENT = "stale_public_announcement"
    WITHDRAWAL_OBSERVED = "withdrawal_observed"
    RESTART_BOUNDARY = "restart_boundary"
    HARD_NEGATIVE = "hard_negative"


class BridgeChaosDecisionKind(str, Enum):
    ACCEPT_BRIDGE_CHAOS_WINDOW = "accept_bridge_chaos_window"
    ACCEPT_WITH_WATCH = "accept_with_watch"
    CONTINUE_MORE_ROUNDS = "continue_more_rounds"
    HOLD_MISSING_EGRESS = "hold_missing_egress"
    HOLD_WATCH_WITHOUT_APPEAL = "hold_watch_without_appeal"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_RESTART_DIVERSITY = "hold_low_restart_diversity"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_PROFILE_DRIFT = "quarantine_profile_drift"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_REQUEST_DRIFT = "quarantine_request_drift"
    QUARANTINE_ACTION_DRIFT = "quarantine_action_drift"
    QUARANTINE_STALE_PUBLIC_REPLAY = "quarantine_stale_public_replay"
    QUARANTINE_HARD_NEGATIVE = "quarantine_hard_negative"
    QUARANTINE_FAMILY_CAPTURE = "quarantine_family_capture"


@dataclass(frozen=True)
class BridgeChaosObservation:
    kind: BridgeChaosObservationKind
    action: ShadowFireAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    evidence_digest: bytes
    restart_id: str
    family_id: str
    path_family: str
    accepted: bool = True
    watch: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "kind", BridgeChaosObservationKind(self.kind))
        object.__setattr__(self, "action", ShadowFireAction(self.action))
        for name, value in (("scope_digest", self.scope_digest), ("request_digest", self.request_digest), ("evidence_digest", self.evidence_digest)):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if not self.profile_id or not self.service_name or not self.restart_id or not self.family_id or not self.path_family:
            raise ValueError("chaos observation needs profile/service/restart/family hints")

    @classmethod
    def from_egress(cls, *, report: BridgeEgressReport, restart_id: str, family_id: str, path_family: str) -> "BridgeChaosObservation":
        return cls(
            kind=BridgeChaosObservationKind.EGRESS_REPORT,
            action=report.action,
            profile_id=report.profile_id,
            service_name=report.service_name,
            scope_digest=report.scope_digest,
            request_digest=report.request_digest,
            evidence_digest=report.report_digest,
            restart_id=restart_id,
            family_id=family_id,
            path_family=path_family,
            accepted=report.accepted,
            watch=report.watch,
        )

    @classmethod
    def from_appeal(cls, *, report: WitnessAppealReport, restart_id: str, family_id: str, path_family: str) -> "BridgeChaosObservation":
        return cls(
            kind=BridgeChaosObservationKind.WITNESS_APPEAL,
            action=report.action,
            profile_id=report.profile_id,
            service_name=report.service_name,
            scope_digest=report.scope_digest,
            request_digest=report.request_digest,
            evidence_digest=report.report_digest,
            restart_id=restart_id,
            family_id=family_id,
            path_family=path_family,
            accepted=report.accepted,
            watch=report.watch,
        )

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"kind": self.kind.value,
            b"action": self.action.value,
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"evidence": self.evidence_digest,
            b"restart": self.restart_id,
            b"family": self.family_id,
            b"path_family": self.path_family,
            b"accepted": 1 if self.accepted else 0,
            b"watch": 1 if self.watch else 0,
        }

    @property
    def observation_digest(self) -> bytes:
        return sha256(BRIDGE_CHAOS_DOMAIN + b":observation:" + bencode(self.bvalue()))


@dataclass(frozen=True)
class BridgeChaosReport:
    decision_kind: BridgeChaosDecisionKind
    accepted: bool
    watch: bool
    reason: str
    action: ShadowFireAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    observation_digests: tuple[bytes, ...]
    restart_count: int
    family_count: int
    path_family_count: int
    stale_public_count: int
    egress_count: int
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _report(
    kind: BridgeChaosDecisionKind,
    accepted: bool,
    watch: bool,
    reason: str,
    *,
    action: ShadowFireAction,
    profile_id: str,
    service_name: str,
    scope_digest: bytes,
    request_digest: bytes,
    observations: Iterable[BridgeChaosObservation],
) -> BridgeChaosReport:
    obs_tuple = tuple(observations)
    digests = tuple(obs.observation_digest for obs in obs_tuple)
    restarts = tuple(sorted({obs.restart_id for obs in obs_tuple}))
    families = tuple(sorted({obs.family_id for obs in obs_tuple}))
    paths = tuple(sorted({obs.path_family for obs in obs_tuple}))
    stale_count = sum(1 for obs in obs_tuple if obs.kind is BridgeChaosObservationKind.STALE_PUBLIC_ANNOUNCEMENT)
    egress_count = sum(1 for obs in obs_tuple if obs.kind is BridgeChaosObservationKind.EGRESS_REPORT)
    digest = sha256(BRIDGE_CHAOS_DOMAIN + b":report:" + bencode({
        b"decision": kind.value,
        b"accepted": 1 if accepted else 0,
        b"watch": 1 if watch else 0,
        b"reason": reason,
        b"action": action.value,
        b"profile": profile_id,
        b"service": service_name,
        b"scope": scope_digest,
        b"request": request_digest,
        b"observations": list(digests),
        b"restarts": list(restarts),
        b"families": list(families),
        b"paths": list(paths),
        b"stale": stale_count,
        b"egress": egress_count,
    }))
    return BridgeChaosReport(kind, accepted, watch, reason, action, profile_id, service_name, scope_digest, request_digest, digests, len(restarts), len(families), len(paths), stale_count, egress_count, digest)


def assess_bridge_chaos_window(
    observations: Iterable[BridgeChaosObservation],
    *,
    expected_action: ShadowFireAction,
    expected_profile_id: str,
    expected_service_name: str,
    expected_scope_digest: bytes,
    expected_request_digest: bytes,
    previously_seen_observation_digests: Iterable[bytes] = (),
    min_restart_diversity: int = 2,
    min_family_diversity: int = 2,
    min_path_diversity: int = 2,
    max_stale_public_count: int = 0,
    max_family_share_numerator: int = 2,
    max_family_share_denominator: int = 3,
    allow_watch: bool = False,
) -> BridgeChaosReport:
    expected_action = ShadowFireAction(expected_action)
    obs_tuple = tuple(observations)
    seen = set(previously_seen_observation_digests)
    if not obs_tuple:
        return _report(BridgeChaosDecisionKind.CONTINUE_MORE_ROUNDS, False, False, "empty bridge chaos window", action=expected_action, profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, observations=obs_tuple)
    if any(obs.observation_digest in seen for obs in obs_tuple):
        return _report(BridgeChaosDecisionKind.QUARANTINE_REPLAY, False, False, "bridge chaos observation replay", action=expected_action, profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, observations=obs_tuple)
    for obs in obs_tuple:
        if obs.profile_id != expected_profile_id or obs.service_name != expected_service_name:
            return _report(BridgeChaosDecisionKind.QUARANTINE_PROFILE_DRIFT, False, False, "chaos profile/service drift", action=expected_action, profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, observations=(obs,))
        if obs.action is not expected_action:
            return _report(BridgeChaosDecisionKind.QUARANTINE_ACTION_DRIFT, False, False, "chaos action drift", action=expected_action, profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, observations=(obs,))
        if obs.scope_digest != expected_scope_digest:
            return _report(BridgeChaosDecisionKind.QUARANTINE_SCOPE_DRIFT, False, False, "chaos scope drift", action=expected_action, profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, observations=(obs,))
        if obs.request_digest != expected_request_digest:
            return _report(BridgeChaosDecisionKind.QUARANTINE_REQUEST_DRIFT, False, False, "chaos request drift", action=expected_action, profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, observations=(obs,))
    if any(obs.kind is BridgeChaosObservationKind.HARD_NEGATIVE for obs in obs_tuple):
        return _report(BridgeChaosDecisionKind.QUARANTINE_HARD_NEGATIVE, False, False, "hard-negative bridge chaos observation", action=expected_action, profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, observations=obs_tuple)
    stale = [obs for obs in obs_tuple if obs.kind is BridgeChaosObservationKind.STALE_PUBLIC_ANNOUNCEMENT]
    if len(stale) > max_stale_public_count:
        return _report(BridgeChaosDecisionKind.QUARANTINE_STALE_PUBLIC_REPLAY, False, False, "stale public announcement replay across bridge chaos window", action=expected_action, profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, observations=obs_tuple)
    egress = [obs for obs in obs_tuple if obs.kind is BridgeChaosObservationKind.EGRESS_REPORT]
    if not egress:
        return _report(BridgeChaosDecisionKind.HOLD_MISSING_EGRESS, False, False, "bridge chaos window has no accepted egress observation", action=expected_action, profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, observations=obs_tuple)
    watch_egress = [obs for obs in egress if obs.watch]
    appeals = [obs for obs in obs_tuple if obs.kind is BridgeChaosObservationKind.WITNESS_APPEAL and obs.accepted]
    if watch_egress and not appeals:
        return _report(BridgeChaosDecisionKind.HOLD_WATCH_WITHOUT_APPEAL, False, True, "watch egress lacks witness appeal observation", action=expected_action, profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, observations=obs_tuple)
    if len({obs.restart_id for obs in obs_tuple}) < min_restart_diversity:
        return _report(BridgeChaosDecisionKind.HOLD_LOW_RESTART_DIVERSITY, False, False, "bridge chaos lacks restart diversity", action=expected_action, profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, observations=obs_tuple)
    if len({obs.family_id for obs in obs_tuple}) < min_family_diversity:
        return _report(BridgeChaosDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, False, "bridge chaos lacks family diversity", action=expected_action, profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, observations=obs_tuple)
    if len({obs.path_family for obs in obs_tuple}) < min_path_diversity:
        return _report(BridgeChaosDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, False, "bridge chaos lacks path diversity", action=expected_action, profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, observations=obs_tuple)
    family_counts: dict[str, int] = {}
    for obs in obs_tuple:
        family_counts[obs.family_id] = family_counts.get(obs.family_id, 0) + 1
    if family_counts and max(family_counts.values()) * max_family_share_denominator > len(obs_tuple) * max_family_share_numerator:
        return _report(BridgeChaosDecisionKind.QUARANTINE_FAMILY_CAPTURE, False, False, "one family dominates bridge chaos observations", action=expected_action, profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, observations=obs_tuple)
    watch = any(obs.watch for obs in obs_tuple)
    if watch and not allow_watch:
        return _report(BridgeChaosDecisionKind.ACCEPT_WITH_WATCH, True, True, "bridge chaos accepted but watch debt remains", action=expected_action, profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, observations=obs_tuple)
    return _report(BridgeChaosDecisionKind.ACCEPT_BRIDGE_CHAOS_WINDOW, True, watch, "bridge chaos window accepted with repeated diverse observations", action=expected_action, profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, observations=obs_tuple)
