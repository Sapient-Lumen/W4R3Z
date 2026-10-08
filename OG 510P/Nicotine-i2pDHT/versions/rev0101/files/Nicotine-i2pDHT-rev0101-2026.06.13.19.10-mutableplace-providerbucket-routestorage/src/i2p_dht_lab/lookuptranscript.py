"""Explicit lookup transcript and routing-pressure objects.

Previous revisions had pressure decisions scattered across provider proofs,
head witnesses, latency forge, and sweep grids.  This module gives those local
judgments a common transcript vocabulary without choosing a live transport.

The transcript is not a packet format.  It is a deterministic evidence object:
which path families were asked, which families replied fast, which claims were
attached, which proofs/refusals arrived, and whether greedy latency would have
collapsed the lookup into a captured fast window.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .ids import DOMAIN, sha256, short_id

LOOKUP_TRANSCRIPT_DOMAIN = DOMAIN + b":lookup-transcript-v1:"


class LookupKind(str, Enum):
    FIND_NODE = "find_node"
    FIND_PROVIDER = "find_provider"
    GET_MUTABLE_HEAD = "get_mutable_head"
    PROVIDER_PROOF = "provider_proof"
    WITNESS_GATHER = "witness_gather"


class LookupEventKind(str, Enum):
    QUERY_SENT = "query_sent"
    RESPONSE_NODES = "response_nodes"
    RESPONSE_PROVIDER_CLAIM = "response_provider_claim"
    RESPONSE_MUTABLE_HEAD = "response_mutable_head"
    PROOF_ATTEMPT = "proof_attempt"
    WITNESS_RECEIPT = "witness_receipt"
    USEFUL_REFUSAL = "useful_refusal"
    TIMEOUT = "timeout"
    BAD_RESPONSE = "bad_response"


class LookupPressureDecisionKind(str, Enum):
    ACCEPT_DIVERSE_SUCCESS = "accept_diverse_success"
    CONTINUE_LOW_PATH_DIVERSITY = "continue_low_path_diversity"
    CONTINUE_TIMEOUT_PRESSURE = "continue_timeout_pressure"
    QUARANTINE_FAST_WINDOW_CAPTURE = "quarantine_fast_window_capture"
    QUARANTINE_BAD_RESPONSE_PRESSURE = "quarantine_bad_response_pressure"
    EVIDENCE_ONLY = "evidence_only"


SUCCESS_EVENTS = {
    LookupEventKind.RESPONSE_NODES,
    LookupEventKind.RESPONSE_PROVIDER_CLAIM,
    LookupEventKind.RESPONSE_MUTABLE_HEAD,
    LookupEventKind.PROOF_ATTEMPT,
    LookupEventKind.WITNESS_RECEIPT,
}


@dataclass(frozen=True)
class LookupEvent:
    sequence: int
    path_id: str
    family_id: str
    node_id: bytes
    kind: LookupEventKind
    sent_at_ms: int
    completed_at_ms: int
    payload_digest: bytes = b""
    note: str = ""

    def __post_init__(self) -> None:
        if len(self.node_id) != 32:
            raise ValueError("node_id must be 32 bytes")
        if self.payload_digest and len(self.payload_digest) != 32:
            raise ValueError("payload_digest must be empty or 32 bytes")
        if self.completed_at_ms < self.sent_at_ms:
            raise ValueError("completed_at_ms cannot be before sent_at_ms")
        if not self.path_id or not self.family_id:
            raise ValueError("path_id and family_id are required")

    @property
    def latency_ms(self) -> int:
        return self.completed_at_ms - self.sent_at_ms

    @property
    def successful(self) -> bool:
        return self.kind in SUCCESS_EVENTS

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"sequence": self.sequence,
            b"path_id": self.path_id,
            b"family_id": self.family_id,
            b"node_id": self.node_id,
            b"kind": self.kind.value,
            b"sent_at_ms": self.sent_at_ms,
            b"completed_at_ms": self.completed_at_ms,
            b"payload_digest": self.payload_digest,
            b"note": self.note[:160],
        }


@dataclass(frozen=True)
class LookupTranscript:
    lookup_id: bytes
    kind: LookupKind
    target: bytes
    events: tuple[LookupEvent, ...]

    def __post_init__(self) -> None:
        if len(self.lookup_id) != 32 or len(self.target) != 32:
            raise ValueError("lookup_id and target must be 32-byte digests")
        seqs = [event.sequence for event in self.events]
        if len(seqs) != len(set(seqs)):
            raise ValueError("lookup event sequences must be unique")

    @property
    def digest(self) -> bytes:
        return sha256(LOOKUP_TRANSCRIPT_DOMAIN + b":transcript:" + bencode({
            b"lookup_id": self.lookup_id,
            b"kind": self.kind.value,
            b"target": self.target,
            b"events": [event.bvalue() for event in sorted(self.events, key=lambda item: item.sequence)],
        }))

    @property
    def families_seen(self) -> frozenset[str]:
        return frozenset(event.family_id for event in self.events)

    @property
    def path_ids(self) -> frozenset[str]:
        return frozenset(event.path_id for event in self.events)

    @property
    def successful_events(self) -> tuple[LookupEvent, ...]:
        return tuple(event for event in self.events if event.successful)

    def fast_window(self, *, window_ms: int) -> tuple[LookupEvent, ...]:
        completed = [event for event in self.events if event.kind is not LookupEventKind.QUERY_SENT]
        if not completed:
            return ()
        first = min(event.completed_at_ms for event in completed)
        return tuple(sorted((event for event in completed if event.completed_at_ms <= first + window_ms), key=lambda item: (item.completed_at_ms, item.sequence)))


@dataclass(frozen=True)
class LookupPressurePolicy:
    min_success_families: int = 3
    min_success_paths: int = 3
    max_fast_family_fraction: float = 0.60
    fast_window_ms: int = 250
    max_bad_events: int = 0
    max_timeout_fraction: float = 0.50
    allow_evidence_only: bool = True

    def validate(self) -> None:
        if self.min_success_families <= 0 or self.min_success_paths <= 0:
            raise ValueError("success thresholds must be positive")
        if not 0.0 < self.max_fast_family_fraction <= 1.0:
            raise ValueError("fast family fraction must be in (0, 1]")
        if not 0.0 <= self.max_timeout_fraction <= 1.0:
            raise ValueError("timeout fraction must be in [0, 1]")
        if self.fast_window_ms < 0 or self.max_bad_events < 0:
            raise ValueError("pressure windows/counts must be non-negative")


@dataclass(frozen=True)
class LookupPressureDecision:
    kind: LookupPressureDecisionKind
    accept: bool
    reason: str


@dataclass(frozen=True)
class LookupPressureReport:
    transcript_digest: bytes
    success_family_count: int
    success_path_count: int
    fast_window_size: int
    fast_window_family_fraction: float
    timeout_fraction: float
    bad_event_count: int
    decision: LookupPressureDecision

    @property
    def needs_more_paths(self) -> bool:
        return not self.decision.accept


def _fraction_largest_family(events: Iterable[LookupEvent]) -> float:
    events = tuple(events)
    if not events:
        return 0.0
    counts: dict[str, int] = {}
    for event in events:
        counts[event.family_id] = counts.get(event.family_id, 0) + 1
    return max(counts.values()) / len(events)


def analyze_lookup_pressure(transcript: LookupTranscript, *, policy: LookupPressurePolicy | None = None) -> LookupPressureReport:
    policy = policy or LookupPressurePolicy()
    policy.validate()
    successes = transcript.successful_events
    success_families = frozenset(event.family_id for event in successes)
    success_paths = frozenset(event.path_id for event in successes)
    fast = transcript.fast_window(window_ms=policy.fast_window_ms)
    fast_fraction = _fraction_largest_family(fast)
    non_query = tuple(event for event in transcript.events if event.kind is not LookupEventKind.QUERY_SENT)
    timeout_count = sum(1 for event in non_query if event.kind is LookupEventKind.TIMEOUT)
    timeout_fraction = timeout_count / len(non_query) if non_query else 0.0
    bad_count = sum(1 for event in non_query if event.kind is LookupEventKind.BAD_RESPONSE)

    if fast and len(frozenset(event.family_id for event in fast)) > 0 and fast_fraction > policy.max_fast_family_fraction and len(fast) >= 3:
        decision = LookupPressureDecision(LookupPressureDecisionKind.QUARANTINE_FAST_WINDOW_CAPTURE, False, "fast response window is dominated by one path family")
    elif bad_count > policy.max_bad_events:
        decision = LookupPressureDecision(LookupPressureDecisionKind.QUARANTINE_BAD_RESPONSE_PRESSURE, False, "bad responses exceeded local pressure budget")
    elif timeout_fraction > policy.max_timeout_fraction:
        decision = LookupPressureDecision(LookupPressureDecisionKind.CONTINUE_TIMEOUT_PRESSURE, False, "too many lookup attempts timed out")
    elif len(success_families) < policy.min_success_families or len(success_paths) < policy.min_success_paths:
        decision = LookupPressureDecision(LookupPressureDecisionKind.CONTINUE_LOW_PATH_DIVERSITY, False, "successful answers are not path/family diverse enough")
    elif policy.allow_evidence_only and transcript.kind in {LookupKind.WITNESS_GATHER, LookupKind.PROVIDER_PROOF}:
        decision = LookupPressureDecision(LookupPressureDecisionKind.EVIDENCE_ONLY, False, "transcript preserves evidence but does not by itself decide truth")
    else:
        decision = LookupPressureDecision(LookupPressureDecisionKind.ACCEPT_DIVERSE_SUCCESS, True, "successful answers crossed local path/family diversity thresholds")

    return LookupPressureReport(
        transcript_digest=transcript.digest,
        success_family_count=len(success_families),
        success_path_count=len(success_paths),
        fast_window_size=len(fast),
        fast_window_family_fraction=fast_fraction,
        timeout_fraction=timeout_fraction,
        bad_event_count=bad_count,
        decision=decision,
    )


def compact_transcript_label(transcript: LookupTranscript) -> str:
    return f"{transcript.kind.value}:{short_id(transcript.target)}:{short_id(transcript.digest)}"
