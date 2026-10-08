"""No-network public send seal.

rev0050 split the public edge into two useful branchlets: a commit barrier and an
outbox/SAM-canary/compact-join lane.  rev0051 joins them before any future live
SAM send or public bridge publication adapter exists.  The send seal is still a
local signed rehearsal artifact, not a network write.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Any, Iterable, Mapping

from .bencode import BValue, bencode
from .commitbarrier import PublicCommitAction
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST

SEND_SEAL_DOMAIN = DOMAIN + b":send-seal-v1:"


class SendSealDecisionKind(str, Enum):
    ACCEPT_SEND_SEAL = "accept_send_seal"
    ACCEPT_IDEMPOTENT_REPLAY = "accept_idempotent_replay"
    ACCEPT_WITH_WATCH = "accept_with_watch"
    EMPTY_NO_SEALS = "empty_no_seals"
    HOLD_COMMIT = "hold_commit"
    HOLD_DRAIN = "hold_drain"
    HOLD_CANARY = "hold_canary"
    HOLD_COMPACT_JOIN = "hold_compact_join"
    HOLD_WATCH_DEBT = "hold_watch_debt"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    QUARANTINE_COMMIT = "quarantine_commit"
    QUARANTINE_DRAIN = "quarantine_drain"
    QUARANTINE_CANARY = "quarantine_canary"
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
    QUARANTINE_ACTION_DRIFT = "quarantine_action_drift"
    QUARANTINE_COMPONENT_DIGEST_DRIFT = "quarantine_component_digest_drift"
    QUARANTINE_IDEMPOTENCY_CONFLICT = "quarantine_idempotency_conflict"
    QUARANTINE_EFFECT_CONFLICT = "quarantine_effect_conflict"


@dataclass(frozen=True)
class PublicSendSeal:
    action: PublicCommitAction
    profile_id: str
    service_name: str
    session_id: str
    destination: str
    scope_digest: bytes
    request_digest: bytes
    public_payload_digest: bytes
    commit_report_digest: bytes
    outbox_drain_digest: bytes
    sam_canary_digest: bytes
    compact_join_digest: bytes
    idempotency_key: bytes
    public_effect_digest: bytes
    sequence: int
    previous_send_seal_digest: bytes
    issued_at: int
    expires_at: int
    family_id: str
    path_family: str
    signer_public_key: bytes
    signature: bytes = b""

    def __post_init__(self) -> None:
        object.__setattr__(self, "action", PublicCommitAction(self.action))
        if not self.profile_id or not self.service_name or not self.session_id or not self.destination:
            raise ValueError("send seal requires profile/service/session/destination")
        if not self.family_id or not self.path_family:
            raise ValueError("send seal requires family and path family")
        if self.sequence < 0:
            raise ValueError("sequence must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("expires_at must follow issued_at")
        for name, value in (
            ("scope_digest", self.scope_digest),
            ("request_digest", self.request_digest),
            ("public_payload_digest", self.public_payload_digest),
            ("commit_report_digest", self.commit_report_digest),
            ("outbox_drain_digest", self.outbox_drain_digest),
            ("sam_canary_digest", self.sam_canary_digest),
            ("compact_join_digest", self.compact_join_digest),
            ("idempotency_key", self.idempotency_key),
            ("public_effect_digest", self.public_effect_digest),
            ("previous_send_seal_digest", self.previous_send_seal_digest),
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
            b"payload": self.public_payload_digest,
            b"commit": self.commit_report_digest,
            b"drain": self.outbox_drain_digest,
            b"canary": self.sam_canary_digest,
            b"compact": self.compact_join_digest,
            b"idem": self.idempotency_key,
            b"effect": self.public_effect_digest,
            b"seq": self.sequence,
            b"prev": self.previous_send_seal_digest,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"family": self.family_id,
            b"path_family": self.path_family,
            b"signer": self.signer_public_key,
        }

    def signature_payload(self) -> bytes:
        return SEND_SEAL_DOMAIN + b":seal-sig:" + bencode(self.unsigned_bvalue())

    @property
    def core_digest(self) -> bytes:
        return sha256(SEND_SEAL_DOMAIN + b":seal-core:" + bencode(self.unsigned_bvalue()))

    @property
    def seal_digest(self) -> bytes:
        return sha256(SEND_SEAL_DOMAIN + b":seal-digest:" + self.signature_payload() + self.signature)

    def verifies(self) -> bool:
        return verify_signature(self.signer_public_key, self.signature_payload(), self.signature)

    def live(self, now: int) -> bool:
        return self.issued_at <= now < self.expires_at


def make_public_send_seal(
    *,
    keypair: DhtKeypair,
    action: PublicCommitAction,
    profile_id: str,
    service_name: str,
    session_id: str,
    destination: str,
    scope_digest: bytes,
    request_digest: bytes,
    public_payload_digest: bytes,
    commit_report: Any,
    outbox_drain: Any,
    sam_canary: Any,
    compact_join: Any,
    idempotency_key: bytes,
    public_effect_digest: bytes,
    sequence: int,
    previous_send_seal_digest: bytes = ZERO_DIGEST,
    issued_at: int,
    expires_at: int,
    family_id: str,
    path_family: str,
) -> PublicSendSeal:
    unsigned = PublicSendSeal(
        action=action,
        profile_id=profile_id,
        service_name=service_name,
        session_id=session_id,
        destination=destination,
        scope_digest=scope_digest,
        request_digest=request_digest,
        public_payload_digest=public_payload_digest,
        commit_report_digest=_digest(commit_report),
        outbox_drain_digest=_digest(outbox_drain),
        sam_canary_digest=_digest(sam_canary),
        compact_join_digest=_digest(compact_join),
        idempotency_key=idempotency_key,
        public_effect_digest=public_effect_digest,
        sequence=sequence,
        previous_send_seal_digest=previous_send_seal_digest,
        issued_at=issued_at,
        expires_at=expires_at,
        family_id=family_id,
        path_family=path_family,
        signer_public_key=keypair.public_key_bytes,
    )
    return replace(unsigned, signature=keypair.sign(unsigned.signature_payload()))


@dataclass(frozen=True)
class SendSealReport:
    decision_kind: SendSealDecisionKind
    accept: bool
    watch: bool
    reason: str
    profile_id: str
    service_name: str
    action: PublicCommitAction
    destination: str
    scope_digest: bytes
    request_digest: bytes
    public_payload_digest: bytes
    accepted_seal_digest: bytes
    idempotency_key: bytes
    public_effect_digest: bytes
    seal_digests: tuple[bytes, ...]
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
        return self.accept


def _digest(report: Any) -> bytes:
    for attr in ("report_digest", "transcript_digest"):
        value = getattr(report, attr, None)
        if isinstance(value, bytes) and len(value) == 32:
            return value
    raise ValueError("component report lacks 32-byte digest")


def _accept(report: Any) -> bool:
    return bool(getattr(report, "accept", False))


def _watch(report: Any) -> bool:
    return bool(getattr(report, "watch", False))


def _quarantined(report: Any) -> bool:
    return bool(getattr(report, "quarantined", False))


def _report(
    kind: SendSealDecisionKind,
    accept: bool,
    watch: bool,
    reason: str,
    *,
    profile_id: str,
    service_name: str,
    action: PublicCommitAction,
    destination: str,
    scope_digest: bytes,
    request_digest: bytes,
    public_payload_digest: bytes,
    seals: Iterable[PublicSendSeal] = (),
    selected: PublicSendSeal | None = None,
    components: Iterable[bytes] = (),
) -> SendSealReport:
    seal_tuple = tuple(sorted(seals, key=lambda item: (item.sequence, item.seal_digest)))
    digests = tuple(item.seal_digest for item in seal_tuple)
    families = len({item.family_id for item in seal_tuple})
    paths = len({item.path_family for item in seal_tuple})
    highest = selected.sequence if selected else max((item.sequence for item in seal_tuple), default=-1)
    accepted = selected.seal_digest if selected and accept else ZERO_DIGEST
    idem = selected.idempotency_key if selected else ZERO_DIGEST
    effect = selected.public_effect_digest if selected else ZERO_DIGEST
    component_tuple = tuple(sorted(set(components)))
    digest = sha256(SEND_SEAL_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"reason": reason,
        b"profile": profile_id,
        b"service": service_name,
        b"action": action.value,
        b"destination": destination,
        b"scope": scope_digest,
        b"request": request_digest,
        b"payload": public_payload_digest,
        b"accepted": accepted,
        b"idem": idem,
        b"effect": effect,
        b"seals": list(digests),
        b"components": list(component_tuple),
        b"families": families,
        b"paths": paths,
        b"highest": highest,
    }))
    return SendSealReport(kind, accept, watch, reason, profile_id, service_name, action, destination, scope_digest, request_digest, public_payload_digest, accepted, idem, effect, digests, component_tuple, families, paths, highest, digest)


def assess_send_seal(
    seals: Iterable[PublicSendSeal],
    *,
    commit_report: Any,
    outbox_drain: Any,
    sam_canary: Any,
    compact_join: Any,
    now: int,
    expected_profile_id: str,
    expected_service_name: str,
    expected_action: PublicCommitAction,
    expected_destination: str,
    expected_scope_digest: bytes,
    expected_request_digest: bytes,
    expected_public_payload_digest: bytes,
    expected_idempotency_key: bytes | None = None,
    expected_public_effect_digest: bytes | None = None,
    committed_idempotency_effects: Mapping[bytes, bytes] | None = None,
    last_sequence: int = -1,
    last_send_seal_digest: bytes = ZERO_DIGEST,
    min_family_diversity: int = 2,
    min_path_diversity: int = 2,
    allow_watch_debt: bool = False,
) -> SendSealReport:
    action = PublicCommitAction(expected_action)
    components = (_digest(commit_report), _digest(outbox_drain), _digest(sam_canary), _digest(compact_join))
    for report, hold, quarantine, label in (
        (commit_report, SendSealDecisionKind.HOLD_COMMIT, SendSealDecisionKind.QUARANTINE_COMMIT, "commit"),
        (outbox_drain, SendSealDecisionKind.HOLD_DRAIN, SendSealDecisionKind.QUARANTINE_DRAIN, "outbox drain"),
        (sam_canary, SendSealDecisionKind.HOLD_CANARY, SendSealDecisionKind.QUARANTINE_CANARY, "SAM canary"),
        (compact_join, SendSealDecisionKind.HOLD_COMPACT_JOIN, SendSealDecisionKind.QUARANTINE_COMPACT_JOIN, "compact join"),
    ):
        if _quarantined(report):
            return _report(quarantine, False, True, f"{label} quarantined", profile_id=expected_profile_id, service_name=expected_service_name, action=action, destination=expected_destination, scope_digest=expected_scope_digest, request_digest=expected_request_digest, public_payload_digest=expected_public_payload_digest, components=components)
        if not _accept(report):
            return _report(hold, False, _watch(report), f"{label} did not accept", profile_id=expected_profile_id, service_name=expected_service_name, action=action, destination=expected_destination, scope_digest=expected_scope_digest, request_digest=expected_request_digest, public_payload_digest=expected_public_payload_digest, components=components)
    watch_debt = any(_watch(report) for report in (commit_report, outbox_drain, sam_canary, compact_join))
    if watch_debt and not allow_watch_debt:
        return _report(SendSealDecisionKind.HOLD_WATCH_DEBT, False, True, "component watch debt before send seal", profile_id=expected_profile_id, service_name=expected_service_name, action=action, destination=expected_destination, scope_digest=expected_scope_digest, request_digest=expected_request_digest, public_payload_digest=expected_public_payload_digest, components=components)

    seal_tuple = tuple(seals)
    if not seal_tuple:
        return _report(SendSealDecisionKind.EMPTY_NO_SEALS, False, False, "no send seal candidates", profile_id=expected_profile_id, service_name=expected_service_name, action=action, destination=expected_destination, scope_digest=expected_scope_digest, request_digest=expected_request_digest, public_payload_digest=expected_public_payload_digest, components=components)
    live: list[PublicSendSeal] = []
    seen_by_seq: dict[int, bytes] = {}
    for seal in seal_tuple:
        if not seal.verifies():
            return _report(SendSealDecisionKind.QUARANTINE_BAD_SIGNATURE, False, True, "bad send seal signature", profile_id=expected_profile_id, service_name=expected_service_name, action=action, destination=expected_destination, scope_digest=expected_scope_digest, request_digest=expected_request_digest, public_payload_digest=expected_public_payload_digest, seals=seal_tuple, components=components)
        if not seal.live(now):
            return _report(SendSealDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, False, True, "send seal expired or future-dated", profile_id=expected_profile_id, service_name=expected_service_name, action=action, destination=expected_destination, scope_digest=expected_scope_digest, request_digest=expected_request_digest, public_payload_digest=expected_public_payload_digest, seals=seal_tuple, components=components)
        previous = seen_by_seq.get(seal.sequence)
        if previous and previous != seal.core_digest:
            return _report(SendSealDecisionKind.QUARANTINE_SEQUENCE_FORK, False, True, "same sequence send seal fork", profile_id=expected_profile_id, service_name=expected_service_name, action=action, destination=expected_destination, scope_digest=expected_scope_digest, request_digest=expected_request_digest, public_payload_digest=expected_public_payload_digest, seals=seal_tuple, components=components)
        seen_by_seq[seal.sequence] = seal.core_digest
        if seal.sequence < last_sequence:
            return _report(SendSealDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, True, "send seal sequence rollback", profile_id=expected_profile_id, service_name=expected_service_name, action=action, destination=expected_destination, scope_digest=expected_scope_digest, request_digest=expected_request_digest, public_payload_digest=expected_public_payload_digest, seals=seal_tuple, components=components)
        if seal.sequence == last_sequence and seal.seal_digest == last_send_seal_digest:
            return _report(SendSealDecisionKind.QUARANTINE_REPLAY, False, True, "send seal replay", profile_id=expected_profile_id, service_name=expected_service_name, action=action, destination=expected_destination, scope_digest=expected_scope_digest, request_digest=expected_request_digest, public_payload_digest=expected_public_payload_digest, seals=seal_tuple, components=components)
        if seal.sequence > last_sequence and seal.previous_send_seal_digest != last_send_seal_digest and last_send_seal_digest != ZERO_DIGEST:
            return _report(SendSealDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, True, "send seal previous link mismatch", profile_id=expected_profile_id, service_name=expected_service_name, action=action, destination=expected_destination, scope_digest=expected_scope_digest, request_digest=expected_request_digest, public_payload_digest=expected_public_payload_digest, seals=seal_tuple, components=components)
        if seal.profile_id != expected_profile_id:
            return _report(SendSealDecisionKind.QUARANTINE_PROFILE_DRIFT, False, True, "profile drift", profile_id=expected_profile_id, service_name=expected_service_name, action=action, destination=expected_destination, scope_digest=expected_scope_digest, request_digest=expected_request_digest, public_payload_digest=expected_public_payload_digest, seals=seal_tuple, components=components)
        if seal.service_name != expected_service_name:
            return _report(SendSealDecisionKind.QUARANTINE_SERVICE_DRIFT, False, True, "service drift", profile_id=expected_profile_id, service_name=expected_service_name, action=action, destination=expected_destination, scope_digest=expected_scope_digest, request_digest=expected_request_digest, public_payload_digest=expected_public_payload_digest, seals=seal_tuple, components=components)
        if seal.destination != expected_destination:
            return _report(SendSealDecisionKind.QUARANTINE_COMPONENT_DIGEST_DRIFT, False, True, "destination drift", profile_id=expected_profile_id, service_name=expected_service_name, action=action, destination=expected_destination, scope_digest=expected_scope_digest, request_digest=expected_request_digest, public_payload_digest=expected_public_payload_digest, seals=seal_tuple, components=components)
        if seal.action is not action:
            return _report(SendSealDecisionKind.QUARANTINE_ACTION_DRIFT, False, True, "action drift", profile_id=expected_profile_id, service_name=expected_service_name, action=action, destination=expected_destination, scope_digest=expected_scope_digest, request_digest=expected_request_digest, public_payload_digest=expected_public_payload_digest, seals=seal_tuple, components=components)
        if seal.scope_digest != expected_scope_digest:
            return _report(SendSealDecisionKind.QUARANTINE_SCOPE_DRIFT, False, True, "scope drift", profile_id=expected_profile_id, service_name=expected_service_name, action=action, destination=expected_destination, scope_digest=expected_scope_digest, request_digest=expected_request_digest, public_payload_digest=expected_public_payload_digest, seals=seal_tuple, components=components)
        if seal.request_digest != expected_request_digest:
            return _report(SendSealDecisionKind.QUARANTINE_REQUEST_DRIFT, False, True, "request drift", profile_id=expected_profile_id, service_name=expected_service_name, action=action, destination=expected_destination, scope_digest=expected_scope_digest, request_digest=expected_request_digest, public_payload_digest=expected_public_payload_digest, seals=seal_tuple, components=components)
        if seal.public_payload_digest != expected_public_payload_digest:
            return _report(SendSealDecisionKind.QUARANTINE_PAYLOAD_DRIFT, False, True, "payload drift", profile_id=expected_profile_id, service_name=expected_service_name, action=action, destination=expected_destination, scope_digest=expected_scope_digest, request_digest=expected_request_digest, public_payload_digest=expected_public_payload_digest, seals=seal_tuple, components=components)
        if seal.commit_report_digest != components[0] or seal.outbox_drain_digest != components[1] or seal.sam_canary_digest != components[2] or seal.compact_join_digest != components[3]:
            return _report(SendSealDecisionKind.QUARANTINE_COMPONENT_DIGEST_DRIFT, False, True, "component digest drift", profile_id=expected_profile_id, service_name=expected_service_name, action=action, destination=expected_destination, scope_digest=expected_scope_digest, request_digest=expected_request_digest, public_payload_digest=expected_public_payload_digest, seals=seal_tuple, components=components)
        if expected_idempotency_key is not None and seal.idempotency_key != expected_idempotency_key:
            return _report(SendSealDecisionKind.QUARANTINE_IDEMPOTENCY_CONFLICT, False, True, "idempotency drift", profile_id=expected_profile_id, service_name=expected_service_name, action=action, destination=expected_destination, scope_digest=expected_scope_digest, request_digest=expected_request_digest, public_payload_digest=expected_public_payload_digest, seals=seal_tuple, components=components)
        if expected_public_effect_digest is not None and seal.public_effect_digest != expected_public_effect_digest:
            return _report(SendSealDecisionKind.QUARANTINE_EFFECT_CONFLICT, False, True, "effect drift", profile_id=expected_profile_id, service_name=expected_service_name, action=action, destination=expected_destination, scope_digest=expected_scope_digest, request_digest=expected_request_digest, public_payload_digest=expected_public_payload_digest, seals=seal_tuple, components=components)
        committed = (committed_idempotency_effects or {}).get(seal.idempotency_key)
        if committed is not None:
            if committed == seal.public_effect_digest:
                return _report(SendSealDecisionKind.ACCEPT_IDEMPOTENT_REPLAY, True, watch_debt, "known idempotent send seal replay", profile_id=expected_profile_id, service_name=expected_service_name, action=action, destination=expected_destination, scope_digest=expected_scope_digest, request_digest=expected_request_digest, public_payload_digest=expected_public_payload_digest, seals=seal_tuple, selected=seal, components=components)
            return _report(SendSealDecisionKind.QUARANTINE_IDEMPOTENCY_CONFLICT, False, True, "same idempotency key maps to different effect", profile_id=expected_profile_id, service_name=expected_service_name, action=action, destination=expected_destination, scope_digest=expected_scope_digest, request_digest=expected_request_digest, public_payload_digest=expected_public_payload_digest, seals=seal_tuple, components=components)
        live.append(seal)
    if len({seal.family_id for seal in live}) < min_family_diversity:
        return _report(SendSealDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, "send seal family diversity too low", profile_id=expected_profile_id, service_name=expected_service_name, action=action, destination=expected_destination, scope_digest=expected_scope_digest, request_digest=expected_request_digest, public_payload_digest=expected_public_payload_digest, seals=live, components=components)
    if len({seal.path_family for seal in live}) < min_path_diversity:
        return _report(SendSealDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, "send seal path diversity too low", profile_id=expected_profile_id, service_name=expected_service_name, action=action, destination=expected_destination, scope_digest=expected_scope_digest, request_digest=expected_request_digest, public_payload_digest=expected_public_payload_digest, seals=live, components=components)
    selected = max(live, key=lambda item: (item.sequence, item.seal_digest))
    return _report(SendSealDecisionKind.ACCEPT_WITH_WATCH if watch_debt else SendSealDecisionKind.ACCEPT_SEND_SEAL, True, watch_debt, "send seal components bind at exact public edge", profile_id=expected_profile_id, service_name=expected_service_name, action=action, destination=expected_destination, scope_digest=expected_scope_digest, request_digest=expected_request_digest, public_payload_digest=expected_public_payload_digest, seals=live, selected=selected, components=components)
