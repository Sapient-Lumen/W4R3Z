from __future__ import annotations

from dataclasses import replace

from i2p_dht_lab.checkpointlane import CheckpointAssessment, CheckpointDecision, CheckpointDecisionKind, StateCheckpoint
from i2p_dht_lab.foldreduce import audit_fold_reduce
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.identity import DhtKeypair
from i2p_dht_lab.journallane import JournalReplayDecisionKind, JournalReplayReport
from i2p_dht_lab.persistjoin import PersistJoinDecisionKind, PersistJoinPolicy, assess_persist_join
from i2p_dht_lab.persistlane import PersistLoadDecisionKind, PersistLoadReport
from i2p_dht_lab.samprobe import SamProbeCommand, SamProbeCommandKind, SamProbeDecisionKind, SamProbeProfile, build_sam_probe_plan, classify_sam_probe_transcript
from i2p_dht_lab.scopeledger import ScopeLedgerDecisionKind, ScopeLedgerReport
from i2p_dht_lab.storedebt import StoreDebtDecisionKind, StoreDebtReport


def d(label: str) -> bytes:
    return sha256(("rev0033:" + label).encode("utf-8"))


def kp(label: str) -> DhtKeypair:
    return DhtKeypair.from_seed(d("seed:" + label))


def persist_report(*, accept: bool = True, hard: int = 1, decision: PersistLoadDecisionKind = PersistLoadDecisionKind.ACCEPT_RELOADED_STATE) -> PersistLoadReport:
    return PersistLoadReport(
        decision_kind=decision,
        accept=accept,
        reason=decision.value,
        loaded=None,
        compacted_records=(),
        quarantine_digests=(d("persist-quarantine"),) if not accept else (),
        hard_negative_count=hard,
        report_digest=d("persist-report:" + decision.value + str(accept) + str(hard)),
    )


def journal_report(*, accept: bool = True, tip: bytes | None = None, decision: JournalReplayDecisionKind = JournalReplayDecisionKind.ACCEPT_REPLAYED_PREFIX) -> JournalReplayReport:
    tip = tip or d("journal-tip")
    return JournalReplayReport(
        decision_kind=decision,
        accept=accept,
        reason=decision.value,
        accepted_entries=(),
        quarantined_entry_digests=(d("journal-quarantine"),) if not accept else (),
        last_entry_digest=tip,
        highest_sequence=3,
        hard_negative_count=1,
        soft_count=2,
        crash_tail_bytes=11 if decision is JournalReplayDecisionKind.ACCEPT_REPLAYED_WITH_CRASH_TAIL else 0,
        report_digest=d("journal-report:" + decision.value + str(accept) + tip.hex()),
    )


def checkpoint(tip: bytes | None = None) -> StateCheckpoint:
    return StateCheckpoint.create(keypair=kp("checkpoint"), generation=1, prev_checkpoint_digest=b"\x00" * 32, journal_tip_digest=tip or d("journal-tip"), facts=(), issued_at=1_766_800_000)


def checkpoint_report(cp: StateCheckpoint, *, accept: bool = True, decision: CheckpointDecisionKind = CheckpointDecisionKind.ACCEPT_FIRST_CHECKPOINT) -> CheckpointAssessment:
    return CheckpointAssessment(
        checkpoint_digest=cp.checkpoint_digest,
        decision=CheckpointDecision(decision, accept, decision.value),
        generation=cp.generation,
        hard_fact_drops=(),
        conflict_fact_digests=(),
        report_digest=d("checkpoint-report:" + decision.value + str(accept)),
    )


def scope_report(*, accept: bool = True, open_obligations: int = 0, decision: ScopeLedgerDecisionKind = ScopeLedgerDecisionKind.ACCEPT_STICKY_SCOPE_ADVANCE) -> ScopeLedgerReport:
    return ScopeLedgerReport(
        decision_kind=decision,
        accept=accept,
        reason=decision.value,
        observation_digests=(d("scope-obs-a"), d("scope-obs-b")),
        source_families=("source-A", "source-B"),
        path_families=("path-A", "path-B"),
        open_obligation_count=open_obligations,
        pressure_digests=(d("scope-pressure"),) if open_obligations or not accept else (),
        report_digest=d("scope-report:" + decision.value + str(accept) + str(open_obligations)),
    )


