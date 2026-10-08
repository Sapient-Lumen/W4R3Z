from __future__ import annotations

from dataclasses import replace

from i2p_dht_lab.ids import sha256
from i2p_dht_lab.identity import DhtKeypair
from i2p_dht_lab.ingressgate import IngressGateDecisionKind, IngressPolicy, IngressRequest, assess_ingress_window
from i2p_dht_lab.launchquorum import LaunchIntent, LaunchMode, assess_launch_quorum
from i2p_dht_lab.loadsheath import LoadSheathPolicy, ServiceLoadBudget
from i2p_dht_lab.routerharness import RouterHarnessConfig, RouterHarnessMode, assess_router_harness
from i2p_dht_lab.safestart import SafeStartDecisionKind, SafeStartReport
from i2p_dht_lab.samprobe import SamProbeProfile, build_sam_probe_plan, classify_sam_probe_transcript
from i2p_dht_lab.serviceannounce import (
    AnnouncementPolicy,
    AnnouncementVisibility,
    ServiceAnnouncementDecisionKind,
    ServiceAnnouncementCapsule,
    assess_service_announcement,
)
from i2p_dht_lab.servicecatalog import (
    GardenServiceClass,
    ServiceCatalogCapsule,
    ServiceDescriptor,
    assess_service_catalog,
)
from i2p_dht_lab.serviceguardfold import audit_serviceguard_fold
from i2p_dht_lab.startmatrix import StartProfile, assess_start_matrix
from i2p_dht_lab.persistjoin import PersistJoinDecisionKind, PersistJoinReport


def d(label: str) -> bytes:
    return sha256(("rev0037:" + label).encode("utf-8"))


def keypair(label: str = "garden") -> DhtKeypair:
    return DhtKeypair.from_seed(d("seed:" + label))


def sam_report():
    profile = SamProbeProfile()
    commands = build_sam_probe_plan(profile, remote_destination="example.b32.i2p")
    replies = [
        "HELLO REPLY RESULT=OK VERSION=3.3",
        "DEST REPLY RESULT=OK PUB=abc PRIV=def",
        "SESSION STATUS RESULT=OK",
        "NAMING REPLY RESULT=OK NAME=example.b32.i2p VALUE=dest",
        "STREAM STATUS RESULT=OK",
    ]
    return classify_sam_probe_transcript(profile, commands, replies)


def safe_start(*, intent: bytes) -> SafeStartReport:
    return SafeStartReport(
        decision_kind=SafeStartDecisionKind.ACCEPT_SAFE_START,
        accept=True,
        reason="safe",
        intent_digest=intent,
        negotiation_report_digest=d("negotiation"),
        migration_report_digest=d("migration"),
        samtrace_report_digest=d("samtrace"),
        pressure_digests=(),
        report_digest=d("safe-start"),
    )


def persist_join() -> PersistJoinReport:
    return PersistJoinReport(
        decision_kind=PersistJoinDecisionKind.ACCEPT_DURABLE_JOIN,
        accept=True,
        reason="durable",
        persist_report_digest=d("persist"),
        journal_report_digest=d("journal"),
        checkpoint_report_digest=d("checkpoint-report"),
        scope_report_digest=d("scope"),
        store_report_digest=d("store"),
        checkpoint_digest=d("checkpoint"),
        journal_tip_digest=d("tip"),
        pressure_digests=(),
        hard_negative_count=2,
        report_digest=d("persist-join"),
    )


def accepted_start(mode: LaunchMode = LaunchMode.GARDEN, *, services: int = 3, public_bridge: bool = False, metadata: str = "power"):
    sam = sam_report()
    intent = LaunchIntent(mode=mode, intent_digest=d("intent:" + mode.value), endpoint_digest=sam.endpoint_digest, generation=11, require_streaming_probe=True)
    launch = assess_launch_quorum(intent, safe_start=safe_start(intent=intent.intent_digest), persist_join=persist_join(), sam_probe=sam)
    router_config = RouterHarnessConfig(
        mode=RouterHarnessMode.BUNDLED_I2PD,
        datadir_digest=d("datadir"),
        destination_digest=d("destination"),
        generated_config_digest=d("config"),
        expected_config_digest=d("config"),
    )
    router = assess_router_harness(router_config, sam)
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


