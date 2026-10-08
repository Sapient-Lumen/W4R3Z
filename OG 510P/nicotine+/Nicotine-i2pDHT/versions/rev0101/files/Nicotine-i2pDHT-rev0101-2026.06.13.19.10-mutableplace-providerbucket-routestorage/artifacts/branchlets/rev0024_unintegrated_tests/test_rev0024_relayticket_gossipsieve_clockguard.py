from dataclasses import replace
from pathlib import Path

from i2p_dht_lab.clockfold import audit_clock_fold
from i2p_dht_lab.clockguard import (
    ClockDecisionKind,
    ClockMemory,
    ClockPolicy,
    TimedObservation,
    assess_clock_window,
)
from i2p_dht_lab.contactlease import ContactLease, ContactLeasePurpose
from i2p_dht_lab.gossipsieve import (
    GossipCandidate,
    GossipSieveDecisionKind,
    GossipSievePolicy,
    sieve_gossip_candidates,
)
from i2p_dht_lab.identity import DhtKeypair, NodeIdentity
from i2p_dht_lab.ids import sha256
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


def h(label: str) -> bytes:
    return sha256(label.encode("utf-8"))


def keypair(label: str) -> DhtKeypair:
    return DhtKeypair.from_seed(h("seed:" + label))


def identity(label: str) -> tuple[DhtKeypair, NodeIdentity]:
    kp = keypair(label)
    return kp, NodeIdentity.create(destination=f"{label}.b32.i2p", keypair=kp)


def observation(label: str, *, sequence: int = 1, issued_at: int = 100, expires_at: int = 300, digest_label: str | None = None) -> TimedObservation:
    return TimedObservation(
        authority_id=h("authority:" + label),
        scope_id=h("scope:" + label),
        purpose="mutable_head",
        sequence=sequence,
        issued_at=issued_at,
        expires_at=expires_at,
        observed_at=150,
        record_digest=h("record:" + (digest_label or label)),
        source_family="fam-a",
    )


def test_clockguard_accepts_advance_and_quarantines_rollback_fork_and_time_regression():
    memory = ClockMemory()
    first = observation("clock", sequence=1, issued_at=100, expires_at=300, digest_label="v1")
    second = observation("clock", sequence=2, issued_at=130, expires_at=330, digest_label="v2")
    old = observation("clock", sequence=1, issued_at=140, expires_at=340, digest_label="v1")
    fork = observation("clock", sequence=2, issued_at=150, expires_at=350, digest_label="fork")
    regress = observation("clock", sequence=3, issued_at=10, expires_at=360, digest_label="v3")

    first_report = assess_clock_window([first], now=150, memory=memory)
    second_report = assess_clock_window([second], now=151, memory=memory)
    old_report = assess_clock_window([old], now=152, memory=memory)
    fork_report = assess_clock_window([fork], now=153, memory=memory)
    regress_report = assess_clock_window([regress], now=154, memory=memory, policy=ClockPolicy(max_issued_regression_seconds=30))

    assert first_report.verdicts[0].decision.kind is ClockDecisionKind.ACCEPT_FIRST
    assert second_report.verdicts[0].decision.kind is ClockDecisionKind.ACCEPT_ADVANCE
    assert old_report.verdicts[0].decision.kind is ClockDecisionKind.QUARANTINE_ROLLBACK
    assert fork_report.verdicts[0].decision.kind is ClockDecisionKind.QUARANTINE_SAME_SEQ_FORK
    assert regress_report.verdicts[0].decision.kind is ClockDecisionKind.QUARANTINE_TIME_REGRESSION


