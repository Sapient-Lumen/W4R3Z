from __future__ import annotations

from dataclasses import replace

from i2p_dht_lab.authorityreceipt import (
    AuthorityReceiptDecisionKind,
    AuthorityReceiptKind,
    ReceiptStatus,
    assess_authority_receipt_mesh,
    make_authority_receipt,
)
from i2p_dht_lab.branchsealfold import audit_branch_seal
from i2p_dht_lab.identity import DhtKeypair
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.policyfirebreak import (
    FirebreakSignalKind,
    PolicyAction,
    PolicyDisposition,
    PolicyFirebreakDecisionKind,
    assess_policy_firebreak,
    make_firebreak_signal,
    make_policy_capsule,
)

NOW = 1_860_000
PROFILE = "garden-profile"
SCOPE = sha256(b"scope")
REQUEST = sha256(b"request")
SUBJECT = sha256(b"service-key-digest")

AUTH = DhtKeypair.from_seed(b"A" * 32)
KEY_A = DhtKeypair.from_seed(b"B" * 32)
KEY_B = DhtKeypair.from_seed(b"C" * 32)
KEY_C = DhtKeypair.from_seed(b"D" * 32)
KEY_D = DhtKeypair.from_seed(b"E" * 32)
KEY_E = DhtKeypair.from_seed(b"F" * 32)
KEY_F = DhtKeypair.from_seed(b"G" * 32)


def d(label: str) -> bytes:
    return sha256(label.encode("utf-8"))


def policy(*, disposition=PolicyDisposition.ALLOW, seq=1, prev=b"\x00" * 32, subject=SUBJECT, action=PolicyAction.PUBLIC_BRIDGE, profile=PROFILE, scope=SCOPE, key=AUTH, family="policy-fam", path="policy-path", reason=""):
    return make_policy_capsule(
        keypair=key,
        authority_name="local-maintainer-policy",
        profile_id=profile,
        action=action,
        subject_key_digest=subject,
        scope_digest=scope,
        sequence=seq,
        previous_policy_digest=prev,
        issued_at=NOW,
        expires_at=NOW + 100,
        family_id=family,
        path_family=path,
        disposition=disposition,
        reason=reason,
    )


def signal(kind: FirebreakSignalKind, *, key=KEY_A, action=PolicyAction.PUBLIC_BRIDGE, subject=SUBJECT, profile=PROFILE, scope=SCOPE, request=REQUEST, accepted=True, clear=True, seq=1, family="fam-a", path="path-a", public=False):
    return make_firebreak_signal(
        keypair=key,
        kind=kind,
        profile_id=profile,
        action=action,
        subject_key_digest=subject,
        scope_digest=scope,
        request_digest=request,
        sequence=seq,
        report_digest=d(f"signal-{kind.value}-{seq}-{family}-{path}"),
        accepted=accepted,
        hard_negative_clear=clear,
        issued_at=NOW,
        expires_at=NOW + 100,
        family_id=family,
        path_family=path,
        public_exposure=public,
    )


def public_signals():
    return (
        signal(FirebreakSignalKind.KEY_COMPARTMENT, key=KEY_A, family="fam-a", path="path-a"),
        signal(FirebreakSignalKind.AUTHORITY_SPLIT, key=KEY_B, family="fam-b", path="path-b"),
        signal(FirebreakSignalKind.CONTROL_INTENT, key=KEY_C, family="fam-c", path="path-c"),
        signal(FirebreakSignalKind.BRIDGE_FIREWALL, key=KEY_D, family="fam-d", path="path-d", public=True),
        signal(FirebreakSignalKind.HARD_NEGATIVE_SCAN, key=KEY_E, family="fam-e", path="path-e"),
    )


def test_policy_firebreak_accepts_diverse_public_bridge_signals() -> None:
    report = assess_policy_firebreak(
        (policy(),),
        public_signals(),
        now=NOW + 1,
        expected_profile_id=PROFILE,
        expected_action=PolicyAction.PUBLIC_BRIDGE,
        expected_subject_key_digest=SUBJECT,
        expected_scope_digest=SCOPE,
        expected_request_digest=REQUEST,
        min_signal_family_diversity=4,
        min_signal_path_diversity=4,
    )
    assert report.decision_kind is PolicyFirebreakDecisionKind.ACCEPT_POLICY_FIREBREAK
    assert report.accepted
    assert report.family_count == 5


