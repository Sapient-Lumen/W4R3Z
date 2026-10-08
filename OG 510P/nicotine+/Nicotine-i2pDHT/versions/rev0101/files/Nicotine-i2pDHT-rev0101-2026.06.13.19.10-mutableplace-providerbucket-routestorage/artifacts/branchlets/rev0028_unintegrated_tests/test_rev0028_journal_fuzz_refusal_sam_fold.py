from pathlib import Path

from i2p_dht_lab.foldspine import audit_fold_spine
from i2p_dht_lab.fuzzwire import deterministic_fuzz_cases
from i2p_dht_lab.generatorfuzz import generate_rejection_corpus, run_generated_fuzz_corpus
from i2p_dht_lab.identity import DhtKeypair
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.journallane import (
    JournalReplayDecisionKind,
    assess_journal_stream,
    compact_journal_entries,
    encode_journal_stream,
    JournalEntry,
)
from i2p_dht_lab.persistlane import PersistRecord, PersistRecordKind, ZERO_DIGEST
from i2p_dht_lab.refusalbudget import (
    RefusalBudgetDecisionKind,
    ScheduleBudgetSignal,
    ScheduleSignalSurface,
    assess_refusal_budget_join,
)
from i2p_dht_lab.refusalloop import RefusalLoopDecisionKind, RefusalLoopPolicy, RefusalWindow, assess_refusal_loop
from i2p_dht_lab.samwire import SamStepKind, SamWireDecisionKind, SamWireSend, SamWireStep, assess_sam_wire_script
from i2p_dht_lab.wirecanon import WireFrame, WireMessageKind
from i2p_dht_lab.workmeter import WorkEvent, WorkEventKind, WorkMeterPolicy


def kp(n: int) -> DhtKeypair:
    return DhtKeypair.from_seed(bytes([n]) * 32)


def digest(label: str) -> bytes:
    return sha256(label.encode("utf-8"))


def record(kind: PersistRecordKind, label: str, *, seq: int = 1, now: int = 1_000, expires: int | None = None) -> PersistRecord:
    return PersistRecord(
        kind=kind,
        scope_id=digest("journal-scope"),
        subject_digest=digest(label),
        value_digest=digest(f"{label}-value-{seq}"),
        sequence=seq,
        source_family="fam-A",
        path_family="path-A",
        issued_at=now,
        expires_at=expires or now + 10_000,
    )


def journal_entry(seq: int, prev: bytes, *, keypair: DhtKeypair, label: str, kind: PersistRecordKind = PersistRecordKind.MUTABLE_HEAD, now: int = 1_000, record_seq: int | None = None) -> JournalEntry:
    return JournalEntry.create(keypair=keypair, sequence=seq, prev_entry_digest=prev, record=record(kind, label, seq=record_seq or seq, now=now), issued_at=now)


def work_event(kind: WorkEventKind, label: str, *, garden: DhtKeypair, fam: str, now: int, unit: int = 1) -> WorkEvent:
    return WorkEvent.create(
        garden=garden,
        event_kind=kind,
        scope_id=digest("refusal-scope"),
        subject_digest=digest(label),
        source_family=fam,
        path_family=f"path-{fam}",
        unit_cost=unit,
        issued_at=now,
        ttl=600,
    )


def balanced_refusal_report(now: int = 20_000):
    garden = kp(7)
    windows = (
        RefusalWindow(1, (work_event(WorkEventKind.SERVED_HEAD, "head", garden=garden, fam="fam-A", now=now),)),
        RefusalWindow(2, (work_event(WorkEventKind.SERVED_WITNESS, "wit", garden=garden, fam="fam-B", now=now + 1),)),
    )
    return assess_refusal_loop(windows, now=now + 2, policy=RefusalLoopPolicy(work_meter_policy=WorkMeterPolicy(min_source_families=1)))


def signal(surface: ScheduleSignalSurface, *, ok: bool = True, protected: int = 1, served: int = 2, refusals: int = 0, families=("fam-A", "fam-B")) -> ScheduleBudgetSignal:
    return ScheduleBudgetSignal(surface, ok, protected, served, refusals, tuple(families), digest(f"signal-{surface.value}-{served}-{refusals}-{ok}"))


def sam_step(keypair: DhtKeypair, kind: SamStepKind, *, session: str = "session-a", destination: str = "dest-a", now: int = 1_000, frame: WireFrame | None = None, payload: bytes = b"") -> SamWireStep:
    return SamWireStep.create(keypair=keypair, kind=kind, session_id=session, destination=destination, issued_at=now, ttl=300, frame=frame, payload=payload)


def sam_frame(keypair: DhtKeypair, *, request_label: str, payload: bytes, now: int) -> WireFrame:
    return WireFrame.create(keypair=keypair, sender_node_id=digest("sam-node"), message_kind=WireMessageKind.FIND_NODE, request_id=digest(request_label), payload=payload, issued_at=now, ttl=120)


