from __future__ import annotations

from dataclasses import replace

from i2p_dht_lab.controlfold import audit_control_fold
from i2p_dht_lab.exitjournal import (
    ExitJournalDecisionKind,
    ExitJournalEntryKind,
    ZERO_DIGEST as JOURNAL_ZERO,
    assess_exit_journal,
    make_exit_journal_entry,
)
from i2p_dht_lab.identity import DhtKeypair
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.routerstop import (
    RouterStopAction,
    RouterStopDecisionKind,
    ZERO_DIGEST as ROUTER_ZERO,
    assess_router_stop_plan,
    make_router_stop_plan,
)
from i2p_dht_lab.sessionresume import (
    SessionResumeDecisionKind,
    SessionResumePolicy,
    SessionResumeSignalKind,
    assess_session_resume,
    make_session_resume_signal,
)

NOW = 10_000
SERVICE = "head_watch"
PROFILE = "garden-profile"
SCOPE = sha256(b"rev0041-scope")
REQUEST = sha256(b"rev0041-request")
SESSION = sha256(b"rev0041-session")
ROUTER = sha256(b"rev0041-router-report")
EXIT = sha256(b"rev0041-exit-report")
OPERATOR = sha256(b"rev0041-operator-intent")
BRIDGE_DRAIN = sha256(b"rev0041-bridge-drain")


def kp(n: int) -> DhtKeypair:
    return DhtKeypair.from_seed(bytes([n]) * 32)


def d(label: str) -> bytes:
    return sha256(label.encode("utf-8"))


def plan(action: RouterStopAction, *, seq: int = 0, prev: bytes = ROUTER_ZERO, key_index: int = 1, **kwargs):
    return make_router_stop_plan(
        keypair=kp(key_index),
        action=action,
        profile_id=kwargs.pop("profile_id", PROFILE),
        service_name=kwargs.pop("service_name", SERVICE),
        session_id_digest=kwargs.pop("session_id_digest", SESSION),
        router_report_digest=kwargs.pop("router_report_digest", ROUTER),
        service_exit_report_digest=kwargs.pop("service_exit_report_digest", EXIT),
        operator_intent_digest=kwargs.pop("operator_intent_digest", OPERATOR),
        sequence=seq,
        previous_plan_digest=prev,
        issued_at=kwargs.pop("issued_at", NOW),
        expires_at=kwargs.pop("expires_at", NOW + 600),
        **kwargs,
    )


def resume_signal(kind: SessionResumeSignalKind, label: str, *, family: str = "fam-a", path: str = "path-a", **kwargs):
    return make_session_resume_signal(
        kind=kind,
        label_digest=d(f"resume-{label}"),
        service_name=kwargs.pop("service_name", SERVICE),
        scope_digest=kwargs.pop("scope_digest", SCOPE),
        request_digest=kwargs.pop("request_digest", REQUEST),
        session_id_digest=kwargs.pop("session_id_digest", SESSION),
        issued_at=kwargs.pop("issued_at", NOW),
        expires_at=kwargs.pop("expires_at", NOW + 600),
        source_family=family,
        path_family=path,
        **kwargs,
    )


def good_resume_signals():
    return (
        resume_signal(SessionResumeSignalKind.SERVICE_EXIT_RESUME, "exit", family="fam-a", path="path-a"),
        resume_signal(SessionResumeSignalKind.BREAKER_RECOVERY, "breaker", family="fam-b", path="path-b"),
        resume_signal(SessionResumeSignalKind.SESSION_LEDGER, "session", family="fam-a", path="path-b"),
        resume_signal(SessionResumeSignalKind.SERVICE_LEASE, "lease", family="fam-b", path="path-a"),
        resume_signal(SessionResumeSignalKind.ANNOUNCEMENT, "announce", family="fam-c", path="path-c"),
        resume_signal(SessionResumeSignalKind.ROUTER_SESSION, "router", family="fam-c", path="path-b"),
    )


