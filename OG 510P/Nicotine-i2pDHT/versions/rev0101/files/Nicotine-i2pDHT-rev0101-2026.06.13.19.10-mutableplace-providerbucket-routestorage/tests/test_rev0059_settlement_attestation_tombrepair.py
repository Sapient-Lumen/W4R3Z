from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

from i2p_dht_lab.attestationpack import (
    AttestationPackDecisionKind,
    AttestationRole,
    assess_attestation_packs,
    component_from_report,
    make_attestation_pack,
)
from i2p_dht_lab.effectreconcile import EffectReconcileDecisionKind
from i2p_dht_lab.identity import DhtKeypair
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.moderationquarantine import ZERO_DIGEST
from i2p_dht_lab.retryquorum import RetryQuorumDecisionKind
from i2p_dht_lab.settlementfold import audit_settlement_fold
from i2p_dht_lab.settlementlane import (
    SettlementDecisionKind,
    SettlementKind,
    assess_settlement_entries,
    make_settlement_entry,
)
from i2p_dht_lab.sideeffectjournal import SideEffectAction, SideEffectPhase
from i2p_dht_lab.tombstonerepair import (
    TombstoneRepairDecisionKind,
    TombstoneRepairKind,
    assess_tombstone_repair,
    make_tombstone_repair_entry,
)

NOW = 580_000
PROFILE = "rev0059-profile"
SERVICE = "rev0059-public-edge"
SCOPE = sha256(b"rev0059-scope")
REQUEST = sha256(b"rev0059-request")
PAYLOAD = sha256(b"rev0059-payload")
IDEM = sha256(b"rev0059-idem")


def kp(n: int) -> DhtKeypair:
    return DhtKeypair.from_seed(bytes([n]) * 32)


def d(label: str) -> bytes:
    return sha256(label.encode("utf-8"))


def report(label: str, *, decision_kind, accept: bool = True, watch: bool = False, final_phase=None, hard: int = 0, dead_required: bool = False, retry_required: bool = False):
    return SimpleNamespace(
        report_digest=d(label),
        accept=accept,
        watch=watch,
        quarantined=False,
        decision_kind=decision_kind,
        action=SideEffectAction.OUTBOUND_PUBLIC_SEND,
        final_phase=final_phase,
        profile_id=PROFILE,
        service_name=SERVICE,
        scope_digest=SCOPE,
        request_digest=REQUEST,
        payload_digest=PAYLOAD,
        idempotency_key=IDEM,
        hard_negative_count=hard,
        dead_letter_required=dead_required,
        retry_required=retry_required,
    )


def retry_reconcile_report():
    return report(
        "effect-reconcile-retry",
        decision_kind=EffectReconcileDecisionKind.ACCEPT_RETRY,
        watch=True,
        final_phase=SideEffectPhase.PREPARE,
        dead_required=True,
        retry_required=True,
    )


def commit_reconcile_report():
    return report(
        "effect-reconcile-commit",
        decision_kind=EffectReconcileDecisionKind.ACCEPT_RECONCILED_COMMIT,
        final_phase=SideEffectPhase.COMMIT,
        dead_required=False,
        retry_required=False,
    )


def dead_report():
    return report("dead-letter", decision_kind=SimpleNamespace(value="accept_with_retry_watch"), accept=True, watch=True)


def retry_report():
    return report("retry-quorum", decision_kind=RetryQuorumDecisionKind.ACCEPT_RETRY_QUORUM, accept=True, watch=True)


