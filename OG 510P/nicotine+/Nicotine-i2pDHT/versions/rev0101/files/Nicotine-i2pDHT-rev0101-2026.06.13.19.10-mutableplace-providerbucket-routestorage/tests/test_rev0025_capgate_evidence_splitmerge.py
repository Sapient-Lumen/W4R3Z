from __future__ import annotations

from dataclasses import replace

from i2p_dht_lab.admissionwall import AdmissionBudget, AdmissionState
from i2p_dht_lab.capability import CapabilityGrant, CapabilityKind, CapabilityRevocation, RevocationSet
from i2p_dht_lab.capgate import CapabilityDispatchDecisionKind, CapabilityDispatchPolicy, evaluate_capability_dispatch
from i2p_dht_lab.evidencegc import EvidenceGcDecisionKind, EvidenceGcPolicy, EvidenceItem, EvidenceKind, collect_evidence_gc
from i2p_dht_lab.epochgate import EpochHead, EpochMemory, EpochPurpose
from i2p_dht_lab.identity import DhtKeypair, NodeIdentity
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.namespaceregistry import NamespacePolicy, NamespaceRegistry, memory_from_policies
from i2p_dht_lab.riskfold import audit_risk_fold
from i2p_dht_lab.splitmerge import PartitionObservation, SplitMergeDecisionKind, merge_partition_observations
from i2p_dht_lab.validatorwall import PayloadEnvelope, PayloadRole
from i2p_dht_lab.wirecanon import WireFrame, WireMessageKind


def kp(n: int) -> DhtKeypair:
    return DhtKeypair.from_seed(bytes([n]) * 32)


def ident(n: int) -> NodeIdentity:
    return NodeIdentity.create(destination=f"rev0025-node-{n}.b32.i2p", keypair=kp(n))


def digest(label: str) -> bytes:
    return sha256(label.encode("utf-8"))


def namespace_policy(now: int, authority: DhtKeypair, *, namespace: str = "i2p-dht-control") -> NamespacePolicy:
    return NamespacePolicy.create(
        authority=authority,
        namespace=namespace,
        sequence=1,
        issued_at=now - 10,
        ttl=1000,
        allowed_roles_by_kind={WireMessageKind.EPOCH_HEAD: frozenset({PayloadRole.MUTABLE_HEAD})},
        max_body_bytes=4096,
        max_ttl_seconds=600,
        required_flags_by_role={PayloadRole.MUTABLE_HEAD: frozenset({"mutable-head"})},
    )


def frame_payload_body(now: int, actor: NodeIdentity, actor_kp: DhtKeypair, *, namespace: str = "i2p-dht-control", scope: bytes | None = None):
    body = b"rev0025 mutable head body"
    scope_id = scope or digest("rev0025-scope")
    envelope = PayloadEnvelope.create(namespace=namespace, role=PayloadRole.MUTABLE_HEAD, scope_id=scope_id, body=body, issued_at=now, ttl=300)
    payload = envelope.to_bytes()
    frame = WireFrame.create(
        keypair=actor_kp,
        sender_node_id=actor.node_id,
        message_kind=WireMessageKind.EPOCH_HEAD,
        request_id=digest("rev0025-request"),
        payload=payload,
        issued_at=now,
        ttl=300,
        flags=("mutable-head",),
    )
    return frame, payload, body, scope_id


