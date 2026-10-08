from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path

from i2p_dht_lab.ids import sha256
from i2p_dht_lab.nativecrashledger import (
    NativeCrashDecisionKind,
    NativeCrashObservation,
    assess_native_crash,
)
from i2p_dht_lab.nativelifecyclefold import audit_native_lifecycle_fold
from i2p_dht_lab.nativeload import (
    NativeLoadDecisionKind,
    NativeLoadIntent,
    assess_native_load,
)
from i2p_dht_lab.nativeperfguard import (
    NativePerfDecisionKind,
    NativePerfObservation,
    assess_native_perf,
)

ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class FakeSelection:
    accepted: bool = True
    native_selected: bool = True
    fallback_selected: bool = True
    watch: bool = False
    quarantine: bool = False
    artifact_digest: bytes = sha256(b"artifact-ok")
    source_digest: bytes = sha256(b"source-ok")
    fallback_digest: bytes = sha256(b"python-fallback-ok")
    report_digest: bytes = sha256(b"selection-ok")


@dataclass(frozen=True)
class FakePromotion:
    accepted: bool = True
    native_active: bool = True
    fallback_active: bool = True
    watch: bool = False
    quarantine: bool = False
    report_digest: bytes = sha256(b"promotion-ok")


@dataclass(frozen=True)
class FakeFallback:
    accepted: bool = True
    fallback_active: bool = True
    watch: bool = False
    quarantine: bool = False
    report_digest: bytes = sha256(b"fallback-journal-ok")


def _load_intent(seq: int = 1, prev: bytes = b"", *, selection=FakeSelection(), promotion=FakePromotion(), fallback=FakeFallback(), native_enabled: bool = True, native_required: bool = False, note: str = "") -> NativeLoadIntent:
    return NativeLoadIntent(
        component="xor_distance",
        profile="portable-default",
        operation="xor_compare",
        request_id="rev0087-load",
        sequence=seq,
        previous_digest=prev,
        selection_digest=selection.report_digest,
        promotion_digest=promotion.report_digest,
        fallback_journal_digest=fallback.report_digest,
        artifact_digest=selection.artifact_digest,
        source_digest=selection.source_digest,
        fallback_digest=selection.fallback_digest,
        loader_id="ctypes-local-no-network",
        load_mode="dry-permission",
        native_enabled=native_enabled,
        native_required=native_required,
        family_id="family-a",
        path_family_id="path-a",
        note=note,
    )