def service_catalog(profile: StartProfile, start, router, *, services=None, kp=None, sequence: int = 1):
    kp = kp or keypair()
    services = tuple(services or (
        ServiceDescriptor(GardenServiceClass.SEED_GATE, max_streams=8, max_units=1_000, reserve_units=100, public=True, metadata_cost="low"),
        ServiceDescriptor(GardenServiceClass.HEAD_WATCH, max_streams=8, max_units=400, reserve_units=80, public=False),
        ServiceDescriptor(GardenServiceClass.WITNESS_QUERY, max_streams=8, max_units=800, reserve_units=100, public=True),
    ))
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


def accepted_catalog():
    profile, start, router = accepted_start()
    catalog = service_catalog(profile, start, router)
    report = assess_service_catalog(catalog, profile=profile, start_report=start, router_report=router, now=200)
    assert report.accept, report
    return profile, catalog, report


def announcement(profile, catalog, catalog_report, *, visibility=AnnouncementVisibility.PUBLIC, services=None, kp=None, sequence=1, hint_count=1):
    return ServiceAnnouncementCapsule.create(
        keypair=kp or keypair(),
        issuer_node_id=d("node"),
        sequence=sequence,
        issued_at=150,
        expires_at=600,
        visibility=visibility,
        catalog=catalog,
        catalog_report=catalog_report,
        profile=profile,
        services=tuple(services or (GardenServiceClass.SEED_GATE, GardenServiceClass.WITNESS_QUERY)),
        label_hashes=(d("redacted-label"),),
        hint_count=hint_count,
    )


def accepted_announcement():
    profile, catalog, catalog_report = accepted_catalog()
    ann = announcement(profile, catalog, catalog_report)
    ann_report = assess_service_announcement(ann, catalog=catalog, catalog_report=catalog_report, profile=profile, now=200)
    assert ann_report.accept, ann_report
    return profile, catalog, catalog_report, ann, ann_report


def load_policy(catalog) -> LoadSheathPolicy:
    return LoadSheathPolicy(
        window_id=d("load-window"),
        catalog_digest=catalog.catalog_digest,
        budgets=(
            ServiceLoadBudget(GardenServiceClass.SEED_GATE, 100, 4, reserve_units=10, protected=True),
            ServiceLoadBudget(GardenServiceClass.WITNESS_QUERY, 60, 2, reserve_units=10, protected=True),
            ServiceLoadBudget(GardenServiceClass.HEAD_WATCH, 40, 2, reserve_units=10, protected=True),
        ),
        max_raw_key_exposures=1,
        min_protected_accepts=1,
    )


def req(label: str, service: GardenServiceClass = GardenServiceClass.SEED_GATE, *, units: int = 20, priority: int = 5, raw: int = 0, requester: str = "req-a", path: str = "path-a") -> IngressRequest:
    return IngressRequest(
        service=service,
        request_id=d("request:" + label),
        requester_family=requester,
        path_family=path,
        scope_digest=d("scope"),
        object_digest=d("object:" + label),
        units=units,
        priority=priority,
        raw_key_exposures=raw,
        issued_at=150,
        expires_at=300,
    )


