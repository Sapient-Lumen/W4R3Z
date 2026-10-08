"""rev0086 native promotion hold.

Promotion from fallback/quarantine back to native is intentionally harder than a
fresh healthy artifact.  The lane prevents a fixed-looking artifact from being
promoted if fallback journal or quarantine memory would be erased.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .bencode import bencode
from .fallbackjournal import FallbackJournalReport
from .ids import DOMAIN, sha256
from .nativecorpus import NativeCorpusReport
from .nativeselection import NativeSelectionReport
from .nativequarantine import NativeQuarantineReport

NATIVE_PROMOTION_DOMAIN = DOMAIN + b":native-promotion-v1:"


class NativePromotionDecisionKind(str, Enum):
    ACCEPT_PROMOTION_TO_NATIVE = "accept_promotion_to_native"
    ACCEPT_STAY_NATIVE = "accept_stay_native"
    HOLD_STAY_FALLBACK = "hold_stay_fallback"
    HOLD_PROMOTION_NEEDS_FRESH_CORPUS = "hold_promotion_needs_fresh_corpus"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_DROPPED_FALLBACK_OR_QUARANTINE_MEMORY = "quarantine_dropped_fallback_or_quarantine_memory"
    QUARANTINE_REPLAY_OR_ROLLBACK = "quarantine_replay_or_rollback"
    QUARANTINE_SAME_SEQUENCE_FORK = "quarantine_same_sequence_fork"
    QUARANTINE_PREVIOUS_LINK_MISMATCH = "quarantine_previous_link_mismatch"
    QUARANTINE_LOW_DIVERSITY = "quarantine_low_diversity"


@dataclass(frozen=True)
class NativePromotionIntent:
    component: str
    profile: str
    operation: str
    request_id: str
    sequence: int
    previous_digest: bytes
    selection_digest: bytes
    fallback_journal_digest: bytes
    quarantine_digest: bytes
    corpus_digest: bytes
    prior_quarantine_marker_digest: bytes
    prior_fallback_entry_digest: bytes
    preserve_quarantine_memory: bool
    preserve_fallback_memory: bool
    promote_native: bool
    family_id: str
    path_family_id: str
    note: str = ""

    @property
    def intent_digest(self) -> bytes:
        return sha256(NATIVE_PROMOTION_DOMAIN + b":intent:" + bencode({
            b"component": self.component,
            b"profile": self.profile,
            b"operation": self.operation,
            b"request": self.request_id,
            b"seq": self.sequence,
            b"prev": self.previous_digest,
            b"selection": self.selection_digest,
            b"fallback_journal": self.fallback_journal_digest,
            b"quarantine": self.quarantine_digest,
            b"corpus": self.corpus_digest,
            b"prior_quarantine_marker": self.prior_quarantine_marker_digest,
            b"prior_fallback_entry": self.prior_fallback_entry_digest,
            b"preserve_quarantine": 1 if self.preserve_quarantine_memory else 0,
            b"preserve_fallback": 1 if self.preserve_fallback_memory else 0,
            b"promote_native": 1 if self.promote_native else 0,
            b"family": self.family_id,
            b"path_family": self.path_family_id,
            b"note": self.note,
        }))


@dataclass(frozen=True)
class NativePromotionReport:
    decision_kind: NativePromotionDecisionKind
    accepted: bool
    native_active: bool
    fallback_active: bool
    watch: bool
    quarantine: bool
    obligations: tuple[str, ...]
    intent_digest: bytes
    selection_digest: bytes
    fallback_journal_digest: bytes
    quarantine_digest: bytes
    corpus_digest: bytes
    family_count: int
    path_family_count: int

    @property
    def report_digest(self) -> bytes:
        return sha256(NATIVE_PROMOTION_DOMAIN + b":report:" + bencode({
            b"decision": NativePromotionDecisionKind(self.decision_kind).value,
            b"accepted": 1 if self.accepted else 0,
            b"native_active": 1 if self.native_active else 0,
            b"fallback_active": 1 if self.fallback_active else 0,
            b"watch": 1 if self.watch else 0,
            b"quarantine": 1 if self.quarantine else 0,
            b"obligations": list(self.obligations),
            b"intent": self.intent_digest,
            b"selection": self.selection_digest,
            b"fallback_journal": self.fallback_journal_digest,
            b"quarantine_digest": self.quarantine_digest,
            b"corpus": self.corpus_digest,
            b"family_count": self.family_count,
            b"path_family_count": self.path_family_count,
        }))


def assess_native_promotion(
    selection: NativeSelectionReport,
    fallback_journal: FallbackJournalReport,
    quarantine_report: NativeQuarantineReport,
    corpus: NativeCorpusReport,
    intent: NativePromotionIntent,
    *,
    previous: NativePromotionIntent | None = None,
    prior_intent_digests: tuple[bytes, ...] = (),
    observed_families: tuple[str, ...] = (),
    observed_path_families: tuple[str, ...] = (),
    min_families: int = 2,
    min_path_families: int = 2,
) -> NativePromotionReport:
    families = set(observed_families or (intent.family_id,))
    path_families = set(observed_path_families or (intent.path_family_id,))

    def report(kind: NativePromotionDecisionKind, accepted: bool, native: bool, fallback: bool, watch: bool, quarantine: bool, obligations: tuple[str, ...]) -> NativePromotionReport:
        return NativePromotionReport(kind, accepted, native, fallback, watch, quarantine, obligations, intent.intent_digest, selection.report_digest, fallback_journal.report_digest, quarantine_report.report_digest, corpus.report_digest, len(families), len(path_families))

    if intent.intent_digest in prior_intent_digests:
        return report(NativePromotionDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, False, True, False, True, ("native-promotion-replay",))
    if previous is not None:
        if intent.sequence < previous.sequence:
            return report(NativePromotionDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, False, True, False, True, ("native-promotion-rollback",))
        if intent.sequence == previous.sequence and intent.intent_digest != previous.intent_digest:
            return report(NativePromotionDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK, False, False, True, False, True, ("native-promotion-fork",))
        if intent.sequence > previous.sequence and intent.previous_digest != previous.intent_digest:
            return report(NativePromotionDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH, False, False, True, False, True, ("native-promotion-previous-link-mismatch",))
    if len(families) < min_families or len(path_families) < min_path_families:
        return report(NativePromotionDecisionKind.QUARANTINE_LOW_DIVERSITY, False, False, True, False, True, ("native-promotion-low-diversity",))
    if intent.selection_digest != selection.report_digest or intent.fallback_journal_digest != fallback_journal.report_digest or intent.quarantine_digest != quarantine_report.report_digest or intent.corpus_digest != corpus.report_digest:
        return report(NativePromotionDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, True, False, True, ("native-promotion-component-digest-drift",))
    if (intent.prior_quarantine_marker_digest and not intent.preserve_quarantine_memory) or (intent.prior_fallback_entry_digest and not intent.preserve_fallback_memory):
        return report(NativePromotionDecisionKind.QUARANTINE_DROPPED_FALLBACK_OR_QUARANTINE_MEMORY, False, False, True, False, True, ("promotion-dropped-native-negative-memory", "preserve-quarantine-and-fallback-history"))
    if not intent.promote_native:
        return report(NativePromotionDecisionKind.HOLD_STAY_FALLBACK, True, False, True, True, False, ("operator-or-policy-keeps-fallback-active", "native-promotion-not-requested"))
    if not selection.accepted or not selection.native_selected:
        return report(NativePromotionDecisionKind.HOLD_STAY_FALLBACK, True, False, True, True, False, ("selection-is-not-native", "fallback-remains-active"))
    if not corpus.accepted or corpus.quarantine or corpus.watch:
        return report(NativePromotionDecisionKind.HOLD_PROMOTION_NEEDS_FRESH_CORPUS, False, False, True, True, False, ("fresh-differential-corpus-required-before-promotion",))
    if quarantine_report.quarantine or quarantine_report.fallback_only or not quarantine_report.native_allowed:
        return report(NativePromotionDecisionKind.HOLD_PROMOTION_NEEDS_FRESH_CORPUS, False, False, True, True, False, ("quarantine-still-active", "do-not-promote-native"))
    if fallback_journal.quarantine:
        return report(NativePromotionDecisionKind.QUARANTINE_DROPPED_FALLBACK_OR_QUARANTINE_MEMORY, False, False, True, False, True, ("fallback-journal-quarantined", "do-not-promote"))
    return report(NativePromotionDecisionKind.ACCEPT_PROMOTION_TO_NATIVE, True, True, True, False, False, ("promote-native-leaf-only", "retain-prior-fallback-quarantine-memory", "python-oracle-still-required"))
