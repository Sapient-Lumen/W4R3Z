from __future__ import annotations

from dataclasses import replace

from i2p_dht_lab.announcementrepair import RepairSignalKind, assess_announcement_repair, make_announcement_repair_signal
from i2p_dht_lab.authorityreceipt import AuthorityReceiptKind, ReceiptStatus, assess_authority_receipt_mesh, make_authority_receipt
from i2p_dht_lab.bridgeepoch import BridgeEpochAction, BridgeEpochDecisionKind, assess_bridge_epoch, make_bridge_epoch_notice
from i2p_dht_lab.bridgeepochfold import audit_bridge_epoch_fold
from i2p_dht_lab.identity import DhtKeypair
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.keyreceiptlane import KeyReceiptDecisionKind, KeyReceiptKind, KeyReceiptStatus, assess_key_authority_receipts, make_key_authority_receipt
from i2p_dht_lab.policyfirebreak import FirebreakSignalKind, PolicyAction, PolicyDisposition, PolicyFirebreakDecisionKind, assess_policy_firebreak, make_firebreak_signal, make_policy_capsule
from i2p_dht_lab.shadowfire import ShadowFireDecisionKind, assess_shadow_fire

NOW = 1_870_000
PROFILE = "garden-profile"
SERVICE = "public-bridge"
SCOPE = sha256(b"scope")
REQUEST = sha256(b"request")
CATALOG = sha256(b"catalog")
ANNOUNCEMENT = sha256(b"announcement")
CONTROL = sha256(b"control-receipt")
SUBJECT = sha256(b"subject-key")
OPERATOR = sha256(b"operator-key")
SUCCESSOR = sha256(b"successor-key")
ZERO = b"\x00" * 32

KEYS = [DhtKeypair.from_seed(bytes([idx]) * 32) for idx in range(1, 12)]


def d(label: str) -> bytes:
    return sha256(label.encode("utf-8"))


def epoch(action=BridgeEpochAction.OPEN_PUBLIC, *, seq=1, prev=ZERO, key=KEYS[0], family="fam-a", path="path-a", public=True, catalog=CATALOG, announcement=ANNOUNCEMENT, hard_clear=True, service=SERVICE):
    return make_bridge_epoch_notice(
        keypair=key,
        profile_id=PROFILE,
        service_name=service,
        action=action,
        sequence=seq,
        previous_epoch_digest=prev,
        scope_digest=SCOPE,
        request_digest=REQUEST,
        catalog_digest=catalog,
        announcement_digest=announcement,
        control_receipt_digest=CONTROL,
        issued_at=NOW,
        expires_at=NOW + 100,
        family_id=family,
        path_family=path,
        public_exposure=public,
        hard_negative_clear=hard_clear,
    )


def key_receipt(kind: KeyReceiptKind, *, status=KeyReceiptStatus.ACCEPT, seq=1, prev=ZERO, key=KEYS[0], family="fam-a", path="path-a", successor=SUCCESSOR, service=SERVICE):
    return make_key_authority_receipt(
        keypair=key,
        kind=kind,
        status=status,
        profile_id=PROFILE,
        service_name=service,
        subject_key_digest=SUBJECT,
        operator_key_digest=OPERATOR,
        successor_key_digest=successor,
        scope_digest=SCOPE,
        request_digest=REQUEST,
        evidence_digest=d(f"evidence-{kind.value}-{seq}-{family}"),
        sequence=seq,
        previous_receipt_digest=prev,
        issued_at=NOW,
        expires_at=NOW + 100,
        family_id=family,
        path_family=path,
    )


def required_key_receipts(status=KeyReceiptStatus.ACCEPT):
    return (
        key_receipt(KeyReceiptKind.KEY_COMPARTMENT, status=status, key=KEYS[0], family="fam-a", path="path-a"),
        key_receipt(KeyReceiptKind.OPERATOR_ROTATION, status=status, key=KEYS[1], family="fam-b", path="path-b"),
        key_receipt(KeyReceiptKind.BRIDGE_EPOCH_AUTH, status=status, key=KEYS[2], family="fam-c", path="path-c"),
        key_receipt(KeyReceiptKind.HARD_NEGATIVE_SCAN, status=status, key=KEYS[3], family="fam-d", path="path-d"),
    )


