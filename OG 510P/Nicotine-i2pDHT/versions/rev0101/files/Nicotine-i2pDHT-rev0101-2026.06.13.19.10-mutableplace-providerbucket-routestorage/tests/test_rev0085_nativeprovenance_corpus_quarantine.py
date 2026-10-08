from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from i2p_dht_lab.ids import sha256
from i2p_dht_lab.nativeaudit import audit_native_leaf_source
from i2p_dht_lab.nativebudget import NativeBudgetDecisionKind, NativeBudgetDemand, NativeOptimizationBudget, assess_native_budget
from i2p_dht_lab.nativecorpus import NativeCorpusDecisionKind, assess_native_corpus, default_native_corpus_vectors
from i2p_dht_lab.nativehotpaths import expected_native_symbols, native_xor_source_path, xor_compare_reference
from i2p_dht_lab.nativeprovenance import NativeBuildStamp, NativeProvenanceDecisionKind, assess_native_provenance
from i2p_dht_lab.nativeprovenancefold import audit_native_provenance_fold
from i2p_dht_lab.nativequarantine import NativeQuarantineDecisionKind, NativeQuarantineMarker, assess_native_quarantine
from i2p_dht_lab.parserhold import ParserHoldProposal, assess_parser_hold
from i2p_dht_lab.sanitizerplan import NativeSanitizerPlan, assess_sanitizer_plan

ROOT = Path(__file__).resolve().parents[1]


def _source_audit():
    source = native_xor_source_path(ROOT).read_text(encoding="utf-8")
    return audit_native_leaf_source(source, required_symbols=expected_native_symbols())


