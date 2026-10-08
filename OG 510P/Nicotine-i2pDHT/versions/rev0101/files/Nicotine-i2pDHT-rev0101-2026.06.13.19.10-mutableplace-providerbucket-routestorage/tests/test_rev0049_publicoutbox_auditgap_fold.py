from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from i2p_dht_lab.auditgap import AuditGapDecisionKind, AuditGapSignalKind, assess_audit_gap, gap_signal
from i2p_dht_lab.auditquorum import AuditReceiptKind, assess_audit_quorum, make_audit_receipt
from i2p_dht_lab.bridgeshadow import BridgeShadowAction, BridgeShadowDecisionKind, assess_bridge_shadow, make_bridge_shadow_step
from i2p_dht_lab.identity import DhtKeypair
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.moderationquarantine import ZERO_DIGEST
from i2p_dht_lab.outboxfold import audit_outbox_fold
from i2p_dht_lab.publicationguard import PublicationIntent
from i2p_dht_lab.publicoutbox import PublicOutboxAction, PublicOutboxDecisionKind, assess_public_outbox, make_public_outbox_entry
from i2p_dht_lab.redressgc import RedressGcItem, RedressGcItemKind, RedressGcPolicy, assess_redress_gc

NOW = 1_900_000
PROFILE = "profile-alpha"
SERVICE = "public-bridge"
SCOPE = sha256(b"scope-alpha")
REQUEST = sha256(b"request-alpha")
PAYLOAD = sha256(b"payload-alpha")
SUBJECT = sha256(b"subject-alpha")
K1 = DhtKeypair.from_seed(b"A" * 32)
K2 = DhtKeypair.from_seed(b"B" * 32)
K3 = DhtKeypair.from_seed(b"C" * 32)
K4 = DhtKeypair.from_seed(b"D" * 32)
K5 = DhtKeypair.from_seed(b"E" * 32)
K6 = DhtKeypair.from_seed(b"F" * 32)


def d(label: str) -> bytes:
    return sha256(label.encode())


def component(label: str, *, accept: bool = True, watch: bool = False, quarantined: bool = False, quench: bool = False, continue_publication: bool = True):
    return SimpleNamespace(
        report_digest=d(f"{label}-{accept}-{watch}-{quarantined}-{quench}-{continue_publication}"),
        accept=accept,
        watch=watch,
        quarantined=quarantined,
        quench=quench,
        continue_publication=continue_publication,
        intent=PublicationIntent.PUBLIC_REFRESH,
    )


def shadow_step(keypair, seq: int, fam: str, path: str, publication, ledger, quench, *, payload=PAYLOAD, effect=None, previous=ZERO_DIGEST):
    return make_bridge_shadow_step(
        keypair=keypair,
        action=BridgeShadowAction.SHADOW_REFRESH,
        profile_id=PROFILE,
        service_name=SERVICE,
        scope_digest=SCOPE,
        request_digest=REQUEST,
        publication_report_digest=publication.report_digest,
        publication_ledger_digest=ledger.report_digest,
        quench_report_digest=quench.report_digest,
        payload_digest=payload,
        shadow_effect_digest=effect or d(f"shadow-effect-{seq}-{fam}-{path}"),
        sequence=seq,
        previous_shadow_digest=previous,
        issued_at=NOW,
        expires_at=NOW + 100,
        family_id=fam,
        path_family=path,
    )


def accepted_shadow(*, watch: bool = False):
    publication = component("publication", watch=watch)
    ledger = component("ledger")
    quench = component("quench")
    steps = (
        shadow_step(K1, 1, "shadow-a", "path-a", publication, ledger, quench),
        shadow_step(K2, 2, "shadow-b", "path-b", publication, ledger, quench),
    )
    report = assess_bridge_shadow(
        steps,
        publication=publication,
        publication_ledger=ledger,
        quench=quench,
        now=NOW + 1,
        expected_profile_id=PROFILE,
        expected_service_name=SERVICE,
        expected_scope_digest=SCOPE,
        expected_request_digest=REQUEST,
        expected_payload_digest=PAYLOAD,
    )
    assert report.decision_kind is (BridgeShadowDecisionKind.ACCEPT_WITH_WATCH if watch else BridgeShadowDecisionKind.ACCEPT_SHADOW)
    return report


