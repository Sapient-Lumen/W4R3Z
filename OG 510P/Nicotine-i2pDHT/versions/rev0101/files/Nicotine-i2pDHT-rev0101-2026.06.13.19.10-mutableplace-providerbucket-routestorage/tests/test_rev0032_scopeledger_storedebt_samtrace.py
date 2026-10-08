from __future__ import annotations

from dataclasses import replace

from i2p_dht_lab.egressmeter import EgressBudget, EgressEvent, EgressEventKind, assess_egress_window
from i2p_dht_lab.foldmap import audit_fold_map
from i2p_dht_lab.identity import DhtKeypair
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.obligationdebt import ObligationKind, ProofEvidence, ProofObligation, assess_obligation_debt
from i2p_dht_lab.probeledger import ProbeLedgerDecisionKind, ProbeLedgerRound, assess_probe_ledger
from i2p_dht_lab.samtrace import SamTraceDecisionKind, SamTracePolicy, assess_sam_trace
from i2p_dht_lab.samwire import SamStepKind, SamWireSend, SamWireStep, assess_sam_wire_script
from i2p_dht_lab.scopefence import ScopePurpose, ScopedClaim, assess_scope_fence
from i2p_dht_lab.scopefold import audit_scope_fold
from i2p_dht_lab.scopeledger import ScopeLedgerDecisionKind, ScopeLedgerObservation, ScopeLedgerPolicy, assess_scope_ledger
from i2p_dht_lab.storedebt import StoreDebtDecisionKind, StoreDebtObservation, StoreDebtPolicy, assess_store_debt
from i2p_dht_lab.storerepair import StoreRepairActionKind, StoreRepairPlan
from i2p_dht_lab.transportshadow import ShadowPayloadKind, create_shadow_frame, validate_shadow_frame
from i2p_dht_lab.wirecanon import WireFrame, WireMessageKind


def digest(label: str) -> bytes:
    return sha256(("rev0032:" + label).encode("utf-8"))


def kp(label: str) -> DhtKeypair:
    return DhtKeypair.from_seed(digest("seed:" + label))


def scope_ids() -> tuple[bytes, bytes, bytes]:
    return digest("scope"), digest("object"), digest("request")


def scope_report(*, now: int, purpose: ScopePurpose = ScopePurpose.BOOTSTRAP):
    scope_id, object_digest, request_id = scope_ids()
    claims = (
        ScopedClaim.create(keypair=kp("scope-A"), scope_id=scope_id, object_digest=object_digest, request_id=request_id, purpose=purpose, source_family="source-A", path_family="path-A", sequence=1, issued_at=now, ttl=300),
        ScopedClaim.create(keypair=kp("scope-B"), scope_id=scope_id, object_digest=object_digest, request_id=request_id, purpose=purpose, source_family="source-B", path_family="path-B", sequence=1, issued_at=now, ttl=300),
    )
    return assess_scope_fence(claims, expected_scope_id=scope_id, expected_object_digest=object_digest, expected_request_id=request_id, expected_purpose=purpose, now=now + 1)


def probe_round(label: str, *, source: str, path: str, now: int, fast: bool = False) -> ProbeLedgerRound:
    return ProbeLedgerRound(
        round_id=digest("round:" + label),
        source_family=source,
        path_family=path,
        issued_at=now,
        expires_at=now + 300,
        bootstrap_digest=digest("bootstrap:" + label),
        bootstrap_accept=True,
        live_probe_digests=(digest("live:" + label),),
        egress_digest=digest("egress:" + label),
        egress_accept=True,
        fast_window_winner=fast,
    )


def probe_report(*, now: int):
    return assess_probe_ledger((probe_round("a", source="source-A", path="path-A", now=now), probe_round("b", source="source-B", path="path-B", now=now)), now=now + 1)


def open_obligation_report(*, now: int):
    scope_id, object_digest, _ = scope_ids()
    ob = ProofObligation.create(keypair=kp("obligation"), kind=ObligationKind.ROUTE_LIVENESS, scope_id=scope_id, object_digest=object_digest, subject_digest=digest("subject"), sequence=1, issued_at=now, due_at=now + 500)
    return assess_obligation_debt((ob,), (), now=now + 1)


