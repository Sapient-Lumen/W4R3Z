from dataclasses import replace
from pathlib import Path

from i2p_dht_lab.foldspine import audit_fold_spine
from i2p_dht_lab.fuzzwire import deterministic_fuzz_cases
from i2p_dht_lab.gardenrefusal import (
    GardenAdmissionBatch,
    GardenAdmissionDecision,
    GardenAdmissionKind,
    GardenLoadState,
    GardenRefusalReason,
    GardenWorkKind,
    GardenWorkRequest,
)
from i2p_dht_lab.gardenscheduler import GardenScheduleDecision, GardenScheduleDecisionKind, GardenScheduleReport, GardenScheduleWindow
from i2p_dht_lab.generatorfuzz import GeneratedFuzzPolicy, default_generated_fuzz_report, generate_fuzz_cases
from i2p_dht_lab.identity import DhtKeypair
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.journallane import (
    ZERO_DIGEST,
    JournalCompactionSummary,
    JournalEntry,
    JournalEntryKind,
    JournalReplayDecisionKind,
    encode_journal_frames,
    replay_journal_bytes,
    replay_journal_entries,
)
from i2p_dht_lab.refusaljoin import RefusalJoinDecisionKind, join_refusal_pressure
from i2p_dht_lab.refusalloop import RefusalLoopDecisionKind, RefusalLoopPolicy, RefusalWindow, assess_refusal_loop
from i2p_dht_lab.samshadow import SamShadowFrame, SamShadowProfile, SamShadowTranscript, make_streaming_first_shadow
from i2p_dht_lab.samwireharness import SamWireDecisionKind, validate_sam_wire_session
from i2p_dht_lab.wirecanon import WireFrame, WireMessageKind
from i2p_dht_lab.workmeter import WorkEvent, WorkEventKind, WorkMeterPolicy


def kp(n: int) -> DhtKeypair:
    return DhtKeypair.from_seed(bytes([n]) * 32)


def digest(label: str) -> bytes:
    return sha256(label.encode("utf-8"))


def journal_entry(keypair: DhtKeypair, *, seq: int, prev: bytes, kind: JournalEntryKind, label: str, now: int, source: str = "fam-A", path: str = "path-A", flags: tuple[str, ...] = ()) -> JournalEntry:
    return JournalEntry.create(
        keypair=keypair,
        sequence=seq,
        previous_digest=prev,
        kind=kind,
        lane_id=digest("journal-lane"),
        subject_digest=digest(label),
        payload_digest=digest(f"payload-{label}-{seq}"),
        issued_at=now,
        source_family=source,
        path_family=path,
        flags=flags,
    )


def work_event(kind: WorkEventKind, *, garden: DhtKeypair, label: str, fam: str, path: str, now: int) -> WorkEvent:
    return WorkEvent.create(
        garden=garden,
        event_kind=kind,
        scope_id=digest("work-scope"),
        subject_digest=digest(label),
        source_family=fam,
        path_family=path,
        unit_cost=1,
        issued_at=now,
        ttl=600,
    )


def garden_request(label: str, *, kind: GardenWorkKind, fam: str, now: int) -> GardenWorkRequest:
    return GardenWorkRequest(
        requester_node_id=digest(f"requester-{label}"),
        family_id=fam,
        kind=kind,
        target=digest(f"target-{label}"),
        issued_at=now,
    )


def fake_garden_schedule(*, accepted: int, refused: int, decision_kind: GardenScheduleDecisionKind, now: int) -> GardenScheduleReport:
    decisions = []
    for idx in range(accepted):
        decisions.append(GardenAdmissionDecision(GardenAdmissionKind.ACCEPTED, garden_request(f"a-{idx}", kind=GardenWorkKind.HEAD_WATCH, fam=f"fam-A{idx}", now=now)))
    for idx in range(refused):
        decisions.append(GardenAdmissionDecision(GardenAdmissionKind.REFUSED_USEFULLY, garden_request(f"r-{idx}", kind=GardenWorkKind.BULK_PROVIDER, fam=f"fam-R{idx}", now=now), GardenRefusalReason.OVER_STREAM_BUDGET))
    batch = GardenAdmissionBatch(tuple(decisions), GardenLoadState())
    window = GardenScheduleWindow(0, now, batch)
    return GardenScheduleReport((window,), (), GardenScheduleDecision(decision_kind, decision_kind is not GardenScheduleDecisionKind.STARVATION_PRESSURE, "test schedule"), digest(f"schedule-{accepted}-{refused}-{decision_kind.value}"))


