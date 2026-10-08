from pathlib import Path

from i2p_dht_lab.admissionwall import AdmissionBudget, AdmissionDecisionKind, AdmissionReceipt, AdmissionRefusalReason
from i2p_dht_lab.capability import CapabilityGrant, CapabilityKind, CapabilityRevocation, RevocationSet
from i2p_dht_lab.capgate import CapabilityDispatchPolicy, evaluate_capability_dispatch
from i2p_dht_lab.foldspine import audit_fold_spine
from i2p_dht_lab.fuzzwire import deterministic_fuzz_cases
from i2p_dht_lab.generatorfuzz import GeneratedCorpusDecisionKind, run_generated_fuzz_corpus
from i2p_dht_lab.identity import DhtKeypair, NodeIdentity
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.journallane import (
    JournalReplayDecisionKind,
    PersistJournalEntry,
    ZERO_ENTRY_DIGEST,
    replay_persist_journal,
)
from i2p_dht_lab.namespaceregistry import NamespacePolicy, NamespaceRegistry, memory_from_policies
from i2p_dht_lab.persistlane import PersistRecord, PersistRecordKind, PersistSnapshot, ZERO_DIGEST
from i2p_dht_lab.queueforge import QueuePolicy, QueueWorkKind
from i2p_dht_lab.refusaljoin import RefusalJoinDecisionKind, assess_refusal_join
from i2p_dht_lab.refusalloop import RefusalLoopDecisionKind, RefusalLoopPolicy, RefusalWindow, assess_refusal_loop
from i2p_dht_lab.schedjoin import JoinedSchedulePolicy, JoinedWorkCandidate, plan_joined_schedule
from i2p_dht_lab.validatorwall import PayloadEnvelope, PayloadRole
from i2p_dht_lab.wirecanon import WireFrame, WireMessageKind
from i2p_dht_lab.workmeter import WorkEvent, WorkEventKind, WorkMeterPolicy


def kp(n: int) -> DhtKeypair:
    return DhtKeypair.from_seed(bytes([n]) * 32)


def ident(n: int) -> NodeIdentity:
    return NodeIdentity.create(destination=f"rev0028-node-{n}.b32.i2p", keypair=kp(n))


def digest(label: str) -> bytes:
    return sha256(label.encode("utf-8"))


def rec(kind: PersistRecordKind, label: str, *, seq: int = 1, fam: str = "fam-A", path: str = "path-A", now: int = 1_000) -> PersistRecord:
    return PersistRecord(
        kind=kind,
        scope_id=digest("scope"),
        subject_digest=digest(label),
        value_digest=digest(f"{label}-value-{seq}"),
        sequence=seq,
        source_family=fam,
        path_family=path,
        issued_at=now,
        expires_at=now + 10_000,
    )


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
    body = f"rev0028 mutable body {request_label}".encode("utf-8")
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


def receipt(label: str, *, garden: DhtKeypair, node_id: bytes, now: int) -> AdmissionReceipt:
    return AdmissionReceipt.create(
        keypair=garden,
        garden_node_id=node_id,
        request_digest=digest(label),
        decision=AdmissionDecisionKind.REFUSE_USEFULLY,
        reason=AdmissionRefusalReason.OVER_BYTE_BUDGET,
        issued_at=now,
        ttl=600,
        retry_after_seconds=60,
    )


def work_event(kind: WorkEventKind, label: str, *, garden: DhtKeypair, fam: str, path: str, now: int, rcpt: AdmissionReceipt | None = None) -> WorkEvent:
    return WorkEvent.create(
        garden=garden,
        event_kind=kind,
        scope_id=digest("refusal-scope"),
        subject_digest=digest(label),
        source_family=fam,
        path_family=path,
        unit_cost=1,
        issued_at=now,
        ttl=600,
        receipt=rcpt,
    )


