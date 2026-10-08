from __future__ import annotations

from dataclasses import replace

from i2p_dht_lab.announcementrepair import (
    AnnouncementRepairDecisionKind,
    RepairSignalKind,
    assess_announcement_repair,
    make_announcement_repair_signal,
)
from i2p_dht_lab.controlplanefold import audit_controlplane_fold
from i2p_dht_lab.identity import DhtKeypair
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.multiservice import (
    MultiServiceAction,
    MultiServiceDecisionKind,
    ServiceRuntimeState,
    assess_multi_service_action,
    make_service_runtime_observation,
)
from i2p_dht_lab.operatorkey import (
    OperatorKeyDecisionKind,
    OperatorKeyNoticeKind,
    assess_operator_key_transition,
    make_operator_key_notice,
    make_operator_key_witness,
)
from i2p_dht_lab.profilecooldown import (
    CooldownDecisionKind,
    CooldownKind,
    RecoverySignalKind,
    assess_profile_cooldown,
    make_profile_cooldown_entry,
    make_recovery_signal,
)

NOW = 1_800_000
PROFILE = "garden-profile"
SERVICE = "seed-gate"
SIBLING = "head-watch"
SCOPE = sha256(b"scope")
SESSION = sha256(b"session")
SESSION2 = sha256(b"session-2")
ROUTER = sha256(b"router")
BRIDGE_DISABLE = sha256(b"bridge-disable")
CATALOG = sha256(b"catalog")
ANNOUNCEMENT = sha256(b"announcement")

KEY_A = DhtKeypair.from_seed(b"A" * 32)
KEY_B = DhtKeypair.from_seed(b"B" * 32)
KEY_C = DhtKeypair.from_seed(b"C" * 32)
KEY_D = DhtKeypair.from_seed(b"D" * 32)
OLD_OPERATOR = DhtKeypair.from_seed(b"O" * 32)
NEW_OPERATOR = DhtKeypair.from_seed(b"N" * 32)


def d(label: str) -> bytes:
    return sha256(label.encode("utf-8"))


def service_obs(name: str, state: ServiceRuntimeState, *, key=KEY_A, session=SESSION, family="fam-a", path="path-a", public=False, seq=0, profile=PROFILE, router=ROUTER):
    return make_service_runtime_observation(
        keypair=key,
        service_name=name,
        profile_id=profile,
        session_id_digest=session,
        router_report_digest=router,
        state=state,
        sequence=seq,
        issued_at=NOW,
        expires_at=NOW + 100,
        family_id=family,
        path_family=path,
        public_bridge_active=public,
    )


def test_multiservice_allows_isolated_stop_but_blocks_shared_router_with_active_sibling() -> None:
    target = service_obs(SERVICE, ServiceRuntimeState.PAUSED, family="fam-a", path="path-a")
    sibling = service_obs(SIBLING, ServiceRuntimeState.ACTIVE, key=KEY_B, session=SESSION2, family="fam-b", path="path-b")
    isolated = assess_multi_service_action((target, sibling), now=NOW + 1, action=MultiServiceAction.STOP_ONE_SESSION, target_service=SERVICE, expected_profile_id=PROFILE, expected_router_report_digest=ROUTER, expected_session_id_digest=SESSION)
    assert isolated.decision_kind is MultiServiceDecisionKind.ACCEPT_ISOLATED_SERVICE_ACTION
    shared = assess_multi_service_action((target, sibling), now=NOW + 1, action=MultiServiceAction.STOP_BUNDLED_ROUTER, target_service=SERVICE, expected_profile_id=PROFILE, expected_router_report_digest=ROUTER)
    assert shared.decision_kind is MultiServiceDecisionKind.HOLD_ACTIVE_SIBLING_SERVICES
    assert shared.active_sibling_services == (SIBLING,)


def test_multiservice_accepts_router_stop_only_after_all_services_drain_and_public_bridge_is_gone() -> None:
    target = service_obs(SERVICE, ServiceRuntimeState.STOPPED, family="fam-a", path="path-a")
    sibling = service_obs(SIBLING, ServiceRuntimeState.DRAINING, key=KEY_B, session=SESSION2, family="fam-b", path="path-b")
    report = assess_multi_service_action((target, sibling), now=NOW + 1, action=MultiServiceAction.STOP_BUNDLED_ROUTER, target_service=SERVICE, expected_profile_id=PROFILE, expected_router_report_digest=ROUTER)
    assert report.decision_kind is MultiServiceDecisionKind.ACCEPT_SHARED_ROUTER_ACTION
    bridge = service_obs(SIBLING, ServiceRuntimeState.DRAINING, key=KEY_B, session=SESSION2, family="fam-b", path="path-b", public=True)
    assert assess_multi_service_action((target, bridge), now=NOW + 1, action=MultiServiceAction.STOP_BUNDLED_ROUTER, target_service=SERVICE, expected_profile_id=PROFILE, expected_router_report_digest=ROUTER).decision_kind is MultiServiceDecisionKind.HOLD_PUBLIC_BRIDGE_STILL_ACTIVE


