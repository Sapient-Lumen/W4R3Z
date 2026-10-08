from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

from i2p_dht_lab.commitbarrier import (
    CommitBarrierDecisionKind,
    PublicCommitAction,
    assess_commit_barrier,
    make_public_commit_candidate,
)
from i2p_dht_lab.identity import DhtKeypair
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.moderationquarantine import ZERO_DIGEST
from i2p_dht_lab.outboxdrain import (
    DrainIntent,
    OutboxDrainDecisionKind,
    assess_outbox_drain,
    make_outbox_drain_step,
)
from i2p_dht_lab.publicedgefold import audit_public_edge_fold
from i2p_dht_lab.publicoutbox import PublicOutboxAction

NOW = 2_000_000
PROFILE = "profile-commit-alpha"
SERVICE = "public-bridge"
SCOPE = sha256(b"scope-commit-alpha")
REQUEST = sha256(b"request-commit-alpha")
SUBJECT = sha256(b"subject-commit-alpha")
PAYLOAD = sha256(b"payload-commit-alpha")
IDEM = sha256(b"idempotency-key-alpha")
EFFECT = sha256(b"public-effect-alpha")
K1 = DhtKeypair.from_seed(b"1" * 32)
K2 = DhtKeypair.from_seed(b"2" * 32)
K3 = DhtKeypair.from_seed(b"3" * 32)
K4 = DhtKeypair.from_seed(b"4" * 32)


def d(label: str) -> bytes:
    return sha256(label.encode("utf-8"))


def component(label: str, *, accept: bool = True, watch: bool = False, quarantined: bool = False, action=PublicOutboxAction.QUEUE_REFRESH):
    return SimpleNamespace(
        report_digest=d(f"{label}:{accept}:{watch}:{quarantined}:{action}"),
        accept=accept,
        watch=watch,
        quarantined=quarantined,
        action=action,
    )


def commit_candidate(keypair, seq: int, fam: str, path: str, dry, outbox, audit_gap, egress, journal, *, effect=EFFECT, idem=IDEM, previous=ZERO_DIGEST, payload=PAYLOAD, action=PublicCommitAction.COMMIT_REFRESH):
    return make_public_commit_candidate(
        keypair=keypair,
        action=action,
        profile_id=PROFILE,
        service_name=SERVICE,
        scope_digest=SCOPE,
        request_digest=REQUEST,
        subject_digest=SUBJECT,
        public_payload_digest=payload,
        dry_run=dry,
        outbox=outbox,
        audit_gap=audit_gap,
        egress=egress,
        scope_journal=journal,
        idempotency_key=idem,
        public_effect_digest=effect,
        sequence=seq,
        previous_commit_digest=previous,
        issued_at=NOW,
        expires_at=NOW + 100,
        family_id=fam,
        path_family=path,
    )


def accepted_commit(*, watch: bool = False, allow_watch: bool = False):
    dry = component("dry", watch=watch)
    outbox = component("outbox")
    audit_gap = component("audit-gap")
    egress = component("egress")
    journal = component("journal")
    first = commit_candidate(K1, 1, "commit-a", "path-a", dry, outbox, audit_gap, egress, journal)
    second = commit_candidate(K2, 2, "commit-b", "path-b", dry, outbox, audit_gap, egress, journal, previous=first.candidate_digest)
    report = assess_commit_barrier(
        (first, second),
        dry_run=dry,
        outbox=outbox,
        audit_gap=audit_gap,
        egress=egress,
        scope_journal=journal,
        now=NOW + 1,
        expected_profile_id=PROFILE,
        expected_service_name=SERVICE,
        expected_scope_digest=SCOPE,
        expected_request_digest=REQUEST,
        expected_subject_digest=SUBJECT,
        expected_public_payload_digest=PAYLOAD,
        allow_watch_debt=allow_watch,
    )
    return report, (first, second), (dry, outbox, audit_gap, egress, journal)


def drain_step(keypair, seq: int, fam: str, path: str, commit, outbox, egress, journal, *, effect=EFFECT, idem=IDEM, previous=ZERO_DIGEST, payload=PAYLOAD, intent=DrainIntent.DRAIN_REFRESH):
    return make_outbox_drain_step(
        keypair=keypair,
        intent=intent,
        profile_id=PROFILE,
        service_name=SERVICE,
        scope_digest=SCOPE,
        request_digest=REQUEST,
        public_payload_digest=payload,
        commit=commit,
        outbox=outbox,
        egress=egress,
        scope_journal=journal,
        idempotency_key=idem,
        public_effect_digest=effect,
        sequence=seq,
        previous_drain_digest=previous,
        issued_at=NOW,
        expires_at=NOW + 100,
        family_id=fam,
        path_family=path,
    )


