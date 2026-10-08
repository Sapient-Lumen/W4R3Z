from dataclasses import replace

from i2p_dht_lab.absencegate import AbsenceDecisionKind, AbsenceObservation, AbsenceObservationKind, AbsencePolicy, assess_absence_window
from i2p_dht_lab.bootstrapjoin import BootstrapJoinDecisionKind, BootstrapJoinPolicy, assess_bootstrap_join
from i2p_dht_lab.checkpointlane import CheckpointDecisionKind, CheckpointFact, CheckpointFactKind, StateCheckpoint, assess_checkpoint
from i2p_dht_lab.contactlease import ContactLease, ContactLeasePurpose
from i2p_dht_lab.deltarepairjoin import DeltaRepairJoinDecisionKind, assess_delta_repair_join
from i2p_dht_lab.deltasketch import DeltaSketchDecisionKind, DeltaSketchItem, DeltaSketchKind, DeltaSketchPolicy, SignedDeltaSketch, assess_delta_sketches, build_delta_sketch
from i2p_dht_lab.egressmeter import EgressBudget, EgressDecisionKind, EgressEvent, EgressEventKind, assess_egress_window
from i2p_dht_lab.identity import DhtKeypair, NodeIdentity
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.keycrisis import KeyCrisisGateDecisionKind, KeyCrisisKind, KeyCrisisMemory, KeyCrisisNotice, gate_keyed_operation
from i2p_dht_lab.keycrisisjoin import KeyCrisisJoinDecisionKind, assess_key_crisis_join
from i2p_dht_lab.liveprobe import LiveProbeChallenge, LiveProbeDecisionKind, LiveProbeReceipt, assess_live_probe
from i2p_dht_lab.livesmoke import SamSmokeDecisionKind, SamSmokeObservation, SamSmokeObservationKind, SamSmokePlan, assess_sam_live_smoke
from i2p_dht_lab.peerbook import PeerBookDecisionKind, PeerBookPolicy, PeerLeaseObservation, build_peerbook_view
from i2p_dht_lab.persistlane import ZERO_DIGEST
from i2p_dht_lab.samwire import SamStepKind, SamWireStep


def kp(n: int) -> DhtKeypair:
    return DhtKeypair.from_seed(bytes([n % 256]) * 32)


def digest(label: str) -> bytes:
    return sha256(label.encode("utf-8"))


def ident(n: int) -> NodeIdentity:
    return NodeIdentity.create(destination=f"rev0030-node-{n}.b32.i2p", keypair=kp(n))


def lease(n: int, *, seq: int, now: int, fam: str, purposes=(ContactLeasePurpose.SEED_GATE, ContactLeasePurpose.ROUTE)) -> ContactLease:
    return ContactLease.create(identity=ident(n), keypair=kp(n), family_id=fam, purposes=purposes, sequence=seq, issued_at=now, ttl=600)


def peer_obs(n: int, *, now: int, fam: str, intro: str, path: str) -> PeerLeaseObservation:
    return PeerLeaseObservation(lease(n, seq=1, now=now, fam=fam), channel_id=path, channel_family=intro, observed_at=now + 1)


def live_report_for(lease_obj: ContactLease, *, now: int):
    challenge = LiveProbeChallenge(challenger_node_id=digest("challenger"), lease_hash=lease_obj.lease_hash, nonce=b"nonce", issued_at=now, expires_at=now + 60)
    receipt = LiveProbeReceipt.create(keypair=kp(lease_obj.public_key[0] if lease_obj.public_key[0] else 1), lease=lease_obj, challenge=challenge, observed_at=now + 1)
    # The helper above cannot recover the seed from the public key; create receipt with the known lease key instead in tests.
    return assess_live_probe(lease=lease_obj, challenge=challenge, receipt=receipt, now=now + 2)


def live_report(n: int, *, now: int, fam: str):
    l = lease(n, seq=1, now=now, fam=fam)
    challenge = LiveProbeChallenge(challenger_node_id=digest("challenger"), lease_hash=l.lease_hash, nonce=b"nonce", issued_at=now, expires_at=now + 60)
    receipt = LiveProbeReceipt.create(keypair=kp(n), lease=l, challenge=challenge, observed_at=now + 1)
    return l, assess_live_probe(lease=l, challenge=challenge, receipt=receipt, now=now + 2)


def egress_event(n: int, *, now: int, fam: str, kind=EgressEventKind.PROVIDER_DECOY_PROBE, raw=False) -> EgressEvent:
    return EgressEvent(kind=kind, scope_id=digest("scope"), object_digest=digest(f"object-{n}"), destination_node_id=ident(n).node_id, destination_family=fam, path_family=f"path-{fam}", issued_at=now, expires_at=now + 60, byte_cost=512, exposes_raw_key=raw)


def absence_obs(n: int, *, now: int, kind: AbsenceObservationKind, fam: str, path: str) -> AbsenceObservation:
    return AbsenceObservation.create(keypair=kp(n), target_digest=digest("target"), kind=kind, source_family=fam, path_family=path, issued_at=now, latency_ms=20)


