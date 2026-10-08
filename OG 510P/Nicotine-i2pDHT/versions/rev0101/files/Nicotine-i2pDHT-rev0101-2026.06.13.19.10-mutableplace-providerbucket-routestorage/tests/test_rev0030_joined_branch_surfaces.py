from i2p_dht_lab.absencegate import AbsenceDecisionKind, AbsenceObservation, AbsenceObservationKind, AbsencePolicy, assess_absence_window
from i2p_dht_lab.bootstrapjoin import BootstrapJoinDecisionKind, BootstrapJoinPolicy, assess_bootstrap_join
from i2p_dht_lab.checkpointlane import CheckpointDecisionKind, CheckpointFact, CheckpointFactKind, StateCheckpoint, assess_checkpoint
from i2p_dht_lab.contactlease import ContactLease, ContactLeasePurpose
from i2p_dht_lab.deltarepairjoin import DeltaRepairJoinDecisionKind, assess_delta_repair_join
from i2p_dht_lab.deltasketch import DeltaSketchDecisionKind, DeltaSketchItem, DeltaSketchKind, DeltaSketchPolicy, SignedDeltaSketch, assess_delta_sketches, build_delta_sketch
from i2p_dht_lab.egressmeter import EgressBudget, EgressDecisionKind, EgressEvent, EgressEventKind, assess_egress_window
from i2p_dht_lab.identity import DhtKeypair, NodeIdentity
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.keycrisis import KeyCrisisDecisionKind, KeyCrisisPolicy, KeyCrisisRecord, RecoveryWitness, assess_key_crisis
from i2p_dht_lab.keycrisisjoin import KeyCrisisJoinDecisionKind, assess_key_crisis_join
from i2p_dht_lab.liveprobe import LiveProbeChallenge, LiveProbeDecisionKind, LiveProbeReceipt, assess_live_probe
from i2p_dht_lab.livesmoke import SamSmokeDecisionKind, SamSmokeObservation, SamSmokeObservationKind, SamSmokePlan, assess_sam_live_smoke
from i2p_dht_lab.peerbook import PeerBookPolicy, PeerLeaseObservation, build_peerbook_view
from i2p_dht_lab.persistlane import ZERO_DIGEST
from i2p_dht_lab.samwire import SamStepKind, SamWireStep


def kp(n: int) -> DhtKeypair:
    return DhtKeypair.from_seed(bytes([n % 256]) * 32)


def digest(label: str) -> bytes:
    return sha256(label.encode("utf-8"))


def ident(n: int) -> NodeIdentity:
    return NodeIdentity.create(destination=f"rev0030-join-{n}.b32.i2p", keypair=kp(n))


def lease(n: int, *, now: int, family: str, purposes=(ContactLeasePurpose.ROUTE, ContactLeasePurpose.SEED_GATE)) -> ContactLease:
    return ContactLease.create(identity=ident(n), keypair=kp(n), family_id=family, purposes=purposes, sequence=1, issued_at=now, ttl=900)


def peer_obs(n: int, *, now: int, family: str, channel_family: str) -> PeerLeaseObservation:
    return PeerLeaseObservation(lease(n, now=now, family=family), channel_id=f"chan-{n}", channel_family=channel_family, observed_at=now + 1)


def egress(n: int, *, now: int, family: str, kind=EgressEventKind.PROVIDER_DECOY_PROBE, raw=False) -> EgressEvent:
    return EgressEvent(kind=kind, scope_id=digest("scope"), object_digest=digest(f"object-{n}"), destination_node_id=ident(n).node_id, destination_family=family, path_family=f"path-{family}", issued_at=now, expires_at=now + 60, byte_cost=512, exposes_raw_key=raw)


