"""Witness-receipt poisoning analysis.

Garden witnesses are useful precisely because they remember and sign what they
saw. They are dangerous if clients treat receipts as votes from an authority.
This module tests the opposite rule: receipts are admitted as evidence only when
cryptographically valid, fresh, and diverse enough. A single garden family can
produce many receipts, but it should not become a quorum by itself.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Mapping

from .forkwatch import WitnessKind, WitnessReceipt


class ReceiptAnalysisKind(str, Enum):
    NO_VALID_RECEIPTS = "no_valid_receipts"
    VALID_EVIDENCE = "valid_evidence"
    SINGLE_FAMILY_ALARM = "single_family_alarm"
    CONTRADICTORY_WITNESS = "contradictory_witness"
    INVALID_OR_EXPIRED_PRESENT = "invalid_or_expired_present"


@dataclass(frozen=True)
class WitnessHint:
    witness_node_id: bytes
    family_id: str
    local_trust: int = 1


@dataclass(frozen=True)
class ReceiptAnalysis:
    kind: ReceiptAnalysisKind
    valid_count: int
    invalid_count: int
    alarm_count: int
    alarm_families: frozenset[str]
    contradictory_witnesses: frozenset[bytes]
    reason: str

    @property
    def usable_alarm_quorum(self) -> bool:
        return self.kind is ReceiptAnalysisKind.VALID_EVIDENCE and self.alarm_count > 0


def _family_for(receipt: WitnessReceipt, hints: Mapping[bytes, WitnessHint]) -> str:
    hint = hints.get(receipt.witness_node_id)
    if hint is not None:
        return hint.family_id
    # Unknown witnesses get their own family by node id. That avoids collapsing
    # unknowns into one bucket while still allowing callers to demand known hints.
    return "unknown:" + receipt.witness_node_id.hex()[:16]


def _is_alarm(receipt: WitnessReceipt) -> bool:
    return receipt.kind in {WitnessKind.ROLLBACK_SEEN, WitnessKind.SAME_SEQ_FORK_SEEN, WitnessKind.INVALID_RECORD_SEEN}


def analyze_witness_receipts(
    receipts: Iterable[WitnessReceipt],
    *,
    hints: Iterable[WitnessHint] = (),
    now: int,
    min_alarm_families: int = 2,
) -> ReceiptAnalysis:
    hint_map = {hint.witness_node_id: hint for hint in hints}
    valid: list[WitnessReceipt] = []
    invalid = 0
    for receipt in receipts:
        if receipt.verify(now=now):
            valid.append(receipt)
        else:
            invalid += 1

    if not valid:
        return ReceiptAnalysis(ReceiptAnalysisKind.NO_VALID_RECEIPTS, 0, invalid, 0, frozenset(), frozenset(), "no valid witness receipts")

    contradictory: set[bytes] = set()
    by_witness_target: dict[tuple[bytes, bytes], list[WitnessReceipt]] = {}
    for receipt in valid:
        by_witness_target.setdefault((receipt.witness_node_id, receipt.target), []).append(receipt)
    for (witness_node_id, _target), group in by_witness_target.items():
        # Same witness claiming incompatible states for the same target in the
        # same evidence window is not proof of malice, but it is poison for using
        # that witness as quorum support.
        state_shapes = {(item.kind, item.highest_seq, item.observed_seq, item.record_hashes) for item in group}
        if len(state_shapes) > 1 and any(_is_alarm(item) for item in group):
            contradictory.add(witness_node_id)

    alarm_receipts = [receipt for receipt in valid if _is_alarm(receipt) and receipt.witness_node_id not in contradictory]
    alarm_families = frozenset(_family_for(receipt, hint_map) for receipt in alarm_receipts)

    if contradictory:
        return ReceiptAnalysis(
            ReceiptAnalysisKind.CONTRADICTORY_WITNESS,
            len(valid),
            invalid,
            len(alarm_receipts),
            alarm_families,
            frozenset(contradictory),
            "one or more witnesses issued contradictory evidence",
        )
    if alarm_receipts and len(alarm_families) < min_alarm_families:
        return ReceiptAnalysis(
            ReceiptAnalysisKind.SINGLE_FAMILY_ALARM,
            len(valid),
            invalid,
            len(alarm_receipts),
            alarm_families,
            frozenset(),
            "alarm evidence came from too few independent families",
        )
    if invalid:
        return ReceiptAnalysis(
            ReceiptAnalysisKind.INVALID_OR_EXPIRED_PRESENT,
            len(valid),
            invalid,
            len(alarm_receipts),
            alarm_families,
            frozenset(),
            "some receipts were invalid or expired; keep evidence but do not trust batch blindly",
        )
    return ReceiptAnalysis(
        ReceiptAnalysisKind.VALID_EVIDENCE,
        len(valid),
        invalid,
        len(alarm_receipts),
        alarm_families,
        frozenset(),
        "valid receipts with sufficient family diversity for lab thresholds",
    )
