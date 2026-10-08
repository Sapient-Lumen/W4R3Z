"""Signed RPC envelope sketches for the Python DHT prototype.

The envelope deliberately avoids committing to SAM Streaming vs datagrams. The
payload can be sent over either once the transport adapter exists.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, replace
from enum import Enum
from typing import Any

from .identity import DhtKeypair, verify_signature


class RpcOp(str, Enum):
    PING = "PING"
    FIND_NODE = "FIND_NODE"
    GET_IMMUTABLE = "GET_IMMUTABLE"
    PUT_IMMUTABLE = "PUT_IMMUTABLE"
    GET_MUTABLE = "GET_MUTABLE"
    PUT_MUTABLE = "PUT_MUTABLE"
    ANNOUNCE_PROVIDER = "ANNOUNCE_PROVIDER"
    FIND_PROVIDERS = "FIND_PROVIDERS"
    SAMPLE_KEYS = "SAMPLE_KEYS"


@dataclass(frozen=True)
class RpcEnvelope:
    version: int
    message_id: str
    op: RpcOp
    sender_node_id: str
    sender_public_key: str
    body: dict[str, Any]
    timestamp: int
    signature: str = ""

    def unsigned_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "message_id": self.message_id,
            "op": self.op.value,
            "sender_node_id": self.sender_node_id,
            "sender_public_key": self.sender_public_key,
            "body": self.body,
            "timestamp": self.timestamp,
        }

    def canonical_payload(self) -> bytes:
        return json.dumps(self.unsigned_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

    def signed(self, keypair: DhtKeypair) -> "RpcEnvelope":
        if keypair.public_key_bytes.hex() != self.sender_public_key:
            raise ValueError("sender_public_key does not match keypair")
        return replace(self, signature=keypair.sign(self.canonical_payload()).hex())

    def verify(self) -> bool:
        if not self.signature:
            return False
        return verify_signature(bytes.fromhex(self.sender_public_key), self.canonical_payload(), bytes.fromhex(self.signature))


def make_find_node_request(*, sender_node_id: bytes, sender_keypair: DhtKeypair, target: bytes, message_id: str, now: int) -> RpcEnvelope:
    return RpcEnvelope(
        version=1,
        message_id=message_id,
        op=RpcOp.FIND_NODE,
        sender_node_id=sender_node_id.hex(),
        sender_public_key=sender_keypair.public_key_bytes.hex(),
        body={"target": target.hex()},
        timestamp=now,
    ).signed(sender_keypair)