def test_commit_barrier_accepts_exact_scope_public_edge_bundle():
    report, _, _ = accepted_commit()
    assert report.decision_kind is CommitBarrierDecisionKind.ACCEPT_COMMIT_READY
    assert report.accept
    assert report.idempotency_key == IDEM
    assert report.public_effect_digest == EFFECT
    assert report.family_count == 2
    assert report.path_family_count == 2


def test_commit_barrier_holds_watch_debt_unless_explicitly_allowed():
    report, _, _ = accepted_commit(watch=True, allow_watch=False)
    assert report.decision_kind is CommitBarrierDecisionKind.HOLD_WATCH_DEBT
    allowed, _, _ = accepted_commit(watch=True, allow_watch=True)
    assert allowed.decision_kind is CommitBarrierDecisionKind.ACCEPT_WITH_WATCH
    assert allowed.watch


def test_commit_barrier_quarantines_component_digest_drift_and_action_drift():
    dry = component("dry")
    outbox = component("outbox")
    audit_gap = component("audit-gap")
    egress = component("egress")
    journal = component("journal")
    wrong_dry = component("dry-wrong")
    candidate = commit_candidate(K1, 1, "commit-a", "path-a", wrong_dry, outbox, audit_gap, egress, journal)
    report = assess_commit_barrier(
        (candidate,),
        dry_run=dry,
        outbox=outbox,
        audit_gap=audit_gap,
        egress=egress,
        scope_journal=journal,
        now=NOW + 1,
        expected_profile_id=PROFILE,
        expected_service_name=SERVICE,
        expected_scope_digest=SCOPE,
        expected_request_digest=REQUEST,
        expected_subject_digest=SUBJECT,
        expected_public_payload_digest=PAYLOAD,
        min_family_diversity=1,
        min_path_diversity=1,
    )
    assert report.decision_kind is CommitBarrierDecisionKind.QUARANTINE_COMPONENT_DIGEST_DRIFT

    action_bad = commit_candidate(K1, 1, "commit-a", "path-a", dry, outbox, audit_gap, egress, journal, action=PublicCommitAction.COMMIT_WITHDRAW)
    action_report = assess_commit_barrier(
        (action_bad,),
        dry_run=dry,
        outbox=outbox,
        audit_gap=audit_gap,
        egress=egress,
        scope_journal=journal,
        now=NOW + 1,
        expected_profile_id=PROFILE,
        expected_service_name=SERVICE,
        expected_scope_digest=SCOPE,
        expected_request_digest=REQUEST,
        expected_subject_digest=SUBJECT,
        expected_public_payload_digest=PAYLOAD,
        expected_action=PublicCommitAction.COMMIT_REFRESH,
        min_family_diversity=1,
        min_path_diversity=1,
    )
    assert action_report.decision_kind is CommitBarrierDecisionKind.QUARANTINE_ACTION_DRIFT


def test_commit_barrier_idempotency_replay_is_not_effect_conflict():
    report, candidates, components = accepted_commit()
    _, _, _, _, _ = components
    replay = assess_commit_barrier(
        (candidates[1],),
        dry_run=components[0],
        outbox=components[1],
        audit_gap=components[2],
        egress=components[3],
        scope_journal=components[4],
        now=NOW + 1,
        expected_profile_id=PROFILE,
        expected_service_name=SERVICE,
        expected_scope_digest=SCOPE,
        expected_request_digest=REQUEST,
        expected_subject_digest=SUBJECT,
        expected_public_payload_digest=PAYLOAD,
        committed_idempotency_effects={IDEM: EFFECT},
        min_family_diversity=1,
        min_path_diversity=1,
    )
    assert replay.decision_kind is CommitBarrierDecisionKind.ACCEPT_IDEMPOTENT_REPLAY
    conflict = assess_commit_barrier(
        (candidates[1],),
        dry_run=components[0],
        outbox=components[1],
        audit_gap=components[2],
        egress=components[3],
        scope_journal=components[4],
        now=NOW + 1,
        expected_profile_id=PROFILE,
        expected_service_name=SERVICE,
        expected_scope_digest=SCOPE,
        expected_request_digest=REQUEST,
        expected_subject_digest=SUBJECT,
        expected_public_payload_digest=PAYLOAD,
        committed_idempotency_effects={IDEM: d("different-effect")},
        min_family_diversity=1,
        min_path_diversity=1,
    )
    assert conflict.decision_kind is CommitBarrierDecisionKind.QUARANTINE_IDEMPOTENCY_CONFLICT
    assert report.accept


def test_outbox_drain_accepts_after_commit_barrier_without_sending():
    commit, _, components = accepted_commit()
    outbox, egress, journal = components[1], components[3], components[4]
    first = drain_step(K3, 1, "drain-a", "drain-path-a", commit, outbox, egress, journal)
    second = drain_step(K4, 2, "drain-b", "drain-path-b", commit, outbox, egress, journal, previous=first.step_digest)
    report = assess_outbox_drain(
        (first, second),
        commit=commit,
        outbox=outbox,
        egress=egress,
        scope_journal=journal,
        now=NOW + 1,
        expected_profile_id=PROFILE,
        expected_service_name=SERVICE,
        expected_scope_digest=SCOPE,
        expected_request_digest=REQUEST,
        expected_public_payload_digest=PAYLOAD,
    )
    assert report.decision_kind is OutboxDrainDecisionKind.ACCEPT_DRAIN_READY
    assert report.accept
    assert report.idempotency_key == IDEM


