"""rev0095 native call ledger.

After shadow settlement and admission, the next danger is restart drift: a later
process might remember "native looked good" but forget that the call path was
still Python.  This ledger makes the Python route sticky.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .bencode import bencode
from .ids import DOMAIN, sha256

NATIVE_CALL_LEDGER_DOMAIN = DOMAIN + b":native-call-ledger-v1:"


class NativeCallLedgerDecisionKind(str, Enum):
    ACCEPT_LEDGERED_PYTHON_ROUTE = "accept_ledgered_python_route"
    HOLD_ADMISSION_NOT_READY = "hold_admission_not_ready"
    QUARANTINE_NATIVE_AUTHORITY = "quarantine_native_authority"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_MEMORY_DROP = "quarantine_memory_drop"
    QUARANTINE_REPLAY_OR_ROLLBACK = "quarantine_replay_or_rollback"
    QUARANTINE_SAME_SEQUENCE_FORK = "quarantine_same_sequence_fork"
    QUARANTINE_PREVIOUS_LINK_MISMATCH = "quarantine_previous_link_mismatch"
    QUARANTINE_LOW_DIVERSITY = "quarantine_low_diversity"


@dataclass(frozen=True)
class NativeCallLedgerEntry:
    component: str
    profile: str
    operation: str
    request_id: str
    sequence: int
    previous_digest: bytes
    admission_digest: bytes
    settlement_digest: bytes
    fault_seal_digest: bytes
    artifact_digest: bytes
    source_digest: bytes
    fallback_digest: bytes
    python_oracle_digest: bytes
    call_vector_digest: bytes
    python_result_digest: bytes
    native_result_digest: bytes
    route: str
    native_shadow_observed: bool
    native_call_executed: bool
    native_result_selected: bool
    python_result_authoritative: bool
    preserve_admission_memory: bool
    preserve_settlement_memory: bool
    preserve_fault_seal_memory: bool
    preserve_python_oracle_memory: bool
    preserve_fallback_memory: bool
    preserve_tombstone_memory: bool
    preserve_quarantine_memory: bool
    preserve_crash_memory: bool
    family_id: str
    path_family_id: str
    note: str = ""

    @property
    def entry_digest(self) -> bytes:
        return sha256(NATIVE_CALL_LEDGER_DOMAIN + b":entry:" + bencode({
            b"component": self.component,
            b"profile": self.profile,
            b"operation": self.operation,
            b"request": self.request_id,
            b"seq": self.sequence,
            b"prev": self.previous_digest,
            b"admission": self.admission_digest,
            b"settlement": self.settlement_digest,
            b"fault_seal": self.fault_seal_digest,
            b"artifact": self.artifact_digest,
            b"source": self.source_digest,
            b"fallback": self.fallback_digest,
            b"oracle": self.python_oracle_digest,
            b"call_vector": self.call_vector_digest,
            b"python_result": self.python_result_digest,
            b"native_result": self.native_result_digest,
            b"route": self.route,
            b"native_shadow": 1 if self.native_shadow_observed else 0,
            b"native_call_executed": 1 if self.native_call_executed else 0,
            b"native_selected": 1 if self.native_result_selected else 0,
            b"python_authority": 1 if self.python_result_authoritative else 0,
            b"preserve_admission": 1 if self.preserve_admission_memory else 0,
            b"preserve_settlement": 1 if self.preserve_settlement_memory else 0,
            b"preserve_fault_seal": 1 if self.preserve_fault_seal_memory else 0,
            b"preserve_oracle": 1 if self.preserve_python_oracle_memory else 0,
            b"preserve_fallback": 1 if self.preserve_fallback_memory else 0,
            b"preserve_tombstone": 1 if self.preserve_tombstone_memory else 0,
            b"preserve_quarantine": 1 if self.preserve_quarantine_memory else 0,
            b"preserve_crash": 1 if self.preserve_crash_memory else 0,
            b"family": self.family_id,
            b"path_family": self.path_family_id,
            b"note": self.note,
        }))


@dataclass(frozen=True)
class NativeCallLedgerReport:
    decision_kind: NativeCallLedgerDecisionKind
    accepted: bool
    python_route_ledgered: bool
    native_call_permission: bool
    native_result_authoritative: bool
    quarantine: bool
    watch: bool
    obligations: tuple[str, ...]
    entry_digest: bytes
    admission_digest: bytes
    settlement_digest: bytes
    fault_seal_digest: bytes
    artifact_digest: bytes
    source_digest: bytes
    fallback_digest: bytes
    python_oracle_digest: bytes
    call_vector_digest: bytes
    python_result_digest: bytes
    native_result_digest: bytes
    tombstone_memory: bool
    fault_memory: bool
    family_count: int
    path_family_count: int

    @property
    def report_digest(self) -> bytes:
        return sha256(NATIVE_CALL_LEDGER_DOMAIN + b":report:" + bencode({
            b"decision": NativeCallLedgerDecisionKind(self.decision_kind).value,
            b"accepted": 1 if self.accepted else 0,
            b"python_route": 1 if self.python_route_ledgered else 0,
            b"native_call_permission": 1 if self.native_call_permission else 0,
            b"native_authority": 1 if self.native_result_authoritative else 0,
            b"quarantine": 1 if self.quarantine else 0,
            b"watch": 1 if self.watch else 0,
            b"obligations": list(self.obligations),
            b"entry": self.entry_digest,
            b"admission": self.admission_digest,
            b"settlement": self.settlement_digest,
            b"fault_seal": self.fault_seal_digest,
            b"artifact": self.artifact_digest,
            b"source": self.source_digest,
            b"fallback_digest": self.fallback_digest,
            b"oracle": self.python_oracle_digest,
            b"call_vector": self.call_vector_digest,
            b"python_result": self.python_result_digest,
            b"native_result": self.native_result_digest,
            b"tombstone": 1 if self.tombstone_memory else 0,
            b"fault": 1 if self.fault_memory else 0,
            b"family_count": self.family_count,
            b"path_family_count": self.path_family_count,
        }))


def assess_native_call_ledger(
    admission: Any,
    entry: NativeCallLedgerEntry,
    *,
    previous: NativeCallLedgerEntry | None = None,
    prior_entry_digests: tuple[bytes, ...] = (),
    observed_families: tuple[str, ...] = (),
    observed_path_families: tuple[str, ...] = (),
    min_families: int = 2,
    min_path_families: int = 2,
) -> NativeCallLedgerReport:
    families = set(observed_families or (entry.family_id,))
    path_families = set(observed_path_families or (entry.path_family_id,))
    tombstone_memory = bool(getattr(admission, "tombstone_memory", False) and entry.preserve_tombstone_memory)
    fault_memory = bool(getattr(admission, "fault_memory", False) and entry.preserve_quarantine_memory and entry.preserve_crash_memory)

    def report(kind: NativeCallLedgerDecisionKind, accepted: bool, ledgered: bool, quarantine: bool, watch: bool, obligations: tuple[str, ...]) -> NativeCallLedgerReport:
        return NativeCallLedgerReport(
            kind, accepted, ledgered, False, False, quarantine, watch, obligations,
            entry.entry_digest, entry.admission_digest, entry.settlement_digest, entry.fault_seal_digest,
            entry.artifact_digest, entry.source_digest, entry.fallback_digest, entry.python_oracle_digest,
            entry.call_vector_digest, entry.python_result_digest, entry.native_result_digest,
            tombstone_memory, fault_memory, len(families), len(path_families)
        )

    if entry.entry_digest in prior_entry_digests:
        return report(NativeCallLedgerDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, False, True, False, ("native-call-ledger-replay",))
    if previous is not None:
        if entry.sequence < previous.sequence:
            return report(NativeCallLedgerDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, False, True, False, ("native-call-ledger-rollback",))
        if entry.sequence == previous.sequence and entry.entry_digest != previous.entry_digest:
            return report(NativeCallLedgerDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK, False, False, True, False, ("native-call-ledger-same-sequence-fork",))
        if entry.sequence > previous.sequence and entry.previous_digest != previous.entry_digest:
            return report(NativeCallLedgerDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH, False, False, True, False, ("native-call-ledger-previous-link-mismatch",))
    if len(families) < min_families or len(path_families) < min_path_families:
        return report(NativeCallLedgerDecisionKind.QUARANTINE_LOW_DIVERSITY, False, False, True, False, ("native-call-ledger-low-diversity",))
    if entry.admission_digest != getattr(admission, "report_digest") or entry.settlement_digest != getattr(admission, "settlement_digest", entry.settlement_digest):
        return report(NativeCallLedgerDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, True, False, ("native-call-ledger-component-digest-drift",))
    if not getattr(admission, "accepted", False) or not getattr(admission, "admitted_to_shadow_slot", False):
        return report(NativeCallLedgerDecisionKind.HOLD_ADMISSION_NOT_READY, False, False, False, True, ("native-admission-not-ready",))
    if entry.native_call_executed or entry.native_result_selected or not entry.python_result_authoritative or entry.route != "python_fallback":
        return report(NativeCallLedgerDecisionKind.QUARANTINE_NATIVE_AUTHORITY, False, False, True, False, ("native-call-ledger-must-route-python",))
    if not all((entry.native_shadow_observed, entry.preserve_admission_memory, entry.preserve_settlement_memory, entry.preserve_fault_seal_memory, entry.preserve_python_oracle_memory, entry.preserve_fallback_memory, tombstone_memory)):
        return report(NativeCallLedgerDecisionKind.QUARANTINE_MEMORY_DROP, False, False, True, False, ("native-call-ledger-memory-drop",))
    return report(NativeCallLedgerDecisionKind.ACCEPT_LEDGERED_PYTHON_ROUTE, True, True, False, False, ("ledger-python-route", "native-shadow-remains-evidence", "native-dispatch-still-forbidden"))
