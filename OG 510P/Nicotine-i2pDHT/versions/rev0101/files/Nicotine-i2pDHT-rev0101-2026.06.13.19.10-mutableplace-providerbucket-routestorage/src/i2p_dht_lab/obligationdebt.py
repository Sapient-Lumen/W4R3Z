"""Proof-obligation debt for accepted local DHT decisions.

Risk-first design creates many gates that say "continue", "accept with watch",
or "accept for now".  Those decisions should leave behind explicit proof debt so
a later restart, garden, or repair pass knows what must still be checked.  This
module models signed obligations and signed evidence that clears them only when
scope/object/subject/kind and path-family diversity line up.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256

OBLIGATION_DEBT_DOMAIN = DOMAIN + b":obligation-debt-v1:"


class ObligationKind(str, Enum):
    PROVIDER_SEMANTIC_PROOF = "provider_semantic_proof"
    MUTABLE_HEAD_WITNESS = "mutable_head_witness"
    ROUTE_LIVENESS = "route_liveness"
    TOMBSTONE_REPAIR = "tombstone_repair"
    CUSTODY_CHALLENGE = "custody_challenge"


class ObligationDebtDecisionKind(str, Enum):
    ACCEPT_OBLIGATIONS_CLEARED = "accept_obligations_cleared"
    HOLD_MISSING_PROOF = "hold_missing_proof"
    HOLD_LOW_DIVERSITY = "hold_low_diversity"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_OVERDUE_DEBT = "quarantine_overdue_debt"
    QUARANTINE_SCOPE_MISMATCH = "quarantine_scope_mismatch"
    QUARANTINE_EVIDENCE_FORK = "quarantine_evidence_fork"


@dataclass(frozen=True)
class ObligationPolicy:
    min_source_families: int = 2
    min_path_families: int = 2
    allow_watch_before_due: bool = True

    def validate(self) -> None:
        if self.min_source_families <= 0 or self.min_path_families <= 0:
            raise ValueError("obligation policy counters must be positive")


@dataclass(frozen=True)
class ProofObligation:
    issuer_public_key: bytes
    kind: ObligationKind
    scope_id: bytes
    object_digest: bytes
    subject_digest: bytes
    sequence: int
    issued_at: int
    due_at: int
    note: str = ""
    signature: bytes = b""

    def __post_init__(self) -> None:
        for name, value in (("issuer_public_key", self.issuer_public_key), ("scope_id", self.scope_id), ("object_digest", self.object_digest), ("subject_digest", self.subject_digest)):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if self.sequence < 0 or self.due_at <= self.issued_at:
            raise ValueError("obligation counters invalid")
        if self.signature and len(self.signature) != 64:
            raise ValueError("obligation signature must be empty or 64 bytes")

    @classmethod
    def create(cls, *, keypair: DhtKeypair, kind: ObligationKind, scope_id: bytes, object_digest: bytes, subject_digest: bytes, sequence: int, issued_at: int, due_at: int, note: str = "") -> "ProofObligation":
        unsigned = cls(keypair.public_key_bytes, kind, scope_id, object_digest, subject_digest, sequence, issued_at, due_at, note)
        return cls(**{**unsigned.__dict__, "signature": keypair.sign(unsigned.signing_payload())})

    @property
    def digest(self) -> bytes:
        return sha256(OBLIGATION_DEBT_DOMAIN + b":obligation:" + self.signing_payload() + self.signature)

    def signing_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"issuer": self.issuer_public_key,
            b"kind": self.kind.value,
            b"scope": self.scope_id,
            b"object": self.object_digest,
            b"subject": self.subject_digest,
            b"sequence": self.sequence,
            b"issued_at": self.issued_at,
            b"due_at": self.due_at,
            b"note": self.note,
        }

    def signing_payload(self) -> bytes:
        return OBLIGATION_DEBT_DOMAIN + bencode(self.signing_bvalue())

    def verify(self) -> bool:
        return verify_signature(self.issuer_public_key, self.signing_payload(), self.signature)


@dataclass(frozen=True)
class ProofEvidence:
    witness_public_key: bytes
    kind: ObligationKind
    scope_id: bytes
    object_digest: bytes
    subject_digest: bytes
    source_family: str
    path_family: str
    sequence: int
    issued_at: int
    ttl: int
    verdict_digest: bytes
    note: str = ""
    signature: bytes = b""

    def __post_init__(self) -> None:
        for name, value in (("witness_public_key", self.witness_public_key), ("scope_id", self.scope_id), ("object_digest", self.object_digest), ("subject_digest", self.subject_digest), ("verdict_digest", self.verdict_digest)):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if not self.source_family or not self.path_family:
            raise ValueError("evidence needs source/path family hints")
        if self.sequence < 0 or self.ttl <= 0:
            raise ValueError("evidence counters invalid")
        if self.signature and len(self.signature) != 64:
            raise ValueError("evidence signature must be empty or 64 bytes")

    @classmethod
    def create(cls, *, keypair: DhtKeypair, kind: ObligationKind, scope_id: bytes, object_digest: bytes, subject_digest: bytes, source_family: str, path_family: str, sequence: int, issued_at: int, ttl: int, verdict_digest: bytes, note: str = "") -> "ProofEvidence":
        unsigned = cls(keypair.public_key_bytes, kind, scope_id, object_digest, subject_digest, source_family, path_family, sequence, issued_at, ttl, verdict_digest, note)
        return cls(**{**unsigned.__dict__, "signature": keypair.sign(unsigned.signing_payload())})

    @property
    def expires_at(self) -> int:
        return self.issued_at + self.ttl

    @property
    def payload_digest(self) -> bytes:
        return sha256(OBLIGATION_DEBT_DOMAIN + b":evidence-payload:" + self.signing_payload())

    @property
    def digest(self) -> bytes:
        return sha256(OBLIGATION_DEBT_DOMAIN + b":evidence:" + self.signing_payload() + self.signature)

    def live(self, *, now: int) -> bool:
        return self.issued_at <= now < self.expires_at

    def signing_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"witness": self.witness_public_key,
            b"kind": self.kind.value,
            b"scope": self.scope_id,
            b"object": self.object_digest,
            b"subject": self.subject_digest,
            b"source_family": self.source_family,
            b"path_family": self.path_family,
            b"sequence": self.sequence,
            b"issued_at": self.issued_at,
            b"ttl": self.ttl,
            b"verdict": self.verdict_digest,
            b"note": self.note,
        }

    def signing_payload(self) -> bytes:
        return OBLIGATION_DEBT_DOMAIN + bencode(self.signing_bvalue())

    def verify(self) -> bool:
        return verify_signature(self.witness_public_key, self.signing_payload(), self.signature)


@dataclass(frozen=True)
class ObligationDebtReport:
    decision_kind: ObligationDebtDecisionKind
    fulfilled_obligation_digests: tuple[bytes, ...]
    open_obligation_digests: tuple[bytes, ...]
    evidence_digests: tuple[bytes, ...]
    source_families: tuple[str, ...]
    path_families: tuple[str, ...]
    report_digest: bytes
    reason: str

    @property
    def accept(self) -> bool:
        return self.decision_kind is ObligationDebtDecisionKind.ACCEPT_OBLIGATIONS_CLEARED


def _report(kind: ObligationDebtDecisionKind, fulfilled: Iterable[bytes], open_: Iterable[bytes], evidence: Iterable[ProofEvidence], reason: str) -> ObligationDebtReport:
    ev = tuple(evidence)
    source_families = tuple(sorted({item.source_family for item in ev}))
    path_families = tuple(sorted({item.path_family for item in ev}))
    fulfilled_t = tuple(sorted(set(fulfilled)))
    open_t = tuple(sorted(set(open_)))
    evidence_digests = tuple(sorted({item.digest for item in ev}))
    digest = sha256(OBLIGATION_DEBT_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"fulfilled": list(fulfilled_t),
        b"open": list(open_t),
        b"evidence": list(evidence_digests),
        b"source_families": list(source_families),
        b"path_families": list(path_families),
        b"reason": reason,
    }))
    return ObligationDebtReport(kind, fulfilled_t, open_t, evidence_digests, source_families, path_families, digest, reason)


def _matches(obligation: ProofObligation, evidence: ProofEvidence) -> bool:
    return (
        obligation.kind is evidence.kind
        and obligation.scope_id == evidence.scope_id
        and obligation.object_digest == evidence.object_digest
        and obligation.subject_digest == evidence.subject_digest
    )


def assess_obligation_debt(obligations: Iterable[ProofObligation], evidence: Iterable[ProofEvidence], *, now: int, policy: ObligationPolicy | None = None) -> ObligationDebtReport:
    policy = policy or ObligationPolicy()
    policy.validate()
    obligations_t = tuple(obligations)
    evidence_t = tuple(evidence)
    for obligation in obligations_t:
        if not obligation.verify():
            return _report(ObligationDebtDecisionKind.QUARANTINE_BAD_SIGNATURE, (), (obligation.digest,), (), "bad obligation signature")
    seen_evidence: dict[tuple[bytes, int], bytes] = {}
    for item in evidence_t:
        if not item.verify():
            return _report(ObligationDebtDecisionKind.QUARANTINE_BAD_SIGNATURE, (), tuple(ob.digest for ob in obligations_t), (), "bad evidence signature")
        prior = seen_evidence.get((item.witness_public_key, item.sequence))
        if prior is not None and prior != item.payload_digest:
            return _report(ObligationDebtDecisionKind.QUARANTINE_EVIDENCE_FORK, (), tuple(ob.digest for ob in obligations_t), (item,), "same witness/sequence carried different evidence")
        seen_evidence[(item.witness_public_key, item.sequence)] = item.payload_digest

    fulfilled: list[bytes] = []
    open_: list[bytes] = []
    used: list[ProofEvidence] = []
    low_diversity = False
    for obligation in obligations_t:
        matching = tuple(item for item in evidence_t if item.live(now=now) and _matches(obligation, item))
        if not matching:
            open_.append(obligation.digest)
            continue
        source_families = {item.source_family for item in matching}
        path_families = {item.path_family for item in matching}
        if len(source_families) < policy.min_source_families or len(path_families) < policy.min_path_families:
            low_diversity = True
            open_.append(obligation.digest)
            used.extend(matching)
            continue
        fulfilled.append(obligation.digest)
        used.extend(matching)

    if open_:
        if any(ob.due_at <= now for ob in obligations_t if ob.digest in set(open_)):
            return _report(ObligationDebtDecisionKind.QUARANTINE_OVERDUE_DEBT, fulfilled, open_, used, "open obligation is past due")
        if low_diversity:
            return _report(ObligationDebtDecisionKind.HOLD_LOW_DIVERSITY, fulfilled, open_, used, "matching proof lacks source/path diversity")
        return _report(ObligationDebtDecisionKind.HOLD_MISSING_PROOF, fulfilled, open_, used, "obligation still awaits proof")
    return _report(ObligationDebtDecisionKind.ACCEPT_OBLIGATIONS_CLEARED, fulfilled, (), used, "all proof debt cleared with live diverse evidence")
