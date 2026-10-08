from __future__ import annotations

from types import SimpleNamespace

from i2p_dht_lab.commitbarrier import CommitBarrierDecisionKind, PublicCommitAction, assess_commit_barrier, make_public_commit_candidate
from i2p_dht_lab.effectledger import EffectLedgerDecisionKind, EffectLedgerStatus, assess_effect_ledger, make_effect_ledger_entry
from i2p_dht_lab.identity import DhtKeypair
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.moderationquarantine import ZERO_DIGEST
from i2p_dht_lab.outboxdrain import OutboxDrainAction, OutboxDrainDecisionKind, OutboxDrainPhase, assess_outbox_drain, make_outbox_drain_receipt
from i2p_dht_lab.publicoutbox import PublicOutboxAction
from i2p_dht_lab.samcanary import SamCanaryDecisionKind, assess_sam_canary, make_sam_canary
from i2p_dht_lab.sendfold import audit_send_fold
from i2p_dht_lab.sendvalve import SendValveAction, SendValveDecisionKind, assess_send_valve, make_send_valve_authorization

NOW = 510_000
PROFILE = "profile-rev0051"
SERVICE = "public-bridge-rev0051"
SESSION = "sam-session-rev0051"
DESTINATION = "rev0051dest.b32.i2p"
SCOPE = sha256(b"rev0051-scope")
REQUEST = sha256(b"rev0051-request")
SUBJECT = sha256(b"rev0051-subject")
PAYLOAD = sha256(b"rev0051-public-payload")
FRAME = sha256(b"rev0051-frame")
IDEM = sha256(b"rev0051-idempotency")
EFFECT = sha256(b"rev0051-effect")
NEGATIVE = sha256(b"rev0051-hard-negative")


def kp(i: int) -> DhtKeypair:
    return DhtKeypair.from_seed(bytes([i]) * 32)


def d(label: str) -> bytes:
    return sha256(label.encode("utf-8"))


def component(label: str, *, accept: bool = True, watch: bool = False, quarantined: bool = False, action=PublicOutboxAction.QUEUE_REFRESH):
    return SimpleNamespace(
        report_digest=d(f"{label}:{accept}:{watch}:{quarantined}:{action}"),
        accept=accept,
        watch=watch,
        quarantined=quarantined,
        action=action,
        accepted_entry_digest=d(f"{label}:accepted-entry"),
        idempotency_key=IDEM,
        scope_digest=SCOPE,
        request_digest=REQUEST,
        payload_digest=PAYLOAD,
    )


def commit_bundle(*, watch: bool = False, allow_watch: bool = False):
    dry = component("dry", watch=watch)
    outbox = component("outbox")
    audit_gap = component("audit-gap")
    egress = component("egress")
    journal = component("journal")
    c0 = make_public_commit_candidate(
        keypair=kp(1), action=PublicCommitAction.COMMIT_REFRESH, profile_id=PROFILE, service_name=SERVICE,
        scope_digest=SCOPE, request_digest=REQUEST, subject_digest=SUBJECT, public_payload_digest=PAYLOAD,
        dry_run=dry, outbox=outbox, audit_gap=audit_gap, egress=egress, scope_journal=journal,
        idempotency_key=IDEM, public_effect_digest=EFFECT, sequence=0, issued_at=NOW, expires_at=NOW+200,
        family_id="commit-a", path_family="path-a",
    )
    c1 = make_public_commit_candidate(
        keypair=kp(2), action=PublicCommitAction.COMMIT_REFRESH, profile_id=PROFILE, service_name=SERVICE,
        scope_digest=SCOPE, request_digest=REQUEST, subject_digest=SUBJECT, public_payload_digest=PAYLOAD,
        dry_run=dry, outbox=outbox, audit_gap=audit_gap, egress=egress, scope_journal=journal,
        idempotency_key=IDEM, public_effect_digest=EFFECT, sequence=1, previous_commit_digest=c0.candidate_digest,
        issued_at=NOW+1, expires_at=NOW+201, family_id="commit-b", path_family="path-b",
    )
    report = assess_commit_barrier(
        (c0, c1), dry_run=dry, outbox=outbox, audit_gap=audit_gap, egress=egress, scope_journal=journal,
        now=NOW+2, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE,
        expected_request_digest=REQUEST, expected_subject_digest=SUBJECT, expected_public_payload_digest=PAYLOAD,
        allow_watch_debt=allow_watch,
    )
    return report, (c0, c1), dry, outbox, audit_gap, egress, journal


