from __future__ import annotations

from types import SimpleNamespace

from i2p_dht_lab.compactjoin import CompactJoinDecisionKind, assess_compact_join
from i2p_dht_lab.identity import DhtKeypair
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.moderationquarantine import ZERO_DIGEST
from i2p_dht_lab.outboxdrain import OutboxDrainAction, OutboxDrainDecisionKind, OutboxDrainPhase, assess_outbox_drain, make_outbox_drain_receipt
from i2p_dht_lab.publicoutbox import PublicOutboxAction, PublicOutboxDecisionKind, PublicOutboxReport
from i2p_dht_lab.samcanary import SamCanaryDecisionKind, assess_sam_canary, make_sam_canary
from i2p_dht_lab.drainfold import audit_drain_fold

NOW = 50_000
PROFILE = "profile-rev0050"
SERVICE = "public-bridge-rev0050"
SCOPE = sha256(b"rev0050-scope")
REQUEST = sha256(b"rev0050-request")
SUBJECT = sha256(b"rev0050-subject")
PAYLOAD = sha256(b"rev0050-public-payload")
ENTRY = sha256(b"rev0050-outbox-entry")
IDEM = sha256(b"rev0050-idempotency")
FRAME = sha256(b"rev0050-frame")


def kp(n: int) -> DhtKeypair:
    return DhtKeypair.from_seed(bytes([n]) * 32)


def d(label: str) -> bytes:
    return sha256(label.encode("utf-8"))


def component(label: str, *, accept: bool = True, watch: bool = False, quarantined: bool = False, decision: str = "accept"):
    return SimpleNamespace(
        report_digest=d(f"{label}:{accept}:{watch}:{quarantined}:{decision}"),
        transcript_digest=d(f"{label}:transcript:{accept}:{watch}:{quarantined}:{decision}"),
        accept=accept,
        watch=watch,
        quarantined=quarantined,
        decision_kind=SimpleNamespace(value=decision),
    )


def outbox_report(*, watch: bool = False) -> PublicOutboxReport:
    return PublicOutboxReport(
        decision_kind=PublicOutboxDecisionKind.ACCEPT_WITH_WATCH if watch else PublicOutboxDecisionKind.ACCEPT_STAGED,
        accept=True,
        watch=watch,
        reason="test outbox",
        profile_id=PROFILE,
        service_name=SERVICE,
        action=PublicOutboxAction.QUEUE_REFRESH,
        scope_digest=SCOPE,
        request_digest=REQUEST,
        payload_digest=PAYLOAD,
        accepted_entry_digest=ENTRY,
        idempotency_key=IDEM,
        bridge_shadow_digest=d("shadow"),
        audit_quorum_digest=d("audit"),
        redress_gc_digest=d("redress"),
        family_count=2,
        path_family_count=2,
        highest_sequence=1,
        report_digest=d(f"outbox-report:{watch}"),
    )


def drain_receipts(outbox=None, *, effect=None, phase=OutboxDrainPhase.COMMIT):
    outbox = outbox or outbox_report()
    effect = effect or d("drain-effect")
    dry = component("dry")
    sam = component("sam")
    journal = component("journal")
    r0 = make_outbox_drain_receipt(
        keypair=kp(1),
        phase=phase,
        action=OutboxDrainAction.DRAIN_REFRESH,
        profile_id=PROFILE,
        service_name=SERVICE,
        scope_digest=SCOPE,
        request_digest=REQUEST,
        payload_digest=PAYLOAD,
        outbox_report_digest=outbox.report_digest,
        outbox_entry_digest=outbox.accepted_entry_digest,
        dry_run_report_digest=dry.report_digest,
        sam_trace_digest=sam.report_digest,
        scope_journal_digest=journal.report_digest,
        idempotency_key=IDEM,
        drain_effect_digest=effect,
        sequence=0,
        issued_at=NOW,
        expires_at=NOW + 300,
        family_id="family-a",
        path_family="path-a",
    )
    r1 = make_outbox_drain_receipt(
        keypair=kp(2),
        phase=phase,
        action=OutboxDrainAction.DRAIN_REFRESH,
        profile_id=PROFILE,
        service_name=SERVICE,
        scope_digest=SCOPE,
        request_digest=REQUEST,
        payload_digest=PAYLOAD,
        outbox_report_digest=outbox.report_digest,
        outbox_entry_digest=outbox.accepted_entry_digest,
        dry_run_report_digest=dry.report_digest,
        sam_trace_digest=sam.report_digest,
        scope_journal_digest=journal.report_digest,
        idempotency_key=IDEM,
        drain_effect_digest=effect,
        sequence=1,
        previous_receipt_digest=r0.receipt_digest,
        issued_at=NOW + 1,
        expires_at=NOW + 301,
        family_id="family-b",
        path_family="path-b",
    )
    return (r0, r1), dry, sam, journal


