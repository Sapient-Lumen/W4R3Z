from __future__ import annotations

from dataclasses import replace

from i2p_dht_lab.bridgeepoch import BridgeEpochAction
from i2p_dht_lab.bridgeledger import (
    BridgeLedgerAction,
    BridgeLedgerDecisionKind,
    assess_bridge_ledger,
    make_bridge_ledger_entry,
)
from i2p_dht_lab.egressmeter import EgressBudget, EgressEvent, EgressEventKind, assess_egress_window
from i2p_dht_lab.identity import DhtKeypair
from i2p_dht_lab.ids import DOMAIN, sha256
from i2p_dht_lab.moderationfold import audit_moderation_fold
from i2p_dht_lab.moderationquarantine import (
    ModerationAction,
    ModerationDecisionKind,
    ModerationDisposition,
    ZERO_DIGEST,
    assess_moderation_quarantine,
    make_quarantine_capsule,
)
from i2p_dht_lab.redresslane import (
    RedressDecisionKind,
    RedressKind,
    RedressPurpose,
    RedressStatus,
    assess_redress,
    make_redress_receipt,
)
from i2p_dht_lab.shadowfire import ShadowFireDecisionKind, ShadowFireReport

NOW = 1_800_000
PROFILE = "profile-alpha"
SERVICE = "public-bridge"
SCOPE = sha256(DOMAIN + b":rev0046:scope")
REQUEST = sha256(DOMAIN + b":rev0046:request")
SUBJECT = sha256(DOMAIN + b":rev0046:subject-key")


def d(label: str) -> bytes:
    return sha256(DOMAIN + b":rev0046-test:" + label.encode("utf-8"))


def key(n: int) -> DhtKeypair:
    return DhtKeypair.from_seed(bytes([n]) * 32)


K1 = key(1)
K2 = key(2)
K3 = key(3)
K4 = key(4)
K5 = key(5)
K6 = key(6)
K7 = key(7)
K8 = key(8)


def quarantine_capsule(*, keypair=K1, disposition=ModerationDisposition.DENY, sequence=1, family="fam-a", path="path-a", appeal_allowed=True, scope=SCOPE, request=REQUEST, reason="policy-test"):
    return make_quarantine_capsule(
        keypair=keypair,
        authority_name="maintainer-policy",
        action=ModerationAction.PUBLIC_BRIDGE,
        disposition=disposition,
        profile_id=PROFILE,
        service_name=SERVICE,
        subject_key_digest=SUBJECT,
        scope_digest=scope,
        request_digest=request,
        evidence_digest=d(f"evidence-{sequence}-{disposition.value}"),
        sequence=sequence,
        previous_capsule_digest=ZERO_DIGEST,
        issued_at=NOW,
        expires_at=NOW + 100,
        appeal_allowed=appeal_allowed,
        hard_negative_clear=True,
        public_exposure=True,
        family_id=family,
        path_family=path,
        reason_code=reason,
    )


def moderation_report(*, disposition=ModerationDisposition.DENY, appeal_allowed=True):
    capsules = (
        quarantine_capsule(keypair=K1, disposition=disposition, family="fam-a", path="path-a", appeal_allowed=appeal_allowed),
        quarantine_capsule(keypair=K2, disposition=disposition, family="fam-b", path="path-b", appeal_allowed=appeal_allowed),
    )
    return assess_moderation_quarantine(
        capsules,
        now=NOW + 1,
        expected_profile_id=PROFILE,
        expected_service_name=SERVICE,
        expected_subject_key_digest=SUBJECT,
        expected_action=ModerationAction.PUBLIC_BRIDGE,
        expected_scope_digest=SCOPE,
        expected_request_digest=REQUEST,
    )


def redress_receipt(kind: RedressKind, *, keypair: DhtKeypair, family: str, path: str, moderation=None, status=RedressStatus.SUPPORT, purpose=RedressPurpose.LIFT, sequence=1):
    moderation = moderation or moderation_report()
    return make_redress_receipt(
        keypair=keypair,
        kind=kind,
        purpose=purpose,
        status=status,
        profile_id=PROFILE,
        service_name=SERVICE,
        subject_key_digest=SUBJECT,
        action=ModerationAction.PUBLIC_BRIDGE,
        scope_digest=SCOPE,
        request_digest=REQUEST,
        quarantine_report_digest=moderation.report_digest,
        evidence_digest=d(f"redress-{kind.value}-{family}-{sequence}"),
        sequence=sequence,
        previous_redress_digest=ZERO_DIGEST,
        issued_at=NOW,
        expires_at=NOW + 100,
        family_id=family,
        path_family=path,
    )


