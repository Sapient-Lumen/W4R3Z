from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from i2p_dht_lab.contactlease import ContactLease, ContactLeasePurpose
from i2p_dht_lab.identity import DhtKeypair, NodeIdentity
from i2p_dht_lab.ids import key_id, sha256
from i2p_dht_lab.keycrisis import (
    KeyCrisisGateDecisionKind,
    KeyCrisisKind,
    KeyCrisisMemory,
    KeyCrisisNotice,
    KeyCrisisVerdictKind,
    gate_keyed_operation,
)
from i2p_dht_lab.keycrisisfold import audit_keycrisis_fold
from i2p_dht_lab.negspace import AbsenceKind, AbsenceObservation, NegspaceDecisionKind, NegspacePolicy, assess_negative_space
from i2p_dht_lab.peerbook import PeerBookDecisionKind, PeerBookPolicy, PeerLeaseObservation, build_peerbook_view
from i2p_dht_lab.peerdelta import PeerDeltaDecisionKind, PeerDeltaItem, PeerDeltaPolicy, PeerDeltaSketch, assess_peer_delta


def seed(label: str) -> bytes:
    return sha256(("rev0030-seed:" + label).encode("utf-8"))


def kp(label: str) -> DhtKeypair:
    return DhtKeypair.from_seed(seed(label))


def digest(label: str) -> bytes:
    return key_id("rev0030", label)


def lease(label: str, *, family: str, seq: int, now: int, purposes=(ContactLeasePurpose.ROUTE, ContactLeasePurpose.SEED_GATE)) -> ContactLease:
    keypair = kp("lease-" + label)
    identity = NodeIdentity.create(destination=f"{label}.b32.i2p", keypair=keypair)
    return ContactLease.create(identity=identity, keypair=keypair, family_id=family, purposes=purposes, sequence=seq, issued_at=now, ttl=900)


def observation(label: str, *, family: str, channel_family: str, channel_id: str, now: int, purposes=(ContactLeasePurpose.ROUTE, ContactLeasePurpose.SEED_GATE)) -> PeerLeaseObservation:
    return PeerLeaseObservation(lease(label, family=family, seq=1, now=now, purposes=purposes), channel_id=channel_id, channel_family=channel_family, observed_at=now + 1)


def absence(label: str, *, kind: AbsenceKind, target: bytes, request: bytes, fam: str, path: str, seq: int, now: int) -> AbsenceObservation:
    return AbsenceObservation.create(keypair=kp("absence-" + label), kind=kind, target_digest=target, request_digest=request, responder_family=fam, path_family=path, sequence=seq, issued_at=now, ttl=120)


def crisis(label: str, *, subject: bytes, kind: KeyCrisisKind, issuer_family: str, seq: int, now: int, successor: bytes = b"") -> KeyCrisisNotice:
    return KeyCrisisNotice.create(issuer_keypair=kp("crisis-issuer-" + label), subject_public_key=subject, kind=kind, issuer_family=issuer_family, sequence=seq, issued_at=now, ttl=3600, scope_digest=digest("scope-main"), successor_public_key=successor, reason=label)


def test_negspace_accepts_diverse_absence_but_not_as_truth() -> None:
    now = 1_766_300_000
    target = digest("target-no-provider")
    request = digest("request-a")
    observations = (
        absence("a", kind=AbsenceKind.NO_PROVIDER, target=target, request=request, fam="fam-A", path="path-1", seq=1, now=now),
        absence("b", kind=AbsenceKind.NO_PROVIDER, target=target, request=request, fam="fam-B", path="path-2", seq=1, now=now),
        absence("c", kind=AbsenceKind.NO_PROVIDER, target=target, request=request, fam="fam-C", path="path-3", seq=1, now=now),
    )
    report = assess_negative_space(observations, now=now + 1, target_digest=target, kind=AbsenceKind.NO_PROVIDER, request_digest=request)
    assert report.decision_kind is NegspaceDecisionKind.ACCEPT_DIVERSE_ABSENCE
    assert report.accept
    assert report.responder_families == ("fam-A", "fam-B", "fam-C")


