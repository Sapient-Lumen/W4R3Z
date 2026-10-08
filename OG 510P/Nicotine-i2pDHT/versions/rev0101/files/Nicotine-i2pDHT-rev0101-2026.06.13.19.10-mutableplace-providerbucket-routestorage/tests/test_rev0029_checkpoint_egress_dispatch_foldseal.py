from dataclasses import replace
from pathlib import Path

from i2p_dht_lab.checkpointlane import (
    CheckpointDecisionKind,
    CheckpointFact,
    CheckpointFactKind,
    CheckpointPolicy,
    StateCheckpoint,
    ZERO_DIGEST,
    assess_checkpoint,
)
from i2p_dht_lab.dispatchjoin import DispatchJoinDecisionKind, assess_bound_dispatch
from i2p_dht_lab.egressmeter import EgressBudget, EgressDecisionKind, EgressEvent, EgressEventKind, assess_egress_window
from i2p_dht_lab.foldseal import audit_fold_seal
from i2p_dht_lab.identity import DhtKeypair, NodeIdentity
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.misbindguard import HandlerIntent, HandlerIntentKind, MisbindDecisionKind, MisbindGuardPolicy, guard_handler_intent
from i2p_dht_lab.validatorwall import PayloadEnvelope, PayloadRole, validate_payload_wall
from i2p_dht_lab.wirecanon import WireFrame, WireMessageKind


def kp(n: int) -> DhtKeypair:
    return DhtKeypair.from_seed(bytes([n]) * 32)


def ident(n: int) -> NodeIdentity:
    return NodeIdentity.create(destination=f"rev0029-node-{n}.b32.i2p", keypair=kp(n))


def digest(label: str) -> bytes:
    return sha256(label.encode("utf-8"))


def fact(kind: CheckpointFactKind, label: str, *, seq: int, now: int, fam: str = "fam-A") -> CheckpointFact:
    return CheckpointFact(
        kind=kind,
        scope_id=digest("scope:" + label),
        object_digest=digest("object:" + label + f":{seq}"),
        sequence=seq,
        source_family=fam,
        path_family="path-" + fam,
        issued_at=now,
        expires_at=now + 10_000,
        byte_cost=128,
    )


def checkpoint(n: int, *, generation: int, prev: bytes, journal: bytes, facts=(), now: int = 1_766_100_000) -> StateCheckpoint:
    return StateCheckpoint.create(keypair=kp(n), generation=generation, prev_checkpoint_digest=prev, journal_tip_digest=journal, facts=facts, issued_at=now, ttl=10_000)


def event(kind: EgressEventKind, label: str, *, scope: bytes, obj: bytes, now: int, fam: str = "fam-A", raw: bool = False, byte_cost: int = 100, streams: int = 1) -> EgressEvent:
    return EgressEvent(
        kind=kind,
        scope_id=scope,
        object_digest=obj,
        destination_node_id=ident(len(label) % 20 + 30).node_id,
        destination_family=fam,
        path_family="path-" + fam,
        issued_at=now,
        expires_at=now + 600,
        byte_cost=byte_cost,
        stream_cost=streams,
        exposes_raw_key=raw,
        note=label,
    )


def validator_and_intent(kind: HandlerIntentKind = HandlerIntentKind.MUTABLE_HEAD_WRITE):
    now = 1_766_200_000
    node = ident(9)
    body = b"rev0029 dispatch body"
    scope = digest("dispatch-scope")
    if kind is HandlerIntentKind.MUTABLE_HEAD_WRITE:
        role = PayloadRole.MUTABLE_HEAD
        wire_kind = WireMessageKind.EPOCH_HEAD
    elif kind is HandlerIntentKind.WITNESS_ACCEPT:
        role = PayloadRole.WITNESS_RECEIPT
        wire_kind = WireMessageKind.WITNESS_RECEIPT
    else:
        role = PayloadRole.PROVIDER_CLAIM
        wire_kind = WireMessageKind.FIND_PROVIDER
    envelope = PayloadEnvelope.create(namespace="i2p-dht-control", role=role, scope_id=scope, body=body, issued_at=now, ttl=300)
    payload = envelope.to_bytes()
    frame = WireFrame.create(keypair=kp(9), sender_node_id=node.node_id, message_kind=wire_kind, request_id=digest("dispatch-request"), payload=payload, issued_at=now, ttl=300, flags=(role.value,))
    validator = validate_payload_wall(frame, payload=payload, body=body, now=now + 1)
    intent = HandlerIntent(kind=kind, namespace=envelope.namespace, scope_id=envelope.scope_id, actor_public_key=node.public_key, request_id=frame.request_id, body_digest=envelope.body_digest)
    misbind = guard_handler_intent(intent=intent, validator=validator, policy=MisbindGuardPolicy(require_capgate_acceptance=False))
    return now, intent, misbind


