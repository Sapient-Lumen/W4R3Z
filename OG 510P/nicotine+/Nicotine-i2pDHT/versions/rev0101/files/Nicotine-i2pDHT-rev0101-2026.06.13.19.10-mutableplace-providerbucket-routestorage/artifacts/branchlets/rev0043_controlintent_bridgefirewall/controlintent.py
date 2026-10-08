"""Profile-level control-intent join pressure.

rev0043 treats shared control-plane actions as joined local protocol data.  A
profile resume, public-bridge disable, operator-key transition, or router stop
must not advance because one component report looked good.  The action needs a
set of scoped, signed, fresh signals that all bind to the same profile, service,
scope, request, and action.

This is intentionally a no-network local reducer.  It does not authorize real
router side effects; it makes the exact join boundary executable before such
side effects exist.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256

CONTROL_INTENT_DOMAIN = DOMAIN + b":control-intent-v1:"
ZERO_DIGEST = b"\x00" * 32


class ControlIntentAction(str, Enum):
    RESUME_PROFILE = "resume_profile"
    DISABLE_PUBLIC_BRIDGE = "disable_public_bridge"
    ROTATE_OPERATOR_KEY = "rotate_operator_key"
    STOP_BUNDLED_ROUTER = "stop_bundled_router"
    KEEP_GARDEN_ONLINE = "keep_garden_online"


class ControlSignalKind(str, Enum):
    OPERATOR_INTENT = "operator_intent"
    MULTISERVICE = "multiservice"
    PROFILE_COOLDOWN = "profile_cooldown"
    OPERATOR_KEY = "operator_key"
    ANNOUNCEMENT_REPAIR = "announcement_repair"
    ROUTER_HARNESS = "router_harness"
    HARD_NEGATIVE_SCAN = "hard_negative_scan"
    EXIT_JOURNAL = "exit_journal"


class ControlIntentDecisionKind(str, Enum):
    ACCEPT_JOINED_CONTROL_INTENT = "accept_joined_control_intent"
    HOLD_MISSING_REQUIRED_SIGNAL = "hold_missing_required_signal"
    HOLD_SIGNAL_NOT_ACCEPTED = "hold_signal_not_accepted"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_HARD_NEGATIVE_PRESENT = "hold_hard_negative_present"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_EXPIRED_OR_FUTURE = "quarantine_expired_or_future"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_ACTION_DRIFT = "quarantine_action_drift"
    QUARANTINE_PROFILE_DRIFT = "quarantine_profile_drift"
    QUARANTINE_SERVICE_DRIFT = "quarantine_service_drift"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_REQUEST_DRIFT = "quarantine_request_drift"


@dataclass(frozen=True)
class ControlIntentSignal:
    kind: ControlSignalKind
    action: ControlIntentAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    sequence: int
    report_digest: bytes
    accepted: bool
    hard_negative_clear: bool
    family_id: str
    path_family: str
    issued_at: int
    expires_at: int
    signer_public_key: bytes
    signature: bytes = b""

    def __post_init__(self) -> None:
        if not self.profile_id or len(self.profile_id.encode("utf-8")) > 80:
            raise ValueError("profile_id must be short and non-empty")
        if not self.service_name or len(self.service_name.encode("utf-8")) > 80:
            raise ValueError("service_name must be short and non-empty")
        if not self.family_id or not self.path_family:
            raise ValueError("signal needs family and path-family labels")
        if self.sequence < 0:
            raise ValueError("control signal sequence must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("control signal expires_at must be after issued_at")
        for name, value in (
            ("scope_digest", self.scope_digest),
            ("request_digest", self.request_digest),
            ("report_digest", self.report_digest),
            ("signer_public_key", self.signer_public_key),
        ):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if self.signature and len(self.signature) != 64:
            raise ValueError("control intent signature must be Ed25519-sized")

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"kind": self.kind.value,
            b"action": self.action.value,
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"seq": self.sequence,
            b"report": self.report_digest,
            b"accepted": 1 if self.accepted else 0,
            b"hard_negative_clear": 1 if self.hard_negative_clear else 0,
            b"family": self.family_id,
            b"path_family": self.path_family,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"signer": self.signer_public_key,
        }

    @property
    def signal_digest(self) -> bytes:
        return sha256(CONTROL_INTENT_DOMAIN + b":signal:" + bencode(self.unsigned_bvalue()))

    def signature_payload(self) -> bytes:
        return CONTROL_INTENT_DOMAIN + b":sig:" + bencode(self.unsigned_bvalue())

    def verifies(self) -> bool:
        return verify_signature(self.signer_public_key, self.signature_payload(), self.signature)


def make_control_intent_signal(
    *,
    keypair: DhtKeypair,
    kind: ControlSignalKind,
    action: ControlIntentAction,
    profile_id: str,
    service_name: str,
    scope_digest: bytes,
    request_digest: bytes,
    sequence: int,
    report_digest: bytes,
    accepted: bool = True,
    hard_negative_clear: bool = True,
    family_id: str,
    path_family: str,
    issued_at: int,
    expires_at: int,
) -> ControlIntentSignal:
    signal = ControlIntentSignal(
        kind=kind,
        action=action,
        profile_id=profile_id,
        service_name=service_name,
        scope_digest=scope_digest,
        request_digest=request_digest,
        sequence=sequence,
        report_digest=report_digest,
        accepted=accepted,
        hard_negative_clear=hard_negative_clear,
        family_id=family_id,
        path_family=path_family,
        issued_at=issued_at,
        expires_at=expires_at,
        signer_public_key=keypair.public_key_bytes,
    )
    return replace(signal, signature=keypair.sign(signal.signature_payload()))


@dataclass(frozen=True)
class ControlIntentPolicy:
    required_signals: tuple[ControlSignalKind, ...]
    min_family_diversity: int = 2
    min_path_diversity: int = 2
    require_all_hard_negative_clear: bool = True

    def __post_init__(self) -> None:
        if not self.required_signals:
            raise ValueError("control intent policy needs at least one required signal")
        if len(set(self.required_signals)) != len(self.required_signals):
            raise ValueError("control intent required signals must be unique")
        if self.min_family_diversity < 1 or self.min_path_diversity < 1:
            raise ValueError("diversity requirements must be positive")


@dataclass(frozen=True)
class ControlIntentJoinReport:
    decision_kind: ControlIntentDecisionKind
    accept: bool
    reason: str
    action: ControlIntentAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    present_signals: tuple[str, ...]
    signal_digests: tuple[bytes, ...]
    pressure_digests: tuple[bytes, ...]
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


_DEFAULT_POLICY_BY_ACTION: dict[ControlIntentAction, ControlIntentPolicy] = {
    ControlIntentAction.RESUME_PROFILE: ControlIntentPolicy((ControlSignalKind.OPERATOR_INTENT, ControlSignalKind.PROFILE_COOLDOWN, ControlSignalKind.ROUTER_HARNESS, ControlSignalKind.HARD_NEGATIVE_SCAN), min_family_diversity=3, min_path_diversity=2),
    ControlIntentAction.DISABLE_PUBLIC_BRIDGE: ControlIntentPolicy((ControlSignalKind.OPERATOR_INTENT, ControlSignalKind.MULTISERVICE, ControlSignalKind.ANNOUNCEMENT_REPAIR, ControlSignalKind.HARD_NEGATIVE_SCAN), min_family_diversity=3, min_path_diversity=2),
    ControlIntentAction.ROTATE_OPERATOR_KEY: ControlIntentPolicy((ControlSignalKind.OPERATOR_INTENT, ControlSignalKind.OPERATOR_KEY, ControlSignalKind.EXIT_JOURNAL, ControlSignalKind.HARD_NEGATIVE_SCAN), min_family_diversity=3, min_path_diversity=2),
    ControlIntentAction.STOP_BUNDLED_ROUTER: ControlIntentPolicy((ControlSignalKind.OPERATOR_INTENT, ControlSignalKind.MULTISERVICE, ControlSignalKind.ROUTER_HARNESS, ControlSignalKind.EXIT_JOURNAL), min_family_diversity=3, min_path_diversity=2),
    ControlIntentAction.KEEP_GARDEN_ONLINE: ControlIntentPolicy((ControlSignalKind.MULTISERVICE, ControlSignalKind.PROFILE_COOLDOWN, ControlSignalKind.ROUTER_HARNESS), min_family_diversity=2, min_path_diversity=2),
}


def default_policy_for_action(action: ControlIntentAction) -> ControlIntentPolicy:
    return _DEFAULT_POLICY_BY_ACTION[action]


def _report(kind: ControlIntentDecisionKind, accept: bool, reason: str, *, action: ControlIntentAction, profile_id: str, service_name: str, scope_digest: bytes, request_digest: bytes, signals: Iterable[ControlIntentSignal], pressures: Iterable[bytes] = ()) -> ControlIntentJoinReport:
    sigs = tuple(sorted(signals, key=lambda item: (item.kind.value, item.sequence, item.signal_digest)))
    digests = tuple(sorted(item.signal_digest for item in sigs))
    pressure_t = tuple(sorted(set(pressures)))
    present = tuple(sorted({item.kind.value for item in sigs}))
    digest = sha256(CONTROL_INTENT_DOMAIN + b":join-report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"reason": reason,
        b"action": action.value,
        b"profile": profile_id,
        b"service": service_name,
        b"scope": scope_digest,
        b"request": request_digest,
        b"present": list(present),
        b"signals": list(digests),
        b"pressures": list(pressure_t),
    }))
    return ControlIntentJoinReport(kind, accept, reason, action, profile_id, service_name, scope_digest, request_digest, present, digests, pressure_t, digest)


def assess_control_intent_join(
    signals: Iterable[ControlIntentSignal],
    *,
    now: int,
    action: ControlIntentAction,
    expected_profile_id: str,
    expected_service_name: str,
    expected_scope_digest: bytes,
    expected_request_digest: bytes,
    policy: ControlIntentPolicy | None = None,
    previously_seen_signals: Iterable[bytes] = (),
) -> ControlIntentJoinReport:
    """Join scoped control-plane signals before sticky control state advances."""
    if len(expected_scope_digest) != 32 or len(expected_request_digest) != 32:
        raise ValueError("expected scope/request digests must be 32 bytes")
    policy = policy or default_policy_for_action(action)
    sigs = tuple(sorted(signals, key=lambda item: (item.kind.value, item.sequence, item.signal_digest)))
    seen = set(previously_seen_signals)
    if any(not item.verifies() for item in sigs):
        return _report(ControlIntentDecisionKind.QUARANTINE_BAD_SIGNATURE, False, "control signal signature failed", action=action, profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, signals=sigs)
    if any(item.issued_at > now or item.expires_at <= now for item in sigs):
        return _report(ControlIntentDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, False, "control signal outside local time window", action=action, profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, signals=sigs)
    if any(item.signal_digest in seen for item in sigs):
        return _report(ControlIntentDecisionKind.QUARANTINE_REPLAY, False, "control signal replay", action=action, profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, signals=sigs)
    if any(item.action is not action for item in sigs):
        return _report(ControlIntentDecisionKind.QUARANTINE_ACTION_DRIFT, False, "control signal action drift", action=action, profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, signals=sigs, pressures=(action.value.encode("utf-8"),))
    if any(item.profile_id != expected_profile_id for item in sigs):
        return _report(ControlIntentDecisionKind.QUARANTINE_PROFILE_DRIFT, False, "control signal profile drift", action=action, profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, signals=sigs)
    if any(item.service_name != expected_service_name for item in sigs):
        return _report(ControlIntentDecisionKind.QUARANTINE_SERVICE_DRIFT, False, "control signal service drift", action=action, profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, signals=sigs)
    if any(item.scope_digest != expected_scope_digest for item in sigs):
        return _report(ControlIntentDecisionKind.QUARANTINE_SCOPE_DRIFT, False, "control signal scope drift", action=action, profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, signals=sigs)
    if any(item.request_digest != expected_request_digest for item in sigs):
        return _report(ControlIntentDecisionKind.QUARANTINE_REQUEST_DRIFT, False, "control signal request drift", action=action, profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, signals=sigs)

    by_kind_sequence: dict[tuple[ControlSignalKind, int], set[bytes]] = {}
    for item in sigs:
        by_kind_sequence.setdefault((item.kind, item.sequence), set()).add(item.signal_digest)
    if any(len(digests) > 1 for digests in by_kind_sequence.values()):
        return _report(ControlIntentDecisionKind.QUARANTINE_SEQUENCE_FORK, False, "same-kind same-sequence control signal fork", action=action, profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, signals=sigs)

    present = {item.kind for item in sigs}
    missing = tuple(kind for kind in policy.required_signals if kind not in present)
    if missing:
        return _report(ControlIntentDecisionKind.HOLD_MISSING_REQUIRED_SIGNAL, False, "control intent missing required signal", action=action, profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, signals=sigs, pressures=tuple(kind.value.encode("utf-8") for kind in missing))
    required = tuple(item for item in sigs if item.kind in set(policy.required_signals))
    rejected = tuple(item for item in required if not item.accepted)
    if rejected:
        return _report(ControlIntentDecisionKind.HOLD_SIGNAL_NOT_ACCEPTED, False, "required control signal was not accepted", action=action, profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, signals=sigs, pressures=(rejected[0].signal_digest,))
    if policy.require_all_hard_negative_clear:
        dirty = tuple(item for item in required if not item.hard_negative_clear)
        if dirty:
            return _report(ControlIntentDecisionKind.HOLD_HARD_NEGATIVE_PRESENT, False, "control intent has live hard-negative pressure", action=action, profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, signals=sigs, pressures=(dirty[0].signal_digest,))
    families = {item.family_id for item in required}
    path_families = {item.path_family for item in required}
    if len(families) < policy.min_family_diversity or len(path_families) < policy.min_path_diversity:
        return _report(ControlIntentDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, "control intent lacks required family/path diversity", action=action, profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, signals=sigs)
    return _report(ControlIntentDecisionKind.ACCEPT_JOINED_CONTROL_INTENT, True, "joined control intent accepted at exact profile/service/scope/request boundary", action=action, profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, signals=sigs)
