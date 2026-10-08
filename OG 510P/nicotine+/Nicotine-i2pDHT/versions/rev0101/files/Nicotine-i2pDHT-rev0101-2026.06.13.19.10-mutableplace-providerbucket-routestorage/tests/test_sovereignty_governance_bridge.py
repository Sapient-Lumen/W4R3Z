from i2p_dht_lab.bridge import (
    BridgeBudget,
    BridgeMode,
    ClassicOperation,
    decide_bridge_operation,
    mode_buys_sovereignty,
    plan_bridge_service,
)
from i2p_dht_lab.governance import (
    BanEntry,
    BanReason,
    BanScope,
    PolicyCapsule,
    PolicyAction,
    decide_card_policy,
    governance_guardrails,
)
from i2p_dht_lab.identity import DhtKeypair, NodeIdentity
from i2p_dht_lab.sovereignty import (
    ContactCard,
    EntranceCache,
    EntranceChannel,
    EntrancePolicy,
    MetadataPosture,
    ParticipationMode,
    assess_i2p_only_readiness,
)


def make_card(seed_byte: int, *, now: int, channel: str = "direct_invite", garden: bool = False) -> ContactCard:
    keypair = DhtKeypair.from_seed(bytes([seed_byte]) * 32)
    identity = NodeIdentity.create(destination=f"dest-{seed_byte}.b32.i2p", keypair=keypair)
    caps = ["dht", "peer"]
    if garden:
        caps.extend(["garden", "seed_gate"])
    return ContactCard.create(
        identity=identity,
        keypair=keypair,
        issued_at=now,
        ttl=72 * 3600,
        capabilities=caps,
        context="test-i2p-dht",
        bootstrap_hints={"channel": channel, "transport": "sam-stream"},
    )


def test_contact_card_recomputes_node_id_and_verifies() -> None:
    now = 1_765_100_000
    card = make_card(1, now=now, garden=True)
    assert card.verify(now=now + 1)
    assert card.has_capability("garden")
    tampered = ContactCard(
        destination=card.destination,
        public_key=card.public_key,
        node_id=b"\x00" * 32,
        work_nonce=card.work_nonce,
        issued_at=card.issued_at,
        expires_at=card.expires_at,
        capabilities=card.capabilities,
        context=card.context,
        bootstrap_hints=card.bootstrap_hints,
        signature=card.signature,
    )
    assert not tampered.verify(now=now + 1)


def test_entrance_policy_and_cache_support_i2p_only_readiness() -> None:
    now = 1_765_100_000
    policy = EntrancePolicy(mode=ParticipationMode.HYBRID_ENTRANCE, metadata_posture=MetadataPosture.CONNECTIVE)
    assert EntranceChannel.CENTRAL_SERVER_SIDELOAD in policy.allowed_channels()
    assert EntranceChannel.SEARCH_RESULT_HINT in policy.allowed_channels()

    cache = EntranceCache(max_cards=32)
    channels = ["central", "buddy", "garden", "room"]
    for idx in range(1, 21):
        card = make_card(idx, now=now - idx, channel=channels[idx % len(channels)], garden=idx <= 3)
        receipt = cache.add(card, channel=EntranceChannel.BUDDY_EXCHANGE, now=now)
        assert receipt.accepted
    readiness = assess_i2p_only_readiness(cache.cards, now=now, min_contacts=16, min_gardens=2, min_channels=3)
    assert readiness.ready
    assert readiness.reason == "ready_for_i2p_only_start"


def test_policy_capsule_can_deny_official_surfaces_without_dht_truth_claim() -> None:
    now = 1_765_100_000
    card = make_card(9, now=now)
    authority = DhtKeypair.from_seed(b"A" * 32)
    entry = BanEntry(
        public_key=card.public_key,
        scopes=(BanScope.OFFICIAL_BOOTSTRAP, BanScope.CLASSIC_BRIDGE),
        reason=BanReason.BRIDGE_ABUSE,
        issued_at=now,
        expires_at=now + 3600,
        note="test ban",
    )
    capsule = PolicyCapsule.create(authority_name="test-maintainers", authority_keypair=authority, sequence=1, issued_at=now, entries=(entry,))
    assert capsule.verify(now=now + 1, trusted_authority_key=authority.public_key_bytes)

    decision = decide_card_policy(
        card,
        capsules=(capsule,),
        mode=ParticipationMode.HYBRID_ENTRANCE,
        now=now + 1,
        official_surface=True,
    )
    assert decision.action is PolicyAction.DENY_OFFICIAL_SURFACE
    assert not decision.allowed
    assert "policy_capsules_are_subjective_not_dht_truth" in governance_guardrails()


def test_bridge_offer_is_gateway_and_can_refuse_policy_banned_keys() -> None:
    now = 1_765_100_000
    card = make_card(10, now=now)
    authority = DhtKeypair.from_seed(b"B" * 32)
    capsule = PolicyCapsule.create(
        authority_name="test-maintainers",
        authority_keypair=authority,
        sequence=2,
        issued_at=now,
        entries=(BanEntry(
            public_key=card.public_key,
            scopes=(BanScope.CLASSIC_BRIDGE,),
            reason=BanReason.SPAM_OR_HARASSMENT,
            issued_at=now,
            expires_at=now + 3600,
        ),),
    )
    policy_decision = decide_card_policy(card, capsules=(capsule,), mode=ParticipationMode.GARDEN, now=now + 1)
    assert policy_decision.action is PolicyAction.DENY_BRIDGE

    offer = plan_bridge_service(BridgeBudget(
        mode=BridgeMode.PUBLIC_GARDEN_GATEWAY,
        max_classic_clients=100,
        upload_kib_s=4096,
        max_queries_per_minute=120,
        max_provider_announces_per_hour=0,
    ))
    assert offer.supports(ClassicOperation.SEARCH)
    assert not offer.supports(ClassicOperation.PROVIDER_ANNOUNCE)
    refused = decide_bridge_operation(offer, ClassicOperation.SEARCH, policy_decision=policy_decision)
    assert not refused.allowed
    assert refused.reason.startswith("policy_refused")


def test_i2p_only_mode_can_run_without_classic_login_and_local_gateway() -> None:
    assert mode_buys_sovereignty(ParticipationMode.I2P_ONLY, BridgeMode.LOCALHOST_COMPAT_SHIM)
    budget = BridgeBudget(
        mode=BridgeMode.LOCALHOST_COMPAT_SHIM,
        max_classic_clients=1,
        upload_kib_s=128,
        max_queries_per_minute=8,
        max_provider_announces_per_hour=0,
    )
    offer = plan_bridge_service(budget)
    allowed = decide_bridge_operation(offer, ClassicOperation.SEARCH)
    assert allowed.allowed
    write_refused = decide_bridge_operation(offer, ClassicOperation.PROVIDER_ANNOUNCE, authenticated_invite=False)
    assert not write_refused.allowed
