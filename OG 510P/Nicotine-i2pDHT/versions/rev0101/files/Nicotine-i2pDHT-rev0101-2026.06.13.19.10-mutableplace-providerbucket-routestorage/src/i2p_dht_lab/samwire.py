"""No-network SAM-shadow script harness carrying canonical wire frames.

This is not a SAM client.  It is a deterministic transcript for the future
Python/I2P boundary: a session must be created before frames are sent, outbound
sends must bind to canonical ``WireFrame`` validation, reconnects should keep the
same persistent destination, and invalid wire frames must fail before transport
noise can hide them.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .wirecanon import WireFrame, WireValidationKind, validate_wire_frame

SAM_WIRE_DOMAIN = DOMAIN + b":sam-wire-shadow-v1:"


class SamStepKind(str, Enum):
    HELLO = "hello"
    SESSION_CREATE = "session_create"
    STREAM_CONNECT = "stream_connect"
    STREAM_SEND = "stream_send"
    STREAM_CLOSE = "stream_close"
    RECONNECT = "reconnect"


class SamWireDecisionKind(str, Enum):
    ACCEPT_SCRIPT = "accept_script"
    WATCH_RECONNECT_SAME_DESTINATION = "watch_reconnect_same_destination"
    QUARANTINE_SEND_BEFORE_SESSION = "quarantine_send_before_session"
    QUARANTINE_DESTINATION_DRIFT = "quarantine_destination_drift"
    QUARANTINE_FRAME_INVALID = "quarantine_frame_invalid"
    QUARANTINE_STEP_SIGNATURE = "quarantine_step_signature"
    QUARANTINE_TIME_WINDOW = "quarantine_time_window"
    EMPTY_NO_STEPS = "empty_no_steps"


@dataclass(frozen=True)
class SamWireStep:
    kind: SamStepKind
    session_id: str
    destination: str
    issued_at: int
    expires_at: int
    public_key: bytes
    frame_digest: bytes = b""
    payload_digest: bytes = b""
    note: str = ""
    signature: bytes = b""

    def __post_init__(self) -> None:
        if not self.session_id or not self.destination:
            raise ValueError("SAM wire step needs session id and destination")
        if len(self.public_key) != 32:
            raise ValueError("SAM wire step public key must be 32 bytes")
        for name, value in (("frame_digest", self.frame_digest), ("payload_digest", self.payload_digest)):
            if value and len(value) != 32:
                raise ValueError(f"{name} must be empty or 32 bytes")
        if self.expires_at <= self.issued_at:
            raise ValueError("SAM wire step expires_at must follow issued_at")

    @classmethod
    def create(
        cls,
        *,
        keypair: DhtKeypair,
        kind: SamStepKind,
        session_id: str,
        destination: str,
        issued_at: int,
        ttl: int = 300,
        frame: WireFrame | None = None,
        payload: bytes = b"",
        note: str = "",
    ) -> "SamWireStep":
        if ttl <= 0:
            raise ValueError("SAM wire step ttl must be positive")
        unsigned = cls(
            kind=kind,
            session_id=session_id,
            destination=destination,
            issued_at=issued_at,
            expires_at=issued_at + ttl,
            public_key=keypair.public_key_bytes,
            frame_digest=b"" if frame is None else frame.frame_digest,
            payload_digest=b"" if not payload else sha256(SAM_WIRE_DOMAIN + b":payload:" + payload),
            note=note,
        )
        return replace(unsigned, signature=keypair.sign(unsigned.unsigned_payload()))

    @property
    def step_digest(self) -> bytes:
        return sha256(SAM_WIRE_DOMAIN + b":step:" + self.unsigned_payload() + self.signature)

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"kind": self.kind.value,
            b"session_id": self.session_id,
            b"destination": self.destination,
            b"issued_at": self.issued_at,
            b"expires_at": self.expires_at,
            b"public_key": self.public_key,
            b"frame_digest": self.frame_digest,
            b"payload_digest": self.payload_digest,
            b"note": self.note,
        }

    def unsigned_payload(self) -> bytes:
        return SAM_WIRE_DOMAIN + b":step-unsigned:" + bencode(self.unsigned_bvalue())

    def verify(self, *, now: int) -> bool:
        if now < self.issued_at or now >= self.expires_at:
            return False
        return verify_signature(self.public_key, self.unsigned_payload(), self.signature)


@dataclass(frozen=True)
class SamWireSend:
    step: SamWireStep
    frame: WireFrame
    payload: bytes

    @property
    def digest(self) -> bytes:
        return sha256(SAM_WIRE_DOMAIN + b":send:" + bencode({
            b"step": self.step.step_digest,
            b"frame": self.frame.frame_digest,
            b"payload": sha256(self.payload),
        }))


@dataclass(frozen=True)
class SamWireScriptReport:
    decision_kind: SamWireDecisionKind
    accept: bool
    reason: str
    step_digests: tuple[bytes, ...]
    send_count: int
    reconnect_count: int
    transcript_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def assess_sam_wire_script(
    steps: Iterable[SamWireStep | SamWireSend],
    *,
    now: int,
    expected_destination: str | None = None,
) -> SamWireScriptReport:
    items = tuple(steps)
    if not items:
        digest = sha256(SAM_WIRE_DOMAIN + b":report:empty")
        return SamWireScriptReport(SamWireDecisionKind.EMPTY_NO_STEPS, True, "no SAM-shadow steps supplied", (), 0, 0, digest)
    session_created = False
    hello_seen = False
    destination = expected_destination
    step_digests: list[bytes] = []
    send_count = 0
    reconnect_count = 0
    decision = SamWireDecisionKind.ACCEPT_SCRIPT
    accept = True
    reason = "SAM-shadow script keeps session/destination order and valid canonical frames"
    for item in items:
        step = item.step if isinstance(item, SamWireSend) else item
        step_digests.append(step.step_digest)
        if not step.verify(now=now):
            decision = SamWireDecisionKind.QUARANTINE_STEP_SIGNATURE if step.issued_at <= now < step.expires_at else SamWireDecisionKind.QUARANTINE_TIME_WINDOW
            accept = False
            reason = "SAM-shadow step failed signature or time-window validation"
            break
        if destination is None:
            destination = step.destination
        elif step.destination != destination:
            decision = SamWireDecisionKind.QUARANTINE_DESTINATION_DRIFT
            accept = False
            reason = "SAM-shadow script changed persistent destination mid-session"
            break
        if step.kind is SamStepKind.HELLO:
            hello_seen = True
        elif step.kind is SamStepKind.SESSION_CREATE:
            if not hello_seen:
                decision = SamWireDecisionKind.QUARANTINE_SEND_BEFORE_SESSION
                accept = False
                reason = "session create appeared before HELLO"
                break
            session_created = True
        elif step.kind is SamStepKind.RECONNECT:
            reconnect_count += 1
            if not session_created:
                decision = SamWireDecisionKind.QUARANTINE_SEND_BEFORE_SESSION
                accept = False
                reason = "reconnect appeared before a session existed"
                break
        elif step.kind in {SamStepKind.STREAM_CONNECT, SamStepKind.STREAM_SEND, SamStepKind.STREAM_CLOSE}:
            if not session_created:
                decision = SamWireDecisionKind.QUARANTINE_SEND_BEFORE_SESSION
                accept = False
                reason = "stream operation appeared before session create"
                break
        if isinstance(item, SamWireSend):
            send_count += 1
            if step.kind is not SamStepKind.STREAM_SEND:
                decision = SamWireDecisionKind.QUARANTINE_FRAME_INVALID
                accept = False
                reason = "SAM-wire send wrapper must use a STREAM_SEND step"
                break
            if step.frame_digest != item.frame.frame_digest or step.payload_digest != sha256(SAM_WIRE_DOMAIN + b":payload:" + item.payload):
                decision = SamWireDecisionKind.QUARANTINE_FRAME_INVALID
                accept = False
                reason = "SAM-wire send digest binding does not match frame/payload"
                break
            validation = validate_wire_frame(item.frame, payload=item.payload, now=now)
            if validation.kind is not WireValidationKind.ACCEPT_FRAME:
                decision = SamWireDecisionKind.QUARANTINE_FRAME_INVALID
                accept = False
                reason = "canonical wire frame failed before SAM send: " + validation.reason
                break
    if accept and reconnect_count:
        decision = SamWireDecisionKind.WATCH_RECONNECT_SAME_DESTINATION
        reason = "SAM-shadow script reconnected while preserving persistent destination"
    digest = sha256(SAM_WIRE_DOMAIN + b":report:" + bencode({
        b"decision": decision.value,
        b"accept": 1 if accept else 0,
        b"steps": step_digests,
        b"send_count": send_count,
        b"reconnect_count": reconnect_count,
    }))
    return SamWireScriptReport(decision, accept, reason, tuple(step_digests), send_count, reconnect_count, digest)
