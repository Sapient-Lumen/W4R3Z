from __future__ import annotations

from dataclasses import replace

from i2p_dht_lab.capgrant import (
    CapabilityDecisionKind,
    CapabilityEvaluator,
    CapabilityGrant,
    CapabilityRequest,
    CapabilityVerb,
    RevocationEntry,
    RevocationHead,
    RevocationReason,
    make_revocation_mutable_head,
)
from i2p_dht_lab.chaos import FakeAsyncLookupHarness, FakeReplica, ReplicaBehavior, assess_seed_capture
from i2p_dht_lab.forkwatch import (
    HeadVerdictKind,
    MutableHeadMemory,
    MutableHeadObservation,
    ObservationSource,
    WitnessKind,
    mutable_record_digest,
    receipts_for_target,
)
from i2p_dht_lab.identity import DhtKeypair, NodeIdentity
from i2p_dht_lab.mutable import MutableRecord
from i2p_dht_lab.mutable_future import SeedPortfolio
from i2p_dht_lab.sovereignty import ContactCard


def kp(n: int) -> DhtKeypair:
    return DhtKeypair.from_seed(bytes([n]) * 32)


def rec(keypair: DhtKeypair, seq: int, value: str, *, now: int = 1000) -> MutableRecord:
    return MutableRecord.create(keypair=keypair, seq=seq, value={b"v": value}, salt=b"lab", now=now, ttl=10_000)


def test_head_memory_detects_valid_stale_record_after_higher_sequence() -> None:
    publisher = kp(1)
    witness = kp(2)
    high = rec(publisher, 3, "fresh")
    low = rec(publisher, 2, "stale")
    memory = MutableHeadMemory()

    v1 = memory.observe(
        MutableHeadObservation(high, b"a" * 32, ObservationSource.LOOKUP_REPLY, at=1100),
        now=1100,
    )
    v2 = memory.observe(
        MutableHeadObservation(low, b"b" * 32, ObservationSource.LOOKUP_REPLY, at=1101),
        now=1101,
    )
    receipt = memory.make_receipt(verdict=v2, record=low, witness_keypair=witness, witness_node_id=b"w" * 32, issued_at=1101)

    assert v1.kind is HeadVerdictKind.ACCEPT_FRESH
    assert v2.kind is HeadVerdictKind.STALE_VALID
    assert v2.highest_seq == 3
    assert receipt.kind is WitnessKind.ROLLBACK_SEEN
    assert receipt.verify(now=1102)
    assert receipts_for_target([receipt], low.target_i2p256, now=1102) == (receipt,)


def test_head_memory_detects_same_sequence_fork_and_receipt_contains_both_hashes() -> None:
    publisher = kp(3)
    witness = kp(4)
    left = rec(publisher, 7, "left")
    right = rec(publisher, 7, "right")
    memory = MutableHeadMemory()

    first = memory.observe(MutableHeadObservation(left, b"l" * 32, ObservationSource.LOOKUP_REPLY, at=2000), now=2000)
    second = memory.observe(MutableHeadObservation(right, b"r" * 32, ObservationSource.GARDEN_WITNESS, at=2001), now=2001)
    receipt = memory.make_receipt(verdict=second, record=right, witness_keypair=witness, witness_node_id=b"w" * 32, issued_at=2001)

    assert first.kind is HeadVerdictKind.ACCEPT_FRESH
    assert second.kind is HeadVerdictKind.SAME_SEQ_FORK
    assert set(second.fork_hashes) == {mutable_record_digest(left), mutable_record_digest(right)}
    assert receipt.kind is WitnessKind.SAME_SEQ_FORK_SEEN
    assert set(receipt.record_hashes) == set(second.fork_hashes)
    assert receipt.verify(now=2002)


def test_head_memory_rejects_tampered_signature_without_learning_highest() -> None:
    publisher = kp(5)
    valid = rec(publisher, 1, "ok")
    tampered = replace(valid, signature=b"x" * 64)
    memory = MutableHeadMemory()
    verdict = memory.observe(MutableHeadObservation(tampered, b"x" * 32, ObservationSource.LOOKUP_REPLY, at=3000), now=3000)

    assert verdict.kind is HeadVerdictKind.INVALID_SIGNATURE
    assert tampered.target_i2p256 not in memory.highest_seq_by_target


def test_capability_grant_allows_precise_delegation_and_denies_wrong_resource() -> None:
    issuer = kp(6)
    subject = kp(7)
    resource = b"mutable-target:" + b"z" * 32
    grant = CapabilityGrant.create(
        issuer_keypair=issuer,
        subject_public_key=subject.public_key_bytes,
        verbs=[CapabilityVerb.WATCH_HEAD, CapabilityVerb.WITNESS_HEAD],
        resource=resource,
        issued_at=4000,
        ttl=100,
        audience=b"garden-alpha",
        caveats=["max_heads=128", "receipts_are_evidence_not_truth"],
    )
    evaluator = CapabilityEvaluator()

    ok = evaluator.decide(grant, CapabilityRequest(CapabilityVerb.WATCH_HEAD, resource, audience=b"garden-alpha", at=4050))
    wrong_resource = evaluator.decide(grant, CapabilityRequest(CapabilityVerb.WATCH_HEAD, b"other", audience=b"garden-alpha", at=4050))
    wrong_audience = evaluator.decide(grant, CapabilityRequest(CapabilityVerb.WATCH_HEAD, resource, audience=b"garden-beta", at=4050))
    wrong_verb = evaluator.decide(grant, CapabilityRequest(CapabilityVerb.BRIDGE_QUERY, resource, audience=b"garden-alpha", at=4050))

    assert ok.allowed
    assert wrong_resource.kind is CapabilityDecisionKind.DENY_RESOURCE
    assert wrong_audience.kind is CapabilityDecisionKind.DENY_AUDIENCE
    assert wrong_verb.kind is CapabilityDecisionKind.DENY_VERB