def test_capability_dispatch_requires_namespace_capability_and_admission() -> None:
    now = 1_765_308_000
    actor = ident(10)
    registry_authority = kp(90)
    cap_authority = kp(91)
    policy = namespace_policy(now, registry_authority)
    registry = NamespaceRegistry((policy,), memory=memory_from_policies((policy,)))
    frame, payload, body, scope_id = frame_payload_body(now, actor, kp(10))
    grant = CapabilityGrant.create(
        issuer_keypair=cap_authority,
        subject_public_key=actor.public_key,
        capability=CapabilityKind.WRITE_HEAD,
        resource=scope_id,
        not_before=now - 5,
        ttl=600,
        sequence=1,
    )
    report = evaluate_capability_dispatch(
        registry=registry,
        frame=frame,
        payload=payload,
        body=body,
        grants=(grant,),
        revocations=RevocationSet(()),
        dispatch_policy=CapabilityDispatchPolicy({"i2p-dht-control": cap_authority.public_key_bytes}),
        admission_budget=AdmissionBudget(allowed_namespaces=frozenset({"i2p-dht-control"}), max_streams=3, max_bytes=4096, max_metadata=10),
        garden_keypair=kp(99),
        garden_node_id=ident(99).node_id,
        source_family="fam-A",
        now=now + 1,
        expected_scope_id=scope_id,
    )
    assert report.decision.kind is CapabilityDispatchDecisionKind.ACCEPT_DISPATCH
    assert report.capability_check is not None and report.capability_check.valid
    assert report.admission_decision is not None and report.admission_decision.accepted


def test_capability_dispatch_rejects_revoked_grant_before_admission() -> None:
    now = 1_765_308_000
    actor = ident(11)
    registry_authority = kp(90)
    cap_authority = kp(91)
    policy = namespace_policy(now, registry_authority)
    registry = NamespaceRegistry((policy,), memory=memory_from_policies((policy,)))
    frame, payload, body, scope_id = frame_payload_body(now, actor, kp(11))
    grant = CapabilityGrant.create(
        issuer_keypair=cap_authority,
        subject_public_key=actor.public_key,
        capability=CapabilityKind.WRITE_HEAD,
        resource=scope_id,
        not_before=now - 5,
        ttl=600,
        sequence=1,
    )
    revocation = CapabilityRevocation.create(issuer_keypair=cap_authority, grant_hash=grant.grant_hash, issued_at=now)
    report = evaluate_capability_dispatch(
        registry=registry,
        frame=frame,
        payload=payload,
        body=body,
        grants=(grant,),
        revocations=RevocationSet((revocation,)),
        dispatch_policy=CapabilityDispatchPolicy({"i2p-dht-control": cap_authority.public_key_bytes}),
        admission_budget=AdmissionBudget(allowed_namespaces=frozenset({"i2p-dht-control"}), max_streams=3, max_bytes=4096, max_metadata=10),
        garden_keypair=kp(99),
        garden_node_id=ident(99).node_id,
        source_family="fam-A",
        now=now + 1,
        expected_scope_id=scope_id,
    )
    assert report.decision.kind is CapabilityDispatchDecisionKind.REJECT_CAPABILITY
    assert report.admission_decision is None


def test_capability_dispatch_usefully_refuses_after_capability_success() -> None:
    now = 1_765_308_000
    actor = ident(12)
    registry_authority = kp(90)
    cap_authority = kp(91)
    policy = namespace_policy(now, registry_authority)
    registry = NamespaceRegistry((policy,), memory=memory_from_policies((policy,)))
    frame, payload, body, scope_id = frame_payload_body(now, actor, kp(12))
    grant = CapabilityGrant.create(
        issuer_keypair=cap_authority,
        subject_public_key=actor.public_key,
        capability=CapabilityKind.WRITE_HEAD,
        resource=scope_id,
        not_before=now - 5,
        ttl=600,
        sequence=1,
    )
    report = evaluate_capability_dispatch(
        registry=registry,
        frame=frame,
        payload=payload,
        body=body,
        grants=(grant,),
        revocations=RevocationSet(()),
        dispatch_policy=CapabilityDispatchPolicy({"i2p-dht-control": cap_authority.public_key_bytes}),
        admission_budget=AdmissionBudget(allowed_namespaces=frozenset({"i2p-dht-control"}), max_streams=0, max_bytes=4096, max_metadata=10),
        garden_keypair=kp(99),
        garden_node_id=ident(99).node_id,
        source_family="fam-A",
        now=now + 1,
        expected_scope_id=scope_id,
    )
    assert report.decision.kind is CapabilityDispatchDecisionKind.REFUSE_ADMISSION_USEFULLY
    assert report.refused_usefully
    assert report.admission_decision is not None and report.admission_decision.receipt is not None