def redress_report(*, moderation=None, status=RedressStatus.SUPPORT, allow_watch=False):
    moderation = moderation or moderation_report()
    receipts = (
        redress_receipt(RedressKind.SUBJECT_COUNTERSIGN, keypair=K3, family="fam-c", path="path-c", moderation=moderation, status=status),
        redress_receipt(RedressKind.MODERATOR_ACK, keypair=K4, family="fam-d", path="path-d", moderation=moderation, status=status),
        redress_receipt(RedressKind.WITNESS_OBSERVATION, keypair=K5, family="fam-e", path="path-e", moderation=moderation, status=status),
        redress_receipt(RedressKind.HARD_NEGATIVE_SCAN, keypair=K6, family="fam-f", path="path-f", moderation=moderation, status=status),
    )
    return assess_redress(
        receipts,
        moderation=moderation,
        now=NOW + 1,
        purpose=RedressPurpose.LIFT,
        expected_scope_digest=SCOPE,
        expected_request_digest=REQUEST,
        allow_watch=allow_watch,
    )


def shadow_report(*, accept=True, watch=False, action=BridgeEpochAction.RENEW_PUBLIC, decision=ShadowFireDecisionKind.ACCEPT_PUBLIC_BRIDGE):
    return ShadowFireReport(decision, accept, watch, "test shadowfire", PROFILE, SERVICE, action, (d("shadow-a"), d("shadow-b")), 5, d(f"shadow-report-{decision.value}-{accept}-{watch}-{action.value}"))


def egress_report(*, byte_cost=300, duplicate=False):
    event_a = EgressEvent(EgressEventKind.SAM_STREAM_SEND, SCOPE, d("bridge-effect"), d("dest-a"), "dest-a", "path-a", NOW, NOW + 100, byte_cost, 1, False, "bridge refresh")
    event_b = EgressEvent(EgressEventKind.USEFUL_REFUSAL, SCOPE, d("bridge-effect"), d("dest-b"), "dest-b", "path-b", NOW, NOW + 100, 50, 1, False, "bounded refusal receipt")
    events = (event_a, event_a) if duplicate else (event_a, event_b)
    return assess_egress_window(events, budget=EgressBudget(max_total_bytes=1_000, max_total_streams=4), now=NOW + 1)


def ledger_entry(*, keypair=K7, sequence=1, family="fam-ledger-a", path="path-ledger-a", shadow=None, egress=None, moderation=None, redress=None, action=BridgeLedgerAction.PUBLIC_REFRESH):
    shadow = shadow or shadow_report()
    egress = egress or egress_report()
    moderation = moderation or assess_moderation_quarantine((), now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_subject_key_digest=SUBJECT, expected_action=ModerationAction.PUBLIC_BRIDGE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST)
    redress_digest = redress.report_digest if redress is not None else ZERO_DIGEST
    return make_bridge_ledger_entry(
        keypair=keypair,
        action=action,
        profile_id=PROFILE,
        service_name=SERVICE,
        shadow_fire_digest=shadow.report_digest,
        egress_digest=egress.report_digest,
        moderation_digest=moderation.report_digest,
        redress_digest=redress_digest,
        side_effect_digest=d(f"side-effect-{sequence}-{action.value}"),
        sequence=sequence,
        previous_ledger_digest=ZERO_DIGEST,
        issued_at=NOW,
        expires_at=NOW + 100,
        family_id=family,
        path_family=path,
    )


def test_moderation_clear_and_blocking_capsules() -> None:
    clear = assess_moderation_quarantine((), now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_subject_key_digest=SUBJECT, expected_action=ModerationAction.PUBLIC_BRIDGE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST)
    assert clear.decision_kind is ModerationDecisionKind.CLEAR_NO_ACTIVE_CAPSULE
    assert not clear.blocked

    blocked = moderation_report()
    assert blocked.decision_kind is ModerationDecisionKind.ACCEPT_DENY
    assert blocked.blocked
    assert blocked.family_count == 2
    assert blocked.appeal_allowed


def test_moderation_catches_replay_fork_and_scope_drift() -> None:
    capsule = quarantine_capsule()
    replay = assess_moderation_quarantine((capsule,), now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_subject_key_digest=SUBJECT, expected_action=ModerationAction.PUBLIC_BRIDGE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, previously_seen_capsules=(capsule.capsule_digest,))
    assert replay.decision_kind is ModerationDecisionKind.QUARANTINE_REPLAY

    fork = (quarantine_capsule(keypair=K1, disposition=ModerationDisposition.DENY, sequence=2, family="fam-a", path="path-a"), quarantine_capsule(keypair=K2, disposition=ModerationDisposition.FREEZE, sequence=2, family="fam-b", path="path-b"))
    assert assess_moderation_quarantine(fork, now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_subject_key_digest=SUBJECT, expected_action=ModerationAction.PUBLIC_BRIDGE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST).decision_kind is ModerationDecisionKind.QUARANTINE_SEQUENCE_FORK

    drift = quarantine_capsule(scope=d("other-scope"))
    assert assess_moderation_quarantine((drift,), now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_subject_key_digest=SUBJECT, expected_action=ModerationAction.PUBLIC_BRIDGE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST).decision_kind is ModerationDecisionKind.QUARANTINE_SCOPE_DRIFT


