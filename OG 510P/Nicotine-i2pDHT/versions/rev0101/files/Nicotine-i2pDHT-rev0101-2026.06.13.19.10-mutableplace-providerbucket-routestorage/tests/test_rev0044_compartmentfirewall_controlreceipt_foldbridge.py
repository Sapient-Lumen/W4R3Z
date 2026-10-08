from __future__ import annotations

from dataclasses import replace

from i2p_dht_lab.authoritysplit import AuthorityComponent, ComponentStatus, assess_authority_split, make_authority_component_report
from i2p_dht_lab.bridgefirewall import BridgeFirewallDecisionKind, BridgeFirewallMode, BridgeFirewallSignalKind, assess_bridge_firewall, make_bridge_firewall_signal
from i2p_dht_lab.compartmentfirewall import CompartmentFirewallDecisionKind, assess_compartment_firewall
from i2p_dht_lab.controlintent import ControlIntentAction, ControlIntentDecisionKind, ControlSignalKind, assess_control_intent_join, make_control_intent_signal
from i2p_dht_lab.controlreceipt import ControlReceiptDecisionKind, ControlReceiptKind, assess_control_receipts, make_control_receipt
from i2p_dht_lab.foldbridge import audit_fold_bridge
from i2p_dht_lab.identity import DhtKeypair
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.keycompartment import CompartmentDecisionKind, KeyRole, assess_key_compartment, make_key_binding_capsule

NOW = 1_000
PROFILE = "garden-profile-alpha"
SERVICE_NAME = "bridge-seed-gate"
SCOPE = sha256(b"rev0044-scope")
OBJECT = sha256(b"rev0044-object")
REQUEST = sha256(b"rev0044-request")
ROOT_BINDING = sha256(b"rev0044-root-binding")
OP_NOTICE = sha256(b"rev0044-operator-notice")
ZERO = b"\x00" * 32


def key(label: str) -> DhtKeypair:
    return DhtKeypair.from_seed(sha256(("rev0044-key-" + label).encode("utf-8")))


ROOT = key("root")
OPERATOR = key("operator")
SERVICE = key("service")
ROUTER = key("router")
WITNESS = key("witness")
A = key("family-a")
B = key("family-b")
C = key("family-c")
D = key("family-d")
E = key("family-e")


def d(label: str) -> bytes:
    return sha256(label.encode("utf-8"))


def binding_report(role: KeyRole, bound: bytes, *, family: str, signer=OPERATOR):
    capsule = make_key_binding_capsule(
        keypair=signer,
        profile_id=PROFILE,
        role=role,
        bound_public_key=bound,
        scope_digest=SCOPE,
        sequence=0,
        previous_binding_digest=ZERO,
        issued_at=NOW,
        expires_at=NOW + 100,
        family_id=family,
        root_binding_digest=ROOT_BINDING,
        operator_notice_digest=OP_NOTICE,
    )
    report = assess_key_compartment(
        (capsule,),
        now=NOW + 1,
        expected_profile_id=PROFILE,
        expected_scope_digest=SCOPE,
        requested_role=role,
        requested_public_key=bound,
        min_family_diversity=1,
    )
    assert report.decision_kind is CompartmentDecisionKind.ACCEPT_COMPARTMENTED_KEY
    return report


def role_reports(*, reuse_service_for_router: bool = False, missing_router: bool = False):
    reports = [
        binding_report(KeyRole.OPERATOR, OPERATOR.public_key_bytes, family="role-a"),
        binding_report(KeyRole.SERVICE_SIGNER, SERVICE.public_key_bytes, family="role-b"),
    ]
    if not missing_router:
        reports.append(binding_report(KeyRole.ROUTER_DESTINATION, SERVICE.public_key_bytes if reuse_service_for_router else ROUTER.public_key_bytes, family="role-c"))
    return tuple(reports)


