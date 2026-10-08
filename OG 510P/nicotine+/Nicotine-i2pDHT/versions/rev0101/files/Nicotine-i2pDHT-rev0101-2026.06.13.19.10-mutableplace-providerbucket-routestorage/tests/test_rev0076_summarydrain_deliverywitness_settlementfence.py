from __future__ import annotations

from pathlib import Path

from i2p_dht_lab.moderationquarantine import ZERO_DIGEST
from i2p_dht_lab.summarydeliveryfold import audit_summary_delivery_fold
from i2p_dht_lab.summarydeliverywitness import (
    SummaryDeliveryDecisionKind,
    SummaryDeliveryObservationKind,
    assess_summary_delivery_witness,
    make_summary_delivery_observation,
)
from i2p_dht_lab.summarydrain import SummaryDrainClass, SummaryDrainDecisionKind, assess_summary_drain, make_summary_drain_marker
from i2p_dht_lab.summarysendcanary import SummarySendCanaryClass, SummarySendCanaryDecisionKind, assess_summary_send_canary, make_summary_send_canary_marker
from i2p_dht_lab.settlementfence import SettlementFenceClass, SettlementFenceDecisionKind, assess_settlement_fence, make_settlement_fence_marker
from test_rev0075_summarysendcanary_redactiongc_outboxsettlement import accepted_outbox_settlement


def accepted_canary_bundle():
    settlement_report, outbox, fence, settlement, ledger, gc = accepted_outbox_settlement()
    markers = []
    prev = ZERO_DIGEST
    classes = (
        SummarySendCanaryClass.OUTBOX_SETTLEMENT,
        SummarySendCanaryClass.PUBLISH_FENCE,
        SummarySendCanaryClass.PUBLIC_LEDGER,
        SummarySendCanaryClass.REDACTION_GC,
        SummarySendCanaryClass.REDACTION_OK,
        SummarySendCanaryClass.CONTRADICTION_MEMORY,
    )
    for seq, cls in enumerate(classes, start=1):
        marker = make_summary_send_canary_marker(
            canary_class=cls,
            sequence=seq,
            previous_digest=prev,
            outbox_settlement_report=settlement_report,
            publish_fence_report=fence,
            public_ledger_report=ledger,
            redaction_gc_report=gc,
            family_id=f"canary-{seq}",
            path_family_id=f"canary-path-{seq}",
        )
        markers.append(marker)
        prev = marker.marker_digest
    canary = assess_summary_send_canary(
        outbox_settlement_report=settlement_report,
        publish_fence_report=fence,
        public_ledger_report=ledger,
        redaction_gc_report=gc,
        markers=tuple(markers),
        previous_digest=ZERO_DIGEST,
    )
    assert canary.decision_kind is SummarySendCanaryDecisionKind.ACCEPT_SUMMARY_SEND_CANARY
    return canary, settlement_report, fence, ledger, gc


def accepted_summary_drain():
    canary, settlement_report, fence, ledger, gc = accepted_canary_bundle()
    markers = []
    prev = ZERO_DIGEST
    classes = (
        SummaryDrainClass.SEND_CANARY,
        SummaryDrainClass.OUTBOX_SETTLEMENT,
        SummaryDrainClass.PUBLIC_LEDGER,
        SummaryDrainClass.REDACTION_GC,
        SummaryDrainClass.REDACTION_OK,
        SummaryDrainClass.IDEMPOTENCY,
        SummaryDrainClass.CONTRADICTION_MEMORY,
    )
    for seq, cls in enumerate(classes, start=1):
        marker = make_summary_drain_marker(
            drain_class=cls,
            sequence=seq,
            previous_digest=prev,
            summary_send_canary_report=canary,
            family_id=f"drain-{seq}",
            path_family_id=f"drain-path-{seq}",
        )
        markers.append(marker)
        prev = marker.marker_digest
    drain = assess_summary_drain(summary_send_canary_report=canary, markers=tuple(markers), previous_digest=ZERO_DIGEST)
    assert drain.decision_kind is SummaryDrainDecisionKind.ACCEPT_SUMMARY_DRAIN_READY
    return drain, canary, settlement_report, fence, ledger, gc


