from __future__ import annotations

from dataclasses import replace

from i2p_dht_lab.foldregistry import audit_fold_registry
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.identity import DhtKeypair
from i2p_dht_lab.launchquorum import LaunchIntent, LaunchMode, assess_launch_quorum
from i2p_dht_lab.loadsheath import (
    LoadSheathDecisionKind,
    LoadSheathPolicy,
    ServiceDemand,
    ServiceLoadBudget,
    assess_load_sheath,
)
from i2p_dht_lab.profilegc import (
    ProfileGcDecisionKind,
    ProfileGcPolicy,
    ProfileMemoryItem,
    ProfileMemoryKind,
    plan_profile_gc,
)
from i2p_dht_lab.routerharness import RouterHarnessConfig, RouterHarnessMode, assess_router_harness
from i2p_dht_lab.safestart import SafeStartDecisionKind, SafeStartReport
from i2p_dht_lab.samprobe import SamProbeDecisionKind, SamProbeProfile, build_sam_probe_plan, classify_sam_probe_transcript
from i2p_dht_lab.servicecatalog import (
    GardenServiceClass,
    ServiceCatalogDecisionKind,
    ServiceCatalogCapsule,
    ServiceDescriptor,
    assess_service_catalog,
)
from i2p_dht_lab.servicefold import audit_service_fold
from i2p_dht_lab.startmatrix import StartMatrixDecisionKind, StartProfile, assess_start_matrix
from i2p_dht_lab.persistjoin import PersistJoinDecisionKind, PersistJoinReport


def d(label: str) -> bytes:
    return sha256(("rev0036:" + label).encode("utf-8"))


def keypair(label: str = "garden") -> DhtKeypair:
    return DhtKeypair.from_seed(d("seed:" + label))


def sam_report(kind: SamProbeDecisionKind = SamProbeDecisionKind.ACCEPT_STREAMING_FIRST_PROBE):
    profile = SamProbeProfile()
    commands = build_sam_probe_plan(profile, remote_destination="example.b32.i2p")
    if kind is SamProbeDecisionKind.ACCEPT_LOCAL_UNAVAILABLE:
        return classify_sam_probe_transcript(profile, commands, (), router_unavailable=True)
    if kind is SamProbeDecisionKind.ACCEPT_SESSION_ONLY:
        commands = build_sam_probe_plan(profile, remote_destination="")
    replies = [
        "HELLO REPLY RESULT=OK VERSION=3.3",
        "DEST REPLY RESULT=OK PUB=abc PRIV=def",
        "SESSION STATUS RESULT=OK",
        "NAMING REPLY RESULT=OK NAME=example.b32.i2p VALUE=dest",
        "STREAM STATUS RESULT=OK",
    ]
    if kind is SamProbeDecisionKind.ACCEPT_SESSION_ONLY:
        replies = replies[:3]
    return classify_sam_probe_transcript(profile, commands, replies)


def safe_start(*, accept: bool = True, intent: bytes | None = None) -> SafeStartReport:
    kind = SafeStartDecisionKind.ACCEPT_SAFE_START if accept else SafeStartDecisionKind.QUARANTINE_SAMTRACE
    return SafeStartReport(
        decision_kind=kind,
        accept=accept,
        reason=kind.value,
        intent_digest=intent or d("intent"),
        negotiation_report_digest=d("negotiation"),
        migration_report_digest=d("migration"),
        samtrace_report_digest=d("samtrace"),
        pressure_digests=(d("safe-pressure"),) if not accept else (),
        report_digest=d("safe-start:" + kind.value),
    )