def test_redress_accepts_lift_and_respects_no_appeal_or_hard_negative() -> None:
    moderation = moderation_report()
    lifted = redress_report(moderation=moderation)
    assert lifted.decision_kind is RedressDecisionKind.ACCEPT_LIFT
    assert lifted.lifted
    assert lifted.family_count == 4

    no_appeal = moderation_report(appeal_allowed=False)
    assert assess_redress((), moderation=no_appeal, now=NOW + 1, purpose=RedressPurpose.LIFT, expected_scope_digest=SCOPE, expected_request_digest=REQUEST).decision_kind is RedressDecisionKind.HOLD_APPEAL_NOT_ALLOWED

    assert assess_redress((), moderation=moderation, now=NOW + 1, purpose=RedressPurpose.LIFT, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, live_hard_negative_digests=(d("live-negative"),)).decision_kind is RedressDecisionKind.QUARANTINE_HARD_NEGATIVE_LIVE


def test_redress_catches_missing_evidence_refusal_and_quarantine_digest_drift() -> None:
    moderation = moderation_report()
    receipts = (
        redress_receipt(RedressKind.SUBJECT_COUNTERSIGN, keypair=K3, family="fam-c", path="path-c", moderation=moderation),
        redress_receipt(RedressKind.MODERATOR_ACK, keypair=K4, family="fam-d", path="path-d", moderation=moderation),
    )
    assert assess_redress(receipts, moderation=moderation, now=NOW + 1, purpose=RedressPurpose.LIFT, expected_scope_digest=SCOPE, expected_request_digest=REQUEST).decision_kind is RedressDecisionKind.HOLD_MISSING_REDRESS_EVIDENCE

    refusal = (redress_receipt(RedressKind.SUBJECT_COUNTERSIGN, keypair=K3, family="fam-c", path="path-c", moderation=moderation, status=RedressStatus.REFUSE),)
    assert assess_redress(refusal, moderation=moderation, now=NOW + 1, purpose=RedressPurpose.LIFT, expected_scope_digest=SCOPE, expected_request_digest=REQUEST).decision_kind is RedressDecisionKind.QUARANTINE_REFUSAL

    other_moderation = replace(moderation, report_digest=d("other-moderation"))
    drift_receipt = redress_receipt(RedressKind.SUBJECT_COUNTERSIGN, keypair=K3, family="fam-c", path="path-c", moderation=other_moderation)
    assert assess_redress((drift_receipt,), moderation=moderation, now=NOW + 1, purpose=RedressPurpose.LIFT, expected_scope_digest=SCOPE, expected_request_digest=REQUEST).decision_kind is RedressDecisionKind.QUARANTINE_QUARANTINE_DIGEST_DRIFT


def test_bridge_ledger_accepts_clear_or_lifted_moderation() -> None:
    clear = assess_moderation_quarantine((), now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_subject_key_digest=SUBJECT, expected_action=ModerationAction.PUBLIC_BRIDGE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST)
    shadow = shadow_report()
    egress = egress_report()
    entries = (
        ledger_entry(sequence=1, family="ledger-a", path="ledger-pa", shadow=shadow, egress=egress, moderation=clear),
        ledger_entry(keypair=K8, sequence=2, family="ledger-b", path="ledger-pb", shadow=shadow, egress=egress, moderation=clear),
    )
    accepted = assess_bridge_ledger(entries, shadow_fire=shadow, egress=egress, moderation=clear, redress=None, now=NOW + 1, action=BridgeLedgerAction.PUBLIC_REFRESH, expected_profile_id=PROFILE, expected_service_name=SERVICE)
    assert accepted.decision_kind is BridgeLedgerDecisionKind.ACCEPT_LEDGER
    assert accepted.accept

    moderation = moderation_report()
    redress = redress_report(moderation=moderation)
    lifted_entries = (
        ledger_entry(sequence=1, family="ledger-a", path="ledger-pa", shadow=shadow, egress=egress, moderation=moderation, redress=redress),
        ledger_entry(keypair=K8, sequence=2, family="ledger-b", path="ledger-pb", shadow=shadow, egress=egress, moderation=moderation, redress=redress),
    )
    lifted = assess_bridge_ledger(lifted_entries, shadow_fire=shadow, egress=egress, moderation=moderation, redress=redress, now=NOW + 1, action=BridgeLedgerAction.PUBLIC_REFRESH, expected_profile_id=PROFILE, expected_service_name=SERVICE)
    assert lifted.decision_kind is BridgeLedgerDecisionKind.ACCEPT_LEDGER
    assert lifted.accept