def test_clockguard_holds_future_and_rejects_expired_or_ttl_excess():
    future = observation("future", sequence=1, issued_at=500, expires_at=700)
    expired = observation("expired", sequence=1, issued_at=100, expires_at=120)
    long_ttl = observation("long", sequence=1, issued_at=100, expires_at=10_000)
    report = assess_clock_window([future, expired, long_ttl], now=150, policy=ClockPolicy(max_ttl_seconds=500, max_future_skew_seconds=60))
    assert [item.decision.kind for item in report.verdicts] == [
        ClockDecisionKind.HOLD_FUTURE_SKEW,
        ClockDecisionKind.REJECT_EXPIRED,
        ClockDecisionKind.REJECT_TTL_EXCESS,
    ]
    assert report.held_count == 1


def ticket(label: str, *, family: str = "fam-a", sequence: int = 1, payload: bytes | None = None, byte_budget: int = 1000, subject: bytes | None = None) -> RelayTicket:
    kp, ident = identity("relay:" + label)
    return RelayTicket.create(
        keypair=kp,
        issuer_node_id=ident.node_id,
        issuer_family=family,
        subject_node_id=subject or h("subject"),
        service=RelayService.WAKE_COURIER,
        scope_id=h("relay-scope"),
        payload_digest=payload or h("payload"),
        byte_budget=byte_budget,
        op_budget=2,
        sequence=sequence,
        issued_at=100,
        ttl=500,
        flags=("wake",),
    )


def relay_request(*, payload: bytes | None = None, byte_cost: int = 100, subject: bytes | None = None) -> RelayTicketRequest:
    return RelayTicketRequest(
        subject_node_id=subject or h("subject"),
        service=RelayService.WAKE_COURIER,
        scope_id=h("relay-scope"),
        payload_digest=payload or h("payload"),
        byte_cost=byte_cost,
        op_cost=1,
    )


def test_relayticket_accepts_scope_bound_family_diverse_tickets():
    request = relay_request()
    tickets = (ticket("a", family="fam-a"), ticket("b", family="fam-b"), ticket("c", family="fam-c"))
    report = assess_relay_tickets(request, tickets, now=120, policy=RelayTicketPolicy(min_ticket_families=2, max_per_family=1))
    assert report.decision_kind is RelayTicketDecisionKind.ACCEPT_RELAY_TICKETS
    assert report.accept
    assert len(report.selected) == 3
    assert set(report.family_counts) == {"fam-a", "fam-b", "fam-c"}


def test_relayticket_rejects_payload_mismatch_over_budget_and_replay():
    request = relay_request()
    mismatch = ticket("mismatch", family="fam-a", payload=h("other"))
    over = ticket("over", family="fam-b", byte_budget=10)
    book = RelayTicketBook()
    first_report = assess_relay_tickets(request, [ticket("replay", family="fam-a")], now=120, policy=RelayTicketPolicy(min_ticket_families=1), book=book)
    replay_report = assess_relay_tickets(request, [first_report.selected[0]], now=121, policy=RelayTicketPolicy(min_ticket_families=1), book=book)
    reject_report = assess_relay_tickets(request, [mismatch, over], now=120, policy=RelayTicketPolicy(min_ticket_families=1))

    assert first_report.accept
    assert replay_report.decision_kind is RelayTicketDecisionKind.QUARANTINE_REPLAY
    assert reject_report.rejected[0].decision_kind is RelayTicketDecisionKind.REJECT_PAYLOAD_SCOPE_MISMATCH
    assert reject_report.rejected[1].decision_kind is RelayTicketDecisionKind.REJECT_OVER_BUDGET


