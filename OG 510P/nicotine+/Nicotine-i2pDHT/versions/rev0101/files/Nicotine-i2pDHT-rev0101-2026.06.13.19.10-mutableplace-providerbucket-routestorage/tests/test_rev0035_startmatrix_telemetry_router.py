from __future__ import annotations

from i2p_dht_lab.evidencegc import EvidenceItem, EvidenceKind, collect_evidence_gc
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.launchquorum import LaunchIntent, LaunchMode, LaunchQuorumDecisionKind, assess_launch_quorum
from i2p_dht_lab.metricsveil import MetricEvent, assess_metric_event
from i2p_dht_lab.persistjoin import PersistJoinDecisionKind, PersistJoinReport
from i2p_dht_lab.routerharness import (
    RouterHarnessConfig,
    RouterHarnessDecisionKind,
    RouterHarnessMode,
    assess_router_harness,
)
from i2p_dht_lab.safestart import SafeStartDecisionKind, SafeStartReport
from i2p_dht_lab.samprobe import (
    SamProbeDecisionKind,
    SamProbeProfile,
    build_sam_probe_plan,
    classify_sam_probe_transcript,
)
from i2p_dht_lab.startfold import audit_start_fold
from i2p_dht_lab.startmatrix import StartMatrixDecisionKind, StartProfile, assess_start_matrix
from i2p_dht_lab.telemetrydebt import (
    TelemetryDebtDecisionKind,
    TelemetryDebtPolicy,
    TelemetryRetentionItem,
    assess_telemetry_debt,
    item_from_metric_assessment,
)


def d(label: str) -> bytes:
    return sha256(("rev0035:" + label).encode("utf-8"))


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


def launch_report(mode: LaunchMode = LaunchMode.LEAF, *, sam=None, allow_no_router: bool = False):
    sam = sam or sam_report()
    intent = LaunchIntent(mode=mode, intent_digest=d("intent"), endpoint_digest=sam.endpoint_digest, generation=5, allow_no_router=allow_no_router, require_streaming_probe=(mode is not LaunchMode.OFFLINE_DESIGN))
    return intent, assess_launch_quorum(intent, safe_start=safe_start(intent=d("intent")), persist_join=persist_join(), sam_probe=sam)


def router_config(mode: RouterHarnessMode = RouterHarnessMode.BUNDLED_I2PD, **overrides):
    base = dict(
        mode=mode,
        datadir_digest=d("datadir"),
        destination_digest=d("destination"),
        generated_config_digest=d("config"),
        expected_config_digest=d("config"),
    )
    base.update(overrides)
    return RouterHarnessConfig(**base)


def test_routerharness_accepts_bundled_and_external_explicit_paths() -> None:
    sam = sam_report()
    bundled = assess_router_harness(router_config(), sam)
    assert bundled.decision_kind is RouterHarnessDecisionKind.ACCEPT_BUNDLED_I2PD_HARNESS
    assert bundled.accept

    external = assess_router_harness(router_config(RouterHarnessMode.EXTERNAL_SAM, host="sam.example", allow_external_endpoint=True), sam_report())
    assert external.decision_kind is RouterHarnessDecisionKind.QUARANTINE_MODE_ENDPOINT_DRIFT

    profile = SamProbeProfile(host="sam.example", allow_external_sam=True)
    commands = build_sam_probe_plan(profile)
    external_sam = classify_sam_probe_transcript(profile, commands, [
        "HELLO REPLY RESULT=OK VERSION=3.3",
        "DEST REPLY RESULT=OK PUB=abc PRIV=def",
        "SESSION STATUS RESULT=OK",
        "NAMING REPLY RESULT=OK NAME=example.b32.i2p VALUE=dest",
        "STREAM STATUS RESULT=OK",
    ])
    external_ok = assess_router_harness(router_config(RouterHarnessMode.EXTERNAL_SAM, host="sam.example", allow_external_endpoint=True), external_sam)
    assert external_ok.decision_kind is RouterHarnessDecisionKind.ACCEPT_EXTERNAL_SAM_HARNESS


def test_routerharness_rejects_ephemeral_proxy_notransit_replay_and_config_drift() -> None:
    sam = sam_report()
    assert assess_router_harness(router_config(destination_digest=b"\x00" * 32), sam).decision_kind is RouterHarnessDecisionKind.QUARANTINE_EPHEMERAL_DESTINATION
    assert assess_router_harness(router_config(http_proxy_disabled=False), sam).decision_kind is RouterHarnessDecisionKind.QUARANTINE_PROXY_EXPOSURE
    assert assess_router_harness(router_config(transit_enabled=False), sam).decision_kind is RouterHarnessDecisionKind.QUARANTINE_NOTRANSIT_BUNDLE
    assert assess_router_harness(router_config(generated_config_digest=d("bad")), sam).decision_kind is RouterHarnessDecisionKind.QUARANTINE_CONFIG_DIGEST_MISMATCH
    assert assess_router_harness(router_config(), sam, previously_seen_reports=(sam.transcript_digest,)).decision_kind is RouterHarnessDecisionKind.QUARANTINE_SAM_PROBE


