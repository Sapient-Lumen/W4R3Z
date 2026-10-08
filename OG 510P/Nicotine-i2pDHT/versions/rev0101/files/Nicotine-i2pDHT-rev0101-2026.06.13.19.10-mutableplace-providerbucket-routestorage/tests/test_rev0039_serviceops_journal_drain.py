from __future__ import annotations

from dataclasses import replace

from i2p_dht_lab.ids import sha256
from i2p_dht_lab.servicehealth import (
    ServiceHealthDecisionKind,
    ServiceHealthObservation,
    ServiceHealthObservationKind,
    ServiceHealthPolicy,
    assess_service_health,
)
from i2p_dht_lab.servicedrain import (
    DrainItemKind,
    DrainState,
    ServiceDrainDecisionKind,
    ServiceDrainItem,
    ServiceDrainPolicy,
    assess_service_drain,
)
from i2p_dht_lab.continuityjournal import (
    ContinuityJournalDecisionKind,
    ContinuityJournalEntry,
    ContinuityJournalEntryKind,
    ZERO_DIGEST,
    replay_continuity_journal,
)
from i2p_dht_lab.serviceopsfold import audit_serviceops_fold


def d(label: str) -> bytes:
    return sha256(b"rev0039-test:" + label.encode())


SCOPE = d("scope")
SERVICE = "head_watch"
NOW = 1_000


HEALTH_POLICY = ServiceHealthPolicy(
    required_kinds=(
        ServiceHealthObservationKind.CONTINUITY_ACCEPTED,
        ServiceHealthObservationKind.PROBE_OK,
        ServiceHealthObservationKind.RECEIPT_COMPLETED,
        ServiceHealthObservationKind.LOAD_OK,
    ),
    min_families=2,
    min_positive_observations=3,
    max_refusal_ratio_percent=50,
    max_raw_key_exposure=0,
    max_metadata_bytes=1024,
)


def obs(kind: ServiceHealthObservationKind, label: str, *, family: str = "a", service: str = SERVICE, scope: bytes = SCOPE, issued: int = 990, expires: int = 1_010, accept: bool = True, refused: bool = False, quarantined: bool = False, raw: int = 0, meta: int = 10) -> ServiceHealthObservation:
    return ServiceHealthObservation(
        kind=kind,
        service_name=service,
        scope_digest=scope,
        observation_digest=d("obs:" + label),
        family_id=family,
        issued_at=issued,
        expires_at=expires,
        branch=kind.value,
        accept=accept,
        refused_usefully=refused,
        quarantined=quarantined,
        raw_key_exposure=raw,
        metadata_bytes=meta,
    )


def healthy_observations() -> tuple[ServiceHealthObservation, ...]:
    return (
        obs(ServiceHealthObservationKind.CONTINUITY_ACCEPTED, "continuity", family="a"),
        obs(ServiceHealthObservationKind.PROBE_OK, "probe", family="b"),
        obs(ServiceHealthObservationKind.RECEIPT_COMPLETED, "receipt", family="a"),
        obs(ServiceHealthObservationKind.LOAD_OK, "load", family="b"),
    )


def test_service_health_accepts_diverse_budgeted_post_continuity_window() -> None:
    report = assess_service_health(healthy_observations(), policy=HEALTH_POLICY, now=NOW, expected_service=SERVICE, expected_scope_digest=SCOPE)
    assert report.accept
    assert report.decision_kind is ServiceHealthDecisionKind.ACCEPT_HEALTHY_CONTINUE
    assert report.families == ("a", "b")
    assert report.raw_key_exposure == 0


def test_service_health_rejects_active_withdrawal_replay_metadata_and_monoculture() -> None:
    base = healthy_observations()
    active = base + (obs(ServiceHealthObservationKind.WITHDRAWAL_ACTIVE, "withdrawal", family="c"),)
    assert assess_service_health(active, policy=HEALTH_POLICY, now=NOW).decision_kind is ServiceHealthDecisionKind.QUARANTINE_WITHDRAWAL_ACTIVE

    replay = assess_service_health(base, policy=HEALTH_POLICY, now=NOW, previously_seen_observations=(base[0].observation_digest,))
    assert replay.decision_kind is ServiceHealthDecisionKind.QUARANTINE_REPLAY

    metadata = tuple(replace(item, raw_key_exposure=1) if item.kind is ServiceHealthObservationKind.PROBE_OK else item for item in base)
    assert assess_service_health(metadata, policy=HEALTH_POLICY, now=NOW).decision_kind is ServiceHealthDecisionKind.QUARANTINE_METADATA_BUDGET

    mono = tuple(replace(item, family_id="captured") for item in base)
    assert assess_service_health(mono, policy=HEALTH_POLICY, now=NOW).decision_kind is ServiceHealthDecisionKind.QUARANTINE_FAMILY_MONOCULTURE