def drain_bundle():
    _, _, dry, outbox, _, _, journal = commit_bundle()
    sam_trace = component("sam-trace")
    r0 = make_outbox_drain_receipt(
        keypair=kp(3), phase=OutboxDrainPhase.PREPARE, action=OutboxDrainAction.DRAIN_REFRESH, profile_id=PROFILE,
        service_name=SERVICE, scope_digest=SCOPE, request_digest=REQUEST, payload_digest=PAYLOAD,
        outbox_report_digest=outbox.report_digest, outbox_entry_digest=outbox.accepted_entry_digest,
        dry_run_report_digest=dry.report_digest, sam_trace_digest=sam_trace.report_digest, scope_journal_digest=journal.report_digest,
        idempotency_key=IDEM, drain_effect_digest=EFFECT, sequence=0, issued_at=NOW, expires_at=NOW+200,
        family_id="drain-a", path_family="drain-path-a",
    )
    r1 = make_outbox_drain_receipt(
        keypair=kp(4), phase=OutboxDrainPhase.COMMIT, action=OutboxDrainAction.DRAIN_REFRESH, profile_id=PROFILE,
        service_name=SERVICE, scope_digest=SCOPE, request_digest=REQUEST, payload_digest=PAYLOAD,
        outbox_report_digest=outbox.report_digest, outbox_entry_digest=outbox.accepted_entry_digest,
        dry_run_report_digest=dry.report_digest, sam_trace_digest=sam_trace.report_digest, scope_journal_digest=journal.report_digest,
        idempotency_key=IDEM, drain_effect_digest=EFFECT, sequence=1, previous_receipt_digest=r0.receipt_digest,
        issued_at=NOW+1, expires_at=NOW+201, family_id="drain-b", path_family="drain-path-b",
    )
    report = assess_outbox_drain(
        (r0, r1), outbox_report=outbox, dry_run_report=dry, sam_trace_report=sam_trace, scope_journal_report=journal,
        now=NOW+2, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE,
        expected_request_digest=REQUEST, expected_payload_digest=PAYLOAD,
    )
    return report, outbox, dry, sam_trace, journal


def canary_bundle(drain, sam_trace, egress):
    c0 = make_sam_canary(
        keypair=kp(5), profile_id=PROFILE, service_name=SERVICE, session_id=SESSION, destination=DESTINATION,
        scope_digest=SCOPE, request_digest=REQUEST, payload_digest=PAYLOAD, outbox_drain_digest=drain.report_digest,
        sam_trace_digest=sam_trace.report_digest, egress_report_digest=egress.report_digest, idempotency_key=IDEM,
        frame_digest=FRAME, canary_effect_digest=EFFECT, sequence=0, issued_at=NOW, expires_at=NOW+200,
        family_id="canary-a", path_family="canary-path-a",
    )
    c1 = make_sam_canary(
        keypair=kp(6), profile_id=PROFILE, service_name=SERVICE, session_id=SESSION, destination=DESTINATION,
        scope_digest=SCOPE, request_digest=REQUEST, payload_digest=PAYLOAD, outbox_drain_digest=drain.report_digest,
        sam_trace_digest=sam_trace.report_digest, egress_report_digest=egress.report_digest, idempotency_key=IDEM,
        frame_digest=FRAME, canary_effect_digest=EFFECT, sequence=1, previous_canary_digest=c0.canary_digest,
        issued_at=NOW+1, expires_at=NOW+201, family_id="canary-b", path_family="canary-path-b",
    )
    report = assess_sam_canary(
        (c0, c1), outbox_drain=drain, sam_trace_report=sam_trace, egress_report=egress, now=NOW+2,
        expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_session_id=SESSION,
        expected_destination=DESTINATION, expected_scope_digest=SCOPE, expected_request_digest=REQUEST,
        expected_payload_digest=PAYLOAD, expected_frame_digest=FRAME,
    )
    return report


def compact_join(*, watch: bool = False, accept: bool = True, quarantined: bool = False):
    return SimpleNamespace(report_digest=d(f"compact:{watch}:{accept}:{quarantined}"), accept=accept, watch=watch, quarantined=quarantined, retained_hard_digests=(NEGATIVE,) if watch else (), scope_digest=SCOPE, request_digest=REQUEST, subject_digest=SUBJECT)


