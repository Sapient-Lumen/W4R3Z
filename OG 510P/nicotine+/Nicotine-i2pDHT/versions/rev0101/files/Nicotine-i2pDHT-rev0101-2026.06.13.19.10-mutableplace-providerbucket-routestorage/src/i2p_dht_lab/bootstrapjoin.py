"""Joined bootstrap pressure for peer books, negative answers, live probes, and egress.

A future I2P DHT needs many entrances, but every entrance surface can be
captured: peer books can be stale, empty answers can be convenient lies, live
probes can leak interest, and outbound probing can exceed local metadata
budgets.  This module joins those surfaces so one local success cannot silently
move the bootstrap state machine by itself.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .absencegate import AbsenceAssessment, AbsenceDecisionKind
from .bencode import bencode
from .egressmeter import EgressWindowReport
from .ids import DOMAIN, sha256
from .liveprobe import LiveProbeReport
from .livesmoke import SamLiveSmokeReport
from .peerbook import PeerBookView

BOOTSTRAP_JOIN_DOMAIN = DOMAIN + b":bootstrap-join-v1:"


class BootstrapJoinDecisionKind(str, Enum):
    ACCEPT_BOOTSTRAP_WINDOW = "accept_bootstrap_window"
    ACCEPT_WITH_CLEAN_ROUTER_SKIP = "accept_with_clean_router_skip"
    CONTINUE_NEEDS_PEERBOOK = "continue_needs_peerbook"
    CONTINUE_NEEDS_LIVE_PROBE = "continue_needs_live_probe"
    CONTINUE_ABSENCE_PRESSURE = "continue_absence_pressure"
    QUARANTINE_PEERBOOK_CAPTURE = "quarantine_peerbook_capture"
    QUARANTINE_ABSENCE_CONFLICT = "quarantine_absence_conflict"
    QUARANTINE_EGRESS_BUDGET = "quarantine_egress_budget"
    QUARANTINE_LIVE_PROBE = "quarantine_live_probe"


@dataclass(frozen=True)
class BootstrapJoinPolicy:
    min_live_probes: int = 1
    allow_clean_router_skip: bool = True
    allow_soft_negative_cache: bool = False

    def validate(self) -> None:
        if self.min_live_probes < 0:
            raise ValueError("bootstrap join min_live_probes cannot be negative")


@dataclass(frozen=True)
class BootstrapJoinReport:
    decision_kind: BootstrapJoinDecisionKind
    accept: bool
    reason: str
    selected_peer_count: int
    live_probe_count: int
    clean_skip_count: int
    transcript_digest: bytes
    pressure_digests: tuple[bytes, ...]

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _probe_ok(report: LiveProbeReport | SamLiveSmokeReport) -> bool:
    if isinstance(report, LiveProbeReport):
        return report.ok and not report.clean_skip and not report.quarantined
    return report.accept and not report.skipped and not report.quarantined


def _probe_clean_skip(report: LiveProbeReport | SamLiveSmokeReport) -> bool:
    if isinstance(report, LiveProbeReport):
        return report.ok and report.clean_skip and not report.quarantined
    return report.accept and report.skipped and not report.quarantined


def _probe_bad(report: LiveProbeReport | SamLiveSmokeReport) -> bool:
    if isinstance(report, LiveProbeReport):
        return report.quarantined or not report.ok
    return report.quarantined or not report.accept


def assess_bootstrap_join(
    *,
    peerbook: PeerBookView,
    live_probes: Iterable[LiveProbeReport | SamLiveSmokeReport] = (),
    absence: AbsenceAssessment | None = None,
    egress: EgressWindowReport | None = None,
    policy: BootstrapJoinPolicy | None = None,
) -> BootstrapJoinReport:
    """Join bootstrap evidence before accepting a fresh entrance set."""
    policy = policy or BootstrapJoinPolicy()
    policy.validate()
    probes = tuple(live_probes)
    pressures: list[bytes] = []

    if egress is not None and (not egress.accept or egress.quarantined):
        pressures.append(egress.report_digest)
        return _report(BootstrapJoinDecisionKind.QUARANTINE_EGRESS_BUDGET, False, "bootstrap egress window failed before side effects", peerbook, probes, pressures)
    if peerbook.quarantined:
        pressures.append(peerbook.report_digest)
        return _report(BootstrapJoinDecisionKind.QUARANTINE_PEERBOOK_CAPTURE, False, peerbook.reason, peerbook, probes, pressures)
    if not peerbook.accept or _selected_count(peerbook) == 0:
        pressures.append(peerbook.report_digest)
        return _report(BootstrapJoinDecisionKind.CONTINUE_NEEDS_PEERBOOK, False, peerbook.reason, peerbook, probes, pressures)

    if absence is not None:
        if absence.quarantined or absence.decision_kind is AbsenceDecisionKind.QUARANTINE_POSITIVE_CONFLICT:
            pressures.append(absence.report_digest)
            return _report(BootstrapJoinDecisionKind.QUARANTINE_ABSENCE_CONFLICT, False, absence.reason, peerbook, probes, pressures)
        if absence.accept and absence.decision_kind is not AbsenceDecisionKind.ACCEPT_DURABLE_TOMBSTONE_ABSENCE and not policy.allow_soft_negative_cache:
            pressures.append(absence.report_digest)
            return _report(BootstrapJoinDecisionKind.CONTINUE_ABSENCE_PRESSURE, False, "soft negative cache cannot close bootstrap join", peerbook, probes, pressures)
        if not absence.accept and absence.decision_kind in {AbsenceDecisionKind.CONTINUE_MORE_PATHS, AbsenceDecisionKind.CONTINUE_TIMEOUT_PRESSURE}:
            pressures.append(absence.report_digest)
            return _report(BootstrapJoinDecisionKind.CONTINUE_ABSENCE_PRESSURE, False, absence.reason, peerbook, probes, pressures)

    bad = tuple(report for report in probes if _probe_bad(report))
    if bad:
        pressures.extend(report.report_digest if isinstance(report, LiveProbeReport) else report.transcript_digest for report in bad)
        return _report(BootstrapJoinDecisionKind.QUARANTINE_LIVE_PROBE, False, "one or more live probe reports were rejected or quarantined", peerbook, probes, pressures)
    live_count = sum(1 for report in probes if _probe_ok(report))
    skip_count = sum(1 for report in probes if _probe_clean_skip(report))
    if live_count < policy.min_live_probes:
        if skip_count and policy.allow_clean_router_skip:
            return _report(BootstrapJoinDecisionKind.ACCEPT_WITH_CLEAN_ROUTER_SKIP, True, "peerbook is accepted and local router absence skipped cleanly", peerbook, probes, pressures)
        return _report(BootstrapJoinDecisionKind.CONTINUE_NEEDS_LIVE_PROBE, False, "bootstrap needs more live reachability evidence", peerbook, probes, pressures)
    return _report(BootstrapJoinDecisionKind.ACCEPT_BOOTSTRAP_WINDOW, True, "peerbook, live probe, absence, and egress pressures are locally coherent", peerbook, probes, pressures)


def _selected_count(peerbook: PeerBookView) -> int:
    return len(peerbook.selected_node_ids)


def _report(kind: BootstrapJoinDecisionKind, accept: bool, reason: str, peerbook: PeerBookView, probes: tuple[LiveProbeReport | SamLiveSmokeReport, ...], pressures: Iterable[bytes]) -> BootstrapJoinReport:
    probe_digests = tuple(report.report_digest if isinstance(report, LiveProbeReport) else report.transcript_digest for report in probes)
    pressure_tuple = tuple(sorted(pressures))
    live_count = sum(1 for report in probes if _probe_ok(report))
    skip_count = sum(1 for report in probes if _probe_clean_skip(report))
    digest = sha256(BOOTSTRAP_JOIN_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"peerbook": peerbook.report_digest,
        b"probes": probe_digests,
        b"pressures": pressure_tuple,
        b"selected": _selected_count(peerbook),
        b"live_count": live_count,
        b"skip_count": skip_count,
    }))
    return BootstrapJoinReport(kind, accept, reason, _selected_count(peerbook), live_count, skip_count, digest, pressure_tuple)