def test_journallane_replays_linked_snapshots_and_preserves_latest() -> None:
    now = 100_000
    key = kp(1)
    first = PersistSnapshot.create(keypair=key, sequence=1, prev_snapshot_digest=ZERO_DIGEST, records=(rec(PersistRecordKind.MUTABLE_HEAD, "head-1", seq=1, now=now),), issued_at=now)
    entry1 = PersistJournalEntry.create_snapshot(keypair=key, entry_sequence=1, prev_entry_digest=ZERO_ENTRY_DIGEST, snapshot=first, issued_at=now)
    second = PersistSnapshot.create(keypair=key, sequence=2, prev_snapshot_digest=first.snapshot_digest, records=(rec(PersistRecordKind.MUTABLE_HEAD, "head-2", seq=2, now=now + 1),), issued_at=now + 1)
    entry2 = PersistJournalEntry.create_snapshot(keypair=key, entry_sequence=2, prev_entry_digest=entry1.entry_digest, snapshot=second, issued_at=now + 1)
    report = replay_persist_journal((entry1.to_bytes(), entry2.to_bytes()), previous_snapshot=None, now=now + 2)
    assert report.decision_kind is JournalReplayDecisionKind.ACCEPT_REPLAYED_PREFIX
    assert report.accept
    assert report.accepted_entry_count == 2
    assert report.last_snapshot is not None
    assert report.last_snapshot.snapshot_digest == second.snapshot_digest


def test_journallane_accepts_trailing_crash_cut_prefix_only() -> None:
    now = 110_000
    key = kp(2)
    first = PersistSnapshot.create(keypair=key, sequence=1, prev_snapshot_digest=ZERO_DIGEST, records=(rec(PersistRecordKind.PROVIDER_TRUE, "provider", now=now),), issued_at=now)
    entry1 = PersistJournalEntry.create_snapshot(keypair=key, entry_sequence=1, prev_entry_digest=ZERO_ENTRY_DIGEST, snapshot=first, issued_at=now)
    report = replay_persist_journal((entry1.to_bytes(), b"d7:partial"), previous_snapshot=None, now=now + 1)
    assert report.decision_kind is JournalReplayDecisionKind.ACCEPT_CRASH_CUT_PREFIX
    assert report.accept
    assert report.accepted_entry_count == 1
    assert report.crash_cut_count == 1


def test_journallane_quarantines_middle_corruption_prev_mismatch_and_hard_negative_drop() -> None:
    now = 120_000
    key = kp(3)
    tomb = rec(PersistRecordKind.TOMBSTONE, "gone", seq=5, now=now)
    first = PersistSnapshot.create(keypair=key, sequence=1, prev_snapshot_digest=ZERO_DIGEST, records=(tomb,), issued_at=now)
    entry1 = PersistJournalEntry.create_snapshot(keypair=key, entry_sequence=1, prev_entry_digest=ZERO_ENTRY_DIGEST, snapshot=first, issued_at=now)
    convenient = PersistSnapshot.create(keypair=key, sequence=2, prev_snapshot_digest=first.snapshot_digest, records=(rec(PersistRecordKind.PROVIDER_TRUE, "resurrected", seq=6, now=now + 1),), issued_at=now + 1)
    drop_entry = PersistJournalEntry.create_snapshot(keypair=key, entry_sequence=2, prev_entry_digest=entry1.entry_digest, snapshot=convenient, issued_at=now + 1)
    middle_bad = replay_persist_journal((entry1.to_bytes(), b"not-bencode", drop_entry.to_bytes()), previous_snapshot=None, now=now + 2)
    assert middle_bad.decision_kind is JournalReplayDecisionKind.QUARANTINE_ENTRY_PARSE_ERROR
    wrong_prev = PersistJournalEntry.create_snapshot(keypair=key, entry_sequence=2, prev_entry_digest=digest("wrong-entry-prev"), snapshot=convenient, issued_at=now + 1)
    assert replay_persist_journal((entry1.to_bytes(), wrong_prev.to_bytes()), previous_snapshot=None, now=now + 2).decision_kind is JournalReplayDecisionKind.QUARANTINE_ENTRY_PREV_MISMATCH
    dropped = replay_persist_journal((entry1.to_bytes(), drop_entry.to_bytes()), previous_snapshot=None, now=now + 2)
    assert dropped.decision_kind is JournalReplayDecisionKind.QUARANTINE_SNAPSHOT_RELOAD
    assert dropped.quarantined


