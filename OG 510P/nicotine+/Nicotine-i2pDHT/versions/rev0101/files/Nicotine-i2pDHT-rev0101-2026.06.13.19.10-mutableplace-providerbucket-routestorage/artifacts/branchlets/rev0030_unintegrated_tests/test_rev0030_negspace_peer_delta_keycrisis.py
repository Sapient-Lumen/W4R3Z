from dataclasses import replace
from pathlib import Path

from i2p_dht_lab.absencegate import (
    AbsenceDecisionKind,
    AbsenceObservation,
    AbsenceObservationKind,
    AbsencePolicy,
    assess_absence_window,
)
from i2p_dht_lab.branchrecoverfold import audit_branch_recover_fold
from i2p_dht_lab.contactlease import ContactLease, ContactLeasePurpose
from i2p_dht_lab.deltasketch import (
    DeltaSketchDecisionKind,
    DeltaSketchItem,
    DeltaSketchKind,
    DeltaSketchPolicy,
    SignedDeltaSketch,
    assess_delta_sketches,
    build_delta_sketch,
)
from i2p_dht_lab.identity import DhtKeypair, NodeIdentity
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.keycrisis import (
    KeyCrisisDecisionKind,
    KeyCrisisPolicy,
    KeyCrisisRecord,
    RecoveryWitness,
    assess_key_crisis,
)
from i2p_dht_lab.liveprobe import (
    LiveProbeConfig,
    LiveProbeDecisionKind,
    SamContactProbe,
    assess_no_router_smoke,
    assess_sam_contact_probe,
)
from i2p_dht_lab.peerbook import PeerBookDecisionKind, PeerBookObservation, PeerBookPolicy, assess_peer_book
from i2p_dht_lab.persistlane import ZERO_DIGEST
from i2p_dht_lab.rangesetdelta import (
    RangeSetDeltaDecisionKind,
    RangeSetDeltaSketch,
    RangeSetRecord,
    compare_range_set_delta_sketches,
)
from i2p_dht_lab.samshadow import SamShadowFrame, SamShadowProfile, SamShadowTranscript, make_streaming_first_shadow


def kp(n: int) -> DhtKeypair:
    return DhtKeypair.from_seed(bytes([n % 256]) * 32)


def ident(n: int) -> NodeIdentity:
    return NodeIdentity.create(destination=f"rev0030-node-{n}.b32.i2p", keypair=kp(n))


def digest(label: str) -> bytes:
    return sha256(label.encode("utf-8"))


def lease(n: int, *, seq: int, now: int, fam: str, purposes=(ContactLeasePurpose.SEED_GATE, ContactLeasePurpose.ROUTE)) -> ContactLease:
    return ContactLease.create(identity=ident(n), keypair=kp(n), family_id=fam, purposes=purposes, sequence=seq, issued_at=now, ttl=600)


def peer_obs(n: int, *, seq: int, now: int, fam: str, intro: str, path: str, channel: str = "buddy") -> PeerBookObservation:
    return PeerBookObservation(lease(n, seq=seq, now=now, fam=fam), introducer_family=intro, path_family=path, channel=channel, observed_at=now + 1)


def absence_obs(n: int, kind: AbsenceObservationKind, *, target: bytes, fam: str, path: str, now: int, latency: int = 100, evidence: bytes | None = None) -> AbsenceObservation:
    return AbsenceObservation.create(keypair=kp(n), target_digest=target, kind=kind, source_family=fam, path_family=path, issued_at=now, ttl=600, latency_ms=latency, evidence_digest=evidence)


def item(label: str, *, kind: DeltaSketchKind = DeltaSketchKind.PROVIDER, seq: int = 1, tombstone: bool = False) -> DeltaSketchItem:
    return DeltaSketchItem(key_digest=digest(f"key-{label}"), value_digest=digest(f"value-{label}-{seq}"), kind=kind, sequence=seq, tombstone=tombstone)


def signed(sketch, n: int, *, fam: str, seq: int, now: int) -> SignedDeltaSketch:
    return SignedDeltaSketch.create(keypair=kp(n), source_node_id=ident(n).node_id, source_family=fam, sketch=sketch, sequence=seq, issued_at=now, ttl=600)


def rrecord(label: str, *, seq: int = 1, tombstone: bool = False) -> RangeSetRecord:
    return RangeSetRecord(key=digest("range-key-" + label), value_digest=digest(f"range-val-{label}-{seq}"), sequence=seq, tombstone=tombstone)


