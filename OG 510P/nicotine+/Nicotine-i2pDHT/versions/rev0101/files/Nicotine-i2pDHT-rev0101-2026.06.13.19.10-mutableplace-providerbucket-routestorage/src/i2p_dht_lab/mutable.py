"""BEP44/BEP46-inspired mutable DHT records for the I2P substrate DHT.

The DHT is not BitTorrent Mainline, but it should be born with the right mutable
primitive: Ed25519 public key, optional salt, monotonic sequence number, CAS,
small canonical value, expiry, and republish semantics. The record exposes two
targets: a 160-bit BEP44-compatible target for interoperability reasoning and a
native 256-bit target for the I2P substrate DHT.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, replace
from enum import Enum

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha1, sha256

MAX_VALUE_BYTES = 1000
MAX_SALT_BYTES = 64
MAX_SEQ = 0x7FFFFFFFFFFFFFFF
MUTABLE_TARGET_DOMAIN = DOMAIN + b":mutable-target-v1:"
DEFAULT_TTL_SECONDS = 2 * 60 * 60
DEFAULT_REPUBLISH_SECONDS = 45 * 60


class StoreCode(str, Enum):
    ACCEPTED_NEW = "accepted_new"
    ACCEPTED_UPDATE = "accepted_update"
    ACCEPTED_REFRESH = "accepted_refresh"
    REJECT_VALUE_TOO_BIG = "reject_205_value_too_big"
    REJECT_BAD_SIGNATURE = "reject_206_invalid_signature"
    REJECT_SALT_TOO_BIG = "reject_207_salt_too_big"
    REJECT_CAS_MISMATCH = "reject_301_cas_mismatch"
    REJECT_STALE_SEQUENCE = "reject_302_stale_sequence"
    REJECT_EQUAL_SEQUENCE_DIFFERENT_VALUE = "reject_equal_seq_different_value"
    REJECT_BAD_SEQUENCE = "reject_bad_sequence"
    REJECT_TARGET_MISMATCH = "reject_target_mismatch"


def _salt_prefix(salt: bytes) -> bytes:
    return b"" if not salt else b"4:salt" + str(len(salt)).encode("ascii") + b":" + salt


def signature_payload(*, seq: int, value: BValue, salt: bytes = b"") -> bytes:
    """Return the BEP44-style bytes signed by a mutable-record publisher."""
    if len(salt) > MAX_SALT_BYTES:
        raise ValueError("salt must be <= 64 bytes")
    if seq < 0 or seq > MAX_SEQ:
        raise ValueError("sequence must fit signed int64 and be non-negative")
    return _salt_prefix(salt) + b"3:seqi" + str(seq).encode("ascii") + b"e1:v" + bencode(value)


def target_id_bep44(public_key: bytes, salt: bytes = b"") -> bytes:
    """Return BEP44/BEP46's 160-bit target: SHA1(public_key || salt)."""
    if len(public_key) != 32:
        raise ValueError("public key must be 32 bytes")
    if len(salt) > MAX_SALT_BYTES:
        raise ValueError("salt must be <= 64 bytes")
    return sha1(public_key + salt)


def target_id_i2p256(public_key: bytes, salt: bytes = b"") -> bytes:
    """Return the native 256-bit target for a mutable slot."""
    if len(public_key) != 32:
        raise ValueError("public key must be 32 bytes")
    if len(salt) > MAX_SALT_BYTES:
        raise ValueError("salt must be <= 64 bytes")
    return sha256(MUTABLE_TARGET_DOMAIN + public_key + salt)


