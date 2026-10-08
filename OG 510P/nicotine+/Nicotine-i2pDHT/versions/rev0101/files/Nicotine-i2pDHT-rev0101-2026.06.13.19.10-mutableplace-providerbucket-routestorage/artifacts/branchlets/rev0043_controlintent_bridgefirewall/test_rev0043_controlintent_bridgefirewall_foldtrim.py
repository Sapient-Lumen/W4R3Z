from __future__ import annotations

from dataclasses import replace

from i2p_dht_lab.bridgefirewall import (
    BridgeFirewallDecisionKind,
    BridgeFirewallMode,
    BridgeFirewallSignalKind,
    assess_bridge_firewall,
    make_bridge_firewall_signal,
)
from i2p_dht_lab.controlintent import (
    ControlIntentAction,
    ControlIntentDecisionKind,
    ControlSignalKind,
    assess_control_intent_join,
    make_control_intent_signal,
)
from i2p_dht_lab.foldtrim import audit_fold_trim
from i2p_dht_lab.identity import DhtKeypair
from i2p_dht_lab.ids import sha256

NOW = 1_850_000
PROFILE = "garden-profile"
SERVICE = "public-bridge"
SCOPE = sha256(b"scope")
REQUEST = sha256(b"request")

KEY_A = DhtKeypair.from_seed(b"A" * 32)
KEY_B = DhtKeypair.from_seed(b"B" * 32)
KEY_C = DhtKeypair.from_seed(b"C" * 32)
KEY_D = DhtKeypair.from_seed(b"D" * 32)
KEY_E = DhtKeypair.from_seed(b"E" * 32)


def d(label: str) -> bytes:
    return sha256(label.encode("utf-8"))


def control_signal(kind: ControlSignalKind, *, key=KEY_A, action=ControlIntentAction.DISABLE_PUBLIC_BRIDGE, profile=PROFILE, service=SERVICE, scope=SCOPE, request=REQUEST, seq=1, accepted=True, clear=True, family="fam-a", path="path-a"):
    return make_control_intent_signal(
        keypair=key,
        kind=kind,
        action=action,
        profile_id=profile,
        service_name=service,
        scope_digest=scope,
        request_digest=request,
        sequence=seq,
        report_digest=d(f"control-{kind.value}-{seq}-{family}"),
        accepted=accepted,
        hard_negative_clear=clear,
        family_id=family,
        path_family=path,
        issued_at=NOW,
        expires_at=NOW + 100,
    )


def disable_bridge_signals():
    return (
        control_signal(ControlSignalKind.OPERATOR_INTENT, key=KEY_A, family="fam-a", path="path-a"),
        control_signal(ControlSignalKind.MULTISERVICE, key=KEY_B, family="fam-b", path="path-b"),
        control_signal(ControlSignalKind.ANNOUNCEMENT_REPAIR, key=KEY_C, family="fam-c", path="path-c"),
        control_signal(ControlSignalKind.HARD_NEGATIVE_SCAN, key=KEY_D, family="fam-d", path="path-d"),
    )


def resume_signals():
    return (
        control_signal(ControlSignalKind.OPERATOR_INTENT, action=ControlIntentAction.RESUME_PROFILE, key=KEY_A, family="fam-a", path="path-a"),
        control_signal(ControlSignalKind.PROFILE_COOLDOWN, action=ControlIntentAction.RESUME_PROFILE, key=KEY_B, family="fam-b", path="path-b"),
        control_signal(ControlSignalKind.ROUTER_HARNESS, action=ControlIntentAction.RESUME_PROFILE, key=KEY_C, family="fam-c", path="path-c"),
        control_signal(ControlSignalKind.HARD_NEGATIVE_SCAN, action=ControlIntentAction.RESUME_PROFILE, key=KEY_D, family="fam-d", path="path-d"),
    )


def test_control_intent_accepts_disable_bridge_only_when_required_signals_join() -> None:
    report = assess_control_intent_join(disable_bridge_signals(), now=NOW + 1, action=ControlIntentAction.DISABLE_PUBLIC_BRIDGE, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST)
    assert report.decision_kind is ControlIntentDecisionKind.ACCEPT_JOINED_CONTROL_INTENT
    assert report.accept
    assert report.present_signals == ("announcement_repair", "hard_negative_scan", "multiservice", "operator_intent")


