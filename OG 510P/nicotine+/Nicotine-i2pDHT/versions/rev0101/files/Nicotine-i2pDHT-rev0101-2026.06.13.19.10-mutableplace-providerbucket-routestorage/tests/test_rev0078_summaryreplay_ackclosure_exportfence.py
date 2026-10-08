from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from i2p_dht_lab.ackclosure import AckClosureClass, AckClosureDecisionKind, assess_ack_closure, make_ack_closure_marker
from i2p_dht_lab.moderationquarantine import ZERO_DIGEST
from i2p_dht_lab.summaryexportfence import SummaryExportClass, SummaryExportDecisionKind, assess_summary_export_fence, make_summary_export_marker
from i2p_dht_lab.summaryreplay import SummaryReplayClass, SummaryReplayDecisionKind, assess_summary_replay, make_summary_replay_marker
from i2p_dht_lab.summaryreplayfold import audit_summary_replay_fold
from test_rev0077_summaryackledger_deliveryarchive_prunefence import accepted_delivery_archive, accepted_summary_ack_ledger, accepted_summary_prune_fence


def accepted_summary_replay():
    prune, archive, ack, fence = accepted_summary_prune_fence()
    markers = []
    prev = ZERO_DIGEST
    classes = (
        SummaryReplayClass.ACK_LEDGER,
        SummaryReplayClass.DELIVERY_ARCHIVE,
        SummaryReplayClass.PRUNE_FENCE,
        SummaryReplayClass.RESTART_GENERATION,
        SummaryReplayClass.REDACTION_MEMORY,
        SummaryReplayClass.CONTRADICTION_MEMORY,
    )
    for seq, cls in enumerate(classes, start=1):
        marker = make_summary_replay_marker(
            replay_class=cls,
            sequence=seq,
            previous_digest=prev,
            restart_generation=9,
            previous_restart_generation=8,
            summary_ack_ledger_report=ack,
            delivery_archive_report=archive,
            summary_prune_fence_report=prune,
            family_id=f"replay-{seq}",
            path_family_id=f"replay-path-{seq}",
        )
        markers.append(marker)
        prev = marker.marker_digest
    report = assess_summary_replay(summary_ack_ledger_report=ack, delivery_archive_report=archive, summary_prune_fence_report=prune, markers=tuple(markers), previous_digest=ZERO_DIGEST)
    assert report.decision_kind is SummaryReplayDecisionKind.ACCEPT_SUMMARY_REPLAYED
    return report, prune, archive, ack, fence


def accepted_ack_closure():
    replay, prune, archive, ack, fence = accepted_summary_replay()
    markers = []
    prev = ZERO_DIGEST
    classes = (
        AckClosureClass.ACK_LEDGER,
        AckClosureClass.DELIVERY_ARCHIVE,
        AckClosureClass.PRUNE_FENCE,
        AckClosureClass.SUMMARY_REPLAY,
        AckClosureClass.REDACTION_MEMORY,
        AckClosureClass.CONTRADICTION_MEMORY,
    )
    for seq, cls in enumerate(classes, start=1):
        marker = make_ack_closure_marker(
            closure_class=cls,
            sequence=seq,
            previous_digest=prev,
            summary_ack_ledger_report=ack,
            delivery_archive_report=archive,
            summary_prune_fence_report=prune,
            summary_replay_report=replay,
            family_id=f"closure-{seq}",
            path_family_id=f"closure-path-{seq}",
        )
        markers.append(marker)
        prev = marker.marker_digest
    report = assess_ack_closure(summary_ack_ledger_report=ack, delivery_archive_report=archive, summary_prune_fence_report=prune, summary_replay_report=replay, markers=tuple(markers), previous_digest=ZERO_DIGEST)
    assert report.decision_kind is AckClosureDecisionKind.ACCEPT_ACK_CLOSED
    return report, replay, prune, archive, ack, fence


def accepted_summary_export_fence():
    closure, replay, prune, archive, ack, fence = accepted_ack_closure()
    markers = []
    prev = ZERO_DIGEST
    classes = (
        SummaryExportClass.ACK_CLOSURE,
        SummaryExportClass.SUMMARY_REPLAY,
        SummaryExportClass.DELIVERY_ARCHIVE,
        SummaryExportClass.SUMMARY_PRUNE_FENCE,
        SummaryExportClass.REDACTED_SUMMARY,
        SummaryExportClass.CONTRADICTION_MEMORY,
    )
    for seq, cls in enumerate(classes, start=1):
        marker = make_summary_export_marker(
            export_class=cls,
            sequence=seq,
            previous_digest=prev,
            ack_closure_report=closure,
            summary_replay_report=replay,
            delivery_archive_report=archive,
            summary_prune_fence_report=prune,
            family_id=f"export-{seq}",
            path_family_id=f"export-path-{seq}",
        )
        markers.append(marker)
        prev = marker.marker_digest
    report = assess_summary_export_fence(ack_closure_report=closure, summary_replay_report=replay, delivery_archive_report=archive, summary_prune_fence_report=prune, markers=tuple(markers), previous_digest=ZERO_DIGEST)
    assert report.decision_kind is SummaryExportDecisionKind.ACCEPT_SUMMARY_EXPORT_FENCED
    return report, closure, replay, prune, archive, ack, fence


def test_summary_replay_closure_export_happy_path() -> None:
    replay, *_ = accepted_summary_replay()
    closure, *_ = accepted_ack_closure()
    export, *_ = accepted_summary_export_fence()
    assert replay.summary_replayed and replay.restart_sticky and replay.contradiction_preserved
    assert closure.ack_closed and closure.terminal_local_summary_ack and closure.redacted
    assert export.summary_export_fenced and export.export_ready and export.contradiction_preserved


