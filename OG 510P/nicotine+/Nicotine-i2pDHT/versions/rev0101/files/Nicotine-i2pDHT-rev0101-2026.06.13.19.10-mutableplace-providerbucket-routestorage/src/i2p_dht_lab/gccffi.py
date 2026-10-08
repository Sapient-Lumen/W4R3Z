"""rev0081 GCC/FFI seam guard for native leaf kernels."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .bencode import bencode
from .ids import DOMAIN, sha256

GCC_FFI_DOMAIN = DOMAIN + b":gcc-ffi-boundary-v1:"


class FfiDecisionKind(str, Enum):
    ACCEPT_STABLE_LEAF_ABI = "accept_stable_leaf_abi"
    HOLD_MISSING_GUARDS = "hold_missing_guards"
    QUARANTINE_HEAP_OWNERSHIP = "quarantine_heap_ownership"
    QUARANTINE_UNTRUSTED_BYTES = "quarantine_untrusted_bytes"
    QUARANTINE_NO_FALLBACK = "quarantine_no_fallback"


@dataclass(frozen=True)
class GccFfiContract:
    symbol_prefix: str
    abi_version: int
    fixed_width_types: bool
    no_heap_ownership_transfer: bool
    no_callbacks: bool
    no_global_mutation: bool
    consumes_untrusted_network_bytes: bool
    deterministic: bool
    python_reference: bool
    golden_vectors: bool
    portable_python_fallback: bool
    endian_vectors: bool
    max_input_len: int
    notes: str = ""

    @property
    def contract_digest(self) -> bytes:
        return sha256(GCC_FFI_DOMAIN + b":contract:" + bencode({
            b"prefix": self.symbol_prefix,
            b"abi": self.abi_version,
            b"fixed": 1 if self.fixed_width_types else 0,
            b"heap": 1 if self.no_heap_ownership_transfer else 0,
            b"callbacks": 1 if self.no_callbacks else 0,
            b"globals": 1 if self.no_global_mutation else 0,
            b"untrusted": 1 if self.consumes_untrusted_network_bytes else 0,
            b"det": 1 if self.deterministic else 0,
            b"py_ref": 1 if self.python_reference else 0,
            b"golden": 1 if self.golden_vectors else 0,
            b"fallback": 1 if self.portable_python_fallback else 0,
            b"endian": 1 if self.endian_vectors else 0,
            b"max": self.max_input_len,
            b"notes": self.notes,
        }))


@dataclass(frozen=True)
class GccFfiAssessment:
    decision_kind: FfiDecisionKind
    accepted: bool
    watch: bool
    obligations: tuple[str, ...]
    contract_digest: bytes

    @property
    def report_digest(self) -> bytes:
        return sha256(GCC_FFI_DOMAIN + b":assessment:" + bencode({
            b"decision": FfiDecisionKind(self.decision_kind).value,
            b"accepted": 1 if self.accepted else 0,
            b"watch": 1 if self.watch else 0,
            b"obligations": list(self.obligations),
            b"contract": self.contract_digest,
        }))


def assess_gcc_ffi_contract(contract: GccFfiContract) -> GccFfiAssessment:
    if not contract.no_heap_ownership_transfer or contract.max_input_len <= 0:
        return GccFfiAssessment(FfiDecisionKind.QUARANTINE_HEAP_OWNERSHIP, False, False, ("no-cross-boundary-heap-ownership", "bounded-inputs"), contract.contract_digest)
    if contract.consumes_untrusted_network_bytes:
        return GccFfiAssessment(FfiDecisionKind.QUARANTINE_UNTRUSTED_BYTES, False, True, ("parser-wall-before-native", "fuzz-sanitizer-differential-tests"), contract.contract_digest)
    if not contract.portable_python_fallback:
        return GccFfiAssessment(FfiDecisionKind.QUARANTINE_NO_FALLBACK, False, True, ("keep-python-fallback",), contract.contract_digest)
    missing = []
    if not contract.symbol_prefix.startswith("i2pdht_"):
        missing.append("symbol-prefix")
    if contract.abi_version < 1:
        missing.append("abi-version")
    if not contract.fixed_width_types:
        missing.append("fixed-width-types")
    if not contract.no_callbacks:
        missing.append("no-callbacks")
    if not contract.no_global_mutation:
        missing.append("no-global-mutation")
    if not contract.deterministic:
        missing.append("determinism")
    if not contract.python_reference:
        missing.append("python-reference")
    if not contract.golden_vectors:
        missing.append("golden-vectors")
    if not contract.endian_vectors:
        missing.append("endian-vectors")
    if missing:
        return GccFfiAssessment(FfiDecisionKind.HOLD_MISSING_GUARDS, False, True, tuple(missing), contract.contract_digest)
    return GccFfiAssessment(
        FfiDecisionKind.ACCEPT_STABLE_LEAF_ABI,
        True,
        False,
        ("keep-python-reference", "compile-both-debug-and-release-before-production", "fuzz-before-production"),
        contract.contract_digest,
    )
