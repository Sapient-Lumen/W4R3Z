from __future__ import annotations

from dataclasses import replace

from i2p_dht_lab.custodyaudit import CustodyAuditChallenge, CustodyProof, CustodyProofKind
from i2p_dht_lab.epochgate import EpochHead, EpochObservation, EpochPurpose
from i2p_dht_lab.epochsplit import EpochSplitDecisionKind, EpochSplitPolicy, analyze_epoch_split_view
from i2p_dht_lab.identity import DhtKeypair, NodeIdentity
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.repairmarket import GardenRepairOffer, RepairOfferKind, RepairSelectionPolicy, RepairService, RepairWorkload, select_repair_offers
from i2p_dht_lab.repairreplay import RepairReplayDecisionKind, RepairReplayPolicy, RepairReplayWindow, analyze_repair_replay
from i2p_dht_lab.storecontract import StoreContractReceipt, StoreContractRequest, StorePurpose, StoreReceiptKind
from i2p_dht_lab.storewire import StoreWireDecisionKind, StoreWirePayloadKind, analyze_store_wire_transcript, make_store_wire_frame, payload_from_challenge, payload_from_proof, payload_from_receipt, payload_from_request
from i2p_dht_lab.surfacefold import audit_surface_fold
from i2p_dht_lab.surfaceledger import active_entries
from i2p_dht_lab.wirecanon import WireFrame, WireMessageKind


def kp(n: int) -> DhtKeypair:
    return DhtKeypair.from_seed(bytes([n % 256]) * 32)


def ident(n: int) -> NodeIdentity:
    return NodeIdentity.create(destination=f"rev0021-{n}.b32.i2p", keypair=kp(n))


def digest(label: str) -> bytes:
    return sha256(label.encode("utf-8"))


def epoch(seq: int, *, prev: bytes = b"\x00" * 32, payload_label: str | None = None, key_index: int = 1, scope: str = "seed-main", now: int = 10_000) -> EpochHead:
    return EpochHead.create(
        keypair=kp(key_index),
        purpose=EpochPurpose.SEED_PORTFOLIO,
        scope=scope,
        sequence=seq,
        prev_digest=prev,
        payload_digest=digest(payload_label or f"payload-{seq}"),
        issued_at=now,
        valid_from=now - 30,
        valid_until=now + 900,
    )


def obs(head: EpochHead, path: str, source: str, *, now: int = 10_010) -> EpochObservation:
    return EpochObservation(head=head, path_family=path, source_family=source, observed_at=now)


def store_request() -> StoreContractRequest:
    return StoreContractRequest(
        target=digest("store-target"),
        record_digest=digest("record-digest"),
        purpose=StorePurpose.MUTABLE_HEAD,
        namespace="rev0021.store",
        byte_count=2048,
        issued_at=20_000,
        expires_at=20_000 + 3600,
        slot_digest=digest("slot"),
    )


def store_receipt(request: StoreContractRequest, n: int, family: str = "famA", *, kind: StoreReceiptKind = StoreReceiptKind.ACCEPTED) -> StoreContractReceipt:
    node = ident(n)
    return StoreContractReceipt.create(
        keypair=kp(n),
        storage_node_id=node.node_id,
        family_id=family,
        request=request,
        kind=kind,
        replica_rank=1,
        issued_at=20_010,
        ttl=1200,
        retry_after_seconds=0 if kind is StoreReceiptKind.ACCEPTED else 600,
    )


def repair_workload() -> RepairWorkload:
    return RepairWorkload(
        workload_digest=digest("repair-workload"),
        services=(RepairService.STORE_REPAIR, RepairService.TOMBSTONE_REPAIR),
        purposes=(StorePurpose.MUTABLE_HEAD, StorePurpose.TOMBSTONE),
        byte_count=10_000,
        record_count=12,
        urgency=4,
        tombstone_pressure=1,
    )


def repair_offer(n: int, family: str, *, sequence: int = 1, now: int = 30_000, kind: RepairOfferKind = RepairOfferKind.CAPACITY, retry: int = 0) -> GardenRepairOffer:
    node = ident(n)
    return GardenRepairOffer.create(
        keypair=kp(n),
        garden_node_id=node.node_id,
        family_id=family,
        services=(RepairService.STORE_REPAIR, RepairService.TOMBSTONE_REPAIR),
        purposes=(StorePurpose.MUTABLE_HEAD, StorePurpose.TOMBSTONE),
        kind=kind,
        max_bytes=0 if kind is not RepairOfferKind.CAPACITY else 20_000,
        max_records=0 if kind is not RepairOfferKind.CAPACITY else 20,
        sequence=sequence,
        issued_at=now,
        ttl=600,
        retry_after_seconds=retry,
    )


def repair_report(offers: tuple[GardenRepairOffer, ...], *, now: int = 30_010):
    return select_repair_offers(
        repair_workload(),
        offers,
        now=now,
        policy=RepairSelectionPolicy(min_capacity_offers=3, min_families=3, max_per_family=1),
    )


