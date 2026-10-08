from dataclasses import replace

from i2p_dht_lab.admissionwall import AdmissionPriority, AdmissionRequest
from i2p_dht_lab.identity import DhtKeypair, NodeIdentity
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.namespaceregistry import NamespacePolicy
from i2p_dht_lab.policyepoch import (
    PolicyEpochDecisionKind,
    PolicyEpochHead,
    PolicyEpochMemory,
    PolicyEpochObservation,
    PolicyEpochPolicy,
    assess_policy_epoch,
    memory_from_policy_epoch_heads,
)
from i2p_dht_lab.policyfold import audit_policy_fold
from i2p_dht_lab.queueforge import (
    QueueDecisionKind,
    QueuePolicy,
    QueueWorkItem,
    QueueWorkKind,
    forge_admission_queue,
)
from i2p_dht_lab.rangemerkle import (
    RangeMerkleDecisionKind,
    RangeMerkleLeaf,
    RangeMerkleLeafKind,
    RangeMerklePolicy,
    RangeMerkleSummary,
    build_range_merkle_tree,
    plan_range_merkle_repair,
)
from i2p_dht_lab.validatorwall import PayloadRole
from i2p_dht_lab.wirecanon import WireMessageKind

NOW = 1_765_310_000


def kp(n: int) -> DhtKeypair:
    return DhtKeypair.from_seed(bytes([n % 256]) * 32)


def ident(n: int) -> NodeIdentity:
    return NodeIdentity.create(destination=f"rev0024-{n}.b32.i2p", keypair=kp(n))


def digest(label: str) -> bytes:
    return sha256(label.encode("utf-8"))


def namespace_policy(*, sequence: int = 1, max_body_bytes: int = 1000, ttl: int = 600) -> NamespacePolicy:
    return NamespacePolicy.create(
        authority=kp(90),
        namespace="i2p-dht-control",
        sequence=sequence,
        issued_at=NOW - 5,
        ttl=ttl,
        allowed_roles_by_kind={
            WireMessageKind.EPOCH_HEAD: frozenset({PayloadRole.MUTABLE_HEAD}),
            WireMessageKind.FIND_PROVIDER: frozenset({PayloadRole.PROVIDER_CLAIM}),
        },
        max_body_bytes=max_body_bytes,
        max_ttl_seconds=300,
        required_flags_by_role={PayloadRole.MUTABLE_HEAD: frozenset({"mutable-head"})},
    )


def policy_head(policy: NamespacePolicy, *, epoch: int, prev: bytes = b"", ttl: int = 300) -> PolicyEpochHead:
    return PolicyEpochHead.create(authority=kp(90), namespace=policy.namespace, policy_digest=policy.policy_digest, epoch=epoch, previous_head_digest=prev, issued_at=NOW, ttl=ttl)


def obs(head: PolicyEpochHead, family: str) -> PolicyEpochObservation:
    return PolicyEpochObservation(head=head, source_family=family)


# ---------------- policy epoch heads ----------------


def test_policy_epoch_accepts_diverse_genesis_head():
    policy = namespace_policy()
    head = policy_head(policy, epoch=0)
    report = assess_policy_epoch((obs(head, "fam-a"), obs(head, "fam-b")), expected_policy=policy, memory=PolicyEpochMemory.empty(), now=NOW + 1)
    assert report.decision.kind is PolicyEpochDecisionKind.ACCEPT_GENESIS
    assert report.decision.accept
    assert report.family_counts == {"fam-a": 1, "fam-b": 1}


def test_policy_epoch_accepts_advance_when_previous_digest_matches_memory():
    policy = namespace_policy(sequence=1)
    genesis = policy_head(policy, epoch=0)
    newer_policy = namespace_policy(sequence=2)
    advance = policy_head(newer_policy, epoch=1, prev=genesis.head_digest)
    memory = memory_from_policy_epoch_heads((genesis,))
    report = assess_policy_epoch((obs(advance, "fam-a"), obs(advance, "fam-b")), expected_policy=newer_policy, memory=memory, now=NOW + 1)
    assert report.decision.kind is PolicyEpochDecisionKind.ACCEPT_ADVANCE
    assert report.chosen_head == advance


def test_policy_epoch_rejects_policy_digest_mismatch():
    policy = namespace_policy()
    wrong_policy = namespace_policy(sequence=2)
    head = PolicyEpochHead.create(authority=kp(90), namespace=policy.namespace, policy_digest=digest("wrong-policy"), epoch=0, previous_head_digest=b"", issued_at=NOW, ttl=300)
    report = assess_policy_epoch((obs(head, "fam-a"), obs(head, "fam-b")), expected_policy=wrong_policy, memory=PolicyEpochMemory.empty(), now=NOW + 1)
    assert report.decision.kind is PolicyEpochDecisionKind.REJECT_POLICY_DIGEST_MISMATCH