def test_capability_dispatch_rejects_actor_mismatch_before_capability_chain() -> None:
    now = 1_765_308_000
    actor = ident(13)
    other_actor = ident(14)
    registry_authority = kp(90)
    cap_authority = kp(91)
    policy = namespace_policy(now, registry_authority)
    registry = NamespaceRegistry((policy,), memory=memory_from_policies((policy,)))
    frame, payload, body, scope_id = frame_payload_body(now, actor, kp(13))
    grant = CapabilityGrant.create(
        issuer_keypair=cap_authority,
        subject_public_key=other_actor.public_key,
        capability=CapabilityKind.WRITE_HEAD,
        resource=scope_id,
        not_before=now - 5,
        ttl=600,
        sequence=1,
    )
    report = evaluate_capability_dispatch(
        registry=registry,
        frame=frame,
        payload=payload,
        body=body,
        grants=(grant,),
        revocations=RevocationSet(()),
        dispatch_policy=CapabilityDispatchPolicy({"i2p-dht-control": cap_authority.public_key_bytes}),
        admission_budget=AdmissionBudget(allowed_namespaces=frozenset({"i2p-dht-control"}), max_streams=3, max_bytes=4096, max_metadata=10),
        garden_keypair=kp(99),
        garden_node_id=ident(99).node_id,
        source_family="fam-A",
        now=now + 1,
        expected_scope_id=scope_id,
        actor_public_key=other_actor.public_key,
    )
    assert report.decision.kind is CapabilityDispatchDecisionKind.REJECT_ACTOR_MISMATCH
    assert report.capability_check is None
    assert report.admission_decision is None

def test_evidence_gc_preserves_pinned_negative_evidence_and_drops_soft_noise() -> None:
    now = 1_765_308_500
    scope = digest("evidence-scope")
    items = (
        EvidenceItem(EvidenceKind.PROVIDER_TRUE, scope, digest("soft-old"), "fam-A", "path-A", now - 2000, now - 1000, byte_cost=100),
        EvidenceItem(EvidenceKind.MUTABLE_FORK, scope, digest("fork-old"), "fam-A", "path-A", now - 2000, now - 1000, byte_cost=100, sequence=4),
        EvidenceItem(EvidenceKind.TOMBSTONE, scope, digest("tomb-old"), "fam-B", "path-B", now - 2000, now - 1000, byte_cost=100, sequence=5),
    )
    report = collect_evidence_gc(items, policy=EvidenceGcPolicy(max_total_bytes=500, max_soft_age_after_expiry=0, max_hard_age_after_expiry=10_000), now=now)
    kept_kinds = {item.kind for item in report.kept}
    dropped_kinds = {item.kind for item in report.dropped}
    assert EvidenceKind.MUTABLE_FORK in kept_kinds
    assert EvidenceKind.TOMBSTONE in kept_kinds
    assert EvidenceKind.PROVIDER_TRUE in dropped_kinds


def test_evidence_gc_family_caps_and_conflict_quarantine() -> None:
    now = 1_765_308_500
    scope = digest("evidence-conflict")
    a = EvidenceItem(EvidenceKind.MUTABLE_LATEST, scope, digest("latest-A"), "fam-A", "path-A", now - 10, now + 1000, byte_cost=100, sequence=7)
    b = EvidenceItem(EvidenceKind.MUTABLE_LATEST, scope, digest("latest-B"), "fam-B", "path-B", now - 9, now + 1000, byte_cost=100, sequence=7)
    c = EvidenceItem(EvidenceKind.PROVIDER_TRUE, scope, digest("soft-one"), "fam-C", "path-C", now - 8, now + 1000, byte_cost=100)
    d = EvidenceItem(EvidenceKind.PROVIDER_TRUE, scope, digest("soft-two"), "fam-C", "path-C", now - 7, now + 1000, byte_cost=100)
    report = collect_evidence_gc((a, b, c, d), policy=EvidenceGcPolicy(max_total_bytes=1000, max_per_family_per_scope=1), now=now)
    assert any(decision.kind is EvidenceGcDecisionKind.QUARANTINE_CONFLICTING_DIGEST for decision in report.decisions)
    assert any(decision.kind is EvidenceGcDecisionKind.DROP_DUPLICATE_FAMILY for decision in report.decisions)
    assert report.quarantine_digests


