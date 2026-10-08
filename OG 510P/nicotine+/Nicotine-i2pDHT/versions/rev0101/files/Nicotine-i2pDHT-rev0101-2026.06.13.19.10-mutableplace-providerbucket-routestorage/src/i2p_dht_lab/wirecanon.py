"""Canonical wire-envelope pressure before live I2P/SAM transport.

This is not a network protocol.  It is a deterministic envelope and transcript
fixture for the DHT's riskiest future messages so that signatures, TTLs,
payload digests, and domain separation are testable before SAM/I2P behavior
adds latency and partial failure.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256

WIRE_CANON_DOMAIN = DOMAIN + b":wire-canon-v1:"
WIRE_VERSION = 1
MAX_FRAME_TTL_SECONDS = 3600
MAX_PAYLOAD_BYTES = 64_000


class WireMessageKind(str, Enum):
    FIND_NODE = "find_node"
    FIND_PROVIDER = "find_provider"
    STORE_RECORD = "store_record"
    CUSTODY_CHALLENGE = "custody_challenge"
    CUSTODY_PROOF = "custody_proof"
    EPOCH_HEAD = "epoch_head"
    REPAIR_OFFER = "repair_offer"
    USEFUL_REFUSAL = "useful_refusal"
    WITNESS_RECEIPT = "witness_receipt"


class WireValidationKind(str, Enum):
    ACCEPT_FRAME = "accept_frame"
    REJECT_BAD_VERSION = "reject_bad_version"
    REJECT_TIME_WINDOW = "reject_time_window"
    REJECT_PAYLOAD_DIGEST = "reject_payload_digest"
    REJECT_BAD_SIGNATURE = "reject_bad_signature"
    REJECT_PAYLOAD_TOO_LARGE = "reject_payload_too_large"


@dataclass(frozen=True)
class WireFrame:
    version: int
    message_kind: WireMessageKind
    sender_node_id: bytes
    sender_public_key: bytes
    request_id: bytes
    payload_digest: bytes
    payload_size: int
    issued_at: int
    expires_at: int
    sequence: int = 0
    flags: tuple[str, ...] = ()
    signature: bytes = b""

    def __post_init__(self) -> None:
        if len(self.sender_node_id) != 32 or len(self.sender_public_key) != 32:
            raise ValueError("wire frame sender id/public key must be 32 bytes")
        if len(self.request_id) != 32 or len(self.payload_digest) != 32:
            raise ValueError("wire frame request_id/payload_digest must be 32 bytes")
        if self.payload_size < 0 or self.sequence < 0:
            raise ValueError("wire frame counters must be non-negative")
        if self.expires_at <= self.issued_at or self.expires_at - self.issued_at > MAX_FRAME_TTL_SECONDS:
            raise ValueError("wire frame ttl is invalid")
        if any(not flag or len(flag) > 64 for flag in self.flags):
            raise ValueError("wire flags must be short non-empty strings")

    @classmethod
    def create(
        cls,
        *,
        keypair: DhtKeypair,
        sender_node_id: bytes,
        message_kind: WireMessageKind,
        request_id: bytes,
        payload: bytes,
        issued_at: int,
        ttl: int = 300,
        sequence: int = 0,
        flags: tuple[str, ...] = (),
    ) -> "WireFrame":
        if ttl <= 0:
            raise ValueError("wire frame ttl must be positive")
        unsigned = cls(
            version=WIRE_VERSION,
            message_kind=message_kind,
            sender_node_id=sender_node_id,
            sender_public_key=keypair.public_key_bytes,
            request_id=request_id,
            payload_digest=sha256(WIRE_CANON_DOMAIN + b":payload:" + payload),
            payload_size=len(payload),
            issued_at=issued_at,
            expires_at=issued_at + min(ttl, MAX_FRAME_TTL_SECONDS),
            sequence=sequence,
            flags=tuple(sorted(flags)),
        )
        return replace(unsigned, signature=keypair.sign(unsigned.unsigned_payload()))

    @property
    def frame_digest(self) -> bytes:
        return sha256(WIRE_CANON_DOMAIN + b":frame:" + self.unsigned_payload() + self.signature)

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"version": self.version,
            b"message_kind": self.message_kind.value,
            b"sender_node_id": self.sender_node_id,
            b"sender_public_key": self.sender_public_key,
            b"request_id": self.request_id,
            b"payload_digest": self.payload_digest,
            b"payload_size": self.payload_size,
            b"issued_at": self.issued_at,
            b"expires_at": self.expires_at,
            b"sequence": self.sequence,
            b"flags": list(self.flags),
        }

    def unsigned_payload(self) -> bytes:
        return WIRE_CANON_DOMAIN + b":frame-unsigned:" + bencode(self.unsigned_bvalue())

    def signature_valid(self) -> bool:
        return verify_signature(self.sender_public_key, self.unsigned_payload(), self.signature)


@dataclass(frozen=True)
class WireValidation:
    kind: WireValidationKind
    accept: bool
    reason: str


@dataclass(frozen=True)
class WireTranscript:
    frames: tuple[WireFrame, ...]
    validations: tuple[WireValidation, ...]
    transcript_digest: bytes

    @property
    def accepted_count(self) -> int:
        return sum(1 for item in self.validations if item.accept)

    @property
    def rejected_count(self) -> int:
        return len(self.validations) - self.accepted_count


def validate_wire_frame(frame: WireFrame, *, payload: bytes, now: int) -> WireValidation:
    if frame.version != WIRE_VERSION:
        return WireValidation(WireValidationKind.REJECT_BAD_VERSION, False, "wire version is not supported")
    if not (frame.issued_at <= now < frame.expires_at):
        return WireValidation(WireValidationKind.REJECT_TIME_WINDOW, False, "wire frame is outside its validity window")
    if frame.payload_size > MAX_PAYLOAD_BYTES:
        return WireValidation(WireValidationKind.REJECT_PAYLOAD_TOO_LARGE, False, "wire payload exceeds prototype maximum")
    if frame.payload_size != len(payload) or frame.payload_digest != sha256(WIRE_CANON_DOMAIN + b":payload:" + payload):
        return WireValidation(WireValidationKind.REJECT_PAYLOAD_DIGEST, False, "wire payload digest or size does not match envelope")
    if not frame.signature_valid():
        return WireValidation(WireValidationKind.REJECT_BAD_SIGNATURE, False, "wire frame signature is invalid")
    return WireValidation(WireValidationKind.ACCEPT_FRAME, True, "wire frame is canonical, fresh, and signed")


def build_wire_transcript(frames_and_payloads: Iterable[tuple[WireFrame, bytes]], *, now: int) -> WireTranscript:
    pairs = tuple(frames_and_payloads)
    frames = tuple(pair[0] for pair in pairs)
    validations = tuple(validate_wire_frame(frame, payload=payload, now=now) for frame, payload in pairs)
    digest = sha256(WIRE_CANON_DOMAIN + b":transcript:" + bencode({
        b"frames": [frame.frame_digest for frame in frames],
        b"validations": [item.kind.value for item in validations],
        b"accepted": sum(1 for item in validations if item.accept),
        b"rejected": sum(1 for item in validations if not item.accept),
    }))
    return WireTranscript(frames, validations, digest)
