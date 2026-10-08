from dataclasses import replace

import pytest

from i2p_dht_lab.admissionwall import (
    AdmissionBudget,
    AdmissionDecisionKind,
    AdmissionPriority,
    AdmissionRequest,
    AdmissionState,
    decide_admission_batch,
)
from i2p_dht_lab.identity import DhtKeypair, NodeIdentity
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.namespaceregistry import (
    NamespaceDecisionKind,
    NamespaceMemory,
    NamespacePolicy,
    NamespaceRegistry,
    memory_from_policies,
    validate_namespace_dispatch,
)
from i2p_dht_lab.namespacefold import audit_namespace_fold
from i2p_dht_lab.rangesketch import (
    LocalRangeMemory,
    RangeCell,
    RangeRepairDecisionKind,
    RangeSketch,
    RangeSketchKind,
    RangeSketchPolicy,
    plan_range_repair,
)
from i2p_dht_lab.validatorwall import PayloadEnvelope, PayloadRole
from i2p_dht_lab.wirecanon import WireFrame, WireMessageKind

NOW = 1_765_306_000


def kp(n: int) -> DhtKeypair:
    return DhtKeypair.from_seed(bytes([n % 256]) * 32)


def ident(n: int) -> NodeIdentity:
    return NodeIdentity.create(destination=f"rev0023-{n}.b32.i2p", keypair=kp(n))


def digest(label: str) -> bytes:
    return sha256(label.encode("utf-8"))


def cell(kind: RangeSketchKind, name: str, seq: int = 1, *, bits: int = 4, prefix: int = 1, tombstones: int = 0) -> RangeCell:
    return RangeCell(kind=kind, region_prefix=prefix, region_bits=bits, sequence=seq, root_digest=digest(name), item_count=4, tombstone_count=tombstones)


def sketch(n: int, family: str, cells, *, issued_at: int = NOW, ttl: int = 300, sequence: int = 1) -> RangeSketch:
    return RangeSketch.create(keypair=kp(n), source_node_id=ident(n).node_id, source_family=family, issued_at=issued_at, ttl=ttl, cells=tuple(cells), sequence=sequence)


def make_policy(*, namespace="i2p-dht-control", sequence=1, max_body_bytes=100, max_ttl_seconds=300, scope_prefixes=()):
    return NamespacePolicy.create(
        authority=kp(91),
        namespace=namespace,
        sequence=sequence,
        issued_at=NOW - 5,
        ttl=1000,
        allowed_roles_by_kind={WireMessageKind.EPOCH_HEAD: frozenset({PayloadRole.MUTABLE_HEAD}), WireMessageKind.FIND_PROVIDER: frozenset({PayloadRole.PROVIDER_CLAIM})},
        max_body_bytes=max_body_bytes,
        max_ttl_seconds=max_ttl_seconds,
        required_flags_by_role={PayloadRole.MUTABLE_HEAD: frozenset({"mutable-head"})},
        scope_prefixes=scope_prefixes,
    )


def make_frame_body(*, namespace="i2p-dht-control", role=PayloadRole.MUTABLE_HEAD, kind=WireMessageKind.EPOCH_HEAD, flags=("mutable-head",), ttl=120, body=b"hello", scope=None):
    node = ident(44)
    scope_id = scope or digest("scope")
    envelope = PayloadEnvelope.create(namespace=namespace, role=role, scope_id=scope_id, body=body, issued_at=NOW, ttl=ttl)
    payload = envelope.to_bytes()
    frame = WireFrame.create(keypair=kp(44), sender_node_id=node.node_id, message_kind=kind, request_id=digest("request" + namespace + role.value + kind.value), payload=payload, issued_at=NOW, ttl=ttl, flags=flags)
    return frame, payload, body, envelope


# ---------------- range sketch ----------------


def test_range_sketch_accepts_in_sync_with_diverse_families():
    local_cell = cell(RangeSketchKind.MUTABLE_HEAD, "root-v1")
    report = plan_range_repair(
        LocalRangeMemory((local_cell,)),
        (sketch(1, "fam-a", (local_cell,)), sketch(2, "fam-b", (local_cell,))),
        now=NOW + 1,
    )
    assert report.decision.kind is RangeRepairDecisionKind.ACCEPT_IN_SYNC
    assert report.decision.accept
    assert report.family_counts == {"fam-a": 1, "fam-b": 1}


def test_range_sketch_requests_repair_for_newer_non_tombstone_root():
    local_cell = cell(RangeSketchKind.MUTABLE_HEAD, "root-v1", seq=1)
    newer = cell(RangeSketchKind.MUTABLE_HEAD, "root-v2", seq=2)
    report = plan_range_repair(LocalRangeMemory((local_cell,)), (sketch(1, "fam-a", (newer,)), sketch(2, "fam-b", (newer,))), now=NOW + 1)
    assert report.decision.kind is RangeRepairDecisionKind.REQUEST_RANGE_REPAIR
    assert report.repair_cells == (newer,)


