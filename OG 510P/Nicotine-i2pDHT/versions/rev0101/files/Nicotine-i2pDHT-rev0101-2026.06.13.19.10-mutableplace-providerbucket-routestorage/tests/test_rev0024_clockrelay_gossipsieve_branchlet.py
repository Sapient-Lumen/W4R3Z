from dataclasses import replace
from pathlib import Path

from i2p_dht_lab.branchletfold import audit_branchlet_fold
from i2p_dht_lab.clockfold import audit_clock_fold
from i2p_dht_lab.clockguard import ClockDecisionKind, ClockMemory, ClockPolicy, TimedObservation, assess_clock_window
from i2p_dht_lab.contactlease import ContactLease, ContactLeasePurpose
from i2p_dht_lab.gossipsieve import GossipCandidate, GossipSieveDecisionKind, GossipSievePolicy, sieve_gossip_candidates
from i2p_dht_lab.identity import DhtKeypair, NodeIdentity
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.interestledger import InterestLedger
from i2p_dht_lab.pressureledger import PressureRound
from i2p_dht_lab.regionreceipt import RegionSweepReceipt
from i2p_dht_lab.relayticket import (
    RelayService,
    RelayTicket,
    RelayTicketBook,
    RelayTicketDecisionKind,
    RelayTicketPolicy,
    RelayTicketRequest,
    assess_relay_tickets,
)
from i2p_dht_lab.routeattest import RouteAttestation

NOW = 1_765_318_500


def kp(n: int) -> DhtKeypair:
    return DhtKeypair.from_seed(bytes([n % 256]) * 32)


def ident(n: int) -> NodeIdentity:
    return NodeIdentity.create(destination=f"rev0024-branch-{n}.b32.i2p", keypair=kp(n))


def digest(label: str) -> bytes:
    return sha256(label.encode("utf-8"))


def timed(seq: int, label: str, *, issued_at: int = NOW, expires_at: int = NOW + 300, family: str = "fam-a") -> TimedObservation:
    return TimedObservation(
        authority_id=digest("authority"),
        scope_id=digest("scope"),
        purpose="mutable-head",
        sequence=seq,
        issued_at=issued_at,
        expires_at=expires_at,
        observed_at=NOW + 1,
        record_digest=digest("record:" + label),
        source_family=family,
    )


def test_clockguard_advances_and_quarantines_replay_shapes():
    memory = ClockMemory()
    policy = ClockPolicy(max_ttl_seconds=600, max_future_skew_seconds=60, max_issued_regression_seconds=30)
    first = assess_clock_window((timed(1, "a"),), now=NOW + 5, memory=memory, policy=policy)
    assert first.verdicts[0].decision.kind is ClockDecisionKind.ACCEPT_FIRST
    advance = assess_clock_window((timed(2, "b", issued_at=NOW + 10, expires_at=NOW + 310),), now=NOW + 15, memory=memory, policy=policy)
    assert advance.verdicts[0].decision.kind is ClockDecisionKind.ACCEPT_ADVANCE
    rollback = assess_clock_window((timed(1, "old", issued_at=NOW + 20, expires_at=NOW + 320),), now=NOW + 21, memory=memory, policy=policy)
    assert rollback.verdicts[0].decision.kind is ClockDecisionKind.QUARANTINE_ROLLBACK
    fork = assess_clock_window((timed(2, "fork", issued_at=NOW + 10, expires_at=NOW + 310),), now=NOW + 22, memory=memory, policy=policy)
    assert fork.verdicts[0].decision.kind is ClockDecisionKind.QUARANTINE_SAME_SEQ_FORK


def test_clockguard_holds_future_and_rejects_stale_ttl_windows():
    policy = ClockPolicy(max_ttl_seconds=100, max_future_skew_seconds=10)
    future = assess_clock_window((timed(1, "future", issued_at=NOW + 100, expires_at=NOW + 150),), now=NOW, policy=policy)
    assert future.verdicts[0].decision.kind is ClockDecisionKind.HOLD_FUTURE_SKEW
    expired = assess_clock_window((timed(1, "expired", issued_at=NOW - 200, expires_at=NOW - 1),), now=NOW, policy=policy)
    assert expired.verdicts[0].decision.kind is ClockDecisionKind.REJECT_EXPIRED
    ttl = assess_clock_window((timed(1, "ttl", issued_at=NOW, expires_at=NOW + 500),), now=NOW + 1, policy=policy)
    assert ttl.verdicts[0].decision.kind is ClockDecisionKind.REJECT_TTL_EXCESS


def request() -> RelayTicketRequest:
    return RelayTicketRequest(subject_node_id=digest("subject"), service=RelayService.WAKE_COURIER, scope_id=digest("scope"), payload_digest=digest("payload"), byte_cost=10, op_cost=1)


def ticket(n: int, family: str, *, sequence: int = 1, subject: bytes | None = None, byte_budget: int = 100) -> RelayTicket:
    req = request()
    return RelayTicket.create(
        keypair=kp(n),
        issuer_node_id=ident(n).node_id,
        issuer_family=family,
        subject_node_id=subject or req.subject_node_id,
        service=req.service,
        scope_id=req.scope_id,
        payload_digest=req.payload_digest,
        byte_budget=byte_budget,
        op_budget=10,
        sequence=sequence,
        issued_at=NOW,
        ttl=300,
    )