def _parser_report():
    proposal = ParserHoldProposal(
        component="wire_parseguard",
        parser_name="canonical_bdecode",
        profile="portable-default",
        sequence=1,
        previous_digest=b"",
        python_parser_digest=sha256(b"python-parseguard-v1"),
        proposed_native_source_digest=b"",
        max_input_len=4096,
        untrusted_bytes=True,
        native_requested=False,
        native_required=False,
        request_id="rev0085-parser",
        family_id="family-a",
        path_family_id="path-a",
    )
    return assess_parser_hold(proposal, expected_python_parser_digest=proposal.python_parser_digest, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b"), min_families=2, min_path_families=2)


def _sanitizer_report(audit=None):
    audit = audit or _source_audit()
    plan = NativeSanitizerPlan(
        component="xor_distance",
        profile="dev-asan-ubsan",
        sequence=1,
        previous_digest=b"",
        source_audit_digest=audit.report_digest,
        compiler_flags=("-shared", "-fPIC", "-std=c11", "-O1", "-Wall", "-Wextra", "-Werror", "-fsanitize=address,undefined", "-fno-omit-frame-pointer"),
        audited_components=("xor_distance",),
        native_enabled=True,
        release_profile=False,
        request_id="rev0085-san",
        family_id="builder-a",
        path_family_id="path-a",
    )
    return assess_sanitizer_plan(plan, audit), plan


def _native_budget_report():
    budget = NativeOptimizationBudget("portable-default", ("xor_distance",), 1, 2, 1000, 32)
    demand = NativeBudgetDemand("xor_distance", "xor_compare", "rev0085-budget", 1, 100, 32, True, True)
    report = assess_native_budget(budget, demand, _parser_report(), _sanitizer_report()[0])
    assert report.decision_kind is NativeBudgetDecisionKind.ACCEPT_NATIVE_BUDGET
    return report


def _build_stamp(seq: int = 1, prev: bytes = b"") -> NativeBuildStamp:
    audit = _source_audit()
    san_report, san_plan = _sanitizer_report(audit)
    budget = _native_budget_report()
    return NativeBuildStamp(
        component="xor_distance",
        profile="portable-default",
        sequence=seq,
        previous_digest=prev,
        compiler_id="gcc",
        compiler_version="gcc-test-version",
        source_audit_digest=audit.report_digest,
        sanitizer_report_digest=san_report.report_digest,
        native_budget_report_digest=budget.report_digest,
        source_digest=audit.source_digest,
        flags_digest=san_plan.flags_digest,
        object_digest=sha256(b"rev0085-object"),
        artifact_digest=sha256(b"rev0085-artifact"),
        builder_id="builder-a",
        family_id="family-a",
        path_family_id="path-a",
    )


def _accepted_provenance():
    audit = _source_audit()
    san_report, _ = _sanitizer_report(audit)
    budget = _native_budget_report()
    stamp = _build_stamp()
    report = assess_native_provenance(audit, san_report, budget, stamp, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b"), min_families=2, min_path_families=2)
    assert report.decision_kind is NativeProvenanceDecisionKind.ACCEPT_REPRODUCIBLE_PROVENANCE
    return report, stamp, budget


def _correct_native(pivot: bytes, left: bytes, right: bytes) -> int:
    return xor_compare_reference(pivot, left, right)


def _bad_native(pivot: bytes, left: bytes, right: bytes) -> int:
    return -xor_compare_reference(pivot, left, right)


def test_native_provenance_accepts_reproducible_build() -> None:
    report, _, _ = _accepted_provenance()
    assert report.accepted
    assert report.native_artifact_allowed
    assert not report.quarantine


def test_native_provenance_rejects_digest_drift_and_single_builder() -> None:
    audit = _source_audit()
    san_report, san_plan = _sanitizer_report(audit)
    budget = _native_budget_report()
    stamp = _build_stamp()
    source_drift = replace(stamp, source_digest=sha256(b"wrong-source"))
    assert assess_native_provenance(audit, san_report, budget, source_drift, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b")).decision_kind is NativeProvenanceDecisionKind.QUARANTINE_SOURCE_DIGEST_DRIFT
    flags_drift = replace(stamp, flags_digest=sha256(b"wrong-flags"))
    assert assess_native_provenance(audit, san_report, budget, flags_drift, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b")).decision_kind is NativeProvenanceDecisionKind.QUARANTINE_FLAGS_DIGEST_DRIFT
    object_drift = replace(stamp, object_digest=stamp.source_digest)
    assert assess_native_provenance(audit, san_report, budget, object_drift, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b")).decision_kind is NativeProvenanceDecisionKind.QUARANTINE_OBJECT_DIGEST_DRIFT
    single = assess_native_provenance(audit, san_report, budget, stamp, observed_families=("family-a",), observed_path_families=("path-a",), min_families=2, min_path_families=2)
    assert single.decision_kind is NativeProvenanceDecisionKind.HOLD_SINGLE_BUILDER


def test_native_provenance_detects_replay_fork_and_previous_link() -> None:
    audit = _source_audit()
    san_report, _ = _sanitizer_report(audit)
    budget = _native_budget_report()
    stamp = _build_stamp()
    assert assess_native_provenance(audit, san_report, budget, stamp, prior_stamp_digests=(stamp.stamp_digest,), observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b")).decision_kind is NativeProvenanceDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK
    fork = replace(stamp, note="fork")
    assert assess_native_provenance(audit, san_report, budget, fork, previous=stamp, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b")).decision_kind is NativeProvenanceDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK
    bad_link = _build_stamp(seq=2, prev=sha256(b"bad-prev"))
    assert assess_native_provenance(audit, san_report, budget, bad_link, previous=stamp, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b")).decision_kind is NativeProvenanceDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH


def test_native_corpus_accepts_python_oracle_matching_native() -> None:
    provenance, _, _ = _accepted_provenance()
    report = assess_native_corpus(provenance, native_compare=_correct_native)
    assert report.decision_kind is NativeCorpusDecisionKind.ACCEPT_DIFFERENTIAL_CORPUS
    assert report.native_allowed
    assert len(report.observations) >= 6


def test_native_corpus_rejects_mismatch_low_diversity_and_unbounded_input() -> None:
    provenance, _, _ = _accepted_provenance()
    mismatch = assess_native_corpus(provenance, native_compare=_bad_native)
    assert mismatch.decision_kind is NativeCorpusDecisionKind.QUARANTINE_NATIVE_MISMATCH
    low = tuple(replace(v, bucket="same") for v in default_native_corpus_vectors())
    assert assess_native_corpus(provenance, low, native_compare=_correct_native).decision_kind is NativeCorpusDecisionKind.QUARANTINE_LOW_DIVERSITY
    too_big = tuple(default_native_corpus_vectors()) + (replace(default_native_corpus_vectors()[0], pivot=b"x" * 33, left=b"y" * 33, right=b"z" * 33, label="too-big", bucket="too-big"),)
    assert assess_native_corpus(provenance, too_big, native_compare=_correct_native).decision_kind is NativeCorpusDecisionKind.QUARANTINE_UNBOUNDED_INPUT


def test_native_quarantine_records_bad_native_and_preserves_fallback() -> None:
    provenance, stamp, budget = _accepted_provenance()
    corpus = assess_native_corpus(provenance, native_compare=_bad_native)
    marker = NativeQuarantineMarker(
        component="xor_distance",
        profile="portable-default",
        sequence=1,
        previous_digest=b"",
        artifact_digest=stamp.artifact_digest,
        source_digest=stamp.source_digest,
        provenance_digest=provenance.report_digest,
        corpus_digest=corpus.report_digest,
        budget_digest=budget.report_digest,
        reason="native-corpus-mismatch",
        fallback_digest=sha256(b"python-xor-reference"),
        family_id="family-a",
        path_family_id="path-a",
    )
    report = assess_native_quarantine(provenance, corpus, budget, marker, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b"))
    assert report.decision_kind is NativeQuarantineDecisionKind.RECORD_NATIVE_QUARANTINE
    assert report.fallback_only
    assert not report.native_allowed

    drift = replace(marker, corpus_digest=sha256(b"wrong-corpus"))
    assert assess_native_quarantine(provenance, corpus, budget, drift, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b")).decision_kind is NativeQuarantineDecisionKind.QUARANTINE_MARKER_DIGEST_DRIFT
    missing = assess_native_quarantine(provenance, corpus, budget, None)
    assert missing.decision_kind is NativeQuarantineDecisionKind.HOLD_MISSING_QUARANTINE_MARKER


def test_native_quarantine_detects_marker_fork_and_allows_healthy_no_marker() -> None:
    provenance, stamp, budget = _accepted_provenance()
    corpus = assess_native_corpus(provenance, native_compare=_correct_native)
    healthy = assess_native_quarantine(provenance, corpus, budget, None)
    assert healthy.decision_kind is NativeQuarantineDecisionKind.ACCEPT_NATIVE_NO_QUARANTINE

    marker = NativeQuarantineMarker("xor_distance", "portable-default", 1, b"", stamp.artifact_digest, stamp.source_digest, provenance.report_digest, corpus.report_digest, budget.report_digest, "retired-by-operator", sha256(b"fallback"), "family-a", "path-a")
    fork = replace(marker, note="fork")
    assert assess_native_quarantine(provenance, corpus, budget, fork, previous=marker, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b")).decision_kind is NativeQuarantineDecisionKind.QUARANTINE_MARKER_FORK


def test_nativeprovenancefold_happy_path() -> None:
    report = audit_native_provenance_fold(ROOT, revision="rev0085", artifact_stem=ROOT.name)
    assert report.status == "pass"
    assert report.predecessor_status == "pass"
    assert report.foldmap_status == "pass"
    assert report.foldregistry_status == "pass"
    assert report.surface_ledger_status == "pass"