def test_range_sketch_tombstone_ranges_are_repaired_first():
    local_cell = cell(RangeSketchKind.TOMBSTONE, "tomb-v1", seq=1, tombstones=1)
    newer = cell(RangeSketchKind.TOMBSTONE, "tomb-v2", seq=2, tombstones=2)
    provider = cell(RangeSketchKind.PROVIDER_LEDGER, "provider-v2", seq=2)
    report = plan_range_repair(LocalRangeMemory((local_cell,)), (sketch(1, "fam-a", (newer, provider)), sketch(2, "fam-b", (newer, provider))), now=NOW + 1)
    assert report.decision.kind is RangeRepairDecisionKind.REQUEST_TOMBSTONE_FIRST
    assert newer in report.tombstone_first_cells
    assert provider in report.repair_cells


def test_range_sketch_quarantines_same_sequence_fork():
    local_cell = cell(RangeSketchKind.MUTABLE_HEAD, "root-v1", seq=1)
    fork_a = cell(RangeSketchKind.MUTABLE_HEAD, "fork-a", seq=2)
    fork_b = cell(RangeSketchKind.MUTABLE_HEAD, "fork-b", seq=2)
    report = plan_range_repair(LocalRangeMemory((local_cell,)), (sketch(1, "fam-a", (fork_a,)), sketch(2, "fam-b", (fork_b,))), now=NOW + 1)
    assert report.decision.kind is RangeRepairDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK
    assert report.quarantined


def test_range_sketch_quarantines_stale_replay_mesh():
    local_cell_a = cell(RangeSketchKind.MUTABLE_HEAD, "root-a-v3", seq=3, prefix=1)
    local_cell_b = cell(RangeSketchKind.PROVIDER_LEDGER, "root-b-v3", seq=3, prefix=2)
    stale_a = cell(RangeSketchKind.MUTABLE_HEAD, "root-a-v2", seq=2, prefix=1)
    stale_b = cell(RangeSketchKind.PROVIDER_LEDGER, "root-b-v2", seq=2, prefix=2)
    report = plan_range_repair(
        LocalRangeMemory((local_cell_a, local_cell_b)),
        (sketch(1, "fam-a", (stale_a, stale_b)), sketch(2, "fam-b", (stale_a, stale_b))),
        now=NOW + 1,
        policy=RangeSketchPolicy(stale_replay_threshold=2),
    )
    assert report.decision.kind is RangeRepairDecisionKind.QUARANTINE_STALE_REPLAY
    assert len(report.stale_cells) >= 2


def test_range_sketch_requires_family_diversity_before_repair():
    newer = cell(RangeSketchKind.MUTABLE_HEAD, "root-v2", seq=2)
    report = plan_range_repair(LocalRangeMemory(()), (sketch(1, "fam-a", (newer,)), sketch(2, "fam-a", (newer,))), now=NOW + 1)
    assert report.decision.kind is RangeRepairDecisionKind.CONTINUE_NEED_FAMILY_DIVERSITY


def test_range_sketch_rejects_bad_signature_or_time():
    valid = sketch(1, "fam-a", (cell(RangeSketchKind.MUTABLE_HEAD, "root"),), issued_at=NOW - 1000, ttl=10)
    report = plan_range_repair(LocalRangeMemory(()), (valid,), now=NOW + 1)
    assert report.decision.kind is RangeRepairDecisionKind.REJECT_BAD_SIGNATURE_OR_TIME


# ---------------- namespace registry ----------------


def test_namespace_registry_accepts_policy_and_validatorwall_agreement():
    policy = make_policy()
    frame, payload, body, _ = make_frame_body()
    registry = NamespaceRegistry((policy,), memory=memory_from_policies((policy,)))
    report = validate_namespace_dispatch(registry, frame, payload=payload, body=body, now=NOW + 1)
    assert report.decision.kind is NamespaceDecisionKind.ACCEPT_NAMESPACE
    assert report.decision.accept


def test_namespace_registry_rejects_unknown_namespace():
    policy = make_policy(namespace="i2p-dht-control")
    frame, payload, body, _ = make_frame_body(namespace="stranger-space")
    report = validate_namespace_dispatch(NamespaceRegistry((policy,), memory=memory_from_policies((policy,))), frame, payload=payload, body=body, now=NOW + 1)
    assert report.decision.kind is NamespaceDecisionKind.REJECT_UNKNOWN_NAMESPACE


def test_namespace_registry_rejects_policy_signature_tamper():
    policy = make_policy()
    tampered = replace(policy, max_body_bytes=policy.max_body_bytes + 1)
    frame, payload, body, _ = make_frame_body()
    report = validate_namespace_dispatch(NamespaceRegistry((tampered,)), frame, payload=payload, body=body, now=NOW + 1)
    assert report.decision.kind is NamespaceDecisionKind.REJECT_BAD_SIGNATURE


