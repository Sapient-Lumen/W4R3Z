from pathlib import Path

from dataclasses import replace

from i2p_dht_lab.foldspine import audit_fold_spine
from i2p_dht_lab.fuzzwire import deterministic_fuzz_cases
from i2p_dht_lab.gardenrefusal import GardenAdmissionPolicy, GardenLoadState, GardenWorkKind, GardenWorkRequest
from i2p_dht_lab.gardenscheduler import GardenScheduleDecisionKind, GardenSchedulePolicy, plan_garden_schedule
from i2p_dht_lab.generatorfuzz import generate_rejection_corpus, run_generated_fuzz_corpus
from i2p_dht_lab.identity import DhtKeypair, NodeIdentity
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.journallane import (
    ENTRY_SEPARATOR,
    JournalEntry,
    JournalReplayDecisionKind,
    assess_journal_stream,
    compact_journal_entries,
    encode_journal_stream,
)
from i2p_dht_lab.persistlane import PersistRecord, PersistRecordKind, ZERO_DIGEST
from i2p_dht_lab.refusaljoin import RefusalJoinDecisionKind, assess_refusal_schedule_join
from i2p_dht_lab.refusalloop import RefusalLoopDecisionKind, RefusalWindow, assess_refusal_loop
from i2p_dht_lab.samwire import SamStepKind, SamWireDecisionKind, SamWireSend, SamWireStep, assess_sam_wire_script
from i2p_dht_lab.wirecanon import WireFrame, WireMessageKind
from i2p_dht_lab.workmeter import WorkEvent, WorkEventKind


def kp(n: int) -> DhtKeypair:
    return DhtKeypair.from_seed(bytes([n]) * 32)


def ident(n: int) -> NodeIdentity:
    return NodeIdentity.create(destination=f"rev0028-node-{n}.b32.i2p", keypair=kp(n))


def digest(label: str) -> bytes:
    return sha256(label.encode("utf-8"))


def record(kind: PersistRecordKind, label: str, *, seq: int, now: int, fam: str = "fam-A") -> PersistRecord:
    return PersistRecord(
        kind=kind,
        scope_id=digest("journal-scope"),
        subject_digest=digest(label),
        value_digest=digest(f"{label}-value-{seq}"),
        sequence=seq,
        source_family=fam,
        path_family=f"path-{fam}",
        issued_at=now,
        expires_at=now + 10_000,
        byte_cost=128,
    )


def entry(n: int, *, sequence: int, prev: bytes, kind: PersistRecordKind, label: str, now: int, fam: str = "fam-A") -> JournalEntry:
    return JournalEntry.create(keypair=kp(n), sequence=sequence, prev_entry_digest=prev, record=record(kind, label, seq=sequence, now=now, fam=fam), issued_at=now)


def work(kind: WorkEventKind, label: str, *, garden: DhtKeypair, fam: str, now: int, unit: int = 1) -> WorkEvent:
    return WorkEvent.create(
        garden=garden,
        event_kind=kind,
        scope_id=digest("refusaljoin-scope"),
        subject_digest=digest(label),
        source_family=fam,
        path_family=f"path-{fam}",
        unit_cost=unit,
        issued_at=now,
        ttl=600,
    )


def request(n: int, kind: GardenWorkKind, *, now: int, fam: str, stream: int = 1, provider: int = 0, watch: int = 0) -> GardenWorkRequest:
    return GardenWorkRequest(
        requester_node_id=ident(n).node_id,
        family_id=fam,
        kind=kind,
        target=digest(f"garden-target-{n}-{kind.value}"),
        issued_at=now,
        ttl=1200,
        stream_cost=stream,
        provider_record_cost=provider,
        mutable_watch_cost=watch,
    )


def test_journallane_replays_linked_prefix_and_crash_cut_tail() -> None:
    now = 1_766_000_000
    first = entry(1, sequence=1, prev=ZERO_DIGEST, kind=PersistRecordKind.MUTABLE_HEAD, label="head", now=now)
    second = entry(1, sequence=2, prev=first.entry_digest, kind=PersistRecordKind.TOMBSTONE, label="gone", now=now + 1, fam="fam-B")
    data = encode_journal_stream((first, second)) + ENTRY_SEPARATOR + b"d1:xi1e"[:5]
    report = assess_journal_stream(data, now=now + 2)
    assert report.decision_kind is JournalReplayDecisionKind.ACCEPT_REPLAYED_WITH_CRASH_TAIL
    assert report.accept
    assert report.highest_sequence == 2
    assert report.last_entry_digest == second.entry_digest
    assert report.hard_negative_count == 1
    assert report.crash_tail_bytes > 0


