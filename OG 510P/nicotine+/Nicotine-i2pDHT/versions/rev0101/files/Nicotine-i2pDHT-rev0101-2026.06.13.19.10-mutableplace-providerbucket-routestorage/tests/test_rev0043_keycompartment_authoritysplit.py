from __future__ import annotations

from dataclasses import replace

from i2p_dht_lab.authoritysplit import (
    AuthorityComponent,
    AuthoritySplitDecisionKind,
    ComponentStatus,
    assess_authority_split,
    make_authority_component_report,
)
from i2p_dht_lab.compartmentfold import audit_compartment_fold
from i2p_dht_lab.identity import DhtKeypair
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.keycompartment import (
    CompartmentDecisionKind,
    KeyRole,
    assess_key_compartment,
    key_fingerprint,
    make_key_binding_capsule,
)

NOW = 1_000
PROFILE = "garden-profile-alpha"


def key(label: str) -> DhtKeypair:
    return DhtKeypair.from_seed(sha256(("rev0043-key-" + label).encode("utf-8")))


ROOT = key("root")
OPERATOR = key("operator")
SERVICE = key("service")
TICKET = key("ticket")
WITNESS = key("witness")
ROUTER = key("router")
FAMILY_A = key("family-a")
FAMILY_B = key("family-b")
FAMILY_C = key("family-c")
FAMILY_D = key("family-d")

SCOPE = sha256(b"rev0043-scope")
OBJECT = sha256(b"rev0043-object")
REQUEST = sha256(b"rev0043-request")
ROOT_BINDING = sha256(b"root-binding")
OP_NOTICE = sha256(b"operator-notice")


def digest(label: str) -> bytes:
    return sha256(label.encode("utf-8"))


def binding(*, signer=OPERATOR, role=KeyRole.SERVICE_SIGNER, bound=None, seq=0, prev=b"\x00" * 32, scope=SCOPE, profile=PROFILE, family="fam-a", issued=NOW, expires=NOW + 100, allowed=()):
    bound = bound or SERVICE.public_key_bytes
    return make_key_binding_capsule(
        keypair=signer,
        profile_id=profile,
        role=role,
        bound_public_key=bound,
        scope_digest=scope,
        sequence=seq,
        previous_binding_digest=prev,
        issued_at=issued,
        expires_at=expires,
        family_id=family,
        allowed_dual_roles=allowed,
        root_binding_digest=ROOT_BINDING,
        operator_notice_digest=OP_NOTICE,
    )


def test_key_compartment_accepts_specific_service_key_and_compatible_ticket_pair() -> None:
    service = binding(role=KeyRole.SERVICE_SIGNER, bound=SERVICE.public_key_bytes, family="fam-a")
    ticket = binding(role=KeyRole.GARDEN_TICKET, bound=SERVICE.public_key_bytes, family="fam-b")
    report = assess_key_compartment(
        (service, ticket),
        now=NOW + 1,
        expected_profile_id=PROFILE,
        expected_scope_digest=SCOPE,
        requested_role=KeyRole.SERVICE_SIGNER,
        requested_public_key=SERVICE.public_key_bytes,
        min_family_diversity=2,
    )
    assert report.decision_kind is CompartmentDecisionKind.ACCEPT_COMPARTMENTED_KEY
    assert report.family_count == 2
    assert report.highest_sequence == 0


