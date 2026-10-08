from __future__ import annotations

from dataclasses import replace

from i2p_dht_lab.foldregistry import audit_fold_registry
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.identity import DhtKeypair
from i2p_dht_lab.launchquorum import LaunchIntent, LaunchMode, assess_launch_quorum
from i2p_dht_lab.loadsheath import LoadSheathPolicy, ServiceDemand, ServiceLoadBudget, assess_load_sheath
from i2p_dht_lab.persistjoin import PersistJoinDecisionKind, PersistJoinReport
from i2p_dht_lab.routerharness import RouterHarnessConfig, RouterHarnessMode, assess_router_harness
from i2p_dht_lab.safestart import SafeStartDecisionKind, SafeStartReport
from i2p_dht_lab.samprobe import SamProbeProfile, build_sam_probe_plan, classify_sam_probe_transcript
from i2p_dht_lab.servicecatalog import (
    GardenServiceClass,
    ServiceCatalogCapsule,
    ServiceDescriptor,
    assess_service_catalog,
)
from i2p_dht_lab.servicereceipt import (
    ServiceReceiptCapsule,
    ServiceReceiptDecisionKind,
    ServiceReceiptResultKind,
    assess_service_receipt,
)
from i2p_dht_lab.serviceticket import (
    ServiceTicketCapsule,
    ServiceTicketDecisionKind,
    ServiceTicketRequest,
    assess_service_ticket,
)
from i2p_dht_lab.startmatrix import StartProfile, assess_start_matrix
from i2p_dht_lab.ticketfold import audit_ticket_fold


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
        reason="accept",
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
        reason="accept",
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


def accepted_service_stack():
    kp = keypair()
    sam = sam_report()
    intent = LaunchIntent(mode=LaunchMode.GARDEN, intent_digest=d("intent"), endpoint_digest=sam.endpoint_digest, generation=37, require_streaming_probe=True)
    launch = assess_launch_quorum(intent, safe_start=safe_start(intent=intent.intent_digest), persist_join=persist_join(), sam_probe=sam)
    router = assess_router_harness(RouterHarnessConfig(
        mode=RouterHarnessMode.BUNDLED_I2PD,
        datadir_digest=d("datadir"),
        destination_digest=d("destination"),
        generated_config_digest=d("config"),
        expected_config_digest=d("config"),
    ), sam)
    profile = StartProfile("profile-garden", LaunchMode.GARDEN, RouterHarnessMode.BUNDLED_I2PD, intent.launch_intent_digest, garden_service_count=2, metadata_budget_level="power")
    start = assess_start_matrix(profile, launch=launch, router=router)
    assert start.accept
    catalog = ServiceCatalogCapsule.create(
        keypair=kp,
        issuer_node_id=d("garden-node"),
        sequence=1,
        issued_at=100,
        expires_at=1_000,
        profile=profile,
        start_report=start,
        router_report=router,
        services=(
            ServiceDescriptor(GardenServiceClass.SEED_GATE, max_streams=8, max_units=1_000, reserve_units=100, public=True),
            ServiceDescriptor(GardenServiceClass.WITNESS_QUERY, max_streams=4, max_units=300, reserve_units=60),
        ),
    )
    catalog_report = assess_service_catalog(catalog, profile=profile, start_report=start, router_report=router, now=200)
    assert catalog_report.accept
    demand = ServiceDemand(GardenServiceClass.SEED_GATE, "caller-family-a", 32, stream_cost=1, priority=10, raw_key_exposures=1)
    load_policy = LoadSheathPolicy(
        window_id=d("load-window"),
        catalog_digest=catalog.catalog_digest,
        budgets=(
            ServiceLoadBudget(GardenServiceClass.SEED_GATE, 64, 4, reserve_units=8, protected=True),
            ServiceLoadBudget(GardenServiceClass.WITNESS_QUERY, 64, 4, reserve_units=8, protected=True),
        ),
        max_raw_key_exposures=3,
        min_protected_accepts=1,
    )
    load_report = assess_load_sheath(load_policy, (demand,), catalog=catalog, catalog_report=catalog_report)
    assert load_report.accept
    request = ServiceTicketRequest.from_demand(
        demand,
        caller_node_id=d("caller-node"),
        scope_digest=d("scope"),
        object_digest=d("object"),
        request_digest=d("request"),
    )
    ticket = ServiceTicketCapsule.create(
        keypair=kp,
        issuer_node_id=d("garden-node"),
        sequence=1,
        issued_at=210,
        expires_at=400,
        catalog=catalog,
        catalog_report=catalog_report,
        load_report=load_report,
        request=request,
    )
    return kp, catalog, catalog_report, load_report, request, ticket


