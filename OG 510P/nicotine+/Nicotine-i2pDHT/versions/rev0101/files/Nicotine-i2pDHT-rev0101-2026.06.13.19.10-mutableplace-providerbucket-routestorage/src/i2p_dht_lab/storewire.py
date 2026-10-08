"""STORE/custody wire fixtures tied to exact-digest contracts.

``wirecanon.py`` made signed transport-neutral frames.  This module adds one
layer of semantic pressure: a STORE request, STORE receipt, custody challenge,
and custody proof should not merely be signed frames.  Their payload digests
must bind to the exact store/custody object they claim to carry, and the frame
kind/flags should match the object role.

No live SAM/I2P transport is implemented here.  The purpose is to make STORE
wire transcripts deterministic and auditable before network noise exists.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .custodyaudit import CustodyAuditChallenge, CustodyProof
from .identity import DhtKeypair
from .ids import DOMAIN, sha256
from .storecontract import StoreContractReceipt, StoreContractRequest
from .wirecanon import WireFrame, WireMessageKind, WireValidation, WireValidationKind, build_wire_transcript, validate_wire_frame

STORE_WIRE_DOMAIN = DOMAIN + b":store-wire-v1:"


class StoreWirePayloadKind(str, Enum):
    STORE_REQUEST = "store_request"
    STORE_RECEIPT = "store_receipt"
    CUSTODY_CHALLENGE = "custody_challenge"
    CUSTODY_PROOF = "custody_proof"


class StoreWireDecisionKind(str, Enum):
    ACCEPT_STORE_WIRE_TRANSCRIPT = "accept_store_wire_transcript"
    CONTINUE_MISSING_REQUIRED_ROLES = "continue_missing_required_roles"
    QUARANTINE_WIRE_VALIDATION = "quarantine_wire_validation"
    QUARANTINE_ROLE_MISMATCH = "quarantine_role_mismatch"
    QUARANTINE_STORE_DIGEST_MISMATCH = "quarantine_store_digest_mismatch"


@dataclass(frozen=True)
class StoreWirePayload:
    kind: StoreWirePayloadKind
    object_digest: bytes
    body: bytes

    def __post_init__(self) -> None:
        if len(self.object_digest) != 32:
            raise ValueError("store wire payload object_digest must be 32 bytes")
        if not self.body:
            raise ValueError("store wire payload body must not be empty")

    @property
    def payload_digest(self) -> bytes:
        return sha256(STORE_WIRE_DOMAIN + b":payload:" + self.kind.value.encode("utf-8") + self.object_digest + self.body)

    def bvalue(self) -> dict[bytes, BValue]:
        return {b"kind": self.kind.value, b"object_digest": self.object_digest, b"body": self.body}

    def to_bytes(self) -> bytes:
        return STORE_WIRE_DOMAIN + b":wire-payload:" + bencode(self.bvalue())


@dataclass(frozen=True)
class StoreWireFrame:
    payload: StoreWirePayload
    frame: WireFrame


@dataclass(frozen=True)
class StoreWireDecision:
    kind: StoreWireDecisionKind
    accept: bool
    reason: str


@dataclass(frozen=True)
class StoreWireTranscriptReport:
    frames: tuple[StoreWireFrame, ...]
    validations: tuple[WireValidation, ...]
    role_counts: dict[StoreWirePayloadKind, int]
    decision: StoreWireDecision
    transcript_digest: bytes

    @property
    def accepted_frame_count(self) -> int:
        return sum(1 for item in self.validations if item.accept)


def payload_from_request(request: StoreContractRequest) -> StoreWirePayload:
    body = bencode(request.bvalue())
    return StoreWirePayload(StoreWirePayloadKind.STORE_REQUEST, request.request_hash, body)


def payload_from_receipt(receipt: StoreContractReceipt) -> StoreWirePayload:
    body = bencode(receipt.bvalue_unsigned() | {b"signature": receipt.signature})
    return StoreWirePayload(StoreWirePayloadKind.STORE_RECEIPT, receipt.receipt_hash, body)


def payload_from_challenge(challenge: CustodyAuditChallenge) -> StoreWirePayload:
    body = bencode(challenge.bvalue())
    return StoreWirePayload(StoreWirePayloadKind.CUSTODY_CHALLENGE, challenge.challenge_hash, body)


def payload_from_proof(proof: CustodyProof) -> StoreWirePayload:
    body = bencode(proof.bvalue_unsigned() | {b"signature": proof.signature})
    return StoreWirePayload(StoreWirePayloadKind.CUSTODY_PROOF, proof.proof_hash, body)


def make_store_wire_frame(
    *,
    keypair: DhtKeypair,
    sender_node_id: bytes,
    request_id: bytes,
    payload: StoreWirePayload,
    issued_at: int,
    ttl: int = 300,
    sequence: int = 0,
) -> StoreWireFrame:
    if payload.kind in {StoreWirePayloadKind.STORE_REQUEST, StoreWirePayloadKind.STORE_RECEIPT}:
        message_kind = WireMessageKind.STORE_RECORD
    elif payload.kind is StoreWirePayloadKind.CUSTODY_CHALLENGE:
        message_kind = WireMessageKind.CUSTODY_CHALLENGE
    else:
        message_kind = WireMessageKind.CUSTODY_PROOF
    frame = WireFrame.create(
        keypair=keypair,
        sender_node_id=sender_node_id,
        message_kind=message_kind,
        request_id=request_id,
        payload=payload.to_bytes(),
        issued_at=issued_at,
        ttl=ttl,
        sequence=sequence,
        flags=("storewire", payload.kind.value),
    )
    return StoreWireFrame(payload, frame)


def _role_matches(item: StoreWireFrame) -> bool:
    if item.payload.kind in {StoreWirePayloadKind.STORE_REQUEST, StoreWirePayloadKind.STORE_RECEIPT}:
        return item.frame.message_kind is WireMessageKind.STORE_RECORD
    if item.payload.kind is StoreWirePayloadKind.CUSTODY_CHALLENGE:
        return item.frame.message_kind is WireMessageKind.CUSTODY_CHALLENGE
    if item.payload.kind is StoreWirePayloadKind.CUSTODY_PROOF:
        return item.frame.message_kind is WireMessageKind.CUSTODY_PROOF
    return False


def analyze_store_wire_transcript(frames: Iterable[StoreWireFrame], *, now: int, require_full_cycle: bool = True) -> StoreWireTranscriptReport:
    frame_tuple = tuple(frames)
    validations = tuple(validate_wire_frame(item.frame, payload=item.payload.to_bytes(), now=now) for item in frame_tuple)
    role_counts: dict[StoreWirePayloadKind, int] = {}
    for item in frame_tuple:
        role_counts[item.payload.kind] = role_counts.get(item.payload.kind, 0) + 1

    digest = build_wire_transcript(((item.frame, item.payload.to_bytes()) for item in frame_tuple), now=now).transcript_digest

    if any(not validation.accept for validation in validations):
        decision = StoreWireDecision(StoreWireDecisionKind.QUARANTINE_WIRE_VALIDATION, False, "one or more STORE wire frames failed canonical validation")
    elif any(not _role_matches(item) for item in frame_tuple):
        decision = StoreWireDecision(StoreWireDecisionKind.QUARANTINE_ROLE_MISMATCH, False, "frame kind does not match payload role")
    elif any(item.payload.payload_digest != sha256(STORE_WIRE_DOMAIN + b":payload:" + item.payload.kind.value.encode("utf-8") + item.payload.object_digest + item.payload.body) for item in frame_tuple):
        decision = StoreWireDecision(StoreWireDecisionKind.QUARANTINE_STORE_DIGEST_MISMATCH, False, "payload digest does not match its store-wire body")
    elif require_full_cycle and any(role_counts.get(kind, 0) <= 0 for kind in StoreWirePayloadKind):
        decision = StoreWireDecision(StoreWireDecisionKind.CONTINUE_MISSING_REQUIRED_ROLES, False, "STORE wire transcript lacks request/receipt/challenge/proof cycle")
    else:
        decision = StoreWireDecision(StoreWireDecisionKind.ACCEPT_STORE_WIRE_TRANSCRIPT, True, "STORE/custody wire transcript is canonical and role-complete")

    return StoreWireTranscriptReport(frame_tuple, validations, role_counts, decision, digest)