def test_policy_firebreak_policy_deny_and_watch_are_first_class() -> None:
    deny = policy(disposition=PolicyDisposition.DENY, reason="official_bridge_ban")
    assert assess_policy_firebreak((deny,), public_signals(), now=NOW + 1, expected_profile_id=PROFILE, expected_action=PolicyAction.PUBLIC_BRIDGE, expected_subject_key_digest=SUBJECT, expected_scope_digest=SCOPE, expected_request_digest=REQUEST).decision_kind is PolicyFirebreakDecisionKind.QUARANTINE_POLICY_DENY
    watch = policy(disposition=PolicyDisposition.REQUIRE_WATCH, reason="operator_key_recently_rotated")
    held = assess_policy_firebreak((watch,), public_signals(), now=NOW + 1, expected_profile_id=PROFILE, expected_action=PolicyAction.PUBLIC_BRIDGE, expected_subject_key_digest=SUBJECT, expected_scope_digest=SCOPE, expected_request_digest=REQUEST)
    assert held.decision_kind is PolicyFirebreakDecisionKind.HOLD_POLICY_WATCH
    accepted = assess_policy_firebreak((watch,), public_signals(), now=NOW + 1, expected_profile_id=PROFILE, expected_action=PolicyAction.PUBLIC_BRIDGE, expected_subject_key_digest=SUBJECT, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, allow_watch=True)
    assert accepted.decision_kind is PolicyFirebreakDecisionKind.ACCEPT_WITH_WATCH
    assert accepted.watch


def test_policy_firebreak_catches_replay_drift_signal_failure_and_hard_negative() -> None:
    good_policy = policy()
    sigs = public_signals()
    assert assess_policy_firebreak((good_policy,), sigs, now=NOW + 1, expected_profile_id=PROFILE, expected_action=PolicyAction.PUBLIC_BRIDGE, expected_subject_key_digest=SUBJECT, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, previously_seen_policy_digests=(good_policy.policy_digest,)).decision_kind is PolicyFirebreakDecisionKind.QUARANTINE_REPLAY
    scope_drift = policy(scope=d("other-scope"))
    assert assess_policy_firebreak((scope_drift,), sigs, now=NOW + 1, expected_profile_id=PROFILE, expected_action=PolicyAction.PUBLIC_BRIDGE, expected_subject_key_digest=SUBJECT, expected_scope_digest=SCOPE, expected_request_digest=REQUEST).decision_kind is PolicyFirebreakDecisionKind.QUARANTINE_SCOPE_DRIFT
    bad_component = sigs[:-1] + (signal(FirebreakSignalKind.HARD_NEGATIVE_SCAN, key=KEY_E, family="fam-e", path="path-e", accepted=False),)
    assert assess_policy_firebreak((good_policy,), bad_component, now=NOW + 1, expected_profile_id=PROFILE, expected_action=PolicyAction.PUBLIC_BRIDGE, expected_subject_key_digest=SUBJECT, expected_scope_digest=SCOPE, expected_request_digest=REQUEST).decision_kind is PolicyFirebreakDecisionKind.HOLD_SIGNAL_NOT_ACCEPTED
    dirty = sigs[:-1] + (signal(FirebreakSignalKind.HARD_NEGATIVE_SCAN, key=KEY_E, family="fam-e", path="path-e", clear=False),)
    assert assess_policy_firebreak((good_policy,), dirty, now=NOW + 1, expected_profile_id=PROFILE, expected_action=PolicyAction.PUBLIC_BRIDGE, expected_subject_key_digest=SUBJECT, expected_scope_digest=SCOPE, expected_request_digest=REQUEST).decision_kind is PolicyFirebreakDecisionKind.QUARANTINE_HARD_NEGATIVE


