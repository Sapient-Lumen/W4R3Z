from __future__ import annotations

from dataclasses import replace

from i2p_dht_lab.capgrant import CapabilityGrant, CapabilityRequest, CapabilityVerb, RevocationEntry, RevocationHead, RevocationReason
from i2p_dht_lab.forkwatch import WitnessKind, WitnessReceipt
from i2p_dht_lab.identity import DhtKeypair, NodeIdentity
from i2p_dht_lab.mutable import MutableRecord
from i2p_dht_lab.mutable_future import SeedPortfolio
from i2p_dht_lab.pathpressure import (
    PathAlarmKind,
    PathHeadReply,
    PathPressureDecisionKind,
    PathPressurePolicy,
    run_path_pressure_lookup,
)
from i2p_dht_lab.revocation_pressure import RevocationHeadMemory, RevocationPressureKind
from i2p_dht_lab.seedcapture import SeedCaptureKind, SeedCapturePolicy, analyze_seed_capture_pressure, select_diverse_seed_entries
from i2p_dht_lab.sovereignty import ContactCard
from i2p_dht_lab.succession import KeySuccessionRecord, SuccessionMemory, SuccessionVerdictKind
from i2p_dht_lab.witnesspoison import ReceiptAnalysisKind, WitnessHint, analyze_witness_receipts


def kp(n: int) -> DhtKeypair:
    return DhtKeypair.from_seed(bytes([n]) * 32)


def rec(keypair: DhtKeypair, seq: int, value: str, *, now: int = 10_000, salt: bytes = b"risk") -> MutableRecord:
    return MutableRecord.create(keypair=keypair, seq=seq, value={b"v": value}, salt=salt, now=now, ttl=10_000)


def card(n: int, *, channel: str, garden: bool = False, weight: int = 1, issued_at: int = 20_000) -> ContactCard:
    keypair = kp(40 + n)
    ident = NodeIdentity.create(destination=f"rev0010-card-{n}.b32.i2p", keypair=keypair)
    caps = ["dht"] + (["garden", "seed_gate"] if garden else ["leaf"])
    # weight lives in the SeedPortfolioEntry, not the card. Tests patch it after
    # portfolio creation where needed.
    return ContactCard.create(identity=ident, keypair=keypair, issued_at=issued_at, ttl=20_000, capabilities=caps, bootstrap_hints={"channel": channel})


def test_path_pressure_refuses_fast_single_family_empty_quorum_then_accepts_diverse_clean_later() -> None:
    publisher = kp(1)
    witness = kp(2)
    latest = rec(publisher, 4, "latest")
    target = latest.target_i2p256
    replies = [
        PathHeadReply.empty(responder_id=b"a1" * 16, family_id="captured-fast", target=target, delay_ms=1, note="fast empty"),
        PathHeadReply.empty(responder_id=b"a2" * 16, family_id="captured-fast", target=target, delay_ms=2, note="fast empty again"),
        PathHeadReply.from_records(responder_id=b"b" * 32, family_id="buddy", records=(latest,), delay_ms=100),
        PathHeadReply.from_records(responder_id=b"c" * 32, family_id="garden", records=(latest,), delay_ms=120),
        PathHeadReply.from_records(responder_id=b"d" * 32, family_id="cache", records=(latest,), delay_ms=140),
    ]
    policy = PathPressurePolicy(min_reply_families=3, min_head_families=2, max_empty_family_fraction=0.50)

    early = run_path_pressure_lookup(replies, target=target, witness_keypair=witness, witness_node_id=b"w" * 32, now=10_000, policy=policy, max_replies=2)
    full = run_path_pressure_lookup(replies, target=target, witness_keypair=witness, witness_node_id=b"w" * 32, now=10_000, policy=policy)

    assert early.decision.kind is PathPressureDecisionKind.CONTINUE_LOW_DIVERSITY
    assert early.needs_more_paths
    assert full.decision.kind is PathPressureDecisionKind.ACCEPT_HIGHEST
    assert full.freshest_seq == 4
    assert len(full.reply_families) == 4


