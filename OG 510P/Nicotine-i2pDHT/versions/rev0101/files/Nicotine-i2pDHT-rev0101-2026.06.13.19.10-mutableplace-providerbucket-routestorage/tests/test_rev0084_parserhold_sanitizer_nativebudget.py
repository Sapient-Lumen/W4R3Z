from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from i2p_dht_lab.ids import sha256
from i2p_dht_lab.nativeaudit import NativeSourceAuditDecisionKind, audit_native_leaf_source
from i2p_dht_lab.nativebudget import NativeBudgetDecisionKind, NativeBudgetDemand, NativeOptimizationBudget, assess_native_budget
from i2p_dht_lab.nativebudgetfold import audit_native_budget_fold
from i2p_dht_lab.nativehotpaths import expected_native_symbols, native_xor_source_path
from i2p_dht_lab.parserhold import ParserHoldDecisionKind, ParserHoldProposal, assess_parser_hold
from i2p_dht_lab.sanitizerplan import NativeSanitizerPlan, SanitizerPlanDecisionKind, assess_sanitizer_plan

ROOT = Path(__file__).resolve().parents[1]


def _source_audit():
    source = native_xor_source_path(ROOT).read_text(encoding="utf-8")
    audit = audit_native_leaf_source(source, required_symbols=expected_native_symbols())
    assert audit.decision_kind is NativeSourceAuditDecisionKind.ACCEPT_LEAF_SOURCE
    return audit


def _parser_proposal() -> ParserHoldProposal:
    return ParserHoldProposal(
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
        request_id="parser-hold-1",
        family_id="family-a",
        path_family_id="path-a",
    )


