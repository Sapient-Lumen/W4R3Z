"""rev0085 differential native corpus boundary.

Parity vectors are not one-time trophies.  This lane treats a deterministic
corpus as persistent local evidence tying native provenance to Python oracle
agreement before native dispatch may stay enabled.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable, Iterable

from .bencode import bencode
from .ids import DOMAIN, sha256
from .nativehotpaths import xor_compare_reference
from .nativeprovenance import NativeProvenanceReport

NATIVE_CORPUS_DOMAIN = DOMAIN + b":native-corpus-v1:"
XorCompareCallable = Callable[[bytes, bytes, bytes], int]


class NativeCorpusDecisionKind(str, Enum):
    ACCEPT_DIFFERENTIAL_CORPUS = "accept_differential_corpus"
    ACCEPT_FALLBACK_CORPUS = "accept_fallback_corpus"
    HOLD_INSUFFICIENT_CORPUS = "hold_insufficient_corpus"
    HOLD_NATIVE_CALLABLE_MISSING = "hold_native_callable_missing"
    QUARANTINE_PROVENANCE_NOT_ACCEPTED = "quarantine_provenance_not_accepted"
    QUARANTINE_NATIVE_MISMATCH = "quarantine_native_mismatch"
    QUARANTINE_NATIVE_EXCEPTION = "quarantine_native_exception"
    QUARANTINE_UNBOUNDED_INPUT = "quarantine_unbounded_input"
    QUARANTINE_LOW_DIVERSITY = "quarantine_low_diversity"


@dataclass(frozen=True)
class NativeCorpusVector:
    pivot: bytes
    left: bytes
    right: bytes
    label: str
    bucket: str

    @property
    def vector_digest(self) -> bytes:
        return sha256(NATIVE_CORPUS_DOMAIN + b":vector:" + bencode({
            b"pivot": self.pivot,
            b"left": self.left,
            b"right": self.right,
            b"label": self.label,
            b"bucket": self.bucket,
        }))


@dataclass(frozen=True)
class NativeCorpusObservation:
    label: str
    vector_digest: bytes
    python_result: int
    native_result: int | None
    mismatch: bool
    exception: str = ""

    def bvalue(self) -> dict[bytes, object]:
        return {
            b"label": self.label,
            b"vector": self.vector_digest,
            b"python": self.python_result,
            b"native": self.native_result if self.native_result is not None else 99,
            b"mismatch": 1 if self.mismatch else 0,
            b"exception": self.exception,
        }


@dataclass(frozen=True)
class NativeCorpusReport:
    decision_kind: NativeCorpusDecisionKind
    accepted: bool
    native_allowed: bool
    fallback_allowed: bool
    watch: bool
    quarantine: bool
    provenance_digest: bytes
    corpus_digest: bytes
    observations: tuple[NativeCorpusObservation, ...]
    vector_count: int
    bucket_count: int
    obligations: tuple[str, ...]

    @property
    def report_digest(self) -> bytes:
        return sha256(NATIVE_CORPUS_DOMAIN + b":report:" + bencode({
            b"decision": NativeCorpusDecisionKind(self.decision_kind).value,
            b"accepted": 1 if self.accepted else 0,
            b"native_allowed": 1 if self.native_allowed else 0,
            b"fallback_allowed": 1 if self.fallback_allowed else 0,
            b"watch": 1 if self.watch else 0,
            b"quarantine": 1 if self.quarantine else 0,
            b"provenance": self.provenance_digest,
            b"corpus": self.corpus_digest,
            b"observations": [obs.bvalue() for obs in self.observations],
            b"vectors": self.vector_count,
            b"buckets": self.bucket_count,
            b"obligations": list(self.obligations),
        }))


def default_native_corpus_vectors() -> tuple[NativeCorpusVector, ...]:
    base = [
        NativeCorpusVector(b"\x00" * 32, b"\x00" * 32, b"\xff" * 32, "zero_vs_far", "edge-zero"),
        NativeCorpusVector(b"\xff" * 32, b"\x00" * 32, b"\xff" * 32, "far_vs_self", "edge-ff"),
        NativeCorpusVector(b"\x55" * 32, b"\xaa" * 32, b"\xaa" * 32, "tie_equal", "tie"),
        NativeCorpusVector(bytes(range(32)), bytes(reversed(range(32))), bytes(range(32)), "reverse_vs_self", "gradient"),
        NativeCorpusVector(b"\x00" * 31 + b"\x80", b"\x00" * 31 + b"\x7f", b"\x00" * 31 + b"\x81", "last_byte_edge", "late-byte"),
        NativeCorpusVector(b"native-corpus-pivot-0000000000"[:32].ljust(32, b"!"), b"left".ljust(32, b"L"), b"right".ljust(32, b"R"), "ascii_pad", "text"),
    ]
    return tuple(base)


def assess_native_corpus(
    provenance: NativeProvenanceReport,
    vectors: Iterable[NativeCorpusVector] | None = None,
    *,
    native_compare: XorCompareCallable | None = None,
    require_native: bool = True,
    max_input_len: int = 32,
    min_vectors: int = 6,
    min_buckets: int = 5,
) -> NativeCorpusReport:
    chosen = tuple(vectors or default_native_corpus_vectors())
    corpus_digest = sha256(NATIVE_CORPUS_DOMAIN + b":corpus:" + bencode([v.vector_digest for v in chosen]))
    buckets = {v.bucket for v in chosen}

    def report(kind: NativeCorpusDecisionKind, accepted: bool, native_allowed: bool, fallback_allowed: bool, watch: bool, quarantine: bool, observations: tuple[NativeCorpusObservation, ...], obligations: tuple[str, ...]) -> NativeCorpusReport:
        return NativeCorpusReport(kind, accepted, native_allowed, fallback_allowed, watch, quarantine, provenance.report_digest, corpus_digest, observations, len(chosen), len(buckets), obligations)

    if not provenance.accepted or not provenance.native_artifact_allowed:
        return report(NativeCorpusDecisionKind.QUARANTINE_PROVENANCE_NOT_ACCEPTED, False, False, True, False, True, tuple(), ("native-provenance-must-accept-first", "use-python-fallback"))
    if len(chosen) < min_vectors:
        return report(NativeCorpusDecisionKind.HOLD_INSUFFICIENT_CORPUS, False, False, True, True, False, tuple(), ("add-differential-corpus-vectors", "keep-native-disabled"))
    if len(buckets) < min_buckets:
        return report(NativeCorpusDecisionKind.QUARANTINE_LOW_DIVERSITY, False, False, True, False, True, tuple(), ("add-diverse-corpus-buckets", "do-not-select-native"))
    if any(len(v.pivot) != len(v.left) or len(v.left) != len(v.right) or len(v.pivot) == 0 or len(v.pivot) > max_input_len for v in chosen):
        return report(NativeCorpusDecisionKind.QUARANTINE_UNBOUNDED_INPUT, False, False, True, False, True, tuple(), ("corpus-vector-violates-input-bound", "do-not-call-native"))
    if native_compare is None:
        kind = NativeCorpusDecisionKind.HOLD_NATIVE_CALLABLE_MISSING if require_native else NativeCorpusDecisionKind.ACCEPT_FALLBACK_CORPUS
        return report(kind, not require_native, False, True, require_native, False, tuple(), ("native-callable-missing", "python-corpus-result-observed"))

    observations: list[NativeCorpusObservation] = []
    for vector in chosen:
        py = xor_compare_reference(vector.pivot, vector.left, vector.right)
        try:
            native = int(native_compare(vector.pivot, vector.left, vector.right))
        except Exception as exc:  # pragma: no cover - tested with a deliberate callable
            observations.append(NativeCorpusObservation(vector.label, vector.vector_digest, py, None, True, type(exc).__name__))
            return report(NativeCorpusDecisionKind.QUARANTINE_NATIVE_EXCEPTION, False, False, True, False, True, tuple(observations), ("native-corpus-exception", "quarantine-native-artifact"))
        mismatch = native != py
        observations.append(NativeCorpusObservation(vector.label, vector.vector_digest, py, native, mismatch))
        if mismatch:
            return report(NativeCorpusDecisionKind.QUARANTINE_NATIVE_MISMATCH, False, False, True, False, True, tuple(observations), ("native-corpus-mismatch", "quarantine-native-artifact", "use-python-oracle"))
    return report(NativeCorpusDecisionKind.ACCEPT_DIFFERENTIAL_CORPUS, True, True, True, False, False, tuple(observations), ("record-differential-corpus", "native-still-exact-boundary", "python-oracle-retained"))