def test_control_intent_blocks_missing_rejected_dirty_and_low_diversity() -> None:
    assert assess_control_intent_join(disable_bridge_signals()[:-1], now=NOW + 1, action=ControlIntentAction.DISABLE_PUBLIC_BRIDGE, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST).decision_kind is ControlIntentDecisionKind.HOLD_MISSING_REQUIRED_SIGNAL
    rejected = tuple(sig if sig.kind is not ControlSignalKind.MULTISERVICE else control_signal(ControlSignalKind.MULTISERVICE, key=KEY_B, family="fam-b", path="path-b", accepted=False) for sig in disable_bridge_signals())
    assert assess_control_intent_join(rejected, now=NOW + 1, action=ControlIntentAction.DISABLE_PUBLIC_BRIDGE, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST).decision_kind is ControlIntentDecisionKind.HOLD_SIGNAL_NOT_ACCEPTED
    dirty = tuple(sig if sig.kind is not ControlSignalKind.HARD_NEGATIVE_SCAN else control_signal(ControlSignalKind.HARD_NEGATIVE_SCAN, key=KEY_D, family="fam-d", path="path-d", clear=False) for sig in disable_bridge_signals())
    assert assess_control_intent_join(dirty, now=NOW + 1, action=ControlIntentAction.DISABLE_PUBLIC_BRIDGE, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST).decision_kind is ControlIntentDecisionKind.HOLD_HARD_NEGATIVE_PRESENT
    mono = tuple(control_signal(sig.kind, key=KEY_A, family="one", path="one") for sig in disable_bridge_signals())
    assert assess_control_intent_join(mono, now=NOW + 1, action=ControlIntentAction.DISABLE_PUBLIC_BRIDGE, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST).decision_kind is ControlIntentDecisionKind.HOLD_LOW_FAMILY_DIVERSITY


def test_control_intent_catches_replay_drift_fork_and_bad_signature() -> None:
    sigs = disable_bridge_signals()
    assert assess_control_intent_join(sigs, now=NOW + 1, action=ControlIntentAction.DISABLE_PUBLIC_BRIDGE, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, previously_seen_signals=(sigs[0].signal_digest,)).decision_kind is ControlIntentDecisionKind.QUARANTINE_REPLAY
    drift = disable_bridge_signals()[:-1] + (control_signal(ControlSignalKind.HARD_NEGATIVE_SCAN, key=KEY_D, family="fam-d", path="path-d", profile="other"),)
    assert assess_control_intent_join(drift, now=NOW + 1, action=ControlIntentAction.DISABLE_PUBLIC_BRIDGE, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST).decision_kind is ControlIntentDecisionKind.QUARANTINE_PROFILE_DRIFT
    fork = disable_bridge_signals() + (control_signal(ControlSignalKind.OPERATOR_INTENT, key=KEY_E, family="fam-e", path="path-e"),)
    assert assess_control_intent_join(fork, now=NOW + 1, action=ControlIntentAction.DISABLE_PUBLIC_BRIDGE, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST).decision_kind is ControlIntentDecisionKind.QUARANTINE_SEQUENCE_FORK
    bad = replace(sigs[0], signature=b"x" * 64)
    assert assess_control_intent_join((bad,) + sigs[1:], now=NOW + 1, action=ControlIntentAction.DISABLE_PUBLIC_BRIDGE, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST).decision_kind is ControlIntentDecisionKind.QUARANTINE_BAD_SIGNATURE


def test_control_intent_resume_profile_is_a_different_join_shape() -> None:
    report = assess_control_intent_join(resume_signals(), now=NOW + 1, action=ControlIntentAction.RESUME_PROFILE, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST)
    assert report.decision_kind is ControlIntentDecisionKind.ACCEPT_JOINED_CONTROL_INTENT
    wrong_action = resume_signals()[:-1] + (control_signal(ControlSignalKind.HARD_NEGATIVE_SCAN, action=ControlIntentAction.DISABLE_PUBLIC_BRIDGE, key=KEY_D, family="fam-d", path="path-d"),)
    assert assess_control_intent_join(wrong_action, now=NOW + 1, action=ControlIntentAction.RESUME_PROFILE, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST).decision_kind is ControlIntentDecisionKind.QUARANTINE_ACTION_DRIFT