def test_path_pressure_detects_posthoc_stale_even_when_stale_arrived_first() -> None:
    publisher = kp(3)
    witness = kp(4)
    stale = rec(publisher, 2, "old")
    latest = rec(publisher, 5, "new")
    target = stale.target_i2p256
    replies = [
        PathHeadReply.from_records(responder_id=b"s" * 32, family_id="fast-captured", records=(stale,), delay_ms=1),
        PathHeadReply.from_records(responder_id=b"h1" * 16, family_id="garden-a", records=(latest,), delay_ms=200),
        PathHeadReply.from_records(responder_id=b"h2" * 16, family_id="garden-b", records=(latest,), delay_ms=220),
    ]

    transcript = run_path_pressure_lookup(
        replies,
        target=target,
        witness_keypair=witness,
        witness_node_id=b"w" * 32,
        now=11_000,
        policy=PathPressurePolicy(min_reply_families=3, min_head_families=2, require_no_posthoc_stale=True),
    )

    assert transcript.freshest_seq == 5
    assert transcript.alarm_count(PathAlarmKind.POSTHOC_STALE) == 1
    assert transcript.decision.kind is PathPressureDecisionKind.CONTINUE_STALE_PRESSURE


def test_path_pressure_same_sequence_fork_keeps_lookup_open() -> None:
    publisher = kp(5)
    witness = kp(6)
    left = rec(publisher, 9, "left")
    right = rec(publisher, 9, "right")
    target = left.target_i2p256
    replies = [
        PathHeadReply.from_records(responder_id=b"l" * 32, family_id="family-left", records=(left,), delay_ms=10),
        PathHeadReply.from_records(responder_id=b"r" * 32, family_id="family-right", records=(right,), delay_ms=20),
        PathHeadReply.from_records(responder_id=b"m" * 32, family_id="family-mirror", records=(left,), delay_ms=30),
    ]

    transcript = run_path_pressure_lookup(replies, target=target, witness_keypair=witness, witness_node_id=b"w" * 32, now=12_000)

    assert transcript.alarm_count(PathAlarmKind.SAME_SEQUENCE_FORK) >= 1
    assert transcript.decision.kind is PathPressureDecisionKind.CONTINUE_FORK_PRESSURE
    assert transcript.receipts
    assert all(receipt.verify(now=12_001) for receipt in transcript.receipts)


def make_receipt(kind: WitnessKind, witness: DhtKeypair, node_id: bytes, target: bytes, *, highest: int, observed: int, hashes: tuple[bytes, ...], at: int) -> WitnessReceipt:
    return WitnessReceipt.create(
        witness_keypair=witness,
        witness_node_id=node_id,
        kind=kind,
        target=target,
        subject_public_key=kp(7).public_key_bytes,
        salt=b"risk",
        highest_seq=highest,
        observed_seq=observed,
        record_hashes=hashes,
        issued_at=at,
        ttl=10_000,
    )


def test_witness_poison_single_garden_family_is_not_alarm_quorum() -> None:
    target = b"t" * 32
    w1 = kp(8)
    w2 = kp(9)
    r1 = make_receipt(WitnessKind.ROLLBACK_SEEN, w1, b"w1" * 16, target, highest=5, observed=2, hashes=(b"a" * 32,), at=13_000)
    r2 = make_receipt(WitnessKind.SAME_SEQ_FORK_SEEN, w2, b"w2" * 16, target, highest=5, observed=5, hashes=(b"b" * 32, b"c" * 32), at=13_000)
    analysis = analyze_witness_receipts(
        (r1, r2),
        hints=(WitnessHint(b"w1" * 16, "same-garden"), WitnessHint(b"w2" * 16, "same-garden")),
        now=13_001,
        min_alarm_families=2,
    )

    assert analysis.kind is ReceiptAnalysisKind.SINGLE_FAMILY_ALARM
    assert not analysis.usable_alarm_quorum
    assert analysis.alarm_families == frozenset({"same-garden"})


