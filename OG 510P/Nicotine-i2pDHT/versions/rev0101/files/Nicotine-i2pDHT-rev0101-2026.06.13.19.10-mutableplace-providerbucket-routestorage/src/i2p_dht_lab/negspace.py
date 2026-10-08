"""Negative-space / absence evidence for risky DHT lookups.

Absence is one of the easiest lies in a DHT: "no provider", "no newer head",
"no route", or "no tombstone" can all be returned quickly by a captured path.
This module makes absence a typed, signed, short-lived observation that needs
family and path diversity before it can influence local behavior.

It is not a proof of non-existence. It is a pressure surface for deciding when
negative answers are merely convenient and when they are diverse enough to stop
or slow a lookup.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256

NEGSPACE_DOMAIN = DOMAIN + b":negative-space-v1:"


class AbsenceKind(str, Enum):
    NO_PROVIDER = "no_provider"
    NO_MUTABLE_HEAD = "no_mutable_head"
    NO_ROUTE = "no_route"
    NO_TOMBSTONE = "no_tombstone"
    NO_CUSTODY = "no_custody"


class NegspaceDecisionKind(str, Enum):
    ACCEPT_DIVERSE_ABSENCE = "accept_diverse_absence"
    ACCEPT_WITH_WATCH = "accept_with_watch"
    CONTINUE_EMPTY = "continue_empty"
    CONTINUE_LOW_FAMILY_DIVERSITY = "continue_low_family_diversity"
    CONTINUE_LOW_PATH_DIVERSITY = "continue_low_path_diversity"
    REJECT_BAD_SIGNATURE = "reject_bad_signature"
    REJECT_EXPIRED = "reject_expired"
    QUARANTINE_POSITIVE_CONTRADICTION = "quarantine_positive_contradiction"
    QUARANTINE_RESPONDER_FORK = "quarantine_responder_fork"
    QUARANTINE_FAMILY_FLOOD = "quarantine_family_flood"


@dataclass(frozen=True)
class AbsenceObservation:
    kind: AbsenceKind
    target_digest: bytes
    request_digest: bytes
    responder_public_key: bytes
    responder_family: str
    path_family: str
    sequence: int
    issued_at: int
    expires_at: int
    note: str = ""
    signature: bytes = b""

    def __post_init__(self) -> None:
        for field_name, value in (("target_digest", self.target_digest), ("request_digest", self.request_digest), ("responder_public_key", self.responder_public_key)):
            if len(value) != 32:
                raise ValueError(f"absence {field_name} must be 32 bytes")
        if self.sequence < 0 or self.expires_at <= self.issued_at:
            raise ValueError("absence observation sequence/time bounds invalid")
        if not self.responder_family or not self.path_family:
            raise ValueError("absence observation needs responder and path families")

    @classmethod
    def create(
        cls,
        *,
        keypair: DhtKeypair,
        kind: AbsenceKind,
        target_digest: bytes,
        request_digest: bytes,
        responder_family: str,
        path_family: str,
        sequence: int,
        issued_at: int,
        ttl: int = 300,
        note: str = "",
    ) -> "AbsenceObservation":
        if ttl <= 0:
            raise ValueError("absence ttl must be positive")
        unsigned = cls(
            kind=kind,
            target_digest=target_digest,
            request_digest=request_digest,
            responder_public_key=keypair.public_key_bytes,
            responder_family=responder_family,
            path_family=path_family,
            sequence=sequence,
            issued_at=issued_at,
            expires_at=issued_at + ttl,
            note=note[:96],
        )
        return replace(unsigned, signature=keypair.sign(unsigned.unsigned_payload()))

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"kind": self.kind.value,
            b"target_digest": self.target_digest,
            b"request_digest": self.request_digest,
            b"responder_public_key": self.responder_public_key,
            b"responder_family": self.responder_family,
            b"path_family": self.path_family,
            b"sequence": self.sequence,
            b"issued_at": self.issued_at,
            b"expires_at": self.expires_at,
            b"note": self.note,
        }

    def unsigned_payload(self) -> bytes:
        return NEGSPACE_DOMAIN + b":absence-unsigned:" + bencode(self.bvalue())

    @property
    def observation_digest(self) -> bytes:
        return sha256(NEGSPACE_DOMAIN + b":absence:" + self.unsigned_payload() + self.signature)

    def live(self, *, now: int) -> bool:
        return self.issued_at <= now < self.expires_at

    def verify(self, *, now: int | None = None, allow_expired: bool = False) -> bool:
        if now is not None and not allow_expired and not self.live(now=now):
            return False
        return verify_signature(self.responder_public_key, self.unsigned_payload(), self.signature)


@dataclass(frozen=True)
class NegspacePolicy:
    min_responder_families: int = 2
    min_path_families: int = 2
    max_per_responder_family: int = 3
    require_positive_free: bool = True

    def validate(self) -> None:
        if self.min_responder_families <= 0 or self.min_path_families <= 0 or self.max_per_responder_family <= 0:
            raise ValueError("negative-space policy thresholds must be positive")


@dataclass(frozen=True)
class NegspaceReport:
    decision_kind: NegspaceDecisionKind
    accept: bool
    reason: str
    valid_observation_digests: tuple[bytes, ...]
    responder_families: tuple[str, ...]
    path_families: tuple[str, ...]
    positive_evidence_digests: tuple[bytes, ...]
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _report(
    *,
    decision_kind: NegspaceDecisionKind,
    accept: bool,
    reason: str,
    observations: Iterable[AbsenceObservation],
    positive_evidence_digests: Iterable[bytes] = (),
) -> NegspaceReport:
    obs_tuple = tuple(observations)
    obs_digests = tuple(sorted(obs.observation_digest for obs in obs_tuple))
    responder_families = tuple(sorted({obs.responder_family for obs in obs_tuple}))
    path_families = tuple(sorted({obs.path_family for obs in obs_tuple}))
    positives = tuple(sorted(positive_evidence_digests))
    digest = sha256(NEGSPACE_DOMAIN + b":report:" + bencode({
        b"decision": decision_kind.value,
        b"accept": 1 if accept else 0,
        b"observations": obs_digests,
        b"responder_families": responder_families,
        b"path_families": path_families,
        b"positives": positives,
    }))
    return NegspaceReport(decision_kind, accept, reason, obs_digests, responder_families, path_families, positives, digest)


def assess_negative_space(
    observations: Iterable[AbsenceObservation],
    *,
    now: int,
    target_digest: bytes,
    kind: AbsenceKind,
    request_digest: bytes | None = None,
    positive_evidence_digests: Iterable[bytes] = (),
    policy: NegspacePolicy | None = None,
) -> NegspaceReport:
    """Assess absence observations without treating them as proof.

    Positive evidence means a confirmed provider/head/route/tombstone/custody fact
    for the same target. If such evidence exists, valid negative answers become
    contradiction evidence rather than lookup termination.
    """
    policy = policy or NegspacePolicy()
    policy.validate()
    if len(target_digest) != 32:
        raise ValueError("target_digest must be 32 bytes")
    if request_digest is not None and len(request_digest) != 32:
        raise ValueError("request_digest must be 32 bytes")
    positives = tuple(positive_evidence_digests)
    valid: list[AbsenceObservation] = []
    saw_bad_signature = False
    saw_expired = False
    for observation in observations:
        if observation.kind is not kind or observation.target_digest != target_digest:
            continue
        if request_digest is not None and observation.request_digest != request_digest:
            continue
        if observation.verify(now=now):
            valid.append(observation)
        elif observation.verify(now=now, allow_expired=True) and not observation.live(now=now):
            saw_expired = True
        else:
            saw_bad_signature = True
    if not valid:
        if saw_bad_signature:
            return _report(decision_kind=NegspaceDecisionKind.REJECT_BAD_SIGNATURE, accept=False, reason="no valid observations; at least one bad signature was seen", observations=(), positive_evidence_digests=positives)
        if saw_expired:
            return _report(decision_kind=NegspaceDecisionKind.REJECT_EXPIRED, accept=False, reason="only expired negative observations were seen", observations=(), positive_evidence_digests=positives)
        return _report(decision_kind=NegspaceDecisionKind.CONTINUE_EMPTY, accept=False, reason="no matching negative observations", observations=(), positive_evidence_digests=positives)
    if positives and policy.require_positive_free:
        return _report(decision_kind=NegspaceDecisionKind.QUARANTINE_POSITIVE_CONTRADICTION, accept=False, reason="absence was contradicted by positive evidence for the same target", observations=valid, positive_evidence_digests=positives)
    by_responder_seq: dict[tuple[bytes, int], bytes] = {}
    for observation in valid:
        key = (observation.responder_public_key, observation.sequence)
        previous = by_responder_seq.get(key)
        if previous is not None and previous != observation.observation_digest:
            return _report(decision_kind=NegspaceDecisionKind.QUARANTINE_RESPONDER_FORK, accept=False, reason="one responder signed different absence observations at the same sequence", observations=valid, positive_evidence_digests=positives)
        by_responder_seq[key] = observation.observation_digest
    family_counts: dict[str, int] = {}
    for observation in valid:
        family_counts[observation.responder_family] = family_counts.get(observation.responder_family, 0) + 1
    if any(count > policy.max_per_responder_family for count in family_counts.values()):
        return _report(decision_kind=NegspaceDecisionKind.QUARANTINE_FAMILY_FLOOD, accept=False, reason="one responder family dominates negative observations", observations=valid, positive_evidence_digests=positives)
    responder_families = {observation.responder_family for observation in valid}
    if len(responder_families) < policy.min_responder_families:
        return _report(decision_kind=NegspaceDecisionKind.CONTINUE_LOW_FAMILY_DIVERSITY, accept=False, reason="absence lacks responder-family diversity", observations=valid, positive_evidence_digests=positives)
    path_families = {observation.path_family for observation in valid}
    if len(path_families) < policy.min_path_families:
        return _report(decision_kind=NegspaceDecisionKind.CONTINUE_LOW_PATH_DIVERSITY, accept=False, reason="absence lacks path-family diversity", observations=valid, positive_evidence_digests=positives)
    decision = NegspaceDecisionKind.ACCEPT_DIVERSE_ABSENCE if len(valid) >= policy.min_responder_families + 1 else NegspaceDecisionKind.ACCEPT_WITH_WATCH
    return _report(decision_kind=decision, accept=True, reason="diverse negative observations are locally useful but not proof of non-existence", observations=valid, positive_evidence_digests=positives)
