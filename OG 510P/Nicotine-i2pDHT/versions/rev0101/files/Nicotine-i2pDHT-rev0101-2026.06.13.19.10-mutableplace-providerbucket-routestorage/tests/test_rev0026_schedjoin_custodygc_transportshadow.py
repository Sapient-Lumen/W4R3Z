from __future__ import annotations

from dataclasses import replace

from i2p_dht_lab.admissionwall import AdmissionBudget
from i2p_dht_lab.capability import CapabilityGrant, CapabilityKind, CapabilityRevocation, RevocationSet
from i2p_dht_lab.capgate import CapabilityDispatchPolicy, evaluate_capability_dispatch
from i2p_dht_lab.custodyaudit import CustodyAuditChallenge, CustodyAuditDecision, CustodyAuditDecisionKind, CustodyAuditReport
from i2p_dht_lab.custodygc import CustodyGcDecisionKind, collect_joined_evidence_gc
from i2p_dht_lab.evidencegc import EvidenceGcDecisionKind, EvidenceGcPolicy, EvidenceItem, EvidenceKind
from i2p_dht_lab.epochgate import EpochHead, EpochMemory, EpochPurpose
from i2p_dht_lab.identity import DhtKeypair, NodeIdentity
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.namespaceregistry import NamespacePolicy, NamespaceRegistry, memory_from_policies
from i2p_dht_lab.partitionwitness import PartitionWitnessDecisionKind, assess_partition_witness_merge
from i2p_dht_lab.queueforge import QueueDecisionKind, QueuePolicy, QueueWorkKind
from i2p_dht_lab.revocation_pressure import RevocationHeadVerdict, RevocationPressureKind
from i2p_dht_lab.routegossip import RouteGossipDecision, RouteGossipDecisionKind, RouteGossipReport
from i2p_dht_lab.schedjoin import JoinedScheduleDecisionKind, JoinedSchedulePolicy, JoinedWorkCandidate, plan_joined_schedule
from i2p_dht_lab.splitmerge import PartitionObservation, SplitMergeDecisionKind
from i2p_dht_lab.tombmesh import TombMeshDecision, TombMeshDecisionKind, TombMeshReport
from i2p_dht_lab.tombstonecache import TombstoneKind
from i2p_dht_lab.transportshadow import ShadowPayload, ShadowPayloadKind, ShadowValidationKind, create_shadow_frame, validate_shadow_frame
from i2p_dht_lab.validatorwall import PayloadEnvelope, PayloadRole
from i2p_dht_lab.wirecanon import WireFrame, WireMessageKind
from i2p_dht_lab.witnesscache import WitnessCacheDecision, WitnessCacheDecisionKind, WitnessCacheSummary


def kp(n: int) -> DhtKeypair:
    return DhtKeypair.from_seed(bytes([n]) * 32)


def ident(n: int) -> NodeIdentity:
    return NodeIdentity.create(destination=f"rev0026-node-{n}.b32.i2p", keypair=kp(n))


def digest(label: str) -> bytes:
    return sha256(label.encode("utf-8"))


def namespace_policy(now: int, authority: DhtKeypair) -> NamespacePolicy:
    return NamespacePolicy.create(
        authority=authority,
        namespace="i2p-dht-control",
        sequence=1,
        issued_at=now - 10,
        ttl=1000,
        allowed_roles_by_kind={WireMessageKind.EPOCH_HEAD: frozenset({PayloadRole.MUTABLE_HEAD})},
        max_body_bytes=4096,
        max_ttl_seconds=600,
        required_flags_by_role={PayloadRole.MUTABLE_HEAD: frozenset({"mutable-head"})},
    )


def frame_payload_body(now: int, actor: NodeIdentity, actor_kp: DhtKeypair, *, request_label: str, scope: bytes):
    body = f"rev0026 mutable body {request_label}".encode("utf-8")
    envelope = PayloadEnvelope.create(namespace="i2p-dht-control", role=PayloadRole.MUTABLE_HEAD, scope_id=scope, body=body, issued_at=now, ttl=300)
    payload = envelope.to_bytes()
    frame = WireFrame.create(
        keypair=actor_kp,
        sender_node_id=actor.node_id,
        message_kind=WireMessageKind.EPOCH_HEAD,
        request_id=digest(request_label),
        payload=payload,
        issued_at=now,
        ttl=300,
        flags=("mutable-head",),
    )
    return frame, payload, body


