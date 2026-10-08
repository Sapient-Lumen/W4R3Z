from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from i2p_dht_lab.auditquorum import (
    AuditQuorumDecisionKind,
    AuditReceiptKind,
    assess_audit_quorum,
    make_audit_receipt,
)
from i2p_dht_lab.shadowauditfold import audit_shadow_audit_fold
from i2p_dht_lab.bridgeshadow import (
    BridgeShadowAction,
    BridgeShadowDecisionKind,
    assess_bridge_shadow,
    make_bridge_shadow_step,
)
from i2p_dht_lab.identity import DhtKeypair
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.moderationquarantine import ZERO_DIGEST
from i2p_dht_lab.publicationguard import PublicationIntent
from i2p_dht_lab.redressgc import (
    RedressGcDecisionKind,
    RedressGcItem,
    RedressGcItemKind,
    RedressGcPolicy,
    assess_redress_gc,
)

NOW = 1_956_606
PROFILE = "profile-alpha"
SERVICE = "public-bridge"
SCOPE = sha256(b"scope-alpha")
REQUEST = sha256(b"request-alpha")
SUBJECT = sha256(b"subject-alpha")
PAYLOAD = sha256(b"public-bridge-payload-alpha")
K1 = DhtKeypair.from_seed(b"A" * 32)
K2 = DhtKeypair.from_seed(b"B" * 32)
K3 = DhtKeypair.from_seed(b"C" * 32)
K4 = DhtKeypair.from_seed(b"D" * 32)
K5 = DhtKeypair.from_seed(b"E" * 32)


def d(label: str) -> bytes:
    return sha256(label.encode())


def component(label: str, *, accept: bool = True, watch: bool = False, quarantined: bool = False, quench: bool = False, continue_publication: bool = True):
    return SimpleNamespace(
        report_digest=d(f"{label}-{accept}-{watch}-{quarantined}-{quench}-{continue_publication}"),
        accept=accept,
        watch=watch,
        quarantined=quarantined,
        quench=quench,
        continue_publication=continue_publication,
        intent=PublicationIntent.PUBLIC_REFRESH,
    )


def step(keypair, seq: int, fam: str, path: str, publication, ledger, quench, *, scope=SCOPE, request=REQUEST, payload=PAYLOAD, effect=None, previous=ZERO_DIGEST):
    return make_bridge_shadow_step(
        keypair=keypair,
        action=BridgeShadowAction.SHADOW_REFRESH,
        profile_id=PROFILE,
        service_name=SERVICE,
        scope_digest=scope,
        request_digest=request,
        publication_report_digest=publication.report_digest,
        publication_ledger_digest=ledger.report_digest,
        quench_report_digest=quench.report_digest,
        payload_digest=payload,
        shadow_effect_digest=effect or d(f"shadow-effect-{seq}-{fam}-{path}"),
        sequence=seq,
        previous_shadow_digest=previous,
        issued_at=NOW,
        expires_at=NOW + 100,
        family_id=fam,
        path_family=path,
    )


def accepted_shadow():
    publication = component("publication")
    ledger = component("ledger")
    quench = component("quench")
    steps = (
        step(K1, 1, "fam-a", "path-a", publication, ledger, quench),
        step(K2, 2, "fam-b", "path-b", publication, ledger, quench),
    )
    return assess_bridge_shadow(
        steps,
        publication=publication,
        publication_ledger=ledger,
        quench=quench,
        now=NOW + 1,
        expected_profile_id=PROFILE,
        expected_service_name=SERVICE,
        expected_scope_digest=SCOPE,
        expected_request_digest=REQUEST,
        expected_payload_digest=PAYLOAD,
    )


def test_bridge_shadow_dryrun_rejects_risky_public_side_effects() -> None:
    publication = component("publication")
    ledger = component("ledger")
    quench = component("quench")
    steps = (
        step(K1, 1, "fam-a", "path-a", publication, ledger, quench),
        step(K2, 2, "fam-b", "path-b", publication, ledger, quench),
    )
    ok = assess_bridge_shadow(steps, publication=publication, publication_ledger=ledger, quench=quench, now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_payload_digest=PAYLOAD)
    assert ok.decision_kind is BridgeShadowDecisionKind.ACCEPT_SHADOW
    assert ok.family_count == 2
    assert ok.path_family_count == 2

    quenching = component("quench", continue_publication=False, quench=True)
    held = assess_bridge_shadow((step(K1, 1, "fam-a", "path-a", publication, ledger, quenching),), publication=publication, publication_ledger=ledger, quench=quenching, now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_payload_digest=PAYLOAD)
    assert held.decision_kind is BridgeShadowDecisionKind.HOLD_QUENCH

    drift = step(K1, 1, "fam-a", "path-a", publication, ledger, quench, scope=d("other-scope"))
    assert assess_bridge_shadow((drift,), publication=publication, publication_ledger=ledger, quench=quench, now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_payload_digest=PAYLOAD).decision_kind is BridgeShadowDecisionKind.QUARANTINE_SCOPE_DRIFT

    fork_a = step(K1, 5, "fam-a", "path-a", publication, ledger, quench, effect=d("fork-a"))
    fork_b = step(K2, 5, "fam-b", "path-b", publication, ledger, quench, effect=d("fork-b"))
    assert assess_bridge_shadow((fork_a, fork_b), publication=publication, publication_ledger=ledger, quench=quench, now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_payload_digest=PAYLOAD).decision_kind is BridgeShadowDecisionKind.QUARANTINE_SEQUENCE_FORK


