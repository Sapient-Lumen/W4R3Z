"""rev0086 native selection boundary.

A native artifact is not selected because provenance/corpus/quarantine reports
look healthy in isolation.  Selection is its own exact-boundary marker carrying
component, operation, artifact, fallback, report digests, sequence memory, and
family/path diversity.  Python remains the oracle and fallback path.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .bencode import bencode
from .ids import DOMAIN, sha256
from .nativebudget import NativeBudgetReport
from .nativecorpus import NativeCorpusReport
from .nativeprovenance import NativeProvenanceReport
from .nativequarantine import NativeQuarantineReport

NATIVE_SELECTION_DOMAIN = DOMAIN + b":native-selection-v1:"


class NativeSelectionDecisionKind(str, Enum):
    ACCEPT_NATIVE_SELECTION = "accept_native_selection"
    ACCEPT_FALLBACK_SELECTION = "accept_fallback_selection"
    HOLD_CORPUS_OR_QUARANTINE_WATCH = "hold_corpus_or_quarantine_watch"
    QUARANTINE_PROVENANCE_NOT_ACCEPTED = "quarantine_provenance_not_accepted"
    QUARANTINE_CORPUS_NOT_ACCEPTED = "quarantine_corpus_not_accepted"
    QUARANTINE_BUDGET_NOT_ACCEPTED = "quarantine_budget_not_accepted"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_FALLBACK_MISSING = "quarantine_fallback_missing"
    QUARANTINE_REPLAY_OR_ROLLBACK = "quarantine_replay_or_rollback"
    QUARANTINE_SAME_SEQUENCE_FORK = "quarantine_same_sequence_fork"
    QUARANTINE_PREVIOUS_LINK_MISMATCH = "quarantine_previous_link_mismatch"
    QUARANTINE_LOW_DIVERSITY = "quarantine_low_diversity"


@dataclass(frozen=True)
class NativeSelectionIntent:
    component: str
    profile: str
    operation: str
    request_id: str
    sequence: int
    previous_digest: bytes
    artifact_digest: bytes
    source_digest: bytes
    fallback_digest: bytes
    provenance_digest: bytes
    corpus_digest: bytes
    quarantine_digest: bytes
    budget_digest: bytes
    allow_native: bool
    require_native: bool
    family_id: str
    path_family_id: str
    note: str = ""

    @property
    def intent_digest(self) -> bytes:
        return sha256(NATIVE_SELECTION_DOMAIN + b":intent:" + bencode({
            b"component": self.component,
            b"profile": self.profile,
            b"operation": self.operation,
            b"request": self.request_id,
            b"seq": self.sequence,
            b"prev": self.previous_digest,
            b"artifact": self.artifact_digest,
            b"source": self.source_digest,
            b"fallback": self.fallback_digest,
            b"provenance": self.provenance_digest,
            b"corpus": self.corpus_digest,
            b"quarantine": self.quarantine_digest,
            b"budget": self.budget_digest,
            b"allow_native": 1 if self.allow_native else 0,
            b"require_native": 1 if self.require_native else 0,
            b"family": self.family_id,
            b"path_family": self.path_family_id,
            b"note": self.note,
        }))


@dataclass(frozen=True)
class NativeSelectionReport:
    decision_kind: NativeSelectionDecisionKind
    accepted: bool
    native_selected: bool
    fallback_selected: bool
    watch: bool
    quarantine: bool
    obligations: tuple[str, ...]
    intent_digest: bytes
    provenance_digest: bytes
    corpus_digest: bytes
    quarantine_digest: bytes
    budget_digest: bytes
    artifact_digest: bytes
    source_digest: bytes
    fallback_digest: bytes
    family_count: int
    path_family_count: int

    @property
    def report_digest(self) -> bytes:
        return sha256(NATIVE_SELECTION_DOMAIN + b":report:" + bencode({
            b"decision": NativeSelectionDecisionKind(self.decision_kind).value,
            b"accepted": 1 if self.accepted else 0,
            b"native_selected": 1 if self.native_selected else 0,
            b"fallback_selected": 1 if self.fallback_selected else 0,
            b"watch": 1 if self.watch else 0,
            b"quarantine": 1 if self.quarantine else 0,
            b"obligations": list(self.obligations),
            b"intent": self.intent_digest,
            b"provenance": self.provenance_digest,
            b"corpus": self.corpus_digest,
            b"quarantine_digest": self.quarantine_digest,
            b"budget": self.budget_digest,
            b"artifact": self.artifact_digest,
            b"source": self.source_digest,
            b"fallback": self.fallback_digest,
            b"family_count": self.family_count,
            b"path_family_count": self.path_family_count,
        }))


def assess_native_selection(
    provenance: NativeProvenanceReport,
    corpus: NativeCorpusReport,
    quarantine_report: NativeQuarantineReport,
    budget: NativeBudgetReport,
    intent: NativeSelectionIntent,
    *,
    previous: NativeSelectionIntent | None = None,
    prior_intent_digests: tuple[bytes, ...] = (),
    observed_families: tuple[str, ...] = (),
    observed_path_families: tuple[str, ...] = (),
    min_families: int = 2,
    min_path_families: int = 2,
) -> NativeSelectionReport:
    families = set(observed_families or (intent.family_id,))
    path_families = set(observed_path_families or (intent.path_family_id,))

    def report(kind: NativeSelectionDecisionKind, accepted: bool, native: bool, fallback: bool, watch: bool, quarantine: bool, obligations: tuple[str, ...]) -> NativeSelectionReport:
        return NativeSelectionReport(
            kind, accepted, native, fallback, watch, quarantine, obligations,
            intent.intent_digest, provenance.report_digest, corpus.report_digest,
            quarantine_report.report_digest, budget.report_digest,
            intent.artifact_digest, intent.source_digest, intent.fallback_digest,
            len(families), len(path_families),
        )

    if intent.intent_digest in prior_intent_digests:
        return report(NativeSelectionDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, False, True, False, True, ("native-selection-intent-replay", "use-python-fallback"))
    if previous is not None:
        if intent.sequence < previous.sequence:
            return report(NativeSelectionDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, False, True, False, True, ("native-selection-rollback",))
        if intent.sequence == previous.sequence and intent.intent_digest != previous.intent_digest:
            return report(NativeSelectionDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK, False, False, True, False, True, ("native-selection-same-sequence-fork", "quarantine-artifact"))
        if intent.sequence > previous.sequence and intent.previous_digest != previous.intent_digest:
            return report(NativeSelectionDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH, False, False, True, False, True, ("native-selection-previous-link-mismatch", "do-not-load-native"))

    if len(families) < min_families or len(path_families) < min_path_families:
        return report(NativeSelectionDecisionKind.QUARANTINE_LOW_DIVERSITY, False, False, True, False, True, ("native-selection-low-diversity", "fallback-only"))
    if not intent.fallback_digest:
        return report(NativeSelectionDecisionKind.QUARANTINE_FALLBACK_MISSING, False, False, False, False, True, ("native-selection-needs-python-fallback",))
    if intent.provenance_digest != provenance.report_digest or intent.corpus_digest != corpus.report_digest or intent.quarantine_digest != quarantine_report.report_digest or intent.budget_digest != budget.report_digest:
        return report(NativeSelectionDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, True, False, True, ("native-selection-component-digest-drift", "recompute-selection-boundary"))
    if intent.artifact_digest != provenance.artifact_digest or intent.source_digest != provenance.source_digest:
        return report(NativeSelectionDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, True, False, True, ("native-selection-artifact-or-source-drift", "use-python-fallback"))
    if not budget.accepted:
        return report(NativeSelectionDecisionKind.QUARANTINE_BUDGET_NOT_ACCEPTED, False, False, True, False, True, ("native-budget-not-accepted", "do-not-select-native"))
    if not provenance.accepted or not provenance.native_artifact_allowed or provenance.quarantine:
        return report(NativeSelectionDecisionKind.QUARANTINE_PROVENANCE_NOT_ACCEPTED, False, False, True, False, True, ("provenance-not-accepted", "use-python-fallback"))
    if not corpus.accepted or corpus.quarantine:
        if corpus.watch or quarantine_report.watch:
            return report(NativeSelectionDecisionKind.HOLD_CORPUS_OR_QUARANTINE_WATCH, False, False, True, True, False, ("corpus-or-quarantine-watch", "keep-fallback-only"))
        return report(NativeSelectionDecisionKind.QUARANTINE_CORPUS_NOT_ACCEPTED, False, False, True, False, True, ("corpus-not-accepted", "quarantine-native-artifact"))

    if quarantine_report.fallback_only or quarantine_report.quarantine or not quarantine_report.native_allowed:
        return report(NativeSelectionDecisionKind.ACCEPT_FALLBACK_SELECTION, True, False, True, quarantine_report.watch, quarantine_report.quarantine, ("route-to-python-fallback", "preserve-native-quarantine-memory"))
    if not intent.allow_native:
        return report(NativeSelectionDecisionKind.ACCEPT_FALLBACK_SELECTION, True, False, True, False, False, ("operator-profile-disabled-native", "fallback-selected"))
    return report(NativeSelectionDecisionKind.ACCEPT_NATIVE_SELECTION, True, True, True, False, False, ("select-native-for-leaf-only", "python-fallback-still-bound", "dispatch-still-exact-boundary"))
