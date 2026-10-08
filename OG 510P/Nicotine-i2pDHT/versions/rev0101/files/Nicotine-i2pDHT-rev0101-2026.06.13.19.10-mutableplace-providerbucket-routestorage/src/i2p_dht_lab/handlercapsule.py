"""Handler capsules after the no-network live adapter.

rev0053 treats handler execution as its own boundary.  A live adapter report
that says "inbound handler work is rehearsed" is still not permission to run a
handler.  The handler capsule binds the exact handler, caller, payload, profile
edge, live adapter, ingress drain, backpressure, metadata budget, and hard
negative scan at the same profile/service/scope/request boundary.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Any, Iterable

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .liveadapter import LiveAdapterMode
from .moderationquarantine import ZERO_DIGEST

HANDLER_CAPSULE_DOMAIN = DOMAIN + b":handler-capsule-v1:"


class HandlerWorkKind(str, Enum):
    PUBLIC_BRIDGE_REQUEST = "public_bridge_request"
    PROVIDER_PROBE = "provider_probe"
    MUTABLE_HEAD_QUERY = "mutable_head_query"
    SERVICE_DIAGNOSTIC = "service_diagnostic"


class HandlerCapsuleDecisionKind(str, Enum):
    ACCEPT_HANDLER_CAPSULE = "accept_handler_capsule"
    ACCEPT_WITH_WATCH = "accept_with_watch"
    HOLD_PROFILE_EDGE = "hold_profile_edge"
    HOLD_LIVE_ADAPTER = "hold_live_adapter"
    HOLD_INGRESS_DRAIN = "hold_ingress_drain"
    HOLD_BACKPRESSURE = "hold_backpressure"
    HOLD_COMPONENT_WATCH = "hold_component_watch"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    EMPTY_NO_CAPSULES = "empty_no_capsules"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_EXPIRED_OR_FUTURE = "quarantine_expired_or_future"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_PROFILE_DRIFT = "quarantine_profile_drift"
    QUARANTINE_SERVICE_DRIFT = "quarantine_service_drift"
    QUARANTINE_MODE_DRIFT = "quarantine_mode_drift"
    QUARANTINE_KIND_DRIFT = "quarantine_kind_drift"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_REQUEST_DRIFT = "quarantine_request_drift"
    QUARANTINE_PAYLOAD_DRIFT = "quarantine_payload_drift"
    QUARANTINE_CALLER_DRIFT = "quarantine_caller_drift"
    QUARANTINE_HANDLER_DRIFT = "quarantine_handler_drift"
    QUARANTINE_COMPONENT_DIGEST_DRIFT = "quarantine_component_digest_drift"
    QUARANTINE_METADATA_BUDGET = "quarantine_metadata_budget"
    QUARANTINE_HANDLER_BUDGET = "quarantine_handler_budget"
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"
    QUARANTINE_MODE_COMPONENT_MISMATCH = "quarantine_mode_component_mismatch"


@dataclass(frozen=True)
class HandlerCapsule:
    mode: LiveAdapterMode
    kind: HandlerWorkKind
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    inbound_payload_digest: bytes
    caller_digest: bytes
    handler_digest: bytes
    profile_edge_digest: bytes
    live_adapter_digest: bytes
    ingress_drain_digest: bytes
    backpressure_digest: bytes
    metadata_units: int
    handler_budget_units: int
    raw_key_units: int
    hard_negative_count: int
    sequence: int
    previous_capsule_digest: bytes
    issued_at: int
    expires_at: int
    family_id: str
    path_family: str
    signer_public_key: bytes
    signature: bytes = b""

    def __post_init__(self) -> None:
        object.__setattr__(self, "mode", LiveAdapterMode(self.mode))
        object.__setattr__(self, "kind", HandlerWorkKind(self.kind))
        if not self.profile_id or not self.service_name or not self.family_id or not self.path_family:
            raise ValueError("handler capsule needs profile/service/family/path")
        for name in ("metadata_units", "handler_budget_units", "raw_key_units", "hard_negative_count", "sequence"):
            if getattr(self, name) < 0:
                raise ValueError(f"{name} must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("expires_at must follow issued_at")
        for name, value in (
            ("scope_digest", self.scope_digest),
            ("request_digest", self.request_digest),
            ("inbound_payload_digest", self.inbound_payload_digest),
            ("caller_digest", self.caller_digest),
            ("handler_digest", self.handler_digest),
            ("profile_edge_digest", self.profile_edge_digest),
            ("live_adapter_digest", self.live_adapter_digest),
            ("ingress_drain_digest", self.ingress_drain_digest),
            ("backpressure_digest", self.backpressure_digest),
            ("previous_capsule_digest", self.previous_capsule_digest),
            ("signer_public_key", self.signer_public_key),
        ):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if self.signature and len(self.signature) != 64:
            raise ValueError("signature must be empty or Ed25519-sized")

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"mode": self.mode.value,
            b"kind": self.kind.value,
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"payload": self.inbound_payload_digest,
            b"caller": self.caller_digest,
            b"handler": self.handler_digest,
            b"profile_edge": self.profile_edge_digest,
            b"live_adapter": self.live_adapter_digest,
            b"ingress": self.ingress_drain_digest,
            b"backpressure": self.backpressure_digest,
            b"metadata_units": self.metadata_units,
            b"handler_budget": self.handler_budget_units,
            b"raw_key_units": self.raw_key_units,
            b"hard_negatives": self.hard_negative_count,
            b"seq": self.sequence,
            b"prev": self.previous_capsule_digest,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"family": self.family_id,
            b"path_family": self.path_family,
            b"signer": self.signer_public_key,
        }

    def signature_payload(self) -> bytes:
        return HANDLER_CAPSULE_DOMAIN + b":capsule-sig:" + bencode(self.unsigned_bvalue())

    @property
    def capsule_core_digest(self) -> bytes:
        return sha256(HANDLER_CAPSULE_DOMAIN + b":capsule-core:" + bencode(self.unsigned_bvalue()))

    @property
    def capsule_digest(self) -> bytes:
        return sha256(HANDLER_CAPSULE_DOMAIN + b":capsule-digest:" + self.signature_payload() + self.signature)

    def verifies(self) -> bool:
        return verify_signature(self.signer_public_key, self.signature_payload(), self.signature)

    def live(self, now: int) -> bool:
        return self.issued_at <= now < self.expires_at


@dataclass(frozen=True)
class HandlerCapsuleReport:
    decision_kind: HandlerCapsuleDecisionKind
    accept: bool
    watch: bool
    reason: str
    mode: LiveAdapterMode
    kind: HandlerWorkKind
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    inbound_payload_digest: bytes
    caller_digest: bytes
    handler_digest: bytes
    accepted_capsule_digest: bytes
    capsule_digests: tuple[bytes, ...]
    component_digests: tuple[bytes, ...]
    total_metadata_units: int
    total_handler_budget_units: int
    raw_key_units: int
    hard_negative_count: int
    family_count: int
    path_family_count: int
    highest_sequence: int
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _component_digest(report: Any | None) -> bytes:
    if report is None:
        return ZERO_DIGEST
    for attr in ("report_digest", "transcript_digest", "canary_digest"):
        value = getattr(report, attr, None)
        if isinstance(value, bytes) and len(value) == 32:
            return value
    raise ValueError("component report lacks 32-byte digest")


def _component_accept(report: Any | None) -> bool:
    if report is None:
        return False
    return bool(getattr(report, "accept", False))


def _component_watch(report: Any | None) -> bool:
    if report is None:
        return False
    return bool(getattr(report, "watch", False))


def _component_quarantined(report: Any | None) -> bool:
    if report is None:
        return False
    return bool(getattr(report, "quarantined", False))


def make_handler_capsule(
    *,
    keypair: DhtKeypair,
    mode: LiveAdapterMode,
    kind: HandlerWorkKind,
    profile_id: str,
    service_name: str,
    scope_digest: bytes,
    request_digest: bytes,
    inbound_payload_digest: bytes,
    caller_digest: bytes,
    handler_digest: bytes,
    profile_edge_report: Any,
    live_adapter_report: Any,
    ingress_drain_report: Any | None,
    backpressure_report: Any,
    metadata_units: int,
    handler_budget_units: int,
    raw_key_units: int,
    hard_negative_count: int,
    sequence: int,
    previous_capsule_digest: bytes = ZERO_DIGEST,
    issued_at: int,
    expires_at: int,
    family_id: str,
    path_family: str,
) -> HandlerCapsule:
    unsigned = HandlerCapsule(
        mode=mode,
        kind=kind,
        profile_id=profile_id,
        service_name=service_name,
        scope_digest=scope_digest,
        request_digest=request_digest,
        inbound_payload_digest=inbound_payload_digest,
        caller_digest=caller_digest,
        handler_digest=handler_digest,
        profile_edge_digest=_component_digest(profile_edge_report),
        live_adapter_digest=_component_digest(live_adapter_report),
        ingress_drain_digest=_component_digest(ingress_drain_report),
        backpressure_digest=_component_digest(backpressure_report),
        metadata_units=metadata_units,
        handler_budget_units=handler_budget_units,
        raw_key_units=raw_key_units,
        hard_negative_count=hard_negative_count,
        sequence=sequence,
        previous_capsule_digest=previous_capsule_digest,
        issued_at=issued_at,
        expires_at=expires_at,
        family_id=family_id,
        path_family=path_family,
        signer_public_key=keypair.public_key_bytes,
    )
    return replace(unsigned, signature=keypair.sign(unsigned.signature_payload()))


def _report(
    kind: HandlerCapsuleDecisionKind,
    accept: bool,
    watch: bool,
    reason: str,
    *,
    mode: LiveAdapterMode,
    handler_kind: HandlerWorkKind,
    profile_id: str,
    service_name: str,
    scope_digest: bytes,
    request_digest: bytes,
    inbound_payload_digest: bytes,
    caller_digest: bytes,
    handler_digest: bytes,
    accepted: HandlerCapsule | None = None,
    capsules: Iterable[HandlerCapsule] = (),
    components: Iterable[bytes] = (),
) -> HandlerCapsuleReport:
    capsule_t = tuple(capsules)
    capsule_digests = tuple(c.capsule_digest for c in capsule_t)
    families = {c.family_id for c in capsule_t}
    paths = {c.path_family for c in capsule_t}
    metadata_total = sum(c.metadata_units for c in capsule_t)
    handler_total = sum(c.handler_budget_units for c in capsule_t)
    raw_total = sum(c.raw_key_units for c in capsule_t)
    hard_total = sum(c.hard_negative_count for c in capsule_t)
    highest = max((c.sequence for c in capsule_t), default=-1)
    accepted_digest = accepted.capsule_digest if accepted else ZERO_DIGEST
    component_t = tuple(components)
    digest = sha256(HANDLER_CAPSULE_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"reason": reason,
        b"mode": mode.value,
        b"handler_kind": handler_kind.value,
        b"profile": profile_id,
        b"service": service_name,
        b"scope": scope_digest,
        b"request": request_digest,
        b"payload": inbound_payload_digest,
        b"caller": caller_digest,
        b"handler": handler_digest,
        b"accepted": accepted_digest,
        b"capsules": list(capsule_digests),
        b"components": list(component_t),
        b"metadata_total": metadata_total,
        b"handler_total": handler_total,
        b"raw_total": raw_total,
        b"hard_total": hard_total,
        b"families": len(families),
        b"paths": len(paths),
        b"highest": highest,
    }))
    return HandlerCapsuleReport(kind, accept, watch, reason, mode, handler_kind, profile_id, service_name, scope_digest, request_digest, inbound_payload_digest, caller_digest, handler_digest, accepted_digest, capsule_digests, component_t, metadata_total, handler_total, raw_total, hard_total, len(families), len(paths), highest, digest)


def assess_handler_capsules(
    capsules: Iterable[HandlerCapsule],
    *,
    profile_edge_report: Any,
    live_adapter_report: Any,
    ingress_drain_report: Any | None,
    backpressure_report: Any,
    now: int,
    expected_mode: LiveAdapterMode,
    expected_kind: HandlerWorkKind,
    expected_profile_id: str,
    expected_service_name: str,
    expected_scope_digest: bytes,
    expected_request_digest: bytes,
    expected_inbound_payload_digest: bytes,
    expected_caller_digest: bytes,
    expected_handler_digest: bytes,
    max_metadata_units: int,
    max_handler_budget_units: int,
    max_raw_key_units: int,
    previous_seen_capsule_digests: Iterable[bytes] = (),
    highest_seen_sequence: int | None = None,
    allow_component_watch: bool = False,
    min_family_count: int = 2,
    min_path_family_count: int = 2,
) -> HandlerCapsuleReport:
    capsule_t = tuple(capsules)
    mode = LiveAdapterMode(expected_mode)
    kind = HandlerWorkKind(expected_kind)
    components = (_component_digest(profile_edge_report), _component_digest(live_adapter_report), _component_digest(ingress_drain_report), _component_digest(backpressure_report))
    common = dict(mode=mode, handler_kind=kind, profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, inbound_payload_digest=expected_inbound_payload_digest, caller_digest=expected_caller_digest, handler_digest=expected_handler_digest, capsules=capsule_t, components=components)
    if not capsule_t:
        return _report(HandlerCapsuleDecisionKind.EMPTY_NO_CAPSULES, False, False, "handler needs capsules", **common)
    if mode is LiveAdapterMode.OUTBOUND_PUBLIC_SEND:
        return _report(HandlerCapsuleDecisionKind.QUARANTINE_MODE_COMPONENT_MISMATCH, False, False, "outbound-only adapter cannot authorize handler work", **common)
    if not _component_accept(profile_edge_report) or _component_quarantined(profile_edge_report):
        return _report(HandlerCapsuleDecisionKind.HOLD_PROFILE_EDGE if not _component_quarantined(profile_edge_report) else HandlerCapsuleDecisionKind.QUARANTINE_COMPONENT_DIGEST_DRIFT, False, False, "profile edge must accept before handler", **common)
    if not _component_accept(live_adapter_report) or _component_quarantined(live_adapter_report):
        return _report(HandlerCapsuleDecisionKind.HOLD_LIVE_ADAPTER if not _component_quarantined(live_adapter_report) else HandlerCapsuleDecisionKind.QUARANTINE_COMPONENT_DIGEST_DRIFT, False, False, "live adapter must accept before handler", **common)
    if not _component_accept(ingress_drain_report) or _component_quarantined(ingress_drain_report):
        return _report(HandlerCapsuleDecisionKind.HOLD_INGRESS_DRAIN if not _component_quarantined(ingress_drain_report) else HandlerCapsuleDecisionKind.QUARANTINE_COMPONENT_DIGEST_DRIFT, False, False, "ingress drain must accept before handler", **common)
    if not _component_accept(backpressure_report) or _component_quarantined(backpressure_report):
        return _report(HandlerCapsuleDecisionKind.HOLD_BACKPRESSURE if not _component_quarantined(backpressure_report) else HandlerCapsuleDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, "backpressure must accept before handler", **common)
    if any(_component_watch(c) for c in (profile_edge_report, live_adapter_report, ingress_drain_report, backpressure_report)) and not allow_component_watch:
        return _report(HandlerCapsuleDecisionKind.HOLD_COMPONENT_WATCH, False, True, "component watch pressure must be carried", **common)

    seen = set(previous_seen_capsule_digests)
    by_sequence: dict[int, HandlerCapsule] = {}
    for capsule in capsule_t:
        if not capsule.verifies():
            return _report(HandlerCapsuleDecisionKind.QUARANTINE_BAD_SIGNATURE, False, False, "bad handler capsule signature", **common)
        if not capsule.live(now):
            return _report(HandlerCapsuleDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, False, False, "expired or future handler capsule", **common)
        if capsule.capsule_digest in seen:
            return _report(HandlerCapsuleDecisionKind.QUARANTINE_REPLAY, False, False, "handler capsule replayed", **common)
        if highest_seen_sequence is not None and capsule.sequence < highest_seen_sequence:
            return _report(HandlerCapsuleDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, False, "handler sequence rollback", **common)
        prior = by_sequence.get(capsule.sequence)
        if prior is not None and prior.capsule_core_digest != capsule.capsule_core_digest:
            return _report(HandlerCapsuleDecisionKind.QUARANTINE_SEQUENCE_FORK, False, False, "same-sequence handler capsule fork", **common)
        by_sequence[capsule.sequence] = capsule
        if capsule.mode is not mode:
            return _report(HandlerCapsuleDecisionKind.QUARANTINE_MODE_DRIFT, False, False, "mode drift", **common)
        if capsule.kind is not kind:
            return _report(HandlerCapsuleDecisionKind.QUARANTINE_KIND_DRIFT, False, False, "handler kind drift", **common)
        if capsule.profile_id != expected_profile_id:
            return _report(HandlerCapsuleDecisionKind.QUARANTINE_PROFILE_DRIFT, False, False, "profile drift", **common)
        if capsule.service_name != expected_service_name:
            return _report(HandlerCapsuleDecisionKind.QUARANTINE_SERVICE_DRIFT, False, False, "service drift", **common)
        if capsule.scope_digest != expected_scope_digest:
            return _report(HandlerCapsuleDecisionKind.QUARANTINE_SCOPE_DRIFT, False, False, "scope drift", **common)
        if capsule.request_digest != expected_request_digest:
            return _report(HandlerCapsuleDecisionKind.QUARANTINE_REQUEST_DRIFT, False, False, "request drift", **common)
        if capsule.inbound_payload_digest != expected_inbound_payload_digest:
            return _report(HandlerCapsuleDecisionKind.QUARANTINE_PAYLOAD_DRIFT, False, False, "payload drift", **common)
        if capsule.caller_digest != expected_caller_digest:
            return _report(HandlerCapsuleDecisionKind.QUARANTINE_CALLER_DRIFT, False, False, "caller drift", **common)
        if capsule.handler_digest != expected_handler_digest:
            return _report(HandlerCapsuleDecisionKind.QUARANTINE_HANDLER_DRIFT, False, False, "handler drift", **common)
        if (capsule.profile_edge_digest, capsule.live_adapter_digest, capsule.ingress_drain_digest, capsule.backpressure_digest) != components:
            return _report(HandlerCapsuleDecisionKind.QUARANTINE_COMPONENT_DIGEST_DRIFT, False, False, "component digest drift", **common)
        if capsule.hard_negative_count:
            return _report(HandlerCapsuleDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, "hard negatives block handler", **common)
    ordered = sorted(by_sequence.values(), key=lambda c: c.sequence)
    for left, right in zip(ordered, ordered[1:]):
        if right.sequence == left.sequence + 1 and right.previous_capsule_digest != left.capsule_digest:
            return _report(HandlerCapsuleDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, False, "handler previous-link mismatch", **common)
    metadata_total = sum(c.metadata_units for c in ordered)
    handler_total = sum(c.handler_budget_units for c in ordered)
    raw_total = sum(c.raw_key_units for c in ordered)
    if metadata_total > max_metadata_units or raw_total > max_raw_key_units:
        return _report(HandlerCapsuleDecisionKind.QUARANTINE_METADATA_BUDGET, False, False, "handler metadata budget exceeded", **common)
    if handler_total > max_handler_budget_units:
        return _report(HandlerCapsuleDecisionKind.QUARANTINE_HANDLER_BUDGET, False, False, "handler budget exceeded", **common)
    family_count = len({c.family_id for c in ordered})
    path_count = len({c.path_family for c in ordered})
    if family_count < min_family_count:
        return _report(HandlerCapsuleDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, "handler needs more family diversity", **common)
    if path_count < min_path_family_count:
        return _report(HandlerCapsuleDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, "handler needs more path diversity", **common)
    latest = ordered[-1]
    watch = any(_component_watch(c) for c in (profile_edge_report, live_adapter_report, ingress_drain_report, backpressure_report))
    return _report(HandlerCapsuleDecisionKind.ACCEPT_WITH_WATCH if watch else HandlerCapsuleDecisionKind.ACCEPT_HANDLER_CAPSULE, True, watch, "handler capsule accepted", accepted=latest, **common)
