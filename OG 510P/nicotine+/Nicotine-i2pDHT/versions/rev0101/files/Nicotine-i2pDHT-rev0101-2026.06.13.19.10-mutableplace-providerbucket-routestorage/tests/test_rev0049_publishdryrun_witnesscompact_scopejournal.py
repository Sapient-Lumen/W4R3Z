from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from i2p_dht_lab.identity import DhtKeypair
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.moderationquarantine import ZERO_DIGEST
from i2p_dht_lab.publishdryrun import (
    PublishChannel,
    PublishDryRunDecisionKind,
    assess_publish_dry_run,
    make_publish_dry_run_attempt,
)
from i2p_dht_lab.publishdryrunfold import audit_publish_dryrun_fold
from i2p_dht_lab.scopejournal import (
    ScopeJournalDecisionKind,
    ScopeJournalEntryKind,
    assess_scope_journal,
    make_scope_journal_entry,
)
from i2p_dht_lab.witnesscompact import (
    WitnessCompactDecisionKind,
    WitnessCompactItem,
    WitnessCompactItemKind,
    WitnessCompactPolicy,
    assess_witness_compaction,
)

NOW = 10_000
PROFILE = "profile-alpha"
SERVICE = "public-bridge"
SCOPE = sha256(b"scope-alpha")
REQUEST = sha256(b"request-alpha")
SUBJECT = sha256(b"subject-alpha")
PAYLOAD = sha256(b"payload-alpha")
K1 = DhtKeypair.from_seed(b"1" * 32)
K2 = DhtKeypair.from_seed(b"2" * 32)
K3 = DhtKeypair.from_seed(b"3" * 32)


def d(label: str) -> bytes:
    return sha256(label.encode())


def report(label: str, *, accept=True, watch=False, quarantined=False):
    return SimpleNamespace(report_digest=d(f"{label}-{accept}-{watch}-{quarantined}"), accept=accept, watch=watch, quarantined=quarantined, decision_kind="quarantine_x" if quarantined else "accept")


def attempt(keypair, seq: int, fam: str, path: str, shadow, audit, redress, *, channel=PublishChannel.PUBLIC_BRIDGE_RECORD, payload=PAYLOAD, subject=SUBJECT, previous=ZERO_DIGEST, transport=ZERO_DIGEST, effect=None):
    return make_publish_dry_run_attempt(
        keypair=keypair,
        channel=channel,
        profile_id=PROFILE,
        service_name=SERVICE,
        scope_digest=SCOPE,
        request_digest=REQUEST,
        subject_digest=subject,
        public_payload_digest=payload,
        bridge_shadow_digest=shadow.report_digest,
        audit_quorum_digest=audit.report_digest,
        redress_gc_digest=redress.report_digest,
        dry_effect_digest=effect or d(f"effect-{seq}-{fam}-{path}"),
        sequence=seq,
        previous_attempt_digest=previous,
        transport_shadow_digest=transport,
        issued_at=NOW,
        expires_at=NOW + 100,
        family_id=fam,
        path_family=path,
    )


def assess(attempts, shadow, audit, redress, **kwargs):
    return assess_publish_dry_run(
        attempts,
        bridge_shadow=shadow,
        audit_quorum=audit,
        redress_gc=redress,
        now=NOW + 1,
        expected_channel=kwargs.pop("channel", PublishChannel.PUBLIC_BRIDGE_RECORD),
        expected_profile_id=PROFILE,
        expected_service_name=SERVICE,
        expected_scope_digest=SCOPE,
        expected_request_digest=REQUEST,
        expected_subject_digest=kwargs.pop("subject", SUBJECT),
        expected_public_payload_digest=kwargs.pop("payload", PAYLOAD),
        **kwargs,
    )