def component(component: AuthorityComponent, *, signer, actor, family: str, status=ComponentStatus.PASS_):
    return make_authority_component_report(
        keypair=signer,
        component=component,
        status=status,
        profile_id=PROFILE,
        scope_digest=SCOPE,
        object_digest=OBJECT,
        request_digest=REQUEST,
        actor_public_key=actor.public_key_bytes,
        evidence_digest=d(f"component-{component.value}-{status.value}"),
        sequence=0,
        issued_at=NOW,
        expires_at=NOW + 100,
        family_id=family,
    )


def authority(status=ComponentStatus.PASS_, *, allow_watch: bool = False):
    reports = (
        component(AuthorityComponent.KEY_COMPARTMENT, signer=A, actor=SERVICE, family="fam-a"),
        component(AuthorityComponent.OPERATOR_KEY, signer=B, actor=OPERATOR, family="fam-b", status=status),
        component(AuthorityComponent.HARD_NEGATIVE_SCAN, signer=C, actor=WITNESS, family="fam-c"),
    )
    return assess_authority_split(
        reports,
        now=NOW + 1,
        expected_profile_id=PROFILE,
        expected_scope_digest=SCOPE,
        expected_object_digest=OBJECT,
        expected_request_digest=REQUEST,
        required_components=(AuthorityComponent.KEY_COMPARTMENT, AuthorityComponent.OPERATOR_KEY, AuthorityComponent.HARD_NEGATIVE_SCAN),
        min_family_diversity=3,
        allow_watch_components=allow_watch,
    )


def control_signal(kind: ControlSignalKind, *, keypair: DhtKeypair, family: str, path: str, action=ControlIntentAction.KEEP_GARDEN_ONLINE, accepted=True, clear=True, request=REQUEST):
    return make_control_intent_signal(
        keypair=keypair,
        kind=kind,
        action=action,
        profile_id=PROFILE,
        service_name=SERVICE_NAME,
        scope_digest=SCOPE,
        request_digest=request,
        sequence=0,
        report_digest=d(f"control-{kind.value}-{family}"),
        accepted=accepted,
        hard_negative_clear=clear,
        family_id=family,
        path_family=path,
        issued_at=NOW,
        expires_at=NOW + 100,
    )


def control(action=ControlIntentAction.KEEP_GARDEN_ONLINE, *, accepted=True, clear=True, request=REQUEST):
    if action is ControlIntentAction.DISABLE_PUBLIC_BRIDGE:
        signals = (
            control_signal(ControlSignalKind.OPERATOR_INTENT, keypair=A, family="fam-a", path="path-a", action=action, accepted=accepted, clear=clear, request=request),
            control_signal(ControlSignalKind.MULTISERVICE, keypair=B, family="fam-b", path="path-b", action=action, request=request),
            control_signal(ControlSignalKind.ANNOUNCEMENT_REPAIR, keypair=C, family="fam-c", path="path-c", action=action, request=request),
            control_signal(ControlSignalKind.HARD_NEGATIVE_SCAN, keypair=D, family="fam-d", path="path-d", action=action, request=request),
        )
    else:
        signals = (
            control_signal(ControlSignalKind.MULTISERVICE, keypair=A, family="fam-a", path="path-a", action=action, accepted=accepted, clear=clear, request=request),
            control_signal(ControlSignalKind.PROFILE_COOLDOWN, keypair=B, family="fam-b", path="path-b", action=action, request=request),
            control_signal(ControlSignalKind.ROUTER_HARNESS, keypair=C, family="fam-c", path="path-c", action=action, request=request),
        )
    report = assess_control_intent_join(signals, now=NOW + 1, action=action, expected_profile_id=PROFILE, expected_service_name=SERVICE_NAME, expected_scope_digest=SCOPE, expected_request_digest=request)
    assert ((report.decision_kind is ControlIntentDecisionKind.ACCEPT_JOINED_CONTROL_INTENT) == accepted) if clear else True
    return report


def firewall_signal(kind: BridgeFirewallSignalKind, *, keypair: DhtKeypair, family: str, path: str, public=False, disabled=False, accepted=True, clear=True):
    return make_bridge_firewall_signal(
        keypair=keypair,
        kind=kind,
        profile_id=PROFILE,
        service_name=SERVICE_NAME,
        scope_digest=SCOPE,
        sequence=0,
        report_digest=d(f"firewall-{kind.value}-{family}"),
        accepted=accepted,
        public_exposure=public,
        bridge_disabled=disabled,
        hard_negative_clear=clear,
        family_id=family,
        path_family=path,
        issued_at=NOW,
        expires_at=NOW + 100,
    )


