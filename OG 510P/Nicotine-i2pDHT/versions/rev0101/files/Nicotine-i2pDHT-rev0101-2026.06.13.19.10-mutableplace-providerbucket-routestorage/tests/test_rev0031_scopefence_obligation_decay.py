from __future__ import annotations

from dataclasses import replace

from i2p_dht_lab.auditmesh import audit_audit_mesh
from i2p_dht_lab.decaymesh import DecayMeshDecisionKind, DecayMeshPolicy, assess_decay_mesh
from i2p_dht_lab.evidencegc import EvidenceItem, EvidenceKind
from i2p_dht_lab.identity import DhtKeypair
from i2p_dht_lab.ids import key_id, sha256
from i2p_dht_lab.obligationdebt import (
    ObligationDebtDecisionKind,
    ObligationKind,
    ObligationPolicy,
    ProofEvidence,
    ProofObligation,
    assess_obligation_debt,
)
from i2p_dht_lab.scopefence import (
    ScopeFenceDecisionKind,
    ScopeFencePolicy,
    ScopePurpose,
    ScopedClaim,
    assess_scope_fence,
)


def seed(label: str) -> bytes:
    return sha256(("rev0031-seed:" + label).encode("utf-8"))


def kp(label: str) -> DhtKeypair:
    return DhtKeypair.from_seed(seed(label))


def digest(label: str) -> bytes:
    return key_id("rev0031", label)


def claim(label: str, *, scope: bytes, obj: bytes, request: bytes, purpose: ScopePurpose, family: str, path: str, seq: int, now: int, ttl: int = 300, note: str = "") -> ScopedClaim:
    return ScopedClaim.create(
        keypair=kp("claim-" + label),
        scope_id=scope,
        object_digest=obj,
        request_id=request,
        purpose=purpose,
        source_family=family,
        path_family=path,
        sequence=seq,
        issued_at=now,
        ttl=ttl,
        note=note,
    )


def obligation(label: str, *, kind: ObligationKind, scope: bytes, obj: bytes, subject: bytes, seq: int, now: int, due_delta: int = 300) -> ProofObligation:
    return ProofObligation.create(
        keypair=kp("obligation-" + label),
        kind=kind,
        scope_id=scope,
        object_digest=obj,
        subject_digest=subject,
        sequence=seq,
        issued_at=now,
        due_at=now + due_delta,
        note=label,
    )


def proof(label: str, *, kind: ObligationKind, scope: bytes, obj: bytes, subject: bytes, family: str, path: str, seq: int, now: int, ttl: int = 300) -> ProofEvidence:
    return ProofEvidence.create(
        keypair=kp("proof-" + label),
        kind=kind,
        scope_id=scope,
        object_digest=obj,
        subject_digest=subject,
        source_family=family,
        path_family=path,
        sequence=seq,
        issued_at=now,
        ttl=ttl,
        verdict_digest=digest("verdict-" + label),
        note=label,
    )


def item(kind: EvidenceKind, label: str, *, scope: bytes, obj: bytes, fam: str, path: str, now: int, seq: int, expires_delta: int, byte_cost: int = 128) -> EvidenceItem:
    return EvidenceItem(
        kind=kind,
        scope_id=scope,
        object_digest=obj,
        source_family=fam,
        path_family=path,
        issued_at=now,
        expires_at=now + expires_delta,
        byte_cost=byte_cost,
        sequence=seq,
        witness_id=digest("witness-" + label),
        note=label,
    )


def test_scope_fence_accepts_exact_boundary_with_diversity() -> None:
    now = 1_766_400_000
    scope = digest("scope-a")
    obj = digest("object-a")
    request = digest("request-a")
    claims = (
        claim("a", scope=scope, obj=obj, request=request, purpose=ScopePurpose.PROVIDER_PROBE, family="fam-A", path="path-1", seq=1, now=now),
        claim("b", scope=scope, obj=obj, request=request, purpose=ScopePurpose.PROVIDER_PROBE, family="fam-B", path="path-2", seq=1, now=now),
    )
    report = assess_scope_fence(claims, expected_scope_id=scope, expected_object_digest=obj, expected_request_id=request, expected_purpose=ScopePurpose.PROVIDER_PROBE, now=now + 1)
    assert report.decision_kind is ScopeFenceDecisionKind.ACCEPT_BOUND_SCOPE
    assert report.accept
    assert report.source_families == ("fam-A", "fam-B")
    assert report.path_families == ("path-1", "path-2")