def test_key_compartment_rejects_operator_service_dual_use_and_router_service_dual_use() -> None:
    service = binding(role=KeyRole.SERVICE_SIGNER, bound=SERVICE.public_key_bytes, family="fam-a")
    operator_reuse = binding(role=KeyRole.OPERATOR, bound=SERVICE.public_key_bytes, family="fam-b")
    assert assess_key_compartment(
        (service, operator_reuse),
        now=NOW + 1,
        expected_profile_id=PROFILE,
        expected_scope_digest=SCOPE,
        requested_role=KeyRole.SERVICE_SIGNER,
        requested_public_key=SERVICE.public_key_bytes,
        min_family_diversity=1,
    ).decision_kind is CompartmentDecisionKind.QUARANTINE_ROLE_REUSE
    router_reuse = binding(role=KeyRole.ROUTER_DESTINATION, bound=SERVICE.public_key_bytes, family="fam-c")
    assert assess_key_compartment(
        (service, router_reuse),
        now=NOW + 1,
        expected_profile_id=PROFILE,
        expected_scope_digest=SCOPE,
        requested_role=KeyRole.SERVICE_SIGNER,
        requested_public_key=SERVICE.public_key_bytes,
        min_family_diversity=1,
    ).decision_kind is CompartmentDecisionKind.QUARANTINE_ROLE_REUSE


def test_key_compartment_detects_bad_signature_replay_scope_and_crisis() -> None:
    service = binding()
    bad = replace(service, signature=b"0" * 64)
    assert assess_key_compartment((bad,), now=NOW + 1, expected_profile_id=PROFILE, expected_scope_digest=SCOPE, requested_role=KeyRole.SERVICE_SIGNER, requested_public_key=SERVICE.public_key_bytes).decision_kind is CompartmentDecisionKind.QUARANTINE_BAD_SIGNATURE
    assert assess_key_compartment((service,), now=NOW + 1, expected_profile_id=PROFILE, expected_scope_digest=SCOPE, requested_role=KeyRole.SERVICE_SIGNER, requested_public_key=SERVICE.public_key_bytes, previously_seen_binding_digests=(service.binding_digest,)).decision_kind is CompartmentDecisionKind.QUARANTINE_REPLAY
    drift = binding(scope=digest("other-scope"))
    assert assess_key_compartment((drift,), now=NOW + 1, expected_profile_id=PROFILE, expected_scope_digest=SCOPE, requested_role=KeyRole.SERVICE_SIGNER, requested_public_key=SERVICE.public_key_bytes).decision_kind is CompartmentDecisionKind.QUARANTINE_SCOPE_DRIFT
    assert assess_key_compartment((service,), now=NOW + 1, expected_profile_id=PROFILE, expected_scope_digest=SCOPE, requested_role=KeyRole.SERVICE_SIGNER, requested_public_key=SERVICE.public_key_bytes, crisis_key_digests=(key_fingerprint(SERVICE.public_key_bytes),)).decision_kind is CompartmentDecisionKind.QUARANTINE_KEY_CRISIS


def test_key_compartment_previous_link_rollback_and_sequence_fork_pressure() -> None:
    first = binding(seq=0, family="fam-a")
    second = binding(seq=1, prev=first.binding_digest, family="fam-b")
    assert assess_key_compartment((first, second), now=NOW + 1, expected_profile_id=PROFILE, expected_scope_digest=SCOPE, requested_role=KeyRole.SERVICE_SIGNER, requested_public_key=SERVICE.public_key_bytes, minimum_sequence=1, previous_binding_digest=first.binding_digest).decision_kind is CompartmentDecisionKind.ACCEPT_COMPARTMENTED_KEY
    wrong_prev = binding(seq=1, prev=digest("wrong-prev"), family="fam-b")
    assert assess_key_compartment((first, wrong_prev), now=NOW + 1, expected_profile_id=PROFILE, expected_scope_digest=SCOPE, requested_role=KeyRole.SERVICE_SIGNER, requested_public_key=SERVICE.public_key_bytes, minimum_sequence=1, previous_binding_digest=first.binding_digest).decision_kind is CompartmentDecisionKind.QUARANTINE_PREVIOUS_LINK
    assert assess_key_compartment((first, second), now=NOW + 1, expected_profile_id=PROFILE, expected_scope_digest=SCOPE, requested_role=KeyRole.SERVICE_SIGNER, requested_public_key=SERVICE.public_key_bytes, minimum_sequence=2).decision_kind is CompartmentDecisionKind.QUARANTINE_ROLLBACK
    fork = binding(seq=1, prev=first.binding_digest, family="fam-c", signer=FAMILY_C)
    assert assess_key_compartment((first, second, fork), now=NOW + 1, expected_profile_id=PROFILE, expected_scope_digest=SCOPE, requested_role=KeyRole.SERVICE_SIGNER, requested_public_key=SERVICE.public_key_bytes, minimum_sequence=1).decision_kind is CompartmentDecisionKind.QUARANTINE_SEQUENCE_FORK