def accepted_send_components(*, compact_watch: bool = False, allow_watch: bool = False):
    commit, _, _, _, _, egress, journal = commit_bundle()
    drain, _, _, sam_trace, _ = drain_bundle()
    assert commit.decision_kind is CommitBarrierDecisionKind.ACCEPT_COMMIT_READY
    assert drain.decision_kind is OutboxDrainDecisionKind.ACCEPT_COMMIT_RECEIPT
    canary = canary_bundle(drain, sam_trace, egress)
    assert canary.decision_kind is SamCanaryDecisionKind.ACCEPT_CANARY
    compact = compact_join(watch=compact_watch)
    a0 = make_send_valve_authorization(
        keypair=kp(7), action=SendValveAction.SEND_REFRESH, profile_id=PROFILE, service_name=SERVICE,
        session_id=SESSION, destination=DESTINATION, scope_digest=SCOPE, request_digest=REQUEST,
        payload_digest=PAYLOAD, commit_barrier_digest=commit.report_digest, outbox_drain_digest=drain.report_digest,
        sam_canary_digest=canary.report_digest, compact_join_digest=compact.report_digest, frame_digest=FRAME,
        idempotency_key=IDEM, public_effect_digest=EFFECT, sequence=0, issued_at=NOW, expires_at=NOW+200,
        family_id="valve-a", path_family="valve-path-a",
    )
    a1 = make_send_valve_authorization(
        keypair=kp(8), action=SendValveAction.SEND_REFRESH, profile_id=PROFILE, service_name=SERVICE,
        session_id=SESSION, destination=DESTINATION, scope_digest=SCOPE, request_digest=REQUEST,
        payload_digest=PAYLOAD, commit_barrier_digest=commit.report_digest, outbox_drain_digest=drain.report_digest,
        sam_canary_digest=canary.report_digest, compact_join_digest=compact.report_digest, frame_digest=FRAME,
        idempotency_key=IDEM, public_effect_digest=EFFECT, sequence=1, previous_authorization_digest=a0.authorization_digest,
        issued_at=NOW+1, expires_at=NOW+201, family_id="valve-b", path_family="valve-path-b",
    )
    report = assess_send_valve(
        (a0, a1), commit_barrier=commit, outbox_drain=drain, sam_canary=canary, compact_join=compact,
        now=NOW+2, expected_action=SendValveAction.SEND_REFRESH, expected_profile_id=PROFILE,
        expected_service_name=SERVICE, expected_session_id=SESSION, expected_destination=DESTINATION,
        expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_payload_digest=PAYLOAD,
        expected_frame_digest=FRAME, allow_watch_debt=allow_watch,
    )
    return report, (a0, a1), commit, drain, canary, compact, journal


def test_folded_commit_barrier_accepts_branchlet_shape() -> None:
    commit, *_ = commit_bundle()
    assert commit.decision_kind is CommitBarrierDecisionKind.ACCEPT_COMMIT_READY
    assert commit.accept
    assert commit.family_count == 2


def test_send_valve_accepts_commit_drain_canary_compact_bundle() -> None:
    report, *_ = accepted_send_components()
    assert report.decision_kind is SendValveDecisionKind.ACCEPT_SEND_VALVE
    assert report.accept
    assert report.idempotency_key == IDEM
    assert report.public_effect_digest == EFFECT


def test_send_valve_holds_watch_debt_unless_explicitly_carried() -> None:
    report, *_ = accepted_send_components(compact_watch=True, allow_watch=False)
    assert report.decision_kind is SendValveDecisionKind.HOLD_WATCH_DEBT
    allowed, *_ = accepted_send_components(compact_watch=True, allow_watch=True)
    assert allowed.decision_kind is SendValveDecisionKind.ACCEPT_WITH_WATCH


def test_send_valve_quarantines_frame_or_component_drift_and_idempotency_conflict() -> None:
    report, auths, commit, drain, canary, compact, _ = accepted_send_components()
    bad_frame = assess_send_valve(auths, commit_barrier=commit, outbox_drain=drain, sam_canary=canary, compact_join=compact,
        now=NOW+2, expected_action=SendValveAction.SEND_REFRESH, expected_profile_id=PROFILE, expected_service_name=SERVICE,
        expected_session_id=SESSION, expected_destination=DESTINATION, expected_scope_digest=SCOPE, expected_request_digest=REQUEST,
        expected_payload_digest=PAYLOAD, expected_frame_digest=d("wrong-frame"))
    assert bad_frame.decision_kind is SendValveDecisionKind.QUARANTINE_COMPONENT_DIGEST_DRIFT
    replay = assess_send_valve(auths[-1:], commit_barrier=commit, outbox_drain=drain, sam_canary=canary, compact_join=compact,
        now=NOW+2, expected_action=SendValveAction.SEND_REFRESH, expected_profile_id=PROFILE, expected_service_name=SERVICE,
        expected_session_id=SESSION, expected_destination=DESTINATION, expected_scope_digest=SCOPE, expected_request_digest=REQUEST,
        expected_payload_digest=PAYLOAD, expected_frame_digest=FRAME, committed_idempotency_effects={IDEM: EFFECT}, min_family_diversity=1, min_path_diversity=1)
    assert replay.decision_kind is SendValveDecisionKind.ACCEPT_IDEMPOTENT_REPLAY
    conflict = assess_send_valve(auths[-1:], commit_barrier=commit, outbox_drain=drain, sam_canary=canary, compact_join=compact,
        now=NOW+2, expected_action=SendValveAction.SEND_REFRESH, expected_profile_id=PROFILE, expected_service_name=SERVICE,
        expected_session_id=SESSION, expected_destination=DESTINATION, expected_scope_digest=SCOPE, expected_request_digest=REQUEST,
        expected_payload_digest=PAYLOAD, expected_frame_digest=FRAME, committed_idempotency_effects={IDEM: d("wrong-effect")}, min_family_diversity=1, min_path_diversity=1)
    assert conflict.decision_kind is SendValveDecisionKind.QUARANTINE_IDEMPOTENCY_CONFLICT
    assert report.accept


