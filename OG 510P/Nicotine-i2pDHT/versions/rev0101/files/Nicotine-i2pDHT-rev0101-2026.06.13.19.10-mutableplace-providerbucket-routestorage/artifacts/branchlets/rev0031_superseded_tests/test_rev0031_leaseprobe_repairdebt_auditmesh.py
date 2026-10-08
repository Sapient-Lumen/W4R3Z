from __future__ import annotations

from pathlib import Path

from i2p_dht_lab.auditmesh import audit_current_mesh
from i2p_dht_lab.contactlease import ContactLease, ContactLeasePurpose
from i2p_dht_lab.egressmeter import EgressBudget, EgressEvent, EgressEventKind, assess_egress_window
from i2p_dht_lab.identity import DhtKeypair, NodeIdentity
from i2p_dht_lab.ids import key_id, sha256
from i2p_dht_lab.leaseprobe import LeaseProbeChallenge, LeaseProbeDecisionKind, LeaseProbeReceipt, assess_lease_probe
from i2p_dht_lab.repairdebt import RepairDebtDecisionKind, RepairDebtKind, RepairDebtPolicy, RepairDebtSignal, plan_repair_debt


def seed(label: str) -> bytes:
    return sha256(("rev0031-seed:" + label).encode("utf-8"))


def kp(label: str) -> DhtKeypair:
    return DhtKeypair.from_seed(seed(label))


def digest(label: str) -> bytes:
    return key_id("rev0031", label)


def lease(label: str, *, now: int, family: str = "lease-fam-A", purposes=(ContactLeasePurpose.ROUTE, ContactLeasePurpose.SEED_GATE)) -> tuple[DhtKeypair, ContactLease]:
    keypair = kp("lease-" + label)
    identity = NodeIdentity.create(destination=f"{label}.b32.i2p", keypair=keypair)
    return keypair, ContactLease.create(identity=identity, keypair=keypair, family_id=family, purposes=purposes, sequence=1, issued_at=now, ttl=900)


def challenge(label: str, *, requester: DhtKeypair, lease_obj: ContactLease, now: int, purpose: ContactLeasePurpose = ContactLeasePurpose.ROUTE, allow_raw: bool = False, max_probe_bytes: int = 2048) -> LeaseProbeChallenge:
    return LeaseProbeChallenge.create(
        requester=requester,
        lease=lease_obj,
        scope_digest=digest("scope-" + label),
        request_digest=digest("request-" + label),
        nonce=("nonce-" + label).encode("utf-8"),
        purpose=purpose,
        issued_at=now,
        ttl=120,
        max_probe_bytes=max_probe_bytes,
        allow_raw_key_exposure=allow_raw,
    )


def receipt(label: str, *, responder: DhtKeypair, lease_obj: ContactLease, challenge_obj: LeaseProbeChallenge, now: int, fam: str, path: str, response_bytes: int = 512, raw: int = 0) -> LeaseProbeReceipt:
    return LeaseProbeReceipt.create(
        responder=responder,
        lease=lease_obj,
        challenge=challenge_obj,
        source_family=fam,
        path_family=path,
        observed_at=now,
        response_bytes=response_bytes,
        raw_key_exposures=raw,
        note=label,
    )


def debt(label: str, *, kind: RepairDebtKind, signer: DhtKeypair, seq: int, now: int, fam: str, path: str, cost: int = 2) -> RepairDebtSignal:
    return RepairDebtSignal.create(
        signer=signer,
        kind=kind,
        scope_digest=digest("repair-scope"),
        object_digest=digest("repair-object-" + label),
        value_digest=digest("repair-value-" + label),
        sequence=seq,
        source_family=fam,
        path_family=path,
        cost=cost,
        issued_at=now,
        ttl=600,
    )


def test_lease_probe_accepts_budgeted_diverse_receipts() -> None:
    now = 1_766_400_000
    responder, lease_obj = lease("alpha", now=now)
    requester = kp("requester")
    ch = challenge("alpha", requester=requester, lease_obj=lease_obj, now=now)
    r1 = receipt("a", responder=responder, lease_obj=lease_obj, challenge_obj=ch, now=now + 1, fam="garden-A", path="path-A")
    r2 = receipt("b", responder=responder, lease_obj=lease_obj, challenge_obj=ch, now=now + 2, fam="garden-B", path="path-B")
    report = assess_lease_probe(lease=lease_obj, challenge=ch, receipts=(r1, r2), now=now + 3, expected_purpose=ContactLeasePurpose.ROUTE, requester_public_key=requester.public_key_bytes)
    assert report.decision_kind is LeaseProbeDecisionKind.ACCEPT_PROBE_RECEIPT
    assert report.accept
    assert report.source_families == ("garden-A", "garden-B")
    assert report.total_response_bytes == 1024