def accepted_delivery_witness():
    drain, canary, settlement_report, fence, ledger, gc = accepted_summary_drain()
    observations = []
    prev = ZERO_DIGEST
    kinds = (
        SummaryDeliveryObservationKind.ACK_DELIVERED,
        SummaryDeliveryObservationKind.REDACTION_OK,
        SummaryDeliveryObservationKind.CONTRADICTION_MEMORY,
    )
    for seq, kind in enumerate(kinds, start=1):
        obs = make_summary_delivery_observation(
            observation_kind=kind,
            sequence=seq,
            previous_digest=prev,
            summary_drain_report=drain,
            family_id=f"delivery-{seq}",
            path_family_id=f"delivery-path-{seq}",
        )
        observations.append(obs)
        prev = obs.observation_digest
    delivery = assess_summary_delivery_witness(summary_drain_report=drain, observations=tuple(observations), previous_digest=ZERO_DIGEST)
    assert delivery.decision_kind is SummaryDeliveryDecisionKind.ACCEPT_SUMMARY_DELIVERY_ACK
    return delivery, drain, canary, gc


def accepted_settlement_fence():
    delivery, drain, canary, gc = accepted_delivery_witness()
    markers = []
    prev = ZERO_DIGEST
    classes = (
        SettlementFenceClass.SEND_CANARY,
        SettlementFenceClass.SUMMARY_DRAIN,
        SettlementFenceClass.DELIVERY_ACK,
        SettlementFenceClass.REDACTION_GC,
        SettlementFenceClass.REDACTION_OK,
        SettlementFenceClass.CONTRADICTION_MEMORY,
    )
    for seq, cls in enumerate(classes, start=1):
        marker = make_settlement_fence_marker(
            fence_class=cls,
            sequence=seq,
            previous_digest=prev,
            summary_send_canary_report=canary,
            summary_drain_report=drain,
            summary_delivery_witness_report=delivery,
            redaction_gc_report=gc,
            family_id=f"fence-{seq}",
            path_family_id=f"fence-path-{seq}",
        )
        markers.append(marker)
        prev = marker.marker_digest
    report = assess_settlement_fence(
        summary_send_canary_report=canary,
        summary_drain_report=drain,
        summary_delivery_witness_report=delivery,
        redaction_gc_report=gc,
        markers=tuple(markers),
        previous_digest=ZERO_DIGEST,
    )
    assert report.decision_kind is SettlementFenceDecisionKind.ACCEPT_SETTLEMENT_FENCE
    return report


def test_summary_delivery_settlement_happy_path() -> None:
    drain, canary, *_ = accepted_summary_drain()
    delivery, *_ = accepted_delivery_witness()
    fence = accepted_settlement_fence()
    assert canary.send_canary_ready
    assert drain.summary_drain_ready and drain.redacted and drain.contradiction_preserved
    assert delivery.summary_delivery_acked and delivery.redacted and delivery.contradiction_preserved
    assert fence.settlement_fenced and fence.summary_delivery_settled


def test_summary_drain_rejects_raw_payload_leak() -> None:
    canary, *_ = accepted_canary_bundle()
    marker = make_summary_drain_marker(
        drain_class=SummaryDrainClass.SEND_CANARY,
        sequence=1,
        summary_send_canary_report=canary,
        raw_payload_exposed=True,
        family_id="drain-a",
        path_family_id="path-a",
    )
    report = assess_summary_drain(
        summary_send_canary_report=canary,
        markers=(marker,),
        required_classes=(SummaryDrainClass.SEND_CANARY,),
        min_family_count=1,
        min_path_family_count=1,
    )
    assert report.decision_kind is SummaryDrainDecisionKind.QUARANTINE_RAW_LEAK


def test_delivery_witness_holds_useful_refusal() -> None:
    drain, *_ = accepted_summary_drain()
    obs1 = make_summary_delivery_observation(
        observation_kind=SummaryDeliveryObservationKind.CONTRADICTION_MEMORY,
        sequence=1,
        summary_drain_report=drain,
        family_id="delivery-a",
        path_family_id="path-a",
    )
    obs2 = make_summary_delivery_observation(
        observation_kind=SummaryDeliveryObservationKind.USEFUL_REFUSAL,
        sequence=2,
        previous_digest=obs1.observation_digest,
        summary_drain_report=drain,
        family_id="delivery-b",
        path_family_id="path-b",
    )
    report = assess_summary_delivery_witness(
        summary_drain_report=drain,
        observations=(obs1, obs2),
        required_observations=(SummaryDeliveryObservationKind.CONTRADICTION_MEMORY,),
        min_family_count=1,
        min_path_family_count=1,
    )
    assert report.decision_kind is SummaryDeliveryDecisionKind.HOLD_USEFUL_REFUSAL
    assert report.useful_refusal_seen and not report.summary_delivery_acked


