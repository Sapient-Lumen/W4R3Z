"""rev0073 summary publication gate after import archive / lineage prune.

A redacted summary receipt, import archive, and guarded lineage prune are not yet
publication permission.  This lane prepares no-network publication intents and
checks that they preserve contradiction memory, redaction, sequence links, and
exact-boundary component digests before a public-looking summary can advance.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .bencode import bencode
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectAction

SUMMARY_PUBLISH_DOMAIN = DOMAIN + b":summary-publish-v1:"


class SummaryPublishChannel(str, Enum):
    OPERATOR_NOTE = "operator_note"
    GARDEN_SUMMARY = "garden_summary"
    PUBLIC_SUMMARY = "public_summary"


class SummaryPublishDecisionKind(str, Enum):
    ACCEPT_SUMMARY_PUBLICATION_READY = "accept_summary_publication_ready"
    HOLD_SUMMARY_RECEIPT_PENDING = "hold_summary_receipt_pending"
    HOLD_IMPORT_ARCHIVE_PENDING = "hold_import_archive_pending"
    HOLD_LINEAGE_PRUNE_PENDING = "hold_lineage_prune_pending"
    HOLD_MISSING_CHANNEL = "hold_missing_channel"
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
class SummaryPublishIntent:
    channel: SummaryPublishChannel
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
    summary_receipt_digest: bytes
    import_archive_digest: bytes
    lineage_prune_digest: bytes
    summary_lineage_digest: bytes
    accepted_summary_entry_digest: bytes
    accepted_import_marker_digest: bytes
    accepted_lineage_prune_marker_digest: bytes
    redacted_summary_digest: bytes
    contradiction_carried: bool
    raw_boundary_exposed: bool
    raw_payload_exposed: bool
    family_id: str
    path_family_id: str
    hard_negative_count: int = 0

    @property
    def intent_digest(self) -> bytes:
        return sha256(SUMMARY_PUBLISH_DOMAIN + b":intent:" + bencode({
            b"channel": SummaryPublishChannel(self.channel).value,
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
            b"summary_receipt": self.summary_receipt_digest,
            b"import_archive": self.import_archive_digest,
            b"lineage_prune": self.lineage_prune_digest,
            b"summary_lineage": self.summary_lineage_digest,
            b"summary_entry": self.accepted_summary_entry_digest,
            b"import_marker": self.accepted_import_marker_digest,
            b"lineage_marker": self.accepted_lineage_prune_marker_digest,
            b"redacted": self.redacted_summary_digest,
            b"contradiction": 1 if self.contradiction_carried else 0,
            b"raw_boundary": 1 if self.raw_boundary_exposed else 0,
            b"raw_payload": 1 if self.raw_payload_exposed else 0,
            b"family": self.family_id,
            b"path": self.path_family_id,
            b"hard": self.hard_negative_count,
        }))


@dataclass(frozen=True)
class SummaryPublishReport:
    decision_kind: SummaryPublishDecisionKind
    accept: bool
    watch: bool
    publication_ready: bool
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
    summary_receipt_digest: bytes
    import_archive_digest: bytes
    lineage_prune_digest: bytes
    summary_lineage_digest: bytes
    accepted_summary_entry_digest: bytes
    accepted_import_marker_digest: bytes
    accepted_lineage_prune_marker_digest: bytes
    accepted_intent_digest: bytes
    channel_values: tuple[str, ...]
    intent_digests: tuple[bytes, ...]
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
    for attr in ("report_digest", "accepted_marker_digest", "accepted_entry_digest", "accepted_packet_digest"):
        value = getattr(report, attr, None)
        if isinstance(value, bytes) and len(value) == 32:
            return value
    raise ValueError("component lacks digest")


def _boundary(report: Any) -> tuple[Any, ...]:
    return (SideEffectAction(getattr(report, "action")), getattr(report, "profile_id"), getattr(report, "service_name"), getattr(report, "scope_digest"), getattr(report, "request_digest"), getattr(report, "payload_digest"), getattr(report, "idempotency_key"))


def _intent_boundary(intent: SummaryPublishIntent) -> tuple[Any, ...]:
    return (SideEffectAction(intent.action), intent.profile_id, intent.service_name, intent.scope_digest, intent.request_digest, intent.payload_digest, intent.idempotency_key)


def make_summary_publish_intent(*, channel: SummaryPublishChannel, sequence: int, summary_receipt_report: Any, import_archive_report: Any, lineage_prune_report: Any, previous_digest: bytes = ZERO_DIGEST, redacted_summary_digest: bytes | None = None, contradiction_carried: bool | None = None, raw_boundary_exposed: bool = False, raw_payload_exposed: bool = False, family_id: str = "summary-publish-family-a", path_family_id: str = "summary-publish-path-a", hard_negative_count: int = 0) -> SummaryPublishIntent:
    digest = redacted_summary_digest or sha256(SUMMARY_PUBLISH_DOMAIN + b":redacted-summary:" + _digest(summary_receipt_report) + b":" + _digest(import_archive_report) + b":" + _digest(lineage_prune_report) + b":" + SummaryPublishChannel(channel).value.encode())
    contradiction = bool(getattr(summary_receipt_report, "contradiction_carried", False) and getattr(import_archive_report, "contradiction_preserved", False) and getattr(lineage_prune_report, "contradiction_preserved", False)) if contradiction_carried is None else bool(contradiction_carried)
    return SummaryPublishIntent(
        channel=SummaryPublishChannel(channel),
        sequence=int(sequence),
        previous_digest=previous_digest,
        action=SideEffectAction(getattr(summary_receipt_report, "action")),
        profile_id=getattr(summary_receipt_report, "profile_id"),
        service_name=getattr(summary_receipt_report, "service_name"),
        scope_digest=getattr(summary_receipt_report, "scope_digest"),
        request_digest=getattr(summary_receipt_report, "request_digest"),
        payload_digest=getattr(summary_receipt_report, "payload_digest"),
        idempotency_key=getattr(summary_receipt_report, "idempotency_key"),
        retry_idempotency_key=getattr(summary_receipt_report, "retry_idempotency_key", ZERO_DIGEST),
        summary_receipt_digest=_digest(summary_receipt_report),
        import_archive_digest=_digest(import_archive_report),
        lineage_prune_digest=_digest(lineage_prune_report),
        summary_lineage_digest=getattr(summary_receipt_report, "summary_lineage_digest", ZERO_DIGEST),
        accepted_summary_entry_digest=getattr(summary_receipt_report, "accepted_summary_entry_digest", ZERO_DIGEST),
        accepted_import_marker_digest=getattr(import_archive_report, "accepted_marker_digest", ZERO_DIGEST),
        accepted_lineage_prune_marker_digest=getattr(lineage_prune_report, "accepted_marker_digest", ZERO_DIGEST),
        redacted_summary_digest=digest,
        contradiction_carried=contradiction,
        raw_boundary_exposed=bool(raw_boundary_exposed),
        raw_payload_exposed=bool(raw_payload_exposed),
        family_id=family_id,
        path_family_id=path_family_id,
        hard_negative_count=hard_negative_count,
    )


def _report(kind: SummaryPublishDecisionKind, accept: bool, watch: bool, ready: bool, contradiction: bool, redacted: bool, reason: str, *, summary_receipt_report: Any, import_archive_report: Any, lineage_prune_report: Any, intents: tuple[SummaryPublishIntent, ...], accepted_intent_digest: bytes = ZERO_DIGEST) -> SummaryPublishReport:
    intent_digests = tuple(intent.intent_digest for intent in intents)
    channels = tuple(sorted({intent.channel.value for intent in intents}))
    families = {intent.family_id for intent in intents}
    paths = {intent.path_family_id for intent in intents}
    hard = int(getattr(summary_receipt_report, "hard_negative_count", 0) or 0) + int(getattr(import_archive_report, "hard_negative_count", 0) or 0) + int(getattr(lineage_prune_report, "hard_negative_count", 0) or 0) + sum(intent.hard_negative_count for intent in intents)
    report_digest = sha256(SUMMARY_PUBLISH_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"ready": 1 if ready else 0,
        b"contradiction": 1 if contradiction else 0,
        b"redacted": 1 if redacted else 0,
        b"action": SideEffectAction(getattr(summary_receipt_report, "action")).value,
        b"profile": getattr(summary_receipt_report, "profile_id"),
        b"service": getattr(summary_receipt_report, "service_name"),
        b"scope": getattr(summary_receipt_report, "scope_digest"),
        b"request": getattr(summary_receipt_report, "request_digest"),
        b"payload": getattr(summary_receipt_report, "payload_digest"),
        b"idem": getattr(summary_receipt_report, "idempotency_key"),
        b"retry_idem": getattr(summary_receipt_report, "retry_idempotency_key", ZERO_DIGEST),
        b"summary_receipt": _digest(summary_receipt_report),
        b"import_archive": _digest(import_archive_report),
        b"lineage_prune": _digest(lineage_prune_report),
        b"summary_lineage": getattr(summary_receipt_report, "summary_lineage_digest", ZERO_DIGEST),
        b"summary_entry": getattr(summary_receipt_report, "accepted_summary_entry_digest", ZERO_DIGEST),
        b"import_marker": getattr(import_archive_report, "accepted_marker_digest", ZERO_DIGEST),
        b"lineage_marker": getattr(lineage_prune_report, "accepted_marker_digest", ZERO_DIGEST),
        b"accepted_intent": accepted_intent_digest,
        b"channels": channels,
        b"intents": intent_digests,
        b"families": sorted(families),
        b"paths": sorted(paths),
        b"hard": hard,
    }))
    return SummaryPublishReport(
        kind, accept, watch, ready, contradiction, redacted, reason,
        SideEffectAction(getattr(summary_receipt_report, "action")),
        getattr(summary_receipt_report, "profile_id"),
        getattr(summary_receipt_report, "service_name"),
        getattr(summary_receipt_report, "scope_digest"),
        getattr(summary_receipt_report, "request_digest"),
        getattr(summary_receipt_report, "payload_digest"),
        getattr(summary_receipt_report, "idempotency_key"),
        getattr(summary_receipt_report, "retry_idempotency_key", ZERO_DIGEST),
        _digest(summary_receipt_report),
        _digest(import_archive_report),
        _digest(lineage_prune_report),
        getattr(summary_receipt_report, "summary_lineage_digest", ZERO_DIGEST),
        getattr(summary_receipt_report, "accepted_summary_entry_digest", ZERO_DIGEST),
        getattr(import_archive_report, "accepted_marker_digest", ZERO_DIGEST),
        getattr(lineage_prune_report, "accepted_marker_digest", ZERO_DIGEST),
        accepted_intent_digest,
        channels,
        intent_digests,
        len(families),
        len(paths),
        hard,
        report_digest,
    )


def assess_summary_publication(*, summary_receipt_report: Any, import_archive_report: Any, lineage_prune_report: Any, intents: tuple[SummaryPublishIntent, ...], previous_digest: bytes = ZERO_DIGEST, required_channels: tuple[SummaryPublishChannel, ...] = (SummaryPublishChannel.OPERATOR_NOTE, SummaryPublishChannel.GARDEN_SUMMARY), min_family_count: int = 2, min_path_family_count: int = 2) -> SummaryPublishReport:
    if not (getattr(summary_receipt_report, "accept", False) and getattr(summary_receipt_report, "summary_receipted", False)):
        return _report(SummaryPublishDecisionKind.HOLD_SUMMARY_RECEIPT_PENDING, False, True, False, False, True, "summary receipt is not accepted", summary_receipt_report=summary_receipt_report, import_archive_report=import_archive_report, lineage_prune_report=lineage_prune_report, intents=intents)
    if not (getattr(import_archive_report, "accept", False) and getattr(import_archive_report, "import_archived", False)):
        return _report(SummaryPublishDecisionKind.HOLD_IMPORT_ARCHIVE_PENDING, False, True, False, False, True, "import archive is not accepted", summary_receipt_report=summary_receipt_report, import_archive_report=import_archive_report, lineage_prune_report=lineage_prune_report, intents=intents)
    if not (getattr(lineage_prune_report, "accept", False) and getattr(lineage_prune_report, "lineage_prune_guarded", False)):
        return _report(SummaryPublishDecisionKind.HOLD_LINEAGE_PRUNE_PENDING, False, True, False, False, True, "lineage prune is not accepted", summary_receipt_report=summary_receipt_report, import_archive_report=import_archive_report, lineage_prune_report=lineage_prune_report, intents=intents)
    expected_boundary = _boundary(summary_receipt_report)
    if expected_boundary != _boundary(import_archive_report) or expected_boundary != _boundary(lineage_prune_report):
        return _report(SummaryPublishDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, True, False, False, False, "component boundary drift", summary_receipt_report=summary_receipt_report, import_archive_report=import_archive_report, lineage_prune_report=lineage_prune_report, intents=intents)
    expected_lineage = getattr(summary_receipt_report, "summary_lineage_digest", ZERO_DIGEST)
    if expected_lineage != getattr(import_archive_report, "summary_lineage_digest", ZERO_DIGEST) or expected_lineage != getattr(lineage_prune_report, "summary_lineage_digest", ZERO_DIGEST):
        return _report(SummaryPublishDecisionKind.QUARANTINE_DIGEST_DRIFT, False, True, False, False, False, "summary lineage digest drift", summary_receipt_report=summary_receipt_report, import_archive_report=import_archive_report, lineage_prune_report=lineage_prune_report, intents=intents)
    if not intents:
        return _report(SummaryPublishDecisionKind.HOLD_MISSING_CHANNEL, False, True, False, False, True, "no summary publication intents", summary_receipt_report=summary_receipt_report, import_archive_report=import_archive_report, lineage_prune_report=lineage_prune_report, intents=intents)
    expected_summary = _digest(summary_receipt_report)
    expected_import = _digest(import_archive_report)
    expected_prune = _digest(lineage_prune_report)
    expected_entry = getattr(summary_receipt_report, "accepted_summary_entry_digest", ZERO_DIGEST)
    expected_import_marker = getattr(import_archive_report, "accepted_marker_digest", ZERO_DIGEST)
    expected_lineage_marker = getattr(lineage_prune_report, "accepted_marker_digest", ZERO_DIGEST)
    prev = previous_digest
    seen_seq: dict[int, bytes] = {}
    seen_digests: set[bytes] = set()
    contradiction = False
    for intent in sorted(intents, key=lambda item: item.sequence):
        digest = intent.intent_digest
        if digest in seen_digests:
            return _report(SummaryPublishDecisionKind.QUARANTINE_REPLAY, False, True, False, False, False, "duplicate summary publication intent", summary_receipt_report=summary_receipt_report, import_archive_report=import_archive_report, lineage_prune_report=lineage_prune_report, intents=intents)
        seen_digests.add(digest)
        if intent.sequence <= 0:
            return _report(SummaryPublishDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, True, False, False, False, "non-positive publication sequence", summary_receipt_report=summary_receipt_report, import_archive_report=import_archive_report, lineage_prune_report=lineage_prune_report, intents=intents)
        if intent.sequence in seen_seq and seen_seq[intent.sequence] != digest:
            return _report(SummaryPublishDecisionKind.QUARANTINE_SEQUENCE_FORK, False, True, False, False, False, "same-sequence publication fork", summary_receipt_report=summary_receipt_report, import_archive_report=import_archive_report, lineage_prune_report=lineage_prune_report, intents=intents)
        seen_seq[intent.sequence] = digest
        if intent.previous_digest != prev:
            return _report(SummaryPublishDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, True, False, False, False, "previous digest mismatch", summary_receipt_report=summary_receipt_report, import_archive_report=import_archive_report, lineage_prune_report=lineage_prune_report, intents=intents)
        if _intent_boundary(intent) != expected_boundary:
            return _report(SummaryPublishDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, True, False, False, False, "publication intent boundary drift", summary_receipt_report=summary_receipt_report, import_archive_report=import_archive_report, lineage_prune_report=lineage_prune_report, intents=intents)
        if (intent.summary_receipt_digest != expected_summary or intent.import_archive_digest != expected_import or intent.lineage_prune_digest != expected_prune or intent.summary_lineage_digest != expected_lineage or intent.accepted_summary_entry_digest != expected_entry or intent.accepted_import_marker_digest != expected_import_marker or intent.accepted_lineage_prune_marker_digest != expected_lineage_marker):
            return _report(SummaryPublishDecisionKind.QUARANTINE_DIGEST_DRIFT, False, True, False, False, False, "publication component digest drift", summary_receipt_report=summary_receipt_report, import_archive_report=import_archive_report, lineage_prune_report=lineage_prune_report, intents=intents)
        if intent.raw_boundary_exposed or intent.raw_payload_exposed:
            return _report(SummaryPublishDecisionKind.QUARANTINE_RAW_LEAK, False, True, False, False, False, "publication leaked raw boundary or payload", summary_receipt_report=summary_receipt_report, import_archive_report=import_archive_report, lineage_prune_report=lineage_prune_report, intents=intents)
        if intent.hard_negative_count or int(getattr(summary_receipt_report, "hard_negative_count", 0) or 0) or int(getattr(import_archive_report, "hard_negative_count", 0) or 0) or int(getattr(lineage_prune_report, "hard_negative_count", 0) or 0):
            return _report(SummaryPublishDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, True, False, bool(intent.contradiction_carried), True, "hard negative pressure", summary_receipt_report=summary_receipt_report, import_archive_report=import_archive_report, lineage_prune_report=lineage_prune_report, intents=intents)
        contradiction = contradiction or intent.contradiction_carried
        prev = digest
    if not contradiction:
        return _report(SummaryPublishDecisionKind.QUARANTINE_CONTRADICTION_DROPPED, False, True, False, False, True, "publication dropped contradiction memory", summary_receipt_report=summary_receipt_report, import_archive_report=import_archive_report, lineage_prune_report=lineage_prune_report, intents=intents)
    required = {SummaryPublishChannel(channel).value for channel in required_channels}
    actual = {intent.channel.value for intent in intents}
    if not required.issubset(actual):
        return _report(SummaryPublishDecisionKind.HOLD_MISSING_CHANNEL, False, True, False, True, True, "missing required publication channel", summary_receipt_report=summary_receipt_report, import_archive_report=import_archive_report, lineage_prune_report=lineage_prune_report, intents=intents)
    if len({intent.family_id for intent in intents}) < min_family_count:
        return _report(SummaryPublishDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, False, True, True, "low summary publication family diversity", summary_receipt_report=summary_receipt_report, import_archive_report=import_archive_report, lineage_prune_report=lineage_prune_report, intents=intents)
    if len({intent.path_family_id for intent in intents}) < min_path_family_count:
        return _report(SummaryPublishDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, False, True, True, "low summary publication path diversity", summary_receipt_report=summary_receipt_report, import_archive_report=import_archive_report, lineage_prune_report=lineage_prune_report, intents=intents)
    return _report(SummaryPublishDecisionKind.ACCEPT_SUMMARY_PUBLICATION_READY, True, False, True, True, True, "summary publication ready", summary_receipt_report=summary_receipt_report, import_archive_report=import_archive_report, lineage_prune_report=lineage_prune_report, intents=intents, accepted_intent_digest=prev)
