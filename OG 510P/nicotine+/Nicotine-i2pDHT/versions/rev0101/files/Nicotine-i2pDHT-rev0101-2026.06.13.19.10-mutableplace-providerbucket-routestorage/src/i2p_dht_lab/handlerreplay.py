"""Restart replay lab for handler capsules and side-effect journals.

rev0054 treats restart replay as its own public-edge boundary.  A handler
capsule report and a side-effect journal report can be valid in isolation, but
a node that restarts must still recover an exact, monotonic, previous-linked,
component-bound local replay window before sticky handler/side-effect memory can
advance.  This module is intentionally no-network and toy-signed.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Any, Iterable

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST

HANDLER_REPLAY_DOMAIN = DOMAIN + b":handler-replay-v1:"


class ReplayLane(str, Enum):
    HANDLER_CAPSULE = "handler_capsule"
    SIDE_EFFECT_JOURNAL = "side_effect_journal"
    ADAPTER_FUZZ = "adapter_fuzz"


class HandlerReplayDecisionKind(str, Enum):
    ACCEPT_REPLAY_WINDOW = "accept_replay_window"
    ACCEPT_WITH_WATCH = "accept_with_watch"
    EMPTY_NO_FRAMES = "empty_no_frames"
    HOLD_MISSING_LANES = "hold_missing_lanes"
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
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"


@dataclass(frozen=True)
class HandlerReplayFrame:
    lane: ReplayLane
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    component_report_digest: bytes
    sequence: int
    previous_frame_digest: bytes
    issued_at: int
    expires_at: int
    hard_negative_count: int
    family_id: str
    path_family: str
    signer_public_key: bytes
    signature: bytes = b""

    def __post_init__(self) -> None:
        object.__setattr__(self, "lane", ReplayLane(self.lane))
        if not self.profile_id or not self.service_name or not self.family_id or not self.path_family:
            raise ValueError("replay frame needs profile/service/family/path")
        if self.sequence < 0 or self.hard_negative_count < 0:
            raise ValueError("sequence and hard_negative_count must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("expires_at must follow issued_at")
        for name, value in (
            ("scope_digest", self.scope_digest),
            ("request_digest", self.request_digest),
            ("component_report_digest", self.component_report_digest),
            ("previous_frame_digest", self.previous_frame_digest),
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
            b"seq": self.sequence,
            b"prev": self.previous_frame_digest,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"hard_negatives": self.hard_negative_count,
            b"family": self.family_id,
            b"path_family": self.path_family,
            b"signer": self.signer_public_key,
        }

    def signature_payload(self) -> bytes:
        return HANDLER_REPLAY_DOMAIN + b":frame-sig:" + bencode(self.unsigned_bvalue())

    @property
    def frame_core_digest(self) -> bytes:
        return sha256(HANDLER_REPLAY_DOMAIN + b":frame-core:" + bencode(self.unsigned_bvalue()))

    @property
    def frame_digest(self) -> bytes:
        return sha256(HANDLER_REPLAY_DOMAIN + b":frame-digest:" + self.signature_payload() + self.signature)

    def verifies(self) -> bool:
        return verify_signature(self.signer_public_key, self.signature_payload(), self.signature)

    def live(self, now: int) -> bool:
        return self.issued_at <= now < self.expires_at


@dataclass(frozen=True)
class HandlerReplayReport:
    decision_kind: HandlerReplayDecisionKind
    accept: bool
    watch: bool
    reason: str
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    required_lanes: tuple[ReplayLane, ...]
    observed_lanes: tuple[ReplayLane, ...]
    accepted_frame_digest: bytes
    frame_digests: tuple[bytes, ...]
    component_digests: tuple[bytes, ...]
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
    raise ValueError("component report lacks 32-byte digest")


def _accept(report: Any | None) -> bool:
    return bool(getattr(report, "accept", False)) if report is not None else False


def _watch(report: Any | None) -> bool:
    return bool(getattr(report, "watch", False)) if report is not None else False


def _quarantined(report: Any | None) -> bool:
    return bool(getattr(report, "quarantined", False)) if report is not None else False


def make_handler_replay_frame(
    *,
    keypair: DhtKeypair,
    lane: ReplayLane,
    profile_id: str,
    service_name: str,
    scope_digest: bytes,
    request_digest: bytes,
    component_report: Any,
    sequence: int,
    previous_frame_digest: bytes = ZERO_DIGEST,
    issued_at: int,
    expires_at: int,
    hard_negative_count: int = 0,
    family_id: str,
    path_family: str,
) -> HandlerReplayFrame:
    unsigned = HandlerReplayFrame(
        lane=lane,
        profile_id=profile_id,
        service_name=service_name,
        scope_digest=scope_digest,
        request_digest=request_digest,
        component_report_digest=_digest(component_report),
        sequence=sequence,
        previous_frame_digest=previous_frame_digest,
        issued_at=issued_at,
        expires_at=expires_at,
        hard_negative_count=hard_negative_count,
        family_id=family_id,
        path_family=path_family,
        signer_public_key=keypair.public_key_bytes,
    )
    return replace(unsigned, signature=keypair.sign(unsigned.signature_payload()))


def assess_handler_replay(
    frames: Iterable[HandlerReplayFrame],
    *,
    component_reports: dict[ReplayLane, Any],
    now: int,
    expected_profile_id: str,
    expected_service_name: str,
    expected_scope_digest: bytes,
    expected_request_digest: bytes,
    required_lanes: Iterable[ReplayLane] = (ReplayLane.HANDLER_CAPSULE, ReplayLane.SIDE_EFFECT_JOURNAL),
    previous_seen_frame_digests: Iterable[bytes] = (),
    highest_seen_sequence: int | None = None,
    allow_component_watch: bool = False,
    min_family_count: int = 2,
    min_path_family_count: int = 2,
) -> HandlerReplayReport:
    frame_t = tuple(frames)
    required = tuple(ReplayLane(lane) for lane in required_lanes)
    components = {ReplayLane(lane): report for lane, report in component_reports.items()}
    component_digests = tuple(_digest(components.get(lane)) for lane in required)
    common = dict(profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, required_lanes=required, component_digests=component_digests)
    if not frame_t:
        return _report(HandlerReplayDecisionKind.EMPTY_NO_FRAMES, False, False, "handler replay needs frames", frames=frame_t, **common)
    for lane in required:
        report = components.get(lane)
        if not _accept(report) or _quarantined(report):
            return _report(HandlerReplayDecisionKind.QUARANTINE_COMPONENT_NOT_ACCEPTED, False, False, f"required component {lane.value} did not accept", frames=frame_t, **common)
    if any(_watch(components.get(lane)) for lane in required) and not allow_component_watch:
        return _report(HandlerReplayDecisionKind.HOLD_COMPONENT_WATCH, False, True, "component watch pressure must be carried across restart", frames=frame_t, **common)

    seen = set(previous_seen_frame_digests)
    by_sequence: dict[int, HandlerReplayFrame] = {}
    observed: set[ReplayLane] = set()
    for frame in frame_t:
        if not frame.verifies():
            return _report(HandlerReplayDecisionKind.QUARANTINE_BAD_SIGNATURE, False, False, "bad replay frame signature", frames=frame_t, **common)
        if not frame.live(now):
            return _report(HandlerReplayDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, False, False, "expired or future replay frame", frames=frame_t, **common)
        if frame.frame_digest in seen:
            return _report(HandlerReplayDecisionKind.QUARANTINE_REPLAY, False, False, "replay frame already seen", frames=frame_t, **common)
        if highest_seen_sequence is not None and frame.sequence < highest_seen_sequence:
            return _report(HandlerReplayDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, False, "replay sequence rollback", frames=frame_t, **common)
        prior = by_sequence.get(frame.sequence)
        if prior is not None and prior.frame_core_digest != frame.frame_core_digest:
            return _report(HandlerReplayDecisionKind.QUARANTINE_SEQUENCE_FORK, False, False, "same-sequence replay fork", frames=frame_t, **common)
        by_sequence[frame.sequence] = frame
        observed.add(frame.lane)
        if frame.profile_id != expected_profile_id:
            return _report(HandlerReplayDecisionKind.QUARANTINE_PROFILE_DRIFT, False, False, "profile drift", frames=frame_t, **common)
        if frame.service_name != expected_service_name:
            return _report(HandlerReplayDecisionKind.QUARANTINE_SERVICE_DRIFT, False, False, "service drift", frames=frame_t, **common)
        if frame.scope_digest != expected_scope_digest:
            return _report(HandlerReplayDecisionKind.QUARANTINE_SCOPE_DRIFT, False, False, "scope drift", frames=frame_t, **common)
        if frame.request_digest != expected_request_digest:
            return _report(HandlerReplayDecisionKind.QUARANTINE_REQUEST_DRIFT, False, False, "request drift", frames=frame_t, **common)
        expected_component = _digest(components.get(frame.lane))
        if expected_component == ZERO_DIGEST or frame.component_report_digest != expected_component:
            return _report(HandlerReplayDecisionKind.QUARANTINE_COMPONENT_DIGEST_DRIFT, False, False, "component digest drift", frames=frame_t, **common)
        if frame.hard_negative_count:
            return _report(HandlerReplayDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, "hard negatives block replay acceptance", frames=frame_t, **common)
    missing = tuple(lane for lane in required if lane not in observed)
    if missing:
        return _report(HandlerReplayDecisionKind.HOLD_MISSING_LANES, False, True, "missing required replay lanes", frames=frame_t, **common)
    ordered = sorted(by_sequence.values(), key=lambda item: item.sequence)
    for left, right in zip(ordered, ordered[1:]):
        if right.sequence == left.sequence + 1 and right.previous_frame_digest != left.frame_digest:
            return _report(HandlerReplayDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, False, "replay previous-link mismatch", frames=frame_t, **common)
    families = {frame.family_id for frame in frame_t}
    paths = {frame.path_family for frame in frame_t}
    if len(families) < min_family_count:
        return _report(HandlerReplayDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, "replay needs more family diversity", frames=frame_t, **common)
    if len(paths) < min_path_family_count:
        return _report(HandlerReplayDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, "replay needs more path diversity", frames=frame_t, **common)
    if any(_watch(components.get(lane)) for lane in required):
        return _report(HandlerReplayDecisionKind.ACCEPT_WITH_WATCH, True, True, "replay window accepted with watch", accepted=ordered[-1], frames=frame_t, **common)
    return _report(HandlerReplayDecisionKind.ACCEPT_REPLAY_WINDOW, True, False, "handler replay window accepted", accepted=ordered[-1], frames=frame_t, **common)


def _report(
    kind: HandlerReplayDecisionKind,
    accept: bool,
    watch: bool,
    reason: str,
    *,
    profile_id: str,
    service_name: str,
    scope_digest: bytes,
    request_digest: bytes,
    required_lanes: tuple[ReplayLane, ...],
    component_digests: tuple[bytes, ...],
    frames: Iterable[HandlerReplayFrame],
    accepted: HandlerReplayFrame | None = None,
) -> HandlerReplayReport:
    frame_t = tuple(frames)
    observed = tuple(sorted({frame.lane for frame in frame_t}, key=lambda item: item.value))
    digests = tuple(frame.frame_digest for frame in frame_t)
    families = {frame.family_id for frame in frame_t}
    paths = {frame.path_family for frame in frame_t}
    highest = max((frame.sequence for frame in frame_t), default=-1)
    hard = sum(frame.hard_negative_count for frame in frame_t)
    accepted_digest = accepted.frame_digest if accepted else ZERO_DIGEST
    digest = sha256(HANDLER_REPLAY_DOMAIN + b":report:" + bencode({
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
        b"frames": list(digests),
        b"components": list(component_digests),
        b"families": len(families),
        b"paths": len(paths),
        b"highest": highest,
        b"hard": hard,
    }))
    return HandlerReplayReport(kind, accept, watch, reason, profile_id, service_name, scope_digest, request_digest, required_lanes, observed, accepted_digest, digests, component_digests, highest, len(families), len(paths), hard, digest)