def test_negspace_quarantines_positive_contradiction_fork_and_monoculture() -> None:
    now = 1_766_300_100
    target = digest("target-conflict")
    request = digest("request-b")
    a = absence("fork", kind=AbsenceKind.NO_MUTABLE_HEAD, target=target, request=request, fam="fam-A", path="path-1", seq=7, now=now)
    positive = assess_negative_space((a,), now=now + 1, target_digest=target, kind=AbsenceKind.NO_MUTABLE_HEAD, request_digest=request, positive_evidence_digests=(digest("positive-head"),))
    assert positive.decision_kind is NegspaceDecisionKind.QUARANTINE_POSITIVE_CONTRADICTION

    # Same responder/key, same sequence, different signed note -> fork pressure.
    fork = AbsenceObservation.create(keypair=kp("absence-fork"), kind=AbsenceKind.NO_MUTABLE_HEAD, target_digest=target, request_digest=request, responder_family="fam-A", path_family="path-2", sequence=7, issued_at=now, ttl=120, note="different")
    fork_report = assess_negative_space((a, fork, absence("b", kind=AbsenceKind.NO_MUTABLE_HEAD, target=target, request=request, fam="fam-B", path="path-3", seq=1, now=now)), now=now + 1, target_digest=target, kind=AbsenceKind.NO_MUTABLE_HEAD, request_digest=request)
    assert fork_report.decision_kind is NegspaceDecisionKind.QUARANTINE_RESPONDER_FORK

    flood = tuple(absence(f"flood-{idx}", kind=AbsenceKind.NO_ROUTE, target=target, request=request, fam="fam-Z", path=f"path-{idx}", seq=idx, now=now) for idx in range(4))
    flood_report = assess_negative_space(flood, now=now + 1, target_digest=target, kind=AbsenceKind.NO_ROUTE, request_digest=request, policy=NegspacePolicy(max_per_responder_family=3))
    assert flood_report.decision_kind is NegspaceDecisionKind.QUARANTINE_FAMILY_FLOOD


def test_peerbook_accepts_diverse_entrance_view_and_rejects_channel_capture() -> None:
    now = 1_766_301_000
    observations = (
        observation("a", family="peer-A", channel_family="chan-A", channel_id="buddy", now=now),
        observation("b", family="peer-B", channel_family="chan-B", channel_id="garden", now=now),
        observation("c", family="peer-C", channel_family="chan-C", channel_id="room", now=now),
    )
    view = build_peerbook_view(observations, now=now + 2)
    assert view.decision_kind is PeerBookDecisionKind.ACCEPT_ENTRANCE_VIEW
    assert view.accept
    assert view.peer_families == ("peer-A", "peer-B", "peer-C")

    captured = tuple(observation(f"cap-{idx}", family=f"peer-{idx}", channel_family="chan-Z", channel_id=f"seed-{idx}", now=now) for idx in range(5))
    captured_view = build_peerbook_view(captured, now=now + 2, policy=PeerBookPolicy(min_channel_families=2, max_per_channel_family=4))
    assert captured_view.decision_kind is PeerBookDecisionKind.QUARANTINE_CHANNEL_MONOCULTURE


def test_peerbook_low_purpose_and_contact_fork_pressure() -> None:
    now = 1_766_301_100
    low = (
        observation("only-route-a", family="peer-A", channel_family="chan-A", channel_id="one", now=now, purposes=(ContactLeasePurpose.ROUTE,)),
        observation("only-route-b", family="peer-B", channel_family="chan-B", channel_id="two", now=now, purposes=(ContactLeasePurpose.ROUTE,)),
    )
    low_view = build_peerbook_view(low, now=now + 1)
    assert low_view.decision_kind is PeerBookDecisionKind.CONTINUE_LOW_PURPOSE_COVERAGE

    keypair = kp("lease-forked")
    identity = NodeIdentity.create(destination="forked.b32.i2p", keypair=keypair)
    first = ContactLease.create(identity=identity, keypair=keypair, family_id="peer-A", purposes=(ContactLeasePurpose.ROUTE, ContactLeasePurpose.SEED_GATE), sequence=5, issued_at=now, ttl=900, note="first")
    second = ContactLease.create(identity=identity, keypair=keypair, family_id="peer-A", purposes=(ContactLeasePurpose.ROUTE, ContactLeasePurpose.SEED_GATE), sequence=5, issued_at=now, ttl=900, note="fork")
    fork_view = build_peerbook_view((PeerLeaseObservation(first, "one", "chan-A", now), PeerLeaseObservation(second, "two", "chan-B", now)), now=now + 1)
    assert fork_view.decision_kind is PeerBookDecisionKind.QUARANTINE_FORK_PRESSURE


