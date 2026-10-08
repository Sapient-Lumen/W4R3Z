from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from i2p_dht_lab.admissionwall import AdmissionDecisionKind, AdmissionReceipt, AdmissionRefusalReason
from i2p_dht_lab.claimbundle import ClaimBundle, ClaimBundleDecisionKind, ClaimBundlePolicy, assess_claim_bundle
from i2p_dht_lab.evidencegc import EvidenceItem, EvidenceKind
from i2p_dht_lab.identity import DhtKeypair
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.lineagefold import audit_lineage_fold
from i2p_dht_lab.lineagewindow import (
    HeadLineageObservation,
    HeadMemoryAnchor,
    LineageDecisionKind,
    LineageWindowPolicy,
    analyze_lineage_window,
)
from i2p_dht_lab.workmeter import WorkEvent, WorkEventKind, WorkMeterDecisionKind, WorkMeterPolicy, meter_work_window


def kp(n: int) -> DhtKeypair:
    return DhtKeypair.from_seed(bytes([n]) * 32)


def digest(label: str) -> bytes:
    return sha256(label.encode("utf-8"))


def head(writer: DhtKeypair, *, scope: bytes, seq: int, prev: bytes, payload: str, source: str, path: str, now: int) -> HeadLineageObservation:
    return HeadLineageObservation.create(
        writer=writer,
        scope_id=scope,
        sequence=seq,
        prev_digest=prev,
        payload_digest=digest(payload),
        source_family=source,
        path_family=path,
        issued_at=now,
        ttl=600,
    )


def evidence(kind: EvidenceKind, *, scope: bytes, obj: str, source: str, path: str, now: int, seq: int = 0) -> EvidenceItem:
    return EvidenceItem(kind, scope, digest(obj), source, path, now - 10, now + 600, sequence=seq)


def work(kind: WorkEventKind, *, garden: DhtKeypair, scope: bytes, subject: str, source: str, path: str, now: int, cost: int = 1, receipt: AdmissionReceipt | None = None) -> WorkEvent:
    return WorkEvent.create(
        garden=garden,
        event_kind=kind,
        scope_id=scope,
        subject_digest=digest(subject),
        source_family=source,
        path_family=path,
        unit_cost=cost,
        issued_at=now,
        ttl=600,
        receipt=receipt,
    )


def test_lineage_window_accepts_diverse_direct_linked_advance() -> None:
    now = 1_765_309_000
    scope = digest("lineage-scope")
    writer = kp(1)
    old = digest("head-7")
    memory = HeadMemoryAnchor(scope, sequence=7, head_digest=old)
    a = head(writer, scope=scope, seq=8, prev=old, payload="head-8", source="fam-A", path="path-A", now=now)
    b = replace(a, source_family="fam-B", path_family="path-B", signature=writer.sign(replace(a, source_family="fam-B", path_family="path-B", signature=b"").unsigned_payload()))
    report = analyze_lineage_window((a, b), memory=memory, now=now + 1)
    assert report.decision.kind is LineageDecisionKind.ACCEPT_LINKED_ADVANCE
    assert report.decision.accept
    assert report.selected is not None and report.selected.head_digest == a.head_digest
    assert set(report.source_families) == {"fam-A", "fam-B"}


def test_lineage_window_requests_predecessor_when_signed_latest_jumps_history() -> None:
    now = 1_765_309_000
    scope = digest("lineage-gap")
    writer = kp(2)
    memory = HeadMemoryAnchor(scope, sequence=7, head_digest=digest("head-7"))
    latest = head(writer, scope=scope, seq=14, prev=digest("head-13"), payload="head-14", source="fam-A", path="path-A", now=now)
    report = analyze_lineage_window((latest,), memory=memory, now=now + 1)
    assert report.decision.kind is LineageDecisionKind.CONTINUE_MISSING_PREV
    assert report.should_continue
    assert report.repair_requests and report.repair_requests[0].wanted_prev_digest == latest.prev_digest


def test_lineage_window_quarantines_same_sequence_fork_before_family_counting() -> None:
    now = 1_765_309_000
    scope = digest("lineage-fork")
    writer = kp(3)
    old = digest("head-9")
    memory = HeadMemoryAnchor(scope, sequence=9, head_digest=old)
    a = head(writer, scope=scope, seq=10, prev=old, payload="branch-A", source="fam-A", path="path-A", now=now)
    b = head(writer, scope=scope, seq=10, prev=old, payload="branch-B", source="fam-B", path="path-B", now=now)
    report = analyze_lineage_window((a, b), memory=memory, now=now + 1)
    assert report.decision.kind is LineageDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK
    assert report.quarantined
    assert set(report.quarantine_digests) == {a.head_digest, b.head_digest}