def test_policy_firebreak_catches_sequence_forks_bad_signature_and_low_diversity() -> None:
    good_policy = policy()
    fork = policy(seq=1, key=KEY_F, family="policy-fork", path="policy-fork")
    assert assess_policy_firebreak((good_policy, fork), public_signals(), now=NOW + 1, expected_profile_id=PROFILE, expected_action=PolicyAction.PUBLIC_BRIDGE, expected_subject_key_digest=SUBJECT, expected_scope_digest=SCOPE, expected_request_digest=REQUEST).decision_kind is PolicyFirebreakDecisionKind.QUARANTINE_SEQUENCE_FORK
    bad_sig = replace(good_policy, signature=b"x" * 64)
    assert assess_policy_firebreak((bad_sig,), public_signals(), now=NOW + 1, expected_profile_id=PROFILE, expected_action=PolicyAction.PUBLIC_BRIDGE, expected_subject_key_digest=SUBJECT, expected_scope_digest=SCOPE, expected_request_digest=REQUEST).decision_kind is PolicyFirebreakDecisionKind.QUARANTINE_BAD_SIGNATURE
    mono = tuple(signal(s.kind, key=KEY_A, family="one", path="one", public=s.public_exposure) for s in public_signals())
    assert assess_policy_firebreak((good_policy,), mono, now=NOW + 1, expected_profile_id=PROFILE, expected_action=PolicyAction.PUBLIC_BRIDGE, expected_subject_key_digest=SUBJECT, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, min_signal_family_diversity=2).decision_kind is PolicyFirebreakDecisionKind.HOLD_LOW_FAMILY_DIVERSITY


def receipt(kind: AuthorityReceiptKind, *, key=KEY_A, status=ReceiptStatus.ACCEPT, action=PolicyAction.PUBLIC_BRIDGE, subject=SUBJECT, profile=PROFILE, scope=SCOPE, request=REQUEST, seq=1, family="fam-a", path="path-a", reason=""):
    return make_authority_receipt(
        keypair=key,
        kind=kind,
        status=status,
        profile_id=profile,
        action=action,
        subject_key_digest=subject,
        scope_digest=scope,
        request_digest=request,
        evidence_digest=d(f"receipt-{kind.value}-{status.value}-{seq}-{family}"),
        sequence=seq,
        issued_at=NOW,
        expires_at=NOW + 100,
        family_id=family,
        path_family=path,
        reason=reason,
    )


REQUIRED_RECEIPTS = (AuthorityReceiptKind.POLICY_FIREBREAK, AuthorityReceiptKind.AUTHORITY_SPLIT, AuthorityReceiptKind.HARD_NEGATIVE_SCAN)


def receipt_mesh():
    return (
        receipt(AuthorityReceiptKind.POLICY_FIREBREAK, key=KEY_A, family="fam-a", path="path-a"),
        receipt(AuthorityReceiptKind.AUTHORITY_SPLIT, key=KEY_B, family="fam-b", path="path-b"),
        receipt(AuthorityReceiptKind.HARD_NEGATIVE_SCAN, key=KEY_C, family="fam-c", path="path-c"),
    )


def test_authority_receipt_mesh_accepts_diverse_exact_scope_receipts() -> None:
    report = assess_authority_receipt_mesh(receipt_mesh(), now=NOW + 1, expected_profile_id=PROFILE, expected_action=PolicyAction.PUBLIC_BRIDGE, expected_subject_key_digest=SUBJECT, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, required_kinds=REQUIRED_RECEIPTS, min_family_diversity=3, min_path_diversity=3)
    assert report.decision_kind is AuthorityReceiptDecisionKind.ACCEPT_RECEIPT_MESH
    assert report.accepted
    assert report.family_count == 3


def test_authority_receipt_mesh_handles_watch_and_refusal() -> None:
    watched = receipt_mesh()[:-1] + (receipt(AuthorityReceiptKind.HARD_NEGATIVE_SCAN, key=KEY_C, status=ReceiptStatus.WATCH, family="fam-c", path="path-c"),)
    assert assess_authority_receipt_mesh(watched, now=NOW + 1, expected_profile_id=PROFILE, expected_action=PolicyAction.PUBLIC_BRIDGE, expected_subject_key_digest=SUBJECT, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, required_kinds=REQUIRED_RECEIPTS).decision_kind is AuthorityReceiptDecisionKind.HOLD_RECEIPT_WATCH
    assert assess_authority_receipt_mesh(watched, now=NOW + 1, expected_profile_id=PROFILE, expected_action=PolicyAction.PUBLIC_BRIDGE, expected_subject_key_digest=SUBJECT, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, required_kinds=REQUIRED_RECEIPTS, allow_watch=True).decision_kind is AuthorityReceiptDecisionKind.ACCEPT_WITH_WATCH
    refused = receipt_mesh()[:-1] + (receipt(AuthorityReceiptKind.HARD_NEGATIVE_SCAN, key=KEY_C, status=ReceiptStatus.REFUSE, family="fam-c", path="path-c", reason="hard_negative_live"),)
    assert assess_authority_receipt_mesh(refused, now=NOW + 1, expected_profile_id=PROFILE, expected_action=PolicyAction.PUBLIC_BRIDGE, expected_subject_key_digest=SUBJECT, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, required_kinds=REQUIRED_RECEIPTS).decision_kind is AuthorityReceiptDecisionKind.QUARANTINE_RECEIPT_REFUSAL


