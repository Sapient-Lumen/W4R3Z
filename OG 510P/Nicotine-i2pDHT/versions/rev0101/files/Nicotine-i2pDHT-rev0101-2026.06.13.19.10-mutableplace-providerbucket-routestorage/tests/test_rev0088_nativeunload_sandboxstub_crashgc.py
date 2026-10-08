from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path

from i2p_dht_lab.ids import sha256
from i2p_dht_lab.nativecontrolfold import audit_native_control_fold
from i2p_dht_lab.nativecrashgc import NativeCrashGcDecisionKind, NativeCrashGcProposal, assess_native_crash_gc
from i2p_dht_lab.nativecrashledger import NativeCrashDecisionKind
from i2p_dht_lab.nativeload import NativeLoadDecisionKind
from i2p_dht_lab.nativeperfguard import NativePerfDecisionKind
from i2p_dht_lab.nativesandboxstub import NativeSandboxDecisionKind, NativeSandboxPlan, assess_native_sandbox_stub
from i2p_dht_lab.nativeunload import NativeUnloadDecisionKind, NativeUnloadIntent, assess_native_unload

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


def _unload_intent(load=FakeLoad(), crash=FakeCrash(), perf=FakePerf(), *, seq=1, prev=b"", reason="keep_loaded", loaded=True, preserve=True, block=True, note="") -> NativeUnloadIntent:
    return NativeUnloadIntent(
        component="xor_distance",
        profile="portable-default",
        operation="xor_compare",
        request_id="rev0088-native",
        sequence=seq,
        previous_digest=prev,
        load_digest=load.report_digest,
        crash_digest=crash.report_digest,
        perf_digest=perf.report_digest,
        artifact_digest=load.artifact_digest,
        source_digest=load.source_digest,
        fallback_digest=load.fallback_digest,
        unload_reason=reason,
        native_loaded_before=loaded,
        preserve_fallback_memory=preserve,
        preserve_quarantine_memory=preserve,
        block_new_dispatch=block,
        family_id="family-a",
        path_family_id="path-a",
        note=note,
    )