def store_report(*, accept: bool = True, decision: StoreDebtDecisionKind = StoreDebtDecisionKind.ACCEPT_NO_STORE_DEBT) -> StoreDebtReport:
    return StoreDebtReport(
        decision_kind=decision,
        accept=accept,
        reason=decision.value,
        observation_digests=(d("store-obs-a"), d("store-obs-b")),
        source_families=("store-A", "store-B"),
        path_families=("store-path-A", "store-path-B"),
        max_replica_count=3,
        max_custody_count=2,
        tombstone_digests=(d("store-tomb"),) if decision is StoreDebtDecisionKind.QUARANTINE_LIVE_TOMBSTONE else (),
        pressure_digests=(d("store-pressure"),) if not accept else (),
        report_digest=d("store-report:" + decision.value + str(accept)),
    )


def test_persistjoin_accepts_linked_restart_boundary() -> None:
    cp = checkpoint()
    report = assess_persist_join(
        persist_report=persist_report(hard=1),
        journal_report=journal_report(tip=cp.journal_tip_digest),
        checkpoint_report=checkpoint_report(cp),
        scope_report=scope_report(),
        store_report=store_report(),
        checkpoint=cp,
        policy=PersistJoinPolicy(required_hard_negative_count=1),
    )
    assert report.decision_kind is PersistJoinDecisionKind.ACCEPT_DURABLE_JOIN
    assert report.accept
    assert report.journal_tip_digest == cp.journal_tip_digest


def test_persistjoin_rejects_checkpoint_journal_tip_mismatch() -> None:
    cp = checkpoint(tip=d("checkpoint-tip"))
    report = assess_persist_join(
        persist_report=persist_report(hard=1),
        journal_report=journal_report(tip=d("different-journal-tip")),
        checkpoint_report=checkpoint_report(cp),
        scope_report=scope_report(),
        store_report=store_report(),
        checkpoint=cp,
        policy=PersistJoinPolicy(required_hard_negative_count=1),
    )
    assert report.decision_kind is PersistJoinDecisionKind.QUARANTINE_CHECKPOINT_JOURNAL_TIP
    assert not report.accept


def test_persistjoin_keeps_scope_store_and_hard_negative_debt_visible() -> None:
    cp = checkpoint()
    debt = assess_persist_join(
        persist_report=persist_report(hard=1),
        journal_report=journal_report(tip=cp.journal_tip_digest),
        checkpoint_report=checkpoint_report(cp),
        scope_report=scope_report(open_obligations=2),
        store_report=store_report(),
        checkpoint=cp,
    )
    assert debt.decision_kind is PersistJoinDecisionKind.HOLD_SCOPE_PROOF_DEBT

    repair = assess_persist_join(
        persist_report=persist_report(hard=1),
        journal_report=journal_report(tip=cp.journal_tip_digest),
        checkpoint_report=checkpoint_report(cp),
        scope_report=scope_report(),
        store_report=store_report(accept=False, decision=StoreDebtDecisionKind.PLAN_REPAIR_REPLICAS),
        checkpoint=cp,
    )
    assert repair.decision_kind is PersistJoinDecisionKind.HOLD_STORE_REPAIR_DEBT

    dropped = assess_persist_join(
        persist_report=persist_report(hard=0),
        journal_report=journal_report(tip=cp.journal_tip_digest),
        checkpoint_report=checkpoint_report(cp),
        scope_report=scope_report(),
        store_report=store_report(),
        checkpoint=cp,
        policy=PersistJoinPolicy(required_hard_negative_count=1),
    )
    assert dropped.decision_kind is PersistJoinDecisionKind.QUARANTINE_HARD_NEGATIVE_DROP


def test_persistjoin_accepts_crash_tail_only_as_watch() -> None:
    cp = checkpoint()
    report = assess_persist_join(
        persist_report=persist_report(hard=1),
        journal_report=journal_report(tip=cp.journal_tip_digest, decision=JournalReplayDecisionKind.ACCEPT_REPLAYED_WITH_CRASH_TAIL),
        checkpoint_report=checkpoint_report(cp),
        scope_report=scope_report(),
        store_report=store_report(),
        checkpoint=cp,
    )
    assert report.decision_kind is PersistJoinDecisionKind.ACCEPT_WITH_CRASH_TAIL_WATCH
    assert report.accept