def test_checkpoint_accepts_first_and_advancing_preserving_tombstone() -> None:
    now = 1_766_100_000
    tomb = fact(CheckpointFactKind.TOMBSTONE, "dead", seq=1, now=now, fam="fam-T")
    head = fact(CheckpointFactKind.MUTABLE_HEAD, "head", seq=1, now=now, fam="fam-H")
    first = checkpoint(1, generation=1, prev=ZERO_DIGEST, journal=digest("journal-1"), facts=(tomb, head), now=now)
    first_report = assess_checkpoint(first, now=now + 1)
    assert first_report.decision.kind is CheckpointDecisionKind.ACCEPT_FIRST_CHECKPOINT
    assert first_report.decision.accept

    newer_head = fact(CheckpointFactKind.MUTABLE_HEAD, "head", seq=2, now=now + 10, fam="fam-H")
    second = checkpoint(1, generation=2, prev=first.checkpoint_digest, journal=digest("journal-2"), facts=(tomb, newer_head), now=now + 10)
    second_report = assess_checkpoint(second, previous=first, now=now + 20)
    assert second_report.decision.kind is CheckpointDecisionKind.ACCEPT_ADVANCING_CHECKPOINT
    assert second_report.decision.accept
    assert second_report.hard_fact_drops == ()


def test_checkpoint_quarantines_rollback_fork_prev_mismatch_and_hard_drop() -> None:
    now = 1_766_100_100
    tomb = fact(CheckpointFactKind.CAPABILITY_REVOCATION, "grant", seq=4, now=now, fam="fam-R")
    first = checkpoint(2, generation=4, prev=ZERO_DIGEST, journal=digest("journal-a"), facts=(tomb,), now=now)
    rollback = checkpoint(2, generation=3, prev=ZERO_DIGEST, journal=digest("journal-old"), facts=(tomb,), now=now + 1)
    assert assess_checkpoint(rollback, previous=first, now=now + 2).decision.kind is CheckpointDecisionKind.QUARANTINE_ROLLBACK

    fork = checkpoint(2, generation=4, prev=ZERO_DIGEST, journal=digest("journal-fork"), facts=(tomb,), now=now + 2)
    assert assess_checkpoint(fork, previous=first, now=now + 3).decision.kind is CheckpointDecisionKind.QUARANTINE_SAME_GENERATION_FORK

    bad_prev = checkpoint(2, generation=5, prev=digest("wrong-prev"), journal=digest("journal-b"), facts=(tomb,), now=now + 3)
    assert assess_checkpoint(bad_prev, previous=first, now=now + 4).decision.kind is CheckpointDecisionKind.QUARANTINE_PREV_MISMATCH

    dropped = checkpoint(2, generation=5, prev=first.checkpoint_digest, journal=digest("journal-c"), facts=(), now=now + 4)
    drop_report = assess_checkpoint(dropped, previous=first, now=now + 5)
    assert drop_report.decision.kind is CheckpointDecisionKind.QUARANTINE_HARD_FACT_DROP
    assert drop_report.hard_fact_drops == (tomb.fact_digest,)


