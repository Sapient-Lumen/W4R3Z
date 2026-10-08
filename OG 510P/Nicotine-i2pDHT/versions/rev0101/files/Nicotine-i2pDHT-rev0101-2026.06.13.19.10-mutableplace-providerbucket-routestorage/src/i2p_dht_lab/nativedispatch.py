"""rev0083 exact-boundary dispatch seal for optional native leaf calls."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable

from .bencode import bencode
from .ids import DOMAIN, sha256
from .nativehotpaths import xor_compare_reference
from .nativeruntime import NativeRuntimeDecisionKind, NativeRuntimeReport

NATIVE_DISPATCH_DOMAIN = DOMAIN + b":native-dispatch-v1:"

XorCompareCallable = Callable[[bytes, bytes, bytes], int]


class NativeDispatchDecisionKind(str, Enum):
    ACCEPT_NATIVE_DISPATCH = "accept_native_dispatch"
    ACCEPT_PYTHON_FALLBACK_DISPATCH = "accept_python_fallback_dispatch"
    HOLD_NATIVE_CALLABLE_MISSING = "hold_native_callable_missing"
    QUARANTINE_RUNTIME_NOT_ACCEPTED = "quarantine_runtime_not_accepted"
    QUARANTINE_OPERATION_MISMATCH = "quarantine_operation_mismatch"
    QUARANTINE_INPUT_LIMIT = "quarantine_input_limit"
    QUARANTINE_NATIVE_RESULT_MISMATCH = "quarantine_native_result_mismatch"
    QUARANTINE_REQUEST_REPLAY = "quarantine_request_replay"


@dataclass(frozen=True)
class NativeCallRequest:
    component: str
    operation: str
    request_id: str
    pivot: bytes
    left: bytes
    right: bytes
    max_input_len: int
    allow_native: bool = True

    @property
    def request_digest(self) -> bytes:
        return sha256(NATIVE_DISPATCH_DOMAIN + b":request:" + bencode({
            b"component": self.component,
            b"operation": self.operation,
            b"request": self.request_id,
            b"pivot": self.pivot,
            b"left": self.left,
            b"right": self.right,
            b"max": self.max_input_len,
            b"allow_native": 1 if self.allow_native else 0,
        }))


@dataclass(frozen=True)
class NativeDispatchReport:
    decision_kind: NativeDispatchDecisionKind
    accepted: bool
    native_used: bool
    fallback_used: bool
    watch: bool
    result: int | None
    python_result: int | None
    native_result: int | None
    obligations: tuple[str, ...]
    request_digest: bytes
    runtime_digest: bytes
    prior_request_digests: tuple[bytes, ...] = ()

    @property
    def report_digest(self) -> bytes:
        return sha256(NATIVE_DISPATCH_DOMAIN + b":report:" + bencode({
            b"decision": NativeDispatchDecisionKind(self.decision_kind).value,
            b"accepted": 1 if self.accepted else 0,
            b"native_used": 1 if self.native_used else 0,
            b"fallback_used": 1 if self.fallback_used else 0,
            b"watch": 1 if self.watch else 0,
            b"result": self.result if self.result is not None else 99,
            b"python_result": self.python_result if self.python_result is not None else 99,
            b"native_result": self.native_result if self.native_result is not None else 99,
            b"obligations": list(self.obligations),
            b"request": self.request_digest,
            b"runtime": self.runtime_digest,
            b"prior_requests": list(self.prior_request_digests),
        }))


def seal_xor_dispatch(
    runtime: NativeRuntimeReport,
    request: NativeCallRequest,
    *,
    native_compare: XorCompareCallable | None = None,
    prior_request_digests: tuple[bytes, ...] = (),
) -> NativeDispatchReport:
    req_digest = request.request_digest

    def report(kind: NativeDispatchDecisionKind, accepted: bool, native_used: bool, fallback_used: bool, watch: bool, result: int | None, py: int | None, native: int | None, obligations: tuple[str, ...]) -> NativeDispatchReport:
        return NativeDispatchReport(kind, accepted, native_used, fallback_used, watch, result, py, native, obligations, req_digest, runtime.report_digest, prior_request_digests)

    if req_digest in prior_request_digests:
        return report(NativeDispatchDecisionKind.QUARANTINE_REQUEST_REPLAY, False, False, False, False, None, None, None, ("preserve-replay-evidence", "do-not-dispatch"))

    if not runtime.accepted:
        return report(NativeDispatchDecisionKind.QUARANTINE_RUNTIME_NOT_ACCEPTED, False, False, False, False, None, None, None, ("runtime-not-accepted", "re-evaluate-runtime-or-use-explicit-fallback"))

    if request.component != "xor_distance" or request.operation != "xor_compare":
        return report(NativeDispatchDecisionKind.QUARANTINE_OPERATION_MISMATCH, False, False, False, False, None, None, None, ("operation-not-in-native-leaf-contract",))

    if not (len(request.pivot) == len(request.left) == len(request.right)) or len(request.pivot) == 0 or len(request.pivot) > request.max_input_len:
        return report(NativeDispatchDecisionKind.QUARANTINE_INPUT_LIMIT, False, False, False, False, None, None, None, ("bounded-input-contract-failed",))

    py_result = xor_compare_reference(request.pivot, request.left, request.right)

    if runtime.native_runtime_allowed and request.allow_native:
        if native_compare is None:
            return report(NativeDispatchDecisionKind.HOLD_NATIVE_CALLABLE_MISSING, False, False, True, True, py_result, py_result, None, ("native-runtime-selected-but-callable-missing", "python-fallback-result-observed"))
        native_result = int(native_compare(request.pivot, request.left, request.right))
        if native_result != py_result:
            return report(NativeDispatchDecisionKind.QUARANTINE_NATIVE_RESULT_MISMATCH, False, False, True, False, py_result, py_result, native_result, ("native-call-result-drift", "quarantine-native-runtime", "use-python-result"))
        return report(NativeDispatchDecisionKind.ACCEPT_NATIVE_DISPATCH, True, True, True, False, native_result, py_result, native_result, ("record-native-dispatch", "python-oracle-agreed"))

    if runtime.fallback_runtime_allowed:
        return report(NativeDispatchDecisionKind.ACCEPT_PYTHON_FALLBACK_DISPATCH, True, False, True, runtime.watch, py_result, py_result, None, ("record-python-fallback-dispatch", "native-not-used"))

    return report(NativeDispatchDecisionKind.QUARANTINE_RUNTIME_NOT_ACCEPTED, False, False, False, False, None, py_result, None, ("no-runtime-dispatch-path",))
