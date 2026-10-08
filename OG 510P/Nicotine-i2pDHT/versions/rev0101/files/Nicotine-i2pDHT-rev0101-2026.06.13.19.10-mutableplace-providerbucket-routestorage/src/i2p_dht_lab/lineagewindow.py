"""Mutable-head lineage windows before accepting convenient latest pointers.

The cube has several local-memory surfaces for mutable heads: monotonic sequence
memory, epoch gates, split-merge pressure, and witness receipts.  This module
attacks a harder edge: a signed head can be higher-sequence and still be unsafe
when the local node cannot connect it to known history.  A future DHT should not
let an adversary jump a client from sequence 7 to sequence 700 just because the
new pointer is signed and fast.

Lineage windows are not consensus.  They are local acceptance pressure:
linked advances may commit; gaps ask for repair; forks and same-sequence splits
are quarantined; family monoculture prevents treating one path as history.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256

LINEAGE_WINDOW_DOMAIN = DOMAIN + b":lineage-window-v1:"


class LineageDecisionKind(str, Enum):
    ACCEPT_LINKED_ADVANCE = "accept_linked_advance"
    ACCEPT_REFRESH = "accept_refresh"
    CONTINUE_MISSING_PREV = "continue_missing_prev"
    CONTINUE_UNDER_DIVERSE = "continue_under_diverse"
    QUARANTINE_ROLLBACK = "quarantine_rollback"
    QUARANTINE_SAME_SEQUENCE_FORK = "quarantine_same_sequence_fork"
    QUARANTINE_PREV_MISMATCH = "quarantine_prev_mismatch"
    QUARANTINE_SCOPE_MIX = "quarantine_scope_mix"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"


@dataclass(frozen=True)
class HeadMemoryAnchor:
    scope_id: bytes
    sequence: int
    head_digest: bytes
    known_digests: frozenset[bytes] = frozenset()

    def __post_init__(self) -> None:
        if len(self.scope_id) != 32 or len(self.head_digest) != 32:
            raise ValueError("head memory anchor requires 32-byte scope/head digest")
        if self.sequence < 0:
            raise ValueError("head sequence must be non-negative")
        for digest in self.known_digests:
            if len(digest) != 32:
                raise ValueError("known head digests must be 32 bytes")

    @property
    def all_known_digests(self) -> frozenset[bytes]:
        return self.known_digests | frozenset({self.head_digest})


@dataclass(frozen=True)
class HeadLineageObservation:
    scope_id: bytes
    writer_public_key: bytes
    sequence: int
    head_digest: bytes
    prev_digest: bytes
    payload_digest: bytes
    source_family: str
    path_family: str
    issued_at: int
    expires_at: int
    signature: bytes = b""

    def __post_init__(self) -> None:
        for name, value in (
            ("scope_id", self.scope_id),
            ("writer_public_key", self.writer_public_key),
            ("head_digest", self.head_digest),
            ("prev_digest", self.prev_digest),
            ("payload_digest", self.payload_digest),
        ):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if self.sequence < 0:
            raise ValueError("sequence must be non-negative")
        if not self.source_family or not self.path_family:
            raise ValueError("lineage observation needs source and path family hints")
        if self.expires_at <= self.issued_at:
            raise ValueError("lineage observation expires_at must follow issued_at")

    @classmethod
    def create(
        cls,
        *,
        writer: DhtKeypair,
        scope_id: bytes,
        sequence: int,
        prev_digest: bytes,
        payload_digest: bytes,
        source_family: str,
        path_family: str,
        issued_at: int,
        ttl: int = 600,
    ) -> "HeadLineageObservation":
        if ttl <= 0:
            raise ValueError("ttl must be positive")
        unsigned = cls(
            scope_id=scope_id,
            writer_public_key=writer.public_key_bytes,
            sequence=sequence,
            head_digest=sha256(LINEAGE_WINDOW_DOMAIN + b":head:" + bencode({
                b"scope_id": scope_id,
                b"writer_public_key": writer.public_key_bytes,
                b"sequence": sequence,
                b"prev_digest": prev_digest,
                b"payload_digest": payload_digest,
            })),
            prev_digest=prev_digest,
            payload_digest=payload_digest,
            source_family=source_family,
            path_family=path_family,
            issued_at=issued_at,
            expires_at=issued_at + ttl,
        )
        return replace(unsigned, signature=writer.sign(unsigned.unsigned_payload()))

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"scope_id": self.scope_id,
            b"writer_public_key": self.writer_public_key,
            b"sequence": self.sequence,
            b"head_digest": self.head_digest,
            b"prev_digest": self.prev_digest,
            b"payload_digest": self.payload_digest,
            b"source_family": self.source_family,
            b"path_family": self.path_family,
            b"issued_at": self.issued_at,
            b"expires_at": self.expires_at,
        }

    def unsigned_payload(self) -> bytes:
        return LINEAGE_WINDOW_DOMAIN + b":observation-unsigned:" + bencode(self.unsigned_bvalue())

    def verify(self, *, now: int, expected_scope_id: bytes | None = None) -> bool:
        if expected_scope_id is not None and self.scope_id != expected_scope_id:
            return False
        if now < self.issued_at or now >= self.expires_at:
            return False
        return verify_signature(self.writer_public_key, self.unsigned_payload(), self.signature)


@dataclass(frozen=True)
class LineageWindowPolicy:
    min_source_families_for_commit: int = 2
    min_path_families_for_commit: int = 2
    max_direct_gap: int = 1
    allow_under_diverse_watch: bool = True

    def validate(self) -> None:
        if self.min_source_families_for_commit <= 0 or self.min_path_families_for_commit <= 0 or self.max_direct_gap < 0:
            raise ValueError("lineage window policy invalid")


@dataclass(frozen=True)
class LineageRepairRequest:
    scope_id: bytes
    wanted_prev_digest: bytes
    from_sequence: int
    to_sequence: int
    reason: str

    def __post_init__(self) -> None:
        if len(self.scope_id) != 32 or len(self.wanted_prev_digest) != 32:
            raise ValueError("lineage repair request ids must be 32 bytes")
        if self.to_sequence < self.from_sequence:
            raise ValueError("lineage repair range invalid")


@dataclass(frozen=True)
class LineageDecision:
    kind: LineageDecisionKind
    accept: bool
    reason: str


@dataclass(frozen=True)
class LineageWindowReport:
    scope_id: bytes
    decision: LineageDecision
    selected: HeadLineageObservation | None
    repair_requests: tuple[LineageRepairRequest, ...]
    quarantine_digests: tuple[bytes, ...]
    source_families: tuple[str, ...]
    path_families: tuple[str, ...]
    report_digest: bytes

    @property
    def should_continue(self) -> bool:
        return self.decision.kind in {LineageDecisionKind.CONTINUE_MISSING_PREV, LineageDecisionKind.CONTINUE_UNDER_DIVERSE}

    @property
    def quarantined(self) -> bool:
        return self.decision.kind.value.startswith("quarantine_")


def _report(
    *,
    scope_id: bytes,
    decision: LineageDecision,
    selected: HeadLineageObservation | None,
    repair_requests: Iterable[LineageRepairRequest] = (),
    quarantine_digests: Iterable[bytes] = (),
    source_families: Iterable[str] = (),
    path_families: Iterable[str] = (),
) -> LineageWindowReport:
    repairs = tuple(repair_requests)
    quarantines = tuple(sorted(quarantine_digests))
    source_tuple = tuple(sorted(set(source_families)))
    path_tuple = tuple(sorted(set(path_families)))
    digest = sha256(LINEAGE_WINDOW_DOMAIN + b":report:" + bencode({
        b"scope_id": scope_id,
        b"decision": decision.kind.value,
        b"selected": b"" if selected is None else selected.head_digest,
        b"repairs": [{b"wanted_prev_digest": item.wanted_prev_digest, b"from_sequence": item.from_sequence, b"to_sequence": item.to_sequence, b"reason": item.reason} for item in repairs],
        b"quarantine": quarantines,
        b"source_families": list(source_tuple),
        b"path_families": list(path_tuple),
    }))
    return LineageWindowReport(scope_id, decision, selected, repairs, quarantines, source_tuple, path_tuple, digest)


def analyze_lineage_window(
    observations: Iterable[HeadLineageObservation],
    *,
    memory: HeadMemoryAnchor,
    policy: LineageWindowPolicy | None = None,
    now: int,
) -> LineageWindowReport:
    policy = policy or LineageWindowPolicy()
    policy.validate()
    obs = tuple(observations)
    if not obs:
        return _report(scope_id=memory.scope_id, decision=LineageDecision(LineageDecisionKind.CONTINUE_MISSING_PREV, False, "no lineage observations were available"), selected=None)

    scope_mixed = [item for item in obs if item.scope_id != memory.scope_id]
    if scope_mixed:
        return _report(scope_id=memory.scope_id, decision=LineageDecision(LineageDecisionKind.QUARANTINE_SCOPE_MIX, False, "lineage window included observations for another scope"), selected=None, quarantine_digests=(item.head_digest for item in scope_mixed))

    bad = [item for item in obs if not item.verify(now=now, expected_scope_id=memory.scope_id)]
    if bad:
        return _report(scope_id=memory.scope_id, decision=LineageDecision(LineageDecisionKind.QUARANTINE_BAD_SIGNATURE, False, "lineage window included invalid or expired signed observation"), selected=None, quarantine_digests=(item.head_digest for item in bad))

    by_seq: dict[int, set[bytes]] = {}
    for item in obs:
        by_seq.setdefault(item.sequence, set()).add(item.head_digest)
    fork_sequences = {seq for seq, digests in by_seq.items() if len(digests) > 1}
    if fork_sequences:
        return _report(scope_id=memory.scope_id, decision=LineageDecision(LineageDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK, False, "same sequence carried multiple signed head digests"), selected=None, quarantine_digests=(item.head_digest for item in obs if item.sequence in fork_sequences))

    latest = max(obs, key=lambda item: (item.sequence, item.issued_at, item.head_digest))
    source_families = {item.source_family for item in obs if item.sequence == latest.sequence and item.head_digest == latest.head_digest}
    path_families = {item.path_family for item in obs if item.sequence == latest.sequence and item.head_digest == latest.head_digest}

    if latest.sequence < memory.sequence:
        return _report(scope_id=memory.scope_id, decision=LineageDecision(LineageDecisionKind.QUARANTINE_ROLLBACK, False, "latest observed head is below local memory"), selected=latest, quarantine_digests=(latest.head_digest,), source_families=source_families, path_families=path_families)
    if latest.sequence == memory.sequence:
        if latest.head_digest == memory.head_digest:
            return _report(scope_id=memory.scope_id, decision=LineageDecision(LineageDecisionKind.ACCEPT_REFRESH, True, "observation refreshes local head memory"), selected=latest, source_families=source_families, path_families=path_families)
        return _report(scope_id=memory.scope_id, decision=LineageDecision(LineageDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK, False, "same sequence conflicts with local memory"), selected=latest, quarantine_digests=(latest.head_digest, memory.head_digest), source_families=source_families, path_families=path_families)

    if latest.prev_digest not in memory.all_known_digests:
        return _report(
            scope_id=memory.scope_id,
            decision=LineageDecision(LineageDecisionKind.CONTINUE_MISSING_PREV, False, "newest head does not link to local history; request predecessor window"),
            selected=latest,
            repair_requests=(LineageRepairRequest(memory.scope_id, latest.prev_digest, memory.sequence, latest.sequence, "missing predecessor digest for newest head"),),
            source_families=source_families,
            path_families=path_families,
        )

    if latest.sequence - memory.sequence > policy.max_direct_gap:
        return _report(
            scope_id=memory.scope_id,
            decision=LineageDecision(LineageDecisionKind.CONTINUE_MISSING_PREV, False, "linked head jumps beyond direct-gap policy; request intermediate history"),
            selected=latest,
            repair_requests=(LineageRepairRequest(memory.scope_id, memory.head_digest, memory.sequence + 1, latest.sequence - 1, "direct jump exceeded local lineage window"),),
            source_families=source_families,
            path_families=path_families,
        )

    if latest.prev_digest != memory.head_digest:
        return _report(scope_id=memory.scope_id, decision=LineageDecision(LineageDecisionKind.QUARANTINE_PREV_MISMATCH, False, "newest head links to an older known digest rather than current memory"), selected=latest, quarantine_digests=(latest.head_digest,), source_families=source_families, path_families=path_families)

    if len(source_families) < policy.min_source_families_for_commit or len(path_families) < policy.min_path_families_for_commit:
        kind = LineageDecisionKind.CONTINUE_UNDER_DIVERSE
        return _report(scope_id=memory.scope_id, decision=LineageDecision(kind, False, "linked advance is under-diverse; watch or ask more paths before commit"), selected=latest, source_families=source_families, path_families=path_families)

    return _report(scope_id=memory.scope_id, decision=LineageDecision(LineageDecisionKind.ACCEPT_LINKED_ADVANCE, True, "linked, fresh, diverse direct advance"), selected=latest, source_families=source_families, path_families=path_families)