def test_namespace_registry_rejects_expired_policy():
    policy = NamespacePolicy.create(authority=kp(91), namespace="i2p-dht-control", sequence=1, issued_at=NOW - 1000, ttl=10, allowed_roles_by_kind={WireMessageKind.EPOCH_HEAD: frozenset({PayloadRole.MUTABLE_HEAD})})
    frame, payload, body, _ = make_frame_body()
    report = validate_namespace_dispatch(NamespaceRegistry((policy,)), frame, payload=payload, body=body, now=NOW + 1)
    assert report.decision.kind is NamespaceDecisionKind.REJECT_TIME_WINDOW


def test_namespace_registry_rejects_policy_rollback_against_memory():
    old = make_policy(sequence=1)
    newer = make_policy(sequence=2)
    memory = memory_from_policies((newer,))
    frame, payload, body, _ = make_frame_body()
    report = validate_namespace_dispatch(NamespaceRegistry((old,), memory=memory), frame, payload=payload, body=body, now=NOW + 1)
    assert report.decision.kind is NamespaceDecisionKind.REJECT_ROLLBACK


def test_namespace_registry_quarantines_same_sequence_policy_fork():
    policy = make_policy(sequence=2)
    fork = NamespacePolicy.create(authority=kp(91), namespace="i2p-dht-control", sequence=2, issued_at=NOW - 5, ttl=1000, allowed_roles_by_kind={WireMessageKind.EPOCH_HEAD: frozenset({PayloadRole.MUTABLE_HEAD})}, max_body_bytes=999)
    memory = NamespaceMemory(highest_sequence={"i2p-dht-control": 2}, seen_digests_by_seq={("i2p-dht-control", 2): frozenset({policy.policy_digest})})
    frame, payload, body, _ = make_frame_body()
    report = validate_namespace_dispatch(NamespaceRegistry((fork,), memory=memory), frame, payload=payload, body=body, now=NOW + 1)
    assert report.decision.kind is NamespaceDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK


def test_namespace_registry_rejects_role_kind_mismatch():
    policy = make_policy()
    frame, payload, body, _ = make_frame_body(kind=WireMessageKind.FIND_PROVIDER, role=PayloadRole.MUTABLE_HEAD)
    report = validate_namespace_dispatch(NamespaceRegistry((policy,), memory=memory_from_policies((policy,))), frame, payload=payload, body=body, now=NOW + 1)
    assert report.decision.kind is NamespaceDecisionKind.REJECT_KIND_ROLE


def test_namespace_registry_rejects_ttl_or_size_excess():
    policy = make_policy(max_body_bytes=5, max_ttl_seconds=30)
    frame, payload, body, _ = make_frame_body(ttl=120, body=b"too large body")
    report = validate_namespace_dispatch(NamespaceRegistry((policy,), memory=memory_from_policies((policy,))), frame, payload=payload, body=body, now=NOW + 1)
    assert report.decision.kind is NamespaceDecisionKind.REJECT_TTL_OR_SIZE


def test_namespace_registry_rejects_scope_prefix_mismatch():
    policy = make_policy(scope_prefixes=(b"ok",))
    frame, payload, body, _ = make_frame_body(scope=b"no" + b"\x00" * 30)
    report = validate_namespace_dispatch(NamespaceRegistry((policy,), memory=memory_from_policies((policy,))), frame, payload=payload, body=body, now=NOW + 1)
    assert report.decision.kind is NamespaceDecisionKind.REJECT_SCOPE_PREFIX


def test_namespace_registry_rejects_missing_required_flag_via_validator_wall():
    policy = make_policy()
    frame, payload, body, _ = make_frame_body(flags=())
    report = validate_namespace_dispatch(NamespaceRegistry((policy,), memory=memory_from_policies((policy,))), frame, payload=payload, body=body, now=NOW + 1)
    assert report.decision.kind is NamespaceDecisionKind.REJECT_VALIDATOR_WALL


# ---------------- admission wall ----------------


def req(n: int, family: str, *, priority=AdmissionPriority.NORMAL, namespace="i2p-dht-control", byte_cost=10, metadata_cost=1, issued_at=NOW, expires_at=NOW + 300) -> AdmissionRequest:
    return AdmissionRequest(frame_digest=digest(f"frame-{n}"), sender_node_id=ident(n).node_id, source_family=family, namespace=namespace, message_kind=WireMessageKind.EPOCH_HEAD, role=PayloadRole.MUTABLE_HEAD, priority=priority, stream_cost=1, byte_cost=byte_cost, metadata_cost=metadata_cost, issued_at=issued_at, expires_at=expires_at)