def test_witness_poison_diverse_alarm_receipts_become_usable_evidence() -> None:
    target = b"u" * 32
    w1 = kp(10)
    w2 = kp(11)
    r1 = make_receipt(WitnessKind.ROLLBACK_SEEN, w1, b"x1" * 16, target, highest=8, observed=3, hashes=(b"a" * 32,), at=14_000)
    r2 = make_receipt(WitnessKind.SAME_SEQ_FORK_SEEN, w2, b"x2" * 16, target, highest=8, observed=8, hashes=(b"b" * 32, b"c" * 32), at=14_000)
    analysis = analyze_witness_receipts(
        (r1, r2),
        hints=(WitnessHint(b"x1" * 16, "garden-east"), WitnessHint(b"x2" * 16, "garden-west")),
        now=14_001,
        min_alarm_families=2,
    )

    assert analysis.kind is ReceiptAnalysisKind.VALID_EVIDENCE
    assert analysis.usable_alarm_quorum
    assert analysis.alarm_families == frozenset({"garden-east", "garden-west"})


def test_witness_poison_contradictory_same_witness_gets_quarantined() -> None:
    target = b"v" * 32
    witness = kp(12)
    node = b"zz" * 16
    good = make_receipt(WitnessKind.HIGHEST_SEEN, witness, node, target, highest=9, observed=9, hashes=(b"h" * 32,), at=15_000)
    bad = make_receipt(WitnessKind.ROLLBACK_SEEN, witness, node, target, highest=9, observed=4, hashes=(b"r" * 32,), at=15_000)
    analysis = analyze_witness_receipts((good, bad), hints=(WitnessHint(node, "one-garden"),), now=15_001)

    assert analysis.kind is ReceiptAnalysisKind.CONTRADICTORY_WITNESS
    assert node in analysis.contradictory_witnesses


def test_seed_capture_pressure_flags_channel_and_family_monoculture_and_selector_spreads_choices() -> None:
    cards = [card(i, channel="central", garden=(i < 3)) for i in range(1, 9)] + [
        card(20, channel="buddy", garden=True),
        card(21, channel="garden", garden=True),
        card(22, channel="direct", garden=False),
    ]
    portfolio = SeedPortfolio.from_cards(label="capture", sequence=1, cards=cards, channel="fallback", issued_at=20_000)
    # Make the central family deliberately heavy by replacing entries.
    heavy_entries = []
    for entry in portfolio.entries:
        if entry.channel == "central":
            heavy_entries.append(replace(entry, weight=5))
        else:
            heavy_entries.append(entry)
    portfolio = replace(portfolio, entries=tuple(heavy_entries))
    families = {entry.node_id: ("central-family" if entry.channel == "central" else f"family-{entry.channel}") for entry in portfolio.entries}

    pressure = analyze_seed_capture_pressure(
        portfolio,
        node_families=families,
        policy=SeedCapturePolicy(max_single_channel_fraction=0.45, max_single_family_fraction=0.45, min_channels=3, min_families=3),
    )
    selected = select_diverse_seed_entries(portfolio, node_families=families, limit=4)

    assert pressure.kind in {SeedCaptureKind.CHANNEL_MONOCULTURE, SeedCaptureKind.FAMILY_MONOCULTURE}
    assert len({entry.channel for entry in selected}) >= 3
    assert len({families[entry.node_id] for entry in selected}) >= 3


def test_seed_capture_pressure_flags_known_attacker_weight_before_other_diversity() -> None:
    cards = [card(30 + i, channel=ch, garden=True) for i, ch in enumerate(["central", "buddy", "garden", "direct", "cache"])]
    portfolio = SeedPortfolio.from_cards(label="attacker", sequence=1, cards=cards, channel="fallback", issued_at=20_000)
    entries = list(portfolio.entries)
    entries[0] = replace(entries[0], weight=10)
    portfolio = replace(portfolio, entries=tuple(entries))
    pressure = analyze_seed_capture_pressure(portfolio, attacker_node_ids=(entries[0].node_id,), policy=SeedCapturePolicy(max_attacker_weight_fraction=0.25))

    assert pressure.kind is SeedCaptureKind.ATTACKER_WEIGHT_TOO_HIGH
    assert pressure.attacker_weight_fraction > 0.25


