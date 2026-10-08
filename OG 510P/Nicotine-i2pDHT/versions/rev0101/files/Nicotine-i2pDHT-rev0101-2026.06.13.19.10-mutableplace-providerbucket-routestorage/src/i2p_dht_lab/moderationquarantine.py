"""Subjective moderation quarantine capsules.

rev0046 makes the uncomfortable maintainer/operator-policy surface explicit:
local builds, gardens, and public bridges may need to refuse a key, service, or
bridge exposure without pretending to rewrite DHT truth.  A moderation capsule
is therefore scoped policy evidence, not protocol consensus.  It can block local
side effects such as public bridge refreshes, require watch, or merely warn.

The lane is intentionally local and deterministic.  It signs compact capsules,
checks monotonic/replay/fork pressure, and exposes appeal/redress metadata for a
separate lane.  It does not ban a key from the DHT globally.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256

MODERATION_QUARANTINE_DOMAIN = DOMAIN + b":moderation-quarantine-v1:"
ZERO_DIGEST = b"\x00" * 32


class ModerationAction(str, Enum):
    PUBLIC_BRIDGE = "public_bridge"
    GARDEN_SERVICE = "garden_service"
    SEED_GATE = "seed_gate"
    ROUTE_GOSSIP = "route_gossip"
    EMERGENCY_HOLD = "emergency_hold"


class ModerationDisposition(str, Enum):
    WARN = "warn"
    WATCH = "watch"
    DENY = "deny"
    FREEZE = "freeze"


class ModerationDecisionKind(str, Enum):
    CLEAR_NO_ACTIVE_CAPSULE = "clear_no_active_capsule"
    ACCEPT_WARNING = "accept_warning"
    ACCEPT_WATCH = "accept_watch"
    ACCEPT_DENY = "accept_deny"
    ACCEPT_FREEZE = "accept_freeze"
    HOLD_WATCH_REQUIRES_EXPLICIT_ALLOWANCE = "hold_watch_requires_explicit_allowance"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_EXPIRED_OR_FUTURE = "quarantine_expired_or_future"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_PROFILE_DRIFT = "quarantine_profile_drift"
    QUARANTINE_SERVICE_DRIFT = "quarantine_service_drift"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_REQUEST_DRIFT = "quarantine_request_drift"
    QUARANTINE_SUBJECT_DRIFT = "quarantine_subject_drift"
    QUARANTINE_ACTION_DRIFT = "quarantine_action_drift"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"


_BLOCKING = {ModerationDisposition.DENY, ModerationDisposition.FREEZE}


@dataclass(frozen=True)
class QuarantineCapsule:
    authority_name: str
    action: ModerationAction
    disposition: ModerationDisposition
    profile_id: str
    service_name: str
    subject_key_digest: bytes
    scope_digest: bytes
    request_digest: bytes
    evidence_digest: bytes
    sequence: int
    previous_capsule_digest: bytes
    issued_at: int
    expires_at: int
    appeal_allowed: bool
    hard_negative_clear: bool
    public_exposure: bool
    family_id: str
    path_family: str
    signer_public_key: bytes
    reason_code: str = ""
    signature: bytes = b""

    def __post_init__(self) -> None:
        if not self.authority_name or len(self.authority_name.encode("utf-8")) > 96:
            raise ValueError("authority name must be short and non-empty")
        if not self.profile_id or len(self.profile_id.encode("utf-8")) > 80:
            raise ValueError("profile_id must be short and non-empty")
        if not self.service_name or len(self.service_name.encode("utf-8")) > 96:
            raise ValueError("service_name must be short and non-empty")
        if len(self.reason_code.encode("utf-8")) > 160:
            raise ValueError("reason code must be short")
        if self.sequence < 0:
            raise ValueError("moderation sequence must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("expires_at must be after issued_at")
        if not self.family_id or not self.path_family:
            raise ValueError("family_id and path_family must be non-empty")
        for name, value in (
            ("subject_key_digest", self.subject_key_digest),
            ("scope_digest", self.scope_digest),
            ("request_digest", self.request_digest),
            ("evidence_digest", self.evidence_digest),
            ("previous_capsule_digest", self.previous_capsule_digest),
            ("signer_public_key", self.signer_public_key),
        ):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if self.signature and len(self.signature) != 64:
            raise ValueError("signature must be Ed25519-sized")
        object.__setattr__(self, "action", ModerationAction(self.action))
        object.__setattr__(self, "disposition", ModerationDisposition(self.disposition))

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"authority": self.authority_name,
            b"action": self.action.value,
            b"disposition": self.disposition.value,
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"subject": self.subject_key_digest,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            # Exclude evidence_digest from the fork core so multiple families can
            # co-sign the same subjective action while attaching independent local evidence.
            b"seq": self.sequence,
            b"prev": self.previous_capsule_digest,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"appeal": 1 if self.appeal_allowed else 0,
            b"hard_clear": 1 if self.hard_negative_clear else 0,
            b"public": 1 if self.public_exposure else 0,
            b"family": self.family_id,
            b"path_family": self.path_family,
            b"signer": self.signer_public_key,
            b"reason": self.reason_code,
        }

    def signature_payload(self) -> bytes:
        return MODERATION_QUARANTINE_DOMAIN + b":capsule-sig:" + bencode(self.unsigned_bvalue())

    @property
    def capsule_core_digest(self) -> bytes:
        return sha256(MODERATION_QUARANTINE_DOMAIN + b":capsule-core:" + bencode({
            b"authority": self.authority_name,
            b"action": self.action.value,
            b"disposition": self.disposition.value,
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"subject": self.subject_key_digest,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            # Exclude evidence_digest from the fork core so multiple families can
            # co-sign the same subjective action while attaching independent local evidence.
            b"seq": self.sequence,
            b"prev": self.previous_capsule_digest,
            b"appeal": 1 if self.appeal_allowed else 0,
            b"hard_clear": 1 if self.hard_negative_clear else 0,
            b"public": 1 if self.public_exposure else 0,
            b"reason": self.reason_code,
        }))

    @property
    def capsule_digest(self) -> bytes:
        return sha256(MODERATION_QUARANTINE_DOMAIN + b":capsule-digest:" + self.signature_payload() + self.signature)

    def verifies(self) -> bool:
        return verify_signature(self.signer_public_key, self.signature_payload(), self.signature)


@dataclass(frozen=True)
class ModerationQuarantineReport:
    decision_kind: ModerationDecisionKind
    active: bool
    blocked: bool
    watch: bool
    reason: str
    profile_id: str
    service_name: str
    action: ModerationAction
    subject_key_digest: bytes
    capsule_digests: tuple[bytes, ...]
    family_count: int
    path_family_count: int
    highest_sequence: int
    appeal_allowed: bool
    accepted_capsule_digest: bytes
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")



def make_quarantine_capsule(
    *,
    keypair: DhtKeypair,
    authority_name: str,
    action: ModerationAction,
    disposition: ModerationDisposition,
    profile_id: str,
    service_name: str,
    subject_key_digest: bytes,
    scope_digest: bytes,
    request_digest: bytes,
    evidence_digest: bytes,
    sequence: int,
    previous_capsule_digest: bytes = ZERO_DIGEST,
    issued_at: int,
    expires_at: int,
    appeal_allowed: bool = True,
    hard_negative_clear: bool = True,
    public_exposure: bool = False,
    family_id: str,
    path_family: str,
    reason_code: str = "",
) -> QuarantineCapsule:
    capsule = QuarantineCapsule(authority_name, action, disposition, profile_id, service_name, subject_key_digest, scope_digest, request_digest, evidence_digest, sequence, previous_capsule_digest, issued_at, expires_at, appeal_allowed, hard_negative_clear, public_exposure, family_id, path_family, keypair.public_key_bytes, reason_code)
    return replace(capsule, signature=keypair.sign(capsule.signature_payload()))



def _report(kind: ModerationDecisionKind, active: bool, blocked: bool, watch: bool, reason: str, *, profile_id: str, service_name: str, action: ModerationAction, subject_key_digest: bytes, capsules: Iterable[QuarantineCapsule] = (), selected: QuarantineCapsule | None = None, family_count: int = 0, path_family_count: int = 0) -> ModerationQuarantineReport:
    capsule_tuple = tuple(sorted(capsules, key=lambda item: (item.sequence, item.capsule_digest)))
    digests = tuple(sorted(item.capsule_digest for item in capsule_tuple))
    highest = selected.sequence if selected else -1
    accepted = selected.capsule_digest if selected and active else ZERO_DIGEST
    appeal_allowed = selected.appeal_allowed if selected else False
    digest = sha256(MODERATION_QUARANTINE_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"active": 1 if active else 0,
        b"blocked": 1 if blocked else 0,
        b"watch": 1 if watch else 0,
        b"reason": reason,
        b"profile": profile_id,
        b"service": service_name,
        b"action": action.value,
        b"subject": subject_key_digest,
        b"capsules": list(digests),
        b"families": family_count,
        b"paths": path_family_count,
        b"highest": highest,
        b"appeal": 1 if appeal_allowed else 0,
        b"accepted": accepted,
    }))
    return ModerationQuarantineReport(kind, active, blocked, watch, reason, profile_id, service_name, action, subject_key_digest, digests, family_count, path_family_count, highest, appeal_allowed, accepted, digest)



def assess_moderation_quarantine(
    capsules: Iterable[QuarantineCapsule],
    *,
    now: int,
    expected_profile_id: str,
    expected_service_name: str,
    expected_subject_key_digest: bytes,
    expected_action: ModerationAction,
    expected_scope_digest: bytes,
    expected_request_digest: bytes,
    previous_sequence: int | None = None,
    previous_capsule_digest: bytes | None = None,
    previously_seen_capsules: Iterable[bytes] = (),
    min_family_diversity_for_block: int = 2,
    min_path_diversity_for_block: int = 2,
    allow_watch: bool = True,
) -> ModerationQuarantineReport:
    action = ModerationAction(expected_action)
    capsule_tuple = tuple(sorted(capsules, key=lambda item: (item.sequence, item.capsule_digest)))
    if not capsule_tuple:
        return _report(ModerationDecisionKind.CLEAR_NO_ACTIVE_CAPSULE, False, False, False, "no active local moderation capsule", profile_id=expected_profile_id, service_name=expected_service_name, action=action, subject_key_digest=expected_subject_key_digest)
    seen = set(previously_seen_capsules)
    families: set[str] = set()
    paths: set[str] = set()
    fork_guard: dict[int, bytes] = {}
    latest: QuarantineCapsule | None = None
    for capsule in capsule_tuple:
        if not capsule.verifies():
            return _report(ModerationDecisionKind.QUARANTINE_BAD_SIGNATURE, False, False, False, "bad moderation capsule signature", profile_id=expected_profile_id, service_name=expected_service_name, action=action, subject_key_digest=expected_subject_key_digest, capsules=capsule_tuple)
        if capsule.issued_at > now or capsule.expires_at <= now:
            return _report(ModerationDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, False, False, False, "moderation capsule expired or future", profile_id=expected_profile_id, service_name=expected_service_name, action=action, subject_key_digest=expected_subject_key_digest, capsules=capsule_tuple)
        if capsule.capsule_digest in seen:
            return _report(ModerationDecisionKind.QUARANTINE_REPLAY, False, False, False, "moderation capsule replay", profile_id=expected_profile_id, service_name=expected_service_name, action=action, subject_key_digest=expected_subject_key_digest, capsules=capsule_tuple)
        if capsule.profile_id != expected_profile_id:
            return _report(ModerationDecisionKind.QUARANTINE_PROFILE_DRIFT, False, False, False, "moderation profile drift", profile_id=expected_profile_id, service_name=expected_service_name, action=action, subject_key_digest=expected_subject_key_digest, capsules=capsule_tuple)
        if capsule.service_name != expected_service_name:
            return _report(ModerationDecisionKind.QUARANTINE_SERVICE_DRIFT, False, False, False, "moderation service drift", profile_id=expected_profile_id, service_name=expected_service_name, action=action, subject_key_digest=expected_subject_key_digest, capsules=capsule_tuple)
        if capsule.subject_key_digest != expected_subject_key_digest:
            return _report(ModerationDecisionKind.QUARANTINE_SUBJECT_DRIFT, False, False, False, "moderation subject drift", profile_id=expected_profile_id, service_name=expected_service_name, action=action, subject_key_digest=expected_subject_key_digest, capsules=capsule_tuple)
        if capsule.action is not action:
            return _report(ModerationDecisionKind.QUARANTINE_ACTION_DRIFT, False, False, False, "moderation action drift", profile_id=expected_profile_id, service_name=expected_service_name, action=action, subject_key_digest=expected_subject_key_digest, capsules=capsule_tuple)
        if capsule.scope_digest != expected_scope_digest:
            return _report(ModerationDecisionKind.QUARANTINE_SCOPE_DRIFT, False, False, False, "moderation scope drift", profile_id=expected_profile_id, service_name=expected_service_name, action=action, subject_key_digest=expected_subject_key_digest, capsules=capsule_tuple)
        if capsule.request_digest != expected_request_digest:
            return _report(ModerationDecisionKind.QUARANTINE_REQUEST_DRIFT, False, False, False, "moderation request drift", profile_id=expected_profile_id, service_name=expected_service_name, action=action, subject_key_digest=expected_subject_key_digest, capsules=capsule_tuple)
        if not capsule.hard_negative_clear:
            return _report(ModerationDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, False, "hard-negative pressure inside moderation capsule", profile_id=expected_profile_id, service_name=expected_service_name, action=action, subject_key_digest=expected_subject_key_digest, capsules=capsule_tuple)
        if previous_sequence is not None and capsule.sequence < previous_sequence:
            return _report(ModerationDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, False, False, "moderation sequence rollback", profile_id=expected_profile_id, service_name=expected_service_name, action=action, subject_key_digest=expected_subject_key_digest, capsules=capsule_tuple)
        prior = fork_guard.get(capsule.sequence)
        if prior is not None and prior != capsule.capsule_core_digest:
            return _report(ModerationDecisionKind.QUARANTINE_SEQUENCE_FORK, False, False, False, "same-sequence moderation capsule fork", profile_id=expected_profile_id, service_name=expected_service_name, action=action, subject_key_digest=expected_subject_key_digest, capsules=capsule_tuple)
        fork_guard[capsule.sequence] = capsule.capsule_core_digest
        families.add(capsule.family_id)
        paths.add(capsule.path_family)
        if latest is None or capsule.sequence > latest.sequence:
            latest = capsule
    assert latest is not None
    if previous_sequence is not None and latest.sequence > previous_sequence and previous_capsule_digest is not None and latest.previous_capsule_digest != previous_capsule_digest:
        return _report(ModerationDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, False, False, "moderation previous-link mismatch", profile_id=expected_profile_id, service_name=expected_service_name, action=action, subject_key_digest=expected_subject_key_digest, capsules=capsule_tuple, selected=latest, family_count=len(families), path_family_count=len(paths))
    if latest.disposition is ModerationDisposition.WARN:
        return _report(ModerationDecisionKind.ACCEPT_WARNING, True, False, False, "moderation warning accepted as local evidence", profile_id=expected_profile_id, service_name=expected_service_name, action=action, subject_key_digest=expected_subject_key_digest, capsules=capsule_tuple, selected=latest, family_count=len(families), path_family_count=len(paths))
    if latest.disposition is ModerationDisposition.WATCH:
        if not allow_watch:
            return _report(ModerationDecisionKind.HOLD_WATCH_REQUIRES_EXPLICIT_ALLOWANCE, False, False, True, "watch disposition requires explicit allowance", profile_id=expected_profile_id, service_name=expected_service_name, action=action, subject_key_digest=expected_subject_key_digest, capsules=capsule_tuple, selected=latest, family_count=len(families), path_family_count=len(paths))
        return _report(ModerationDecisionKind.ACCEPT_WATCH, True, False, True, "moderation watch accepted as local pressure", profile_id=expected_profile_id, service_name=expected_service_name, action=action, subject_key_digest=expected_subject_key_digest, capsules=capsule_tuple, selected=latest, family_count=len(families), path_family_count=len(paths))
    if latest.disposition in _BLOCKING:
        if len(families) < min_family_diversity_for_block:
            return _report(ModerationDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, False, "blocking moderation lacks family diversity", profile_id=expected_profile_id, service_name=expected_service_name, action=action, subject_key_digest=expected_subject_key_digest, capsules=capsule_tuple, selected=latest, family_count=len(families), path_family_count=len(paths))
        if len(paths) < min_path_diversity_for_block:
            return _report(ModerationDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, False, "blocking moderation lacks path diversity", profile_id=expected_profile_id, service_name=expected_service_name, action=action, subject_key_digest=expected_subject_key_digest, capsules=capsule_tuple, selected=latest, family_count=len(families), path_family_count=len(paths))
        kind = ModerationDecisionKind.ACCEPT_FREEZE if latest.disposition is ModerationDisposition.FREEZE else ModerationDecisionKind.ACCEPT_DENY
        return _report(kind, True, True, latest.disposition is ModerationDisposition.FREEZE, "blocking moderation accepted as subjective local policy", profile_id=expected_profile_id, service_name=expected_service_name, action=action, subject_key_digest=expected_subject_key_digest, capsules=capsule_tuple, selected=latest, family_count=len(families), path_family_count=len(paths))
    raise AssertionError("unhandled moderation disposition")