def test_service_ticket_accepts_exact_scope_ticket() -> None:
    _, catalog, catalog_report, load_report, request, ticket = accepted_service_stack()
    report = assess_service_ticket(ticket, request=request, catalog=catalog, catalog_report=catalog_report, load_report=load_report, now=220)
    assert report.decision_kind is ServiceTicketDecisionKind.ACCEPT_SERVICE_TICKET
    assert report.accept
    assert report.request_capsule_digest == request.request_capsule_digest


def test_service_ticket_rejects_replay_time_signature_sequence_and_scope_drift() -> None:
    kp, catalog, catalog_report, load_report, request, ticket = accepted_service_stack()
    assert assess_service_ticket(ticket, request=request, catalog=catalog, catalog_report=catalog_report, load_report=load_report, now=220, previously_seen_tickets=(ticket.ticket_digest,)).decision_kind is ServiceTicketDecisionKind.QUARANTINE_REPLAY
    expired = ServiceTicketCapsule.create(keypair=kp, issuer_node_id=d("garden-node"), sequence=2, issued_at=1, expires_at=10, catalog=catalog, catalog_report=catalog_report, load_report=load_report, request=request)
    assert assess_service_ticket(expired, request=request, catalog=catalog, catalog_report=catalog_report, load_report=load_report, now=220).decision_kind is ServiceTicketDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE
    bad_sig = replace(ticket, signature=b"x" * 64)
    assert assess_service_ticket(bad_sig, request=request, catalog=catalog, catalog_report=catalog_report, load_report=load_report, now=220).decision_kind is ServiceTicketDecisionKind.QUARANTINE_BAD_SIGNATURE
    assert assess_service_ticket(ticket, request=request, catalog=catalog, catalog_report=catalog_report, load_report=load_report, now=220, highest_seen_sequence=7).decision_kind is ServiceTicketDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK
    fork = ServiceTicketCapsule.create(keypair=kp, issuer_node_id=d("garden-node"), sequence=1, issued_at=210, expires_at=400, catalog=catalog, catalog_report=catalog_report, load_report=load_report, request=request, granted_units=16)
    assert assess_service_ticket(fork, request=request, catalog=catalog, catalog_report=catalog_report, load_report=load_report, now=220, highest_seen_sequence=1, same_sequence_digest=ticket.ticket_digest).decision_kind is ServiceTicketDecisionKind.QUARANTINE_SEQUENCE_FORK
    wrong_scope = replace(request, scope_digest=d("other-scope"))
    assert assess_service_ticket(ticket, request=wrong_scope, catalog=catalog, catalog_report=catalog_report, load_report=load_report, now=220).decision_kind is ServiceTicketDecisionKind.QUARANTINE_CALLER_MISMATCH