def test_serviceannouncement_accepts_redacted_public_subset_and_private_hidden_service() -> None:
    profile, catalog, catalog_report = accepted_catalog()
    ann = announcement(profile, catalog, catalog_report)
    report = assess_service_announcement(ann, catalog=catalog, catalog_report=catalog_report, profile=profile, now=200)
    assert report.decision_kind is ServiceAnnouncementDecisionKind.ACCEPT_PUBLIC_ANNOUNCEMENT
    assert report.visible_services == ("seed_gate", "witness_query")

    private = announcement(profile, catalog, catalog_report, visibility=AnnouncementVisibility.FRIEND, services=(GardenServiceClass.HEAD_WATCH,))
    private_report = assess_service_announcement(private, catalog=catalog, catalog_report=catalog_report, profile=profile, now=200)
    assert private_report.decision_kind is ServiceAnnouncementDecisionKind.ACCEPT_PRIVATE_ANNOUNCEMENT


def test_serviceannouncement_rejects_public_hidden_bridge_signature_replay_and_rollbacks() -> None:
    profile, catalog, catalog_report = accepted_catalog()
    hidden = announcement(profile, catalog, catalog_report, services=(GardenServiceClass.HEAD_WATCH,))
    assert assess_service_announcement(hidden, catalog=catalog, catalog_report=catalog_report, profile=profile, now=200).decision_kind is ServiceAnnouncementDecisionKind.QUARANTINE_PUBLIC_HIDDEN_SERVICE

    bridge_profile, start, router = accepted_start(LaunchMode.BRIDGE, services=2, public_bridge=True)
    bridge_catalog = service_catalog(bridge_profile, start, router, services=(
        ServiceDescriptor(GardenServiceClass.SEED_GATE, 8, 1_000, public=True),
        ServiceDescriptor(GardenServiceClass.BRIDGE_GATEWAY, 8, 1_000, public=True),
    ))
    bridge_report = assess_service_catalog(bridge_catalog, profile=bridge_profile, start_report=start, router_report=router, now=200)
    bridge_ann = announcement(bridge_profile, bridge_catalog, bridge_report, services=(GardenServiceClass.BRIDGE_GATEWAY,))
    assert assess_service_announcement(bridge_ann, catalog=bridge_catalog, catalog_report=bridge_report, profile=bridge_profile, now=200).decision_kind is ServiceAnnouncementDecisionKind.QUARANTINE_PUBLIC_BRIDGE_EXPOSURE
    assert assess_service_announcement(bridge_ann, catalog=bridge_catalog, catalog_report=bridge_report, profile=bridge_profile, now=200, policy=AnnouncementPolicy(allow_public_bridge=True)).accept

    tampered = replace(bridge_ann, signature=b"x" * 64)
    assert assess_service_announcement(tampered, catalog=bridge_catalog, catalog_report=bridge_report, profile=bridge_profile, now=200, policy=AnnouncementPolicy(allow_public_bridge=True)).decision_kind is ServiceAnnouncementDecisionKind.QUARANTINE_BAD_SIGNATURE
    assert assess_service_announcement(bridge_ann, catalog=bridge_catalog, catalog_report=bridge_report, profile=bridge_profile, now=200, policy=AnnouncementPolicy(allow_public_bridge=True), previously_seen_announcements=(bridge_ann.announcement_digest,)).decision_kind is ServiceAnnouncementDecisionKind.QUARANTINE_REPLAY
    assert assess_service_announcement(bridge_ann, catalog=bridge_catalog, catalog_report=bridge_report, profile=bridge_profile, now=200, policy=AnnouncementPolicy(allow_public_bridge=True), highest_seen_sequence=9).decision_kind is ServiceAnnouncementDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK
    fork = announcement(bridge_profile, bridge_catalog, bridge_report, services=(GardenServiceClass.SEED_GATE,), sequence=1)
    assert assess_service_announcement(fork, catalog=bridge_catalog, catalog_report=bridge_report, profile=bridge_profile, now=200, highest_seen_sequence=1, same_sequence_digest=bridge_ann.announcement_digest).decision_kind is ServiceAnnouncementDecisionKind.QUARANTINE_SEQUENCE_FORK


