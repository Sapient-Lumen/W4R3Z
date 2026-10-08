from __future__ import annotations

from dataclasses import replace

from i2p_dht_lab.auditquorum import (
    AuditQuorumDecisionKind,
    ZERO_DIGEST as AQ_ZERO,
    assess_audit_quorum,
    make_checkpoint,
)
from i2p_dht_lab.bridgeauditfold import audit_bridge_audit_fold
from i2p_dht_lab.bridgeshadow import (
    BridgeShadowDecisionKind,
    BridgeShadowIntent,
    ShadowComponentReport,
    assess_bridge_shadow,
    make_bridge_shadow_capsule,
)
from i2p_dht_lab.identity import DhtKeypair
from i2p_dht_lab.ids import DOMAIN, sha256
from i2p_dht_lab.redressgc import (
    RedressEvidenceKind,
    RedressGcDecisionKind,
    RedressGcPolicy,
    assess_redress_gc,
    make_redress_evidence,
)

NOW = 1_910_000
PROFILE = "profile-alpha"
SERVICE = "public-bridge"
SCOPE = sha256(DOMAIN + b":rev0048:scope")
REQUEST = sha256(DOMAIN + b":rev0048:request")
SUBJECT = sha256(DOMAIN + b":rev0048:subject")
PUBLICATION = sha256(DOMAIN + b":rev0048:publication")
PAYLOAD = sha256(DOMAIN + b":rev0048:payload")


def d(label: str) -> bytes:
    return sha256(DOMAIN + b":rev0048-test:" + label.encode("utf-8"))


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
K9 = key(9)


def checkpoint(*, keypair=K1, log_id="log-a", seq=1, root=None, prev=AQ_ZERO, family="fam-a", path="path-a", publication=PUBLICATION, scope=SCOPE):
    return make_checkpoint(
        keypair=keypair,
        log_id=log_id,
        profile_id=PROFILE,
        service_name=SERVICE,
        scope_digest=scope,
        request_digest=REQUEST,
        publication_digest=publication,
        tree_size=seq * 10,
        root_digest=root or d(f"root-{log_id}-{seq}"),
        sequence=seq,
        previous_checkpoint_digest=prev,
        issued_at=NOW,
        expires_at=NOW + 100,
        family_id=family,
        path_family=path,
    )


def component(name: str, *, accept=True, watch=False, family="fam-a", path="path-a", digest=None, scope=SCOPE, request=REQUEST, reason="ok") -> ShadowComponentReport:
    return ShadowComponentReport(name, accept, watch, PROFILE, SERVICE, scope, request, digest or d(f"component-{name}-{family}-{path}"), family, path, reason)


def components(*, watch=False, bad_scope=False):
    scope = d("bad-scope") if bad_scope else SCOPE
    return (
        component("publication_guard", family="pub", path="pub-path", scope=scope),
        component("audit_quorum", watch=watch, family="audit", path="audit-path", scope=scope),
        component("publication_ledger", family="ledger", path="ledger-path", scope=scope),
        component("bridge_quench", family="quench", path="quench-path", scope=scope),
    )


def redress_record(kind: RedressEvidenceKind, *, keypair=K1, seq=1, family="red-a", path="path-a", scope=SCOPE, request=REQUEST, subject=SUBJECT, expires=None, pinned=False, evidence=None):
    return make_redress_evidence(
        keypair=keypair,
        kind=kind,
        profile_id=PROFILE,
        service_name=SERVICE,
        subject_digest=subject,
        scope_digest=scope,
        request_digest=request,
        evidence_digest=evidence or d(f"redress-{kind.value}-{seq}-{family}"),
        sequence=seq,
        previous_evidence_digest=AQ_ZERO,
        issued_at=NOW,
        expires_at=expires if expires is not None else NOW + 100,
        family_id=family,
        path_family=path,
        pinned=pinned,
    )


def test_audit_quorum_accepts_diverse_checkpoint_witnesses() -> None:
    checkpoints = (
        checkpoint(keypair=K1, log_id="log-a", seq=1, family="fam-a", path="path-a"),
        checkpoint(keypair=K2, log_id="log-b", seq=1, family="fam-b", path="path-b"),
    )
    report = assess_audit_quorum(
        checkpoints,
        now=NOW + 1,
        expected_profile_id=PROFILE,
        expected_service_name=SERVICE,
        expected_scope_digest=SCOPE,
        expected_request_digest=REQUEST,
        expected_publication_digest=PUBLICATION,
    )
    assert report.decision_kind is AuditQuorumDecisionKind.ACCEPT_QUORUM
    assert report.accept
    assert report.family_count == 2
    assert len(report.accepted_checkpoint_digests) == 2