def test_bootstrap_join_accepts_only_after_peerbook_live_probe_and_egress_agree() -> None:
    now = 1_766_400_000
    view = build_peerbook_view(
        (peer_obs(1, now=now, family="peer-A", channel_family="chan-A"), peer_obs(2, now=now, family="peer-B", channel_family="chan-B"), peer_obs(3, now=now, family="peer-C", channel_family="chan-C")),
        now=now + 2,
        target_id=digest("bootstrap"),
        policy=PeerBookPolicy(min_peer_families=3, min_channel_families=3, min_channels=3),
    )
    assert view.accept
    l = lease(1, now=now, family="peer-A")
    challenge = LiveProbeChallenge(challenger_node_id=digest("challenger"), lease_hash=l.lease_hash, nonce=b"n", issued_at=now, expires_at=now + 60)
    receipt = LiveProbeReceipt.create(keypair=kp(1), lease=l, challenge=challenge, observed_at=now + 1)
    live = assess_live_probe(lease=l, challenge=challenge, receipt=receipt, now=now + 2)
    assert live.decision_kind is LiveProbeDecisionKind.ACCEPT_LIVE_PROBE
    budget = assess_egress_window((egress(1, now=now, family="eg-A"), egress(2, now=now, family="eg-B")), now=now + 1)
    joined = assess_bootstrap_join(peerbook=view, live_probes=(live,), egress=budget)
    assert joined.decision_kind is BootstrapJoinDecisionKind.ACCEPT_BOOTSTRAP_WINDOW


def test_bootstrap_join_does_not_let_soft_absence_or_bad_egress_close_window() -> None:
    now = 1_766_400_100
    view = build_peerbook_view((peer_obs(1, now=now, family="A", channel_family="IA"), peer_obs(2, now=now, family="B", channel_family="IB"), peer_obs(3, now=now, family="C", channel_family="IC")), now=now + 2, policy=PeerBookPolicy(min_peer_families=3, min_channel_families=3, min_channels=3))
    target = digest("target")
    soft = assess_absence_window(
        target,
        tuple(AbsenceObservation.create(keypair=kp(20 + i), target_digest=target, kind=AbsenceObservationKind.EMPTY_PROVIDER, source_family=f"F{i}", path_family=f"P{i}", issued_at=now) for i in range(3)),
        now=now + 1,
        policy=AbsencePolicy(min_empty_families=3, min_empty_paths=3),
    )
    assert soft.decision_kind is AbsenceDecisionKind.ACCEPT_SOFT_NEGATIVE_CACHE
    held = assess_bootstrap_join(peerbook=view, absence=soft, policy=BootstrapJoinPolicy(min_live_probes=0))
    assert held.decision_kind is BootstrapJoinDecisionKind.CONTINUE_ABSENCE_PRESSURE
    bad_budget = assess_egress_window((egress(1, now=now, family="X", kind=EgressEventKind.PROVIDER_REAL_PROBE, raw=True),), budget=EgressBudget(min_destination_families_for_risky=2, min_decoy_per_real_probe=1), now=now + 1)
    assert not bad_budget.accept or bad_budget.decision_kind is EgressDecisionKind.QUARANTINE_FAMILY_MONOCULTURE
    blocked = assess_bootstrap_join(peerbook=view, egress=bad_budget, policy=BootstrapJoinPolicy(min_live_probes=0))
    assert blocked.decision_kind is BootstrapJoinDecisionKind.QUARANTINE_EGRESS_BUDGET


def test_livesmoke_accepts_lease_bound_sam_wire_and_rejects_destination_drift() -> None:
    now = 1_766_400_200
    l = lease(5, now=now, family="smoke-A")
    steps = (
        SamWireStep.create(keypair=kp(5), kind=SamStepKind.HELLO, session_id="dht", destination=l.destination, issued_at=now),
        SamWireStep.create(keypair=kp(5), kind=SamStepKind.SESSION_CREATE, session_id="dht", destination=l.destination, issued_at=now + 1),
    )
    report = assess_sam_live_smoke(lease=l, plan=SamSmokePlan(), observations=(SamSmokeObservation(SamSmokeObservationKind.HELLO_OK, now + 2), SamSmokeObservation(SamSmokeObservationKind.SESSION_OK, now + 2)), sam_steps=steps, now=now + 3)
    assert report.decision_kind is SamSmokeDecisionKind.ACCEPT_SMOKE_PROBE
    drift_steps = (
        SamWireStep.create(keypair=kp(5), kind=SamStepKind.HELLO, session_id="dht", destination="wrong.b32.i2p", issued_at=now),
        SamWireStep.create(keypair=kp(5), kind=SamStepKind.SESSION_CREATE, session_id="dht", destination="wrong.b32.i2p", issued_at=now + 1),
    )
    drift = assess_sam_live_smoke(lease=l, plan=SamSmokePlan(), observations=(SamSmokeObservation(SamSmokeObservationKind.HELLO_OK, now + 2),), sam_steps=drift_steps, now=now + 3)
    assert drift.decision_kind is SamSmokeDecisionKind.QUARANTINE_DESTINATION_DRIFT