def test_authority_receipt_mesh_catches_replay_drift_fork_and_conflict() -> None:
    receipts = receipt_mesh()
    assert assess_authority_receipt_mesh(receipts, now=NOW + 1, expected_profile_id=PROFILE, expected_action=PolicyAction.PUBLIC_BRIDGE, expected_subject_key_digest=SUBJECT, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, required_kinds=REQUIRED_RECEIPTS, previously_seen_receipt_digests=(receipts[0].receipt_digest,)).decision_kind is AuthorityReceiptDecisionKind.QUARANTINE_REPLAY
    drift = receipts[:-1] + (receipt(AuthorityReceiptKind.HARD_NEGATIVE_SCAN, key=KEY_C, profile="other", family="fam-c", path="path-c"),)
    assert assess_authority_receipt_mesh(drift, now=NOW + 1, expected_profile_id=PROFILE, expected_action=PolicyAction.PUBLIC_BRIDGE, expected_subject_key_digest=SUBJECT, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, required_kinds=REQUIRED_RECEIPTS).decision_kind is AuthorityReceiptDecisionKind.QUARANTINE_PROFILE_DRIFT
    fork = receipts + (receipt(AuthorityReceiptKind.POLICY_FIREBREAK, key=KEY_D, family="fam-d", path="path-d"),)
    assert assess_authority_receipt_mesh(fork, now=NOW + 1, expected_profile_id=PROFILE, expected_action=PolicyAction.PUBLIC_BRIDGE, expected_subject_key_digest=SUBJECT, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, required_kinds=REQUIRED_RECEIPTS).decision_kind is AuthorityReceiptDecisionKind.QUARANTINE_SEQUENCE_FORK
    conflict = receipts + (receipt(AuthorityReceiptKind.POLICY_FIREBREAK, key=KEY_D, status=ReceiptStatus.WATCH, seq=2, family="fam-d", path="path-d"),)
    assert assess_authority_receipt_mesh(conflict, now=NOW + 1, expected_profile_id=PROFILE, expected_action=PolicyAction.PUBLIC_BRIDGE, expected_subject_key_digest=SUBJECT, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, required_kinds=REQUIRED_RECEIPTS).decision_kind is AuthorityReceiptDecisionKind.QUARANTINE_CONFLICTING_STATUS


def test_authority_receipt_mesh_catches_bad_signature_and_low_diversity() -> None:
    bad = replace(receipt_mesh()[0], signature=b"x" * 64)
    assert assess_authority_receipt_mesh((bad,) + receipt_mesh()[1:], now=NOW + 1, expected_profile_id=PROFILE, expected_action=PolicyAction.PUBLIC_BRIDGE, expected_subject_key_digest=SUBJECT, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, required_kinds=REQUIRED_RECEIPTS).decision_kind is AuthorityReceiptDecisionKind.QUARANTINE_BAD_SIGNATURE
    mono = (
        receipt(AuthorityReceiptKind.POLICY_FIREBREAK, key=KEY_A, family="one", path="one"),
        receipt(AuthorityReceiptKind.AUTHORITY_SPLIT, key=KEY_B, family="one", path="one"),
        receipt(AuthorityReceiptKind.HARD_NEGATIVE_SCAN, key=KEY_C, family="one", path="one"),
    )
    assert assess_authority_receipt_mesh(mono, now=NOW + 1, expected_profile_id=PROFILE, expected_action=PolicyAction.PUBLIC_BRIDGE, expected_subject_key_digest=SUBJECT, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, required_kinds=REQUIRED_RECEIPTS, min_family_diversity=2).decision_kind is AuthorityReceiptDecisionKind.HOLD_LOW_FAMILY_DIVERSITY


def test_branchseal_current_revision_path_passes() -> None:
    report = audit_branch_seal(".", revision="rev0044")
    assert report.status == "pass"
    assert report.predecessor_status == "pass"
    assert report.foldmap_status == "pass"
    assert report.registry_status == "pass"
    assert report.surface_ledger_status == "pass"