def test_audit_quorum_catches_same_sequence_fork_replay_and_consistency_gap() -> None:
    a = checkpoint(keypair=K1, log_id="log-a", seq=2, prev=d("prev-a"), root=d("root-one"), family="fam-a", path="path-a")
    fork = checkpoint(keypair=K2, log_id="log-a", seq=2, prev=d("prev-a"), root=d("root-two"), family="fam-b", path="path-b")
    report = assess_audit_quorum((a, fork), now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_publication_digest=PUBLICATION)
    assert report.decision_kind is AuditQuorumDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK

    replay = assess_audit_quorum((a,), now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_publication_digest=PUBLICATION, previously_seen=(a.checkpoint_digest,))
    assert replay.decision_kind is AuditQuorumDecisionKind.QUARANTINE_REPLAY

    gap = checkpoint(keypair=K3, log_id="log-c", seq=3, prev=AQ_ZERO, family="fam-c", path="path-c")
    assert assess_audit_quorum((gap,), now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_publication_digest=PUBLICATION).decision_kind is AuditQuorumDecisionKind.HOLD_CONSISTENCY_GAP


def test_bridge_shadow_accepts_only_exact_bound_diverse_components() -> None:
    comps = components()
    capsule = make_bridge_shadow_capsule(
        keypair=K4,
        intent=BridgeShadowIntent.PUBLIC_REFRESH,
        profile_id=PROFILE,
        service_name=SERVICE,
        scope_digest=SCOPE,
        request_digest=REQUEST,
        publication_payload_digest=PAYLOAD,
        components=comps,
        sequence=1,
        issued_at=NOW,
        expires_at=NOW + 100,
        ttl_seconds=300,
        family_id="shadow-a",
        path_family="shadow-path-a",
    )
    report = assess_bridge_shadow((capsule,), comps, now=NOW + 1, expected_intent=BridgeShadowIntent.PUBLIC_REFRESH, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_publication_payload_digest=PAYLOAD)
    assert report.decision_kind is BridgeShadowDecisionKind.ACCEPT_SHADOW
    assert report.accept
    assert report.component_root_digest == capsule.component_root_digest

    watched = assess_bridge_shadow((capsule,), components(watch=True), now=NOW + 1, expected_intent=BridgeShadowIntent.PUBLIC_REFRESH, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_publication_payload_digest=PAYLOAD)
    assert watched.decision_kind is BridgeShadowDecisionKind.QUARANTINE_BINDING_DRIFT


def test_bridge_shadow_catches_missing_reject_scope_drift_replay_and_fork() -> None:
    comps = components()
    capsule = make_bridge_shadow_capsule(keypair=K4, intent=BridgeShadowIntent.PUBLIC_REFRESH, profile_id=PROFILE, service_name=SERVICE, scope_digest=SCOPE, request_digest=REQUEST, publication_payload_digest=PAYLOAD, components=comps, sequence=1, issued_at=NOW, expires_at=NOW + 100, ttl_seconds=300, family_id="shadow-a", path_family="shadow-path-a")
    assert assess_bridge_shadow((capsule,), comps[:-1], now=NOW + 1, expected_intent=BridgeShadowIntent.PUBLIC_REFRESH, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_publication_payload_digest=PAYLOAD).decision_kind is BridgeShadowDecisionKind.HOLD_MISSING_COMPONENT

    rejected = comps[:1] + (component("audit_quorum", accept=False, family="audit", path="audit-path", reason="fork"),) + comps[2:]
    assert assess_bridge_shadow((capsule,), rejected, now=NOW + 1, expected_intent=BridgeShadowIntent.PUBLIC_REFRESH, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_publication_payload_digest=PAYLOAD).decision_kind is BridgeShadowDecisionKind.QUARANTINE_COMPONENT_REJECT

    assert assess_bridge_shadow((capsule,), components(bad_scope=True), now=NOW + 1, expected_intent=BridgeShadowIntent.PUBLIC_REFRESH, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_publication_payload_digest=PAYLOAD).decision_kind is BridgeShadowDecisionKind.QUARANTINE_SCOPE_DRIFT

    assert assess_bridge_shadow((capsule,), comps, now=NOW + 1, expected_intent=BridgeShadowIntent.PUBLIC_REFRESH, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_publication_payload_digest=PAYLOAD, previously_seen=(capsule.shadow_digest,)).decision_kind is BridgeShadowDecisionKind.QUARANTINE_REPLAY

    fork = make_bridge_shadow_capsule(keypair=K5, intent=BridgeShadowIntent.PUBLIC_REFRESH, profile_id=PROFILE, service_name=SERVICE, scope_digest=SCOPE, request_digest=REQUEST, publication_payload_digest=d("other-payload"), components=comps, sequence=1, issued_at=NOW, expires_at=NOW + 100, ttl_seconds=300, family_id="shadow-b", path_family="shadow-path-b")
    assert assess_bridge_shadow((capsule, fork), comps, now=NOW + 1, expected_intent=BridgeShadowIntent.PUBLIC_REFRESH, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_publication_payload_digest=PAYLOAD).decision_kind is BridgeShadowDecisionKind.QUARANTINE_BINDING_DRIFT


