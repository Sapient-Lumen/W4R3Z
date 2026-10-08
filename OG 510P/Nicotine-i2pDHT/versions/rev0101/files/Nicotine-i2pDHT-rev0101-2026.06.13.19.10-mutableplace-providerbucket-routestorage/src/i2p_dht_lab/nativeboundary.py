"""rev0081 language/native-boundary policy for the I2P DHT cube.

This module answers the GCC question in executable form.  The current guess is
not "rewrite the DHT in C".  It is "keep the semantics in Python while allowing
small, deterministic, side-effect-free native kernels behind a narrow ABI".
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .bencode import bencode
from .ids import DOMAIN, sha256

NATIVE_BOUNDARY_DOMAIN = DOMAIN + b":native-boundary-v1:"


class ComponentKind(str, Enum):
    PROTOCOL_STATE = "protocol_state"
    MUTABLE_HEAD_ACCEPTANCE = "mutable_head_acceptance"
    POLICY_GOVERNANCE = "policy_governance"
    I2P_TRANSPORT_CONTROL = "i2p_transport_control"
    UNTRUSTED_BYTE_PARSER = "untrusted_byte_parser"
    CRYPTO_IMPLEMENTATION = "crypto_implementation"
    XOR_DISTANCE_HOTPATH = "xor_distance_hotpath"
    RANGE_SKETCH_KERNEL = "range_sketch_kernel"
    SET_RECONCILIATION_KERNEL = "set_reconciliation_kernel"
    BULK_HASH_PIPELINE = "bulk_hash_pipeline"


class LanguageLane(str, Enum):
    PYTHON_FIRST = "python_first"
    GCC_C_LEAF = "gcc_c_leaf"
    VETTED_NATIVE_LIBRARY = "vetted_native_library"
    DEFER_MEMORY_SAFE_NATIVE = "defer_memory_safe_native"


class NativeBoundaryDecisionKind(str, Enum):
    KEEP_PYTHON = "keep_python"
    ACCEPT_GCC_LEAF_KERNEL = "accept_gcc_leaf_kernel"
    USE_VETTED_NATIVE_LIBRARY = "use_vetted_native_library"
    HOLD_UNTIL_FUZZ_AND_SANITIZERS = "hold_until_fuzz_and_sanitizers"
    REJECT_NATIVE_FOR_NOW = "reject_native_for_now"
    QUARANTINE_HAND_ROLLED_CRYPTO = "quarantine_hand_rolled_crypto"


@dataclass(frozen=True)
class NativeCandidate:
    component_kind: ComponentKind
    language_lane: LanguageLane
    deterministic: bool
    side_effect_free: bool
    owns_heap_across_boundary: bool
    consumes_untrusted_bytes: bool
    has_python_reference: bool
    has_golden_vectors: bool
    has_fuzz_harness: bool
    has_sanitizer_profile: bool
    portable_fallback: bool
    stable_abi: bool
    reason: str = ""

    @property
    def candidate_digest(self) -> bytes:
        return sha256(NATIVE_BOUNDARY_DOMAIN + b":candidate:" + bencode({
            b"kind": ComponentKind(self.component_kind).value,
            b"lane": LanguageLane(self.language_lane).value,
            b"det": 1 if self.deterministic else 0,
            b"side_effect_free": 1 if self.side_effect_free else 0,
            b"heap": 1 if self.owns_heap_across_boundary else 0,
            b"untrusted": 1 if self.consumes_untrusted_bytes else 0,
            b"py_ref": 1 if self.has_python_reference else 0,
            b"golden": 1 if self.has_golden_vectors else 0,
            b"fuzz": 1 if self.has_fuzz_harness else 0,
            b"asan": 1 if self.has_sanitizer_profile else 0,
            b"fallback": 1 if self.portable_fallback else 0,
            b"abi": 1 if self.stable_abi else 0,
            b"reason": self.reason,
        }))


@dataclass(frozen=True)
class NativeBoundaryDecision:
    decision_kind: NativeBoundaryDecisionKind
    accepted: bool
    watch: bool
    native_allowed: bool
    python_required: bool
    rationale: str
    obligations: tuple[str, ...]
    candidate_digest: bytes

    @property
    def report_digest(self) -> bytes:
        return sha256(NATIVE_BOUNDARY_DOMAIN + b":decision:" + bencode({
            b"decision": NativeBoundaryDecisionKind(self.decision_kind).value,
            b"accepted": 1 if self.accepted else 0,
            b"watch": 1 if self.watch else 0,
            b"native_allowed": 1 if self.native_allowed else 0,
            b"python_required": 1 if self.python_required else 0,
            b"rationale": self.rationale,
            b"obligations": list(self.obligations),
            b"candidate": self.candidate_digest,
        }))


def assess_native_candidate(candidate: NativeCandidate) -> NativeBoundaryDecision:
    kind = ComponentKind(candidate.component_kind)
    lane = LanguageLane(candidate.language_lane)

    if kind is ComponentKind.CRYPTO_IMPLEMENTATION and lane is LanguageLane.GCC_C_LEAF:
        return NativeBoundaryDecision(
            NativeBoundaryDecisionKind.QUARANTINE_HAND_ROLLED_CRYPTO,
            accepted=False,
            watch=False,
            native_allowed=False,
            python_required=True,
            rationale="do not hand-roll cryptography in a GCC C leaf; bind a vetted library instead",
            obligations=("vetted-library-binding", "test-vectors", "constant-time-review"),
            candidate_digest=candidate.candidate_digest,
        )

    if kind in {ComponentKind.PROTOCOL_STATE, ComponentKind.MUTABLE_HEAD_ACCEPTANCE, ComponentKind.POLICY_GOVERNANCE, ComponentKind.I2P_TRANSPORT_CONTROL}:
        return NativeBoundaryDecision(
            NativeBoundaryDecisionKind.KEEP_PYTHON,
            accepted=True,
            watch=False,
            native_allowed=False,
            python_required=True,
            rationale="semantics are still moving and need transparent audit/refactor speed",
            obligations=("python-orchestrates", "native-cannot-decide-truth", "boundary-tests-before-ffi"),
            candidate_digest=candidate.candidate_digest,
        )

    if kind is ComponentKind.UNTRUSTED_BYTE_PARSER:
        if candidate.has_fuzz_harness and candidate.has_sanitizer_profile and candidate.has_python_reference and candidate.portable_fallback and candidate.stable_abi:
            return NativeBoundaryDecision(
                NativeBoundaryDecisionKind.HOLD_UNTIL_FUZZ_AND_SANITIZERS,
                accepted=False,
                watch=True,
                native_allowed=False,
                python_required=True,
                rationale="native parser remains a high-risk option even with harnesses; prefer parser wall stability first",
                obligations=("differential-fuzz", "asan-ubsan-ci", "memory-safe-native-option-review"),
                candidate_digest=candidate.candidate_digest,
            )
        return NativeBoundaryDecision(
            NativeBoundaryDecisionKind.REJECT_NATIVE_FOR_NOW,
            accepted=False,
            watch=True,
            native_allowed=False,
            python_required=True,
            rationale="untrusted byte parsing in C is not the first GCC boundary to trust",
            obligations=("keep-parseguard-python", "fuzz-before-native", "no-network-bytes-to-c-leaf"),
            candidate_digest=candidate.candidate_digest,
        )

    if lane is LanguageLane.VETTED_NATIVE_LIBRARY:
        return NativeBoundaryDecision(
            NativeBoundaryDecisionKind.USE_VETTED_NATIVE_LIBRARY,
            accepted=True,
            watch=True,
            native_allowed=True,
            python_required=True,
            rationale="native dependency may be useful when it is a vetted library and Python retains policy semantics",
            obligations=("pin-abi", "golden-vectors", "portable-fallback-or-clear-packaging-failure"),
            candidate_digest=candidate.candidate_digest,
        )

    leaf_ready = all((
        lane is LanguageLane.GCC_C_LEAF,
        candidate.deterministic,
        candidate.side_effect_free,
        not candidate.owns_heap_across_boundary,
        not candidate.consumes_untrusted_bytes,
        candidate.has_python_reference,
        candidate.has_golden_vectors,
        candidate.portable_fallback,
        candidate.stable_abi,
    ))
    if leaf_ready and kind in {ComponentKind.XOR_DISTANCE_HOTPATH, ComponentKind.RANGE_SKETCH_KERNEL, ComponentKind.SET_RECONCILIATION_KERNEL, ComponentKind.BULK_HASH_PIPELINE}:
        obligations = ("python-reference-must-remain", "ctypes-cffi-abi-test", "golden-vectors", "no-cross-boundary-allocation")
        if not candidate.has_fuzz_harness or not candidate.has_sanitizer_profile:
            obligations += ("add-fuzz-and-sanitizer-before-production",)
        return NativeBoundaryDecision(
            NativeBoundaryDecisionKind.ACCEPT_GCC_LEAF_KERNEL,
            accepted=True,
            watch=not (candidate.has_fuzz_harness and candidate.has_sanitizer_profile),
            native_allowed=True,
            python_required=True,
            rationale="small pure hotpath can be native while Python keeps routing/protocol decisions",
            obligations=obligations,
            candidate_digest=candidate.candidate_digest,
        )

    return NativeBoundaryDecision(
        NativeBoundaryDecisionKind.REJECT_NATIVE_FOR_NOW,
        accepted=False,
        watch=True,
        native_allowed=False,
        python_required=True,
        rationale="candidate fails the narrow native-leaf boundary",
        obligations=("keep-python", "write-reference-tests", "tighten-boundary-before-ffi"),
        candidate_digest=candidate.candidate_digest,
    )


def default_language_matrix() -> tuple[NativeCandidate, ...]:
    """Return the rev0081 default answer to the GCC question."""
    return (
        NativeCandidate(ComponentKind.PROTOCOL_STATE, LanguageLane.PYTHON_FIRST, True, False, False, False, True, True, False, False, True, False, "mutable DHT semantics still moving"),
        NativeCandidate(ComponentKind.I2P_TRANSPORT_CONTROL, LanguageLane.PYTHON_FIRST, True, False, False, True, True, True, False, False, True, False, "SAM/router orchestration should stay inspectable"),
        NativeCandidate(ComponentKind.UNTRUSTED_BYTE_PARSER, LanguageLane.GCC_C_LEAF, True, True, False, True, True, True, False, False, True, True, "parser is an attack surface"),
        NativeCandidate(ComponentKind.CRYPTO_IMPLEMENTATION, LanguageLane.GCC_C_LEAF, True, True, False, True, False, False, False, False, False, False, "hand-rolled crypto is a trap"),
        NativeCandidate(ComponentKind.XOR_DISTANCE_HOTPATH, LanguageLane.GCC_C_LEAF, True, True, False, False, True, True, False, False, True, True, "routing sort/comparison hotpath"),
        NativeCandidate(ComponentKind.SET_RECONCILIATION_KERNEL, LanguageLane.GCC_C_LEAF, True, True, False, False, True, True, True, True, True, True, "future Minisketch/IBLT-style adapter seam"),
    )


def summarize_language_plan(candidates: tuple[NativeCandidate, ...] | None = None) -> dict[str, str]:
    """Compact human-readable answer: component kind -> decision kind."""
    chosen = candidates or default_language_matrix()
    return {candidate.component_kind.value: assess_native_candidate(candidate).decision_kind.value for candidate in chosen}