def test_effect_ledger_accepts_idempotent_memory_after_send_valve() -> None:
    valve, _, _, _, _, compact, journal = accepted_send_components(compact_watch=True, allow_watch=True)
    e0 = make_effect_ledger_entry(keypair=kp(9), status=EffectLedgerStatus.COMMITTED_SHADOW, profile_id=PROFILE, service_name=SERVICE,
        scope_digest=SCOPE, request_digest=REQUEST, payload_digest=PAYLOAD, send_valve_digest=valve.report_digest,
        scope_journal_digest=journal.report_digest, compact_join_digest=compact.report_digest, idempotency_key=IDEM,
        public_effect_digest=EFFECT, negative_evidence_digest=NEGATIVE, sequence=0, issued_at=NOW, expires_at=NOW+200,
        family_id="ledger-a", path_family="ledger-path-a")
    e1 = make_effect_ledger_entry(keypair=kp(10), status=EffectLedgerStatus.COMMITTED_SHADOW, profile_id=PROFILE, service_name=SERVICE,
        scope_digest=SCOPE, request_digest=REQUEST, payload_digest=PAYLOAD, send_valve_digest=valve.report_digest,
        scope_journal_digest=journal.report_digest, compact_join_digest=compact.report_digest, idempotency_key=IDEM,
        public_effect_digest=EFFECT, negative_evidence_digest=NEGATIVE, sequence=1, previous_entry_digest=e0.entry_digest,
        issued_at=NOW+1, expires_at=NOW+201, family_id="ledger-b", path_family="ledger-path-b")
    report = assess_effect_ledger((e0, e1), send_valve=valve, scope_journal=journal, compact_join=compact, now=NOW+2,
        expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST,
        expected_payload_digest=PAYLOAD, required_negative_evidence_digest=NEGATIVE, allow_watch_debt=True)
    assert report.decision_kind is EffectLedgerDecisionKind.ACCEPT_WITH_WATCH
    assert report.retained_negative_digest == NEGATIVE


def test_effect_ledger_rejects_negative_split_and_idempotency_conflict() -> None:
    valve, _, _, _, _, compact, journal = accepted_send_components(compact_watch=True, allow_watch=True)
    entry = make_effect_ledger_entry(keypair=kp(11), status=EffectLedgerStatus.COMMITTED_SHADOW, profile_id=PROFILE, service_name=SERVICE,
        scope_digest=SCOPE, request_digest=REQUEST, payload_digest=PAYLOAD, send_valve_digest=valve.report_digest,
        scope_journal_digest=journal.report_digest, compact_join_digest=compact.report_digest, idempotency_key=IDEM,
        public_effect_digest=EFFECT, negative_evidence_digest=ZERO_DIGEST, sequence=0, issued_at=NOW, expires_at=NOW+200,
        family_id="ledger-a", path_family="ledger-path-a")
    split = assess_effect_ledger((entry,), send_valve=valve, scope_journal=journal, compact_join=compact, now=NOW+1,
        expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST,
        expected_payload_digest=PAYLOAD, required_negative_evidence_digest=NEGATIVE, min_family_diversity=1, min_path_diversity=1, allow_watch_debt=True)
    assert split.decision_kind is EffectLedgerDecisionKind.QUARANTINE_NEGATIVE_EVIDENCE_SPLIT
    conflict = assess_effect_ledger((entry,), send_valve=valve, scope_journal=journal, compact_join=compact, now=NOW+1,
        expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST,
        expected_payload_digest=PAYLOAD, committed_idempotency_effects={IDEM: d("other-effect")}, min_family_diversity=1, min_path_diversity=1, allow_watch_debt=True)
    assert conflict.decision_kind is EffectLedgerDecisionKind.QUARANTINE_IDEMPOTENCY_CONFLICT


def test_sendfold_current_revision_audit_passes() -> None:
    report = audit_send_fold(".", revision="rev0051", artifact_stem="Nicotine-i2pDHT-rev0051-test")
    assert report.status == "pass"