def test_generatorfuzz_expands_seed_cases_and_pins_rejection_families() -> None:
    now = 130_000
    seed = deterministic_fuzz_cases(keypair=kp(8), node_id=digest("node-8"), now=now)
    report = run_generated_fuzz_corpus(seed)
    assert report.decision_kind is GeneratedCorpusDecisionKind.ACCEPT_COVERAGE
    assert report.accept
    assert report.generated_count >= 8
    assert report.fuzz_report.passed
    assert {"payload", "digest"}.issubset(set(report.rejection_families))


def test_refusaljoin_holds_bulk_but_allows_protected_after_bad_history() -> None:
    now = 140_000
    garden = kp(12)
    node_id = digest("garden-node-12")
    windows = tuple(
        RefusalWindow(idx, (work_event(WorkEventKind.REFUSED_USEFULLY, f"refuse-{idx}", garden=garden, fam=f"fam-{idx}", path=f"path-{idx}", now=now + idx, rcpt=receipt(f"r-{idx}", garden=garden, node_id=node_id, now=now + idx)),))
        for idx in range(1, 4)
    )
    history = assess_refusal_loop(windows, now=now + 10, policy=RefusalLoopPolicy(max_consecutive_refusal_heavy=2, work_meter_policy=WorkMeterPolicy(min_source_families=1)))
    assert history.decision_kind is RefusalLoopDecisionKind.QUARANTINE_REFUSAL_ONLY_LOOP
    schedule = plan_joined_schedule(
        (JoinedWorkCandidate("head", dispatch_report(now, actor_n=1, family="fam-control"), QueueWorkKind.HEAD_WATCH, deadline=now + 60),),
        queue_policy=QueuePolicy(max_streams=1, reserve_for_survivors=0),
        garden_keypair=kp(99),
        garden_node_id=ident(99).node_id,
        now=now + 2,
    )
    joined = assess_refusal_join(schedule, history)
    assert joined.decision_kind is RefusalJoinDecisionKind.HOLD_BULK_ALLOW_PROTECTED
    assert joined.accept
    assert joined.allow_protected
    assert not joined.allow_bulk


def test_refusaljoin_quarantines_bad_history_when_bulk_starts() -> None:
    now = 150_000
    garden = kp(13)
    node_id = digest("garden-node-13")
    history = assess_refusal_loop(
        tuple(RefusalWindow(idx, (work_event(WorkEventKind.REFUSED_USEFULLY, f"refuse-{idx}", garden=garden, fam=f"fam-{idx}", path=f"path-{idx}", now=now + idx, rcpt=receipt(f"rr-{idx}", garden=garden, node_id=node_id, now=now + idx)),)) for idx in range(1, 4)),
        now=now + 10,
        policy=RefusalLoopPolicy(max_consecutive_refusal_heavy=2, work_meter_policy=WorkMeterPolicy(min_source_families=1)),
    )
    schedule = plan_joined_schedule(
        (JoinedWorkCandidate("bulk", dispatch_report(now, actor_n=2, family="fam-bulk"), QueueWorkKind.PROVIDER_BULK, deadline=now + 60),),
        queue_policy=QueuePolicy(max_streams=1, reserve_for_survivors=0),
        garden_keypair=kp(99),
        garden_node_id=ident(99).node_id,
        now=now + 2,
    )
    joined = assess_refusal_join(schedule, history)
    assert joined.decision_kind is RefusalJoinDecisionKind.QUARANTINE_REFUSAL_LAUNDERING
    assert joined.quarantined
    assert not joined.allow_bulk


def test_foldspine_pins_current_revision_surface_and_previous_fold() -> None:
    root = Path(__file__).resolve().parents[1]
    report = audit_fold_spine(root, revision="rev0028")
    assert report.status == "pass"
    assert report.error_count == 0
