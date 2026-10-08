from __future__ import annotations

from pathlib import Path

from i2p_dht_lab.deliveryarchive import (
    DeliveryArchiveClass,
    DeliveryArchiveDecisionKind,
    assess_delivery_archive,
    make_delivery_archive_marker,
)
from i2p_dht_lab.moderationquarantine import ZERO_DIGEST
from i2p_dht_lab.summaryackfold import audit_summary_ack_fold
from i2p_dht_lab.summaryackledger import (
    SummaryAckClass,
    SummaryAckDecisionKind,
    assess_summary_ack_ledger,
    make_summary_ack_marker,
)
from i2p_dht_lab.summaryprunefence import (
    SummaryPruneClass,
    SummaryPruneDecisionKind,
    assess_summary_prune_fence,
    make_summary_prune_proposal,
)
from i2p_dht_lab.summarydeliverywitness import (
    SummaryDeliveryObservationKind,
    assess_summary_delivery_witness,
    make_summary_delivery_observation,
)
from test_rev0076_summarydrain_deliverywitness_settlementfence import accepted_delivery_witness, accepted_settlement_fence, accepted_summary_drain


def accepted_summary_ack_ledger():
    fence = accepted_settlement_fence()
    delivery, drain, _canary, _gc = accepted_delivery_witness()
    markers = []
    prev = ZERO_DIGEST
    classes = (
        SummaryAckClass.SETTLEMENT_FENCE,
        SummaryAckClass.DELIVERY_ACK,
        SummaryAckClass.SUMMARY_DRAIN,
        SummaryAckClass.REDACTION_OK,
        SummaryAckClass.CONTRADICTION_MEMORY,
        SummaryAckClass.IDEMPOTENCY,
    )
    for seq, cls in enumerate(classes, start=1):
        marker = make_summary_ack_marker(
            ack_class=cls,
            sequence=seq,
            previous_digest=prev,
            settlement_fence_report=fence,
            delivery_witness_report=delivery,
            summary_drain_report=drain,
            family_id=f"ack-{seq}",
            path_family_id=f"ack-path-{seq}",
        )
        markers.append(marker)
        prev = marker.marker_digest
    report = assess_summary_ack_ledger(settlement_fence_report=fence, delivery_witness_report=delivery, summary_drain_report=drain, markers=tuple(markers), previous_digest=ZERO_DIGEST)
    assert report.decision_kind is SummaryAckDecisionKind.ACCEPT_SUMMARY_ACK_SETTLED
    return report, fence, delivery, drain


def accepted_delivery_archive():
    ack, fence, _delivery, _drain = accepted_summary_ack_ledger()
    markers = []
    prev = ZERO_DIGEST
    classes = (
        DeliveryArchiveClass.ACK_LEDGER,
        DeliveryArchiveClass.SETTLEMENT_FENCE,
        DeliveryArchiveClass.REDACTION_MEMORY,
        DeliveryArchiveClass.CONTRADICTION_MEMORY,
        DeliveryArchiveClass.RESTART_GENERATION,
        DeliveryArchiveClass.IDEMPOTENCY,
    )
    for seq, cls in enumerate(classes, start=1):
        marker = make_delivery_archive_marker(
            archive_class=cls,
            sequence=seq,
            previous_digest=prev,
            summary_ack_ledger_report=ack,
            settlement_fence_report=fence,
            restart_generation=7,
            family_id=f"archive-{seq}",
            path_family_id=f"archive-path-{seq}",
        )
        markers.append(marker)
        prev = marker.marker_digest
    report = assess_delivery_archive(summary_ack_ledger_report=ack, settlement_fence_report=fence, markers=tuple(markers), previous_digest=ZERO_DIGEST)
    assert report.decision_kind is DeliveryArchiveDecisionKind.ACCEPT_DELIVERY_ARCHIVED
    return report, ack, fence


def accepted_summary_prune_fence():
    archive, ack, fence = accepted_delivery_archive()
    proposals = []
    prev = ZERO_DIGEST
    classes = (
        SummaryPruneClass.KEEP_ACK_LEDGER,
        SummaryPruneClass.KEEP_DELIVERY_ARCHIVE,
        SummaryPruneClass.KEEP_SETTLEMENT_FENCE,
        SummaryPruneClass.KEEP_REDACTION_MEMORY,
        SummaryPruneClass.KEEP_CONTRADICTION_MEMORY,
        SummaryPruneClass.SOFT_WORKING_SET_PRUNED,
    )
    for seq, cls in enumerate(classes, start=1):
        proposal = make_summary_prune_proposal(
            prune_class=cls,
            sequence=seq,
            previous_digest=prev,
            summary_ack_ledger_report=ack,
            delivery_archive_report=archive,
            settlement_fence_report=fence,
            family_id=f"prune-{seq}",
            path_family_id=f"prune-path-{seq}",
        )
        proposals.append(proposal)
        prev = proposal.proposal_digest
    report = assess_summary_prune_fence(summary_ack_ledger_report=ack, delivery_archive_report=archive, settlement_fence_report=fence, proposals=tuple(proposals), previous_digest=ZERO_DIGEST)
    assert report.decision_kind is SummaryPruneDecisionKind.ACCEPT_SUMMARY_PRUNE_FENCED
    return report, archive, ack, fence


def test_summary_ack_archive_prune_happy_path() -> None:
    ack, *_ = accepted_summary_ack_ledger()
    archive, *_ = accepted_delivery_archive()
    prune, *_ = accepted_summary_prune_fence()
    assert ack.summary_ack_settled and ack.delivery_terminal and ack.contradiction_preserved
    assert archive.delivery_archived and archive.restart_sticky and archive.redacted
    assert prune.summary_prune_fenced and prune.soft_prune_allowed and prune.ack_memory_preserved


