"""Region-ledger receipts for garden sweep scheduling.

Region ledgers decide what should be reannounced; garden schedulers decide what
fits.  The hard join is accountability without authority: a garden should leave
small signed receipts for accepted/refused region work, but those receipts must
not become proof that a provider record is true.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum

from .bencode import BValue, bencode
from .gardenrefusal import GardenAdmissionKind, GardenWorkKind, GardenWorkRequest, UsefulRefusalReceipt
from .gardenscheduler import GardenScheduleReport, plan_garden_schedule
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .regionledger import RegionLedgerBatch, RegionLedgerReport

REGION_RECEIPT_DOMAIN = DOMAIN + b":region-receipt-v1:"


class RegionReceiptDecisionKind(str, Enum):
    ACCEPTED = "accepted"
    REFUSED_USEFULLY = "refused_usefully"
    DROPPED = "dropped"


@dataclass(frozen=True)
class RegionSweepReceipt:
    garden_node_id: bytes
    garden_public_key: bytes
    region: int
    batch_digest: bytes
    request_digest: bytes
    decision: RegionReceiptDecisionKind
    advertisement_count: int
    tombstone_count: int
    total_weight: int
    issued_at: int
    refusal_receipt_hash: bytes = b""
    signature: bytes = b""

    @classmethod
    def create(
        cls,
        *,
        garden_keypair: DhtKeypair,
        garden_node_id: bytes,
        batch: RegionLedgerBatch,
        request: GardenWorkRequest,
        decision: RegionReceiptDecisionKind,
        issued_at: int,
        refusal_receipt: UsefulRefusalReceipt | None = None,
    ) -> "RegionSweepReceipt":
        unsigned = cls(
            garden_node_id=garden_node_id,
            garden_public_key=garden_keypair.public_key_bytes,
            region=batch.region,
            batch_digest=batch_digest(batch),
            request_digest=request.digest,
            decision=decision,
            advertisement_count=len(batch.advertisements),
            tombstone_count=len(batch.tombstones),
            total_weight=batch.total_weight,
            issued_at=issued_at,
            refusal_receipt_hash=b"" if refusal_receipt is None else sha256(refusal_receipt.unsigned_payload() + refusal_receipt.signature),
        )
        return replace(unsigned, signature=garden_keypair.sign(unsigned.unsigned_payload()))

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"garden_node_id": self.garden_node_id,
            b"garden_public_key": self.garden_public_key,
            b"region": self.region,
            b"batch_digest": self.batch_digest,
            b"request_digest": self.request_digest,
            b"decision": self.decision.value,
            b"advertisement_count": self.advertisement_count,
            b"tombstone_count": self.tombstone_count,
            b"total_weight": self.total_weight,
            b"issued_at": self.issued_at,
            b"refusal_receipt_hash": self.refusal_receipt_hash,
        }

    def unsigned_payload(self) -> bytes:
        return REGION_RECEIPT_DOMAIN + b":receipt:" + bencode(self.bvalue())

    @property
    def receipt_hash(self) -> bytes:
        return sha256(self.unsigned_payload() + self.signature)

    def verify(self, *, expected_garden_public_key: bytes | None = None) -> bool:
        if len(self.garden_node_id) != 32 or len(self.garden_public_key) != 32 or len(self.signature) != 64:
            return False
        if expected_garden_public_key is not None and self.garden_public_key != expected_garden_public_key:
            return False
        if self.advertisement_count < 0 or self.tombstone_count < 0 or self.total_weight < 0:
            return False
        return verify_signature(self.garden_public_key, self.unsigned_payload(), self.signature)


@dataclass(frozen=True)
class RegionReceiptBridgeReport:
    ledger_digest: bytes
    schedule_digest: bytes
    request_count: int
    receipts: tuple[RegionSweepReceipt, ...]
    accepted_count: int
    refused_count: int
    dropped_count: int
    transcript_digest: bytes

    @property
    def all_receipts_verify(self) -> bool:
        return all(receipt.verify() for receipt in self.receipts)


def batch_digest(batch: RegionLedgerBatch) -> bytes:
    return sha256(REGION_RECEIPT_DOMAIN + b":batch:" + bencode(batch.bvalue()))


def request_from_region_batch(batch: RegionLedgerBatch, *, requester_node_id: bytes, family_id: str, issued_at: int, ttl: int = 10 * 60) -> GardenWorkRequest:
    return GardenWorkRequest(
        requester_node_id=requester_node_id,
        family_id=family_id,
        kind=GardenWorkKind.REGION_REPROVIDE,
        target=batch_digest(batch),
        issued_at=issued_at,
        ttl=ttl,
        stream_cost=1,
        provider_record_cost=sum(item.weight for item in batch.advertisements),
        mutable_watch_cost=len(batch.tombstones),
        priority_bonus=10 if batch.tombstones else 0,
        note=f"region={batch.region};adverts={len(batch.advertisements)};tombs={len(batch.tombstones)}",
    )


def bridge_region_ledger_to_garden_schedule(
    ledger_report: RegionLedgerReport,
    *,
    garden_keypair: DhtKeypair,
    garden_node_id: bytes,
    requester_node_id: bytes,
    requester_family: str,
    start_at: int,
    schedule_kwargs: dict | None = None,
) -> RegionReceiptBridgeReport:
    requests = tuple(request_from_region_batch(batch, requester_node_id=requester_node_id, family_id=requester_family, issued_at=start_at) for batch in ledger_report.batches)
    schedule = plan_garden_schedule(requests, garden_keypair=garden_keypair, garden_node_id=garden_node_id, start_at=start_at, **(schedule_kwargs or {}))
    batch_by_request = {request.digest: batch for batch, request in zip(ledger_report.batches, requests)}
    receipts: list[RegionSweepReceipt] = []
    for window in schedule.windows:
        for admission in window.batch.decisions:
            batch = batch_by_request.get(admission.request.digest)
            if batch is None:
                continue
            if admission.kind is GardenAdmissionKind.ACCEPTED:
                kind = RegionReceiptDecisionKind.ACCEPTED
            elif admission.kind is GardenAdmissionKind.REFUSED_USEFULLY:
                kind = RegionReceiptDecisionKind.REFUSED_USEFULLY
            else:
                kind = RegionReceiptDecisionKind.DROPPED
            receipts.append(RegionSweepReceipt.create(
                garden_keypair=garden_keypair,
                garden_node_id=garden_node_id,
                batch=batch,
                request=admission.request,
                decision=kind,
                issued_at=window.starts_at,
                refusal_receipt=admission.receipt,
            ))
    transcript_digest = sha256(REGION_RECEIPT_DOMAIN + b":bridge:" + ledger_report.transcript_digest + schedule.transcript_digest + b"".join(receipt.receipt_hash for receipt in receipts))
    return RegionReceiptBridgeReport(
        ledger_digest=ledger_report.transcript_digest,
        schedule_digest=schedule.transcript_digest,
        request_count=len(requests),
        receipts=tuple(receipts),
        accepted_count=sum(1 for receipt in receipts if receipt.decision is RegionReceiptDecisionKind.ACCEPTED),
        refused_count=sum(1 for receipt in receipts if receipt.decision is RegionReceiptDecisionKind.REFUSED_USEFULLY),
        dropped_count=sum(1 for receipt in receipts if receipt.decision is RegionReceiptDecisionKind.DROPPED),
        transcript_digest=transcript_digest,
    )