def budget(**kwargs) -> AdmissionBudget:
    params = dict(allowed_namespaces=frozenset({"i2p-dht-control", "i2p-dht-provider"}), max_streams=4, max_bytes=100, max_metadata=10, max_per_family=2, reserve_for_critical=1)
    params.update(kwargs)
    return AdmissionBudget(**params)


def test_admission_accepts_high_priority_before_bulk():
    requests = (req(1, "fam-a", priority=AdmissionPriority.BULK), req(2, "fam-b", priority=AdmissionPriority.CRITICAL), req(3, "fam-c", priority=AdmissionPriority.HIGH))
    report = decide_admission_batch(requests, budget=budget(max_streams=2, reserve_for_critical=0), keypair=kp(88), garden_node_id=ident(88).node_id, now=NOW + 1)
    accepted = [decision.request.priority for decision in report.accepted]
    assert AdmissionPriority.CRITICAL in accepted
    assert AdmissionPriority.HIGH in accepted
    assert AdmissionPriority.BULK not in accepted
    assert any(decision.useful_refusal for decision in report.refused)


def test_admission_reserves_capacity_for_critical_work():
    requests = (req(1, "fam-a", priority=AdmissionPriority.BULK), req(2, "fam-b", priority=AdmissionPriority.BULK), req(3, "fam-c", priority=AdmissionPriority.CRITICAL))
    report = decide_admission_batch(requests, budget=budget(max_streams=2, reserve_for_critical=1), keypair=kp(88), garden_node_id=ident(88).node_id, now=NOW + 1)
    assert any(decision.request.priority is AdmissionPriority.CRITICAL and decision.accepted for decision in report.decisions)
    assert report.accepted_streams <= 2


def test_admission_usefully_refuses_unknown_namespace():
    report = decide_admission_batch((req(1, "fam-a", namespace="unknown"),), budget=budget(), keypair=kp(88), garden_node_id=ident(88).node_id, now=NOW + 1)
    decision = report.decisions[0]
    assert decision.kind is AdmissionDecisionKind.REFUSE_USEFULLY
    assert decision.receipt and decision.receipt.verify(now=NOW + 2, expected_public_key=kp(88).public_key_bytes)


def test_admission_quarantines_family_flood():
    requests = tuple(req(n, "fam-a", priority=AdmissionPriority.HIGH) for n in range(1, 5))
    report = decide_admission_batch(requests, budget=budget(max_per_family=1, max_streams=4), keypair=kp(88), garden_node_id=ident(88).node_id, now=NOW + 1)
    assert len(report.accepted) == 1
    assert any(decision.kind is AdmissionDecisionKind.QUARANTINE_FAMILY_FLOOD for decision in report.decisions)


def test_admission_refuses_metadata_budget_exhaustion():
    requests = (req(1, "fam-a", metadata_cost=5), req(2, "fam-b", metadata_cost=5), req(3, "fam-c", metadata_cost=5))
    report = decide_admission_batch(requests, budget=budget(max_metadata=8, max_streams=5, reserve_for_critical=0), keypair=kp(88), garden_node_id=ident(88).node_id, now=NOW + 1)
    assert report.accepted_metadata <= 8
    assert any(decision.reason and decision.reason.value == "over_metadata_budget" for decision in report.refused)


def test_admission_drops_expired_request_without_receipt():
    report = decide_admission_batch((req(1, "fam-a", issued_at=NOW - 100, expires_at=NOW - 10),), budget=budget(), keypair=kp(88), garden_node_id=ident(88).node_id, now=NOW + 1)
    decision = report.decisions[0]
    assert decision.kind is AdmissionDecisionKind.DROP_INVALID
    assert decision.receipt is None


def test_admission_quarantines_replayed_request_from_state():
    request = req(1, "fam-a")
    state = AdmissionState(seen_request_digests=frozenset({request.digest}))
    report = decide_admission_batch((request,), budget=budget(), keypair=kp(88), garden_node_id=ident(88).node_id, now=NOW + 1, state=state)
    decision = report.decisions[0]
    assert decision.kind is AdmissionDecisionKind.QUARANTINE_REPLAY
    assert decision.receipt and decision.receipt.verify(now=NOW + 2)


def test_admission_quarantines_duplicate_request_in_batch():
    request = req(1, "fam-a")
    report = decide_admission_batch((request, request), budget=budget(max_streams=5), keypair=kp(88), garden_node_id=ident(88).node_id, now=NOW + 1)
    assert [decision.kind for decision in report.decisions].count(AdmissionDecisionKind.QUARANTINE_REPLAY) == 1


# ---------------- audit/refactor ----------------


def test_namespacefold_audit_passes_current_cube():
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    report = audit_namespace_fold(root, revision="rev0023")
    assert report.status == "pass", report.findings
    assert report.warning_count == 0
