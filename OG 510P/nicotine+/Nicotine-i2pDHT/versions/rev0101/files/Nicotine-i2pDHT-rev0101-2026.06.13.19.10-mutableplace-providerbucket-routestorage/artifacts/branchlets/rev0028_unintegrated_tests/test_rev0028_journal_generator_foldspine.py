from dataclasses import replace
from pathlib import Path

from i2p_dht_lab.foldspine import audit_fold_spine
from i2p_dht_lab.fuzzwire import deterministic_fuzz_cases
from i2p_dht_lab.generatorfuzz import generate_rejection_corpus, run_generated_fuzz_corpus
from i2p_dht_lab.identity import DhtKeypair, NodeIdentity
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.journallane import (
    JournalEntry,
    JournalEventKind,
    JournalReplayDecisionKind,
    JournalReplayPolicy,
    JournalTip,
    ZERO_DIGEST,
    assess_journal_replay,
)


def kp(n: int) -> DhtKeypair:
    return DhtKeypair.from_seed(bytes([n]) * 32)


def ident(n: int) -> NodeIdentity:
    return NodeIdentity.create(destination=f"rev0028-node-{n}.b32.i2p", keypair=kp(n))


def digest(label: str) -> bytes:
    return sha256(label.encode("utf-8"))


def entry(
    seq: int,
    prev: bytes,
    kind: JournalEventKind,
    label: str,
    *,
    keypair: DhtKeypair = kp(1),
    lane: bytes | None = None,
    now: int = 1000,
    fam: str = "fam-A",
    path: str = "path-A",
    retained: tuple[bytes, ...] = (),
) -> JournalEntry:
    return JournalEntry.create(
        keypair=keypair,
        lane_id=lane or digest("journal-lane"),
        sequence=seq,
        prev_entry_digest=prev,
        event_kind=kind,
        subject_digest=digest(f"subject:{label}"),
        value_digest=digest(f"value:{label}:{seq}"),
        source_family=fam,
        path_family=path,
        issued_at=now,
        ttl=10_000,
        retained_negative_subjects=retained,
    )


def test_journallane_accepts_linked_append_and_serialized_replay() -> None:
    now = 10_000
    first = entry(1, ZERO_DIGEST, JournalEventKind.TOMBSTONE, "gone", now=now)
    tip = JournalTip.from_entries((first,))
    second = entry(2, first.entry_digest, JournalEventKind.WITNESS_RECEIPT, "witness", now=now + 1, fam="fam-B", path="path-B")
    report = assess_journal_replay((second.to_bytes(),), previous_tip=tip, now=now + 2)
    assert report.decision_kind is JournalReplayDecisionKind.ACCEPT_APPEND
    assert report.accept
    assert report.tip is not None
    assert report.tip.sequence == 2
    assert digest("subject:gone") in report.tip.hard_negative_subjects


def test_journallane_rejects_bad_signature_time_and_parse_errors() -> None:
    now = 20_000
    first = entry(1, ZERO_DIGEST, JournalEventKind.PROVIDER_TRUE, "provider", now=now)
    tip = JournalTip.from_entries((first,))
    second = entry(2, first.entry_digest, JournalEventKind.PROVIDER_FALSE, "provider", now=now + 1)
    bad_sig = replace(second, signature=second.signature[:-1] + bytes([second.signature[-1] ^ 1]))
    expired = entry(2, first.entry_digest, JournalEventKind.WITNESS_RECEIPT, "expired", now=now - 20_000)
    assert assess_journal_replay((bad_sig,), previous_tip=tip, now=now + 2).decision_kind is JournalReplayDecisionKind.QUARANTINE_BAD_SIGNATURE
    assert assess_journal_replay((expired,), previous_tip=tip, now=now + 2).decision_kind is JournalReplayDecisionKind.QUARANTINE_TIME_WINDOW
    assert assess_journal_replay((b"d01:a1:be",), previous_tip=tip, now=now + 2).decision_kind is JournalReplayDecisionKind.QUARANTINE_PARSE_ERROR