def dispatch_report(now: int, *, actor_n: int, family: str, max_streams: int = 5, revoked: bool = False):
    actor = ident(actor_n)
    registry_authority = kp(90)
    cap_authority = kp(91)
    policy = namespace_policy(now, registry_authority)
    registry = NamespaceRegistry((policy,), memory=memory_from_policies((policy,)))
    scope = digest(f"scope-{actor_n}")
    frame, payload, body = frame_payload_body(now, actor, kp(actor_n), request_label=f"request-{actor_n}", scope=scope)
    grant = CapabilityGrant.create(
        issuer_keypair=cap_authority,
        subject_public_key=actor.public_key,
        capability=CapabilityKind.WRITE_HEAD,
        resource=scope,
        not_before=now - 5,
        ttl=600,
        sequence=1,
    )
    revocations = RevocationSet((CapabilityRevocation.create(issuer_keypair=cap_authority, grant_hash=grant.grant_hash, issued_at=now),)) if revoked else RevocationSet(())
    return evaluate_capability_dispatch(
        registry=registry,
        frame=frame,
        payload=payload,
        body=body,
        grants=(grant,),
        revocations=revocations,
        dispatch_policy=CapabilityDispatchPolicy({"i2p-dht-control": cap_authority.public_key_bytes}),
        admission_budget=AdmissionBudget(allowed_namespaces=frozenset({"i2p-dht-control"}), max_streams=max_streams, max_bytes=4096, max_metadata=10),
        garden_keypair=kp(99),
        garden_node_id=ident(99).node_id,
        source_family=family,
        now=now + 1,
        expected_scope_id=scope,
    )


def test_schedjoin_protected_work_survives_bulk_and_refusal_pressure() -> None:
    now = 1_765_400_000
    candidates = (
        JoinedWorkCandidate("head", dispatch_report(now, actor_n=1, family="fam-control"), QueueWorkKind.HEAD_WATCH, deadline=now + 60, estimated_latency_ms=100),
        JoinedWorkCandidate("bulk-a", dispatch_report(now, actor_n=2, family="fam-bulk-a"), QueueWorkKind.PROVIDER_BULK, deadline=now + 60, estimated_latency_ms=100),
        JoinedWorkCandidate("bulk-b", dispatch_report(now, actor_n=3, family="fam-bulk-b"), QueueWorkKind.PROVIDER_BULK, deadline=now + 60, estimated_latency_ms=100),
    )
    report = plan_joined_schedule(
        candidates,
        queue_policy=QueuePolicy(max_streams=1, reserve_for_survivors=1),
        garden_keypair=kp(99),
        garden_node_id=ident(99).node_id,
        now=now + 2,
    )
    assert report.decision.kind is JoinedScheduleDecisionKind.SCHEDULED_WITH_REFUSALS
    assert report.protected_started_count == 1
    assert report.queue_plan is not None
    assert [decision.item.work_kind for decision in report.queue_plan.started] == [QueueWorkKind.HEAD_WATCH]
    assert any(decision.kind in {QueueDecisionKind.REFUSE_USEFULLY, QueueDecisionKind.DEFER_FOR_RESERVE} for decision in report.queue_plan.decisions)


