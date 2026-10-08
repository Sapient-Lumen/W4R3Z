from pathlib import Path

from i2p_dht_lab.foldspine import audit_fold_spine
from i2p_dht_lab.generatorfuzz import GeneratedFuzzDecisionKind, assess_generated_fuzz, generate_fuzz_corpus
from i2p_dht_lab.identity import DhtKeypair
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.journallane import (
    JournalFrame,
    JournalReplayDecisionKind,
    JournalReplayPolicy,
    ZERO_DIGEST as JOURNAL_ZERO,
    replay_journal,
)
from i2p_dht_lab.persistlane import PersistRecord, PersistRecordKind, PersistSnapshot, ZERO_DIGEST
from i2p_dht_lab.refusalloop import RefusalLoopDecisionKind, RefusalLoopPolicy, RefusalWindow, assess_refusal_loop
from i2p_dht_lab.refusalschedule import RefusalScheduleDecisionKind, join_refusal_loop_to_schedule
from i2p_dht_lab.schedjoin import JoinedScheduleDecision, JoinedScheduleDecisionKind, JoinedScheduleReport
from i2p_dht_lab.workmeter import WorkEvent, WorkEventKind, WorkMeterPolicy


def kp(n: int) -> DhtKeypair:
    return DhtKeypair.from_seed(bytes([n]) * 32)


def digest(label: str) -> bytes:
    return sha256(label.encode("utf-8"))


def rec(kind: PersistRecordKind, label: str, *, seq: int = 1, fam: str = "fam-A", path: str = "path-A", now: int = 1_000) -> PersistRecord:
    return PersistRecord(
        kind=kind,
        scope_id=digest("scope"),
        subject_digest=digest(label),
        value_digest=digest(f"{label}-value-{seq}"),
        sequence=seq,
        source_family=fam,
        path_family=path,
        issued_at=now,
        expires_at=now + 10_000,
    )


def snapshot(key: DhtKeypair, *, sequence: int, prev: bytes, records: tuple[PersistRecord, ...], now: int) -> PersistSnapshot:
    return PersistSnapshot.create(keypair=key, sequence=sequence, prev_snapshot_digest=prev, records=records, issued_at=now, ttl=20_000)


def frame(key: DhtKeypair, *, lane: bytes, sequence: int, prev_frame: bytes, snap: PersistSnapshot, now: int) -> JournalFrame:
    return JournalFrame.create(keypair=key, lane_id=lane, sequence=sequence, prev_frame_digest=prev_frame, snapshot=snap, issued_at=now, ttl=20_000)


def event(kind: WorkEventKind, label: str, *, garden: DhtKeypair, fam: str, path: str, now: int, unit: int = 1) -> WorkEvent:
    return WorkEvent.create(
        garden=garden,
        event_kind=kind,
        scope_id=digest("work-scope"),
        subject_digest=digest(label),
        source_family=fam,
        path_family=path,
        unit_cost=unit,
        issued_at=now,
        ttl=1_000,
    )


def joined(kind: JoinedScheduleDecisionKind, *, refused: dict[str, int] | None = None, protected_started: int = 1) -> JoinedScheduleReport:
    refused = refused or {}
    return JoinedScheduleReport(
        candidate_decisions=(),
        queue_plan=None,
        useful_refusals_by_family=refused,
        protected_authorized_count=protected_started,
        protected_started_count=protected_started,
        decision=JoinedScheduleDecision(kind, kind is not JoinedScheduleDecisionKind.STARVATION_PROTECTED_WORK, kind.value),
        transcript_digest=digest("joined-" + kind.value + repr(sorted(refused.items()))),
    )


def test_journallane_replays_two_linked_snapshots() -> None:
    now = 100_000
    key = kp(21)
    lane = digest("journal-lane")
    s1 = snapshot(key, sequence=1, prev=ZERO_DIGEST, records=(rec(PersistRecordKind.MUTABLE_HEAD, "head", seq=1, now=now),), now=now)
    f1 = frame(key, lane=lane, sequence=1, prev_frame=JOURNAL_ZERO, snap=s1, now=now)
    s2 = snapshot(key, sequence=2, prev=s1.snapshot_digest, records=(rec(PersistRecordKind.MUTABLE_HEAD, "head", seq=2, now=now + 1), rec(PersistRecordKind.TOMBSTONE, "bad-provider", seq=1, fam="fam-B", path="path-B", now=now + 1)), now=now + 1)
    f2 = frame(key, lane=lane, sequence=2, prev_frame=f1.frame_digest, snap=s2, now=now + 1)

    report = replay_journal((f1.to_bytes(), f2.to_bytes()), previous_snapshot=None, now=now + 2)

    assert report.decision.kind is JournalReplayDecisionKind.ACCEPT_JOURNAL_REPLAY
    assert report.accepted
    assert report.loaded_snapshot is not None
    assert report.loaded_snapshot.snapshot_digest == s2.snapshot_digest
    assert report.hard_negative_count == 1
    assert report.accepted_frame_digests == (f1.frame_digest, f2.frame_digest)