def test_checkpoint_rejects_bad_signature_conflicts_and_generation_gap_watch() -> None:
    now = 1_766_100_200
    a = fact(CheckpointFactKind.MUTABLE_HEAD, "same", seq=1, now=now, fam="fam-A")
    b = replace(a, object_digest=digest("different-object"), source_family="fam-B", path_family="path-fam-B")
    conflict = checkpoint(3, generation=1, prev=ZERO_DIGEST, journal=digest("journal-conflict"), facts=(a, b), now=now)
    assert assess_checkpoint(conflict, now=now + 1).decision.kind is CheckpointDecisionKind.QUARANTINE_CONFLICTING_FACTS

    good = checkpoint(3, generation=1, prev=ZERO_DIGEST, journal=digest("journal-good"), facts=(a,), now=now)
    tampered = replace(good, signature=b"0" * 64)
    assert assess_checkpoint(tampered, now=now + 1).decision.kind is CheckpointDecisionKind.REJECT_BAD_SIGNATURE

    gap = checkpoint(3, generation=4, prev=good.checkpoint_digest, journal=digest("journal-gap"), facts=(a,), now=now + 1)
    gap_report = assess_checkpoint(gap, previous=good, now=now + 2, policy=CheckpointPolicy(allow_generation_gap=False))
    assert gap_report.decision.kind is CheckpointDecisionKind.WATCH_GENERATION_GAP
    assert not gap_report.decision.accept


def test_egressmeter_accepts_balanced_provider_probe_window() -> None:
    now = 1_766_200_100
    scope = digest("egress-scope")
    obj = digest("egress-object")
    events = (
        event(EgressEventKind.PROVIDER_REAL_PROBE, "real", scope=scope, obj=obj, now=now, fam="fam-A", raw=True),
        event(EgressEventKind.PROVIDER_DECOY_PROBE, "decoy", scope=scope, obj=obj, now=now, fam="fam-B"),
    )
    report = assess_egress_window(events, now=now + 1, budget=EgressBudget(max_raw_key_exposures=1, min_destination_families_for_risky=2))
    assert report.decision_kind is EgressDecisionKind.ACCEPT_WITH_WATCH
    assert report.accept
    assert report.raw_key_exposures == 1
    assert report.destination_families == ("fam-A", "fam-B")


def test_egressmeter_rejects_decoy_gap_raw_budget_replay_and_family_monoculture() -> None:
    now = 1_766_200_200
    scope = digest("egress-bad-scope")
    obj = digest("egress-bad-object")
    real_a = event(EgressEventKind.PROVIDER_REAL_PROBE, "real-a", scope=scope, obj=obj, now=now, fam="fam-A", raw=True)
    real_b = event(EgressEventKind.PROVIDER_REAL_PROBE, "real-b", scope=scope, obj=obj, now=now, fam="fam-B", raw=True)
    no_decoy = assess_egress_window((real_a,), now=now + 1, budget=EgressBudget(max_raw_key_exposures=2, min_destination_families_for_risky=1, min_decoy_per_real_probe=1))
    assert no_decoy.decision_kind is EgressDecisionKind.REJECT_DECOY_RATIO
    too_raw = assess_egress_window((real_a, real_b), now=now + 1, budget=EgressBudget(max_raw_key_exposures=1, min_destination_families_for_risky=2, min_decoy_per_real_probe=0))
    assert too_raw.decision_kind is EgressDecisionKind.REJECT_RAW_KEY_EXPOSURE
    replay = assess_egress_window((real_a, real_a), now=now + 1, budget=EgressBudget(max_raw_key_exposures=2, min_destination_families_for_risky=1, min_decoy_per_real_probe=0))
    assert replay.decision_kind is EgressDecisionKind.QUARANTINE_REPLAYED_EVENT
    mono = tuple(event(EgressEventKind.REPAIR_REQUEST, f"r{idx}", scope=scope, obj=obj, now=now, fam="fam-Z") for idx in range(3))
    mono_report = assess_egress_window(mono, now=now + 1, budget=EgressBudget(max_events_per_destination_family=2, min_decoy_per_real_probe=0))
    assert mono_report.decision_kind is EgressDecisionKind.QUARANTINE_FAMILY_MONOCULTURE