def test_bootstrap_join_accepts_diverse_peerbook_live_probe_and_budget() -> None:
    now = 1_766_200_000
    observations = (
        peer_obs(1, now=now, fam="contact-A", intro="intro-A", path="path-A"),
        peer_obs(2, now=now, fam="contact-B", intro="intro-B", path="path-B"),
        peer_obs(3, now=now, fam="contact-C", intro="intro-C", path="path-C"),
    )
    peerbook = build_peerbook_view(observations, target_id=digest("bootstrap"), now=now + 2, policy=PeerBookPolicy(min_peer_families=3, min_channel_families=3, min_channels=3))
    assert peerbook.decision_kind in {PeerBookDecisionKind.ACCEPT_ENTRANCE_VIEW, PeerBookDecisionKind.ACCEPT_WITH_WATCH}
    _, live = live_report(1, now=now, fam="contact-A")
    assert live.decision_kind is LiveProbeDecisionKind.ACCEPT_LIVE_PROBE
    egress = assess_egress_window((egress_event(1, now=now, fam="eg-A"), egress_event(2, now=now, fam="eg-B")), now=now + 1)
    assert egress.accept
    joined = assess_bootstrap_join(peerbook=peerbook, live_probes=(live,), egress=egress)
    assert joined.decision_kind is BootstrapJoinDecisionKind.ACCEPT_BOOTSTRAP_WINDOW
    assert joined.accept


def test_bootstrap_join_blocks_soft_absence_and_egress_failure() -> None:
    now = 1_766_200_100
    peerbook = build_peerbook_view(
        (peer_obs(1, now=now, fam="A", intro="IA", path="PA"), peer_obs(2, now=now, fam="B", intro="IB", path="PB"), peer_obs(3, now=now, fam="C", intro="IC", path="PC")),
        target_id=digest("bootstrap"),
        now=now + 2,
        policy=PeerBookPolicy(min_peer_families=3, min_channel_families=3, min_channels=3),
    )
    soft_absence = assess_absence_window(
        digest("target"),
        (
            absence_obs(10, now=now, kind=AbsenceObservationKind.EMPTY_PROVIDER, fam="F1", path="P1"),
            absence_obs(11, now=now, kind=AbsenceObservationKind.EMPTY_PROVIDER, fam="F2", path="P2"),
            absence_obs(12, now=now, kind=AbsenceObservationKind.EMPTY_PROVIDER, fam="F3", path="P3"),
        ),
        now=now + 1,
        policy=AbsencePolicy(min_empty_families=3, min_empty_paths=3),
    )
    assert soft_absence.decision_kind is AbsenceDecisionKind.ACCEPT_SOFT_NEGATIVE_CACHE
    joined = assess_bootstrap_join(peerbook=peerbook, absence=soft_absence, policy=BootstrapJoinPolicy(min_live_probes=0))
    assert joined.decision_kind is BootstrapJoinDecisionKind.CONTINUE_ABSENCE_PRESSURE
    bad_egress = assess_egress_window((egress_event(1, now=now, fam="F", kind=EgressEventKind.PROVIDER_REAL_PROBE, raw=True),), now=now + 1, budget=EgressBudget(min_decoy_per_real_probe=1))
    assert bad_egress.decision_kind is EgressDecisionKind.QUARANTINE_FAMILY_MONOCULTURE or not bad_egress.accept
    blocked = assess_bootstrap_join(peerbook=peerbook, egress=bad_egress, policy=BootstrapJoinPolicy(min_live_probes=0))
    assert blocked.decision_kind is BootstrapJoinDecisionKind.QUARANTINE_EGRESS_BUDGET


def test_livesmoke_binds_sam_script_to_contact_destination() -> None:
    now = 1_766_200_200
    l = lease(5, seq=1, now=now, fam="smoke-A")
    steps = (
        SamWireStep.create(keypair=kp(5), kind=SamStepKind.HELLO, session_id="dht", destination=l.destination, issued_at=now),
        SamWireStep.create(keypair=kp(5), kind=SamStepKind.SESSION_CREATE, session_id="dht", destination=l.destination, issued_at=now + 1),
    )
    report = assess_sam_live_smoke(lease=l, plan=SamSmokePlan(), observations=(SamSmokeObservation(SamSmokeObservationKind.HELLO_OK, now + 2), SamSmokeObservation(SamSmokeObservationKind.SESSION_OK, now + 2)), sam_steps=steps, now=now + 3)
    assert report.decision_kind is SamSmokeDecisionKind.ACCEPT_SMOKE_PROBE
    drift = (
        SamWireStep.create(keypair=kp(5), kind=SamStepKind.HELLO, session_id="dht", destination="other-dest.b32.i2p", issued_at=now),
        SamWireStep.create(keypair=kp(5), kind=SamStepKind.SESSION_CREATE, session_id="dht", destination="other-dest.b32.i2p", issued_at=now + 1),
    )
    bad = assess_sam_live_smoke(lease=l, plan=SamSmokePlan(), observations=(SamSmokeObservation(SamSmokeObservationKind.HELLO_OK, now + 2),), sam_steps=drift, now=now + 3)
    assert bad.decision_kind is SamSmokeDecisionKind.QUARANTINE_DESTINATION_DRIFT