def test_journal_replays_linked_entries_and_counts_hard_negatives() -> None:
    now = 10_000
    keypair = kp(1)
    first = journal_entry(1, ZERO_DIGEST, keypair=keypair, label="head", now=now)
    tomb = journal_entry(2, first.entry_digest, keypair=keypair, label="gone", kind=PersistRecordKind.TOMBSTONE, now=now + 1)
    report = assess_journal_stream(encode_journal_stream((first, tomb)), now=now + 2)
    assert report.decision_kind is JournalReplayDecisionKind.ACCEPT_REPLAYED_PREFIX
    assert report.accept
    assert report.last_entry_digest == tomb.entry_digest
    assert report.hard_negative_count == 1


def test_journal_accepts_crash_cut_tail_but_rejects_bad_first_entry() -> None:
    now = 11_000
    keypair = kp(2)
    first = journal_entry(1, ZERO_DIGEST, keypair=keypair, label="head", now=now)
    stream = encode_journal_stream((first,)) + b"\n--i2p-dht-journal-entry--\nd01:x1:ye"
    prefix = assess_journal_stream(stream, now=now + 2)
    assert prefix.decision_kind is JournalReplayDecisionKind.ACCEPT_REPLAYED_WITH_CRASH_TAIL
    assert prefix.accept
    bad_first = assess_journal_stream(b"d01:x1:ye", now=now + 2)
    assert bad_first.decision_kind is JournalReplayDecisionKind.QUARANTINE_PARSE_ERROR
    assert not bad_first.accept


def test_journal_quarantines_prev_mismatch_rollback_and_same_sequence_fork() -> None:
    now = 12_000
    keypair = kp(3)
    first = journal_entry(2, ZERO_DIGEST, keypair=keypair, label="head", now=now)
    wrong_prev = journal_entry(3, digest("wrong-prev"), keypair=keypair, label="next", now=now + 1)
    assert assess_journal_stream(encode_journal_stream((first, wrong_prev)), now=now + 2).decision_kind is JournalReplayDecisionKind.QUARANTINE_PREV_MISMATCH
    rollback = journal_entry(1, first.entry_digest, keypair=keypair, label="old", now=now + 2)
    fork = journal_entry(2, first.entry_digest, keypair=keypair, label="fork", now=now + 2)
    assert assess_journal_stream(encode_journal_stream((rollback,)), previous_entry_digest=first.entry_digest, previous_highest_sequence=2, now=now + 3).decision_kind is JournalReplayDecisionKind.QUARANTINE_ROLLBACK
    assert assess_journal_stream(encode_journal_stream((fork,)), previous_entry_digest=first.entry_digest, previous_highest_sequence=2, now=now + 3).decision_kind is JournalReplayDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK


def test_journal_compaction_preserves_hard_negative_and_latest_soft() -> None:
    now = 13_000
    keypair = kp(4)
    old_soft = JournalEntry.create(keypair=keypair, sequence=1, prev_entry_digest=ZERO_DIGEST, record=record(PersistRecordKind.PROVIDER_TRUE, "same", seq=1, now=now, expires=now - 10), issued_at=now)
    new_soft = JournalEntry.create(keypair=keypair, sequence=2, prev_entry_digest=old_soft.entry_digest, record=record(PersistRecordKind.PROVIDER_TRUE, "same", seq=2, now=now), issued_at=now + 1)
    tomb = JournalEntry.create(keypair=keypair, sequence=3, prev_entry_digest=new_soft.entry_digest, record=record(PersistRecordKind.PROVIDER_FALSE, "bad", seq=3, now=now, expires=now - 100), issued_at=now + 2)
    compacted = compact_journal_entries((old_soft, new_soft, tomb), now=now + 1, soft_retention_seconds=5)
    assert old_soft not in compacted
    assert new_soft in compacted
    assert tomb in compacted


def test_generated_fuzz_corpus_extends_seed_cases_and_rejects_mutations() -> None:
    keypair = kp(8)
    seeds = deterministic_fuzz_cases(keypair=keypair, node_id=digest("node-8"), now=30_000)
    corpus = generate_rejection_corpus(seeds)
    assert corpus.seed_count == len(seeds)
    assert corpus.case_count >= 6
    report = run_generated_fuzz_corpus(corpus)
    assert report.passed
    assert report.rejected_generated_cases == corpus.case_count