def test_dispatchjoin_accepts_bound_intent_and_rejects_misbind() -> None:
    now, intent, misbind = validator_and_intent()
    assert misbind.decision_kind is MisbindDecisionKind.ACCEPT_BOUND_INTENT
    e = event(EgressEventKind.WITNESS_PUBLISH, "publish", scope=intent.scope_id, obj=intent.body_digest, now=now + 2, fam="fam-A")
    accepted = assess_bound_dispatch(intent=intent, misbind=misbind, egress_events=(e,), now=now + 3)
    assert accepted.decision_kind is DispatchJoinDecisionKind.ACCEPT_BOUND_DISPATCH
    assert accepted.accept

    _now2, bad_intent, bad_misbind = validator_and_intent()
    bad_intent = replace(bad_intent, request_id=digest("wrong-request"))
    # Re-run the guard with the wrong request id to get a real upstream reject.
    _now3, real_intent, _ = validator_and_intent()
    # Use existing validator by rebuilding from helper internals via accepted misbind is enough
    # for dispatch to reject a synthetic upstream failure from the guard output.
    bad = replace(misbind, decision_kind=MisbindDecisionKind.QUARANTINE_REQUEST_MISMATCH, accept=False, reason="synthetic request mismatch")
    rejected = assess_bound_dispatch(intent=real_intent, misbind=bad, egress_events=(e,), now=now + 3)
    assert rejected.decision_kind is DispatchJoinDecisionKind.REJECT_MISBIND_GUARD
    assert not rejected.accept


def test_dispatchjoin_quarantines_scope_and_object_leaks() -> None:
    now, intent, misbind = validator_and_intent()
    scope_leak = event(EgressEventKind.WITNESS_PUBLISH, "scope-leak", scope=digest("other-scope"), obj=intent.body_digest, now=now + 2, fam="fam-A")
    scope_report = assess_bound_dispatch(intent=intent, misbind=misbind, egress_events=(scope_leak,), now=now + 3)
    assert scope_report.decision_kind is DispatchJoinDecisionKind.QUARANTINE_SCOPE_LEAK
    assert scope_report.quarantined

    object_leak = event(EgressEventKind.WITNESS_PUBLISH, "object-leak", scope=intent.scope_id, obj=digest("other-object"), now=now + 2, fam="fam-A")
    object_report = assess_bound_dispatch(intent=intent, misbind=misbind, egress_events=(object_leak,), now=now + 3)
    assert object_report.decision_kind is DispatchJoinDecisionKind.QUARANTINE_OBJECT_LEAK


def test_dispatchjoin_blocks_raw_key_egress_for_witness_intent_and_egress_rejects() -> None:
    now, intent, misbind = validator_and_intent(HandlerIntentKind.WITNESS_ACCEPT)
    raw = event(EgressEventKind.WITNESS_PUBLISH, "raw-witness", scope=intent.scope_id, obj=intent.body_digest, now=now + 2, fam="fam-A", raw=True)
    raw_report = assess_bound_dispatch(intent=intent, misbind=misbind, egress_events=(raw,), now=now + 3, budget=EgressBudget(min_destination_families_for_risky=1, min_decoy_per_real_probe=0))
    assert raw_report.decision_kind is DispatchJoinDecisionKind.REJECT_FORBIDDEN_RAW_KEY_EGRESS
    assert not raw_report.accept

    huge = event(EgressEventKind.WITNESS_PUBLISH, "huge", scope=intent.scope_id, obj=intent.body_digest, now=now + 2, fam="fam-A", byte_cost=100_000)
    huge_report = assess_bound_dispatch(intent=intent, misbind=misbind, egress_events=(huge,), now=now + 3, budget=EgressBudget(max_total_bytes=1))
    assert huge_report.decision_kind is DispatchJoinDecisionKind.REJECT_EGRESS_BUDGET


def test_foldseal_pins_current_revision_navigation() -> None:
    root = Path(__file__).resolve().parents[1]
    report = audit_fold_seal(root, revision="rev0029", artifact_stem=root.name)
    assert report.status == "pass"
    assert report.error_count == 0
    assert report.warning_count == 0
    assert report.predecessor_status == "rev0028_foldspine:pass"