def make_pack_report(effect=None, dead=None, retry=None):
    effect = effect or retry_reconcile_report()
    dead = dead or dead_report()
    retry = retry or retry_report()
    components = (
        component_from_report(AttestationRole.EFFECT_RECONCILE, effect),
        component_from_report(AttestationRole.DEAD_LETTER, dead),
        component_from_report(AttestationRole.RETRY_QUORUM, retry),
    )
    p0 = make_attestation_pack(keypair=kp(1), action=SideEffectAction.OUTBOUND_PUBLIC_SEND, profile_id=PROFILE, service_name=SERVICE, scope_digest=SCOPE, request_digest=REQUEST, payload_digest=PAYLOAD, idempotency_key=IDEM, components=components, sequence=0, issued_at=NOW, expires_at=NOW + 300, family_id="family-a", path_family="path-a")
    p1 = make_attestation_pack(keypair=kp(2), action=SideEffectAction.OUTBOUND_PUBLIC_SEND, profile_id=PROFILE, service_name=SERVICE, scope_digest=SCOPE, request_digest=REQUEST, payload_digest=PAYLOAD, idempotency_key=IDEM, components=components, sequence=1, previous_pack_digest=p0.pack_digest, issued_at=NOW + 1, expires_at=NOW + 301, family_id="family-b", path_family="path-b")
    pack = assess_attestation_packs(
        (p0, p1),
        action=SideEffectAction.OUTBOUND_PUBLIC_SEND,
        profile_id=PROFILE,
        service_name=SERVICE,
        scope_digest=SCOPE,
        request_digest=REQUEST,
        payload_digest=PAYLOAD,
        idempotency_key=IDEM,
        now=NOW + 2,
        required_roles=(AttestationRole.EFFECT_RECONCILE, AttestationRole.DEAD_LETTER),
        expected_role_digests={AttestationRole.EFFECT_RECONCILE: effect.report_digest, AttestationRole.DEAD_LETTER: dead.report_digest},
    )
    assert pack.accept
    return pack


def make_settlement_report(effect=None, dead=None, retry=None, pack=None):
    effect = effect or retry_reconcile_report()
    dead = dead or dead_report()
    retry = retry or retry_report()
    pack = pack or make_pack_report(effect, dead, retry)
    s0 = make_settlement_entry(keypair=kp(3), effect_reconcile_report=effect, dead_letter_report=dead, retry_quorum_report=retry, attestation_pack_report=pack, sequence=0, issued_at=NOW + 3, expires_at=NOW + 303, family_id="family-a", path_family="path-a")
    s1 = make_settlement_entry(keypair=kp(4), effect_reconcile_report=effect, dead_letter_report=dead, retry_quorum_report=retry, attestation_pack_report=pack, sequence=1, previous_entry_digest=s0.entry_digest, issued_at=NOW + 4, expires_at=NOW + 304, family_id="family-b", path_family="path-b")
    settled = assess_settlement_entries((s0, s1), effect_reconcile_report=effect, dead_letter_report=dead, retry_quorum_report=retry, attestation_pack_report=pack, now=NOW + 5)
    assert settled.accept
    return settled


def test_attestation_pack_accepts_diverse_typed_components_and_rejects_duplicate_role() -> None:
    effect = retry_reconcile_report()
    dead = dead_report()
    retry = retry_report()
    pack = make_pack_report(effect, dead, retry)
    assert pack.decision_kind is AttestationPackDecisionKind.ACCEPT_WITH_WATCH
    assert pack.family_count == 2
    assert (AttestationRole.EFFECT_RECONCILE, effect.report_digest) in pack.role_digests

    dup_components = (
        component_from_report(AttestationRole.EFFECT_RECONCILE, effect),
        component_from_report(AttestationRole.EFFECT_RECONCILE, dead),
    )
    dup = make_attestation_pack(keypair=kp(5), action=SideEffectAction.OUTBOUND_PUBLIC_SEND, profile_id=PROFILE, service_name=SERVICE, scope_digest=SCOPE, request_digest=REQUEST, payload_digest=PAYLOAD, idempotency_key=IDEM, components=dup_components, sequence=0, issued_at=NOW, expires_at=NOW + 300, family_id="family-x", path_family="path-x")
    verdict = assess_attestation_packs((dup,), action=SideEffectAction.OUTBOUND_PUBLIC_SEND, profile_id=PROFILE, service_name=SERVICE, scope_digest=SCOPE, request_digest=REQUEST, payload_digest=PAYLOAD, idempotency_key=IDEM, now=NOW + 1, min_family_count=1, min_path_family_count=1)
    assert verdict.decision_kind is AttestationPackDecisionKind.QUARANTINE_DUPLICATE_ROLE