def cleared_obligation_report(*, now: int):
    scope_id, object_digest, _ = scope_ids()
    subject = digest("subject-cleared")
    ob = ProofObligation.create(keypair=kp("obligation-cleared"), kind=ObligationKind.ROUTE_LIVENESS, scope_id=scope_id, object_digest=object_digest, subject_digest=subject, sequence=1, issued_at=now, due_at=now + 500)
    ev = (
        ProofEvidence.create(keypair=kp("evidence-A"), kind=ObligationKind.ROUTE_LIVENESS, scope_id=scope_id, object_digest=object_digest, subject_digest=subject, source_family="source-A", path_family="path-A", sequence=1, issued_at=now, ttl=300, verdict_digest=digest("verdict-A")),
        ProofEvidence.create(keypair=kp("evidence-B"), kind=ObligationKind.ROUTE_LIVENESS, scope_id=scope_id, object_digest=object_digest, subject_digest=subject, source_family="source-B", path_family="path-B", sequence=1, issued_at=now, ttl=300, verdict_digest=digest("verdict-B")),
    )
    return assess_obligation_debt((ob,), ev, now=now + 1)


def scope_obs(label: str, *, source: str, path: str, seq: int, now: int, obligation=None, probe=None, scope=None) -> ScopeLedgerObservation:
    scope_id, object_digest, request_id = scope_ids()
    return ScopeLedgerObservation.create(
        keypair=kp("scope-ledger:" + label),
        scope_id=scope_id,
        object_digest=object_digest,
        request_id=request_id,
        purpose=ScopePurpose.BOOTSTRAP,
        source_family=source,
        path_family=path,
        sequence=seq,
        issued_at=now,
        ttl=300,
        scope_report=scope or scope_report(now=now),
        probe_report=probe or probe_report(now=now),
        obligation_report=obligation,
    )


def test_scopeledger_accepts_diverse_joined_scope_without_debt() -> None:
    now = 1_766_700_000
    obligation = cleared_obligation_report(now=now)
    observations = (
        scope_obs("a", source="source-A", path="path-A", seq=1, now=now, obligation=obligation),
        scope_obs("b", source="source-B", path="path-B", seq=1, now=now, obligation=obligation),
    )
    report = assess_scope_ledger(observations, expected_scope_id=scope_ids()[0], expected_object_digest=scope_ids()[1], expected_request_id=scope_ids()[2], expected_purpose=ScopePurpose.BOOTSTRAP, now=now + 2)
    assert report.decision_kind is ScopeLedgerDecisionKind.ACCEPT_STICKY_SCOPE_ADVANCE
    assert report.accept
    assert len(report.source_families) == 2


def test_scopeledger_blocks_replay_scope_mismatch_and_probe_failure() -> None:
    now = 1_766_700_100
    first = scope_obs("replay", source="source-A", path="path-A", seq=1, now=now)
    replay = assess_scope_ledger((first, first), expected_scope_id=scope_ids()[0], expected_object_digest=scope_ids()[1], expected_request_id=scope_ids()[2], expected_purpose=ScopePurpose.BOOTSTRAP, now=now + 2)
    assert replay.decision_kind is ScopeLedgerDecisionKind.QUARANTINE_REPLAYED_OBSERVATION

    wrong_scope_observation = ScopeLedgerObservation.create(
        keypair=kp("wrong-scope"),
        scope_id=digest("wrong-scope"),
        object_digest=scope_ids()[1],
        request_id=scope_ids()[2],
        purpose=ScopePurpose.BOOTSTRAP,
        source_family="source-A",
        path_family="path-A",
        sequence=1,
        issued_at=now,
        ttl=300,
        scope_report=scope_report(now=now),
        probe_report=probe_report(now=now),
    )
    mismatch = assess_scope_ledger((wrong_scope_observation,), expected_scope_id=scope_ids()[0], expected_object_digest=scope_ids()[1], expected_request_id=scope_ids()[2], expected_purpose=ScopePurpose.BOOTSTRAP, now=now + 2)
    assert mismatch.decision_kind is ScopeLedgerDecisionKind.QUARANTINE_SCOPE_MISMATCH

    captured_probe = assess_probe_ledger(tuple(probe_round(f"fast-{idx}", source="captured", path=f"path-{idx}", now=now, fast=True) for idx in range(3)), now=now + 1)
    assert captured_probe.decision_kind is ProbeLedgerDecisionKind.QUARANTINE_FAST_FAMILY_CAPTURE
    poisoned = scope_obs("poisoned", source="source-B", path="path-B", seq=2, now=now, probe=captured_probe)
    report = assess_scope_ledger((poisoned,), expected_scope_id=scope_ids()[0], expected_object_digest=scope_ids()[1], expected_request_id=scope_ids()[2], expected_purpose=ScopePurpose.BOOTSTRAP, now=now + 2)
    assert report.decision_kind is ScopeLedgerDecisionKind.QUARANTINE_PROBE_LEDGER


