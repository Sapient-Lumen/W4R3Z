"""Evidence-GC join across custody, tombstones, witnesses, and revocations.

``evidencegc.py`` can retain or drop typed evidence once it is already an
``EvidenceItem``.  The riskier seam is upstream: custody audits, tombstone mesh
reports, witness caches, and revocation-head pressure all produce differently
shaped observations.  If those observations are not normalized conservatively,
soft convenience evidence can bury hard negative evidence.

This module synthesizes local evidence items from those pressure reports, then
runs the ordinary GC pass.  It is not durable storage, deletion consensus,
revocation consensus, or a custody protocol.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .custodyaudit import CustodyAuditDecisionKind, CustodyAuditReport
from .evidencegc import EvidenceGcPolicy, EvidenceGcReport, EvidenceItem, EvidenceKind, collect_evidence_gc
from .ids import DOMAIN, sha256
from .revocation_pressure import RevocationHeadVerdict
from .tombmesh import TombMeshReport
from .witnesscache import WitnessCacheDecisionKind, WitnessCacheSummary

CUSTODY_GC_DOMAIN = DOMAIN + b":custody-gc-v1:"


class CustodyGcDecisionKind(str, Enum):
    KEEP_WITH_NEGATIVE_PRESSURE = "keep_with_negative_pressure"
    QUARANTINE_SYNTHESIZED_CONFLICT = "quarantine_synthesized_conflict"
    KEEP_ORDINARY_GC = "keep_ordinary_gc"
    EMPTY = "empty"


@dataclass(frozen=True)
class CustodyGcDecision:
    kind: CustodyGcDecisionKind
    ok: bool
    reason: str


@dataclass(frozen=True)
class CustodyGcReport:
    synthesized_items: tuple[EvidenceItem, ...]
    gc_report: EvidenceGcReport
    negative_pressure_count: int
    decision: CustodyGcDecision
    report_digest: bytes

    @property
    def kept(self) -> tuple[EvidenceItem, ...]:
        return self.gc_report.kept

    @property
    def dropped(self) -> tuple[EvidenceItem, ...]:
        return self.gc_report.dropped


def _item(kind: EvidenceKind, scope: bytes, obj: bytes, family: str, path: str, now: int, *, sequence: int = 0, note: str = "", byte_cost: int = 192) -> EvidenceItem:
    return EvidenceItem(kind, scope, obj, family, path, now, now + 7 * 24 * 3600, byte_cost=byte_cost, sequence=sequence, note=note[:160])


def _custody_items(report: CustodyAuditReport, *, now: int) -> tuple[EvidenceItem, ...]:
    scope = report.challenge.target
    family = "+".join(sorted(report.proof_families)) or "custody-none"
    path = "custody-audit"
    if report.decision.accept:
        return (_item(EvidenceKind.CUSTODY_PROOF, scope, report.transcript_digest, family, path, now, note=report.decision.kind.value),)
    if report.decision.kind in {
        CustodyAuditDecisionKind.QUARANTINE_FALSE_PROOF,
        CustodyAuditDecisionKind.QUARANTINE_REPLAY_PRESSURE,
        CustodyAuditDecisionKind.QUARANTINE_CONTRACT_GAP,
    }:
        return (_item(EvidenceKind.PROVIDER_FALSE, scope, report.transcript_digest, family, path, now, note=report.decision.kind.value),)
    if report.useful_refusals:
        return (_item(EvidenceKind.USEFUL_REFUSAL, scope, report.transcript_digest, family, path, now, note=report.decision.kind.value),)
    return ()


def _tombmesh_items(report: TombMeshReport, *, now: int) -> tuple[EvidenceItem, ...]:
    if not report.live_tombstone_count:
        return ()
    family = "+".join(sorted(report.tombstone_families)) or "tombstone-none"
    path = "+".join(sorted(report.witness_families)) or "tombstone-path"
    return (_item(EvidenceKind.TOMBSTONE, report.target_commitment, report.transcript_digest, family, path, now, sequence=report.newest_tombstone_seq or 0, note=report.decision.kind.value, byte_cost=256),)


def _witness_items(summary: WitnessCacheSummary, *, now: int) -> tuple[EvidenceItem, ...]:
    family = "+".join(sorted(summary.family_weights)) or "witness-none"
    if summary.decision.kind is WitnessCacheDecisionKind.QUARANTINE_CONTRADICTION:
        return (_item(EvidenceKind.MUTABLE_FORK, summary.target_commitment, summary.transcript_digest, family, "witness-cache", now, note=summary.decision.kind.value),)
    if summary.decision.kind is WitnessCacheDecisionKind.PRESERVE_DIVERSE_EVIDENCE:
        return (_item(EvidenceKind.MUTABLE_LATEST, summary.target_commitment, summary.transcript_digest, family, "witness-cache", now, note=summary.decision.kind.value),)
    return ()


def _revocation_items(verdict: RevocationHeadVerdict, *, now: int) -> tuple[EvidenceItem, ...]:
    # The authority key is not a 32-byte scope digest for all future uses, so bind
    # it into the evidence namespace explicitly.
    scope = sha256(CUSTODY_GC_DOMAIN + b":revocation-authority:" + verdict.authority_public_key)
    kind = EvidenceKind.CAPABILITY_REVOCATION if verdict.risky or verdict.accepted else EvidenceKind.USEFUL_REFUSAL
    return (_item(kind, scope, verdict.head_hash, "revocation-authority", "revocation-head", now, sequence=verdict.sequence, note=verdict.kind.value, byte_cost=256),)


def collect_joined_evidence_gc(
    base_items: Iterable[EvidenceItem] = (),
    *,
    custody_reports: Iterable[CustodyAuditReport] = (),
    tomb_mesh_reports: Iterable[TombMeshReport] = (),
    witness_summaries: Iterable[WitnessCacheSummary] = (),
    revocation_verdicts: Iterable[RevocationHeadVerdict] = (),
    now: int,
    policy: EvidenceGcPolicy | None = None,
) -> CustodyGcReport:
    synthesized: list[EvidenceItem] = []
    negative_pressure = 0
    for report in custody_reports:
        items = _custody_items(report, now=now)
        synthesized.extend(items)
        if report.decision.kind.value.startswith("quarantine_"):
            negative_pressure += 1
    for report in tomb_mesh_reports:
        items = _tombmesh_items(report, now=now)
        synthesized.extend(items)
        if report.blocks_resurrection:
            negative_pressure += 1
    for summary in witness_summaries:
        items = _witness_items(summary, now=now)
        synthesized.extend(items)
        if summary.decision.kind is WitnessCacheDecisionKind.QUARANTINE_CONTRADICTION:
            negative_pressure += 1
    for verdict in revocation_verdicts:
        items = _revocation_items(verdict, now=now)
        synthesized.extend(items)
        if verdict.risky:
            negative_pressure += 1

    all_items = tuple(base_items) + tuple(synthesized)
    gc = collect_evidence_gc(all_items, policy=policy, now=now)
    if gc.quarantine_digests:
        decision = CustodyGcDecision(CustodyGcDecisionKind.QUARANTINE_SYNTHESIZED_CONFLICT, False, "evidence GC saw conflicting synthesized/local digests")
    elif negative_pressure:
        decision = CustodyGcDecision(CustodyGcDecisionKind.KEEP_WITH_NEGATIVE_PRESSURE, True, "negative custody/tombstone/witness/revocation pressure survived normalization")
    elif not all_items:
        decision = CustodyGcDecision(CustodyGcDecisionKind.EMPTY, True, "no evidence supplied")
    else:
        decision = CustodyGcDecision(CustodyGcDecisionKind.KEEP_ORDINARY_GC, True, "ordinary evidence GC completed without negative pressure")
    digest = sha256(CUSTODY_GC_DOMAIN + b":report:" + bencode({
        b"synthesized": [item.digest for item in synthesized],
        b"gc": gc.report_digest,
        b"negative": negative_pressure,
        b"decision": decision.kind.value,
    }))
    return CustodyGcReport(tuple(synthesized), gc, negative_pressure, decision, digest)