def key_report(status=KeyReceiptStatus.ACCEPT, *, allow_watch=False):
    return assess_key_authority_receipts(
        required_key_receipts(status),
        now=NOW + 1,
        expected_profile_id=PROFILE,
        expected_service_name=SERVICE,
        expected_subject_key_digest=SUBJECT,
        expected_operator_key_digest=OPERATOR,
        expected_successor_key_digest=SUCCESSOR,
        expected_scope_digest=SCOPE,
        expected_request_digest=REQUEST,
        required_kinds=(KeyReceiptKind.KEY_COMPARTMENT, KeyReceiptKind.OPERATOR_ROTATION, KeyReceiptKind.BRIDGE_EPOCH_AUTH, KeyReceiptKind.HARD_NEGATIVE_SCAN),
        min_family_diversity=4,
        min_path_diversity=4,
        allow_watch=allow_watch,
    )


def policy_capsule(disposition=PolicyDisposition.ALLOW):
    return make_policy_capsule(
        keypair=KEYS[4],
        authority_name="local-policy",
        profile_id=PROFILE,
        action=PolicyAction.PUBLIC_BRIDGE,
        subject_key_digest=SUBJECT,
        scope_digest=SCOPE,
        sequence=1,
        previous_policy_digest=ZERO,
        issued_at=NOW,
        expires_at=NOW + 100,
        family_id="policy-fam",
        path_family="policy-path",
        disposition=disposition,
        reason="watch" if disposition is PolicyDisposition.REQUIRE_WATCH else "",
    )


def firebreak_signal(kind: FirebreakSignalKind, *, key, family, path, public=False):
    return make_firebreak_signal(
        keypair=key,
        kind=kind,
        profile_id=PROFILE,
        action=PolicyAction.PUBLIC_BRIDGE,
        subject_key_digest=SUBJECT,
        scope_digest=SCOPE,
        request_digest=REQUEST,
        sequence=1,
        report_digest=d(f"firebreak-{kind.value}-{family}"),
        accepted=True,
        hard_negative_clear=True,
        issued_at=NOW,
        expires_at=NOW + 100,
        family_id=family,
        path_family=path,
        public_exposure=public,
    )


def policy_report(disposition=PolicyDisposition.ALLOW, *, allow_watch=False):
    signals = (
        firebreak_signal(FirebreakSignalKind.KEY_COMPARTMENT, key=KEYS[0], family="fam-a", path="path-a"),
        firebreak_signal(FirebreakSignalKind.AUTHORITY_SPLIT, key=KEYS[1], family="fam-b", path="path-b"),
        firebreak_signal(FirebreakSignalKind.CONTROL_INTENT, key=KEYS[2], family="fam-c", path="path-c"),
        firebreak_signal(FirebreakSignalKind.BRIDGE_FIREWALL, key=KEYS[3], family="fam-d", path="path-d", public=True),
        firebreak_signal(FirebreakSignalKind.HARD_NEGATIVE_SCAN, key=KEYS[4], family="fam-e", path="path-e"),
    )
    return assess_policy_firebreak(
        (policy_capsule(disposition),),
        signals,
        now=NOW + 1,
        expected_profile_id=PROFILE,
        expected_action=PolicyAction.PUBLIC_BRIDGE,
        expected_subject_key_digest=SUBJECT,
        expected_scope_digest=SCOPE,
        expected_request_digest=REQUEST,
        min_signal_family_diversity=5,
        min_signal_path_diversity=5,
        allow_watch=allow_watch,
    )


def authority_receipt(kind: AuthorityReceiptKind, *, key, family, path, status=ReceiptStatus.ACCEPT):
    return make_authority_receipt(
        keypair=key,
        kind=kind,
        status=status,
        profile_id=PROFILE,
        action=PolicyAction.PUBLIC_BRIDGE,
        subject_key_digest=SUBJECT,
        scope_digest=SCOPE,
        request_digest=REQUEST,
        evidence_digest=d(f"authority-{kind.value}-{family}"),
        sequence=1,
        issued_at=NOW,
        expires_at=NOW + 100,
        family_id=family,
        path_family=path,
    )


