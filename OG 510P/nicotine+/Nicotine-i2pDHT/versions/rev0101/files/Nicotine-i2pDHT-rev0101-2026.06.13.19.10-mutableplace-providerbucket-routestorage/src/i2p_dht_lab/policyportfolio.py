"""Subjective policy-source portfolios for local bridge/garden decisions.

rev0047 keeps the rev0046 moderation stance but makes the source set explicit.
A local build, garden, or bridge may subscribe to several policy heads. A single
valid policy source is not enough to shape a risky public side effect: the
portfolio has to survive freshness, monotonicity, scope binding, and capture
pressure. This is local policy, not DHT truth.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .moderationquarantine import ModerationAction, ZERO_DIGEST

POLICY_PORTFOLIO_DOMAIN = DOMAIN + b":policy-portfolio-v1:"


class PolicySourceKind(str, Enum):
    MAINTAINER = "maintainer"
    LOCAL_OPERATOR = "local_operator"
    GARDEN_SENTINEL = "garden_sentinel"
    FRIEND_TRUST = "friend_trust"
    EMERGENCY = "emergency"


class PolicyDisposition(str, Enum):
    ALLOW = "allow"
    WARN = "warn"
    WATCH = "watch"
    DENY = "deny"
    FREEZE = "freeze"


class PolicyPortfolioDecisionKind(str, Enum):
    CLEAR_NO_POLICY = "clear_no_policy"
    ACCEPT_ALLOW = "accept_allow"
    ACCEPT_WARN = "accept_warn"
    HOLD_WATCH = "hold_watch"
    HOLD_LOW_SOURCE_DIVERSITY = "hold_low_source_diversity"
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
    QUARANTINE_CAPTURED_AUTHORITY_FAMILY = "quarantine_captured_authority_family"
    QUARANTINE_DENY = "quarantine_deny"
    QUARANTINE_FREEZE = "quarantine_freeze"
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"


_BLOCKING = {PolicyDisposition.DENY, PolicyDisposition.FREEZE}


@dataclass(frozen=True)
class PolicySourceCapsule:
    source_name: str
    source_kind: PolicySourceKind
    action: ModerationAction
    disposition: PolicyDisposition
    profile_id: str
    service_name: str
    subject_key_digest: bytes
    scope_digest: bytes
    request_digest: bytes
    policy_head_digest: bytes
    sequence: int
    previous_source_digest: bytes
    issued_at: int
    expires_at: int
    family_id: str
    path_family: str
    signer_public_key: bytes
    note: str = ""
    signature: bytes = b""

    def __post_init__(self) -> None:
        if not self.source_name or len(self.source_name.encode("utf-8")) > 96:
            raise ValueError("source_name must be short and non-empty")
        if not self.profile_id or len(self.profile_id.encode("utf-8")) > 80:
            raise ValueError("profile_id must be short and non-empty")
        if not self.service_name or len(self.service_name.encode("utf-8")) > 96:
            raise ValueError("service_name must be short and non-empty")
        if len(self.note.encode("utf-8")) > 180:
            raise ValueError("note must be short")
        if self.sequence < 0:
            raise ValueError("policy source sequence must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("expires_at must be after issued_at")
        if not self.family_id or not self.path_family:
            raise ValueError("family_id and path_family must be non-empty")
        for name, value in (("subject_key_digest", self.subject_key_digest), ("scope_digest", self.scope_digest), ("request_digest", self.request_digest), ("policy_head_digest", self.policy_head_digest), ("previous_source_digest", self.previous_source_digest), ("signer_public_key", self.signer_public_key)):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if self.signature and len(self.signature) != 64:
            raise ValueError("signature must be Ed25519-sized")
        object.__setattr__(self, "source_kind", PolicySourceKind(self.source_kind))
        object.__setattr__(self, "action", ModerationAction(self.action))
        object.__setattr__(self, "disposition", PolicyDisposition(self.disposition))

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"source": self.source_name,
            b"kind": self.source_kind.value,
            b"action": self.action.value,
            b"disposition": self.disposition.value,
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"subject": self.subject_key_digest,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"policy_head": self.policy_head_digest,
            b"seq": self.sequence,
            b"prev": self.previous_source_digest,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"family": self.family_id,
            b"path_family": self.path_family,
            b"signer": self.signer_public_key,
            b"note": self.note,
        }

    def signature_payload(self) -> bytes:
        return POLICY_PORTFOLIO_DOMAIN + b":source-sig:" + bencode(self.unsigned_bvalue())

    @property
    def source_core_digest(self) -> bytes:
        return sha256(POLICY_PORTFOLIO_DOMAIN + b":source-core:" + bencode(self.unsigned_bvalue()))

    @property
    def source_digest(self) -> bytes:
        return sha256(POLICY_PORTFOLIO_DOMAIN + b":source-digest:" + self.signature_payload() + self.signature)

    def verifies(self) -> bool:
        return verify_signature(self.signer_public_key, self.signature_payload(), self.signature)


@dataclass(frozen=True)
class PolicyPortfolioReport:
    decision_kind: PolicyPortfolioDecisionKind
    allow: bool
    watch: bool
    blocked: bool
    reason: str
    profile_id: str
    service_name: str
    action: ModerationAction
    subject_key_digest: bytes
    source_digests: tuple[bytes, ...]
    source_kind_count: int
    family_count: int
    path_family_count: int
    highest_sequence: int
    selected_disposition: PolicyDisposition | None
    accepted_source_digest: bytes
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")

    @property
    def accept(self) -> bool:
        # Compatibility with joined-boundary gates that use `accept` for
        # other local reports.  This lane calls the positive bit `allow`
        # because subjective policy is local control, not DHT truth.
        return self.allow


def make_policy_source_capsule(*, keypair: DhtKeypair, source_name: str, source_kind: PolicySourceKind, action: ModerationAction, disposition: PolicyDisposition, profile_id: str, service_name: str, subject_key_digest: bytes, scope_digest: bytes, request_digest: bytes, policy_head_digest: bytes, sequence: int, previous_source_digest: bytes = ZERO_DIGEST, issued_at: int, expires_at: int, family_id: str, path_family: str, note: str = "") -> PolicySourceCapsule:
    capsule = PolicySourceCapsule(source_name, source_kind, action, disposition, profile_id, service_name, subject_key_digest, scope_digest, request_digest, policy_head_digest, sequence, previous_source_digest, issued_at, expires_at, family_id, path_family, keypair.public_key_bytes, note)
    return replace(capsule, signature=keypair.sign(capsule.signature_payload()))


def _report(kind: PolicyPortfolioDecisionKind, allow: bool, watch: bool, blocked: bool, reason: str, *, profile_id: str, service_name: str, action: ModerationAction, subject_key_digest: bytes, sources: Iterable[PolicySourceCapsule] = (), selected: PolicySourceCapsule | None = None, source_kind_count: int = 0, family_count: int = 0, path_family_count: int = 0) -> PolicyPortfolioReport:
    source_tuple = tuple(sorted(sources, key=lambda item: (item.sequence, item.source_digest)))
    digests = tuple(sorted(item.source_digest for item in source_tuple))
    highest = selected.sequence if selected else -1
    accepted = selected.source_digest if selected and (allow or watch or blocked) else ZERO_DIGEST
    selected_disposition = selected.disposition if selected else None
    digest = sha256(POLICY_PORTFOLIO_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"allow": 1 if allow else 0,
        b"watch": 1 if watch else 0,
        b"blocked": 1 if blocked else 0,
        b"reason": reason,
        b"profile": profile_id,
        b"service": service_name,
        b"action": action.value,
        b"subject": subject_key_digest,
        b"sources": list(digests),
        b"source_kinds": source_kind_count,
        b"families": family_count,
        b"paths": path_family_count,
        b"highest": highest,
        b"disposition": selected_disposition.value if selected_disposition else "none",
        b"accepted": accepted,
    }))
    return PolicyPortfolioReport(kind, allow, watch, blocked, reason, profile_id, service_name, action, subject_key_digest, digests, source_kind_count, family_count, path_family_count, highest, selected_disposition, accepted, digest)


def assess_policy_portfolio(sources: Iterable[PolicySourceCapsule], *, now: int, expected_profile_id: str, expected_service_name: str, expected_subject_key_digest: bytes, expected_action: ModerationAction, expected_scope_digest: bytes, expected_request_digest: bytes, previous_sequence: int | None = None, previous_source_digest: bytes | None = None, previously_seen_sources: Iterable[bytes] = (), live_hard_negative_digests: Iterable[bytes] = (), min_source_kind_diversity: int = 2, min_family_diversity: int = 2, min_path_diversity: int = 2, allow_watch: bool = False, allow_empty: bool = True) -> PolicyPortfolioReport:
    action = ModerationAction(expected_action)
    source_tuple = tuple(sorted(sources, key=lambda item: (item.sequence, item.source_digest)))
    if not source_tuple:
        if allow_empty:
            return _report(PolicyPortfolioDecisionKind.CLEAR_NO_POLICY, True, False, False, "no active policy portfolio", profile_id=expected_profile_id, service_name=expected_service_name, action=action, subject_key_digest=expected_subject_key_digest)
        return _report(PolicyPortfolioDecisionKind.HOLD_LOW_SOURCE_DIVERSITY, False, False, False, "missing policy portfolio", profile_id=expected_profile_id, service_name=expected_service_name, action=action, subject_key_digest=expected_subject_key_digest)
    if tuple(live_hard_negative_digests):
        return _report(PolicyPortfolioDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, True, "live hard negative pressure blocks policy portfolio", profile_id=expected_profile_id, service_name=expected_service_name, action=action, subject_key_digest=expected_subject_key_digest, sources=source_tuple)
    seen = set(previously_seen_sources)
    fork_guard: dict[int, bytes] = {}
    kinds: set[PolicySourceKind] = set()
    families: set[str] = set()
    paths: set[str] = set()
    signer_families: dict[bytes, set[str]] = {}
    latest: PolicySourceCapsule | None = None
    blocking: PolicySourceCapsule | None = None
    watch_source: PolicySourceCapsule | None = None
    warn_source: PolicySourceCapsule | None = None
    allow_source: PolicySourceCapsule | None = None
    for source in source_tuple:
        if not source.verifies():
            return _report(PolicyPortfolioDecisionKind.QUARANTINE_BAD_SIGNATURE, False, False, True, "bad policy source signature", profile_id=expected_profile_id, service_name=expected_service_name, action=action, subject_key_digest=expected_subject_key_digest, sources=source_tuple)
        if source.issued_at > now or source.expires_at <= now:
            return _report(PolicyPortfolioDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, False, False, True, "policy source expired or future", profile_id=expected_profile_id, service_name=expected_service_name, action=action, subject_key_digest=expected_subject_key_digest, sources=source_tuple)
        if source.source_digest in seen:
            return _report(PolicyPortfolioDecisionKind.QUARANTINE_REPLAY, False, False, True, "policy source replay", profile_id=expected_profile_id, service_name=expected_service_name, action=action, subject_key_digest=expected_subject_key_digest, sources=source_tuple)
        if source.profile_id != expected_profile_id:
            return _report(PolicyPortfolioDecisionKind.QUARANTINE_PROFILE_DRIFT, False, False, True, "policy profile drift", profile_id=expected_profile_id, service_name=expected_service_name, action=action, subject_key_digest=expected_subject_key_digest, sources=source_tuple)
        if source.service_name != expected_service_name:
            return _report(PolicyPortfolioDecisionKind.QUARANTINE_SERVICE_DRIFT, False, False, True, "policy service drift", profile_id=expected_profile_id, service_name=expected_service_name, action=action, subject_key_digest=expected_subject_key_digest, sources=source_tuple)
        if source.scope_digest != expected_scope_digest:
            return _report(PolicyPortfolioDecisionKind.QUARANTINE_SCOPE_DRIFT, False, False, True, "policy scope drift", profile_id=expected_profile_id, service_name=expected_service_name, action=action, subject_key_digest=expected_subject_key_digest, sources=source_tuple)
        if source.request_digest != expected_request_digest:
            return _report(PolicyPortfolioDecisionKind.QUARANTINE_REQUEST_DRIFT, False, False, True, "policy request drift", profile_id=expected_profile_id, service_name=expected_service_name, action=action, subject_key_digest=expected_subject_key_digest, sources=source_tuple)
        if source.subject_key_digest != expected_subject_key_digest:
            return _report(PolicyPortfolioDecisionKind.QUARANTINE_SUBJECT_DRIFT, False, False, True, "policy subject drift", profile_id=expected_profile_id, service_name=expected_service_name, action=action, subject_key_digest=expected_subject_key_digest, sources=source_tuple)
        if source.action is not action:
            return _report(PolicyPortfolioDecisionKind.QUARANTINE_ACTION_DRIFT, False, False, True, "policy action drift", profile_id=expected_profile_id, service_name=expected_service_name, action=action, subject_key_digest=expected_subject_key_digest, sources=source_tuple)
        if previous_sequence is not None and source.sequence < previous_sequence:
            return _report(PolicyPortfolioDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, False, True, "policy source sequence rollback", profile_id=expected_profile_id, service_name=expected_service_name, action=action, subject_key_digest=expected_subject_key_digest, sources=source_tuple)
        fork_key = source.sequence
        prior = fork_guard.get(fork_key)
        if prior is not None and prior != source.source_core_digest:
            return _report(PolicyPortfolioDecisionKind.QUARANTINE_SEQUENCE_FORK, False, False, True, "policy source same-sequence fork", profile_id=expected_profile_id, service_name=expected_service_name, action=action, subject_key_digest=expected_subject_key_digest, sources=source_tuple)
        fork_guard[fork_key] = source.source_core_digest
        kinds.add(source.source_kind)
        families.add(source.family_id)
        paths.add(source.path_family)
        signer_families.setdefault(source.signer_public_key, set()).add(source.family_id)
        if latest is None or source.sequence > latest.sequence:
            latest = source
        if source.disposition in _BLOCKING:
            blocking = source if blocking is None or source.sequence >= blocking.sequence else blocking
        elif source.disposition is PolicyDisposition.WATCH:
            watch_source = source if watch_source is None or source.sequence >= watch_source.sequence else watch_source
        elif source.disposition is PolicyDisposition.WARN:
            warn_source = source if warn_source is None or source.sequence >= warn_source.sequence else warn_source
        else:
            allow_source = source if allow_source is None or source.sequence >= allow_source.sequence else allow_source
    assert latest is not None
    if previous_sequence is not None and latest.sequence > previous_sequence and previous_source_digest is not None and latest.previous_source_digest != previous_source_digest:
        return _report(PolicyPortfolioDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, False, True, "policy source previous-link mismatch", profile_id=expected_profile_id, service_name=expected_service_name, action=action, subject_key_digest=expected_subject_key_digest, sources=source_tuple, selected=latest, source_kind_count=len(kinds), family_count=len(families), path_family_count=len(paths))
    if len(kinds) < min_source_kind_diversity:
        return _report(PolicyPortfolioDecisionKind.HOLD_LOW_SOURCE_DIVERSITY, False, False, False, "policy source kind diversity too low", profile_id=expected_profile_id, service_name=expected_service_name, action=action, subject_key_digest=expected_subject_key_digest, sources=source_tuple, selected=latest, source_kind_count=len(kinds), family_count=len(families), path_family_count=len(paths))
    if len(families) < min_family_diversity:
        return _report(PolicyPortfolioDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, False, False, "policy family diversity too low", profile_id=expected_profile_id, service_name=expected_service_name, action=action, subject_key_digest=expected_subject_key_digest, sources=source_tuple, selected=latest, source_kind_count=len(kinds), family_count=len(families), path_family_count=len(paths))
    if len(paths) < min_path_diversity:
        return _report(PolicyPortfolioDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, False, False, "policy path diversity too low", profile_id=expected_profile_id, service_name=expected_service_name, action=action, subject_key_digest=expected_subject_key_digest, sources=source_tuple, selected=latest, source_kind_count=len(kinds), family_count=len(families), path_family_count=len(paths))
    if any(len(family_set) > 1 for family_set in signer_families.values()):
        return _report(PolicyPortfolioDecisionKind.QUARANTINE_CAPTURED_AUTHORITY_FAMILY, False, False, True, "one signer inflated policy-family diversity", profile_id=expected_profile_id, service_name=expected_service_name, action=action, subject_key_digest=expected_subject_key_digest, sources=source_tuple, selected=latest, source_kind_count=len(kinds), family_count=len(families), path_family_count=len(paths))
    if blocking is not None:
        kind = PolicyPortfolioDecisionKind.QUARANTINE_FREEZE if blocking.disposition is PolicyDisposition.FREEZE else PolicyPortfolioDecisionKind.QUARANTINE_DENY
        return _report(kind, False, False, True, "blocking policy source active", profile_id=expected_profile_id, service_name=expected_service_name, action=action, subject_key_digest=expected_subject_key_digest, sources=source_tuple, selected=blocking, source_kind_count=len(kinds), family_count=len(families), path_family_count=len(paths))
    if watch_source is not None:
        return _report(PolicyPortfolioDecisionKind.ACCEPT_WARN if allow_watch else PolicyPortfolioDecisionKind.HOLD_WATCH, allow_watch, True, False, "watch policy source active", profile_id=expected_profile_id, service_name=expected_service_name, action=action, subject_key_digest=expected_subject_key_digest, sources=source_tuple, selected=watch_source, source_kind_count=len(kinds), family_count=len(families), path_family_count=len(paths))
    if warn_source is not None:
        return _report(PolicyPortfolioDecisionKind.ACCEPT_WARN, True, True, False, "warning policy source active", profile_id=expected_profile_id, service_name=expected_service_name, action=action, subject_key_digest=expected_subject_key_digest, sources=source_tuple, selected=warn_source, source_kind_count=len(kinds), family_count=len(families), path_family_count=len(paths))
    return _report(PolicyPortfolioDecisionKind.ACCEPT_ALLOW, True, False, False, "diverse policy portfolio allows action", profile_id=expected_profile_id, service_name=expected_service_name, action=action, subject_key_digest=expected_subject_key_digest, sources=source_tuple, selected=allow_source or latest, source_kind_count=len(kinds), family_count=len(families), path_family_count=len(paths))