def test_summary_ack_holds_missing_delivery_ack() -> None:
    drain, _canary, *_ = accepted_summary_drain()
    obs = make_summary_delivery_observation(
        observation_kind=SummaryDeliveryObservationKind.MISSING_ACK,
        sequence=1,
        summary_drain_report=drain,
        family_id="delivery-a",
        path_family_id="delivery-path-a",
    )
    delivery = assess_summary_delivery_witness(
        summary_drain_report=drain,
        observations=(obs,),
        required_observations=(SummaryDeliveryObservationKind.MISSING_ACK,),
        min_family_count=1,
        min_path_family_count=1,
    )
    fence = accepted_settlement_fence()
    marker = make_summary_ack_marker(
        ack_class=SummaryAckClass.DELIVERY_ACK,
        sequence=1,
        settlement_fence_report=fence,
        delivery_witness_report=delivery,
        summary_drain_report=drain,
        family_id="ack-a",
        path_family_id="ack-path-a",
    )
    report = assess_summary_ack_ledger(
        settlement_fence_report=fence,
        delivery_witness_report=delivery,
        summary_drain_report=drain,
        markers=(marker,),
        required_classes=(SummaryAckClass.DELIVERY_ACK,),
        min_family_count=1,
        min_path_family_count=1,
    )
    assert report.decision_kind is SummaryAckDecisionKind.HOLD_DELIVERY_PENDING


def test_summary_ack_quarantines_redaction_drop() -> None:
    fence = accepted_settlement_fence()
    delivery, drain, *_ = accepted_delivery_witness()
    marker = make_summary_ack_marker(
        ack_class=SummaryAckClass.REDACTION_OK,
        sequence=1,
        settlement_fence_report=fence,
        delivery_witness_report=delivery,
        summary_drain_report=drain,
        redaction_carried=False,
        family_id="ack-a",
        path_family_id="ack-path-a",
    )
    report = assess_summary_ack_ledger(
        settlement_fence_report=fence,
        delivery_witness_report=delivery,
        summary_drain_report=drain,
        markers=(marker,),
        required_classes=(SummaryAckClass.REDACTION_OK,),
        min_family_count=1,
        min_path_family_count=1,
    )
    assert report.decision_kind is SummaryAckDecisionKind.QUARANTINE_REDACTION_DROPPED


def test_delivery_archive_rejects_previous_link_mismatch() -> None:
    ack, fence, *_ = accepted_summary_ack_ledger()
    first = make_delivery_archive_marker(
        archive_class=DeliveryArchiveClass.ACK_LEDGER,
        sequence=1,
        summary_ack_ledger_report=ack,
        settlement_fence_report=fence,
        family_id="archive-a",
        path_family_id="archive-path-a",
    )
    second = make_delivery_archive_marker(
        archive_class=DeliveryArchiveClass.CONTRADICTION_MEMORY,
        sequence=2,
        previous_digest=ZERO_DIGEST,
        summary_ack_ledger_report=ack,
        settlement_fence_report=fence,
        family_id="archive-b",
        path_family_id="archive-path-b",
    )
    report = assess_delivery_archive(
        summary_ack_ledger_report=ack,
        settlement_fence_report=fence,
        markers=(first, second),
        required_classes=(DeliveryArchiveClass.ACK_LEDGER, DeliveryArchiveClass.CONTRADICTION_MEMORY),
        min_family_count=1,
        min_path_family_count=1,
    )
    assert report.decision_kind is DeliveryArchiveDecisionKind.QUARANTINE_PREVIOUS_MISMATCH


def test_summary_prune_rejects_contradiction_drop() -> None:
    archive, ack, fence = accepted_delivery_archive()
    proposal = make_summary_prune_proposal(
        prune_class=SummaryPruneClass.KEEP_CONTRADICTION_MEMORY,
        sequence=1,
        summary_ack_ledger_report=ack,
        delivery_archive_report=archive,
        settlement_fence_report=fence,
        keep_contradiction_memory=False,
        family_id="prune-a",
        path_family_id="prune-path-a",
    )
    report = assess_summary_prune_fence(
        summary_ack_ledger_report=ack,
        delivery_archive_report=archive,
        settlement_fence_report=fence,
        proposals=(proposal,),
        required_classes=(SummaryPruneClass.KEEP_CONTRADICTION_MEMORY,),
        min_family_count=1,
        min_path_family_count=1,
    )
    assert report.decision_kind is SummaryPruneDecisionKind.QUARANTINE_CONTRADICTION_DROPPED


def test_summary_prune_rejects_archive_memory_drop() -> None:
    archive, ack, fence = accepted_delivery_archive()
    proposal = make_summary_prune_proposal(
        prune_class=SummaryPruneClass.KEEP_DELIVERY_ARCHIVE,
        sequence=1,
        summary_ack_ledger_report=ack,
        delivery_archive_report=archive,
        settlement_fence_report=fence,
        keep_archive_memory=False,
        family_id="prune-a",
        path_family_id="prune-path-a",
    )
    report = assess_summary_prune_fence(
        summary_ack_ledger_report=ack,
        delivery_archive_report=archive,
        settlement_fence_report=fence,
        proposals=(proposal,),
        required_classes=(SummaryPruneClass.KEEP_DELIVERY_ARCHIVE,),
        min_family_count=1,
        min_path_family_count=1,
    )
    assert report.decision_kind is SummaryPruneDecisionKind.QUARANTINE_ARCHIVE_MEMORY_DROPPED


def test_summary_ack_fold_audit_passes() -> None:
    root = Path(__file__).resolve().parents[1]
    report = audit_summary_ack_fold(root, artifact_stem=root.name)
    assert report.status == "pass"
    assert report.error_count == 0