def test_service_health_detects_refusal_loops_and_scope_drift() -> None:
    policy = ServiceHealthPolicy(
        required_kinds=(ServiceHealthObservationKind.RECEIPT_REFUSED, ServiceHealthObservationKind.LOAD_REFUSED),
        min_families=2,
        min_positive_observations=1,
        max_refusal_ratio_percent=50,
    )
    refusal_only = (
        obs(ServiceHealthObservationKind.RECEIPT_REFUSED, "receipt-refused", family="a", refused=True),
        obs(ServiceHealthObservationKind.LOAD_REFUSED, "load-refused", family="b", refused=True),
    )
    assert assess_service_health(refusal_only, policy=policy, now=NOW).decision_kind is ServiceHealthDecisionKind.QUARANTINE_REFUSAL_ONLY_LOOP

    drift = healthy_observations()[:-1] + (obs(ServiceHealthObservationKind.LOAD_OK, "load-drift", family="b", scope=d("other-scope")),)
    assert assess_service_health(drift, policy=HEALTH_POLICY, now=NOW).decision_kind is ServiceHealthDecisionKind.QUARANTINE_SCOPE_DRIFT


def drain_item(kind: DrainItemKind, state: DrainState, label: str, *, service: str = SERVICE, scope: bytes = SCOPE, request: bytes | None = None, protected: bool = False, receipt_for: bytes | None = None, issued: int = 900, expires: int = 1_100) -> ServiceDrainItem:
    return ServiceDrainItem(
        kind=kind,
        state=state,
        service_name=service,
        scope_digest=scope,
        item_digest=d("drain:" + label),
        issued_at=issued,
        expires_at=expires,
        request_digest=request,
        family_id="family-" + label[:1],
        protected=protected,
        receipt_for=receipt_for,
    )


def closed_drain_items() -> tuple[ServiceDrainItem, ...]:
    ticket = drain_item(DrainItemKind.TICKET, DrainState.COMPLETED, "ticket", request=d("request"))
    return (
        ticket,
        drain_item(DrainItemKind.RECEIPT, DrainState.COMPLETED, "receipt", receipt_for=ticket.item_digest),
        drain_item(DrainItemKind.WITHDRAWAL, DrainState.WITHDRAWN, "withdrawal"),
        drain_item(DrainItemKind.HARD_NEGATIVE, DrainState.HARD_NEGATIVE, "hard-negative"),
    )


def test_service_drain_accepts_closed_withdrawn_hard_negative_preserving_window() -> None:
    items = closed_drain_items()
    policy = ServiceDrainPolicy(required_hard_negative_digests=(items[-1].item_digest,))
    report = assess_service_drain(items, policy=policy, now=NOW, expected_service=SERVICE, expected_scope_digest=SCOPE)
    assert report.accept
    assert report.decision_kind is ServiceDrainDecisionKind.ACCEPT_SAFE_DRAIN
    assert items[0].item_digest in report.closed_work_digests


def test_service_drain_holds_inflight_public_announcement_and_missing_receipts() -> None:
    policy = ServiceDrainPolicy()
    open_ticket = drain_item(DrainItemKind.TICKET, DrainState.OPEN, "open-ticket")
    with_open = (open_ticket, drain_item(DrainItemKind.WITHDRAWAL, DrainState.WITHDRAWN, "withdrawal"))
    assert assess_service_drain(with_open, policy=policy, now=NOW).decision_kind is ServiceDrainDecisionKind.HOLD_INFLIGHT_WORK

    public_live = closed_drain_items() + (drain_item(DrainItemKind.PUBLIC_ANNOUNCEMENT, DrainState.OPEN, "announce"),)
    assert assess_service_drain(public_live, policy=policy, now=NOW).decision_kind is ServiceDrainDecisionKind.HOLD_PUBLIC_ANNOUNCEMENT_LIVE

    ticket_only = (drain_item(DrainItemKind.TICKET, DrainState.COMPLETED, "ticket-no-receipt"), drain_item(DrainItemKind.WITHDRAWAL, DrainState.WITHDRAWN, "withdrawal-2"))
    assert assess_service_drain(ticket_only, policy=policy, now=NOW).decision_kind is ServiceDrainDecisionKind.HOLD_MISSING_RECEIPTS


