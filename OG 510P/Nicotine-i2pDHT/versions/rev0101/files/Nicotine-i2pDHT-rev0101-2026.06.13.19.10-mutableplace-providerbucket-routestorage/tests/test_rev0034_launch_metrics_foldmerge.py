from __future__ import annotations

from i2p_dht_lab.foldmerge import audit_fold_merge
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.launchquorum import (
    LaunchIntent,
    LaunchMode,
    LaunchQuorumDecisionKind,
    assess_launch_quorum,
)
from i2p_dht_lab.metricsveil import (
    MetricDecisionKind,
    MetricEvent,
    MetricsPolicy,
    assess_metric_event,
)
from i2p_dht_lab.persistjoin import PersistJoinDecisionKind, PersistJoinReport
from i2p_dht_lab.safestart import SafeStartDecisionKind, SafeStartReport
from i2p_dht_lab.samprobe import SamProbeDecisionKind, SamProbeReport


def d(label: str) -> bytes:
    return sha256(("rev0034:" + label).encode("utf-8"))


def safe_start(*, accept: bool = True, intent: bytes | None = None) -> SafeStartReport:
    kind = SafeStartDecisionKind.ACCEPT_SAFE_START if accept else SafeStartDecisionKind.QUARANTINE_SAMTRACE
    return SafeStartReport(
        decision_kind=kind,
        accept=accept,
        reason=kind.value,
        intent_digest=intent or d("intent"),
        negotiation_report_digest=d("negotiation-report"),
        migration_report_digest=d("migration-report"),
        samtrace_report_digest=d("samtrace-report"),
        pressure_digests=(d("safe-pressure"),) if not accept else (),
        report_digest=d("safe-start-report:" + kind.value + str(accept)),
    )


def persist_join(*, accept: bool = True, crash_tail: bool = False) -> PersistJoinReport:
    if not accept:
        kind = PersistJoinDecisionKind.QUARANTINE_HARD_NEGATIVE_DROP
    elif crash_tail:
        kind = PersistJoinDecisionKind.ACCEPT_WITH_CRASH_TAIL_WATCH
    else:
        kind = PersistJoinDecisionKind.ACCEPT_DURABLE_JOIN
    return PersistJoinReport(
        decision_kind=kind,
        accept=accept,
        reason=kind.value,
        persist_report_digest=d("persist-report"),
        journal_report_digest=d("journal-report"),
        checkpoint_report_digest=d("checkpoint-report"),
        scope_report_digest=d("scope-report"),
        store_report_digest=d("store-report"),
        checkpoint_digest=d("checkpoint"),
        journal_tip_digest=d("journal-tip"),
        pressure_digests=(d("persist-pressure"),) if not accept or crash_tail else (),
        hard_negative_count=2,
        report_digest=d("persist-join-report:" + kind.value + str(accept)),
    )


def sam_probe(kind: SamProbeDecisionKind = SamProbeDecisionKind.ACCEPT_STREAMING_FIRST_PROBE, *, endpoint: bytes | None = None) -> SamProbeReport:
    accept = kind in {SamProbeDecisionKind.ACCEPT_STREAMING_FIRST_PROBE, SamProbeDecisionKind.ACCEPT_LOCAL_UNAVAILABLE, SamProbeDecisionKind.ACCEPT_SESSION_ONLY}
    return SamProbeReport(
        decision_kind=kind,
        accept=accept,
        reason=kind.value,
        command_digests=(d("sam-command-a"), d("sam-command-b")),
        reply_digests=(d("sam-reply-a"),) if kind is not SamProbeDecisionKind.ACCEPT_LOCAL_UNAVAILABLE else (),
        endpoint_digest=endpoint or d("endpoint"),
        transcript_digest=d("sam-transcript:" + kind.value),
    )


def launch_intent(**overrides: object) -> LaunchIntent:
    base = dict(
        mode=LaunchMode.LEAF,
        intent_digest=d("intent"),
        endpoint_digest=d("endpoint"),
        generation=4,
        allow_no_router=False,
        allow_crash_tail_watch=False,
        require_streaming_probe=True,
    )
    base.update(overrides)
    return LaunchIntent(**base)  # type: ignore[arg-type]


def test_launchquorum_accepts_streaming_restart_safe_start_join() -> None:
    report = assess_launch_quorum(
        launch_intent(),
        safe_start=safe_start(),
        persist_join=persist_join(),
        sam_probe=sam_probe(),
    )
    assert report.decision_kind is LaunchQuorumDecisionKind.ACCEPT_LAUNCH
    assert report.accept


def test_launchquorum_holds_router_unavailable_except_offline_design() -> None:
    live = assess_launch_quorum(
        launch_intent(),
        safe_start=safe_start(),
        persist_join=persist_join(),
        sam_probe=sam_probe(SamProbeDecisionKind.ACCEPT_LOCAL_UNAVAILABLE),
    )
    assert live.decision_kind is LaunchQuorumDecisionKind.HOLD_ROUTER_UNAVAILABLE
    assert not live.accept

    offline = assess_launch_quorum(
        launch_intent(mode=LaunchMode.OFFLINE_DESIGN, allow_no_router=True),
        safe_start=safe_start(),
        persist_join=persist_join(),
        sam_probe=sam_probe(SamProbeDecisionKind.ACCEPT_LOCAL_UNAVAILABLE),
    )
    assert offline.decision_kind is LaunchQuorumDecisionKind.ACCEPT_OFFLINE_DESIGN_LAUNCH
    assert offline.accept