def firewall(mode=BridgeFirewallMode.PUBLIC_BRIDGE, *, stale=False, public=True):
    if mode is BridgeFirewallMode.PUBLIC_BRIDGE:
        signals = (
            firewall_signal(BridgeFirewallSignalKind.ANNOUNCEMENT, keypair=A, family="fam-a", path="path-a", public=public),
            firewall_signal(BridgeFirewallSignalKind.INGRESS_GATE, keypair=B, family="fam-b", path="path-b", public=public),
            firewall_signal(BridgeFirewallSignalKind.LOAD_SHEATH, keypair=C, family="fam-c", path="path-c"),
            firewall_signal(BridgeFirewallSignalKind.OPERATOR_KEY, keypair=D, family="fam-d", path="path-d"),
            firewall_signal(BridgeFirewallSignalKind.HARD_NEGATIVE_SCAN, keypair=E, family="fam-e", path="path-e"),
        )
        if stale:
            signals += (firewall_signal(BridgeFirewallSignalKind.STALE_PUBLIC_ANNOUNCEMENT, keypair=E, family="fam-z", path="path-z", public=True),)
    elif mode is BridgeFirewallMode.PRIVATE_GARDEN:
        signals = (
            firewall_signal(BridgeFirewallSignalKind.ANNOUNCEMENT, keypair=A, family="fam-a", path="path-a"),
            firewall_signal(BridgeFirewallSignalKind.INGRESS_GATE, keypair=B, family="fam-b", path="path-b"),
            firewall_signal(BridgeFirewallSignalKind.LOAD_SHEATH, keypair=C, family="fam-c", path="path-c"),
        )
    else:
        signals = (
            firewall_signal(BridgeFirewallSignalKind.BRIDGE_DISABLE, keypair=A, family="fam-a", path="path-a", disabled=True),
            firewall_signal(BridgeFirewallSignalKind.ANNOUNCEMENT_REPAIR, keypair=B, family="fam-b", path="path-b"),
            firewall_signal(BridgeFirewallSignalKind.HARD_NEGATIVE_SCAN, keypair=C, family="fam-c", path="path-c"),
        )
    return assess_bridge_firewall(signals, now=NOW + 1, mode=mode, expected_profile_id=PROFILE, expected_service_name=SERVICE_NAME, expected_scope_digest=SCOPE)


def joined_report(*, mode=BridgeFirewallMode.PUBLIC_BRIDGE, action=ControlIntentAction.KEEP_GARDEN_ONLINE, roles=None, auth=None, ctrl=None, fw=None, hard_negatives=()):
    return assess_compartment_firewall(
        authority_split=auth or authority(),
        role_reports=roles or role_reports(),
        control_intent=ctrl or control(action),
        bridge_firewall=fw or firewall(mode),
        expected_profile_id=PROFILE,
        expected_service_name=SERVICE_NAME,
        expected_scope_digest=SCOPE,
        expected_request_digest=REQUEST,
        mode=mode,
        hard_negative_digests=hard_negatives,
    )


def test_compartment_firewall_accepts_public_bridge_only_after_key_control_firewall_join() -> None:
    report = joined_report()
    assert report.decision_kind is CompartmentFirewallDecisionKind.ACCEPT_COMPARTMENT_FIREWALL
    assert report.accept
    assert len(report.role_digests) == 3


def test_compartment_firewall_blocks_role_reuse_missing_role_and_wrong_action() -> None:
    assert joined_report(roles=role_reports(reuse_service_for_router=True)).decision_kind is CompartmentFirewallDecisionKind.QUARANTINE_ROLE_REUSE
    assert joined_report(roles=role_reports(missing_router=True)).decision_kind is CompartmentFirewallDecisionKind.HOLD_MISSING_ROLE
    assert joined_report(action=ControlIntentAction.DISABLE_PUBLIC_BRIDGE, ctrl=control(ControlIntentAction.DISABLE_PUBLIC_BRIDGE)).decision_kind is CompartmentFirewallDecisionKind.QUARANTINE_ACTION_MISMATCH


