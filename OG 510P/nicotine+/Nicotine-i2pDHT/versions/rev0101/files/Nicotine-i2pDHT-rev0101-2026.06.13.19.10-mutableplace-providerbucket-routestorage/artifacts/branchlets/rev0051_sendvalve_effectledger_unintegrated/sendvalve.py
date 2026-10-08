"""No-network public send valve.

rev0050 left two useful public-edge paths: one line with commit barriers and one
line with outbox-drain/SAM-canary/compact-join checks.  rev0051 joins those
paths at the last no-network boundary before a future router-backed public
write.  The send valve still does not open SAM, publish to the DHT, or mutate a
router.  It only says whether one exact side-effect tuple is locally ready to
leave the shadow lane.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Any, Iterable

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST

SEND_VALVE_DOMAIN = DOMAIN + b":send-valve-v1:"


class SendValveAction(str, Enum):
    SEND_REFRESH = "send_refresh"
    SEND_WITHDRAW = "send_withdraw"
    SEND_REPAIR = "send_repair"


class SendValveDecisionKind(str, Enum):
    ACCEPT_SEND_VALVE = "accept_send_valve"
    ACCEPT_IDEMPOTENT_REPLAY = "accept_idempotent_replay"
    ACCEPT_WITH_WATCH = "accept_with_watch"
    EMPTY_NO_AUTHORIZATIONS = "empty_no_authorizations"
    HOLD_COMMIT_BARRIER = "hold_commit_barrier"
    HOLD_OUTBOX_DRAIN = "hold_outbox_drain"
    HOLD_SAM_CANARY = "hold_sam_canary"
    HOLD_COMPACT_JOIN = "hold_compact_join"
    HOLD_WATCH_DEBT = "hold_watch_debt"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    QUARANTINE_COMMIT_BARRIER = "quarantine_commit_barrier"
    QUARANTINE_OUTBOX_DRAIN = "quarantine_outbox_drain"
    QUARANTINE_SAM_CANARY = "quarantine_sam_canary"
    QUARANTINE_COMPACT_JOIN = "quarantine_compact_join"
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
    QUARANTINE_SESSION_DRIFT = "quarantine_session_drift"
    QUARANTINE_DESTINATION_DRIFT = "quarantine_destination_drift"
    QUARANTINE_ACTION_DRIFT = "quarantine_action_drift"
    QUARANTINE_COMPONENT_DIGEST_DRIFT = "quarantine_component_digest_drift"
    QUARANTINE_IDEMPOTENCY_CONFLICT = "quarantine_idempotency_conflict"
    QUARANTINE_EFFECT_DRIFT = "quarantine_effect_drift"


@dataclass(frozen=True)
class SendValveAuthorization:
    action: SendValveAction
    profile_id: str
    service_name: str
    session_id: str
    destination: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    commit_barrier_digest: bytes
    outbox_drain_digest: bytes
    sam_canary_digest: bytes
    compact_join_digest: bytes
    frame_digest: bytes
    idempotency_key: bytes
    public_effect_digest: bytes
    sequence: int
    previous_authorization_digest: bytes
    issued_at: int
    expires_at: int
    family_id: str
    path_family: str
    signer_public_key: bytes
    signature: bytes = b""

    def __post_init__(self) -> None:
        object.__setattr__(self, "action", SendValveAction(self.action))
        if not self.profile_id or not self.service_name or not self.session_id or not self.destination or not self.family_id or not self.path_family:
            raise ValueError("send valve authorization needs profile/service/session/destination/family/path")
        if self.sequence < 0:
            raise ValueError("sequence must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("expires_at must follow issued_at")
        for name, value in (
            ("scope_digest", self.scope_digest),
            ("request_digest", self.request_digest),
            ("payload_digest", self.payload_digest),
            ("commit_barrier_digest", self.commit_barrier_digest),
            ("outbox_drain_digest", self.outbox_drain_digest),
            ("sam_canary_digest", self.sam_canary_digest),
            ("compact_join_digest", self.compact_join_digest),
            ("frame_digest", self.frame_digest),
            ("idempotency_key", self.idempotency_key),
            ("public_effect_digest", self.public_effect_digest),
            ("previous_authorization_digest", self.previous_authorization_digest),
            ("signer_public_key", self.signer_public_key),
        ):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if self.signature and len(self.signature) != 64:
            raise ValueError("signature must be empty or Ed25519-sized")

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"action": self.action.value,
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"session": self.session_id,
            b"destination": self.destination,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"payload": self.payload_digest,
            b"commit": self.commit_barrier_digest,
            b"drain": self.outbox_drain_digest,
            b"canary": self.sam_canary_digest,
            b"compact": self.compact_join_digest,
            b"frame": self.frame_digest,
            b"idem": self.idempotency_key,
            b"effect": self.public_effect_digest,
            b"seq": self.sequence,
            b"prev": self.previous_authorization_digest,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"family": self.family_id,
            b"path_family": self.path_family,
            b"signer": self.signer_public_key,
        }

    def signature_payload(self) -> bytes:
        return SEND_VALVE_DOMAIN + b":authorization-sig:" + bencode(self.unsigned_bvalue())

    @property
    def authorization_core_digest(self) -> bytes:
        return sha256(SEND_VALVE_DOMAIN + b":authorization-core:" + bencode(self.unsigned_bvalue()))

    @property
    def authorization_digest(self) -> bytes:
        return sha256(SEND_VALVE_DOMAIN + b":authorization-digest:" + self.signature_payload() + self.signature)

    def verifies(self) -> bool:
        return verify_signature(self.signer_public_key, self.signature_payload(), self.signature)

    def live(self, now: int) -> bool:
        return self.issued_at <= now < self.expires_at


def make_send_valve_authorization(
    *,
    keypair: DhtKeypair,
    action: SendValveAction,
    profile_id: str,
    service_name: str,
    session_id: str,
    destination: str,
    scope_digest: bytes,
    request_digest: bytes,
    payload_digest: bytes,
    commit_barrier_digest: bytes,
    outbox_drain_digest: bytes,
    sam_canary_digest: bytes,
    compact_join_digest: bytes,
    frame_digest: bytes,
    idempotency_key: bytes,
    public_effect_digest: bytes,
    sequence: int,
    previous_authorization_digest: bytes = ZERO_DIGEST,
    issued_at: int,
    expires_at: int,
    family_id: str,
    path_family: str,
) -> SendValveAuthorization:
    unsigned = SendValveAuthorization(action, profile_id, service_name, session_id, destination, scope_digest, request_digest, payload_digest, commit_barrier_digest, outbox_drain_digest, sam_canary_digest, compact_join_digest, frame_digest, idempotency_key, public_effect_digest, sequence, previous_authorization_digest, issued_at, expires_at, family_id, path_family, keypair.public_key_bytes)
    return replace(unsigned, signature=keypair.sign(unsigned.signature_payload()))


@dataclass(frozen=True)
class SendValveReport:
    decision_kind: SendValveDecisionKind
    accept: bool
    watch: bool
    reason: str
    action: SendValveAction
    profile_id: str
    service_name: str
    session_id: str
    destination: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    accepted_authorization_digest: bytes
    idempotency_key: bytes
    public_effect_digest: bytes
    component_digests: tuple[bytes, ...]
    authorization_digests: tuple[bytes, ...]
    family_count: int
    path_family_count: int
    highest_sequence: int
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


_COMPONENT_DECISIONS = (
    ("commit barrier", "commit_barrier", SendValveDecisionKind.HOLD_COMMIT_BARRIER, SendValveDecisionKind.QUARANTINE_COMMIT_BARRIER),
    ("outbox drain", "outbox_drain", SendValveDecisionKind.HOLD_OUTBOX_DRAIN, SendValveDecisionKind.QUARANTINE_OUTBOX_DRAIN),
    ("SAM canary", "sam_canary", SendValveDecisionKind.HOLD_SAM_CANARY, SendValveDecisionKind.QUARANTINE_SAM_CANARY),
    ("compact join", "compact_join", SendValveDecisionKind.HOLD_COMPACT_JOIN, SendValveDecisionKind.QUARANTINE_COMPACT_JOIN),
)


def _digest(report: Any) -> bytes:
    for attr in ("report_digest", "transcript_digest", "candidate_digest"):
        value = getattr(report, attr, None)
        if isinstance(value, bytes) and len(value) == 32:
            return value
    raise ValueError("component lacks 32-byte digest")


def _accept(report: Any) -> bool:
    return bool(getattr(report, "accept", False))


def _watch(report: Any) -> bool:
    return bool(getattr(report, "watch", False))


def _quarantined(report: Any) -> bool:
    return bool(getattr(report, "quarantined", False))


def _report(
    kind: SendValveDecisionKind,
    accept: bool,
    watch: bool,
    reason: str,
    *,
    action: SendValveAction,
    profile_id: str,
    service_name: str,
    session_id: str,
    destination: str,
    scope_digest: bytes,
    request_digest: bytes,
    payload_digest: bytes,
    authorizations: Iterable[SendValveAuthorization] = (),
    selected: SendValveAuthorization | None = None,
    components: Iterable[bytes] = (),
    idempotency_key: bytes = ZERO_DIGEST,
    public_effect_digest: bytes = ZERO_DIGEST,
) -> SendValveReport:
    auth_tuple = tuple(sorted(authorizations, key=lambda item: (item.sequence, item.authorization_digest)))
    auth_digests = tuple(item.authorization_digest for item in auth_tuple)
    component_tuple = tuple(sorted(set(components)))
    families = len({item.family_id for item in auth_tuple})
    paths = len({item.path_family for item in auth_tuple})
    highest = selected.sequence if selected else max((item.sequence for item in auth_tuple), default=-1)
    accepted = selected.authorization_digest if selected and accept else ZERO_DIGEST
    if selected is not None:
        idempotency_key = selected.idempotency_key
        public_effect_digest = selected.public_effect_digest
    digest = sha256(SEND_VALVE_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"reason": reason,
        b"action": action.value,
        b"profile": profile_id,
        b"service": service_name,
        b"session": session_id,
        b"destination": destination,
        b"scope": scope_digest,
        b"request": request_digest,
        b"payload": payload_digest,
        b"accepted": accepted,
        b"idem": idempotency_key,
        b"effect": public_effect_digest,
        b"components": list(component_tuple),
        b"auths": list(auth_digests),
        b"families": families,
        b"paths": paths,
        b"highest": highest,
    }))
    return SendValveReport(kind, accept, watch, reason, action, profile_id, service_name, session_id, destination, scope_digest, request_digest, payload_digest, accepted, idempotency_key, public_effect_digest, component_tuple, auth_digests, families, paths, highest, digest)


def assess_send_valve(
    authorizations: Iterable[SendValveAuthorization],
    *,
    commit_barrier: Any,
    outbox_drain: Any,
    sam_canary: Any,
    compact_join: Any,
    now: int,
    expected_action: SendValveAction,
    expected_profile_id: str,
    expected_service_name: str,
    expected_session_id: str,
    expected_destination: str,
    expected_scope_digest: bytes,
    expected_request_digest: bytes,
    expected_payload_digest: bytes,
    expected_frame_digest: bytes,
    previous_highest_sequence: int = -1,
    previous_authorization_digest: bytes = ZERO_DIGEST,
    previously_seen_authorizations: Iterable[bytes] = (),
    committed_idempotency_effects: dict[bytes, bytes] | None = None,
    min_family_diversity: int = 2,
    min_path_diversity: int = 2,
    allow_watch_debt: bool = False,
) -> SendValveReport:
    components_by_name = {
        "commit_barrier": commit_barrier,
        "outbox_drain": outbox_drain,
        "sam_canary": sam_canary,
        "compact_join": compact_join,
    }
    component_digests = tuple(_digest(components_by_name[name]) for _, name, _, _ in _COMPONENT_DECISIONS)

    def make_report(kind: SendValveDecisionKind, accept: bool, watch: bool, reason: str, *, selected: SendValveAuthorization | None = None, candidates: Iterable[SendValveAuthorization] = ()) -> SendValveReport:
        return _report(kind, accept, watch, reason, action=expected_action, profile_id=expected_profile_id, service_name=expected_service_name, session_id=expected_session_id, destination=expected_destination, scope_digest=expected_scope_digest, request_digest=expected_request_digest, payload_digest=expected_payload_digest, authorizations=candidates, selected=selected, components=component_digests)

    for label, key, hold_kind, quarantine_kind in _COMPONENT_DECISIONS:
        component = components_by_name[key]
        if _quarantined(component):
            return make_report(quarantine_kind, False, True, f"{label} quarantined")
        if not _accept(component):
            return make_report(hold_kind, False, _watch(component), f"{label} did not accept")
    if any(_watch(component) for component in components_by_name.values()) and not allow_watch_debt:
        return make_report(SendValveDecisionKind.HOLD_WATCH_DEBT, False, True, "component watch debt must be explicitly carried into send valve")

    auth_tuple = tuple(sorted(authorizations, key=lambda item: (item.sequence, item.authorization_digest)))
    if not auth_tuple:
        return make_report(SendValveDecisionKind.EMPTY_NO_AUTHORIZATIONS, False, True, "no send valve authorizations supplied")

    seen = set(previously_seen_authorizations)
    core_by_seq: dict[int, bytes] = {}
    effect_by_idem: dict[bytes, bytes] = {}
    committed_effects = committed_idempotency_effects or {}
    for auth in auth_tuple:
        if not auth.verifies():
            return make_report(SendValveDecisionKind.QUARANTINE_BAD_SIGNATURE, False, True, "send valve authorization signature failed", candidates=auth_tuple)
        if not auth.live(now):
            return make_report(SendValveDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, False, True, "send valve authorization expired or future", candidates=auth_tuple)
        if auth.authorization_digest in seen:
            return make_report(SendValveDecisionKind.QUARANTINE_REPLAY, False, True, "send valve authorization replay", candidates=auth_tuple)
        if auth.sequence <= previous_highest_sequence:
            return make_report(SendValveDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, True, "send valve sequence rollback", candidates=auth_tuple)
        if previous_highest_sequence >= 0 and auth.previous_authorization_digest != previous_authorization_digest:
            return make_report(SendValveDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, True, "send valve previous digest mismatch", candidates=auth_tuple)
        if auth.profile_id != expected_profile_id:
            return make_report(SendValveDecisionKind.QUARANTINE_PROFILE_DRIFT, False, True, "profile drift", candidates=auth_tuple)
        if auth.service_name != expected_service_name:
            return make_report(SendValveDecisionKind.QUARANTINE_SERVICE_DRIFT, False, True, "service drift", candidates=auth_tuple)
        if auth.session_id != expected_session_id:
            return make_report(SendValveDecisionKind.QUARANTINE_SESSION_DRIFT, False, True, "session drift", candidates=auth_tuple)
        if auth.destination != expected_destination:
            return make_report(SendValveDecisionKind.QUARANTINE_DESTINATION_DRIFT, False, True, "destination drift", candidates=auth_tuple)
        if auth.action is not expected_action:
            return make_report(SendValveDecisionKind.QUARANTINE_ACTION_DRIFT, False, True, "send action drift", candidates=auth_tuple)
        if auth.scope_digest != expected_scope_digest:
            return make_report(SendValveDecisionKind.QUARANTINE_SCOPE_DRIFT, False, True, "scope drift", candidates=auth_tuple)
        if auth.request_digest != expected_request_digest:
            return make_report(SendValveDecisionKind.QUARANTINE_REQUEST_DRIFT, False, True, "request drift", candidates=auth_tuple)
        if auth.payload_digest != expected_payload_digest:
            return make_report(SendValveDecisionKind.QUARANTINE_PAYLOAD_DRIFT, False, True, "payload drift", candidates=auth_tuple)
        if auth.frame_digest != expected_frame_digest or auth.commit_barrier_digest != _digest(commit_barrier) or auth.outbox_drain_digest != _digest(outbox_drain) or auth.sam_canary_digest != _digest(sam_canary) or auth.compact_join_digest != _digest(compact_join):
            return make_report(SendValveDecisionKind.QUARANTINE_COMPONENT_DIGEST_DRIFT, False, True, "component/frame digest drift", candidates=auth_tuple)
        drain_idem = getattr(outbox_drain, "idempotency_key", ZERO_DIGEST)
        canary_idem = getattr(sam_canary, "idempotency_key", drain_idem)
        if auth.idempotency_key != drain_idem or auth.idempotency_key != canary_idem:
            return make_report(SendValveDecisionKind.QUARANTINE_IDEMPOTENCY_CONFLICT, False, True, "idempotency key drift", candidates=auth_tuple)
        expected_effect = getattr(outbox_drain, "drain_effect_digest", ZERO_DIGEST)
        canary_effect = getattr(sam_canary, "canary_effect_digest", None)
        if expected_effect != ZERO_DIGEST and auth.public_effect_digest != expected_effect:
            return make_report(SendValveDecisionKind.QUARANTINE_EFFECT_DRIFT, False, True, "drain effect drift", candidates=auth_tuple)
        if isinstance(canary_effect, bytes) and len(canary_effect) == 32 and canary_effect != ZERO_DIGEST and canary_effect != auth.public_effect_digest:
            return make_report(SendValveDecisionKind.QUARANTINE_EFFECT_DRIFT, False, True, "SAM canary effect drift", candidates=auth_tuple)
        prior_core = core_by_seq.setdefault(auth.sequence, auth.authorization_core_digest)
        if prior_core != auth.authorization_core_digest:
            return make_report(SendValveDecisionKind.QUARANTINE_SEQUENCE_FORK, False, True, "same-sequence send valve fork", candidates=auth_tuple)
        prior_effect = effect_by_idem.setdefault(auth.idempotency_key, auth.public_effect_digest)
        if prior_effect != auth.public_effect_digest:
            return make_report(SendValveDecisionKind.QUARANTINE_IDEMPOTENCY_CONFLICT, False, True, "idempotency maps to two public effects", candidates=auth_tuple)
        committed_effect = committed_effects.get(auth.idempotency_key)
        if committed_effect is not None:
            if committed_effect == auth.public_effect_digest:
                return make_report(SendValveDecisionKind.ACCEPT_IDEMPOTENT_REPLAY, True, True, "same idempotency/effect already committed", selected=auth, candidates=auth_tuple)
            return make_report(SendValveDecisionKind.QUARANTINE_IDEMPOTENCY_CONFLICT, False, True, "committed idempotency maps to different effect", candidates=auth_tuple)
    if len({item.family_id for item in auth_tuple}) < min_family_diversity:
        return make_report(SendValveDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, "send valve authorizations lack family diversity", candidates=auth_tuple)
    if len({item.path_family for item in auth_tuple}) < min_path_diversity:
        return make_report(SendValveDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, "send valve authorizations lack path diversity", candidates=auth_tuple)
    selected = max(auth_tuple, key=lambda item: (item.sequence, item.authorization_digest))
    watch = any(_watch(component) for component in components_by_name.values())
    return make_report(SendValveDecisionKind.ACCEPT_WITH_WATCH if watch else SendValveDecisionKind.ACCEPT_SEND_VALVE, True, watch, "send valve binds commit, drain, canary, compact evidence before live send", selected=selected, candidates=auth_tuple)