def receipt(kind: AuditReceiptKind, keypair, fam: str, path: str, shadow, *, payload=PAYLOAD, accepted: bool = True, watch: bool = False):
    return make_audit_receipt(
        keypair=keypair,
        kind=kind,
        profile_id=PROFILE,
        service_name=SERVICE,
        scope_digest=SCOPE,
        request_digest=REQUEST,
        bridge_shadow_digest=shadow.report_digest,
        public_payload_digest=payload,
        observation_digest=d(f"audit-{kind.value}-{fam}-{path}-{accepted}-{watch}"),
        issued_at=NOW,
        expires_at=NOW + 100,
        family_id=fam,
        path_family=path,
        accepted=accepted,
        watch=watch,
    )


def test_audit_quorum_is_local_evidence_not_truth() -> None:
    shadow = accepted_shadow()
    statements = (
        receipt(AuditReceiptKind.PUBLICATION_OBSERVED, K3, "audit-a", "path-a", shadow),
        receipt(AuditReceiptKind.REPAIR_OBSERVED, K4, "audit-b", "path-b", shadow),
    )
    ok = assess_audit_quorum(statements, bridge_shadow=shadow, now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_public_payload_digest=PAYLOAD)
    assert ok.decision_kind is AuditQuorumDecisionKind.ACCEPT_AUDITED

    mono = (
        receipt(AuditReceiptKind.PUBLICATION_OBSERVED, K3, "same", "path-a", shadow),
        receipt(AuditReceiptKind.REPAIR_OBSERVED, K4, "same", "path-b", shadow),
    )
    assert assess_audit_quorum(mono, bridge_shadow=shadow, now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_public_payload_digest=PAYLOAD).decision_kind is AuditQuorumDecisionKind.HOLD_LOW_FAMILY_DIVERSITY

    stale = (statements[0], receipt(AuditReceiptKind.STALE_PUBLIC_RECORD, K4, "audit-b", "path-b", shadow))
    assert assess_audit_quorum(stale, bridge_shadow=shadow, now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_public_payload_digest=PAYLOAD).decision_kind is AuditQuorumDecisionKind.QUARANTINE_STALE_PUBLIC_RECORD

    mismatch = (statements[0], receipt(AuditReceiptKind.PAYLOAD_MISMATCH, K4, "audit-b", "path-b", shadow, payload=d("wrong-public-payload")))
    assert assess_audit_quorum(mismatch, bridge_shadow=shadow, now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_public_payload_digest=PAYLOAD).decision_kind is AuditQuorumDecisionKind.QUARANTINE_PAYLOAD_MISMATCH


def gc_item(kind: RedressGcItemKind, seq: int, fam: str, *, subject=SUBJECT, evidence=None, scope=SCOPE, request=REQUEST, expires=NOW + 100, byte_cost=10, pinned=False) -> RedressGcItem:
    return RedressGcItem(
        kind=kind,
        scope_digest=scope,
        request_digest=request,
        subject_digest=subject,
        evidence_digest=evidence or d(f"gc-{kind.value}-{seq}-{fam}"),
        sequence=seq,
        issued_at=NOW,
        expires_at=expires,
        family_id=fam,
        byte_cost=byte_cost,
        pinned=pinned,
    )


def test_redress_gc_preserves_hard_negatives_and_redress_memory() -> None:
    hard = gc_item(RedressGcItemKind.HARD_NEGATIVE, 1, "hard", byte_cost=20)
    redress = gc_item(RedressGcItemKind.REDRESS_LIFT, 2, "redress", byte_cost=20)
    expired_soft = gc_item(RedressGcItemKind.SOFT_EXPIRED, 3, "old", expires=NOW + 1, byte_cost=20)
    result = assess_redress_gc((hard, redress, expired_soft), now=NOW + 2, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, live_hard_negative_digests=(hard.item_digest,), active_redress_digests=(redress.item_digest,), policy=RedressGcPolicy(max_retained_bytes=80))
    assert result.decision_kind is RedressGcDecisionKind.ACCEPT_WITH_WATCH
    assert hard.item_digest in result.retained_digests
    assert redress.item_digest in result.retained_digests
    assert expired_soft.item_digest in result.dropped_digests

    expired_hard = gc_item(RedressGcItemKind.HARD_NEGATIVE, 4, "expired-hard", expires=NOW + 1)
    assert assess_redress_gc((expired_hard,), now=NOW + 2, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, live_hard_negative_digests=(expired_hard.item_digest,)).decision_kind is RedressGcDecisionKind.QUARANTINE_LIVE_HARD_NEGATIVE_DROP

    fork_a = gc_item(RedressGcItemKind.REDRESS_WATCH, 9, "fork-a", evidence=d("fork-a"))
    fork_b = gc_item(RedressGcItemKind.REDRESS_WATCH, 9, "fork-b", evidence=d("fork-b"))
    assert assess_redress_gc((fork_a, fork_b), now=NOW + 1, expected_scope_digest=SCOPE, expected_request_digest=REQUEST).decision_kind is RedressGcDecisionKind.QUARANTINE_SAME_SEQUENCE_CONFLICT

    oversized_hard = gc_item(RedressGcItemKind.HARD_NEGATIVE, 10, "too-big", byte_cost=100)
    assert assess_redress_gc((oversized_hard,), now=NOW + 1, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, live_hard_negative_digests=(oversized_hard.item_digest,), policy=RedressGcPolicy(max_retained_bytes=16)).decision_kind is RedressGcDecisionKind.HOLD_MEMORY_BUDGET


def test_shadow_audit_fold_current_path_visible() -> None:
    root = Path(__file__).resolve().parents[1]
    fold = audit_shadow_audit_fold(root, revision="rev0048", artifact_stem="Nicotine-i2pDHT-rev0048-2026.06.06.02.45-bridgeshadow-auditquorum-redressgc")
    assert fold.status == "pass"
    assert fold.error_count == 0