def jentry(kind: ExitJournalEntryKind, label: str, *, seq: int, prev: bytes, hard_negative: bool = False, key_index: int = 5, **kwargs):
    return make_exit_journal_entry(
        keypair=kp(key_index),
        kind=kind,
        service_name=kwargs.pop("service_name", SERVICE),
        scope_digest=kwargs.pop("scope_digest", SCOPE),
        request_digest=kwargs.pop("request_digest", REQUEST),
        sequence=seq,
        previous_entry_digest=prev,
        value_digest=kwargs.pop("value_digest", d(f"journal-{label}")),
        issued_at=kwargs.pop("issued_at", NOW + seq),
        hard_negative=hard_negative,
    )


def test_routerstop_accepts_keep_running_session_stop_and_router_stop_with_drain() -> None:
    keep = plan(RouterStopAction.KEEP_ROUTER_RUNNING)
    keep_report = assess_router_stop_plan(
        (keep,),
        now=NOW + 1,
        expected_profile_id=PROFILE,
        expected_service_name=SERVICE,
        expected_session_id_digest=SESSION,
        expected_router_report_digest=ROUTER,
        expected_service_exit_report_digest=EXIT,
        service_exit_accepted=False,
    )
    assert keep_report.decision_kind is RouterStopDecisionKind.ACCEPT_KEEP_ROUTER_RUNNING

    session = plan(RouterStopAction.STOP_SERVICE_SESSION)
    assert assess_router_stop_plan((session,), now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_session_id_digest=SESSION, expected_router_report_digest=ROUTER, expected_service_exit_report_digest=EXIT, service_exit_accepted=True).decision_kind is RouterStopDecisionKind.ACCEPT_SESSION_STOP

    stop = plan(RouterStopAction.STOP_BUNDLED_ROUTER, public_bridge_active=True, bridge_drain_report_digest=BRIDGE_DRAIN)
    assert assess_router_stop_plan((stop,), now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_session_id_digest=SESSION, expected_router_report_digest=ROUTER, expected_service_exit_report_digest=EXIT, service_exit_accepted=True, bridge_drain_accepted=True).decision_kind is RouterStopDecisionKind.ACCEPT_ROUTER_STOP


def test_routerstop_rejects_unsafe_side_effects_and_notorious_drifts() -> None:
    stop = plan(RouterStopAction.STOP_BUNDLED_ROUTER)
    assert assess_router_stop_plan((stop,), now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_session_id_digest=SESSION, expected_router_report_digest=ROUTER, expected_service_exit_report_digest=EXIT).decision_kind is RouterStopDecisionKind.HOLD_NEEDS_SERVICE_EXIT
    bridge = plan(RouterStopAction.STOP_BUNDLED_ROUTER, public_bridge_active=True)
    assert assess_router_stop_plan((bridge,), now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_session_id_digest=SESSION, expected_router_report_digest=ROUTER, expected_service_exit_report_digest=EXIT, service_exit_accepted=True).decision_kind is RouterStopDecisionKind.QUARANTINE_PUBLIC_BRIDGE_NOT_DRAINED
    ephemeral = plan(RouterStopAction.STOP_BUNDLED_ROUTER, persisted_destination=False)
    assert assess_router_stop_plan((ephemeral,), now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_session_id_digest=SESSION, expected_router_report_digest=ROUTER, expected_service_exit_report_digest=EXIT, service_exit_accepted=True).decision_kind is RouterStopDecisionKind.QUARANTINE_EPHEMERAL_DESTINATION
    notransit = plan(RouterStopAction.KEEP_ROUTER_RUNNING, notransit_requested=True)
    assert assess_router_stop_plan((notransit,), now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_session_id_digest=SESSION, expected_router_report_digest=ROUTER).decision_kind is RouterStopDecisionKind.QUARANTINE_NOTRANSIT_REGRESSION
    service_drift = plan(RouterStopAction.STOP_SERVICE_SESSION, service_name="other")
    assert assess_router_stop_plan((service_drift,), now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_session_id_digest=SESSION, expected_router_report_digest=ROUTER, service_exit_accepted=True).decision_kind is RouterStopDecisionKind.QUARANTINE_SERVICE_DRIFT


