"""Key-compromise and succession pressure for mutable DHT writers.

A DHT that treats mutability seriously needs a crisis path before real users
need it.  This is deliberately toy code: it models local acceptance pressure for
key succession and recovery rotation, not a production governance system.
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum

from .bencode import bencode
from .ids import DOMAIN, sha256
from .identity import DhtKeypair, verify_signature
from .persistlane import ZERO_DIGEST

KEY_CRISIS_DOMAIN = DOMAIN + b":key-crisis-v1:"


class KeyCrisisKind(str, Enum):
    SUCCESSION = "succession"
    RECOVERY_ROTATION = "recovery_rotation"
    KEY_COMPROMISED = "key_compromised"
    DESTINATION_LOST = "destination_lost"
    SIGNER_FORKED = "signer_forked"
    EMERGENCY_FREEZE = "emergency_freeze"
    SUCCESSION_REQUIRED = "succession_required"

class KeyCrisisDecisionKind(str, Enum):
    ACCEPT_SUCCESSION = "accept_succession"
    ACCEPT_RECOVERY_ROTATION = "accept_recovery_rotation"
    CONTINUE_NEEDS_RECOVERY_WITNESSES = "continue_needs_recovery_witnesses"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_ROLLBACK = "quarantine_rollback"
    QUARANTINE_SAME_SEQUENCE_FORK = "quarantine_same_sequence_fork"
    QUARANTINE_PREV_MISMATCH = "quarantine_prev_mismatch"
    QUARANTINE_COMPROMISED_OLD_KEY = "quarantine_compromised_old_key"
    QUARANTINE_UNAUTHORIZED_RECOVERY = "quarantine_unauthorized_recovery"
    QUARANTINE_ONE_FAMILY_RECOVERY = "quarantine_one_family_recovery"
    QUARANTINE_EXPIRED_EVENT = "quarantine_expired_event"


@dataclass(frozen=True)
class KeyCrisisRecord:
    kind: KeyCrisisKind
    scope_id: bytes
    old_public_key: bytes
    new_public_key: bytes
    sequence: int
    prev_event_digest: bytes
    issued_at: int
    expires_at: int
    old_signature: bytes = b""
    new_signature: bytes = b""

    def __post_init__(self) -> None:
        for name, value in (("scope_id", self.scope_id), ("old_public_key", self.old_public_key), ("new_public_key", self.new_public_key), ("prev_event_digest", self.prev_event_digest)):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if self.sequence <= 0 or self.expires_at <= self.issued_at:
            raise ValueError("key crisis counters invalid")

    @classmethod
    def create_succession(
        cls,
        *,
        old_keypair: DhtKeypair,
        new_keypair: DhtKeypair,
        scope_id: bytes,
        sequence: int,
        prev_event_digest: bytes = ZERO_DIGEST,
        issued_at: int,
        ttl: int = 86_400,
    ) -> "KeyCrisisRecord":
        unsigned = cls(
            kind=KeyCrisisKind.SUCCESSION,
            scope_id=scope_id,
            old_public_key=old_keypair.public_key_bytes,
            new_public_key=new_keypair.public_key_bytes,
            sequence=sequence,
            prev_event_digest=prev_event_digest,
            issued_at=issued_at,
            expires_at=issued_at + ttl,
        )
        payload = unsigned.unsigned_payload()
        return replace(unsigned, old_signature=old_keypair.sign(payload), new_signature=new_keypair.sign(payload))

    @classmethod
    def create_recovery_rotation(
        cls,
        *,
        old_public_key: bytes,
        new_keypair: DhtKeypair,
        scope_id: bytes,
        sequence: int,
        prev_event_digest: bytes = ZERO_DIGEST,
        issued_at: int,
        ttl: int = 86_400,
    ) -> "KeyCrisisRecord":
        unsigned = cls(
            kind=KeyCrisisKind.RECOVERY_ROTATION,
            scope_id=scope_id,
            old_public_key=old_public_key,
            new_public_key=new_keypair.public_key_bytes,
            sequence=sequence,
            prev_event_digest=prev_event_digest,
            issued_at=issued_at,
            expires_at=issued_at + ttl,
        )
        return replace(unsigned, new_signature=new_keypair.sign(unsigned.unsigned_payload()))

    def unsigned_bvalue(self) -> dict[bytes, object]:
        return {
            b"kind": self.kind.value,
            b"scope_id": self.scope_id,
            b"old_public_key": self.old_public_key,
            b"new_public_key": self.new_public_key,
            b"sequence": self.sequence,
            b"prev_event_digest": self.prev_event_digest,
            b"issued_at": self.issued_at,
            b"expires_at": self.expires_at,
        }

    def unsigned_payload(self) -> bytes:
        return KEY_CRISIS_DOMAIN + b":record-unsigned:" + bencode(self.unsigned_bvalue())

    @property
    def record_digest(self) -> bytes:
        return sha256(KEY_CRISIS_DOMAIN + b":record:" + self.unsigned_payload() + self.old_signature + self.new_signature)

    def verify(self, *, now: int) -> bool:
        if not (self.issued_at <= now < self.expires_at):
            return False
        payload = self.unsigned_payload()
        new_ok = verify_signature(self.new_public_key, payload, self.new_signature)
        old_ok = verify_signature(self.old_public_key, payload, self.old_signature)
        if self.kind is KeyCrisisKind.SUCCESSION:
            return old_ok and new_ok
        return new_ok


@dataclass(frozen=True)
class RecoveryWitness:
    witness_public_key: bytes
    crisis_digest: bytes
    source_family: str
    path_family: str
    issued_at: int
    expires_at: int
    signature: bytes = b""

    def __post_init__(self) -> None:
        if len(self.witness_public_key) != 32 or len(self.crisis_digest) != 32:
            raise ValueError("recovery witness keys/digests must be 32 bytes")
        if not self.source_family or not self.path_family:
            raise ValueError("recovery witness needs family hints")
        if self.expires_at <= self.issued_at:
            raise ValueError("recovery witness expiry invalid")

    @classmethod
    def create(
        cls,
        *,
        keypair: DhtKeypair,
        crisis_digest: bytes,
        source_family: str,
        path_family: str,
        issued_at: int,
        ttl: int = 86_400,
    ) -> "RecoveryWitness":
        unsigned = cls(
            witness_public_key=keypair.public_key_bytes,
            crisis_digest=crisis_digest,
            source_family=source_family,
            path_family=path_family,
            issued_at=issued_at,
            expires_at=issued_at + ttl,
        )
        return replace(unsigned, signature=keypair.sign(unsigned.unsigned_payload()))

    def unsigned_bvalue(self) -> dict[bytes, object]:
        return {
            b"witness_public_key": self.witness_public_key,
            b"crisis_digest": self.crisis_digest,
            b"source_family": self.source_family,
            b"path_family": self.path_family,
            b"issued_at": self.issued_at,
            b"expires_at": self.expires_at,
        }

    def unsigned_payload(self) -> bytes:
        return KEY_CRISIS_DOMAIN + b":recovery-witness-unsigned:" + bencode(self.unsigned_bvalue())

    @property
    def witness_digest(self) -> bytes:
        return sha256(KEY_CRISIS_DOMAIN + b":witness:" + self.unsigned_payload() + self.signature)

    def verify(self, *, now: int) -> bool:
        return self.issued_at <= now < self.expires_at and verify_signature(self.witness_public_key, self.unsigned_payload(), self.signature)


@dataclass(frozen=True)
class KeyCrisisPolicy:
    recovery_public_keys: tuple[bytes, ...] = ()
    recovery_threshold: int = 2
    min_recovery_families: int = 2

    def validate(self) -> None:
        if self.recovery_threshold <= 0 or self.min_recovery_families <= 0:
            raise ValueError("key crisis policy minimums invalid")
        for key in self.recovery_public_keys:
            if len(key) != 32:
                raise ValueError("recovery public keys must be 32 bytes")


@dataclass(frozen=True)
class KeyCrisisAssessment:
    decision_kind: KeyCrisisDecisionKind
    accept: bool
    reason: str
    record_digest: bytes
    accepted_new_public_key: bytes | None
    recovery_witness_count: int
    recovery_family_count: int
    quarantine_digests: tuple[bytes, ...]
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def assess_key_crisis(
    record: KeyCrisisRecord,
    witnesses: tuple[RecoveryWitness, ...] = (),
    *,
    now: int,
    previous_sequence: int = 0,
    previous_event_digest: bytes = ZERO_DIGEST,
    previous_same_sequence_digest: bytes | None = None,
    old_key_compromised: bool = False,
    policy: KeyCrisisPolicy | None = None,
) -> KeyCrisisAssessment:
    policy = policy or KeyCrisisPolicy()
    policy.validate()
    quarantine: list[bytes] = []
    accepted_key: bytes | None = None

    if not (record.issued_at <= now < record.expires_at):
        decision = KeyCrisisDecisionKind.QUARANTINE_EXPIRED_EVENT
        reason = "key crisis record is outside its validity window"
    elif not record.verify(now=now):
        decision = KeyCrisisDecisionKind.QUARANTINE_BAD_SIGNATURE
        reason = "key crisis record signature set is invalid"
    elif record.sequence < previous_sequence:
        decision = KeyCrisisDecisionKind.QUARANTINE_ROLLBACK
        reason = "key crisis record rolls back local succession memory"
    elif previous_same_sequence_digest is not None and record.sequence == previous_sequence and record.record_digest != previous_same_sequence_digest:
        decision = KeyCrisisDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK
        reason = "same-sequence key crisis fork detected"
    elif previous_sequence and record.sequence > previous_sequence and record.prev_event_digest != previous_event_digest:
        decision = KeyCrisisDecisionKind.QUARANTINE_PREV_MISMATCH
        reason = "key crisis record does not link to previous accepted key event"
    elif record.kind is KeyCrisisKind.SUCCESSION and old_key_compromised:
        decision = KeyCrisisDecisionKind.QUARANTINE_COMPROMISED_OLD_KEY
        reason = "ordinary old-key succession is not enough after compromise is declared"
    elif record.kind is KeyCrisisKind.SUCCESSION:
        decision = KeyCrisisDecisionKind.ACCEPT_SUCCESSION
        reason = "old and new writer keys co-signed a linked succession"
        accepted_key = record.new_public_key
    else:
        allowed = set(policy.recovery_public_keys)
        valid_witnesses = tuple(
            witness for witness in witnesses
            if witness.crisis_digest == record.record_digest and witness.witness_public_key in allowed and witness.verify(now=now)
        )
        unique_keys = {witness.witness_public_key for witness in valid_witnesses}
        families = {witness.source_family for witness in valid_witnesses}
        if len(unique_keys) < policy.recovery_threshold:
            decision = KeyCrisisDecisionKind.CONTINUE_NEEDS_RECOVERY_WITNESSES
            reason = "recovery rotation lacks enough authorized recovery witnesses"
        elif len(families) < policy.min_recovery_families:
            decision = KeyCrisisDecisionKind.QUARANTINE_ONE_FAMILY_RECOVERY
            reason = "recovery witnesses are authorized but source-family monocultured"
        else:
            decision = KeyCrisisDecisionKind.ACCEPT_RECOVERY_ROTATION
            reason = "new key plus diverse authorized recovery witnesses can rotate away from compromised old key"
            accepted_key = record.new_public_key

    if decision.value.startswith("quarantine_"):
        quarantine.append(record.record_digest)
    valid_recovery_witnesses = tuple(
        witness for witness in witnesses
        if witness.crisis_digest == record.record_digest and witness.verify(now=now)
    )
    family_count = len({witness.source_family for witness in valid_recovery_witnesses})
    report_digest = sha256(KEY_CRISIS_DOMAIN + b":report:" + bencode({
        b"decision": decision.value,
        b"record": record.record_digest,
        b"accepted": accepted_key or b"",
        b"witnesses": [witness.witness_digest for witness in valid_recovery_witnesses],
        b"families": family_count,
        b"quarantine": quarantine,
    }))
    return KeyCrisisAssessment(
        decision_kind=decision,
        accept=accepted_key is not None,
        reason=reason,
        record_digest=record.record_digest,
        accepted_new_public_key=accepted_key,
        recovery_witness_count=len({witness.witness_public_key for witness in valid_recovery_witnesses}),
        recovery_family_count=family_count,
        quarantine_digests=tuple(quarantine),
        report_digest=report_digest,
    )

# --- rev0030 local key-crisis gate extension ---------------------------------
# The earlier rev0030 branchlet modeled writer succession and recovery rotation.
# The active fold also needs operational crisis notices that gate peer leases,
# mutable heads, and garden offers.  These classes intentionally coexist with
# KeyCrisisRecord/assess_key_crisis above instead of deleting that branchlet.

class KeyCrisisVerdictKind(str, Enum):
    ACCEPT_FIRST = "accept_first"
    ACCEPT_ADVANCE = "accept_advance"
    ACCEPT_REFRESH = "accept_refresh"
    REJECT_BAD_SIGNATURE = "reject_bad_signature"
    REJECT_EXPIRED = "reject_expired"
    REJECT_ROLLBACK = "reject_rollback"
    QUARANTINE_SAME_SEQUENCE_FORK = "quarantine_same_sequence_fork"


class KeyCrisisGateDecisionKind(str, Enum):
    ACCEPT_NO_LIVE_CRISIS = "accept_no_live_crisis"
    ACCEPT_SUCCESSION_RECOVERY = "accept_succession_recovery"
    WATCH_DESTINATION_LOST = "watch_destination_lost"
    BLOCK_KEY_COMPROMISED = "block_key_compromised"
    BLOCK_EMERGENCY_FREEZE = "block_emergency_freeze"
    BLOCK_SIGNER_FORKED = "block_signer_forked"
    BLOCK_SUCCESSION_REQUIRED = "block_succession_required"
    QUARANTINE_CRISIS_FORK = "quarantine_crisis_fork"


@dataclass(frozen=True)
class KeyCrisisNotice:
    subject_public_key: bytes
    kind: KeyCrisisKind
    issuer_public_key: bytes
    issuer_family: str
    sequence: int
    issued_at: int
    expires_at: int
    scope_digest: bytes
    successor_public_key: bytes = b""
    reason: str = ""
    signature: bytes = b""

    def __post_init__(self) -> None:
        for name, value in (("subject_public_key", self.subject_public_key), ("issuer_public_key", self.issuer_public_key), ("scope_digest", self.scope_digest)):
            if len(value) != 32:
                raise ValueError(f"key crisis {name} must be 32 bytes")
        if self.successor_public_key and len(self.successor_public_key) != 32:
            raise ValueError("successor_public_key must be empty or 32 bytes")
        if self.sequence < 0 or self.expires_at <= self.issued_at:
            raise ValueError("key crisis notice sequence/time invalid")
        if not self.issuer_family:
            raise ValueError("issuer_family is required")

    @classmethod
    def create(
        cls,
        *,
        issuer_keypair: DhtKeypair,
        subject_public_key: bytes,
        kind: KeyCrisisKind,
        issuer_family: str,
        sequence: int,
        issued_at: int,
        ttl: int,
        scope_digest: bytes,
        successor_public_key: bytes = b"",
        reason: str = "",
    ) -> "KeyCrisisNotice":
        if ttl <= 0:
            raise ValueError("key crisis notice ttl must be positive")
        unsigned = cls(
            subject_public_key=subject_public_key,
            kind=kind,
            issuer_public_key=issuer_keypair.public_key_bytes,
            issuer_family=issuer_family,
            sequence=sequence,
            issued_at=issued_at,
            expires_at=issued_at + ttl,
            scope_digest=scope_digest,
            successor_public_key=successor_public_key,
            reason=reason[:160],
        )
        return replace(unsigned, signature=issuer_keypair.sign(unsigned.notice_unsigned_payload()))

    def notice_bvalue(self) -> dict[bytes, object]:
        return {
            b"subject_public_key": self.subject_public_key,
            b"kind": self.kind.value,
            b"issuer_public_key": self.issuer_public_key,
            b"issuer_family": self.issuer_family,
            b"sequence": self.sequence,
            b"issued_at": self.issued_at,
            b"expires_at": self.expires_at,
            b"scope_digest": self.scope_digest,
            b"successor_public_key": self.successor_public_key,
            b"reason": self.reason,
        }

    def notice_unsigned_payload(self) -> bytes:
        return KEY_CRISIS_DOMAIN + b":notice-unsigned:" + bencode(self.notice_bvalue())

    @property
    def notice_digest(self) -> bytes:
        return sha256(KEY_CRISIS_DOMAIN + b":notice:" + self.notice_unsigned_payload() + self.signature)

    def live(self, *, now: int) -> bool:
        return self.issued_at <= now < self.expires_at

    def verify_notice(self, *, now: int | None = None, allow_expired: bool = False) -> bool:
        if now is not None and not allow_expired and not self.live(now=now):
            return False
        return verify_signature(self.issuer_public_key, self.notice_unsigned_payload(), self.signature)


@dataclass(frozen=True)
class KeyCrisisState:
    subject_public_key: bytes
    highest_sequence: int
    accepted_notice_digest: bytes
    active_kind: KeyCrisisKind
    expires_at: int
    issuer_families: frozenset[str]
    successor_public_key: bytes = b""
    fork_digests: frozenset[bytes] = frozenset()

    @property
    def forked(self) -> bool:
        return bool(self.fork_digests)

    def live(self, *, now: int) -> bool:
        return now < self.expires_at


@dataclass(frozen=True)
class KeyCrisisVerdict:
    kind: KeyCrisisVerdictKind
    accepted: bool
    reason: str
    subject_public_key: bytes
    sequence: int
    notice_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.kind is KeyCrisisVerdictKind.QUARANTINE_SAME_SEQUENCE_FORK


@dataclass
class KeyCrisisMemory:
    states: dict[bytes, KeyCrisisState] = field(default_factory=dict)
    verdicts: list[KeyCrisisVerdict] = field(default_factory=list)

    def observe(self, notice: KeyCrisisNotice, *, now: int) -> KeyCrisisVerdict:
        current = self.states.get(notice.subject_public_key)
        if not notice.verify_notice(now=now):
            if notice.verify_notice(now=now, allow_expired=True) and not notice.live(now=now):
                verdict = KeyCrisisVerdict(KeyCrisisVerdictKind.REJECT_EXPIRED, False, "key crisis notice is expired", notice.subject_public_key, notice.sequence, notice.notice_digest)
            else:
                verdict = KeyCrisisVerdict(KeyCrisisVerdictKind.REJECT_BAD_SIGNATURE, False, "key crisis notice failed signature or shape validation", notice.subject_public_key, notice.sequence, notice.notice_digest)
            self.verdicts.append(verdict)
            return verdict
        if current is None:
            self.states[notice.subject_public_key] = KeyCrisisState(notice.subject_public_key, notice.sequence, notice.notice_digest, notice.kind, notice.expires_at, frozenset({notice.issuer_family}), notice.successor_public_key)
            verdict = KeyCrisisVerdict(KeyCrisisVerdictKind.ACCEPT_FIRST, True, "first live crisis notice for key", notice.subject_public_key, notice.sequence, notice.notice_digest)
            self.verdicts.append(verdict)
            return verdict
        if notice.sequence < current.highest_sequence:
            verdict = KeyCrisisVerdict(KeyCrisisVerdictKind.REJECT_ROLLBACK, False, "older key crisis notice replayed", notice.subject_public_key, notice.sequence, notice.notice_digest)
            self.verdicts.append(verdict)
            return verdict
        if notice.sequence == current.highest_sequence:
            if notice.notice_digest == current.accepted_notice_digest:
                self.states[notice.subject_public_key] = replace(current, issuer_families=frozenset(set(current.issuer_families) | {notice.issuer_family}), expires_at=max(current.expires_at, notice.expires_at))
                verdict = KeyCrisisVerdict(KeyCrisisVerdictKind.ACCEPT_REFRESH, True, "same key crisis notice refreshed", notice.subject_public_key, notice.sequence, notice.notice_digest)
                self.verdicts.append(verdict)
                return verdict
            forks = frozenset(set(current.fork_digests) | {current.accepted_notice_digest, notice.notice_digest})
            self.states[notice.subject_public_key] = replace(current, fork_digests=forks, issuer_families=frozenset(set(current.issuer_families) | {notice.issuer_family}))
            verdict = KeyCrisisVerdict(KeyCrisisVerdictKind.QUARANTINE_SAME_SEQUENCE_FORK, False, "same-sequence key crisis fork", notice.subject_public_key, notice.sequence, notice.notice_digest)
            self.verdicts.append(verdict)
            return verdict
        self.states[notice.subject_public_key] = KeyCrisisState(notice.subject_public_key, notice.sequence, notice.notice_digest, notice.kind, notice.expires_at, frozenset({notice.issuer_family}), notice.successor_public_key)
        verdict = KeyCrisisVerdict(KeyCrisisVerdictKind.ACCEPT_ADVANCE, True, "key crisis notice advanced", notice.subject_public_key, notice.sequence, notice.notice_digest)
        self.verdicts.append(verdict)
        return verdict


@dataclass(frozen=True)
class KeyCrisisGateReport:
    decision_kind: KeyCrisisGateDecisionKind
    accept: bool
    reason: str
    subject_public_key: bytes
    active_notice_digest: bytes
    report_digest: bytes

    @property
    def blocked(self) -> bool:
        return self.decision_kind.value.startswith("block_")


def gate_keyed_operation(
    *,
    subject_public_key: bytes,
    memory: KeyCrisisMemory,
    now: int,
    successor_evidence_public_key: bytes = b"",
) -> KeyCrisisGateReport:
    if len(subject_public_key) != 32:
        raise ValueError("subject_public_key must be 32 bytes")
    state = memory.states.get(subject_public_key)
    if state is None or not state.live(now=now):
        return _gate_report(KeyCrisisGateDecisionKind.ACCEPT_NO_LIVE_CRISIS, True, "no live crisis notice gates this key", subject_public_key, b"")
    if state.forked:
        return _gate_report(KeyCrisisGateDecisionKind.QUARANTINE_CRISIS_FORK, False, "key crisis evidence forked at the same sequence", subject_public_key, state.accepted_notice_digest)
    if state.active_kind is KeyCrisisKind.DESTINATION_LOST:
        return _gate_report(KeyCrisisGateDecisionKind.WATCH_DESTINATION_LOST, True, "destination-loss notice should prefer alternate routes but does not block all key use", subject_public_key, state.accepted_notice_digest)
    if state.active_kind in {KeyCrisisKind.KEY_COMPROMISED, KeyCrisisKind.SUCCESSION_REQUIRED} and successor_evidence_public_key and successor_evidence_public_key == state.successor_public_key:
        return _gate_report(KeyCrisisGateDecisionKind.ACCEPT_SUCCESSION_RECOVERY, True, "successor evidence matches live crisis notice", subject_public_key, state.accepted_notice_digest)
    if state.active_kind is KeyCrisisKind.KEY_COMPROMISED:
        return _gate_report(KeyCrisisGateDecisionKind.BLOCK_KEY_COMPROMISED, False, "live key-compromise notice blocks risky keyed operations", subject_public_key, state.accepted_notice_digest)
    if state.active_kind is KeyCrisisKind.EMERGENCY_FREEZE:
        return _gate_report(KeyCrisisGateDecisionKind.BLOCK_EMERGENCY_FREEZE, False, "live emergency freeze blocks risky keyed operations", subject_public_key, state.accepted_notice_digest)
    if state.active_kind is KeyCrisisKind.SIGNER_FORKED:
        return _gate_report(KeyCrisisGateDecisionKind.BLOCK_SIGNER_FORKED, False, "live signer-fork notice blocks risky keyed operations", subject_public_key, state.accepted_notice_digest)
    return _gate_report(KeyCrisisGateDecisionKind.BLOCK_SUCCESSION_REQUIRED, False, "live succession-required notice lacks matching successor evidence", subject_public_key, state.accepted_notice_digest)


def _gate_report(kind: KeyCrisisGateDecisionKind, accept: bool, reason: str, subject_public_key: bytes, active_notice_digest: bytes) -> KeyCrisisGateReport:
    digest = sha256(KEY_CRISIS_DOMAIN + b":gate-report:" + bencode({
        b"decision": kind.value,
        b"accept": 1 if accept else 0,
        b"subject": subject_public_key,
        b"notice": active_notice_digest,
    }))
    return KeyCrisisGateReport(kind, accept, reason, subject_public_key, active_notice_digest, digest)
