"""Generic DHT record algebra and validators.

The DHT core should not be born as a single-purpose file index. It needs a
small vocabulary of records that future consumers can use without changing the
routing substrate: immutable content records, provider records, peer/contact
records, and mutable slots.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, replace
from enum import Enum
from typing import Any

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import content_target, key_id

MAX_IMMUTABLE_VALUE_BYTES = 4096
MAX_PROVIDER_HINT_BYTES = 512


class RecordKind(str, Enum):
    CONTACT = "contact"
    IMMUTABLE = "immutable"
    PROVIDER = "provider"
    MUTABLE = "mutable"


@dataclass(frozen=True)
class ValidationResult:
    ok: bool
    code: str
    detail: str = ""


@dataclass(frozen=True)
class ImmutableRecord:
    namespace: str
    value: BValue
    publisher_node_id: bytes = b""
    expires_at: int | None = None

    @property
    def encoded_value(self) -> bytes:
        return bencode(self.value)

    @property
    def target(self) -> bytes:
        return content_target(self.namespace, self.encoded_value)

    @property
    def key_hex(self) -> str:
        return self.target.hex()

    def validate(self, *, now: int | None = None) -> ValidationResult:
        if len(self.encoded_value) > MAX_IMMUTABLE_VALUE_BYTES:
            return ValidationResult(False, "immutable_value_too_big")
        if self.expires_at is not None:
            if now is None:
                now = int(time.time())
            if now >= self.expires_at:
                return ValidationResult(False, "immutable_expired")
        return ValidationResult(True, "ok")


@dataclass(frozen=True)
class ProviderRecord:
    namespace: str
    content_key: bytes
    provider_node_id: bytes
    provider_public_key: bytes
    sequence: int
    expires_at: int
    hints: dict[str, str]
    signature: bytes = b""

    @property
    def target(self) -> bytes:
        return key_id("provider:" + self.namespace, self.content_key)

    @property
    def key_hex(self) -> str:
        return self.target.hex()

    def unsigned_payload(self) -> bytes:
        # Keep this bencoded and small so validation is cheap for storage nodes.
        return bencode({
            b"namespace": self.namespace.encode("utf-8"),
            b"content_key": self.content_key,
            b"provider_node_id": self.provider_node_id,
            b"sequence": self.sequence,
            b"expires_at": self.expires_at,
            b"hints": {key.encode("utf-8"): value.encode("utf-8") for key, value in self.hints.items()},
        })

    def signed(self, keypair: DhtKeypair) -> "ProviderRecord":
        if keypair.public_key_bytes != self.provider_public_key:
            raise ValueError("provider keypair does not match provider_public_key")
        return replace(self, signature=keypair.sign(self.unsigned_payload()))

    def validate(self, *, now: int | None = None) -> ValidationResult:
        if self.sequence < 0:
            return ValidationResult(False, "negative_sequence")
        if now is None:
            now = int(time.time())
        if now >= self.expires_at:
            return ValidationResult(False, "provider_expired")
        if len(self.unsigned_payload()) > MAX_PROVIDER_HINT_BYTES:
            return ValidationResult(False, "provider_payload_too_big")
        if not verify_signature(self.provider_public_key, self.unsigned_payload(), self.signature):
            return ValidationResult(False, "bad_provider_signature")
        return ValidationResult(True, "ok")


@dataclass
class RecordBook:
    immutable: dict[str, ImmutableRecord]
    providers: dict[str, list[ProviderRecord]]

    @classmethod
    def empty(cls) -> "RecordBook":
        return cls(immutable={}, providers={})

    def put_immutable(self, record: ImmutableRecord, *, now: int) -> ValidationResult:
        result = record.validate(now=now)
        if not result.ok:
            return result
        self.immutable[record.key_hex] = record
        return result

    def put_provider(self, record: ProviderRecord, *, now: int, max_per_key: int = 20) -> ValidationResult:
        result = record.validate(now=now)
        if not result.ok:
            return result
        bucket = self.providers.setdefault(record.key_hex, [])
        bucket = [old for old in bucket if old.provider_node_id != record.provider_node_id and old.expires_at > now]
        bucket.append(record)
        bucket.sort(key=lambda rec: rec.sequence, reverse=True)
        self.providers[record.key_hex] = bucket[:max_per_key]
        return result

    def get_providers(self, key_hex: str, *, now: int) -> list[ProviderRecord]:
        records = [record for record in self.providers.get(key_hex, []) if record.expires_at > now]
        self.providers[key_hex] = records
        return records