def test_serviceannouncement_rejects_binding_ttl_unknown_service_and_metadata_exposure() -> None:
    profile, catalog, catalog_report = accepted_catalog()
    ann = announcement(profile, catalog, catalog_report)
    wrong_profile, _, _ = accepted_start(metadata="power")
    wrong_profile = StartProfile("wrong", wrong_profile.mode, wrong_profile.router_mode, wrong_profile.bound_launch_intent_digest, garden_service_count=3, metadata_budget_level="power")
    assert assess_service_announcement(ann, catalog=catalog, catalog_report=catalog_report, profile=wrong_profile, now=200).decision_kind is ServiceAnnouncementDecisionKind.QUARANTINE_BINDING_MISMATCH

    long_ttl = ServiceAnnouncementCapsule.create(keypair=keypair(), issuer_node_id=d("node"), sequence=2, issued_at=1, expires_at=10_000, visibility=AnnouncementVisibility.PUBLIC, catalog=catalog, catalog_report=catalog_report, profile=profile, services=(GardenServiceClass.SEED_GATE,))
    assert assess_service_announcement(long_ttl, catalog=catalog, catalog_report=catalog_report, profile=profile, now=200).decision_kind is ServiceAnnouncementDecisionKind.QUARANTINE_TTL_EXCESS
    expired = ServiceAnnouncementCapsule.create(keypair=keypair(), issuer_node_id=d("node"), sequence=3, issued_at=1, expires_at=10, visibility=AnnouncementVisibility.PUBLIC, catalog=catalog, catalog_report=catalog_report, profile=profile, services=(GardenServiceClass.SEED_GATE,))
    assert assess_service_announcement(expired, catalog=catalog, catalog_report=catalog_report, profile=profile, now=200).decision_kind is ServiceAnnouncementDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE

    unknown = announcement(profile, catalog, catalog_report, services=(GardenServiceClass.REGION_REPROVIDE,))
    assert assess_service_announcement(unknown, catalog=catalog, catalog_report=catalog_report, profile=profile, now=200).decision_kind is ServiceAnnouncementDecisionKind.QUARANTINE_UNKNOWN_SERVICE
    noisy = announcement(profile, catalog, catalog_report, hint_count=999)
    assert assess_service_announcement(noisy, catalog=catalog, catalog_report=catalog_report, profile=profile, now=200).decision_kind is ServiceAnnouncementDecisionKind.HOLD_METADATA_OVEREXPOSURE


def test_ingressgate_accepts_catalog_bound_announced_requests_and_refuses_overflow() -> None:
    _profile, catalog, catalog_report, ann, ann_report = accepted_announcement()
    lp = load_policy(catalog)
    policy = IngressPolicy(
        window_id=d("ingress-window"),
        catalog_digest=catalog.catalog_digest,
        announcement_digest=ann.announcement_digest,
        allowed_services=(GardenServiceClass.SEED_GATE, GardenServiceClass.WITNESS_QUERY),
        max_raw_key_exposures=1,
    )
    requests = (
        req("a", GardenServiceClass.SEED_GATE, units=20, priority=10, requester="req-a", path="path-a"),
        req("b", GardenServiceClass.WITNESS_QUERY, units=80, priority=1, requester="req-b", path="path-b"),
    )
    report = assess_ingress_window(requests, policy=policy, catalog=catalog, catalog_report=catalog_report, load_policy=lp, announcement=ann, announcement_report=ann_report, now=200)
    assert report.decision_kind is IngressGateDecisionKind.ACCEPT_WITH_USEFUL_REFUSALS
    assert len(report.accepted_request_digests) == 1
    assert len(report.refused_request_digests) == 1