def test_refusal_budget_accepts_balanced_refusals_with_scheduled_work() -> None:
    report = balanced_refusal_report()
    joined = assess_refusal_budget_join(report, (signal(ScheduleSignalSurface.SCHED_JOIN, served=3, refusals=1), signal(ScheduleSignalSurface.GARDEN_SCHEDULER, served=2, refusals=1)))
    assert joined.decision_kind is RefusalBudgetDecisionKind.ACCEPT_BALANCED_BUDGET
    assert joined.accept
    assert joined.total_served_units == 5


def test_refusal_budget_quarantines_refusal_loop_and_no_service() -> None:
    now = 40_000
    garden = kp(10)
    windows = tuple(RefusalWindow(idx, (work_event(WorkEventKind.REFUSED_USEFULLY, f"refuse-{idx}", garden=garden, fam=f"fam-{idx}", now=now + idx),)) for idx in range(3))
    loop = assess_refusal_loop(windows, now=now + 10, policy=RefusalLoopPolicy(max_consecutive_refusal_heavy=1, work_meter_policy=WorkMeterPolicy(min_source_families=1)))
    joined = assess_refusal_budget_join(loop, (signal(ScheduleSignalSurface.SCHED_JOIN, served=0, refusals=3),))
    assert loop.decision_kind is RefusalLoopDecisionKind.QUARANTINE_REFUSAL_ONLY_LOOP
    assert joined.decision_kind is RefusalBudgetDecisionKind.QUARANTINE_REFUSAL_LAUNDERING
    assert not joined.accept


def test_refusal_budget_watches_under_diverse_schedule() -> None:
    report = balanced_refusal_report()
    joined = assess_refusal_budget_join(report, (signal(ScheduleSignalSurface.GARDEN_SCHEDULER, served=2, refusals=0, families=("fam-A",)),))
    assert joined.decision_kind is RefusalBudgetDecisionKind.WATCH_UNDER_DIVERSE
    assert joined.accept


def test_samwire_accepts_ordered_persistent_stream_send() -> None:
    now = 50_000
    keypair = kp(20)
    payload = b"find-node-payload"
    frame = sam_frame(keypair, request_label="req-a", payload=payload, now=now)
    hello = sam_step(keypair, SamStepKind.HELLO, now=now)
    session = sam_step(keypair, SamStepKind.SESSION_CREATE, now=now + 1)
    send_step = sam_step(keypair, SamStepKind.STREAM_SEND, now=now + 2, frame=frame, payload=payload)
    report = assess_sam_wire_script((hello, session, SamWireSend(send_step, frame, payload)), now=now + 3, expected_destination="dest-a")
    assert report.decision_kind is SamWireDecisionKind.ACCEPT_SCRIPT
    assert report.accept
    assert report.send_count == 1


def test_samwire_rejects_send_before_session_destination_drift_and_bad_frame() -> None:
    now = 51_000
    keypair = kp(21)
    payload = b"payload"
    frame = sam_frame(keypair, request_label="bad-payload", payload=payload, now=now)
    send_step = sam_step(keypair, SamStepKind.STREAM_SEND, now=now, frame=frame, payload=payload)
    assert assess_sam_wire_script((SamWireSend(send_step, frame, payload),), now=now + 1).decision_kind is SamWireDecisionKind.QUARANTINE_SEND_BEFORE_SESSION
    hello = sam_step(keypair, SamStepKind.HELLO, destination="dest-a", now=now)
    drift = sam_step(keypair, SamStepKind.SESSION_CREATE, destination="dest-b", now=now + 1)
    assert assess_sam_wire_script((hello, drift), now=now + 2).decision_kind is SamWireDecisionKind.QUARANTINE_DESTINATION_DRIFT
    session = sam_step(keypair, SamStepKind.SESSION_CREATE, now=now + 1)
    bad_send_step = sam_step(keypair, SamStepKind.STREAM_SEND, now=now + 2, frame=frame, payload=b"tampered")
    bad = assess_sam_wire_script((sam_step(keypair, SamStepKind.HELLO, now=now), session, SamWireSend(bad_send_step, frame, b"tampered")), now=now + 3)
    assert bad.decision_kind is SamWireDecisionKind.QUARANTINE_FRAME_INVALID


def test_samwire_watches_reconnect_same_destination() -> None:
    now = 52_000
    keypair = kp(22)
    report = assess_sam_wire_script((
        sam_step(keypair, SamStepKind.HELLO, now=now),
        sam_step(keypair, SamStepKind.SESSION_CREATE, now=now + 1),
        sam_step(keypair, SamStepKind.RECONNECT, now=now + 2),
    ), now=now + 3)
    assert report.decision_kind is SamWireDecisionKind.WATCH_RECONNECT_SAME_DESTINATION
    assert report.accept


def test_foldspine_audit_pins_rev0028_navigation() -> None:
    root = Path(__file__).resolve().parents[1]
    report = audit_fold_spine(root, revision="rev0028")
    assert report.status == "pass"
    assert report.error_count == 0