def test_routerstop_blocks_bad_signature_replay_sequence_fork_and_prev_mismatch() -> None:
    first = plan(RouterStopAction.STOP_SERVICE_SESSION, seq=0)
    tampered = replace(first, profile_id="evil-profile")
    assert assess_router_stop_plan((tampered,), now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_session_id_digest=SESSION, expected_router_report_digest=ROUTER, service_exit_accepted=True).decision_kind is RouterStopDecisionKind.QUARANTINE_BAD_SIGNATURE
    assert assess_router_stop_plan((first,), now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_session_id_digest=SESSION, expected_router_report_digest=ROUTER, service_exit_accepted=True, previously_seen_plans=(first.plan_digest,)).decision_kind is RouterStopDecisionKind.QUARANTINE_REPLAY
    assert assess_router_stop_plan((first,), now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_session_id_digest=SESSION, expected_router_report_digest=ROUTER, service_exit_accepted=True, previous_sequence=5).decision_kind is RouterStopDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK
    fork = plan(RouterStopAction.KEEP_ROUTER_RUNNING, seq=0)
    assert assess_router_stop_plan((first, fork), now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_session_id_digest=SESSION, expected_router_report_digest=ROUTER, service_exit_accepted=True).decision_kind is RouterStopDecisionKind.QUARANTINE_SEQUENCE_FORK
    second = plan(RouterStopAction.STOP_SERVICE_SESSION, seq=1, prev=d("wrong-prev"))
    assert assess_router_stop_plan((second,), now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_session_id_digest=SESSION, expected_router_report_digest=ROUTER, service_exit_accepted=True, previous_plan_digest=first.plan_digest).decision_kind is RouterStopDecisionKind.QUARANTINE_PREVIOUS_MISMATCH


def test_session_resume_accepts_joined_diverse_resume_and_bridge_relay() -> None:
    relay = resume_signal(SessionResumeSignalKind.RELAY_TICKET, "relay", family="fam-d", path="path-d")
    report = assess_session_resume(good_resume_signals() + (relay,), now=NOW + 1, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_session_id_digest=SESSION, bridge_mode=True)
    assert report.decision_kind is SessionResumeDecisionKind.ACCEPT_RESUME


def test_session_resume_blocks_missing_components_withdrawal_hard_negative_and_replay() -> None:
    without_lease = tuple(sig for sig in good_resume_signals() if sig.kind is not SessionResumeSignalKind.SERVICE_LEASE)
    assert assess_session_resume(without_lease, now=NOW + 1, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_session_id_digest=SESSION).decision_kind is SessionResumeDecisionKind.HOLD_NEEDS_SERVICE_LEASE
    withdrawn = good_resume_signals()[:-2] + (resume_signal(SessionResumeSignalKind.ANNOUNCEMENT, "announce", withdrawn=True, family="fam-c", path="path-c"), good_resume_signals()[-1])
    assert assess_session_resume(withdrawn, now=NOW + 1, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_session_id_digest=SESSION).decision_kind is SessionResumeDecisionKind.QUARANTINE_WITHDRAWN_ANNOUNCEMENT
    hard = good_resume_signals()[:-1] + (resume_signal(SessionResumeSignalKind.ROUTER_SESSION, "router", hard_negative_clear=False, family="fam-c", path="path-b"),)
    assert assess_session_resume(hard, now=NOW + 1, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_session_id_digest=SESSION).decision_kind is SessionResumeDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESENT
    seen = good_resume_signals()[0].signal_digest
    assert assess_session_resume(good_resume_signals(), now=NOW + 1, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_session_id_digest=SESSION, previously_seen_signals=(seen,)).decision_kind is SessionResumeDecisionKind.QUARANTINE_REPLAY


def test_session_resume_blocks_kind_fork_drift_and_family_monoculture() -> None:
    fork = good_resume_signals() + (resume_signal(SessionResumeSignalKind.SERVICE_LEASE, "lease-other", family="fam-d", path="path-d"),)
    assert assess_session_resume(fork, now=NOW + 1, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_session_id_digest=SESSION).decision_kind is SessionResumeDecisionKind.QUARANTINE_KIND_FORK
    drift = good_resume_signals()[:-1] + (resume_signal(SessionResumeSignalKind.ROUTER_SESSION, "router", session_id_digest=d("other-session"), family="fam-c", path="path-b"),)
    assert assess_session_resume(drift, now=NOW + 1, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_session_id_digest=SESSION).decision_kind is SessionResumeDecisionKind.QUARANTINE_SESSION_DRIFT
    mono = tuple(resume_signal(sig.kind, sig.kind.value, family="one-family", path="one-path") for sig in good_resume_signals())
    assert assess_session_resume(mono, now=NOW + 1, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_session_id_digest=SESSION, policy=SessionResumePolicy(min_signal_families=2, min_path_families=2)).decision_kind is SessionResumeDecisionKind.HOLD_LOW_FAMILY_DIVERSITY


