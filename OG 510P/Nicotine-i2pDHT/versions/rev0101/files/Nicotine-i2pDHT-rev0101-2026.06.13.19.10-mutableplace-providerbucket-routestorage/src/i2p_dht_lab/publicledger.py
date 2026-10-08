"""rev0074 public-summary ledger after local settlement.

Settlement is still not restart-sticky public-summary ledger memory.  This lane
records a redacted public-summary ledger with class coverage and contradiction
carriage before later redaction GC may compact working evidence.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .bencode import bencode
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectAction

PUBLIC_LEDGER_DOMAIN = DOMAIN + b":public-summary-ledger-v1:"


class PublicLedgerClass(str, Enum):
    SUMMARY_SETTLEMENT = "summary_settlement"
    SUMMARY_PUBLICATION = "summary_publication"
    REDACTION_WITNESS = "redaction_witness"
    IMPORT_PRUNE_AUDIT = "import_prune_audit"
    CONTRADICTION_MEMORY = "contradiction_memory"
    REDACTED_PUBLIC_SUMMARY = "redacted_public_summary"
    LOCAL_LEDGER_STATE = "local_ledger_state"


class PublicLedgerDecisionKind(str, Enum):
    ACCEPT_PUBLIC_SUMMARY_LEDGERED = "accept_public_summary_ledg ered".replace(" ", "")
    HOLD_SETTLEMENT_PENDING = "hold_settlement_pending"
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
class PublicLedgerEntry:
    ledger_class: PublicLedgerClass
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
    summary_settlement_digest: bytes
    summary_publish_digest: bytes
    redaction_witness_digest: bytes
    import_prune_audit_digest: bytes
    accepted_settlement_marker_digest: bytes
    contradiction_carried: bool
    redacted: bool
    raw_boundary_exposed: bool
    raw_payload_exposed: bool
    family_id: str
    path_family_id: str
    hard_negative_count: int = 0

    @property
    def entry_digest(self) -> bytes:
        return sha256(PUBLIC_LEDGER_DOMAIN + b":entry:" + bencode({
            b"class": PublicLedgerClass(self.ledger_class).value,
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
            b"settlement": self.summary_settlement_digest,
            b"publish": self.summary_publish_digest,
            b"redaction": self.redaction_witness_digest,
            b"audit": self.import_prune_audit_digest,
            b"marker": self.accepted_settlement_marker_digest,
            b"contradiction": 1 if self.contradiction_carried else 0,
            b"redacted": 1 if self.redacted else 0,
            b"raw_boundary": 1 if self.raw_boundary_exposed else 0,
            b"raw_payload": 1 if self.raw_payload_exposed else 0,
            b"family": self.family_id,
            b"path": self.path_family_id,
            b"hard": self.hard_negative_count,
        }))


@dataclass(frozen=True)
class PublicLedgerReport:
    decision_kind: PublicLedgerDecisionKind
    accept: bool
    watch: bool
    public_summary_ledgered: bool
    contradiction_preserved: bool
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
    summary_settlement_digest: bytes
    summary_publish_digest: bytes
    redaction_witness_digest: bytes
    import_prune_audit_digest: bytes
    accepted_entry_digest: bytes
    class_values: tuple[str, ...]
    entry_digests: tuple[bytes, ...]
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
    for attr in ("report_digest", "accepted_marker_digest", "accepted_entry_digest"):
        value = getattr(report, attr, None)
        if isinstance(value, bytes) and len(value) == 32:
            return value
    raise ValueError("component lacks digest")


def _boundary(report: Any) -> tuple[Any, ...]:
    return (SideEffectAction(getattr(report, "action")), getattr(report, "profile_id"), getattr(report, "service_name"), getattr(report, "scope_digest"), getattr(report, "request_digest"), getattr(report, "payload_digest"), getattr(report, "idempotency_key"))


def _entry_boundary(entry: PublicLedgerEntry) -> tuple[Any, ...]:
    return (SideEffectAction(entry.action), entry.profile_id, entry.service_name, entry.scope_digest, entry.request_digest, entry.payload_digest, entry.idempotency_key)


def make_public_ledger_entry(*, ledger_class: PublicLedgerClass, sequence: int, summary_settlement_report: Any, previous_digest: bytes = ZERO_DIGEST, contradiction_carried: bool | None = None, redacted: bool | None = None, raw_boundary_exposed: bool = False, raw_payload_exposed: bool = False, family_id: str = "public-ledger-family-a", path_family_id: str = "public-ledger-path-a", hard_negative_count: int = 0) -> PublicLedgerEntry:
    contradiction = bool(getattr(summary_settlement_report, "contradiction_preserved", False)) if contradiction_carried is None else bool(contradiction_carried)
    redaction_ok = bool(getattr(summary_settlement_report, "redacted", False)) if redacted is None else bool(redacted)
    return PublicLedgerEntry(
        ledger_class=PublicLedgerClass(ledger_class),
        sequence=int(sequence),
        previous_digest=previous_digest,
        action=SideEffectAction(getattr(summary_settlement_report, "action")),
        profile_id=getattr(summary_settlement_report, "profile_id"),
        service_name=getattr(summary_settlement_report, "service_name"),
        scope_digest=getattr(summary_settlement_report, "scope_digest"),
        request_digest=getattr(summary_settlement_report, "request_digest"),
        payload_digest=getattr(summary_settlement_report, "payload_digest"),
        idempotency_key=getattr(summary_settlement_report, "idempotency_key"),
        retry_idempotency_key=getattr(summary_settlement_report, "retry_idempotency_key", ZERO_DIGEST),
        summary_settlement_digest=_digest(summary_settlement_report),
        summary_publish_digest=getattr(summary_settlement_report, "summary_publish_digest", ZERO_DIGEST),
        redaction_witness_digest=getattr(summary_settlement_report, "redaction_witness_digest", ZERO_DIGEST),
        import_prune_audit_digest=getattr(summary_settlement_report, "import_prune_audit_digest", ZERO_DIGEST),
        accepted_settlement_marker_digest=getattr(summary_settlement_report, "accepted_marker_digest", ZERO_DIGEST),
        contradiction_carried=contradiction,
        redacted=redaction_ok,
        raw_boundary_exposed=bool(raw_boundary_exposed),
        raw_payload_exposed=bool(raw_payload_exposed),
        family_id=family_id,
        path_family_id=path_family_id,
        hard_negative_count=int(hard_negative_count),
    )


def _report(kind: PublicLedgerDecisionKind, accept: bool, watch: bool, ledgered: bool, contradiction: bool, redacted: bool, reason: str, *, summary_settlement_report: Any, entries: tuple[PublicLedgerEntry, ...], accepted_entry_digest: bytes = ZERO_DIGEST) -> PublicLedgerReport:
    entry_digests = tuple(entry.entry_digest for entry in entries)
    class_values = tuple(sorted({entry.ledger_class.value for entry in entries}))
    families = {entry.family_id for entry in entries}
    paths = {entry.path_family_id for entry in entries}
    hard = int(getattr(summary_settlement_report, "hard_negative_count", 0) or 0) + sum(entry.hard_negative_count for entry in entries)
    digest = sha256(PUBLIC_LEDGER_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"ledgered": 1 if ledgered else 0,
        b"contradiction": 1 if contradiction else 0,
        b"redacted": 1 if redacted else 0,
        b"reason": reason,
        b"settlement": _digest(summary_settlement_report),
        b"accepted": accepted_entry_digest,
        b"classes": list(class_values),
        b"entries": list(entry_digests),
        b"families": len(families),
        b"paths": len(paths),
        b"hard": hard,
    }))
    return PublicLedgerReport(kind, accept, watch, ledgered, contradiction, redacted, reason, SideEffectAction(getattr(summary_settlement_report, "action")), getattr(summary_settlement_report, "profile_id"), getattr(summary_settlement_report, "service_name"), getattr(summary_settlement_report, "scope_digest"), getattr(summary_settlement_report, "request_digest"), getattr(summary_settlement_report, "payload_digest"), getattr(summary_settlement_report, "idempotency_key"), getattr(summary_settlement_report, "retry_idempotency_key", ZERO_DIGEST), _digest(summary_settlement_report), getattr(summary_settlement_report, "summary_publish_digest", ZERO_DIGEST), getattr(summary_settlement_report, "redaction_witness_digest", ZERO_DIGEST), getattr(summary_settlement_report, "import_prune_audit_digest", ZERO_DIGEST), accepted_entry_digest, class_values, entry_digests, len(families), len(paths), hard, digest)


def assess_public_ledger(*, summary_settlement_report: Any, entries: tuple[PublicLedgerEntry, ...], previous_digest: bytes = ZERO_DIGEST, min_family_count: int = 2, min_path_family_count: int = 2, required_classes: tuple[PublicLedgerClass, ...] = (PublicLedgerClass.SUMMARY_SETTLEMENT, PublicLedgerClass.SUMMARY_PUBLICATION, PublicLedgerClass.REDACTION_WITNESS, PublicLedgerClass.IMPORT_PRUNE_AUDIT, PublicLedgerClass.CONTRADICTION_MEMORY, PublicLedgerClass.REDACTED_PUBLIC_SUMMARY, PublicLedgerClass.LOCAL_LEDGER_STATE)) -> PublicLedgerReport:
    entries = tuple(entries)
    if not getattr(summary_settlement_report, "accept", False) or not getattr(summary_settlement_report, "summary_settled", False):
        return _report(PublicLedgerDecisionKind.HOLD_SETTLEMENT_PENDING, False, True, False, False, False, "summary settlement not accepted", summary_settlement_report=summary_settlement_report, entries=entries)
    boundary = _boundary(summary_settlement_report)
    if any(_entry_boundary(entry) != boundary for entry in entries):
        return _report(PublicLedgerDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, True, False, False, False, "ledger boundary drift", summary_settlement_report=summary_settlement_report, entries=entries)
    settlement_digest = _digest(summary_settlement_report)
    if any(entry.summary_settlement_digest != settlement_digest or entry.summary_publish_digest != getattr(summary_settlement_report, "summary_publish_digest", ZERO_DIGEST) or entry.redaction_witness_digest != getattr(summary_settlement_report, "redaction_witness_digest", ZERO_DIGEST) or entry.import_prune_audit_digest != getattr(summary_settlement_report, "import_prune_audit_digest", ZERO_DIGEST) for entry in entries):
        return _report(PublicLedgerDecisionKind.QUARANTINE_DIGEST_DRIFT, False, True, False, False, False, "ledger digest drift", summary_settlement_report=summary_settlement_report, entries=entries)
    if any(entry.raw_boundary_exposed or entry.raw_payload_exposed for entry in entries):
        return _report(PublicLedgerDecisionKind.QUARANTINE_RAW_LEAK, False, True, False, False, False, "raw public-summary ledger leak", summary_settlement_report=summary_settlement_report, entries=entries)
    required = {PublicLedgerClass(item).value for item in required_classes}
    classes = {entry.ledger_class.value for entry in entries}
    if not required.issubset(classes):
        return _report(PublicLedgerDecisionKind.HOLD_MISSING_REQUIRED_CLASS, False, True, False, False, False, "missing public ledger class", summary_settlement_report=summary_settlement_report, entries=entries)
    prev = previous_digest
    seen: dict[int, bytes] = {}
    for entry in sorted(entries, key=lambda item: item.sequence):
        if entry.sequence <= 0:
            return _report(PublicLedgerDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, True, False, False, False, "non-positive ledger sequence", summary_settlement_report=summary_settlement_report, entries=entries)
        digest = entry.entry_digest
        old = seen.get(entry.sequence)
        if old is not None and old != digest:
            return _report(PublicLedgerDecisionKind.QUARANTINE_SEQUENCE_FORK, False, True, False, False, False, "same-sequence ledger fork", summary_settlement_report=summary_settlement_report, entries=entries)
        if entry.previous_digest != prev:
            return _report(PublicLedgerDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, True, False, False, False, "ledger previous digest mismatch", summary_settlement_report=summary_settlement_report, entries=entries)
        seen[entry.sequence] = digest
        prev = digest
    if len({entry.family_id for entry in entries}) < min_family_count:
        return _report(PublicLedgerDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, False, False, False, "low ledger family diversity", summary_settlement_report=summary_settlement_report, entries=entries)
    if len({entry.path_family_id for entry in entries}) < min_path_family_count:
        return _report(PublicLedgerDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, False, False, False, "low ledger path diversity", summary_settlement_report=summary_settlement_report, entries=entries)
    contradiction = bool(getattr(summary_settlement_report, "contradiction_preserved", False) and all(entry.contradiction_carried for entry in entries))
    if not contradiction:
        return _report(PublicLedgerDecisionKind.QUARANTINE_CONTRADICTION_DROPPED, False, True, False, False, False, "ledger dropped contradiction memory", summary_settlement_report=summary_settlement_report, entries=entries)
    redacted = bool(getattr(summary_settlement_report, "redacted", False) and all(entry.redacted for entry in entries))
    if not redacted:
        return _report(PublicLedgerDecisionKind.QUARANTINE_RAW_LEAK, False, True, False, False, False, "ledger dropped redaction evidence", summary_settlement_report=summary_settlement_report, entries=entries)
    hard = int(getattr(summary_settlement_report, "hard_negative_count", 0) or 0) + sum(entry.hard_negative_count for entry in entries)
    if hard:
        return _report(PublicLedgerDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, True, False, True, True, "hard negative pressure", summary_settlement_report=summary_settlement_report, entries=entries)
    return _report(PublicLedgerDecisionKind.ACCEPT_PUBLIC_SUMMARY_LEDGERED, True, False, True, True, True, "public summary ledger accepted", summary_settlement_report=summary_settlement_report, entries=entries, accepted_entry_digest=prev)
