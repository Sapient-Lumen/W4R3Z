"""Cold-launch quorum gate for restart + negotiation + transport probe.

rev0034 joins two rev0033 lines that must meet before a future node wakes up:

* negotiation/migration/SAM-shadow safe-start says a peer session is locally safe;
* persistence/journal/checkpoint/store restart join says local memory is durable;
* SAM probe says the router assumption is explicit, local, and streaming-first.

This is still a no-network design surface.  It prevents convenient component
success from silently becoming sticky launch state.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .bencode import bencode
from .ids import DOMAIN, sha256
from .persistjoin import PersistJoinDecisionKind, PersistJoinReport
from .safestart import SafeStartReport
from .samprobe import SamProbeDecisionKind, SamProbeReport

LAUNCH_QUORUM_DOMAIN = DOMAIN + b":launch-quorum-v1:"


class LaunchMode(str, Enum):
    LEAF = "leaf"
    GARDEN = "garden"
    BRIDGE = "bridge"
    OFFLINE_DESIGN = "offline_design"


class LaunchQuorumDecisionKind(str, Enum):
    ACCEPT_LAUNCH = "accept_launch"
    ACCEPT_OFFLINE_DESIGN_LAUNCH = "accept_offline_design_launch"
    HOLD_ROUTER_UNAVAILABLE = "hold_router_unavailable"
    HOLD_CRASH_TAIL_WATCH = "hold_crash_tail_watch"
    HOLD_MODE_REQUIREMENT = "hold_mode_requirement"
    QUARANTINE_SAFE_START = "quarantine_safe_start"
    QUARANTINE_PERSIST_JOIN = "quarantine_persist_join"
    QUARANTINE_SAM_PROBE = "quarantine_sam_probe"
    QUARANTINE_DIGEST_REPLAY = "quarantine_digest_replay"
    QUARANTINE_INTENT_MISMATCH = "quarantine_intent_mismatch"
    QUARANTINE_ENDPOINT_DRIFT = "quarantine_endpoint_drift"


@dataclass(frozen=True)
class LaunchIntent:
    mode: LaunchMode
    intent_digest: bytes
    endpoint_digest: bytes
    generation: int
    allow_no_router: bool = False
    allow_crash_tail_watch: bool = False
    require_streaming_probe: bool = True

    def __post_init__(self) -> None:
        if len(self.intent_digest) != 32:
            raise ValueError("launch intent digest must be 32 bytes")
        if len(self.endpoint_digest) != 32:
            raise ValueError("launch endpoint digest must be 32 bytes")
        if self.generation < 0:
            raise ValueError("launch generation must be non-negative")

    @property
    def launch_intent_digest(self) -> bytes:
        return sha256(LAUNCH_QUORUM_DOMAIN + b":intent:" + bencode({
            b"mode": self.mode.value,
            b"intent": self.intent_digest,
            b"endpoint": self.endpoint_digest,
            b"generation": self.generation,
            b"allow_no_router": 1 if self.allow_no_router else 0,
            b"allow_crash_tail": 1 if self.allow_crash_tail_watch else 0,
            b"require_streaming": 1 if self.require_streaming_probe else 0,
        }))


@dataclass(frozen=True)
class LaunchQuorumReport:
    decision_kind: LaunchQuorumDecisionKind
    accept: bool
    reason: str
    launch_intent_digest: bytes
    safe_start_report_digest: bytes
    persist_join_report_digest: bytes
    sam_probe_transcript_digest: bytes
    pressure_digests: tuple[bytes, ...]
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _report(
    kind: LaunchQuorumDecisionKind,
    accept: bool,
    reason: str,
    *,
    intent: LaunchIntent,
    safe_start: SafeStartReport,
    persist_join: PersistJoinReport,
    sam_probe: SamProbeReport,
    pressures: Iterable[bytes] = (),
) -> LaunchQuorumReport:
    pressure_t = tuple(sorted(set(pressures)))
    digest = sha256(LAUNCH_QUORUM_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"reason": reason,
        b"intent": intent.launch_intent_digest,
        b"safe_start": safe_start.report_digest,
        b"persist_join": persist_join.report_digest,
        b"sam_probe": sam_probe.transcript_digest,
        b"pressures": list(pressure_t),
    }))
    return LaunchQuorumReport(kind, accept, reason, intent.launch_intent_digest, safe_start.report_digest, persist_join.report_digest, sam_probe.transcript_digest, pressure_t, digest)


def assess_launch_quorum(
    intent: LaunchIntent,
    *,
    safe_start: SafeStartReport,
    persist_join: PersistJoinReport,
    sam_probe: SamProbeReport,
    previously_seen_digests: Iterable[bytes] = (),
) -> LaunchQuorumReport:
    """Join launch reports before any future sticky node start."""
    component_digests = (safe_start.report_digest, persist_join.report_digest, sam_probe.transcript_digest)
    prior = set(previously_seen_digests)
    if any(digest in prior for digest in component_digests) or len(set(component_digests)) != len(component_digests):
        return _report(LaunchQuorumDecisionKind.QUARANTINE_DIGEST_REPLAY, False, "launch component report digest replay or alias", intent=intent, safe_start=safe_start, persist_join=persist_join, sam_probe=sam_probe, pressures=component_digests)
    if safe_start.quarantined or not safe_start.accept:
        return _report(LaunchQuorumDecisionKind.QUARANTINE_SAFE_START, False, "safe-start report did not accept", intent=intent, safe_start=safe_start, persist_join=persist_join, sam_probe=sam_probe, pressures=(safe_start.report_digest, *safe_start.pressure_digests))
    if persist_join.quarantined or not persist_join.accept:
        return _report(LaunchQuorumDecisionKind.QUARANTINE_PERSIST_JOIN, False, "persist-join report did not accept", intent=intent, safe_start=safe_start, persist_join=persist_join, sam_probe=sam_probe, pressures=(persist_join.report_digest, *persist_join.pressure_digests))
    if sam_probe.quarantined:
        return _report(LaunchQuorumDecisionKind.QUARANTINE_SAM_PROBE, False, "SAM probe quarantined", intent=intent, safe_start=safe_start, persist_join=persist_join, sam_probe=sam_probe, pressures=(sam_probe.transcript_digest,))
    if safe_start.intent_digest != intent.intent_digest:
        return _report(LaunchQuorumDecisionKind.QUARANTINE_INTENT_MISMATCH, False, "safe-start intent does not match launch intent", intent=intent, safe_start=safe_start, persist_join=persist_join, sam_probe=sam_probe, pressures=(safe_start.intent_digest, intent.intent_digest))
    if sam_probe.endpoint_digest != intent.endpoint_digest:
        return _report(LaunchQuorumDecisionKind.QUARANTINE_ENDPOINT_DRIFT, False, "SAM probe endpoint changed under launch intent", intent=intent, safe_start=safe_start, persist_join=persist_join, sam_probe=sam_probe, pressures=(sam_probe.endpoint_digest, intent.endpoint_digest))

    no_router = sam_probe.decision_kind is SamProbeDecisionKind.ACCEPT_LOCAL_UNAVAILABLE
    streaming_ok = sam_probe.decision_kind is SamProbeDecisionKind.ACCEPT_STREAMING_FIRST_PROBE
    session_only = sam_probe.decision_kind is SamProbeDecisionKind.ACCEPT_SESSION_ONLY
    if no_router:
        if intent.allow_no_router and intent.mode is LaunchMode.OFFLINE_DESIGN:
            return _report(LaunchQuorumDecisionKind.ACCEPT_OFFLINE_DESIGN_LAUNCH, True, "offline design launch accepted with explicit local-unavailable SAM probe", intent=intent, safe_start=safe_start, persist_join=persist_join, sam_probe=sam_probe)
        return _report(LaunchQuorumDecisionKind.HOLD_ROUTER_UNAVAILABLE, False, "router unavailable is explicit but not enough for live launch", intent=intent, safe_start=safe_start, persist_join=persist_join, sam_probe=sam_probe, pressures=(sam_probe.transcript_digest,))
    if intent.require_streaming_probe and not streaming_ok:
        return _report(LaunchQuorumDecisionKind.HOLD_MODE_REQUIREMENT, False, "launch mode requires completed streaming-first probe", intent=intent, safe_start=safe_start, persist_join=persist_join, sam_probe=sam_probe, pressures=(sam_probe.transcript_digest,))
    if intent.mode in {LaunchMode.GARDEN, LaunchMode.BRIDGE} and not streaming_ok:
        return _report(LaunchQuorumDecisionKind.HOLD_MODE_REQUIREMENT, False, "garden/bridge mode must prove stream connect before service", intent=intent, safe_start=safe_start, persist_join=persist_join, sam_probe=sam_probe, pressures=(sam_probe.transcript_digest,))
    if persist_join.decision_kind is PersistJoinDecisionKind.ACCEPT_WITH_CRASH_TAIL_WATCH and not intent.allow_crash_tail_watch:
        return _report(LaunchQuorumDecisionKind.HOLD_CRASH_TAIL_WATCH, False, "restart has crash-tail watch and launch intent does not allow it", intent=intent, safe_start=safe_start, persist_join=persist_join, sam_probe=sam_probe, pressures=(persist_join.report_digest,))
    if session_only and intent.mode is LaunchMode.LEAF and not intent.require_streaming_probe:
        return _report(LaunchQuorumDecisionKind.ACCEPT_LAUNCH, True, "leaf launch accepted with session-only probe under explicit policy", intent=intent, safe_start=safe_start, persist_join=persist_join, sam_probe=sam_probe)
    return _report(LaunchQuorumDecisionKind.ACCEPT_LAUNCH, True, "launch quorum accepted at joined restart/session/router boundary", intent=intent, safe_start=safe_start, persist_join=persist_join, sam_probe=sam_probe)