def test_redress_gc_preserves_hard_negatives_and_compacts_soft_memory() -> None:
    hard = redress_record(RedressEvidenceKind.HARD_NEGATIVE, keypair=K1, seq=1, family="hard-a", path="hard-path")
    narrow_a = redress_record(RedressEvidenceKind.REDRESS_NARROW, keypair=K2, seq=2, family="red-a", path="red-path-a")
    narrow_b = redress_record(RedressEvidenceKind.REDRESS_NARROW, keypair=K3, seq=3, family="red-b", path="red-path-b")
    expired = redress_record(RedressEvidenceKind.SOFT_EXPIRED, keypair=K4, seq=4, family="soft-a", path="soft-path", expires=NOW - 1)
    soft_live = tuple(redress_record(RedressEvidenceKind.SOFT_EXPIRED, keypair=keypair, seq=seq, family=f"soft-{seq}", path=f"soft-path-{seq}") for seq, keypair in enumerate((K5, K6, K7, K8), start=5))
    report = assess_redress_gc((hard, narrow_a, narrow_b, expired) + soft_live, now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_subject_digest=SUBJECT, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, policy=RedressGcPolicy(max_soft_records=2, max_retained_bytes=100_000))
    assert report.decision_kind is RedressGcDecisionKind.ACCEPT_WITH_WATCH
    assert hard.record_digest in report.kept_digests
    assert expired.record_digest in report.dropped_digests
    assert report.redress_count == 2
    assert len(report.dropped_digests) >= 2


def test_redress_gc_catches_widening_low_diversity_scope_drift_and_fork() -> None:
    hard = redress_record(RedressEvidenceKind.HARD_NEGATIVE, keypair=K1, seq=1, family="hard-a", path="hard-path")
    lift_a = redress_record(RedressEvidenceKind.REDRESS_LIFT, keypair=K2, seq=2, family="red-a", path="red-path-a")
    lift_b = redress_record(RedressEvidenceKind.REDRESS_LIFT, keypair=K3, seq=3, family="red-b", path="red-path-b")
    widening = assess_redress_gc((hard, lift_a, lift_b), now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_subject_digest=SUBJECT, expected_scope_digest=SCOPE, expected_request_digest=REQUEST)
    assert widening.decision_kind is RedressGcDecisionKind.QUARANTINE_REDRESS_WIDENING

    low = assess_redress_gc((lift_a,), now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_subject_digest=SUBJECT, expected_scope_digest=SCOPE, expected_request_digest=REQUEST)
    assert low.decision_kind is RedressGcDecisionKind.HOLD_LOW_REDRESS_DIVERSITY

    drift = redress_record(RedressEvidenceKind.REDRESS_NARROW, keypair=K4, seq=4, family="red-c", path="red-path-c", scope=d("other-scope"))
    assert assess_redress_gc((drift,), now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_subject_digest=SUBJECT, expected_scope_digest=SCOPE, expected_request_digest=REQUEST).decision_kind is RedressGcDecisionKind.QUARANTINE_SCOPE_DRIFT

    fork_a = redress_record(RedressEvidenceKind.REDRESS_NARROW, keypair=K5, seq=9, family="fork-a", path="fork-path-a", evidence=d("fork-a"))
    fork_b = redress_record(RedressEvidenceKind.REDRESS_WATCH, keypair=K6, seq=9, family="fork-b", path="fork-path-b", evidence=d("fork-b"))
    assert assess_redress_gc((fork_a, fork_b), now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_subject_digest=SUBJECT, expected_scope_digest=SCOPE, expected_request_digest=REQUEST).decision_kind is RedressGcDecisionKind.QUARANTINE_SEQUENCE_FORK


def test_bridgeauditfold_pins_current_revision_surface() -> None:
    report = audit_bridge_audit_fold(".", revision="rev0048", artifact_stem="Nicotine-i2pDHT-rev0048-2026.06.06.02.45-bridgeshadow-auditquorum-redressgc")
    assert report.status == "pass"
    assert report.predecessor_status == "pass"
    assert report.registry_status == "pass"
