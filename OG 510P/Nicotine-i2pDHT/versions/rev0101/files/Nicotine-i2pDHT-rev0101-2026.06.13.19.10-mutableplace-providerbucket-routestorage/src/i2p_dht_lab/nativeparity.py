"""rev0082 native/Python parity guard for optional GCC leaf kernels.

A native hotpath may be fast, but it is never truth.  This module keeps the
Python reference as the semantic oracle and turns native results into typed
local evidence: accept native parity, use Python fallback, hold for missing
coverage, or quarantine mismatches/exceptions.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable, Iterable

from .bencode import bencode
from .ids import DOMAIN, sha256
from .nativehotpaths import xor_compare_reference

NATIVE_PARITY_DOMAIN = DOMAIN + b":native-parity-v1:"

XorCompareCallable = Callable[[bytes, bytes, bytes], int]


class NativeParityDecisionKind(str, Enum):
    ACCEPT_NATIVE_PARITY = "accept_native_parity"
    USE_PYTHON_FALLBACK_NATIVE_MISSING = "use_python_fallback_native_missing"
    HOLD_INSUFFICIENT_VECTORS = "hold_insufficient_vectors"
    HOLD_LOW_VECTOR_DIVERSITY = "hold_low_vector_diversity"
    QUARANTINE_NATIVE_MISMATCH = "quarantine_native_mismatch"
    QUARANTINE_NATIVE_EXCEPTION = "quarantine_native_exception"
    QUARANTINE_REQUIRE_NATIVE_MISSING = "quarantine_require_native_missing"


@dataclass(frozen=True)
class XorParityVector:
    pivot: bytes
    left: bytes
    right: bytes
    label: str = ""

    def __post_init__(self) -> None:
        if not (len(self.pivot) == len(self.left) == len(self.right)):
            raise ValueError("pivot/left/right must have the same length")
        if len(self.pivot) == 0:
            raise ValueError("parity vector length must be positive")

    @property
    def expected(self) -> int:
        return xor_compare_reference(self.pivot, self.left, self.right)

    @property
    def vector_digest(self) -> bytes:
        return sha256(NATIVE_PARITY_DOMAIN + b":vector:" + bencode({
            b"pivot": self.pivot,
            b"left": self.left,
            b"right": self.right,
            b"label": self.label,
        }))

    @property
    def diversity_bucket(self) -> int:
        # A cheap deterministic coverage bucket.  This is not statistical proof;
        # it merely prevents a parity report from using N copies of one shape.
        return self.vector_digest[0] >> 4


@dataclass(frozen=True)
class NativeParityObservation:
    vector_digest: bytes
    expected: int
    observed: int | None
    ok: bool
    error: str = ""

    def bvalue(self) -> dict[bytes, object]:
        return {
            b"vector": self.vector_digest,
            b"expected": self.expected,
            b"observed": self.observed if self.observed is not None else b"none",
            b"ok": 1 if self.ok else 0,
            b"error": self.error,
        }


@dataclass(frozen=True)
class NativeParityReport:
    decision_kind: NativeParityDecisionKind
    accepted: bool
    native_allowed: bool
    fallback_allowed: bool
    watch: bool
    vector_count: int
    diversity_count: int
    observations: tuple[NativeParityObservation, ...]
    obligations: tuple[str, ...]

    @property
    def mismatch_count(self) -> int:
        return sum(1 for observation in self.observations if observation.observed is not None and not observation.ok)

    @property
    def exception_count(self) -> int:
        return sum(1 for observation in self.observations if observation.observed is None and observation.error)

    @property
    def report_digest(self) -> bytes:
        return sha256(NATIVE_PARITY_DOMAIN + b":report:" + bencode({
            b"decision": NativeParityDecisionKind(self.decision_kind).value,
            b"accepted": 1 if self.accepted else 0,
            b"native_allowed": 1 if self.native_allowed else 0,
            b"fallback_allowed": 1 if self.fallback_allowed else 0,
            b"watch": 1 if self.watch else 0,
            b"vector_count": self.vector_count,
            b"diversity_count": self.diversity_count,
            b"mismatch_count": self.mismatch_count,
            b"exception_count": self.exception_count,
            b"observations": [obs.bvalue() for obs in self.observations],
            b"obligations": list(self.obligations),
        }))


def default_xor_parity_vectors() -> tuple[XorParityVector, ...]:
    """Return deterministic coverage for the XOR comparator leaf.

    The cases intentionally include left wins, right wins, equality, early-byte
    differences, late-byte differences, and all-zero/all-ff edges.
    """
    vectors: list[XorParityVector] = [
        XorParityVector(b"\x00" * 32, b"\x00" * 32, b"\x01" + b"\x00" * 31, "left_zero_wins"),
        XorParityVector(b"\x00" * 32, b"\xff" * 32, b"\x7f" + b"\xff" * 31, "right_highbit_wins"),
        XorParityVector(b"\x55" * 32, b"\xaa" * 32, b"\xaa" * 32, "equal_distance"),
        XorParityVector(bytes(range(32)), bytes(reversed(range(32))), bytes(range(31, -1, -1)), "same_candidate_bytes"),
        XorParityVector(b"\xff" * 32, b"\x00" * 31 + b"\x01", b"\x00" * 31 + b"\x02", "late_byte_diff"),
    ]
    for i in range(19):
        pivot = bytes(((j * 17 + i * 11) % 256) for j in range(32))
        left = bytes(((j * 29 + i * 3 + 5) % 256) for j in range(32))
        right = bytes(((j * 31 + i * 7 + 13) % 256) for j in range(32))
        vectors.append(XorParityVector(pivot, left, right, f"generated_{i:02d}"))
    return tuple(vectors)


def evaluate_xor_native_parity(
    vectors: Iterable[XorParityVector] | None = None,
    native_compare: XorCompareCallable | None = None,
    *,
    require_native: bool = False,
    min_vectors: int = 8,
    min_diversity_buckets: int = 4,
) -> NativeParityReport:
    chosen = tuple(vectors or default_xor_parity_vectors())
    diversity_count = len({vector.diversity_bucket for vector in chosen})
    if len(chosen) < min_vectors:
        return NativeParityReport(
            NativeParityDecisionKind.HOLD_INSUFFICIENT_VECTORS,
            accepted=False,
            native_allowed=False,
            fallback_allowed=True,
            watch=True,
            vector_count=len(chosen),
            diversity_count=diversity_count,
            observations=tuple(),
            obligations=("add-golden-vectors", "keep-python-fallback"),
        )
    if diversity_count < min_diversity_buckets:
        return NativeParityReport(
            NativeParityDecisionKind.HOLD_LOW_VECTOR_DIVERSITY,
            accepted=False,
            native_allowed=False,
            fallback_allowed=True,
            watch=True,
            vector_count=len(chosen),
            diversity_count=diversity_count,
            observations=tuple(),
            obligations=("add-diverse-vectors", "no-native-fastpath-yet"),
        )
    if native_compare is None:
        if require_native:
            return NativeParityReport(
                NativeParityDecisionKind.QUARANTINE_REQUIRE_NATIVE_MISSING,
                accepted=False,
                native_allowed=False,
                fallback_allowed=False,
                watch=False,
                vector_count=len(chosen),
                diversity_count=diversity_count,
                observations=tuple(),
                obligations=("do-not-launch-native-required-profile", "compile-or-disable-native-requirement"),
            )
        return NativeParityReport(
            NativeParityDecisionKind.USE_PYTHON_FALLBACK_NATIVE_MISSING,
            accepted=True,
            native_allowed=False,
            fallback_allowed=True,
            watch=True,
            vector_count=len(chosen),
            diversity_count=diversity_count,
            observations=tuple(),
            obligations=("record-fallback", "do-not-treat-missing-native-as-failure"),
        )

    observations: list[NativeParityObservation] = []
    for vector in chosen:
        expected = vector.expected
        try:
            observed = int(native_compare(vector.pivot, vector.left, vector.right))
        except Exception as exc:  # pragma: no cover - test triggers intentionally
            observations.append(NativeParityObservation(vector.vector_digest, expected, None, False, f"{type(exc).__name__}: {exc}"))
            continue
        observations.append(NativeParityObservation(vector.vector_digest, expected, observed, observed == expected))

    if any(obs.observed is None for obs in observations):
        return NativeParityReport(
            NativeParityDecisionKind.QUARANTINE_NATIVE_EXCEPTION,
            accepted=False,
            native_allowed=False,
            fallback_allowed=True,
            watch=False,
            vector_count=len(chosen),
            diversity_count=diversity_count,
            observations=tuple(observations),
            obligations=("quarantine-native-library", "use-python-fallback", "preserve-exception-observations"),
        )
    if any(not obs.ok for obs in observations):
        return NativeParityReport(
            NativeParityDecisionKind.QUARANTINE_NATIVE_MISMATCH,
            accepted=False,
            native_allowed=False,
            fallback_allowed=True,
            watch=False,
            vector_count=len(chosen),
            diversity_count=diversity_count,
            observations=tuple(observations),
            obligations=("quarantine-native-library", "use-python-fallback", "preserve-mismatch-vectors"),
        )
    return NativeParityReport(
        NativeParityDecisionKind.ACCEPT_NATIVE_PARITY,
        accepted=True,
        native_allowed=True,
        fallback_allowed=True,
        watch=False,
        vector_count=len(chosen),
        diversity_count=diversity_count,
        observations=tuple(observations),
        obligations=("keep-python-reference", "rerun-parity-after-rebuild", "record-native-artifact-digest"),
    )
