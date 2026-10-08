from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path

from i2p_dht_lab.ids import sha256
from i2p_dht_lab.loadergc import NativeLoaderGcDecisionKind, NativeLoaderGcProposal, assess_native_loader_gc
from i2p_dht_lab.nativecoldfold import audit_native_cold_fold
from i2p_dht_lab.nativecoldstart import NativeColdStartCapsule, NativeColdStartDecisionKind, assess_native_cold_start
from i2p_dht_lab.nativecrashgc import NativeCrashGcProposal, assess_native_crash_gc
from i2p_dht_lab.nativecrashledger import NativeCrashDecisionKind
from i2p_dht_lab.nativeload import NativeLoadDecisionKind
from i2p_dht_lab.nativeperfguard import NativePerfDecisionKind
from i2p_dht_lab.nativesandboxstub import NativeSandboxPlan, assess_native_sandbox_stub
from i2p_dht_lab.nativeunload import NativeUnloadIntent, assess_native_unload
from i2p_dht_lab.probecorpus import NativeProbeCorpusDecisionKind, NativeProbeCorpusPlan, assess_native_probe_corpus

ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class FakeLoad:
    decision_kind = NativeLoadDecisionKind.ACCEPT_NATIVE_LOAD
    accepted: bool = True
    native_load_allowed: bool = True
    fallback_active: bool = True
    artifact_digest: bytes = sha256(b"artifact-v1")
    source_digest: bytes = sha256(b"source-v1")
    fallback_digest: bytes = sha256(b"python-fallback-v1")
    report_seed: bytes = b"load-report-v1"

    @property
    def report_digest(self) -> bytes:
        return sha256(self.report_seed + self.artifact_digest + self.source_digest + self.fallback_digest + (b"native" if self.native_load_allowed else b"fallback"))


@dataclass(frozen=True)
class FakeCrash:
    decision_kind = NativeCrashDecisionKind.ACCEPT_NO_FAULT
    accepted: bool = True
    fallback_required: bool = False
    quarantine: bool = False
    watch: bool = False
    fault_kind: str = "none"
    artifact_digest: bytes = sha256(b"artifact-v1")
    source_digest: bytes = sha256(b"source-v1")
    report_seed: bytes = b"crash-report-v1"

    @property
    def report_digest(self) -> bytes:
        return sha256(self.report_seed + self.artifact_digest + self.source_digest + self.fault_kind.encode() + (b"q" if self.quarantine else b"clean"))


@dataclass(frozen=True)
class FakePerf:
    decision_kind = NativePerfDecisionKind.ACCEPT_REDACTED_PROFILE
    accepted: bool = True
    usable_for_operator_hint: bool = True
    usable_for_selection: bool = False
    watch: bool = False
    quarantine: bool = False
    report_seed: bytes = b"perf-report-v1"

    @property
    def report_digest(self) -> bytes:
        return sha256(self.report_seed + (b"watch" if self.watch else b"ok"))