def component(component: AuthorityComponent, *, signer, actor, status=ComponentStatus.PASS_, family="fam-a", seq=0, profile=PROFILE, scope=SCOPE, obj=OBJECT, req=REQUEST):
    return make_authority_component_report(
        keypair=signer,
        component=component,
        status=status,
        profile_id=profile,
        scope_digest=scope,
        object_digest=obj,
        request_digest=req,
        actor_public_key=actor.public_key_bytes,
        evidence_digest=digest(component.value + status.value),
        sequence=seq,
        issued_at=NOW,
        expires_at=NOW + 100,
        family_id=family,
    )


REQUIRED = (AuthorityComponent.KEY_COMPARTMENT, AuthorityComponent.OPERATOR_KEY, AuthorityComponent.HARD_NEGATIVE_SCAN)


def good_components():
    return (
        component(AuthorityComponent.KEY_COMPARTMENT, signer=FAMILY_A, actor=SERVICE, family="fam-a"),
        component(AuthorityComponent.OPERATOR_KEY, signer=FAMILY_B, actor=OPERATOR, family="fam-b"),
        component(AuthorityComponent.HARD_NEGATIVE_SCAN, signer=FAMILY_C, actor=WITNESS, family="fam-c"),
    )


def test_authority_split_accepts_diverse_same_boundary_reports() -> None:
    report = assess_authority_split(good_components(), now=NOW + 1, expected_profile_id=PROFILE, expected_scope_digest=SCOPE, expected_object_digest=OBJECT, expected_request_digest=REQUEST, required_components=REQUIRED, min_family_diversity=3)
    assert report.decision_kind is AuthoritySplitDecisionKind.ACCEPT_AUTHORITY_SPLIT
    assert report.family_count == 3


def test_authority_split_rejects_missing_watch_failed_replay_and_drift() -> None:
    reports = good_components()
    assert assess_authority_split(reports[:-1], now=NOW + 1, expected_profile_id=PROFILE, expected_scope_digest=SCOPE, expected_object_digest=OBJECT, expected_request_digest=REQUEST, required_components=REQUIRED).decision_kind is AuthoritySplitDecisionKind.HOLD_MISSING_COMPONENT
    watch = (reports[0], component(AuthorityComponent.OPERATOR_KEY, signer=FAMILY_B, actor=OPERATOR, status=ComponentStatus.WATCH, family="fam-b"), reports[2])
    assert assess_authority_split(watch, now=NOW + 1, expected_profile_id=PROFILE, expected_scope_digest=SCOPE, expected_object_digest=OBJECT, expected_request_digest=REQUEST, required_components=REQUIRED).decision_kind is AuthoritySplitDecisionKind.HOLD_COMPONENT_WATCH
    assert assess_authority_split(watch, now=NOW + 1, expected_profile_id=PROFILE, expected_scope_digest=SCOPE, expected_object_digest=OBJECT, expected_request_digest=REQUEST, required_components=REQUIRED, allow_watch_components=True).decision_kind is AuthoritySplitDecisionKind.ACCEPT_WITH_WATCH
    failed = (reports[0], component(AuthorityComponent.OPERATOR_KEY, signer=FAMILY_B, actor=OPERATOR, status=ComponentStatus.FAIL, family="fam-b"), reports[2])
    assert assess_authority_split(failed, now=NOW + 1, expected_profile_id=PROFILE, expected_scope_digest=SCOPE, expected_object_digest=OBJECT, expected_request_digest=REQUEST, required_components=REQUIRED).decision_kind is AuthoritySplitDecisionKind.QUARANTINE_COMPONENT_FAILED
    assert assess_authority_split(reports, now=NOW + 1, expected_profile_id=PROFILE, expected_scope_digest=SCOPE, expected_object_digest=OBJECT, expected_request_digest=REQUEST, required_components=REQUIRED, previously_seen_report_digests=(reports[0].report_digest,)).decision_kind is AuthoritySplitDecisionKind.QUARANTINE_REPLAY
    drift = (reports[0], component(AuthorityComponent.OPERATOR_KEY, signer=FAMILY_B, actor=OPERATOR, req=digest("other-request"), family="fam-b"), reports[2])
    assert assess_authority_split(drift, now=NOW + 1, expected_profile_id=PROFILE, expected_scope_digest=SCOPE, expected_object_digest=OBJECT, expected_request_digest=REQUEST, required_components=REQUIRED).decision_kind is AuthoritySplitDecisionKind.QUARANTINE_REQUEST_DRIFT


