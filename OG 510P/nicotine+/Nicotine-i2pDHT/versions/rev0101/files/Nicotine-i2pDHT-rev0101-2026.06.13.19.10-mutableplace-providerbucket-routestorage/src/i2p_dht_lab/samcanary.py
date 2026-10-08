"""SAM-shadow canary lane before any live router-backed publication send.

A SAM trace can be valid, an outbox drain can be committed, and egress can be
budgeted, but a future live send still needs a tiny canary boundary that binds
session/destination, frame/payload digest, idempotency, and exact scope.  This is
not a router probe and does not open a socket.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Any, Iterable

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .outboxdrain import OutboxDrainReport

SAM_CANARY_DOMAIN = DOMAIN + b":sam-canary-v1:"


class SamCanaryDecisionKind(str, Enum):
    ACCEPT_CANARY = "accept_canary"
    ACCEPT_WITH_RECONNECT_WATCH = "accept_with_reconnect_watch"
    HOLD_DRAIN = "hold_drain"
    HOLD_SAM_TRACE = "hold_sam_trace"
    HOLD_EGRESS = "hold_egress"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    EMPTY_NO_CANARIES = "empty_no_canaries"
    QUARANTINE_DRAIN = "quarantine_drain"
    QUARANTINE_SAM_TRACE = "quarantine_sam_trace"
    QUARANTINE_EGRESS = "quarantine_egress"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_EXPIRED_OR_FUTURE = "quarantine_expired_or_future"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_PROFILE_DRIFT = "quarantine_profile_drift"
    QUARANTINE_SERVICE_DRIFT = "quarantine_service_drift"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_REQUEST_DRIFT = "quarantine_request_drift"
    QUARANTINE_PAYLOAD_DRIFT = "quarantine_payload_drift"
    QUARANTINE_DESTINATION_DRIFT = "quarantine_destination_drift"
    QUARANTINE_COMPONENT_DIGEST_DRIFT = "quarantine_component_digest_drift"
    QUARANTINE_IDEMPOTENCY_CONFLICT = "quarantine_idempotency_conflict"
    QUARANTINE_PUBLIC_PAYLOAD_LEAK = "quarantine_public_payload_leak"


@dataclass(frozen=True)
class SamCanary:
    profile_id: str
    service_name: str
    session_id: str
    destination: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    outbox_drain_digest: bytes
    sam_trace_digest: bytes
    egress_report_digest: bytes
    idempotency_key: bytes
    frame_digest: bytes
    canary_effect_digest: bytes
    sequence: int
    previous_canary_digest: bytes
    issued_at: int
    expires_at: int
    family_id: str
    path_family: str
    signer_public_key: bytes
    public_label: str = ""
    signature: bytes = b""

    def __post_init__(self) -> None:
        if not self.profile_id or not self.service_name or not self.session_id or not self.destination or not self.family_id or not self.path_family:
            raise ValueError("SAM canary needs profile/service/session/destination/family/path")
        if self.sequence < 0:
            raise ValueError("sequence must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("expires_at must follow issued_at")
        if len(self.public_label.encode("utf-8")) > 96:
            raise ValueError("public label must be short")
        for name, value in (
            ("scope_digest", self.scope_digest),
            ("request_digest", self.request_digest),
            ("payload_digest", self.payload_digest),
            ("outbox_drain_digest", self.outbox_drain_digest),
            ("sam_trace_digest", self.sam_trace_digest),
            ("egress_report_digest", self.egress_report_digest),
            ("idempotency_key", self.idempotency_key),
            ("frame_digest", self.frame_digest),
            ("canary_effect_digest", self.canary_effect_digest),
            ("previous_canary_digest", self.previous_canary_digest),
            ("signer_public_key", self.signer_public_key),
        ):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if self.signature and len(self.signature) != 64:
            raise ValueError("signature must be empty or Ed25519-sized")

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"session": self.session_id,
            b"destination": self.destination,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"payload": self.payload_digest,
            b"drain": self.outbox_drain_digest,
            b"sam_trace": self.sam_trace_digest,
            b"egress": self.egress_report_digest,
            b"idem": self.idempotency_key,
            b"frame": self.frame_digest,
            b"effect": self.canary_effect_digest,
            b"seq": self.sequence,
            b"prev": self.previous_canary_digest,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"family": self.family_id,
            b"path_family": self.path_family,
            b"label": self.public_label,
            b"signer": self.signer_public_key,
        }

    def signature_payload(self) -> bytes:
        return SAM_CANARY_DOMAIN + b":canary-sig:" + bencode(self.unsigned_bvalue())

    @property
    def canary_core_digest(self) -> bytes:
        return sha256(SAM_CANARY_DOMAIN + b":canary-core:" + bencode(self.unsigned_bvalue()))

    @property
    def canary_digest(self) -> bytes:
        return sha256(SAM_CANARY_DOMAIN + b":canary-digest:" + self.signature_payload() + self.signature)

    def verifies(self) -> bool:
        return verify_signature(self.signer_public_key, self.signature_payload(), self.signature)

    def live(self, now: int) -> bool:
        return self.issued_at <= now < self.expires_at


def make_sam_canary(
    *,
    keypair: DhtKeypair,
    profile_id: str,
    service_name: str,
    session_id: str,
    destination: str,
    scope_digest: bytes,
    request_digest: bytes,
    payload_digest: bytes,
    outbox_drain_digest: bytes,
    sam_trace_digest: bytes,
    egress_report_digest: bytes,
    idempotency_key: bytes,
    frame_digest: bytes,
    canary_effect_digest: bytes,
    sequence: int,
    previous_canary_digest: bytes = ZERO_DIGEST,
    issued_at: int,
    expires_at: int,
    family_id: str,
    path_family: str,
    public_label: str = "",
) -> SamCanary:
    unsigned = SamCanary(profile_id, service_name, session_id, destination, scope_digest, request_digest, payload_digest, outbox_drain_digest, sam_trace_digest, egress_report_digest, idempotency_key, frame_digest, canary_effect_digest, sequence, previous_canary_digest, issued_at, expires_at, family_id, path_family, keypair.public_key_bytes, public_label)
    return replace(unsigned, signature=keypair.sign(unsigned.signature_payload()))


@dataclass(frozen=True)
class SamCanaryReport:
    decision_kind: SamCanaryDecisionKind
    accept: bool
    watch: bool
    reason: str
    profile_id: str
    service_name: str
    destination: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    accepted_canary_digest: bytes
    idempotency_key: bytes
    canary_digests: tuple[bytes, ...]
    component_digests: tuple[bytes, ...]
    family_count: int
    path_family_count: int
    highest_sequence: int
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _digest(report: Any) -> bytes:
    for attr in ("report_digest", "transcript_digest"):
        value = getattr(report, attr, None)
        if isinstance(value, bytes) and len(value) == 32:
            return value
    raise ValueError("component lacks digest")


def _accept(report: Any) -> bool:
    return bool(getattr(report, "accept", False))


def _watch(report: Any) -> bool:
    return bool(getattr(report, "watch", False)) or getattr(report, "decision_kind", None).__class__.__name__.endswith("SamTraceDecisionKind") and "watch" in getattr(getattr(report, "decision_kind", None), "value", "")


def _quarantined(report: Any) -> bool:
    return bool(getattr(report, "quarantined", False))


def _report(kind: SamCanaryDecisionKind, accept: bool, watch: bool, reason: str, *, profile_id: str, service_name: str, destination: str, scope_digest: bytes, request_digest: bytes, payload_digest: bytes, canaries: Iterable[SamCanary] = (), selected: SamCanary | None = None, components: Iterable[bytes] = ()) -> SamCanaryReport:
    canary_tuple = tuple(sorted(canaries, key=lambda item: (item.sequence, item.canary_digest)))
    digests = tuple(item.canary_digest for item in canary_tuple)
    families = len({item.family_id for item in canary_tuple})
    paths = len({item.path_family for item in canary_tuple})
    highest = selected.sequence if selected else max((item.sequence for item in canary_tuple), default=-1)
    accepted = selected.canary_digest if selected and accept else ZERO_DIGEST
    idem = selected.idempotency_key if selected else ZERO_DIGEST
    component_digests = tuple(sorted(set(components)))
    digest = sha256(SAM_CANARY_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"reason": reason,
        b"profile": profile_id,
        b"service": service_name,
        b"destination": destination,
        b"scope": scope_digest,
        b"request": request_digest,
        b"payload": payload_digest,
        b"accepted": accepted,
        b"idem": idem,
        b"canaries": list(digests),
        b"components": list(component_digests),
        b"families": families,
        b"paths": paths,
        b"highest": highest,
    }))
    return SamCanaryReport(kind, accept, watch, reason, profile_id, service_name, destination, scope_digest, request_digest, payload_digest, accepted, idem, digests, component_digests, families, paths, highest, digest)


def assess_sam_canary(
    canaries: Iterable[SamCanary],
    *,
    outbox_drain: OutboxDrainReport,
    sam_trace_report: Any,
    egress_report: Any,
    now: int,
    expected_profile_id: str,
    expected_service_name: str,
    expected_session_id: str,
    expected_destination: str,
    expected_scope_digest: bytes,
    expected_request_digest: bytes,
    expected_payload_digest: bytes,
    expected_frame_digest: bytes,
    previous_highest_sequence: int = -1,
    previous_canary_digest: bytes = ZERO_DIGEST,
    previously_seen_canaries: Iterable[bytes] = (),
    min_family_diversity: int = 2,
    min_path_diversity: int = 2,
    forbid_public_payload_fragments: Iterable[str] = (),
) -> SamCanaryReport:
    components = (outbox_drain.report_digest, _digest(sam_trace_report), _digest(egress_report))

    def make_report(kind: SamCanaryDecisionKind, accept: bool, watch: bool, reason: str, *, selected: SamCanary | None = None, candidate_canaries: Iterable[SamCanary] = ()) -> SamCanaryReport:
        return _report(kind, accept, watch, reason, profile_id=expected_profile_id, service_name=expected_service_name, destination=expected_destination, scope_digest=expected_scope_digest, request_digest=expected_request_digest, payload_digest=expected_payload_digest, canaries=candidate_canaries, selected=selected, components=components)

    for component, hold, quarantine, label in (
        (outbox_drain, SamCanaryDecisionKind.HOLD_DRAIN, SamCanaryDecisionKind.QUARANTINE_DRAIN, "outbox drain"),
        (sam_trace_report, SamCanaryDecisionKind.HOLD_SAM_TRACE, SamCanaryDecisionKind.QUARANTINE_SAM_TRACE, "SAM trace"),
        (egress_report, SamCanaryDecisionKind.HOLD_EGRESS, SamCanaryDecisionKind.QUARANTINE_EGRESS, "egress"),
    ):
        if _quarantined(component):
            return make_report(quarantine, False, True, f"{label} quarantined")
        if not _accept(component):
            return make_report(hold, False, _watch(component), f"{label} did not accept")

    canary_tuple = tuple(sorted(canaries, key=lambda item: (item.sequence, item.canary_digest)))
    if not canary_tuple:
        return make_report(SamCanaryDecisionKind.EMPTY_NO_CANARIES, False, True, "no SAM canaries supplied")
    seen = set(previously_seen_canaries)
    core_by_seq: dict[int, bytes] = {}
    effect_by_idem: dict[bytes, bytes] = {}
    forbidden = tuple(fragment for fragment in forbid_public_payload_fragments if fragment)
    for canary in canary_tuple:
        if not canary.verifies():
            return make_report(SamCanaryDecisionKind.QUARANTINE_BAD_SIGNATURE, False, True, "SAM canary signature failed", candidate_canaries=canary_tuple)
        if not canary.live(now):
            return make_report(SamCanaryDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, False, True, "SAM canary expired or future", candidate_canaries=canary_tuple)
        if canary.canary_digest in seen:
            return make_report(SamCanaryDecisionKind.QUARANTINE_REPLAY, False, True, "SAM canary replay", candidate_canaries=canary_tuple)
        if canary.sequence <= previous_highest_sequence:
            return make_report(SamCanaryDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, True, "SAM canary sequence rollback", candidate_canaries=canary_tuple)
        if previous_highest_sequence >= 0 and canary.previous_canary_digest != previous_canary_digest:
            return make_report(SamCanaryDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, True, "SAM canary previous digest mismatch", candidate_canaries=canary_tuple)
        if any(fragment in canary.public_label for fragment in forbidden):
            return make_report(SamCanaryDecisionKind.QUARANTINE_PUBLIC_PAYLOAD_LEAK, False, True, "SAM canary label leaks public payload fragment", candidate_canaries=canary_tuple)
        if canary.profile_id != expected_profile_id:
            return make_report(SamCanaryDecisionKind.QUARANTINE_PROFILE_DRIFT, False, True, "SAM canary profile drift", candidate_canaries=canary_tuple)
        if canary.service_name != expected_service_name:
            return make_report(SamCanaryDecisionKind.QUARANTINE_SERVICE_DRIFT, False, True, "SAM canary service drift", candidate_canaries=canary_tuple)
        if canary.session_id != expected_session_id or canary.destination != expected_destination:
            return make_report(SamCanaryDecisionKind.QUARANTINE_DESTINATION_DRIFT, False, True, "SAM canary session/destination drift", candidate_canaries=canary_tuple)
        if canary.scope_digest != expected_scope_digest:
            return make_report(SamCanaryDecisionKind.QUARANTINE_SCOPE_DRIFT, False, True, "SAM canary scope drift", candidate_canaries=canary_tuple)
        if canary.request_digest != expected_request_digest:
            return make_report(SamCanaryDecisionKind.QUARANTINE_REQUEST_DRIFT, False, True, "SAM canary request drift", candidate_canaries=canary_tuple)
        if canary.payload_digest != expected_payload_digest:
            return make_report(SamCanaryDecisionKind.QUARANTINE_PAYLOAD_DRIFT, False, True, "SAM canary payload drift", candidate_canaries=canary_tuple)
        if canary.outbox_drain_digest != outbox_drain.report_digest or canary.sam_trace_digest != _digest(sam_trace_report) or canary.egress_report_digest != _digest(egress_report) or canary.frame_digest != expected_frame_digest:
            return make_report(SamCanaryDecisionKind.QUARANTINE_COMPONENT_DIGEST_DRIFT, False, True, "SAM canary component/frame digest drift", candidate_canaries=canary_tuple)
        if canary.idempotency_key != outbox_drain.idempotency_key:
            return make_report(SamCanaryDecisionKind.QUARANTINE_IDEMPOTENCY_CONFLICT, False, True, "SAM canary idempotency key drift", candidate_canaries=canary_tuple)
        prior_core = core_by_seq.setdefault(canary.sequence, canary.canary_core_digest)
        if prior_core != canary.canary_core_digest:
            return make_report(SamCanaryDecisionKind.QUARANTINE_SEQUENCE_FORK, False, True, "same-sequence SAM canary fork", candidate_canaries=canary_tuple)
        prior_effect = effect_by_idem.setdefault(canary.idempotency_key, canary.canary_effect_digest)
        if prior_effect != canary.canary_effect_digest:
            return make_report(SamCanaryDecisionKind.QUARANTINE_IDEMPOTENCY_CONFLICT, False, True, "SAM canary idempotency maps to different effect", candidate_canaries=canary_tuple)
    if len({item.family_id for item in canary_tuple}) < min_family_diversity:
        return make_report(SamCanaryDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, "SAM canaries lack family diversity", candidate_canaries=canary_tuple)
    if len({item.path_family for item in canary_tuple}) < min_path_diversity:
        return make_report(SamCanaryDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, "SAM canaries lack path diversity", candidate_canaries=canary_tuple)
    newest = max(canary_tuple, key=lambda item: (item.sequence, item.canary_digest))
    reconnect_watch = "reconnect" in getattr(getattr(sam_trace_report, "decision_kind", None), "value", "")
    watch = _watch(outbox_drain) or _watch(sam_trace_report) or _watch(egress_report) or reconnect_watch
    kind = SamCanaryDecisionKind.ACCEPT_WITH_RECONNECT_WATCH if reconnect_watch else (SamCanaryDecisionKind.ACCEPT_CANARY if not watch else SamCanaryDecisionKind.ACCEPT_WITH_RECONNECT_WATCH)
    return make_report(kind, True, watch, "SAM canary is exact-scope, idempotent, egress-budgeted, and no-network", selected=newest, candidate_canaries=canary_tuple)