def test_publish_dry_run_requires_component_acceptance_and_exact_boundary() -> None:
    shadow = report("shadow")
    audit = report("audit")
    redress = report("redress")
    attempts = (attempt(K1, 0, "fam-a", "path-a", shadow, audit, redress), attempt(K2, 1, "fam-b", "path-b", shadow, audit, redress))
    ok = assess(attempts, shadow, audit, redress)
    assert ok.decision_kind is PublishDryRunDecisionKind.ACCEPT_DRY_RUN
    assert ok.family_count == 2
    assert ok.path_family_count == 2
    assert ok.highest_sequence == 1

    held = assess(attempts, shadow, report("audit", accept=False, watch=True), redress)
    assert held.decision_kind is PublishDryRunDecisionKind.HOLD_AUDIT_QUORUM

    quarantined = assess(attempts, report("shadow", quarantined=True), audit, redress)
    assert quarantined.decision_kind is PublishDryRunDecisionKind.QUARANTINE_BRIDGE_SHADOW

    drift = (attempt(K1, 0, "fam-a", "path-a", shadow, audit, redress, payload=d("wrong-payload")),)
    assert assess(drift, shadow, audit, redress).decision_kind is PublishDryRunDecisionKind.QUARANTINE_PAYLOAD_DRIFT

    fork_a = attempt(K1, 3, "fam-a", "path-a", shadow, audit, redress, effect=d("fork-a"))
    fork_b = attempt(K2, 3, "fam-b", "path-b", shadow, audit, redress, effect=d("fork-b"))
    assert assess((fork_a, fork_b), shadow, audit, redress).decision_kind is PublishDryRunDecisionKind.QUARANTINE_SEQUENCE_FORK

    watch_component = report("redress", accept=True, watch=True)
    watch_attempts = (attempt(K1, 0, "fam-a", "path-a", shadow, audit, watch_component), attempt(K2, 1, "fam-b", "path-b", shadow, audit, watch_component))
    assert assess(watch_attempts, shadow, audit, watch_component).decision_kind is PublishDryRunDecisionKind.ACCEPT_WITH_WATCH
    assert assess(watch_attempts, shadow, audit, watch_component, allow_component_watch=False).decision_kind is PublishDryRunDecisionKind.HOLD_WATCH_COMPONENT


def witem(kind, seq: int, fam: str, *, path=None, evidence=None, expires=NOW + 100, byte_cost=10, pinned=False, subject=SUBJECT):
    return WitnessCompactItem(
        kind=kind,
        scope_digest=SCOPE,
        request_digest=REQUEST,
        subject_digest=subject,
        evidence_digest=evidence or d(f"witness-{kind.value}-{seq}-{fam}"),
        sequence=seq,
        issued_at=NOW,
        expires_at=expires,
        family_id=fam,
        path_family=path or f"path-{fam}",
        byte_cost=byte_cost,
        pinned=pinned,
    )


def test_witness_compaction_preserves_refutes_forks_and_redress_gaps() -> None:
    refute = witem(WitnessCompactItemKind.PAYLOAD_MISMATCH, 1, "fam-a", byte_cost=20)
    redress_gap = witem(WitnessCompactItemKind.REDRESS_GAP, 2, "fam-b", byte_cost=20)
    expired_soft = witem(WitnessCompactItemKind.SOFT_OBSERVATION, 3, "fam-c", expires=NOW + 1, byte_cost=20)
    result = assess_witness_compaction(
        (refute, redress_gap, expired_soft),
        now=NOW + 2,
        expected_scope_digest=SCOPE,
        expected_request_digest=REQUEST,
        expected_subject_digest=SUBJECT,
        live_refute_digests=(refute.item_digest,),
        redress_gap_digests=(redress_gap.item_digest,),
        policy=WitnessCompactPolicy(max_retained_bytes=80),
    )
    assert result.decision_kind is WitnessCompactDecisionKind.ACCEPT_WITH_WATCH
    assert refute.item_digest in result.retained_digests
    assert redress_gap.item_digest in result.retained_digests
    assert expired_soft.item_digest in result.dropped_digests

    too_big = witem(WitnessCompactItemKind.AUDIT_REFUTE, 4, "fam-hard", byte_cost=100)
    assert assess_witness_compaction((too_big,), now=NOW + 1, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_subject_digest=SUBJECT, live_refute_digests=(too_big.item_digest,), policy=WitnessCompactPolicy(max_retained_bytes=16)).decision_kind is WitnessCompactDecisionKind.HOLD_MEMORY_BUDGET

    fork_a = witem(WitnessCompactItemKind.FORK_EVIDENCE, 9, "fork-a", evidence=d("fork-a"))
    fork_b = witem(WitnessCompactItemKind.FORK_EVIDENCE, 9, "fork-b", evidence=d("fork-b"))
    assert assess_witness_compaction((fork_a, fork_b), now=NOW + 1, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_subject_digest=SUBJECT).decision_kind is WitnessCompactDecisionKind.QUARANTINE_SAME_SEQUENCE_CONFLICT

    drift = witem(WitnessCompactItemKind.AUDIT_OK, 5, "fam-d", subject=d("other-subject"))
    assert assess_witness_compaction((drift,), now=NOW + 1, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_subject_digest=SUBJECT).decision_kind is WitnessCompactDecisionKind.QUARANTINE_SUBJECT_DRIFT