def test_policy_epoch_rejects_rollback_against_memory():
    policy = namespace_policy()
    old = policy_head(policy, epoch=0)
    latest = policy_head(policy, epoch=2, prev=old.head_digest)
    memory = memory_from_policy_epoch_heads((latest,))
    report = assess_policy_epoch((obs(old, "fam-a"), obs(old, "fam-b")), expected_policy=policy, memory=memory, now=NOW + 1)
    assert report.decision.kind is PolicyEpochDecisionKind.REJECT_ROLLBACK


def test_policy_epoch_quarantines_same_epoch_fork():
    policy = namespace_policy()
    fork_a = policy_head(policy, epoch=1, prev=digest("prev"))
    fork_b = PolicyEpochHead.create(authority=kp(90), namespace=policy.namespace, policy_digest=policy.policy_digest, epoch=1, previous_head_digest=digest("other-prev"), issued_at=NOW, ttl=300)
    report = assess_policy_epoch((obs(fork_a, "fam-a"), obs(fork_b, "fam-b")), expected_policy=policy, memory=PolicyEpochMemory.empty(), now=NOW + 1)
    assert report.decision.kind is PolicyEpochDecisionKind.QUARANTINE_SAME_EPOCH_FORK
    assert report.quarantined


def test_policy_epoch_quarantines_previous_link_mismatch():
    policy = namespace_policy(sequence=1)
    genesis = policy_head(policy, epoch=0)
    newer_policy = namespace_policy(sequence=2)
    bad = policy_head(newer_policy, epoch=1, prev=digest("not-genesis"))
    report = assess_policy_epoch((obs(bad, "fam-a"), obs(bad, "fam-b")), expected_policy=newer_policy, memory=memory_from_policy_epoch_heads((genesis,)), now=NOW + 1)
    assert report.decision.kind is PolicyEpochDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH


def test_policy_epoch_requires_family_diversity():
    policy = namespace_policy()
    head = policy_head(policy, epoch=0)
    report = assess_policy_epoch((obs(head, "fam-a"), obs(head, "fam-a")), expected_policy=policy, memory=PolicyEpochMemory.empty(), now=NOW + 1)
    assert report.decision.kind is PolicyEpochDecisionKind.CONTINUE_NEED_FAMILY_DIVERSITY


def test_policy_epoch_accepts_with_watch_when_previous_history_missing():
    policy = namespace_policy()
    head = policy_head(policy, epoch=3, prev=digest("unknown-previous"))
    report = assess_policy_epoch((obs(head, "fam-a"), obs(head, "fam-b")), expected_policy=policy, memory=PolicyEpochMemory.empty(), now=NOW + 1, policy=PolicyEpochPolicy(allow_watch_without_memory=True))
    assert report.decision.kind is PolicyEpochDecisionKind.ACCEPT_WITH_WATCH
    assert report.decision.accept


# ---------------- range Merkle repair ----------------


def leaf(name: str, *, kind: RangeMerkleLeafKind = RangeMerkleLeafKind.PROVIDER_RECORD, seq: int = 1, tombstone: bool = False) -> RangeMerkleLeaf:
    return RangeMerkleLeaf(key_digest=digest("key-" + name), object_digest=digest("obj-" + name), kind=kind, sequence=seq, tombstone=tombstone)


def summary(n: int, family: str, tree, *, seq: int = 1, ttl: int = 300) -> RangeMerkleSummary:
    return RangeMerkleSummary.create(keypair=kp(n), source_node_id=ident(n).node_id, source_family=family, region_prefix=2, region_bits=4, sequence=seq, tree=tree, issued_at=NOW, ttl=ttl)


def test_range_merkle_inclusion_proof_verifies_and_tamper_fails():
    tree = build_range_merkle_tree((leaf("a"), leaf("b"), leaf("c")))
    proof = tree.proof_for_leaf(tree.leaves[1])
    assert proof.verify(tree.root_digest)
    tampered = replace(proof, leaf=replace(proof.leaf, object_digest=digest("evil")))
    assert not tampered.verify(tree.root_digest)