def test_revocation_head_memory_keeps_revoked_grant_after_stale_head_replay() -> None:
    authority = kp(13)
    subject = kp(14)
    grant = CapabilityGrant.create(
        issuer_keypair=authority,
        subject_public_key=subject.public_key_bytes,
        verbs=[CapabilityVerb.SEED_GATE],
        resource=b"*",
        issued_at=30_000,
        ttl=10_000,
    )
    empty_head = RevocationHead.create(authority_keypair=authority, sequence=1, issued_at=30_100, ttl=10_000, entries=[])
    revoke_head = RevocationHead.create(
        authority_keypair=authority,
        sequence=2,
        issued_at=30_200,
        ttl=10_000,
        entries=[RevocationEntry(grant.grant_hash, RevocationReason.KEY_COMPROMISE, issued_at=30_200)],
        previous_head_hash=empty_head.head_hash,
    )
    memory = RevocationHeadMemory()

    assert memory.observe(revoke_head, now=30_300).kind is RevocationPressureKind.ACCEPT_FIRST
    stale = memory.observe(empty_head, now=30_301)

    assert stale.kind is RevocationPressureKind.STALE_ROLLBACK
    assert memory.is_revoked(authority.public_key_bytes, grant.grant_hash)


def test_revocation_head_memory_detects_same_sequence_fork_and_unions_revoked_hashes() -> None:
    authority = kp(15)
    subject1 = kp(16)
    subject2 = kp(17)
    grant1 = CapabilityGrant.create(issuer_keypair=authority, subject_public_key=subject1.public_key_bytes, verbs=[CapabilityVerb.WATCH_HEAD], resource=b"x", issued_at=31_000, ttl=10_000)
    grant2 = CapabilityGrant.create(issuer_keypair=authority, subject_public_key=subject2.public_key_bytes, verbs=[CapabilityVerb.WATCH_HEAD], resource=b"y", issued_at=31_000, ttl=10_000)
    head_a = RevocationHead.create(authority_keypair=authority, sequence=4, issued_at=31_100, ttl=10_000, entries=[RevocationEntry(grant1.grant_hash, RevocationReason.ABUSE_OR_DOS, issued_at=31_100)])
    head_b = RevocationHead.create(authority_keypair=authority, sequence=4, issued_at=31_101, ttl=10_000, entries=[RevocationEntry(grant2.grant_hash, RevocationReason.OPERATOR_REQUEST, issued_at=31_101)])
    memory = RevocationHeadMemory()

    assert memory.observe(head_a, now=31_200).accepted
    fork = memory.observe(head_b, now=31_201)

    assert fork.kind is RevocationPressureKind.SAME_SEQ_FORK
    assert memory.is_revoked(authority.public_key_bytes, grant1.grant_hash)
    assert memory.is_revoked(authority.public_key_bytes, grant2.grant_hash)


def test_key_succession_requires_old_and_new_key_signatures_and_rejects_tampering() -> None:
    old = kp(18)
    new = kp(19)
    record = KeySuccessionRecord.create(old_keypair=old, new_keypair=new, sequence=1, issued_at=40_000, ttl=10_000, reason="operator rotation")
    tampered = replace(record, new_public_key=kp(20).public_key_bytes)
    head = record.make_mutable_head(old_keypair=old, now=40_000)

    assert record.verify(now=40_001)
    assert not tampered.verify(now=40_001)
    assert head.verify()
    assert head.seq == record.sequence


def test_key_succession_memory_detects_rollback_and_same_sequence_fork() -> None:
    old = kp(21)
    new1 = kp(22)
    new2 = kp(23)
    new3 = kp(24)
    r1 = KeySuccessionRecord.create(old_keypair=old, new_keypair=new1, sequence=1, issued_at=41_000, ttl=20_000)
    r2 = KeySuccessionRecord.create(old_keypair=old, new_keypair=new2, sequence=2, issued_at=41_100, ttl=20_000, previous_record_hash=r1.record_hash)
    fork2 = KeySuccessionRecord.create(old_keypair=old, new_keypair=new3, sequence=2, issued_at=41_101, ttl=20_000, previous_record_hash=r1.record_hash)
    memory = SuccessionMemory()

    assert memory.observe(r1, now=41_200).kind is SuccessionVerdictKind.ACCEPT_FIRST
    assert memory.observe(r2, now=41_201).kind is SuccessionVerdictKind.ACCEPT_ADVANCE
    rollback = memory.observe(r1, now=41_202)
    fork = memory.observe(fork2, now=41_203)

    assert rollback.kind is SuccessionVerdictKind.REJECT_ROLLBACK
    assert fork.kind is SuccessionVerdictKind.SAME_SEQUENCE_FORK
    assert memory.current_key_for(old.public_key_bytes) == new2.public_key_bytes