def test_schedjoin_quarantines_refusal_laundering_and_ignores_revoked_work() -> None:
    now = 1_765_400_000
    refused = tuple(JoinedWorkCandidate(f"refused-{i}", dispatch_report(now, actor_n=10 + i, family="fam-captured", max_streams=0), QueueWorkKind.WITNESS_QUERY, deadline=now + 60) for i in range(3))
    revoked = JoinedWorkCandidate("revoked", dispatch_report(now, actor_n=20, family="fam-captured", revoked=True), QueueWorkKind.HEAD_WATCH, deadline=now + 60)
    report = plan_joined_schedule(
        refused + (revoked,),
        queue_policy=QueuePolicy(max_streams=2),
        garden_keypair=kp(99),
        garden_node_id=ident(99).node_id,
        now=now + 2,
        policy=JoinedSchedulePolicy(max_useful_refusals_per_family=2),
    )
    assert report.decision.kind is JoinedScheduleDecisionKind.QUARANTINE_REFUSAL_LAUNDERING
    assert report.queue_plan is None
    assert report.useful_refusals_by_family["fam-captured"] == 3


def custody_report(kind: CustodyAuditDecisionKind, *, now: int) -> CustodyAuditReport:
    challenge = CustodyAuditChallenge.create(target=digest("custody-target"), record_digest=digest("record"), nonce=b"nonce", issued_at=now - 5)
    return CustodyAuditReport(
        challenge=challenge,
        valid_proofs=(),
        custody_proofs=(),
        useful_refusals=(),
        false_proof_count=1 if kind.value.startswith("quarantine_") else 0,
        replay_pressure_count=0,
        contract_gap_count=0,
        proof_families=frozenset({"fam-custody"}),
        family_counts={"fam-custody": 1},
        decision=CustodyAuditDecision(kind, kind in {CustodyAuditDecisionKind.PROVEN_DIVERSE, CustodyAuditDecisionKind.PROVEN_WITH_REFUSAL_BACKOFF}, kind.value),
        transcript_digest=digest(f"custody-{kind.value}"),
    )


def test_custodygc_keeps_negative_pressure_from_different_sources() -> None:
    now = 1_765_400_500
    tomb = TombMeshReport(
        target_commitment=digest("tomb-target"),
        live_tombstone_count=1,
        tombstone_kinds=(TombstoneKind.KEY_COMPROMISED,),
        tombstone_families=frozenset({"fam-tomb"}),
        witness_families=frozenset({"fam-witness-a", "fam-witness-b"}),
        resurrection_weight=200,
        newest_head_seq=7,
        newest_tombstone_seq=6,
        decision=TombMeshDecision(TombMeshDecisionKind.BLOCK_RESURRECTION_MESH, False, "block stale alive evidence"),
        transcript_digest=digest("tombmesh-report"),
    )
    verdict = RevocationHeadVerdict(RevocationPressureKind.STALE_ROLLBACK, kp(88).public_key_bytes, 2, 3, digest("revocation-stale"), "old revocation head replayed")
    soft = EvidenceItem(EvidenceKind.PROVIDER_TRUE, digest("soft-scope"), digest("soft-object"), "fam-soft", "path-soft", now - 2000, now - 1000, byte_cost=64)
    report = collect_joined_evidence_gc(
        (soft,),
        custody_reports=(custody_report(CustodyAuditDecisionKind.QUARANTINE_FALSE_PROOF, now=now),),
        tomb_mesh_reports=(tomb,),
        revocation_verdicts=(verdict,),
        now=now,
        policy=EvidenceGcPolicy(max_total_bytes=4096),
    )
    kinds = {item.kind for item in report.kept}
    assert report.decision.kind is CustodyGcDecisionKind.KEEP_WITH_NEGATIVE_PRESSURE
    assert EvidenceKind.PROVIDER_FALSE in kinds
    assert EvidenceKind.TOMBSTONE in kinds
    assert EvidenceKind.CAPABILITY_REVOCATION in kinds
    assert EvidenceKind.PROVIDER_TRUE not in kinds


def test_custodygc_quarantines_conflicting_same_sequence_evidence() -> None:
    now = 1_765_400_500
    scope = digest("gc-conflict-scope")
    a = EvidenceItem(EvidenceKind.MUTABLE_LATEST, scope, digest("latest-a"), "fam-a", "path-a", now - 10, now + 1000, sequence=9)
    b = EvidenceItem(EvidenceKind.MUTABLE_LATEST, scope, digest("latest-b"), "fam-b", "path-b", now - 9, now + 1000, sequence=9)
    report = collect_joined_evidence_gc((a, b), now=now, policy=EvidenceGcPolicy(max_total_bytes=4096))
    assert report.decision.kind is CustodyGcDecisionKind.QUARANTINE_SYNTHESIZED_CONFLICT
    assert any(decision.kind is EvidenceGcDecisionKind.QUARANTINE_CONFLICTING_DIGEST for decision in report.gc_report.decisions)


