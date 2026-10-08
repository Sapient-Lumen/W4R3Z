from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path

from i2p_dht_lab.ids import sha256
from i2p_dht_lab.loaderseal import NativeLoaderSealCapsule, NativeLoaderSealDecisionKind, assess_native_loader_seal
from i2p_dht_lab.nativehandoff import NativeHandoffCapsule, NativeHandoffDecisionKind, assess_native_handoff
from i2p_dht_lab.nativehandofffold import audit_native_handoff_fold
from i2p_dht_lab.nativefoldspine import audit_native_fold_spine
from i2p_dht_lab.relaunchgate import NativeRelaunchGateDecisionKind, NativeRelaunchGatePlan, assess_native_relaunch_gate

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT.name

ART = sha256(b"rev0090-artifact")
SRC = sha256(b"rev0090-source")
FB = sha256(b"rev0090-fallback")
ORACLE = sha256(b"rev0090-python-oracle")


@dataclass(frozen=True)
class FakeColdStart:
    accepted: bool = True
    quarantine: bool = False
    probe_required: bool = True
    fallback_active: bool = True
    native_load_forbidden: bool = True
    artifact_digest: bytes = ART
    source_digest: bytes = SRC
    fallback_digest: bytes = FB
    fault_pressure: bool = True
    report_digest: bytes = sha256(b"cold-start-report")


@dataclass(frozen=True)
class FakeProbeCorpus:
    accepted: bool = True
    refreshed: bool = True
    watch: bool = False
    quarantine: bool = False
    artifact_digest: bytes = ART
    source_digest: bytes = SRC
    fallback_digest: bytes = FB
    python_oracle_digest: bytes = ORACLE
    report_digest: bytes = sha256(b"probe-corpus-report")


@dataclass(frozen=True)
class FakeLoaderGc:
    accepted: bool = True
    loader_gc_applied: bool = True
    fallback_active: bool = True
    tombstone_retained: bool = True
    quarantine: bool = False
    watch: bool = False
    artifact_digest: bytes = ART
    source_digest: bytes = SRC
    fallback_digest: bytes = FB
    report_digest: bytes = sha256(b"loader-gc-report")


def _handoff_capsule(cold=FakeColdStart(), probe=FakeProbeCorpus(), loader=FakeLoaderGc(), **kw):
    data = dict(
        component="xor_distance", profile="portable-default", operation="xor_compare", request_id="rev0090-native",
        sequence=1, previous_digest=b"", cold_start_digest=cold.report_digest, probe_corpus_digest=probe.report_digest,
        loader_gc_digest=loader.report_digest, artifact_digest=ART, source_digest=SRC, fallback_digest=FB,
        python_oracle_digest=ORACLE, relaunch_candidate_requested=True, load_attempted=False, dispatch_attempted=False,
        python_fallback_active=True, preserve_cold_start_memory=True, preserve_probe_memory=True,
        preserve_loader_gc_memory=True, preserve_tombstone_memory=True, preserve_quarantine_memory=True,
        preserve_crash_memory=True, family_id="family-a", path_family_id="path-a",
    )
    data.update(kw)
    return NativeHandoffCapsule(**data)