def test_scopeledger_handles_open_proof_debt_explicitly() -> None:
    now = 1_766_700_200
    obligation = open_obligation_report(now=now)
    observations = (
        scope_obs("debt-a", source="source-A", path="path-A", seq=1, now=now, obligation=obligation),
        scope_obs("debt-b", source="source-B", path="path-B", seq=1, now=now, obligation=obligation),
    )
    hold = assess_scope_ledger(observations, expected_scope_id=scope_ids()[0], expected_object_digest=scope_ids()[1], expected_request_id=scope_ids()[2], expected_purpose=ScopePurpose.BOOTSTRAP, now=now + 2)
    assert hold.decision_kind is ScopeLedgerDecisionKind.HOLD_OPEN_OBLIGATIONS
    watch = assess_scope_ledger(observations, expected_scope_id=scope_ids()[0], expected_object_digest=scope_ids()[1], expected_request_id=scope_ids()[2], expected_purpose=ScopePurpose.BOOTSTRAP, now=now + 2, policy=ScopeLedgerPolicy(allow_accept_with_debt=True, max_open_obligations_for_watch=2))
    assert watch.decision_kind is ScopeLedgerDecisionKind.ACCEPT_WITH_PROOF_DEBT
    assert watch.accept


def repair_plan(action: StoreRepairActionKind, label: str) -> StoreRepairPlan:
    return StoreRepairPlan(action=action, reason=label, retry_after_seconds=600 if action is StoreRepairActionKind.HOLD_FOR_BACKOFF else 0, digest=digest("repair:" + label))


def store_obs(label: str, *, action: StoreRepairActionKind, source: str, path: str, seq: int, now: int, replicas: int = 3, custody: int = 2, tombstones=()) -> StoreDebtObservation:
    return StoreDebtObservation.create(
        keypair=kp("store-debt:" + label),
        scope_digest=digest("store-scope"),
        target=digest("store-target"),
        record_digest=digest("store-record"),
        source_family=source,
        path_family=path,
        sequence=seq,
        issued_at=now,
        ttl=300,
        repair_plan=repair_plan(action, label),
        accepted_replica_count=replicas,
        custody_proof_count=custody,
        store_report_digest=digest("store-report:" + label),
        custody_report_digest=digest("custody-report:" + label),
        tombstone_digests=tombstones,
    )


def test_storedebt_accepts_sufficient_diverse_storage() -> None:
    now = 1_766_701_000
    observations = (
        store_obs("a", action=StoreRepairActionKind.NO_ACTION, source="family-A", path="path-A", seq=1, now=now),
        store_obs("b", action=StoreRepairActionKind.NO_ACTION, source="family-B", path="path-B", seq=1, now=now),
    )
    report = assess_store_debt(observations, expected_scope_digest=digest("store-scope"), expected_target=digest("store-target"), expected_record_digest=digest("store-record"), now=now + 1)
    assert report.decision_kind is StoreDebtDecisionKind.ACCEPT_NO_STORE_DEBT
    assert report.accept


def test_storedebt_keeps_replica_custody_and_tombstone_debt_visible() -> None:
    now = 1_766_701_100
    short = assess_store_debt((store_obs("short", action=StoreRepairActionKind.CAST_TO_RESERVES, source="family-A", path="path-A", seq=1, now=now, replicas=1, custody=2), store_obs("short-b", action=StoreRepairActionKind.NO_ACTION, source="family-B", path="path-B", seq=1, now=now, replicas=1, custody=2)), expected_scope_digest=digest("store-scope"), expected_target=digest("store-target"), expected_record_digest=digest("store-record"), now=now + 1)
    assert short.decision_kind is StoreDebtDecisionKind.PLAN_REPAIR_REPLICAS

    custody = assess_store_debt((store_obs("custody-a", action=StoreRepairActionKind.NO_ACTION, source="family-A", path="path-A", seq=1, now=now, replicas=3, custody=0), store_obs("custody-b", action=StoreRepairActionKind.NO_ACTION, source="family-B", path="path-B", seq=1, now=now, replicas=3, custody=0)), expected_scope_digest=digest("store-scope"), expected_target=digest("store-target"), expected_record_digest=digest("store-record"), now=now + 1)
    assert custody.decision_kind is StoreDebtDecisionKind.PLAN_CUSTODY_AUDIT

    tombstone = assess_store_debt((store_obs("tomb", action=StoreRepairActionKind.NO_ACTION, source="family-A", path="path-A", seq=1, now=now, tombstones=(digest("tombstone"),)), store_obs("tomb-b", action=StoreRepairActionKind.NO_ACTION, source="family-B", path="path-B", seq=1, now=now)), expected_scope_digest=digest("store-scope"), expected_target=digest("store-target"), expected_record_digest=digest("store-record"), now=now + 1)
    assert tombstone.decision_kind is StoreDebtDecisionKind.QUARANTINE_LIVE_TOMBSTONE