def test_journallane_rejects_rollback_same_sequence_fork_prev_mismatch_and_gap() -> None:
    now = 30_000
    first = entry(1, ZERO_DIGEST, JournalEventKind.MUTABLE_HEAD, "head", now=now)
    tip = JournalTip.from_entries((first,))
    rollback = entry(0, ZERO_DIGEST, JournalEventKind.MUTABLE_HEAD, "old", now=now + 1)
    fork = entry(1, ZERO_DIGEST, JournalEventKind.MUTABLE_HEAD, "fork", now=now + 1)
    mismatch = entry(2, digest("wrong-prev"), JournalEventKind.MUTABLE_HEAD, "mismatch", now=now + 1)
    gap = entry(5, first.entry_digest, JournalEventKind.MUTABLE_HEAD, "gap", now=now + 1)
    assert assess_journal_replay((rollback,), previous_tip=tip, now=now + 2).decision_kind is JournalReplayDecisionKind.QUARANTINE_ROLLBACK
    assert assess_journal_replay((fork,), previous_tip=tip, now=now + 2).decision_kind is JournalReplayDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK
    assert assess_journal_replay((mismatch,), previous_tip=tip, now=now + 2).decision_kind is JournalReplayDecisionKind.QUARANTINE_PREV_MISMATCH
    assert assess_journal_replay((gap,), previous_tip=tip, now=now + 2).decision_kind is JournalReplayDecisionKind.CONTINUE_WITH_GAP
    assert assess_journal_replay((gap,), previous_tip=tip, now=now + 2, policy=JournalReplayPolicy(max_sequence_gap=10)).decision_kind is JournalReplayDecisionKind.ACCEPT_APPEND


def test_journallane_rejects_lane_actor_mix_and_compaction_dropping_hard_negative() -> None:
    now = 40_000
    tomb = entry(1, ZERO_DIGEST, JournalEventKind.TOMBSTONE, "gone", now=now)
    tip = JournalTip.from_entries((tomb,))
    wrong_lane = entry(2, tomb.entry_digest, JournalEventKind.WITNESS_RECEIPT, "other-lane", lane=digest("other-lane"), now=now + 1)
    wrong_actor = entry(2, tomb.entry_digest, JournalEventKind.WITNESS_RECEIPT, "other-actor", keypair=kp(2), now=now + 1)
    compact_bad = entry(2, tomb.entry_digest, JournalEventKind.COMPACTION_MARKER, "compact-bad", now=now + 1, retained=())
    compact_good = entry(2, tomb.entry_digest, JournalEventKind.COMPACTION_MARKER, "compact-good", now=now + 1, retained=(tomb.subject_digest,))
    assert assess_journal_replay((wrong_lane,), previous_tip=tip, now=now + 2).decision_kind is JournalReplayDecisionKind.QUARANTINE_LANE_MIX
    assert assess_journal_replay((wrong_actor,), previous_tip=tip, now=now + 2).decision_kind is JournalReplayDecisionKind.QUARANTINE_LANE_MIX
    assert assess_journal_replay((compact_bad,), previous_tip=tip, now=now + 2).decision_kind is JournalReplayDecisionKind.QUARANTINE_HARD_NEGATIVE_DROPPED
    assert assess_journal_replay((compact_good,), previous_tip=tip, now=now + 2).decision_kind is JournalReplayDecisionKind.ACCEPT_COMPACTED_APPEND


def test_generatorfuzz_corpus_expands_accepted_fuzzwire_seeds_into_rejections() -> None:
    now = 50_000
    seed_cases = deterministic_fuzz_cases(keypair=kp(9), node_id=ident(9).node_id, now=now)
    corpus = generate_rejection_corpus(seed_cases)
    report = run_generated_fuzz_corpus(corpus)
    assert report.passed
    assert corpus.seed_count == len(seed_cases)
    assert corpus.case_count >= 6
    assert report.rejected_generated_cases == corpus.case_count
    assert report.run.accepted_cases == 0
    labels = {result.label for result in report.run.results}
    assert any(label.endswith("generated-depth") for label in labels)
    assert any(label.endswith("generated-append") for label in labels)
    assert any(label.endswith("generated-drift") for label in labels)


def test_foldspine_pins_current_revision_navigation() -> None:
    root = Path(__file__).resolve().parents[1]
    report = audit_fold_spine(root, revision="rev0028", artifact_stem=root.name)
    assert report.status == "pass"
    assert report.error_count == 0
