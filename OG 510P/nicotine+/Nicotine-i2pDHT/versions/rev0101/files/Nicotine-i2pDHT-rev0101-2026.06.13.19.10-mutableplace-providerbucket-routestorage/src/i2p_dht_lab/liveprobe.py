"""No-router live-probe shadow for SAM/I2P readiness.

A future prototype should run a smoke probe against a local SAM endpoint, but the
cube must stay clean when no router exists.  Connection absence is a clean skip;
successful HELLO/session shadowing must bind to a persistent contact lease.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable, Protocol

from .bencode import bencode
from .contactlease import ContactLease
from .ids import DOMAIN, sha256
from .samshadow import SamShadowProfile, SamShadowTranscript, make_streaming_first_shadow
from .samwire import SamWireScriptReport

LIVE_PROBE_DOMAIN = DOMAIN + b":live-probe-v1:"


class LiveProbeDecisionKind(str, Enum):
    SKIP_NO_ROUTER = "skip_no_router"
    ACCEPT_LIVE_PROBE = "accept_live_probe"
    WATCH_RECONNECT_PROBE = "watch_reconnect_probe"
    ACCEPT_STREAMING_FIRST = "accept_streaming_first"
    WATCH_ROUTER_PRESENT_BUT_CONTACT_UNPROBED = "watch_router_present_but_contact_unprobed"
    QUARANTINE_TRANSCRIPT_INVALID = "quarantine_transcript_invalid"
    QUARANTINE_CHALLENGE_MISMATCH = "quarantine_challenge_mismatch"
    QUARANTINE_FAMILY_MONOCULTURE = "quarantine_family_monoculture"
    QUARANTINE_DESTINATION_DRIFT = "quarantine_destination_drift"
    QUARANTINE_LEASE_INVALID = "quarantine_lease_invalid"
    QUARANTINE_SOCKET_ERROR = "quarantine_socket_error"


class SocketLike(Protocol):
    def settimeout(self, seconds: float) -> None: ...
    def connect(self, address: tuple[str, int]) -> None: ...
    def sendall(self, data: bytes) -> None: ...
    def recv(self, size: int) -> bytes: ...
    def close(self) -> None: ...


SocketFactory = Callable[[], SocketLike]


@dataclass(frozen=True)
class LiveProbeConfig:
    host: str = "127.0.0.1"
    port: int = 7656
    timeout: float = 0.05
    session_id: str = "i2p-dht-lab"
    require_persistent_destination: bool = True

    def __post_init__(self) -> None:
        if not self.host or self.port <= 0 or self.timeout <= 0 or not self.session_id:
            raise ValueError("live probe config invalid")


@dataclass(frozen=True)
class LiveProbeReport:
    decision_kind: LiveProbeDecisionKind
    ok: bool
    reason: str
    transcript_digest: bytes
    router_present: bool
    clean_skip: bool
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


@dataclass(frozen=True)
class SamContactProbe:
    lease: ContactLease
    shadow_transcript: SamShadowTranscript | None
    wire_report: SamWireScriptReport | None = None

    @property
    def digest(self) -> bytes:
        return sha256(LIVE_PROBE_DOMAIN + b":contact-probe:" + bencode({b"lease": self.lease.lease_hash, b"shadow": b"" if self.shadow_transcript is None else self.shadow_transcript.digest, b"wire": b"" if self.wire_report is None else self.wire_report.transcript_digest}))


def assess_sam_contact_probe(probe: SamContactProbe, *, now: int, profile: SamShadowProfile | None = None) -> LiveProbeReport:
    profile = profile or SamShadowProfile(session_id="i2p-dht-lab", destination_name=probe.lease.destination)
    if not probe.lease.verify(now=now):
        return _report(LiveProbeDecisionKind.QUARANTINE_LEASE_INVALID, False, "contact lease failed before SAM contact probing", b"", True, False)
    if profile.destination_name != probe.lease.destination:
        return _report(LiveProbeDecisionKind.QUARANTINE_DESTINATION_DRIFT, False, "SAM profile destination does not match contact lease destination", b"", True, False)
    if probe.shadow_transcript is None:
        return _report(LiveProbeDecisionKind.WATCH_ROUTER_PRESENT_BUT_CONTACT_UNPROBED, True, "router may be present but no transcript was attached to this contact", b"", True, False)
    validation = probe.shadow_transcript.validate(profile=profile)
    if not validation.ok:
        return _report(LiveProbeDecisionKind.QUARANTINE_TRANSCRIPT_INVALID, False, validation.reason, validation.transcript_digest, True, False)
    if probe.wire_report is not None and (not probe.wire_report.accept or probe.wire_report.quarantined):
        return _report(LiveProbeDecisionKind.QUARANTINE_TRANSCRIPT_INVALID, False, probe.wire_report.reason, validation.transcript_digest, True, False)
    return _report(LiveProbeDecisionKind.ACCEPT_STREAMING_FIRST, True, "streaming-first SAM contact probe matches persistent lease destination", validation.transcript_digest, True, False)


def assess_no_router_smoke(*, config: LiveProbeConfig = LiveProbeConfig(), socket_factory: SocketFactory | None = None) -> LiveProbeReport:
    if socket_factory is None:
        import socket
        socket_factory = socket.socket  # type: ignore[assignment]
    sock: SocketLike | None = None
    try:
        sock = socket_factory()
        sock.settimeout(config.timeout)
        sock.connect((config.host, config.port))
        sock.sendall(b"HELLO VERSION MIN=3.1 MAX=3.3\n")
        data = sock.recv(256)
    except ConnectionRefusedError:
        return _report(LiveProbeDecisionKind.SKIP_NO_ROUTER, True, "no SAM router is listening; smoke probe skipped cleanly", b"", False, True)
    except OSError as exc:
        text = str(exc).lower()
        if any(word in text for word in ("refused", "timed out", "timeout", "unreachable", "reset")):
            return _report(LiveProbeDecisionKind.SKIP_NO_ROUTER, True, "SAM smoke probe skipped cleanly after local socket absence", b"", False, True)
        return _report(LiveProbeDecisionKind.QUARANTINE_SOCKET_ERROR, False, f"unexpected socket error: {exc}", b"", False, False)
    finally:
        if sock is not None:
            try:
                sock.close()
            except Exception:
                pass
    if b"HELLO REPLY" not in data.upper():
        return _report(LiveProbeDecisionKind.QUARANTINE_TRANSCRIPT_INVALID, False, "SAM endpoint answered without HELLO REPLY", sha256(data), True, False)
    profile = SamShadowProfile(session_id=config.session_id, destination_name="probe-destination.keys", persistent_destination=config.require_persistent_destination)
    transcript = make_streaming_first_shadow(profile, "remote-dest.b32.i2p")
    validation = transcript.validate(profile=profile)
    if not validation.ok:
        return _report(LiveProbeDecisionKind.QUARANTINE_TRANSCRIPT_INVALID, False, validation.reason, validation.transcript_digest, True, False)
    return _report(LiveProbeDecisionKind.ACCEPT_STREAMING_FIRST, True, "SAM endpoint answered HELLO and streaming-first shadow validates", validation.transcript_digest, True, False)


def _report(kind: LiveProbeDecisionKind, ok: bool, reason: str, transcript_digest: bytes, router_present: bool, clean_skip: bool) -> LiveProbeReport:
    digest = sha256(LIVE_PROBE_DOMAIN + b":report:" + bencode({b"kind": kind.value, b"ok": 1 if ok else 0, b"reason": reason, b"transcript": transcript_digest, b"router_present": 1 if router_present else 0, b"clean_skip": 1 if clean_skip else 0}))
    return LiveProbeReport(kind, ok, reason, transcript_digest, router_present, clean_skip, digest)


# rev0029 foldseal compatibility: challenge/receipt live-probe branchlet.
from dataclasses import replace as _dataclass_replace
from .identity import DhtKeypair, verify_signature


@dataclass(frozen=True)
class LiveProbeChallenge:
    challenger_node_id: bytes
    lease_hash: bytes
    nonce: bytes
    issued_at: int
    expires_at: int

    def __post_init__(self) -> None:
        if len(self.challenger_node_id) != 32 or len(self.lease_hash) != 32:
            raise ValueError("live probe challenge digests must be 32 bytes")
        if not self.nonce or self.expires_at <= self.issued_at:
            raise ValueError("live probe challenge nonce/time invalid")

    @property
    def challenge_digest(self) -> bytes:
        return sha256(LIVE_PROBE_DOMAIN + b":challenge:" + bencode({b"challenger": self.challenger_node_id, b"lease": self.lease_hash, b"nonce": self.nonce, b"issued_at": self.issued_at, b"expires_at": self.expires_at}))


@dataclass(frozen=True)
class LiveProbeReceipt:
    lease_hash: bytes
    challenge_digest: bytes
    responder_public_key: bytes
    observed_at: int
    signature: bytes = b""

    @classmethod
    def create(cls, *, keypair: DhtKeypair, lease: ContactLease, challenge: LiveProbeChallenge, observed_at: int) -> "LiveProbeReceipt":
        unsigned = cls(lease.lease_hash, challenge.challenge_digest, keypair.public_key_bytes, observed_at)
        return _dataclass_replace(unsigned, signature=keypair.sign(unsigned.unsigned_payload()))

    def unsigned_payload(self) -> bytes:
        return LIVE_PROBE_DOMAIN + b":receipt-unsigned:" + bencode({b"lease": self.lease_hash, b"challenge": self.challenge_digest, b"public_key": self.responder_public_key, b"observed_at": self.observed_at})

    @property
    def receipt_digest(self) -> bytes:
        return sha256(LIVE_PROBE_DOMAIN + b":receipt:" + self.unsigned_payload() + self.signature)

    def verify(self) -> bool:
        return verify_signature(self.responder_public_key, self.unsigned_payload(), self.signature)


def assess_live_probe(*, lease: ContactLease, challenge: LiveProbeChallenge, receipt: LiveProbeReceipt, now: int, sam_report: SamWireScriptReport | None = None) -> LiveProbeReport:
    if not lease.verify(now=now):
        return _report(LiveProbeDecisionKind.QUARANTINE_LEASE_INVALID, False, "contact lease failed before challenge receipt", b"", True, False)
    if challenge.lease_hash != lease.lease_hash or receipt.lease_hash != lease.lease_hash or receipt.challenge_digest != challenge.challenge_digest or receipt.responder_public_key != lease.public_key or not receipt.verify():
        return _report(LiveProbeDecisionKind.QUARANTINE_CHALLENGE_MISMATCH, False, "live probe receipt does not bind lease/challenge/key", receipt.receipt_digest, True, False)
    if not (challenge.issued_at <= now < challenge.expires_at) or receipt.observed_at < challenge.issued_at or receipt.observed_at >= challenge.expires_at:
        return _report(LiveProbeDecisionKind.QUARANTINE_CHALLENGE_MISMATCH, False, "live probe challenge/receipt outside time window", receipt.receipt_digest, True, False)
    if sam_report is not None and (not sam_report.accept or sam_report.quarantined):
        return _report(LiveProbeDecisionKind.QUARANTINE_TRANSCRIPT_INVALID, False, sam_report.reason, sam_report.transcript_digest, True, False)
    if sam_report is not None and sam_report.decision_kind.value == "watch_reconnect_same_destination":
        return _report(LiveProbeDecisionKind.WATCH_RECONNECT_PROBE, True, "live probe accepted but SAM shadow included reconnect", sam_report.transcript_digest, True, False)
    return _report(LiveProbeDecisionKind.ACCEPT_LIVE_PROBE, True, "live challenge receipt proves current local reachability observation", receipt.receipt_digest, True, False)


def assess_live_probe_window(reports: Iterable[tuple[LiveProbeReport, str]], *, min_families: int, max_per_family: int) -> LiveProbeReport:
    pairs = tuple(reports)
    counts: dict[str, int] = {}
    accepted = 0
    for report, family in pairs:
        if report.ok and not report.quarantined:
            accepted += 1
            counts[family] = counts.get(family, 0) + 1
    digest = sha256(LIVE_PROBE_DOMAIN + b":window:" + bencode({b"reports": [report.report_digest for report, _ in pairs], b"families": counts}))
    if accepted == 0 or len(counts) < min_families or any(count > max_per_family for count in counts.values()):
        return _report(LiveProbeDecisionKind.QUARANTINE_FAMILY_MONOCULTURE, False, "live probe window lacks family diversity", digest, True, False)
    return _report(LiveProbeDecisionKind.ACCEPT_LIVE_PROBE, True, "live probe window has diverse accepted receipts", digest, True, False)
