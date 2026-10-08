from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path

from i2p_dht_lab.fallbackjournal import (
    FallbackJournalDecisionKind,
    FallbackJournalEntry,
    assess_fallback_journal,
)
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.nativepromotion import (
    NativePromotionDecisionKind,
    NativePromotionIntent,
    assess_native_promotion,
)
from i2p_dht_lab.nativeselection import (
    NativeSelectionDecisionKind,
    NativeSelectionIntent,
    assess_native_selection,
)
from i2p_dht_lab.nativeselectionfold import audit_native_selection_fold

ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class FakeProvenance:
    accepted: bool = True
    native_artifact_allowed: bool = True
    quarantine: bool = False
    artifact_digest: bytes = sha256(b"artifact-ok")
    source_digest: bytes = sha256(b"source-ok")
    report_digest: bytes = sha256(b"provenance-ok")


@dataclass(frozen=True)
class FakeCorpus:
    accepted: bool = True
    native_allowed: bool = True
    fallback_allowed: bool = True
    watch: bool = False
    quarantine: bool = False
    report_digest: bytes = sha256(b"corpus-ok")


@dataclass(frozen=True)
class FakeBudget:
    accepted: bool = True
    report_digest: bytes = sha256(b"budget-ok")


@dataclass(frozen=True)
class FakeQuarantine:
    accepted: bool = True
    native_allowed: bool = True
    fallback_only: bool = False
    watch: bool = False
    quarantine: bool = False
    report_digest: bytes = sha256(b"quarantine-ok")


def _intent(seq: int = 1, prev: bytes = b"", *, provenance=FakeProvenance(), corpus=FakeCorpus(), quarantine=FakeQuarantine(), budget=FakeBudget(), allow_native: bool = True, note: str = "") -> NativeSelectionIntent:
    return NativeSelectionIntent(
        component="xor_distance",
        profile="portable-default",
        operation="xor_compare",
        request_id="rev0086-select",
        sequence=seq,
        previous_digest=prev,
        artifact_digest=provenance.artifact_digest,
        source_digest=provenance.source_digest,
        fallback_digest=sha256(b"python-xor-reference"),
        provenance_digest=provenance.report_digest,
        corpus_digest=corpus.report_digest,
        quarantine_digest=quarantine.report_digest,
        budget_digest=budget.report_digest,
        allow_native=allow_native,
        require_native=False,
        family_id="family-a",
        path_family_id="path-a",
        note=note,
    )