def test_scope_fence_rejects_cross_scope_object_request_and_purpose_laundering() -> None:
    now = 1_766_400_100
    scope = digest("scope-b")
    obj = digest("object-b")
    request = digest("request-b")
    base_kwargs = dict(scope=scope, obj=obj, request=request, purpose=ScopePurpose.MUTABLE_HEAD, family="fam-A", path="path-1", seq=1, now=now)

    wrong_scope = assess_scope_fence((claim("scope-mis", **{**base_kwargs, "scope": digest("other-scope")}),), expected_scope_id=scope, expected_object_digest=obj, expected_request_id=request, expected_purpose=ScopePurpose.MUTABLE_HEAD, now=now + 1)
    assert wrong_scope.decision_kind is ScopeFenceDecisionKind.QUARANTINE_SCOPE_MISMATCH

    wrong_object = assess_scope_fence((claim("object-mis", **{**base_kwargs, "obj": digest("other-object")}),), expected_scope_id=scope, expected_object_digest=obj, expected_request_id=request, expected_purpose=ScopePurpose.MUTABLE_HEAD, now=now + 1)
    assert wrong_object.decision_kind is ScopeFenceDecisionKind.QUARANTINE_OBJECT_MISMATCH

    wrong_request = assess_scope_fence((claim("request-mis", **{**base_kwargs, "request": digest("other-request")}),), expected_scope_id=scope, expected_object_digest=obj, expected_request_id=request, expected_purpose=ScopePurpose.MUTABLE_HEAD, now=now + 1)
    assert wrong_request.decision_kind is ScopeFenceDecisionKind.QUARANTINE_REQUEST_MISMATCH

    wrong_purpose = assess_scope_fence((claim("purpose-mis", **{**base_kwargs, "purpose": ScopePurpose.ROUTE_REPAIR}),), expected_scope_id=scope, expected_object_digest=obj, expected_request_id=request, expected_purpose=ScopePurpose.MUTABLE_HEAD, now=now + 1)
    assert wrong_purpose.decision_kind is ScopeFenceDecisionKind.QUARANTINE_PURPOSE_MIX


def test_scope_fence_catches_signature_expiry_family_flood_and_same_sequence_fork() -> None:
    now = 1_766_400_200
    scope = digest("scope-c")
    obj = digest("object-c")
    request = digest("request-c")
    good = claim("good", scope=scope, obj=obj, request=request, purpose=ScopePurpose.WITNESS, family="fam-A", path="path-1", seq=1, now=now)
    bad_sig = replace(good, signature=b"x" * 64)
    bad_report = assess_scope_fence((bad_sig,), expected_scope_id=scope, expected_object_digest=obj, expected_request_id=request, expected_purpose=ScopePurpose.WITNESS, now=now + 1)
    assert bad_report.decision_kind is ScopeFenceDecisionKind.QUARANTINE_BAD_SIGNATURE

    expired = claim("expired", scope=scope, obj=obj, request=request, purpose=ScopePurpose.WITNESS, family="fam-B", path="path-2", seq=1, now=now - 20, ttl=5)
    expired_report = assess_scope_fence((expired,), expected_scope_id=scope, expected_object_digest=obj, expected_request_id=request, expected_purpose=ScopePurpose.WITNESS, now=now)
    assert expired_report.decision_kind is ScopeFenceDecisionKind.QUARANTINE_EXPIRED

    flood = tuple(claim(f"flood-{idx}", scope=scope, obj=obj, request=request, purpose=ScopePurpose.WITNESS, family="fam-Z", path=f"path-{idx}", seq=idx, now=now) for idx in range(3))
    flood_report = assess_scope_fence(flood, expected_scope_id=scope, expected_object_digest=obj, expected_request_id=request, expected_purpose=ScopePurpose.WITNESS, now=now + 1, policy=ScopeFencePolicy(max_per_source_family=2))
    assert flood_report.decision_kind is ScopeFenceDecisionKind.QUARANTINE_SOURCE_FAMILY_FLOOD

    shared_key = kp("forked-claim")
    first = ScopedClaim.create(keypair=shared_key, scope_id=scope, object_digest=obj, request_id=request, purpose=ScopePurpose.WITNESS, source_family="fam-A", path_family="path-1", sequence=7, issued_at=now, ttl=300, note="first")
    second = ScopedClaim.create(keypair=shared_key, scope_id=scope, object_digest=obj, request_id=request, purpose=ScopePurpose.WITNESS, source_family="fam-B", path_family="path-2", sequence=7, issued_at=now, ttl=300, note="fork")
    fork_report = assess_scope_fence((first, second), expected_scope_id=scope, expected_object_digest=obj, expected_request_id=request, expected_purpose=ScopePurpose.WITNESS, now=now + 1)
    assert fork_report.decision_kind is ScopeFenceDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK


def test_obligation_debt_clears_only_with_live_diverse_matching_proofs() -> None:
    now = 1_766_401_000
    scope = digest("ob-scope-a")
    obj = digest("ob-object-a")
    subject = digest("ob-subject-a")
    ob = obligation("provider", kind=ObligationKind.PROVIDER_SEMANTIC_PROOF, scope=scope, obj=obj, subject=subject, seq=1, now=now)
    proofs = (
        proof("a", kind=ob.kind, scope=scope, obj=obj, subject=subject, family="fam-A", path="path-1", seq=1, now=now),
        proof("b", kind=ob.kind, scope=scope, obj=obj, subject=subject, family="fam-B", path="path-2", seq=1, now=now),
    )
    report = assess_obligation_debt((ob,), proofs, now=now + 1)
    assert report.decision_kind is ObligationDebtDecisionKind.ACCEPT_OBLIGATIONS_CLEARED
    assert report.accept
    assert report.fulfilled_obligation_digests == (ob.digest,)


def test_obligation_debt_holds_before_due_and_quarantines_after_due() -> None:
    now = 1_766_401_100
    scope = digest("ob-scope-b")
    obj = digest("ob-object-b")
    subject = digest("ob-subject-b")
    ob = obligation("witness", kind=ObligationKind.MUTABLE_HEAD_WITNESS, scope=scope, obj=obj, subject=subject, seq=1, now=now, due_delta=100)
    hold = assess_obligation_debt((ob,), (), now=now + 10)
    assert hold.decision_kind is ObligationDebtDecisionKind.HOLD_MISSING_PROOF
    overdue = assess_obligation_debt((ob,), (), now=now + 101)
    assert overdue.decision_kind is ObligationDebtDecisionKind.QUARANTINE_OVERDUE_DEBT


def test_obligation_debt_low_diversity_and_evidence_fork_pressure() -> None:
    now = 1_766_401_200
    scope = digest("ob-scope-c")
    obj = digest("ob-object-c")
    subject = digest("ob-subject-c")
    ob = obligation("route", kind=ObligationKind.ROUTE_LIVENESS, scope=scope, obj=obj, subject=subject, seq=1, now=now)
    low = (
        proof("low-a", kind=ob.kind, scope=scope, obj=obj, subject=subject, family="fam-A", path="path-1", seq=1, now=now),
        proof("low-b", kind=ob.kind, scope=scope, obj=obj, subject=subject, family="fam-A", path="path-2", seq=2, now=now),
    )
    low_report = assess_obligation_debt((ob,), low, now=now + 1, policy=ObligationPolicy(min_source_families=2, min_path_families=2))
    assert low_report.decision_kind is ObligationDebtDecisionKind.HOLD_LOW_DIVERSITY

    shared = kp("proof-fork")
    first = ProofEvidence.create(keypair=shared, kind=ob.kind, scope_id=scope, object_digest=obj, subject_digest=subject, source_family="fam-A", path_family="path-1", sequence=4, issued_at=now, ttl=300, verdict_digest=digest("v1"))
    second = ProofEvidence.create(keypair=shared, kind=ob.kind, scope_id=scope, object_digest=obj, subject_digest=subject, source_family="fam-B", path_family="path-2", sequence=4, issued_at=now, ttl=300, verdict_digest=digest("v2"))
    fork_report = assess_obligation_debt((ob,), (first, second), now=now + 1)
    assert fork_report.decision_kind is ObligationDebtDecisionKind.QUARANTINE_EVIDENCE_FORK


