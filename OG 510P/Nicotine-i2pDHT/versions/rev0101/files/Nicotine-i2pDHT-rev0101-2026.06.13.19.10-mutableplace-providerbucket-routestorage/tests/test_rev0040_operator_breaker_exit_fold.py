from __future__ import annotations

from dataclasses import replace

from i2p_dht_lab.ids import sha256
from i2p_dht_lab.operatorintent import (
    OperatorIntentAction,
    OperatorIntentDecisionKind,
    OperatorIntentPolicy,
    ZERO_DIGEST,
    assess_operator_intent,
    make_operator_intent,
)
from i2p_dht_lab.servicebreaker import (
    ServiceBreakerDecisionKind,
    ServiceBreakerObservation,
    ServiceBreakerObservationKind,
    ServiceBreakerPolicy,
    ServiceBreakerState,
    assess_service_breaker,
)
from i2p_dht_lab.serviceexit import (
    ServiceExitDecisionKind,
    ServiceExitSignalKind,
    ServiceExitPolicy,
    assess_service_exit,
    make_service_exit_signal,
    signal_from_operator_intent,
)
from i2p_dht_lab.operationsfold import audit_operations_fold


def d(label: str) -> bytes:
    return sha256(label.encode("utf-8"))


OP_KEY = d("operator-key")
SCOPE = d("scope")
REQUEST = d("request")


def intent(action: OperatorIntentAction, seq: int = 0, *, scope: bytes = SCOPE, request: bytes = REQUEST, bridge: bool = False, prev: bytes = ZERO_DIGEST):
    return make_operator_intent(
        action=action,
        profile_id="garden-profile",
        service_name="head_watch",
        scope_digest=scope,
        request_digest=request,
        sequence=seq,
        previous_intent_digest=prev,
        operator_key=OP_KEY,
        issued_at=100,
        expires_at=200,
        bridge_public=bridge,
    )


def obs(label: str, kind: ServiceBreakerObservationKind, *, family: str = "fam-a", issued: int = 100) -> ServiceBreakerObservation:
    return ServiceBreakerObservation(
        kind=kind,
        service_name="head_watch",
        scope_digest=SCOPE,
        request_digest=REQUEST,
        observation_digest=d("breaker:" + label),
        family_id=family,
        issued_at=issued,
        expires_at=300,
    )


def sig(kind: ServiceExitSignalKind, label: str, *, accept: bool = True, action: OperatorIntentAction | None = None, breaker_state: ServiceBreakerState | None = None, hard_negative_preserved: bool = True):
    return make_service_exit_signal(
        kind=kind,
        report_digest=d("exit:" + label),
        accept=accept,
        service_name="head_watch",
        scope_digest=SCOPE,
        request_digest=REQUEST,
        action=action,
        breaker_state=breaker_state,
        hard_negative_preserved=hard_negative_preserved,
    )


def test_operator_intent_accepts_sequence_link_and_bridge_requires_explicit_bit() -> None:
    first = intent(OperatorIntentAction.PAUSE_SERVICE, seq=0)
    report = assess_operator_intent((first,), now=150, expected_profile_id="garden-profile", expected_service_name="head_watch", expected_scope_digest=SCOPE, expected_request_digest=REQUEST)
    assert report.decision_kind is OperatorIntentDecisionKind.ACCEPT_INTENT
    second = intent(OperatorIntentAction.DEMOTE_TO_LEAF, seq=1, prev=first.intent_digest)
    assert assess_operator_intent((second,), now=150, previous_sequence=0, previous_intent_digest=first.intent_digest).decision_kind is OperatorIntentDecisionKind.ACCEPT_INTENT
    bridge_bad = intent(OperatorIntentAction.DISABLE_BRIDGE, seq=0, bridge=False)
    assert assess_operator_intent((bridge_bad,), now=150).decision_kind is OperatorIntentDecisionKind.QUARANTINE_BRIDGE_ACTION_NOT_EXPLICIT
    bridge_good = intent(OperatorIntentAction.DISABLE_BRIDGE, seq=0, bridge=True)
    assert assess_operator_intent((bridge_good,), now=150).decision_kind is OperatorIntentDecisionKind.ACCEPT_INTENT