def authority_report(status=ReceiptStatus.ACCEPT):
    receipts = (
        authority_receipt(AuthorityReceiptKind.POLICY_FIREBREAK, key=KEYS[5], family="fam-f", path="path-f", status=status),
        authority_receipt(AuthorityReceiptKind.AUTHORITY_SPLIT, key=KEYS[6], family="fam-g", path="path-g", status=status),
        authority_receipt(AuthorityReceiptKind.HARD_NEGATIVE_SCAN, key=KEYS[7], family="fam-h", path="path-h", status=status),
    )
    return assess_authority_receipt_mesh(
        receipts,
        now=NOW + 1,
        expected_profile_id=PROFILE,
        expected_action=PolicyAction.PUBLIC_BRIDGE,
        expected_subject_key_digest=SUBJECT,
        expected_scope_digest=SCOPE,
        expected_request_digest=REQUEST,
        required_kinds=(AuthorityReceiptKind.POLICY_FIREBREAK, AuthorityReceiptKind.AUTHORITY_SPLIT, AuthorityReceiptKind.HARD_NEGATIVE_SCAN),
        min_family_diversity=3,
        min_path_diversity=3,
    )


def repair_report():
    signals = (
        make_announcement_repair_signal(keypair=KEYS[0], service_name=SERVICE, scope_digest=SCOPE, kind=RepairSignalKind.BRIDGE_DISABLE, sequence=2, catalog_digest=CATALOG, announcement_digest=ANNOUNCEMENT, bridge_disable_digest=CONTROL, issued_at=NOW, expires_at=NOW + 100, family_id="fam-a"),
        make_announcement_repair_signal(keypair=KEYS[1], service_name=SERVICE, scope_digest=SCOPE, kind=RepairSignalKind.PUBLIC_WITHDRAWAL, sequence=2, catalog_digest=CATALOG, announcement_digest=ANNOUNCEMENT, bridge_disable_digest=CONTROL, issued_at=NOW, expires_at=NOW + 100, family_id="fam-b", public_exposure=False),
        make_announcement_repair_signal(keypair=KEYS[2], service_name=SERVICE, scope_digest=SCOPE, kind=RepairSignalKind.SUCCESSOR_CATALOG, sequence=3, catalog_digest=CATALOG, announcement_digest=ANNOUNCEMENT, bridge_disable_digest=CONTROL, issued_at=NOW, expires_at=NOW + 100, family_id="fam-c"),
        make_announcement_repair_signal(keypair=KEYS[3], service_name=SERVICE, scope_digest=SCOPE, kind=RepairSignalKind.TOMBSTONE_SCAN, sequence=2, catalog_digest=CATALOG, announcement_digest=ANNOUNCEMENT, bridge_disable_digest=CONTROL, issued_at=NOW, expires_at=NOW + 100, family_id="fam-d"),
    )
    return assess_announcement_repair(signals, now=NOW + 1, expected_service_name=SERVICE, expected_scope_digest=SCOPE, bridge_disable_digest=CONTROL, previous_catalog_sequence=1)


def accepted_open_epoch_report():
    notices = (epoch(key=KEYS[0], family="fam-a", path="path-a"), epoch(key=KEYS[1], family="fam-b", path="path-b"))
    return assess_bridge_epoch(notices, now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_catalog_digest=CATALOG, expected_announcement_digest=ANNOUNCEMENT, min_family_diversity=2)


def test_bridge_epoch_accepts_diverse_public_open() -> None:
    report = accepted_open_epoch_report()
    assert report.decision_kind is BridgeEpochDecisionKind.ACCEPT_EPOCH
    assert report.accept
    assert report.public_open
    assert report.family_count == 2