def test_ingressgate_rejects_missing_announcement_binding_replay_unadvertised_and_metadata() -> None:
    _profile, catalog, catalog_report, ann, ann_report = accepted_announcement()
    lp = load_policy(catalog)
    policy = IngressPolicy(d("ingress-window-2"), catalog.catalog_digest, ann.announcement_digest, allowed_services=(GardenServiceClass.SEED_GATE,), max_raw_key_exposures=0)
    good = req("good", GardenServiceClass.SEED_GATE)
    assert assess_ingress_window((good,), policy=policy, catalog=catalog, catalog_report=catalog_report, load_policy=lp, now=200).decision_kind is IngressGateDecisionKind.QUARANTINE_ANNOUNCEMENT
    drift = replace(policy, announcement_digest=d("wrong-ann"))
    assert assess_ingress_window((good,), policy=drift, catalog=catalog, catalog_report=catalog_report, load_policy=lp, announcement=ann, announcement_report=ann_report, now=200).decision_kind is IngressGateDecisionKind.QUARANTINE_BINDING_MISMATCH
    assert assess_ingress_window((good,), policy=policy, catalog=catalog, catalog_report=catalog_report, load_policy=lp, announcement=ann, announcement_report=ann_report, now=200, previously_seen_request_ids=(good.request_id,)).decision_kind is IngressGateDecisionKind.QUARANTINE_REPLAYED_REQUEST
    hidden_request = req("hidden", GardenServiceClass.HEAD_WATCH)
    assert assess_ingress_window((hidden_request,), policy=policy, catalog=catalog, catalog_report=catalog_report, load_policy=lp, announcement=ann, announcement_report=ann_report, now=200).decision_kind is IngressGateDecisionKind.QUARANTINE_UNADVERTISED_SERVICE
    raw = req("raw", GardenServiceClass.SEED_GATE, raw=1)
    assert assess_ingress_window((raw,), policy=policy, catalog=catalog, catalog_report=catalog_report, load_policy=lp, announcement=ann, announcement_report=ann_report, now=200).decision_kind is IngressGateDecisionKind.QUARANTINE_METADATA_BUDGET


def test_ingressgate_holds_family_flood_and_load_sheath_starvation() -> None:
    _profile, catalog, catalog_report, ann, ann_report = accepted_announcement()
    lp = load_policy(catalog)
    policy = IngressPolicy(d("ingress-window-3"), catalog.catalog_digest, ann.announcement_digest, allowed_services=(GardenServiceClass.SEED_GATE,), max_requests_per_requester_family=1)
    flood = (req("f1", GardenServiceClass.SEED_GATE, requester="same"), req("f2", GardenServiceClass.SEED_GATE, requester="same"))
    assert assess_ingress_window(flood, policy=policy, catalog=catalog, catalog_report=catalog_report, load_policy=lp, announcement=ann, announcement_report=ann_report, now=200).decision_kind is IngressGateDecisionKind.HOLD_FAMILY_FLOOD

    starve_lp = LoadSheathPolicy(d("starve-window"), catalog.catalog_digest, budgets=(
        ServiceLoadBudget(GardenServiceClass.SEED_GATE, 0, 0, protected=True),
        ServiceLoadBudget(GardenServiceClass.WITNESS_QUERY, 60, 2, reserve_units=10, protected=True),
        ServiceLoadBudget(GardenServiceClass.HEAD_WATCH, 40, 2, reserve_units=10, protected=True),
    ), min_protected_accepts=1)
    assert assess_ingress_window((req("s1", GardenServiceClass.SEED_GATE),), policy=replace(policy, max_requests_per_requester_family=8), catalog=catalog, catalog_report=catalog_report, load_policy=starve_lp, announcement=ann, announcement_report=ann_report, now=200).decision_kind is IngressGateDecisionKind.HOLD_LOAD_SHEATH


def test_serviceguard_fold_audit_passes_for_current_revision() -> None:
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    report = audit_serviceguard_fold(root, revision="rev0037", artifact_stem=root.name)
    assert report.status == "pass", report.findings
    assert report.registry_status == "pass"
    assert report.predecessor_status == "pass"
