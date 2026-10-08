"""Skip-clean SAM smoke-probe planning before real router integration.

This is still a no-network shadow surface.  A future live SAM harness should be
allowed to skip cleanly when no router is present, but if a transcript is
supplied it must bind to the contact lease destination and to the canonical
SAM-wire script report.  The bug class here is treating "router answered" as
proof that the selected DHT contact is the same identity the lease advertised.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .contactlease import ContactLease
from .ids import DOMAIN, sha256
from .samwire import SamWireDecisionKind, SamWireScriptReport, SamWireSend, SamWireStep, assess_sam_wire_script

LIVE_SMOKE_DOMAIN = DOMAIN + b":live-smoke-v2:"
MAX_PROBE_TTL_SECONDS = 60


class SamSmokeObservationKind(str, Enum):
    ENDPOINT_ABSENT = "endpoint_absent"
    HELLO_OK = "hello_ok"
    BAD_BANNER = "bad_banner"
    CONNECT_ERROR = "connect_error"
    SESSION_OK = "session_ok"
    SESSION_REJECTED = "session_rejected"
    FRAME_SENT = "frame_sent"


class SamSmokeDecisionKind(str, Enum):
    SKIP_CLEAN_NO_ENDPOINT = "skip_clean_no_endpoint"
    ACCEPT_SMOKE_PROBE = "accept_smoke_probe"
    WATCH_SESSION_REJECTED = "watch_session_rejected"
    QUARANTINE_BAD_BANNER = "quarantine_bad_banner"
    QUARANTINE_DESTINATION_DRIFT = "quarantine_destination_drift"
    QUARANTINE_SAM_SCRIPT = "quarantine_sam_script"
    QUARANTINE_TIME_WINDOW = "quarantine_time_window"
    EMPTY_NO_OBSERVATIONS = "empty_no_observations"


@dataclass(frozen=True)
class SamSmokeObservation:
    kind: SamSmokeObservationKind
    issued_at: int
    detail: str = ""

    def bvalue(self) -> dict[bytes, BValue]:
        return {b"kind": self.kind.value, b"issued_at": self.issued_at, b"detail": self.detail[:200]}


@dataclass(frozen=True)
class SamSmokePlan:
    host: str = "127.0.0.1"
    port: int = 7656
    connect_timeout_ms: int = 500
    probe_ttl_seconds: int = MAX_PROBE_TTL_SECONDS
    allow_absent_skip: bool = True

    def validate(self) -> None:
        if not self.host or not (0 < self.port < 65536):
            raise ValueError("SAM smoke plan needs a host and valid port")
        if self.connect_timeout_ms <= 0 or self.probe_ttl_seconds <= 0 or self.probe_ttl_seconds > MAX_PROBE_TTL_SECONDS:
            raise ValueError("SAM smoke timeouts outside prototype bounds")

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"host": self.host,
            b"port": self.port,
            b"connect_timeout_ms": self.connect_timeout_ms,
            b"probe_ttl_seconds": self.probe_ttl_seconds,
            b"allow_absent_skip": 1 if self.allow_absent_skip else 0,
        }


@dataclass(frozen=True)
class SamLiveSmokeReport:
    decision_kind: SamSmokeDecisionKind
    accept: bool
    skipped: bool
    reason: str
    sam_binding: SamWireScriptReport | None
    transcript_digest: bytes

    @property
    def quarantine(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")

    @property
    def quarantined(self) -> bool:
        return self.quarantine


def _digest(label: bytes, *parts: bytes) -> bytes:
    return sha256(LIVE_SMOKE_DOMAIN + label + bencode(list(parts)))


def assess_sam_live_smoke(
    *,
    lease: ContactLease,
    plan: SamSmokePlan,
    observations: Iterable[SamSmokeObservation],
    sam_steps: Iterable[SamWireStep | SamWireSend],
    now: int,
) -> SamLiveSmokeReport:
    """Assess a no-network SAM smoke transcript against a selected contact lease.

    Endpoint absence is allowed to be a clean skip.  Any supplied SAM-wire script
    is assessed against the lease destination so a later implementation cannot
    accidentally prove a different persistent destination.
    """
    plan.validate()
    obs = tuple(observations)
    steps = tuple(sam_steps)
    if not obs:
        digest = _digest(b":report:empty:", bencode(plan.bvalue()))
        return SamLiveSmokeReport(SamSmokeDecisionKind.EMPTY_NO_OBSERVATIONS, False, False, "no SAM smoke observations supplied", None, digest)
    if any(now - item.issued_at > plan.probe_ttl_seconds or item.issued_at > now + plan.probe_ttl_seconds for item in obs):
        digest = _digest(b":report:time:", bencode([item.bvalue() for item in obs]))
        return SamLiveSmokeReport(SamSmokeDecisionKind.QUARANTINE_TIME_WINDOW, False, False, "SAM smoke observations outside local time window", None, digest)
    kinds = {item.kind for item in obs}
    if SamSmokeObservationKind.BAD_BANNER in kinds:
        digest = _digest(b":report:bad-banner:", bencode([item.bvalue() for item in obs]))
        return SamLiveSmokeReport(SamSmokeDecisionKind.QUARANTINE_BAD_BANNER, False, False, "endpoint responded with a non-SAM or malformed banner", None, digest)
    if SamSmokeObservationKind.ENDPOINT_ABSENT in kinds or SamSmokeObservationKind.CONNECT_ERROR in kinds:
        if plan.allow_absent_skip:
            digest = _digest(b":report:skip:", bencode([plan.bvalue(), [item.bvalue() for item in obs]]))
            return SamLiveSmokeReport(SamSmokeDecisionKind.SKIP_CLEAN_NO_ENDPOINT, True, True, "SAM endpoint absent; live smoke probe skipped cleanly", None, digest)
    binding = assess_sam_wire_script(steps, now=now, expected_destination=lease.destination)
    if binding.decision_kind is SamWireDecisionKind.QUARANTINE_DESTINATION_DRIFT:
        digest = _digest(b":report:drift:", binding.transcript_digest)
        return SamLiveSmokeReport(SamSmokeDecisionKind.QUARANTINE_DESTINATION_DRIFT, False, False, binding.reason, binding, digest)
    if binding.quarantined or not binding.accept:
        digest = _digest(b":report:sam-script:", binding.transcript_digest)
        return SamLiveSmokeReport(SamSmokeDecisionKind.QUARANTINE_SAM_SCRIPT, False, False, binding.reason, binding, digest)
    if SamSmokeObservationKind.SESSION_REJECTED in kinds:
        digest = _digest(b":report:session-watch:", binding.transcript_digest)
        return SamLiveSmokeReport(SamSmokeDecisionKind.WATCH_SESSION_REJECTED, False, False, "SAM endpoint answered but rejected the test session", binding, digest)
    digest = sha256(LIVE_SMOKE_DOMAIN + b":report:accept:" + bencode({
        b"plan": plan.bvalue(),
        b"obs": [item.bvalue() for item in obs],
        b"binding": binding.transcript_digest,
    }))
    return SamLiveSmokeReport(SamSmokeDecisionKind.ACCEPT_SMOKE_PROBE, True, False, "SAM smoke transcript and contact lease binding are locally coherent", binding, digest)
