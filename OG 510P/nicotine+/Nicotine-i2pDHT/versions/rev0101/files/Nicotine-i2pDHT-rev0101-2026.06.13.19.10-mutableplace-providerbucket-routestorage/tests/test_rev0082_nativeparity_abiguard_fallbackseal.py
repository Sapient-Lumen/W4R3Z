from __future__ import annotations

import ctypes
import shutil
import subprocess
from dataclasses import replace
from pathlib import Path

import pytest

from i2p_dht_lab.abiguard import AbiGuardDecisionKind, NativeArtifactManifest, NativeRuntimeProbe, assess_native_abi
from i2p_dht_lab.fallbackseal import FallbackSealDecisionKind, seal_native_or_fallback
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.nativehotpaths import expected_native_symbols, native_xor_source_path
from i2p_dht_lab.nativeparity import NativeParityDecisionKind, default_xor_parity_vectors, evaluate_xor_native_parity
from i2p_dht_lab.nativeparityfold import audit_native_parity_fold

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
    assert lib.i2pdht_abi_version() == 1
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
        notes="rev0082 parity test artifact",
    )
    probe = NativeRuntimeProbe(
        artifact_present=True,
        abi_version=1,
        symbols_present=expected_native_symbols(),
        source_digest=source_digest,
        compiler_flags_digest=flags_digest,
        object_digest=object_digest,
        max_input_len=32,
    )
    return manifest, probe


def test_native_parity_accepts_missing_native_as_python_fallback() -> None:
    report = evaluate_xor_native_parity(native_compare=None, require_native=False)
    assert report.decision_kind is NativeParityDecisionKind.USE_PYTHON_FALLBACK_NATIVE_MISSING
    assert report.accepted
    assert report.fallback_allowed
    assert not report.native_allowed

    required = evaluate_xor_native_parity(native_compare=None, require_native=True)
    assert required.decision_kind is NativeParityDecisionKind.QUARANTINE_REQUIRE_NATIVE_MISSING
    assert not required.accepted


def test_native_parity_quarantines_mismatch_and_exception() -> None:
    def wrong(_pivot: bytes, _left: bytes, _right: bytes) -> int:
        return 42

    mismatch = evaluate_xor_native_parity(native_compare=wrong)
    assert mismatch.decision_kind is NativeParityDecisionKind.QUARANTINE_NATIVE_MISMATCH
    assert mismatch.mismatch_count > 0
    assert mismatch.fallback_allowed

    def boom(_pivot: bytes, _left: bytes, _right: bytes) -> int:
        raise RuntimeError("native leaf exploded")

    exploded = evaluate_xor_native_parity(native_compare=boom)
    assert exploded.decision_kind is NativeParityDecisionKind.QUARANTINE_NATIVE_EXCEPTION
    assert exploded.exception_count == len(default_xor_parity_vectors())


def test_native_parity_accepts_real_compiled_leaf(tmp_path: Path) -> None:
    shared = _compile_xor_shared(tmp_path)
    parity = evaluate_xor_native_parity(native_compare=_native_callable(shared))
    assert parity.decision_kind is NativeParityDecisionKind.ACCEPT_NATIVE_PARITY
    assert parity.native_allowed
    assert parity.mismatch_count == 0
    assert parity.exception_count == 0


def test_abi_guard_accepts_compiled_artifact_and_rejects_drift(tmp_path: Path) -> None:
    shared = _compile_xor_shared(tmp_path)
    manifest, probe = _manifest_and_probe(shared)
    ok = assess_native_abi(manifest, probe)
    assert ok.decision_kind is AbiGuardDecisionKind.ACCEPT_NATIVE_ARTIFACT
    assert ok.native_allowed

    assert assess_native_abi(manifest, replace(probe, abi_version=2)).decision_kind is AbiGuardDecisionKind.QUARANTINE_ABI_VERSION
    assert assess_native_abi(manifest, replace(probe, symbols_present=("i2pdht_abi_version",))).decision_kind is AbiGuardDecisionKind.QUARANTINE_SYMBOL_SET
    assert assess_native_abi(manifest, replace(probe, source_digest=sha256(b"other-source"))).decision_kind is AbiGuardDecisionKind.QUARANTINE_SOURCE_DIGEST
    assert assess_native_abi(manifest, replace(probe, compiler_flags_digest=sha256(b"-O0"))).decision_kind is AbiGuardDecisionKind.QUARANTINE_COMPILER_FLAGS
    assert assess_native_abi(manifest, replace(probe, max_input_len=64)).decision_kind is AbiGuardDecisionKind.QUARANTINE_INPUT_LIMIT

    missing = assess_native_abi(manifest, replace(probe, artifact_present=False, abi_version=None, symbols_present=(), source_digest=None, compiler_flags_digest=None, object_digest=None, max_input_len=None))
    assert missing.decision_kind is AbiGuardDecisionKind.USE_FALLBACK_ARTIFACT_MISSING
    assert missing.fallback_allowed

    no_fallback = assess_native_abi(replace(manifest, fallback_available=False), probe)
    assert no_fallback.decision_kind is AbiGuardDecisionKind.QUARANTINE_NO_FALLBACK
    assert not no_fallback.fallback_allowed


def test_fallback_seal_selects_native_only_after_parity_and_abi(tmp_path: Path) -> None:
    shared = _compile_xor_shared(tmp_path)
    manifest, probe = _manifest_and_probe(shared)
    parity = evaluate_xor_native_parity(native_compare=_native_callable(shared))
    abi = assess_native_abi(manifest, probe)
    selected = seal_native_or_fallback(parity, abi)
    assert selected.decision_kind is FallbackSealDecisionKind.USE_NATIVE_LEAF_WITH_PYTHON_ORACLE
    assert selected.native_selected
    assert selected.fallback_selected

    missing_parity = evaluate_xor_native_parity(native_compare=None)
    missing_abi = assess_native_abi(manifest, replace(probe, artifact_present=False, abi_version=None, symbols_present=(), source_digest=None, compiler_flags_digest=None, object_digest=None, max_input_len=None))
    fallback = seal_native_or_fallback(missing_parity, missing_abi)
    assert fallback.decision_kind is FallbackSealDecisionKind.USE_PYTHON_FALLBACK_NATIVE_MISSING
    assert fallback.fallback_selected
    assert not fallback.native_selected

    required = seal_native_or_fallback(missing_parity, missing_abi, native_required=True)
    assert required.decision_kind is FallbackSealDecisionKind.QUARANTINE_NATIVE_REQUIRED_PROFILE
    assert not required.accepted


def test_fallback_seal_quarantines_native_but_keeps_python_path(tmp_path: Path) -> None:
    shared = _compile_xor_shared(tmp_path)
    manifest, probe = _manifest_and_probe(shared)

    def wrong(_pivot: bytes, _left: bytes, _right: bytes) -> int:
        return 42

    parity = evaluate_xor_native_parity(native_compare=wrong)
    abi = assess_native_abi(manifest, probe)
    report = seal_native_or_fallback(parity, abi)
    assert report.decision_kind is FallbackSealDecisionKind.USE_PYTHON_FALLBACK_NATIVE_QUARANTINED
    assert report.accepted
    assert report.quarantine_native
    assert report.fallback_selected
    assert not report.native_selected


def test_nativeparityfold_happy_path() -> None:
    report = audit_native_parity_fold(ROOT, revision="rev0082", artifact_stem=ROOT.name)
    assert report.status == "pass"
    assert report.predecessor_status == "pass"
    assert report.foldmap_status == "pass"
    assert report.foldregistry_status == "pass"
    assert report.surface_ledger_status == "pass"