def test_journallane_repairs_truncated_tail_without_losing_last_good_frame() -> None:
    now = 110_000
    key = kp(22)
    lane = digest("journal-tail")
    s1 = snapshot(key, sequence=1, prev=ZERO_DIGEST, records=(rec(PersistRecordKind.PROVIDER_FALSE, "liar", seq=1, now=now),), now=now)
    f1 = frame(key, lane=lane, sequence=1, prev_frame=JOURNAL_ZERO, snap=s1, now=now)

    report = replay_journal((f1.to_bytes(), b"d1:a1:b"), previous_snapshot=None, now=now + 1)

    assert report.decision.kind is JournalReplayDecisionKind.ACCEPT_REPAIRED_TRUNCATED_TAIL
    assert report.accepted
    assert report.repaired_tail_count == 1
    assert report.loaded_snapshot is not None
    assert report.loaded_snapshot.snapshot_digest == s1.snapshot_digest


def test_journallane_quarantines_prev_frame_mismatch_and_snapshot_tamper() -> None:
    now = 120_000
    key = kp(23)
    lane = digest("journal-mismatch")
    s1 = snapshot(key, sequence=1, prev=ZERO_DIGEST, records=(rec(PersistRecordKind.MUTABLE_HEAD, "head", now=now),), now=now)
    f1 = frame(key, lane=lane, sequence=1, prev_frame=digest("wrong-frame"), snap=s1, now=now)
    report = replay_journal((f1.to_bytes(),), previous_snapshot=None, now=now + 1)
    assert report.decision.kind is JournalReplayDecisionKind.QUARANTINE_PREV_FRAME_MISMATCH
    assert report.quarantined

    good = frame(key, lane=lane, sequence=1, prev_frame=JOURNAL_ZERO, snap=s1, now=now)
    raw = bytearray(good.to_bytes())
    raw[-10] = raw[-10] ^ 1
    tampered = replay_journal((bytes(raw),), previous_snapshot=None, now=now + 1, policy=JournalReplayPolicy(allow_truncated_tail_repair=False))
    assert tampered.decision.kind in {JournalReplayDecisionKind.QUARANTINE_FRAME_PARSE, JournalReplayDecisionKind.QUARANTINE_BAD_FRAME_SIGNATURE}


def test_journallane_quarantines_hard_negative_loss_after_restart() -> None:
    now = 130_000
    key = kp(24)
    lane = digest("journal-negative")
    previous = snapshot(key, sequence=1, prev=ZERO_DIGEST, records=(rec(PersistRecordKind.TOMBSTONE, "gone", seq=7, now=now),), now=now)
    convenient = snapshot(key, sequence=2, prev=previous.snapshot_digest, records=(rec(PersistRecordKind.PROVIDER_TRUE, "resurrected", seq=8, now=now + 1),), now=now + 1)
    f2 = frame(key, lane=lane, sequence=2, prev_frame=JOURNAL_ZERO, snap=convenient, now=now + 1)

    report = replay_journal((f2.to_bytes(),), previous_snapshot=previous, now=now + 2)

    assert report.decision.kind is JournalReplayDecisionKind.QUARANTINE_HARD_NEGATIVE_LOSS
    assert report.quarantined


def test_generatorfuzz_is_deterministic_and_covers_all_three_surfaces() -> None:
    now = 140_000
    key = kp(25)
    node_id = digest("generator-node")
    cases_a = generate_fuzz_corpus(keypair=key, node_id=node_id, seed=42, now=now, generated_rounds=4)
    first = assess_generated_fuzz(cases_a, seed=42)
    cases_b = generate_fuzz_corpus(keypair=key, node_id=node_id, seed=42, now=now, generated_rounds=4)
    second = assess_generated_fuzz(cases_b, seed=42, repeat_digest=first.corpus_digest)

    assert first.decision.kind is GeneratedFuzzDecisionKind.ACCEPT_GENERATED_CORPUS
    assert second.accepted
    assert first.corpus_digest == second.corpus_digest
    assert first.run.failed_cases == 0
    assert first.run.rejected_cases >= 6
    assert {surface.value for surface in first.surfaces} == {"parse_guard", "wire_frame", "shadow_frame"}


