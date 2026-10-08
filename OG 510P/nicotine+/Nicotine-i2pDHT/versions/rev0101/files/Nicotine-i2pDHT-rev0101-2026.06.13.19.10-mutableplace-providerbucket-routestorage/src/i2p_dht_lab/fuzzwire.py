"""Deterministic malformed-input pressure before live transport.

Fuzzing here is intentionally tiny and reproducible.  It does not replace real
fuzzing.  It pins classes of mistakes that a live SAM/I2P transport would make
harder to diagnose: non-canonical bencode, payload digest tampering, TTL
expiry, report-kind mismatch, and parser/resource-limit failures.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .ids import DOMAIN, sha256
from .identity import DhtKeypair
from .parseguard import ParseGuardError, ParseGuardKind, ParseLimits, bdecode_guarded
from .transportshadow import ShadowPayloadKind, ShadowValidationKind, create_shadow_frame, validate_shadow_frame
from .wirecanon import WireFrame, WireMessageKind, validate_wire_frame

FUZZ_WIRE_DOMAIN = DOMAIN + b":fuzz-wire-v1:"


class FuzzSurfaceKind(str, Enum):
    PARSE_GUARD = "parse_guard"
    WIRE_FRAME = "wire_frame"
    SHADOW_FRAME = "shadow_frame"


class FuzzExpectation(str, Enum):
    ACCEPT = "accept"
    REJECT = "reject"


@dataclass(frozen=True)
class FuzzCase:
    label: str
    surface: FuzzSurfaceKind
    payload: bytes
    expectation: FuzzExpectation
    expected_reason: str
    frame: WireFrame | None = None
    now: int = 0
    expected_report_digest: bytes | None = None

    def __post_init__(self) -> None:
        if not self.label or not self.expected_reason:
            raise ValueError("fuzz case needs label and reason")
        if self.surface in {FuzzSurfaceKind.WIRE_FRAME, FuzzSurfaceKind.SHADOW_FRAME} and self.frame is None:
            raise ValueError("wire/shadow fuzz cases require a frame")

    @property
    def case_digest(self) -> bytes:
        return sha256(FUZZ_WIRE_DOMAIN + b":case:" + bencode({
            b"label": self.label,
            b"surface": self.surface.value,
            b"payload": self.payload,
            b"expectation": self.expectation.value,
            b"frame": b"" if self.frame is None else self.frame.frame_digest,
        }))


@dataclass(frozen=True)
class FuzzCaseResult:
    case_digest: bytes
    label: str
    passed: bool
    observed_accept: bool
    observed_reason: str


@dataclass(frozen=True)
class FuzzRunReport:
    results: tuple[FuzzCaseResult, ...]
    accepted_cases: int
    rejected_cases: int
    failed_cases: int
    report_digest: bytes

    @property
    def passed(self) -> bool:
        return self.failed_cases == 0


def deterministic_fuzz_cases(*, keypair: DhtKeypair, node_id: bytes, now: int) -> tuple[FuzzCase, ...]:
    good_parse = bencode({b"a": 1, b"b": b"ok"})
    request_id = sha256(FUZZ_WIRE_DOMAIN + b":request")
    wire_payload = b"wire-payload"
    good_frame = WireFrame.create(keypair=keypair, sender_node_id=node_id, message_kind=WireMessageKind.FIND_NODE, request_id=request_id, payload=wire_payload, issued_at=now, ttl=120)
    expired_frame = WireFrame.create(keypair=keypair, sender_node_id=node_id, message_kind=WireMessageKind.FIND_NODE, request_id=sha256(b"expired"), payload=wire_payload, issued_at=now - 500, ttl=120)
    report_digest = sha256(b"fuzz-shadow-report")
    shadow = create_shadow_frame(keypair=keypair, sender_node_id=node_id, request_id=sha256(b"shadow-request"), payload_kind=ShadowPayloadKind.JOINED_SCHEDULE_REPORT, report_digest=report_digest, subject_digest=sha256(b"shadow-subject"), note="joined schedule report", issued_at=now, ttl=120)
    shadow_frame = shadow.frame
    shadow_payload = shadow.payload
    wrong_kind_shadow = replace(shadow_frame, message_kind=WireMessageKind.FIND_NODE)
    # Signature intentionally remains from the original frame so validation should
    # fail at signature or role/kind; either is useful shadow-boundary pressure.
    return (
        FuzzCase("canonical-dict", FuzzSurfaceKind.PARSE_GUARD, good_parse, FuzzExpectation.ACCEPT, "accept canonical parse"),
        FuzzCase("leading-zero-int", FuzzSurfaceKind.PARSE_GUARD, b"i03e", FuzzExpectation.REJECT, ParseGuardKind.REJECT_INVALID_INTEGER.value),
        FuzzCase("unsorted-dict", FuzzSurfaceKind.PARSE_GUARD, b"d1:b1:21:a1:1e", FuzzExpectation.REJECT, ParseGuardKind.REJECT_UNSORTED_KEY.value),
        FuzzCase("oversize-input", FuzzSurfaceKind.PARSE_GUARD, b"9:abcdefghi", FuzzExpectation.REJECT, ParseGuardKind.REJECT_TOO_LARGE.value),
        FuzzCase("wire-good", FuzzSurfaceKind.WIRE_FRAME, wire_payload, FuzzExpectation.ACCEPT, "accept wire", frame=good_frame, now=now + 1),
        FuzzCase("wire-payload-tamper", FuzzSurfaceKind.WIRE_FRAME, b"wire-tampered", FuzzExpectation.REJECT, "payload", frame=good_frame, now=now + 1),
        FuzzCase("wire-expired", FuzzSurfaceKind.WIRE_FRAME, wire_payload, FuzzExpectation.REJECT, "window", frame=expired_frame, now=now + 1),
        FuzzCase("shadow-good", FuzzSurfaceKind.SHADOW_FRAME, shadow_payload.to_bytes(), FuzzExpectation.ACCEPT, "accept shadow", frame=shadow_frame, now=now + 1, expected_report_digest=report_digest),
        FuzzCase("shadow-report-digest-mismatch", FuzzSurfaceKind.SHADOW_FRAME, shadow_payload.to_bytes(), FuzzExpectation.REJECT, "digest", frame=shadow_frame, now=now + 1, expected_report_digest=sha256(b"different")),
        FuzzCase("shadow-kind-mismatch", FuzzSurfaceKind.SHADOW_FRAME, shadow_payload.to_bytes(), FuzzExpectation.REJECT, "signature", frame=wrong_kind_shadow, now=now + 1, expected_report_digest=report_digest),
    )


def _run_case(case: FuzzCase) -> FuzzCaseResult:
    try:
        if case.surface is FuzzSurfaceKind.PARSE_GUARD:
            limits = ParseLimits(max_bytes=8) if case.label == "oversize-input" else ParseLimits()
            bdecode_guarded(case.payload, limits=limits)
            accept = True
            reason = "accept canonical parse"
        elif case.surface is FuzzSurfaceKind.WIRE_FRAME:
            assert case.frame is not None
            validation = validate_wire_frame(case.frame, payload=case.payload, now=case.now)
            accept = validation.accept
            reason = validation.reason.lower()
        else:
            assert case.frame is not None
            report = validate_shadow_frame(case.frame, payload_bytes=case.payload, now=case.now, expected_report_digest=case.expected_report_digest)
            accept = report.validation.accept
            reason = report.validation.reason.lower()
    except ParseGuardError as exc:
        accept = False
        reason = exc.kind.value
    except Exception as exc:  # pragma: no cover - defensive fuzz harness
        accept = False
        reason = type(exc).__name__.lower()
    expected_accept = case.expectation is FuzzExpectation.ACCEPT
    passed = accept is expected_accept and (case.expected_reason.lower() in reason or expected_accept)
    return FuzzCaseResult(case.case_digest, case.label, passed, accept, reason)


def run_fuzz_wire_cases(cases: Iterable[FuzzCase]) -> FuzzRunReport:
    results = tuple(_run_case(case) for case in cases)
    accepted = sum(1 for result in results if result.observed_accept)
    rejected = len(results) - accepted
    failed = sum(1 for result in results if not result.passed)
    digest = sha256(FUZZ_WIRE_DOMAIN + b":report:" + bencode({
        b"results": [{b"case": item.case_digest, b"label": item.label, b"passed": 1 if item.passed else 0, b"accept": 1 if item.observed_accept else 0, b"reason": item.observed_reason} for item in results],
        b"accepted": accepted,
        b"rejected": rejected,
        b"failed": failed,
    }))
    return FuzzRunReport(results, accepted, rejected, failed, digest)