def test_routerharness_offline_and_session_only_are_explicit_holds() -> None:
    no_router = sam_report(SamProbeDecisionKind.ACCEPT_LOCAL_UNAVAILABLE)
    offline = assess_router_harness(router_config(RouterHarnessMode.OFFLINE_NO_ROUTER, datadir_digest=b"\x00" * 32, destination_digest=b"\x00" * 32), no_router)
    assert offline.decision_kind is RouterHarnessDecisionKind.ACCEPT_OFFLINE_DESIGN_HARNESS

    live_hold = assess_router_harness(router_config(), no_router)
    assert live_hold.decision_kind is RouterHarnessDecisionKind.HOLD_ROUTER_UNAVAILABLE

    session_only = sam_report(SamProbeDecisionKind.ACCEPT_SESSION_ONLY)
    held = assess_router_harness(router_config(), session_only)
    assert held.decision_kind is RouterHarnessDecisionKind.HOLD_SESSION_ONLY
    allowed = assess_router_harness(router_config(allow_session_only=True), session_only)
    assert allowed.decision_kind is RouterHarnessDecisionKind.ACCEPT_BUNDLED_I2PD_HARNESS


def test_startmatrix_accepts_leaf_garden_bridge_and_offline_profiles() -> None:
    intent, launch = launch_report()
    router = assess_router_harness(router_config(), sam_report())
    leaf = StartProfile("leaf-default", LaunchMode.LEAF, RouterHarnessMode.BUNDLED_I2PD, intent.launch_intent_digest)
    assert assess_start_matrix(leaf, launch=launch, router=router).decision_kind is StartMatrixDecisionKind.ACCEPT_LEAF_PROFILE

    garden = StartProfile("garden-giver", LaunchMode.GARDEN, RouterHarnessMode.BUNDLED_I2PD, intent.launch_intent_digest, garden_service_count=3, metadata_budget_level="power")
    assert assess_start_matrix(garden, launch=launch, router=router).decision_kind is StartMatrixDecisionKind.ACCEPT_GARDEN_PROFILE

    bridge = StartProfile("bridge-explicit", LaunchMode.BRIDGE, RouterHarnessMode.BUNDLED_I2PD, intent.launch_intent_digest, public_bridge_enabled=True, garden_service_count=1)
    assert assess_start_matrix(bridge, launch=launch, router=router).decision_kind is StartMatrixDecisionKind.ACCEPT_BRIDGE_PROFILE

    no_router = sam_report(SamProbeDecisionKind.ACCEPT_LOCAL_UNAVAILABLE)
    offline_intent, offline_launch = launch_report(LaunchMode.OFFLINE_DESIGN, sam=no_router, allow_no_router=True)
    offline_router = assess_router_harness(router_config(RouterHarnessMode.OFFLINE_NO_ROUTER, datadir_digest=b"\x00" * 32, destination_digest=b"\x00" * 32), no_router)
    offline = StartProfile("offline-design", LaunchMode.OFFLINE_DESIGN, RouterHarnessMode.OFFLINE_NO_ROUTER, offline_intent.launch_intent_digest, require_persistent_destination=False)
    assert assess_start_matrix(offline, launch=offline_launch, router=offline_router).decision_kind is StartMatrixDecisionKind.ACCEPT_OFFLINE_DESIGN_PROFILE


def test_startmatrix_rejects_profile_drift_and_unsafe_modes() -> None:
    intent, launch = launch_report()
    router = assess_router_harness(router_config(), sam_report())
    mismatch = StartProfile("mismatch", LaunchMode.LEAF, RouterHarnessMode.BUNDLED_I2PD, d("other-intent"))
    assert assess_start_matrix(mismatch, launch=launch, router=router).decision_kind is StartMatrixDecisionKind.QUARANTINE_INTENT_MISMATCH

    replay = StartProfile("leaf-default", LaunchMode.LEAF, RouterHarnessMode.BUNDLED_I2PD, intent.launch_intent_digest)
    assert assess_start_matrix(replay, launch=launch, router=router, previously_seen_profile_digests=(replay.profile_digest,)).decision_kind is StartMatrixDecisionKind.QUARANTINE_PROFILE_REPLAY

    i2p_only_bad = StartProfile("i2p-only-bad", LaunchMode.LEAF, RouterHarnessMode.BUNDLED_I2PD, intent.launch_intent_digest, i2p_only=True, classic_fallback_enabled=True)
    assert assess_start_matrix(i2p_only_bad, launch=launch, router=router).decision_kind is StartMatrixDecisionKind.QUARANTINE_CLASSIC_FALLBACK_DRIFT

    no_services = StartProfile("garden-no-services", LaunchMode.GARDEN, RouterHarnessMode.BUNDLED_I2PD, intent.launch_intent_digest)
    assert assess_start_matrix(no_services, launch=launch, router=router).decision_kind is StartMatrixDecisionKind.HOLD_GARDEN_SERVICE_PROOF

    hidden_bridge = StartProfile("bridge-hidden", LaunchMode.BRIDGE, RouterHarnessMode.BUNDLED_I2PD, intent.launch_intent_digest)
    assert assess_start_matrix(hidden_bridge, launch=launch, router=router).decision_kind is StartMatrixDecisionKind.HOLD_BRIDGE_EXPLICITNESS

    metric_budget = StartProfile("leaf-chatty", LaunchMode.LEAF, RouterHarnessMode.BUNDLED_I2PD, intent.launch_intent_digest, max_metric_cardinality=64)
    assert assess_start_matrix(metric_budget, launch=launch, router=router).decision_kind is StartMatrixDecisionKind.HOLD_METRICS_BUDGET


