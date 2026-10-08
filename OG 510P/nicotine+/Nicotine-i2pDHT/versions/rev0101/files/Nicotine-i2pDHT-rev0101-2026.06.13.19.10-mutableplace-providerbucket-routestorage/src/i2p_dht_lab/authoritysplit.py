"""Joined authority-split gate for key compartments.

A key compartment can pass while a profile cooldown, router harness, service
catalog, or crisis scan fails.  rev0043 adds a tiny generic join surface: signed
component reports have to agree on profile/scope/object/request and show enough
independent families before authority-sensitive side effects are allowed.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256

AUTHORITY_SPLIT_DOMAIN = DOMAIN + b":authority-split-v1:"
ZERO_DIGEST = b"\x00" * 32


class AuthorityComponent(str, Enum):
    KEY_COMPARTMENT = "key_compartment"
    OPERATOR_KEY = "operator_key"
    PROFILE_COOLDOWN = "profile_cooldown"
    ROUTER_HARNESS = "router_harness"
    SERVICE_CATALOG = "service_catalog"
    HARD_NEGATIVE_SCAN = "hard_negative_scan"


class ComponentStatus(str, Enum):
    PASS_ = "pass"
    WATCH = "watch"
    FAIL = "fail"
    QUARANTINE = "quarantine"


class AuthoritySplitDecisionKind(str, Enum):
    ACCEPT_AUTHORITY_SPLIT = "accept_authority_split"
    ACCEPT_WITH_WATCH = "accept_with_watch"
    HOLD_MISSING_COMPONENT = "hold_missing_component"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_COMPONENT_WATCH = "hold_component_watch"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_EXPIRED_OR_FUTURE = "quarantine_expired_or_future"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_PROFILE_DRIFT = "quarantine_profile_drift"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_OBJECT_DRIFT = "quarantine_object_drift"
    QUARANTINE_REQUEST_DRIFT = "quarantine_request_drift"
    QUARANTINE_COMPONENT_FAILED = "quarantine_component_failed"
    QUARANTINE_ACTOR_KEY_REUSE = "quarantine_actor_key_reuse"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"


@dataclass(frozen=True)
class AuthorityComponentReport:
    component: AuthorityComponent
    status: ComponentStatus
    profile_id: str
    scope_digest: bytes
    object_digest: bytes
    request_digest: bytes
    actor_public_key: bytes
    evidence_digest: bytes
    sequence: int
    issued_at: int
    expires_at: int
    signer_public_key: bytes
    family_id: str
    signature: bytes = b""

    def __post_init__(self) -> None:
        if not self.profile_id or len(self.profile_id.encode("utf-8")) > 80:
            raise ValueError("profile_id must be short and non-empty")
        for name, value in (("scope_digest", self.scope_digest), ("object_digest", self.object_digest), ("request_digest", self.request_digest), ("actor_public_key", self.actor_public_key), ("evidence_digest", self.evidence_digest), ("signer_public_key", self.signer_public_key)):
            expected = 32
            if len(value) != expected:
                raise ValueError(f"{name} must be {expected} bytes")
        if self.sequence < 0:
            raise ValueError("sequence must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("component report must expire after issue")
        if not self.family_id:
            raise ValueError("family_id must be non-empty")

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"component": self.component.value,
            b"status": self.status.value,
            b"profile": self.profile_id,
            b"scope": self.scope_digest,
            b"object": self.object_digest,
            b"request": self.request_digest,
            b"actor": self.actor_public_key,
            b"evidence": self.evidence_digest,
            b"seq": self.sequence,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"signer": self.signer_public_key,
            b"family": self.family_id,
        }

    def payload(self) -> bytes:
        return AUTHORITY_SPLIT_DOMAIN + b":component:" + bencode(self.unsigned_bvalue())

    @property
    def report_digest(self) -> bytes:
        return sha256(AUTHORITY_SPLIT_DOMAIN + b":component-digest:" + self.payload() + self.signature)

    def verify(self) -> bool:
        return verify_signature(self.signer_public_key, self.payload(), self.signature)

    def with_signature(self, signature: bytes) -> "AuthorityComponentReport":
        return replace(self, signature=signature)


@dataclass(frozen=True)
class AuthoritySplitAssessment:
    decision_kind: AuthoritySplitDecisionKind
    accepted_components: tuple[AuthorityComponent, ...] = ()
    watch_components: tuple[AuthorityComponent, ...] = ()
    family_count: int = 0
    reasons: tuple[str, ...] = ()
    report_digest: bytes = ZERO_DIGEST


def make_authority_component_report(
    *,
    keypair: DhtKeypair,
    component: AuthorityComponent,
    status: ComponentStatus,
    profile_id: str,
    scope_digest: bytes,
    object_digest: bytes,
    request_digest: bytes,
    actor_public_key: bytes,
    evidence_digest: bytes,
    sequence: int,
    issued_at: int,
    expires_at: int,
    family_id: str,
) -> AuthorityComponentReport:
    report = AuthorityComponentReport(component, status, profile_id, scope_digest, object_digest, request_digest, actor_public_key, evidence_digest, sequence, issued_at, expires_at, keypair.public_key_bytes, family_id)
    return report.with_signature(keypair.sign(report.payload()))


def _assessment(kind: AuthoritySplitDecisionKind, *, components: Iterable[AuthorityComponent] = (), watch: Iterable[AuthorityComponent] = (), family_count: int = 0, reasons: Iterable[str] = ()) -> AuthoritySplitAssessment:
    component_tuple = tuple(components)
    watch_tuple = tuple(watch)
    reasons_tuple = tuple(reasons)
    digest = sha256(AUTHORITY_SPLIT_DOMAIN + b":assessment:" + bencode({
        b"kind": kind.value,
        b"components": [component.value for component in component_tuple],
        b"watch": [component.value for component in watch_tuple],
        b"families": family_count,
        b"reasons": list(reasons_tuple),
    }))
    return AuthoritySplitAssessment(kind, component_tuple, watch_tuple, family_count, reasons_tuple, digest)


def assess_authority_split(
    reports: Iterable[AuthorityComponentReport],
    *,
    now: int,
    expected_profile_id: str,
    expected_scope_digest: bytes,
    expected_object_digest: bytes,
    expected_request_digest: bytes,
    required_components: Iterable[AuthorityComponent],
    min_family_diversity: int = 2,
    previously_seen_report_digests: Iterable[bytes] = (),
    allow_watch_components: bool = False,
) -> AuthoritySplitAssessment:
    required = tuple(required_components)
    seen = set(previously_seen_report_digests)
    latest_by_component: dict[AuthorityComponent, AuthorityComponentReport] = {}
    fork_guard: dict[tuple[AuthorityComponent, int], bytes] = {}
    families: set[str] = set()
    actor_keys: dict[bytes, set[AuthorityComponent]] = {}

    for report in reports:
        if report.report_digest in seen:
            return _assessment(AuthoritySplitDecisionKind.QUARANTINE_REPLAY, reasons=("report_replayed",))
        if not report.verify():
            return _assessment(AuthoritySplitDecisionKind.QUARANTINE_BAD_SIGNATURE, reasons=("bad_signature",))
        if report.issued_at > now or report.expires_at <= now:
            return _assessment(AuthoritySplitDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, reasons=("expired_or_future",))
        if report.profile_id != expected_profile_id:
            return _assessment(AuthoritySplitDecisionKind.QUARANTINE_PROFILE_DRIFT, reasons=("profile_drift",))
        if report.scope_digest != expected_scope_digest:
            return _assessment(AuthoritySplitDecisionKind.QUARANTINE_SCOPE_DRIFT, reasons=("scope_drift",))
        if report.object_digest != expected_object_digest:
            return _assessment(AuthoritySplitDecisionKind.QUARANTINE_OBJECT_DRIFT, reasons=("object_drift",))
        if report.request_digest != expected_request_digest:
            return _assessment(AuthoritySplitDecisionKind.QUARANTINE_REQUEST_DRIFT, reasons=("request_drift",))
        prior = fork_guard.get((report.component, report.sequence))
        if prior is not None and prior != report.report_digest:
            return _assessment(AuthoritySplitDecisionKind.QUARANTINE_SEQUENCE_FORK, reasons=("same_component_sequence_fork",))
        fork_guard[(report.component, report.sequence)] = report.report_digest
        families.add(report.family_id)
        actor_keys.setdefault(report.actor_public_key, set()).add(report.component)
        current = latest_by_component.get(report.component)
        if current is None or report.sequence > current.sequence:
            latest_by_component[report.component] = report

    missing = [component for component in required if component not in latest_by_component]
    if missing:
        return _assessment(AuthoritySplitDecisionKind.HOLD_MISSING_COMPONENT, family_count=len(families), reasons=("missing:" + ",".join(component.value for component in missing),))
    selected = tuple(latest_by_component[component] for component in required)
    failed = [item.component for item in selected if item.status in (ComponentStatus.FAIL, ComponentStatus.QUARANTINE)]
    if failed:
        return _assessment(AuthoritySplitDecisionKind.QUARANTINE_COMPONENT_FAILED, components=failed, family_count=len(families), reasons=("component_failed",))
    watch = [item.component for item in selected if item.status is ComponentStatus.WATCH]
    if watch and not allow_watch_components:
        return _assessment(AuthoritySplitDecisionKind.HOLD_COMPONENT_WATCH, components=[item.component for item in selected], watch=watch, family_count=len(families), reasons=("watch_component_present",))
    for actor, components in actor_keys.items():
        interesting = components.intersection(required)
        if len(interesting) > 1:
            return _assessment(AuthoritySplitDecisionKind.QUARANTINE_ACTOR_KEY_REUSE, components=interesting, family_count=len(families), reasons=("actor_key_reused_across_components",))
    selected_families = {item.family_id for item in selected}
    if len(selected_families) < min_family_diversity:
        return _assessment(AuthoritySplitDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, components=[item.component for item in selected], watch=watch, family_count=len(selected_families), reasons=("low_family_diversity",))
    kind = AuthoritySplitDecisionKind.ACCEPT_WITH_WATCH if watch else AuthoritySplitDecisionKind.ACCEPT_AUTHORITY_SPLIT
    return _assessment(kind, components=[item.component for item in selected], watch=watch, family_count=len(selected_families), reasons=("accepted",))