def test_obligation_debt_rejects_bad_signatures_and_mismatched_scope_as_missing_proof() -> None:
    now = 1_766_401_300
    scope = digest("ob-scope-d")
    obj = digest("ob-object-d")
    subject = digest("ob-subject-d")
    ob = obligation("custody", kind=ObligationKind.CUSTODY_CHALLENGE, scope=scope, obj=obj, subject=subject, seq=1, now=now)
    bad_ob = replace(ob, signature=b"z" * 64)
    bad_report = assess_obligation_debt((bad_ob,), (), now=now + 1)
    assert bad_report.decision_kind is ObligationDebtDecisionKind.QUARANTINE_BAD_SIGNATURE

    wrong_scope_proofs = (
        proof("wrong-a", kind=ob.kind, scope=digest("wrong-scope"), obj=obj, subject=subject, family="fam-A", path="path-1", seq=1, now=now),
        proof("wrong-b", kind=ob.kind, scope=digest("wrong-scope"), obj=obj, subject=subject, family="fam-B", path="path-2", seq=1, now=now),
    )
    report = assess_obligation_debt((ob,), wrong_scope_proofs, now=now + 1)
    assert report.decision_kind is ObligationDebtDecisionKind.HOLD_MISSING_PROOF


def test_decay_mesh_keeps_hard_negative_and_fresh_diverse_soft_evidence() -> None:
    now = 1_766_402_000
    scope = digest("decay-scope-a")
    obj = digest("decay-object-a")
    hard = item(EvidenceKind.TOMBSTONE, "hard", scope=scope, obj=obj, fam="fam-A", path="path-1", now=now - 10_000, seq=5, expires_delta=10)
    soft_a = item(EvidenceKind.PROVIDER_TRUE, "soft-a", scope=scope, obj=obj, fam="fam-A", path="path-1", now=now, seq=6, expires_delta=60)
    soft_b = item(EvidenceKind.PROVIDER_TRUE, "soft-b", scope=scope, obj=obj, fam="fam-B", path="path-2", now=now, seq=7, expires_delta=60)
    report = assess_decay_mesh((hard, soft_a, soft_b), now=now + 30)
    kept_kinds = {decision.kind for decision in report.decisions if decision.keep}
    assert DecayMeshDecisionKind.KEEP_HARD_NEGATIVE in kept_kinds
    assert DecayMeshDecisionKind.KEEP_FRESH_DIVERSE in kept_kinds
    assert hard in report.kept
    assert soft_a in report.kept and soft_b in report.kept


def test_decay_mesh_drops_old_soft_and_quarantines_same_family_replay() -> None:
    now = 1_766_402_100
    scope = digest("decay-scope-b")
    obj = digest("decay-object-b")
    old_soft = item(EvidenceKind.PROVIDER_TRUE, "old-soft", scope=scope, obj=obj, fam="fam-A", path="path-1", now=now - 1000, seq=1, expires_delta=5)
    replay = tuple(item(EvidenceKind.PROVIDER_TRUE, f"replay-{idx}", scope=scope, obj=obj, fam="fam-Z", path=f"path-{idx}", now=now, seq=idx + 2, expires_delta=60) for idx in range(4))
    report = assess_decay_mesh((old_soft,) + replay, now=now + 1, policy=DecayMeshPolicy(max_refreshes_per_family=2, min_refresh_families=1))
    assert any(decision.kind is DecayMeshDecisionKind.DROP_EXPIRED_SOFT and decision.item is old_soft for decision in report.decisions)
    assert any(decision.kind is DecayMeshDecisionKind.QUARANTINE_REPLAY_MONOCULTURE for decision in report.decisions)
    assert report.quarantine_count >= 1


def test_decay_mesh_conflicting_same_sequence_does_not_become_convenient_memory() -> None:
    now = 1_766_402_200
    scope = digest("decay-scope-c")
    first = item(EvidenceKind.MUTABLE_LATEST, "first", scope=scope, obj=digest("head-1"), fam="fam-A", path="path-1", now=now, seq=10, expires_delta=60)
    second = item(EvidenceKind.MUTABLE_LATEST, "second", scope=scope, obj=digest("head-2"), fam="fam-B", path="path-2", now=now, seq=10, expires_delta=60)
    report = assess_decay_mesh((first, second), now=now + 1, policy=DecayMeshPolicy(min_refresh_families=1))
    assert any(decision.kind is DecayMeshDecisionKind.QUARANTINE_CONFLICTING_SEQUENCE for decision in report.decisions)


def test_auditmesh_current_path_and_predecessor_fold_passes() -> None:
    root = __import__("pathlib").Path(__file__).resolve().parents[1]
    report = audit_audit_mesh(root, revision="rev0031", artifact_stem=root.name)
    assert report.status == "pass"
    assert report.predecessor_status.endswith(":pass")
    assert report.error_count == 0
