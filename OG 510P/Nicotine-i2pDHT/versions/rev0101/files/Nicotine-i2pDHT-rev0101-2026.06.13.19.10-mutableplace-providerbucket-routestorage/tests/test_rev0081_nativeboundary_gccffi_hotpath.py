from __future__ import annotations

import ctypes
import shutil
import subprocess
from dataclasses import replace
from pathlib import Path

import pytest

from i2p_dht_lab.gccffi import FfiDecisionKind, GccFfiContract, assess_gcc_ffi_contract
from i2p_dht_lab.nativeboundary import ComponentKind, LanguageLane, NativeBoundaryDecisionKind, NativeCandidate, assess_native_candidate, default_language_matrix, summarize_language_plan
from i2p_dht_lab.nativeboundaryfold import audit_native_boundary_fold
from i2p_dht_lab.nativehotpaths import native_xor_source_path, sort_by_xor_reference, xor_compare_reference

ROOT = Path(__file__).resolve().parents[1]


def test_native_boundary_matrix_answers_gcc_question() -> None:
    plan = summarize_language_plan(default_language_matrix())
    assert plan[ComponentKind.PROTOCOL_STATE.value] == NativeBoundaryDecisionKind.KEEP_PYTHON.value
    assert plan[ComponentKind.I2P_TRANSPORT_CONTROL.value] == NativeBoundaryDecisionKind.KEEP_PYTHON.value
    assert plan[ComponentKind.UNTRUSTED_BYTE_PARSER.value] == NativeBoundaryDecisionKind.REJECT_NATIVE_FOR_NOW.value
    assert plan[ComponentKind.CRYPTO_IMPLEMENTATION.value] == NativeBoundaryDecisionKind.QUARANTINE_HAND_ROLLED_CRYPTO.value
    assert plan[ComponentKind.XOR_DISTANCE_HOTPATH.value] == NativeBoundaryDecisionKind.ACCEPT_GCC_LEAF_KERNEL.value


def test_native_boundary_rejects_cross_boundary_heap_and_semantic_native() -> None:
    semantic = NativeCandidate(
        ComponentKind.MUTABLE_HEAD_ACCEPTANCE,
        LanguageLane.GCC_C_LEAF,
        deterministic=True,
        side_effect_free=False,
        owns_heap_across_boundary=False,
        consumes_untrusted_bytes=False,
        has_python_reference=True,
        has_golden_vectors=True,
        has_fuzz_harness=True,
        has_sanitizer_profile=True,
        portable_fallback=True,
        stable_abi=True,
        reason="tempting rewrite",
    )
    assert assess_native_candidate(semantic).decision_kind is NativeBoundaryDecisionKind.KEEP_PYTHON

    heap_crossing = replace(default_language_matrix()[-2], owns_heap_across_boundary=True)
    decision = assess_native_candidate(heap_crossing)
    assert not decision.native_allowed
    assert decision.decision_kind is NativeBoundaryDecisionKind.REJECT_NATIVE_FOR_NOW


def test_gcc_ffi_contract_accepts_only_narrow_leaf_abi() -> None:
    contract = GccFfiContract(
        symbol_prefix="i2pdht_",
        abi_version=1,
        fixed_width_types=True,
        no_heap_ownership_transfer=True,
        no_callbacks=True,
        no_global_mutation=True,
        consumes_untrusted_network_bytes=False,
        deterministic=True,
        python_reference=True,
        golden_vectors=True,
        portable_python_fallback=True,
        endian_vectors=True,
        max_input_len=32,
        notes="xor compare hotpath",
    )
    assert assess_gcc_ffi_contract(contract).decision_kind is FfiDecisionKind.ACCEPT_STABLE_LEAF_ABI

    assert assess_gcc_ffi_contract(replace(contract, consumes_untrusted_network_bytes=True)).decision_kind is FfiDecisionKind.QUARANTINE_UNTRUSTED_BYTES
    assert assess_gcc_ffi_contract(replace(contract, no_heap_ownership_transfer=False)).decision_kind is FfiDecisionKind.QUARANTINE_HEAP_OWNERSHIP
    assert assess_gcc_ffi_contract(replace(contract, portable_python_fallback=False)).decision_kind is FfiDecisionKind.QUARANTINE_NO_FALLBACK
    assert assess_gcc_ffi_contract(replace(contract, endian_vectors=False)).decision_kind is FfiDecisionKind.HOLD_MISSING_GUARDS


def _compile_xor_shared(tmp_path: Path) -> Path:
    gcc = shutil.which("gcc")
    if not gcc:
        pytest.skip("gcc not available in this runner")
    source = native_xor_source_path(ROOT)
    shared = tmp_path / "libi2pdht_xor_distance.so"
    subprocess.run(
        [gcc, "-shared", "-fPIC", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", str(source), "-o", str(shared)],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return shared


def test_gcc_leaf_kernel_matches_python_reference_when_compiled(tmp_path: Path) -> None:
    shared = _compile_xor_shared(tmp_path)
    lib = ctypes.CDLL(str(shared))
    assert lib.i2pdht_abi_version() == 1
    lib.i2pdht_xor_compare.argtypes = [ctypes.POINTER(ctypes.c_uint8), ctypes.POINTER(ctypes.c_uint8), ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t]
    lib.i2pdht_xor_compare.restype = ctypes.c_int

    vectors = []
    for i in range(16):
        pivot = bytes(((j * 17 + i) % 256) for j in range(32))
        left = bytes(((j * 13 + i * 3) % 256) for j in range(32))
        right = bytes(((j * 19 + i * 5 + 7) % 256) for j in range(32))
        vectors.append((pivot, left, right))
    vectors.append((b"\x00" * 32, b"\x00" * 32, b"\x01" + b"\x00" * 31))
    vectors.append((b"\xff" * 32, b"\x00" * 32, b"\xff" * 32))

    for pivot, left, right in vectors:
        arr = ctypes.c_uint8 * len(pivot)
        got = lib.i2pdht_xor_compare(arr.from_buffer_copy(pivot), arr.from_buffer_copy(left), arr.from_buffer_copy(right), len(pivot))
        expected = xor_compare_reference(pivot, left, right)
        assert got == expected

    pivot = bytes(range(32))
    candidates = tuple(bytes(((j * (k + 3) + k) % 256) for j in range(32)) for k in range(8))
    assert sort_by_xor_reference(pivot, candidates)[0] == min(candidates, key=lambda c: bytes(a ^ b for a, b in zip(pivot, c)))


def test_nativeboundaryfold_happy_path() -> None:
    report = audit_native_boundary_fold(ROOT, revision="rev0081", artifact_stem=ROOT.name)
    assert report.status == "pass"
    assert report.predecessor_status == "pass"
    assert report.foldmap_status == "pass"
    assert report.foldregistry_status == "pass"
    assert report.surface_ledger_status == "pass"
