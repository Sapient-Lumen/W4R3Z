"""Transport-neutral wire transcript fixtures.

The DHT should not wait for live SAM/I2P transport before testing canonical
signing and transcript hashing.  These frames are not a production wire format;
they are deterministic fixtures for requests, replies, witness receipts, and
provider probes.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256

WIRE_TRANSCRIPT_DOMAIN = DOMAIN + b":wire-transcript-v1:"


class WireFrameKind(str, Enum):
    FIND_NODE = "find_node"
    FIND_PROVIDER = "find_provider"
    PROVIDER_PROBE = "provider_probe"
    WITNESS_RECEIPT = "witness_receipt"
    GARDEN_REFUSAL = "garden_refusal"
    MUTABLE_HEAD = "mutable_head"


@dataclass(frozen=True)
class WireFrame:
    sender_public_key: bytes
    sender_node_id: bytes
    receiver_node_id: bytes
    request_id: bytes
    kind: WireFrameKind
    sequence: int
    issued_at: int
    payload: dict[bytes, BValue]
    signature: bytes = b""

    @classmethod
    def create(
        cls,
        *,
        keypair: DhtKeypair,
        sender_node_id: bytes,
        receiver_node_id: bytes,
        request_id: bytes,
        kind: WireFrameKind,
        sequence: int,
        issued_at: int,
        payload: dict[bytes, BValue],
    ) -> "WireFrame":
        frame = cls(
            sender_public_key=keypair.public_key_bytes,
            sender_node_id=sender_node_id,
            receiver_node_id=receiver_node_id,
            request_id=request_id,
            kind=kind,
            sequence=sequence,
            issued_at=issued_at,
            payload=payload,
        )
        return replace(frame, signature=keypair.sign(frame.unsigned_payload()))

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"sender_public_key": self.sender_public_key,
            b"sender_node_id": self.sender_node_id,
            b"receiver_node_id": self.receiver_node_id,
            b"request_id": self.request_id,
            b"kind": self.kind.value,
            b"sequence": self.sequence,
            b"issued_at": self.issued_at,
            b"payload": self.payload,
        }

    def unsigned_payload(self) -> bytes:
        return WIRE_TRANSCRIPT_DOMAIN + b":frame:" + bencode(self.bvalue())

    @property
    def digest(self) -> bytes:
        return sha256(self.unsigned_payload() + self.signature)

    def verify(self) -> bool:
        if len(self.sender_public_key) != 32 or len(self.sender_node_id) != 32 or len(self.receiver_node_id) != 32:
            return False
        if len(self.request_id) != 32 or len(self.signature) != 64:
            return False
        if self.sequence < 0 or self.issued_at < 0:
            return False
        return verify_signature(self.sender_public_key, self.unsigned_payload(), self.signature)


@dataclass(frozen=True)
class WireTranscript:
    frames: tuple[WireFrame, ...]

    @property
    def digest(self) -> bytes:
        return sha256(WIRE_TRANSCRIPT_DOMAIN + b":transcript:" + b"".join(frame.digest for frame in self.frames))

    @property
    def request_ids(self) -> frozenset[bytes]:
        return frozenset(frame.request_id for frame in self.frames)

    def verify_all(self) -> bool:
        return all(frame.verify() for frame in self.frames)

    def duplicate_sequences(self) -> tuple[tuple[bytes, int], ...]:
        seen: set[tuple[bytes, int]] = set()
        duplicates: list[tuple[bytes, int]] = []
        for frame in self.frames:
            key = (frame.request_id, frame.sequence)
            if key in seen:
                duplicates.append(key)
            seen.add(key)
        return tuple(duplicates)


def make_transcript(frames: Iterable[WireFrame]) -> WireTranscript:
    return WireTranscript(tuple(frames))