def jentry(keypair, kind, seq: int, component: bytes, *, prev=ZERO_DIGEST, fam="fam-a", path="path-a", subject=SUBJECT):
    return make_scope_journal_entry(
        keypair=keypair,
        kind=kind,
        profile_id=PROFILE,
        service_name=SERVICE,
        scope_digest=SCOPE,
        request_digest=REQUEST,
        subject_digest=subject,
        component_digest=component,
        sequence=seq,
        previous_entry_digest=prev,
        issued_at=NOW + seq,
        family_id=fam,
        path_family=path,
    )


def assess_journal(entries, **kwargs):
    return assess_scope_journal(
        entries,
        expected_profile_id=PROFILE,
        expected_service_name=SERVICE,
        expected_scope_digest=SCOPE,
        expected_request_digest=REQUEST,
        expected_subject_digest=SUBJECT,
        **kwargs,
    )


def test_scope_journal_pins_public_side_effect_attempts_across_restart() -> None:
    e0 = jentry(K1, ScopeJournalEntryKind.PUBLISH_DRY_RUN, 0, d("publish-report"), fam="fam-a", path="path-a")
    e1 = jentry(K2, ScopeJournalEntryKind.WITNESS_COMPACT, 1, d("compact-report"), prev=e0.entry_digest, fam="fam-b", path="path-b")
    ok = assess_journal((e0, e1), required_component_digests=(d("publish-report"), d("compact-report")))
    assert ok.decision_kind is ScopeJournalDecisionKind.ACCEPT_JOURNAL
    assert ok.highest_sequence == 1
    assert ok.family_count == 2

    missing = assess_journal((e0,), required_component_digests=(d("publish-report"), d("compact-report")))
    assert missing.decision_kind is ScopeJournalDecisionKind.QUARANTINE_COMPONENT_DROP

    hard = jentry(K3, ScopeJournalEntryKind.HARD_NEGATIVE, 2, d("hard-negative"), prev=e1.entry_digest, fam="fam-c", path="path-c")
    accepted_watch = assess_journal((e0, e1, hard), live_hard_negative_digests=(d("hard-negative"),))
    assert accepted_watch.decision_kind is ScopeJournalDecisionKind.ACCEPT_WITH_WATCH

    hard_missing = assess_journal((e0, e1), live_hard_negative_digests=(d("hard-negative"),))
    assert hard_missing.decision_kind is ScopeJournalDecisionKind.QUARANTINE_HARD_NEGATIVE_DROP

    fork_a = jentry(K1, ScopeJournalEntryKind.PUBLISH_DRY_RUN, 0, d("fork-a"))
    fork_b = jentry(K2, ScopeJournalEntryKind.PUBLISH_DRY_RUN, 0, d("fork-b"))
    assert assess_journal((fork_a, fork_b)).decision_kind is ScopeJournalDecisionKind.QUARANTINE_SEQUENCE_FORK

    drift = jentry(K1, ScopeJournalEntryKind.PUBLISH_DRY_RUN, 0, d("drift"), subject=d("other-subject"))
    assert assess_journal((drift,)).decision_kind is ScopeJournalDecisionKind.QUARANTINE_SUBJECT_DRIFT


def test_publishdryrun_fold_current_path_visible() -> None:
    root = Path(__file__).resolve().parents[1]
    fold = audit_publish_dryrun_fold(root, revision="rev0049", artifact_stem="Nicotine-i2pDHT-rev0049-2026.06.06.03.50-publishdryrun-witnesscompact-scopejournal")
    assert fold.status == "pass"
    assert fold.error_count == 0
