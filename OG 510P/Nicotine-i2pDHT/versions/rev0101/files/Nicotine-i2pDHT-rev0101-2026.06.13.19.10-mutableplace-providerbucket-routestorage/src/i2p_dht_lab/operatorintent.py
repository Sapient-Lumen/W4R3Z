"""Operator intent capsules for garden service operation.

rev0040 treats manual/operator control as a protocol boundary, not as an
escape hatch.  A garden operator may need to pause, demote, freeze, disable a
bridge surface, or resume a service, but that local intent must be scoped,
sequenced, restart-aware, and checked before it can authorize service side
effects.  This is deliberately a toy local surface: signatures are deterministic
lab digests, not production cryptography.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .ids import DOMAIN, sha256

OPERATOR_INTENT_DOMAIN = DOMAIN + b":operator-intent-v1:"
ZERO_DIGEST = b"\x00" * 32


class OperatorIntentAction(str, Enum):
    PAUSE_SERVICE = "pause_service"
    RESUME_SERVICE = "resume_service"
    DEMOTE_TO_LEAF = "demote_to_leaf"
    DISABLE_BRIDGE = "disable_bridge"
    ENTER_MAINTENANCE = "enter_maintenance"
    EMERGENCY_FREEZE = "emergency_freeze"


class OperatorIntentDecisionKind(str, Enum):
    ACCEPT_INTENT = "accept_intent"
    ACCEPT_EMERGENCY_HOLD = "accept_emergency_hold"
    HOLD_NO_INTENT = "hold_no_intent"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_EXPIRED_OR_FUTURE = "quarantine_expired_or_future"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_PROFILE_DRIFT = "quarantine_profile_drift"
    QUARANTINE_ACTION_NOT_ALLOWED = "quarantine_action_not_allowed"
    QUARANTINE_BRIDGE_ACTION_NOT_EXPLICIT = "quarantine_bridge_action_not_explicit"


@dataclass(frozen=True)
class OperatorIntentCapsule:
    action: OperatorIntentAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    sequence: int
    previous_intent_digest: bytes
    reason_digest: bytes
    operator_key: bytes
    issued_at: int
    expires_at: int
    bridge_public: bool = False
    signature: bytes = b""

    def __post_init__(self) -> None:
        if not self.profile_id or len(self.profile_id.encode("utf-8")) > 80:
            raise ValueError("profile_id must be short and non-empty")
        if not self.service_name or len(self.service_name.encode("utf-8")) > 80:
            raise ValueError("service_name must be short and non-empty")
        if self.sequence < 0:
            raise ValueError("intent sequence must be non-negative")
        for name, value in (
            ("scope_digest", self.scope_digest),
            ("request_digest", self.request_digest),
            ("previous_intent_digest", self.previous_intent_digest),
            ("reason_digest", self.reason_digest),
            ("operator_key", self.operator_key),
        ):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if self.expires_at <= self.issued_at:
            raise ValueError("intent expires_at must be after issued_at")
        if self.signature and len(self.signature) != 32:
            raise ValueError("toy intent signature must be 32 bytes")

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"action": self.action.value,
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"seq": self.sequence,
            b"prev": self.previous_intent_digest,
            b"reason": self.reason_digest,
            b"operator": self.operator_key,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"bridge_public": 1 if self.bridge_public else 0,
        }

    @property
    def intent_digest(self) -> bytes:
        return sha256(OPERATOR_INTENT_DOMAIN + b":digest:" + bencode(self.unsigned_bvalue()))

    def signed_bvalue(self) -> dict[bytes, BValue]:
        value = dict(self.unsigned_bvalue())
        value[b"sig"] = self.signature
        return value

    def expected_signature(self) -> bytes:
        return sha256(OPERATOR_INTENT_DOMAIN + b":sig:" + bencode(self.unsigned_bvalue()) + self.operator_key)

    def with_signature(self) -> "OperatorIntentCapsule":
        return replace(self, signature=self.expected_signature())

    def verifies(self) -> bool:
        return self.signature == self.expected_signature()


def make_operator_intent(
    *,
    action: OperatorIntentAction,
    profile_id: str,
    service_name: str,
    scope_digest: bytes,
    request_digest: bytes,
    sequence: int,
    previous_intent_digest: bytes = ZERO_DIGEST,
    reason_digest: bytes | None = None,
    operator_key: bytes,
    issued_at: int,
    expires_at: int,
    bridge_public: bool = False,
) -> OperatorIntentCapsule:
    return OperatorIntentCapsule(
        action=action,
        profile_id=profile_id,
        service_name=service_name,
        scope_digest=scope_digest,
        request_digest=request_digest,
        sequence=sequence,
        previous_intent_digest=previous_intent_digest,
        reason_digest=reason_digest or sha256(OPERATOR_INTENT_DOMAIN + b":no-reason"),
        operator_key=operator_key,
        issued_at=issued_at,
        expires_at=expires_at,
        bridge_public=bridge_public,
    ).with_signature()


@dataclass(frozen=True)
class OperatorIntentPolicy:
    allowed_actions: tuple[OperatorIntentAction, ...] = (
        OperatorIntentAction.PAUSE_SERVICE,
        OperatorIntentAction.RESUME_SERVICE,
        OperatorIntentAction.DEMOTE_TO_LEAF,
        OperatorIntentAction.DISABLE_BRIDGE,
        OperatorIntentAction.ENTER_MAINTENANCE,
        OperatorIntentAction.EMERGENCY_FREEZE,
    )
    require_bridge_bit_for_bridge_action: bool = True
    allow_resume: bool = True
    emergency_actions_hold_not_accept: bool = True


@dataclass(frozen=True)
class OperatorIntentReport:
    decision_kind: OperatorIntentDecisionKind
    accept: bool
    reason: str
    action: OperatorIntentAction | None
    profile_id: str | None
    service_name: str | None
    scope_digest: bytes | None
    request_digest: bytes | None
    highest_sequence: int
    intent_digests: tuple[bytes, ...]
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")

    @property
    def emergency_hold(self) -> bool:
        return self.decision_kind is OperatorIntentDecisionKind.ACCEPT_EMERGENCY_HOLD


def _report(
    kind: OperatorIntentDecisionKind,
    accept: bool,
    reason: str,
    intents: Iterable[OperatorIntentCapsule],
    *,
    action: OperatorIntentAction | None = None,
    profile_id: str | None = None,
    service_name: str | None = None,
    scope_digest: bytes | None = None,
    request_digest: bytes | None = None,
) -> OperatorIntentReport:
    intent_tuple = tuple(sorted(intents, key=lambda item: (item.sequence, item.intent_digest)))
    digests = tuple(sorted(item.intent_digest for item in intent_tuple))
    highest = max((item.sequence for item in intent_tuple), default=-1)
    digest = sha256(OPERATOR_INTENT_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"reason": reason,
        b"action": action.value if action else "",
        b"profile": profile_id or "",
        b"service": service_name or "",
        b"scope": scope_digest or b"",
        b"request": request_digest or b"",
        b"highest": highest,
        b"intents": list(digests),
    }))
    return OperatorIntentReport(kind, accept, reason, action, profile_id, service_name, scope_digest, request_digest, highest, digests, digest)


def assess_operator_intent(
    intents: Iterable[OperatorIntentCapsule],
    *,
    policy: OperatorIntentPolicy | None = None,
    now: int,
    expected_profile_id: str | None = None,
    expected_service_name: str | None = None,
    expected_scope_digest: bytes | None = None,
    expected_request_digest: bytes | None = None,
    previous_sequence: int | None = None,
    previous_intent_digest: bytes | None = None,
    previously_seen_intents: Iterable[bytes] = (),
) -> OperatorIntentReport:
    policy = policy or OperatorIntentPolicy()
    capsules = tuple(sorted(intents, key=lambda item: (item.sequence, item.intent_digest)))
    if not capsules:
        return _report(OperatorIntentDecisionKind.HOLD_NO_INTENT, False, "no operator intent", capsules)
    if any(not item.verifies() for item in capsules):
        return _report(OperatorIntentDecisionKind.QUARANTINE_BAD_SIGNATURE, False, "operator intent signature mismatch", capsules)
    if any(item.issued_at > now or item.expires_at <= now for item in capsules):
        return _report(OperatorIntentDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, False, "operator intent outside local time window", capsules)
    seen = set(previously_seen_intents)
    if any(item.intent_digest in seen for item in capsules):
        return _report(OperatorIntentDecisionKind.QUARANTINE_REPLAY, False, "operator intent replayed", capsules)
    if previous_sequence is not None and max(item.sequence for item in capsules) < previous_sequence:
        return _report(OperatorIntentDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, "operator intent sequence rolled back", capsules)
    by_sequence: dict[int, set[bytes]] = {}
    for item in capsules:
        by_sequence.setdefault(item.sequence, set()).add(item.intent_digest)
    if any(len(digests) > 1 for digests in by_sequence.values()):
        return _report(OperatorIntentDecisionKind.QUARANTINE_SEQUENCE_FORK, False, "operator intent sequence fork", capsules)
    if previous_intent_digest is not None:
        first = capsules[0]
        if first.sequence > 0 and first.previous_intent_digest != previous_intent_digest:
            return _report(OperatorIntentDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, "operator intent does not link to local previous digest", capsules)
    if expected_profile_id and any(item.profile_id != expected_profile_id for item in capsules):
        return _report(OperatorIntentDecisionKind.QUARANTINE_PROFILE_DRIFT, False, "operator intent profile drift", capsules)
    if expected_service_name and any(item.service_name != expected_service_name for item in capsules):
        return _report(OperatorIntentDecisionKind.QUARANTINE_SCOPE_DRIFT, False, "operator intent service drift", capsules)
    if expected_scope_digest and any(item.scope_digest != expected_scope_digest for item in capsules):
        return _report(OperatorIntentDecisionKind.QUARANTINE_SCOPE_DRIFT, False, "operator intent scope drift", capsules)
    if expected_request_digest and any(item.request_digest != expected_request_digest for item in capsules):
        return _report(OperatorIntentDecisionKind.QUARANTINE_SCOPE_DRIFT, False, "operator intent request drift", capsules)
    if any(item.action not in policy.allowed_actions for item in capsules):
        return _report(OperatorIntentDecisionKind.QUARANTINE_ACTION_NOT_ALLOWED, False, "operator intent action not allowed by local profile", capsules)
    if not policy.allow_resume and any(item.action is OperatorIntentAction.RESUME_SERVICE for item in capsules):
        return _report(OperatorIntentDecisionKind.QUARANTINE_ACTION_NOT_ALLOWED, False, "resume disabled by local policy", capsules)
    if policy.require_bridge_bit_for_bridge_action and any(item.action is OperatorIntentAction.DISABLE_BRIDGE and not item.bridge_public for item in capsules):
        return _report(OperatorIntentDecisionKind.QUARANTINE_BRIDGE_ACTION_NOT_EXPLICIT, False, "bridge action lacks explicit public-bridge binding", capsules)
    latest = capsules[-1]
    kind = OperatorIntentDecisionKind.ACCEPT_EMERGENCY_HOLD if latest.action is OperatorIntentAction.EMERGENCY_FREEZE and policy.emergency_actions_hold_not_accept else OperatorIntentDecisionKind.ACCEPT_INTENT
    return _report(kind, True, "operator intent accepted locally", capsules, action=latest.action, profile_id=latest.profile_id, service_name=latest.service_name, scope_digest=latest.scope_digest, request_digest=latest.request_digest)
