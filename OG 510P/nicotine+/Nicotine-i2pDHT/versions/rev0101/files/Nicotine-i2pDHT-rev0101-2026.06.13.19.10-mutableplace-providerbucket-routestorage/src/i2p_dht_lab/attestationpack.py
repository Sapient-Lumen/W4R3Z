"""Signed attestation packs for post-reconcile exact-boundary evidence.

rev0058 keeps component reports from becoming an implicit oracle.  A pack is a
small, signed, local bundle of typed report digests.  It can make repeated
restart/recovery decisions easier to carry, but it is not DHT truth and it does
not replace validation of the underlying components.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Any, Iterable

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectAction

ATTESTATION_PACK_DOMAIN = DOMAIN + b":attestation-pack-v1:"


class AttestationRole(str, Enum):
    EFFECT_RECONCILE = "effect_reconcile"
    DEAD_LETTER = "dead_letter"
    RETRY_QUORUM = "retry_quorum"
    RECOVERY_MESH = "recovery_mesh"
    SIDE_EFFECT_JOURNAL = "side_effect_journal"
    SETTLEMENT = "settlement"
    TOMBSTONE = "tombstone"
    REDRESS = "redress"
    AUDIT_QUORUM = "audit_quorum"


class AttestationPackDecisionKind(str, Enum):
    ACCEPT_PACK = "accept_pack"
    ACCEPT_WITH_WATCH = "accept_with_watch"
    EMPTY_NO_COMPONENTS = "empty_no_components"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    HOLD_MISSING_REQUIRED_ROLE = "hold_missing_required_role"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_EXPIRED_OR_FUTURE = "quarantine_expired_or_future"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_BOUNDARY_DRIFT = "quarantine_boundary_drift"
    QUARANTINE_DUPLICATE_ROLE = "quarantine_duplicate_role"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"


@dataclass(frozen=True)
class AttestationComponent:
    role: AttestationRole
    component_digest: bytes
    component_decision: str
    accepted: bool
    watch: bool
    hard_negative_count: int = 0

    def __post_init__(self) -> None:
        object.__setattr__(self, "role", AttestationRole(self.role))
        if len(self.component_digest) != 32:
            raise ValueError("component_digest must be 32 bytes")
        if not self.component_decision:
            raise ValueError("component_decision must not be empty")
        if self.hard_negative_count < 0:
            raise ValueError("hard_negative_count must be non-negative")

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"role": self.role.value,
            b"digest": self.component_digest,
            b"decision": self.component_decision,
            b"accepted": 1 if self.accepted else 0,
            b"watch": 1 if self.watch else 0,
            b"hard": self.hard_negative_count,
        }


@dataclass(frozen=True)
class AttestationPack:
    action: SideEffectAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    components: tuple[AttestationComponent, ...]
    sequence: int
    previous_pack_digest: bytes
    issued_at: int
    expires_at: int
    family_id: str
    path_family: str
    signer_public_key: bytes
    signature: bytes = b""

    def __post_init__(self) -> None:
        object.__setattr__(self, "action", SideEffectAction(self.action))
        object.__setattr__(self, "components", tuple(self.components))
        if not self.profile_id or not self.service_name or not self.family_id or not self.path_family:
            raise ValueError("attestation pack needs profile/service/family/path")
        if min(self.sequence, self.issued_at, self.expires_at) < 0:
            raise ValueError("attestation sequence/time must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("attestation expires_at must follow issued_at")
        for name, value in (
            ("scope_digest", self.scope_digest),
            ("request_digest", self.request_digest),
            ("payload_digest", self.payload_digest),
            ("idempotency_key", self.idempotency_key),
            ("previous_pack_digest", self.previous_pack_digest),
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
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"payload": self.payload_digest,
            b"idem": self.idempotency_key,
            b"components": [component.bvalue() for component in self.components],
            b"seq": self.sequence,
            b"prev": self.previous_pack_digest,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"family": self.family_id,
            b"path_family": self.path_family,
            b"signer": self.signer_public_key,
        }

    def signature_payload(self) -> bytes:
        return ATTESTATION_PACK_DOMAIN + b":pack-sig:" + bencode(self.unsigned_bvalue())

    @property
    def pack_core_digest(self) -> bytes:
        return sha256(ATTESTATION_PACK_DOMAIN + b":pack-core:" + bencode(self.unsigned_bvalue()))

    @property
    def pack_digest(self) -> bytes:
        return sha256(ATTESTATION_PACK_DOMAIN + b":pack-digest:" + self.signature_payload() + self.signature)

    def verifies(self) -> bool:
        return verify_signature(self.signer_public_key, self.signature_payload(), self.signature)

    def live(self, now: int) -> bool:
        return self.issued_at <= now < self.expires_at


@dataclass(frozen=True)
class AttestationPackReport:
    decision_kind: AttestationPackDecisionKind
    accept: bool
    watch: bool
    reason: str
    action: SideEffectAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    accepted_pack_digest: bytes
    pack_digests: tuple[bytes, ...]
    role_digests: tuple[tuple[AttestationRole, bytes], ...]
    highest_sequence: int
    family_count: int
    path_family_count: int
    hard_negative_count: int
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _digest(report: Any) -> bytes:
    for attr in ("report_digest", "pack_digest", "entry_digest", "vote_digest", "seal_digest"):
        value = getattr(report, attr, None)
        if isinstance(value, bytes) and len(value) == 32:
            return value
    raise ValueError("component lacks a digest field")


def component_from_report(role: AttestationRole, report: Any) -> AttestationComponent:
    decision = getattr(getattr(report, "decision_kind", None), "value", None) or str(getattr(report, "decision_kind", "unknown"))
    return AttestationComponent(
        role=role,
        component_digest=_digest(report),
        component_decision=decision,
        accepted=bool(getattr(report, "accept", False)),
        watch=bool(getattr(report, "watch", False)),
        hard_negative_count=int(getattr(report, "hard_negative_count", 0) or 0),
    )


def make_attestation_pack(
    *,
    keypair: DhtKeypair,
    action: SideEffectAction,
    profile_id: str,
    service_name: str,
    scope_digest: bytes,
    request_digest: bytes,
    payload_digest: bytes,
    idempotency_key: bytes,
    components: Iterable[AttestationComponent],
    sequence: int,
    previous_pack_digest: bytes = ZERO_DIGEST,
    issued_at: int,
    expires_at: int,
    family_id: str,
    path_family: str,
) -> AttestationPack:
    unsigned = AttestationPack(
        action=action,
        profile_id=profile_id,
        service_name=service_name,
        scope_digest=scope_digest,
        request_digest=request_digest,
        payload_digest=payload_digest,
        idempotency_key=idempotency_key,
        components=tuple(components),
        sequence=sequence,
        previous_pack_digest=previous_pack_digest,
        issued_at=issued_at,
        expires_at=expires_at,
        family_id=family_id,
        path_family=path_family,
        signer_public_key=keypair.public_key_bytes,
    )
    return replace(unsigned, signature=keypair.sign(unsigned.signature_payload()))


def assess_attestation_packs(
    packs: Iterable[AttestationPack],
    *,
    action: SideEffectAction,
    profile_id: str,
    service_name: str,
    scope_digest: bytes,
    request_digest: bytes,
    payload_digest: bytes,
    idempotency_key: bytes,
    now: int,
    required_roles: Iterable[AttestationRole] = (),
    expected_role_digests: dict[AttestationRole, bytes] | None = None,
    previous_highest_sequence: int = -1,
    previous_seen_pack_digests: Iterable[bytes] = (),
    min_family_count: int = 2,
    min_path_family_count: int = 2,
    allow_watch: bool = True,
) -> AttestationPackReport:
    pack_tuple = tuple(packs)
    expected_role_digests = expected_role_digests or {}
    seen = set(previous_seen_pack_digests)
    common = dict(action=SideEffectAction(action), profile_id=profile_id, service_name=service_name, scope_digest=scope_digest, request_digest=request_digest, payload_digest=payload_digest, idempotency_key=idempotency_key)
    if not pack_tuple:
        return _report(AttestationPackDecisionKind.EMPTY_NO_COMPONENTS, False, True, "no attestation packs", accepted_pack_digest=ZERO_DIGEST, pack_digests=(), role_digests=(), highest_sequence=previous_highest_sequence, family_count=0, path_family_count=0, hard_negative_count=0, **common)
    valid: list[AttestationPack] = []
    for pack in pack_tuple:
        if not pack.verifies():
            return _pack_report(AttestationPackDecisionKind.QUARANTINE_BAD_SIGNATURE, False, False, "bad pack signature", pack_tuple, valid, **common)
        if not pack.live(now):
            return _pack_report(AttestationPackDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, False, False, "pack expired or from future", pack_tuple, valid, **common)
        if pack.pack_digest in seen:
            return _pack_report(AttestationPackDecisionKind.QUARANTINE_REPLAY, False, False, "pack replay", pack_tuple, valid, **common)
        if pack.sequence <= previous_highest_sequence:
            return _pack_report(AttestationPackDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, False, "pack sequence rollback", pack_tuple, valid, **common)
        if pack.action is not SideEffectAction(action) or pack.profile_id != profile_id or pack.service_name != service_name:
            return _pack_report(AttestationPackDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, "action/profile/service drift", pack_tuple, valid, **common)
        if pack.scope_digest != scope_digest or pack.request_digest != request_digest or pack.payload_digest != payload_digest or pack.idempotency_key != idempotency_key:
            return _pack_report(AttestationPackDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, "scope/request/payload/idempotency drift", pack_tuple, valid, **common)
        valid.append(pack)
    by_sequence: dict[int, bytes] = {}
    ordered = sorted(valid, key=lambda p: p.sequence)
    for pack in ordered:
        core = pack.pack_core_digest
        prior = by_sequence.get(pack.sequence)
        if prior is not None and prior != core:
            return _pack_report(AttestationPackDecisionKind.QUARANTINE_SEQUENCE_FORK, False, False, "same-sequence pack fork", pack_tuple, valid, **common)
        by_sequence[pack.sequence] = core
    for prev, nxt in zip(ordered, ordered[1:]):
        if nxt.previous_pack_digest != prev.pack_digest:
            return _pack_report(AttestationPackDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, False, "pack previous-link mismatch", pack_tuple, valid, **common)
    role_map: dict[AttestationRole, bytes] = {}
    hard = 0
    watch = False
    for pack in ordered:
        local_roles: set[AttestationRole] = set()
        for component in pack.components:
            if component.role in local_roles:
                return _pack_report(AttestationPackDecisionKind.QUARANTINE_DUPLICATE_ROLE, False, False, "duplicate role inside pack", pack_tuple, valid, **common)
            local_roles.add(component.role)
            expected = expected_role_digests.get(component.role)
            if expected is not None and component.component_digest != expected:
                return _pack_report(AttestationPackDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, "expected role digest drift", pack_tuple, valid, **common)
            prior = role_map.get(component.role)
            if prior is not None and prior != component.component_digest:
                return _pack_report(AttestationPackDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, "role digest disagrees across packs", pack_tuple, valid, **common)
            role_map[component.role] = component.component_digest
            hard += component.hard_negative_count
            watch = watch or component.watch or not component.accepted
    if hard:
        return _pack_report(AttestationPackDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, "hard negatives in attestation pack", pack_tuple, valid, hard_negative_count=hard, **common)
    missing = set(AttestationRole(role) for role in required_roles) - set(role_map)
    if missing:
        return _pack_report(AttestationPackDecisionKind.HOLD_MISSING_REQUIRED_ROLE, False, True, "missing required attestation role", pack_tuple, valid, **common)
    families = {pack.family_id for pack in valid}
    paths = {pack.path_family for pack in valid}
    if len(families) < min_family_count:
        return _pack_report(AttestationPackDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, "low attestation family diversity", pack_tuple, valid, **common)
    if len(paths) < min_path_family_count:
        return _pack_report(AttestationPackDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, "low attestation path diversity", pack_tuple, valid, **common)
    kind = AttestationPackDecisionKind.ACCEPT_WITH_WATCH if watch and allow_watch else AttestationPackDecisionKind.ACCEPT_PACK
    return _pack_report(kind, True, watch, "attestation pack accepted", pack_tuple, valid, hard_negative_count=hard, **common)


def _pack_report(kind: AttestationPackDecisionKind, accept: bool, watch: bool, reason: str, all_packs: tuple[AttestationPack, ...], valid: list[AttestationPack], *, action: SideEffectAction, profile_id: str, service_name: str, scope_digest: bytes, request_digest: bytes, payload_digest: bytes, idempotency_key: bytes, hard_negative_count: int = 0) -> AttestationPackReport:
    pack_digests = tuple(pack.pack_digest for pack in valid)
    role_pairs: list[tuple[AttestationRole, bytes]] = []
    for pack in valid:
        role_pairs.extend((component.role, component.component_digest) for component in pack.components)
    highest = max((pack.sequence for pack in valid), default=-1)
    accepted = pack_digests[-1] if pack_digests and accept else ZERO_DIGEST
    return _report(kind, accept, watch, reason, action=action, profile_id=profile_id, service_name=service_name, scope_digest=scope_digest, request_digest=request_digest, payload_digest=payload_digest, idempotency_key=idempotency_key, accepted_pack_digest=accepted, pack_digests=pack_digests, role_digests=tuple(role_pairs), highest_sequence=highest, family_count=len({p.family_id for p in valid}), path_family_count=len({p.path_family for p in valid}), hard_negative_count=hard_negative_count)


def _report(kind: AttestationPackDecisionKind, accept: bool, watch: bool, reason: str, *, action: SideEffectAction, profile_id: str, service_name: str, scope_digest: bytes, request_digest: bytes, payload_digest: bytes, idempotency_key: bytes, accepted_pack_digest: bytes, pack_digests: tuple[bytes, ...], role_digests: tuple[tuple[AttestationRole, bytes], ...], highest_sequence: int, family_count: int, path_family_count: int, hard_negative_count: int) -> AttestationPackReport:
    body = {
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"reason": reason,
        b"action": SideEffectAction(action).value,
        b"profile": profile_id,
        b"service": service_name,
        b"scope": scope_digest,
        b"request": request_digest,
        b"payload": payload_digest,
        b"idem": idempotency_key,
        b"accepted": accepted_pack_digest,
        b"packs": list(pack_digests),
        b"roles": [{b"role": role.value, b"digest": digest} for role, digest in role_digests],
        b"highest": highest_sequence,
        b"families": family_count,
        b"paths": path_family_count,
        b"hard": hard_negative_count,
    }
    return AttestationPackReport(kind, accept, watch, reason, SideEffectAction(action), profile_id, service_name, scope_digest, request_digest, payload_digest, idempotency_key, accepted_pack_digest, pack_digests, role_digests, highest_sequence, family_count, path_family_count, hard_negative_count, sha256(ATTESTATION_PACK_DOMAIN + b":report:" + bencode(body)))