def _select(*, provenance=FakeProvenance(), corpus=FakeCorpus(), quarantine=FakeQuarantine(), budget=FakeBudget(), intent: NativeSelectionIntent | None = None):
    intent = intent or _intent(provenance=provenance, corpus=corpus, quarantine=quarantine, budget=budget)
    return assess_native_selection(provenance, corpus, quarantine, budget, intent, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b"), min_families=2, min_path_families=2)


def _fallback_entry(selection, seq: int = 1, prev: bytes = b"", note: str = "") -> FallbackJournalEntry:
    return FallbackJournalEntry(
        component="xor_distance",
        profile="portable-default",
        operation="xor_compare",
        request_id="rev0086-select",
        sequence=seq,
        previous_digest=prev,
        selection_digest=selection.report_digest,
        quarantine_digest=selection.quarantine_digest,
        corpus_digest=selection.corpus_digest,
        fallback_digest=selection.fallback_digest,
        reason="fallback-selected",
        family_id="family-a",
        path_family_id="path-a",
        note=note,
    )


def _fallback_report(selection, entry=None):
    return assess_fallback_journal(selection, entry, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b"), min_families=2, min_path_families=2)


def _promotion_intent(selection, fallback_report, quarantine=FakeQuarantine(), corpus=FakeCorpus(), seq: int = 1, prev: bytes = b"", promote: bool = True, preserve: bool = True) -> NativePromotionIntent:
    return NativePromotionIntent(
        component="xor_distance",
        profile="portable-default",
        operation="xor_compare",
        request_id="rev0086-select",
        sequence=seq,
        previous_digest=prev,
        selection_digest=selection.report_digest,
        fallback_journal_digest=fallback_report.report_digest,
        quarantine_digest=quarantine.report_digest,
        corpus_digest=corpus.report_digest,
        prior_quarantine_marker_digest=sha256(b"old-quarantine"),
        prior_fallback_entry_digest=sha256(b"old-fallback"),
        preserve_quarantine_memory=preserve,
        preserve_fallback_memory=preserve,
        promote_native=promote,
        family_id="family-a",
        path_family_id="path-a",
    )


def test_native_selection_accepts_only_after_reports_bind() -> None:
    selection = _select()
    assert selection.decision_kind is NativeSelectionDecisionKind.ACCEPT_NATIVE_SELECTION
    assert selection.native_selected
    assert selection.fallback_selected

    no_fallback = replace(_intent(), fallback_digest=b"")
    assert _select(intent=no_fallback).decision_kind is NativeSelectionDecisionKind.QUARANTINE_FALLBACK_MISSING

    drift = replace(_intent(), corpus_digest=sha256(b"wrong-corpus"))
    assert _select(intent=drift).decision_kind is NativeSelectionDecisionKind.QUARANTINE_DIGEST_DRIFT


def test_native_selection_detects_replay_fork_previous_link_and_low_diversity() -> None:
    first = _intent()
    assert assess_native_selection(FakeProvenance(), FakeCorpus(), FakeQuarantine(), FakeBudget(), first, prior_intent_digests=(first.intent_digest,), observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b")).decision_kind is NativeSelectionDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK
    fork = replace(first, note="fork")
    assert assess_native_selection(FakeProvenance(), FakeCorpus(), FakeQuarantine(), FakeBudget(), fork, previous=first, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b")).decision_kind is NativeSelectionDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK
    bad_link = _intent(seq=2, prev=sha256(b"wrong-prev"))
    assert assess_native_selection(FakeProvenance(), FakeCorpus(), FakeQuarantine(), FakeBudget(), bad_link, previous=first, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b")).decision_kind is NativeSelectionDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH
    low = assess_native_selection(FakeProvenance(), FakeCorpus(), FakeQuarantine(), FakeBudget(), first, observed_families=("family-a",), observed_path_families=("path-a",), min_families=2, min_path_families=2)
    assert low.decision_kind is NativeSelectionDecisionKind.QUARANTINE_LOW_DIVERSITY


def test_fallback_selection_requires_restart_journal_memory() -> None:
    quarantine = FakeQuarantine(native_allowed=False, fallback_only=True, quarantine=True, report_digest=sha256(b"quarantined"))
    selection = _select(quarantine=quarantine, intent=_intent(quarantine=quarantine))
    assert selection.decision_kind is NativeSelectionDecisionKind.ACCEPT_FALLBACK_SELECTION
    assert assess_fallback_journal(selection).decision_kind is FallbackJournalDecisionKind.HOLD_MISSING_FALLBACK_ENTRY
    entry = _fallback_entry(selection)
    report = _fallback_report(selection, entry)
    assert report.decision_kind is FallbackJournalDecisionKind.RECORD_FALLBACK_ENTRY
    assert report.fallback_active

    drift = replace(entry, corpus_digest=sha256(b"wrong-corpus"))
    assert _fallback_report(selection, drift).decision_kind is FallbackJournalDecisionKind.QUARANTINE_DIGEST_DRIFT


def test_fallback_journal_detects_replay_fork_and_previous_link() -> None:
    quarantine = FakeQuarantine(native_allowed=False, fallback_only=True, quarantine=True, report_digest=sha256(b"quarantined"))
    selection = _select(quarantine=quarantine, intent=_intent(quarantine=quarantine))
    entry = _fallback_entry(selection)
    assert assess_fallback_journal(selection, entry, prior_entry_digests=(entry.entry_digest,), observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b")).decision_kind is FallbackJournalDecisionKind.QUARANTINE_ENTRY_REPLAY_OR_ROLLBACK
    fork = replace(entry, note="fork")
    assert assess_fallback_journal(selection, fork, previous=entry, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b")).decision_kind is FallbackJournalDecisionKind.QUARANTINE_ENTRY_FORK
    bad_link = _fallback_entry(selection, seq=2, prev=sha256(b"wrong-prev"))
    assert assess_fallback_journal(selection, bad_link, previous=entry, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b")).decision_kind is FallbackJournalDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH


def test_native_promotion_requires_memory_carry_and_fresh_native_selection() -> None:
    selection = _select()
    fallback = _fallback_report(selection, None)
    intent = _promotion_intent(selection, fallback)
    report = assess_native_promotion(selection, fallback, FakeQuarantine(), FakeCorpus(), intent, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b"), min_families=2, min_path_families=2)
    assert report.decision_kind is NativePromotionDecisionKind.ACCEPT_PROMOTION_TO_NATIVE
    assert report.native_active

    dropped = _promotion_intent(selection, fallback, preserve=False)
    assert assess_native_promotion(selection, fallback, FakeQuarantine(), FakeCorpus(), dropped, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b")).decision_kind is NativePromotionDecisionKind.QUARANTINE_DROPPED_FALLBACK_OR_QUARANTINE_MEMORY

    corpus_watch = FakeCorpus(watch=True, accepted=False, quarantine=False, report_digest=sha256(b"watch-corpus"))
    selection2 = _select(corpus=corpus_watch, intent=_intent(corpus=corpus_watch))
    fallback2 = _fallback_report(selection2, _fallback_entry(selection2))
    intent2 = _promotion_intent(selection2, fallback2, corpus=corpus_watch)
    assert assess_native_promotion(selection2, fallback2, FakeQuarantine(), corpus_watch, intent2, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b")).decision_kind in (NativePromotionDecisionKind.HOLD_STAY_FALLBACK, NativePromotionDecisionKind.HOLD_PROMOTION_NEEDS_FRESH_CORPUS)


def test_native_promotion_detects_replay_fork_previous_link_and_digest_drift() -> None:
    selection = _select()
    fallback = _fallback_report(selection, None)
    intent = _promotion_intent(selection, fallback)
    assert assess_native_promotion(selection, fallback, FakeQuarantine(), FakeCorpus(), intent, prior_intent_digests=(intent.intent_digest,), observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b")).decision_kind is NativePromotionDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK
    fork = replace(intent, note="fork")
    assert assess_native_promotion(selection, fallback, FakeQuarantine(), FakeCorpus(), fork, previous=intent, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b")).decision_kind is NativePromotionDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK
    bad_link = _promotion_intent(selection, fallback, seq=2, prev=sha256(b"bad-prev"))
    assert assess_native_promotion(selection, fallback, FakeQuarantine(), FakeCorpus(), bad_link, previous=intent, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b")).decision_kind is NativePromotionDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH
    drift = replace(intent, selection_digest=sha256(b"wrong-selection"))
    assert assess_native_promotion(selection, fallback, FakeQuarantine(), FakeCorpus(), drift, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b")).decision_kind is NativePromotionDecisionKind.QUARANTINE_DIGEST_DRIFT


def test_nativeselectionfold_happy_path() -> None:
    report = audit_native_selection_fold(ROOT, revision="rev0086", artifact_stem=ROOT.name)
    assert report.status == "pass"
    assert report.predecessor_status == "pass"
    assert report.foldmap_status == "pass"
    assert report.foldregistry_status == "pass"
    assert report.surface_ledger_status == "pass"