def test_peerdelta_requests_missing_and_detects_forks_and_monoculture() -> None:
    now = 1_766_302_000
    signer = kp("delta-signer")
    obs_a = observation("delta-a", family="peer-A", channel_family="chan-A", channel_id="a", now=now)
    obs_b = observation("delta-b", family="peer-B", channel_family="chan-B", channel_id="b", now=now)
    obs_c = observation("delta-c", family="peer-C", channel_family="chan-C", channel_id="c", now=now)
    item_a, item_b, item_c = (PeerDeltaItem.from_observation(obs) for obs in (obs_a, obs_b, obs_c))
    remote = PeerDeltaSketch.create(keypair=signer, range_id=digest("range-1"), sequence=2, items=(item_a, item_b, item_c), issued_at=now)
    report = assess_peer_delta(local_items=(item_a,), remote_sketch=remote, now=now + 1)
    assert report.decision_kind is PeerDeltaDecisionKind.REQUEST_LOCAL_MISSING
    assert report.local_missing == tuple(sorted((item_b.item_digest, item_c.item_digest)))

    prior = PeerDeltaSketch.create(keypair=signer, range_id=digest("range-1"), sequence=2, items=(item_a, item_b), issued_at=now - 10)
    fork_report = assess_peer_delta(local_items=(item_a,), remote_sketch=remote, previous_remote=prior, now=now + 1)
    assert fork_report.decision_kind is PeerDeltaDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK

    mono_items = tuple(PeerDeltaItem.from_observation(observation(f"mono-{idx}", family="peer-Z", channel_family="chan-Z", channel_id=f"m{idx}", now=now)) for idx in range(3))
    mono = PeerDeltaSketch.create(keypair=signer, range_id=digest("range-mono"), sequence=1, items=mono_items, issued_at=now)
    mono_report = assess_peer_delta(local_items=(), remote_sketch=mono, now=now + 1, policy=PeerDeltaPolicy(min_peer_families=2, min_channel_families=2, max_items_per_peer_family=4))
    assert mono_report.decision_kind is PeerDeltaDecisionKind.QUARANTINE_FAMILY_MONOCULTURE


def test_keycrisis_blocks_compromised_key_and_accepts_successor_recovery() -> None:
    now = 1_766_303_000
    subject = kp("subject").public_key_bytes
    successor = kp("successor").public_key_bytes
    memory = KeyCrisisMemory()
    notice = crisis("compromised", subject=subject, kind=KeyCrisisKind.KEY_COMPROMISED, issuer_family="fam-A", seq=1, now=now, successor=successor)
    verdict = memory.observe(notice, now=now + 1)
    assert verdict.kind is KeyCrisisVerdictKind.ACCEPT_FIRST
    blocked = gate_keyed_operation(subject_public_key=subject, memory=memory, now=now + 2)
    assert blocked.decision_kind is KeyCrisisGateDecisionKind.BLOCK_KEY_COMPROMISED
    assert blocked.blocked
    recovered = gate_keyed_operation(subject_public_key=subject, memory=memory, now=now + 2, successor_evidence_public_key=successor)
    assert recovered.decision_kind is KeyCrisisGateDecisionKind.ACCEPT_SUCCESSION_RECOVERY
    assert recovered.accept


def test_keycrisis_detects_rollback_same_seq_fork_and_destination_watch() -> None:
    now = 1_766_303_100
    subject = kp("subject-two").public_key_bytes
    memory = KeyCrisisMemory()
    first = crisis("freeze", subject=subject, kind=KeyCrisisKind.EMERGENCY_FREEZE, issuer_family="fam-A", seq=4, now=now)
    assert memory.observe(first, now=now + 1).accepted
    rollback = crisis("rollback", subject=subject, kind=KeyCrisisKind.EMERGENCY_FREEZE, issuer_family="fam-A", seq=3, now=now)
    assert memory.observe(rollback, now=now + 1).kind is KeyCrisisVerdictKind.REJECT_ROLLBACK
    fork = crisis("fork", subject=subject, kind=KeyCrisisKind.SIGNER_FORKED, issuer_family="fam-B", seq=4, now=now)
    assert memory.observe(fork, now=now + 1).kind is KeyCrisisVerdictKind.QUARANTINE_SAME_SEQUENCE_FORK
    gate = gate_keyed_operation(subject_public_key=subject, memory=memory, now=now + 2)
    assert gate.decision_kind is KeyCrisisGateDecisionKind.QUARANTINE_CRISIS_FORK

    lost_subject = kp("lost-subject").public_key_bytes
    lost_mem = KeyCrisisMemory()
    lost_mem.observe(crisis("lost", subject=lost_subject, kind=KeyCrisisKind.DESTINATION_LOST, issuer_family="fam-C", seq=1, now=now), now=now + 1)
    lost_gate = gate_keyed_operation(subject_public_key=lost_subject, memory=lost_mem, now=now + 2)
    assert lost_gate.decision_kind is KeyCrisisGateDecisionKind.WATCH_DESTINATION_LOST
    assert lost_gate.accept


def test_keycrisisfold_pins_current_revision_navigation() -> None:
    root = Path(__file__).resolve().parents[1]
    report = audit_keycrisis_fold(root, revision="rev0030", artifact_stem=root.name)
    assert report.status == "pass"
    assert report.error_count == 0
    assert report.warning_count == 0
    assert report.predecessor_status == "rev0029_foldseal:pass"