def test_range_merkle_accepts_in_sync_diverse_summaries():
    tree = build_range_merkle_tree((leaf("a"), leaf("b")))
    local = summary(1, "local", tree, seq=1)
    report = plan_range_merkle_repair(local, (summary(2, "fam-a", tree, seq=1), summary(3, "fam-b", tree, seq=1)), now=NOW + 1)
    assert report.decision is RangeMerkleDecisionKind.ACCEPT_IN_SYNC
    assert report.accept


def test_range_merkle_requests_child_repair_for_newer_root_without_proofs():
    local_tree = build_range_merkle_tree((leaf("a"),))
    remote_tree = build_range_merkle_tree((leaf("a"), leaf("b")))
    report = plan_range_merkle_repair(summary(1, "local", local_tree, seq=1), (summary(2, "fam-a", remote_tree, seq=2), summary(3, "fam-b", remote_tree, seq=2)), now=NOW + 1)
    assert report.decision is RangeMerkleDecisionKind.REQUEST_CHILD_RANGE_REPAIR


def test_range_merkle_accepts_verified_exact_repair_proofs():
    local_tree = build_range_merkle_tree((leaf("a"),))
    remote_tree = build_range_merkle_tree((leaf("a"), leaf("b")))
    proof = remote_tree.proof_for_leaf(leaf("b"))
    report = plan_range_merkle_repair(summary(1, "local", local_tree, seq=1), (summary(2, "fam-a", remote_tree, seq=2), summary(3, "fam-b", remote_tree, seq=2)), proofs=(proof,), now=NOW + 1)
    assert report.decision is RangeMerkleDecisionKind.ACCEPT_VERIFIED_EXACT_REPAIR
    assert report.accept


def test_range_merkle_tombstone_proofs_are_repaired_first():
    local_tree = build_range_merkle_tree((leaf("a"),))
    tomb = leaf("delete-a", kind=RangeMerkleLeafKind.TOMBSTONE, seq=3, tombstone=True)
    remote_tree = build_range_merkle_tree((leaf("a"), tomb))
    proof = remote_tree.proof_for_leaf(tomb)
    report = plan_range_merkle_repair(summary(1, "local", local_tree, seq=1), (summary(2, "fam-a", remote_tree, seq=2), summary(3, "fam-b", remote_tree, seq=2)), proofs=(proof,), now=NOW + 1)
    assert report.decision is RangeMerkleDecisionKind.REQUEST_TOMBSTONE_FIRST
    assert not report.accept


def test_range_merkle_quarantines_same_sequence_root_fork():
    tree_a = build_range_merkle_tree((leaf("a"),))
    tree_b = build_range_merkle_tree((leaf("b"),))
    report = plan_range_merkle_repair(None, (summary(2, "fam-a", tree_a, seq=5), summary(3, "fam-b", tree_b, seq=5)), now=NOW + 1)
    assert report.decision is RangeMerkleDecisionKind.QUARANTINE_ROOT_FORK


def test_range_merkle_rejects_bad_proof_against_chosen_root():
    local_tree = build_range_merkle_tree((leaf("a"),))
    remote_tree = build_range_merkle_tree((leaf("a"), leaf("b")))
    wrong_tree = build_range_merkle_tree((leaf("x"), leaf("y")))
    wrong_proof = wrong_tree.proof_for_leaf(wrong_tree.leaves[0])
    report = plan_range_merkle_repair(summary(1, "local", local_tree, seq=1), (summary(2, "fam-a", remote_tree, seq=2), summary(3, "fam-b", remote_tree, seq=2)), proofs=(wrong_proof,), now=NOW + 1)
    assert report.decision is RangeMerkleDecisionKind.REJECT_BAD_PROOF


def test_range_merkle_requires_family_diversity():
    tree = build_range_merkle_tree((leaf("a"), leaf("b")))
    report = plan_range_merkle_repair(None, (summary(2, "fam-a", tree, seq=2), summary(3, "fam-a", tree, seq=2)), now=NOW + 1)
    assert report.decision is RangeMerkleDecisionKind.CONTINUE_NEED_FAMILY_DIVERSITY


# ---------------- queue forge ----------------


def req(n: int, family: str, *, priority: AdmissionPriority = AdmissionPriority.NORMAL, issued_at: int = NOW, expires_at: int = NOW + 300) -> AdmissionRequest:
    return AdmissionRequest(
        frame_digest=digest(f"frame-{n}"),
        sender_node_id=ident(n).node_id,
        source_family=family,
        namespace="i2p-dht-control",
        message_kind=WireMessageKind.EPOCH_HEAD,
        role=PayloadRole.MUTABLE_HEAD,
        priority=priority,
        stream_cost=1,
        byte_cost=10,
        metadata_cost=1,
        issued_at=issued_at,
        expires_at=expires_at,
    )