def test_relayticket_quarantines_same_sequence_fork():
    request = relay_request()
    first = ticket("fork", family="fam-a", sequence=1)
    forked = replace(first, payload_digest=h("payload-fork"))
    forked = replace(forked, signature=keypair("relay:fork").sign(forked.unsigned_payload()))
    report = assess_relay_tickets(request, [first, forked], now=120, policy=RelayTicketPolicy(min_ticket_families=1))
    # The forked ticket is also a payload mismatch for this request, so pin the
    # lower-level replay/fork behavior directly through shared book state.
    book = RelayTicketBook()
    direct_first = book.check_and_spend(first, request, now=120)
    fork_same_request = replace(first, flags=("wake", "fork"))
    fork_same_request = replace(fork_same_request, signature=keypair("relay:fork").sign(fork_same_request.unsigned_payload()))
    direct_fork = book.check_and_spend(fork_same_request, request, now=121)
    assert direct_first.accepted
    assert direct_fork.decision_kind is RelayTicketDecisionKind.QUARANTINE_SAME_SEQ_FORK
    assert report.decision_kind in {RelayTicketDecisionKind.ACCEPT_RELAY_TICKETS, RelayTicketDecisionKind.REJECT_PAYLOAD_SCOPE_MISMATCH}


def lease(label: str, family: str) -> ContactLease:
    kp, ident = identity("contact:" + label)
    return ContactLease.create(identity=ident, keypair=kp, family_id=family, purposes=(ContactLeasePurpose.ROUTE,), sequence=1, issued_at=100, ttl=500)


def attest(label: str, lease_obj: ContactLease, *, attester_family: str, path_family: str) -> RouteAttestation:
    kp, ident = identity("attester:" + label)
    return RouteAttestation.create(
        keypair=kp,
        attester_node_id=ident.node_id,
        attester_family=attester_family,
        path_family=path_family,
        lease=lease_obj,
        purpose=ContactLeasePurpose.ROUTE,
        sequence=1,
        issued_at=110,
        ttl=300,
    )


def candidate(label: str, contact_family: str, introducer_family: str, path_family: str, *, interest_points: int = 1) -> GossipCandidate:
    item_lease = lease(label, contact_family)
    return GossipCandidate(
        lease=item_lease,
        introducer_node_id=h("intro:" + label),
        introducer_family=introducer_family,
        attestation=attest(label, item_lease, attester_family="att-" + introducer_family, path_family=path_family),
        distance_rank=0,
        interest_points=interest_points,
    )


def test_gossipsieve_accepts_attested_diverse_route_gossip():
    candidates = (
        candidate("a", "contact-a", "intro-a", "path-a"),
        candidate("b", "contact-b", "intro-b", "path-b"),
        candidate("c", "contact-c", "intro-b", "path-a"),
    )
    report = sieve_gossip_candidates(candidates, now=120, target=h("target"))
    assert report.decision_kind is GossipSieveDecisionKind.ACCEPT_GOSSIP_BATCH
    assert report.accept
    assert set(report.contact_family_counts) == {"contact-a", "contact-b", "contact-c"}


def test_gossipsieve_rejects_interest_budget_and_intro_capture():
    expensive = (
        candidate("exp-a", "contact-a", "intro-a", "path-a", interest_points=10),
        candidate("exp-b", "contact-b", "intro-b", "path-b", interest_points=10),
        candidate("exp-c", "contact-c", "intro-c", "path-c", interest_points=10),
    )
    expensive_report = sieve_gossip_candidates(expensive, now=120, target=h("target"), policy=GossipSievePolicy(max_interest_points=5))
    captured = (
        candidate("cap-a", "contact-a", "one-intro", "path-a"),
        candidate("cap-b", "contact-b", "one-intro", "path-b"),
        candidate("cap-c", "contact-c", "one-intro", "path-c"),
    )
    captured_report = sieve_gossip_candidates(captured, now=120, target=h("target"), policy=GossipSievePolicy(min_introducer_families=1, max_per_introducer_family=3))
    assert expensive_report.decision_kind is GossipSieveDecisionKind.REJECT_INTEREST_BUDGET
    assert captured_report.decision_kind is GossipSieveDecisionKind.QUARANTINE_INTRODUCER_CAPTURE
    assert captured_report.quarantined


def test_clockfold_audit_passes_current_clock_relay_gossip_surfaces():
    root = Path(__file__).resolve().parents[1]
    report = audit_clock_fold(root, revision="rev0024")
    assert report.status == "pass"
    assert report.error_count == 0