def firewall_signal(kind: BridgeFirewallSignalKind, *, key=KEY_A, profile=PROFILE, service=SERVICE, scope=SCOPE, seq=1, accepted=True, public=False, disabled=False, clear=True, family="fam-a", path="path-a"):
    return make_bridge_firewall_signal(
        keypair=key,
        kind=kind,
        profile_id=profile,
        service_name=service,
        scope_digest=scope,
        sequence=seq,
        report_digest=d(f"firewall-{kind.value}-{seq}-{family}"),
        accepted=accepted,
        public_exposure=public,
        bridge_disabled=disabled,
        hard_negative_clear=clear,
        family_id=family,
        path_family=path,
        issued_at=NOW,
        expires_at=NOW + 100,
    )


def public_firewall_signals():
    return (
        firewall_signal(BridgeFirewallSignalKind.ANNOUNCEMENT, key=KEY_A, family="fam-a", path="path-a", public=True),
        firewall_signal(BridgeFirewallSignalKind.INGRESS_GATE, key=KEY_B, family="fam-b", path="path-b", public=True),
        firewall_signal(BridgeFirewallSignalKind.LOAD_SHEATH, key=KEY_C, family="fam-c", path="path-c"),
        firewall_signal(BridgeFirewallSignalKind.OPERATOR_KEY, key=KEY_D, family="fam-d", path="path-d"),
        firewall_signal(BridgeFirewallSignalKind.HARD_NEGATIVE_SCAN, key=KEY_E, family="fam-e", path="path-e"),
    )


def private_firewall_signals():
    return (
        firewall_signal(BridgeFirewallSignalKind.ANNOUNCEMENT, key=KEY_A, family="fam-a", path="path-a"),
        firewall_signal(BridgeFirewallSignalKind.INGRESS_GATE, key=KEY_B, family="fam-b", path="path-b"),
        firewall_signal(BridgeFirewallSignalKind.LOAD_SHEATH, key=KEY_C, family="fam-c", path="path-c"),
    )


def closed_firewall_signals():
    return (
        firewall_signal(BridgeFirewallSignalKind.BRIDGE_DISABLE, key=KEY_A, family="fam-a", path="path-a", disabled=True),
        firewall_signal(BridgeFirewallSignalKind.ANNOUNCEMENT_REPAIR, key=KEY_B, family="fam-b", path="path-b"),
        firewall_signal(BridgeFirewallSignalKind.HARD_NEGATIVE_SCAN, key=KEY_C, family="fam-c", path="path-c"),
    )


def test_bridge_firewall_accepts_public_private_and_closed_modes_separately() -> None:
    public = assess_bridge_firewall(public_firewall_signals(), now=NOW + 1, mode=BridgeFirewallMode.PUBLIC_BRIDGE, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE)
    assert public.decision_kind is BridgeFirewallDecisionKind.ACCEPT_PUBLIC_BRIDGE_WINDOW
    assert public.public_exposure_seen
    private = assess_bridge_firewall(private_firewall_signals(), now=NOW + 1, mode=BridgeFirewallMode.PRIVATE_GARDEN, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE)
    assert private.decision_kind is BridgeFirewallDecisionKind.ACCEPT_PRIVATE_GARDEN_WINDOW
    closed = assess_bridge_firewall(closed_firewall_signals(), now=NOW + 1, mode=BridgeFirewallMode.CLOSED_PUBLIC_BRIDGE, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE)
    assert closed.decision_kind is BridgeFirewallDecisionKind.ACCEPT_CLOSED_PUBLIC_BRIDGE