def rsketch(n: int, records, *, fam: str, seq: int, now: int) -> RangeSetDeltaSketch:
    return RangeSetDeltaSketch.create(keypair=kp(n), namespace="rev0030-provider-ledger", source_family=fam, sequence=seq, issued_at=now, records=tuple(records), range_bits=4)


def test_absence_gate_only_turns_empty_answers_into_durable_absence_with_tombstone_support() -> None:
    now = 1_766_300_000
    target = digest("missing-provider")
    tomb = digest("signed-tombstone")
    observations = (
        absence_obs(1, AbsenceObservationKind.EMPTY_PROVIDER, target=target, fam="fam-A", path="path-A", now=now, latency=300),
        absence_obs(2, AbsenceObservationKind.EMPTY_PROVIDER, target=target, fam="fam-B", path="path-B", now=now, latency=310),
        absence_obs(3, AbsenceObservationKind.EMPTY_PROVIDER, target=target, fam="fam-C", path="path-C", now=now, latency=320),
        absence_obs(4, AbsenceObservationKind.TOMBSTONE_SEEN, target=target, fam="fam-D", path="path-D", now=now, evidence=tomb),
        absence_obs(5, AbsenceObservationKind.TOMBSTONE_SEEN, target=target, fam="fam-E", path="path-E", now=now, evidence=tomb),
    )
    report = assess_absence_window(target, observations, now=now + 5)
    assert report.decision_kind is AbsenceDecisionKind.ACCEPT_DURABLE_TOMBSTONE_ABSENCE
    assert report.accept
    assert report.negative_cache_ttl == 0


def test_absence_gate_quarantines_fast_empty_capture_and_positive_conflict() -> None:
    now = 1_766_300_100
    target = digest("captured-empty")
    captured = tuple(absence_obs(i, AbsenceObservationKind.EMPTY_MUTABLE, target=target, fam="fam-capture", path=f"path-{i}", now=now, latency=20 + i) for i in range(1, 5))
    report = assess_absence_window(target, captured, now=now + 1, policy=AbsencePolicy(min_empty_families=2, min_empty_paths=2, max_fast_family_share=0.66))
    assert report.decision_kind is AbsenceDecisionKind.QUARANTINE_FAST_EMPTY_CAPTURE
    assert report.quarantined

    mixed = captured[:2] + (absence_obs(9, AbsenceObservationKind.POSITIVE_MUTABLE_HEAD, target=target, fam="fam-good", path="path-good", now=now, latency=90, evidence=digest("head")),)
    conflict = assess_absence_window(target, mixed, now=now + 2)
    assert conflict.decision_kind is AbsenceDecisionKind.QUARANTINE_POSITIVE_CONFLICT
    assert conflict.positive_count == 1


def test_keycrisis_splits_normal_succession_from_compromise_recovery_rotation() -> None:
    now = 1_766_300_200
    scope = digest("writer-scope")
    succession = KeyCrisisRecord.create_succession(old_keypair=kp(10), new_keypair=kp(11), scope_id=scope, sequence=1, issued_at=now)
    accepted = assess_key_crisis(succession, now=now + 1)
    assert accepted.decision_kind is KeyCrisisDecisionKind.ACCEPT_SUCCESSION
    assert accepted.accepted_new_public_key == kp(11).public_key_bytes

    compromised = assess_key_crisis(succession, now=now + 1, old_key_compromised=True)
    assert compromised.decision_kind is KeyCrisisDecisionKind.QUARANTINE_COMPROMISED_OLD_KEY

    recovery_keys = (kp(21).public_key_bytes, kp(22).public_key_bytes, kp(23).public_key_bytes)
    policy = KeyCrisisPolicy(recovery_public_keys=recovery_keys, recovery_threshold=2, min_recovery_families=2)
    rotation = KeyCrisisRecord.create_recovery_rotation(old_public_key=kp(10).public_key_bytes, new_keypair=kp(24), scope_id=scope, sequence=2, prev_event_digest=succession.record_digest, issued_at=now + 10)
    witnesses = (
        RecoveryWitness.create(keypair=kp(21), crisis_digest=rotation.record_digest, source_family="fam-R", path_family="path-R", issued_at=now + 11),
        RecoveryWitness.create(keypair=kp(22), crisis_digest=rotation.record_digest, source_family="fam-S", path_family="path-S", issued_at=now + 11),
    )
    recovery = assess_key_crisis(rotation, witnesses, now=now + 12, previous_sequence=1, previous_event_digest=succession.record_digest, old_key_compromised=True, policy=policy)
    assert recovery.decision_kind is KeyCrisisDecisionKind.ACCEPT_RECOVERY_ROTATION
    assert recovery.accept


