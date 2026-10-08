from dataclasses import replace
from pathlib import Path

from i2p_dht_lab.generatorfuzz import GeneratedFuzzDecisionKind, generated_fuzz_cases, run_generated_fuzz_corpus
from i2p_dht_lab.identity import DhtKeypair, NodeIdentity
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.journallane import (
    JournalDropTarget,
    JournalEntry,
    JournalOperation,
    JournalReplayDecisionKind,
    decode_and_replay_journal,
    replay_journal_entries,
)
from i2p_dht_lab.misbindguard import HandlerIntent, HandlerIntentKind, MisbindDecisionKind, MisbindGuardPolicy, guard_handler_intent
from i2p_dht_lab.persistlane import PersistRecord, PersistRecordKind, PersistSnapshot, ZERO_DIGEST
from i2p_dht_lab.validatorwall import PayloadEnvelope, PayloadRole, validate_payload_wall
from i2p_dht_lab.wirecanon import WireFrame, WireMessageKind
from i2p_dht_lab.foldspine import audit_fold_spine


def kp(n: int) -> DhtKeypair:
    return DhtKeypair.from_seed(bytes([n]) * 32)


def ident(n: int) -> NodeIdentity:
    return NodeIdentity.create(destination=f"rev0028-{n}.b32.i2p", keypair=kp(n))


def digest(label: str) -> bytes:
    return sha256(label.encode("utf-8"))


def record(kind: PersistRecordKind, label: str, *, sequence: int = 1, source: str = "src-A", path: str = "path-A") -> PersistRecord:
    return PersistRecord(
        kind=kind,
        scope_id=digest("scope:" + label),
        subject_digest=digest("subject:" + label),
        value_digest=digest("value:" + label + f":{sequence}"),
        sequence=sequence,
        source_family=source,
        path_family=path,
        issued_at=1000,
        expires_at=10_000,
        byte_cost=128,
    )


def base_snapshot(*records: PersistRecord) -> PersistSnapshot:
    return PersistSnapshot.create(keypair=kp(1), sequence=10, prev_snapshot_digest=ZERO_DIGEST, records=records, issued_at=1000, ttl=20_000)


def test_journal_accepts_linked_replay_and_preserves_hard_negative() -> None:
    tomb = record(PersistRecordKind.TOMBSTONE, "dead", sequence=1)
    snap = base_snapshot(tomb)
    provider = record(PersistRecordKind.PROVIDER_TRUE, "alive", sequence=11, source="src-B", path="path-B")
    e1 = JournalEntry.create_put(keypair=kp(1), sequence=11, prev_entry_digest=snap.snapshot_digest, base_snapshot_digest=snap.snapshot_digest, record=provider, issued_at=1100)
    e2 = JournalEntry.create_checkpoint(keypair=kp(1), sequence=12, prev_entry_digest=e1.entry_digest, base_snapshot_digest=snap.snapshot_digest, issued_at=1110)

    report = replay_journal_entries(base_snapshot=snap, entries=(e1, e2), now=1200)

    assert report.decision_kind is JournalReplayDecisionKind.ACCEPT_REPLAY
    assert report.accept
    assert tomb.record_digest in {item.record_digest for item in report.replayed_records}
    assert provider.record_digest in {item.record_digest for item in report.replayed_records}
    assert report.hard_negative_count == 1


def test_journal_accepts_parse_safe_prefix_after_crash_cut() -> None:
    snap = base_snapshot()
    provider = record(PersistRecordKind.PROVIDER_TRUE, "prefix", sequence=11)
    e1 = JournalEntry.create_put(keypair=kp(1), sequence=11, prev_entry_digest=snap.snapshot_digest, base_snapshot_digest=snap.snapshot_digest, record=provider, issued_at=1100)

    report = decode_and_replay_journal((e1.to_bytes(), b"d1:broken"), base_snapshot=snap, now=1200)

    assert report.decision_kind is JournalReplayDecisionKind.ACCEPT_PREFIX_AFTER_CRASH_CUT
    assert report.accept
    assert report.accepted_entries == (e1.entry_digest,)
    assert provider.record_digest in {item.record_digest for item in report.replayed_records}


def test_journal_quarantines_prev_mismatch_and_hard_negative_drop() -> None:
    tomb = record(PersistRecordKind.PROVIDER_FALSE, "liar", sequence=3)
    snap = base_snapshot(tomb)
    provider = record(PersistRecordKind.PROVIDER_TRUE, "other", sequence=11)
    bad_prev = JournalEntry.create_put(keypair=kp(1), sequence=11, prev_entry_digest=digest("wrong-prev"), base_snapshot_digest=snap.snapshot_digest, record=provider, issued_at=1100)
    prev_report = replay_journal_entries(base_snapshot=snap, entries=(bad_prev,), now=1200)
    assert prev_report.decision_kind is JournalReplayDecisionKind.QUARANTINE_PREV_MISMATCH
    assert not prev_report.accept

    drop = JournalEntry.create_drop(
        keypair=kp(1),
        sequence=11,
        prev_entry_digest=snap.snapshot_digest,
        base_snapshot_digest=snap.snapshot_digest,
        drop_target=JournalDropTarget(tomb.kind, tomb.scope_id, tomb.subject_digest),
        issued_at=1100,
    )
    drop_report = replay_journal_entries(base_snapshot=snap, entries=(drop,), now=1200)
    assert drop_report.decision_kind is JournalReplayDecisionKind.QUARANTINE_HARD_NEGATIVE_DROPPED
    assert not drop_report.accept


