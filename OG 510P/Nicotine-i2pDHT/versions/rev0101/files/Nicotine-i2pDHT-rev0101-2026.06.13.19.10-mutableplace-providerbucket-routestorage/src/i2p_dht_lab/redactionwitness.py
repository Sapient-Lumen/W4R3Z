"""rev0073 redaction witness receipts for summary publication.

Publication-ready redacted summaries still need local witness evidence that the
boundary/payload redaction, digest binding, and contradiction memory survived.
Witnesses are evidence, not quorum or global truth.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .bencode import bencode
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectAction

REDACTION_WITNESS_DOMAIN = DOMAIN + b":redaction-witness-v1:"


class RedactionWitnessClass(str, Enum):
    BOUNDARY_REDACTED = "boundary_redacted"
    PAYLOAD_REDACTED = "payload_redacted"
    DIGEST_BOUND = "digest_bound"
    CONTRADICTION_CARRIED = "contradiction_carried"
    AUDIENCE_SCOPED = "audience_scoped"


class RedactionWitnessDecisionKind(str, Enum):
    ACCEPT_REDACTION_WITNESSED = "accept_redaction_witnessed"
    HOLD_SUMMARY_PUBLICATION_PENDING = "hold_summary_publication_pending"
    HOLD_MISSING_REQUIRED_CLASS = "hold_missing_required_class"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    QUARANTINE_BOUNDARY_DRIFT = "quarantine_boundary_drift"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_RAW_LEAK = "quarantine_raw_leak"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_CONTRADICTION_DROPPED = "quarantine_contradiction_dropped"
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"


@dataclass(frozen=True)
class RedactionWitnessReceipt:
    witness_class: RedactionWitnessClass
    sequence: int
    previous_digest: bytes
    action: SideEffectAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    retry_idempotency_key: bytes
    summary_publish_digest: bytes
    accepted_intent_digest: bytes
    summary_receipt_digest: bytes
    import_archive_digest: bytes
    lineage_prune_digest: bytes
    redacted_summary_digest: bytes
    contradiction_carried: bool
    raw_boundary_exposed: bool
    raw_payload_exposed: bool
    family_id: str
    path_family_id: str
    hard_negative_count: int = 0

    @property
    def receipt_digest(self) -> bytes:
        return sha256(REDACTION_WITNESS_DOMAIN + b":receipt:" + bencode({
            b"class": RedactionWitnessClass(self.witness_class).value,
            b"seq": self.sequence,
            b"prev": self.previous_digest,
            b"action": SideEffectAction(self.action).value,
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"payload": self.payload_digest,
            b"idem": self.idempotency_key,
            b"retry_idem": self.retry_idempotency_key,
            b"publish": self.summary_publish_digest,
            b"intent": self.accepted_intent_digest,
            b"summary_receipt": self.summary_receipt_digest,
            b"import_archive": self.import_archive_digest,
            b"lineage_prune": self.lineage_prune_digest,
            b"redacted": self.redacted_summary_digest,
            b"contradiction": 1 if self.contradiction_carried else 0,
            b"raw_boundary": 1 if self.raw_boundary_exposed else 0,
            b"raw_payload": 1 if self.raw_payload_exposed else 0,
            b"family": self.family_id,
            b"path": self.path_family_id,
            b"hard": self.hard_negative_count,
        }))


@dataclass(frozen=True)
class RedactionWitnessReport:
    decision_kind: RedactionWitnessDecisionKind
    accept: bool
    watch: bool
    redaction_witnessed: bool
    contradiction_carried: bool
    redacted: bool
    reason: str
    action: SideEffectAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    retry_idempotency_key: bytes
    summary_publish_digest: bytes
    accepted_intent_digest: bytes
    summary_receipt_digest: bytes
    import_archive_digest: bytes
    lineage_prune_digest: bytes
    accepted_receipt_digest: bytes
    class_values: tuple[str, ...]
    receipt_digests: tuple[bytes, ...]
    family_count: int
    path_family_count: int
    hard_negative_count: int
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _digest(report: Any | None) -> bytes:
    if report is None:
        return ZERO_DIGEST
    for attr in ("report_digest", "accepted_intent_digest", "accepted_marker_digest", "accepted_entry_digest", "accepted_packet_digest"):
        value = getattr(report, attr, None)
        if isinstance(value, bytes) and len(value) == 32:
            return value
    raise ValueError("component lacks digest")


def _boundary(report: Any) -> tuple[Any, ...]:
    return (SideEffectAction(getattr(report, "action")), getattr(report, "profile_id"), getattr(report, "service_name"), getattr(report, "scope_digest"), getattr(report, "request_digest"), getattr(report, "payload_digest"), getattr(report, "idempotency_key"))


def _receipt_boundary(receipt: RedactionWitnessReceipt) -> tuple[Any, ...]:
    return (SideEffectAction(receipt.action), receipt.profile_id, receipt.service_name, receipt.scope_digest, receipt.request_digest, receipt.payload_digest, receipt.idempotency_key)


def make_redaction_witness_receipt(*, witness_class: RedactionWitnessClass, sequence: int, summary_publish_report: Any, previous_digest: bytes = ZERO_DIGEST, contradiction_carried: bool | None = None, raw_boundary_exposed: bool = False, raw_payload_exposed: bool = False, family_id: str = "redaction-witness-family-a", path_family_id: str = "redaction-witness-path-a", hard_negative_count: int = 0) -> RedactionWitnessReceipt:
    contradiction = bool(getattr(summary_publish_report, "contradiction_carried", False)) if contradiction_carried is None else bool(contradiction_carried)
    return RedactionWitnessReceipt(
        witness_class=RedactionWitnessClass(witness_class),
        sequence=int(sequence),
        previous_digest=previous_digest,
        action=SideEffectAction(getattr(summary_publish_report, "action")),
        profile_id=getattr(summary_publish_report, "profile_id"),
        service_name=getattr(summary_publish_report, "service_name"),
        scope_digest=getattr(summary_publish_report, "scope_digest"),
        request_digest=getattr(summary_publish_report, "request_digest"),
        payload_digest=getattr(summary_publish_report, "payload_digest"),
        idempotency_key=getattr(summary_publish_report, "idempotency_key"),
        retry_idempotency_key=getattr(summary_publish_report, "retry_idempotency_key", ZERO_DIGEST),
        summary_publish_digest=_digest(summary_publish_report),
        accepted_intent_digest=getattr(summary_publish_report, "accepted_intent_digest", ZERO_DIGEST),
        summary_receipt_digest=getattr(summary_publish_report, "summary_receipt_digest", ZERO_DIGEST),
        import_archive_digest=getattr(summary_publish_report, "import_archive_digest", ZERO_DIGEST),
        lineage_prune_digest=getattr(summary_publish_report, "lineage_prune_digest", ZERO_DIGEST),
        redacted_summary_digest=sha256(REDACTION_WITNESS_DOMAIN + b":redacted-summary-observed:" + _digest(summary_publish_report)),
        contradiction_carried=contradiction,
        raw_boundary_exposed=bool(raw_boundary_exposed),
        raw_payload_exposed=bool(raw_payload_exposed),
        family_id=family_id,
        path_family_id=path_family_id,
        hard_negative_count=hard_negative_count,
    )


def _report(kind: RedactionWitnessDecisionKind, accept: bool, watch: bool, witnessed: bool, contradiction: bool, redacted: bool, reason: str, *, summary_publish_report: Any, receipts: tuple[RedactionWitnessReceipt, ...], accepted_receipt_digest: bytes = ZERO_DIGEST) -> RedactionWitnessReport:
    digests = tuple(receipt.receipt_digest for receipt in receipts)
    classes = tuple(sorted({receipt.witness_class.value for receipt in receipts}))
    families = {receipt.family_id for receipt in receipts}
    paths = {receipt.path_family_id for receipt in receipts}
    hard = int(getattr(summary_publish_report, "hard_negative_count", 0) or 0) + sum(receipt.hard_negative_count for receipt in receipts)
    report_digest = sha256(REDACTION_WITNESS_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"witnessed": 1 if witnessed else 0,
        b"contradiction": 1 if contradiction else 0,
        b"redacted": 1 if redacted else 0,
        b"action": SideEffectAction(getattr(summary_publish_report, "action")).value,
        b"profile": getattr(summary_publish_report, "profile_id"),
        b"service": getattr(summary_publish_report, "service_name"),
        b"scope": getattr(summary_publish_report, "scope_digest"),
        b"request": getattr(summary_publish_report, "request_digest"),
        b"payload": getattr(summary_publish_report, "payload_digest"),
        b"idem": getattr(summary_publish_report, "idempotency_key"),
        b"retry_idem": getattr(summary_publish_report, "retry_idempotency_key", ZERO_DIGEST),
        b"publish": _digest(summary_publish_report),
        b"intent": getattr(summary_publish_report, "accepted_intent_digest", ZERO_DIGEST),
        b"summary_receipt": getattr(summary_publish_report, "summary_receipt_digest", ZERO_DIGEST),
        b"import_archive": getattr(summary_publish_report, "import_archive_digest", ZERO_DIGEST),
        b"lineage_prune": getattr(summary_publish_report, "lineage_prune_digest", ZERO_DIGEST),
        b"accepted_receipt": accepted_receipt_digest,
        b"classes": classes,
        b"receipts": digests,
        b"families": sorted(families),
        b"paths": sorted(paths),
        b"hard": hard,
    }))
    return RedactionWitnessReport(
        kind, accept, watch, witnessed, contradiction, redacted, reason,
        SideEffectAction(getattr(summary_publish_report, "action")),
        getattr(summary_publish_report, "profile_id"),
        getattr(summary_publish_report, "service_name"),
        getattr(summary_publish_report, "scope_digest"),
        getattr(summary_publish_report, "request_digest"),
        getattr(summary_publish_report, "payload_digest"),
        getattr(summary_publish_report, "idempotency_key"),
        getattr(summary_publish_report, "retry_idempotency_key", ZERO_DIGEST),
        _digest(summary_publish_report),
        getattr(summary_publish_report, "accepted_intent_digest", ZERO_DIGEST),
        getattr(summary_publish_report, "summary_receipt_digest", ZERO_DIGEST),
        getattr(summary_publish_report, "import_archive_digest", ZERO_DIGEST),
        getattr(summary_publish_report, "lineage_prune_digest", ZERO_DIGEST),
        accepted_receipt_digest,
        classes,
        digests,
        len(families),
        len(paths),
        hard,
        report_digest,
    )


def assess_redaction_witnesses(*, summary_publish_report: Any, receipts: tuple[RedactionWitnessReceipt, ...], previous_digest: bytes = ZERO_DIGEST, required_classes: tuple[RedactionWitnessClass, ...] = (RedactionWitnessClass.BOUNDARY_REDACTED, RedactionWitnessClass.PAYLOAD_REDACTED, RedactionWitnessClass.DIGEST_BOUND, RedactionWitnessClass.CONTRADICTION_CARRIED), min_family_count: int = 2, min_path_family_count: int = 2) -> RedactionWitnessReport:
    if not (getattr(summary_publish_report, "accept", False) and getattr(summary_publish_report, "publication_ready", False)):
        return _report(RedactionWitnessDecisionKind.HOLD_SUMMARY_PUBLICATION_PENDING, False, True, False, False, True, "summary publication is not accepted", summary_publish_report=summary_publish_report, receipts=receipts)
    if not receipts:
        return _report(RedactionWitnessDecisionKind.HOLD_MISSING_REQUIRED_CLASS, False, True, False, False, True, "no redaction witness receipts", summary_publish_report=summary_publish_report, receipts=receipts)
    expected_boundary = _boundary(summary_publish_report)
    expected_publish = _digest(summary_publish_report)
    expected_intent = getattr(summary_publish_report, "accepted_intent_digest", ZERO_DIGEST)
    expected_summary = getattr(summary_publish_report, "summary_receipt_digest", ZERO_DIGEST)
    expected_import = getattr(summary_publish_report, "import_archive_digest", ZERO_DIGEST)
    expected_prune = getattr(summary_publish_report, "lineage_prune_digest", ZERO_DIGEST)
    prev = previous_digest
    seen_seq: dict[int, bytes] = {}
    seen_digests: set[bytes] = set()
    contradiction = False
    for receipt in sorted(receipts, key=lambda item: item.sequence):
        digest = receipt.receipt_digest
        if digest in seen_digests:
            return _report(RedactionWitnessDecisionKind.QUARANTINE_REPLAY, False, True, False, False, False, "duplicate redaction witness receipt", summary_publish_report=summary_publish_report, receipts=receipts)
        seen_digests.add(digest)
        if receipt.sequence <= 0:
            return _report(RedactionWitnessDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, True, False, False, False, "non-positive redaction witness sequence", summary_publish_report=summary_publish_report, receipts=receipts)
        if receipt.sequence in seen_seq and seen_seq[receipt.sequence] != digest:
            return _report(RedactionWitnessDecisionKind.QUARANTINE_SEQUENCE_FORK, False, True, False, False, False, "same-sequence redaction witness fork", summary_publish_report=summary_publish_report, receipts=receipts)
        seen_seq[receipt.sequence] = digest
        if receipt.previous_digest != prev:
            return _report(RedactionWitnessDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, True, False, False, False, "previous digest mismatch", summary_publish_report=summary_publish_report, receipts=receipts)
        if _receipt_boundary(receipt) != expected_boundary:
            return _report(RedactionWitnessDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, True, False, False, False, "redaction witness boundary drift", summary_publish_report=summary_publish_report, receipts=receipts)
        if (receipt.summary_publish_digest != expected_publish or receipt.accepted_intent_digest != expected_intent or receipt.summary_receipt_digest != expected_summary or receipt.import_archive_digest != expected_import or receipt.lineage_prune_digest != expected_prune):
            return _report(RedactionWitnessDecisionKind.QUARANTINE_DIGEST_DRIFT, False, True, False, False, False, "redaction witness digest drift", summary_publish_report=summary_publish_report, receipts=receipts)
        if receipt.raw_boundary_exposed or receipt.raw_payload_exposed:
            return _report(RedactionWitnessDecisionKind.QUARANTINE_RAW_LEAK, False, True, False, False, False, "redaction witness leaked raw boundary or payload", summary_publish_report=summary_publish_report, receipts=receipts)
        if receipt.hard_negative_count or int(getattr(summary_publish_report, "hard_negative_count", 0) or 0):
            return _report(RedactionWitnessDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, True, False, bool(receipt.contradiction_carried), True, "hard negative pressure", summary_publish_report=summary_publish_report, receipts=receipts)
        contradiction = contradiction or receipt.contradiction_carried
        prev = digest
    if not contradiction:
        return _report(RedactionWitnessDecisionKind.QUARANTINE_CONTRADICTION_DROPPED, False, True, False, False, True, "redaction witness dropped contradiction memory", summary_publish_report=summary_publish_report, receipts=receipts)
    required = {RedactionWitnessClass(cls).value for cls in required_classes}
    actual = {receipt.witness_class.value for receipt in receipts}
    if not required.issubset(actual):
        return _report(RedactionWitnessDecisionKind.HOLD_MISSING_REQUIRED_CLASS, False, True, False, True, True, "missing required redaction witness class", summary_publish_report=summary_publish_report, receipts=receipts)
    if len({receipt.family_id for receipt in receipts}) < min_family_count:
        return _report(RedactionWitnessDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, False, True, True, "low redaction witness family diversity", summary_publish_report=summary_publish_report, receipts=receipts)
    if len({receipt.path_family_id for receipt in receipts}) < min_path_family_count:
        return _report(RedactionWitnessDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, False, True, True, "low redaction witness path diversity", summary_publish_report=summary_publish_report, receipts=receipts)
    return _report(RedactionWitnessDecisionKind.ACCEPT_REDACTION_WITNESSED, True, False, True, True, True, "redaction witnessed", summary_publish_report=summary_publish_report, receipts=receipts, accepted_receipt_digest=prev)
