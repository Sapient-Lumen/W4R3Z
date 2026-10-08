"""Joined safe-start gate for negotiation, migration, and transport trace.

rev0033 asks whether three locally valid reports can accidentally authorize a
future side effect when joined incorrectly: protocol negotiation, migrated local
memory, and SAM-shadow transport trace.  This module binds those reports to one
session/scope/request tuple before sticky peer state or transport sends are
considered locally safe.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .bencode import bencode
from .ids import DOMAIN, sha256
from .migrationlane import MigrationReport
from .negotiationlane import NegotiationReport
from .samtrace import SamTraceReport

SAFE_START_DOMAIN = DOMAIN + b":safe-start-v1:"
ZERO_DIGEST = b"\x00" * 32


class SafeStartDecisionKind(str, Enum):
    ACCEPT_SAFE_START = "accept_safe_start"
    ACCEPT_WITH_MIGRATION_WATCH = "accept_with_migration_watch"
    HOLD_NEGOTIATION_WATCH = "hold_negotiation_watch"
    HOLD_MIGRATION_WATCH = "hold_migration_watch"
    QUARANTINE_NEGOTIATION = "quarantine_negotiation"
    QUARANTINE_MIGRATION = "quarantine_migration"
    QUARANTINE_SAMTRACE = "quarantine_samtrace"
    QUARANTINE_SCOPE_MISMATCH = "quarantine_scope_mismatch"
    QUARANTINE_REQUEST_MISMATCH = "quarantine_request_mismatch"
    QUARANTINE_OBJECT_MISMATCH = "quarantine_object_mismatch"


@dataclass(frozen=True)
class SafeStartIntent:
    session_id: bytes
    scope_id: bytes
    object_digest: bytes
    request_id: bytes
    purpose: str

    def __post_init__(self) -> None:
        for name, value in (("session_id", self.session_id), ("scope_id", self.scope_id), ("object_digest", self.object_digest), ("request_id", self.request_id)):
            if len(value) != 32:
                raise ValueError(f"safe-start intent {name} must be 32 bytes")
        if not self.purpose:
            raise ValueError("safe-start intent purpose must not be empty")

    @property
    def intent_digest(self) -> bytes:
        return sha256(SAFE_START_DOMAIN + b":intent:" + bencode({
            b"session": self.session_id,
            b"scope": self.scope_id,
            b"object": self.object_digest,
            b"request": self.request_id,
            b"purpose": self.purpose,
        }))


@dataclass(frozen=True)
class SafeStartReport:
    decision_kind: SafeStartDecisionKind
    accept: bool
    reason: str
    intent_digest: bytes
    negotiation_report_digest: bytes
    migration_report_digest: bytes
    samtrace_report_digest: bytes
    pressure_digests: tuple[bytes, ...]
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _report(kind: SafeStartDecisionKind, accept: bool, reason: str, intent: SafeStartIntent, negotiation: NegotiationReport, migration: MigrationReport, samtrace: SamTraceReport, pressures: Iterable[bytes] = ()) -> SafeStartReport:
    pressure_t = tuple(sorted(set(pressures)))
    digest = sha256(SAFE_START_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"reason": reason,
        b"intent": intent.intent_digest,
        b"negotiation": negotiation.report_digest,
        b"migration": migration.report_digest,
        b"samtrace": samtrace.report_digest,
        b"pressures": list(pressure_t),
    }))
    return SafeStartReport(kind, accept, reason, intent.intent_digest, negotiation.report_digest, migration.report_digest, samtrace.report_digest, pressure_t, digest)


def assess_safe_start(intent: SafeStartIntent, *, negotiation: NegotiationReport, migration: MigrationReport, samtrace: SamTraceReport, allow_migration_watch: bool = True) -> SafeStartReport:
    if negotiation.quarantined or not negotiation.accept:
        return _report(SafeStartDecisionKind.QUARANTINE_NEGOTIATION if negotiation.quarantined else SafeStartDecisionKind.HOLD_NEGOTIATION_WATCH, False, "negotiation did not accept", intent, negotiation, migration, samtrace, (negotiation.report_digest,))
    if migration.quarantined or not migration.accept:
        return _report(SafeStartDecisionKind.QUARANTINE_MIGRATION if migration.quarantined else SafeStartDecisionKind.HOLD_MIGRATION_WATCH, False, "migration did not accept", intent, negotiation, migration, samtrace, (migration.report_digest,))
    # SamTraceReport has accept/quarantined in the current cube surface.
    if getattr(samtrace, "quarantined", False) or not samtrace.accept:
        return _report(SafeStartDecisionKind.QUARANTINE_SAMTRACE, False, "samtrace did not accept", intent, negotiation, migration, samtrace, (samtrace.report_digest,))
    if getattr(samtrace, "scope_id", intent.scope_id) != intent.scope_id:
        return _report(SafeStartDecisionKind.QUARANTINE_SCOPE_MISMATCH, False, "samtrace scope does not match safe-start intent", intent, negotiation, migration, samtrace, (samtrace.report_digest,))
    if getattr(samtrace, "object_digest", intent.object_digest) != intent.object_digest:
        return _report(SafeStartDecisionKind.QUARANTINE_OBJECT_MISMATCH, False, "samtrace object does not match safe-start intent", intent, negotiation, migration, samtrace, (samtrace.report_digest,))
    if getattr(samtrace, "request_id", intent.request_id) != intent.request_id:
        return _report(SafeStartDecisionKind.QUARANTINE_REQUEST_MISMATCH, False, "samtrace request does not match safe-start intent", intent, negotiation, migration, samtrace, (samtrace.report_digest,))
    if migration.decision_kind.value == "accept_with_soft_drop":
        if allow_migration_watch:
            return _report(SafeStartDecisionKind.ACCEPT_WITH_MIGRATION_WATCH, True, "safe start accepted with migrated soft-drop watch", intent, negotiation, migration, samtrace)
        return _report(SafeStartDecisionKind.HOLD_MIGRATION_WATCH, False, "migration soft-drop watch disabled", intent, negotiation, migration, samtrace, (migration.report_digest,))
    return _report(SafeStartDecisionKind.ACCEPT_SAFE_START, True, "safe start accepted at joined boundary", intent, negotiation, migration, samtrace)