def test_journal_quarantines_bad_signature_and_same_sequence_fork() -> None:
    snap = base_snapshot()
    rec_a = record(PersistRecordKind.PROVIDER_TRUE, "a", sequence=11)
    rec_b = record(PersistRecordKind.PROVIDER_TRUE, "b", sequence=11)
    e1 = JournalEntry.create_put(keypair=kp(1), sequence=11, prev_entry_digest=snap.snapshot_digest, base_snapshot_digest=snap.snapshot_digest, record=rec_a, issued_at=1100)
    tampered = replace(e1, signature=b"0" * 64)
    bad_sig = replay_journal_entries(base_snapshot=snap, entries=(tampered,), now=1200)
    assert bad_sig.decision_kind is JournalReplayDecisionKind.QUARANTINE_BAD_SIGNATURE

    e2 = JournalEntry.create_put(keypair=kp(1), sequence=11, prev_entry_digest=e1.entry_digest, base_snapshot_digest=snap.snapshot_digest, record=rec_b, issued_at=1101)
    fork = replay_journal_entries(base_snapshot=snap, entries=(e1, e2), now=1200)
    assert fork.decision_kind in {JournalReplayDecisionKind.QUARANTINE_ROLLBACK, JournalReplayDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK}
    assert not fork.accept


def test_generated_fuzz_corpus_rejects_mutated_cases() -> None:
    node = ident(7)
    cases = generated_fuzz_cases(keypair=kp(7), node_id=node.node_id, now=2000)
    report = run_generated_fuzz_corpus(cases)
    assert report.decision_kind is GeneratedFuzzDecisionKind.ACCEPT_CORPUS
    assert report.accept
    assert report.case_count >= 8
    assert report.failed_case_labels == ()


def build_validator_report(*, role: PayloadRole = PayloadRole.MUTABLE_HEAD, kind: WireMessageKind = WireMessageKind.EPOCH_HEAD):
    node = ident(9)
    body = b"mutable head body"
    scope = digest("misbind-scope")
    envelope = PayloadEnvelope.create(namespace="i2p-dht-control", role=role, scope_id=scope, body=body, issued_at=3000, ttl=300)
    payload = envelope.to_bytes()
    frame = WireFrame.create(keypair=kp(9), sender_node_id=node.node_id, message_kind=kind, request_id=digest("misbind-request"), payload=payload, issued_at=3000, ttl=300, flags=("mutable-head",))
    report = validate_payload_wall(frame, payload=payload, body=body, now=3001)
    return node, body, envelope, frame, report


def test_misbindguard_accepts_fully_bound_handler_intent() -> None:
    node, _body, envelope, frame, validator = build_validator_report()
    intent = HandlerIntent(
        kind=HandlerIntentKind.MUTABLE_HEAD_WRITE,
        namespace=envelope.namespace,
        scope_id=envelope.scope_id,
        actor_public_key=node.public_key,
        request_id=frame.request_id,
        body_digest=envelope.body_digest,
    )
    report = guard_handler_intent(intent=intent, validator=validator, policy=MisbindGuardPolicy(require_capgate_acceptance=False))
    assert report.decision_kind is MisbindDecisionKind.ACCEPT_BOUND_INTENT
    assert report.accept


def test_misbindguard_rejects_kind_role_and_actor_or_request_mismatch() -> None:
    node, _body, envelope, frame, validator = build_validator_report()
    wrong_kind_intent = HandlerIntent(HandlerIntentKind.PROVIDER_PUBLISH, envelope.namespace, envelope.scope_id, node.public_key, frame.request_id, envelope.body_digest)
    wrong_kind = guard_handler_intent(intent=wrong_kind_intent, validator=validator, policy=MisbindGuardPolicy(require_capgate_acceptance=False))
    assert wrong_kind.decision_kind is MisbindDecisionKind.REJECT_KIND_ROLE_MISMATCH

    wrong_request_intent = HandlerIntent(HandlerIntentKind.MUTABLE_HEAD_WRITE, envelope.namespace, envelope.scope_id, node.public_key, digest("other-request"), envelope.body_digest)
    wrong_request = guard_handler_intent(intent=wrong_request_intent, validator=validator, policy=MisbindGuardPolicy(require_capgate_acceptance=False))
    assert wrong_request.decision_kind is MisbindDecisionKind.QUARANTINE_REQUEST_MISMATCH

    wrong_actor_intent = HandlerIntent(HandlerIntentKind.MUTABLE_HEAD_WRITE, envelope.namespace, envelope.scope_id, kp(8).public_key_bytes, frame.request_id, envelope.body_digest)
    wrong_actor = guard_handler_intent(intent=wrong_actor_intent, validator=validator, policy=MisbindGuardPolicy(require_capgate_acceptance=False))
    assert wrong_actor.decision_kind is MisbindDecisionKind.REJECT_ACTOR_MISMATCH


def test_foldspine_audits_current_and_predecessor_surfaces() -> None:
    root = Path(__file__).resolve().parents[1]
    report = audit_fold_spine(root, revision="rev0028", artifact_stem=root.name)
    assert report.status == "pass"
    assert report.error_count == 0
    assert report.predecessor_fold_status == ("rev0027_branchmerge:pass",)