def make_head(key: DhtKeypair, *, seq: int, prev: bytes, payload: str, now: int) -> EpochHead:
    return EpochHead.create(
        keypair=key,
        purpose=EpochPurpose.POLICY_PORTFOLIO,
        scope="rev0026-partition",
        sequence=seq,
        prev_digest=prev,
        payload_digest=digest(payload),
        issued_at=now - 5,
        valid_from=now - 10,
        valid_until=now + 1000,
    )


def route_report(kind: RouteGossipDecisionKind) -> RouteGossipReport:
    return RouteGossipReport(
        target=digest("route-target"),
        selected_contacts=(),
        stale_evictions=(),
        quarantined_contacts=(),
        family_counts={"fam-route-a": 1, "fam-route-b": 1} if kind is RouteGossipDecisionKind.ACCEPT_REPAIR_CONTACTS else {"fam-route-a": 2},
        issuer_family_fraction=0.4 if kind is RouteGossipDecisionKind.ACCEPT_REPAIR_CONTACTS else 1.0,
        transcript_digest=digest(f"route-{kind.value}"),
        decision=RouteGossipDecision(kind, kind is RouteGossipDecisionKind.ACCEPT_REPAIR_CONTACTS, kind.value),
    )


def witness_summary(kind: WitnessCacheDecisionKind) -> WitnessCacheSummary:
    return WitnessCacheSummary(
        target_commitment=digest("witness-target"),
        now=1_765_400_900,
        valid_cached_count=2,
        expired_count=0,
        counted_count=2,
        family_weights={"fam-w-a": 100, "fam-w-b": 100} if kind is WitnessCacheDecisionKind.PRESERVE_DIVERSE_EVIDENCE else {"fam-w-a": 100},
        claim_weights={"mutable_latest": 200},
        contradictions=(),
        decision=WitnessCacheDecision(kind, kind is WitnessCacheDecisionKind.PRESERVE_DIVERSE_EVIDENCE, kind.value),
        transcript_digest=digest(f"witness-{kind.value}"),
    )


def test_partitionwitness_requires_route_and_witness_before_commit() -> None:
    now = 1_765_400_900
    authority = kp(40)
    memory = EpochMemory()
    first = make_head(authority, seq=1, prev=b"\x00" * 32, payload="v1", now=now)
    memory.commit(first)
    second = make_head(authority, seq=2, prev=first.head_digest, payload="v2", now=now)
    observations = (
        PartitionObservation("part-a", second, "source-a", "path-a", now),
        PartitionObservation("part-b", second, "source-b", "path-b", now),
    )
    blocked = assess_partition_witness_merge(
        memory,
        observations,
        now=now,
        route_report=route_report(RouteGossipDecisionKind.CONTINUE_LOW_DIVERSITY),
        witness_summary=witness_summary(WitnessCacheDecisionKind.PRESERVE_DIVERSE_EVIDENCE),
    )
    assert blocked.decision.kind is PartitionWitnessDecisionKind.WATCH_ROUTE_GAP
    assert memory.accepted[first.scope_id].head_digest == first.head_digest
    accepted = assess_partition_witness_merge(
        memory,
        observations,
        now=now,
        route_report=route_report(RouteGossipDecisionKind.ACCEPT_REPAIR_CONTACTS),
        witness_summary=witness_summary(WitnessCacheDecisionKind.PRESERVE_DIVERSE_EVIDENCE),
    )
    assert accepted.decision.kind is PartitionWitnessDecisionKind.ACCEPT_MERGED_WITH_ROUTE_AND_WITNESS
    assert memory.accepted[first.scope_id].head_digest == second.head_digest