def test_operator_intent_blocks_signature_replay_rollback_fork_and_scope_drift() -> None:
    good = intent(OperatorIntentAction.PAUSE_SERVICE)
    tampered = replace(good, service_name="other")
    assert assess_operator_intent((tampered,), now=150).decision_kind is OperatorIntentDecisionKind.QUARANTINE_BAD_SIGNATURE
    assert assess_operator_intent((good,), now=150, previously_seen_intents=(good.intent_digest,)).decision_kind is OperatorIntentDecisionKind.QUARANTINE_REPLAY
    assert assess_operator_intent((good,), now=150, previous_sequence=5).decision_kind is OperatorIntentDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK
    fork = intent(OperatorIntentAction.DEMOTE_TO_LEAF, seq=0)
    assert assess_operator_intent((good, fork), now=150).decision_kind is OperatorIntentDecisionKind.QUARANTINE_SEQUENCE_FORK
    drift = intent(OperatorIntentAction.PAUSE_SERVICE, scope=d("other-scope"))
    assert assess_operator_intent((drift,), now=150, expected_scope_digest=SCOPE).decision_kind is OperatorIntentDecisionKind.QUARANTINE_SCOPE_DRIFT


def test_operator_intent_emergency_is_hold_and_resume_can_be_disabled() -> None:
    emergency = intent(OperatorIntentAction.EMERGENCY_FREEZE)
    assert assess_operator_intent((emergency,), now=150).decision_kind is OperatorIntentDecisionKind.ACCEPT_EMERGENCY_HOLD
    resume = intent(OperatorIntentAction.RESUME_SERVICE)
    assert assess_operator_intent((resume,), now=150, policy=OperatorIntentPolicy(allow_resume=False)).decision_kind is OperatorIntentDecisionKind.QUARANTINE_ACTION_NOT_ALLOWED


def test_service_breaker_trips_on_false_service_hard_negative_withdrawal_and_operator_pause() -> None:
    assert assess_service_breaker((obs("false", ServiceBreakerObservationKind.FALSE_SERVICE),), now=150).decision_kind is ServiceBreakerDecisionKind.TRIP_OPEN_FALSE_SERVICE
    assert assess_service_breaker((obs("hard", ServiceBreakerObservationKind.HARD_NEGATIVE),), now=150).decision_kind is ServiceBreakerDecisionKind.TRIP_OPEN_HARD_NEGATIVE
    assert assess_service_breaker((obs("withdraw", ServiceBreakerObservationKind.WITHDRAWAL),), now=150).decision_kind is ServiceBreakerDecisionKind.TRIP_OPEN_WITHDRAWAL
    assert assess_service_breaker((obs("pause", ServiceBreakerObservationKind.OPERATOR_PAUSE),), now=150).decision_kind is ServiceBreakerDecisionKind.TRIP_OPEN_OPERATOR_PAUSE


def test_service_breaker_half_opens_with_diverse_recovery_and_blocks_monoculture() -> None:
    policy = ServiceBreakerPolicy(min_recovery_successes=2, min_positive_families=2)
    recovery = (obs("a", ServiceBreakerObservationKind.RECOVERY_SUCCESS, family="fam-a"), obs("b", ServiceBreakerObservationKind.RECOVERY_SUCCESS, family="fam-b"))
    report = assess_service_breaker(recovery, policy=policy, prior_state=ServiceBreakerState.OPEN, now=150)
    assert report.decision_kind is ServiceBreakerDecisionKind.ACCEPT_HALF_OPEN_PROBE
    assert report.state is ServiceBreakerState.HALF_OPEN
    mono = (obs("a", ServiceBreakerObservationKind.RECOVERY_SUCCESS, family="fam-a"), obs("b", ServiceBreakerObservationKind.RECOVERY_SUCCESS, family="fam-a"))
    assert assess_service_breaker(mono, policy=policy, prior_state=ServiceBreakerState.OPEN, now=150).decision_kind is ServiceBreakerDecisionKind.QUARANTINE_FAMILY_MONOCULTURE