def test_attestation_pack_rejects_digest_drift_replay_and_low_diversity() -> None:
    effect = retry_reconcile_report()
    dead = dead_report()
    retry = retry_report()
    component = component_from_report(AttestationRole.EFFECT_RECONCILE, effect)
    p0 = make_attestation_pack(keypair=kp(6), action=SideEffectAction.OUTBOUND_PUBLIC_SEND, profile_id=PROFILE, service_name=SERVICE, scope_digest=SCOPE, request_digest=REQUEST, payload_digest=PAYLOAD, idempotency_key=IDEM, components=(component,), sequence=0, issued_at=NOW, expires_at=NOW + 300, family_id="family-a", path_family="path-a")
    drift = assess_attestation_packs((p0,), action=SideEffectAction.OUTBOUND_PUBLIC_SEND, profile_id=PROFILE, service_name=SERVICE, scope_digest=SCOPE, request_digest=REQUEST, payload_digest=PAYLOAD, idempotency_key=IDEM, now=NOW + 1, expected_role_digests={AttestationRole.EFFECT_RECONCILE: d("wrong")}, min_family_count=1, min_path_family_count=1)
    assert drift.decision_kind is AttestationPackDecisionKind.QUARANTINE_DIGEST_DRIFT
    replay = assess_attestation_packs((p0,), action=SideEffectAction.OUTBOUND_PUBLIC_SEND, profile_id=PROFILE, service_name=SERVICE, scope_digest=SCOPE, request_digest=REQUEST, payload_digest=PAYLOAD, idempotency_key=IDEM, now=NOW + 1, previous_seen_pack_digests=(p0.pack_digest,), min_family_count=1, min_path_family_count=1)
    assert replay.decision_kind is AttestationPackDecisionKind.QUARANTINE_REPLAY
    low = assess_attestation_packs((p0,), action=SideEffectAction.OUTBOUND_PUBLIC_SEND, profile_id=PROFILE, service_name=SERVICE, scope_digest=SCOPE, request_digest=REQUEST, payload_digest=PAYLOAD, idempotency_key=IDEM, now=NOW + 1)
    assert low.decision_kind is AttestationPackDecisionKind.HOLD_LOW_FAMILY_DIVERSITY


def test_settlement_accepts_retry_hold_without_erasing_dead_letter() -> None:
    settled = make_settlement_report()
    assert settled.decision_kind is SettlementDecisionKind.ACCEPT_RETRY_HOLD
    assert settled.settlement_kind is SettlementKind.RETRY_HELD
    assert settled.watch
    assert settled.dead_letter_required
    assert settled.retry_required


def test_settlement_accepts_terminal_commit_and_rejects_retry_that_drops_dead_letter() -> None:
    effect = commit_reconcile_report()
    dead = report("dead-letter-terminal", decision_kind=SimpleNamespace(value="accept_dead_letter"), accept=True, watch=False)
    retry = None
    pack = make_pack_report(effect, dead, report("retry-zero", decision_kind=SimpleNamespace(value="none"), accept=True, watch=False))
    settled = make_settlement_report(effect=effect, dead=dead, retry=retry, pack=pack)
    assert settled.decision_kind is SettlementDecisionKind.ACCEPT_TERMINAL_SETTLEMENT
    assert not settled.watch

    effect = retry_reconcile_report()
    dead = dead_report()
    retry = retry_report()
    pack = make_pack_report(effect, dead, retry)
    bad = make_settlement_entry(keypair=kp(7), effect_reconcile_report=effect, dead_letter_report=dead, retry_quorum_report=retry, attestation_pack_report=pack, sequence=0, issued_at=NOW, expires_at=NOW + 300, family_id="family-a", path_family="path-a")
    unsigned_bad = replace(bad, dead_letter_required=False, signature=b"")
    bad = replace(unsigned_bad, signature=kp(7).sign(unsigned_bad.signature_payload()))
    verdict = assess_settlement_entries((bad,), effect_reconcile_report=effect, dead_letter_report=dead, retry_quorum_report=retry, attestation_pack_report=pack, now=NOW + 1, min_family_count=1, min_path_family_count=1)
    assert verdict.decision_kind is SettlementDecisionKind.QUARANTINE_RETRY_DROPS_DEAD_LETTER


