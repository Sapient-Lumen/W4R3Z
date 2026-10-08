from __future__ import annotations

from dataclasses import replace

from i2p_dht_lab.continuityjournal import (
    ContinuityEvidenceKind,
    ContinuityJournalDecisionKind,
    ContinuityJournalRecord,
    ZERO_DIGEST,
    assess_continuity_journal,
    compact_continuity_journal,
)
from i2p_dht_lab.continuityjournalfold import audit_continuityjournal_fold
from i2p_dht_lab.identity import DhtKeypair
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.probeloop import (
    ProbeLoopDecisionKind,
    ProbeLoopObservation,
    ProbeLoopObservationKind,
    ProbeLoopPolicy,
    assess_probe_loop,
)
from i2p_dht_lab.successionrepair import (
    SuccessionRepairDecisionKind,
    SuccessionRepairPolicy,
    SuccessionRepairSignal,
    SuccessionRepairSignalKind,
    assess_succession_repair,
)


def d(label: str) -> bytes:
    return sha256(("rev0039:" + label).encode("utf-8"))


def kp(n: int = 39) -> DhtKeypair:
    return DhtKeypair.from_seed(bytes([n]) * 32)


def record(seq: int, prev: bytes, report: bytes | None = None, *, kind: ContinuityEvidenceKind = ContinuityEvidenceKind.SERVICE_ADVANCED, catalog: bytes | None = None, scope: bytes | None = None, request: bytes | None = None) -> ContinuityJournalRecord:
    return ContinuityJournalRecord.create(
        keypair=kp(),
        sequence=seq,
        previous_record_digest=prev,
        continuity_report_digest=report or d(f"report-{seq}"),
        catalog_digest=catalog or d("catalog"),
        scope_digest=scope or d("scope"),
        request_digest=request or d("request"),
        service_name="head_watch",
        evidence_kind=kind,
        issued_at=100 + seq,
    )


def test_continuity_journal_accepts_restart_memory_and_preserves_hard_negatives() -> None:
    r0 = record(0, ZERO_DIGEST, kind=ContinuityEvidenceKind.SERVICE_ADVANCED)
    r1 = record(1, r0.record_digest, report=d("withdrawal-report"), kind=ContinuityEvidenceKind.ACTIVE_WITHDRAWAL)
    r2 = record(2, r1.record_digest, kind=ContinuityEvidenceKind.SUCCESSOR_REPAIR)
    report = assess_continuity_journal(
        (r0, r1, r2),
        expected_catalog_digest=d("catalog"),
        expected_scope_digest=d("scope"),
        expected_request_digest=d("request"),
        required_hard_negative_digests=(d("withdrawal-report"),),
    )
    assert report.decision_kind is ContinuityJournalDecisionKind.ACCEPT_JOURNAL_ADVANCE
    assert report.accept
    assert report.hard_negative_count == 1
    compacted = compact_continuity_journal((r0, r1, r2), keep_last_positive=1)
    assert r1 in compacted
    assert r2 in compacted
    assert r0 not in compacted


def test_continuity_journal_blocks_replay_fork_prev_mismatch_and_scope_drift() -> None:
    r0 = record(0, ZERO_DIGEST)
    r1 = record(1, r0.record_digest)
    assert assess_continuity_journal((r0, r1), expected_catalog_digest=d("catalog"), expected_scope_digest=d("scope"), expected_request_digest=d("request"), previously_seen_report_digests=(d("report-1"),)).decision_kind is ContinuityJournalDecisionKind.QUARANTINE_REPORT_REPLAY

    fork = record(1, r0.record_digest, report=d("fork-report"))
    assert assess_continuity_journal((r0, r1, fork), expected_catalog_digest=d("catalog"), expected_scope_digest=d("scope"), expected_request_digest=d("request")).decision_kind is ContinuityJournalDecisionKind.QUARANTINE_SEQUENCE_FORK

    bad_prev = record(1, d("wrong-prev"))
    assert assess_continuity_journal((r0, bad_prev), expected_catalog_digest=d("catalog"), expected_scope_digest=d("scope"), expected_request_digest=d("request")).decision_kind is ContinuityJournalDecisionKind.QUARANTINE_PREVIOUS_MISMATCH

    drift = record(0, ZERO_DIGEST, scope=d("other-scope"))
    assert assess_continuity_journal((drift,), expected_catalog_digest=d("catalog"), expected_scope_digest=d("scope"), expected_request_digest=d("request")).decision_kind is ContinuityJournalDecisionKind.QUARANTINE_SCOPE_DRIFT


