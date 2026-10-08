"""Join witness/audit/redress compaction lanes before public-edge forgetting.

rev0049 added witness compaction, audit compaction, redress GC, and scope-journal
restart memory as separate surfaces.  rev0050 makes the risk explicit: if those
lanes compact independently, hard-negative evidence can be split apart and then
forgotten.  This module joins the reports at exact scope/request/subject before
local memory may treat compaction as safe.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .auditcompact import AuditCompactReport
from .bencode import bencode
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .redressgc import RedressGcReport
from .scopejournal import ScopeJournalReport
from .witnesscompact import WitnessCompactReport

COMPACT_JOIN_DOMAIN = DOMAIN + b":compact-join-v1:"


class CompactJoinDecisionKind(str, Enum):
    ACCEPT_COMPACT_JOIN = "accept_compact_join"
    ACCEPT_WITH_WATCH = "accept_with_watch"
    HOLD_WITNESS_COMPACT = "hold_witness_compact"
    HOLD_AUDIT_COMPACT = "hold_audit_compact"
    HOLD_REDRESS_GC = "hold_redress_gc"
    HOLD_SCOPE_JOURNAL = "hold_scope_journal"
    HOLD_MISSING_LIVE_NEGATIVE = "hold_missing_live_negative"
    QUARANTINE_WITNESS_COMPACT = "quarantine_witness_compact"
    QUARANTINE_AUDIT_COMPACT = "quarantine_audit_compact"
    QUARANTINE_REDRESS_GC = "quarantine_redress_gc"
    QUARANTINE_SCOPE_JOURNAL = "quarantine_scope_journal"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_REQUEST_DRIFT = "quarantine_request_drift"
    QUARANTINE_SUBJECT_DRIFT = "quarantine_subject_drift"
    QUARANTINE_NEGATIVE_SPLIT = "quarantine_negative_split"
    QUARANTINE_COMPONENT_DIGEST_DROP = "quarantine_component_digest_drop"
    QUARANTINE_LOW_DIVERSITY_FOR_SOFT_ONLY = "quarantine_low_diversity_for_soft_only"


@dataclass(frozen=True)
class CompactJoinReport:
    decision_kind: CompactJoinDecisionKind
    accept: bool
    watch: bool
    reason: str
    scope_digest: bytes
    request_digest: bytes
    subject_digest: bytes
    component_digests: tuple[bytes, ...]
    retained_hard_digests: tuple[bytes, ...]
    missing_hard_digests: tuple[bytes, ...]
    family_count: int
    path_family_count: int
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _report(kind: CompactJoinDecisionKind, accept: bool, watch: bool, reason: str, *, scope_digest: bytes, request_digest: bytes, subject_digest: bytes, components: Iterable[bytes], retained_hard: Iterable[bytes] = (), missing_hard: Iterable[bytes] = (), family_count: int = 0, path_family_count: int = 0) -> CompactJoinReport:
    component_tuple = tuple(sorted(set(components)))
    retained_tuple = tuple(sorted(set(retained_hard)))
    missing_tuple = tuple(sorted(set(missing_hard)))
    digest = sha256(COMPACT_JOIN_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"reason": reason,
        b"scope": scope_digest,
        b"request": request_digest,
        b"subject": subject_digest,
        b"components": list(component_tuple),
        b"retained_hard": list(retained_tuple),
        b"missing_hard": list(missing_tuple),
        b"families": family_count,
        b"paths": path_family_count,
    }))
    return CompactJoinReport(kind, accept, watch, reason, scope_digest, request_digest, subject_digest, component_tuple, retained_tuple, missing_tuple, family_count, path_family_count, digest)


def assess_compact_join(
    *,
    witness_compact: WitnessCompactReport,
    audit_compact: AuditCompactReport,
    redress_gc: RedressGcReport,
    scope_journal: ScopeJournalReport,
    expected_scope_digest: bytes,
    expected_request_digest: bytes,
    expected_subject_digest: bytes,
    live_hard_negative_digests: Iterable[bytes] = (),
    required_component_digests: Iterable[bytes] = (),
    min_family_diversity: int = 1,
    min_path_diversity: int = 1,
) -> CompactJoinReport:
    components = (witness_compact.report_digest, audit_compact.report_digest, redress_gc.report_digest, scope_journal.report_digest)
    required = set(required_component_digests)
    if required and not required.issubset(set(scope_journal.entry_digests) | set(components)):
        return _report(CompactJoinDecisionKind.QUARANTINE_COMPONENT_DIGEST_DROP, False, True, "scope journal dropped required component digest", scope_digest=expected_scope_digest, request_digest=expected_request_digest, subject_digest=expected_subject_digest, components=components)
    for report, hold, quarantine, label in (
        (witness_compact, CompactJoinDecisionKind.HOLD_WITNESS_COMPACT, CompactJoinDecisionKind.QUARANTINE_WITNESS_COMPACT, "witness compact"),
        (audit_compact, CompactJoinDecisionKind.HOLD_AUDIT_COMPACT, CompactJoinDecisionKind.QUARANTINE_AUDIT_COMPACT, "audit compact"),
        (redress_gc, CompactJoinDecisionKind.HOLD_REDRESS_GC, CompactJoinDecisionKind.QUARANTINE_REDRESS_GC, "redress GC"),
        (scope_journal, CompactJoinDecisionKind.HOLD_SCOPE_JOURNAL, CompactJoinDecisionKind.QUARANTINE_SCOPE_JOURNAL, "scope journal"),
    ):
        if getattr(report, "quarantined", False):
            return _report(quarantine, False, True, f"{label} quarantined", scope_digest=expected_scope_digest, request_digest=expected_request_digest, subject_digest=expected_subject_digest, components=components)
        if not getattr(report, "accept", False):
            return _report(hold, False, bool(getattr(report, "watch", False)), f"{label} did not accept", scope_digest=expected_scope_digest, request_digest=expected_request_digest, subject_digest=expected_subject_digest, components=components)
    for report in (witness_compact, scope_journal):
        if getattr(report, "scope_digest", expected_scope_digest) != expected_scope_digest:
            return _report(CompactJoinDecisionKind.QUARANTINE_SCOPE_DRIFT, False, True, "scope drift across compaction lanes", scope_digest=expected_scope_digest, request_digest=expected_request_digest, subject_digest=expected_subject_digest, components=components)
        if getattr(report, "request_digest", expected_request_digest) != expected_request_digest:
            return _report(CompactJoinDecisionKind.QUARANTINE_REQUEST_DRIFT, False, True, "request drift across compaction lanes", scope_digest=expected_scope_digest, request_digest=expected_request_digest, subject_digest=expected_subject_digest, components=components)
    if getattr(scope_journal, "subject_digest", expected_subject_digest) != expected_subject_digest:
        return _report(CompactJoinDecisionKind.QUARANTINE_SUBJECT_DRIFT, False, True, "scope journal subject drift", scope_digest=expected_scope_digest, request_digest=expected_request_digest, subject_digest=expected_subject_digest, components=components)

    retained = (
        set(getattr(witness_compact, "retained_digests", ()))
        | set(getattr(audit_compact, "retained_digests", ()))
        | set(getattr(audit_compact, "refute_digests", ()))
        | set(getattr(audit_compact, "fork_evidence_digests", ()))
    )
    hard = set(live_hard_negative_digests)
    missing = hard - retained
    family_count = min(getattr(witness_compact, "family_count", 0), getattr(audit_compact, "family_count", 0) or getattr(witness_compact, "family_count", 0))
    path_count = min(getattr(witness_compact, "path_family_count", 0), getattr(audit_compact, "path_family_count", 0) or getattr(witness_compact, "path_family_count", 0))
    audit_has_negative = bool(getattr(audit_compact, "refute_digests", ())) or bool(getattr(audit_compact, "fork_evidence_digests", ())) or bool(getattr(audit_compact, "hard_count", 0))
    if missing and (getattr(redress_gc, "hard_negative_count", 0) or getattr(witness_compact, "hard_negative_count", 0) or audit_has_negative):
        return _report(CompactJoinDecisionKind.QUARANTINE_NEGATIVE_SPLIT, False, True, "live hard negative split across compaction lanes", scope_digest=expected_scope_digest, request_digest=expected_request_digest, subject_digest=expected_subject_digest, components=components, retained_hard=retained & hard, missing_hard=missing, family_count=family_count, path_family_count=path_count)
    if missing:
        return _report(CompactJoinDecisionKind.HOLD_MISSING_LIVE_NEGATIVE, False, True, "missing live hard negative evidence", scope_digest=expected_scope_digest, request_digest=expected_request_digest, subject_digest=expected_subject_digest, components=components, retained_hard=retained & hard, missing_hard=missing, family_count=family_count, path_family_count=path_count)
    if not hard and (family_count < min_family_diversity or path_count < min_path_diversity):
        return _report(CompactJoinDecisionKind.QUARANTINE_LOW_DIVERSITY_FOR_SOFT_ONLY, False, True, "soft-only compaction lacks diversity", scope_digest=expected_scope_digest, request_digest=expected_request_digest, subject_digest=expected_subject_digest, components=components, retained_hard=retained & hard, family_count=family_count, path_family_count=path_count)
    watch = any(bool(getattr(report, "watch", False)) for report in (witness_compact, audit_compact, redress_gc, scope_journal)) or bool(hard)
    return _report(CompactJoinDecisionKind.ACCEPT_WITH_WATCH if watch else CompactJoinDecisionKind.ACCEPT_COMPACT_JOIN, True, watch, "compaction lanes preserve hard evidence at exact scope", scope_digest=expected_scope_digest, request_digest=expected_request_digest, subject_digest=expected_subject_digest, components=components, retained_hard=retained & hard, family_count=family_count, path_family_count=path_count)