def test_compartment_firewall_blocks_component_pressure_and_hard_negative_pressure() -> None:
    watch = joined_report(auth=authority(ComponentStatus.WATCH, allow_watch=True))
    assert watch.decision_kind is CompartmentFirewallDecisionKind.HOLD_AUTHORITY_WATCH
    stale_fw = firewall(stale=True)
    assert stale_fw.decision_kind is BridgeFirewallDecisionKind.QUARANTINE_STALE_PUBLIC_ANNOUNCEMENT
    assert joined_report(fw=stale_fw).decision_kind is CompartmentFirewallDecisionKind.QUARANTINE_FIREWALL_REJECTED
    assert joined_report(hard_negatives=(d("hard-negative"),)).decision_kind is CompartmentFirewallDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE


def test_compartment_firewall_closed_mode_requires_disable_action() -> None:
    closed = joined_report(mode=BridgeFirewallMode.CLOSED_PUBLIC_BRIDGE, action=ControlIntentAction.DISABLE_PUBLIC_BRIDGE, ctrl=control(ControlIntentAction.DISABLE_PUBLIC_BRIDGE), fw=firewall(BridgeFirewallMode.CLOSED_PUBLIC_BRIDGE))
    assert closed.decision_kind is CompartmentFirewallDecisionKind.ACCEPT_COMPARTMENT_FIREWALL
    wrong = joined_report(mode=BridgeFirewallMode.CLOSED_PUBLIC_BRIDGE, fw=firewall(BridgeFirewallMode.CLOSED_PUBLIC_BRIDGE))
    assert wrong.decision_kind is CompartmentFirewallDecisionKind.QUARANTINE_ACTION_MISMATCH


def test_control_receipt_accepts_exact_joined_report_and_blocks_replay_drift_bad_signature() -> None:
    report = joined_report()
    receipt = make_control_receipt(keypair=A, kind=ControlReceiptKind.COMPARTMENT_FIREWALL, joined_report=report, sequence=0, issued_at=NOW, expires_at=NOW + 100, family_id="fam-a")
    assessment = assess_control_receipts((receipt,), now=NOW + 1, kind=ControlReceiptKind.COMPARTMENT_FIREWALL, expected_profile_id=PROFILE, expected_service_name=SERVICE_NAME, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_joined_report_digest=report.report_digest)
    assert assessment.decision_kind is ControlReceiptDecisionKind.ACCEPT_CONTROL_RECEIPT
    assert assess_control_receipts((receipt,), now=NOW + 1, kind=ControlReceiptKind.COMPARTMENT_FIREWALL, expected_profile_id=PROFILE, expected_service_name=SERVICE_NAME, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_joined_report_digest=report.report_digest, previously_seen_receipts=(receipt.receipt_digest,)).decision_kind is ControlReceiptDecisionKind.QUARANTINE_REPLAY
    assert assess_control_receipts((receipt,), now=NOW + 1, kind=ControlReceiptKind.PUBLIC_BRIDGE_SIDE_EFFECT, expected_profile_id=PROFILE, expected_service_name=SERVICE_NAME, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_joined_report_digest=report.report_digest).decision_kind is ControlReceiptDecisionKind.QUARANTINE_KIND_MISMATCH
    assert assess_control_receipts((receipt,), now=NOW + 1, kind=ControlReceiptKind.COMPARTMENT_FIREWALL, expected_profile_id=PROFILE, expected_service_name=SERVICE_NAME, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_joined_report_digest=d("different-report")).decision_kind is ControlReceiptDecisionKind.QUARANTINE_REPORT_DIGEST_DRIFT
    bad = replace(receipt, signature=b"x" * 64)
    assert assess_control_receipts((bad,), now=NOW + 1, kind=ControlReceiptKind.COMPARTMENT_FIREWALL, expected_profile_id=PROFILE, expected_service_name=SERVICE_NAME, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_joined_report_digest=report.report_digest).decision_kind is ControlReceiptDecisionKind.QUARANTINE_BAD_SIGNATURE