def test_journal_replays_signed_gapless_chain_and_crash_cut_tail() -> None:
    now = 100_000
    key = kp(1)
    first = journal_entry(key, seq=0, prev=ZERO_DIGEST, kind=JournalEntryKind.MUTABLE_HEAD, label="head", now=now)
    second = journal_entry(key, seq=1, prev=first.entry_digest, kind=JournalEntryKind.PROVIDER_TRUE, label="provider", now=now + 1, source="fam-B", path="path-B")
    clean = replay_journal_entries((first, second))
    assert clean.decision_kind is JournalReplayDecisionKind.ACCEPT_REPLAYED_JOURNAL
    assert clean.accept
    bytes_report = replay_journal_bytes(encode_journal_frames((first, second), trailing_bytes=b"JDL1 999\npartial"))
    assert bytes_report.decision_kind is JournalReplayDecisionKind.ACCEPT_REPLAYED_WITH_TRUNCATED_TAIL
    assert bytes_report.truncated_tail
    assert len(bytes_report.entries) == 2


def test_journal_quarantines_bad_signature_prev_mismatch_and_sequence_fork() -> None:
    now = 110_000
    key = kp(2)
    first = journal_entry(key, seq=0, prev=ZERO_DIGEST, kind=JournalEntryKind.MUTABLE_HEAD, label="head", now=now)
    bad_sig = replace(first, signature=b"0" * 64)
    assert replay_journal_entries((bad_sig,)).decision_kind is JournalReplayDecisionKind.QUARANTINE_BAD_SIGNATURE
    wrong_prev = journal_entry(key, seq=1, prev=digest("wrong-prev"), kind=JournalEntryKind.PROVIDER_TRUE, label="provider", now=now + 1)
    assert replay_journal_entries((first, wrong_prev)).decision_kind is JournalReplayDecisionKind.QUARANTINE_PREV_MISMATCH
    fork = journal_entry(key, seq=0, prev=ZERO_DIGEST, kind=JournalEntryKind.PROVIDER_FALSE, label="fork", now=now, source="fam-B", path="path-B")
    assert replay_journal_entries((first, fork)).decision_kind is JournalReplayDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK


def test_journal_quarantines_gap_parse_error_and_compaction_amnesia() -> None:
    now = 120_000
    key = kp(3)
    gap = journal_entry(key, seq=2, prev=ZERO_DIGEST, kind=JournalEntryKind.MUTABLE_HEAD, label="gap", now=now)
    assert replay_journal_entries((gap,)).decision_kind is JournalReplayDecisionKind.QUARANTINE_SEQUENCE_GAP
    malformed = replay_journal_bytes(b"JDL1 10\nd1:a1:b\n")
    assert malformed.decision_kind is JournalReplayDecisionKind.QUARANTINE_PARSE_ERROR
    old_negative = digest("known-negative")
    summary = JournalCompactionSummary(compacted_through_sequence=4, compacted_head_digest=digest("compacted-head"), hard_negative_digests=(old_negative,))
    marker = journal_entry(key, seq=5, prev=summary.compacted_head_digest, kind=JournalEntryKind.COMPACTION_MARK, label="compact", now=now)
    assert replay_journal_entries((marker,), compaction_summary=summary).decision_kind is JournalReplayDecisionKind.QUARANTINE_HARD_NEGATIVE_DROPPED
    kept = journal_entry(key, seq=5, prev=summary.compacted_head_digest, kind=JournalEntryKind.COMPACTION_MARK, label="compact", now=now, flags=(f"kept-negative:{old_negative.hex()[:16]}",))
    assert replay_journal_entries((kept,), compaction_summary=summary).decision_kind is JournalReplayDecisionKind.ACCEPT_COMPACTED_WITH_NEGATIVES


def test_generated_fuzz_expands_controls_and_all_cases_pass_expectations() -> None:
    key = kp(4)
    now = 130_000
    seeds = deterministic_fuzz_cases(keypair=key, node_id=digest("node-4"), now=now)
    generated = generate_fuzz_cases(seeds, policy=GeneratedFuzzPolicy(max_cases_per_seed=3))
    assert len(generated) > len(seeds)
    assert any(item.mutation_kind.value == "truncate" for item in generated)
    report = default_generated_fuzz_report(keypair=key, node_id=digest("node-4"), now=now, policy=GeneratedFuzzPolicy(max_cases_per_seed=3))
    assert report.passed
    assert report.run_report.failed_cases == 0
    assert report.mutation_counts["keep_control"] == len(seeds)


