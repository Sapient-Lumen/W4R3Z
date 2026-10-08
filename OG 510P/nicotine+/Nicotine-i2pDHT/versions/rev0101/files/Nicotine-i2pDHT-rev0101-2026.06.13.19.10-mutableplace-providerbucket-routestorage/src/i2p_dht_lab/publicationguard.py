"""Final no-network publication guard after bridge-ledger acceptance.

rev0046 proved that a public bridge side effect can be locally ledgered against
shadow-fire, egress, moderation, and redress.  rev0047 adds the next boundary:
publication itself.  A bridge ledger report is still not permission to refresh a
mutable public seed head, bridge catalog, or public contact hint.  Publication
needs its own short-lived, redaction-aware, monotonic, family-diverse capsule.

This module is intentionally transport-neutral and no-network.  It models the
side-effect gate that should exist before future SAM/I2P or mutable-DHT writes.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .bridgeledger import BridgeLedgerAction, BridgeLedgerReport
from .egressmeter import EgressWindowReport
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .moderationquarantine import ModerationAction, ZERO_DIGEST
from .policyportfolio import PolicyPortfolioReport

PUBLICATION_GUARD_DOMAIN = DOMAIN + b":publication-guard-v1:"


class PublicationIntent(str, Enum):
    PUBLIC_REFRESH = "public_refresh"
    PUBLIC_WITHDRAW = "public_withdraw"
    PUBLIC_REPAIR = "public_repair"


class ExposureClass(str, Enum):
    DIGEST_ONLY = "digest_only"
    PUBLIC_B32_HINT = "public_b32_hint"
    WITHDRAWAL_ONLY = "withdrawal_only"
    RAW_DESTINATION = "raw_destination"


class PublicationDecisionKind(str, Enum):
    ACCEPT_PUBLICATION = "accept_publication"
    ACCEPT_WITH_WATCH = "accept_with_watch"
    HOLD_LEDGER_NOT_ACCEPTED = "hold_ledger_not_accepted"
    HOLD_LEDGER_WATCH = "hold_ledger_watch"
    HOLD_POLICY_NOT_ACCEPTED = "hold_policy_not_accepted"
    HOLD_POLICY_WATCH = "hold_policy_watch"
    HOLD_EGRESS_NOT_ACCEPTED = "hold_egress_not_accepted"
    HOLD_EGRESS_WATCH = "hold_egress_watch"
    HOLD_PUBLIC_CONTACT_NOT_ALLOWED = "hold_public_contact_not_allowed"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_EXPIRED_OR_FUTURE = "quarantine_expired_or_future"
    QUARANTINE_TTL_EXCESS = "quarantine_ttl_excess"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_PROFILE_DRIFT = "quarantine_profile_drift"
    QUARANTINE_SERVICE_DRIFT = "quarantine_service_drift"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_REQUEST_DRIFT = "quarantine_request_drift"
    QUARANTINE_SUBJECT_DRIFT = "quarantine_subject_drift"
    QUARANTINE_INTENT_DRIFT = "quarantine_intent_drift"
    QUARANTINE_LEDGER_DIGEST_DRIFT = "quarantine_ledger_digest_drift"
    QUARANTINE_POLICY_DIGEST_DRIFT = "quarantine_policy_digest_drift"
    QUARANTINE_EGRESS_DIGEST_DRIFT = "quarantine_egress_digest_drift"
    QUARANTINE_RAW_DESTINATION_EXPOSURE = "quarantine_raw_destination_exposure"
    QUARANTINE_STALE_PUBLIC_REPLAY = "quarantine_stale_public_replay"
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"


LEDGER_TO_PUBLICATION_INTENT = {
    BridgeLedgerAction.PUBLIC_REFRESH: PublicationIntent.PUBLIC_REFRESH,
    BridgeLedgerAction.PUBLIC_WITHDRAW: PublicationIntent.PUBLIC_WITHDRAW,
    BridgeLedgerAction.PUBLIC_REPAIR: PublicationIntent.PUBLIC_REPAIR,
}


@dataclass(frozen=True)
class PublicationCapsule:
    intent: PublicationIntent
    exposure_class: ExposureClass
    profile_id: str
    service_name: str
    subject_key_digest: bytes
    scope_digest: bytes
    request_digest: bytes
    bridge_ledger_digest: bytes
    policy_portfolio_digest: bytes
    egress_digest: bytes
    public_payload_digest: bytes
    sequence: int
    previous_publication_digest: bytes
    issued_at: int
    expires_at: int
    ttl_seconds: int
    family_id: str
    path_family: str
    signer_public_key: bytes
    signature: bytes = b""

    def __post_init__(self) -> None:
        if not self.profile_id or len(self.profile_id.encode("utf-8")) > 80:
            raise ValueError("profile_id must be short and non-empty")
        if not self.service_name or len(self.service_name.encode("utf-8")) > 96:
            raise ValueError("service_name must be short and non-empty")
        if self.sequence < 0:
            raise ValueError("publication sequence must be non-negative")
        if self.expires_at <= self.issued_at or self.ttl_seconds <= 0:
            raise ValueError("publication validity window invalid")
        if not self.family_id or not self.path_family:
            raise ValueError("family_id and path_family must be non-empty")
        for name, value in (
            ("subject_key_digest", self.subject_key_digest),
            ("scope_digest", self.scope_digest),
            ("request_digest", self.request_digest),
            ("bridge_ledger_digest", self.bridge_ledger_digest),
            ("policy_portfolio_digest", self.policy_portfolio_digest),
            ("egress_digest", self.egress_digest),
            ("public_payload_digest", self.public_payload_digest),
            ("previous_publication_digest", self.previous_publication_digest),
            ("signer_public_key", self.signer_public_key),
        ):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if self.signature and len(self.signature) != 64:
            raise ValueError("signature must be Ed25519-sized")
        object.__setattr__(self, "intent", PublicationIntent(self.intent))
        object.__setattr__(self, "exposure_class", ExposureClass(self.exposure_class))

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"intent": self.intent.value,
            b"exposure": self.exposure_class.value,
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"subject": self.subject_key_digest,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"ledger": self.bridge_ledger_digest,
            b"policy": self.policy_portfolio_digest,
            b"egress": self.egress_digest,
            b"payload": self.public_payload_digest,
            b"seq": self.sequence,
            b"prev": self.previous_publication_digest,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"ttl": self.ttl_seconds,
            b"family": self.family_id,
            b"path_family": self.path_family,
            b"signer": self.signer_public_key,
        }

    def signature_payload(self) -> bytes:
        return PUBLICATION_GUARD_DOMAIN + b":capsule-sig:" + bencode(self.unsigned_bvalue())

    @property
    def capsule_core_digest(self) -> bytes:
        return sha256(PUBLICATION_GUARD_DOMAIN + b":capsule-core:" + bencode({
            b"intent": self.intent.value,
            b"exposure": self.exposure_class.value,
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"subject": self.subject_key_digest,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"ledger": self.bridge_ledger_digest,
            b"policy": self.policy_portfolio_digest,
            b"egress": self.egress_digest,
            b"payload": self.public_payload_digest,
            b"seq": self.sequence,
            b"prev": self.previous_publication_digest,
            b"ttl": self.ttl_seconds,
        }))

    @property
    def capsule_digest(self) -> bytes:
        return sha256(PUBLICATION_GUARD_DOMAIN + b":capsule-digest:" + self.signature_payload() + self.signature)

    def verifies(self) -> bool:
        return verify_signature(self.signer_public_key, self.signature_payload(), self.signature)


@dataclass(frozen=True)
class PublicationReport:
    decision_kind: PublicationDecisionKind
    accept: bool
    watch: bool
    reason: str
    profile_id: str
    service_name: str
    intent: PublicationIntent
    exposure_class: ExposureClass | None
    accepted_capsule_digest: bytes
    component_digests: tuple[bytes, ...]
    family_count: int
    path_family_count: int
    highest_sequence: int
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")

    @property
    def allow(self) -> bool:
        """Compatibility alias: publication acceptance is local allow."""
        return self.accept


def make_publication_capsule(
    *,
    keypair: DhtKeypair,
    intent: PublicationIntent,
    exposure_class: ExposureClass,
    profile_id: str,
    service_name: str,
    subject_key_digest: bytes,
    scope_digest: bytes,
    request_digest: bytes,
    bridge_ledger_digest: bytes,
    policy_portfolio_digest: bytes,
    egress_digest: bytes,
    public_payload_digest: bytes,
    sequence: int,
    previous_publication_digest: bytes = ZERO_DIGEST,
    issued_at: int,
    expires_at: int,
    ttl_seconds: int,
    family_id: str,
    path_family: str,
) -> PublicationCapsule:
    capsule = PublicationCapsule(intent, exposure_class, profile_id, service_name, subject_key_digest, scope_digest, request_digest, bridge_ledger_digest, policy_portfolio_digest, egress_digest, public_payload_digest, sequence, previous_publication_digest, issued_at, expires_at, ttl_seconds, family_id, path_family, keypair.public_key_bytes)
    return replace(capsule, signature=keypair.sign(capsule.signature_payload()))


def _report(kind: PublicationDecisionKind, accept: bool, watch: bool, reason: str, *, profile_id: str, service_name: str, intent: PublicationIntent, exposure_class: ExposureClass | None = None, capsules: Iterable[PublicationCapsule] = (), selected: PublicationCapsule | None = None, components: Iterable[bytes] = ()) -> PublicationReport:
    capsule_tuple = tuple(sorted(capsules, key=lambda item: (item.sequence, item.capsule_digest)))
    component_tuple = tuple(sorted(set(components)))
    accepted = selected.capsule_digest if selected and accept else ZERO_DIGEST
    family_count = len({item.family_id for item in capsule_tuple})
    path_count = len({item.path_family for item in capsule_tuple})
    highest = selected.sequence if selected else max((item.sequence for item in capsule_tuple), default=-1)
    digest = sha256(PUBLICATION_GUARD_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"reason": reason,
        b"profile": profile_id,
        b"service": service_name,
        b"intent": intent.value,
        b"exposure": exposure_class.value if exposure_class is not None else b"none",
        b"accepted": accepted,
        b"capsules": [item.capsule_digest for item in capsule_tuple],
        b"components": list(component_tuple),
        b"families": family_count,
        b"paths": path_count,
        b"highest": highest,
    }))
    return PublicationReport(kind, accept, watch, reason, profile_id, service_name, intent, exposure_class, accepted, component_tuple, family_count, path_count, highest, digest)


def assess_publication(
    capsules: Iterable[PublicationCapsule],
    *,
    bridge_ledger: BridgeLedgerReport,
    policy_portfolio: PolicyPortfolioReport,
    egress: EgressWindowReport,
    now: int,
    expected_profile_id: str,
    expected_service_name: str,
    expected_action: BridgeLedgerAction,
    expected_subject_key_digest: bytes,
    expected_scope_digest: bytes,
    expected_request_digest: bytes,
    previous_sequence: int | None = None,
    previous_publication_digest: bytes | None = None,
    previously_seen_capsules: Iterable[bytes] = (),
    stale_public_payload_digests: Iterable[bytes] = (),
    live_hard_negative_digests: Iterable[bytes] = (),
    allow_watch: bool = False,
    allow_public_contact: bool = False,
    max_ttl_seconds: int = 3600,
    min_family_diversity: int = 2,
    min_path_diversity: int = 2,
) -> PublicationReport:
    expected_action = BridgeLedgerAction(expected_action)
    expected_intent = LEDGER_TO_PUBLICATION_INTENT[expected_action]
    components = [bridge_ledger.report_digest, policy_portfolio.report_digest, egress.report_digest]
    capsule_tuple = tuple(capsules)
    if not bridge_ledger.accept:
        return _report(PublicationDecisionKind.HOLD_LEDGER_NOT_ACCEPTED, False, True, "bridge ledger did not accept side effect", profile_id=expected_profile_id, service_name=expected_service_name, intent=expected_intent, capsules=capsule_tuple, components=components)
    if bridge_ledger.watch and not allow_watch:
        return _report(PublicationDecisionKind.HOLD_LEDGER_WATCH, False, True, "bridge ledger accepted only with watch pressure", profile_id=expected_profile_id, service_name=expected_service_name, intent=expected_intent, capsules=capsule_tuple, components=components)
    if not policy_portfolio.allow:
        return _report(PublicationDecisionKind.HOLD_POLICY_NOT_ACCEPTED, False, True, "policy portfolio did not accept publication", profile_id=expected_profile_id, service_name=expected_service_name, intent=expected_intent, capsules=capsule_tuple, components=components)
    if policy_portfolio.watch and not allow_watch:
        return _report(PublicationDecisionKind.HOLD_POLICY_WATCH, False, True, "policy portfolio accepted only with watch pressure", profile_id=expected_profile_id, service_name=expected_service_name, intent=expected_intent, capsules=capsule_tuple, components=components)
    if not egress.accept:
        return _report(PublicationDecisionKind.HOLD_EGRESS_NOT_ACCEPTED, False, True, "egress window did not accept side effect", profile_id=expected_profile_id, service_name=expected_service_name, intent=expected_intent, capsules=capsule_tuple, components=components)
    if egress.decision_kind.value == "accept_with_watch" and not allow_watch:
        return _report(PublicationDecisionKind.HOLD_EGRESS_WATCH, False, True, "egress accepted only with watch pressure", profile_id=expected_profile_id, service_name=expected_service_name, intent=expected_intent, capsules=capsule_tuple, components=components)
    if not capsule_tuple:
        return _report(PublicationDecisionKind.HOLD_LEDGER_NOT_ACCEPTED, False, True, "publication capsule missing", profile_id=expected_profile_id, service_name=expected_service_name, intent=expected_intent, capsules=(), components=components)
    if live_hard_negative_digests:
        return _report(PublicationDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, "live hard-negative pressure blocks publication", profile_id=expected_profile_id, service_name=expected_service_name, intent=expected_intent, capsules=capsule_tuple, components=components)
    seen = set(previously_seen_capsules)
    stale_payloads = set(stale_public_payload_digests)
    core_by_sequence: dict[int, bytes] = {}
    candidates: list[PublicationCapsule] = []
    for capsule in capsule_tuple:
        if not capsule.verifies():
            return _report(PublicationDecisionKind.QUARANTINE_BAD_SIGNATURE, False, False, "publication capsule signature failed", profile_id=expected_profile_id, service_name=expected_service_name, intent=expected_intent, capsules=capsule_tuple, components=components)
        if not (capsule.issued_at <= now < capsule.expires_at):
            return _report(PublicationDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, False, False, "publication capsule expired or future", profile_id=expected_profile_id, service_name=expected_service_name, intent=expected_intent, capsules=capsule_tuple, components=components)
        if capsule.ttl_seconds > max_ttl_seconds:
            return _report(PublicationDecisionKind.QUARANTINE_TTL_EXCESS, False, False, "publication TTL exceeds local maximum", profile_id=expected_profile_id, service_name=expected_service_name, intent=expected_intent, exposure_class=capsule.exposure_class, capsules=capsule_tuple, components=components)
        if capsule.capsule_digest in seen:
            return _report(PublicationDecisionKind.QUARANTINE_REPLAY, False, False, "publication capsule replayed", profile_id=expected_profile_id, service_name=expected_service_name, intent=expected_intent, exposure_class=capsule.exposure_class, capsules=capsule_tuple, components=components)
        if capsule.profile_id != expected_profile_id:
            return _report(PublicationDecisionKind.QUARANTINE_PROFILE_DRIFT, False, False, "publication profile drift", profile_id=expected_profile_id, service_name=expected_service_name, intent=expected_intent, exposure_class=capsule.exposure_class, capsules=capsule_tuple, components=components)
        if capsule.service_name != expected_service_name:
            return _report(PublicationDecisionKind.QUARANTINE_SERVICE_DRIFT, False, False, "publication service drift", profile_id=expected_profile_id, service_name=expected_service_name, intent=expected_intent, exposure_class=capsule.exposure_class, capsules=capsule_tuple, components=components)
        if capsule.subject_key_digest != expected_subject_key_digest:
            return _report(PublicationDecisionKind.QUARANTINE_SUBJECT_DRIFT, False, False, "publication subject drift", profile_id=expected_profile_id, service_name=expected_service_name, intent=expected_intent, exposure_class=capsule.exposure_class, capsules=capsule_tuple, components=components)
        if capsule.scope_digest != expected_scope_digest:
            return _report(PublicationDecisionKind.QUARANTINE_SCOPE_DRIFT, False, False, "publication scope drift", profile_id=expected_profile_id, service_name=expected_service_name, intent=expected_intent, exposure_class=capsule.exposure_class, capsules=capsule_tuple, components=components)
        if capsule.request_digest != expected_request_digest:
            return _report(PublicationDecisionKind.QUARANTINE_REQUEST_DRIFT, False, False, "publication request drift", profile_id=expected_profile_id, service_name=expected_service_name, intent=expected_intent, exposure_class=capsule.exposure_class, capsules=capsule_tuple, components=components)
        if capsule.intent is not expected_intent:
            return _report(PublicationDecisionKind.QUARANTINE_INTENT_DRIFT, False, False, "publication intent drift", profile_id=expected_profile_id, service_name=expected_service_name, intent=expected_intent, exposure_class=capsule.exposure_class, capsules=capsule_tuple, components=components)
        if capsule.bridge_ledger_digest != bridge_ledger.report_digest:
            return _report(PublicationDecisionKind.QUARANTINE_LEDGER_DIGEST_DRIFT, False, False, "publication bridge-ledger digest drift", profile_id=expected_profile_id, service_name=expected_service_name, intent=expected_intent, exposure_class=capsule.exposure_class, capsules=capsule_tuple, components=components)
        if capsule.policy_portfolio_digest != policy_portfolio.report_digest:
            return _report(PublicationDecisionKind.QUARANTINE_POLICY_DIGEST_DRIFT, False, False, "publication policy-portfolio digest drift", profile_id=expected_profile_id, service_name=expected_service_name, intent=expected_intent, exposure_class=capsule.exposure_class, capsules=capsule_tuple, components=components)
        if capsule.egress_digest != egress.report_digest:
            return _report(PublicationDecisionKind.QUARANTINE_EGRESS_DIGEST_DRIFT, False, False, "publication egress digest drift", profile_id=expected_profile_id, service_name=expected_service_name, intent=expected_intent, exposure_class=capsule.exposure_class, capsules=capsule_tuple, components=components)
        if capsule.exposure_class is ExposureClass.RAW_DESTINATION:
            return _report(PublicationDecisionKind.QUARANTINE_RAW_DESTINATION_EXPOSURE, False, False, "raw destination exposure is not a publication capsule", profile_id=expected_profile_id, service_name=expected_service_name, intent=expected_intent, exposure_class=capsule.exposure_class, capsules=capsule_tuple, components=components)
        if capsule.exposure_class is ExposureClass.PUBLIC_B32_HINT and not allow_public_contact:
            return _report(PublicationDecisionKind.HOLD_PUBLIC_CONTACT_NOT_ALLOWED, False, True, "public contact hint needs explicit allowance", profile_id=expected_profile_id, service_name=expected_service_name, intent=expected_intent, exposure_class=capsule.exposure_class, capsules=capsule_tuple, components=components)
        if expected_intent is PublicationIntent.PUBLIC_WITHDRAW and capsule.exposure_class is not ExposureClass.WITHDRAWAL_ONLY:
            return _report(PublicationDecisionKind.QUARANTINE_INTENT_DRIFT, False, False, "withdraw publication must be withdrawal-only", profile_id=expected_profile_id, service_name=expected_service_name, intent=expected_intent, exposure_class=capsule.exposure_class, capsules=capsule_tuple, components=components)
        if capsule.public_payload_digest in stale_payloads:
            return _report(PublicationDecisionKind.QUARANTINE_STALE_PUBLIC_REPLAY, False, False, "publication would replay stale public payload", profile_id=expected_profile_id, service_name=expected_service_name, intent=expected_intent, exposure_class=capsule.exposure_class, capsules=capsule_tuple, components=components)
        if previous_sequence is not None and capsule.sequence <= previous_sequence:
            return _report(PublicationDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, False, "publication sequence rollback", profile_id=expected_profile_id, service_name=expected_service_name, intent=expected_intent, exposure_class=capsule.exposure_class, capsules=capsule_tuple, components=components)
        if previous_publication_digest is not None and capsule.previous_publication_digest != previous_publication_digest:
            return _report(PublicationDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, False, "publication previous digest mismatch", profile_id=expected_profile_id, service_name=expected_service_name, intent=expected_intent, exposure_class=capsule.exposure_class, capsules=capsule_tuple, components=components)
        other = core_by_sequence.get(capsule.sequence)
        if other is not None and other != capsule.capsule_core_digest:
            return _report(PublicationDecisionKind.QUARANTINE_SEQUENCE_FORK, False, False, "publication sequence fork", profile_id=expected_profile_id, service_name=expected_service_name, intent=expected_intent, exposure_class=capsule.exposure_class, capsules=capsule_tuple, components=components)
        core_by_sequence[capsule.sequence] = capsule.capsule_core_digest
        candidates.append(capsule)
    if len({item.family_id for item in candidates}) < min_family_diversity:
        return _report(PublicationDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, "publication lacks family diversity", profile_id=expected_profile_id, service_name=expected_service_name, intent=expected_intent, capsules=capsule_tuple, components=components)
    if len({item.path_family for item in candidates}) < min_path_diversity:
        return _report(PublicationDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, "publication lacks path-family diversity", profile_id=expected_profile_id, service_name=expected_service_name, intent=expected_intent, capsules=capsule_tuple, components=components)
    selected = max(candidates, key=lambda item: (item.sequence, item.capsule_digest))
    watch = bool(bridge_ledger.watch or policy_portfolio.watch or egress.decision_kind.value == "accept_with_watch")
    if watch:
        return _report(PublicationDecisionKind.ACCEPT_WITH_WATCH, True, True, "publication accepted with inherited watch pressure", profile_id=expected_profile_id, service_name=expected_service_name, intent=expected_intent, exposure_class=selected.exposure_class, capsules=capsule_tuple, selected=selected, components=components)
    return _report(PublicationDecisionKind.ACCEPT_PUBLICATION, True, False, "publication capsule is fresh, scoped, diverse, and redaction-safe", profile_id=expected_profile_id, service_name=expected_service_name, intent=expected_intent, exposure_class=selected.exposure_class, capsules=capsule_tuple, selected=selected, components=components)