def test_exitjournal_accepts_chain_and_preserves_hard_negatives() -> None:
    hard_value = d("hard-negative-withdrawal")
    e0 = jentry(ExitJournalEntryKind.OPERATOR_INTENT, "intent", seq=0, prev=JOURNAL_ZERO)
    e1 = jentry(ExitJournalEntryKind.SERVICE_EXIT, "exit", seq=1, prev=e0.entry_digest)
    e2 = jentry(ExitJournalEntryKind.HARD_NEGATIVE, "hard", seq=2, prev=e1.entry_digest, hard_negative=True, value_digest=hard_value)
    report = assess_exit_journal((e0, e1, e2), expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, required_hard_negative_digests=(hard_value,))
    assert report.decision_kind is ExitJournalDecisionKind.ACCEPT_JOURNAL
    assert report.tip_digest == e2.entry_digest
    assert hard_value in report.hard_negative_digests


def test_exitjournal_blocks_bad_signature_replay_rollback_fork_prev_gap_and_drift() -> None:
    e0 = jentry(ExitJournalEntryKind.OPERATOR_INTENT, "intent", seq=0, prev=JOURNAL_ZERO)
    bad = replace(e0, service_name="other")
    assert assess_exit_journal((bad,), expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST).decision_kind is ExitJournalDecisionKind.QUARANTINE_BAD_SIGNATURE
    assert assess_exit_journal((e0,), expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, previously_seen_entries=(e0.entry_digest,)).decision_kind is ExitJournalDecisionKind.QUARANTINE_REPLAY
    assert assess_exit_journal((e0,), expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, previous_sequence=5).decision_kind is ExitJournalDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK
    fork = jentry(ExitJournalEntryKind.ROUTER_STOP, "stop", seq=0, prev=JOURNAL_ZERO)
    assert assess_exit_journal((e0, fork), expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST).decision_kind is ExitJournalDecisionKind.QUARANTINE_SEQUENCE_FORK
    bad_prev = jentry(ExitJournalEntryKind.SERVICE_EXIT, "exit", seq=1, prev=d("bad-prev"))
    assert assess_exit_journal((e0, bad_prev), expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST).decision_kind is ExitJournalDecisionKind.QUARANTINE_PREVIOUS_MISMATCH
    gap = jentry(ExitJournalEntryKind.SESSION_RESUME, "resume", seq=3, prev=e0.entry_digest)
    assert assess_exit_journal((e0, gap), expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST).decision_kind is ExitJournalDecisionKind.HOLD_GAP_NEEDS_REPLAY
    drift = jentry(ExitJournalEntryKind.SERVICE_EXIT, "exit", seq=1, prev=e0.entry_digest, scope_digest=d("other-scope"))
    assert assess_exit_journal((drift,), expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST).decision_kind is ExitJournalDecisionKind.QUARANTINE_SCOPE_DRIFT


def test_exitjournal_refuses_to_drop_required_hard_negative() -> None:
    e0 = jentry(ExitJournalEntryKind.OPERATOR_INTENT, "intent", seq=0, prev=JOURNAL_ZERO)
    missing = d("required-hard-negative")
    assert assess_exit_journal((e0,), expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, required_hard_negative_digests=(missing,)).decision_kind is ExitJournalDecisionKind.QUARANTINE_HARD_NEGATIVE_DROP


def test_controlfold_current_revision_path_passes() -> None:
    report = audit_control_fold(".", revision="rev0041")
    assert report.status == "pass"
    assert report.predecessor_status == "pass"
    assert report.foldmap_status == "pass"
    assert report.registry_status == "pass"
    assert report.surface_ledger_status == "pass"