def test_continuity_journal_detects_dropped_required_negative_and_bad_signature() -> None:
    r0 = record(0, ZERO_DIGEST)
    report = assess_continuity_journal((r0,), expected_catalog_digest=d("catalog"), expected_scope_digest=d("scope"), expected_request_digest=d("request"), required_hard_negative_digests=(d("missing-negative"),))
    assert report.decision_kind is ContinuityJournalDecisionKind.QUARANTINE_DROPPED_HARD_NEGATIVE

    tampered = replace(r0, continuity_report_digest=d("tampered"))
    assert assess_continuity_journal((tampered,), expected_catalog_digest=d("catalog"), expected_scope_digest=d("scope"), expected_request_digest=d("request")).decision_kind is ContinuityJournalDecisionKind.QUARANTINE_BAD_SIGNATURE


def obs(label: str, kind: ProbeLoopObservationKind = ProbeLoopObservationKind.HEALTHY, *, source: str = "src-a", path: str = "path-a", raw: int = 0, decoy: int = 0) -> ProbeLoopObservation:
    return ProbeLoopObservation(
        receipt_digest=d("receipt:" + label),
        plan_digest=d("plan"),
        service_name="head_watch",
        kind=kind,
        source_family=source,
        path_family=path,
        raw_key_exposures=raw,
        decoy_count=decoy,
    )


def test_probe_loop_accepts_diverse_health_and_blocks_metadata_family_replay() -> None:
    policy = ProbeLoopPolicy(min_healthy=2, min_source_families=2, min_path_families=2, max_raw_key_exposures=1, min_decoy_count=1)
    good = (obs("a", source="src-a", path="path-a", raw=1, decoy=1), obs("b", source="src-b", path="path-b"), obs("c", ProbeLoopObservationKind.USEFUL_REFUSAL, source="src-c", path="path-c"))
    assert assess_probe_loop(good, policy=policy).decision_kind is ProbeLoopDecisionKind.ACCEPT_PROBE_LOOP_HEALTH
    assert assess_probe_loop((obs("a"),), policy=policy, previously_seen_receipts=(d("receipt:a"),)).decision_kind is ProbeLoopDecisionKind.QUARANTINE_REPLAY
    assert assess_probe_loop((obs("x", raw=2, decoy=3), obs("y", source="src-b", path="path-b")), policy=policy).decision_kind is ProbeLoopDecisionKind.QUARANTINE_RAW_KEY_BUDGET
    assert assess_probe_loop((obs("x", raw=1, decoy=0), obs("y", source="src-b", path="path-b")), policy=policy).decision_kind is ProbeLoopDecisionKind.QUARANTINE_DECOY_SHORTFALL
    mono = (obs("a", source="src-a", path="path-a"), obs("b", source="src-a", path="path-a"), obs("c", source="src-a", path="path-a"))
    assert assess_probe_loop(mono, policy=policy).decision_kind is ProbeLoopDecisionKind.QUARANTINE_FAMILY_MONOCULTURE


def test_probe_loop_holds_refusal_only_and_quarantines_false_service() -> None:
    policy = ProbeLoopPolicy(min_healthy=2, min_source_families=2, min_path_families=2)
    refusal_only = (obs("a", ProbeLoopObservationKind.USEFUL_REFUSAL, source="src-a", path="path-a"), obs("b", ProbeLoopObservationKind.USEFUL_REFUSAL, source="src-b", path="path-b"))
    assert assess_probe_loop(refusal_only, policy=policy).decision_kind is ProbeLoopDecisionKind.HOLD_REFUSAL_ONLY
    false = (obs("a", source="src-a", path="path-a"), obs("b", ProbeLoopObservationKind.FALSE_SERVICE, source="src-b", path="path-b"))
    assert assess_probe_loop(false, policy=policy).decision_kind is ProbeLoopDecisionKind.QUARANTINE_FALSE_SERVICE