def persist_join(*, accept: bool = True) -> PersistJoinReport:
    kind = PersistJoinDecisionKind.ACCEPT_DURABLE_JOIN if accept else PersistJoinDecisionKind.QUARANTINE_PERSIST_RELOAD
    return PersistJoinReport(
        decision_kind=kind,
        accept=accept,
        reason=kind.value,
        persist_report_digest=d("persist"),
        journal_report_digest=d("journal"),
        checkpoint_report_digest=d("checkpoint-report"),
        scope_report_digest=d("scope"),
        store_report_digest=d("store"),
        checkpoint_digest=d("checkpoint"),
        journal_tip_digest=d("tip"),
        pressure_digests=(d("persist-pressure"),) if not accept else (),
        hard_negative_count=2,
        report_digest=d("persist-join:" + kind.value),
    )


def router_config(mode: RouterHarnessMode = RouterHarnessMode.BUNDLED_I2PD, **overrides) -> RouterHarnessConfig:
    base = dict(
        mode=mode,
        datadir_digest=d("datadir"),
        destination_digest=d("destination"),
        generated_config_digest=d("config"),
        expected_config_digest=d("config"),
    )
    base.update(overrides)
    return RouterHarnessConfig(**base)


def accepted_start(mode: LaunchMode = LaunchMode.GARDEN, *, services: int = 3, public_bridge: bool = False, metadata: str = "power"):
    sam = sam_report()
    intent = LaunchIntent(mode=mode, intent_digest=d("intent:" + mode.value), endpoint_digest=sam.endpoint_digest, generation=9, require_streaming_probe=True)
    launch = assess_launch_quorum(intent, safe_start=safe_start(intent=intent.intent_digest), persist_join=persist_join(), sam_probe=sam)
    router = assess_router_harness(router_config(), sam)
    profile = StartProfile(
        "profile-" + mode.value,
        mode,
        RouterHarnessMode.BUNDLED_I2PD,
        intent.launch_intent_digest,
        garden_service_count=services,
        public_bridge_enabled=public_bridge,
        metadata_budget_level=metadata,
    )
    start = assess_start_matrix(profile, launch=launch, router=router)
    assert start.accept, start
    return profile, start, router


def service_catalog(profile: StartProfile, start, router, *, sequence: int = 1, services=None, kp=None):
    kp = kp or keypair()
    services = tuple((
        ServiceDescriptor(GardenServiceClass.SEED_GATE, max_streams=8, max_units=1_000, reserve_units=100, public=True),
        ServiceDescriptor(GardenServiceClass.HEAD_WATCH, max_streams=8, max_units=400, reserve_units=80),
        ServiceDescriptor(GardenServiceClass.WITNESS_QUERY, max_streams=8, max_units=800, reserve_units=100),
    ) if services is None else services)
    return ServiceCatalogCapsule.create(
        keypair=kp,
        issuer_node_id=d("node"),
        sequence=sequence,
        issued_at=100,
        expires_at=1_000,
        profile=profile,
        start_report=start,
        router_report=router,
        services=services,
    )


def test_servicecatalog_accepts_signed_garden_catalog_and_leaf_empty_catalog() -> None:
    profile, start, router = accepted_start()
    catalog = service_catalog(profile, start, router)
    report = assess_service_catalog(catalog, profile=profile, start_report=start, router_report=router, now=200)
    assert report.decision_kind is ServiceCatalogDecisionKind.ACCEPT_SERVICE_CATALOG
    assert report.accept
    assert set(report.accepted_services) == {"seed_gate", "head_watch", "witness_query"}

    leaf_profile, leaf_start, leaf_router = accepted_start(LaunchMode.LEAF, services=0, metadata="normal")
    leaf_catalog = service_catalog(leaf_profile, leaf_start, leaf_router, services=())
    leaf_report = assess_service_catalog(leaf_catalog, profile=leaf_profile, start_report=leaf_start, router_report=leaf_router, now=200)
    assert leaf_report.decision_kind is ServiceCatalogDecisionKind.ACCEPT_LEAF_MINIMAL_CATALOG