def _load(*, selection=FakeSelection(), promotion=FakePromotion(), fallback=FakeFallback(), intent: NativeLoadIntent | None = None):
    intent = intent or _load_intent(selection=selection, promotion=promotion, fallback=fallback)
    return assess_native_load(selection, promotion, fallback, intent, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b"), min_families=2, min_path_families=2)


def _crash_observation(load, fault: str = "none", seq: int = 1, prev: bytes = b"", *, preserve: bool = True, note: str = "") -> NativeCrashObservation:
    return NativeCrashObservation(
        component="xor_distance",
        profile="portable-default",
        operation="xor_compare",
        request_id="rev0087-load",
        sequence=seq,
        previous_digest=prev,
        load_digest=load.report_digest,
        artifact_digest=load.artifact_digest,
        source_digest=load.source_digest,
        fault_kind=fault,
        preserve_fallback_memory=preserve,
        preserve_quarantine_memory=preserve,
        family_id="family-a",
        path_family_id="path-a",
        note=note,
    )


def _crash(load, observation=None):
    observation = observation or _crash_observation(load)
    return assess_native_crash(load, observation, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b"), min_families=2, min_path_families=2)


def _perf_observation(load, crash, seq: int = 1, prev: bytes = b"", *, samples: int = 16, speedup: int = 120_000, raw=(), override: bool = False, preserve: bool = True, note: str = "") -> NativePerfObservation:
    return NativePerfObservation(
        component="xor_distance",
        profile="portable-default",
        operation="xor_compare",
        request_id="rev0087-load",
        sequence=seq,
        previous_digest=prev,
        load_digest=load.report_digest,
        crash_digest=crash.report_digest,
        sample_count=samples,
        speedup_ppm=speedup,
        redacted_label="xor-distance-leaf",
        raw_label_fragments=tuple(raw),
        wants_selection_override=override,
        preserve_crash_memory=preserve,
        preserve_fallback_memory=preserve,
        family_id="family-a",
        path_family_id="path-a",
        note=note,
    )


def _perf(load, crash, observation=None):
    observation = observation or _perf_observation(load, crash)
    return assess_native_perf(load, crash, observation, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b"), min_families=2, min_path_families=2, min_samples=8)


def test_native_load_accepts_only_after_selection_and_promotion_bind() -> None:
    report = _load()
    assert report.decision_kind is NativeLoadDecisionKind.ACCEPT_NATIVE_LOAD
    assert report.native_load_allowed
    assert report.fallback_active

    selection = FakeSelection(native_selected=False, report_digest=sha256(b"selection-fallback"))
    hold_intent = _load_intent(selection=selection)
    hold = _load(selection=selection, intent=hold_intent)
    assert hold.decision_kind is NativeLoadDecisionKind.ACCEPT_STAY_FALLBACK
    assert not hold.native_load_allowed

    drift = replace(_load_intent(), source_digest=sha256(b"wrong-source"))
    assert _load(intent=drift).decision_kind is NativeLoadDecisionKind.QUARANTINE_DIGEST_DRIFT

    disabled_required = _load(intent=_load_intent(native_enabled=False, native_required=True))
    assert disabled_required.decision_kind is NativeLoadDecisionKind.QUARANTINE_NATIVE_DISABLED_BUT_REQUIRED


def test_native_load_detects_replay_fork_previous_link_and_low_diversity() -> None:
    first = _load_intent()
    assert assess_native_load(FakeSelection(), FakePromotion(), FakeFallback(), first, prior_intent_digests=(first.intent_digest,), observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b")).decision_kind is NativeLoadDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK
    fork = replace(first, note="fork")
    assert assess_native_load(FakeSelection(), FakePromotion(), FakeFallback(), fork, previous=first, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b")).decision_kind is NativeLoadDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK
    bad_link = _load_intent(seq=2, prev=sha256(b"bad-prev"))
    assert assess_native_load(FakeSelection(), FakePromotion(), FakeFallback(), bad_link, previous=first, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b")).decision_kind is NativeLoadDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH
    low = assess_native_load(FakeSelection(), FakePromotion(), FakeFallback(), first, observed_families=("family-a",), observed_path_families=("path-a",), min_families=2, min_path_families=2)
    assert low.decision_kind is NativeLoadDecisionKind.QUARANTINE_LOW_DIVERSITY


def test_crash_ledger_records_faults_as_fallback_quarantine_memory() -> None:
    load = _load()
    clean = _crash(load)
    assert clean.decision_kind is NativeCrashDecisionKind.ACCEPT_NO_FAULT
    assert not clean.quarantine

    fault = _crash(load, _crash_observation(load, "wrong_result"))
    assert fault.decision_kind is NativeCrashDecisionKind.RECORD_FAULT_QUARANTINE
    assert fault.fallback_required
    assert fault.quarantine

    watch = _crash(load, _crash_observation(load, "slow_path"))
    assert watch.decision_kind is NativeCrashDecisionKind.HOLD_WATCH_FAULT
    assert watch.watch

    drift = _crash(load, replace(_crash_observation(load), artifact_digest=sha256(b"wrong-artifact")))
    assert drift.decision_kind is NativeCrashDecisionKind.QUARANTINE_DIGEST_DRIFT


def test_crash_ledger_detects_replay_fork_previous_link_and_low_diversity() -> None:
    load = _load(); first = _crash_observation(load)
    assert assess_native_crash(load, first, prior_observation_digests=(first.observation_digest,), observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b")).decision_kind is NativeCrashDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK
    fork = replace(first, note="fork")
    assert assess_native_crash(load, fork, previous=first, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b")).decision_kind is NativeCrashDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK
    bad_link = _crash_observation(load, seq=2, prev=sha256(b"bad-prev"))
    assert assess_native_crash(load, bad_link, previous=first, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b")).decision_kind is NativeCrashDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH
    low = assess_native_crash(load, first, observed_families=("family-a",), observed_path_families=("path-a",), min_families=2, min_path_families=2)
    assert low.decision_kind is NativeCrashDecisionKind.QUARANTINE_LOW_DIVERSITY


def test_performance_guard_is_operator_hint_not_selection_authority() -> None:
    load = _load(); crash = _crash(load)
    perf = _perf(load, crash)
    assert perf.decision_kind is NativePerfDecisionKind.ACCEPT_REDACTED_PROFILE
    assert perf.usable_for_operator_hint
    assert not perf.usable_for_selection

    override = _perf(load, crash, _perf_observation(load, crash, override=True))
    assert override.decision_kind is NativePerfDecisionKind.QUARANTINE_PERF_AS_AUTHORITY

    raw = _perf(load, crash, _perf_observation(load, crash, raw=("request:abc123",)))
    assert raw.decision_kind is NativePerfDecisionKind.QUARANTINE_RAW_LABEL_LEAK

    low_samples = _perf(load, crash, _perf_observation(load, crash, samples=2))
    assert low_samples.decision_kind is NativePerfDecisionKind.HOLD_INSUFFICIENT_PROFILE

    crash_fault = _crash(load, _crash_observation(load, "segfault"))
    held = _perf(load, crash_fault, _perf_observation(load, crash_fault))
    assert held.decision_kind is NativePerfDecisionKind.HOLD_CRASH_OR_FALLBACK_PRESSURE


def test_performance_guard_detects_replay_fork_previous_link_and_digest_drift() -> None:
    load = _load(); crash = _crash(load); first = _perf_observation(load, crash)
    assert assess_native_perf(load, crash, first, prior_observation_digests=(first.observation_digest,), observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b")).decision_kind is NativePerfDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK
    fork = replace(first, note="fork")
    assert assess_native_perf(load, crash, fork, previous=first, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b")).decision_kind is NativePerfDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK
    bad_link = _perf_observation(load, crash, seq=2, prev=sha256(b"bad-prev"))
    assert assess_native_perf(load, crash, bad_link, previous=first, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b")).decision_kind is NativePerfDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH
    drift = replace(first, crash_digest=sha256(b"wrong-crash"))
    assert assess_native_perf(load, crash, drift, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b")).decision_kind is NativePerfDecisionKind.QUARANTINE_DIGEST_DRIFT


def test_nativelifecyclefold_happy_path() -> None:
    report = audit_native_lifecycle_fold(ROOT, revision="rev0087", artifact_stem=ROOT.name)
    assert report.status == "pass"
    assert report.predecessor_status == "pass"
    assert report.foldmap_status == "pass"
    assert report.foldregistry_status == "pass"
    assert report.surface_ledger_status == "pass"