def test_storedebt_catches_replay_sequence_fork_and_bad_scope() -> None:
    now = 1_766_701_200
    first = store_obs("fork", action=StoreRepairActionKind.NO_ACTION, source="family-A", path="path-A", seq=1, now=now)
    replay = assess_store_debt((first, first), expected_scope_digest=digest("store-scope"), expected_target=digest("store-target"), expected_record_digest=digest("store-record"), now=now + 1)
    assert replay.decision_kind is StoreDebtDecisionKind.QUARANTINE_REPLAYED_OBSERVATION

    second = store_obs("fork-other", action=StoreRepairActionKind.NO_ACTION, source="family-B", path="path-B", seq=1, now=now)
    forked_same_actor = replace(second, actor_public_key=first.actor_public_key, sequence=first.sequence, signature=first.signature)
    fork = assess_store_debt((first, forked_same_actor), expected_scope_digest=digest("store-scope"), expected_target=digest("store-target"), expected_record_digest=digest("store-record"), now=now + 1)
    assert fork.decision_kind in {StoreDebtDecisionKind.QUARANTINE_BAD_SIGNATURE, StoreDebtDecisionKind.QUARANTINE_SEQUENCE_FORK}

    bad = replace(first, scope_digest=digest("wrong-store-scope"))
    mismatch = assess_store_debt((bad,), expected_scope_digest=digest("store-scope"), expected_target=digest("store-target"), expected_record_digest=digest("store-record"), now=now + 1)
    assert mismatch.decision_kind in {StoreDebtDecisionKind.QUARANTINE_BAD_SIGNATURE, StoreDebtDecisionKind.QUARANTINE_SCOPE_MISMATCH}


def egress_report(*, now: int, watch: bool = False, accept: bool = True):
    event = EgressEvent(
        kind=EgressEventKind.SAM_STREAM_SEND,
        scope_id=scope_ids()[0],
        object_digest=scope_ids()[1],
        destination_node_id=digest("dest-node"),
        destination_family="dest-A",
        path_family="path-A",
        issued_at=now,
        expires_at=now + 300,
        byte_cost=256,
        stream_cost=1,
    )
    if not accept:
        event = replace(event, byte_cost=100_000)
    if watch:
        raw = EgressEvent(
            kind=EgressEventKind.PROVIDER_REAL_PROBE,
            scope_id=scope_ids()[0],
            object_digest=scope_ids()[1],
            destination_node_id=digest("dest-raw"),
            destination_family="dest-B",
            path_family="path-B",
            issued_at=now,
            expires_at=now + 300,
            byte_cost=1,
            stream_cost=1,
            exposes_raw_key=True,
        )
        decoy = replace(raw, kind=EgressEventKind.PROVIDER_DECOY_PROBE, exposes_raw_key=False, destination_node_id=digest("dest-decoy"), destination_family="dest-C")
        return assess_egress_window((event, raw, decoy), now=now + 1, budget=EgressBudget(max_raw_key_exposures=1))
    return assess_egress_window((event,), now=now + 1)


def sam_shadow_bundle(*, now: int, reconnect: bool = False, object_digest: bytes | None = None, request_id: bytes | None = None):
    keypair = kp("samtrace")
    sender_node = digest("sam-node")
    req = request_id or scope_ids()[2]
    obj = object_digest or scope_ids()[1]
    shadow = create_shadow_frame(keypair=keypair, sender_node_id=sender_node, request_id=req, payload_kind=ShadowPayloadKind.EVIDENCE_GC_REPORT, report_digest=digest("shadow-report"), subject_digest=obj, issued_at=now, ttl=300)
    validation = validate_shadow_frame(shadow.frame, payload_bytes=shadow.payload.to_bytes(), now=now + 1, expected_report_digest=digest("shadow-report"))
    hello = SamWireStep.create(keypair=keypair, kind=SamStepKind.HELLO, session_id="s", destination="dest.i2p", issued_at=now)
    sess = SamWireStep.create(keypair=keypair, kind=SamStepKind.SESSION_CREATE, session_id="s", destination="dest.i2p", issued_at=now + 1)
    send_step = SamWireStep.create(keypair=keypair, kind=SamStepKind.STREAM_SEND, session_id="s", destination="dest.i2p", issued_at=now + 2, frame=shadow.frame, payload=shadow.payload.to_bytes())
    steps = [hello, sess]
    if reconnect:
        steps.append(SamWireStep.create(keypair=keypair, kind=SamStepKind.RECONNECT, session_id="s", destination="dest.i2p", issued_at=now + 2))
    steps.append(SamWireSend(send_step, shadow.frame, shadow.payload.to_bytes()))
    return validation, assess_sam_wire_script(tuple(steps), now=now + 3, expected_destination="dest.i2p")