def test_servicecatalog_rejects_signature_binding_time_and_sequence_pressure() -> None:
    profile, start, router = accepted_start()
    catalog = service_catalog(profile, start, router)
    tampered = replace(catalog, signature=b"x" * 64)
    assert assess_service_catalog(tampered, profile=profile, start_report=start, router_report=router, now=200).decision_kind is ServiceCatalogDecisionKind.QUARANTINE_BAD_SIGNATURE
    expired = replace(catalog, expires_at=150, signature=catalog.signature)
    # Changing expires_at invalidates the signature first; create a real expired catalog instead.
    expired = ServiceCatalogCapsule.create(keypair=keypair(), issuer_node_id=d("node"), sequence=2, issued_at=1, expires_at=10, profile=profile, start_report=start, router_report=router, services=catalog.services)
    assert assess_service_catalog(expired, profile=profile, start_report=start, router_report=router, now=200).decision_kind is ServiceCatalogDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE
    assert assess_service_catalog(catalog, profile=profile, start_report=start, router_report=router, now=200, previously_seen_catalogs=(catalog.catalog_digest,)).decision_kind is ServiceCatalogDecisionKind.QUARANTINE_REPLAY
    assert assess_service_catalog(catalog, profile=profile, start_report=start, router_report=router, now=200, highest_seen_sequence=5).decision_kind is ServiceCatalogDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK
    fork = service_catalog(profile, start, router, sequence=1, services=(ServiceDescriptor(GardenServiceClass.SEED_GATE, 8, 1_000, public=True), ServiceDescriptor(GardenServiceClass.HEAD_WATCH, 8, 400), ServiceDescriptor(GardenServiceClass.BULK_PROVIDER, 1, 1)))
    assert assess_service_catalog(fork, profile=profile, start_report=start, router_report=router, now=200, highest_seen_sequence=1, same_sequence_digest=catalog.catalog_digest).decision_kind is ServiceCatalogDecisionKind.QUARANTINE_SEQUENCE_FORK


def test_servicecatalog_rejects_profile_binding_bridge_and_overclaim_drift() -> None:
    profile, start, router = accepted_start()
    catalog = service_catalog(profile, start, router)
    wrong_profile = StartProfile("wrong-garden", LaunchMode.GARDEN, RouterHarnessMode.BUNDLED_I2PD, profile.bound_launch_intent_digest, garden_service_count=3, metadata_budget_level="power")
    assert assess_service_catalog(catalog, profile=wrong_profile, start_report=start, router_report=router, now=200).decision_kind is ServiceCatalogDecisionKind.QUARANTINE_BINDING_MISMATCH

    bridge_profile, bridge_start, bridge_router = accepted_start(LaunchMode.BRIDGE, services=2, public_bridge=True)
    no_bridge_service = service_catalog(bridge_profile, bridge_start, bridge_router, services=(
        ServiceDescriptor(GardenServiceClass.SEED_GATE, 8, 1_000, public=True),
        ServiceDescriptor(GardenServiceClass.HEAD_WATCH, 8, 1_000),
    ))
    assert assess_service_catalog(no_bridge_service, profile=bridge_profile, start_report=bridge_start, router_report=bridge_router, now=200).decision_kind is ServiceCatalogDecisionKind.QUARANTINE_BRIDGE_DRIFT
    with_bridge = service_catalog(bridge_profile, bridge_start, bridge_router, services=(
        ServiceDescriptor(GardenServiceClass.SEED_GATE, 8, 1_000, public=True),
        ServiceDescriptor(GardenServiceClass.BRIDGE_GATEWAY, 8, 1_000, public=True),
    ))
    assert assess_service_catalog(with_bridge, profile=bridge_profile, start_report=bridge_start, router_report=bridge_router, now=200).accept

    normal_profile, normal_start, normal_router = accepted_start(LaunchMode.GARDEN, services=1, metadata="normal")
    overclaim = service_catalog(normal_profile, normal_start, normal_router, services=(ServiceDescriptor(GardenServiceClass.BULK_PROVIDER, 200, 1_000_000),))
    assert assess_service_catalog(overclaim, profile=normal_profile, start_report=normal_start, router_report=normal_router, now=200).decision_kind is ServiceCatalogDecisionKind.QUARANTINE_BUDGET_OVERCLAIM