def test_bridge_firewall_blocks_public_after_disable_stale_or_dirty_signals() -> None:
    disabled_public = public_firewall_signals() + (firewall_signal(BridgeFirewallSignalKind.BRIDGE_DISABLE, key=KEY_A, family="fam-z", path="path-z", disabled=True),)
    assert assess_bridge_firewall(disabled_public, now=NOW + 1, mode=BridgeFirewallMode.PUBLIC_BRIDGE, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE).decision_kind is BridgeFirewallDecisionKind.QUARANTINE_PUBLIC_EXPOSURE_AFTER_DISABLE
    stale = public_firewall_signals() + (firewall_signal(BridgeFirewallSignalKind.STALE_PUBLIC_ANNOUNCEMENT, key=KEY_A, family="fam-z", path="path-z", public=True),)
    assert assess_bridge_firewall(stale, now=NOW + 1, mode=BridgeFirewallMode.PUBLIC_BRIDGE, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE).decision_kind is BridgeFirewallDecisionKind.QUARANTINE_STALE_PUBLIC_ANNOUNCEMENT
    dirty = public_firewall_signals()[:-1] + (firewall_signal(BridgeFirewallSignalKind.HARD_NEGATIVE_SCAN, key=KEY_E, family="fam-e", path="path-e", clear=False),)
    assert assess_bridge_firewall(dirty, now=NOW + 1, mode=BridgeFirewallMode.PUBLIC_BRIDGE, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE).decision_kind is BridgeFirewallDecisionKind.HOLD_COOLDOWN_OR_HARD_NEGATIVE


def test_bridge_firewall_catches_missing_mismatch_low_diversity_and_fork() -> None:
    assert assess_bridge_firewall(public_firewall_signals()[:-1], now=NOW + 1, mode=BridgeFirewallMode.PUBLIC_BRIDGE, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE).decision_kind is BridgeFirewallDecisionKind.HOLD_MISSING_REQUIRED_SIGNAL
    mismatch = private_firewall_signals()
    assert assess_bridge_firewall(mismatch, now=NOW + 1, mode=BridgeFirewallMode.PUBLIC_BRIDGE, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE).decision_kind is BridgeFirewallDecisionKind.HOLD_MISSING_REQUIRED_SIGNAL
    mono = tuple(firewall_signal(sig.kind, key=KEY_A, family="one", path="one", public=sig.public_exposure) for sig in public_firewall_signals())
    assert assess_bridge_firewall(mono, now=NOW + 1, mode=BridgeFirewallMode.PUBLIC_BRIDGE, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE).decision_kind is BridgeFirewallDecisionKind.HOLD_LOW_FAMILY_DIVERSITY
    fork = public_firewall_signals() + (firewall_signal(BridgeFirewallSignalKind.ANNOUNCEMENT, key=KEY_E, family="fam-fork", path="path-fork", public=True),)
    assert assess_bridge_firewall(fork, now=NOW + 1, mode=BridgeFirewallMode.PUBLIC_BRIDGE, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE).decision_kind is BridgeFirewallDecisionKind.QUARANTINE_SEQUENCE_FORK


def test_bridge_firewall_private_mode_refuses_accidental_public_exposure_and_replay() -> None:
    leaked_private = private_firewall_signals()[:-1] + (firewall_signal(BridgeFirewallSignalKind.LOAD_SHEATH, key=KEY_C, family="fam-c", path="path-c", public=True),)
    assert assess_bridge_firewall(leaked_private, now=NOW + 1, mode=BridgeFirewallMode.PRIVATE_GARDEN, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE).decision_kind is BridgeFirewallDecisionKind.QUARANTINE_PUBLIC_EXPOSURE_MISMATCH
    sigs = private_firewall_signals()
    assert assess_bridge_firewall(sigs, now=NOW + 1, mode=BridgeFirewallMode.PRIVATE_GARDEN, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, previously_seen_signals=(sigs[0].signal_digest,)).decision_kind is BridgeFirewallDecisionKind.QUARANTINE_REPLAY


def test_foldtrim_current_revision_path_passes() -> None:
    report = audit_fold_trim(".", revision="rev0043")
    assert report.status == "pass"
    assert report.predecessor_status == "pass"
    assert report.foldmap_status == "pass"
    assert report.registry_status == "pass"