def test_launchquorum_rejects_intent_endpoint_component_and_replay_drift() -> None:
    mismatch = assess_launch_quorum(
        launch_intent(intent_digest=d("intent-other")),
        safe_start=safe_start(intent=d("intent")),
        persist_join=persist_join(),
        sam_probe=sam_probe(),
    )
    assert mismatch.decision_kind is LaunchQuorumDecisionKind.QUARANTINE_INTENT_MISMATCH

    endpoint = assess_launch_quorum(
        launch_intent(),
        safe_start=safe_start(),
        persist_join=persist_join(),
        sam_probe=sam_probe(endpoint=d("endpoint-other")),
    )
    assert endpoint.decision_kind is LaunchQuorumDecisionKind.QUARANTINE_ENDPOINT_DRIFT

    component = assess_launch_quorum(
        launch_intent(),
        safe_start=safe_start(accept=False),
        persist_join=persist_join(),
        sam_probe=sam_probe(),
    )
    assert component.decision_kind is LaunchQuorumDecisionKind.QUARANTINE_SAFE_START

    replay = assess_launch_quorum(
        launch_intent(),
        safe_start=safe_start(),
        persist_join=persist_join(),
        sam_probe=sam_probe(),
        previously_seen_digests=(safe_start().report_digest,),
    )
    assert replay.decision_kind is LaunchQuorumDecisionKind.QUARANTINE_DIGEST_REPLAY


def test_launchquorum_crash_tail_and_garden_require_completed_stream() -> None:
    crash = assess_launch_quorum(
        launch_intent(),
        safe_start=safe_start(),
        persist_join=persist_join(crash_tail=True),
        sam_probe=sam_probe(),
    )
    assert crash.decision_kind is LaunchQuorumDecisionKind.HOLD_CRASH_TAIL_WATCH

    session_only_garden = assess_launch_quorum(
        launch_intent(mode=LaunchMode.GARDEN, require_streaming_probe=False),
        safe_start=safe_start(),
        persist_join=persist_join(),
        sam_probe=sam_probe(SamProbeDecisionKind.ACCEPT_SESSION_ONLY),
    )
    assert session_only_garden.decision_kind is LaunchQuorumDecisionKind.HOLD_MODE_REQUIREMENT


def test_metricsveil_accepts_redacted_metric_and_aggregate_metric() -> None:
    scope = d("scope")
    event = MetricEvent.create(
        name="launch_quorum_decision",
        labels={"scope": "launch", "decision": "accept_launch", "mode": "leaf"},
        value=1,
        scope_digest=scope,
        issued_at=1_766_900_000,
    )
    report = assess_metric_event(event, expected_scope_digest=scope)
    assert report.decision_kind is MetricDecisionKind.ACCEPT_REDACTED_METRIC
    assert report.accept
    assert report.veiled_metric is not None
    assert all(len(digest) == 32 for _, digest in report.veiled_metric.label_digests)

    aggregate = MetricEvent.create(name="storage_repair_debt", labels={}, value=3, scope_digest=scope, issued_at=1_766_900_001)
    aggregate_report = assess_metric_event(aggregate, expected_scope_digest=scope)
    assert aggregate_report.decision_kind is MetricDecisionKind.ACCEPT_AGGREGATE_METRIC


def test_metricsveil_rejects_raw_keys_destinations_scope_and_cardinality() -> None:
    scope = d("scope")
    raw_key = MetricEvent.create(
        name="provider_probe_result",
        labels={"scope": "provider", "decision": "false", "bucket": "a" * 64},
        value=1,
        scope_digest=scope,
        issued_at=1,
    )
    assert assess_metric_event(raw_key).decision_kind is MetricDecisionKind.QUARANTINE_RAW_KEY_LABEL

    raw_destination = MetricEvent.create(
        name="sam_probe_result",
        labels={"scope": "sam", "family": "abcdefghijklmnopqrstuvwxyz234567abcdefghijklmnopqrstuvwxyz234567.b32.i2p"},
        value=1,
        scope_digest=scope,
        issued_at=1,
    )
    assert assess_metric_event(raw_destination).decision_kind is MetricDecisionKind.QUARANTINE_RAW_DESTINATION_LABEL

    wrong_scope = MetricEvent.create(name="garden_refusal", labels={"scope": "garden"}, value=1, scope_digest=scope, issued_at=1)
    assert assess_metric_event(wrong_scope, expected_scope_digest=d("other-scope")).decision_kind is MetricDecisionKind.QUARANTINE_SCOPE_MISMATCH

    budget = MetricEvent.create(name="garden_refusal", labels={"scope": "garden", "family": "new-family"}, value=1, scope_digest=scope, issued_at=1)
    report = assess_metric_event(
        budget,
        policy=MetricsPolicy(max_values_per_label=2),
        prior_label_values={"family": {"a", "b"}},
    )
    assert report.decision_kind is MetricDecisionKind.HOLD_CARDINALITY_BUDGET


def test_foldmerge_current_revision_audit_passes() -> None:
    report = audit_fold_merge(".")
    assert report.status == "pass"
    assert report.branchlet_status == "pass"
    assert report.error_count == 0
