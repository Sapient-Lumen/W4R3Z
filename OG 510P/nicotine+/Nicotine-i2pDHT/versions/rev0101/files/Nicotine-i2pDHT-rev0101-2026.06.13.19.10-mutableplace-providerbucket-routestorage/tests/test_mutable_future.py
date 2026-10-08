
from i2p_dht_lab.governance import BanEntry, BanReason, BanScope, PolicyCapsule
from i2p_dht_lab.identity import DhtKeypair, NodeIdentity
from i2p_dht_lab.mutable import MutableRecord
from i2p_dht_lab.mutable_future import (
    HeadAlertKind,
    HeadObservation,
    MutableDreamKind,
    PolicyPointer,
    PolicyPortfolio,
    SeedPortfolio,
    analyze_head_observations,
    dream_register,
    open_question_register,
    slot_salt,
)
from i2p_dht_lab.sovereignty import ContactCard


def _card(idx: int, now: int, channel: str, garden: bool = False) -> ContactCard:
    kp = DhtKeypair.from_seed(bytes([idx]) * 32)
    ident = NodeIdentity.create(destination=f"rev0008-node-{idx}.b32.i2p", keypair=kp)
    caps = ["dht", "peer"] + (["garden", "seed_gate"] if garden else [])
    return ContactCard.create(
        identity=ident,
        keypair=kp,
        issued_at=now - idx,
        ttl=72 * 3600,
        capabilities=caps,
        context="rev0008-mutable-future-test",
        bootstrap_hints={"channel": channel},
    )


def test_question_and_dream_registers_are_deep_enough():
    questions = open_question_register()
    dreams = dream_register()
    assert len(questions) >= 8
    assert len(dreams) >= 10
    assert any(q.slug == "same_seq_equivocation" for q in questions)
    assert any(d.kind is MutableDreamKind.FLOSS_SYNC for d in dreams)
    assert any(d.kind is MutableDreamKind.CAPABILITY_REVOCATION for d in dreams)


def test_seed_portfolio_head_is_mutable_and_diversity_scored():
    now = 1_765_000_000
    channels = ["central", "buddy", "garden", "room", "cache", "direct"]
    cards = tuple(_card(i + 1, now, channels[i % len(channels)], garden=i < 3) for i in range(8))
    publisher = DhtKeypair.from_seed(b"S" * 32)
    portfolio = SeedPortfolio.from_cards(label="official+friends", sequence=3, cards=cards, channel="fallback", issued_at=now)
    assert portfolio.diversity_score >= 20
    head = portfolio.make_head(publisher, now=now)
    assert head.verify()
    assert head.kind == "future.seed_portfolio"
    assert head.salt == slot_salt(MutableDreamKind.SEED_PORTFOLIO, "official+friends")


def test_policy_portfolio_points_to_capsules_without_making_them_truth():
    now = 1_765_000_000
    authority = DhtKeypair.from_seed(b"P" * 32)
    banned = DhtKeypair.from_seed(b"B" * 32).public_key_bytes
    capsule = PolicyCapsule.create(
        authority_name="rev0008-demo-authority",
        authority_keypair=authority,
        sequence=9,
        issued_at=now,
        entries=(BanEntry(
            public_key=banned,
            scopes=(BanScope.OFFICIAL_BOOTSTRAP,),
            reason=BanReason.BRIDGE_ABUSE,
            issued_at=now,
            expires_at=now + 3600,
        ),),
    )
    pointer = PolicyPointer.from_capsule(capsule, scope_hint="official-default")
    portfolio = PolicyPortfolio(label="defaults", sequence=4, issued_at=now, expires_at=now + 86400, pointers=(pointer,))
    head = portfolio.make_head(authority, now=now)
    assert head.verify()
    assert head.value[b"kind"] in {b"policy_portfolio", b"policy_portfolio_pointer"}
    if head.value[b"kind"] == b"policy_portfolio":
        assert head.value[b"pointers"][0][b"hash"] == capsule.capsule_hash
    assert head.kind == "future.policy_portfolio"


def test_head_observation_detects_same_sequence_fork_and_rollback():
    now = 1_765_000_000
    kp = DhtKeypair.from_seed(b"H" * 32)
    rec_a = MutableRecord.create(keypair=kp, seq=5, value={b"v": b"a"}, salt=b"fork-demo", now=now)
    rec_b = MutableRecord.create(keypair=kp, seq=5, value={b"v": b"b"}, salt=b"fork-demo", now=now)
    obs_a = HeadObservation.from_record(rec_a, source_node_id=b"a" * 32, observed_at=now)
    obs_b = HeadObservation.from_record(rec_b, source_node_id=b"b" * 32, observed_at=now)
    health = analyze_head_observations((obs_a, obs_b), known_seq=4)
    assert health.kind is HeadAlertKind.SAME_SEQUENCE_FORK
    assert not health.healthy

    stale = analyze_head_observations((obs_a,), known_seq=9)
    assert stale.kind is HeadAlertKind.STALE_OR_ROLLBACK
    assert stale.stale_sources


def test_head_observation_accepts_newer_consistent_head():
    now = 1_765_000_000
    kp = DhtKeypair.from_seed(b"N" * 32)
    rec = MutableRecord.create(keypair=kp, seq=10, value={b"v": b"new"}, salt=b"advance-demo", now=now)
    obs = HeadObservation.from_record(rec, source_node_id=b"n" * 32, observed_at=now)
    health = analyze_head_observations((obs,), known_seq=9)
    assert health.kind is HeadAlertKind.ADVANCED
    assert health.healthy