def test_bridge_epoch_catches_replay_fork_prev_mismatch_and_stale_public_close() -> None:
    n = epoch()
    assert assess_bridge_epoch((n,), now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_catalog_digest=CATALOG, expected_announcement_digest=ANNOUNCEMENT, previously_seen_notices=(n.notice_digest,)).decision_kind is BridgeEpochDecisionKind.QUARANTINE_REPLAY
    fork = epoch(BridgeEpochAction.RENEW_PUBLIC, seq=1, key=KEYS[1], family="fam-b", path="path-b")
    assert assess_bridge_epoch((n, fork), now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_catalog_digest=CATALOG, expected_announcement_digest=ANNOUNCEMENT).decision_kind is BridgeEpochDecisionKind.QUARANTINE_SEQUENCE_FORK
    advanced = epoch(seq=2, prev=d("wrong-prev"), key=KEYS[2], family="fam-c", path="path-c")
    assert assess_bridge_epoch((advanced,), now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_catalog_digest=CATALOG, expected_announcement_digest=ANNOUNCEMENT, previous_sequence=1, previous_epoch_digest=d("actual-prev")).decision_kind is BridgeEpochDecisionKind.QUARANTINE_PREVIOUS_MISMATCH
    close_still_public = epoch(BridgeEpochAction.CLOSE_PUBLIC, seq=2, key=KEYS[2], family="fam-c", path="path-c", public=True)
    assert assess_bridge_epoch((close_still_public,), now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_catalog_digest=CATALOG, expected_announcement_digest=ANNOUNCEMENT, min_family_diversity=1).decision_kind is BridgeEpochDecisionKind.QUARANTINE_STALE_PUBLIC_REPLAY


def test_bridge_close_requires_announcement_repair_when_configured() -> None:
    close = epoch(BridgeEpochAction.CLOSE_PUBLIC, seq=2, key=KEYS[0], family="fam-a", path="path-a", public=False)
    held = assess_bridge_epoch((close,), now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_catalog_digest=CATALOG, expected_announcement_digest=ANNOUNCEMENT, min_family_diversity=1, require_repair_for_close=True)
    assert held.decision_kind is BridgeEpochDecisionKind.HOLD_NEEDS_REPAIR
    accepted = assess_bridge_epoch((close,), now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_catalog_digest=CATALOG, expected_announcement_digest=ANNOUNCEMENT, min_family_diversity=1, require_repair_for_close=True, repair_report=repair_report())
    assert accepted.decision_kind is BridgeEpochDecisionKind.ACCEPT_CLOSE_WITH_REPAIR


def test_key_receipt_lane_accepts_and_catches_watch_refusal_fork_and_drift() -> None:
    accepted = key_report()
    assert accepted.decision_kind is KeyReceiptDecisionKind.ACCEPT_KEY_RECEIPTS
    assert accepted.accept
    watch = key_report(KeyReceiptStatus.WATCH)
    assert watch.decision_kind is KeyReceiptDecisionKind.HOLD_RECEIPT_WATCH
    watch_allowed = key_report(KeyReceiptStatus.WATCH, allow_watch=True)
    assert watch_allowed.decision_kind is KeyReceiptDecisionKind.ACCEPT_WITH_WATCH
    refused = key_report(KeyReceiptStatus.REFUSE)
    assert refused.decision_kind is KeyReceiptDecisionKind.QUARANTINE_REFUSAL
    fork_a = key_receipt(KeyReceiptKind.KEY_COMPARTMENT, seq=2, key=KEYS[0], family="fam-a", path="path-a")
    fork_b = key_receipt(KeyReceiptKind.KEY_COMPARTMENT, seq=2, key=KEYS[1], family="fam-b", path="path-b")
    assert assess_key_authority_receipts((fork_a, fork_b), now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_subject_key_digest=SUBJECT, expected_operator_key_digest=OPERATOR, expected_successor_key_digest=SUCCESSOR, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, required_kinds=(KeyReceiptKind.KEY_COMPARTMENT,), min_family_diversity=1, min_path_diversity=1).decision_kind is KeyReceiptDecisionKind.QUARANTINE_SEQUENCE_FORK
    drift = key_receipt(KeyReceiptKind.KEY_COMPARTMENT, successor=d("different-successor"))
    assert assess_key_authority_receipts((drift,), now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_subject_key_digest=SUBJECT, expected_operator_key_digest=OPERATOR, expected_successor_key_digest=SUCCESSOR, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, required_kinds=(KeyReceiptKind.KEY_COMPARTMENT,), min_family_diversity=1, min_path_diversity=1).decision_kind is KeyReceiptDecisionKind.QUARANTINE_SUCCESSOR_DRIFT


