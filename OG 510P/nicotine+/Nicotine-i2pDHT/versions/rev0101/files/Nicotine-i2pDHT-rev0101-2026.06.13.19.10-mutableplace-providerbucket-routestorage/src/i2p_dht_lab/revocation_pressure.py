"""History-aware revocation-head pressure.

Revocation heads are mutable heads too, so they inherit the same ugly risk as
IPNS-like pointers: a valid old revocation head can be replayed. The dangerous
failure mode is allowing a grant because a stale head omitted a later revocation.
This module makes the conservative guess executable: local memory keeps the
highest seen revocation sequence and the union of verified revoked grant hashes.
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Iterable

from .capgrant import RevocationHead


class RevocationPressureKind(str, Enum):
    ACCEPT_FIRST = "accept_first"
    ACCEPT_ADVANCE = "accept_advance"
    ACCEPT_REFRESH = "accept_refresh"
    STALE_ROLLBACK = "stale_rollback"
    SAME_SEQ_FORK = "same_seq_fork"
    INVALID_HEAD = "invalid_head"


@dataclass(frozen=True)
class RevocationHeadVerdict:
    kind: RevocationPressureKind
    authority_public_key: bytes
    sequence: int
    known_sequence: int | None
    head_hash: bytes
    reason: str

    @property
    def accepted(self) -> bool:
        return self.kind in {RevocationPressureKind.ACCEPT_FIRST, RevocationPressureKind.ACCEPT_ADVANCE, RevocationPressureKind.ACCEPT_REFRESH}

    @property
    def risky(self) -> bool:
        return self.kind in {RevocationPressureKind.STALE_ROLLBACK, RevocationPressureKind.SAME_SEQ_FORK, RevocationPressureKind.INVALID_HEAD}


@dataclass(frozen=True)
class RevocationAuthorityState:
    authority_public_key: bytes
    highest_sequence: int
    accepted_head_hash: bytes
    revoked_hashes: frozenset[bytes]
    fork_hashes_at_highest: frozenset[bytes] = frozenset()


@dataclass
class RevocationHeadMemory:
    states: dict[bytes, RevocationAuthorityState] = field(default_factory=dict)
    risky_verdicts: list[RevocationHeadVerdict] = field(default_factory=list)

    def observe(self, head: RevocationHead, *, now: int) -> RevocationHeadVerdict:
        authority = head.authority_public_key
        current = self.states.get(authority)
        known = None if current is None else current.highest_sequence
        if not head.verify(now=now):
            verdict = RevocationHeadVerdict(RevocationPressureKind.INVALID_HEAD, authority, head.sequence, known, head.head_hash, "revocation head failed signature/shape/time validation")
            self.risky_verdicts.append(verdict)
            return verdict
        revoked = head.revoked_hashes
        if current is None:
            self.states[authority] = RevocationAuthorityState(authority, head.sequence, head.head_hash, revoked)
            return RevocationHeadVerdict(RevocationPressureKind.ACCEPT_FIRST, authority, head.sequence, None, head.head_hash, "first revocation head for authority")
        if head.sequence < current.highest_sequence:
            # Preserve union from previously accepted higher head. Never let a
            # stale head make a known revocation disappear.
            verdict = RevocationHeadVerdict(RevocationPressureKind.STALE_ROLLBACK, authority, head.sequence, current.highest_sequence, head.head_hash, "older revocation head replayed")
            self.risky_verdicts.append(verdict)
            return verdict
        if head.sequence == current.highest_sequence:
            if head.head_hash == current.accepted_head_hash:
                return RevocationHeadVerdict(RevocationPressureKind.ACCEPT_REFRESH, authority, head.sequence, current.highest_sequence, head.head_hash, "same revocation head refreshed")
            forks = frozenset(set(current.fork_hashes_at_highest) | {current.accepted_head_hash, head.head_hash})
            self.states[authority] = replace(current, fork_hashes_at_highest=forks, revoked_hashes=frozenset(set(current.revoked_hashes) | set(revoked)))
            verdict = RevocationHeadVerdict(RevocationPressureKind.SAME_SEQ_FORK, authority, head.sequence, current.highest_sequence, head.head_hash, "same revocation sequence has different entries")
            self.risky_verdicts.append(verdict)
            return verdict
        self.states[authority] = RevocationAuthorityState(authority, head.sequence, head.head_hash, frozenset(set(current.revoked_hashes) | set(revoked)))
        return RevocationHeadVerdict(RevocationPressureKind.ACCEPT_ADVANCE, authority, head.sequence, current.highest_sequence, head.head_hash, "revocation head advanced")

    def revoked_hashes_for(self, authority_public_key: bytes) -> frozenset[bytes]:
        state = self.states.get(authority_public_key)
        return frozenset() if state is None else state.revoked_hashes

    def is_revoked(self, authority_public_key: bytes, grant_hash: bytes) -> bool:
        return grant_hash in self.revoked_hashes_for(authority_public_key)

    def observe_many(self, heads: Iterable[RevocationHead], *, now: int) -> tuple[RevocationHeadVerdict, ...]:
        return tuple(self.observe(head, now=now) for head in heads)