def test_lineage_window_does_not_commit_one_family_direct_advance() -> None:
    now = 1_765_309_000
    scope = digest("lineage-mono")
    writer = kp(4)
    old = digest("head-1")
    memory = HeadMemoryAnchor(scope, sequence=1, head_digest=old)
    latest = head(writer, scope=scope, seq=2, prev=old, payload="head-2", source="fam-A", path="path-A", now=now)
    report = analyze_lineage_window((latest,), memory=memory, now=now + 1, policy=LineageWindowPolicy(min_source_families_for_commit=2, min_path_families_for_commit=2))
    assert report.decision.kind is LineageDecisionKind.CONTINUE_UNDER_DIVERSE
    assert not report.decision.accept


def test_lineage_window_quarantines_scope_mix_and_bad_signature() -> None:
    now = 1_765_309_000
    scope = digest("lineage-scope-a")
    other_scope = digest("lineage-scope-b")
    writer = kp(5)
    memory = HeadMemoryAnchor(scope, sequence=1, head_digest=digest("head-1"))
    mixed = head(writer, scope=other_scope, seq=2, prev=memory.head_digest, payload="bad-scope", source="fam-A", path="path-A", now=now)
    assert analyze_lineage_window((mixed,), memory=memory, now=now + 1).decision.kind is LineageDecisionKind.QUARANTINE_SCOPE_MIX
    valid = head(writer, scope=scope, seq=2, prev=memory.head_digest, payload="valid", source="fam-A", path="path-A", now=now)
    tampered = replace(valid, signature=b"0" * 64)
    assert analyze_lineage_window((tampered,), memory=memory, now=now + 1).decision.kind is LineageDecisionKind.QUARANTINE_BAD_SIGNATURE


def test_claim_bundle_accepts_signed_scoped_diverse_nonconflicting_evidence() -> None:
    now = 1_765_309_100
    scope = digest("bundle-good")
    bundle = ClaimBundle.create(
        bundler=kp(10),
        scope_id=scope,
        bundle_sequence=1,
        evidence=(
            evidence(EvidenceKind.PROVIDER_TRUE, scope=scope, obj="provider", source="fam-A", path="path-A", now=now),
            evidence(EvidenceKind.CUSTODY_PROOF, scope=scope, obj="custody", source="fam-B", path="path-B", now=now),
        ),
        issued_at=now,
    )
    report = assess_claim_bundle(bundle, now=now + 1)
    assert report.decision.kind is ClaimBundleDecisionKind.ACCEPT_BUNDLE
    assert report.decision.accept
    assert report.positive_count == 2


def test_claim_bundle_rejects_bad_signature_and_expiry() -> None:
    now = 1_765_309_100
    scope = digest("bundle-sig")
    bundle = ClaimBundle.create(
        bundler=kp(11),
        scope_id=scope,
        bundle_sequence=1,
        evidence=(evidence(EvidenceKind.PROVIDER_TRUE, scope=scope, obj="provider", source="fam-A", path="path-A", now=now),),
        issued_at=now,
        ttl=10,
    )
    assert assess_claim_bundle(bundle, now=now + 11).decision.kind is ClaimBundleDecisionKind.REJECT_TIME_WINDOW
    assert assess_claim_bundle(replace(bundle, signature=b"1" * 64), now=now + 1).decision.kind is ClaimBundleDecisionKind.REJECT_BAD_SIGNATURE


def test_claim_bundle_quarantines_scope_mix_and_monoculture() -> None:
    now = 1_765_309_100
    scope = digest("bundle-scope-a")
    other = digest("bundle-scope-b")
    mixed = ClaimBundle.create(
        bundler=kp(12),
        scope_id=scope,
        bundle_sequence=1,
        evidence=(
            evidence(EvidenceKind.PROVIDER_TRUE, scope=scope, obj="provider", source="fam-A", path="path-A", now=now),
            evidence(EvidenceKind.CUSTODY_PROOF, scope=other, obj="custody", source="fam-B", path="path-B", now=now),
        ),
        issued_at=now,
    )
    assert assess_claim_bundle(mixed, now=now + 1).decision.kind is ClaimBundleDecisionKind.QUARANTINE_SCOPE_MIX
    mono = ClaimBundle.create(
        bundler=kp(13),
        scope_id=scope,
        bundle_sequence=1,
        evidence=(
            evidence(EvidenceKind.PROVIDER_TRUE, scope=scope, obj="a", source="fam-A", path="path-A", now=now),
            evidence(EvidenceKind.CUSTODY_PROOF, scope=scope, obj="b", source="fam-A", path="path-A", now=now),
        ),
        issued_at=now,
    )
    assert assess_claim_bundle(mono, now=now + 1).decision.kind is ClaimBundleDecisionKind.QUARANTINE_FAMILY_MONOCULTURE