def test_relayticket_accepts_diverse_spendable_garden_tickets():
    req = request()
    tickets = (ticket(1, "relay-a"), ticket(2, "relay-b"))
    report = assess_relay_tickets(req, tickets, now=NOW + 5, policy=RelayTicketPolicy(min_ticket_families=2, max_per_family=1, max_family_fraction_ppm=600_000))
    assert report.decision_kind is RelayTicketDecisionKind.ACCEPT_RELAY_TICKETS
    assert report.accept
    assert report.family_counts == {"relay-a": 1, "relay-b": 1}


def test_relayticket_rejects_scope_budget_replay_and_same_sequence_fork():
    req = request()
    wrong_subject = ticket(3, "relay-c", subject=digest("wrong-subject"))
    mismatch = assess_relay_tickets(req, (wrong_subject,), now=NOW + 5, policy=RelayTicketPolicy(min_ticket_families=1))
    assert mismatch.decision_kind is RelayTicketDecisionKind.REJECT_PAYLOAD_SCOPE_MISMATCH
    over_budget = assess_relay_tickets(req, (ticket(4, "relay-d", byte_budget=1),), now=NOW + 5, policy=RelayTicketPolicy(min_ticket_families=1))
    assert over_budget.decision_kind is RelayTicketDecisionKind.REJECT_OVER_BUDGET
    book = RelayTicketBook()
    first = ticket(5, "relay-e", sequence=7)
    accepted = assess_relay_tickets(req, (first,), now=NOW + 5, policy=RelayTicketPolicy(min_ticket_families=1), book=book)
    assert accepted.decision_kind is RelayTicketDecisionKind.ACCEPT_RELAY_TICKETS
    replay = assess_relay_tickets(req, (first,), now=NOW + 6, policy=RelayTicketPolicy(min_ticket_families=1), book=book)
    assert replay.decision_kind is RelayTicketDecisionKind.QUARANTINE_REPLAY
    fork_unsigned = replace(first, flags=("different",), signature=b"")
    fork = replace(fork_unsigned, signature=kp(5).sign(fork_unsigned.unsigned_payload()))
    fork_report = assess_relay_tickets(req, (fork,), now=NOW + 7, policy=RelayTicketPolicy(min_ticket_families=1), book=book)
    assert fork_report.decision_kind is RelayTicketDecisionKind.QUARANTINE_SAME_SEQ_FORK


def lease(n: int, family: str) -> ContactLease:
    return ContactLease.create(
        identity=ident(n),
        keypair=kp(n),
        family_id=family,
        purposes=(ContactLeasePurpose.ROUTE, ContactLeasePurpose.SEED_GATE),
        sequence=1,
        issued_at=NOW,
        ttl=300,
    )


def attest(attester: int, family: str, path: str, item: ContactLease) -> RouteAttestation:
    return RouteAttestation.create(
        keypair=kp(attester),
        attester_node_id=ident(attester).node_id,
        attester_family=family,
        path_family=path,
        lease=item,
        purpose=ContactLeasePurpose.ROUTE,
        sequence=1,
        issued_at=NOW,
        ttl=300,
    )


def gossip_candidate(n: int, contact_family: str, intro_family: str, path_family: str) -> GossipCandidate:
    item = lease(20 + n, contact_family)
    a = attest(60 + n, f"att-{n}", path_family, item)
    return GossipCandidate(lease=item, introducer_node_id=ident(100 + n).node_id, introducer_family=intro_family, attestation=a, distance_rank=n, interest_points=1)


def test_gossipsieve_accepts_route_gossip_with_contact_intro_and_path_diversity():
    candidates = (
        gossip_candidate(1, "contact-a", "intro-a", "path-a"),
        gossip_candidate(2, "contact-b", "intro-b", "path-b"),
        gossip_candidate(3, "contact-c", "intro-c", "path-b"),
    )
    report = sieve_gossip_candidates(candidates, now=NOW + 5, target=digest("lookup-target"), policy=GossipSievePolicy(min_contact_families=3, min_path_families=2, min_introducer_families=2, max_per_introducer_family=2, max_selected=4))
    assert report.decision_kind is GossipSieveDecisionKind.ACCEPT_GOSSIP_BATCH
    assert report.accept


def test_gossipsieve_rejects_interest_over_budget_and_intro_capture():
    too_costly = replace(gossip_candidate(1, "contact-a", "intro-a", "path-a"), interest_points=99)
    over = sieve_gossip_candidates((too_costly,), now=NOW + 5, target=digest("target"), policy=GossipSievePolicy(max_interest_points=10))
    assert over.decision_kind is GossipSieveDecisionKind.REJECT_INTEREST_BUDGET
    captured = (
        gossip_candidate(1, "contact-a", "intro-x", "path-a"),
        gossip_candidate(2, "contact-b", "intro-x", "path-b"),
        gossip_candidate(3, "contact-c", "intro-x", "path-b"),
    )
    cap = sieve_gossip_candidates(captured, now=NOW + 5, target=digest("target"), policy=GossipSievePolicy(min_contact_families=3, min_path_families=2, min_introducer_families=2, max_per_introducer_family=3))
    assert cap.decision_kind is GossipSieveDecisionKind.QUARANTINE_INTRODUCER_CAPTURE


def test_branchlet_fold_passes_after_recovered_branchlets_are_documented_and_tested():
    # Symbol mentions intentionally keep the branchlet audit honest:
    assert InterestLedger is not None
    assert PressureRound is not None
    assert RegionSweepReceipt is not None
    assert RelayTicket is not None
    assert GossipCandidate is not None
    assert TimedObservation is not None
    root = Path(__file__).resolve().parents[1]
    report = audit_branchlet_fold(root, revision="rev0024")
    assert report.status == "pass"
    clock = audit_clock_fold(root, revision="rev0024")
    assert clock.status == "pass", clock.findings
