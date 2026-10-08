"""Ingress drain boundary for public-bridge work admitted from outside.

Outbound publication work has dry-run/outbox/drain/canary lanes.  A public bridge
also has the mirror-image risk: inbound requests that entered through a public
service announcement must be drained into handler work without replay, metadata
budget drift, refusal laundering, or component misbinding.

This is still a no-network toy surface.  It intentionally joins generic report
objects by digest so the risky algebra can be tested before real service code is
wired in.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Any, Iterable

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST

INGRESS_DRAIN_DOMAIN = DOMAIN + b":ingress-drain-v1:"


class IngressDrainPhase(str, Enum):
    ACCEPT_WORK = "accept_work"
    USEFUL_REFUSAL = "useful_refusal"
    COMPLETE_WORK = "complete_work"


class IngressDrainDecisionKind(str, Enum):
    ACCEPT_INGRESS_DRAIN = "accept_ingress_drain"
    ACCEPT_WITH_USEFUL_REFUSAL_PRESSURE = "accept_with_useful_refusal_pressure"
    HOLD_INGRESS_GATE = "hold_ingress_gate"
    HOLD_SERVICE_TICKET = "hold_service_ticket"
    HOLD_LOAD_SHEATH = "hold_load_sheath"
    HOLD_CONTINUITY = "hold_continuity"
    HOLD_COMPONENT_WATCH = "hold_component_watch"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    HOLD_REFUSAL_ONLY_LOOP = "hold_refusal_only_loop"
    EMPTY_NO_RECEIPTS = "empty_no_receipts"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_EXPIRED_OR_FUTURE = "quarantine_expired_or_future"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_PROFILE_DRIFT = "quarantine_profile_drift"
    QUARANTINE_SERVICE_DRIFT = "quarantine_service_drift"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_REQUEST_DRIFT = "quarantine_request_drift"
    QUARANTINE_CALLER_DRIFT = "quarantine_caller_drift"
    QUARANTINE_HANDLER_DRIFT = "quarantine_handler_drift"
    QUARANTINE_COMPONENT_DIGEST_DRIFT = "quarantine_component_digest_drift"
    QUARANTINE_METADATA_BUDGET = "quarantine_metadata_budget"
    QUARANTINE_PHASE_REGRESSION = "quarantine_phase_regression"
    QUARANTINE_COMPLETION_AFTER_REFUSAL = "quarantine_completion_after_refusal"


PHASE_ORDER = {
    IngressDrainPhase.ACCEPT_WORK: 0,
    IngressDrainPhase.USEFUL_REFUSAL: 1,
    IngressDrainPhase.COMPLETE_WORK: 2,
}


@dataclass(frozen=True)
class IngressDrainReceipt:
    phase: IngressDrainPhase
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    caller_digest: bytes
    handler_digest: bytes
    ingress_gate_digest: bytes
    service_ticket_digest: bytes
    load_sheath_digest: bytes
    continuity_digest: bytes
    ingress_request_digest: bytes
    metadata_units: int
    refusal_reason_digest: bytes
    sequence: int
    previous_receipt_digest: bytes
    issued_at: int
    expires_at: int
    family_id: str
    path_family: str
    signer_public_key: bytes
    signature: bytes = b""

    def __post_init__(self) -> None:
        object.__setattr__(self, "phase", IngressDrainPhase(self.phase))
        if not self.profile_id or not self.service_name or not self.family_id or not self.path_family:
            raise ValueError("ingress drain receipt needs profile/service/family/path")
        if self.sequence < 0 or self.metadata_units < 0:
            raise ValueError("sequence and metadata_units must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("expires_at must follow issued_at")
        for name, value in (
            ("scope_digest", self.scope_digest),
            ("request_digest", self.request_digest),
            ("caller_digest", self.caller_digest),
            ("handler_digest", self.handler_digest),
            ("ingress_gate_digest", self.ingress_gate_digest),
            ("service_ticket_digest", self.service_ticket_digest),
            ("load_sheath_digest", self.load_sheath_digest),
            ("continuity_digest", self.continuity_digest),
            ("ingress_request_digest", self.ingress_request_digest),
            ("refusal_reason_digest", self.refusal_reason_digest),
            ("previous_receipt_digest", self.previous_receipt_digest),
            ("signer_public_key", self.signer_public_key),
        ):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if self.signature and len(self.signature) != 64:
            raise ValueError("signature must be empty or Ed25519-sized")

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"phase": self.phase.value,
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"caller": self.caller_digest,
            b"handler": self.handler_digest,
            b"ingress_gate": self.ingress_gate_digest,
            b"ticket": self.service_ticket_digest,
            b"load": self.load_sheath_digest,
            b"continuity": self.continuity_digest,
            b"ingress_request": self.ingress_request_digest,
            b"metadata_units": self.metadata_units,
            b"refusal_reason": self.refusal_reason_digest,
            b"seq": self.sequence,
            b"prev": self.previous_receipt_digest,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"family": self.family_id,
            b"path_family": self.path_family,
            b"signer": self.signer_public_key,
        }

    def signature_payload(self) -> bytes:
        return INGRESS_DRAIN_DOMAIN + b":receipt-sig:" + bencode(self.unsigned_bvalue())

    @property
    def receipt_core_digest(self) -> bytes:
        return sha256(INGRESS_DRAIN_DOMAIN + b":receipt-core:" + bencode(self.unsigned_bvalue()))

    @property
    def receipt_digest(self) -> bytes:
        return sha256(INGRESS_DRAIN_DOMAIN + b":receipt-digest:" + self.signature_payload() + self.signature)

    def verifies(self) -> bool:
        return verify_signature(self.signer_public_key, self.signature_payload(), self.signature)

    def live(self, now: int) -> bool:
        return self.issued_at <= now < self.expires_at


@dataclass(frozen=True)
class IngressDrainReport:
    decision_kind: IngressDrainDecisionKind
    accept: bool
    watch: bool
    reason: str
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    caller_digest: bytes
    handler_digest: bytes
    accepted_receipt_digest: bytes
    receipt_digests: tuple[bytes, ...]
    component_digests: tuple[bytes, ...]
    metadata_units: int
    family_count: int
    path_family_count: int
    highest_sequence: int
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _component_digest(report: Any) -> bytes:
    for attr in ("report_digest", "transcript_digest", "ticket_digest"):
        value = getattr(report, attr, None)
        if isinstance(value, bytes) and len(value) == 32:
            return value
    raise ValueError("component report lacks 32-byte digest")


def _component_accept(report: Any) -> bool:
    return bool(getattr(report, "accept", False))


def _component_watch(report: Any) -> bool:
    return bool(getattr(report, "watch", False))


def _component_quarantined(report: Any) -> bool:
    return bool(getattr(report, "quarantined", False))


def make_ingress_drain_receipt(
    *,
    keypair: DhtKeypair,
    phase: IngressDrainPhase,
    profile_id: str,
    service_name: str,
    scope_digest: bytes,
    request_digest: bytes,
    caller_digest: bytes,
    handler_digest: bytes,
    ingress_gate_digest: bytes,
    service_ticket_digest: bytes,
    load_sheath_digest: bytes,
    continuity_digest: bytes,
    ingress_request_digest: bytes,
    metadata_units: int,
    refusal_reason_digest: bytes = ZERO_DIGEST,
    sequence: int,
    previous_receipt_digest: bytes = ZERO_DIGEST,
    issued_at: int = 0,
    expires_at: int = 1,
    family_id: str = "family-default",
    path_family: str = "path-default",
) -> IngressDrainReceipt:
    unsigned = IngressDrainReceipt(
        phase=phase,
        profile_id=profile_id,
        service_name=service_name,
        scope_digest=scope_digest,
        request_digest=request_digest,
        caller_digest=caller_digest,
        handler_digest=handler_digest,
        ingress_gate_digest=ingress_gate_digest,
        service_ticket_digest=service_ticket_digest,
        load_sheath_digest=load_sheath_digest,
        continuity_digest=continuity_digest,
        ingress_request_digest=ingress_request_digest,
        metadata_units=metadata_units,
        refusal_reason_digest=refusal_reason_digest,
        sequence=sequence,
        previous_receipt_digest=previous_receipt_digest,
        issued_at=issued_at,
        expires_at=expires_at,
        family_id=family_id,
        path_family=path_family,
        signer_public_key=keypair.public_key_bytes,
    )
    return replace(unsigned, signature=keypair.sign(unsigned.signature_payload()))


def _report(
    kind: IngressDrainDecisionKind,
    accept: bool,
    watch: bool,
    reason: str,
    *,
    expected_profile_id: str,
    expected_service_name: str,
    expected_scope_digest: bytes,
    expected_request_digest: bytes,
    expected_caller_digest: bytes,
    expected_handler_digest: bytes,
    accepted: IngressDrainReceipt | None = None,
    receipts: Iterable[IngressDrainReceipt] = (),
    components: Iterable[bytes] = (),
) -> IngressDrainReport:
    receipt_t = tuple(receipts)
    receipt_digests = tuple(receipt.receipt_digest for receipt in receipt_t)
    families = {receipt.family_id for receipt in receipt_t}
    paths = {receipt.path_family for receipt in receipt_t}
    metadata_units = sum(receipt.metadata_units for receipt in receipt_t)
    highest = max((receipt.sequence for receipt in receipt_t), default=-1)
    accepted_digest = accepted.receipt_digest if accepted else ZERO_DIGEST
    component_t = tuple(components)
    digest = sha256(INGRESS_DRAIN_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"reason": reason,
        b"profile": expected_profile_id,
        b"service": expected_service_name,
        b"scope": expected_scope_digest,
        b"request": expected_request_digest,
        b"caller": expected_caller_digest,
        b"handler": expected_handler_digest,
        b"accepted": accepted_digest,
        b"receipts": list(receipt_digests),
        b"components": list(component_t),
        b"metadata_units": metadata_units,
        b"families": len(families),
        b"paths": len(paths),
        b"highest": highest,
    }))
    return IngressDrainReport(kind, accept, watch, reason, expected_profile_id, expected_service_name, expected_scope_digest, expected_request_digest, expected_caller_digest, expected_handler_digest, accepted_digest, receipt_digests, component_t, metadata_units, len(families), len(paths), highest, digest)


def assess_ingress_drain(
    receipts: Iterable[IngressDrainReceipt],
    *,
    ingress_gate_report: Any,
    service_ticket_report: Any,
    load_sheath_report: Any,
    continuity_report: Any,
    now: int,
    expected_profile_id: str,
    expected_service_name: str,
    expected_scope_digest: bytes,
    expected_request_digest: bytes,
    expected_caller_digest: bytes,
    expected_handler_digest: bytes,
    expected_ingress_request_digest: bytes,
    max_metadata_units: int,
    previous_seen_receipt_digests: Iterable[bytes] = (),
    highest_seen_sequence: int | None = None,
    previous_refusal_streak: int = 0,
    max_refusal_streak: int = 2,
    min_family_count: int = 2,
    min_path_family_count: int = 2,
    allow_component_watch: bool = False,
) -> IngressDrainReport:
    recs = tuple(receipts)
    component_digests = (_component_digest(ingress_gate_report), _component_digest(service_ticket_report), _component_digest(load_sheath_report), _component_digest(continuity_report))
    common = dict(
        expected_profile_id=expected_profile_id,
        expected_service_name=expected_service_name,
        expected_scope_digest=expected_scope_digest,
        expected_request_digest=expected_request_digest,
        expected_caller_digest=expected_caller_digest,
        expected_handler_digest=expected_handler_digest,
        receipts=recs,
        components=component_digests,
    )
    if not recs:
        return _report(IngressDrainDecisionKind.EMPTY_NO_RECEIPTS, False, False, "ingress drain needs receipts", **common)
    component_kinds = (
        (ingress_gate_report, IngressDrainDecisionKind.HOLD_INGRESS_GATE),
        (service_ticket_report, IngressDrainDecisionKind.HOLD_SERVICE_TICKET),
        (load_sheath_report, IngressDrainDecisionKind.HOLD_LOAD_SHEATH),
        (continuity_report, IngressDrainDecisionKind.HOLD_CONTINUITY),
    )
    for component, hold_kind in component_kinds:
        if not _component_accept(component) or _component_quarantined(component):
            return _report(hold_kind if not _component_quarantined(component) else IngressDrainDecisionKind.QUARANTINE_COMPONENT_DIGEST_DRIFT, False, False, "ingress drain requires accepted component reports", **common)
    if any(_component_watch(component) for component, _ in component_kinds) and not allow_component_watch:
        return _report(IngressDrainDecisionKind.HOLD_COMPONENT_WATCH, False, True, "component watch pressure must be carried explicitly", **common)

    seen = set(previous_seen_receipt_digests)
    by_sequence: dict[int, IngressDrainReceipt] = {}
    for receipt in recs:
        if not receipt.verifies():
            return _report(IngressDrainDecisionKind.QUARANTINE_BAD_SIGNATURE, False, False, "bad ingress drain signature", **common)
        if not receipt.live(now):
            return _report(IngressDrainDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, False, False, "expired or future ingress drain receipt", **common)
        if receipt.receipt_digest in seen:
            return _report(IngressDrainDecisionKind.QUARANTINE_REPLAY, False, False, "ingress drain receipt replayed", **common)
        if highest_seen_sequence is not None and receipt.sequence < highest_seen_sequence:
            return _report(IngressDrainDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, False, "ingress drain sequence rolled back", **common)
        prior = by_sequence.get(receipt.sequence)
        if prior is not None and prior.receipt_core_digest != receipt.receipt_core_digest:
            return _report(IngressDrainDecisionKind.QUARANTINE_SEQUENCE_FORK, False, False, "same-sequence ingress drain fork", **common)
        by_sequence[receipt.sequence] = receipt
        if receipt.profile_id != expected_profile_id:
            return _report(IngressDrainDecisionKind.QUARANTINE_PROFILE_DRIFT, False, False, "profile drift", **common)
        if receipt.service_name != expected_service_name:
            return _report(IngressDrainDecisionKind.QUARANTINE_SERVICE_DRIFT, False, False, "service drift", **common)
        if receipt.scope_digest != expected_scope_digest:
            return _report(IngressDrainDecisionKind.QUARANTINE_SCOPE_DRIFT, False, False, "scope drift", **common)
        if receipt.request_digest != expected_request_digest:
            return _report(IngressDrainDecisionKind.QUARANTINE_REQUEST_DRIFT, False, False, "request drift", **common)
        if receipt.caller_digest != expected_caller_digest:
            return _report(IngressDrainDecisionKind.QUARANTINE_CALLER_DRIFT, False, False, "caller drift", **common)
        if receipt.handler_digest != expected_handler_digest:
            return _report(IngressDrainDecisionKind.QUARANTINE_HANDLER_DRIFT, False, False, "handler drift", **common)
        if receipt.ingress_request_digest != expected_ingress_request_digest:
            return _report(IngressDrainDecisionKind.QUARANTINE_REQUEST_DRIFT, False, False, "ingress request digest drift", **common)
        if receipt.ingress_gate_digest != component_digests[0] or receipt.service_ticket_digest != component_digests[1] or receipt.load_sheath_digest != component_digests[2] or receipt.continuity_digest != component_digests[3]:
            return _report(IngressDrainDecisionKind.QUARANTINE_COMPONENT_DIGEST_DRIFT, False, False, "component digest drift", **common)
    ordered = sorted(by_sequence.values(), key=lambda item: item.sequence)
    for left, right in zip(ordered, ordered[1:]):
        if right.sequence == left.sequence + 1 and right.previous_receipt_digest != left.receipt_digest:
            return _report(IngressDrainDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, False, "previous-link mismatch", **common)
        if PHASE_ORDER[right.phase] < PHASE_ORDER[left.phase]:
            return _report(IngressDrainDecisionKind.QUARANTINE_PHASE_REGRESSION, False, False, "ingress drain phase regressed", **common)
        if left.phase is IngressDrainPhase.USEFUL_REFUSAL and right.phase is IngressDrainPhase.COMPLETE_WORK:
            return _report(IngressDrainDecisionKind.QUARANTINE_COMPLETION_AFTER_REFUSAL, False, False, "completion after useful refusal must use a new request", **common)
    metadata_units = sum(receipt.metadata_units for receipt in ordered)
    if metadata_units > max_metadata_units:
        return _report(IngressDrainDecisionKind.QUARANTINE_METADATA_BUDGET, False, False, "ingress drain exceeded metadata budget", **common)
    family_count = len({receipt.family_id for receipt in ordered})
    path_count = len({receipt.path_family for receipt in ordered})
    if family_count < min_family_count:
        return _report(IngressDrainDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, "ingress drain needs more family diversity", **common)
    if path_count < min_path_family_count:
        return _report(IngressDrainDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, "ingress drain needs more path diversity", **common)
    refusal_count = sum(1 for receipt in ordered if receipt.phase is IngressDrainPhase.USEFUL_REFUSAL)
    complete_count = sum(1 for receipt in ordered if receipt.phase is IngressDrainPhase.COMPLETE_WORK)
    if refusal_count and not complete_count:
        if previous_refusal_streak + refusal_count > max_refusal_streak:
            return _report(IngressDrainDecisionKind.HOLD_REFUSAL_ONLY_LOOP, False, True, "refusal-only ingress drain loop", **common)
        return _report(IngressDrainDecisionKind.ACCEPT_WITH_USEFUL_REFUSAL_PRESSURE, True, True, "ingress drain accepted as useful refusal pressure", accepted=ordered[-1], **common)
    return _report(IngressDrainDecisionKind.ACCEPT_INGRESS_DRAIN, True, any(_component_watch(component) for component, _ in component_kinds), "ingress drain accepted", accepted=ordered[-1], **common)