def test_authority_split_rejects_actor_reuse_low_diversity_bad_signature_and_fork() -> None:
    reused = (
        component(AuthorityComponent.KEY_COMPARTMENT, signer=FAMILY_A, actor=SERVICE, family="fam-a"),
        component(AuthorityComponent.OPERATOR_KEY, signer=FAMILY_B, actor=SERVICE, family="fam-b"),
        component(AuthorityComponent.HARD_NEGATIVE_SCAN, signer=FAMILY_C, actor=WITNESS, family="fam-c"),
    )
    assert assess_authority_split(reused, now=NOW + 1, expected_profile_id=PROFILE, expected_scope_digest=SCOPE, expected_object_digest=OBJECT, expected_request_digest=REQUEST, required_components=REQUIRED).decision_kind is AuthoritySplitDecisionKind.QUARANTINE_ACTOR_KEY_REUSE
    mono = (
        component(AuthorityComponent.KEY_COMPARTMENT, signer=FAMILY_A, actor=SERVICE, family="one"),
        component(AuthorityComponent.OPERATOR_KEY, signer=FAMILY_B, actor=OPERATOR, family="one"),
        component(AuthorityComponent.HARD_NEGATIVE_SCAN, signer=FAMILY_C, actor=WITNESS, family="one"),
    )
    assert assess_authority_split(mono, now=NOW + 1, expected_profile_id=PROFILE, expected_scope_digest=SCOPE, expected_object_digest=OBJECT, expected_request_digest=REQUEST, required_components=REQUIRED).decision_kind is AuthoritySplitDecisionKind.HOLD_LOW_FAMILY_DIVERSITY
    bad = replace(good_components()[0], signature=b"1" * 64)
    assert assess_authority_split((bad,) + good_components()[1:], now=NOW + 1, expected_profile_id=PROFILE, expected_scope_digest=SCOPE, expected_object_digest=OBJECT, expected_request_digest=REQUEST, required_components=REQUIRED).decision_kind is AuthoritySplitDecisionKind.QUARANTINE_BAD_SIGNATURE
    fork_a = component(AuthorityComponent.OPERATOR_KEY, signer=FAMILY_B, actor=OPERATOR, family="fam-b", seq=4)
    fork_b = component(AuthorityComponent.OPERATOR_KEY, signer=FAMILY_D, actor=OPERATOR, family="fam-d", seq=4)
    assert assess_authority_split((good_components()[0], fork_a, fork_b, good_components()[2]), now=NOW + 1, expected_profile_id=PROFILE, expected_scope_digest=SCOPE, expected_object_digest=OBJECT, expected_request_digest=REQUEST, required_components=REQUIRED).decision_kind is AuthoritySplitDecisionKind.QUARANTINE_SEQUENCE_FORK


def test_compartmentfold_current_revision_path_passes() -> None:
    report = audit_compartment_fold(".", revision="rev0043")
    assert report.status == "pass"
    assert report.predecessor_status == "pass"
    assert report.foldmap_status == "pass"
    assert report.registry_status == "pass"
    assert report.surface_ledger_status == "pass"