def test_keycrisis_join_blocks_compromise_and_accepts_successor_only_with_checkpoint_pressure_clear() -> None:
    now = 1_766_200_300
    subject = kp(20)
    successor = kp(21)
    issuer = kp(30)
    scope = digest("writer-scope")
    notice = KeyCrisisNotice.create(
        issuer_keypair=issuer,
        subject_public_key=subject.public_key_bytes,
        kind=KeyCrisisKind.KEY_COMPROMISED,
        issuer_family="issuer-A",
        sequence=1,
        issued_at=now,
        ttl=600,
        scope_digest=scope,
        successor_public_key=successor.public_key_bytes,
        reason="test compromise",
    )
    memory = KeyCrisisMemory()
    verdict = memory.observe(notice, now=now + 1)
    assert verdict.accepted
    blocked_gate = gate_keyed_operation(subject_public_key=subject.public_key_bytes, memory=memory, now=now + 2)
    assert blocked_gate.decision_kind is KeyCrisisGateDecisionKind.BLOCK_KEY_COMPROMISED
    blocked = assess_key_crisis_join(gate=blocked_gate)
    assert blocked.decision_kind is KeyCrisisJoinDecisionKind.BLOCK_LIVE_KEY_CRISIS

    successor_gate = gate_keyed_operation(subject_public_key=subject.public_key_bytes, memory=memory, now=now + 2, successor_evidence_public_key=successor.public_key_bytes)
    assert successor_gate.decision_kind is KeyCrisisGateDecisionKind.ACCEPT_SUCCESSION_RECOVERY
    fact = CheckpointFact(CheckpointFactKind.TOMBSTONE, scope, digest("old-key-compromise"), 1, "cf-A", "pf-A", now, now + 600)
    checkpoint = StateCheckpoint.create(keypair=kp(40), generation=1, prev_checkpoint_digest=ZERO_DIGEST, journal_tip_digest=digest("journal"), facts=(fact,), issued_at=now)
    checkpoint_assessment = assess_checkpoint(checkpoint, now=now + 1)
    joined = assess_key_crisis_join(gate=successor_gate, checkpoint=checkpoint_assessment)
    assert joined.decision_kind is KeyCrisisJoinDecisionKind.ACCEPT_SUCCESSOR_OPERATION

    next_checkpoint = StateCheckpoint.create(keypair=kp(40), generation=2, prev_checkpoint_digest=checkpoint.checkpoint_digest, journal_tip_digest=digest("journal2"), facts=(), issued_at=now + 2)
    dropped = assess_checkpoint(next_checkpoint, previous=checkpoint, now=now + 3)
    assert dropped.decision.kind is CheckpointDecisionKind.QUARANTINE_HARD_FACT_DROP
    held = assess_key_crisis_join(gate=successor_gate, checkpoint=dropped)
    assert held.decision_kind is KeyCrisisJoinDecisionKind.QUARANTINE_CHECKPOINT_MEMORY


def test_delta_repair_join_requests_tombstone_first_then_accepts_in_sync() -> None:
    now = 1_766_200_400
    local = build_delta_sketch((DeltaSketchItem(digest("k1"), digest("v1"), DeltaSketchKind.PROVIDER, sequence=1),), bucket_count=4)
    remote = build_delta_sketch((DeltaSketchItem(digest("k1"), digest("v1"), DeltaSketchKind.PROVIDER, sequence=1), DeltaSketchItem(digest("k2"), digest("tomb"), DeltaSketchKind.TOMBSTONE, sequence=2, tombstone=True)), bucket_count=4)
    signed_remote = (
        SignedDeltaSketch.create(keypair=kp(50), source_node_id=ident(50).node_id, source_family="DF-A", sketch=remote, sequence=1, issued_at=now),
        SignedDeltaSketch.create(keypair=kp(51), source_node_id=ident(51).node_id, source_family="DF-B", sketch=remote, sequence=1, issued_at=now),
    )
    report = assess_delta_sketches(local, signed_remote, now=now + 1, policy=DeltaSketchPolicy(min_source_families=2, tombstone_first=True))
    assert report.decision_kind is DeltaSketchDecisionKind.REQUEST_TOMBSTONE_FIRST
    joined = assess_delta_repair_join(sketch=report)
    assert joined.decision_kind is DeltaRepairJoinDecisionKind.CONTINUE_TOMBSTONE_FIRST
    in_sync = assess_delta_sketches(remote, signed_remote, now=now + 1, policy=DeltaSketchPolicy(min_source_families=2))
    accepted = assess_delta_repair_join(sketch=in_sync)
    assert accepted.decision_kind is DeltaRepairJoinDecisionKind.ACCEPT_IN_SYNC
    assert accepted.accept