def audit_receipt(kind: AuditReceiptKind, keypair, fam: str, path: str, shadow, *, payload=PAYLOAD, accepted: bool = True, watch: bool = False):
    return make_audit_receipt(
        keypair=keypair,
        kind=kind,
        profile_id=PROFILE,
        service_name=SERVICE,
        scope_digest=SCOPE,
        request_digest=REQUEST,
        bridge_shadow_digest=shadow.report_digest,
        public_payload_digest=payload,
        observation_digest=d(f"audit-{kind.value}-{fam}-{path}-{accepted}-{watch}"),
        issued_at=NOW,
        expires_at=NOW + 100,
        family_id=fam,
        path_family=path,
        accepted=accepted,
        watch=watch,
    )


def accepted_audit(shadow, *, watch: bool = False):
    receipts = (
        audit_receipt(AuditReceiptKind.PUBLICATION_OBSERVED, K3, "audit-a", "audit-path-a", shadow, watch=watch),
        audit_receipt(AuditReceiptKind.REPAIR_OBSERVED, K4, "audit-b", "audit-path-b", shadow),
    )
    report = assess_audit_quorum(receipts, bridge_shadow=shadow, now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_public_payload_digest=PAYLOAD)
    assert report.accept
    return report


def redress_empty():
    report = assess_redress_gc((), now=NOW + 1, expected_scope_digest=SCOPE, expected_request_digest=REQUEST)
    assert report.accept
    return report


def redress_hard():
    hard = RedressGcItem(RedressGcItemKind.HARD_NEGATIVE, SCOPE, REQUEST, SUBJECT, d("hard-negative"), 1, NOW, NOW + 100, "hard-family", byte_cost=8)
    report = assess_redress_gc((hard,), now=NOW + 1, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, live_hard_negative_digests=(hard.item_digest,), policy=RedressGcPolicy(max_retained_bytes=32))
    assert report.accept
    assert report.hard_negative_count == 1
    return report


def outbox_entry(keypair, seq: int, fam: str, path: str, shadow, audit, redress, *, action=PublicOutboxAction.QUEUE_REFRESH, payload=PAYLOAD, effect=None, idem=None, previous=ZERO_DIGEST):
    return make_public_outbox_entry(
        keypair=keypair,
        action=action,
        profile_id=PROFILE,
        service_name=SERVICE,
        scope_digest=SCOPE,
        request_digest=REQUEST,
        payload_digest=payload,
        bridge_shadow_digest=shadow.report_digest,
        audit_quorum_digest=audit.report_digest,
        redress_gc_digest=redress.report_digest,
        outbox_effect_digest=effect or d(f"effect-{seq}-{fam}-{path}"),
        idempotency_key=idem or d(f"idem-{seq}-{fam}-{path}"),
        sequence=seq,
        previous_entry_digest=previous,
        issued_at=NOW,
        expires_at=NOW + 100,
        family_id=fam,
        path_family=path,
    )


def staged_outbox(*, allow_watch_debt: bool = False):
    shadow = accepted_shadow(watch=allow_watch_debt)
    audit = accepted_audit(shadow)
    redress = redress_empty()
    entries = (
        outbox_entry(K5, 1, "out-a", "out-path-a", shadow, audit, redress),
        outbox_entry(K6, 2, "out-b", "out-path-b", shadow, audit, redress),
    )
    return assess_public_outbox(entries, bridge_shadow=shadow, audit_quorum=audit, redress_gc=redress, now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_payload_digest=PAYLOAD, allow_watch_debt=allow_watch_debt), shadow, audit, redress


def test_public_outbox_stages_after_shadow_audit_redress_join() -> None:
    report, shadow, audit, redress = staged_outbox()
    assert report.decision_kind is PublicOutboxDecisionKind.ACCEPT_STAGED
    assert report.family_count == 2
    assert report.path_family_count == 2

    action_drift = outbox_entry(K5, 1, "out-a", "out-path-a", shadow, audit, redress, action=PublicOutboxAction.QUEUE_WITHDRAW)
    assert assess_public_outbox((action_drift,), bridge_shadow=shadow, audit_quorum=audit, redress_gc=redress, now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_payload_digest=PAYLOAD).decision_kind is PublicOutboxDecisionKind.QUARANTINE_ACTION_DRIFT

    payload_drift = outbox_entry(K5, 1, "out-a", "out-path-a", shadow, audit, redress, payload=d("wrong-payload"))
    assert assess_public_outbox((payload_drift,), bridge_shadow=shadow, audit_quorum=audit, redress_gc=redress, now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_payload_digest=PAYLOAD).decision_kind is PublicOutboxDecisionKind.QUARANTINE_PAYLOAD_DRIFT

    stale_component = make_public_outbox_entry(keypair=K5, action=PublicOutboxAction.QUEUE_REFRESH, profile_id=PROFILE, service_name=SERVICE, scope_digest=SCOPE, request_digest=REQUEST, payload_digest=PAYLOAD, bridge_shadow_digest=d("wrong-shadow"), audit_quorum_digest=audit.report_digest, redress_gc_digest=redress.report_digest, outbox_effect_digest=d("effect"), idempotency_key=d("idem"), sequence=1, issued_at=NOW, expires_at=NOW + 100, family_id="out-a", path_family="out-path-a")
    assert assess_public_outbox((stale_component,), bridge_shadow=shadow, audit_quorum=audit, redress_gc=redress, now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_payload_digest=PAYLOAD).decision_kind is PublicOutboxDecisionKind.QUARANTINE_COMPONENT_DIGEST_DRIFT