def test_samtrace_accepts_scope_bound_shadow_send_and_reconnect_watch() -> None:
    now = 1_766_702_000
    shadow, sam_report = sam_shadow_bundle(now=now)
    report = assess_sam_trace(scope_report=scope_report(now=now), sam_report=sam_report, egress_report=egress_report(now=now), shadow_reports=(shadow,), expected_request_id=scope_ids()[2], expected_object_digest=scope_ids()[1])
    assert report.decision_kind is SamTraceDecisionKind.ACCEPT_SCOPE_BOUND_TRACE
    assert report.accept

    shadow2, sam_reconnect = sam_shadow_bundle(now=now + 20, reconnect=True)
    reconnect_report = assess_sam_trace(scope_report=scope_report(now=now + 20), sam_report=sam_reconnect, egress_report=egress_report(now=now + 20), shadow_reports=(shadow2,), expected_request_id=scope_ids()[2], expected_object_digest=scope_ids()[1])
    assert reconnect_report.decision_kind is SamTraceDecisionKind.ACCEPT_WITH_RECONNECT_WATCH
    assert reconnect_report.accept


def test_samtrace_rejects_cross_request_cross_object_and_bad_egress() -> None:
    now = 1_766_702_100
    shadow, sam_report = sam_shadow_bundle(now=now, request_id=digest("wrong-request"))
    request_report = assess_sam_trace(scope_report=scope_report(now=now), sam_report=sam_report, egress_report=egress_report(now=now), shadow_reports=(shadow,), expected_request_id=scope_ids()[2], expected_object_digest=scope_ids()[1])
    assert request_report.decision_kind is SamTraceDecisionKind.QUARANTINE_REQUEST_MISMATCH

    shadow_obj, sam_obj = sam_shadow_bundle(now=now + 10, object_digest=digest("wrong-object"))
    obj_report = assess_sam_trace(scope_report=scope_report(now=now + 10), sam_report=sam_obj, egress_report=egress_report(now=now + 10), shadow_reports=(shadow_obj,), expected_request_id=scope_ids()[2], expected_object_digest=scope_ids()[1])
    assert obj_report.decision_kind is SamTraceDecisionKind.QUARANTINE_OBJECT_MISMATCH

    shadow_ok, sam_ok = sam_shadow_bundle(now=now + 20)
    bad_egress = assess_sam_trace(scope_report=scope_report(now=now + 20), sam_report=sam_ok, egress_report=egress_report(now=now + 20, accept=False), shadow_reports=(shadow_ok,), expected_request_id=scope_ids()[2], expected_object_digest=scope_ids()[1])
    assert bad_egress.decision_kind is SamTraceDecisionKind.QUARANTINE_EGRESS


def test_samtrace_can_hold_accept_with_watch_egress_by_policy() -> None:
    now = 1_766_702_200
    shadow, sam_report = sam_shadow_bundle(now=now)
    watch = assess_sam_trace(scope_report=scope_report(now=now), sam_report=sam_report, egress_report=egress_report(now=now, watch=True), shadow_reports=(shadow,), expected_request_id=scope_ids()[2], expected_object_digest=scope_ids()[1])
    assert watch.decision_kind is SamTraceDecisionKind.HOLD_EGRESS_WATCH
    allowed = assess_sam_trace(scope_report=scope_report(now=now), sam_report=sam_report, egress_report=egress_report(now=now, watch=True), shadow_reports=(shadow,), expected_request_id=scope_ids()[2], expected_object_digest=scope_ids()[1], policy=SamTracePolicy(allow_egress_accept_with_watch=True))
    assert allowed.decision_kind is SamTraceDecisionKind.ACCEPT_SCOPE_BOUND_TRACE
    assert allowed.accept


def test_scopefold_and_foldmap_current_path_are_visible() -> None:
    fold = audit_scope_fold(".")
    assert fold.status == "pass"
    assert fold.error_count == 0
    historical = audit_fold_map(".", revision="rev0031")
    assert historical.status == "pass"