def test_service_breaker_refusal_loop_replay_expiry_and_drift() -> None:
    policy = ServiceBreakerPolicy(max_refusal_streak=1, max_failure_streak=1)
    refusals = (obs("a", ServiceBreakerObservationKind.USEFUL_REFUSAL, issued=100), obs("b", ServiceBreakerObservationKind.USEFUL_REFUSAL, issued=101))
    assert assess_service_breaker(refusals, policy=policy, now=150).decision_kind is ServiceBreakerDecisionKind.TRIP_OPEN_REFUSAL_LOOP
    o = obs("x", ServiceBreakerObservationKind.HEALTHY)
    assert assess_service_breaker((o,), now=150, previously_seen_observations=(o.observation_digest,)).decision_kind is ServiceBreakerDecisionKind.QUARANTINE_REPLAY
    expired = replace(o, expires_at=120)
    assert assess_service_breaker((expired,), now=150).decision_kind is ServiceBreakerDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE
    drift = replace(o, scope_digest=d("other-scope"))
    assert assess_service_breaker((drift,), now=150, expected_scope_digest=SCOPE).decision_kind is ServiceBreakerDecisionKind.QUARANTINE_SCOPE_DRIFT


def test_service_exit_accepts_pause_demote_disable_and_freeze_only_when_joined() -> None:
    pause_intent = sig(ServiceExitSignalKind.OPERATOR_INTENT, "intent", action=OperatorIntentAction.PAUSE_SERVICE)
    breaker_open = sig(ServiceExitSignalKind.BREAKER, "breaker", breaker_state=ServiceBreakerState.OPEN, accept=False)
    journal = sig(ServiceExitSignalKind.CONTINUITY_JOURNAL, "journal")
    assert assess_service_exit((pause_intent, breaker_open, journal), expected_service_name="head_watch", expected_scope_digest=SCOPE, expected_request_digest=REQUEST).decision_kind is ServiceExitDecisionKind.ACCEPT_PAUSE

    demote = sig(ServiceExitSignalKind.OPERATOR_INTENT, "demote", action=OperatorIntentAction.DEMOTE_TO_LEAF)
    drain = sig(ServiceExitSignalKind.DRAIN, "drain")
    profile_gc = sig(ServiceExitSignalKind.PROFILE_GC, "profile")
    assert assess_service_exit((demote, drain, journal, profile_gc), expected_service_name="head_watch", expected_scope_digest=SCOPE, expected_request_digest=REQUEST).decision_kind is ServiceExitDecisionKind.ACCEPT_DEMOTE_TO_LEAF

    bridge = sig(ServiceExitSignalKind.OPERATOR_INTENT, "bridge", action=OperatorIntentAction.DISABLE_BRIDGE)
    assert assess_service_exit((bridge, drain, journal), expected_service_name="head_watch", expected_scope_digest=SCOPE, expected_request_digest=REQUEST).decision_kind is ServiceExitDecisionKind.ACCEPT_DISABLE_BRIDGE

    freeze = sig(ServiceExitSignalKind.OPERATOR_INTENT, "freeze", action=OperatorIntentAction.EMERGENCY_FREEZE)
    assert assess_service_exit((freeze, journal), expected_service_name="head_watch", expected_scope_digest=SCOPE, expected_request_digest=REQUEST).decision_kind is ServiceExitDecisionKind.ACCEPT_EMERGENCY_FREEZE