def test_journallane_rejects_prev_mismatch_same_sequence_fork_and_rollback() -> None:
    now = 1_766_000_100
    first = entry(2, sequence=1, prev=ZERO_DIGEST, kind=PersistRecordKind.MUTABLE_HEAD, label="head", now=now)
    wrong_prev = entry(2, sequence=2, prev=digest("wrong-prev"), kind=PersistRecordKind.PROVIDER_TRUE, label="provider", now=now + 1)
    fork = entry(2, sequence=1, prev=first.entry_digest, kind=PersistRecordKind.MUTABLE_HEAD, label="head-fork", now=now + 2)
    rollback = entry(2, sequence=1, prev=ZERO_DIGEST, kind=PersistRecordKind.PROVIDER_TRUE, label="old-provider", now=now + 3)
    assert assess_journal_stream(encode_journal_stream((first, wrong_prev)), now=now + 4).decision_kind is JournalReplayDecisionKind.QUARANTINE_PREV_MISMATCH
    assert assess_journal_stream(encode_journal_stream((first, fork)), now=now + 4).decision_kind is JournalReplayDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK
    assert assess_journal_stream(encode_journal_stream((rollback,)), previous_highest_sequence=2, previous_entry_digest=ZERO_DIGEST, now=now + 4).decision_kind is JournalReplayDecisionKind.QUARANTINE_ROLLBACK


def test_journallane_compaction_preserves_hard_negative_over_soft_noise() -> None:
    now = 1_766_000_200
    prev = ZERO_DIGEST
    entries = []
    for idx in range(5):
        kind = PersistRecordKind.PROVIDER_TRUE
        current = entry(3, sequence=idx + 1, prev=prev, kind=kind, label=f"soft-{idx}", now=now - 20_000, fam=f"fam-{idx}")
        entries.append(current)
        prev = current.entry_digest
    tomb = entry(3, sequence=6, prev=prev, kind=PersistRecordKind.TOMBSTONE, label="gone", now=now - 20_000, fam="fam-T")
    compacted = compact_journal_entries(tuple(entries) + (tomb,), now=now, soft_retention_seconds=100)
    assert tomb in compacted
    assert all(item.record.kind is PersistRecordKind.TOMBSTONE for item in compacted)


def test_generatorfuzz_expands_accept_cases_into_rejecting_corpus() -> None:
    now = 1_766_000_300
    seeds = deterministic_fuzz_cases(keypair=kp(4), node_id=ident(4).node_id, now=now)
    corpus = generate_rejection_corpus(seeds)
    report = run_generated_fuzz_corpus(corpus)
    assert corpus.seed_count == len(seeds)
    assert corpus.case_count >= 6
    assert report.passed
    assert report.rejected_generated_cases == corpus.case_count
    assert report.run.accepted_cases == 0


def test_refusaljoin_accepts_balanced_schedule_and_blocks_refusal_laundering() -> None:
    now = 1_766_000_400
    garden = kp(5)
    garden_node = ident(5).node_id
    schedule = plan_garden_schedule(
        (
            request(10, GardenWorkKind.HEAD_WATCH, now=now, fam="fam-control", watch=1),
            request(11, GardenWorkKind.BULK_PROVIDER, now=now, fam="fam-bulk", provider=5_000),
        ),
        garden_keypair=garden,
        garden_node_id=garden_node,
        start_at=now + 1,
        schedule_policy=GardenSchedulePolicy(windows=1),
        admission_policy=GardenAdmissionPolicy(max_streams=1, max_provider_records=1, max_mutable_watches=2, max_refusals_per_window=4),
        initial_state=GardenLoadState(),
    )
    refusal = assess_refusal_loop((
        RefusalWindow(1, (work(WorkEventKind.SERVED_HEAD, "head", garden=garden, fam="fam-A", now=now + 1, unit=2), work(WorkEventKind.SERVED_WITNESS, "wit", garden=garden, fam="fam-B", now=now + 1, unit=2))),
    ), now=now + 2)
    joined = assess_refusal_schedule_join(schedule=schedule, refusal=refusal)
    assert schedule.decision.kind is GardenScheduleDecisionKind.SCHEDULED_WITH_REFUSALS
    assert refusal.decision_kind is RefusalLoopDecisionKind.ACCEPT_BALANCED_SERVICE
    assert joined.decision_kind is RefusalJoinDecisionKind.ACCEPT_SCHEDULE_AND_REFUSAL_BALANCED
    assert joined.accept

    bad_refusal = assess_refusal_loop(tuple(
        RefusalWindow(idx, (work(WorkEventKind.REFUSED_USEFULLY, f"refuse-{idx}", garden=garden, fam=f"fam-{idx}", now=now + idx),))
        for idx in range(1, 4)
    ), now=now + 10)
    blocked = assess_refusal_schedule_join(schedule=schedule, refusal=bad_refusal)
    assert blocked.decision_kind is RefusalJoinDecisionKind.QUARANTINE_REFUSAL_LOOP_BLOCKS_SCHEDULE
    assert blocked.quarantined