def test_service_ticket_rejects_unscheduled_service_and_budget_overclaim() -> None:
    kp, catalog, catalog_report, load_report, request, ticket = accepted_service_stack()
    unscheduled_request = replace(request, demand_digest=d("not-scheduled"))
    unscheduled_ticket = ServiceTicketCapsule.create(keypair=kp, issuer_node_id=d("garden-node"), sequence=3, issued_at=210, expires_at=400, catalog=catalog, catalog_report=catalog_report, load_report=load_report, request=unscheduled_request)
    assert assess_service_ticket(unscheduled_ticket, request=unscheduled_request, catalog=catalog, catalog_report=catalog_report, load_report=load_report, now=220).decision_kind is ServiceTicketDecisionKind.HOLD_DEMAND_NOT_SCHEDULED
    overclaim = ServiceTicketCapsule.create(keypair=kp, issuer_node_id=d("garden-node"), sequence=4, issued_at=210, expires_at=400, catalog=catalog, catalog_report=catalog_report, load_report=load_report, request=request, granted_units=request.requested_units + 1)
    assert assess_service_ticket(overclaim, request=request, catalog=catalog, catalog_report=catalog_report, load_report=load_report, now=220).decision_kind is ServiceTicketDecisionKind.QUARANTINE_BUDGET_OVERCLAIM


def accepted_ticket_report():
    kp, catalog, catalog_report, load_report, request, ticket = accepted_service_stack()
    ticket_report = assess_service_ticket(ticket, request=request, catalog=catalog, catalog_report=catalog_report, load_report=load_report, now=220)
    assert ticket_report.accept
    return kp, ticket, ticket_report


def test_service_receipt_accepts_completion_refusal_and_partial_shapes() -> None:
    kp, ticket, ticket_report = accepted_ticket_report()
    complete = ServiceReceiptCapsule.create(keypair=kp, issuer_node_id=d("garden-node"), sequence=1, issued_at=230, expires_at=500, ticket=ticket, ticket_report=ticket_report, result_kind=ServiceReceiptResultKind.COMPLETED, completed_units=32, refused_units=0, evidence_digest=d("complete-evidence"))
    assert assess_service_receipt(complete, ticket=ticket, ticket_report=ticket_report, now=240).decision_kind is ServiceReceiptDecisionKind.ACCEPT_SERVICE_COMPLETION
    refusal = ServiceReceiptCapsule.create(keypair=kp, issuer_node_id=d("garden-node"), sequence=2, issued_at=230, expires_at=500, ticket=ticket, ticket_report=ticket_report, result_kind=ServiceReceiptResultKind.USEFUL_REFUSAL, completed_units=0, refused_units=12, evidence_digest=d("refusal-evidence"))
    assert assess_service_receipt(refusal, ticket=ticket, ticket_report=ticket_report, now=240).decision_kind is ServiceReceiptDecisionKind.ACCEPT_USEFUL_REFUSAL
    partial = ServiceReceiptCapsule.create(keypair=kp, issuer_node_id=d("garden-node"), sequence=3, issued_at=230, expires_at=500, ticket=ticket, ticket_report=ticket_report, result_kind=ServiceReceiptResultKind.PARTIAL, completed_units=12, refused_units=8, evidence_digest=d("partial-evidence"))
    assert assess_service_receipt(partial, ticket=ticket, ticket_report=ticket_report, now=240).decision_kind is ServiceReceiptDecisionKind.ACCEPT_PARTIAL_RESULT