def _unload(load=FakeLoad(), crash=FakeCrash(), perf=FakePerf(), *, reason="normal_shutdown", loaded=True):
    intent = NativeUnloadIntent(
        "xor_distance", "portable-default", "xor_compare", "rev0089-native", 1, b"",
        load.report_digest, crash.report_digest, perf.report_digest,
        load.artifact_digest, load.source_digest, load.fallback_digest,
        reason, loaded, True, True, True, "family-a", "path-a",
    )
    return assess_native_unload(load, crash, perf, intent, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b"))


def _sandbox(load, unload, *, native=False):
    plan = NativeSandboxPlan(
        "xor_distance", "portable-default", "xor_compare", "rev0089-native", 1, b"",
        load.report_digest, unload.report_digest, "fallback_only_stub" if not native else "ctypes_leaf_stub",
        native, True, True, False, False, False, False, False, False, False, 64, 10_000,
        "family-a", "path-a",
    )
    return assess_native_sandbox_stub(load, unload, plan, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b"))


def _gc(crash, unload, *, retained=None, preserve=True, budget=256):
    retained = (crash.report_digest,) if retained is None else retained
    prop = NativeCrashGcProposal(
        "xor_distance", "portable-default", "xor_compare", "rev0089-native", 1, b"",
        crash.report_digest, unload.report_digest, retained, (sha256(b"soft"),), False,
        preserve, preserve, preserve, budget, "family-a", "path-a",
    )
    return assess_native_crash_gc(crash, unload, prop, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b"))


def _cold(load=FakeLoad(), unload=None, sandbox=None, gc=None, *, seq=1, prev=b"", discovered=True, load_attempted=False, dyn=False, enabled=True, fallback=True, preserve=True, require_probe=True, note=""):
    unload = unload or _unload(load)
    sandbox = sandbox or _sandbox(load, unload)
    gc = gc or _gc(FakeCrash(), unload, retained=())
    capsule = NativeColdStartCapsule(
        "xor_distance", "portable-default", "xor_compare", "rev0089-native", seq, prev,
        unload.report_digest, sandbox.report_digest, gc.report_digest,
        load.artifact_digest, load.source_digest, load.fallback_digest,
        discovered, load_attempted, dyn, enabled, fallback, preserve, preserve, preserve,
        require_probe, "family-a", "path-a", note,
    )
    return assess_native_cold_start(unload, sandbox, gc, capsule, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b")), capsule


def _probe_plan(cold, *, seq=1, prev=b"", vectors=8, buckets=4, oracle=sha256(b"python-oracle"), max_input=64, boundary=True, fault_vectors=True, fallback_vectors=True, preserve=True, note=""):
    return NativeProbeCorpusPlan(
        "xor_distance", "portable-default", "xor_compare", "rev0089-native", seq, prev,
        cold.report_digest, cold.artifact_digest, cold.source_digest, cold.fallback_digest, oracle,
        vectors, buckets, max_input, boundary, fault_vectors, fallback_vectors, preserve, preserve,
        "family-a", "path-a", note,
    )


def _probe(cold, plan=None):
    return assess_native_probe_corpus(cold, plan or _probe_plan(cold), observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b"))


def _loader_gc(unload, gc, cold, *, seq=1, prev=b"", handles=(), tombstones=None, preserve=True, budget=256, dropped=(b"soft",), note=""):
    tombstones = (cold.artifact_digest,) if tombstones is None else tombstones
    prop = NativeLoaderGcProposal(
        "xor_distance", "portable-default", "xor_compare", "rev0089-native", seq, prev,
        unload.report_digest, gc.report_digest, cold.report_digest,
        cold.artifact_digest, cold.source_digest, cold.fallback_digest,
        tuple(handles), tuple(tombstones), tuple(x if isinstance(x, bytes) and len(x) == 32 else (sha256(x) if isinstance(x, bytes) else x) for x in dropped),
        preserve, preserve, preserve, preserve, budget, "family-a", "path-a", note,
    )
    return assess_native_loader_gc(unload, gc, cold, prop, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b")), prop


def test_native_cold_start_holds_probe_without_loading() -> None:
    clean, _ = _cold()
    assert clean.decision_kind is NativeColdStartDecisionKind.HOLD_PROBE_REQUIRED
    assert clean.probe_required and clean.fallback_active and clean.native_load_forbidden

    fallback_only, _ = _cold(discovered=False, require_probe=False)
    assert fallback_only.decision_kind is NativeColdStartDecisionKind.ACCEPT_FALLBACK_ONLY_COLD_START

    disabled, _ = _cold(enabled=False)
    assert disabled.decision_kind is NativeColdStartDecisionKind.HOLD_NATIVE_DISABLED

    load_on_discovery, _ = _cold(load_attempted=True)
    assert load_on_discovery.decision_kind is NativeColdStartDecisionKind.QUARANTINE_LOAD_ON_DISCOVERY
    dynamic_load, _ = _cold(dyn=True)
    assert dynamic_load.decision_kind is NativeColdStartDecisionKind.QUARANTINE_LOAD_ON_DISCOVERY

    drop_memory, _ = _cold(preserve=False)
    assert drop_memory.decision_kind is NativeColdStartDecisionKind.QUARANTINE_MEMORY_DROP


def test_native_cold_start_detects_replay_fork_link_low_diversity_and_digest_drift() -> None:
    unload = _unload(); sandbox = _sandbox(FakeLoad(), unload); gc = _gc(FakeCrash(), unload, retained=())
    first = NativeColdStartCapsule("xor_distance", "portable-default", "xor_compare", "rev0089-native", 1, b"", unload.report_digest, sandbox.report_digest, gc.report_digest, FakeLoad().artifact_digest, FakeLoad().source_digest, FakeLoad().fallback_digest, True, False, False, True, True, True, True, True, True, "family-a", "path-a")
    assert assess_native_cold_start(unload, sandbox, gc, first, prior_capsule_digests=(first.capsule_digest,), observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b")).decision_kind is NativeColdStartDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK
    assert assess_native_cold_start(unload, sandbox, gc, replace(first, note="fork"), previous=first, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b")).decision_kind is NativeColdStartDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK
    bad_link = replace(first, sequence=2, previous_digest=sha256(b"bad-prev"))
    assert assess_native_cold_start(unload, sandbox, gc, bad_link, previous=first, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b")).decision_kind is NativeColdStartDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH
    assert assess_native_cold_start(unload, sandbox, gc, first, observed_families=("family-a",), observed_path_families=("path-a",), min_families=2, min_path_families=2).decision_kind is NativeColdStartDecisionKind.QUARANTINE_LOW_DIVERSITY
    drift = replace(first, sandbox_digest=sha256(b"wrong-sandbox"))
    assert assess_native_cold_start(unload, sandbox, gc, drift, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b")).decision_kind is NativeColdStartDecisionKind.QUARANTINE_DIGEST_DRIFT


def test_probe_corpus_refresh_requires_python_oracle_bounds_and_fault_regression_vectors() -> None:
    fault = FakeCrash(fallback_required=True, quarantine=True, fault_kind="wrong_result")
    unload = _unload(FakeLoad(), fault, FakePerf(), reason="fault_quarantine")
    sandbox = _sandbox(FakeLoad(), unload)
    gc = _gc(fault, unload)
    cold, _ = _cold(unload=unload, sandbox=sandbox, gc=gc)
    assert cold.fault_pressure

    refreshed = _probe(cold)
    assert refreshed.decision_kind is NativeProbeCorpusDecisionKind.ACCEPT_REFRESHED_CORPUS

    no_oracle = _probe(cold, _probe_plan(cold, oracle=b""))
    assert no_oracle.decision_kind is NativeProbeCorpusDecisionKind.QUARANTINE_MISSING_PYTHON_ORACLE
    unbounded = _probe(cold, _probe_plan(cold, max_input=999_999))
    assert unbounded.decision_kind is NativeProbeCorpusDecisionKind.QUARANTINE_UNBOUNDED_INPUT
    too_small = _probe(cold, _probe_plan(cold, vectors=1, buckets=1, boundary=False))
    assert too_small.decision_kind is NativeProbeCorpusDecisionKind.HOLD_MORE_VECTORS_REQUIRED
    no_fault_vectors = _probe(cold, _probe_plan(cold, fault_vectors=False))
    assert no_fault_vectors.decision_kind is NativeProbeCorpusDecisionKind.HOLD_FAULT_REGRESSION_VECTORS_REQUIRED
    memory_drop = _probe(cold, _probe_plan(cold, preserve=False))
    assert memory_drop.decision_kind is NativeProbeCorpusDecisionKind.QUARANTINE_MEMORY_DROP


def test_probe_corpus_detects_replay_fork_link_low_diversity_and_drift() -> None:
    cold, _ = _cold()
    first = _probe_plan(cold)
    assert assess_native_probe_corpus(cold, first, prior_plan_digests=(first.plan_digest,), observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b")).decision_kind is NativeProbeCorpusDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK
    assert assess_native_probe_corpus(cold, replace(first, note="fork"), previous=first, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b")).decision_kind is NativeProbeCorpusDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK
    bad_link = replace(first, sequence=2, previous_digest=sha256(b"bad-prev"))
    assert assess_native_probe_corpus(cold, bad_link, previous=first, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b")).decision_kind is NativeProbeCorpusDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH
    assert assess_native_probe_corpus(cold, first, observed_families=("family-a",), observed_path_families=("path-a",), min_families=2, min_path_families=2).decision_kind is NativeProbeCorpusDecisionKind.QUARANTINE_LOW_DIVERSITY
    drift = replace(first, artifact_digest=sha256(b"wrong-artifact"))
    assert _probe(cold, drift).decision_kind is NativeProbeCorpusDecisionKind.QUARANTINE_DIGEST_DRIFT


def test_loader_gc_keeps_tombstone_and_blocks_active_handle_drop() -> None:
    fault = FakeCrash(fallback_required=True, quarantine=True, fault_kind="segfault")
    unload = _unload(FakeLoad(), fault, FakePerf(), reason="fault_quarantine")
    gc = _gc(fault, unload)
    cold, _ = _cold(unload=unload, sandbox=_sandbox(FakeLoad(), unload), gc=gc)

    ok, _ = _loader_gc(unload, gc, cold)
    assert ok.decision_kind is NativeLoaderGcDecisionKind.ACCEPT_LOADER_GC
    assert ok.tombstone_retained and ok.fallback_active

    drop_tombstone, _ = _loader_gc(unload, gc, cold, tombstones=())
    assert drop_tombstone.decision_kind is NativeLoaderGcDecisionKind.QUARANTINE_ACTIVE_HANDLE_DROP

    active_hold, _ = _loader_gc(unload, gc, cold, handles=(cold.artifact_digest,), dropped=())
    assert active_hold.decision_kind is NativeLoaderGcDecisionKind.HOLD_ACTIVE_HANDLE_PRESENT

    active_drop, _ = _loader_gc(unload, gc, cold, handles=(cold.artifact_digest,), dropped=(cold.artifact_digest,))
    assert active_drop.decision_kind is NativeLoaderGcDecisionKind.QUARANTINE_ACTIVE_HANDLE_DROP

    memory_drop, _ = _loader_gc(unload, gc, cold, preserve=False)
    assert memory_drop.decision_kind is NativeLoaderGcDecisionKind.QUARANTINE_MEMORY_DROP

    low_budget, _ = _loader_gc(unload, gc, cold, budget=1)
    assert low_budget.decision_kind is NativeLoaderGcDecisionKind.HOLD_RETAIN_TOMBSTONE


def test_loader_gc_detects_replay_fork_previous_link_low_diversity_and_drift() -> None:
    unload = _unload(); gc = _gc(FakeCrash(), unload, retained=()); cold, _ = _cold(unload=unload, sandbox=_sandbox(FakeLoad(), unload), gc=gc)
    first_report, first = _loader_gc(unload, gc, cold)
    assert first_report.decision_kind is NativeLoaderGcDecisionKind.ACCEPT_LOADER_GC
    assert assess_native_loader_gc(unload, gc, cold, first, prior_proposal_digests=(first.proposal_digest,), observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b")).decision_kind is NativeLoaderGcDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK
    assert assess_native_loader_gc(unload, gc, cold, replace(first, note="fork"), previous=first, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b")).decision_kind is NativeLoaderGcDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK
    bad_link = replace(first, sequence=2, previous_digest=sha256(b"bad-prev"))
    assert assess_native_loader_gc(unload, gc, cold, bad_link, previous=first, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b")).decision_kind is NativeLoaderGcDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH
    assert assess_native_loader_gc(unload, gc, cold, first, observed_families=("family-a",), observed_path_families=("path-a",), min_families=2, min_path_families=2).decision_kind is NativeLoaderGcDecisionKind.QUARANTINE_LOW_DIVERSITY
    drift = replace(first, cold_start_digest=sha256(b"wrong-cold"))
    assert assess_native_loader_gc(unload, gc, cold, drift, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b")).decision_kind is NativeLoaderGcDecisionKind.QUARANTINE_DIGEST_DRIFT


def test_nativecoldfold_happy_path() -> None:
    report = audit_native_cold_fold(ROOT, revision="rev0089", artifact_stem=ROOT.name)
    assert report.status == "pass"
    assert report.predecessor_status == "pass"
    assert report.foldmap_status == "pass"
    assert report.foldregistry_status == "pass"
    assert report.surface_ledger_status == "pass"