def test_summary_replay_quarantines_restart_rollback() -> None:
    prune, archive, ack, _fence = accepted_summary_prune_fence()
    marker = make_summary_replay_marker(
        replay_class=SummaryReplayClass.RESTART_GENERATION,
        sequence=1,
        restart_generation=3,
        previous_restart_generation=3,
        summary_ack_ledger_report=ack,
        delivery_archive_report=archive,
        summary_prune_fence_report=prune,
        family_id="replay-a",
        path_family_id="replay-path-a",
    )
    report = assess_summary_replay(summary_ack_ledger_report=ack, delivery_archive_report=archive, summary_prune_fence_report=prune, markers=(marker,), required_classes=(SummaryReplayClass.RESTART_GENERATION,), min_family_count=1, min_path_family_count=1)
    assert report.decision_kind is SummaryReplayDecisionKind.QUARANTINE_RESTART_ROLLBACK


def test_summary_replay_quarantines_contradiction_drop() -> None:
    prune, archive, ack, _fence = accepted_summary_prune_fence()
    marker = make_summary_replay_marker(
        replay_class=SummaryReplayClass.CONTRADICTION_MEMORY,
        sequence=1,
        summary_ack_ledger_report=ack,
        delivery_archive_report=archive,
        summary_prune_fence_report=prune,
        contradiction_carried=False,
        family_id="replay-a",
        path_family_id="replay-path-a",
    )
    report = assess_summary_replay(summary_ack_ledger_report=ack, delivery_archive_report=archive, summary_prune_fence_report=prune, markers=(marker,), required_classes=(SummaryReplayClass.CONTRADICTION_MEMORY,), min_family_count=1, min_path_family_count=1)
    assert report.decision_kind is SummaryReplayDecisionKind.QUARANTINE_CONTRADICTION_DROPPED


def test_ack_closure_holds_without_replay() -> None:
    replay, prune, archive, ack, _fence = accepted_summary_replay()
    pending_replay = replace(replay, summary_replayed=False, accept=False, watch=True)
    marker = make_ack_closure_marker(
        closure_class=AckClosureClass.SUMMARY_REPLAY,
        sequence=1,
        summary_ack_ledger_report=ack,
        delivery_archive_report=archive,
        summary_prune_fence_report=prune,
        summary_replay_report=pending_replay,
        family_id="closure-a",
        path_family_id="closure-path-a",
    )
    report = assess_ack_closure(summary_ack_ledger_report=ack, delivery_archive_report=archive, summary_prune_fence_report=prune, summary_replay_report=pending_replay, markers=(marker,), required_classes=(AckClosureClass.SUMMARY_REPLAY,), min_family_count=1, min_path_family_count=1)
    assert report.decision_kind is AckClosureDecisionKind.HOLD_REPLAY_PENDING


def test_ack_closure_quarantines_digest_drift() -> None:
    replay, prune, archive, ack, _fence = accepted_summary_replay()
    marker = make_ack_closure_marker(
        closure_class=AckClosureClass.SUMMARY_REPLAY,
        sequence=1,
        summary_ack_ledger_report=ack,
        delivery_archive_report=archive,
        summary_prune_fence_report=prune,
        summary_replay_report=replay,
        family_id="closure-a",
        path_family_id="closure-path-a",
    )
    bad = replace(marker, summary_replay_digest=ZERO_DIGEST)
    report = assess_ack_closure(summary_ack_ledger_report=ack, delivery_archive_report=archive, summary_prune_fence_report=prune, summary_replay_report=replay, markers=(bad,), required_classes=(AckClosureClass.SUMMARY_REPLAY,), min_family_count=1, min_path_family_count=1)
    assert report.decision_kind is AckClosureDecisionKind.QUARANTINE_DIGEST_DRIFT


def test_summary_export_quarantines_raw_leak() -> None:
    closure, replay, prune, archive, _ack, _fence = accepted_ack_closure()
    marker = make_summary_export_marker(
        export_class=SummaryExportClass.REDACTED_SUMMARY,
        sequence=1,
        ack_closure_report=closure,
        summary_replay_report=replay,
        delivery_archive_report=archive,
        summary_prune_fence_report=prune,
        raw_payload_exposed=True,
        family_id="export-a",
        path_family_id="export-path-a",
    )
    report = assess_summary_export_fence(ack_closure_report=closure, summary_replay_report=replay, delivery_archive_report=archive, summary_prune_fence_report=prune, markers=(marker,), required_classes=(SummaryExportClass.REDACTED_SUMMARY,), min_family_count=1, min_path_family_count=1)
    assert report.decision_kind is SummaryExportDecisionKind.QUARANTINE_RAW_LEAK


def test_summary_export_quarantines_redaction_drop() -> None:
    closure, replay, prune, archive, _ack, _fence = accepted_ack_closure()
    marker = make_summary_export_marker(
        export_class=SummaryExportClass.REDACTED_SUMMARY,
        sequence=1,
        ack_closure_report=closure,
        summary_replay_report=replay,
        delivery_archive_report=archive,
        summary_prune_fence_report=prune,
        redaction_carried=False,
        family_id="export-a",
        path_family_id="export-path-a",
    )
    report = assess_summary_export_fence(ack_closure_report=closure, summary_replay_report=replay, delivery_archive_report=archive, summary_prune_fence_report=prune, markers=(marker,), required_classes=(SummaryExportClass.REDACTED_SUMMARY,), min_family_count=1, min_path_family_count=1)
    assert report.decision_kind is SummaryExportDecisionKind.QUARANTINE_REDACTION_DROPPED


def test_summary_replay_fold_audit_passes() -> None:
    root = Path(__file__).resolve().parents[1]
    report = audit_summary_replay_fold(root, artifact_stem=root.name)
    assert report.status == "pass"
    assert report.error_count == 0