def test_epochsplit_accepts_linked_diverse_latest_despite_single_stale_family() -> None:
    first = epoch(1)
    second = epoch(2, prev=first.head_digest)
    report = analyze_epoch_split_view(
        (obs(second, "pathA", "sourceA"), obs(second, "pathB", "sourceB"), obs(first, "pathC", "sourceStale")),
        now=10_020,
        accepted_head=first,
    )
    assert report.decision.kind is EpochSplitDecisionKind.ACCEPT_STABLE_ADVANCE
    assert report.decision.accept
    assert report.candidate == second
    assert len(report.stale_replays) == 1


def test_epochsplit_quarantines_same_sequence_fork_and_prev_split() -> None:
    first = epoch(1)
    second = epoch(2, prev=first.head_digest, payload_label="v2")
    fork = epoch(2, prev=first.head_digest, payload_label="v2-fork")
    fork_report = analyze_epoch_split_view((obs(second, "pathA", "sourceA"), obs(fork, "pathB", "sourceB")), now=10_020, accepted_head=first)
    assert fork_report.decision.kind is EpochSplitDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK
    assert fork_report.quarantined

    wrong_prev = epoch(3, prev=digest("wrong-prev"))
    prev_report = analyze_epoch_split_view((obs(wrong_prev, "pathA", "sourceA"), obs(wrong_prev, "pathB", "sourceB")), now=10_020, accepted_head=second)
    assert prev_report.decision.kind is EpochSplitDecisionKind.QUARANTINE_PREVIOUS_LINK_SPLIT


def test_epochsplit_quarantines_mesh_stale_replay_against_local_memory() -> None:
    first = epoch(1)
    second = epoch(2, prev=first.head_digest)
    report = analyze_epoch_split_view(
        (obs(first, "pathA", "sourceA"), obs(first, "pathB", "sourceB")),
        now=10_020,
        accepted_head=second,
        policy=EpochSplitPolicy(stale_replay_mesh_threshold=2),
    )
    assert report.decision.kind is EpochSplitDecisionKind.QUARANTINE_STALE_REPLAY_MESH
    assert len(report.stale_replays) == 2


def test_epochsplit_continues_when_latest_lacks_family_diversity() -> None:
    first = epoch(1)
    second = epoch(2, prev=first.head_digest)
    report = analyze_epoch_split_view((obs(second, "pathA", "sourceA"), obs(second, "pathA", "sourceA")), now=10_020, accepted_head=first)
    assert report.decision.kind is EpochSplitDecisionKind.CONTINUE_NEED_LATEST_DIVERSITY
    assert report.needs_more_rounds


def test_storewire_full_store_custody_cycle_validates() -> None:
    request = store_request()
    receipt = store_receipt(request, 11, "famA")
    challenge = CustodyAuditChallenge.create(nonce=b"nonce-1", issued_at=20_030, contract=receipt, ttl=300)
    proof = CustodyProof.create(keypair=kp(11), contract=receipt, challenge=challenge, kind=CustodyProofKind.HAVE_EXACT_DIGEST, observed_at=20_040, ttl=300)
    sender = ident(70)

    payloads = (payload_from_request(request), payload_from_receipt(receipt), payload_from_challenge(challenge), payload_from_proof(proof))
    frames = tuple(
        make_store_wire_frame(
            keypair=kp(70),
            sender_node_id=sender.node_id,
            request_id=digest(f"wire-{index}"),
            payload=payload,
            issued_at=20_050 + index,
            ttl=300,
            sequence=index,
        )
        for index, payload in enumerate(payloads)
    )
    report = analyze_store_wire_transcript(frames, now=20_060)
    assert report.decision.kind is StoreWireDecisionKind.ACCEPT_STORE_WIRE_TRANSCRIPT
    assert report.accepted_frame_count == 4
    assert report.role_counts[StoreWirePayloadKind.CUSTODY_PROOF] == 1


def test_storewire_detects_payload_tamper_and_role_mismatch() -> None:
    request = store_request()
    payload = payload_from_request(request)
    sender = ident(71)
    frame = make_store_wire_frame(keypair=kp(71), sender_node_id=sender.node_id, request_id=digest("wire-tamper"), payload=payload, issued_at=21_000, ttl=300)
    tampered_frame = replace(frame.frame, payload_digest=digest("wrong-wire-payload"))
    tampered = analyze_store_wire_transcript((replace(frame, frame=tampered_frame),), now=21_010, require_full_cycle=False)
    assert tampered.decision.kind is StoreWireDecisionKind.QUARANTINE_WIRE_VALIDATION

    wrong_role_frame = WireFrame.create(
        keypair=kp(71),
        sender_node_id=sender.node_id,
        message_kind=WireMessageKind.CUSTODY_PROOF,
        request_id=digest("wire-wrong-role"),
        payload=payload.to_bytes(),
        issued_at=21_000,
        ttl=300,
        flags=("storewire", payload.kind.value),
    )
    wrong_role = analyze_store_wire_transcript((replace(frame, frame=wrong_role_frame),), now=21_010, require_full_cycle=False)
    assert wrong_role.decision.kind is StoreWireDecisionKind.QUARANTINE_ROLE_MISMATCH