def test_loadsheath_accepts_protected_work_and_sheds_bulk_overflow() -> None:
    profile, start, router = accepted_start()
    catalog = service_catalog(profile, start, router)
    catalog_report = assess_service_catalog(catalog, profile=profile, start_report=start, router_report=router, now=200)
    policy = LoadSheathPolicy(
        window_id=d("window-1"),
        catalog_digest=catalog.catalog_digest,
        budgets=(
            ServiceLoadBudget(GardenServiceClass.SEED_GATE, 100, 4, reserve_units=10, protected=True),
            ServiceLoadBudget(GardenServiceClass.HEAD_WATCH, 100, 4, reserve_units=10, protected=True),
            ServiceLoadBudget(GardenServiceClass.WITNESS_QUERY, 100, 4, reserve_units=10, protected=True),
        ),
    )
    demands = [
        ServiceDemand(GardenServiceClass.SEED_GATE, "family-a", 20, priority=10),
        ServiceDemand(GardenServiceClass.HEAD_WATCH, "family-b", 20, priority=10),
        ServiceDemand(GardenServiceClass.WITNESS_QUERY, "family-c", 120, priority=1),
    ]
    report = assess_load_sheath(policy, demands, catalog=catalog, catalog_report=catalog_report)
    assert report.decision_kind is LoadSheathDecisionKind.ACCEPT_WITH_USEFUL_REFUSALS
    assert report.accept
    assert len(report.accepted_digests) == 2
    assert len(report.refused_digests) == 1


def test_loadsheath_rejects_catalog_mismatch_starvation_refusal_loop_and_metadata_overflow() -> None:
    profile, start, router = accepted_start()
    catalog = service_catalog(profile, start, router)
    catalog_report = assess_service_catalog(catalog, profile=profile, start_report=start, router_report=router, now=200)
    policy = LoadSheathPolicy(
        window_id=d("window-2"),
        catalog_digest=catalog.catalog_digest,
        budgets=(
            ServiceLoadBudget(GardenServiceClass.SEED_GATE, 10, 1, protected=True, max_refusals_per_window=2),
            ServiceLoadBudget(GardenServiceClass.HEAD_WATCH, 10, 1, protected=True, max_refusals_per_window=2),
            ServiceLoadBudget(GardenServiceClass.WITNESS_QUERY, 10, 1, protected=True, max_refusals_per_window=2),
        ),
        max_raw_key_exposures=0,
    )
    assert assess_load_sheath(replace(policy, catalog_digest=d("other-catalog")), (), catalog=catalog, catalog_report=catalog_report).decision_kind is LoadSheathDecisionKind.QUARANTINE_CATALOG_DIGEST_MISMATCH
    assert assess_load_sheath(policy, (), catalog=catalog, catalog_report=catalog_report).decision_kind is LoadSheathDecisionKind.HOLD_PROTECTED_STARVATION
    overflow = [ServiceDemand(GardenServiceClass.SEED_GATE, f"family-{i}", 99, priority=1) for i in range(5)]
    assert assess_load_sheath(policy, overflow, catalog=catalog, catalog_report=catalog_report).decision_kind is LoadSheathDecisionKind.HOLD_REFUSAL_ONLY_LOOP
    leak = [ServiceDemand(GardenServiceClass.SEED_GATE, "family-a", 1, priority=10, raw_key_exposures=1)]
    assert assess_load_sheath(policy, leak, catalog=catalog, catalog_report=catalog_report).decision_kind is LoadSheathDecisionKind.QUARANTINE_BUDGET_OVERFLOW
    assert assess_load_sheath(policy, leak, catalog=catalog, catalog_report=catalog_report, previously_seen_windows=(policy.window_id,)).decision_kind is LoadSheathDecisionKind.QUARANTINE_REPLAYED_WINDOW


