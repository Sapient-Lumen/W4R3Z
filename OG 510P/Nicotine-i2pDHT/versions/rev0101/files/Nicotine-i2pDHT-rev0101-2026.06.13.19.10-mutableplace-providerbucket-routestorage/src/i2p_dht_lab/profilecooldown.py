"""Profile-level cooldown after emergency freeze.

Emergency freeze is useful only if resume cannot bypass it by presenting one
fresh service/session report.  rev0042 models cooldown as signed local profile
memory that must be monotonic, previous-linked, and cleared by diverse recovery
evidence before garden/bridge operation resumes.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256

PROFILE_COOLDOWN_DOMAIN = DOMAIN + b":profile-cooldown-v1:"
ZERO_DIGEST = b"\x00" * 32


class CooldownKind(str, Enum):
    EMERGENCY_FREEZE = "emergency_freeze"
    KEY_CRISIS = "key_crisis"
    ROUTER_CRISIS = "router_crisis"
    OPERATOR_HOLD = "operator_hold"
    CLEARANCE = "clearance"


class RecoverySignalKind(str, Enum):
    OPERATOR_RESUME = "operator_resume"
    BREAKER_RECOVERY = "breaker_recovery"
    ROUTER_OK = "router_ok"
    HARD_NEGATIVE_SCAN = "hard_negative_scan"
    ANNOUNCEMENT_REPAIR = "announcement_repair"
    SUCCESSOR_KEY_READY = "successor_key_ready"


class CooldownDecisionKind(str, Enum):
    ACCEPT_RESUME_AFTER_COOLDOWN = "accept_resume_after_cooldown"
    ACCEPT_CLEARANCE_RECORD = "accept_clearance_record"
    HOLD_COOLDOWN_ACTIVE = "hold_cooldown_active"
    HOLD_NEEDS_RECOVERY_EVIDENCE = "hold_needs_recovery_evidence"
    HOLD_LOW_RECOVERY_FAMILY_DIVERSITY = "hold_low_recovery_family_diversity"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_SIGNAL_BAD_SIGNATURE = "quarantine_signal_bad_signature"
    QUARANTINE_EXPIRED_OR_FUTURE = "quarantine_expired_or_future"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_PROFILE_DRIFT = "quarantine_profile_drift"
    QUARANTINE_HARD_NEGATIVE_PRESENT = "quarantine_hard_negative_present"


@dataclass(frozen=True)
class ProfileCooldownEntry:
    profile_id: str
    kind: CooldownKind
    sequence: int
    previous_entry_digest: bytes
    issued_at: int
    expires_at: int
    frozen_until: int
    required_signal_kinds: tuple[RecoverySignalKind, ...]
    signer_public_key: bytes
    hard_negative_present: bool = False
    signature: bytes = b""

    def __post_init__(self) -> None:
        if not self.profile_id or len(self.profile_id.encode("utf-8")) > 80:
            raise ValueError("profile_id must be short and non-empty")
        if self.sequence < 0:
            raise ValueError("cooldown sequence must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("cooldown entry must expire after issue")
        if self.frozen_until < self.issued_at:
            raise ValueError("frozen_until must not precede issue")
        if len(self.previous_entry_digest) != 32 or len(self.signer_public_key) != 32:
            raise ValueError("cooldown digests and signer key must be 32 bytes")
        if self.signature and len(self.signature) != 64:
            raise ValueError("cooldown signature must be Ed25519-sized")

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"profile": self.profile_id,
            b"kind": self.kind.value,
            b"seq": self.sequence,
            b"prev": self.previous_entry_digest,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"frozen_until": self.frozen_until,
            b"required": [kind.value for kind in self.required_signal_kinds],
            b"signer": self.signer_public_key,
            b"hard_negative": 1 if self.hard_negative_present else 0,
        }

    @property
    def entry_digest(self) -> bytes:
        return sha256(PROFILE_COOLDOWN_DOMAIN + b":entry-digest:" + bencode(self.unsigned_bvalue()))

    def signature_payload(self) -> bytes:
        return PROFILE_COOLDOWN_DOMAIN + b":entry-sig:" + bencode(self.unsigned_bvalue())

    def verifies(self) -> bool:
        return verify_signature(self.signer_public_key, self.signature_payload(), self.signature)


@dataclass(frozen=True)
class RecoverySignal:
    profile_id: str
    kind: RecoverySignalKind
    evidence_digest: bytes
    issued_at: int
    expires_at: int
    family_id: str
    signer_public_key: bytes
    hard_negative_clear: bool = True
    signature: bytes = b""

    def __post_init__(self) -> None:
        if not self.profile_id:
            raise ValueError("profile_id must be non-empty")
        if len(self.evidence_digest) != 32 or len(self.signer_public_key) != 32:
            raise ValueError("signal digest and signer must be 32 bytes")
        if self.expires_at <= self.issued_at:
            raise ValueError("recovery signal expires_at must be after issued_at")
        if not self.family_id:
            raise ValueError("recovery family must be non-empty")
        if self.signature and len(self.signature) != 64:
            raise ValueError("recovery signature must be Ed25519-sized")

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"profile": self.profile_id,
            b"kind": self.kind.value,
            b"evidence": self.evidence_digest,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"family": self.family_id,
            b"signer": self.signer_public_key,
            b"clear": 1 if self.hard_negative_clear else 0,
        }

    @property
    def signal_digest(self) -> bytes:
        return sha256(PROFILE_COOLDOWN_DOMAIN + b":signal-digest:" + bencode(self.unsigned_bvalue()))

    def signature_payload(self) -> bytes:
        return PROFILE_COOLDOWN_DOMAIN + b":signal-sig:" + bencode(self.unsigned_bvalue())

    def verifies(self) -> bool:
        return verify_signature(self.signer_public_key, self.signature_payload(), self.signature)


@dataclass(frozen=True)
class CooldownPolicy:
    min_recovery_families: int = 2
    default_required_signals: tuple[RecoverySignalKind, ...] = (RecoverySignalKind.OPERATOR_RESUME, RecoverySignalKind.BREAKER_RECOVERY, RecoverySignalKind.ROUTER_OK, RecoverySignalKind.HARD_NEGATIVE_SCAN)


@dataclass(frozen=True)
class CooldownReport:
    decision_kind: CooldownDecisionKind
    accept: bool
    reason: str
    profile_id: str
    latest_sequence: int
    latest_entry_digest: bytes | None
    signal_digests: tuple[bytes, ...]
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def make_profile_cooldown_entry(
    *,
    keypair: DhtKeypair,
    profile_id: str,
    kind: CooldownKind,
    sequence: int,
    previous_entry_digest: bytes = ZERO_DIGEST,
    issued_at: int,
    expires_at: int,
    frozen_until: int,
    required_signal_kinds: tuple[RecoverySignalKind, ...] | None = None,
    hard_negative_present: bool = False,
) -> ProfileCooldownEntry:
    entry = ProfileCooldownEntry(
        profile_id=profile_id,
        kind=kind,
        sequence=sequence,
        previous_entry_digest=previous_entry_digest,
        issued_at=issued_at,
        expires_at=expires_at,
        frozen_until=frozen_until,
        required_signal_kinds=required_signal_kinds or CooldownPolicy().default_required_signals,
        signer_public_key=keypair.public_key_bytes,
        hard_negative_present=hard_negative_present,
    )
    return replace(entry, signature=keypair.sign(entry.signature_payload()))


def make_recovery_signal(
    *,
    keypair: DhtKeypair,
    profile_id: str,
    kind: RecoverySignalKind,
    evidence_digest: bytes,
    issued_at: int,
    expires_at: int,
    family_id: str,
    hard_negative_clear: bool = True,
) -> RecoverySignal:
    signal = RecoverySignal(
        profile_id=profile_id,
        kind=kind,
        evidence_digest=evidence_digest,
        issued_at=issued_at,
        expires_at=expires_at,
        family_id=family_id,
        signer_public_key=keypair.public_key_bytes,
        hard_negative_clear=hard_negative_clear,
    )
    return replace(signal, signature=keypair.sign(signal.signature_payload()))


def _report(kind: CooldownDecisionKind, accept: bool, reason: str, profile_id: str, entries: Iterable[ProfileCooldownEntry], signals: Iterable[RecoverySignal]) -> CooldownReport:
    entry_tuple = tuple(sorted(entries, key=lambda item: (item.sequence, item.entry_digest)))
    signal_tuple = tuple(sorted(signals, key=lambda item: (item.kind.value, item.signal_digest)))
    latest = entry_tuple[-1] if entry_tuple else None
    signal_digests = tuple(sorted(item.signal_digest for item in signal_tuple))
    digest = sha256(PROFILE_COOLDOWN_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"reason": reason,
        b"profile": profile_id,
        b"latest_seq": latest.sequence if latest else -1,
        b"latest": latest.entry_digest if latest else b"",
        b"signals": list(signal_digests),
    }))
    return CooldownReport(kind, accept, reason, profile_id, latest.sequence if latest else -1, latest.entry_digest if latest else None, signal_digests, digest)


def assess_profile_cooldown(
    entries: Iterable[ProfileCooldownEntry],
    signals: Iterable[RecoverySignal],
    *,
    now: int,
    expected_profile_id: str,
    previous_sequence: int | None = None,
    previous_entry_digest: bytes | None = None,
    previously_seen_entries: Iterable[bytes] = (),
    policy: CooldownPolicy | None = None,
) -> CooldownReport:
    policy = policy or CooldownPolicy()
    entry_tuple = tuple(sorted(entries, key=lambda item: (item.sequence, item.entry_digest)))
    signal_tuple = tuple(sorted(signals, key=lambda item: (item.kind.value, item.signal_digest)))
    seen = set(previously_seen_entries)
    for entry in entry_tuple:
        if not entry.verifies():
            return _report(CooldownDecisionKind.QUARANTINE_BAD_SIGNATURE, False, "bad cooldown signature", expected_profile_id, entry_tuple, signal_tuple)
        if entry.profile_id != expected_profile_id:
            return _report(CooldownDecisionKind.QUARANTINE_PROFILE_DRIFT, False, "cooldown profile drift", expected_profile_id, entry_tuple, signal_tuple)
        if entry.issued_at > now or entry.expires_at <= now:
            return _report(CooldownDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, False, "cooldown expired or future", expected_profile_id, entry_tuple, signal_tuple)
        if entry.entry_digest in seen:
            return _report(CooldownDecisionKind.QUARANTINE_REPLAY, False, "cooldown replay", expected_profile_id, entry_tuple, signal_tuple)
    if not entry_tuple:
        required = set(policy.default_required_signals)
        latest = None
    else:
        seq_map: dict[int, bytes] = {}
        for entry in entry_tuple:
            previous = seq_map.setdefault(entry.sequence, entry.entry_digest)
            if previous != entry.entry_digest:
                return _report(CooldownDecisionKind.QUARANTINE_SEQUENCE_FORK, False, "same-sequence cooldown fork", expected_profile_id, entry_tuple, signal_tuple)
        if previous_sequence is not None and max(item.sequence for item in entry_tuple) < previous_sequence:
            return _report(CooldownDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, "cooldown sequence rollback", expected_profile_id, entry_tuple, signal_tuple)
        if previous_entry_digest is not None and min(item.sequence for item in entry_tuple) == (previous_sequence or -1) + 1:
            first = min(entry_tuple, key=lambda item: item.sequence)
            if first.previous_entry_digest != previous_entry_digest:
                return _report(CooldownDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, "cooldown previous link mismatch", expected_profile_id, entry_tuple, signal_tuple)
        latest = max(entry_tuple, key=lambda item: (item.sequence, item.issued_at, item.entry_digest))
        required = set(latest.required_signal_kinds)
        if latest.hard_negative_present:
            return _report(CooldownDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESENT, False, "latest cooldown carries hard negative pressure", expected_profile_id, entry_tuple, signal_tuple)
        if latest.kind is CooldownKind.CLEARANCE:
            return _report(CooldownDecisionKind.ACCEPT_CLEARANCE_RECORD, True, "cooldown clearance record accepted", expected_profile_id, entry_tuple, signal_tuple)
        if now < latest.frozen_until:
            return _report(CooldownDecisionKind.HOLD_COOLDOWN_ACTIVE, False, "profile cooldown is still active", expected_profile_id, entry_tuple, signal_tuple)
    for signal in signal_tuple:
        if not signal.verifies():
            return _report(CooldownDecisionKind.QUARANTINE_SIGNAL_BAD_SIGNATURE, False, "bad recovery signal signature", expected_profile_id, entry_tuple, signal_tuple)
        if signal.profile_id != expected_profile_id:
            return _report(CooldownDecisionKind.QUARANTINE_PROFILE_DRIFT, False, "recovery signal profile drift", expected_profile_id, entry_tuple, signal_tuple)
        if signal.issued_at > now or signal.expires_at <= now:
            return _report(CooldownDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, False, "recovery signal expired or future", expected_profile_id, entry_tuple, signal_tuple)
        if not signal.hard_negative_clear:
            return _report(CooldownDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESENT, False, "recovery signal reports hard negative pressure", expected_profile_id, entry_tuple, signal_tuple)
    present = {signal.kind for signal in signal_tuple}
    missing = required - present
    if missing:
        return _report(CooldownDecisionKind.HOLD_NEEDS_RECOVERY_EVIDENCE, False, "missing required recovery signal kinds", expected_profile_id, entry_tuple, signal_tuple)
    families = {signal.family_id for signal in signal_tuple if signal.kind in required}
    if len(families) < policy.min_recovery_families:
        return _report(CooldownDecisionKind.HOLD_LOW_RECOVERY_FAMILY_DIVERSITY, False, "low recovery signal family diversity", expected_profile_id, entry_tuple, signal_tuple)
    return _report(CooldownDecisionKind.ACCEPT_RESUME_AFTER_COOLDOWN, True, "cooldown expired and recovery evidence is sufficient", expected_profile_id, entry_tuple, signal_tuple)