def test_public_outbox_rejects_idempotency_conflict_and_sequence_fork() -> None:
    shadow = accepted_shadow()
    audit = accepted_audit(shadow)
    redress = redress_empty()
    idem = d("shared-idempotency")
    a = outbox_entry(K5, 1, "out-a", "out-path-a", shadow, audit, redress, idem=idem, effect=d("effect-a"))
    b = outbox_entry(K6, 2, "out-b", "out-path-b", shadow, audit, redress, idem=idem, effect=d("effect-b"))
    assert assess_public_outbox((a, b), bridge_shadow=shadow, audit_quorum=audit, redress_gc=redress, now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_payload_digest=PAYLOAD).decision_kind is PublicOutboxDecisionKind.QUARANTINE_IDEMPOTENCY_CONFLICT

    fork_a = outbox_entry(K5, 9, "out-a", "out-path-a", shadow, audit, redress, effect=d("fork-a"))
    fork_b = outbox_entry(K6, 9, "out-b", "out-path-b", shadow, audit, redress, effect=d("fork-b"))
    assert assess_public_outbox((fork_a, fork_b), bridge_shadow=shadow, audit_quorum=audit, redress_gc=redress, now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_payload_digest=PAYLOAD).decision_kind is PublicOutboxDecisionKind.QUARANTINE_SEQUENCE_FORK

    ok_replay = assess_public_outbox((a,), bridge_shadow=shadow, audit_quorum=audit, redress_gc=redress, now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_payload_digest=PAYLOAD, previously_committed_idempotency=(idem,), min_family_diversity=1, min_path_diversity=1)
    assert ok_replay.decision_kind is PublicOutboxDecisionKind.ACCEPT_IDEMPOTENT_REPLAY


def test_public_outbox_carries_watch_debt_and_hard_negative_pressure() -> None:
    shadow = accepted_shadow(watch=True)
    audit = accepted_audit(shadow)
    redress = redress_empty()
    entry = outbox_entry(K5, 1, "out-a", "out-path-a", shadow, audit, redress)
    assert assess_public_outbox((entry,), bridge_shadow=shadow, audit_quorum=audit, redress_gc=redress, now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_payload_digest=PAYLOAD, min_family_diversity=1, min_path_diversity=1).decision_kind is PublicOutboxDecisionKind.HOLD_WATCH_DEBT
    assert assess_public_outbox((entry,), bridge_shadow=shadow, audit_quorum=audit, redress_gc=redress, now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_payload_digest=PAYLOAD, min_family_diversity=1, min_path_diversity=1, allow_watch_debt=True).decision_kind is PublicOutboxDecisionKind.ACCEPT_WITH_WATCH

    clean_shadow = accepted_shadow()
    clean_audit = accepted_audit(clean_shadow)
    hard = redress_hard()
    hard_entry = outbox_entry(K5, 1, "out-a", "out-path-a", clean_shadow, clean_audit, hard)
    assert assess_public_outbox((hard_entry,), bridge_shadow=clean_shadow, audit_quorum=clean_audit, redress_gc=hard, now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_payload_digest=PAYLOAD, min_family_diversity=1, min_path_diversity=1).decision_kind is PublicOutboxDecisionKind.QUARANTINE_HARD_NEGATIVE_DROPPED
    assert assess_public_outbox((hard_entry,), bridge_shadow=clean_shadow, audit_quorum=clean_audit, redress_gc=hard, now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_payload_digest=PAYLOAD, min_family_diversity=1, min_path_diversity=1, allow_watch_debt=True).decision_kind is PublicOutboxDecisionKind.ACCEPT_WITH_WATCH