def _handoff(cold=FakeColdStart(), probe=FakeProbeCorpus(), loader=FakeLoaderGc(), capsule=None):
    cap = capsule or _handoff_capsule(cold, probe, loader)
    return assess_native_handoff(cold, probe, loader, cap, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b")), cap


def _relaunch_plan(handoff_report, **kw):
    data = dict(
        component="xor_distance", profile="portable-default", operation="xor_compare", request_id="rev0090-native",
        sequence=1, previous_digest=b"", handoff_digest=handoff_report.report_digest,
        parity_digest=sha256(b"parity"), abi_digest=sha256(b"abi"), fallback_seal_digest=sha256(b"fallback-seal"),
        runtime_stamp_digest=sha256(b"runtime"), selection_digest=sha256(b"selection"), artifact_digest=ART,
        source_digest=SRC, fallback_digest=FB, python_oracle_digest=ORACLE, prior_native_lanes_revalidated=True,
        fallback_only_profile=False, python_fallback_available=True, no_network=True, load_attempted=False,
        dispatch_attempted=False, family_id="family-a", path_family_id="path-a",
    )
    data.update(kw)
    return NativeRelaunchGatePlan(**data)


def _relaunch(handoff_report=None, plan=None):
    if handoff_report is None:
        handoff_report, _ = _handoff()
    p = plan or _relaunch_plan(handoff_report)
    return assess_native_relaunch_gate(handoff_report, p, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b")), p


def _loader_seal_capsule(handoff_report, relaunch_report, probe=FakeProbeCorpus(), loader=FakeLoaderGc(), **kw):
    data = dict(
        component="xor_distance", profile="portable-default", operation="xor_compare", request_id="rev0090-native",
        sequence=1, previous_digest=b"", handoff_digest=handoff_report.report_digest,
        relaunch_gate_digest=relaunch_report.report_digest, probe_corpus_digest=probe.report_digest,
        loader_gc_digest=loader.report_digest, artifact_digest=ART, source_digest=SRC, fallback_digest=FB,
        python_oracle_digest=ORACLE, preserve_handoff_memory=True, preserve_relaunch_memory=True,
        preserve_probe_memory=True, preserve_loader_gc_memory=True, preserve_tombstone_memory=True,
        preserve_fallback_memory=True, preserve_quarantine_memory=True, preserve_crash_memory=True,
        seal_for_relaunch_candidate=True, family_id="family-a", path_family_id="path-a",
    )
    data.update(kw)
    return NativeLoaderSealCapsule(**data)


def _loader_seal(handoff_report=None, relaunch_report=None, capsule=None, probe=FakeProbeCorpus(), loader=FakeLoaderGc()):
    if handoff_report is None:
        handoff_report, _ = _handoff(probe=probe, loader=loader)
    if relaunch_report is None:
        relaunch_report, _ = _relaunch(handoff_report)
    cap = capsule or _loader_seal_capsule(handoff_report, relaunch_report, probe, loader)
    return assess_native_loader_seal(handoff_report, relaunch_report, probe, loader, cap, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b")), cap


def test_native_handoff_accepts_candidate_but_forbids_load_and_dispatch() -> None:
    report, _ = _handoff()
    assert report.decision_kind is NativeHandoffDecisionKind.ACCEPT_RELAUNCH_CANDIDATE
    assert report.relaunch_candidate and report.fallback_active
    assert report.native_load_forbidden and report.dispatch_forbidden
    assert report.tombstone_carried and report.fault_memory_carried

    no_candidate, _ = _handoff(capsule=_handoff_capsule(relaunch_candidate_requested=False))
    assert no_candidate.decision_kind is NativeHandoffDecisionKind.HOLD_FALLBACK_ONLY

    load_attempt, _ = _handoff(capsule=_handoff_capsule(load_attempted=True))
    assert load_attempt.decision_kind is NativeHandoffDecisionKind.QUARANTINE_LOAD_OR_DISPATCH_ATTEMPT

    dispatch_attempt, _ = _handoff(capsule=_handoff_capsule(dispatch_attempted=True))
    assert dispatch_attempt.decision_kind is NativeHandoffDecisionKind.QUARANTINE_LOAD_OR_DISPATCH_ATTEMPT

    memory_drop, _ = _handoff(capsule=_handoff_capsule(preserve_quarantine_memory=False))
    assert memory_drop.decision_kind is NativeHandoffDecisionKind.QUARANTINE_MEMORY_DROP


def test_native_handoff_detects_probe_loader_digest_and_sequence_pressure() -> None:
    cold = FakeColdStart(); probe = FakeProbeCorpus(); loader = FakeLoaderGc()
    probe_bad = replace(probe, refreshed=False)
    hold_probe, _ = _handoff(cold, probe_bad, loader)
    assert hold_probe.decision_kind is NativeHandoffDecisionKind.HOLD_PROBE_REQUIRED

    loader_bad = replace(loader, tombstone_retained=False)
    hold_loader, _ = _handoff(cold, probe, loader_bad)
    assert hold_loader.decision_kind is NativeHandoffDecisionKind.HOLD_LOADER_GC_NOT_READY

    bad_digest, _ = _handoff(capsule=_handoff_capsule(probe_corpus_digest=sha256(b"wrong-probe")))
    assert bad_digest.decision_kind is NativeHandoffDecisionKind.QUARANTINE_DIGEST_DRIFT

    first = _handoff_capsule()
    replay = assess_native_handoff(cold, probe, loader, first, prior_capsule_digests=(first.capsule_digest,), observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b"))
    assert replay.decision_kind is NativeHandoffDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK
    fork = assess_native_handoff(cold, probe, loader, replace(first, note="fork"), previous=first, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b"))
    assert fork.decision_kind is NativeHandoffDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK
    bad_link = replace(first, sequence=2, previous_digest=sha256(b"bad-prev"))
    link = assess_native_handoff(cold, probe, loader, bad_link, previous=first, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b"))
    assert link.decision_kind is NativeHandoffDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH
    low_div = assess_native_handoff(cold, probe, loader, first, observed_families=("family-a",), observed_path_families=("path-a",))
    assert low_div.decision_kind is NativeHandoffDecisionKind.QUARANTINE_LOW_DIVERSITY


def test_relaunch_gate_requires_prior_native_revalidation_and_stays_no_network() -> None:
    handoff_report, _ = _handoff()
    report, _ = _relaunch(handoff_report)
    assert report.decision_kind is NativeRelaunchGateDecisionKind.ACCEPT_NO_NETWORK_RELAUNCH_PLAN
    assert report.relaunch_plan_ready and report.fallback_active
    assert not report.native_load_allowed and not report.dispatch_allowed

    no_revalidation, _ = _relaunch(handoff_report, _relaunch_plan(handoff_report, prior_native_lanes_revalidated=False, runtime_stamp_digest=b""))
    assert no_revalidation.decision_kind is NativeRelaunchGateDecisionKind.HOLD_PRIOR_NATIVE_REVALIDATION_REQUIRED

    fallback_only, _ = _relaunch(handoff_report, _relaunch_plan(handoff_report, fallback_only_profile=True))
    assert fallback_only.decision_kind is NativeRelaunchGateDecisionKind.HOLD_FALLBACK_ONLY_PROFILE

    dispatch_attempt, _ = _relaunch(handoff_report, _relaunch_plan(handoff_report, dispatch_attempted=True))
    assert dispatch_attempt.decision_kind is NativeRelaunchGateDecisionKind.QUARANTINE_DISPATCH_OR_LOAD_ATTEMPT

    missing_fallback, _ = _relaunch(handoff_report, _relaunch_plan(handoff_report, python_fallback_available=False))
    assert missing_fallback.decision_kind is NativeRelaunchGateDecisionKind.QUARANTINE_PYTHON_FALLBACK_MISSING

    drift, _ = _relaunch(handoff_report, _relaunch_plan(handoff_report, handoff_digest=sha256(b"wrong-handoff")))
    assert drift.decision_kind is NativeRelaunchGateDecisionKind.QUARANTINE_DIGEST_DRIFT


def test_loader_seal_preserves_relaunch_memory_and_holds_watch_debt() -> None:
    handoff_report, _ = _handoff()
    relaunch_report, _ = _relaunch(handoff_report)
    report, _ = _loader_seal(handoff_report, relaunch_report)
    assert report.decision_kind is NativeLoaderSealDecisionKind.ACCEPT_RELAUNCH_LOADER_SEAL
    assert report.sealed and report.fallback_active and report.native_load_forbidden
    assert report.tombstone_memory and report.fault_memory

    drop = _loader_seal_capsule(handoff_report, relaunch_report, preserve_tombstone_memory=False)
    dropped, _ = _loader_seal(handoff_report, relaunch_report, drop)
    assert dropped.decision_kind is NativeLoaderSealDecisionKind.QUARANTINE_MEMORY_DROP

    not_ready_report, _ = _relaunch(handoff_report, _relaunch_plan(handoff_report, fallback_only_profile=True))
    not_ready, _ = _loader_seal(handoff_report, not_ready_report)
    assert not_ready.decision_kind is NativeLoaderSealDecisionKind.HOLD_RELAUNCH_NOT_READY

    watch_probe = replace(FakeProbeCorpus(), watch=True)
    handoff_watch, _ = _handoff(probe=watch_probe)
    relaunch_watch, _ = _relaunch(handoff_watch)
    hold_watch, _ = _loader_seal(handoff_watch, relaunch_watch, probe=watch_probe)
    assert hold_watch.decision_kind is NativeLoaderSealDecisionKind.HOLD_WATCH_DEBT

    drift, _ = _loader_seal(handoff_report, relaunch_report, _loader_seal_capsule(handoff_report, relaunch_report, relaunch_gate_digest=sha256(b"wrong")))
    assert drift.decision_kind is NativeLoaderSealDecisionKind.QUARANTINE_DIGEST_DRIFT


def test_loader_seal_detects_replay_fork_previous_link_and_low_diversity() -> None:
    handoff_report, _ = _handoff()
    relaunch_report, _ = _relaunch(handoff_report)
    first = _loader_seal_capsule(handoff_report, relaunch_report)
    replay = assess_native_loader_seal(handoff_report, relaunch_report, FakeProbeCorpus(), FakeLoaderGc(), first, prior_capsule_digests=(first.capsule_digest,), observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b"))
    assert replay.decision_kind is NativeLoaderSealDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK
    fork = assess_native_loader_seal(handoff_report, relaunch_report, FakeProbeCorpus(), FakeLoaderGc(), replace(first, note="fork"), previous=first, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b"))
    assert fork.decision_kind is NativeLoaderSealDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK
    bad_link = replace(first, sequence=2, previous_digest=sha256(b"bad-prev"))
    link = assess_native_loader_seal(handoff_report, relaunch_report, FakeProbeCorpus(), FakeLoaderGc(), bad_link, previous=first, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b"))
    assert link.decision_kind is NativeLoaderSealDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH
    low = assess_native_loader_seal(handoff_report, relaunch_report, FakeProbeCorpus(), FakeLoaderGc(), first, observed_families=("family-a",), observed_path_families=("path-a",))
    assert low.decision_kind is NativeLoaderSealDecisionKind.QUARANTINE_LOW_DIVERSITY


def test_native_fold_spine_and_handoff_fold_happy_path() -> None:
    spine = audit_native_fold_spine(ROOT, revision="rev0090")
    assert spine.status == "pass"
    assert spine.checked_count >= 10
    fold = audit_native_handoff_fold(ROOT, revision="rev0090", artifact_stem=ARTIFACT)
    assert fold.status == "pass"
    assert fold.predecessor_status == "pass"
    assert fold.foldmap_status == "pass"
    assert fold.foldregistry_status == "pass"
    assert fold.surface_ledger_status == "pass"
    assert fold.native_spine_status == "pass"
