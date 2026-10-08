"""Final no-network public publication dry-run gate.

rev0048 created a bridge-shadow step, local audit receipts, and redress GC.
rev0049 joins those with compacted audit evidence, scope-journal restart memory,
and SAM-trace shadow evidence before a future public bridge write could even be
considered.  This module is still not a publisher.  It is a dry-run side-effect
receipt that deliberately refuses to let one successful component authorize the
next component's egress.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable, Any

from .auditcompact import AuditCompactReport
from .auditquorum import AuditQuorumReport
from .bencode import BValue, bencode
from .bridgeshadow import BridgeShadowAction, BridgeShadowReport
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .redressgc import RedressGcReport
from .scopejournal import ScopeJournalReport

PUBLISH_DRY_RUN_DOMAIN = DOMAIN + b":publish-dry-run-v1:"


class PublishDryRunDecisionKind(str, Enum):
    ACCEPT_DRY_RUN = "accept_dry_run"
    ACCEPT_WITH_WATCH = "accept_with_watch"
    HOLD_BRIDGE_SHADOW = "hold_bridge_shadow"
    HOLD_AUDIT_QUORUM = "hold_audit_quorum"
    HOLD_AUDIT_COMPACT = "hold_audit_compact"
    HOLD_REDRESS_GC = "hold_redress_gc"
    HOLD_SAM_TRACE = "hold_sam_trace"
    HOLD_SCOPE_JOURNAL = "hold_scope_journal"
    HOLD_WATCH_COMPONENT = "hold_watch_component"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    EMPTY_NO_DRY_RUN_STEPS = "empty_no_dry_run_steps"
    QUARANTINE_BRIDGE_SHADOW = "quarantine_bridge_shadow"
    QUARANTINE_AUDIT_QUORUM = "quarantine_audit_quorum"
    QUARANTINE_AUDIT_COMPACT = "quarantine_audit_compact"
    QUARANTINE_REDRESS_GC = "quarantine_redress_gc"
    QUARANTINE_SAM_TRACE = "quarantine_sam_trace"
    QUARANTINE_SCOPE_JOURNAL = "quarantine_scope_journal"
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
    QUARANTINE_PAYLOAD_DRIFT = "quarantine_payload_drift"
    QUARANTINE_ACTION_DRIFT = "quarantine_action_drift"
    QUARANTINE_CHANNEL_DRIFT = "quarantine_channel_drift"
    QUARANTINE_SUBJECT_DRIFT = "quarantine_subject_drift"
    QUARANTINE_COMPONENT_DIGEST_DRIFT = "quarantine_component_digest_drift"


@dataclass(frozen=True)
class PublicationDryRunStep:
    action: BridgeShadowAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    bridge_shadow_digest: bytes
    audit_quorum_digest: bytes
    audit_compact_digest: bytes
    redress_gc_digest: bytes
    sam_trace_digest: bytes
    scope_journal_digest: bytes
    dry_effect_digest: bytes
    sequence: int
    previous_dry_run_digest: bytes
    issued_at: int
    expires_at: int
    family_id: str
    path_family: str
    signer_public_key: bytes
    signature: bytes = b""

    def __post_init__(self) -> None:
        object.__setattr__(self, "action", BridgeShadowAction(self.action))
        if not self.profile_id or not self.service_name or not self.family_id or not self.path_family:
            raise ValueError("publication dry-run step needs profile/service/family/path")
        if self.sequence < 0:
            raise ValueError("sequence must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("expires_at must follow issued_at")
        for name, value in (
            ("scope_digest", self.scope_digest),
            ("request_digest", self.request_digest),
            ("payload_digest", self.payload_digest),
            ("bridge_shadow_digest", self.bridge_shadow_digest),
            ("audit_quorum_digest", self.audit_quorum_digest),
            ("audit_compact_digest", self.audit_compact_digest),
            ("redress_gc_digest", self.redress_gc_digest),
            ("sam_trace_digest", self.sam_trace_digest),
            ("scope_journal_digest", self.scope_journal_digest),
            ("dry_effect_digest", self.dry_effect_digest),
            ("previous_dry_run_digest", self.previous_dry_run_digest),
            ("signer_public_key", self.signer_public_key),
        ):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if self.signature and len(self.signature) != 64:
            raise ValueError("signature must be empty or Ed25519-sized")

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"action": self.action.value,
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"payload": self.payload_digest,
            b"shadow": self.bridge_shadow_digest,
            b"quorum": self.audit_quorum_digest,
            b"compact": self.audit_compact_digest,
            b"redress_gc": self.redress_gc_digest,
            b"sam_trace": self.sam_trace_digest,
            b"journal": self.scope_journal_digest,
            b"effect": self.dry_effect_digest,
            b"seq": self.sequence,
            b"prev": self.previous_dry_run_digest,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"family": self.family_id,
            b"path_family": self.path_family,
            b"signer": self.signer_public_key,
        }

    def signature_payload(self) -> bytes:
        return PUBLISH_DRY_RUN_DOMAIN + b":step-sig:" + bencode(self.unsigned_bvalue())

    @property
    def step_core_digest(self) -> bytes:
        return sha256(PUBLISH_DRY_RUN_DOMAIN + b":step-core:" + bencode(self.unsigned_bvalue()))

    @property
    def step_digest(self) -> bytes:
        return sha256(PUBLISH_DRY_RUN_DOMAIN + b":step-digest:" + self.signature_payload() + self.signature)

    def verifies(self) -> bool:
        return verify_signature(self.signer_public_key, self.signature_payload(), self.signature)

    def live(self, now: int) -> bool:
        return self.issued_at <= now < self.expires_at


@dataclass(frozen=True)
class PublicationDryRunReport:
    decision_kind: PublishDryRunDecisionKind
    accept: bool
    watch: bool
    reason: str
    accepted_step_digest: bytes
    step_digests: tuple[bytes, ...]
    component_digests: tuple[bytes, ...]
    family_count: int
    path_family_count: int
    highest_sequence: int
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _component_accept(report: Any) -> bool:
    return bool(getattr(report, "accept", False))


def _component_watch(report: Any) -> bool:
    return bool(getattr(report, "watch", False))


def _component_quarantined(report: Any) -> bool:
    return bool(getattr(report, "quarantined", False))


def _component_digest(report: Any) -> bytes:
    for attr in ("report_digest", "transcript_digest"):
        value = getattr(report, attr, None)
        if isinstance(value, bytes) and len(value) == 32:
            return value
    raise ValueError("component report lacks a 32-byte report/transcript digest")


def make_publication_dry_run_step(
    *,
    keypair: DhtKeypair,
    action: BridgeShadowAction,
    profile_id: str,
    service_name: str,
    scope_digest: bytes,
    request_digest: bytes,
    payload_digest: bytes,
    bridge_shadow: BridgeShadowReport,
    audit_quorum: AuditQuorumReport,
    audit_compact: AuditCompactReport,
    redress_gc: RedressGcReport,
    sam_trace: Any,
    scope_journal: ScopeJournalReport,
    dry_effect_digest: bytes,
    sequence: int,
    previous_dry_run_digest: bytes = ZERO_DIGEST,
    issued_at: int,
    expires_at: int,
    family_id: str,
    path_family: str,
) -> PublicationDryRunStep:
    step = PublicationDryRunStep(
        action=action,
        profile_id=profile_id,
        service_name=service_name,
        scope_digest=scope_digest,
        request_digest=request_digest,
        payload_digest=payload_digest,
        bridge_shadow_digest=bridge_shadow.report_digest,
        audit_quorum_digest=audit_quorum.report_digest,
        audit_compact_digest=audit_compact.report_digest,
        redress_gc_digest=redress_gc.report_digest,
        sam_trace_digest=_component_digest(sam_trace),
        scope_journal_digest=scope_journal.report_digest,
        dry_effect_digest=dry_effect_digest,
        sequence=sequence,
        previous_dry_run_digest=previous_dry_run_digest,
        issued_at=issued_at,
        expires_at=expires_at,
        family_id=family_id,
        path_family=path_family,
        signer_public_key=keypair.public_key_bytes,
    )
    return replace(step, signature=keypair.sign(step.signature_payload()))


def _report(kind: PublishDryRunDecisionKind, accept: bool, watch: bool, reason: str, *, steps: Iterable[PublicationDryRunStep], selected: PublicationDryRunStep | None = None, components: Iterable[bytes] = ()) -> PublicationDryRunReport:
    step_tuple = tuple(sorted(steps, key=lambda item: (item.sequence, item.step_digest)))
    step_digests = tuple(item.step_digest for item in step_tuple)
    component_digests = tuple(sorted(set(components)))
    accepted = selected.step_digest if selected and accept else ZERO_DIGEST
    families = len({item.family_id for item in step_tuple})
    paths = len({item.path_family for item in step_tuple})
    highest = selected.sequence if selected else max((item.sequence for item in step_tuple), default=-1)
    digest = sha256(PUBLISH_DRY_RUN_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"reason": reason,
        b"accepted": accepted,
        b"steps": list(step_digests),
        b"components": list(component_digests),
        b"families": families,
        b"paths": paths,
        b"highest": highest,
    }))
    return PublicationDryRunReport(kind, accept, watch, reason, accepted, step_digests, component_digests, families, paths, highest, digest)


def assess_publication_dry_run(
    steps: Iterable[PublicationDryRunStep],
    *,
    bridge_shadow: BridgeShadowReport,
    audit_quorum: AuditQuorumReport,
    audit_compact: AuditCompactReport,
    redress_gc: RedressGcReport,
    sam_trace: Any,
    scope_journal: ScopeJournalReport,
    now: int,
    expected_profile_id: str,
    expected_service_name: str,
    expected_scope_digest: bytes,
    expected_request_digest: bytes,
    expected_payload_digest: bytes,
    expected_action: BridgeShadowAction,
    previous_highest_sequence: int = -1,
    previous_dry_run_digest: bytes = ZERO_DIGEST,
    previously_seen_steps: Iterable[bytes] = (),
    min_family_diversity: int = 1,
    min_path_diversity: int = 1,
) -> PublicationDryRunReport:
    step_tuple = tuple(sorted(steps, key=lambda item: (item.sequence, item.step_digest)))
    component_digests = (
        bridge_shadow.report_digest,
        audit_quorum.report_digest,
        audit_compact.report_digest,
        redress_gc.report_digest,
        _component_digest(sam_trace),
        scope_journal.report_digest,
    )
    if not step_tuple:
        return _report(PublishDryRunDecisionKind.EMPTY_NO_DRY_RUN_STEPS, False, True, "no publication dry-run steps supplied", steps=(), components=component_digests)
    component_checks = (
        (bridge_shadow, PublishDryRunDecisionKind.HOLD_BRIDGE_SHADOW, PublishDryRunDecisionKind.QUARANTINE_BRIDGE_SHADOW, "bridge shadow"),
        (audit_quorum, PublishDryRunDecisionKind.HOLD_AUDIT_QUORUM, PublishDryRunDecisionKind.QUARANTINE_AUDIT_QUORUM, "audit quorum"),
        (audit_compact, PublishDryRunDecisionKind.HOLD_AUDIT_COMPACT, PublishDryRunDecisionKind.QUARANTINE_AUDIT_COMPACT, "audit compact"),
        (redress_gc, PublishDryRunDecisionKind.HOLD_REDRESS_GC, PublishDryRunDecisionKind.QUARANTINE_REDRESS_GC, "redress GC"),
        (sam_trace, PublishDryRunDecisionKind.HOLD_SAM_TRACE, PublishDryRunDecisionKind.QUARANTINE_SAM_TRACE, "SAM trace"),
        (scope_journal, PublishDryRunDecisionKind.HOLD_SCOPE_JOURNAL, PublishDryRunDecisionKind.QUARANTINE_SCOPE_JOURNAL, "scope journal"),
    )
    for component, hold_kind, quarantine_kind, label in component_checks:
        if _component_quarantined(component):
            return _report(quarantine_kind, False, True, f"{label} quarantined", steps=step_tuple, components=component_digests)
        if not _component_accept(component):
            return _report(hold_kind, False, _component_watch(component), f"{label} did not accept", steps=step_tuple, components=component_digests)
    seen = set(previously_seen_steps)
    core_by_seq: dict[int, bytes] = {}
    expected_action = BridgeShadowAction(expected_action)
    for step in step_tuple:
        if not step.verifies():
            return _report(PublishDryRunDecisionKind.QUARANTINE_BAD_SIGNATURE, False, True, "bad publication dry-run signature", steps=step_tuple, components=component_digests)
        if not step.live(now):
            return _report(PublishDryRunDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, False, True, "publication dry-run expired or future", steps=step_tuple, components=component_digests)
        if step.step_digest in seen:
            return _report(PublishDryRunDecisionKind.QUARANTINE_REPLAY, False, True, "publication dry-run replay", steps=step_tuple, components=component_digests)
        if step.sequence <= previous_highest_sequence:
            return _report(PublishDryRunDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, True, "publication dry-run sequence rollback", steps=step_tuple, components=component_digests)
        if previous_highest_sequence >= 0 and step.previous_dry_run_digest != previous_dry_run_digest:
            return _report(PublishDryRunDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, True, "publication dry-run previous digest mismatch", steps=step_tuple, components=component_digests)
        prev = core_by_seq.setdefault(step.sequence, step.step_core_digest)
        if prev != step.step_core_digest:
            return _report(PublishDryRunDecisionKind.QUARANTINE_SEQUENCE_FORK, False, True, "publication dry-run same-sequence fork", steps=step_tuple, components=component_digests)
        if step.profile_id != expected_profile_id:
            return _report(PublishDryRunDecisionKind.QUARANTINE_PROFILE_DRIFT, False, True, "publication dry-run profile drift", steps=step_tuple, components=component_digests)
        if step.service_name != expected_service_name:
            return _report(PublishDryRunDecisionKind.QUARANTINE_SERVICE_DRIFT, False, True, "publication dry-run service drift", steps=step_tuple, components=component_digests)
        if step.scope_digest != expected_scope_digest:
            return _report(PublishDryRunDecisionKind.QUARANTINE_SCOPE_DRIFT, False, True, "publication dry-run scope drift", steps=step_tuple, components=component_digests)
        if step.request_digest != expected_request_digest:
            return _report(PublishDryRunDecisionKind.QUARANTINE_REQUEST_DRIFT, False, True, "publication dry-run request drift", steps=step_tuple, components=component_digests)
        if step.payload_digest != expected_payload_digest:
            return _report(PublishDryRunDecisionKind.QUARANTINE_PAYLOAD_DRIFT, False, True, "publication dry-run payload drift", steps=step_tuple, components=component_digests)
        if step.action is not expected_action:
            return _report(PublishDryRunDecisionKind.QUARANTINE_ACTION_DRIFT, False, True, "publication dry-run action drift", steps=step_tuple, components=component_digests)
        if (
            step.bridge_shadow_digest != bridge_shadow.report_digest
            or step.audit_quorum_digest != audit_quorum.report_digest
            or step.audit_compact_digest != audit_compact.report_digest
            or step.redress_gc_digest != redress_gc.report_digest
            or step.sam_trace_digest != _component_digest(sam_trace)
            or step.scope_journal_digest != scope_journal.report_digest
        ):
            return _report(PublishDryRunDecisionKind.QUARANTINE_COMPONENT_DIGEST_DRIFT, False, True, "publication dry-run component digest drift", steps=step_tuple, components=component_digests)
    if len({item.family_id for item in step_tuple}) < min_family_diversity:
        return _report(PublishDryRunDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, "publication dry-run family diversity too low", steps=step_tuple, components=component_digests)
    if len({item.path_family for item in step_tuple}) < min_path_diversity:
        return _report(PublishDryRunDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, "publication dry-run path-family diversity too low", steps=step_tuple, components=component_digests)
    selected = max(step_tuple, key=lambda item: (item.sequence, item.step_digest))
    watch = any(_component_watch(component) for component, *_ in component_checks)
    kind = PublishDryRunDecisionKind.ACCEPT_WITH_WATCH if watch else PublishDryRunDecisionKind.ACCEPT_DRY_RUN
    return _report(kind, True, watch, "publication dry-run binds shadow, audit, redress, SAM trace, and restart journal", steps=step_tuple, selected=selected, components=component_digests)

# ---------------------------------------------------------------------------
# Compatibility/public-edge dry-run API folded from the rev0049 branchlet.
# The richer PublicationDryRunStep above joins audit-compact/scope-journal/SAM
# trace.  This older API is still useful and tests the smaller public-edge seam:
# bridge-shadow + audit-quorum + redress-GC + optional transport-shadow digest.

class PublishChannel(str, Enum):
    PUBLIC_BRIDGE_RECORD = "public_bridge_record"
    PUBLIC_BRIDGE_WITHDRAWAL = "public_bridge_withdrawal"
    PUBLIC_BRIDGE_REPAIR = "public_bridge_repair"


@dataclass(frozen=True)
class PublishDryRunAttempt:
    channel: PublishChannel
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    subject_digest: bytes
    public_payload_digest: bytes
    bridge_shadow_digest: bytes
    audit_quorum_digest: bytes
    redress_gc_digest: bytes
    dry_effect_digest: bytes
    sequence: int
    previous_attempt_digest: bytes
    transport_shadow_digest: bytes
    issued_at: int
    expires_at: int
    family_id: str
    path_family: str
    signer_public_key: bytes
    signature: bytes = b""

    def __post_init__(self) -> None:
        object.__setattr__(self, "channel", PublishChannel(self.channel))
        if not self.profile_id or not self.service_name or not self.family_id or not self.path_family:
            raise ValueError("publish dry-run attempt needs profile/service/family/path")
        if self.sequence < 0:
            raise ValueError("sequence must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("expires_at must follow issued_at")
        for name, value in (
            ("scope_digest", self.scope_digest),
            ("request_digest", self.request_digest),
            ("subject_digest", self.subject_digest),
            ("public_payload_digest", self.public_payload_digest),
            ("bridge_shadow_digest", self.bridge_shadow_digest),
            ("audit_quorum_digest", self.audit_quorum_digest),
            ("redress_gc_digest", self.redress_gc_digest),
            ("dry_effect_digest", self.dry_effect_digest),
            ("previous_attempt_digest", self.previous_attempt_digest),
            ("transport_shadow_digest", self.transport_shadow_digest),
            ("signer_public_key", self.signer_public_key),
        ):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if self.signature and len(self.signature) != 64:
            raise ValueError("signature must be Ed25519-sized")

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"channel": self.channel.value,
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"subject": self.subject_digest,
            b"payload": self.public_payload_digest,
            b"shadow": self.bridge_shadow_digest,
            b"audit": self.audit_quorum_digest,
            b"redress": self.redress_gc_digest,
            b"effect": self.dry_effect_digest,
            b"seq": self.sequence,
            b"prev": self.previous_attempt_digest,
            b"transport": self.transport_shadow_digest,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"family": self.family_id,
            b"path_family": self.path_family,
            b"signer": self.signer_public_key,
        }

    def signature_payload(self) -> bytes:
        return PUBLISH_DRY_RUN_DOMAIN + b":attempt-sig:" + bencode(self.unsigned_bvalue())

    @property
    def attempt_core_digest(self) -> bytes:
        return sha256(PUBLISH_DRY_RUN_DOMAIN + b":attempt-core:" + bencode(self.unsigned_bvalue()))

    @property
    def attempt_digest(self) -> bytes:
        return sha256(PUBLISH_DRY_RUN_DOMAIN + b":attempt-digest:" + self.signature_payload() + self.signature)

    def verifies(self) -> bool:
        return verify_signature(self.signer_public_key, self.signature_payload(), self.signature)

    def live(self, now: int) -> bool:
        return self.issued_at <= now < self.expires_at


def make_publish_dry_run_attempt(
    *,
    keypair: DhtKeypair,
    channel: PublishChannel,
    profile_id: str,
    service_name: str,
    scope_digest: bytes,
    request_digest: bytes,
    subject_digest: bytes,
    public_payload_digest: bytes,
    bridge_shadow_digest: bytes,
    audit_quorum_digest: bytes,
    redress_gc_digest: bytes,
    dry_effect_digest: bytes,
    sequence: int,
    previous_attempt_digest: bytes = ZERO_DIGEST,
    transport_shadow_digest: bytes = ZERO_DIGEST,
    issued_at: int,
    expires_at: int,
    family_id: str,
    path_family: str,
) -> PublishDryRunAttempt:
    attempt = PublishDryRunAttempt(channel, profile_id, service_name, scope_digest, request_digest, subject_digest, public_payload_digest, bridge_shadow_digest, audit_quorum_digest, redress_gc_digest, dry_effect_digest, sequence, previous_attempt_digest, transport_shadow_digest, issued_at, expires_at, family_id, path_family, keypair.public_key_bytes)
    return replace(attempt, signature=keypair.sign(attempt.signature_payload()))


def _legacy_report(kind: PublishDryRunDecisionKind, accept: bool, watch: bool, reason: str, *, attempts: Iterable[PublishDryRunAttempt], selected: PublishDryRunAttempt | None = None, components: Iterable[bytes] = ()) -> PublicationDryRunReport:
    attempt_tuple = tuple(sorted(attempts, key=lambda item: (item.sequence, item.attempt_digest)))
    digests = tuple(item.attempt_digest for item in attempt_tuple)
    component_digests = tuple(sorted(set(components)))
    accepted = selected.attempt_digest if selected and accept else ZERO_DIGEST
    families = len({item.family_id for item in attempt_tuple})
    paths = len({item.path_family for item in attempt_tuple})
    highest = selected.sequence if selected else max((item.sequence for item in attempt_tuple), default=-1)
    digest = sha256(PUBLISH_DRY_RUN_DOMAIN + b":legacy-report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"reason": reason,
        b"accepted": accepted,
        b"attempts": list(digests),
        b"components": list(component_digests),
        b"families": families,
        b"paths": paths,
        b"highest": highest,
    }))
    return PublicationDryRunReport(kind, accept, watch, reason, accepted, digests, component_digests, families, paths, highest, digest)


def assess_publish_dry_run(
    attempts: Iterable[PublishDryRunAttempt],
    *,
    bridge_shadow: Any,
    audit_quorum: Any,
    redress_gc: Any,
    now: int,
    expected_channel: PublishChannel,
    expected_profile_id: str,
    expected_service_name: str,
    expected_scope_digest: bytes,
    expected_request_digest: bytes,
    expected_subject_digest: bytes,
    expected_public_payload_digest: bytes,
    previous_highest_sequence: int = -1,
    previous_attempt_digest: bytes = ZERO_DIGEST,
    previously_seen_attempts: Iterable[bytes] = (),
    min_family_diversity: int = 2,
    min_path_diversity: int = 2,
    allow_component_watch: bool = True,
) -> PublicationDryRunReport:
    attempt_tuple = tuple(sorted(attempts, key=lambda item: (item.sequence, item.attempt_digest)))
    components = (_component_digest(bridge_shadow), _component_digest(audit_quorum), _component_digest(redress_gc))
    if not attempt_tuple:
        return _legacy_report(PublishDryRunDecisionKind.EMPTY_NO_DRY_RUN_STEPS, False, True, "no publish dry-run attempts supplied", attempts=(), components=components)
    component_checks = (
        (bridge_shadow, PublishDryRunDecisionKind.HOLD_BRIDGE_SHADOW, PublishDryRunDecisionKind.QUARANTINE_BRIDGE_SHADOW, "bridge shadow"),
        (audit_quorum, PublishDryRunDecisionKind.HOLD_AUDIT_QUORUM, PublishDryRunDecisionKind.QUARANTINE_AUDIT_QUORUM, "audit quorum"),
        (redress_gc, PublishDryRunDecisionKind.HOLD_REDRESS_GC, PublishDryRunDecisionKind.QUARANTINE_REDRESS_GC, "redress GC"),
    )
    for component, hold_kind, quarantine_kind, label in component_checks:
        if _component_quarantined(component):
            return _legacy_report(quarantine_kind, False, True, f"{label} quarantined", attempts=attempt_tuple, components=components)
        if not _component_accept(component):
            return _legacy_report(hold_kind, False, _component_watch(component), f"{label} did not accept", attempts=attempt_tuple, components=components)
    if any(_component_watch(component) for component, *_ in component_checks) and not allow_component_watch:
        return _legacy_report(PublishDryRunDecisionKind.HOLD_WATCH_COMPONENT, False, True, "component watch debt not allowed", attempts=attempt_tuple, components=components)
    seen = set(previously_seen_attempts)
    core_by_seq: dict[int, bytes] = {}
    expected_channel = PublishChannel(expected_channel)
    for attempt in attempt_tuple:
        if not attempt.verifies():
            return _legacy_report(PublishDryRunDecisionKind.QUARANTINE_BAD_SIGNATURE, False, True, "bad publish dry-run signature", attempts=attempt_tuple, components=components)
        if not attempt.live(now):
            return _legacy_report(PublishDryRunDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, False, True, "publish dry-run expired or future", attempts=attempt_tuple, components=components)
        if attempt.attempt_digest in seen:
            return _legacy_report(PublishDryRunDecisionKind.QUARANTINE_REPLAY, False, True, "publish dry-run replay", attempts=attempt_tuple, components=components)
        if attempt.sequence <= previous_highest_sequence:
            return _legacy_report(PublishDryRunDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, True, "publish dry-run sequence rollback", attempts=attempt_tuple, components=components)
        if previous_highest_sequence >= 0 and attempt.previous_attempt_digest != previous_attempt_digest:
            return _legacy_report(PublishDryRunDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, True, "publish dry-run previous digest mismatch", attempts=attempt_tuple, components=components)
        prior = core_by_seq.setdefault(attempt.sequence, attempt.attempt_core_digest)
        if prior != attempt.attempt_core_digest:
            return _legacy_report(PublishDryRunDecisionKind.QUARANTINE_SEQUENCE_FORK, False, True, "publish dry-run same-sequence fork", attempts=attempt_tuple, components=components)
        if attempt.channel is not expected_channel:
            return _legacy_report(PublishDryRunDecisionKind.QUARANTINE_CHANNEL_DRIFT, False, True, "publish dry-run channel drift", attempts=attempt_tuple, components=components)
        if attempt.profile_id != expected_profile_id:
            return _legacy_report(PublishDryRunDecisionKind.QUARANTINE_PROFILE_DRIFT, False, True, "publish dry-run profile drift", attempts=attempt_tuple, components=components)
        if attempt.service_name != expected_service_name:
            return _legacy_report(PublishDryRunDecisionKind.QUARANTINE_SERVICE_DRIFT, False, True, "publish dry-run service drift", attempts=attempt_tuple, components=components)
        if attempt.scope_digest != expected_scope_digest:
            return _legacy_report(PublishDryRunDecisionKind.QUARANTINE_SCOPE_DRIFT, False, True, "publish dry-run scope drift", attempts=attempt_tuple, components=components)
        if attempt.request_digest != expected_request_digest:
            return _legacy_report(PublishDryRunDecisionKind.QUARANTINE_REQUEST_DRIFT, False, True, "publish dry-run request drift", attempts=attempt_tuple, components=components)
        if attempt.subject_digest != expected_subject_digest:
            return _legacy_report(PublishDryRunDecisionKind.QUARANTINE_SUBJECT_DRIFT, False, True, "publish dry-run subject drift", attempts=attempt_tuple, components=components)
        if attempt.public_payload_digest != expected_public_payload_digest:
            return _legacy_report(PublishDryRunDecisionKind.QUARANTINE_PAYLOAD_DRIFT, False, True, "publish dry-run payload drift", attempts=attempt_tuple, components=components)
        if attempt.bridge_shadow_digest != _component_digest(bridge_shadow) or attempt.audit_quorum_digest != _component_digest(audit_quorum) or attempt.redress_gc_digest != _component_digest(redress_gc):
            return _legacy_report(PublishDryRunDecisionKind.QUARANTINE_COMPONENT_DIGEST_DRIFT, False, True, "publish dry-run component digest drift", attempts=attempt_tuple, components=components)
    if len({item.family_id for item in attempt_tuple}) < min_family_diversity:
        return _legacy_report(PublishDryRunDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, "publish dry-run family diversity too low", attempts=attempt_tuple, components=components)
    if len({item.path_family for item in attempt_tuple}) < min_path_diversity:
        return _legacy_report(PublishDryRunDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, "publish dry-run path diversity too low", attempts=attempt_tuple, components=components)
    selected = max(attempt_tuple, key=lambda item: (item.sequence, item.attempt_digest))
    watch = any(_component_watch(component) for component, *_ in component_checks)
    return _legacy_report(PublishDryRunDecisionKind.ACCEPT_WITH_WATCH if watch else PublishDryRunDecisionKind.ACCEPT_DRY_RUN, True, watch, "publish dry-run is component-bound, exact-scope, and no-network", attempts=attempt_tuple, selected=selected, components=components)
