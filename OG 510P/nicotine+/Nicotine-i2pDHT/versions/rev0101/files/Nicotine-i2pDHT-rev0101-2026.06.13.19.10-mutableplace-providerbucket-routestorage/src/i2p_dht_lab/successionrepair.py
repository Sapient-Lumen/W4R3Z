"""Joined repair after service-catalog succession, withdrawal, and continuity memory.

rev0038 made service continuity a joined boundary. rev0039 adds the recovery
side: if a catalog key rotates, a service withdraws, or a successor catalog is
announced, the node must not repair service state from just one lane. Repair is
accepted only when succession, withdrawal, journal, and probe-loop signals agree
at the same catalog/scope/request boundary.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .bencode import bencode
from .ids import DOMAIN, sha256

SUCCESSION_REPAIR_DOMAIN = DOMAIN + b":succession-repair-v1:"
ZERO_DIGEST = b"\x00" * 32


class SuccessionRepairSignalKind(str, Enum):
    SUCCESSOR_CATALOG = "successor_catalog"
    WITHDRAWAL = "withdrawal"
    CONTINUITY_JOURNAL = "continuity_journal"
    PROBE_LOOP = "probe_loop"
    TOMBSTONE = "tombstone"


class SuccessionRepairDecisionKind(str, Enum):
    ACCEPT_SUCCESSOR_REPAIR = "accept_successor_repair"
    ACCEPT_STABLE_NO_REPAIR_NEEDED = "accept_stable_no_repair_needed"
    HOLD_MISSING_SUCCESSOR = "hold_missing_successor"
    HOLD_MISSING_JOURNAL = "hold_missing_journal"
    HOLD_MISSING_PROBE_HEALTH = "hold_missing_probe_health"
    QUARANTINE_SIGNAL = "quarantine_signal"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_CATALOG_DRIFT = "quarantine_catalog_drift"
    QUARANTINE_ACTIVE_TOMBSTONE = "quarantine_active_tombstone"
    QUARANTINE_WITHDRAWAL_WITHOUT_SUCCESSOR = "quarantine_withdrawal_without_successor"


@dataclass(frozen=True)
class SuccessionRepairSignal:
    kind: SuccessionRepairSignalKind
    report_digest: bytes
    accept: bool
    catalog_digest: bytes
    scope_digest: bytes
    request_digest: bytes
    successor_catalog_digest: bytes = ZERO_DIGEST
    active_withdrawal: bool = False
    active_tombstone: bool = False
    quarantined: bool = False
    reason: str = ""

    def __post_init__(self) -> None:
        for name, value in (
            ("report_digest", self.report_digest),
            ("catalog_digest", self.catalog_digest),
            ("scope_digest", self.scope_digest),
            ("request_digest", self.request_digest),
            ("successor_catalog_digest", self.successor_catalog_digest),
        ):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if len(self.reason.encode("utf-8")) > 120:
            raise ValueError("succession repair reason too large")

    def bvalue(self) -> dict[bytes, object]:
        return {
            b"kind": self.kind.value,
            b"report_digest": self.report_digest,
            b"accept": 1 if self.accept else 0,
            b"catalog_digest": self.catalog_digest,
            b"scope_digest": self.scope_digest,
            b"request_digest": self.request_digest,
            b"successor_catalog_digest": self.successor_catalog_digest,
            b"active_withdrawal": 1 if self.active_withdrawal else 0,
            b"active_tombstone": 1 if self.active_tombstone else 0,
            b"quarantined": 1 if self.quarantined else 0,
            b"reason": self.reason,
        }


@dataclass(frozen=True)
class SuccessionRepairPolicy:
    require_probe_health: bool = True
    require_journal: bool = True
    allow_stable_without_successor: bool = True


@dataclass(frozen=True)
class SuccessionRepairReport:
    decision_kind: SuccessionRepairDecisionKind
    accept: bool
    reason: str
    catalog_digest: bytes
    successor_catalog_digest: bytes | None
    signal_kinds: tuple[str, ...]
    pressure_digests: tuple[bytes, ...]
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _report(kind: SuccessionRepairDecisionKind, accept: bool, reason: str, *, signals: Iterable[SuccessionRepairSignal], catalog_digest: bytes, successor_catalog_digest: bytes | None = None, pressures: Iterable[bytes] = ()) -> SuccessionRepairReport:
    signal_tuple = tuple(signals)
    signal_kinds = tuple(sorted({signal.kind.value for signal in signal_tuple}))
    pressure_tuple = tuple(sorted(set(pressures)))
    digest = sha256(SUCCESSION_REPAIR_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"reason": reason,
        b"catalog_digest": catalog_digest,
        b"successor_catalog_digest": successor_catalog_digest or b"",
        b"signal_kinds": list(signal_kinds),
        b"pressures": list(pressure_tuple),
    }))
    return SuccessionRepairReport(kind, accept, reason, catalog_digest, successor_catalog_digest, signal_kinds, pressure_tuple, digest)


def assess_succession_repair(signals: Iterable[SuccessionRepairSignal], *, policy: SuccessionRepairPolicy, expected_catalog_digest: bytes, expected_scope_digest: bytes, expected_request_digest: bytes) -> SuccessionRepairReport:
    signal_tuple = tuple(signals)
    if not signal_tuple:
        return _report(SuccessionRepairDecisionKind.HOLD_MISSING_JOURNAL, False, "no succession repair signals supplied", signals=(), catalog_digest=expected_catalog_digest)
    by_kind: dict[SuccessionRepairSignalKind, list[SuccessionRepairSignal]] = {}
    for signal in signal_tuple:
        by_kind.setdefault(signal.kind, []).append(signal)
        if signal.quarantined or not signal.accept:
            return _report(SuccessionRepairDecisionKind.QUARANTINE_SIGNAL, False, "succession repair input signal is not accepted", signals=signal_tuple, catalog_digest=expected_catalog_digest, pressures=(signal.report_digest,))
        if (signal.scope_digest, signal.request_digest) != (expected_scope_digest, expected_request_digest):
            return _report(SuccessionRepairDecisionKind.QUARANTINE_SCOPE_DRIFT, False, "succession repair signal drifted away from exact scope/request", signals=signal_tuple, catalog_digest=expected_catalog_digest, pressures=(signal.report_digest,))
        if signal.catalog_digest != expected_catalog_digest and signal.successor_catalog_digest != expected_catalog_digest:
            return _report(SuccessionRepairDecisionKind.QUARANTINE_CATALOG_DRIFT, False, "succession repair signal does not bind to expected catalog or successor", signals=signal_tuple, catalog_digest=expected_catalog_digest, pressures=(signal.report_digest,))
        if signal.active_tombstone or signal.kind is SuccessionRepairSignalKind.TOMBSTONE:
            return _report(SuccessionRepairDecisionKind.QUARANTINE_ACTIVE_TOMBSTONE, False, "active tombstone blocks service repair", signals=signal_tuple, catalog_digest=expected_catalog_digest, pressures=(signal.report_digest,))

    successor = by_kind.get(SuccessionRepairSignalKind.SUCCESSOR_CATALOG, [])
    withdrawal = by_kind.get(SuccessionRepairSignalKind.WITHDRAWAL, [])
    journal = by_kind.get(SuccessionRepairSignalKind.CONTINUITY_JOURNAL, [])
    probe = by_kind.get(SuccessionRepairSignalKind.PROBE_LOOP, [])

    if policy.require_journal and not journal:
        return _report(SuccessionRepairDecisionKind.HOLD_MISSING_JOURNAL, False, "no continuity journal signal for repair", signals=signal_tuple, catalog_digest=expected_catalog_digest)
    if policy.require_probe_health and not probe:
        return _report(SuccessionRepairDecisionKind.HOLD_MISSING_PROBE_HEALTH, False, "no probe-loop health signal for repair", signals=signal_tuple, catalog_digest=expected_catalog_digest)
    if withdrawal and not successor:
        return _report(SuccessionRepairDecisionKind.QUARANTINE_WITHDRAWAL_WITHOUT_SUCCESSOR, False, "withdrawal cannot repair service without successor evidence", signals=signal_tuple, catalog_digest=expected_catalog_digest, pressures=(item.report_digest for item in withdrawal))
    if successor:
        successor_digests = {item.successor_catalog_digest for item in successor if item.successor_catalog_digest != ZERO_DIGEST}
        if len(successor_digests) != 1:
            return _report(SuccessionRepairDecisionKind.QUARANTINE_CATALOG_DRIFT, False, "successor repair has ambiguous successor catalog digests", signals=signal_tuple, catalog_digest=expected_catalog_digest, pressures=(item.report_digest for item in successor))
        successor_digest = next(iter(successor_digests))
        return _report(SuccessionRepairDecisionKind.ACCEPT_SUCCESSOR_REPAIR, True, "successor repair accepted with journal and probe pressure", signals=signal_tuple, catalog_digest=expected_catalog_digest, successor_catalog_digest=successor_digest)
    if policy.allow_stable_without_successor:
        return _report(SuccessionRepairDecisionKind.ACCEPT_STABLE_NO_REPAIR_NEEDED, True, "stable catalog has continuity journal and probe health", signals=signal_tuple, catalog_digest=expected_catalog_digest)
    return _report(SuccessionRepairDecisionKind.HOLD_MISSING_SUCCESSOR, False, "successor required but absent", signals=signal_tuple, catalog_digest=expected_catalog_digest)
