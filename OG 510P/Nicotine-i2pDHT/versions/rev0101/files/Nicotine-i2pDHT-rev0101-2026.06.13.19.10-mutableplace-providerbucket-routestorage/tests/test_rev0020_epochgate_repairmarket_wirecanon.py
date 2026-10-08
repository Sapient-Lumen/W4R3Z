from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from i2p_dht_lab.epochgate import (
    EpochGateDecisionKind,
    EpochGatePolicy,
    EpochHead,
    EpochMemory,
    EpochObservation,
    EpochPurpose,
    assess_epoch_observations,
)
from i2p_dht_lab.identity import DhtKeypair, NodeIdentity
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.repairmarket import (
    GardenRepairOffer,
    RepairOfferKind,
    RepairSelectionKind,
    RepairSelectionPolicy,
    RepairService,
    RepairWorkload,
    select_repair_offers,
)
from i2p_dht_lab.storecontract import StorePurpose
from i2p_dht_lab.surfacefold import audit_surface_fold
from i2p_dht_lab.wirecanon import WireFrame, WireMessageKind, WireValidationKind, build_wire_transcript, validate_wire_frame


def kp(n: int) -> DhtKeypair:
    return DhtKeypair.from_seed(bytes([n % 256]) * 32)


def ident(n: int) -> NodeIdentity:
    return NodeIdentity.create(destination=f"rev0020-{n}.b32.i2p", keypair=kp(n))


def digest(label: str) -> bytes:
    return sha256(label.encode("utf-8"))


def epoch(seq: int, *, prev: bytes = b"\x00" * 32, key_index: int = 1, scope: str = "seed-main", payload_label: str | None = None, now: int = 1000) -> EpochHead:
    return EpochHead.create(
        keypair=kp(key_index),
        purpose=EpochPurpose.SEED_PORTFOLIO,
        scope=scope,
        sequence=seq,
        prev_digest=prev,
        payload_digest=digest(payload_label or f"payload:{seq}"),
        issued_at=now,
        valid_from=now - 10,
        valid_until=now + 500,
    )


def obs(head: EpochHead, path: str, source: str, *, now: int = 1010) -> EpochObservation:
    return EpochObservation(head=head, path_family=path, source_family=source, observed_at=now)


def offer(n: int, family: str, services: tuple[RepairService, ...], *, now: int = 2000, kind: RepairOfferKind = RepairOfferKind.CAPACITY, retry: int = 0) -> GardenRepairOffer:
    node = ident(n)
    return GardenRepairOffer.create(
        keypair=kp(n),
        garden_node_id=node.node_id,
        family_id=family,
        services=services,
        purposes=(StorePurpose.MUTABLE_HEAD, StorePurpose.TOMBSTONE),
        kind=kind,
        max_bytes=0 if kind is not RepairOfferKind.CAPACITY else 10_000,
        max_records=0 if kind is not RepairOfferKind.CAPACITY else 10,
        sequence=1,
        issued_at=now - 5,
        ttl=600,
        retry_after_seconds=retry,
    )


def workload(*, tombstone: int = 0) -> RepairWorkload:
    return RepairWorkload(
        workload_digest=digest("repair-workload"),
        services=(RepairService.STORE_REPAIR, RepairService.TOMBSTONE_REPAIR),
        purposes=(StorePurpose.MUTABLE_HEAD, StorePurpose.TOMBSTONE),
        byte_count=20_000,
        record_count=12,
        urgency=5,
        tombstone_pressure=tombstone,
    )


def test_epoch_gate_accepts_first_and_linked_advance() -> None:
    memory = EpochMemory()
    first = epoch(1)
    report = assess_epoch_observations(memory, (obs(first, "pA", "sA"), obs(first, "pB", "sB")), now=1010)
    assert report.decision.kind is EpochGateDecisionKind.ACCEPT_FIRST_EPOCH
    assert report.decision.accept
    assert memory.accepted[first.scope_id].head_digest == first.head_digest

    second = epoch(2, prev=first.head_digest, payload_label="payload:2")
    advance = assess_epoch_observations(memory, (obs(second, "pA", "sA"), obs(second, "pC", "sC")), now=1010)
    assert advance.decision.kind is EpochGateDecisionKind.ACCEPT_ADVANCE
    assert memory.accepted[first.scope_id].head_digest == second.head_digest


def test_epoch_gate_detects_rollback_fork_and_missing_prev() -> None:
    memory = EpochMemory()
    first = epoch(1)
    second = epoch(2, prev=first.head_digest)
    assert assess_epoch_observations(memory, (obs(first, "pA", "sA"), obs(first, "pB", "sB")), now=1010).decision.accept
    assert assess_epoch_observations(memory, (obs(second, "pA", "sA"), obs(second, "pB", "sB")), now=1010).decision.accept

    rollback = assess_epoch_observations(memory, (obs(first, "pA", "sA"), obs(first, "pB", "sB")), now=1010)
    assert rollback.decision.kind is EpochGateDecisionKind.QUARANTINE_ROLLBACK
    assert first.scope_id in memory.rollbacks

    fork = epoch(2, prev=first.head_digest, payload_label="payload:fork")
    fork_report = assess_epoch_observations(EpochMemory(accepted={first.scope_id: first}), (obs(second, "pA", "sA"), obs(fork, "pB", "sB")), now=1010)
    assert fork_report.decision.kind is EpochGateDecisionKind.QUARANTINE_FORK

    gap = epoch(3, prev=digest("wrong-prev"))
    gap_report = assess_epoch_observations(memory, (obs(gap, "pA", "sA"), obs(gap, "pB", "sB")), now=1010)
    assert gap_report.decision.kind is EpochGateDecisionKind.CONTINUE_MISSING_PREV
    assert gap.scope_id in memory.gaps