def test_multiservice_blocks_forks_drift_replay_and_low_diversity() -> None:
    first = service_obs(SERVICE, ServiceRuntimeState.STOPPED, family="one", path="one")
    fork = service_obs(SERVICE, ServiceRuntimeState.PAUSED, family="two", path="two")
    assert assess_multi_service_action((first, fork), now=NOW + 1, action=MultiServiceAction.STOP_BUNDLED_ROUTER, target_service=SERVICE, expected_profile_id=PROFILE, expected_router_report_digest=ROUTER).decision_kind is MultiServiceDecisionKind.QUARANTINE_SEQUENCE_FORK
    drift = service_obs(SERVICE, ServiceRuntimeState.STOPPED, profile="other", family="one", path="one")
    assert assess_multi_service_action((drift,), now=NOW + 1, action=MultiServiceAction.STOP_ONE_SESSION, target_service=SERVICE, expected_profile_id=PROFILE, expected_router_report_digest=ROUTER).decision_kind is MultiServiceDecisionKind.QUARANTINE_PROFILE_DRIFT
    assert assess_multi_service_action((first,), now=NOW + 1, action=MultiServiceAction.STOP_ONE_SESSION, target_service=SERVICE, expected_profile_id=PROFILE, expected_router_report_digest=ROUTER, previously_seen_observations=(first.observation_digest,)).decision_kind is MultiServiceDecisionKind.QUARANTINE_REPLAY
    assert assess_multi_service_action((first,), now=NOW + 1, action=MultiServiceAction.STOP_BUNDLED_ROUTER, target_service=SERVICE, expected_profile_id=PROFILE, expected_router_report_digest=ROUTER).decision_kind is MultiServiceDecisionKind.HOLD_LOW_SERVICE_FAMILY_DIVERSITY


def cooldown_entry(**kw):
    args = dict(keypair=OLD_OPERATOR, profile_id=PROFILE, kind=CooldownKind.EMERGENCY_FREEZE, sequence=0, previous_entry_digest=b"\x00" * 32, issued_at=NOW, expires_at=NOW + 500, frozen_until=NOW + 50)
    args.update(kw)
    return make_profile_cooldown_entry(**args)


def recovery(kind: RecoverySignalKind, *, key=KEY_A, family="fam-a", clear=True):
    return make_recovery_signal(keypair=key, profile_id=PROFILE, kind=kind, evidence_digest=d(kind.value), issued_at=NOW + 60, expires_at=NOW + 500, family_id=family, hard_negative_clear=clear)


def recovery_signals():
    return (
        recovery(RecoverySignalKind.OPERATOR_RESUME, key=KEY_A, family="fam-a"),
        recovery(RecoverySignalKind.BREAKER_RECOVERY, key=KEY_B, family="fam-b"),
        recovery(RecoverySignalKind.ROUTER_OK, key=KEY_C, family="fam-c"),
        recovery(RecoverySignalKind.HARD_NEGATIVE_SCAN, key=KEY_D, family="fam-d"),
    )


def test_profile_cooldown_holds_until_window_expires_then_accepts_diverse_recovery() -> None:
    entry = cooldown_entry()
    assert assess_profile_cooldown((entry,), recovery_signals(), now=NOW + 10, expected_profile_id=PROFILE).decision_kind is CooldownDecisionKind.HOLD_COOLDOWN_ACTIVE
    report = assess_profile_cooldown((entry,), recovery_signals(), now=NOW + 80, expected_profile_id=PROFILE)
    assert report.decision_kind is CooldownDecisionKind.ACCEPT_RESUME_AFTER_COOLDOWN


