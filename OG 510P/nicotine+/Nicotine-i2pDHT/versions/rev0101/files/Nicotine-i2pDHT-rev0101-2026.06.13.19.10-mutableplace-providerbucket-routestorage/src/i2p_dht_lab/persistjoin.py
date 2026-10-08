"""Joined persistence/restart gate for sticky DHT memory.

rev0033 takes the rev0032 joined reports and pushes them across the restart
boundary.  A persist snapshot can reload, a journal prefix can replay, a
checkpoint can verify, a scope ledger can accept, and store debt can look paid;
that still does not mean sticky state should advance after restart.  The join
must bind journal tip, hard-negative preservation, scope observations, and store
repair debt before convenient local memory becomes durable local memory.

This is local pressure only.  It is not a production database format or global
truth protocol.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .bencode import bencode
from .checkpointlane import CheckpointAssessment, CheckpointDecisionKind, StateCheckpoint
from .ids import DOMAIN, sha256
from .journallane import JournalReplayDecisionKind, JournalReplayReport
from .persistlane import PersistLoadDecisionKind, PersistLoadReport
from .scopeledger import ScopeLedgerReport
from .storedebt import StoreDebtDecisionKind, StoreDebtReport

PERSIST_JOIN_DOMAIN = DOMAIN + b":persist-join-v1:"
ZERO_DIGEST = b"\x00" * 32


class PersistJoinDecisionKind(str, Enum):
    ACCEPT_DURABLE_JOIN = "accept_durable_join"
    ACCEPT_WITH_CRASH_TAIL_WATCH = "accept_with_crash_tail_watch"
    HOLD_SCOPE_PROOF_DEBT = "hold_scope_proof_debt"
    HOLD_STORE_REPAIR_DEBT = "hold_store_repair_debt"
    QUARANTINE_PERSIST_RELOAD = "quarantine_persist_reload"
    QUARANTINE_JOURNAL_REPLAY = "quarantine_journal_replay"
    QUARANTINE_CHECKPOINT = "quarantine_checkpoint"
    QUARANTINE_SCOPE_LEDGER = "quarantine_scope_ledger"
    QUARANTINE_STORE_DEBT = "quarantine_store_debt"
    QUARANTINE_CHECKPOINT_JOURNAL_TIP = "quarantine_checkpoint_journal_tip"
    QUARANTINE_HARD_NEGATIVE_DROP = "quarantine_hard_negative_drop"
    QUARANTINE_DIGEST_REPLAY = "quarantine_digest_replay"


@dataclass(frozen=True)
class PersistJoinPolicy:
    require_checkpoint_tip_match: bool = True
    required_hard_negative_count: int = 0
    allow_crash_tail_watch: bool = True
    allow_scope_proof_debt_watch: bool = False
    allow_store_repair_debt_watch: bool = False

    def validate(self) -> None:
        if self.required_hard_negative_count < 0:
            raise ValueError("required hard-negative count cannot be negative")


@dataclass(frozen=True)
class PersistJoinReport:
    decision_kind: PersistJoinDecisionKind
    accept: bool
    reason: str
    persist_report_digest: bytes
    journal_report_digest: bytes
    checkpoint_report_digest: bytes
    scope_report_digest: bytes
    store_report_digest: bytes
    checkpoint_digest: bytes
    journal_tip_digest: bytes
    pressure_digests: tuple[bytes, ...]
    hard_negative_count: int
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _report(
    kind: PersistJoinDecisionKind,
    accept: bool,
    reason: str,
    *,
    persist_report: PersistLoadReport,
    journal_report: JournalReplayReport,
    checkpoint_report: CheckpointAssessment,
    scope_report: ScopeLedgerReport,
    store_report: StoreDebtReport,
    checkpoint: StateCheckpoint | None,
    pressures: Iterable[bytes] = (),
) -> PersistJoinReport:
    pressure_t = tuple(sorted(set(pressures)))
    checkpoint_digest = ZERO_DIGEST if checkpoint is None else checkpoint.checkpoint_digest
    journal_tip = journal_report.last_entry_digest
    digest = sha256(PERSIST_JOIN_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"persist": persist_report.report_digest,
        b"journal": journal_report.report_digest,
        b"checkpoint_report": checkpoint_report.report_digest,
        b"scope": scope_report.report_digest,
        b"store": store_report.report_digest,
        b"checkpoint": checkpoint_digest,
        b"journal_tip": journal_tip,
        b"pressures": pressure_t,
        b"hard_negative_count": persist_report.hard_negative_count,
        b"reason": reason,
    }))
    return PersistJoinReport(
        kind,
        accept,
        reason,
        persist_report.report_digest,
        journal_report.report_digest,
        checkpoint_report.report_digest,
        scope_report.report_digest,
        store_report.report_digest,
        checkpoint_digest,
        journal_tip,
        pressure_t,
        persist_report.hard_negative_count,
        digest,
    )


def assess_persist_join(
    *,
    persist_report: PersistLoadReport,
    journal_report: JournalReplayReport,
    checkpoint_report: CheckpointAssessment,
    scope_report: ScopeLedgerReport,
    store_report: StoreDebtReport,
    checkpoint: StateCheckpoint | None = None,
    policy: PersistJoinPolicy | None = None,
    previously_seen_report_digests: Iterable[bytes] = (),
) -> PersistJoinReport:
    """Join restart evidence before sticky local state advances.

    The function deliberately accepts already-typed reports.  rev0033 is about
    the boundary between valid component reports, not about revalidating their
    internals.  It checks replay, local accept/quarantine state, journal-tip
    binding, hard-negative survival, proof debt, and store repair debt.
    """
    policy = policy or PersistJoinPolicy()
    policy.validate()
    report_digests = (
        persist_report.report_digest,
        journal_report.report_digest,
        checkpoint_report.report_digest,
        scope_report.report_digest,
        store_report.report_digest,
    )
    prior = set(previously_seen_report_digests)
    if any(digest in prior for digest in report_digests) or len(set(report_digests)) != len(report_digests):
        return _report(PersistJoinDecisionKind.QUARANTINE_DIGEST_REPLAY, False, "one or more joined restart reports were replayed or aliased", persist_report=persist_report, journal_report=journal_report, checkpoint_report=checkpoint_report, scope_report=scope_report, store_report=store_report, checkpoint=checkpoint, pressures=report_digests)
    if not persist_report.accept or persist_report.quarantined:
        return _report(PersistJoinDecisionKind.QUARANTINE_PERSIST_RELOAD, False, "persist reload did not accept before joined restart", persist_report=persist_report, journal_report=journal_report, checkpoint_report=checkpoint_report, scope_report=scope_report, store_report=store_report, checkpoint=checkpoint, pressures=persist_report.quarantine_digests)
    if not journal_report.accept or journal_report.quarantined:
        return _report(PersistJoinDecisionKind.QUARANTINE_JOURNAL_REPLAY, False, "journal replay did not accept before joined restart", persist_report=persist_report, journal_report=journal_report, checkpoint_report=checkpoint_report, scope_report=scope_report, store_report=store_report, checkpoint=checkpoint, pressures=journal_report.quarantined_entry_digests)
    if not checkpoint_report.decision.accept or checkpoint_report.quarantined:
        return _report(PersistJoinDecisionKind.QUARANTINE_CHECKPOINT, False, "checkpoint assessment did not accept before joined restart", persist_report=persist_report, journal_report=journal_report, checkpoint_report=checkpoint_report, scope_report=scope_report, store_report=store_report, checkpoint=checkpoint, pressures=(checkpoint_report.checkpoint_digest, *checkpoint_report.hard_fact_drops, *checkpoint_report.conflict_fact_digests))
    if not scope_report.accept or scope_report.quarantined:
        return _report(PersistJoinDecisionKind.QUARANTINE_SCOPE_LEDGER, False, "scope ledger did not accept before durable restart join", persist_report=persist_report, journal_report=journal_report, checkpoint_report=checkpoint_report, scope_report=scope_report, store_report=store_report, checkpoint=checkpoint, pressures=scope_report.pressure_digests)
    if store_report.quarantined:
        return _report(PersistJoinDecisionKind.QUARANTINE_STORE_DEBT, False, "store debt report is quarantined before durable restart join", persist_report=persist_report, journal_report=journal_report, checkpoint_report=checkpoint_report, scope_report=scope_report, store_report=store_report, checkpoint=checkpoint, pressures=store_report.pressure_digests or store_report.tombstone_digests)
    if policy.require_checkpoint_tip_match and checkpoint is not None and checkpoint.journal_tip_digest != journal_report.last_entry_digest:
        return _report(PersistJoinDecisionKind.QUARANTINE_CHECKPOINT_JOURNAL_TIP, False, "checkpoint journal tip does not match replayed journal tip", persist_report=persist_report, journal_report=journal_report, checkpoint_report=checkpoint_report, scope_report=scope_report, store_report=store_report, checkpoint=checkpoint, pressures=(checkpoint.journal_tip_digest, journal_report.last_entry_digest))
    if persist_report.hard_negative_count < policy.required_hard_negative_count:
        return _report(PersistJoinDecisionKind.QUARANTINE_HARD_NEGATIVE_DROP, False, "persisted/replayed restart view lost required hard-negative evidence", persist_report=persist_report, journal_report=journal_report, checkpoint_report=checkpoint_report, scope_report=scope_report, store_report=store_report, checkpoint=checkpoint, pressures=persist_report.quarantine_digests)
    if scope_report.open_obligation_count and not policy.allow_scope_proof_debt_watch:
        return _report(PersistJoinDecisionKind.HOLD_SCOPE_PROOF_DEBT, False, "scope ledger carries proof debt after restart", persist_report=persist_report, journal_report=journal_report, checkpoint_report=checkpoint_report, scope_report=scope_report, store_report=store_report, checkpoint=checkpoint, pressures=scope_report.pressure_digests or scope_report.observation_digests)
    if store_report.decision_kind is not StoreDebtDecisionKind.ACCEPT_NO_STORE_DEBT and not policy.allow_store_repair_debt_watch:
        return _report(PersistJoinDecisionKind.HOLD_STORE_REPAIR_DEBT, False, "store repair/custody debt still exists after restart", persist_report=persist_report, journal_report=journal_report, checkpoint_report=checkpoint_report, scope_report=scope_report, store_report=store_report, checkpoint=checkpoint, pressures=store_report.pressure_digests or store_report.observation_digests)
    if journal_report.decision_kind is JournalReplayDecisionKind.ACCEPT_REPLAYED_WITH_CRASH_TAIL:
        return _report(PersistJoinDecisionKind.ACCEPT_WITH_CRASH_TAIL_WATCH if policy.allow_crash_tail_watch else PersistJoinDecisionKind.QUARANTINE_JOURNAL_REPLAY, policy.allow_crash_tail_watch, "journal replay accepted a linked prefix with crash-tail bytes still watch-listed", persist_report=persist_report, journal_report=journal_report, checkpoint_report=checkpoint_report, scope_report=scope_report, store_report=store_report, checkpoint=checkpoint, pressures=journal_report.quarantined_entry_digests)
    if persist_report.decision_kind is PersistLoadDecisionKind.ACCEPT_COMPACTED_WITH_NEGATIVES or checkpoint_report.decision.kind is CheckpointDecisionKind.WATCH_GENERATION_GAP:
        return _report(PersistJoinDecisionKind.ACCEPT_DURABLE_JOIN, True, "durable join accepted with compaction/gap already surfaced by component reports", persist_report=persist_report, journal_report=journal_report, checkpoint_report=checkpoint_report, scope_report=scope_report, store_report=store_report, checkpoint=checkpoint)
    return _report(PersistJoinDecisionKind.ACCEPT_DURABLE_JOIN, True, "restart evidence is durable, linked, scoped, and store-debt clean", persist_report=persist_report, journal_report=journal_report, checkpoint_report=checkpoint_report, scope_report=scope_report, store_report=store_report, checkpoint=checkpoint)