def test_keycrisis_detects_sequence_fork_rollback_and_prev_mismatch() -> None:
    now = 1_766_300_300
    scope = digest("writer-lineage")
    first = KeyCrisisRecord.create_succession(old_keypair=kp(30), new_keypair=kp(31), scope_id=scope, sequence=1, issued_at=now)
    fork = KeyCrisisRecord.create_succession(old_keypair=kp(30), new_keypair=kp(32), scope_id=scope, sequence=1, issued_at=now)
    assert assess_key_crisis(fork, now=now + 1, previous_sequence=1, previous_same_sequence_digest=first.record_digest).decision_kind is KeyCrisisDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK
    assert assess_key_crisis(first, now=now + 1, previous_sequence=2, previous_event_digest=digest("later")).decision_kind is KeyCrisisDecisionKind.QUARANTINE_ROLLBACK
    bad_prev = KeyCrisisRecord.create_succession(old_keypair=kp(31), new_keypair=kp(33), scope_id=scope, sequence=2, prev_event_digest=ZERO_DIGEST, issued_at=now + 2)
    assert assess_key_crisis(bad_prev, now=now + 3, previous_sequence=1, previous_event_digest=first.record_digest).decision_kind is KeyCrisisDecisionKind.QUARANTINE_PREV_MISMATCH


def test_peerbook_accepts_diverse_fresh_entrances_and_rejects_introducer_capture() -> None:
    now = 1_766_300_400
    observations = (
        peer_obs(1, seq=1, now=now, fam="contact-A", intro="intro-A", path="path-A"),
        peer_obs(2, seq=1, now=now, fam="contact-B", intro="intro-B", path="path-B"),
        peer_obs(3, seq=1, now=now, fam="contact-C", intro="intro-C", path="path-C"),
    )
    report = assess_peer_book(observations, target=digest("route-target"), now=now + 2)
    assert report.decision_kind is PeerBookDecisionKind.ACCEPT_DIVERSE_BOOK
    assert report.accept
    assert report.selected_count == 3

    captured = tuple(peer_obs(10 + idx, seq=1, now=now, fam=f"contact-{idx}", intro="captured-intro", path=f"path-{idx}") for idx in range(4))
    capture_report = assess_peer_book(captured, target=digest("route-target"), now=now + 2, policy=PeerBookPolicy(min_contacts=3, min_contact_families=2, min_introducer_families=2, max_per_introducer_family=99))
    assert capture_report.decision_kind is PeerBookDecisionKind.QUARANTINE_INTRODUCER_CAPTURE


def test_peerbook_liveprobe_binds_sam_shadow_to_contact_destination() -> None:
    now = 1_766_300_500
    contact = lease(40, seq=1, now=now, fam="contact-A")
    profile = SamShadowProfile(session_id="i2p-dht-lab", destination_name=contact.destination)
    transcript = make_streaming_first_shadow(profile, "remote.b32.i2p")
    report = assess_sam_contact_probe(SamContactProbe(contact, transcript), now=now + 1, profile=profile)
    assert report.decision_kind is LiveProbeDecisionKind.ACCEPT_STREAMING_FIRST
    assert report.ok

    drift = assess_sam_contact_probe(SamContactProbe(contact, transcript), now=now + 1, profile=SamShadowProfile(session_id="i2p-dht-lab", destination_name="other-destination.keys"))
    assert drift.decision_kind is LiveProbeDecisionKind.QUARANTINE_DESTINATION_DRIFT
    assert drift.quarantined


def test_liveprobe_skips_cleanly_when_sam_router_is_absent() -> None:
    class RefusingSocket:
        def settimeout(self, seconds: float) -> None: pass
        def connect(self, address: tuple[str, int]) -> None: raise ConnectionRefusedError("refused")
        def sendall(self, data: bytes) -> None: pass
        def recv(self, size: int) -> bytes: return b""
        def close(self) -> None: pass

    report = assess_no_router_smoke(config=LiveProbeConfig(timeout=0.01), socket_factory=RefusingSocket)
    assert report.decision_kind is LiveProbeDecisionKind.SKIP_NO_ROUTER
    assert report.ok
    assert report.clean_skip