def test_keycrisis_join_accepts_recovery_only_when_checkpoint_preserves_hard_negative() -> None:
    now = 1_766_400_300
    old = kp(20)
    new = kp(21)
    recovery_a = kp(30)
    recovery_b = kp(31)
    scope = digest("writer-scope")
    record = KeyCrisisRecord.create_recovery_rotation(old_public_key=old.public_key_bytes, new_keypair=new, scope_id=scope, sequence=1, issued_at=now)
    witnesses = (
        RecoveryWitness.create(keypair=recovery_a, crisis_digest=record.record_digest, source_family="RA", path_family="PA", issued_at=now),
        RecoveryWitness.create(keypair=recovery_b, crisis_digest=record.record_digest, source_family="RB", path_family="PB", issued_at=now),
    )
    crisis = assess_key_crisis(record, witnesses, now=now + 10, old_key_compromised=True, policy=KeyCrisisPolicy(recovery_public_keys=(recovery_a.public_key_bytes, recovery_b.public_key_bytes), recovery_threshold=2, min_recovery_families=2))
    assert crisis.decision_kind is KeyCrisisDecisionKind.ACCEPT_RECOVERY_ROTATION
    fact = CheckpointFact(CheckpointFactKind.TOMBSTONE, scope, digest("old-key-compromise"), 1, "cf-A", "pf-A", now, now + 600)
    checkpoint = StateCheckpoint.create(keypair=kp(40), generation=1, prev_checkpoint_digest=ZERO_DIGEST, journal_tip_digest=digest("journal"), facts=(fact,), issued_at=now)
    ok = assess_checkpoint(checkpoint, now=now + 1)
    accepted = assess_key_crisis_join(crisis=crisis, checkpoint=ok)
    assert accepted.decision_kind is KeyCrisisJoinDecisionKind.ACCEPT_RECOVERY_ROTATION
    later = StateCheckpoint.create(keypair=kp(40), generation=2, prev_checkpoint_digest=checkpoint.checkpoint_digest, journal_tip_digest=digest("journal2"), facts=(), issued_at=now + 2)
    dropped = assess_checkpoint(later, previous=checkpoint, now=now + 3)
    assert dropped.decision.kind is CheckpointDecisionKind.QUARANTINE_HARD_FACT_DROP
    blocked = assess_key_crisis_join(crisis=crisis, checkpoint=dropped)
    assert blocked.decision_kind is KeyCrisisJoinDecisionKind.QUARANTINE_CHECKPOINT_MEMORY


def test_delta_repair_join_keeps_tombstone_first_until_exact_repair_or_sync() -> None:
    now = 1_766_400_400
    provider = DeltaSketchItem(digest("k1"), digest("v1"), DeltaSketchKind.PROVIDER, sequence=1)
    tomb = DeltaSketchItem(digest("k2"), digest("tomb"), DeltaSketchKind.TOMBSTONE, sequence=2, tombstone=True)
    local = build_delta_sketch((provider,), bucket_count=4)
    remote = build_delta_sketch((provider, tomb), bucket_count=4)
    remotes = (
        SignedDeltaSketch.create(keypair=kp(50), source_node_id=ident(50).node_id, source_family="DF-A", sketch=remote, sequence=1, issued_at=now),
        SignedDeltaSketch.create(keypair=kp(51), source_node_id=ident(51).node_id, source_family="DF-B", sketch=remote, sequence=1, issued_at=now),
    )
    repair = assess_delta_sketches(local, remotes, now=now + 1, policy=DeltaSketchPolicy(min_source_families=2, tombstone_first=True))
    assert repair.decision_kind is DeltaSketchDecisionKind.REQUEST_TOMBSTONE_FIRST
    joined = assess_delta_repair_join(sketch=repair)
    assert joined.decision_kind is DeltaRepairJoinDecisionKind.CONTINUE_TOMBSTONE_FIRST
    synced = assess_delta_sketches(remote, remotes, now=now + 1, policy=DeltaSketchPolicy(min_source_families=2))
    assert assess_delta_repair_join(sketch=synced).decision_kind is DeltaRepairJoinDecisionKind.ACCEPT_IN_SYNC