def _accepted_parser_hold():
    proposal = _parser_proposal()
    return assess_parser_hold(proposal, expected_python_parser_digest=proposal.python_parser_digest, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b"), min_families=2, min_path_families=2)


def _sanitizer_plan(source_audit, *, release: bool = False, native_enabled: bool = True) -> NativeSanitizerPlan:
    flags = ("-shared", "-fPIC", "-std=c11", "-O1", "-Wall", "-Wextra", "-Werror", "-fsanitize=address,undefined", "-fno-omit-frame-pointer")
    if release:
        flags = ("-shared", "-fPIC", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror")
    return NativeSanitizerPlan(
        component="xor_distance",
        profile="dev-asan-ubsan" if not release else "release-portable",
        sequence=1,
        previous_digest=b"",
        source_audit_digest=source_audit.report_digest,
        compiler_flags=flags,
        audited_components=("xor_distance",),
        native_enabled=native_enabled,
        release_profile=release,
        request_id="san-plan-1",
        family_id="builder-a",
        path_family_id="path-a",
    )


def _accepted_sanitizer_report():
    audit = _source_audit()
    plan = _sanitizer_plan(audit)
    return assess_sanitizer_plan(plan, audit)


def test_parser_hold_keeps_untrusted_parsing_python_owned() -> None:
    proposal = _parser_proposal()
    report = assess_parser_hold(proposal, expected_python_parser_digest=proposal.python_parser_digest, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b"), min_families=2, min_path_families=2)
    assert report.decision_kind is ParserHoldDecisionKind.ACCEPT_PYTHON_PARSER_HOLD
    assert report.python_parser_must_own

    native_parser = replace(proposal, native_requested=True, proposed_native_source_digest=sha256(b"native-parser"), sequence=2, previous_digest=proposal.proposal_digest)
    native_report = assess_parser_hold(native_parser, previous=proposal, expected_python_parser_digest=proposal.python_parser_digest, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b"), min_families=2, min_path_families=2)
    assert native_report.decision_kind is ParserHoldDecisionKind.QUARANTINE_UNTRUSTED_NATIVE_PARSER

    digest_drift = replace(proposal, python_parser_digest=sha256(b"wrong-python-parser"))
    assert assess_parser_hold(digest_drift, expected_python_parser_digest=proposal.python_parser_digest).decision_kind is ParserHoldDecisionKind.QUARANTINE_PARSER_DIGEST_DRIFT


def test_parser_hold_detects_replay_fork_and_previous_link() -> None:
    proposal = _parser_proposal()
    assert assess_parser_hold(proposal, prior_proposal_digests=(proposal.proposal_digest,)).decision_kind is ParserHoldDecisionKind.QUARANTINE_REQUEST_REPLAY
    fork = replace(proposal, note="fork")
    assert assess_parser_hold(fork, previous=proposal).decision_kind is ParserHoldDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK
    bad_link = replace(proposal, sequence=2, previous_digest=sha256(b"bad-link"))
    assert assess_parser_hold(bad_link, previous=proposal).decision_kind is ParserHoldDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH
    low = assess_parser_hold(proposal, observed_families=("one",), observed_path_families=("one",), min_families=2, min_path_families=2)
    assert low.decision_kind is ParserHoldDecisionKind.QUARANTINE_LOW_DIVERSITY


def test_sanitizer_plan_requires_audited_leaf_and_dev_sanitizers() -> None:
    audit = _source_audit()
    plan = _sanitizer_plan(audit)
    report = assess_sanitizer_plan(plan, audit)
    assert report.decision_kind is SanitizerPlanDecisionKind.ACCEPT_DEV_SANITIZER_PLAN
    assert report.accepted

    missing_san = replace(plan, compiler_flags=("-shared", "-fPIC", "-std=c11", "-O1", "-Wall"))
    assert assess_sanitizer_plan(missing_san, audit).decision_kind is SanitizerPlanDecisionKind.QUARANTINE_MISSING_SANITIZER

    forbidden = replace(plan, compiler_flags=plan.compiler_flags + ("-Ofast",), sequence=2, previous_digest=plan.plan_digest)
    assert assess_sanitizer_plan(forbidden, audit, previous=plan).decision_kind is SanitizerPlanDecisionKind.QUARANTINE_FORBIDDEN_FLAG

    unaudited = replace(plan, component="new_parser", audited_components=("xor_distance",))
    assert assess_sanitizer_plan(unaudited, audit).decision_kind is SanitizerPlanDecisionKind.QUARANTINE_UNAUDITED_COMPONENT

    release_hold = _sanitizer_plan(audit, release=True, native_enabled=True)
    assert assess_sanitizer_plan(release_hold, audit).decision_kind is SanitizerPlanDecisionKind.HOLD_RELEASE_NATIVE_NEEDS_PRIOR_DEV_SANITIZER
    release_ok = assess_sanitizer_plan(release_hold, audit, prior_dev_sanitizer_report=report)
    assert release_ok.decision_kind is SanitizerPlanDecisionKind.ACCEPT_RELEASE_NO_NATIVE_SANITIZER


def test_native_budget_admits_only_leaf_hotpaths_with_fallbacks() -> None:
    parser_report = _accepted_parser_hold()
    sanitizer_report = _accepted_sanitizer_report()
    budget = NativeOptimizationBudget("portable-default", ("xor_distance",), max_native_components=1, max_call_sites=2, max_estimated_calls=1000, max_input_len=32)
    demand = NativeBudgetDemand("xor_distance", "xor_compare", "budget-1", call_sites=1, estimated_calls=100, max_input_len=32, native_required=True, fallback_available=True)
    accepted = assess_native_budget(budget, demand, parser_report, sanitizer_report)
    assert accepted.decision_kind is NativeBudgetDecisionKind.ACCEPT_NATIVE_BUDGET

    fallback = assess_native_budget(budget, replace(demand, native_required=False), parser_report, sanitizer_report)
    assert fallback.decision_kind is NativeBudgetDecisionKind.ACCEPT_FALLBACK_ONLY

    missing_fallback = assess_native_budget(budget, replace(demand, fallback_available=False), parser_report, sanitizer_report)
    assert missing_fallback.decision_kind is NativeBudgetDecisionKind.QUARANTINE_MISSING_FALLBACK

    parser_touch = assess_native_budget(budget, replace(demand, touches_parser=True), parser_report, sanitizer_report)
    assert parser_touch.decision_kind is NativeBudgetDecisionKind.QUARANTINE_SEMANTIC_SURFACE

    too_large = assess_native_budget(budget, replace(demand, max_input_len=4096), parser_report, sanitizer_report)
    assert too_large.decision_kind is NativeBudgetDecisionKind.QUARANTINE_BUDGET_EXCEEDED

    unknown = assess_native_budget(budget, replace(demand, component="mutable_head"), parser_report, sanitizer_report)
    assert unknown.decision_kind is NativeBudgetDecisionKind.QUARANTINE_UNKNOWN_COMPONENT


def test_native_budget_rejects_bad_parser_or_sanitizer_reports() -> None:
    parser_report = _accepted_parser_hold()
    sanitizer_report = _accepted_sanitizer_report()
    budget = NativeOptimizationBudget("portable-default", ("xor_distance",), 1, 2, 1000, 32)
    demand = NativeBudgetDemand("xor_distance", "xor_compare", "budget-2", 1, 10, 32, True, True)

    bad_parser_proposal = replace(_parser_proposal(), native_requested=True)
    bad_parser = assess_parser_hold(bad_parser_proposal)
    assert assess_native_budget(budget, demand, bad_parser, sanitizer_report).decision_kind is NativeBudgetDecisionKind.QUARANTINE_PARSER_HOLD_NOT_ACCEPTED

    audit = _source_audit()
    missing_san = assess_sanitizer_plan(replace(_sanitizer_plan(audit), compiler_flags=("-shared", "-fPIC")), audit)
    assert assess_native_budget(budget, demand, parser_report, missing_san).decision_kind is NativeBudgetDecisionKind.QUARANTINE_SANITIZER_NOT_ACCEPTED


def test_nativebudgetfold_happy_path() -> None:
    report = audit_native_budget_fold(ROOT, revision="rev0084", artifact_stem=ROOT.name)
    assert report.status == "pass"
    assert report.predecessor_status == "pass"
    assert report.foldmap_status == "pass"
    assert report.foldregistry_status == "pass"
    assert report.surface_ledger_status == "pass"
