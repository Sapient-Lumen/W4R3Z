from pathlib import Path

from i2p_dht_lab.admissionwall import AdmissionDecisionKind, AdmissionReceipt, AdmissionRefusalReason
from i2p_dht_lab.branchmergefold import audit_branch_merge_fold
from i2p_dht_lab.fuzzwire import deterministic_fuzz_cases, run_fuzz_wire_cases
from i2p_dht_lab.identity import DhtKeypair
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.persistlane import (
    PersistLoadDecisionKind,
    PersistLoadPolicy,
    PersistRecord,
    PersistRecordKind,
    PersistSnapshot,
    ZERO_DIGEST,
    assess_persist_reload,
)
from i2p_dht_lab.refusalloop import RefusalLoopDecisionKind, RefusalLoopPolicy, RefusalWindow, assess_refusal_loop
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


def receipt(label: str, *, garden: DhtKeypair, node_id: bytes, now: int) -> AdmissionReceipt:
    return AdmissionReceipt.create(
        keypair=garden,
        garden_node_id=node_id,
        request_digest=digest(label),
        decision=AdmissionDecisionKind.REFUSE_USEFULLY,
        reason=AdmissionRefusalReason.OVER_BYTE_BUDGET,
        issued_at=now,
        ttl=600,
        retry_after_seconds=60,
    )


def event(kind: WorkEventKind, label: str, *, garden: DhtKeypair, fam: str, path: str, now: int, unit: int = 1, rcpt: AdmissionReceipt | None = None) -> WorkEvent:
    return WorkEvent.create(
        garden=garden,
        event_kind=kind,
        scope_id=digest("work-scope"),
        subject_digest=digest(label),
        source_family=fam,
        path_family=path,
        unit_cost=unit,
        issued_at=now,
        ttl=600,
        receipt=rcpt,
    )


def test_persistlane_accepts_canonical_reload_round_trip() -> None:
    now = 10_000
    snapshot = PersistSnapshot.create(
        keypair=kp(1),
        sequence=1,
        prev_snapshot_digest=ZERO_DIGEST,
        records=(rec(PersistRecordKind.PROVIDER_TRUE, "provider", now=now), rec(PersistRecordKind.TOMBSTONE, "provider", seq=2, fam="fam-B", path="path-B", now=now)),
        issued_at=now,
    )
    report = assess_persist_reload(snapshot.to_bytes(), previous_snapshot=None, now=now + 1)
    assert report.decision_kind is PersistLoadDecisionKind.ACCEPT_RELOADED_STATE
    assert report.accept
    assert report.loaded is not None
    assert report.loaded.snapshot_digest == snapshot.snapshot_digest
    assert report.hard_negative_count == 1


def test_persistlane_compaction_preserves_hard_negative_records() -> None:
    now = 20_000
    old = PersistSnapshot.create(keypair=kp(2), sequence=1, prev_snapshot_digest=ZERO_DIGEST, records=(rec(PersistRecordKind.TOMBSTONE, "gone", seq=5, now=now),), issued_at=now)
    noisy_records = tuple(rec(PersistRecordKind.PROVIDER_TRUE, f"provider-{idx}", seq=idx + 1, fam=f"fam-{idx}", path=f"path-{idx}", now=now) for idx in range(6)) + old.records
    newer = PersistSnapshot.create(keypair=kp(2), sequence=2, prev_snapshot_digest=old.snapshot_digest, records=noisy_records, issued_at=now + 1)
    report = assess_persist_reload(newer.to_bytes(), previous_snapshot=old, now=now + 2, policy=PersistLoadPolicy(max_records=3, max_total_bytes=512))
    assert report.decision_kind is PersistLoadDecisionKind.ACCEPT_COMPACTED_WITH_NEGATIVES
    assert report.accept
    assert any(item.kind is PersistRecordKind.TOMBSTONE for item in report.compacted_records)


def test_persistlane_rejects_snapshot_rollback_and_same_sequence_fork() -> None:
    now = 30_000
    first = PersistSnapshot.create(keypair=kp(3), sequence=2, prev_snapshot_digest=ZERO_DIGEST, records=(rec(PersistRecordKind.MUTABLE_HEAD, "head", seq=2, now=now),), issued_at=now)
    rollback = PersistSnapshot.create(keypair=kp(3), sequence=1, prev_snapshot_digest=ZERO_DIGEST, records=(rec(PersistRecordKind.MUTABLE_HEAD, "head-old", seq=1, now=now),), issued_at=now + 1)
    fork = PersistSnapshot.create(keypair=kp(3), sequence=2, prev_snapshot_digest=ZERO_DIGEST, records=(rec(PersistRecordKind.MUTABLE_HEAD, "head-fork", seq=2, now=now),), issued_at=now + 1)
    assert assess_persist_reload(rollback.to_bytes(), previous_snapshot=first, now=now + 2).decision_kind is PersistLoadDecisionKind.QUARANTINE_ROLLBACK
    assert assess_persist_reload(fork.to_bytes(), previous_snapshot=first, now=now + 2).decision_kind is PersistLoadDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK


def test_persistlane_rejects_missing_previous_link_and_dropped_tombstone() -> None:
    now = 40_000
    tomb = rec(PersistRecordKind.TOMBSTONE, "gone", seq=7, now=now)
    previous = PersistSnapshot.create(keypair=kp(4), sequence=1, prev_snapshot_digest=ZERO_DIGEST, records=(tomb,), issued_at=now)
    wrong_link = PersistSnapshot.create(keypair=kp(4), sequence=2, prev_snapshot_digest=digest("wrong-prev"), records=(tomb,), issued_at=now + 1)
    dropped = PersistSnapshot.create(keypair=kp(4), sequence=2, prev_snapshot_digest=previous.snapshot_digest, records=(rec(PersistRecordKind.PROVIDER_TRUE, "convenient", seq=8, now=now),), issued_at=now + 1)
    assert assess_persist_reload(wrong_link.to_bytes(), previous_snapshot=previous, now=now + 2).decision_kind is PersistLoadDecisionKind.QUARANTINE_PREV_MISMATCH
    assert assess_persist_reload(dropped.to_bytes(), previous_snapshot=previous, now=now + 2).decision_kind is PersistLoadDecisionKind.QUARANTINE_HARD_NEGATIVE_DROPPED


def test_persistlane_parseguard_rejects_malformed_snapshot_bytes() -> None:
    report = assess_persist_reload(b"d01:a1:be", previous_snapshot=None, now=1)
    assert report.decision_kind is PersistLoadDecisionKind.QUARANTINE_PARSE_ERROR
    assert report.quarantined


def test_fuzzwire_generated_cases_pin_parser_wire_and_shadow_boundaries() -> None:
    keypair = kp(9)
    cases = deterministic_fuzz_cases(keypair=keypair, node_id=digest("node-9"), now=50_000)
    report = run_fuzz_wire_cases(cases)
    assert report.passed
    assert report.failed_cases == 0
    assert report.accepted_cases == 3
    assert report.rejected_cases == len(cases) - 3


def test_refusalloop_accepts_balanced_service_with_bounded_refusal() -> None:
    now = 60_000
    garden = kp(10)
    node_id = digest("garden-node")
    windows = (
        RefusalWindow(1, (
            event(WorkEventKind.SERVED_HEAD, "head-a", garden=garden, fam="fam-A", path="path-A", now=now),
            event(WorkEventKind.SERVED_WITNESS, "wit-b", garden=garden, fam="fam-B", path="path-B", now=now),
        )),
        RefusalWindow(2, (
            event(WorkEventKind.SERVED_REPAIR, "repair-c", garden=garden, fam="fam-C", path="path-C", now=now + 10, unit=2),
            event(WorkEventKind.REFUSED_USEFULLY, "refuse-d", garden=garden, fam="fam-D", path="path-D", now=now + 10, rcpt=receipt("refuse-d", garden=garden, node_id=node_id, now=now + 10)),
        )),
    )
    report = assess_refusal_loop(windows, now=now + 20)
    assert report.decision_kind is RefusalLoopDecisionKind.ACCEPT_BALANCED_SERVICE
    assert report.accept


def test_refusalloop_quarantines_replayed_receipt_across_windows() -> None:
    now = 70_000
    garden = kp(11)
    node_id = digest("garden-node-11")
    rcpt = receipt("same-refusal", garden=garden, node_id=node_id, now=now)
    windows = (
        RefusalWindow(1, (event(WorkEventKind.SERVED_HEAD, "head-a", garden=garden, fam="fam-A", path="path-A", now=now), event(WorkEventKind.REFUSED_USEFULLY, "refuse-a", garden=garden, fam="fam-B", path="path-B", now=now, rcpt=rcpt))),
        RefusalWindow(2, (event(WorkEventKind.SERVED_WITNESS, "wit-c", garden=garden, fam="fam-C", path="path-C", now=now + 1), event(WorkEventKind.REFUSED_USEFULLY, "refuse-b", garden=garden, fam="fam-D", path="path-D", now=now + 1, rcpt=rcpt))),
    )
    report = assess_refusal_loop(windows, now=now + 2)
    assert report.decision_kind is RefusalLoopDecisionKind.QUARANTINE_REPLAY_ACROSS_WINDOWS
    assert report.replay_receipts == (rcpt.request_digest,)


def test_refusalloop_quarantines_refusal_only_laundering_streak() -> None:
    now = 80_000
    garden = kp(12)
    node_id = digest("garden-node-12")
    windows = tuple(
        RefusalWindow(idx, (event(WorkEventKind.REFUSED_USEFULLY, f"refuse-{idx}", garden=garden, fam=f"fam-{idx}", path=f"path-{idx}", now=now + idx, rcpt=receipt(f"r-{idx}", garden=garden, node_id=node_id, now=now + idx)),))
        for idx in range(1, 4)
    )
    report = assess_refusal_loop(windows, now=now + 10, policy=RefusalLoopPolicy(max_consecutive_refusal_heavy=2, work_meter_policy=WorkMeterPolicy(min_source_families=1)))
    assert report.decision_kind is RefusalLoopDecisionKind.QUARANTINE_REFUSAL_ONLY_LOOP
    assert report.quarantined


def test_refusalloop_watches_under_diverse_repeated_windows() -> None:
    now = 90_000
    garden = kp(13)
    windows = (
        RefusalWindow(1, (event(WorkEventKind.SERVED_HEAD, "head-a", garden=garden, fam="fam-A", path="path-A", now=now, unit=2),)),
        RefusalWindow(2, (event(WorkEventKind.SERVED_WITNESS, "wit-a", garden=garden, fam="fam-A", path="path-B", now=now + 1, unit=2),)),
    )
    report = assess_refusal_loop(windows, now=now + 2, policy=RefusalLoopPolicy(work_meter_policy=WorkMeterPolicy(min_source_families=1)))
    assert report.decision_kind is RefusalLoopDecisionKind.WATCH_UNDER_DIVERSE
    assert report.accept


def test_branchmergefold_pins_schedjoin_and_lineage_branchlets() -> None:
    root = Path(__file__).resolve().parents[1]
    report = audit_branch_merge_fold(root, revision="rev0027")
    assert report.status == "pass"
    assert report.error_count == 0
