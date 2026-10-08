from i2p_dht_lab.garden import (
    EncounterEvent,
    EncounterObservation,
    GardenReceipt,
    GardenServiceKind,
    LocalAutocurator,
    MetadataCost,
    ResourceBudget,
    benefit_for_service,
    non_authority_guardrails,
    plan_garden_services,
    with_garden_capabilities,
)
from i2p_dht_lab.ids import key_id
from i2p_dht_lab.routing import Contact


def contact(n: int, destination: str | None = None) -> Contact:
    node_id = n.to_bytes(32, "big")
    return Contact(node_id=node_id, destination=destination or f"dest-{n}.b32.i2p", public_key=bytes([n % 251]) * 32)


def test_garden_budget_unlocks_services_but_not_authority():
    leaf_budget = ResourceBudget(
        storage_mb=64,
        ram_mb=64,
        upload_kib_s=32,
        max_concurrent_streams=2,
        target_uptime_hours=1,
        max_provider_records=0,
        max_mutable_watches=8,
        metadata_cost_ceiling=MetadataCost.CONNECTIVE,
    )
    leaf_plan = plan_garden_services(leaf_budget)
    assert leaf_plan.offers == ()

    garden_budget = ResourceBudget(
        storage_mb=4096,
        ram_mb=2048,
        upload_kib_s=2048,
        max_concurrent_streams=64,
        target_uptime_hours=18,
        max_provider_records=1_000_000,
        max_mutable_watches=50_000,
        metadata_cost_ceiling=MetadataCost.INDEX,
    )
    garden_plan = plan_garden_services(garden_budget)
    assert garden_plan.has(GardenServiceKind.SEED_GATE)
    assert garden_plan.has(GardenServiceKind.REGION_GARDENER)
    assert garden_plan.has(GardenServiceKind.MUTABLE_STEWARD)
    assert "garden:helper_not_authority" in garden_plan.capability_tags
    guardrails = non_authority_guardrails(garden_plan)
    assert "no_global_truth" in guardrails
    assert "sentinel_reports_are_evidence_not_truth" in guardrails


def test_metadata_ceiling_prevents_index_services_by_default():
    connective_budget = ResourceBudget(
        storage_mb=4096,
        ram_mb=2048,
        upload_kib_s=2048,
        max_concurrent_streams=64,
        target_uptime_hours=18,
        max_provider_records=1_000_000,
        max_mutable_watches=50_000,
        metadata_cost_ceiling=MetadataCost.CONNECTIVE,
    )
    plan = plan_garden_services(connective_budget)
    assert plan.has(GardenServiceKind.SEED_GATE)
    assert plan.has(GardenServiceKind.SLOPPY_CACHE)
    assert not plan.has(GardenServiceKind.REGION_GARDENER)
    assert not plan.has(GardenServiceKind.MUTABLE_STEWARD)


def test_autocuration_prefers_useful_diverse_gardens_and_punishes_lies():
    now = 10_000
    good = contact(1)
    liar = contact(2)
    slow_but_honest = contact(3)
    observations = [
        EncounterObservation(good, EncounterEvent.QUERY_OK, GardenServiceKind.SEED_GATE, at=now - 10),
        EncounterObservation(good, EncounterEvent.STORE_OK, GardenServiceKind.SEED_GATE, at=now - 9),
        EncounterObservation(good, EncounterEvent.DIVERSE_PATH, GardenServiceKind.SEED_GATE, at=now - 8),
        EncounterObservation(liar, EncounterEvent.QUERY_OK, GardenServiceKind.SEED_GATE, at=now - 7),
        EncounterObservation(liar, EncounterEvent.FALSE_PROVIDER, GardenServiceKind.SEED_GATE, at=now - 6),
        EncounterObservation(slow_but_honest, EncounterEvent.QUERY_OK, GardenServiceKind.SEED_GATE, at=now - 5, rtt_ms=3000),
        EncounterObservation(slow_but_honest, EncounterEvent.GRACEFUL_REFUSAL, GardenServiceKind.SEED_GATE, at=now - 4),
    ]
    curator = LocalAutocurator()
    ranked = curator.score_contacts(observations, now=now)
    assert ranked[0].node_id == good.node_id
    assert ranked[-1].node_id == liar.node_id
    assert ranked[-1].score < 0

    chosen = curator.choose_gardens(observations, now=now, service=GardenServiceKind.SEED_GATE, count=2)
    assert good.node_id in {item.node_id for item in chosen}
    assert liar.node_id not in {item.node_id for item in chosen}


def test_benefit_for_service_names_reciprocal_gain():
    benefit = benefit_for_service(GardenServiceKind.REGION_GARDENER)
    assert "provider" in benefit.leaf_gain
    assert "predictable" in benefit.garden_gain
    assert "global authority" in benefit.salience_hint


def test_garden_receipts_turn_into_local_observations_not_global_reputation():
    c = contact(9)
    receipt = GardenReceipt(
        garden_node_id=c.node_id,
        service=GardenServiceKind.MUTABLE_STEWARD,
        target_digest=key_id("mutable", b"slot"),
        outcome="repaired",
        count=3,
        issued_at=1234,
    )
    obs = receipt.as_observation(c)
    assert obs.event is EncounterEvent.QUERY_OK
    assert obs.service is GardenServiceKind.MUTABLE_STEWARD
    assert len(receipt.transcript_digest) == 32


def test_contacts_can_be_decorated_with_garden_capabilities():
    budget = ResourceBudget(
        storage_mb=2048,
        ram_mb=1024,
        upload_kib_s=1024,
        max_concurrent_streams=48,
        target_uptime_hours=12,
        max_provider_records=500_000,
        max_mutable_watches=10_000,
        metadata_cost_ceiling=MetadataCost.INDEX,
    )
    plan = plan_garden_services(budget)
    decorated = with_garden_capabilities(contact(11), plan)
    assert "garden:helper_not_authority" in decorated.capabilities
    assert any(tag.startswith("garden:") for tag in decorated.capabilities)