def test_audit_gap_repair_plans_do_not_treat_audits_as_truth() -> None:
    outbox, shadow, audit, redress = staged_outbox()
    no_gap = assess_audit_gap((gap_signal(AuditGapSignalKind.PUBLICATION_OBSERVED, scope_digest=SCOPE, request_digest=REQUEST, payload_digest=PAYLOAD, family_id="gap-a", path_family="gap-path-a"),), bridge_shadow=shadow, audit_quorum=audit, redress_gc=redress, outbox=outbox, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_payload_digest=PAYLOAD)
    assert no_gap.decision_kind is AuditGapDecisionKind.ACCEPT_NO_GAP

    stale = (
        gap_signal(AuditGapSignalKind.STALE_PUBLIC_RECORD, scope_digest=SCOPE, request_digest=REQUEST, payload_digest=PAYLOAD, family_id="gap-a", path_family="gap-path-a"),
        gap_signal(AuditGapSignalKind.STALE_PUBLIC_RECORD, scope_digest=SCOPE, request_digest=REQUEST, payload_digest=PAYLOAD, evidence_digest=d("stale"), family_id="gap-b", path_family="gap-path-b"),
    )
    withdraw = assess_audit_gap(stale, bridge_shadow=shadow, audit_quorum=audit, redress_gc=redress, outbox=outbox, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_payload_digest=PAYLOAD)
    assert withdraw.decision_kind is AuditGapDecisionKind.ACCEPT_WITHDRAW_PLAN
    assert withdraw.withdraw

    low = (gap_signal(AuditGapSignalKind.PAYLOAD_MISMATCH, scope_digest=SCOPE, request_digest=REQUEST, payload_digest=PAYLOAD, family_id="same", path_family="a"),)
    assert assess_audit_gap(low, bridge_shadow=shadow, audit_quorum=audit, redress_gc=redress, outbox=outbox, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_payload_digest=PAYLOAD).decision_kind is AuditGapDecisionKind.HOLD_LOW_SIGNAL_DIVERSITY

    drift = (gap_signal(AuditGapSignalKind.REDRESS_GAP, scope_digest=d("other-scope"), request_digest=REQUEST, payload_digest=PAYLOAD, family_id="gap-a", path_family="a"),)
    assert assess_audit_gap(drift, bridge_shadow=shadow, audit_quorum=audit, redress_gc=redress, outbox=outbox, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_payload_digest=PAYLOAD).decision_kind is AuditGapDecisionKind.QUARANTINE_SCOPE_DRIFT


def test_audit_gap_blocks_repair_when_outbox_or_hard_negative_pressure_disagree() -> None:
    outbox, shadow, audit, redress = staged_outbox()
    mismatch = (
        gap_signal(AuditGapSignalKind.PAYLOAD_MISMATCH, scope_digest=SCOPE, request_digest=REQUEST, payload_digest=PAYLOAD, evidence_digest=d("mismatch-a"), family_id="gap-a", path_family="gap-path-a"),
        gap_signal(AuditGapSignalKind.REDRESS_GAP, scope_digest=SCOPE, request_digest=REQUEST, payload_digest=PAYLOAD, evidence_digest=d("gap-b"), family_id="gap-b", path_family="gap-path-b"),
    )
    assert assess_audit_gap(mismatch, bridge_shadow=shadow, audit_quorum=audit, redress_gc=redress, outbox=None, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_payload_digest=PAYLOAD).decision_kind is AuditGapDecisionKind.HOLD_OUTBOX_NOT_STAGED
    repair = assess_audit_gap(mismatch, bridge_shadow=shadow, audit_quorum=audit, redress_gc=redress, outbox=outbox, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_payload_digest=PAYLOAD)
    assert repair.decision_kind is AuditGapDecisionKind.ACCEPT_REPAIR_PLAN
    assert repair.repair

    hard = redress_hard()
    hard_outbox_entry = outbox_entry(K5, 1, "out-a", "out-path-a", shadow, audit, hard)
    hard_outbox = assess_public_outbox((hard_outbox_entry,), bridge_shadow=shadow, audit_quorum=audit, redress_gc=hard, now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_payload_digest=PAYLOAD, min_family_diversity=1, min_path_diversity=1, allow_watch_debt=True)
    assert hard_outbox.accept
    assert assess_audit_gap(mismatch, bridge_shadow=shadow, audit_quorum=audit, redress_gc=hard, outbox=hard_outbox, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_payload_digest=PAYLOAD).decision_kind is AuditGapDecisionKind.QUARANTINE_REPAIR_WITH_HARD_NEGATIVE


def test_outbox_fold_current_path_visible() -> None:
    root = Path(__file__).resolve().parents[1]
    fold = audit_outbox_fold(root, revision="rev0049", artifact_stem="Nicotine-i2pDHT-rev0049-2026.06.06.03.50-publishdryrun-witnesscompact-scopejournal")
    assert fold.status == "pass"
    assert fold.error_count == 0