def test_refusaljoin_quarantines_schedule_that_refuses_without_protected_service() -> None:
    now = 1_766_000_500
    garden = kp(6)
    garden_node = ident(6).node_id
    schedule = plan_garden_schedule(
        (request(12, GardenWorkKind.BULK_PROVIDER, now=now, fam="fam-bulk", provider=99_999),),
        garden_keypair=garden,
        garden_node_id=garden_node,
        start_at=now + 1,
        schedule_policy=GardenSchedulePolicy(windows=1),
        admission_policy=GardenAdmissionPolicy(max_streams=1, max_provider_records=0, max_refusals_per_window=2),
    )
    refusal = assess_refusal_loop((RefusalWindow(1, (work(WorkEventKind.SERVED_HEAD, "head", garden=garden, fam="fam-A", now=now, unit=2), work(WorkEventKind.SERVED_WITNESS, "wit", garden=garden, fam="fam-B", now=now, unit=2))),), now=now + 2)
    report = assess_refusal_schedule_join(schedule=schedule, refusal=refusal)
    assert report.decision_kind is RefusalJoinDecisionKind.QUARANTINE_REFUSAL_WITHOUT_PROTECTED_SERVICE
    assert not report.accept


def test_samwire_accepts_persistent_destination_script_and_reconnect_watch() -> None:
    now = 1_766_000_600
    actor = ident(7)
    payload = b"canonical dht frame over sam-shadow"
    frame = WireFrame.create(keypair=kp(7), sender_node_id=actor.node_id, message_kind=WireMessageKind.FIND_NODE, request_id=digest("sam-request"), payload=payload, issued_at=now, ttl=300)
    destination = actor.destination
    hello = SamWireStep.create(keypair=kp(7), kind=SamStepKind.HELLO, session_id="sam-a", destination=destination, issued_at=now)
    session = SamWireStep.create(keypair=kp(7), kind=SamStepKind.SESSION_CREATE, session_id="sam-a", destination=destination, issued_at=now + 1)
    connect = SamWireStep.create(keypair=kp(7), kind=SamStepKind.STREAM_CONNECT, session_id="sam-a", destination=destination, issued_at=now + 2)
    send_step = SamWireStep.create(keypair=kp(7), kind=SamStepKind.STREAM_SEND, session_id="sam-a", destination=destination, issued_at=now + 3, frame=frame, payload=payload)
    reconnect = SamWireStep.create(keypair=kp(7), kind=SamStepKind.RECONNECT, session_id="sam-a", destination=destination, issued_at=now + 4)
    report = assess_sam_wire_script((hello, session, connect, SamWireSend(send_step, frame, payload), reconnect), now=now + 5, expected_destination=destination)
    assert report.decision_kind is SamWireDecisionKind.WATCH_RECONNECT_SAME_DESTINATION
    assert report.accept
    assert report.send_count == 1
    assert report.reconnect_count == 1


def test_samwire_rejects_send_before_session_frame_tamper_and_destination_drift() -> None:
    now = 1_766_000_700
    actor = ident(8)
    payload = b"real payload"
    frame = WireFrame.create(keypair=kp(8), sender_node_id=actor.node_id, message_kind=WireMessageKind.FIND_PROVIDER, request_id=digest("sam-bad"), payload=payload, issued_at=now, ttl=300)
    send_step = SamWireStep.create(keypair=kp(8), kind=SamStepKind.STREAM_SEND, session_id="sam-b", destination=actor.destination, issued_at=now + 1, frame=frame, payload=payload)
    assert assess_sam_wire_script((SamWireSend(send_step, frame, payload),), now=now + 2).decision_kind is SamWireDecisionKind.QUARANTINE_SEND_BEFORE_SESSION

    hello = SamWireStep.create(keypair=kp(8), kind=SamStepKind.HELLO, session_id="sam-b", destination=actor.destination, issued_at=now)
    session = SamWireStep.create(keypair=kp(8), kind=SamStepKind.SESSION_CREATE, session_id="sam-b", destination=actor.destination, issued_at=now + 1)
    tamper_step = SamWireStep.create(keypair=kp(8), kind=SamStepKind.STREAM_SEND, session_id="sam-b", destination=actor.destination, issued_at=now + 2, frame=frame, payload=b"tampered")
    assert assess_sam_wire_script((hello, session, SamWireSend(tamper_step, frame, b"tampered")), now=now + 3).decision_kind is SamWireDecisionKind.QUARANTINE_FRAME_INVALID

    drift = SamWireStep.create(keypair=kp(8), kind=SamStepKind.RECONNECT, session_id="sam-b", destination="other-dest.b32.i2p", issued_at=now + 3)
    assert assess_sam_wire_script((hello, session, drift), now=now + 4, expected_destination=actor.destination).decision_kind is SamWireDecisionKind.QUARANTINE_DESTINATION_DRIFT


def test_foldspine_pins_current_revision_navigation() -> None:
    root = Path(__file__).resolve().parents[1]
    report = audit_fold_spine(root, revision="rev0028", artifact_stem=root.name)
    assert report.status == "pass"
    assert report.error_count == 0
    assert report.warning_count == 0
