"""Subjective policy firebreak for DHT/garden authority side effects.

rev0044 makes maintainer/garden/local policy explicit without letting policy
become DHT truth. A scoped policy capsule can deny, warn, allow, or require
watch for a key/action, but the side effect only advances when exact local
signals agree at the same profile, scope, request, action, and subject-key
boundary.

This is toy Python design code. It signs and validates small capsules so tests
can pin the hard guesses before any production keystore or live I2P transport
exists.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256

POLICY_FIREBREAK_DOMAIN = DOMAIN + b":policy-firebreak-v1:"
ZERO_DIGEST = b"\x00" * 32


class PolicyAction(str, Enum):
    PUBLIC_BRIDGE = "public_bridge"
    PRIVATE_GARDEN = "private_garden"
    DISABLE_PUBLIC_BRIDGE = "disable_public_bridge"
    RESUME_PROFILE = "resume_profile"
    SERVICE_TICKET = "service_ticket"
    MUTABLE_PUBLISH = "mutable_publish"


class PolicyDisposition(str, Enum):
    ALLOW = "allow"
    WARN = "warn"
    REQUIRE_WATCH = "require_watch"
    DENY = "deny"


class FirebreakSignalKind(str, Enum):
    KEY_COMPARTMENT = "key_compartment"
    AUTHORITY_SPLIT = "authority_split"
    CONTROL_INTENT = "control_intent"
    BRIDGE_FIREWALL = "bridge_firewall"
    KEY_CRISIS_SCAN = "key_crisis_scan"
    HARD_NEGATIVE_SCAN = "hard_negative_scan"


class PolicyFirebreakDecisionKind(str, Enum):
    ACCEPT_POLICY_FIREBREAK = "accept_policy_firebreak"
    ACCEPT_WITH_WATCH = "accept_with_watch"
    HOLD_MISSING_POLICY = "hold_missing_policy"
    HOLD_MISSING_SIGNAL = "hold_missing_signal"
    HOLD_SIGNAL_NOT_ACCEPTED = "hold_signal_not_accepted"
    HOLD_POLICY_WATCH = "hold_policy_watch"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_EXPIRED_OR_FUTURE = "quarantine_expired_or_future"
    QUARANTINE_PROFILE_DRIFT = "quarantine_profile_drift"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_REQUEST_DRIFT = "quarantine_request_drift"
    QUARANTINE_ACTION_DRIFT = "quarantine_action_drift"
    QUARANTINE_SUBJECT_DRIFT = "quarantine_subject_drift"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_ROLLBACK = "quarantine_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_POLICY_DENY = "quarantine_policy_deny"
    QUARANTINE_HARD_NEGATIVE = "quarantine_hard_negative"


@dataclass(frozen=True)
class SubjectivePolicyCapsule:
    authority_name: str
    profile_id: str
    action: PolicyAction
    subject_key_digest: bytes
    scope_digest: bytes
    sequence: int
    previous_policy_digest: bytes
    issued_at: int
    expires_at: int
    signer_public_key: bytes
    family_id: str
    path_family: str
    disposition: PolicyDisposition = PolicyDisposition.ALLOW
    reason: str = ""
    signature: bytes = b""

    def __post_init__(self) -> None:
        if not self.authority_name or len(self.authority_name.encode("utf-8")) > 80:
            raise ValueError("authority_name must be short and non-empty")
        if not self.profile_id or len(self.profile_id.encode("utf-8")) > 80:
            raise ValueError("profile_id must be short and non-empty")
        for name, value in (("subject_key_digest", self.subject_key_digest), ("scope_digest", self.scope_digest), ("previous_policy_digest", self.previous_policy_digest)):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if len(self.signer_public_key) != 32:
            raise ValueError("signer public key must be 32 bytes")
        if self.sequence < 0:
            raise ValueError("sequence must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("expires_at must be greater than issued_at")
        if not self.family_id or not self.path_family:
            raise ValueError("family_id and path_family must be non-empty")
        if len(self.reason.encode("utf-8")) > 160:
            raise ValueError("reason must be short")
        object.__setattr__(self, "action", PolicyAction(self.action))
        object.__setattr__(self, "disposition", PolicyDisposition(self.disposition))

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"authority": self.authority_name,
            b"profile": self.profile_id,
            b"action": self.action.value,
            b"subject": self.subject_key_digest,
            b"scope": self.scope_digest,
            b"seq": self.sequence,
            b"prev": self.previous_policy_digest,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"signer": self.signer_public_key,
            b"family": self.family_id,
            b"path_family": self.path_family,
            b"disposition": self.disposition.value,
            b"reason": self.reason,
        }

    def payload(self) -> bytes:
        return POLICY_FIREBREAK_DOMAIN + b":policy:" + bencode(self.unsigned_bvalue())

    @property
    def policy_digest(self) -> bytes:
        return sha256(POLICY_FIREBREAK_DOMAIN + b":policy-digest:" + self.payload() + self.signature)

    def verify(self) -> bool:
        return verify_signature(self.signer_public_key, self.payload(), self.signature)

    def with_signature(self, signature: bytes) -> "SubjectivePolicyCapsule":
        return replace(self, signature=signature)


@dataclass(frozen=True)
class FirebreakSignal:
    kind: FirebreakSignalKind
    profile_id: str
    action: PolicyAction
    subject_key_digest: bytes
    scope_digest: bytes
    request_digest: bytes
    sequence: int
    report_digest: bytes
    accepted: bool
    hard_negative_clear: bool
    issued_at: int
    expires_at: int
    signer_public_key: bytes
    family_id: str
    path_family: str
    public_exposure: bool = False
    signature: bytes = b""

    def __post_init__(self) -> None:
        if not self.profile_id or len(self.profile_id.encode("utf-8")) > 80:
            raise ValueError("profile_id must be short and non-empty")
        for name, value in (("subject_key_digest", self.subject_key_digest), ("scope_digest", self.scope_digest), ("request_digest", self.request_digest), ("report_digest", self.report_digest)):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if len(self.signer_public_key) != 32:
            raise ValueError("signer public key must be 32 bytes")
        if self.sequence < 0:
            raise ValueError("sequence must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("expires_at must be greater than issued_at")
        if not self.family_id or not self.path_family:
            raise ValueError("family_id and path_family must be non-empty")
        object.__setattr__(self, "kind", FirebreakSignalKind(self.kind))
        object.__setattr__(self, "action", PolicyAction(self.action))

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"kind": self.kind.value,
            b"profile": self.profile_id,
            b"action": self.action.value,
            b"subject": self.subject_key_digest,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"seq": self.sequence,
            b"report": self.report_digest,
            b"accepted": 1 if self.accepted else 0,
            b"clear": 1 if self.hard_negative_clear else 0,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"signer": self.signer_public_key,
            b"family": self.family_id,
            b"path_family": self.path_family,
            b"public": 1 if self.public_exposure else 0,
        }

    def payload(self) -> bytes:
        return POLICY_FIREBREAK_DOMAIN + b":signal:" + bencode(self.unsigned_bvalue())

    @property
    def signal_digest(self) -> bytes:
        return sha256(POLICY_FIREBREAK_DOMAIN + b":signal-digest:" + self.payload() + self.signature)

    def verify(self) -> bool:
        return verify_signature(self.signer_public_key, self.payload(), self.signature)

    def with_signature(self, signature: bytes) -> "FirebreakSignal":
        return replace(self, signature=signature)


@dataclass(frozen=True)
class PolicyFirebreakReport:
    decision_kind: PolicyFirebreakDecisionKind
    accepted: bool
    watch: bool
    subject_key_digest: bytes = ZERO_DIGEST
    accepted_policy_digest: bytes = ZERO_DIGEST
    accepted_signal_digests: tuple[bytes, ...] = ()
    family_count: int = 0
    path_family_count: int = 0
    reasons: tuple[str, ...] = ()
    report_digest: bytes = ZERO_DIGEST


def make_policy_capsule(
    *,
    keypair: DhtKeypair,
    authority_name: str,
    profile_id: str,
    action: PolicyAction,
    subject_key_digest: bytes,
    scope_digest: bytes,
    sequence: int,
    previous_policy_digest: bytes = ZERO_DIGEST,
    issued_at: int,
    expires_at: int,
    family_id: str,
    path_family: str,
    disposition: PolicyDisposition = PolicyDisposition.ALLOW,
    reason: str = "",
) -> SubjectivePolicyCapsule:
    capsule = SubjectivePolicyCapsule(
        authority_name=authority_name,
        profile_id=profile_id,
        action=action,
        subject_key_digest=subject_key_digest,
        scope_digest=scope_digest,
        sequence=sequence,
        previous_policy_digest=previous_policy_digest,
        issued_at=issued_at,
        expires_at=expires_at,
        signer_public_key=keypair.public_key_bytes,
        family_id=family_id,
        path_family=path_family,
        disposition=disposition,
        reason=reason,
    )
    return capsule.with_signature(keypair.sign(capsule.payload()))


def make_firebreak_signal(
    *,
    keypair: DhtKeypair,
    kind: FirebreakSignalKind,
    profile_id: str,
    action: PolicyAction,
    subject_key_digest: bytes,
    scope_digest: bytes,
    request_digest: bytes,
    sequence: int,
    report_digest: bytes,
    accepted: bool,
    hard_negative_clear: bool,
    issued_at: int,
    expires_at: int,
    family_id: str,
    path_family: str,
    public_exposure: bool = False,
) -> FirebreakSignal:
    signal = FirebreakSignal(
        kind=kind,
        profile_id=profile_id,
        action=action,
        subject_key_digest=subject_key_digest,
        scope_digest=scope_digest,
        request_digest=request_digest,
        sequence=sequence,
        report_digest=report_digest,
        accepted=accepted,
        hard_negative_clear=hard_negative_clear,
        issued_at=issued_at,
        expires_at=expires_at,
        signer_public_key=keypair.public_key_bytes,
        family_id=family_id,
        path_family=path_family,
        public_exposure=public_exposure,
    )
    return signal.with_signature(keypair.sign(signal.payload()))


def _report(kind: PolicyFirebreakDecisionKind, *, accepted: bool = False, watch: bool = False, subject_key_digest: bytes = ZERO_DIGEST, policy: SubjectivePolicyCapsule | None = None, signals: Iterable[FirebreakSignal] = (), family_count: int = 0, path_family_count: int = 0, reasons: Iterable[str] = ()) -> PolicyFirebreakReport:
    signal_tuple = tuple(signals)
    reason_tuple = tuple(reasons)
    policy_digest = policy.policy_digest if policy else ZERO_DIGEST
    signal_digests = tuple(signal.signal_digest for signal in signal_tuple)
    digest = sha256(POLICY_FIREBREAK_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accepted": 1 if accepted else 0,
        b"watch": 1 if watch else 0,
        b"subject": subject_key_digest,
        b"policy": policy_digest,
        b"signals": list(signal_digests),
        b"families": family_count,
        b"paths": path_family_count,
        b"reasons": list(reason_tuple),
    }))
    return PolicyFirebreakReport(kind, accepted, watch, subject_key_digest, policy_digest, signal_digests, family_count, path_family_count, reason_tuple, digest)


_REQUIRED_BY_ACTION: dict[PolicyAction, frozenset[FirebreakSignalKind]] = {
    PolicyAction.PUBLIC_BRIDGE: frozenset({FirebreakSignalKind.KEY_COMPARTMENT, FirebreakSignalKind.AUTHORITY_SPLIT, FirebreakSignalKind.CONTROL_INTENT, FirebreakSignalKind.BRIDGE_FIREWALL, FirebreakSignalKind.HARD_NEGATIVE_SCAN}),
    PolicyAction.PRIVATE_GARDEN: frozenset({FirebreakSignalKind.KEY_COMPARTMENT, FirebreakSignalKind.AUTHORITY_SPLIT, FirebreakSignalKind.HARD_NEGATIVE_SCAN}),
    PolicyAction.DISABLE_PUBLIC_BRIDGE: frozenset({FirebreakSignalKind.AUTHORITY_SPLIT, FirebreakSignalKind.CONTROL_INTENT, FirebreakSignalKind.BRIDGE_FIREWALL, FirebreakSignalKind.HARD_NEGATIVE_SCAN}),
    PolicyAction.RESUME_PROFILE: frozenset({FirebreakSignalKind.KEY_COMPARTMENT, FirebreakSignalKind.AUTHORITY_SPLIT, FirebreakSignalKind.CONTROL_INTENT, FirebreakSignalKind.KEY_CRISIS_SCAN, FirebreakSignalKind.HARD_NEGATIVE_SCAN}),
    PolicyAction.SERVICE_TICKET: frozenset({FirebreakSignalKind.KEY_COMPARTMENT, FirebreakSignalKind.AUTHORITY_SPLIT, FirebreakSignalKind.HARD_NEGATIVE_SCAN}),
    PolicyAction.MUTABLE_PUBLISH: frozenset({FirebreakSignalKind.KEY_COMPARTMENT, FirebreakSignalKind.AUTHORITY_SPLIT, FirebreakSignalKind.KEY_CRISIS_SCAN}),
}


def assess_policy_firebreak(
    policies: Iterable[SubjectivePolicyCapsule],
    signals: Iterable[FirebreakSignal],
    *,
    now: int,
    expected_profile_id: str,
    expected_action: PolicyAction,
    expected_subject_key_digest: bytes,
    expected_scope_digest: bytes,
    expected_request_digest: bytes,
    minimum_policy_sequence: int = 0,
    previous_policy_digest: bytes | None = None,
    min_signal_family_diversity: int = 3,
    min_signal_path_diversity: int = 2,
    allow_watch: bool = False,
    previously_seen_policy_digests: Iterable[bytes] = (),
    previously_seen_signal_digests: Iterable[bytes] = (),
) -> PolicyFirebreakReport:
    expected_action = PolicyAction(expected_action)
    if len(expected_subject_key_digest) != 32 or len(expected_scope_digest) != 32 or len(expected_request_digest) != 32:
        raise ValueError("expected digests must be 32 bytes")
    seen_policies = set(previously_seen_policy_digests)
    seen_signals = set(previously_seen_signal_digests)
    policy_list = tuple(policies)
    signal_list = tuple(signals)
    if not policy_list:
        return _report(PolicyFirebreakDecisionKind.HOLD_MISSING_POLICY, subject_key_digest=expected_subject_key_digest, reasons=("no_policy_capsules",))
    valid_policies: list[SubjectivePolicyCapsule] = []
    policy_by_seq: dict[int, bytes] = {}
    highest_seq = -1
    for policy in policy_list:
        if not policy.verify():
            return _report(PolicyFirebreakDecisionKind.QUARANTINE_BAD_SIGNATURE, subject_key_digest=expected_subject_key_digest, policy=policy, reasons=("policy_bad_signature",))
        if policy.issued_at > now or policy.expires_at <= now:
            return _report(PolicyFirebreakDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, subject_key_digest=expected_subject_key_digest, policy=policy, reasons=("policy_time_window",))
        if policy.profile_id != expected_profile_id:
            return _report(PolicyFirebreakDecisionKind.QUARANTINE_PROFILE_DRIFT, subject_key_digest=expected_subject_key_digest, policy=policy, reasons=("policy_profile_drift",))
        if policy.scope_digest != expected_scope_digest:
            return _report(PolicyFirebreakDecisionKind.QUARANTINE_SCOPE_DRIFT, subject_key_digest=expected_subject_key_digest, policy=policy, reasons=("policy_scope_drift",))
        if policy.action is not expected_action:
            return _report(PolicyFirebreakDecisionKind.QUARANTINE_ACTION_DRIFT, subject_key_digest=expected_subject_key_digest, policy=policy, reasons=("policy_action_drift",))
        if policy.subject_key_digest != expected_subject_key_digest:
            return _report(PolicyFirebreakDecisionKind.QUARANTINE_SUBJECT_DRIFT, subject_key_digest=expected_subject_key_digest, policy=policy, reasons=("policy_subject_drift",))
        if policy.policy_digest in seen_policies:
            return _report(PolicyFirebreakDecisionKind.QUARANTINE_REPLAY, subject_key_digest=expected_subject_key_digest, policy=policy, reasons=("policy_replay",))
        existing = policy_by_seq.setdefault(policy.sequence, policy.policy_digest)
        if existing != policy.policy_digest:
            return _report(PolicyFirebreakDecisionKind.QUARANTINE_SEQUENCE_FORK, subject_key_digest=expected_subject_key_digest, policy=policy, reasons=("policy_sequence_fork",))
        highest_seq = max(highest_seq, policy.sequence)
        valid_policies.append(policy)
    if highest_seq < minimum_policy_sequence:
        return _report(PolicyFirebreakDecisionKind.QUARANTINE_ROLLBACK, subject_key_digest=expected_subject_key_digest, reasons=("policy_rollback",))
    latest = max(valid_policies, key=lambda item: (item.sequence, item.issued_at, item.policy_digest))
    if previous_policy_digest is not None and latest.sequence > 0 and latest.previous_policy_digest != previous_policy_digest:
        return _report(PolicyFirebreakDecisionKind.QUARANTINE_ROLLBACK, subject_key_digest=expected_subject_key_digest, policy=latest, reasons=("policy_previous_link_mismatch",))
    if latest.disposition is PolicyDisposition.DENY:
        return _report(PolicyFirebreakDecisionKind.QUARANTINE_POLICY_DENY, subject_key_digest=expected_subject_key_digest, policy=latest, reasons=(latest.reason or "policy_denies_action",))
    watch = latest.disposition in (PolicyDisposition.WARN, PolicyDisposition.REQUIRE_WATCH)
    if latest.disposition is PolicyDisposition.REQUIRE_WATCH and not allow_watch:
        return _report(PolicyFirebreakDecisionKind.HOLD_POLICY_WATCH, subject_key_digest=expected_subject_key_digest, policy=latest, reasons=(latest.reason or "policy_requires_watch",))
    if not signal_list:
        return _report(PolicyFirebreakDecisionKind.HOLD_MISSING_SIGNAL, subject_key_digest=expected_subject_key_digest, policy=latest, reasons=("no_firebreak_signals",))
    valid_signals: list[FirebreakSignal] = []
    signal_by_kind_seq: dict[tuple[FirebreakSignalKind, int], bytes] = {}
    for signal in signal_list:
        if not signal.verify():
            return _report(PolicyFirebreakDecisionKind.QUARANTINE_BAD_SIGNATURE, subject_key_digest=expected_subject_key_digest, policy=latest, signals=(signal,), reasons=("signal_bad_signature",))
        if signal.issued_at > now or signal.expires_at <= now:
            return _report(PolicyFirebreakDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, subject_key_digest=expected_subject_key_digest, policy=latest, signals=(signal,), reasons=("signal_time_window",))
        if signal.signal_digest in seen_signals:
            return _report(PolicyFirebreakDecisionKind.QUARANTINE_REPLAY, subject_key_digest=expected_subject_key_digest, policy=latest, signals=(signal,), reasons=("signal_replay",))
        if signal.profile_id != expected_profile_id:
            return _report(PolicyFirebreakDecisionKind.QUARANTINE_PROFILE_DRIFT, subject_key_digest=expected_subject_key_digest, policy=latest, signals=(signal,), reasons=("signal_profile_drift",))
        if signal.scope_digest != expected_scope_digest:
            return _report(PolicyFirebreakDecisionKind.QUARANTINE_SCOPE_DRIFT, subject_key_digest=expected_subject_key_digest, policy=latest, signals=(signal,), reasons=("signal_scope_drift",))
        if signal.request_digest != expected_request_digest:
            return _report(PolicyFirebreakDecisionKind.QUARANTINE_REQUEST_DRIFT, subject_key_digest=expected_subject_key_digest, policy=latest, signals=(signal,), reasons=("signal_request_drift",))
        if signal.action is not expected_action:
            return _report(PolicyFirebreakDecisionKind.QUARANTINE_ACTION_DRIFT, subject_key_digest=expected_subject_key_digest, policy=latest, signals=(signal,), reasons=("signal_action_drift",))
        if signal.subject_key_digest != expected_subject_key_digest:
            return _report(PolicyFirebreakDecisionKind.QUARANTINE_SUBJECT_DRIFT, subject_key_digest=expected_subject_key_digest, policy=latest, signals=(signal,), reasons=("signal_subject_drift",))
        key = (signal.kind, signal.sequence)
        existing = signal_by_kind_seq.setdefault(key, signal.signal_digest)
        if existing != signal.signal_digest:
            return _report(PolicyFirebreakDecisionKind.QUARANTINE_SEQUENCE_FORK, subject_key_digest=expected_subject_key_digest, policy=latest, signals=(signal,), reasons=("signal_sequence_fork",))
        if not signal.accepted:
            return _report(PolicyFirebreakDecisionKind.HOLD_SIGNAL_NOT_ACCEPTED, subject_key_digest=expected_subject_key_digest, policy=latest, signals=(signal,), reasons=(f"{signal.kind.value}_not_accepted",))
        if not signal.hard_negative_clear:
            return _report(PolicyFirebreakDecisionKind.QUARANTINE_HARD_NEGATIVE, subject_key_digest=expected_subject_key_digest, policy=latest, signals=(signal,), reasons=(f"{signal.kind.value}_hard_negative",))
        valid_signals.append(signal)
    present = {signal.kind for signal in valid_signals}
    required = _REQUIRED_BY_ACTION[expected_action]
    missing = sorted(kind.value for kind in required - present)
    if missing:
        return _report(PolicyFirebreakDecisionKind.HOLD_MISSING_SIGNAL, subject_key_digest=expected_subject_key_digest, policy=latest, signals=valid_signals, reasons=("missing:" + ",".join(missing),))
    families = {signal.family_id for signal in valid_signals if signal.kind in required}
    paths = {signal.path_family for signal in valid_signals if signal.kind in required}
    if len(families) < min_signal_family_diversity:
        return _report(PolicyFirebreakDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, subject_key_digest=expected_subject_key_digest, policy=latest, signals=valid_signals, family_count=len(families), path_family_count=len(paths), reasons=("signal_family_diversity",))
    if len(paths) < min_signal_path_diversity:
        return _report(PolicyFirebreakDecisionKind.HOLD_LOW_PATH_DIVERSITY, subject_key_digest=expected_subject_key_digest, policy=latest, signals=valid_signals, family_count=len(families), path_family_count=len(paths), reasons=("signal_path_diversity",))
    kind = PolicyFirebreakDecisionKind.ACCEPT_WITH_WATCH if watch else PolicyFirebreakDecisionKind.ACCEPT_POLICY_FIREBREAK
    return _report(kind, accepted=True, watch=watch, subject_key_digest=expected_subject_key_digest, policy=latest, signals=valid_signals, family_count=len(families), path_family_count=len(paths), reasons=(latest.reason,) if latest.reason else ())
