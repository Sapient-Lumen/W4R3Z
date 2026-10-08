from __future__ import annotations

import ctypes
import shutil
import subprocess
from dataclasses import replace
from pathlib import Path

import pytest

from i2p_dht_lab.abiguard import NativeArtifactManifest, NativeRuntimeProbe, assess_native_abi
from i2p_dht_lab.fallbackseal import seal_native_or_fallback
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.nativeaudit import NativeSourceAuditDecisionKind, audit_native_leaf_source
from i2p_dht_lab.nativedispatch import NativeCallRequest, NativeDispatchDecisionKind, seal_xor_dispatch
from i2p_dht_lab.nativedispatchfold import audit_native_dispatch_fold
from i2p_dht_lab.nativehotpaths import expected_native_symbols, native_xor_source_path
from i2p_dht_lab.nativeparity import evaluate_xor_native_parity
from i2p_dht_lab.nativeruntime import NativeRuntimeDecisionKind, NativeRuntimeStamp, assess_native_runtime

ROOT = Path(__file__).resolve().parents[1]
COMPILE_FLAGS = ("-shared", "-fPIC", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror")


def _compile_xor_shared(tmp_path: Path) -> Path:
    gcc = shutil.which("gcc")
    if not gcc:
        pytest.skip("gcc not available in this runner")
    source = native_xor_source_path(ROOT)
    shared = tmp_path / "libi2pdht_xor_distance.so"
    subprocess.run([gcc, *COMPILE_FLAGS, str(source), "-o", str(shared)], cwd=ROOT, check=True, capture_output=True, text=True)
    return shared


def _native_callable(shared: Path):
    lib = ctypes.CDLL(str(shared))
    lib.i2pdht_xor_compare.argtypes = [ctypes.POINTER(ctypes.c_uint8), ctypes.POINTER(ctypes.c_uint8), ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t]
    lib.i2pdht_xor_compare.restype = ctypes.c_int

    def compare(pivot: bytes, left: bytes, right: bytes) -> int:
        arr = ctypes.c_uint8 * len(pivot)
        return int(lib.i2pdht_xor_compare(arr.from_buffer_copy(pivot), arr.from_buffer_copy(left), arr.from_buffer_copy(right), len(pivot)))

    return compare


def _manifest_and_probe(shared: Path) -> tuple[NativeArtifactManifest, NativeRuntimeProbe]:
    source = native_xor_source_path(ROOT)
    source_digest = sha256(source.read_bytes())
    flags_digest = sha256(" ".join(COMPILE_FLAGS).encode("utf-8"))
    object_digest = sha256(shared.read_bytes())
    manifest = NativeArtifactManifest(
        component="xor_distance",
        abi_version=1,
        required_symbols=expected_native_symbols(),
        source_digest=source_digest,
        compiler_flags_digest=flags_digest,
        object_digest=object_digest,
        max_input_len=32,
        fallback_available=True,
        notes="rev0083 runtime test artifact",
    )
    probe = NativeRuntimeProbe(True, 1, expected_native_symbols(), source_digest, flags_digest, object_digest, 32)
    return manifest, probe


def _accepted_native_runtime(tmp_path: Path):
    shared = _compile_xor_shared(tmp_path)
    manifest, probe = _manifest_and_probe(shared)
    parity = evaluate_xor_native_parity(native_compare=_native_callable(shared))
    abi = assess_native_abi(manifest, probe)
    fallback = seal_native_or_fallback(parity, abi)
    stamp = NativeRuntimeStamp(
        component="xor_distance",
        profile="portable-default",
        sequence=1,
        previous_digest=b"",
        parity_digest=parity.report_digest,
        abi_digest=abi.report_digest,
        fallback_seal_digest=fallback.report_digest,
        object_digest=probe.object_digest or b"",
        source_digest=probe.source_digest or b"",
        compiler_flags_digest=probe.compiler_flags_digest or b"",
        max_input_len=probe.max_input_len or 0,
        native_selected=True,
        fallback_selected=True,
        quarantine_native=False,
        family_id="builder-a",
        path_family_id="path-a",
    )
    runtime = assess_native_runtime(parity, abi, fallback, stamp, observed_families=("builder-a", "builder-b"), observed_path_families=("path-a", "path-b"), min_families=2, min_path_families=2)
    return shared, parity, abi, fallback, stamp, runtime


def test_runtime_accepts_native_only_when_stamp_matches(tmp_path: Path) -> None:
    _shared, parity, abi, fallback, stamp, runtime = _accepted_native_runtime(tmp_path)
    assert runtime.decision_kind is NativeRuntimeDecisionKind.ACCEPT_NATIVE_RUNTIME
    assert runtime.native_runtime_allowed
    assert runtime.fallback_runtime_allowed

    drift = replace(stamp, fallback_seal_digest=sha256(b"wrong-seal"), sequence=2, previous_digest=stamp.stamp_digest)
    report = assess_native_runtime(parity, abi, fallback, drift, previous=stamp)
    assert report.decision_kind is NativeRuntimeDecisionKind.QUARANTINE_STAMP_DRIFT

    same_seq_fork = replace(stamp, note="forked")
    assert assess_native_runtime(parity, abi, fallback, same_seq_fork, previous=stamp).decision_kind is NativeRuntimeDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK

    bad_link = replace(stamp, sequence=2, previous_digest=sha256(b"not-previous"))
    assert assess_native_runtime(parity, abi, fallback, bad_link, previous=stamp).decision_kind is NativeRuntimeDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH

    low_diversity = assess_native_runtime(parity, abi, fallback, stamp, observed_families=("one",), observed_path_families=("one",), min_families=2, min_path_families=2)
    assert low_diversity.decision_kind is NativeRuntimeDecisionKind.QUARANTINE_LOW_DIVERSITY


def test_runtime_accepts_python_fallback_when_native_missing(tmp_path: Path) -> None:
    shared = _compile_xor_shared(tmp_path)
    manifest, probe = _manifest_and_probe(shared)
    missing_probe = replace(probe, artifact_present=False, abi_version=None, symbols_present=(), source_digest=None, compiler_flags_digest=None, object_digest=None, max_input_len=None)
    parity = evaluate_xor_native_parity(native_compare=None)
    abi = assess_native_abi(manifest, missing_probe)
    fallback = seal_native_or_fallback(parity, abi)
    stamp = NativeRuntimeStamp("xor_distance", "portable-default", 1, b"", parity.report_digest, abi.report_digest, fallback.report_digest, b"", b"", b"", 32, False, True, False, "fallback-family", "fallback-path")
    runtime = assess_native_runtime(parity, abi, fallback, stamp)
    assert runtime.decision_kind is NativeRuntimeDecisionKind.ACCEPT_PYTHON_FALLBACK_RUNTIME
    assert runtime.fallback_runtime_allowed
    assert not runtime.native_runtime_allowed


def test_dispatch_seal_accepts_native_and_fallback_paths(tmp_path: Path) -> None:
    shared, _parity, _abi, _fallback, _stamp, runtime = _accepted_native_runtime(tmp_path)
    request = NativeCallRequest("xor_distance", "xor_compare", "req-1", b"\x00" * 32, b"\x01" + b"\x00" * 31, b"\x02" + b"\x00" * 31, 32)
    native = seal_xor_dispatch(runtime, request, native_compare=_native_callable(shared))
    assert native.decision_kind is NativeDispatchDecisionKind.ACCEPT_NATIVE_DISPATCH
    assert native.result == -1
    assert native.native_used

    fallback = seal_xor_dispatch(replace(runtime, native_runtime_allowed=False, watch=True), replace(request, request_id="req-2"), native_compare=None)
    assert fallback.decision_kind is NativeDispatchDecisionKind.ACCEPT_PYTHON_FALLBACK_DISPATCH
    assert fallback.result == -1
    assert fallback.fallback_used


def test_dispatch_seal_quarantines_mismatch_replay_operation_and_limits(tmp_path: Path) -> None:
    _shared, _parity, _abi, _fallback, _stamp, runtime = _accepted_native_runtime(tmp_path)
    request = NativeCallRequest("xor_distance", "xor_compare", "req-1", b"\x00" * 32, b"\x01" + b"\x00" * 31, b"\x02" + b"\x00" * 31, 32)

    def wrong(_pivot: bytes, _left: bytes, _right: bytes) -> int:
        return 1

    mismatch = seal_xor_dispatch(runtime, request, native_compare=wrong)
    assert mismatch.decision_kind is NativeDispatchDecisionKind.QUARANTINE_NATIVE_RESULT_MISMATCH

    replay = seal_xor_dispatch(runtime, request, prior_request_digests=(request.request_digest,))
    assert replay.decision_kind is NativeDispatchDecisionKind.QUARANTINE_REQUEST_REPLAY

    bad_operation = seal_xor_dispatch(runtime, replace(request, operation="sort"))
    assert bad_operation.decision_kind is NativeDispatchDecisionKind.QUARANTINE_OPERATION_MISMATCH

    too_large = seal_xor_dispatch(runtime, replace(request, max_input_len=8))
    assert too_large.decision_kind is NativeDispatchDecisionKind.QUARANTINE_INPUT_LIMIT


def test_native_source_audit_accepts_leaf_and_rejects_danger() -> None:
    source = native_xor_source_path(ROOT).read_text(encoding="utf-8")
    ok = audit_native_leaf_source(source, required_symbols=expected_native_symbols())
    assert ok.decision_kind is NativeSourceAuditDecisionKind.ACCEPT_LEAF_SOURCE
    assert ok.accepted

    dangerous = audit_native_leaf_source(source + "\nvoid *x = malloc(4);\n", required_symbols=expected_native_symbols())
    assert dangerous.decision_kind is NativeSourceAuditDecisionKind.QUARANTINE_DANGEROUS_TOKEN
    assert "malloc" in dangerous.dangerous_tokens

    missing = audit_native_leaf_source("int nothing(void) { return 0; }", required_symbols=expected_native_symbols(), require_version_comment=False)
    assert missing.decision_kind is NativeSourceAuditDecisionKind.QUARANTINE_MISSING_SYMBOL

    too_large = audit_native_leaf_source(source + ("/*pad*/" * 2000), required_symbols=expected_native_symbols(), max_bytes=128)
    assert too_large.decision_kind is NativeSourceAuditDecisionKind.QUARANTINE_SOURCE_TOO_LARGE


def test_nativedispatchfold_happy_path() -> None:
    report = audit_native_dispatch_fold(ROOT, revision="rev0083", artifact_stem=ROOT.name)
    assert report.status == "pass"
    assert report.predecessor_status == "pass"
    assert report.foldmap_status == "pass"
    assert report.foldregistry_status == "pass"
    assert report.surface_ledger_status == "pass"