def test_liveprobe_rejects_invalid_shadow_ordering() -> None:
    now = 1_766_300_550
    contact = lease(41, seq=1, now=now, fam="contact-A")
    profile = SamShadowProfile(session_id="i2p-dht-lab", destination_name=contact.destination)
    bad = SamShadowTranscript((SamShadowFrame.command("STREAM CONNECT", ID="i2p-dht-lab", DESTINATION="remote"),))
    report = assess_sam_contact_probe(SamContactProbe(contact, bad), now=now + 1, profile=profile)
    assert report.decision_kind is LiveProbeDecisionKind.QUARANTINE_TRANSCRIPT_INVALID


def test_deltasketch_requests_tombstone_first_exact_delta_and_quarantines_forks() -> None:
    now = 1_766_300_600
    local = build_delta_sketch((item("a"), item("b")), bucket_count=8)
    remote_tomb = build_delta_sketch((item("a"), item("b"), item("gone", kind=DeltaSketchKind.TOMBSTONE, tombstone=True, seq=9)), bucket_count=8)
    tomb_report = assess_delta_sketches(local, (signed(remote_tomb, 22, fam="fam-A", seq=3, now=now), signed(remote_tomb, 23, fam="fam-B", seq=3, now=now)), now=now + 1)
    assert tomb_report.decision_kind is DeltaSketchDecisionKind.REQUEST_TOMBSTONE_FIRST

    remote_small = build_delta_sketch((item("a"), item("b"), item("c")), bucket_count=8)
    exact = assess_delta_sketches(local, (signed(remote_small, 24, fam="fam-A", seq=4, now=now), signed(remote_small, 25, fam="fam-B", seq=4, now=now)), now=now + 1, policy=DeltaSketchPolicy(tombstone_first=False))
    assert exact.decision_kind is DeltaSketchDecisionKind.REQUEST_EXACT_DELTA

    remote_one = build_delta_sketch((item("a"), item("b"), item("c")), bucket_count=8)
    remote_two = build_delta_sketch((item("a"), item("b"), item("d")), bucket_count=8)
    fork = assess_delta_sketches(local, (signed(remote_one, 30, fam="fam-A", seq=7, now=now), signed(remote_two, 31, fam="fam-B", seq=7, now=now)), now=now + 1)
    assert fork.decision_kind is DeltaSketchDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK


def test_rangesetdelta_requests_tombstone_first_and_detects_replay_or_family_monoculture() -> None:
    now = 1_766_300_700
    local = rsketch(50, (rrecord("a"), rrecord("b")), fam="local", seq=4, now=now)
    remote = rsketch(51, (rrecord("a"), rrecord("b"), rrecord("gone", seq=9, tombstone=True)), fam="fam-A", seq=5, now=now)
    remote_b = rsketch(52, (rrecord("a"), rrecord("b"), rrecord("gone", seq=9, tombstone=True)), fam="fam-B", seq=5, now=now)
    report = compare_range_set_delta_sketches(local, (remote, remote_b), now=now + 1)
    assert report.decision_kind is RangeSetDeltaDecisionKind.REQUEST_TOMBSTONE_FIRST_REPAIR
    assert report.repair_ranges[0].tombstone_first

    mono = compare_range_set_delta_sketches(local, (remote,), now=now + 1)
    assert mono.decision_kind is RangeSetDeltaDecisionKind.QUARANTINE_ONE_FAMILY_SKETCHES

    old = rsketch(53, (rrecord("a"), rrecord("c")), fam="fam-A", seq=3, now=now)
    old_b = rsketch(54, (rrecord("a"), rrecord("c")), fam="fam-B", seq=3, now=now)
    replay = compare_range_set_delta_sketches(local, (old, old_b), now=now + 1)
    assert replay.decision_kind is RangeSetDeltaDecisionKind.QUARANTINE_ROLLBACK


def test_branchrecoverfold_pins_rev0030_navigation_and_rev0029_predecessor() -> None:
    root = Path(__file__).resolve().parents[1]
    report = audit_branch_recover_fold(root, revision="rev0030", artifact_stem=root.name)
    assert report.status == "pass"
    assert report.error_count == 0
    assert report.predecessor_status == "rev0029_foldseal:pass"
