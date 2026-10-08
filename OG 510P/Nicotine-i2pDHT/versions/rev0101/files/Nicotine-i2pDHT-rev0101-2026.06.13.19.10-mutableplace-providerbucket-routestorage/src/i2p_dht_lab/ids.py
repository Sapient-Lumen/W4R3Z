"""Identity, target, and XOR helpers for the I2P DHT prototype."""
from __future__ import annotations

import hashlib

DOMAIN = b"i2p-substrate-dht-v1"
NODE_ID_BYTES = 32
BT_TARGET_BYTES = 20


def sha256(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def sha1(data: bytes) -> bytes:
    return hashlib.sha1(data).digest()


def normalize_destination(destination: str) -> bytes:
    """Normalize a synthetic I2P Destination string for deterministic tests.

    Real code must hash the binary I2P Destination, not a display string.
    """
    normalized = " ".join(destination.strip().split())
    if not normalized:
        raise ValueError("destination must not be empty")
    return normalized.encode("utf-8")


def destination_hash(destination: str) -> bytes:
    return sha256(normalize_destination(destination))


def node_id_from_destination(destination: str) -> bytes:
    """Destination-only node id, retained for simple tests and cold contacts."""
    return sha256(DOMAIN + b":node-id-destination-only:" + destination_hash(destination))


def node_id_from_parts(destination: str, public_key: bytes, work_nonce: bytes = b"") -> bytes:
    """Return the preferred node id: bound to I2P Destination + DHT pubkey + nonce."""
    if len(public_key) != 32:
        raise ValueError("public key must be 32 bytes")
    return sha256(DOMAIN + b":node-id:" + destination_hash(destination) + public_key + work_nonce)


def key_id(namespace: str, material: str | bytes) -> bytes:
    if isinstance(material, str):
        material_bytes = material.encode("utf-8")
    else:
        material_bytes = material
    if not namespace:
        raise ValueError("namespace must not be empty")
    return sha256(DOMAIN + b":key:" + namespace.encode("utf-8") + b":" + material_bytes)


def content_target(namespace: str, payload: bytes) -> bytes:
    if not namespace:
        raise ValueError("namespace must not be empty")
    return sha256(DOMAIN + b":content:" + namespace.encode("utf-8") + b":" + payload)


def xor_distance(left: bytes, right: bytes) -> int:
    if len(left) != len(right):
        raise ValueError("ids must be the same length")
    return int.from_bytes(left, "big") ^ int.from_bytes(right, "big")


def bucket_index(local_id: bytes, remote_id: bytes) -> int:
    """Return Kademlia-style bucket index for the XOR distance.

    Returns -1 for self distance. Otherwise returns 0 for the nearest bucket and
    255 for the farthest bucket in a 256-bit keyspace.
    """
    distance = xor_distance(local_id, remote_id)
    if distance == 0:
        return -1
    return distance.bit_length() - 1


def leading_zero_bits(data: bytes) -> int:
    count = 0
    for byte in data:
        if byte == 0:
            count += 8
            continue
        count += 8 - byte.bit_length()
        break
    return count


def hex_id(value: bytes) -> str:
    if len(value) != NODE_ID_BYTES:
        raise ValueError(f"expected {NODE_ID_BYTES} bytes")
    return value.hex()


def short_id(value: bytes, chars: int = 12) -> str:
    return value.hex()[:chars]