def test_profile_cooldown_blocks_missing_low_diversity_hard_negative_and_fork() -> None:
    entry = cooldown_entry()
    missing = recovery_signals()[:-1]
    assert assess_profile_cooldown((entry,), missing, now=NOW + 80, expected_profile_id=PROFILE).decision_kind is CooldownDecisionKind.HOLD_NEEDS_RECOVERY_EVIDENCE
    mono = tuple(make_recovery_signal(keypair=KEY_A, profile_id=PROFILE, kind=kind, evidence_digest=d(kind.value), issued_at=NOW + 60, expires_at=NOW + 500, family_id="one") for kind in (RecoverySignalKind.OPERATOR_RESUME, RecoverySignalKind.BREAKER_RECOVERY, RecoverySignalKind.ROUTER_OK, RecoverySignalKind.HARD_NEGATIVE_SCAN))
    assert assess_profile_cooldown((entry,), mono, now=NOW + 80, expected_profile_id=PROFILE).decision_kind is CooldownDecisionKind.HOLD_LOW_RECOVERY_FAMILY_DIVERSITY
    bad = recovery(RecoverySignalKind.HARD_NEGATIVE_SCAN, clear=False)
    assert assess_profile_cooldown((entry,), recovery_signals()[:-1] + (bad,), now=NOW + 80, expected_profile_id=PROFILE).decision_kind is CooldownDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESENT
    fork = cooldown_entry(kind=CooldownKind.KEY_CRISIS)
    assert assess_profile_cooldown((entry, fork), recovery_signals(), now=NOW + 80, expected_profile_id=PROFILE).decision_kind is CooldownDecisionKind.QUARANTINE_SEQUENCE_FORK


def operator_notice(kind: OperatorKeyNoticeKind, *, seq=0, old=OLD_OPERATOR, new=NEW_OPERATOR, signer=None, cosign=True, scope=SCOPE, hard=b"\x00" * 32):
    signer = signer or (new if kind is OperatorKeyNoticeKind.RECOVER else old)
    return make_operator_key_notice(
        signer=signer,
        profile_id=PROFILE,
        kind=kind,
        sequence=seq,
        previous_notice_digest=b"\x00" * 32,
        scope_digest=scope,
        old_operator_key=old.public_key_bytes,
        successor_operator_key=new.public_key_bytes,
        issued_at=NOW,
        expires_at=NOW + 100,
        hard_negative_digest=hard,
        successor=new if cosign else None,
    )


def test_operator_key_rotation_requires_successor_cosign_and_blocks_drift() -> None:
    notice = operator_notice(OperatorKeyNoticeKind.ROTATE)
    report = assess_operator_key_transition((notice,), (), now=NOW + 1, expected_profile_id=PROFILE, expected_old_operator_key=OLD_OPERATOR.public_key_bytes, expected_scope_digest=SCOPE)
    assert report.decision_kind is OperatorKeyDecisionKind.ACCEPT_ROTATION
    missing = operator_notice(OperatorKeyNoticeKind.ROTATE, cosign=False)
    assert assess_operator_key_transition((missing,), (), now=NOW + 1, expected_profile_id=PROFILE, expected_old_operator_key=OLD_OPERATOR.public_key_bytes, expected_scope_digest=SCOPE).decision_kind is OperatorKeyDecisionKind.HOLD_NEEDS_COSIGN
    drift = operator_notice(OperatorKeyNoticeKind.ROTATE, scope=d("wider-scope"))
    assert assess_operator_key_transition((drift,), (), now=NOW + 1, expected_profile_id=PROFILE, expected_old_operator_key=OLD_OPERATOR.public_key_bytes, expected_scope_digest=SCOPE).decision_kind is OperatorKeyDecisionKind.QUARANTINE_SCOPE_WIDENING


def test_operator_key_recovery_needs_witness_diversity_and_preserves_hard_negative() -> None:
    hard = d("compromised-old-key")
    recover = operator_notice(OperatorKeyNoticeKind.RECOVER, signer=NEW_OPERATOR, hard=hard)
    w1 = make_operator_key_witness(keypair=KEY_A, profile_id=PROFILE, notice_digest=recover.notice_digest, family_id="fam-a", issued_at=NOW + 1, expires_at=NOW + 100)
    w2 = make_operator_key_witness(keypair=KEY_B, profile_id=PROFILE, notice_digest=recover.notice_digest, family_id="fam-b", issued_at=NOW + 1, expires_at=NOW + 100)
    assert assess_operator_key_transition((recover,), (w1,), now=NOW + 2, expected_profile_id=PROFILE, expected_old_operator_key=OLD_OPERATOR.public_key_bytes, expected_scope_digest=SCOPE, required_hard_negative_digest=hard).decision_kind is OperatorKeyDecisionKind.HOLD_NEEDS_WITNESS_DIVERSITY
    assert assess_operator_key_transition((recover,), (w1, w2), now=NOW + 2, expected_profile_id=PROFILE, expected_old_operator_key=OLD_OPERATOR.public_key_bytes, expected_scope_digest=SCOPE, required_hard_negative_digest=hard).decision_kind is OperatorKeyDecisionKind.ACCEPT_RECOVERY
    assert assess_operator_key_transition((recover,), (w1, w2), now=NOW + 2, expected_profile_id=PROFILE, expected_old_operator_key=OLD_OPERATOR.public_key_bytes, expected_scope_digest=SCOPE, required_hard_negative_digest=d("other-hard-negative")).decision_kind is OperatorKeyDecisionKind.QUARANTINE_HARD_NEGATIVE_DROP