def test_epoch_gate_watches_low_diversity_without_commit() -> None:
    memory = EpochMemory()
    head = epoch(1)
    report = assess_epoch_observations(memory, (obs(head, "pA", "sA"), obs(head, "pA", "sA")), now=1010)
    assert report.decision.kind is EpochGateDecisionKind.WATCH_LOW_DIVERSITY
    assert head.scope_id not in memory.accepted


def test_repair_market_accepts_diverse_capacity_and_tombstone_service() -> None:
    report = select_repair_offers(
        workload(tombstone=1),
        (
            offer(10, "famA", (RepairService.STORE_REPAIR, RepairService.TOMBSTONE_REPAIR)),
            offer(11, "famB", (RepairService.STORE_REPAIR,)),
            offer(12, "famC", (RepairService.CUSTODY_AUDIT, RepairService.STORE_REPAIR)),
        ),
        now=2000,
    )
    assert report.decision.kind is RepairSelectionKind.ACCEPT_DIVERSE_REPAIR_SET
    assert report.total_records >= 30
    assert set(report.family_counts) == {"famA", "famB", "famC"}


def test_repair_market_quarantines_family_capture_and_holds_refusal() -> None:
    captured = select_repair_offers(
        workload(),
        (
            offer(20, "famA", (RepairService.STORE_REPAIR,)),
            offer(21, "famA", (RepairService.STORE_REPAIR,)),
            offer(22, "famA", (RepairService.STORE_REPAIR,)),
        ),
        now=2000,
    )
    assert captured.decision.kind is RepairSelectionKind.QUARANTINE_FAMILY_CAPTURE

    refused = select_repair_offers(
        workload(),
        (offer(30, "famR", (RepairService.STORE_REPAIR,), kind=RepairOfferKind.USEFUL_REFUSAL, retry=900),),
        now=2000,
        policy=RepairSelectionPolicy(min_capacity_offers=2, min_families=2),
    )
    assert refused.decision.kind is RepairSelectionKind.HOLD_USEFUL_REFUSAL
    assert refused.decision.retry_after_seconds == 900


def test_repair_market_rejects_bad_signed_offer() -> None:
    bad = replace(offer(40, "famBad", (RepairService.STORE_REPAIR,)), signature=b"x" * 64)
    report = select_repair_offers(workload(), (bad,), now=2000)
    assert report.decision.kind is RepairSelectionKind.QUARANTINE_BAD_SIGNATURE


def test_wirecanon_validates_payloads_and_transcripts() -> None:
    node = ident(50)
    payload = b"canonical request body"
    frame = WireFrame.create(
        keypair=kp(50),
        sender_node_id=node.node_id,
        message_kind=WireMessageKind.STORE_RECORD,
        request_id=digest("request-1"),
        payload=payload,
        issued_at=3000,
        ttl=100,
        flags=("garden", "store"),
    )
    verdict = validate_wire_frame(frame, payload=payload, now=3010)
    assert verdict.kind is WireValidationKind.ACCEPT_FRAME

    tampered = validate_wire_frame(frame, payload=b"other payload", now=3010)
    assert tampered.kind is WireValidationKind.REJECT_PAYLOAD_DIGEST

    transcript = build_wire_transcript(((frame, payload), (frame, b"other payload")), now=3010)
    assert transcript.accepted_count == 1
    assert transcript.rejected_count == 1
    assert transcript.transcript_digest == build_wire_transcript(((frame, payload), (frame, b"other payload")), now=3010).transcript_digest


def test_wirecanon_rejects_bad_signature_and_expired_frame() -> None:
    node = ident(60)
    payload = b"epoch body"
    frame = WireFrame.create(keypair=kp(60), sender_node_id=node.node_id, message_kind=WireMessageKind.EPOCH_HEAD, request_id=digest("request-2"), payload=payload, issued_at=4000, ttl=50)
    bad_sig = replace(frame, signature=b"z" * 64)
    assert validate_wire_frame(bad_sig, payload=payload, now=4010).kind is WireValidationKind.REJECT_BAD_SIGNATURE
    assert validate_wire_frame(frame, payload=payload, now=4100).kind is WireValidationKind.REJECT_TIME_WINDOW


def test_surfacefold_current_cube_navigation() -> None:
    root = Path(__file__).resolve().parents[1]
    stem = root.name
    report = audit_surface_fold(root, revision="rev0020", artifact_stem=stem)
    assert report.status == "pass"
    assert any("rev0020" in path for path in report.current_docs)