def assess_good_drain(*, watch_outbox: bool = False, allow_watch: bool = False):
    outbox = outbox_report(watch=watch_outbox)
    receipts, dry, sam, journal = drain_receipts(outbox)
    return assess_outbox_drain(
        receipts,
        outbox_report=outbox,
        dry_run_report=dry,
        sam_trace_report=sam,
        scope_journal_report=journal,
        now=NOW + 2,
        expected_profile_id=PROFILE,
        expected_service_name=SERVICE,
        expected_scope_digest=SCOPE,
        expected_request_digest=REQUEST,
        expected_payload_digest=PAYLOAD,
        allow_component_watch=allow_watch,
    ), outbox, receipts, dry, sam, journal


def test_outbox_drain_accepts_exact_commit_receipts() -> None:
    report, *_ = assess_good_drain()
    assert report.decision_kind is OutboxDrainDecisionKind.ACCEPT_COMMIT_RECEIPT
    assert report.accept
    assert report.idempotency_key == IDEM
    assert report.family_count == 2


def test_outbox_drain_holds_component_watch_until_explicitly_carried() -> None:
    report, *_ = assess_good_drain(watch_outbox=True, allow_watch=False)
    assert report.decision_kind is OutboxDrainDecisionKind.HOLD_COMPONENT_WATCH
    report2, *_ = assess_good_drain(watch_outbox=True, allow_watch=True)
    assert report2.decision_kind is OutboxDrainDecisionKind.ACCEPT_WITH_WATCH


def test_outbox_drain_rejects_idempotency_effect_conflict() -> None:
    outbox = outbox_report()
    receipts, dry, sam, journal = drain_receipts(outbox)
    bad = make_outbox_drain_receipt(
        keypair=kp(3),
        phase=OutboxDrainPhase.COMMIT,
        action=OutboxDrainAction.DRAIN_REFRESH,
        profile_id=PROFILE,
        service_name=SERVICE,
        scope_digest=SCOPE,
        request_digest=REQUEST,
        payload_digest=PAYLOAD,
        outbox_report_digest=outbox.report_digest,
        outbox_entry_digest=outbox.accepted_entry_digest,
        dry_run_report_digest=dry.report_digest,
        sam_trace_digest=sam.report_digest,
        scope_journal_digest=journal.report_digest,
        idempotency_key=IDEM,
        drain_effect_digest=d("different-effect"),
        sequence=2,
        previous_receipt_digest=receipts[-1].receipt_digest,
        issued_at=NOW + 2,
        expires_at=NOW + 302,
        family_id="family-c",
        path_family="path-c",
    )
    report = assess_outbox_drain(
        (*receipts, bad),
        outbox_report=outbox,
        dry_run_report=dry,
        sam_trace_report=sam,
        scope_journal_report=journal,
        now=NOW + 3,
        expected_profile_id=PROFILE,
        expected_service_name=SERVICE,
        expected_scope_digest=SCOPE,
        expected_request_digest=REQUEST,
        expected_payload_digest=PAYLOAD,
    )
    assert report.decision_kind is OutboxDrainDecisionKind.QUARANTINE_IDEMPOTENCY_CONFLICT


def test_sam_canary_accepts_after_drain_and_budget() -> None:
    drain, _, _, _, sam, _ = assess_good_drain()
    egress = component("egress")
    c0 = make_sam_canary(
        keypair=kp(4), profile_id=PROFILE, service_name=SERVICE, session_id="sess", destination="dest.b32.i2p", scope_digest=SCOPE, request_digest=REQUEST, payload_digest=PAYLOAD, outbox_drain_digest=drain.report_digest, sam_trace_digest=sam.report_digest, egress_report_digest=egress.report_digest, idempotency_key=IDEM, frame_digest=FRAME, canary_effect_digest=d("canary-effect"), sequence=0, issued_at=NOW, expires_at=NOW+300, family_id="family-a", path_family="path-a"
    )
    c1 = make_sam_canary(
        keypair=kp(5), profile_id=PROFILE, service_name=SERVICE, session_id="sess", destination="dest.b32.i2p", scope_digest=SCOPE, request_digest=REQUEST, payload_digest=PAYLOAD, outbox_drain_digest=drain.report_digest, sam_trace_digest=sam.report_digest, egress_report_digest=egress.report_digest, idempotency_key=IDEM, frame_digest=FRAME, canary_effect_digest=d("canary-effect"), sequence=1, previous_canary_digest=c0.canary_digest, issued_at=NOW+1, expires_at=NOW+301, family_id="family-b", path_family="path-b"
    )
    report = assess_sam_canary((c0, c1), outbox_drain=drain, sam_trace_report=sam, egress_report=egress, now=NOW+2, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_session_id="sess", expected_destination="dest.b32.i2p", expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_payload_digest=PAYLOAD, expected_frame_digest=FRAME)
    assert report.decision_kind is SamCanaryDecisionKind.ACCEPT_CANARY
    assert report.accept


