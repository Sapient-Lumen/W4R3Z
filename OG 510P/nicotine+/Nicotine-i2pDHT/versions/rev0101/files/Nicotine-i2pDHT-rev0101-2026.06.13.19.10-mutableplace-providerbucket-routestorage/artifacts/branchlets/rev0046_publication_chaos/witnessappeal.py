"""Witness appeal lane for watch-required public bridge policy.

Subjective policy is allowed to require watch instead of allowing a public bridge
side effect directly. This module models a local appeal lane: independent
witnesses can support a watched shadow-fire report as locally usable *with watch*
without turning witnesses into global authorities or bypassing hard negatives.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .shadowfire import ShadowFireAction, ShadowFireReport

WITNESS_APPEAL_DOMAIN = DOMAIN + b":witness-appeal-v1:"
ZERO_DIGEST = b"\x00" * 32


class WitnessAppealStatementKind(str, Enum):
    SUPPORT_WATCHED_ACTION = "support_watched_action"
    REFUTE_ACTION = "refute_action"
    REQUIRE_MORE_EVIDENCE = "require_more_evidence"
    HARD_NEGATIVE_CLEAR = "hard_negative_clear"


class WitnessAppealDecisionKind(str, Enum):
    ACCEPT_APPEAL_WITH_WATCH = "accept_appeal_with_watch"
    HOLD_NOT_WATCHED = "hold_not_watched"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    HOLD_MISSING_REQUIRED_KIND = "hold_missing_required_kind"
    HOLD_TOO_MANY_WATCH_STATEMENTS = "hold_too_many_watch_statements"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_EXPIRED_OR_FUTURE = "quarantine_expired_or_future"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_REQUEST_DRIFT = "quarantine_request_drift"
    QUARANTINE_ACTION_DRIFT = "quarantine_action_drift"
    QUARANTINE_REPORT_DIGEST_DRIFT = "quarantine_report_digest_drift"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_REFUTED = "quarantine_refuted"
    QUARANTINE_HARD_NEGATIVE = "quarantine_hard_negative"


@dataclass(frozen=True)
class WitnessAppealStatement:
    kind: WitnessAppealStatementKind
    action: ShadowFireAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    shadow_report_digest: bytes
    sequence: int
    issued_at: int
    expires_at: int
    signer_public_key: bytes
    family_id: str
    path_family: str
    note: str = ""
    signature: bytes = b""

    def __post_init__(self) -> None:
        for name, value in (("scope_digest", self.scope_digest), ("request_digest", self.request_digest), ("shadow_report_digest", self.shadow_report_digest), ("signer_public_key", self.signer_public_key)):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if self.sequence < 0 or self.expires_at <= self.issued_at:
            raise ValueError("invalid statement sequence/window")
        if not self.profile_id or not self.service_name or not self.family_id or not self.path_family:
            raise ValueError("statement ids/families must be non-empty")
        if len(self.note.encode("utf-8")) > 160:
            raise ValueError("statement note must be short")
        object.__setattr__(self, "kind", WitnessAppealStatementKind(self.kind))
        object.__setattr__(self, "action", ShadowFireAction(self.action))

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"kind": self.kind.value,
            b"action": self.action.value,
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"shadow": self.shadow_report_digest,
            b"seq": self.sequence,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"signer": self.signer_public_key,
            b"family": self.family_id,
            b"path_family": self.path_family,
            b"note": self.note,
        }

    def payload(self) -> bytes:
        return WITNESS_APPEAL_DOMAIN + b":statement:" + bencode(self.unsigned_bvalue())

    @property
    def statement_digest(self) -> bytes:
        return sha256(WITNESS_APPEAL_DOMAIN + b":statement-digest:" + self.payload() + self.signature)

    def verify(self) -> bool:
        return verify_signature(self.signer_public_key, self.payload(), self.signature)

    def with_signature(self, signature: bytes) -> "WitnessAppealStatement":
        return replace(self, signature=signature)


def make_witness_appeal_statement(*, keypair: DhtKeypair, kind: WitnessAppealStatementKind, action: ShadowFireAction, profile_id: str, service_name: str, scope_digest: bytes, request_digest: bytes, shadow_report_digest: bytes, sequence: int, issued_at: int, expires_at: int, family_id: str, path_family: str, note: str = "") -> WitnessAppealStatement:
    statement = WitnessAppealStatement(kind, action, profile_id, service_name, scope_digest, request_digest, shadow_report_digest, sequence, issued_at, expires_at, keypair.public_key_bytes, family_id, path_family, note)
    return statement.with_signature(keypair.sign(statement.payload()))


@dataclass(frozen=True)
class WitnessAppealPolicy:
    min_support_families: int = 3
    min_path_families: int = 2
    max_watch_statements: int = 1
    require_hard_negative_clear: bool = True


@dataclass(frozen=True)
class WitnessAppealReport:
    decision_kind: WitnessAppealDecisionKind
    accepted: bool
    reason: str
    action: ShadowFireAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    shadow_report_digest: bytes
    statement_digests: tuple[bytes, ...]
    family_count: int
    path_family_count: int
    watch: bool
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _report(kind: WitnessAppealDecisionKind, accepted: bool, reason: str, *, shadow_fire: ShadowFireReport, statements: Iterable[WitnessAppealStatement] = (), family_count: int = 0, path_family_count: int = 0, watch: bool = True) -> WitnessAppealReport:
    st = tuple(statements)
    digests = tuple(sorted(item.statement_digest for item in st))
    digest = sha256(WITNESS_APPEAL_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accepted": 1 if accepted else 0,
        b"reason": reason,
        b"action": shadow_fire.action.value,
        b"profile": shadow_fire.profile_id,
        b"service": shadow_fire.service_name,
        b"scope": shadow_fire.scope_digest,
        b"request": shadow_fire.request_digest,
        b"shadow": shadow_fire.report_digest,
        b"statements": list(digests),
        b"families": family_count,
        b"paths": path_family_count,
        b"watch": 1 if watch else 0,
    }))
    return WitnessAppealReport(kind, accepted, reason, shadow_fire.action, shadow_fire.profile_id, shadow_fire.service_name, shadow_fire.scope_digest, shadow_fire.request_digest, shadow_fire.report_digest, digests, family_count, path_family_count, watch, digest)


def assess_witness_appeal(*, shadow_fire: ShadowFireReport, statements: Iterable[WitnessAppealStatement], now: int, policy: WitnessAppealPolicy = WitnessAppealPolicy(), previously_seen_statement_digests: Iterable[bytes] = (), hard_negative_digests: Iterable[bytes] = ()) -> WitnessAppealReport:
    st = tuple(statements)
    if hard_negative_digests:
        return _report(WitnessAppealDecisionKind.QUARANTINE_HARD_NEGATIVE, False, "hard negative before appeal", shadow_fire=shadow_fire, statements=st)
    if not shadow_fire.watch:
        return _report(WitnessAppealDecisionKind.HOLD_NOT_WATCHED, False, "appeal only applies to watched shadow-fire reports", shadow_fire=shadow_fire, statements=st, watch=False)
    seen = set(previously_seen_statement_digests)
    valid: list[WitnessAppealStatement] = []
    by_signer_seq: dict[tuple[bytes, int], bytes] = {}
    for item in st:
        if item.statement_digest in seen:
            return _report(WitnessAppealDecisionKind.QUARANTINE_REPLAY, False, "appeal statement replay", shadow_fire=shadow_fire, statements=(item,))
        if not item.verify():
            return _report(WitnessAppealDecisionKind.QUARANTINE_BAD_SIGNATURE, False, "bad witness appeal signature", shadow_fire=shadow_fire, statements=(item,))
        if not (item.issued_at <= now < item.expires_at):
            return _report(WitnessAppealDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, False, "appeal statement expired or from future", shadow_fire=shadow_fire, statements=(item,))
        if item.action is not shadow_fire.action:
            return _report(WitnessAppealDecisionKind.QUARANTINE_ACTION_DRIFT, False, "appeal action drift", shadow_fire=shadow_fire, statements=(item,))
        if item.scope_digest != shadow_fire.scope_digest:
            return _report(WitnessAppealDecisionKind.QUARANTINE_SCOPE_DRIFT, False, "appeal scope drift", shadow_fire=shadow_fire, statements=(item,))
        if item.request_digest != shadow_fire.request_digest:
            return _report(WitnessAppealDecisionKind.QUARANTINE_REQUEST_DRIFT, False, "appeal request drift", shadow_fire=shadow_fire, statements=(item,))
        if item.shadow_report_digest != shadow_fire.report_digest or item.profile_id != shadow_fire.profile_id or item.service_name != shadow_fire.service_name:
            return _report(WitnessAppealDecisionKind.QUARANTINE_REPORT_DIGEST_DRIFT, False, "appeal report/profile/service drift", shadow_fire=shadow_fire, statements=(item,))
        key = (item.signer_public_key, item.sequence)
        if key in by_signer_seq and by_signer_seq[key] != item.statement_digest:
            return _report(WitnessAppealDecisionKind.QUARANTINE_SEQUENCE_FORK, False, "same signer emitted same-sequence appeal fork", shadow_fire=shadow_fire, statements=(item,))
        by_signer_seq[key] = item.statement_digest
        valid.append(item)
    if any(item.kind is WitnessAppealStatementKind.REFUTE_ACTION for item in valid):
        return _report(WitnessAppealDecisionKind.QUARANTINE_REFUTED, False, "witness appeal contains a refutation", shadow_fire=shadow_fire, statements=valid)
    support = [item for item in valid if item.kind is WitnessAppealStatementKind.SUPPORT_WATCHED_ACTION]
    hard_clear = [item for item in valid if item.kind is WitnessAppealStatementKind.HARD_NEGATIVE_CLEAR]
    watch_count = sum(1 for item in valid if item.kind is WitnessAppealStatementKind.REQUIRE_MORE_EVIDENCE)
    if watch_count > policy.max_watch_statements:
        return _report(WitnessAppealDecisionKind.HOLD_TOO_MANY_WATCH_STATEMENTS, False, "too many witnesses still require more evidence", shadow_fire=shadow_fire, statements=valid, watch=True)
    if policy.require_hard_negative_clear and not hard_clear:
        return _report(WitnessAppealDecisionKind.HOLD_MISSING_REQUIRED_KIND, False, "missing hard-negative-clear appeal statement", shadow_fire=shadow_fire, statements=valid, watch=True)
    support_families = {item.family_id for item in support}
    path_families = {item.path_family for item in support}
    if len(support_families) < policy.min_support_families:
        return _report(WitnessAppealDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, "appeal support lacks family diversity", shadow_fire=shadow_fire, statements=valid, family_count=len(support_families), path_family_count=len(path_families), watch=True)
    if len(path_families) < policy.min_path_families:
        return _report(WitnessAppealDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, "appeal support lacks path diversity", shadow_fire=shadow_fire, statements=valid, family_count=len(support_families), path_family_count=len(path_families), watch=True)
    return _report(WitnessAppealDecisionKind.ACCEPT_APPEAL_WITH_WATCH, True, "watched action has local witness appeal support", shadow_fire=shadow_fire, statements=valid, family_count=len(support_families), path_family_count=len(path_families), watch=True)