def test_samprobe_accepts_local_unavailable_as_safe_no_router_outcome() -> None:
    profile = SamProbeProfile()
    commands = build_sam_probe_plan(profile)
    report = classify_sam_probe_transcript(profile, commands, (), router_unavailable=True)
    assert report.decision_kind is SamProbeDecisionKind.ACCEPT_LOCAL_UNAVAILABLE
    assert report.accept
    assert len(report.command_digests) == len(commands)


def test_samprobe_accepts_streaming_first_ok_transcript() -> None:
    profile = SamProbeProfile()
    commands = build_sam_probe_plan(profile)
    replies = (
        "HELLO REPLY RESULT=OK VERSION=3.1",
        "DEST REPLY RESULT=OK PUB=abc PRIV=def",
        "SESSION STATUS RESULT=OK DESTINATION=abc",
        "NAMING REPLY RESULT=OK NAME=example.b32.i2p VALUE=dest",
        "STREAM STATUS RESULT=OK ID=i2p-dht-probe",
    )
    report = classify_sam_probe_transcript(profile, commands, replies)
    assert report.decision_kind is SamProbeDecisionKind.ACCEPT_STREAMING_FIRST_PROBE
    assert report.accept


def test_samprobe_refuses_external_datagram_and_ephemeral_surfaces() -> None:
    commands = build_sam_probe_plan(SamProbeProfile())
    external = classify_sam_probe_transcript(SamProbeProfile(host="192.0.2.5"), commands, (), router_unavailable=True)
    assert external.decision_kind is SamProbeDecisionKind.QUARANTINE_EXTERNAL_SAM

    datagram = classify_sam_probe_transcript(SamProbeProfile(datagram_primary=True), commands, (), router_unavailable=True)
    assert datagram.decision_kind is SamProbeDecisionKind.QUARANTINE_DATAGRAM_PRIMARY

    bad_commands = (
        SamProbeCommand.create(SamProbeCommandKind.HELLO, MIN="3.1", MAX="3.3"),
        SamProbeCommand.create(SamProbeCommandKind.DEST_GENERATE, SIGNATURE_TYPE=7),
        SamProbeCommand.create(SamProbeCommandKind.SESSION_CREATE, STYLE="STREAM", ID="i2p-dht-probe", DESTINATION="TRANSIENT"),
    )
    reply = ("HELLO REPLY RESULT=OK VERSION=3.1", "DEST REPLY RESULT=OK", "SESSION STATUS RESULT=OK")
    ephemeral = classify_sam_probe_transcript(SamProbeProfile(), bad_commands, reply)
    assert ephemeral.decision_kind is SamProbeDecisionKind.QUARANTINE_OPTION_DRIFT


def test_samprobe_catches_bad_order_and_router_rejection() -> None:
    profile = SamProbeProfile()
    wrong_order = (
        SamProbeCommand.create(SamProbeCommandKind.SESSION_CREATE, STYLE="STREAM", ID="i2p-dht-probe", DESTINATION="persistent"),
        SamProbeCommand.create(SamProbeCommandKind.HELLO, MIN="3.1", MAX="3.3"),
        SamProbeCommand.create(SamProbeCommandKind.DEST_GENERATE, SIGNATURE_TYPE=7),
    )
    ok_replies = ("SESSION STATUS RESULT=OK", "HELLO REPLY RESULT=OK", "DEST REPLY RESULT=OK")
    bad_order = classify_sam_probe_transcript(profile, wrong_order, ok_replies)
    assert bad_order.decision_kind is SamProbeDecisionKind.QUARANTINE_BAD_ORDER

    commands = build_sam_probe_plan(profile)
    rejected = classify_sam_probe_transcript(profile, commands, ("HELLO REPLY RESULT=I2P_ERROR MESSAGE=nope",))
    assert rejected.decision_kind is SamProbeDecisionKind.HOLD_ROUTER_REJECTED
    assert not rejected.accept


def test_foldreduce_current_revision_audit_passes() -> None:
    report = audit_fold_reduce(".")
    assert report.status == "pass"
    assert report.error_count == 0
    assert report.predecessor_status == "pass"
    assert report.surface_ledger_status == "pass"