def test_sam_canary_rejects_public_payload_label_leak() -> None:
    drain, _, _, _, sam, _ = assess_good_drain()
    egress = component("egress")
    c0 = make_sam_canary(keypair=kp(6), profile_id=PROFILE, service_name=SERVICE, session_id="sess", destination="dest.b32.i2p", scope_digest=SCOPE, request_digest=REQUEST, payload_digest=PAYLOAD, outbox_drain_digest=drain.report_digest, sam_trace_digest=sam.report_digest, egress_report_digest=egress.report_digest, idempotency_key=IDEM, frame_digest=FRAME, canary_effect_digest=d("canary-effect"), sequence=0, issued_at=NOW, expires_at=NOW+300, family_id="family-a", path_family="path-a", public_label="leaks forbidden-title")
    c1 = make_sam_canary(keypair=kp(7), profile_id=PROFILE, service_name=SERVICE, session_id="sess", destination="dest.b32.i2p", scope_digest=SCOPE, request_digest=REQUEST, payload_digest=PAYLOAD, outbox_drain_digest=drain.report_digest, sam_trace_digest=sam.report_digest, egress_report_digest=egress.report_digest, idempotency_key=IDEM, frame_digest=FRAME, canary_effect_digest=d("canary-effect"), sequence=1, previous_canary_digest=c0.canary_digest, issued_at=NOW+1, expires_at=NOW+301, family_id="family-b", path_family="path-b")
    report = assess_sam_canary((c0, c1), outbox_drain=drain, sam_trace_report=sam, egress_report=egress, now=NOW+2, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_session_id="sess", expected_destination="dest.b32.i2p", expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_payload_digest=PAYLOAD, expected_frame_digest=FRAME, forbid_public_payload_fragments=("forbidden-title",))
    assert report.decision_kind is SamCanaryDecisionKind.QUARANTINE_PUBLIC_PAYLOAD_LEAK


def test_compact_join_accepts_when_hard_negative_survives_in_witness_or_audit() -> None:
    hard = d("hard-negative")
    witness = SimpleNamespace(report_digest=d("witness"), accept=True, watch=True, quarantined=False, scope_digest=SCOPE, request_digest=REQUEST, retained_digests=(hard,), hard_negative_count=1, family_count=1, path_family_count=1)
    audit = SimpleNamespace(report_digest=d("audit-compact"), accept=True, watch=True, quarantined=False, refute_digests=(hard,), fork_evidence_digests=(), family_count=1, path_family_count=1)
    redress = SimpleNamespace(report_digest=d("redress-gc"), accept=True, watch=True, quarantined=False, hard_negative_count=1)
    journal = SimpleNamespace(report_digest=d("journal"), accept=True, watch=False, quarantined=False, scope_digest=SCOPE, request_digest=REQUEST, subject_digest=SUBJECT, entry_digests=(witness.report_digest, audit.report_digest, redress.report_digest))
    report = assess_compact_join(witness_compact=witness, audit_compact=audit, redress_gc=redress, scope_journal=journal, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_subject_digest=SUBJECT, live_hard_negative_digests=(hard,), required_component_digests=(witness.report_digest, audit.report_digest))
    assert report.decision_kind is CompactJoinDecisionKind.ACCEPT_WITH_WATCH
    assert hard in report.retained_hard_digests


def test_compact_join_quarantines_split_negative_evidence() -> None:
    hard = d("hard-negative")
    witness = SimpleNamespace(report_digest=d("witness"), accept=True, watch=True, quarantined=False, scope_digest=SCOPE, request_digest=REQUEST, retained_digests=(), hard_negative_count=1, family_count=1, path_family_count=1)
    audit = SimpleNamespace(report_digest=d("audit-compact"), accept=True, watch=True, quarantined=False, refute_digests=(), fork_evidence_digests=(), family_count=1, path_family_count=1)
    redress = SimpleNamespace(report_digest=d("redress-gc"), accept=True, watch=True, quarantined=False, hard_negative_count=1)
    journal = SimpleNamespace(report_digest=d("journal"), accept=True, watch=False, quarantined=False, scope_digest=SCOPE, request_digest=REQUEST, subject_digest=SUBJECT, entry_digests=(witness.report_digest, audit.report_digest, redress.report_digest))
    report = assess_compact_join(witness_compact=witness, audit_compact=audit, redress_gc=redress, scope_journal=journal, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_subject_digest=SUBJECT, live_hard_negative_digests=(hard,))
    assert report.decision_kind is CompactJoinDecisionKind.QUARANTINE_NEGATIVE_SPLIT


def test_drainfold_current_revision_audit_passes() -> None:
    report = audit_drain_fold(".", revision="rev0050", artifact_stem="Nicotine-i2pDHT-rev0050-test")
    assert report.status == "pass"