@dataclass(frozen=True)
class MutableRecord:
    public_key: bytes
    seq: int
    value: BValue
    signature: bytes
    salt: bytes = b""
    kind: str = "generic.mutable"
    expires_at: int | None = None

    @classmethod
    def create(
        cls,
        *,
        keypair: DhtKeypair,
        seq: int,
        value: BValue,
        salt: bytes = b"",
        kind: str = "generic.mutable",
        now: int | None = None,
        ttl: int = DEFAULT_TTL_SECONDS,
    ) -> "MutableRecord":
        encoded = bencode(value)
        if len(encoded) > MAX_VALUE_BYTES:
            raise ValueError("bencoded mutable value exceeds 1000 bytes")
        payload = signature_payload(seq=seq, value=value, salt=salt)
        if now is None:
            now = int(time.time())
        return cls(
            public_key=keypair.public_key_bytes,
            seq=seq,
            value=value,
            signature=keypair.sign(payload),
            salt=salt,
            kind=kind,
            expires_at=now + ttl,
        )

    @property
    def encoded_value(self) -> bytes:
        return bencode(self.value)

    @property
    def signing_payload(self) -> bytes:
        return signature_payload(seq=self.seq, value=self.value, salt=self.salt)

    @property
    def target_bep44(self) -> bytes:
        return target_id_bep44(self.public_key, self.salt)

    @property
    def target_i2p256(self) -> bytes:
        return target_id_i2p256(self.public_key, self.salt)

    @property
    def target_hex(self) -> str:
        return self.target_i2p256.hex()

    def verify(self) -> bool:
        return verify_signature(self.public_key, self.signing_payload, self.signature)

    def is_expired(self, now: int | None = None) -> bool:
        if self.expires_at is None:
            return False
        if now is None:
            now = int(time.time())
        return now >= self.expires_at

    def validate_for_store(self, *, target: bytes | None = None) -> StoreCode | None:
        if self.seq < 0 or self.seq > MAX_SEQ:
            return StoreCode.REJECT_BAD_SEQUENCE
        if len(self.salt) > MAX_SALT_BYTES:
            return StoreCode.REJECT_SALT_TOO_BIG
        if len(self.encoded_value) > MAX_VALUE_BYTES:
            return StoreCode.REJECT_VALUE_TOO_BIG
        if target is not None and target != self.target_i2p256:
            return StoreCode.REJECT_TARGET_MISMATCH
        if not self.verify():
            return StoreCode.REJECT_BAD_SIGNATURE
        return None

    def same_version_payload(self, other: "MutableRecord") -> bool:
        return (
            self.public_key == other.public_key
            and self.salt == other.salt
            and self.seq == other.seq
            and self.encoded_value == other.encoded_value
            and self.signature == other.signature
        )

    def refreshed(self, *, now: int, ttl: int = DEFAULT_TTL_SECONDS) -> "MutableRecord":
        return replace(self, expires_at=now + ttl)


@dataclass(frozen=True)
class StoreDecision:
    accepted: bool
    code: StoreCode
    previous_seq: int | None = None
    stored_seq: int | None = None


@dataclass
class MutableSlotStore:
    """Tiny local storage policy for BEP44-like mutable slots."""

    records: dict[str, MutableRecord]

    @classmethod
    def empty(cls) -> "MutableSlotStore":
        return cls(records={})

    def put(self, record: MutableRecord, *, now: int, cas: int | None = None) -> StoreDecision:
        failure = record.validate_for_store(target=record.target_i2p256)
        if failure is not None:
            return StoreDecision(False, failure)

        key = record.target_hex
        current = self.records.get(key)
        previous_seq = None if current is None else current.seq

        if cas is not None and current is not None and cas != current.seq:
            return StoreDecision(False, StoreCode.REJECT_CAS_MISMATCH, previous_seq=previous_seq)

        if current is None:
            self.records[key] = record.refreshed(now=now)
            return StoreDecision(True, StoreCode.ACCEPTED_NEW, stored_seq=record.seq)

        if record.seq < current.seq:
            return StoreDecision(False, StoreCode.REJECT_STALE_SEQUENCE, previous_seq=current.seq)

        if record.seq == current.seq:
            if record.same_version_payload(current):
                self.records[key] = current.refreshed(now=now)
                return StoreDecision(True, StoreCode.ACCEPTED_REFRESH, previous_seq=current.seq, stored_seq=current.seq)
            return StoreDecision(False, StoreCode.REJECT_EQUAL_SEQUENCE_DIFFERENT_VALUE, previous_seq=current.seq)

        self.records[key] = record.refreshed(now=now)
        return StoreDecision(True, StoreCode.ACCEPTED_UPDATE, previous_seq=current.seq, stored_seq=record.seq)

    def get(self, target_hex: str, *, now: int, seq_gt: int | None = None) -> MutableRecord | None:
        record = self.records.get(target_hex)
        if record is None or record.is_expired(now):
            return None
        if seq_gt is not None and record.seq <= seq_gt:
            return None
        return record


def make_bep46_value(info_hash: bytes) -> dict[bytes, bytes]:
    if len(info_hash) != 20:
        raise ValueError("BEP46 infohash must be 20 bytes")
    return {b"ih": info_hash}


def make_mutable_torrent_head(
    *,
    keypair: DhtKeypair,
    info_hash: bytes,
    seq: int,
    salt: bytes = b"",
    now: int | None = None,
) -> MutableRecord:
    return MutableRecord.create(
        keypair=keypair,
        seq=seq,
        value=make_bep46_value(info_hash),
        salt=salt,
        kind="bt.bep46.mutable_torrent_head",
        now=now,
    )


def mutable_magnet_btpk(public_key: bytes, salt: bytes = b"") -> str:
    if len(public_key) != 32:
        raise ValueError("public key must be 32 bytes")
    base = f"magnet:?xs=urn:btpk:{public_key.hex()}"
    if salt:
        return base + f"&s={salt.hex()}"
    return base