def test_generatorfuzz_rejects_missing_surface_corpus() -> None:
    now = 150_000
    key = kp(26)
    node_id = digest("generator-node-small")
    cases = tuple(case for case in generate_fuzz_corpus(keypair=key, node_id=node_id, seed=7, now=now, generated_rounds=1) if case.surface.value == "parse_guard")
    report = assess_generated_fuzz(cases, seed=7)
    assert report.decision.kind is GeneratedFuzzDecisionKind.REJECT_MISSING_SURFACE
    assert not report.accepted


def test_refusal_schedule_join_backs_off_refusal_heavy_families() -> None:
    now = 160_000
    garden = kp(27)
    windows = (
        RefusalWindow(1, (event(WorkEventKind.SERVED_HEAD, "head-a", garden=garden, fam="fam-A", path="path-A", now=now), event(WorkEventKind.REFUSED_USEFULLY, "r-a", garden=garden, fam="fam-A", path="path-B", now=now, unit=4))),
        RefusalWindow(2, (event(WorkEventKind.SERVED_WITNESS, "wit-b", garden=garden, fam="fam-B", path="path-C", now=now + 1), event(WorkEventKind.REFUSED_USEFULLY, "r-b", garden=garden, fam="fam-B", path="path-D", now=now + 1, unit=4))),
    )
    refusal = assess_refusal_loop(windows, now=now + 2, policy=RefusalLoopPolicy(work_meter_policy=WorkMeterPolicy(min_source_families=1, max_refusal_ratio=0.6)))
    report = join_refusal_loop_to_schedule(refusal_report=refusal, joined_report=joined(JoinedScheduleDecisionKind.SCHEDULED_WITH_REFUSALS, refused={"fam-A": 2, "fam-B": 1}), now=now + 2)

    assert report.decision.kind is RefusalScheduleDecisionKind.BACKOFF_REFUSAL_HEAVY_FAMILIES
    assert report.decision.accept_next_schedule
    assert report.bulk_throttle_factor < 1.0
    assert set(report.family_backoff) == {"fam-A", "fam-B"}


def test_refusal_schedule_join_quarantines_loop_before_scheduler_laundering() -> None:
    now = 170_000
    garden = kp(28)
    windows = tuple(
        RefusalWindow(idx, (event(WorkEventKind.REFUSED_USEFULLY, f"r-{idx}", garden=garden, fam=f"fam-{idx}", path=f"path-{idx}", now=now + idx),))
        for idx in range(1, 4)
    )
    refusal = assess_refusal_loop(windows, now=now + 5, policy=RefusalLoopPolicy(max_consecutive_refusal_heavy=2, work_meter_policy=WorkMeterPolicy(min_source_families=1)))
    report = join_refusal_loop_to_schedule(refusal_report=refusal, joined_report=joined(JoinedScheduleDecisionKind.SCHEDULED_WITH_REFUSALS, refused={"fam-X": 1}), now=now + 5)

    assert refusal.decision_kind is RefusalLoopDecisionKind.QUARANTINE_REFUSAL_ONLY_LOOP
    assert report.decision.kind is RefusalScheduleDecisionKind.QUARANTINE_REFUSAL_LOOP
    assert report.quarantined
    assert report.bulk_throttle_factor == 0.0


def test_refusal_schedule_join_detects_protected_scheduler_starvation() -> None:
    now = 180_000
    garden = kp(29)
    refusal = assess_refusal_loop(
        (RefusalWindow(1, (event(WorkEventKind.SERVED_HEAD, "head", garden=garden, fam="fam-A", path="path-A", now=now, unit=2), event(WorkEventKind.SERVED_WITNESS, "wit", garden=garden, fam="fam-B", path="path-B", now=now, unit=2))),),
        now=now + 1,
    )
    report = join_refusal_loop_to_schedule(refusal_report=refusal, joined_report=joined(JoinedScheduleDecisionKind.STARVATION_PROTECTED_WORK, refused={"fam-A": 1}, protected_started=0), now=now + 1)
    assert report.decision.kind is RefusalScheduleDecisionKind.QUARANTINE_SCHEDULER_STARVATION
    assert report.quarantined


def test_foldspine_audits_current_revision_navigation() -> None:
    root = Path(__file__).resolve().parents[1]
    report = audit_fold_spine(root, revision="rev0028")
    assert report.status == "pass"
    assert report.error_count == 0