def item(kind: ProfileMemoryKind, profile: bytes, obj: bytes, *, generation: int = 3, issued: int = 10, expires: int = 100, byte_cost: int = 10, pinned: bool = False) -> ProfileMemoryItem:
    return ProfileMemoryItem(kind, d("scope"), obj, profile, generation, issued, expires, byte_cost=byte_cost, pinned=pinned)


def test_profilegc_preserves_hard_negatives_and_compacts_soft_memory() -> None:
    profile = d("active-profile")
    router = d("active-router")
    policy = ProfileGcPolicy(profile, router, current_generation=3, max_soft_bytes=20)
    active = item(ProfileMemoryKind.ACTIVE_PROFILE, profile, profile)
    router_item = item(ProfileMemoryKind.ROUTER_CONFIG, profile, router)
    tombstone = item(ProfileMemoryKind.TOMBSTONE, profile, d("tombstone"), byte_cost=999)
    soft_a = item(ProfileMemoryKind.TELEMETRY_SOFT, profile, d("soft-a"), byte_cost=15)
    soft_b = item(ProfileMemoryKind.PEERBOOK_SOFT, profile, d("soft-b"), byte_cost=15)
    report = plan_profile_gc((active, router_item, tombstone, soft_a, soft_b), policy=policy, now=20)
    assert report.decision_kind is ProfileGcDecisionKind.ACCEPT_WITH_COMPACTION
    assert tombstone.digest in report.kept_digests
    assert len(report.gc_candidate_digests) == 1


def test_profilegc_rejects_active_router_hard_negative_and_generation_failures() -> None:
    profile = d("active-profile")
    router = d("active-router")
    policy = ProfileGcPolicy(profile, router, current_generation=3)
    active = item(ProfileMemoryKind.ACTIVE_PROFILE, profile, profile)
    router_item = item(ProfileMemoryKind.ROUTER_CONFIG, profile, router)
    tombstone = item(ProfileMemoryKind.TOMBSTONE, profile, d("tombstone"))
    assert plan_profile_gc((router_item, tombstone), policy=policy, now=20).decision_kind is ProfileGcDecisionKind.QUARANTINE_ACTIVE_PROFILE_DROP
    assert plan_profile_gc((active, tombstone), policy=policy, now=20).decision_kind is ProfileGcDecisionKind.QUARANTINE_ROUTER_CONFIG_DROP
    future = item(ProfileMemoryKind.TELEMETRY_SOFT, profile, d("future"), generation=4)
    assert plan_profile_gc((active, router_item, future), policy=policy, now=20).decision_kind is ProfileGcDecisionKind.QUARANTINE_GENERATION_ROLLBACK
    digest = sha256(b"different-generation")
    assert plan_profile_gc((active, router_item, tombstone), policy=policy, now=20, previous_generation_digest=digest).decision_kind is ProfileGcDecisionKind.QUARANTINE_GENERATION_FORK
    change_policy = ProfileGcPolicy(profile, d("new-router"), current_generation=3, allow_config_change_gc=True)
    assert plan_profile_gc((active, router_item, tombstone), policy=change_policy, now=20).decision_kind is ProfileGcDecisionKind.HOLD_CONFIG_CHANGE_REQUIRES_MIGRATION


def test_servicefold_and_registry_audit_current_revision() -> None:
    registry = audit_fold_registry(".", revision="rev0036")
    assert registry.status == "pass"
    assert registry.error_count == 0
    report = audit_service_fold(".", revision="rev0036", artifact_stem="Nicotine-i2pDHT-rev0036-2026.06.04.03.36-servicecatalog-loadsheath-profilegc")
    assert report.status == "pass"
    assert report.error_count == 0