def test_lease_probe_rejects_replay_purpose_and_metadata_budget() -> None:
    now = 1_766_400_100
    responder, lease_obj = lease("beta", now=now, purposes=(ContactLeasePurpose.SEED_GATE,))
    requester = kp("requester-beta")
    ch = challenge("beta", requester=requester, lease_obj=lease_obj, now=now, purpose=ContactLeasePurpose.SEED_GATE)
    r1 = receipt("a", responder=responder, lease_obj=lease_obj, challenge_obj=ch, now=now + 1, fam="garden-A", path="path-A")
    purpose = assess_lease_probe(lease=lease_obj, challenge=ch, receipts=(r1,), now=now + 2, expected_purpose=ContactLeasePurpose.ROUTE)
    assert purpose.decision_kind is LeaseProbeDecisionKind.QUARANTINE_PURPOSE_MISMATCH

    replay = assess_lease_probe(lease=lease_obj, challenge=ch, receipts=(r1,), now=now + 2, expected_purpose=ContactLeasePurpose.SEED_GATE, previous_receipt_digests=(r1.receipt_digest,))
    assert replay.decision_kind is LeaseProbeDecisionKind.QUARANTINE_REPLAYED_RECEIPT

    raw_ch = challenge("beta-raw", requester=requester, lease_obj=lease_obj, now=now, purpose=ContactLeasePurpose.SEED_GATE, allow_raw=False)
    raw_receipt = receipt("raw", responder=responder, lease_obj=lease_obj, challenge_obj=raw_ch, now=now + 1, fam="garden-A", path="path-A", raw=1)
    raw_report = assess_lease_probe(lease=lease_obj, challenge=raw_ch, receipts=(raw_receipt,), now=now + 2, expected_purpose=ContactLeasePurpose.SEED_GATE)
    assert raw_report.decision_kind is LeaseProbeDecisionKind.QUARANTINE_EGRESS_BUDGET


def test_lease_probe_joins_egress_meter_before_side_effects() -> None:
    now = 1_766_400_200
    _responder, lease_obj = lease("gamma", now=now)
    requester = kp("requester-gamma")
    ch = challenge("gamma", requester=requester, lease_obj=lease_obj, now=now)
    bad_egress = assess_egress_window((
        EgressEvent(EgressEventKind.PROVIDER_REAL_PROBE, digest("egress-scope"), digest("obj"), lease_obj.node_id, "fam-A", "path-A", now, now + 100, 1024, exposes_raw_key=True),
    ), now=now + 1, budget=EgressBudget(min_decoy_per_real_probe=1))
    report = assess_lease_probe(lease=lease_obj, challenge=ch, receipts=(), now=now + 2, expected_purpose=ContactLeasePurpose.ROUTE, egress=bad_egress)
    assert report.decision_kind is LeaseProbeDecisionKind.QUARANTINE_EGRESS_BUDGET


def test_repair_debt_selects_hard_negatives_before_soft_repairs() -> None:
    now = 1_766_401_000
    signer = kp("repair-signer")
    signals = (
        debt("tomb", kind=RepairDebtKind.TOMBSTONE, signer=signer, seq=1, now=now, fam="fam-A", path="path-A", cost=3),
        debt("crisis", kind=RepairDebtKind.KEY_CRISIS, signer=signer, seq=1, now=now, fam="fam-B", path="path-B", cost=3),
        debt("provider", kind=RepairDebtKind.PROVIDER_TRUE, signer=signer, seq=1, now=now, fam="fam-C", path="path-C", cost=6),
    )
    plan = plan_repair_debt(signals, now=now + 1, policy=RepairDebtPolicy(max_total_cost=8, hard_negative_reserve=6))
    assert plan.accept
    assert plan.decision_kind in {RepairDebtDecisionKind.ACCEPT_REPAIR_PLAN, RepairDebtDecisionKind.CONTINUE_BUDGET_LIMITED}
    assert plan.hard_selected == 2
    assert plan.soft_selected == 0
    assert len(plan.deferred_digests) == 1


def test_repair_debt_detects_rollback_fork_and_family_monoculture() -> None:
    now = 1_766_401_100
    signer = kp("repair-signer-fork")
    first = debt("same", kind=RepairDebtKind.MUTABLE_HEAD, signer=signer, seq=5, now=now, fam="fam-A", path="path-A")
    rollback = RepairDebtSignal.create(signer=signer, kind=RepairDebtKind.MUTABLE_HEAD, scope_digest=first.scope_digest, object_digest=first.object_digest, value_digest=first.value_digest, sequence=4, source_family="fam-B", path_family="path-B", cost=2, issued_at=now)
    rollback_report = plan_repair_debt((rollback,), now=now + 1, previous_sequences={first.subject_key: (5, first.signal_digest)})
    assert rollback_report.decision_kind is RepairDebtDecisionKind.QUARANTINE_ROLLBACK

    fork = RepairDebtSignal.create(signer=signer, kind=RepairDebtKind.MUTABLE_HEAD, scope_digest=first.scope_digest, object_digest=first.object_digest, value_digest=digest("different"), sequence=5, source_family="fam-B", path_family="path-B", cost=2, issued_at=now)
    fork_report = plan_repair_debt((fork,), now=now + 1, previous_sequences={first.subject_key: (5, first.signal_digest)})
    assert fork_report.decision_kind is RepairDebtDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK

    flood = tuple(debt(f"flood-{idx}", kind=RepairDebtKind.TOMBSTONE, signer=signer, seq=idx + 1, now=now, fam="fam-Z", path=f"path-{idx}") for idx in range(5))
    flood_report = plan_repair_debt(flood, now=now + 1, policy=RepairDebtPolicy(max_per_source_family=3, min_source_families=2))
    assert flood_report.decision_kind is RepairDebtDecisionKind.QUARANTINE_FAMILY_MONOCULTURE


def test_audit_mesh_keeps_rev0031_surface_and_predecessor_visible() -> None:
    root = Path(__file__).resolve().parents[1]
    report = audit_current_mesh(root)
    assert report.status == "pass"
    assert report.predecessor_status == "rev0030_keycrisisfold:pass"
    assert report.error_count == 0