def test_storewire_requires_full_cycle_when_asked() -> None:
    request = store_request()
    sender = ident(72)
    frame = make_store_wire_frame(keypair=kp(72), sender_node_id=sender.node_id, request_id=digest("wire-partial"), payload=payload_from_request(request), issued_at=22_000, ttl=300)
    report = analyze_store_wire_transcript((frame,), now=22_010, require_full_cycle=True)
    assert report.decision.kind is StoreWireDecisionKind.CONTINUE_MISSING_REQUIRED_ROLES


def test_repairreplay_accepts_fresh_diverse_windows() -> None:
    report_a = repair_report((repair_offer(81, "famA", sequence=1), repair_offer(82, "famB", sequence=1), repair_offer(83, "famC", sequence=1)))
    report_b = repair_report((repair_offer(84, "famA", sequence=2), repair_offer(85, "famB", sequence=2), repair_offer(86, "famC", sequence=2)), now=30_100)
    replay = analyze_repair_replay((RepairReplayWindow(report_a, 0, 30_010), RepairReplayWindow(report_b, 1, 30_100)))
    assert replay.decision.kind is RepairReplayDecisionKind.ACCEPT_FRESH_DIVERSE_REPAIR_WINDOWS
    assert replay.decision.accept


def test_repairreplay_quarantines_replayed_offer_digest_and_sequence_rollback() -> None:
    reused = (repair_offer(91, "famA", sequence=4), repair_offer(92, "famB", sequence=4), repair_offer(93, "famC", sequence=4))
    report_a = repair_report(reused)
    report_b = repair_report(reused, now=30_100)
    replayed = analyze_repair_replay((RepairReplayWindow(report_a, 0, 30_010), RepairReplayWindow(report_b, 1, 30_100)))
    assert replayed.decision.kind is RepairReplayDecisionKind.QUARANTINE_REPLAYED_OFFERS

    early = repair_report((repair_offer(94, "famA", sequence=7), repair_offer(95, "famB", sequence=7), repair_offer(96, "famC", sequence=7)))
    rolled_offer = replace(early.selected[0], sequence=6)
    # Re-signing is intentionally absent: the replay analyzer checks sequence history on selected reports,
    # so use a synthetic report to pin the rollback pressure surface without pretending it is a valid new offer.
    late = replace(early, selected=(rolled_offer, early.selected[1], early.selected[2]))
    rollback = analyze_repair_replay((RepairReplayWindow(early, 0, 30_010), RepairReplayWindow(late, 1, 30_100)))
    assert rollback.decision.kind is RepairReplayDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK


def test_repairreplay_holds_useful_refusal_and_low_diversity() -> None:
    refusal = repair_offer(101, "famR", kind=RepairOfferKind.USEFUL_REFUSAL, retry=900)
    partial = select_repair_offers(
        repair_workload(),
        (repair_offer(102, "famA"), repair_offer(103, "famB"), refusal),
        now=30_010,
        policy=RepairSelectionPolicy(min_capacity_offers=3, min_families=3, max_per_family=1),
    )
    other = repair_report((repair_offer(104, "famA", sequence=2), repair_offer(105, "famB", sequence=2), repair_offer(106, "famC", sequence=2)), now=30_100)
    hold = analyze_repair_replay((RepairReplayWindow(partial, 0, 30_010), RepairReplayWindow(other, 1, 30_100)))
    assert hold.decision.kind is RepairReplayDecisionKind.HOLD_USEFUL_REFUSAL_BACKOFF
    assert hold.decision.retry_after_seconds == 900

    low_a = repair_report((repair_offer(111, "famA"), repair_offer(112, "famA"), repair_offer(113, "famA")))
    low_b = repair_report((repair_offer(114, "famA", sequence=2), repair_offer(115, "famA", sequence=2), repair_offer(116, "famA", sequence=2)), now=30_100)
    low = analyze_repair_replay((RepairReplayWindow(low_a, 0, 30_010), RepairReplayWindow(low_b, 1, 30_100)), policy=RepairReplayPolicy(min_distinct_families=2))
    assert low.decision.kind in {RepairReplayDecisionKind.CONTINUE_LOW_FAMILY_DIVERSITY, RepairReplayDecisionKind.QUARANTINE_COLLUDING_FAMILIES}


def test_surfaceledger_and_surfacefold_are_revision_aware() -> None:
    root = __import__("pathlib").Path(__file__).resolve().parents[1]
    entries = active_entries()
    assert any(entry.module.endswith("epochsplit.py") for entry in entries)
    assert any(entry.module.endswith("storewire.py") for entry in entries)
    assert any(entry.module.endswith("repairreplay.py") for entry in entries)
    report = audit_surface_fold(root, revision="rev0021", artifact_stem=root.name)
    assert report.status == "pass"
    assert any("rev0021" in path for path in report.current_docs)
