"""rev0084 parser-hold boundary for optional native code.

The cube allows tiny GCC leaves for deterministic hot paths, but hostile-byte
parsing remains Python-owned until the parser semantics, fuzz corpus, and
restart evidence stop moving.  This module treats a native parser proposal as a
protocol claim that must be held or quarantined rather than as an optimization.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .bencode import bencode
from .ids import DOMAIN, sha256

PARSER_HOLD_DOMAIN = DOMAIN + b":parser-hold-v1:"


class ParserHoldDecisionKind(str, Enum):
    ACCEPT_PYTHON_PARSER_HOLD = "accept_python_parser_hold"
    HOLD_NATIVE_PARSER_PROPOSAL = "hold_native_parser_proposal"
    QUARANTINE_UNTRUSTED_NATIVE_PARSER = "quarantine_untrusted_native_parser"
    QUARANTINE_PARSER_DIGEST_DRIFT = "quarantine_parser_digest_drift"
    QUARANTINE_REQUEST_REPLAY = "quarantine_request_replay"
    QUARANTINE_ROLLBACK = "quarantine_rollback"
    QUARANTINE_SAME_SEQUENCE_FORK = "quarantine_same_sequence_fork"
    QUARANTINE_PREVIOUS_LINK_MISMATCH = "quarantine_previous_link_mismatch"
    QUARANTINE_LOW_DIVERSITY = "quarantine_low_diversity"


@dataclass(frozen=True)
class ParserHoldProposal:
    component: str
    parser_name: str
    profile: str
    sequence: int
    previous_digest: bytes
    python_parser_digest: bytes
    proposed_native_source_digest: bytes
    max_input_len: int
    untrusted_bytes: bool
    native_requested: bool
    native_required: bool
    request_id: str
    family_id: str
    path_family_id: str
    note: str = ""

    @property
    def proposal_digest(self) -> bytes:
        return sha256(PARSER_HOLD_DOMAIN + b":proposal:" + bencode({
            b"component": self.component,
            b"parser": self.parser_name,
            b"profile": self.profile,
            b"sequence": self.sequence,
            b"previous": self.previous_digest,
            b"python": self.python_parser_digest,
            b"native_source": self.proposed_native_source_digest,
            b"max_input": self.max_input_len,
            b"untrusted": 1 if self.untrusted_bytes else 0,
            b"native_requested": 1 if self.native_requested else 0,
            b"native_required": 1 if self.native_required else 0,
            b"request": self.request_id,
            b"family": self.family_id,
            b"path_family": self.path_family_id,
            b"note": self.note,
        }))


@dataclass(frozen=True)
class ParserHoldReport:
    decision_kind: ParserHoldDecisionKind
    accepted: bool
    hold: bool
    quarantine: bool
    python_parser_must_own: bool
    proposal_digest: bytes
    report_sequence: int
    obligations: tuple[str, ...]

    @property
    def report_digest(self) -> bytes:
        return sha256(PARSER_HOLD_DOMAIN + b":report:" + bencode({
            b"decision": ParserHoldDecisionKind(self.decision_kind).value,
            b"accepted": 1 if self.accepted else 0,
            b"hold": 1 if self.hold else 0,
            b"quarantine": 1 if self.quarantine else 0,
            b"python_owns": 1 if self.python_parser_must_own else 0,
            b"proposal": self.proposal_digest,
            b"sequence": self.report_sequence,
            b"obligations": list(self.obligations),
        }))


def assess_parser_hold(
    proposal: ParserHoldProposal,
    *,
    previous: ParserHoldProposal | None = None,
    prior_proposal_digests: tuple[bytes, ...] = (),
    expected_python_parser_digest: bytes | None = None,
    observed_families: tuple[str, ...] = (),
    observed_path_families: tuple[str, ...] = (),
    min_families: int = 1,
    min_path_families: int = 1,
) -> ParserHoldReport:
    """Assess whether parser authority stays with Python at this boundary."""

    def report(kind: ParserHoldDecisionKind, accepted: bool, hold: bool, quarantine: bool, obligations: tuple[str, ...]) -> ParserHoldReport:
        return ParserHoldReport(kind, accepted, hold, quarantine, True, proposal.proposal_digest, proposal.sequence, obligations)

    if proposal.proposal_digest in prior_proposal_digests:
        return report(ParserHoldDecisionKind.QUARANTINE_REQUEST_REPLAY, False, False, True, ("parser-hold-proposal-replay",))

    if expected_python_parser_digest is not None and proposal.python_parser_digest != expected_python_parser_digest:
        return report(ParserHoldDecisionKind.QUARANTINE_PARSER_DIGEST_DRIFT, False, False, True, ("python-parser-digest-drift", "do-not-select-native-parser"))

    if previous is not None:
        if proposal.sequence < previous.sequence:
            return report(ParserHoldDecisionKind.QUARANTINE_ROLLBACK, False, False, True, ("parser-hold-sequence-rollback",))
        if proposal.sequence == previous.sequence and proposal.proposal_digest != previous.proposal_digest:
            return report(ParserHoldDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK, False, False, True, ("parser-hold-same-sequence-fork",))
        if proposal.sequence > previous.sequence and proposal.previous_digest != previous.proposal_digest:
            return report(ParserHoldDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH, False, False, True, ("parser-hold-previous-link-mismatch",))

    families = set(observed_families or (proposal.family_id,))
    path_families = set(observed_path_families or (proposal.path_family_id,))
    if len(families) < min_families or len(path_families) < min_path_families:
        return report(ParserHoldDecisionKind.QUARANTINE_LOW_DIVERSITY, False, False, True, ("parser-hold-low-family-or-path-diversity",))

    if proposal.native_requested and proposal.untrusted_bytes:
        return report(ParserHoldDecisionKind.QUARANTINE_UNTRUSTED_NATIVE_PARSER, False, False, True, ("untrusted-bytes-remain-python-owned", "native-parser-forbidden-at-this-stage"))

    if proposal.native_requested or proposal.native_required:
        return report(ParserHoldDecisionKind.HOLD_NATIVE_PARSER_PROPOSAL, False, True, False, ("keep-python-parser-oracle", "require-fuzz-and-proof-before-native-parser"))

    return report(ParserHoldDecisionKind.ACCEPT_PYTHON_PARSER_HOLD, True, False, False, ("python-parser-remains-authority", "native-leaf-boundary-does-not-include-parsing"))