def test_refusal_join_quarantines_loop_before_scheduling_and_backs_off_heavy_ratio() -> None:
    now = 140_000
    garden = kp(5)
    windows = tuple(
        RefusalWindow(idx, (work_event(WorkEventKind.REFUSED_USEFULLY, garden=garden, label=f"r-{idx}", fam=f"fam-{idx}", path=f"path-{idx}", now=now + idx),))
        for idx in range(3)
    )
    quarantined_loop = assess_refusal_loop(windows, now=now + 10, policy=RefusalLoopPolicy(max_consecutive_refusal_heavy=1, work_meter_policy=WorkMeterPolicy(min_source_families=1)))
    report = join_refusal_pressure(quarantined_loop, garden_schedule=fake_garden_schedule(accepted=1, refused=1, decision_kind=GardenScheduleDecisionKind.SCHEDULED_WITH_REFUSALS, now=now))
    assert report.decision_kind is RefusalJoinDecisionKind.QUARANTINE_LOOP_BEFORE_SCHEDULE
    balanced_loop = assess_refusal_loop((RefusalWindow(1, (work_event(WorkEventKind.SERVED_HEAD, garden=garden, label="h", fam="fam-A", path="path-A", now=now),)),), now=now + 1, policy=RefusalLoopPolicy(work_meter_policy=WorkMeterPolicy(min_source_families=1)))
    heavy = join_refusal_pressure(balanced_loop, garden_schedule=fake_garden_schedule(accepted=1, refused=4, decision_kind=GardenScheduleDecisionKind.SCHEDULED_WITH_REFUSALS, now=now))
    assert heavy.decision_kind is RefusalJoinDecisionKind.BACKOFF_REFUSAL_HEAVY
    assert heavy.accept


def test_refusal_join_quarantines_schedule_starvation_but_accepts_balanced_join() -> None:
    now = 150_000
    garden = kp(6)
    loop = assess_refusal_loop(
        (RefusalWindow(1, (
            work_event(WorkEventKind.SERVED_HEAD, garden=garden, label="h", fam="fam-A", path="path-A", now=now),
            work_event(WorkEventKind.SERVED_WITNESS, garden=garden, label="w", fam="fam-B", path="path-B", now=now),
        )),),
        now=now + 1,
        policy=RefusalLoopPolicy(work_meter_policy=WorkMeterPolicy(min_source_families=2)),
    )
    starvation = join_refusal_pressure(loop, garden_schedule=fake_garden_schedule(accepted=0, refused=2, decision_kind=GardenScheduleDecisionKind.STARVATION_PRESSURE, now=now))
    assert starvation.decision_kind is RefusalJoinDecisionKind.QUARANTINE_SCHEDULE_STARVATION
    good = join_refusal_pressure(loop, garden_schedule=fake_garden_schedule(accepted=3, refused=1, decision_kind=GardenScheduleDecisionKind.SCHEDULED_WITH_REFUSALS, now=now))
    assert good.decision_kind is RefusalJoinDecisionKind.ACCEPT_BALANCED_JOIN
    assert good.accept


def test_sam_wire_harness_accepts_streaming_first_canonical_frames() -> None:
    now = 160_000
    key = kp(7)
    profile = SamShadowProfile(session_id="dht", destination_name="dht.keys")
    sam = make_streaming_first_shadow(profile, "remote-destination")
    payload = b"find-provider-payload"
    frame = WireFrame.create(keypair=key, sender_node_id=digest("node-7"), message_kind=WireMessageKind.FIND_PROVIDER, request_id=digest("request-1"), payload=payload, issued_at=now, ttl=120)
    report = validate_sam_wire_session(sam, ((frame, payload),), now=now + 1)
    assert report.decision_kind is SamWireDecisionKind.ACCEPT_STREAM_FRAMES
    assert report.accept
    assert report.wire_transcript.accepted_count == 1


def test_sam_wire_harness_rejects_bad_sam_duplicate_request_and_tampered_payload() -> None:
    now = 170_000
    key = kp(8)
    bad_sam = SamShadowTranscript((SamShadowFrame.command("STREAM CONNECT", ID="dht", DESTINATION="remote"),))
    payload = b"epoch-head"
    frame = WireFrame.create(keypair=key, sender_node_id=digest("node-8"), message_kind=WireMessageKind.EPOCH_HEAD, request_id=digest("dup-request"), payload=payload, issued_at=now, ttl=120)
    assert validate_sam_wire_session(bad_sam, ((frame, payload),), now=now + 1).decision_kind is SamWireDecisionKind.REJECT_SAM_SHADOW
    good_sam = make_streaming_first_shadow(SamShadowProfile(session_id="dht", destination_name="dht.keys"), "remote")
    dup = validate_sam_wire_session(good_sam, ((frame, payload), (frame, payload)), now=now + 1)
    assert dup.decision_kind is SamWireDecisionKind.REJECT_DUPLICATE_REQUEST
    tampered = validate_sam_wire_session(good_sam, ((frame, b"tampered"),), now=now + 1)
    assert tampered.decision_kind is SamWireDecisionKind.REJECT_WIRE_VALIDATION


def test_foldspine_pins_rev0028_navigation() -> None:
    root = Path(__file__).resolve().parents[1]
    report = audit_fold_spine(root, revision="rev0028")
    assert report.status == "pass"
    assert report.error_count == 0