def _unload(load=FakeLoad(), crash=FakeCrash(), perf=FakePerf(), intent: NativeUnloadIntent | None = None):
    return assess_native_unload(load, crash, perf, intent or _unload_intent(load, crash, perf), observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b"))


def _sandbox_plan(load, unload, *, seq=1, prev=b"", native=True, ack=True, fallback=True, isolation="ctypes_leaf_stub", untrusted=False, crypto=False, net=False, fs=False, proc=False, threads=False, dyn=False, max_input=64, runtime=10_000, note="") -> NativeSandboxPlan:
    return NativeSandboxPlan(
        component="xor_distance",
        profile="portable-default",
        operation="xor_compare",
        request_id="rev0088-native",
        sequence=seq,
        previous_digest=prev,
        load_digest=load.report_digest,
        unload_digest=unload.report_digest,
        isolation_kind=isolation,
        native_execution_requested=native,
        nonproduction_stub_ack=ack,
        python_fallback_available=fallback,
        touches_untrusted_bytes=untrusted,
        touches_crypto_or_secret_keys=crypto,
        allow_filesystem=fs,
        allow_network=net,
        allow_process_spawn=proc,
        allow_threads=threads,
        allow_dynamic_load=dyn,
        max_input_bytes=max_input,
        max_runtime_us=runtime,
        family_id="family-a",
        path_family_id="path-a",
        note=note,
    )


def _sandbox(load, unload, plan=None):
    return assess_native_sandbox_stub(load, unload, plan or _sandbox_plan(load, unload), observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b"))


def _gc_proposal(crash, unload, *, seq=1, prev=b"", retained=None, dropped=(b"soft",), drop=False, preserve=True, budget=256, note="") -> NativeCrashGcProposal:
    retained = (crash.report_digest,) if retained is None else retained
    return NativeCrashGcProposal(
        component="xor_distance",
        profile="portable-default",
        operation="xor_compare",
        request_id="rev0088-native",
        sequence=seq,
        previous_digest=prev,
        crash_digest=crash.report_digest,
        unload_digest=unload.report_digest,
        retained_fault_digests=retained,
        dropped_soft_digests=tuple(sha256(x) if isinstance(x, bytes) else x for x in dropped),
        drop_active_faults=drop,
        preserve_fallback_memory=preserve,
        preserve_quarantine_memory=preserve,
        preserve_crash_digest=preserve,
        byte_budget=budget,
        family_id="family-a",
        path_family_id="path-a",
        note=note,
    )


def _gc(crash, unload, proposal=None):
    return assess_native_crash_gc(crash, unload, proposal or _gc_proposal(crash, unload), observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b"))


def test_native_unload_forces_faults_to_fallback_and_quarantine() -> None:
    load = FakeLoad(); perf = FakePerf(); clean_crash = FakeCrash()
    keep = _unload(load, clean_crash, perf)
    assert keep.decision_kind is NativeUnloadDecisionKind.ACCEPT_KEEP_LOADED
    assert not keep.unloaded
    assert keep.fallback_active

    fault = FakeCrash(fallback_required=True, quarantine=True, fault_kind="wrong_result")
    unload = _unload(load, fault, perf, _unload_intent(load, fault, perf, reason="fault_quarantine"))
    assert unload.decision_kind is NativeUnloadDecisionKind.ACCEPT_UNLOAD_TO_FALLBACK
    assert unload.unloaded and unload.quarantine

    keep_fault = _unload(load, fault, perf, _unload_intent(load, fault, perf, reason="keep_loaded"))
    assert keep_fault.decision_kind is NativeUnloadDecisionKind.QUARANTINE_KEEP_LOADED_AFTER_FAULT

    drop_memory = _unload(load, fault, perf, _unload_intent(load, fault, perf, reason="fault_quarantine", preserve=False))
    assert drop_memory.decision_kind is NativeUnloadDecisionKind.QUARANTINE_MEMORY_DROP


def test_native_unload_detects_replay_fork_previous_link_low_diversity_and_drift() -> None:
    first = _unload_intent()
    assert assess_native_unload(FakeLoad(), FakeCrash(), FakePerf(), first, prior_intent_digests=(first.intent_digest,), observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b")).decision_kind is NativeUnloadDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK
    assert assess_native_unload(FakeLoad(), FakeCrash(), FakePerf(), replace(first, note="fork"), previous=first, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b")).decision_kind is NativeUnloadDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK
    bad_link = _unload_intent(seq=2, prev=sha256(b"bad-prev"))
    assert assess_native_unload(FakeLoad(), FakeCrash(), FakePerf(), bad_link, previous=first, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b")).decision_kind is NativeUnloadDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH
    assert assess_native_unload(FakeLoad(), FakeCrash(), FakePerf(), first, observed_families=("family-a",), observed_path_families=("path-a",), min_families=2, min_path_families=2).decision_kind is NativeUnloadDecisionKind.QUARANTINE_LOW_DIVERSITY
    drift = replace(first, source_digest=sha256(b"wrong-source"))
    assert _unload(intent=drift).decision_kind is NativeUnloadDecisionKind.QUARANTINE_DIGEST_DRIFT


def test_sandbox_stub_accepts_tiny_leaf_and_blocks_dangerous_surfaces() -> None:
    load = FakeLoad(); clean = _unload(load, FakeCrash(), FakePerf())
    accepted = _sandbox(load, clean)
    assert accepted.decision_kind is NativeSandboxDecisionKind.ACCEPT_NO_NETWORK_STUB
    assert accepted.native_execution_allowed

    assert _sandbox(load, clean, _sandbox_plan(load, clean, untrusted=True)).decision_kind is NativeSandboxDecisionKind.QUARANTINE_UNTRUSTED_BYTES_OR_CRYPTO
    assert _sandbox(load, clean, _sandbox_plan(load, clean, crypto=True)).decision_kind is NativeSandboxDecisionKind.QUARANTINE_UNTRUSTED_BYTES_OR_CRYPTO
    assert _sandbox(load, clean, _sandbox_plan(load, clean, net=True)).decision_kind is NativeSandboxDecisionKind.QUARANTINE_IO_OR_PROCESS_POWER
    assert _sandbox(load, clean, _sandbox_plan(load, clean, fallback=False)).decision_kind is NativeSandboxDecisionKind.QUARANTINE_NO_FALLBACK
    assert _sandbox(load, clean, _sandbox_plan(load, clean, max_input=999_999)).decision_kind is NativeSandboxDecisionKind.QUARANTINE_BOUNDS
    assert _sandbox(load, clean, _sandbox_plan(load, clean, ack=False)).decision_kind is NativeSandboxDecisionKind.HOLD_SANDBOX_NOT_PRODUCTION

    fault = FakeCrash(fallback_required=True, quarantine=True, fault_kind="segfault")
    unloaded = _unload(load, fault, FakePerf(), _unload_intent(load, fault, FakePerf(), reason="fault_quarantine"))
    assert _sandbox(load, unloaded, _sandbox_plan(load, unloaded, native=True)).decision_kind is NativeSandboxDecisionKind.QUARANTINE_NATIVE_REQUEST_AFTER_UNLOAD
    assert _sandbox(load, unloaded, _sandbox_plan(load, unloaded, native=False)).decision_kind is NativeSandboxDecisionKind.ACCEPT_FALLBACK_ONLY


def test_sandbox_stub_detects_replay_fork_previous_link_and_low_diversity() -> None:
    load = FakeLoad(); unload = _unload(load, FakeCrash(), FakePerf()); first = _sandbox_plan(load, unload)
    assert assess_native_sandbox_stub(load, unload, first, prior_plan_digests=(first.plan_digest,), observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b")).decision_kind is NativeSandboxDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK
    assert assess_native_sandbox_stub(load, unload, replace(first, note="fork"), previous=first, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b")).decision_kind is NativeSandboxDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK
    bad_link = _sandbox_plan(load, unload, seq=2, prev=sha256(b"bad-prev"))
    assert assess_native_sandbox_stub(load, unload, bad_link, previous=first, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b")).decision_kind is NativeSandboxDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH
    assert assess_native_sandbox_stub(load, unload, first, observed_families=("family-a",), observed_path_families=("path-a",), min_families=2, min_path_families=2).decision_kind is NativeSandboxDecisionKind.QUARANTINE_LOW_DIVERSITY


def test_crash_gc_retains_active_faults_and_compacts_only_soft_memory() -> None:
    load = FakeLoad(); perf = FakePerf()
    fault = FakeCrash(fallback_required=True, quarantine=True, fault_kind="memory_fault")
    unloaded = _unload(load, fault, perf, _unload_intent(load, fault, perf, reason="fault_quarantine"))
    retained = _gc(fault, unloaded)
    assert retained.decision_kind is NativeCrashGcDecisionKind.HOLD_RETAIN_ACTIVE_FAULT
    assert retained.retained_hard_fault

    drop = _gc(fault, unloaded, _gc_proposal(fault, unloaded, retained=(), drop=True))
    assert drop.decision_kind is NativeCrashGcDecisionKind.QUARANTINE_HARD_FAULT_DROP

    memory_drop = _gc(fault, unloaded, _gc_proposal(fault, unloaded, preserve=False))
    assert memory_drop.decision_kind is NativeCrashGcDecisionKind.QUARANTINE_MEMORY_DROP

    budget = _gc(fault, unloaded, _gc_proposal(fault, unloaded, budget=1))
    assert budget.decision_kind is NativeCrashGcDecisionKind.HOLD_INSUFFICIENT_BUDGET

    clean = FakeCrash(); clean_unload = _unload(load, clean, perf, _unload_intent(load, clean, perf, reason="normal_shutdown"))
    soft = _gc(clean, clean_unload, _gc_proposal(clean, clean_unload, retained=(), dropped=(b"slow-path",)))
    assert soft.decision_kind is NativeCrashGcDecisionKind.ACCEPT_SOFT_GC


def test_crash_gc_detects_replay_fork_previous_link_low_diversity_and_drift() -> None:
    fault = FakeCrash(fallback_required=True, quarantine=True, fault_kind="timeout")
    unload = _unload(FakeLoad(), fault, FakePerf(), _unload_intent(FakeLoad(), fault, FakePerf(), reason="fault_quarantine"))
    first = _gc_proposal(fault, unload)
    assert assess_native_crash_gc(fault, unload, first, prior_proposal_digests=(first.proposal_digest,), observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b")).decision_kind is NativeCrashGcDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK
    assert assess_native_crash_gc(fault, unload, replace(first, note="fork"), previous=first, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b")).decision_kind is NativeCrashGcDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK
    bad_link = _gc_proposal(fault, unload, seq=2, prev=sha256(b"bad-prev"))
    assert assess_native_crash_gc(fault, unload, bad_link, previous=first, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b")).decision_kind is NativeCrashGcDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH
    assert assess_native_crash_gc(fault, unload, first, observed_families=("family-a",), observed_path_families=("path-a",), min_families=2, min_path_families=2).decision_kind is NativeCrashGcDecisionKind.QUARANTINE_LOW_DIVERSITY
    drift = replace(first, unload_digest=sha256(b"wrong-unload"))
    assert _gc(fault, unload, drift).decision_kind is NativeCrashGcDecisionKind.QUARANTINE_DIGEST_DRIFT


def test_nativecontrolfold_happy_path() -> None:
    report = audit_native_control_fold(ROOT, revision="rev0088", artifact_stem=ROOT.name)
    assert report.status == "pass"
    assert report.predecessor_status == "pass"
    assert report.foldmap_status == "pass"
    assert report.foldregistry_status == "pass"
    assert report.surface_ledger_status == "pass"