def test_settlement_rejects_replay_and_component_digest_drift() -> None:
    effect = retry_reconcile_report()
    dead = dead_report()
    retry = retry_report()
    pack = make_pack_report(effect, dead, retry)
    s0 = make_settlement_entry(keypair=kp(8), effect_reconcile_report=effect, dead_letter_report=dead, retry_quorum_report=retry, attestation_pack_report=pack, sequence=0, issued_at=NOW, expires_at=NOW + 300, family_id="family-a", path_family="path-a")
    replay = assess_settlement_entries((s0,), effect_reconcile_report=effect, dead_letter_report=dead, retry_quorum_report=retry, attestation_pack_report=pack, now=NOW + 1, previous_seen_entry_digests=(s0.entry_digest,), min_family_count=1, min_path_family_count=1)
    assert replay.decision_kind is SettlementDecisionKind.QUARANTINE_REPLAY
    other_pack = replace(pack, report_digest=d("other-pack"))
    drift = assess_settlement_entries((s0,), effect_reconcile_report=effect, dead_letter_report=dead, retry_quorum_report=retry, attestation_pack_report=other_pack, now=NOW + 1, min_family_count=1, min_path_family_count=1)
    assert drift.decision_kind is SettlementDecisionKind.QUARANTINE_COMPONENT_DIGEST_DRIFT


def test_tombstone_repair_accepts_diverse_coverage_and_no_live_tombstones() -> None:
    settled = make_settlement_report()
    none = assess_tombstone_repair((), settlement_report=settled, expected_live_tombstone_count=0, now=NOW + 1)
    assert none.decision_kind is TombstoneRepairDecisionKind.ACCEPT_NO_LIVE_TOMBSTONES

    e0 = make_tombstone_repair_entry(keypair=kp(9), repair_kind=TombstoneRepairKind.TOMBSTONE_CARRIED, settlement_report=settled, tombstone_digest=d("tomb-a"), repair_subject_digest=d("subject-a"), live_tombstone_count=2, carried_tombstone_count=1, sequence=0, issued_at=NOW, expires_at=NOW + 300, family_id="family-a", path_family="path-a")
    e1 = make_tombstone_repair_entry(keypair=kp(10), repair_kind=TombstoneRepairKind.REPAIR_PUBLISHED, settlement_report=settled, tombstone_digest=d("tomb-b"), repair_subject_digest=d("subject-b"), live_tombstone_count=2, carried_tombstone_count=1, sequence=1, previous_entry_digest=e0.entry_digest, issued_at=NOW + 1, expires_at=NOW + 301, family_id="family-b", path_family="path-b")
    repair = assess_tombstone_repair((e0, e1), settlement_report=settled, expected_live_tombstone_count=2, now=NOW + 2)
    assert repair.decision_kind is TombstoneRepairDecisionKind.ACCEPT_REPAIR_COVERAGE
    assert repair.carried_tombstone_count == 2


def test_tombstone_repair_holds_missing_and_quarantines_resurrection() -> None:
    settled = make_settlement_report()
    missing = assess_tombstone_repair((), settlement_report=settled, expected_live_tombstone_count=1, now=NOW)
    assert missing.decision_kind is TombstoneRepairDecisionKind.HOLD_MISSING_REPAIR

    e0 = make_tombstone_repair_entry(keypair=kp(11), repair_kind=TombstoneRepairKind.RESURRECTION_BLOCKED, settlement_report=settled, tombstone_digest=d("tomb"), repair_subject_digest=d("subject"), live_tombstone_count=1, carried_tombstone_count=1, resurrection_count=1, sequence=0, issued_at=NOW, expires_at=NOW + 300, family_id="family-a", path_family="path-a")
    verdict = assess_tombstone_repair((e0,), settlement_report=settled, expected_live_tombstone_count=1, now=NOW + 1, min_family_count=1, min_path_family_count=1)
    assert verdict.decision_kind is TombstoneRepairDecisionKind.QUARANTINE_RESURRECTION_PRESSURE


def test_settlementfold_current_revision_audit_passes() -> None:
    root = Path(__file__).resolve().parents[1]
    report = audit_settlement_fold(root)
    assert report.status == "pass", report.findings