def test_outbox_drain_rejects_watch_debt_component_drift_and_idempotency_conflict():
    commit, _, components = accepted_commit(watch=True, allow_watch=True)
    outbox, egress, journal = components[1], components[3], components[4]
    step = drain_step(K3, 1, "drain-a", "drain-path-a", commit, outbox, egress, journal)
    hold = assess_outbox_drain(
        (step,),
        commit=commit,
        outbox=outbox,
        egress=egress,
        scope_journal=journal,
        now=NOW + 1,
        expected_profile_id=PROFILE,
        expected_service_name=SERVICE,
        expected_scope_digest=SCOPE,
        expected_request_digest=REQUEST,
        expected_public_payload_digest=PAYLOAD,
        min_family_diversity=1,
        min_path_diversity=1,
    )
    assert hold.decision_kind is OutboxDrainDecisionKind.HOLD_WATCH_DEBT

    bad_step = drain_step(K3, 1, "drain-a", "drain-path-a", commit, component("outbox-other"), egress, journal)
    bad = assess_outbox_drain(
        (bad_step,),
        commit=commit,
        outbox=outbox,
        egress=egress,
        scope_journal=journal,
        now=NOW + 1,
        expected_profile_id=PROFILE,
        expected_service_name=SERVICE,
        expected_scope_digest=SCOPE,
        expected_request_digest=REQUEST,
        expected_public_payload_digest=PAYLOAD,
        min_family_diversity=1,
        min_path_diversity=1,
        allow_watch_debt=True,
    )
    assert bad.decision_kind is OutboxDrainDecisionKind.QUARANTINE_COMPONENT_DIGEST_DRIFT

    conflict = assess_outbox_drain(
        (step,),
        commit=commit,
        outbox=outbox,
        egress=egress,
        scope_journal=journal,
        now=NOW + 1,
        expected_profile_id=PROFILE,
        expected_service_name=SERVICE,
        expected_scope_digest=SCOPE,
        expected_request_digest=REQUEST,
        expected_public_payload_digest=PAYLOAD,
        min_family_diversity=1,
        min_path_diversity=1,
        allow_watch_debt=True,
        already_drained_idempotency_effects={IDEM: d("wrong-effect")},
    )
    assert conflict.decision_kind is OutboxDrainDecisionKind.QUARANTINE_IDEMPOTENCY_CONFLICT


def test_commit_and_drain_detect_signature_and_sequence_forks():
    dry = component("dry")
    outbox = component("outbox")
    audit_gap = component("audit-gap")
    egress = component("egress")
    journal = component("journal")
    a = commit_candidate(K1, 1, "fam-a", "path-a", dry, outbox, audit_gap, egress, journal)
    bad_sig = replace(a, signature=b"0" * 64)
    sig_report = assess_commit_barrier(
        (bad_sig,),
        dry_run=dry,
        outbox=outbox,
        audit_gap=audit_gap,
        egress=egress,
        scope_journal=journal,
        now=NOW + 1,
        expected_profile_id=PROFILE,
        expected_service_name=SERVICE,
        expected_scope_digest=SCOPE,
        expected_request_digest=REQUEST,
        expected_subject_digest=SUBJECT,
        expected_public_payload_digest=PAYLOAD,
        min_family_diversity=1,
        min_path_diversity=1,
    )
    assert sig_report.decision_kind is CommitBarrierDecisionKind.QUARANTINE_BAD_SIGNATURE
    fork = commit_candidate(K2, 1, "fam-b", "path-b", dry, outbox, audit_gap, egress, journal, effect=d("fork-effect"))
    fork_report = assess_commit_barrier(
        (a, fork),
        dry_run=dry,
        outbox=outbox,
        audit_gap=audit_gap,
        egress=egress,
        scope_journal=journal,
        now=NOW + 1,
        expected_profile_id=PROFILE,
        expected_service_name=SERVICE,
        expected_scope_digest=SCOPE,
        expected_request_digest=REQUEST,
        expected_subject_digest=SUBJECT,
        expected_public_payload_digest=PAYLOAD,
    )
    assert fork_report.decision_kind is CommitBarrierDecisionKind.QUARANTINE_SEQUENCE_FORK


def test_public_edge_fold_audit_pins_rev0050_surface():
    root = Path(__file__).resolve().parents[1]
    report = audit_public_edge_fold(root, revision="rev0050", artifact_stem=root.name)
    assert report.status == "pass"
    assert report.predecessor_status == "pass"
