"""rev0091 native re-entry preflight.

A relaunch candidate can only re-enter the existing native load gate through a
no-network preflight.  This module deliberately does not load native code and
does not dispatch a native call.  It only produces a route-back-to-load-gate
marker when handoff, relaunch, loader seal, and Python-oracle seal agree.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .bencode import bencode
from .ids import DOMAIN, sha256
from .loaderseal import NativeLoaderSealReport
from .nativehandoff import NativeHandoffReport
from .nativeoracleseal import NativeOracleSealReport
from .relaunchgate import NativeRelaunchGateReport

NATIVE_PREFLIGHT_DOMAIN = DOMAIN + b":native-preflight-v1:"


class NativePreflightDecisionKind(str, Enum):
    ACCEPT_ROUTE_TO_LOAD_GATE_ONLY = "accept_route_to_load_gate_only"
    HOLD_HANDOFF_NOT_READY = "hold_handoff_not_ready"
    HOLD_RELAUNCH_NOT_READY = "hold_relaunch_not_ready"
    HOLD_LOADER_SEAL_NOT_READY = "hold_loader_seal_not_ready"
    HOLD_ORACLE_SEAL_NOT_READY = "hold_oracle_seal_not_ready"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_DISPATCH_OR_LOAD_ATTEMPT = "quarantine_dispatch_or_load_attempt"
    QUARANTINE_MEMORY_DROP = "quarantine_memory_drop"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_REPLAY_OR_ROLLBACK = "quarantine_replay_or_rollback"
    QUARANTINE_SAME_SEQUENCE_FORK = "quarantine_same_sequence_fork"
    QUARANTINE_PREVIOUS_LINK_MISMATCH = "quarantine_previous_link_mismatch"
    QUARANTINE_LOW_DIVERSITY = "quarantine_low_diversity"


@dataclass(frozen=True)
class NativePreflightIntent:
    component: str
    profile: str
    operation: str
    request_id: str
    sequence: int
    previous_digest: bytes
    handoff_digest: bytes
    relaunch_gate_digest: bytes
    loader_seal_digest: bytes
    oracle_seal_digest: bytes
    artifact_digest: bytes
    source_digest: bytes
    fallback_digest: bytes
    python_oracle_digest: bytes
    loader_id: str
    route_to_load_gate_requested: bool
    native_load_attempted: bool
    native_dispatch_attempted: bool
    python_fallback_active: bool
    preserve_handoff_memory: bool
    preserve_relaunch_memory: bool
    preserve_loader_seal_memory: bool
    preserve_oracle_seal_memory: bool
    preserve_fallback_memory: bool
    preserve_tombstone_memory: bool
    preserve_quarantine_memory: bool
    preserve_crash_memory: bool
    family_id: str
    path_family_id: str
    note: str = ""

    @property
    def intent_digest(self) -> bytes:
        return sha256(NATIVE_PREFLIGHT_DOMAIN + b":intent:" + bencode({
            b"component": self.component,
            b"profile": self.profile,
            b"operation": self.operation,
            b"request": self.request_id,
            b"seq": self.sequence,
            b"prev": self.previous_digest,
            b"handoff": self.handoff_digest,
            b"relaunch": self.relaunch_gate_digest,
            b"loader_seal": self.loader_seal_digest,
            b"oracle_seal": self.oracle_seal_digest,
            b"artifact": self.artifact_digest,
            b"source": self.source_digest,
            b"fallback": self.fallback_digest,
            b"oracle": self.python_oracle_digest,
            b"loader_id": self.loader_id,
            b"route_to_load_gate": 1 if self.route_to_load_gate_requested else 0,
            b"load_attempted": 1 if self.native_load_attempted else 0,
            b"dispatch_attempted": 1 if self.native_dispatch_attempted else 0,
            b"fallback_active": 1 if self.python_fallback_active else 0,
            b"preserve_handoff": 1 if self.preserve_handoff_memory else 0,
            b"preserve_relaunch": 1 if self.preserve_relaunch_memory else 0,
            b"preserve_loader": 1 if self.preserve_loader_seal_memory else 0,
            b"preserve_oracle": 1 if self.preserve_oracle_seal_memory else 0,
            b"preserve_fallback": 1 if self.preserve_fallback_memory else 0,
            b"preserve_tombstone": 1 if self.preserve_tombstone_memory else 0,
            b"preserve_quarantine": 1 if self.preserve_quarantine_memory else 0,
            b"preserve_crash": 1 if self.preserve_crash_memory else 0,
            b"family": self.family_id,
            b"path_family": self.path_family_id,
            b"note": self.note,
        }))


@dataclass(frozen=True)
class NativePreflightReport:
    decision_kind: NativePreflightDecisionKind
    accepted: bool
    route_to_load_gate_only: bool
    native_load_allowed: bool
    dispatch_allowed: bool
    fallback_active: bool
    quarantine: bool
    watch: bool
    obligations: tuple[str, ...]
    intent_digest: bytes
    handoff_digest: bytes
    relaunch_gate_digest: bytes
    loader_seal_digest: bytes
    oracle_seal_digest: bytes
    artifact_digest: bytes
    source_digest: bytes
    fallback_digest: bytes
    python_oracle_digest: bytes
    loader_id: str
    tombstone_memory: bool
    fault_memory: bool
    family_count: int
    path_family_count: int

    @property
    def report_digest(self) -> bytes:
        return sha256(NATIVE_PREFLIGHT_DOMAIN + b":report:" + bencode({
            b"decision": NativePreflightDecisionKind(self.decision_kind).value,
            b"accepted": 1 if self.accepted else 0,
            b"route_to_load_gate_only": 1 if self.route_to_load_gate_only else 0,
            b"load_allowed": 1 if self.native_load_allowed else 0,
            b"dispatch_allowed": 1 if self.dispatch_allowed else 0,
            b"fallback_active": 1 if self.fallback_active else 0,
            b"quarantine": 1 if self.quarantine else 0,
            b"watch": 1 if self.watch else 0,
            b"obligations": list(self.obligations),
            b"intent": self.intent_digest,
            b"handoff": self.handoff_digest,
            b"relaunch": self.relaunch_gate_digest,
            b"loader_seal": self.loader_seal_digest,
            b"oracle_seal": self.oracle_seal_digest,
            b"artifact": self.artifact_digest,
            b"source": self.source_digest,
            b"fallback": self.fallback_digest,
            b"oracle": self.python_oracle_digest,
            b"loader_id": self.loader_id,
            b"tombstone": 1 if self.tombstone_memory else 0,
            b"fault_memory": 1 if self.fault_memory else 0,
            b"family_count": self.family_count,
            b"path_family_count": self.path_family_count,
        }))


def assess_native_preflight(
    handoff: NativeHandoffReport,
    relaunch: NativeRelaunchGateReport,
    loader_seal: NativeLoaderSealReport,
    oracle_seal: NativeOracleSealReport,
    intent: NativePreflightIntent,
    *,
    previous: NativePreflightIntent | None = None,
    prior_intent_digests: tuple[bytes, ...] = (),
    observed_families: tuple[str, ...] = (),
    observed_path_families: tuple[str, ...] = (),
    min_families: int = 2,
    min_path_families: int = 2,
) -> NativePreflightReport:
    families = set(observed_families or (intent.family_id,))
    path_families = set(observed_path_families or (intent.path_family_id,))
    tombstone_memory = bool(handoff.tombstone_carried and loader_seal.tombstone_memory and oracle_seal.tombstone_memory and intent.preserve_tombstone_memory)
    fault_memory = bool(handoff.fault_memory_carried and loader_seal.fault_memory and oracle_seal.fault_memory and intent.preserve_quarantine_memory and intent.preserve_crash_memory)

    def report(kind: NativePreflightDecisionKind, accepted: bool, route: bool, fallback: bool, quarantine: bool, watch: bool, obligations: tuple[str, ...]) -> NativePreflightReport:
        return NativePreflightReport(kind, accepted, route, False, False, fallback, quarantine, watch, obligations, intent.intent_digest, handoff.report_digest, relaunch.report_digest, loader_seal.report_digest, oracle_seal.report_digest, intent.artifact_digest, intent.source_digest, intent.fallback_digest, intent.python_oracle_digest, intent.loader_id, tombstone_memory, fault_memory, len(families), len(path_families))

    if intent.intent_digest in prior_intent_digests:
        return report(NativePreflightDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, False, True, True, False, ("native-preflight-replay",))
    if previous is not None:
        if intent.sequence < previous.sequence:
            return report(NativePreflightDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, False, True, True, False, ("native-preflight-rollback",))
        if intent.sequence == previous.sequence and intent.intent_digest != previous.intent_digest:
            return report(NativePreflightDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK, False, False, True, True, False, ("native-preflight-same-sequence-fork",))
        if intent.sequence > previous.sequence and intent.previous_digest != previous.intent_digest:
            return report(NativePreflightDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH, False, False, True, True, False, ("native-preflight-previous-link-mismatch",))
    if len(families) < min_families or len(path_families) < min_path_families:
        return report(NativePreflightDecisionKind.QUARANTINE_LOW_DIVERSITY, False, False, True, True, False, ("native-preflight-low-diversity",))
    if not all((intent.component, intent.profile, intent.operation, intent.request_id, intent.loader_id)):
        return report(NativePreflightDecisionKind.QUARANTINE_SCOPE_DRIFT, False, False, True, True, False, ("native-preflight-missing-boundary",))
    if intent.native_load_attempted or intent.native_dispatch_attempted:
        return report(NativePreflightDecisionKind.QUARANTINE_DISPATCH_OR_LOAD_ATTEMPT, False, False, True, True, False, ("native-preflight-load-or-dispatch-attempt",))
    if not handoff.accepted or not handoff.relaunch_candidate:
        return report(NativePreflightDecisionKind.HOLD_HANDOFF_NOT_READY, False, False, True, handoff.quarantine, True, ("handoff-not-relaunch-candidate",))
    if not relaunch.accepted or not relaunch.relaunch_plan_ready:
        return report(NativePreflightDecisionKind.HOLD_RELAUNCH_NOT_READY, False, False, True, relaunch.quarantine, True, ("relaunch-gate-not-ready",))
    if not loader_seal.accepted or not loader_seal.sealed:
        return report(NativePreflightDecisionKind.HOLD_LOADER_SEAL_NOT_READY, False, False, True, loader_seal.quarantine, True, ("loader-seal-not-ready",))
    if not oracle_seal.accepted or not oracle_seal.python_oracle_sealed:
        return report(NativePreflightDecisionKind.HOLD_ORACLE_SEAL_NOT_READY, False, False, True, oracle_seal.quarantine, True, ("oracle-seal-not-ready",))
    if intent.handoff_digest != handoff.report_digest or intent.relaunch_gate_digest != relaunch.report_digest or intent.loader_seal_digest != loader_seal.report_digest or intent.oracle_seal_digest != oracle_seal.report_digest:
        return report(NativePreflightDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, True, True, False, ("native-preflight-component-digest-drift",))
    if intent.artifact_digest != handoff.artifact_digest or intent.artifact_digest != relaunch.artifact_digest or intent.artifact_digest != loader_seal.artifact_digest or intent.artifact_digest != oracle_seal.artifact_digest:
        return report(NativePreflightDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, True, True, False, ("native-preflight-artifact-digest-drift",))
    if intent.source_digest != handoff.source_digest or intent.source_digest != relaunch.source_digest or intent.source_digest != loader_seal.source_digest or intent.source_digest != oracle_seal.source_digest:
        return report(NativePreflightDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, True, True, False, ("native-preflight-source-digest-drift",))
    if intent.fallback_digest != handoff.fallback_digest or intent.fallback_digest != relaunch.fallback_digest or intent.fallback_digest != loader_seal.fallback_digest or intent.fallback_digest != oracle_seal.fallback_digest:
        return report(NativePreflightDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, True, True, False, ("native-preflight-fallback-digest-drift",))
    if intent.python_oracle_digest != handoff.python_oracle_digest or intent.python_oracle_digest != relaunch.python_oracle_digest or intent.python_oracle_digest != loader_seal.python_oracle_digest or intent.python_oracle_digest != oracle_seal.python_oracle_digest:
        return report(NativePreflightDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, True, True, False, ("native-preflight-oracle-digest-drift",))
    if not intent.python_fallback_active or not intent.preserve_handoff_memory or not intent.preserve_relaunch_memory or not intent.preserve_loader_seal_memory or not intent.preserve_oracle_seal_memory or not intent.preserve_fallback_memory or not tombstone_memory or not fault_memory:
        return report(NativePreflightDecisionKind.QUARANTINE_MEMORY_DROP, False, False, True, True, False, ("native-preflight-memory-drop",))
    if not intent.route_to_load_gate_requested:
        return report(NativePreflightDecisionKind.HOLD_RELAUNCH_NOT_READY, False, False, True, False, True, ("native-preflight-route-not-requested",))
    return report(NativePreflightDecisionKind.ACCEPT_ROUTE_TO_LOAD_GATE_ONLY, True, True, True, False, handoff.watch or relaunch.watch or loader_seal.watch or oracle_seal.watch, ("route-to-native-load-gate-only", "native-load-and-dispatch-remain-forbidden", "python-fallback-active"))