def test_service_drain_quarantines_protected_stop_hard_negative_drop_and_drift() -> None:
    protected = (
        drain_item(DrainItemKind.TICKET, DrainState.OPEN, "protected", protected=True),
        drain_item(DrainItemKind.WITHDRAWAL, DrainState.WITHDRAWN, "withdrawal"),
    )
    policy = ServiceDrainPolicy(max_pending_work=1)
    assert assess_service_drain(protected, policy=policy, now=NOW).decision_kind is ServiceDrainDecisionKind.QUARANTINE_PROTECTED_SERVICE_STOP

    missing_hard_policy = ServiceDrainPolicy(required_hard_negative_digests=(d("must-preserve"),))
    assert assess_service_drain(closed_drain_items(), policy=missing_hard_policy, now=NOW).decision_kind is ServiceDrainDecisionKind.QUARANTINE_HARD_NEGATIVE_DROP

    drift = closed_drain_items()[:-1] + (drain_item(DrainItemKind.HARD_NEGATIVE, DrainState.HARD_NEGATIVE, "hard-drift", scope=d("other-scope")),)
    assert assess_service_drain(drift, policy=ServiceDrainPolicy(), now=NOW).decision_kind is ServiceDrainDecisionKind.QUARANTINE_SCOPE_DRIFT


def journal_entry(seq: int, kind: ContinuityJournalEntryKind, label: str, *, prev: bytes = ZERO_DIGEST, accepted: bool = False, hard: tuple[bytes, ...] = (), service: str = SERVICE, scope: bytes = SCOPE) -> ContinuityJournalEntry:
    return ContinuityJournalEntry(
        sequence=seq,
        kind=kind,
        service_name=service,
        scope_digest=scope,
        continuity_report_digest=d("journal-report:" + label),
        previous_entry_digest=prev,
        accepted=accepted,
        hard_negative_digests=hard,
    )


def journal_chain() -> tuple[ContinuityJournalEntry, ...]:
    e0 = journal_entry(0, ContinuityJournalEntryKind.ACCEPTED_CONTINUITY, "0", accepted=True)
    e1 = journal_entry(1, ContinuityJournalEntryKind.HARD_NEGATIVE, "1", prev=e0.entry_digest, hard=(d("hard"),))
    e2 = journal_entry(2, ContinuityJournalEntryKind.WITHDRAWAL, "2", prev=e1.entry_digest)
    return (e0, e1, e2)


def test_continuity_journal_rehydrates_monotonic_hard_negative_memory() -> None:
    chain = journal_chain()
    report = replay_continuity_journal(chain, expected_service=SERVICE, expected_scope_digest=SCOPE, required_hard_negative_digests=(d("hard"),))
    assert report.accept
    assert report.decision_kind is ContinuityJournalDecisionKind.ACCEPT_REHYDRATED_MEMORY
    assert report.highest_sequence == 2
    assert d("hard") in report.hard_negative_digests


def test_continuity_journal_detects_forks_prev_mismatch_and_hard_negative_drop() -> None:
    chain = journal_chain()
    fork = chain + (journal_entry(1, ContinuityJournalEntryKind.ACCEPTED_CONTINUITY, "fork", prev=chain[0].entry_digest, accepted=True),)
    assert replay_continuity_journal(fork).decision_kind is ContinuityJournalDecisionKind.QUARANTINE_SEQUENCE_FORK

    bad_prev = (chain[0], replace(chain[1], previous_entry_digest=d("bad-prev")), chain[2])
    assert replay_continuity_journal(bad_prev).decision_kind is ContinuityJournalDecisionKind.QUARANTINE_PREVIOUS_LINK

    assert replay_continuity_journal(chain, required_hard_negative_digests=(d("missing-hard"),)).decision_kind is ContinuityJournalDecisionKind.QUARANTINE_HARD_NEGATIVE_DROP


def test_continuity_journal_detects_rollback_gap_replay_and_scope_drift() -> None:
    chain = journal_chain()
    assert replay_continuity_journal(chain, known_highest_sequence=1).decision_kind is ContinuityJournalDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK
    assert replay_continuity_journal((chain[0], chain[2])).decision_kind is ContinuityJournalDecisionKind.HOLD_GAP_OR_CRASH_TAIL
    assert replay_continuity_journal((chain[0], chain[0])).decision_kind is ContinuityJournalDecisionKind.QUARANTINE_REPLAY
    drift1 = replace(chain[1], scope_digest=d("other"))
    drift2 = replace(chain[2], previous_entry_digest=drift1.entry_digest)
    drift = (chain[0], drift1, drift2)
    assert replay_continuity_journal(drift).decision_kind is ContinuityJournalDecisionKind.QUARANTINE_SCOPE_DRIFT


def test_serviceopsfold_audits_current_revision() -> None:
    report = audit_serviceops_fold(".", revision="rev0039", artifact_stem="Nicotine-i2pDHT-rev0039-2026.06.04.06.15-continuityjournal-probeloop-successionrepair")
    assert report.status == "pass"
    assert report.error_count == 0
    assert report.predecessor_status == "pass"
    assert report.foldmap_status == "pass"
    assert report.registry_status == "pass"