def test_partitionwitness_preserves_splitmerge_quarantine() -> None:
    now = 1_765_400_900
    authority = kp(41)
    memory = EpochMemory()
    first = make_head(authority, seq=1, prev=b"\x00" * 32, payload="v1", now=now)
    memory.commit(first)
    left = make_head(authority, seq=2, prev=first.head_digest, payload="left", now=now)
    right = make_head(authority, seq=2, prev=first.head_digest, payload="right", now=now)
    report = assess_partition_witness_merge(
        memory,
        (PartitionObservation("part-a", left, "source-a", "path-a", now), PartitionObservation("part-b", right, "source-b", "path-b", now)),
        now=now,
        route_report=route_report(RouteGossipDecisionKind.ACCEPT_REPAIR_CONTACTS),
        witness_summary=witness_summary(WitnessCacheDecisionKind.PRESERVE_DIVERSE_EVIDENCE),
    )
    assert report.decision.kind is PartitionWitnessDecisionKind.QUARANTINE_SPLITMERGE
    assert report.split_report.decision.kind is SplitMergeDecisionKind.QUARANTINE_SAME_SEQUENCE_SPLIT


def test_transportshadow_accepts_signed_canonical_shadow_report() -> None:
    now = 1_765_401_000
    sender = ident(70)
    shadow = create_shadow_frame(
        keypair=kp(70),
        sender_node_id=sender.node_id,
        request_id=digest("shadow-request"),
        payload_kind=ShadowPayloadKind.CUSTODY_GC_REPORT,
        report_digest=digest("report"),
        subject_digest=digest("subject"),
        issued_at=now,
        ttl=300,
        note="custody gc report",
    )
    report = validate_shadow_frame(shadow.frame, payload_bytes=shadow.payload.to_bytes(), now=now + 1, expected_report_digest=digest("report"))
    assert report.validation.kind is ShadowValidationKind.ACCEPT_SHADOW
    assert report.payload is not None and report.payload.kind is ShadowPayloadKind.CUSTODY_GC_REPORT


def test_transportshadow_rejects_tampering_kind_mismatch_and_digest_mismatch() -> None:
    now = 1_765_401_000
    sender = ident(71)
    shadow = create_shadow_frame(
        keypair=kp(71),
        sender_node_id=sender.node_id,
        request_id=digest("shadow-request-2"),
        payload_kind=ShadowPayloadKind.JOINED_SCHEDULE_REPORT,
        report_digest=digest("report-a"),
        subject_digest=digest("subject"),
        issued_at=now,
        ttl=300,
    )
    tampered = validate_shadow_frame(shadow.frame, payload_bytes=shadow.payload.to_bytes() + b"x", now=now + 1)
    assert tampered.validation.kind is ShadowValidationKind.REJECT_WIRE
    payload = ShadowPayload(ShadowPayloadKind.CUSTODY_GC_REPORT, digest("report-a"), digest("subject"), now, now + 300)
    mismatch_frame = WireFrame.create(
        keypair=kp(71),
        sender_node_id=sender.node_id,
        message_kind=WireMessageKind.EPOCH_HEAD,
        request_id=digest("shadow-request-3"),
        payload=payload.to_bytes(),
        issued_at=now,
        ttl=300,
        flags=("shadow-report", ShadowPayloadKind.CUSTODY_GC_REPORT.value),
    )
    mismatch = validate_shadow_frame(mismatch_frame, payload_bytes=payload.to_bytes(), now=now + 1)
    assert mismatch.validation.kind is ShadowValidationKind.REJECT_ROLE_KIND
    digest_mismatch = validate_shadow_frame(shadow.frame, payload_bytes=shadow.payload.to_bytes(), now=now + 1, expected_report_digest=digest("other-report"))
    assert digest_mismatch.validation.kind is ShadowValidationKind.REJECT_DIGEST_BINDING

from i2p_dht_lab.joinfold import audit_join_fold


def test_joinfold_current_surfaces_visible() -> None:
    report = audit_join_fold('.', revision='rev0026')
    assert report.status == 'pass', report.findings