def test_telemetrydebt_accepts_veiled_metrics_and_drops_expired_soft_items() -> None:
    scope = d("scope")
    metric = MetricEvent.create(name="launch_quorum_decision", labels={"scope": "launch", "decision": "accept_launch"}, value=1, scope_digest=scope, issued_at=100)
    assessment = assess_metric_event(metric, expected_scope_digest=scope)
    item = item_from_metric_assessment(assessment, issued_at=100, ttl=50)
    expired = TelemetryRetentionItem(metric_digest=d("expired"), scope_digest=scope, kind="garden_refusal", issued_at=1, expires_at=10)
    report = assess_telemetry_debt((item, expired), now=120)
    assert report.decision_kind is TelemetryDebtDecisionKind.ACCEPT_RETENTION_PLAN
    assert item.item_digest in report.retained_digests
    assert expired.item_digest in report.gc_candidate_digests


def test_telemetrydebt_rejects_leaks_scope_mix_cardinality_and_byte_debt() -> None:
    scope = d("scope")
    clean = TelemetryRetentionItem(metric_digest=d("metric"), scope_digest=scope, kind="sam_probe_result", issued_at=10, expires_at=100, label_cardinality=2)
    leak = TelemetryRetentionItem(metric_digest=d("leak"), scope_digest=scope, kind="provider_probe_result", issued_at=10, expires_at=100, raw_fragment_count=1)
    assert assess_telemetry_debt((leak,), now=20).decision_kind is TelemetryDebtDecisionKind.QUARANTINE_RAW_LEAK

    other_scope = TelemetryRetentionItem(metric_digest=d("other"), scope_digest=d("other-scope"), kind="sam_probe_result", issued_at=10, expires_at=100)
    assert assess_telemetry_debt((clean, other_scope), now=20).decision_kind is TelemetryDebtDecisionKind.QUARANTINE_SCOPE_MIX

    chatty = TelemetryRetentionItem(metric_digest=d("chatty"), scope_digest=scope, kind="provider_probe_result", issued_at=10, expires_at=100, label_cardinality=99)
    assert assess_telemetry_debt((chatty,), policy=TelemetryDebtPolicy(max_cardinality_per_item=8), now=20).decision_kind is TelemetryDebtDecisionKind.HOLD_CARDINALITY_COMPACTION

    big = TelemetryRetentionItem(metric_digest=d("big"), scope_digest=scope, kind="storage_repair_debt", issued_at=10, expires_at=100, byte_cost=1_000)
    assert assess_telemetry_debt((big,), policy=TelemetryDebtPolicy(max_total_bytes=128), now=20).decision_kind is TelemetryDebtDecisionKind.HOLD_RETENTION_GC_REQUIRED


def test_telemetrydebt_requires_hard_negative_evidence_when_summary_claims_it() -> None:
    scope = d("scope")
    summary = TelemetryRetentionItem(metric_digest=d("summary"), scope_digest=scope, kind="provider_probe_result", issued_at=10, expires_at=100, hard_negative_count=1)
    without_gc = assess_telemetry_debt((summary,), now=20)
    assert without_gc.decision_kind is TelemetryDebtDecisionKind.QUARANTINE_EVIDENCE_DROP

    hard_item = EvidenceItem(EvidenceKind.PROVIDER_FALSE, scope, d("object"), "family-a", "path-a", 10, 100)
    gc = collect_evidence_gc((hard_item,), now=20)
    with_gc = assess_telemetry_debt((summary,), now=20, evidence_gc=gc)
    assert with_gc.decision_kind is TelemetryDebtDecisionKind.ACCEPT_RETENTION_PLAN


def test_startfold_audits_current_revision_surface() -> None:
    report = audit_start_fold(".", revision="rev0035", artifact_stem="Nicotine-i2pDHT-rev0035-2026.06.04.00.45-startmatrix-telemetrydebt-routerharness")
    assert report.status == "pass"
    assert report.error_count == 0
