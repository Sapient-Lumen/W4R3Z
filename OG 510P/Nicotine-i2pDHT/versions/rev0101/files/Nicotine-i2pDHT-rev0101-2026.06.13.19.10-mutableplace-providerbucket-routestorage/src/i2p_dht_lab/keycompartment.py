"""Key-compartment pressure for a DHT above I2P.

rev0043 moves one layer beneath operator and service lifecycle: the same public
key should not silently become transport identity, operator authority, service
signer, mutable publisher, witness signer, and ticket minter.  This module does
not handle private keys.  It models signed public-key binding capsules and local
acceptance pressure around role separation, scope binding, replay, rollback,
family diversity, and crisis notices.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256

KEY_COMPARTMENT_DOMAIN = DOMAIN + b":key-compartment-v1:"
ZERO_DIGEST = b"\x00" * 32


class KeyRole(str, Enum):
    ROOT = "root"
    OPERATOR = "operator"
    ROUTER_DESTINATION = "router_destination"
    DHT_NODE = "dht_node"
    SERVICE_SIGNER = "service_signer"
    GARDEN_TICKET = "garden_ticket"
    WITNESS_SIGNER = "witness_signer"
    MUTABLE_PUBLISHER = "mutable_publisher"
    METRICS_SIGNER = "metrics_signer"


class CompartmentDecisionKind(str, Enum):
    ACCEPT_COMPARTMENTED_KEY = "accept_compartmented_key"
    HOLD_MISSING_BINDING = "hold_missing_binding"
    HOLD_NEEDS_FAMILY_DIVERSITY = "hold_needs_family_diversity"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_EXPIRED_OR_FUTURE = "quarantine_expired_or_future"
    QUARANTINE_PROFILE_DRIFT = "quarantine_profile_drift"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_ROLLBACK = "quarantine_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_ROLE_REUSE = "quarantine_role_reuse"
    QUARANTINE_FORBIDDEN_KEY = "quarantine_forbidden_key"
    QUARANTINE_KEY_CRISIS = "quarantine_key_crisis"
    QUARANTINE_PREVIOUS_LINK = "quarantine_previous_link"


# These are deliberately conservative for future DHT/garden control lanes.  A
# caller can explicitly allow a pair only inside a binding capsule, but the
# default stance treats dual use as a local quarantine condition.
INCOMPATIBLE_ROLE_PAIRS: frozenset[frozenset[KeyRole]] = frozenset({
    frozenset((KeyRole.ROOT, KeyRole.ROUTER_DESTINATION)),
    frozenset((KeyRole.ROOT, KeyRole.SERVICE_SIGNER)),
    frozenset((KeyRole.OPERATOR, KeyRole.ROUTER_DESTINATION)),
    frozenset((KeyRole.OPERATOR, KeyRole.SERVICE_SIGNER)),
    frozenset((KeyRole.OPERATOR, KeyRole.GARDEN_TICKET)),
    frozenset((KeyRole.OPERATOR, KeyRole.WITNESS_SIGNER)),
    frozenset((KeyRole.OPERATOR, KeyRole.MUTABLE_PUBLISHER)),
    frozenset((KeyRole.ROUTER_DESTINATION, KeyRole.SERVICE_SIGNER)),
    frozenset((KeyRole.ROUTER_DESTINATION, KeyRole.WITNESS_SIGNER)),
    frozenset((KeyRole.ROUTER_DESTINATION, KeyRole.MUTABLE_PUBLISHER)),
    frozenset((KeyRole.WITNESS_SIGNER, KeyRole.MUTABLE_PUBLISHER)),
    frozenset((KeyRole.METRICS_SIGNER, KeyRole.MUTABLE_PUBLISHER)),
})


def key_fingerprint(public_key: bytes) -> bytes:
    if len(public_key) != 32:
        raise ValueError("public key must be 32 bytes")
    return sha256(KEY_COMPARTMENT_DOMAIN + b":fingerprint:" + public_key)


def roles_are_compatible(left: KeyRole, right: KeyRole, allowed_dual_use: Iterable[tuple[KeyRole, KeyRole]] = ()) -> bool:
    if left is right:
        return True
    pair = frozenset((left, right))
    allowed = {frozenset(item) for item in allowed_dual_use}
    return pair not in INCOMPATIBLE_ROLE_PAIRS or pair in allowed


@dataclass(frozen=True)
class KeyBindingCapsule:
    profile_id: str
    role: KeyRole
    bound_public_key: bytes
    scope_digest: bytes
    sequence: int
    previous_binding_digest: bytes
    issued_at: int
    expires_at: int
    signer_public_key: bytes
    family_id: str
    allowed_dual_roles: tuple[KeyRole, ...] = ()
    root_binding_digest: bytes = ZERO_DIGEST
    operator_notice_digest: bytes = ZERO_DIGEST
    signature: bytes = b""

    def __post_init__(self) -> None:
        if not self.profile_id or len(self.profile_id.encode("utf-8")) > 80:
            raise ValueError("profile_id must be short and non-empty")
        if len(self.bound_public_key) != 32 or len(self.signer_public_key) != 32:
            raise ValueError("public keys must be 32 bytes")
        for name, value in (("scope_digest", self.scope_digest), ("previous_binding_digest", self.previous_binding_digest), ("root_binding_digest", self.root_binding_digest), ("operator_notice_digest", self.operator_notice_digest)):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if self.sequence < 0:
            raise ValueError("sequence must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("expires_at must be greater than issued_at")
        if not self.family_id:
            raise ValueError("family_id must be non-empty")
        normalized = tuple(KeyRole(item) for item in self.allowed_dual_roles)
        object.__setattr__(self, "allowed_dual_roles", normalized)

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"profile": self.profile_id,
            b"role": self.role.value,
            b"bound": self.bound_public_key,
            b"scope": self.scope_digest,
            b"seq": self.sequence,
            b"prev": self.previous_binding_digest,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"signer": self.signer_public_key,
            b"family": self.family_id,
            b"allowed_dual": [role.value for role in self.allowed_dual_roles],
            b"root": self.root_binding_digest,
            b"operator_notice": self.operator_notice_digest,
        }

    def payload(self) -> bytes:
        return KEY_COMPARTMENT_DOMAIN + b":binding:" + bencode(self.unsigned_bvalue())

    @property
    def binding_digest(self) -> bytes:
        return sha256(KEY_COMPARTMENT_DOMAIN + b":binding-digest:" + self.payload() + self.signature)

    @property
    def key_digest(self) -> bytes:
        return key_fingerprint(self.bound_public_key)

    def verify(self) -> bool:
        return verify_signature(self.signer_public_key, self.payload(), self.signature)

    def with_signature(self, signature: bytes) -> "KeyBindingCapsule":
        return replace(self, signature=signature)


@dataclass(frozen=True)
class CompartmentReport:
    decision_kind: CompartmentDecisionKind
    accepted_binding_digest: bytes = ZERO_DIGEST
    accepted_key_digest: bytes = ZERO_DIGEST
    role: KeyRole | None = None
    reasons: tuple[str, ...] = ()
    family_count: int = 0
    highest_sequence: int = -1
    report_digest: bytes = ZERO_DIGEST


def make_key_binding_capsule(
    *,
    keypair: DhtKeypair,
    profile_id: str,
    role: KeyRole,
    bound_public_key: bytes,
    scope_digest: bytes,
    sequence: int,
    previous_binding_digest: bytes,
    issued_at: int,
    expires_at: int,
    family_id: str,
    allowed_dual_roles: Iterable[KeyRole] = (),
    root_binding_digest: bytes = ZERO_DIGEST,
    operator_notice_digest: bytes = ZERO_DIGEST,
) -> KeyBindingCapsule:
    capsule = KeyBindingCapsule(
        profile_id=profile_id,
        role=role,
        bound_public_key=bound_public_key,
        scope_digest=scope_digest,
        sequence=sequence,
        previous_binding_digest=previous_binding_digest,
        issued_at=issued_at,
        expires_at=expires_at,
        signer_public_key=keypair.public_key_bytes,
        family_id=family_id,
        allowed_dual_roles=tuple(allowed_dual_roles),
        root_binding_digest=root_binding_digest,
        operator_notice_digest=operator_notice_digest,
    )
    return capsule.with_signature(keypair.sign(capsule.payload()))


def _report(kind: CompartmentDecisionKind, *, binding: KeyBindingCapsule | None = None, role: KeyRole | None = None, reasons: Iterable[str] = (), family_count: int = 0, highest_sequence: int = -1) -> CompartmentReport:
    reasons_tuple = tuple(reasons)
    digest = sha256(KEY_COMPARTMENT_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"binding": binding.binding_digest if binding else ZERO_DIGEST,
        b"key": binding.key_digest if binding else ZERO_DIGEST,
        b"role": role.value if role else b"",
        b"reasons": list(reasons_tuple),
        b"families": family_count,
        b"highest_seq": highest_sequence,
    }))
    return CompartmentReport(kind, binding.binding_digest if binding else ZERO_DIGEST, binding.key_digest if binding else ZERO_DIGEST, role, reasons_tuple, family_count, highest_sequence, digest)


def assess_key_compartment(
    bindings: Iterable[KeyBindingCapsule],
    *,
    now: int,
    expected_profile_id: str,
    expected_scope_digest: bytes,
    requested_role: KeyRole,
    requested_public_key: bytes,
    minimum_sequence: int = 0,
    previous_binding_digest: bytes | None = None,
    min_family_diversity: int = 1,
    forbidden_key_digests: Iterable[bytes] = (),
    crisis_key_digests: Iterable[bytes] = (),
    previously_seen_binding_digests: Iterable[bytes] = (),
) -> CompartmentReport:
    if len(requested_public_key) != 32:
        raise ValueError("requested_public_key must be 32 bytes")
    forbidden = set(forbidden_key_digests)
    crisis = set(crisis_key_digests)
    seen = set(previously_seen_binding_digests)
    requested_key_digest = key_fingerprint(requested_public_key)
    if requested_key_digest in forbidden:
        return _report(CompartmentDecisionKind.QUARANTINE_FORBIDDEN_KEY, role=requested_role, reasons=("requested_key_forbidden",))
    if requested_key_digest in crisis:
        return _report(CompartmentDecisionKind.QUARANTINE_KEY_CRISIS, role=requested_role, reasons=("requested_key_in_crisis",))

    candidate_bindings: list[KeyBindingCapsule] = []
    same_key_bindings: list[KeyBindingCapsule] = []
    families: set[str] = set()
    highest_by_role_key: dict[tuple[bytes, KeyRole, int], bytes] = {}
    highest_sequence = -1

    for binding in bindings:
        if binding.binding_digest in seen:
            return _report(CompartmentDecisionKind.QUARANTINE_REPLAY, binding=binding, role=requested_role, reasons=("binding_replayed",))
        if not binding.verify():
            return _report(CompartmentDecisionKind.QUARANTINE_BAD_SIGNATURE, binding=binding, role=requested_role, reasons=("bad_signature",))
        if binding.issued_at > now or binding.expires_at <= now:
            return _report(CompartmentDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, binding=binding, role=requested_role, reasons=("expired_or_future",))
        if binding.profile_id != expected_profile_id:
            return _report(CompartmentDecisionKind.QUARANTINE_PROFILE_DRIFT, binding=binding, role=requested_role, reasons=("profile_drift",))
        if binding.scope_digest != expected_scope_digest:
            return _report(CompartmentDecisionKind.QUARANTINE_SCOPE_DRIFT, binding=binding, role=requested_role, reasons=("scope_drift",))
        if binding.key_digest in crisis:
            return _report(CompartmentDecisionKind.QUARANTINE_KEY_CRISIS, binding=binding, role=requested_role, reasons=("observed_key_in_crisis",))
        key = (binding.bound_public_key, binding.role, binding.sequence)
        other = highest_by_role_key.get(key)
        if other is not None and other != binding.binding_digest:
            return _report(CompartmentDecisionKind.QUARANTINE_SEQUENCE_FORK, binding=binding, role=requested_role, reasons=("same_sequence_different_binding",))
        highest_by_role_key[key] = binding.binding_digest
        if binding.bound_public_key == requested_public_key:
            same_key_bindings.append(binding)
            families.add(binding.family_id)
            if binding.role is requested_role:
                candidate_bindings.append(binding)
                highest_sequence = max(highest_sequence, binding.sequence)

    if not candidate_bindings:
        return _report(CompartmentDecisionKind.HOLD_MISSING_BINDING, role=requested_role, family_count=len(families), highest_sequence=highest_sequence, reasons=("no_binding_for_requested_role",))
    if highest_sequence < minimum_sequence:
        latest = max(candidate_bindings, key=lambda item: item.sequence)
        return _report(CompartmentDecisionKind.QUARANTINE_ROLLBACK, binding=latest, role=requested_role, family_count=len(families), highest_sequence=highest_sequence, reasons=("sequence_below_minimum",))
    latest_candidates = [binding for binding in candidate_bindings if binding.sequence == highest_sequence]
    if len({binding.binding_digest for binding in latest_candidates}) > 1:
        return _report(CompartmentDecisionKind.QUARANTINE_SEQUENCE_FORK, binding=latest_candidates[0], role=requested_role, family_count=len(families), highest_sequence=highest_sequence, reasons=("latest_sequence_fork",))
    latest = latest_candidates[0]
    if previous_binding_digest is not None and latest.sequence > 0 and latest.previous_binding_digest != previous_binding_digest:
        return _report(CompartmentDecisionKind.QUARANTINE_PREVIOUS_LINK, binding=latest, role=requested_role, family_count=len(families), highest_sequence=highest_sequence, reasons=("previous_link_mismatch",))
    if len(families) < min_family_diversity:
        return _report(CompartmentDecisionKind.HOLD_NEEDS_FAMILY_DIVERSITY, binding=latest, role=requested_role, family_count=len(families), highest_sequence=highest_sequence, reasons=("low_family_diversity",))

    allowed_pairs = tuple((latest.role, allowed) for allowed in latest.allowed_dual_roles)
    for other in same_key_bindings:
        if other.role is latest.role:
            continue
        if not roles_are_compatible(latest.role, other.role, allowed_pairs):
            return _report(CompartmentDecisionKind.QUARANTINE_ROLE_REUSE, binding=latest, role=requested_role, family_count=len(families), highest_sequence=highest_sequence, reasons=(f"role_reuse:{latest.role.value}+{other.role.value}",))
    return _report(CompartmentDecisionKind.ACCEPT_COMPARTMENTED_KEY, binding=latest, role=requested_role, family_count=len(families), highest_sequence=highest_sequence, reasons=("accepted",))