def test_service_exit_blocks_unjoined_or_drifting_actions_and_hard_negative_drop() -> None:
    pause_intent = sig(ServiceExitSignalKind.OPERATOR_INTENT, "intent", action=OperatorIntentAction.PAUSE_SERVICE)
    assert assess_service_exit((pause_intent,), expected_service_name="head_watch", expected_scope_digest=SCOPE, expected_request_digest=REQUEST).decision_kind is ServiceExitDecisionKind.HOLD_NEEDS_BREAKER_OR_DRAIN
    drift = make_service_exit_signal(kind=ServiceExitSignalKind.CONTINUITY_JOURNAL, report_digest=d("exit:drift"), accept=True, service_name="head_watch", scope_digest=d("other-scope"), request_digest=REQUEST)
    assert assess_service_exit((pause_intent, drift), expected_service_name="head_watch", expected_scope_digest=SCOPE, expected_request_digest=REQUEST).decision_kind is ServiceExitDecisionKind.QUARANTINE_SCOPE_DRIFT
    drop = sig(ServiceExitSignalKind.CONTINUITY_JOURNAL, "drop", hard_negative_preserved=False)
    assert assess_service_exit((pause_intent, drop), expected_service_name="head_watch", expected_scope_digest=SCOPE, expected_request_digest=REQUEST).decision_kind is ServiceExitDecisionKind.QUARANTINE_HARD_NEGATIVE_DROP
    seen = pause_intent.report_digest
    assert assess_service_exit((pause_intent,), expected_service_name="head_watch", expected_scope_digest=SCOPE, expected_request_digest=REQUEST, previously_seen_reports=(seen,)).decision_kind is ServiceExitDecisionKind.QUARANTINE_REPLAY


def test_service_exit_resume_needs_closed_breaker_and_not_clean_drain() -> None:
    resume = sig(ServiceExitSignalKind.OPERATOR_INTENT, "resume", action=OperatorIntentAction.RESUME_SERVICE)
    open_breaker = sig(ServiceExitSignalKind.BREAKER, "open", breaker_state=ServiceBreakerState.OPEN, accept=False)
    assert assess_service_exit((resume, open_breaker), expected_service_name="head_watch", expected_scope_digest=SCOPE, expected_request_digest=REQUEST).decision_kind is ServiceExitDecisionKind.HOLD_RESUME_NEEDS_CLOSED_BREAKER
    closed_breaker = sig(ServiceExitSignalKind.BREAKER, "closed", breaker_state=ServiceBreakerState.CLOSED, accept=True)
    assert assess_service_exit((resume, closed_breaker), expected_service_name="head_watch", expected_scope_digest=SCOPE, expected_request_digest=REQUEST).decision_kind is ServiceExitDecisionKind.ACCEPT_RESUME
    drain = sig(ServiceExitSignalKind.DRAIN, "drain")
    assert assess_service_exit((resume, closed_breaker, drain), expected_service_name="head_watch", expected_scope_digest=SCOPE, expected_request_digest=REQUEST).decision_kind is ServiceExitDecisionKind.QUARANTINE_ACTION_MISMATCH


def test_service_exit_can_consume_real_operator_report_signal() -> None:
    cap = intent(OperatorIntentAction.PAUSE_SERVICE)
    op_report = assess_operator_intent((cap,), now=150, expected_scope_digest=SCOPE, expected_request_digest=REQUEST)
    op_signal = signal_from_operator_intent(op_report)
    breaker = sig(ServiceExitSignalKind.BREAKER, "breaker", breaker_state=ServiceBreakerState.OPEN, accept=False)
    journal = sig(ServiceExitSignalKind.CONTINUITY_JOURNAL, "journal")
    report = assess_service_exit((op_signal, breaker, journal), expected_service_name="head_watch", expected_scope_digest=SCOPE, expected_request_digest=REQUEST)
    assert report.decision_kind is ServiceExitDecisionKind.ACCEPT_PAUSE


def test_operationsfold_audits_current_revision() -> None:
    report = audit_operations_fold(".", revision="rev0040", artifact_stem="Nicotine-i2pDHT-rev0040-2026.06.04.15.XX-operatorbreaker-serviceexit-fold")
    assert report.status == "pass"
    assert report.error_count == 0
    assert report.predecessor_status == "pass"