def sig(kind: SuccessionRepairSignalKind, label: str, *, catalog: bytes | None = None, successor: bytes | None = None, scope: bytes | None = None, request: bytes | None = None, accept: bool = True, quarantined: bool = False, withdrawal: bool = False, tombstone: bool = False) -> SuccessionRepairSignal:
    return SuccessionRepairSignal(
        kind=kind,
        report_digest=d("sig:" + label),
        accept=accept,
        catalog_digest=catalog or d("catalog"),
        successor_catalog_digest=successor or d("successor") if kind is SuccessionRepairSignalKind.SUCCESSOR_CATALOG else successor or b"\x00" * 32,
        scope_digest=scope or d("scope"),
        request_digest=request or d("request"),
        active_withdrawal=withdrawal,
        active_tombstone=tombstone,
        quarantined=quarantined,
    )


def test_succession_repair_accepts_successor_only_with_journal_and_probe() -> None:
    policy = SuccessionRepairPolicy()
    signals = (
        sig(SuccessionRepairSignalKind.SUCCESSOR_CATALOG, "succ", successor=d("successor")),
        sig(SuccessionRepairSignalKind.WITHDRAWAL, "withdraw", withdrawal=True),
        sig(SuccessionRepairSignalKind.CONTINUITY_JOURNAL, "journal"),
        sig(SuccessionRepairSignalKind.PROBE_LOOP, "probe"),
    )
    report = assess_succession_repair(signals, policy=policy, expected_catalog_digest=d("catalog"), expected_scope_digest=d("scope"), expected_request_digest=d("request"))
    assert report.decision_kind is SuccessionRepairDecisionKind.ACCEPT_SUCCESSOR_REPAIR
    assert report.successor_catalog_digest == d("successor")

    no_probe = tuple(item for item in signals if item.kind is not SuccessionRepairSignalKind.PROBE_LOOP)
    assert assess_succession_repair(no_probe, policy=policy, expected_catalog_digest=d("catalog"), expected_scope_digest=d("scope"), expected_request_digest=d("request")).decision_kind is SuccessionRepairDecisionKind.HOLD_MISSING_PROBE_HEALTH

    no_successor = tuple(item for item in signals if item.kind is not SuccessionRepairSignalKind.SUCCESSOR_CATALOG)
    assert assess_succession_repair(no_successor, policy=policy, expected_catalog_digest=d("catalog"), expected_scope_digest=d("scope"), expected_request_digest=d("request")).decision_kind is SuccessionRepairDecisionKind.QUARANTINE_WITHDRAWAL_WITHOUT_SUCCESSOR


def test_succession_repair_blocks_drift_tombstone_and_bad_signal() -> None:
    policy = SuccessionRepairPolicy()
    base = (sig(SuccessionRepairSignalKind.CONTINUITY_JOURNAL, "journal"), sig(SuccessionRepairSignalKind.PROBE_LOOP, "probe"))
    assert assess_succession_repair(base, policy=policy, expected_catalog_digest=d("catalog"), expected_scope_digest=d("scope"), expected_request_digest=d("request")).decision_kind is SuccessionRepairDecisionKind.ACCEPT_STABLE_NO_REPAIR_NEEDED

    drift = base + (sig(SuccessionRepairSignalKind.SUCCESSOR_CATALOG, "drift", scope=d("other-scope")),)
    assert assess_succession_repair(drift, policy=policy, expected_catalog_digest=d("catalog"), expected_scope_digest=d("scope"), expected_request_digest=d("request")).decision_kind is SuccessionRepairDecisionKind.QUARANTINE_SCOPE_DRIFT

    tomb = base + (sig(SuccessionRepairSignalKind.TOMBSTONE, "tomb", tombstone=True),)
    assert assess_succession_repair(tomb, policy=policy, expected_catalog_digest=d("catalog"), expected_scope_digest=d("scope"), expected_request_digest=d("request")).decision_kind is SuccessionRepairDecisionKind.QUARANTINE_ACTIVE_TOMBSTONE

    bad = base + (sig(SuccessionRepairSignalKind.SUCCESSOR_CATALOG, "bad", accept=False),)
    assert assess_succession_repair(bad, policy=policy, expected_catalog_digest=d("catalog"), expected_scope_digest=d("scope"), expected_request_digest=d("request")).decision_kind is SuccessionRepairDecisionKind.QUARANTINE_SIGNAL


def test_continuityjournalfold_audits_current_revision() -> None:
    report = audit_continuityjournal_fold(".", revision="rev0039", artifact_stem="Nicotine-i2pDHT-rev0039-2026.06.04.06.15-continuityjournal-probeloop-successionrepair")
    assert report.status == "pass"
    assert report.error_count == 0
    assert report.predecessor_status == "pass"