def test_claim_bundle_quarantines_positive_plus_live_tombstone_and_same_seq_conflict() -> None:
    now = 1_765_309_100
    scope = digest("bundle-conflict")
    conflict = ClaimBundle.create(
        bundler=kp(14),
        scope_id=scope,
        bundle_sequence=1,
        evidence=(
            evidence(EvidenceKind.PROVIDER_TRUE, scope=scope, obj="provider", source="fam-A", path="path-A", now=now, seq=4),
            evidence(EvidenceKind.TOMBSTONE, scope=scope, obj="tomb", source="fam-B", path="path-B", now=now, seq=4),
        ),
        issued_at=now,
    )
    assert assess_claim_bundle(conflict, now=now + 1).decision.kind is ClaimBundleDecisionKind.QUARANTINE_CONFLICTING_CLAIMS
    fork = ClaimBundle.create(
        bundler=kp(15),
        scope_id=scope,
        bundle_sequence=1,
        evidence=(
            evidence(EvidenceKind.MUTABLE_LATEST, scope=scope, obj="latest-a", source="fam-A", path="path-A", now=now, seq=8),
            evidence(EvidenceKind.MUTABLE_LATEST, scope=scope, obj="latest-b", source="fam-B", path="path-B", now=now, seq=8),
        ),
        issued_at=now,
    )
    assert assess_claim_bundle(fork, now=now + 1).decision.kind is ClaimBundleDecisionKind.QUARANTINE_CONFLICTING_CLAIMS


def test_work_meter_accepts_diverse_served_work_and_tracks_refusal_without_currency() -> None:
    now = 1_765_309_200
    scope = digest("work-good")
    garden = kp(20)
    report = meter_work_window(
        (
            work(WorkEventKind.SERVED_HEAD, garden=garden, scope=scope, subject="head", source="fam-A", path="path-A", now=now, cost=2),
            work(WorkEventKind.SERVED_WITNESS, garden=garden, scope=scope, subject="witness", source="fam-B", path="path-B", now=now, cost=1),
            work(WorkEventKind.REFUSED_USEFULLY, garden=garden, scope=scope, subject="refusal", source="fam-C", path="path-C", now=now, cost=1),
        ),
        now=now + 1,
        policy=WorkMeterPolicy(min_served_units=2, min_source_families=2, max_refusal_ratio=0.50),
    )
    assert report.decision_kind is WorkMeterDecisionKind.HEALTHY_CONTRIBUTION
    assert report.healthy
    assert report.served_units == 3
    assert report.refused_units == 1


def test_work_meter_quarantines_refusal_only_and_replayed_receipts() -> None:
    now = 1_765_309_200
    scope = digest("work-refusal")
    garden = kp(21)
    receipt = AdmissionReceipt.create(
        keypair=garden,
        garden_node_id=digest("garden-node"),
        request_digest=digest("request"),
        decision=AdmissionDecisionKind.REFUSE_USEFULLY,
        reason=AdmissionRefusalReason.OVER_STREAM_BUDGET,
        issued_at=now,
    )
    refusal_a = work(WorkEventKind.REFUSED_USEFULLY, garden=garden, scope=scope, subject="a", source="fam-A", path="path-A", now=now, receipt=receipt)
    refusal_b = work(WorkEventKind.REFUSED_USEFULLY, garden=garden, scope=scope, subject="b", source="fam-B", path="path-B", now=now, receipt=receipt)
    replay = meter_work_window((refusal_a, refusal_b), now=now + 1)
    assert replay.decision_kind is WorkMeterDecisionKind.QUARANTINE_RECEIPT_REPLAY
    refusal_only = meter_work_window((refusal_a,), now=now + 1, policy=WorkMeterPolicy(min_source_families=1))
    assert refusal_only.decision_kind is WorkMeterDecisionKind.QUARANTINE_REFUSAL_ONLY


def test_work_meter_flags_under_diverse_and_family_flood() -> None:
    now = 1_765_309_200
    scope = digest("work-diversity")
    garden = kp(22)
    under = meter_work_window(
        (work(WorkEventKind.SERVED_REPAIR, garden=garden, scope=scope, subject="a", source="fam-A", path="path-A", now=now, cost=3),),
        now=now + 1,
        policy=WorkMeterPolicy(min_source_families=2),
    )
    assert under.decision_kind is WorkMeterDecisionKind.WATCH_UNDER_DIVERSE
    flood_events = tuple(work(WorkEventKind.SERVED_PROVIDER_PROOF, garden=garden, scope=scope, subject=f"x-{i}", source="fam-A", path=f"path-{i}", now=now) for i in range(4))
    flood = meter_work_window(flood_events, now=now + 1, policy=WorkMeterPolicy(min_source_families=1, max_events_per_family=2))
    assert flood.decision_kind is WorkMeterDecisionKind.QUARANTINE_FAMILY_FLOOD
    assert flood.quarantined


def test_work_meter_quarantines_bad_signature() -> None:
    now = 1_765_309_200
    scope = digest("work-bad-sig")
    event = work(WorkEventKind.SERVED_SEED_GATE, garden=kp(23), scope=scope, subject="seed", source="fam-A", path="path-A", now=now)
    tampered = replace(event, signature=b"2" * 64)
    report = meter_work_window((tampered,), now=now + 1)
    assert report.decision_kind is WorkMeterDecisionKind.QUARANTINE_INVALID_EVENT
    assert report.quarantined_event_digests


def test_lineagefold_audit_pins_current_revision_surfaces() -> None:
    root = Path(__file__).resolve().parents[1]
    report = audit_lineage_fold(root, revision="rev0026")
    assert report.status == "pass"
    assert report.error_count == 0