def item(n: int, family: str, work_kind: QueueWorkKind, *, deadline: int = NOW + 60, latency_ms: int = 1000, priority: AdmissionPriority = AdmissionPriority.NORMAL) -> QueueWorkItem:
    return QueueWorkItem(request=req(n, family, priority=priority), work_kind=work_kind, enqueue_time=NOW, deadline=deadline, estimated_latency_ms=latency_ms)


def test_queueforge_survivor_work_survives_bulk_flood():
    bulk = tuple(item(n, "fam-bulk", QueueWorkKind.PROVIDER_BULK) for n in range(1, 6))
    head = item(10, "fam-head", QueueWorkKind.HEAD_WATCH)
    witness = item(11, "fam-witness", QueueWorkKind.WITNESS_QUERY)
    plan = forge_admission_queue(bulk + (head, witness), policy=QueuePolicy(max_streams=2, max_per_family=2, reserve_for_survivors=1), keypair=kp(70), garden_node_id=ident(70).node_id, now=NOW + 1)
    started_kinds = {decision.item.work_kind for decision in plan.started}
    assert QueueWorkKind.HEAD_WATCH in started_kinds
    assert QueueWorkKind.WITNESS_QUERY in started_kinds
    assert QueueWorkKind.PROVIDER_BULK not in started_kinds


def test_queueforge_family_flood_quarantines_after_quota():
    items = tuple(item(n, "fam-a", QueueWorkKind.STORE_REPAIR) for n in range(1, 5))
    plan = forge_admission_queue(items, policy=QueuePolicy(max_streams=5, max_per_family=2, reserve_for_survivors=0), keypair=kp(70), garden_node_id=ident(70).node_id, now=NOW + 1)
    assert sum(1 for decision in plan.decisions if decision.kind is QueueDecisionKind.START_NOW) == 2
    assert len(plan.quarantined) == 2


def test_queueforge_drops_work_that_cannot_meet_latency_deadline():
    slow = item(1, "fam-a", QueueWorkKind.HEAD_WATCH, deadline=NOW + 1, latency_ms=5000)
    plan = forge_admission_queue((slow,), policy=QueuePolicy(max_streams=1), keypair=kp(70), garden_node_id=ident(70).node_id, now=NOW + 1)
    assert plan.decisions[0].kind is QueueDecisionKind.DROP_EXPIRED
    later_slow = item(2, "fam-b", QueueWorkKind.HEAD_WATCH, deadline=NOW + 2, latency_ms=5000)
    plan2 = forge_admission_queue((later_slow,), policy=QueuePolicy(max_streams=1), keypair=kp(70), garden_node_id=ident(70).node_id, now=NOW + 1)
    assert plan2.decisions[0].kind is QueueDecisionKind.DROP_LATENCY_DEADLINE


def test_queueforge_bulk_defer_creates_verifiable_useful_refusal():
    critical = item(1, "fam-a", QueueWorkKind.SEED_GATE)
    bulk = item(2, "fam-b", QueueWorkKind.PROVIDER_BULK)
    plan = forge_admission_queue((bulk, critical), policy=QueuePolicy(max_streams=2, reserve_for_survivors=1), keypair=kp(70), garden_node_id=ident(70).node_id, now=NOW + 1)
    refused = [decision for decision in plan.decisions if decision.kind is QueueDecisionKind.DEFER_FOR_RESERVE]
    assert refused
    assert refused[0].receipt is not None
    assert refused[0].receipt.verify(now=NOW + 2, expected_public_key=kp(70).public_key_bytes)


def test_queueforge_no_stream_capacity_refuses_usefully():
    a = item(1, "fam-a", QueueWorkKind.HEAD_WATCH)
    b = item(2, "fam-b", QueueWorkKind.WITNESS_QUERY)
    plan = forge_admission_queue((a, b), policy=QueuePolicy(max_streams=1, reserve_for_survivors=0), keypair=kp(70), garden_node_id=ident(70).node_id, now=NOW + 1)
    assert any(decision.kind is QueueDecisionKind.REFUSE_USEFULLY for decision in plan.decisions)
    assert all(decision.receipt.verify(now=NOW + 2, expected_public_key=kp(70).public_key_bytes) for decision in plan.refused)


# ---------------- policy fold audit ----------------


def test_policyfold_current_surfaces_are_visible():
    report = audit_policy_fold(".", revision="rev0024")
    assert report.status == "pass"
    assert report.error_count == 0
