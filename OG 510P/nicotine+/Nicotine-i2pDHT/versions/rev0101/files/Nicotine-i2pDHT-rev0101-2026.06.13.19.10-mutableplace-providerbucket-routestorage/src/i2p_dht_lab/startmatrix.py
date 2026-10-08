"""Launch profile matrix for leaf/garden/bridge/offline DHT modes.

rev0035 stops treating "start the node" as one bit.  A future DHT can start as
a leaf, garden, bridge, or offline design harness; each mode has different
preconditions around router harness, destination persistence, metrics/metadata
budget, useful services, and classic-fallback drift.

This is still local pressure only.  It is not a production launcher.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .bencode import bencode
from .ids import DOMAIN, sha256
from .launchquorum import LaunchMode, LaunchQuorumReport
from .routerharness import RouterHarnessDecisionKind, RouterHarnessMode, RouterHarnessReport

START_MATRIX_DOMAIN = DOMAIN + b":start-matrix-v1:"


class StartMatrixDecisionKind(str, Enum):
    ACCEPT_LEAF_PROFILE = "accept_leaf_profile"
    ACCEPT_GARDEN_PROFILE = "accept_garden_profile"
    ACCEPT_BRIDGE_PROFILE = "accept_bridge_profile"
    ACCEPT_OFFLINE_DESIGN_PROFILE = "accept_offline_design_profile"
    HOLD_ROUTER_UNAVAILABLE = "hold_router_unavailable"
    HOLD_DESTINATION_PERSISTENCE = "hold_destination_persistence"
    HOLD_GARDEN_SERVICE_PROOF = "hold_garden_service_proof"
    HOLD_BRIDGE_EXPLICITNESS = "hold_bridge_explicitness"
    HOLD_METRICS_BUDGET = "hold_metrics_budget"
    QUARANTINE_LAUNCH_QUORUM = "quarantine_launch_quorum"
    QUARANTINE_ROUTER_HARNESS = "quarantine_router_harness"
    QUARANTINE_PROFILE_REPLAY = "quarantine_profile_replay"
    QUARANTINE_INTENT_MISMATCH = "quarantine_intent_mismatch"
    QUARANTINE_CLASSIC_FALLBACK_DRIFT = "quarantine_classic_fallback_drift"
    QUARANTINE_MODE_ROUTER_DRIFT = "quarantine_mode_router_drift"


@dataclass(frozen=True)
class StartProfile:
    name: str
    mode: LaunchMode
    router_mode: RouterHarnessMode
    bound_launch_intent_digest: bytes
    require_persistent_destination: bool = True
    i2p_only: bool = False
    classic_fallback_enabled: bool = False
    garden_service_count: int = 0
    public_bridge_enabled: bool = False
    max_metric_cardinality: int = 8
    metadata_budget_level: str = "normal"

    def __post_init__(self) -> None:
        if not self.name or len(self.name.encode("utf-8")) > 64:
            raise ValueError("start profile needs a short name")
        if len(self.bound_launch_intent_digest) != 32:
            raise ValueError("start profile launch intent digest must be 32 bytes")
        if self.garden_service_count < 0 or self.max_metric_cardinality <= 0:
            raise ValueError("start profile budgets must be positive")
        if self.metadata_budget_level not in {"low", "normal", "power"}:
            raise ValueError("metadata budget must be low/normal/power")

    @property
    def profile_digest(self) -> bytes:
        return sha256(START_MATRIX_DOMAIN + b":profile:" + bencode({
            b"name": self.name,
            b"mode": self.mode.value,
            b"router_mode": self.router_mode.value,
            b"intent": self.bound_launch_intent_digest,
            b"persistent_destination": 1 if self.require_persistent_destination else 0,
            b"i2p_only": 1 if self.i2p_only else 0,
            b"classic_fallback": 1 if self.classic_fallback_enabled else 0,
            b"garden_services": self.garden_service_count,
            b"public_bridge": 1 if self.public_bridge_enabled else 0,
            b"max_metric_cardinality": self.max_metric_cardinality,
            b"metadata_budget": self.metadata_budget_level,
        }))


@dataclass(frozen=True)
class StartMatrixReport:
    decision_kind: StartMatrixDecisionKind
    accept: bool
    reason: str
    profile_digest: bytes
    launch_report_digest: bytes
    router_report_digest: bytes
    pressure_digests: tuple[bytes, ...]
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _report(kind: StartMatrixDecisionKind, accept: bool, reason: str, *, profile: StartProfile, launch: LaunchQuorumReport, router: RouterHarnessReport, pressures: Iterable[bytes] = ()) -> StartMatrixReport:
    pressure_t = tuple(sorted(set(pressures)))
    digest = sha256(START_MATRIX_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"reason": reason,
        b"profile": profile.profile_digest,
        b"launch": launch.report_digest,
        b"router": router.report_digest,
        b"pressures": pressure_t,
    }))
    return StartMatrixReport(kind, accept, reason, profile.profile_digest, launch.report_digest, router.report_digest, pressure_t, digest)


def assess_start_matrix(profile: StartProfile, *, launch: LaunchQuorumReport, router: RouterHarnessReport, previously_seen_profile_digests: Iterable[bytes] = ()) -> StartMatrixReport:
    prior = set(previously_seen_profile_digests)
    if profile.profile_digest in prior:
        return _report(StartMatrixDecisionKind.QUARANTINE_PROFILE_REPLAY, False, "start profile digest was replayed at launch boundary", profile=profile, launch=launch, router=router, pressures=(profile.profile_digest,))
    if profile.bound_launch_intent_digest != launch.launch_intent_digest:
        return _report(StartMatrixDecisionKind.QUARANTINE_INTENT_MISMATCH, False, "start profile is not bound to this launch intent", profile=profile, launch=launch, router=router, pressures=(profile.bound_launch_intent_digest, launch.launch_intent_digest))
    if not launch.accept or launch.quarantined:
        return _report(StartMatrixDecisionKind.QUARANTINE_LAUNCH_QUORUM, False, "launch quorum did not accept before profile matrix", profile=profile, launch=launch, router=router, pressures=(launch.report_digest,))
    if not router.accept or router.quarantined:
        return _report(StartMatrixDecisionKind.QUARANTINE_ROUTER_HARNESS, False, "router harness did not accept before profile matrix", profile=profile, launch=launch, router=router, pressures=(router.report_digest,))
    if profile.i2p_only and profile.classic_fallback_enabled:
        return _report(StartMatrixDecisionKind.QUARANTINE_CLASSIC_FALLBACK_DRIFT, False, "I2P-only start profile cannot silently enable classic fallback", profile=profile, launch=launch, router=router, pressures=(profile.profile_digest,))
    router_offline = router.decision_kind is RouterHarnessDecisionKind.ACCEPT_OFFLINE_DESIGN_HARNESS
    if profile.mode is LaunchMode.OFFLINE_DESIGN:
        if profile.router_mode is not RouterHarnessMode.OFFLINE_NO_ROUTER or not router_offline:
            return _report(StartMatrixDecisionKind.QUARANTINE_MODE_ROUTER_DRIFT, False, "offline design profile must bind to offline router harness", profile=profile, launch=launch, router=router, pressures=(router.report_digest,))
        return _report(StartMatrixDecisionKind.ACCEPT_OFFLINE_DESIGN_PROFILE, True, "offline design profile accepted without live router side effects", profile=profile, launch=launch, router=router)
    if router_offline:
        return _report(StartMatrixDecisionKind.HOLD_ROUTER_UNAVAILABLE, False, "live start profile cannot advance on offline router harness", profile=profile, launch=launch, router=router, pressures=(router.report_digest,))
    if profile.require_persistent_destination and router.decision_kind not in {RouterHarnessDecisionKind.ACCEPT_BUNDLED_I2PD_HARNESS, RouterHarnessDecisionKind.ACCEPT_EXTERNAL_SAM_HARNESS}:
        return _report(StartMatrixDecisionKind.HOLD_DESTINATION_PERSISTENCE, False, "live profile needs accepted persistent router harness", profile=profile, launch=launch, router=router, pressures=(router.report_digest,))
    if profile.max_metric_cardinality > 32 and profile.metadata_budget_level != "power":
        return _report(StartMatrixDecisionKind.HOLD_METRICS_BUDGET, False, "high-cardinality diagnostics require explicit power metadata budget", profile=profile, launch=launch, router=router, pressures=(profile.profile_digest,))
    if profile.mode is LaunchMode.GARDEN:
        if profile.garden_service_count <= 0:
            return _report(StartMatrixDecisionKind.HOLD_GARDEN_SERVICE_PROOF, False, "garden profile needs at least one declared giving service", profile=profile, launch=launch, router=router, pressures=(profile.profile_digest,))
        return _report(StartMatrixDecisionKind.ACCEPT_GARDEN_PROFILE, True, "garden start profile accepted with explicit service surface", profile=profile, launch=launch, router=router)
    if profile.mode is LaunchMode.BRIDGE:
        if not profile.public_bridge_enabled:
            return _report(StartMatrixDecisionKind.HOLD_BRIDGE_EXPLICITNESS, False, "bridge profile requires explicit public bridge bit", profile=profile, launch=launch, router=router, pressures=(profile.profile_digest,))
        return _report(StartMatrixDecisionKind.ACCEPT_BRIDGE_PROFILE, True, "bridge start profile accepted with explicit public-bridge bit", profile=profile, launch=launch, router=router)
    return _report(StartMatrixDecisionKind.ACCEPT_LEAF_PROFILE, True, "leaf start profile accepted", profile=profile, launch=launch, router=router)