def test_control_receipt_previous_link_sequence_fork_and_low_family_pressure() -> None:
    report = joined_report()
    first = make_control_receipt(keypair=A, kind=ControlReceiptKind.COMPARTMENT_FIREWALL, joined_report=report, sequence=0, issued_at=NOW, expires_at=NOW + 100, family_id="fam-a")
    second = make_control_receipt(keypair=B, kind=ControlReceiptKind.COMPARTMENT_FIREWALL, joined_report=report, sequence=1, previous_receipt_digest=first.receipt_digest, issued_at=NOW, expires_at=NOW + 100, family_id="fam-b")
    assert assess_control_receipts((first, second), now=NOW + 1, kind=ControlReceiptKind.COMPARTMENT_FIREWALL, expected_profile_id=PROFILE, expected_service_name=SERVICE_NAME, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_joined_report_digest=report.report_digest, minimum_sequence=1, previous_receipt_digest=first.receipt_digest, min_family_diversity=2).decision_kind is ControlReceiptDecisionKind.ACCEPT_CONTROL_RECEIPT
    wrong_prev = make_control_receipt(keypair=B, kind=ControlReceiptKind.COMPARTMENT_FIREWALL, joined_report=report, sequence=1, previous_receipt_digest=d("wrong-prev"), issued_at=NOW, expires_at=NOW + 100, family_id="fam-b")
    assert assess_control_receipts((first, wrong_prev), now=NOW + 1, kind=ControlReceiptKind.COMPARTMENT_FIREWALL, expected_profile_id=PROFILE, expected_service_name=SERVICE_NAME, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_joined_report_digest=report.report_digest, minimum_sequence=1, previous_receipt_digest=first.receipt_digest).decision_kind is ControlReceiptDecisionKind.QUARANTINE_PREVIOUS_LINK
    fork = make_control_receipt(keypair=C, kind=ControlReceiptKind.COMPARTMENT_FIREWALL, joined_report=report, sequence=1, previous_receipt_digest=first.receipt_digest, issued_at=NOW, expires_at=NOW + 100, family_id="fam-c")
    assert assess_control_receipts((first, second, fork), now=NOW + 1, kind=ControlReceiptKind.COMPARTMENT_FIREWALL, expected_profile_id=PROFILE, expected_service_name=SERVICE_NAME, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_joined_report_digest=report.report_digest, minimum_sequence=1, previous_receipt_digest=first.receipt_digest).decision_kind is ControlReceiptDecisionKind.QUARANTINE_SEQUENCE_FORK
    assert assess_control_receipts((first,), now=NOW + 1, kind=ControlReceiptKind.COMPARTMENT_FIREWALL, expected_profile_id=PROFILE, expected_service_name=SERVICE_NAME, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_joined_report_digest=report.report_digest, min_family_diversity=2).decision_kind is ControlReceiptDecisionKind.HOLD_LOW_FAMILY_DIVERSITY


def test_control_receipt_does_not_accept_unaccepted_joined_report() -> None:
    bad_join = joined_report(roles=role_reports(missing_router=True))
    receipt = make_control_receipt(keypair=A, kind=ControlReceiptKind.COMPARTMENT_FIREWALL, joined_report=bad_join, sequence=0, issued_at=NOW, expires_at=NOW + 100, family_id="fam-a")
    assert assess_control_receipts((receipt,), now=NOW + 1, kind=ControlReceiptKind.COMPARTMENT_FIREWALL, expected_profile_id=PROFILE, expected_service_name=SERVICE_NAME, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_joined_report_digest=bad_join.report_digest).decision_kind is ControlReceiptDecisionKind.HOLD_UNACCEPTED_REPORT


def test_foldbridge_current_revision_path_passes() -> None:
    report = audit_fold_bridge(".", revision="rev0044")
    assert report.status == "pass"
    assert report.predecessor_status == "pass"
    assert report.branchlet_status == "pass"
    assert report.foldmap_status == "pass"
    assert report.registry_status == "pass"
    assert report.ledger_status == "pass"