def test_shadow_fire_accepts_public_bridge_and_rejects_mismatched_close() -> None:
    accepted = assess_shadow_fire(
        bridge_epoch=accepted_open_epoch_report(),
        key_receipts=key_report(),
        policy_firebreak=policy_report(),
        authority_receipts=authority_report(),
        announcement_repair=None,
        expected_profile_id=PROFILE,
        expected_service_name=SERVICE,
        expected_public=True,
        min_combined_family_count=4,
    )
    assert accepted.decision_kind is ShadowFireDecisionKind.ACCEPT_PUBLIC_BRIDGE
    assert accepted.accept
    mismatch = assess_shadow_fire(
        bridge_epoch=accepted_open_epoch_report(),
        key_receipts=key_report(),
        policy_firebreak=policy_report(),
        authority_receipts=authority_report(),
        announcement_repair=None,
        expected_profile_id=PROFILE,
        expected_service_name=SERVICE,
        expected_public=False,
        min_combined_family_count=4,
    )
    assert mismatch.decision_kind is ShadowFireDecisionKind.QUARANTINE_ACTION_MISMATCH


def test_shadow_fire_close_needs_repair_and_watch_propagates() -> None:
    close_notice = epoch(BridgeEpochAction.CLOSE_PUBLIC, seq=2, key=KEYS[0], family="fam-a", path="path-a", public=False)
    close_report = assess_bridge_epoch((close_notice,), now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_catalog_digest=CATALOG, expected_announcement_digest=ANNOUNCEMENT, min_family_diversity=1)
    held = assess_shadow_fire(
        bridge_epoch=close_report,
        key_receipts=key_report(),
        policy_firebreak=policy_report(),
        authority_receipts=authority_report(),
        announcement_repair=None,
        expected_profile_id=PROFILE,
        expected_service_name=SERVICE,
        expected_public=False,
        min_combined_family_count=4,
    )
    assert held.decision_kind is ShadowFireDecisionKind.HOLD_REPAIR_REQUIRED
    watched = assess_shadow_fire(
        bridge_epoch=accepted_open_epoch_report(),
        key_receipts=key_report(KeyReceiptStatus.WATCH, allow_watch=True),
        policy_firebreak=policy_report(PolicyDisposition.ALLOW),
        authority_receipts=authority_report(),
        announcement_repair=None,
        expected_profile_id=PROFILE,
        expected_service_name=SERVICE,
        expected_public=True,
        min_combined_family_count=4,
    )
    assert watched.decision_kind is ShadowFireDecisionKind.ACCEPT_WITH_WATCH


def test_shadow_fire_quarantines_policy_deny_and_hard_negative() -> None:
    denied_policy = policy_report(PolicyDisposition.DENY)
    assert denied_policy.decision_kind is PolicyFirebreakDecisionKind.QUARANTINE_POLICY_DENY
    denied = assess_shadow_fire(
        bridge_epoch=accepted_open_epoch_report(),
        key_receipts=key_report(),
        policy_firebreak=denied_policy,
        authority_receipts=authority_report(),
        announcement_repair=None,
        expected_profile_id=PROFILE,
        expected_service_name=SERVICE,
        expected_public=True,
    )
    assert denied.decision_kind is ShadowFireDecisionKind.QUARANTINE_POLICY
    dirty = assess_shadow_fire(
        bridge_epoch=accepted_open_epoch_report(),
        key_receipts=key_report(),
        policy_firebreak=policy_report(),
        authority_receipts=authority_report(),
        announcement_repair=None,
        expected_profile_id=PROFILE,
        expected_service_name=SERVICE,
        expected_public=True,
        hard_negative_digests=(d("live-tombstone"),),
    )
    assert dirty.decision_kind is ShadowFireDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE


def test_bridge_epoch_fold_audit_passes_current_surface() -> None:
    report = audit_bridge_epoch_fold(".", revision="rev0045", artifact_stem="Nicotine-i2pDHT-rev0045-2026.06.06.00.45-bridgeepoch-keyreceipt-shadowfire")
    assert report.status == "pass"
    assert report.error_count == 0
