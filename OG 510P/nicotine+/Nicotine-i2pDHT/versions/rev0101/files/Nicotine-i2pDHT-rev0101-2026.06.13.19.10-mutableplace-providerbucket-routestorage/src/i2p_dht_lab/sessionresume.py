"""Session resume gate after service exit and router-stop shadows.

A service may have a valid resume intent, but that does not mean it should
immediately re-enter garden/bridge operation.  rev0041 models resume as a join
across exit reports, breaker recovery, session ledgers, leases, announcements,
relay tickets, router-session shadows, and hard-negative scans.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .bencode import bencode
from .ids import DOMAIN, sha256

SESSION_RESUME_DOMAIN = DOMAIN + b":session-resume-v1:"


class SessionResumeSignalKind(str, Enum):
    SERVICE_EXIT_RESUME = "service_exit_resume"
    BREAKER_RECOVERY = "breaker_recovery"
    SESSION_LEDGER = "session_ledger"
    SERVICE_LEASE = "service_lease"
    ANNOUNCEMENT = "announcement"
    RELAY_TICKET = "relay_ticket"
    ROUTER_SESSION = "router_session"
    HARD_NEGATIVE_SCAN = "hard_negative_scan"


class SessionResumeDecisionKind(str, Enum):
    ACCEPT_RESUME = "accept_resume"
    HOLD_NO_SIGNALS = "hold_no_signals"
    HOLD_NEEDS_EXIT_RESUME = "hold_needs_exit_resume"
    HOLD_NEEDS_BREAKER_RECOVERY = "hold_needs_breaker_recovery"
    HOLD_NEEDS_SESSION_LEDGER = "hold_needs_session_ledger"
    HOLD_NEEDS_SERVICE_LEASE = "hold_needs_service_lease"
    HOLD_NEEDS_ANNOUNCEMENT = "hold_needs_announcement"
    HOLD_NEEDS_RELAY_TICKET = "hold_needs_relay_ticket"
    HOLD_NEEDS_ROUTER_SESSION = "hold_needs_router_session"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    QUARANTINE_SIGNAL = "quarantine_signal"
    QUARANTINE_EXPIRED_OR_FUTURE = "quarantine_expired_or_future"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_KIND_FORK = "quarantine_kind_fork"
    QUARANTINE_SERVICE_DRIFT = "quarantine_service_drift"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_REQUEST_DRIFT = "quarantine_request_drift"
    QUARANTINE_SESSION_DRIFT = "quarantine_session_drift"
    QUARANTINE_WITHDRAWN_ANNOUNCEMENT = "quarantine_withdrawn_announcement"
    QUARANTINE_HARD_NEGATIVE_PRESENT = "quarantine_hard_negative_present"


@dataclass(frozen=True)
class SessionResumeSignal:
    kind: SessionResumeSignalKind
    report_digest: bytes
    accept: bool
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    session_id_digest: bytes
    issued_at: int
    expires_at: int
    source_family: str
    path_family: str
    quarantined: bool = False
    withdrawn: bool = False
    hard_negative_clear: bool = True
    detail: str = ""

    def __post_init__(self) -> None:
        if not self.service_name or len(self.service_name.encode("utf-8")) > 80:
            raise ValueError("service_name must be short and non-empty")
        if self.expires_at <= self.issued_at:
            raise ValueError("resume signal expires_at must be after issued_at")
        if not self.source_family or not self.path_family:
            raise ValueError("resume signal needs source and path family labels")
        for name, value in (
            ("report_digest", self.report_digest),
            ("scope_digest", self.scope_digest),
            ("request_digest", self.request_digest),
            ("session_id_digest", self.session_id_digest),
        ):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")

    @property
    def signal_digest(self) -> bytes:
        return sha256(SESSION_RESUME_DOMAIN + b":signal:" + bencode(self.bvalue()))

    def bvalue(self) -> dict[bytes, object]:
        return {
            b"kind": self.kind.value,
            b"report": self.report_digest,
            b"accept": 1 if self.accept else 0,
            b"service": self.service_name,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"session": self.session_id_digest,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"source_family": self.source_family,
            b"path_family": self.path_family,
            b"quarantined": 1 if self.quarantined else 0,
            b"withdrawn": 1 if self.withdrawn else 0,
            b"hard_negative_clear": 1 if self.hard_negative_clear else 0,
            b"detail": self.detail,
        }



def make_session_resume_signal(
    *,
    kind: SessionResumeSignalKind,
    label_digest: bytes,
    service_name: str,
    scope_digest: bytes,
    request_digest: bytes,
    session_id_digest: bytes,
    issued_at: int,
    expires_at: int,
    source_family: str = "family-a",
    path_family: str = "path-a",
    accept: bool = True,
    quarantined: bool = False,
    withdrawn: bool = False,
    hard_negative_clear: bool = True,
    detail: str = "",
) -> SessionResumeSignal:
    return SessionResumeSignal(kind, label_digest, accept, service_name, scope_digest, request_digest, session_id_digest, issued_at, expires_at, source_family, path_family, quarantined, withdrawn, hard_negative_clear, detail)


@dataclass(frozen=True)
class SessionResumePolicy:
    require_public_announcement: bool = True
    require_relay_ticket_for_bridge: bool = False
    min_signal_families: int = 2
    min_path_families: int = 2


@dataclass(frozen=True)
class SessionResumeReport:
    decision_kind: SessionResumeDecisionKind
    accept: bool
    reason: str
    service_name: str | None
    scope_digest: bytes | None
    request_digest: bytes | None
    session_id_digest: bytes | None
    signal_digests: tuple[bytes, ...]
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")



def _report(kind: SessionResumeDecisionKind, accept: bool, reason: str, signals: Iterable[SessionResumeSignal]) -> SessionResumeReport:
    sigs = tuple(sorted(signals, key=lambda item: (item.kind.value, item.signal_digest)))
    first = sigs[0] if sigs else None
    digests = tuple(sorted(signal.signal_digest for signal in sigs))
    digest = sha256(SESSION_RESUME_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"reason": reason,
        b"service": first.service_name if first else "",
        b"scope": first.scope_digest if first else b"",
        b"request": first.request_digest if first else b"",
        b"session": first.session_id_digest if first else b"",
        b"signals": list(digests),
    }))
    return SessionResumeReport(kind, accept, reason, first.service_name if first else None, first.scope_digest if first else None, first.request_digest if first else None, first.session_id_digest if first else None, digests, digest)



def assess_session_resume(
    signals: Iterable[SessionResumeSignal],
    *,
    now: int,
    expected_service_name: str,
    expected_scope_digest: bytes,
    expected_request_digest: bytes,
    expected_session_id_digest: bytes,
    previously_seen_signals: Iterable[bytes] = (),
    bridge_mode: bool = False,
    policy: SessionResumePolicy | None = None,
) -> SessionResumeReport:
    policy = policy or SessionResumePolicy()
    sigs = tuple(signals)
    if not sigs:
        return _report(SessionResumeDecisionKind.HOLD_NO_SIGNALS, False, "no resume signals", sigs)
    if any(sig.quarantined for sig in sigs):
        return _report(SessionResumeDecisionKind.QUARANTINE_SIGNAL, False, "component signal quarantined", sigs)
    if any(sig.issued_at > now or sig.expires_at <= now for sig in sigs):
        return _report(SessionResumeDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, False, "resume signal outside local time window", sigs)
    seen = set(previously_seen_signals)
    if any(sig.signal_digest in seen for sig in sigs):
        return _report(SessionResumeDecisionKind.QUARANTINE_REPLAY, False, "resume signal replay", sigs)
    if any(sig.service_name != expected_service_name for sig in sigs):
        return _report(SessionResumeDecisionKind.QUARANTINE_SERVICE_DRIFT, False, "resume service drift", sigs)
    if any(sig.scope_digest != expected_scope_digest for sig in sigs):
        return _report(SessionResumeDecisionKind.QUARANTINE_SCOPE_DRIFT, False, "resume scope drift", sigs)
    if any(sig.request_digest != expected_request_digest for sig in sigs):
        return _report(SessionResumeDecisionKind.QUARANTINE_REQUEST_DRIFT, False, "resume request drift", sigs)
    if any(sig.session_id_digest != expected_session_id_digest for sig in sigs):
        return _report(SessionResumeDecisionKind.QUARANTINE_SESSION_DRIFT, False, "resume session drift", sigs)
    by_kind: dict[SessionResumeSignalKind, set[bytes]] = {}
    for sig in sigs:
        by_kind.setdefault(sig.kind, set()).add(sig.report_digest)
    if any(len(digests) > 1 for digests in by_kind.values()):
        return _report(SessionResumeDecisionKind.QUARANTINE_KIND_FORK, False, "same resume surface produced conflicting reports", sigs)
    if any(not sig.hard_negative_clear for sig in sigs):
        return _report(SessionResumeDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESENT, False, "resume still sees hard-negative pressure", sigs)
    if any(sig.kind is SessionResumeSignalKind.ANNOUNCEMENT and sig.withdrawn for sig in sigs):
        return _report(SessionResumeDecisionKind.QUARANTINE_WITHDRAWN_ANNOUNCEMENT, False, "resume announcement is withdrawn", sigs)
    accepted = {sig.kind for sig in sigs if sig.accept}
    required = (
        (SessionResumeSignalKind.SERVICE_EXIT_RESUME, SessionResumeDecisionKind.HOLD_NEEDS_EXIT_RESUME),
        (SessionResumeSignalKind.BREAKER_RECOVERY, SessionResumeDecisionKind.HOLD_NEEDS_BREAKER_RECOVERY),
        (SessionResumeSignalKind.SESSION_LEDGER, SessionResumeDecisionKind.HOLD_NEEDS_SESSION_LEDGER),
        (SessionResumeSignalKind.SERVICE_LEASE, SessionResumeDecisionKind.HOLD_NEEDS_SERVICE_LEASE),
        (SessionResumeSignalKind.ROUTER_SESSION, SessionResumeDecisionKind.HOLD_NEEDS_ROUTER_SESSION),
    )
    for kind, decision in required:
        if kind not in accepted:
            return _report(decision, False, f"resume needs accepted {kind.value}", sigs)
    if policy.require_public_announcement and SessionResumeSignalKind.ANNOUNCEMENT not in accepted:
        return _report(SessionResumeDecisionKind.HOLD_NEEDS_ANNOUNCEMENT, False, "resume needs accepted announcement", sigs)
    if bridge_mode or policy.require_relay_ticket_for_bridge:
        if SessionResumeSignalKind.RELAY_TICKET not in accepted:
            return _report(SessionResumeDecisionKind.HOLD_NEEDS_RELAY_TICKET, False, "bridge resume needs accepted relay ticket", sigs)
    source_families = {sig.source_family for sig in sigs if sig.accept}
    path_families = {sig.path_family for sig in sigs if sig.accept}
    if len(source_families) < policy.min_signal_families or len(path_families) < policy.min_path_families:
        return _report(SessionResumeDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, "resume needs source/path family diversity", sigs)
    return _report(SessionResumeDecisionKind.ACCEPT_RESUME, True, "resume joined across exit, breaker, lease, session, router, and exposure signals", sigs)