def repair_signal(kind: RepairSignalKind, *, key=KEY_A, family="fam-a", seq=1, public=False, clear=True, catalog=CATALOG):
    return make_announcement_repair_signal(
        keypair=key,
        service_name=SERVICE,
        scope_digest=SCOPE,
        kind=kind,
        sequence=seq,
        catalog_digest=catalog,
        announcement_digest=ANNOUNCEMENT,
        bridge_disable_digest=BRIDGE_DISABLE,
        issued_at=NOW,
        expires_at=NOW + 100,
        family_id=family,
        public_exposure=public,
        hard_negative_clear=clear,
    )


def good_repair_signals():
    return (
        repair_signal(RepairSignalKind.BRIDGE_DISABLE, key=KEY_A, family="fam-a"),
        repair_signal(RepairSignalKind.PUBLIC_WITHDRAWAL, key=KEY_B, family="fam-b"),
        repair_signal(RepairSignalKind.SUCCESSOR_CATALOG, key=KEY_C, family="fam-c", seq=2, catalog=d("catalog-v2")),
        repair_signal(RepairSignalKind.TOMBSTONE_SCAN, key=KEY_D, family="fam-d"),
    )


def test_announcement_repair_accepts_bridge_disable_withdrawal_and_successor_catalog() -> None:
    report = assess_announcement_repair(good_repair_signals(), now=NOW + 1, expected_service_name=SERVICE, expected_scope_digest=SCOPE, bridge_disable_digest=BRIDGE_DISABLE, previous_catalog_sequence=1)
    assert report.decision_kind is AnnouncementRepairDecisionKind.ACCEPT_REPAIR


def test_announcement_repair_rejects_stale_public_rollback_fork_and_low_diversity() -> None:
    stale = good_repair_signals() + (repair_signal(RepairSignalKind.STALE_PUBLIC_ANNOUNCEMENT, key=KEY_A, family="fam-a", public=True),)
    assert assess_announcement_repair(stale, now=NOW + 1, expected_service_name=SERVICE, expected_scope_digest=SCOPE, bridge_disable_digest=BRIDGE_DISABLE, previous_catalog_sequence=1).decision_kind is AnnouncementRepairDecisionKind.QUARANTINE_STALE_PUBLIC_ANNOUNCEMENT
    rollback = tuple(sig if sig.kind is not RepairSignalKind.SUCCESSOR_CATALOG else repair_signal(RepairSignalKind.SUCCESSOR_CATALOG, key=KEY_C, family="fam-c", seq=1, catalog=d("old-catalog")) for sig in good_repair_signals())
    assert assess_announcement_repair(rollback, now=NOW + 1, expected_service_name=SERVICE, expected_scope_digest=SCOPE, bridge_disable_digest=BRIDGE_DISABLE, previous_catalog_sequence=1).decision_kind is AnnouncementRepairDecisionKind.QUARANTINE_SUCCESSOR_ROLLBACK
    fork = good_repair_signals() + (repair_signal(RepairSignalKind.SUCCESSOR_CATALOG, key=KEY_A, family="fam-a", seq=2, catalog=d("fork-catalog")),)
    assert assess_announcement_repair(fork, now=NOW + 1, expected_service_name=SERVICE, expected_scope_digest=SCOPE, bridge_disable_digest=BRIDGE_DISABLE, previous_catalog_sequence=1).decision_kind is AnnouncementRepairDecisionKind.QUARANTINE_SUCCESSOR_FORK
    mono = tuple(repair_signal(sig.kind, key=KEY_A, family="one", seq=sig.sequence, catalog=sig.catalog_digest) for sig in good_repair_signals())
    assert assess_announcement_repair(mono, now=NOW + 1, expected_service_name=SERVICE, expected_scope_digest=SCOPE, bridge_disable_digest=BRIDGE_DISABLE, previous_catalog_sequence=1).decision_kind is AnnouncementRepairDecisionKind.HOLD_LOW_FAMILY_DIVERSITY


def test_controlplanefold_current_revision_path_passes() -> None:
    report = audit_controlplane_fold(".", revision="rev0042")
    assert report.status == "pass"
    assert report.predecessor_status == "pass"
    assert report.foldmap_status == "pass"
    assert report.registry_status == "pass"