def make_head(key: DhtKeypair, *, seq: int, prev: bytes, payload: str, now: int, scope: str = "split-scope") -> EpochHead:
    return EpochHead.create(
        keypair=key,
        purpose=EpochPurpose.POLICY_PORTFOLIO,
        scope=scope,
        sequence=seq,
        prev_digest=prev,
        payload_digest=digest(payload),
        issued_at=now - 5,
        valid_from=now - 10,
        valid_until=now + 1000,
    )


def test_splitmerge_accepts_diverse_linked_advance_after_partition() -> None:
    now = 1_765_309_000
    authority = kp(31)
    memory = EpochMemory()
    first = make_head(authority, seq=1, prev=b"\x00" * 32, payload="policy-v1", now=now)
    memory.commit(first)
    second = make_head(authority, seq=2, prev=first.head_digest, payload="policy-v2", now=now)
    observations = (
        PartitionObservation("partition-A", second, "source-A", "path-A", now),
        PartitionObservation("partition-B", second, "source-B", "path-B", now),
    )
    report = merge_partition_observations(memory, observations, now=now)
    assert report.decision.kind is SplitMergeDecisionKind.ACCEPT_MERGED_ADVANCE
    assert memory.accepted[first.scope_id].head_digest == second.head_digest


def test_splitmerge_quarantines_same_sequence_partition_fork() -> None:
    now = 1_765_309_000
    authority = kp(32)
    memory = EpochMemory()
    first = make_head(authority, seq=1, prev=b"\x00" * 32, payload="policy-v1", now=now)
    memory.commit(first)
    left = make_head(authority, seq=2, prev=first.head_digest, payload="policy-left", now=now)
    right = make_head(authority, seq=2, prev=first.head_digest, payload="policy-right", now=now)
    report = merge_partition_observations(
        memory,
        (
            PartitionObservation("partition-A", left, "source-A", "path-A", now),
            PartitionObservation("partition-B", right, "source-B", "path-B", now),
        ),
        now=now,
    )
    assert report.decision.kind is SplitMergeDecisionKind.QUARANTINE_SAME_SEQUENCE_SPLIT
    assert memory.forks


def test_splitmerge_rejects_prev_split_and_under_diverse_latest() -> None:
    now = 1_765_309_000
    authority = kp(33)
    memory = EpochMemory()
    first = make_head(authority, seq=1, prev=b"\x00" * 32, payload="policy-v1", now=now)
    memory.commit(first)
    skipped = make_head(authority, seq=2, prev=digest("wrong-prev"), payload="policy-v2", now=now)
    prev_report = merge_partition_observations(
        memory,
        (PartitionObservation("partition-A", skipped, "source-A", "path-A", now), PartitionObservation("partition-B", skipped, "source-B", "path-B", now)),
        now=now,
    )
    assert prev_report.decision.kind is SplitMergeDecisionKind.QUARANTINE_PREV_SPLIT

    memory2 = EpochMemory()
    lonely = make_head(authority, seq=1, prev=b"\x00" * 32, payload="lonely", now=now, scope="lonely-scope")
    low_report = merge_partition_observations(memory2, (PartitionObservation("partition-A", lonely, "source-A", "path-A", now),), now=now)
    assert low_report.decision.kind is SplitMergeDecisionKind.WATCH_UNDER_DIVERSE_LATEST
    assert not low_report.decision.accept


def test_riskfold_current_surfaces_visible() -> None:
    report = audit_risk_fold(".", revision="rev0025")
    # This test is expected to pass after the rev0025 metadata/docs are folded.
    assert report.status == "pass", report.findings