def test_service_receipt_rejects_replay_overclaim_bad_shape_and_binding_drift() -> None:
    kp, ticket, ticket_report = accepted_ticket_report()
    receipt = ServiceReceiptCapsule.create(keypair=kp, issuer_node_id=d("garden-node"), sequence=1, issued_at=230, expires_at=500, ticket=ticket, ticket_report=ticket_report, result_kind=ServiceReceiptResultKind.COMPLETED, completed_units=32, refused_units=0)
    assert assess_service_receipt(receipt, ticket=ticket, ticket_report=ticket_report, now=240, previously_seen_receipts=(receipt.receipt_digest,)).decision_kind is ServiceReceiptDecisionKind.QUARANTINE_REPLAY
    overclaim = ServiceReceiptCapsule.create(keypair=kp, issuer_node_id=d("garden-node"), sequence=2, issued_at=230, expires_at=500, ticket=ticket, ticket_report=ticket_report, result_kind=ServiceReceiptResultKind.COMPLETED, completed_units=33, refused_units=0)
    assert assess_service_receipt(overclaim, ticket=ticket, ticket_report=ticket_report, now=240).decision_kind is ServiceReceiptDecisionKind.QUARANTINE_UNITS_OVERCLAIM
    bad_shape = ServiceReceiptCapsule.create(keypair=kp, issuer_node_id=d("garden-node"), sequence=3, issued_at=230, expires_at=500, ticket=ticket, ticket_report=ticket_report, result_kind=ServiceReceiptResultKind.COMPLETED, completed_units=20, refused_units=1)
    assert assess_service_receipt(bad_shape, ticket=ticket, ticket_report=ticket_report, now=240).decision_kind is ServiceReceiptDecisionKind.QUARANTINE_RESULT_SHAPE
    drift = replace(receipt, request_digest=d("wrong-request"), signature=receipt.signature)
    assert assess_service_receipt(drift, ticket=ticket, ticket_report=ticket_report, now=240).decision_kind is ServiceReceiptDecisionKind.QUARANTINE_BAD_SIGNATURE
    drift_signed = ServiceReceiptCapsule.create(keypair=kp, issuer_node_id=d("garden-node"), sequence=4, issued_at=230, expires_at=500, ticket=ticket, ticket_report=ticket_report, result_kind=ServiceReceiptResultKind.COMPLETED, completed_units=32, refused_units=0)
    drift_signed = replace(drift_signed, request_digest=d("wrong-request"), signature=keypair().sign(replace(drift_signed, request_digest=d("wrong-request"), signature=b"").unsigned_payload()))
    assert assess_service_receipt(drift_signed, ticket=ticket, ticket_report=ticket_report, now=240).decision_kind is ServiceReceiptDecisionKind.QUARANTINE_BINDING_MISMATCH


def test_service_receipt_refusal_loop_and_sequence_pressure() -> None:
    kp, ticket, ticket_report = accepted_ticket_report()
    refusal = ServiceReceiptCapsule.create(keypair=kp, issuer_node_id=d("garden-node"), sequence=2, issued_at=230, expires_at=500, ticket=ticket, ticket_report=ticket_report, result_kind=ServiceReceiptResultKind.USEFUL_REFUSAL, completed_units=0, refused_units=12)
    recent = (d("old-refusal-1"), d("old-refusal-2"))
    assert assess_service_receipt(refusal, ticket=ticket, ticket_report=ticket_report, now=240, recent_refusal_receipts=recent, max_refusal_only_receipts=2).decision_kind is ServiceReceiptDecisionKind.HOLD_REFUSAL_ONLY_LOOP
    assert assess_service_receipt(refusal, ticket=ticket, ticket_report=ticket_report, now=240, highest_seen_sequence=9).decision_kind is ServiceReceiptDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK
    fork = ServiceReceiptCapsule.create(keypair=kp, issuer_node_id=d("garden-node"), sequence=2, issued_at=230, expires_at=500, ticket=ticket, ticket_report=ticket_report, result_kind=ServiceReceiptResultKind.USEFUL_REFUSAL, completed_units=0, refused_units=10)
    assert assess_service_receipt(fork, ticket=ticket, ticket_report=ticket_report, now=240, highest_seen_sequence=2, same_sequence_digest=refusal.receipt_digest).decision_kind is ServiceReceiptDecisionKind.QUARANTINE_SEQUENCE_FORK


def test_ticket_fold_and_registry_pin_rev0037_surfaces() -> None:
    root = __import__("pathlib").Path(__file__).resolve().parents[1]
    fold = audit_ticket_fold(root, revision="rev0037", artifact_stem=root.name)
    assert fold.status == "pass", fold.findings
    registry = audit_fold_registry(root, revision="rev0037")
    assert registry.status == "pass", registry.findings