def test_revocation_head_denies_a_previously_valid_grant_and_can_be_mutable() -> None:
    issuer = kp(8)
    subject = kp(9)
    grant = CapabilityGrant.create(
        issuer_keypair=issuer,
        subject_public_key=subject.public_key_bytes,
        verbs=[CapabilityVerb.SEED_GATE],
        resource=b"*",
        issued_at=5000,
        ttl=500,
    )
    entry = RevocationEntry(grant.grant_hash, RevocationReason.OPERATOR_REQUEST, issued_at=5010, note="operator rotated garden key")
    head = RevocationHead.create(authority_keypair=issuer, sequence=2, issued_at=5010, ttl=500, entries=[entry])
    evaluator = CapabilityEvaluator(revocation_heads=[head])
    decision = evaluator.decide(grant, CapabilityRequest(CapabilityVerb.SEED_GATE, b"anything", at=5020))
    mutable_head = make_revocation_mutable_head(authority_keypair=issuer, revocation_head=head, now=5010)

    assert head.verify(now=5020)
    assert decision.kind is CapabilityDecisionKind.DENY_REVOKED
    assert mutable_head.verify()
    assert mutable_head.seq == head.sequence
    assert mutable_head.kind == "capgrant.revocation_head"


def test_fake_lookup_harness_generates_receipts_for_stale_and_forked_replies() -> None:
    publisher = kp(10)
    witness = kp(11)
    old = rec(publisher, 1, "old")
    new = rec(publisher, 2, "new")
    fork_a = rec(publisher, 3, "fork-a")
    fork_b = rec(publisher, 3, "fork-b")

    honest = FakeReplica(replica_id=b"h" * 32, behavior=ReplicaBehavior.HONEST, delay_ms=100)
    stale = FakeReplica(replica_id=b"s" * 32, behavior=ReplicaBehavior.STALE, delay_ms=200)
    fork = FakeReplica(replica_id=b"f" * 32, behavior=ReplicaBehavior.FORK, delay_ms=300)
    for replica in (honest, stale, fork):
        replica.store(old)
    honest.store(new)
    fork.store(fork_a)
    fork.store(fork_b)

    transcript = FakeAsyncLookupHarness([stale, honest, fork]).lookup_mutable(
        target=old.target_i2p256,
        witness_keypair=witness,
        witness_node_id=b"w" * 32,
        now=6000,
    )

    assert transcript.freshest_seq == 3
    assert transcript.saw_stale
    assert transcript.saw_fork
    assert transcript.alarm_count >= 2
    assert all(receipt.verify(now=6001) for receipt in transcript.receipts)


def make_card(n: int, *, channel: str, garden: bool = False, issued_at: int = 7000) -> ContactCard:
    keypair = kp(30 + n)
    identity = NodeIdentity.create(destination=f"dest-{n}.b32.i2p", keypair=keypair)
    caps = ["seed_gate"] if garden else ["leaf"]
    if garden:
        caps.append("garden")
    return ContactCard.create(
        identity=identity,
        keypair=keypair,
        issued_at=issued_at,
        ttl=10_000,
        capabilities=caps,
        bootstrap_hints={"channel": channel},
    )


def test_seed_capture_report_flags_overcaptured_entrance_portfolio() -> None:
    cards = [
        make_card(1, channel="central", garden=True),
        make_card(2, channel="central", garden=True),
        make_card(3, channel="buddy"),
        make_card(4, channel="garden"),
    ]
    portfolio = SeedPortfolio.from_cards(label="lab", sequence=1, cards=cards, channel="fallback", issued_at=7000)
    report = assess_seed_capture(portfolio, attacker_node_ids=[cards[0].node_id, cards[1].node_id], max_capture_ratio=0.35)

    assert report.total_entries == 4
    assert report.captured_entries == 2
    assert report.capture_ratio == 0.5
    assert report.risky
    assert report.reason == "attacker_weight_too_high"


def test_seed_capture_report_accepts_diverse_uncaptured_portfolio() -> None:
    cards = [
        make_card(11, channel="central", garden=True),
        make_card(12, channel="garden", garden=True),
        make_card(13, channel="buddy"),
        make_card(14, channel="direct"),
        make_card(15, channel="cache"),
    ]
    portfolio = SeedPortfolio.from_cards(label="lab2", sequence=1, cards=cards, channel="fallback", issued_at=7000)
    report = assess_seed_capture(portfolio, attacker_node_ids=[cards[0].node_id], max_capture_ratio=0.35)

    assert not report.risky
    assert report.channel_diversity >= 4
    assert report.garden_entries == 2
