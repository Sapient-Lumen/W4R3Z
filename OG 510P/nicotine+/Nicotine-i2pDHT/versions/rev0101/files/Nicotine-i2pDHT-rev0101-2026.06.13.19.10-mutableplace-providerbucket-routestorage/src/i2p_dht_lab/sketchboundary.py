"""Set-reconciliation adapter boundary for peer/range delta work.

The cube has exact toy sketches because they are easy to test.  rev0031 draws a
harder line: exact debug sketches are acceptable only inside the lab, while the
future production boundary should be an adapter to a real reconciliation engine
such as minisketch/PinSketch or an IBLT-style codec.

This module does not implement minisketch or IBLT.  It pins the handshake,
capacity, salt/replay, and privacy-budget decisions that must exist before such
an adapter can be trusted by garden nodes or bootstrap repair.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .ids import DOMAIN, sha256

SKETCH_BOUNDARY_DOMAIN = DOMAIN + b":sketch-boundary-v1:"


class SketchEngineKind(str, Enum):
    EXACT_DEBUG = "exact_debug"
    MINISKETCH = "minisketch"
    IBLT = "iblt"


class SketchContextKind(str, Enum):
    LAB = "lab"
    PRODUCTION = "production"
    GARDEN_SERVICE = "garden_service"


class SketchBoundaryDecisionKind(str, Enum):
    ACCEPT_EXACT_DEBUG_LAB = "accept_exact_debug_lab"
    ACCEPT_NATIVE_ADAPTER_BOUNDARY = "accept_native_adapter_boundary"
    REQUEST_SKETCH_EXTENSION = "request_sketch_extension"
    CONTINUE_NEED_NATIVE_ADAPTER = "continue_need_native_adapter"
    REJECT_CAPACITY_TOO_LOW = "reject_capacity_too_low"
    REJECT_PRIVACY_BUDGET = "reject_privacy_budget"
    QUARANTINE_EXACT_DEBUG_OUTSIDE_LAB = "quarantine_exact_debug_outside_lab"
    QUARANTINE_SALT_REPLAY = "quarantine_salt_replay"
    QUARANTINE_ENGINE_MISMATCH = "quarantine_engine_mismatch"


@dataclass(frozen=True)
class SketchAdapterOffer:
    engine: SketchEngineKind
    version: str
    source_family: str
    max_capacity: int
    element_bits: int
    supports_extension: bool
    adapter_digest: bytes = b""

    def __post_init__(self) -> None:
        if not self.version or not self.source_family or self.max_capacity <= 0 or self.element_bits <= 0:
            raise ValueError("sketch adapter offer shape invalid")
        if self.adapter_digest and len(self.adapter_digest) != 32:
            raise ValueError("sketch adapter digest must be empty or 32 bytes")

    @property
    def offer_digest(self) -> bytes:
        return self.adapter_digest or sha256(SKETCH_BOUNDARY_DOMAIN + b":offer:" + bencode(self.bvalue()))

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"engine": self.engine.value,
            b"version": self.version,
            b"source_family": self.source_family,
            b"max_capacity": self.max_capacity,
            b"element_bits": self.element_bits,
            b"supports_extension": 1 if self.supports_extension else 0,
        }


@dataclass(frozen=True)
class SketchRequest:
    range_id: bytes
    engine: SketchEngineKind
    context: SketchContextKind
    expected_difference: int
    capacity: int
    element_bits: int
    session_salt: bytes
    allow_exact_debug: bool = False
    privacy_budget_bytes: int = 2048
    raw_element_count: int = 0

    def __post_init__(self) -> None:
        if len(self.range_id) != 32 or len(self.session_salt) < 16:
            raise ValueError("sketch request range/salt invalid")
        if self.expected_difference < 0 or self.capacity <= 0 or self.element_bits <= 0 or self.privacy_budget_bytes < 0 or self.raw_element_count < 0:
            raise ValueError("sketch request counters invalid")

    @property
    def request_digest(self) -> bytes:
        return sha256(SKETCH_BOUNDARY_DOMAIN + b":request:" + bencode(self.bvalue()))

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"range_id": self.range_id,
            b"engine": self.engine.value,
            b"context": self.context.value,
            b"expected_difference": self.expected_difference,
            b"capacity": self.capacity,
            b"element_bits": self.element_bits,
            b"session_salt": self.session_salt,
            b"allow_exact_debug": 1 if self.allow_exact_debug else 0,
            b"privacy_budget_bytes": self.privacy_budget_bytes,
            b"raw_element_count": self.raw_element_count,
        }


@dataclass(frozen=True)
class SketchBoundaryAssessment:
    decision_kind: SketchBoundaryDecisionKind
    accept: bool
    reason: str
    request_digest: bytes
    selected_engine: SketchEngineKind
    selected_capacity: int
    estimated_wire_bytes: int
    pressure_digests: tuple[bytes, ...]
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def short_reconciliation_id(element_digest: bytes, *, salt: bytes, bits: int = 32) -> int:
    if len(element_digest) != 32 or len(salt) < 16:
        raise ValueError("short reconciliation id needs 32-byte digest and fresh salt")
    if bits <= 0 or bits > 64:
        raise ValueError("prototype short ids are limited to 1..64 bits")
    value = int.from_bytes(sha256(SKETCH_BOUNDARY_DOMAIN + b":short-id:" + salt + element_digest), "big")
    return 1 + (value % ((1 << bits) - 1))


def assess_sketch_boundary(
    request: SketchRequest,
    *,
    offer: SketchAdapterOffer | None = None,
    now: int = 0,
    previously_used_salts: Iterable[bytes] = (),
) -> SketchBoundaryAssessment:
    del now  # reserved for future signed adapter offers
    if request.session_salt in set(previously_used_salts):
        return _assessment(SketchBoundaryDecisionKind.QUARANTINE_SALT_REPLAY, False, "set reconciliation salt was replayed across sessions", request, offer, (sha256(request.session_salt),))
    if request.raw_element_count and request.raw_element_count * 32 > request.privacy_budget_bytes:
        return _assessment(SketchBoundaryDecisionKind.REJECT_PRIVACY_BUDGET, False, "raw element fallback would exceed local privacy/metadata budget", request, offer, ())
    if request.expected_difference > request.capacity:
        if offer is not None and offer.supports_extension and offer.engine is request.engine and offer.max_capacity >= request.expected_difference:
            return _assessment(SketchBoundaryDecisionKind.REQUEST_SKETCH_EXTENSION, False, "declared capacity is low; request extension before raw fallback", request, offer, (offer.offer_digest,))
        return _assessment(SketchBoundaryDecisionKind.REJECT_CAPACITY_TOO_LOW, False, "declared sketch capacity cannot cover expected difference", request, offer, ())
    if offer is not None:
        if offer.engine is not request.engine or offer.element_bits != request.element_bits:
            return _assessment(SketchBoundaryDecisionKind.QUARANTINE_ENGINE_MISMATCH, False, "adapter offer does not match requested engine/field width", request, offer, (offer.offer_digest,))
        if offer.max_capacity < request.capacity:
            return _assessment(SketchBoundaryDecisionKind.REJECT_CAPACITY_TOO_LOW, False, "adapter offer cannot satisfy requested capacity", request, offer, (offer.offer_digest,))
    if request.engine is SketchEngineKind.EXACT_DEBUG:
        if request.context is SketchContextKind.LAB and request.allow_exact_debug:
            return _assessment(SketchBoundaryDecisionKind.ACCEPT_EXACT_DEBUG_LAB, True, "exact sketch boundary accepted only inside lab/debug context", request, offer, ())
        return _assessment(SketchBoundaryDecisionKind.QUARANTINE_EXACT_DEBUG_OUTSIDE_LAB, False, "exact toy sketches are not admitted outside the lab", request, offer, ())
    if offer is None:
        return _assessment(SketchBoundaryDecisionKind.CONTINUE_NEED_NATIVE_ADAPTER, False, "native set-reconciliation adapter is not present yet", request, offer, ())
    return _assessment(SketchBoundaryDecisionKind.ACCEPT_NATIVE_ADAPTER_BOUNDARY, True, "native set-reconciliation adapter boundary is shape-compatible", request, offer, (offer.offer_digest,))


def _estimated_wire_bytes(request: SketchRequest, offer: SketchAdapterOffer | None) -> int:
    del offer
    # Boundary estimate only.  PinSketch/minisketch uses capacity * element_bits;
    # IBLT-style encodings typically need a larger overhead, so double it here.
    multiplier = 2 if request.engine is SketchEngineKind.IBLT else 1
    return ((request.capacity * request.element_bits * multiplier) + 7) // 8


def _assessment(kind: SketchBoundaryDecisionKind, accept: bool, reason: str, request: SketchRequest, offer: SketchAdapterOffer | None, pressures: Iterable[bytes]) -> SketchBoundaryAssessment:
    pressure_tuple = tuple(sorted(pressures))
    wire = _estimated_wire_bytes(request, offer)
    digest = sha256(SKETCH_BOUNDARY_DOMAIN + b":assessment:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"request": request.request_digest,
        b"offer": b"" if offer is None else offer.offer_digest,
        b"wire": wire,
        b"pressures": pressure_tuple,
    }))
    return SketchBoundaryAssessment(kind, accept, reason, request.request_digest, request.engine, request.capacity, wire, pressure_tuple, digest)
