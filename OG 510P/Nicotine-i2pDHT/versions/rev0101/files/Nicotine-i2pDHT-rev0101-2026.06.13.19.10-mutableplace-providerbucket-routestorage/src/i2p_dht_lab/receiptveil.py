"""Veiled garden contribution receipts.

Garden nodes need operator feedback and local receipts, but receipts can turn
into metadata leakage or accidental reputation if they contain raw keys,
unbounded labels, or globally comparable scores.  This module signs small local
receipts and then assesses a window for replay, same-sequence fork pressure,
family monoculture, budget overclaim, and raw-label leakage.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .servicecatalog import GardenServiceClass

RECEIPT_VEIL_DOMAIN = DOMAIN + b":receipt-veil-v1:"
HEX_KEY_RE = re.compile(r"\b[0-9a-fA-F]{40,64}\b")
B32_RE = re.compile(r"[a-z2-7]{20,}\.b32\.i2p", re.IGNORECASE)


class ReceiptDecisionKind(str, Enum):
    ACCEPT_VEILED_RECEIPTS = "accept_veiled_receipts"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_CONTRIBUTION_OVERCLAIM = "hold_contribution_overclaim"
    QUARANTINE_BAD_SIGNATURE_OR_TIME = "quarantine_bad_signature_or_time"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SAME_SEQ_FORK = "quarantine_same_seq_fork"
    QUARANTINE_RAW_LABEL = "quarantine_raw_label"
    QUARANTINE_SCOPE_MISMATCH = "quarantine_scope_mismatch"


@dataclass(frozen=True)
class ContributionReceipt:
    issuer_public_key: bytes
    issuer_node_id: bytes
    issuer_family: str
    service: GardenServiceClass
    scope_id: bytes
    window_id: bytes
    sequence: int
    served_units: int
    refused_units: int
    byte_units: int
    issued_at: int
    expires_at: int
    label: str = ""
    signature: bytes = b""

    def __post_init__(self) -> None:
        for name, value in (("issuer_public_key", self.issuer_public_key), ("issuer_node_id", self.issuer_node_id), ("scope_id", self.scope_id), ("window_id", self.window_id)):
            if len(value) != 32:
                raise ValueError(f"receipt {name} must be 32 bytes")
        if not self.issuer_family:
            raise ValueError("receipt needs issuer family")
        if min(self.sequence, self.served_units, self.refused_units, self.byte_units, self.issued_at, self.expires_at) < 0:
            raise ValueError("receipt counters must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("receipt expires_at must be after issued_at")
        if len(self.label.encode("utf-8")) > 96:
            raise ValueError("receipt label too long")

    @classmethod
    def create(
        cls,
        *,
        keypair: DhtKeypair,
        issuer_node_id: bytes,
        issuer_family: str,
        service: GardenServiceClass,
        scope_id: bytes,
        window_id: bytes,
        sequence: int,
        served_units: int,
        refused_units: int,
        byte_units: int,
        issued_at: int,
        ttl: int,
        label: str = "",
    ) -> "ContributionReceipt":
        unsigned = cls(
            issuer_public_key=keypair.public_key_bytes,
            issuer_node_id=issuer_node_id,
            issuer_family=issuer_family,
            service=service,
            scope_id=scope_id,
            window_id=window_id,
            sequence=sequence,
            served_units=served_units,
            refused_units=refused_units,
            byte_units=byte_units,
            issued_at=issued_at,
            expires_at=issued_at + ttl,
            label=label,
        )
        return replace(unsigned, signature=keypair.sign(unsigned.unsigned_payload()))

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"issuer_public_key": self.issuer_public_key,
            b"issuer_node_id": self.issuer_node_id,
            b"issuer_family": self.issuer_family,
            b"service": self.service.value,
            b"scope": self.scope_id,
            b"window": self.window_id,
            b"sequence": self.sequence,
            b"served": self.served_units,
            b"refused": self.refused_units,
            b"bytes": self.byte_units,
            b"issued_at": self.issued_at,
            b"expires_at": self.expires_at,
            b"label": self.label,
        }

    def unsigned_payload(self) -> bytes:
        return RECEIPT_VEIL_DOMAIN + b":receipt:" + bencode(self.bvalue())

    @property
    def receipt_digest(self) -> bytes:
        return sha256(self.unsigned_payload() + self.signature)

    @property
    def issuer_sequence_key(self) -> tuple[bytes, int]:
        return (self.issuer_public_key, self.sequence)

    def verify(self, *, now: int) -> bool:
        return self.issued_at <= now < self.expires_at and verify_signature(self.issuer_public_key, self.unsigned_payload(), self.signature)


@dataclass(frozen=True)
class ReceiptVeilPolicy:
    min_families: int = 2
    max_family_fraction_ppm: int = 700_000
    max_served_units: int = 10_000
    max_refusal_ratio_ppm: int = 900_000

    def validate(self) -> None:
        if self.min_families <= 0 or not 0 <= self.max_family_fraction_ppm <= 1_000_000:
            raise ValueError("receipt family policy invalid")
        if self.max_served_units < 0 or not 0 <= self.max_refusal_ratio_ppm <= 1_000_000:
            raise ValueError("receipt unit policy invalid")


@dataclass(frozen=True)
class ReceiptVeilReport:
    decision_kind: ReceiptDecisionKind
    accept: bool
    reason: str
    scope_id: bytes
    accepted_receipt_digests: tuple[bytes, ...]
    pressure_digests: tuple[bytes, ...]
    veiled_service_totals: tuple[tuple[str, int, int], ...]
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _raw_label(label: str) -> bool:
    return bool(label and (HEX_KEY_RE.search(label) or B32_RE.search(label) or "destination=" in label.lower()))


def _report(kind: ReceiptDecisionKind, accept: bool, reason: str, *, scope_id: bytes, receipts: Iterable[ContributionReceipt] = (), pressures: Iterable[bytes] = ()) -> ReceiptVeilReport:
    receipt_tuple = tuple(receipts)
    totals: dict[str, list[int]] = {}
    for receipt in receipt_tuple:
        pair = totals.setdefault(receipt.service.value, [0, 0])
        pair[0] += receipt.served_units
        pair[1] += receipt.refused_units
    totals_tuple = tuple(sorted((service, served, refused) for service, (served, refused) in totals.items()))
    accepted = tuple(sorted(receipt.receipt_digest for receipt in receipt_tuple))
    pressure_t = tuple(sorted(set(pressures)))
    digest = sha256(RECEIPT_VEIL_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"reason": reason,
        b"scope": scope_id,
        b"accepted": list(accepted),
        b"pressures": list(pressure_t),
        b"totals": [[service, served, refused] for service, served, refused in totals_tuple],
    }))
    return ReceiptVeilReport(kind, accept, reason, scope_id, accepted, pressure_t, totals_tuple, digest)


def assess_receipt_window(
    receipts: Iterable[ContributionReceipt],
    *,
    now: int,
    expected_scope_id: bytes,
    previously_seen_receipts: Iterable[bytes] = (),
    known_sequence_digests: dict[tuple[bytes, int], bytes] | None = None,
    policy: ReceiptVeilPolicy | None = None,
) -> ReceiptVeilReport:
    """Assess receipts as local diagnostics, not reputation or currency."""
    policy = policy or ReceiptVeilPolicy()
    policy.validate()
    receipt_tuple = tuple(receipts)
    seen_digests = set(previously_seen_receipts)
    known = dict(known_sequence_digests or {})
    if not receipt_tuple:
        return _report(ReceiptDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, "empty receipt window", scope_id=expected_scope_id)
    for receipt in receipt_tuple:
        if receipt.scope_id != expected_scope_id:
            return _report(ReceiptDecisionKind.QUARANTINE_SCOPE_MISMATCH, False, "receipt scope does not match expected scope", scope_id=expected_scope_id, pressures=(receipt.receipt_digest, receipt.scope_id))
        if not receipt.verify(now=now):
            return _report(ReceiptDecisionKind.QUARANTINE_BAD_SIGNATURE_OR_TIME, False, "receipt signature or time window invalid", scope_id=expected_scope_id, pressures=(receipt.receipt_digest,))
        if receipt.receipt_digest in seen_digests:
            return _report(ReceiptDecisionKind.QUARANTINE_REPLAY, False, "receipt digest replayed", scope_id=expected_scope_id, pressures=(receipt.receipt_digest,))
        prior = known.get(receipt.issuer_sequence_key)
        if prior is not None and prior != receipt.receipt_digest:
            return _report(ReceiptDecisionKind.QUARANTINE_SAME_SEQ_FORK, False, "issuer emitted same-sequence receipt fork", scope_id=expected_scope_id, pressures=(prior, receipt.receipt_digest))
        if _raw_label(receipt.label):
            return _report(ReceiptDecisionKind.QUARANTINE_RAW_LABEL, False, "receipt label contains raw key or destination-looking material", scope_id=expected_scope_id, pressures=(receipt.receipt_digest,))
    families: dict[str, int] = {}
    served_total = 0
    refused_total = 0
    for receipt in receipt_tuple:
        families[receipt.issuer_family] = families.get(receipt.issuer_family, 0) + 1
        served_total += receipt.served_units
        refused_total += receipt.refused_units
    if len(families) < policy.min_families:
        return _report(ReceiptDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, "receipt window lacks family diversity", scope_id=expected_scope_id, receipts=receipt_tuple, pressures=(receipt_tuple[0].receipt_digest,))
    max_fraction = max(families.values()) * 1_000_000 // len(receipt_tuple)
    if max_fraction > policy.max_family_fraction_ppm:
        return _report(ReceiptDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, "one receipt family dominates the window", scope_id=expected_scope_id, receipts=receipt_tuple, pressures=[r.receipt_digest for r in receipt_tuple])
    if served_total > policy.max_served_units:
        return _report(ReceiptDecisionKind.HOLD_CONTRIBUTION_OVERCLAIM, False, "receipt window overclaims served units", scope_id=expected_scope_id, receipts=receipt_tuple, pressures=[r.receipt_digest for r in receipt_tuple])
    total = served_total + refused_total
    if total and refused_total * 1_000_000 // total > policy.max_refusal_ratio_ppm:
        return _report(ReceiptDecisionKind.HOLD_CONTRIBUTION_OVERCLAIM, False, "receipt window is refusal-heavy enough to require watch", scope_id=expected_scope_id, receipts=receipt_tuple, pressures=[r.receipt_digest for r in receipt_tuple])
    return _report(ReceiptDecisionKind.ACCEPT_VEILED_RECEIPTS, True, "receipts are fresh, scoped, diverse, and locally veiled", scope_id=expected_scope_id, receipts=receipt_tuple)