def test_delivery_witness_quarantines_payload_mismatch() -> None:
    drain, *_ = accepted_summary_drain()
    obs1 = make_summary_delivery_observation(
        observation_kind=SummaryDeliveryObservationKind.CONTRADICTION_MEMORY,
        sequence=1,
        summary_drain_report=drain,
        family_id="delivery-a",
        path_family_id="path-a",
    )
    obs2 = make_summary_delivery_observation(
        observation_kind=SummaryDeliveryObservationKind.PAYLOAD_MISMATCH,
        sequence=2,
        previous_digest=obs1.observation_digest,
        summary_drain_report=drain,
        family_id="delivery-b",
        path_family_id="path-b",
    )
    report = assess_summary_delivery_witness(
        summary_drain_report=drain,
        observations=(obs1, obs2),
        required_observations=(SummaryDeliveryObservationKind.CONTRADICTION_MEMORY,),
        min_family_count=1,
        min_path_family_count=1,
    )
    assert report.decision_kind is SummaryDeliveryDecisionKind.QUARANTINE_PAYLOAD_MISMATCH


def test_settlement_fence_holds_missing_delivery_ack() -> None:
    drain, canary, _settlement, _fence, _ledger, gc = accepted_summary_drain()
    obs = make_summary_delivery_observation(
        observation_kind=SummaryDeliveryObservationKind.MISSING_ACK,
        sequence=1,
        summary_drain_report=drain,
        family_id="delivery-a",
        path_family_id="path-a",
    )
    delivery = assess_summary_delivery_witness(
        summary_drain_report=drain,
        observations=(obs,),
        required_observations=(SummaryDeliveryObservationKind.MISSING_ACK,),
        min_family_count=1,
        min_path_family_count=1,
    )
    marker = make_settlement_fence_marker(
        fence_class=SettlementFenceClass.SUMMARY_DRAIN,
        sequence=1,
        summary_send_canary_report=canary,
        summary_drain_report=drain,
        summary_delivery_witness_report=delivery,
        redaction_gc_report=gc,
        family_id="fence-a",
        path_family_id="path-a",
    )
    report = assess_settlement_fence(
        summary_send_canary_report=canary,
        summary_drain_report=drain,
        summary_delivery_witness_report=delivery,
        redaction_gc_report=gc,
        markers=(marker,),
        required_classes=(SettlementFenceClass.SUMMARY_DRAIN,),
        min_family_count=1,
        min_path_family_count=1,
    )
    assert report.decision_kind is SettlementFenceDecisionKind.HOLD_DELIVERY_PENDING


def test_settlement_fence_quarantines_contradiction_drop() -> None:
    delivery, drain, canary, gc = accepted_delivery_witness()
    marker = make_settlement_fence_marker(
        fence_class=SettlementFenceClass.CONTRADICTION_MEMORY,
        sequence=1,
        summary_send_canary_report=canary,
        summary_drain_report=drain,
        summary_delivery_witness_report=delivery,
        redaction_gc_report=gc,
        contradiction_carried=False,
        family_id="fence-a",
        path_family_id="path-a",
    )
    report = assess_settlement_fence(
        summary_send_canary_report=canary,
        summary_drain_report=drain,
        summary_delivery_witness_report=delivery,
        redaction_gc_report=gc,
        markers=(marker,),
        required_classes=(SettlementFenceClass.CONTRADICTION_MEMORY,),
        min_family_count=1,
        min_path_family_count=1,
    )
    assert report.decision_kind is SettlementFenceDecisionKind.QUARANTINE_CONTRADICTION_DROPPED


def test_summary_delivery_fold_audit_passes() -> None:
    root = Path(__file__).resolve().parents[1]
    report = audit_summary_delivery_fold(root, artifact_stem=root.name)
    assert report.status == "pass"
    assert report.error_count == 0