def test_bridge_ledger_blocks_unredressed_moderation_and_bad_egress() -> None:
    moderation = moderation_report()
    shadow = shadow_report()
    egress = egress_report()
    entries = (
        ledger_entry(sequence=1, family="ledger-a", path="ledger-pa", shadow=shadow, egress=egress, moderation=moderation),
        ledger_entry(keypair=K8, sequence=2, family="ledger-b", path="ledger-pb", shadow=shadow, egress=egress, moderation=moderation),
    )
    blocked = assess_bridge_ledger(entries, shadow_fire=shadow, egress=egress, moderation=moderation, redress=None, now=NOW + 1, action=BridgeLedgerAction.PUBLIC_REFRESH, expected_profile_id=PROFILE, expected_service_name=SERVICE)
    assert blocked.decision_kind is BridgeLedgerDecisionKind.HOLD_REDRESS_NEEDED

    bad_egress = egress_report(duplicate=True)
    bad_entries = (
        ledger_entry(sequence=1, family="ledger-a", path="ledger-pa", shadow=shadow, egress=bad_egress, moderation=moderation),
        ledger_entry(keypair=K8, sequence=2, family="ledger-b", path="ledger-pb", shadow=shadow, egress=bad_egress, moderation=moderation),
    )
    assert assess_bridge_ledger(bad_entries, shadow_fire=shadow, egress=bad_egress, moderation=moderation, redress=None, now=NOW + 1, action=BridgeLedgerAction.PUBLIC_REFRESH, expected_profile_id=PROFILE, expected_service_name=SERVICE).decision_kind is BridgeLedgerDecisionKind.QUARANTINE_EGRESS


def test_bridge_ledger_catches_component_drift_action_drift_and_watch_hold() -> None:
    moderation = moderation_report(disposition=ModerationDisposition.WATCH)
    shadow = shadow_report(watch=True, decision=ShadowFireDecisionKind.ACCEPT_WITH_WATCH)
    egress = egress_report()
    entry = ledger_entry(shadow=shadow, egress=egress, moderation=moderation)
    assert assess_bridge_ledger((entry, ledger_entry(keypair=K8, sequence=2, family="ledger-b", path="ledger-pb", shadow=shadow, egress=egress, moderation=moderation)), shadow_fire=shadow, egress=egress, moderation=moderation, redress=None, now=NOW + 1, action=BridgeLedgerAction.PUBLIC_REFRESH, expected_profile_id=PROFILE, expected_service_name=SERVICE).decision_kind is BridgeLedgerDecisionKind.HOLD_MODERATION_WATCH

    drifted = replace(entry, shadow_fire_digest=d("drifted-shadow"))
    assert assess_bridge_ledger((drifted,), shadow_fire=shadow, egress=egress, moderation=moderation, redress=None, now=NOW + 1, action=BridgeLedgerAction.PUBLIC_REFRESH, expected_profile_id=PROFILE, expected_service_name=SERVICE).decision_kind is BridgeLedgerDecisionKind.QUARANTINE_BAD_SIGNATURE

    close_shadow = shadow_report(action=BridgeEpochAction.WITHDRAW_PUBLIC, decision=ShadowFireDecisionKind.ACCEPT_CLOSE_OR_WITHDRAW)
    close_entry = ledger_entry(shadow=close_shadow, egress=egress, moderation=moderation, action=BridgeLedgerAction.PUBLIC_REFRESH)
    assert assess_bridge_ledger((close_entry,), shadow_fire=close_shadow, egress=egress, moderation=moderation, redress=None, now=NOW + 1, action=BridgeLedgerAction.PUBLIC_REFRESH, expected_profile_id=PROFILE, expected_service_name=SERVICE).decision_kind is BridgeLedgerDecisionKind.QUARANTINE_ACTION_DRIFT


def test_moderationfold_current_revision_path_passes() -> None:
    report = audit_moderation_fold(".", revision="rev0046")
    assert report.status == "pass"
    assert report.predecessor_status == "pass"
    assert report.foldmap_status == "pass"
    assert report.registry_status == "pass"
    assert report.surface_ledger_status == "pass"
