"""Mutable namespace registry pressure for a generic I2P DHT.

A consumer-agnostic DHT cannot hard-code one application's record validators.
It also cannot let arbitrary payloads self-declare a namespace and dispatch into
handlers.  This module models a tiny signed namespace registry: each namespace
has an authority key, a monotonic policy sequence, allowed wire kinds, payload
roles, TTL/size caps, and required flags.

This is not global governance.  A node chooses which registry snapshots to load.
The registry merely prevents local handler dispatch from accepting untyped or
scope-confused records because a signature happened to verify.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable, Mapping

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .validatorwall import PayloadEnvelope, PayloadRole, ValidatorWallPolicy, validate_payload_wall
from .wirecanon import WireFrame, WireMessageKind

NAMESPACE_REGISTRY_DOMAIN = DOMAIN + b":namespace-registry-v1:"


class NamespaceDecisionKind(str, Enum):
    ACCEPT_NAMESPACE = "accept_namespace"
    REJECT_UNKNOWN_NAMESPACE = "reject_unknown_namespace"
    REJECT_BAD_SIGNATURE = "reject_bad_signature"
    REJECT_TIME_WINDOW = "reject_time_window"
    REJECT_ROLLBACK = "reject_rollback"
    QUARANTINE_SAME_SEQUENCE_FORK = "quarantine_same_sequence_fork"
    REJECT_KIND_ROLE = "reject_kind_role"
    REJECT_TTL_OR_SIZE = "reject_ttl_or_size"
    REJECT_SCOPE_PREFIX = "reject_scope_prefix"
    REJECT_VALIDATOR_WALL = "reject_validator_wall"


@dataclass(frozen=True)
class NamespacePolicy:
    namespace: str
    authority_public_key: bytes
    sequence: int
    issued_at: int
    expires_at: int
    allowed_roles_by_kind: Mapping[WireMessageKind, frozenset[PayloadRole]]
    max_body_bytes: int = 64_000
    max_ttl_seconds: int = 3600
    required_flags_by_role: Mapping[PayloadRole, frozenset[str]] | None = None
    scope_prefixes: tuple[bytes, ...] = ()
    signature: bytes = b""

    def __post_init__(self) -> None:
        if not self.namespace:
            raise ValueError("namespace must not be empty")
        if len(self.authority_public_key) != 32:
            raise ValueError("namespace authority public key must be 32 bytes")
        if self.sequence < 0 or self.expires_at <= self.issued_at or self.max_body_bytes <= 0 or self.max_ttl_seconds <= 0:
            raise ValueError("namespace policy counters invalid")
        if self.required_flags_by_role is None:
            object.__setattr__(self, "required_flags_by_role", {})
        for prefix in self.scope_prefixes:
            if len(prefix) > 32:
                raise ValueError("scope prefixes must be at most 32 bytes")

    @classmethod
    def create(
        cls,
        *,
        authority: DhtKeypair,
        namespace: str,
        sequence: int,
        issued_at: int,
        ttl: int,
        allowed_roles_by_kind: Mapping[WireMessageKind, frozenset[PayloadRole]],
        max_body_bytes: int = 64_000,
        max_ttl_seconds: int = 3600,
        required_flags_by_role: Mapping[PayloadRole, frozenset[str]] | None = None,
        scope_prefixes: tuple[bytes, ...] = (),
    ) -> "NamespacePolicy":
        if ttl <= 0:
            raise ValueError("namespace policy ttl must be positive")
        unsigned = cls(namespace=namespace, authority_public_key=authority.public_key_bytes, sequence=sequence, issued_at=issued_at, expires_at=issued_at + ttl, allowed_roles_by_kind=dict(allowed_roles_by_kind), max_body_bytes=max_body_bytes, max_ttl_seconds=max_ttl_seconds, required_flags_by_role=required_flags_by_role, scope_prefixes=scope_prefixes)
        return replace(unsigned, signature=authority.sign(unsigned.unsigned_payload()))

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        roles_by_kind = []
        for kind, roles in sorted(self.allowed_roles_by_kind.items(), key=lambda item: item[0].value):
            roles_by_kind.append({b"kind": kind.value, b"roles": sorted(role.value for role in roles)})
        flags = []
        for role, role_flags in sorted((self.required_flags_by_role or {}).items(), key=lambda item: item[0].value):
            flags.append({b"role": role.value, b"flags": sorted(role_flags)})
        return {
            b"namespace": self.namespace,
            b"authority_public_key": self.authority_public_key,
            b"sequence": self.sequence,
            b"issued_at": self.issued_at,
            b"expires_at": self.expires_at,
            b"allowed_roles_by_kind": roles_by_kind,
            b"max_body_bytes": self.max_body_bytes,
            b"max_ttl_seconds": self.max_ttl_seconds,
            b"required_flags_by_role": flags,
            b"scope_prefixes": list(self.scope_prefixes),
        }

    def unsigned_payload(self) -> bytes:
        return NAMESPACE_REGISTRY_DOMAIN + b":policy-unsigned:" + bencode(self.unsigned_bvalue())

    @property
    def policy_digest(self) -> bytes:
        return sha256(NAMESPACE_REGISTRY_DOMAIN + b":policy:" + self.unsigned_payload() + self.signature)

    def signature_valid(self) -> bool:
        return verify_signature(self.authority_public_key, self.unsigned_payload(), self.signature)

    def live(self, *, now: int, max_future_skew: int = 300) -> bool:
        return self.issued_at - max_future_skew <= now < self.expires_at + max_future_skew

    def wall_policy(self) -> ValidatorWallPolicy:
        return ValidatorWallPolicy(allowed_namespaces=frozenset({self.namespace}), roles_by_kind=self.allowed_roles_by_kind, required_flags_by_role=self.required_flags_by_role or {}, max_body_bytes=self.max_body_bytes)

    def allows_scope(self, scope_id: bytes) -> bool:
        if not self.scope_prefixes:
            return True
        return any(scope_id.startswith(prefix) for prefix in self.scope_prefixes)


@dataclass(frozen=True)
class NamespaceMemory:
    highest_sequence: Mapping[str, int]
    seen_digests_by_seq: Mapping[tuple[str, int], frozenset[bytes]]

    @classmethod
    def empty(cls) -> "NamespaceMemory":
        return cls(highest_sequence={}, seen_digests_by_seq={})


@dataclass(frozen=True)
class NamespaceRegistry:
    policies: tuple[NamespacePolicy, ...]
    memory: NamespaceMemory = NamespaceMemory.empty()

    def best_policy(self, namespace: str) -> NamespacePolicy | None:
        candidates = [policy for policy in self.policies if policy.namespace == namespace]
        if not candidates:
            return None
        return sorted(candidates, key=lambda p: (p.sequence, p.policy_digest), reverse=True)[0]

    def detect_policy_pressure(self, policy: NamespacePolicy) -> NamespaceDecisionKind | None:
        highest = self.memory.highest_sequence.get(policy.namespace, -1)
        if policy.sequence < highest:
            return NamespaceDecisionKind.REJECT_ROLLBACK
        digests = set(self.memory.seen_digests_by_seq.get((policy.namespace, policy.sequence), frozenset()))
        if digests and policy.policy_digest not in digests:
            return NamespaceDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK
        return None


@dataclass(frozen=True)
class NamespaceDecision:
    kind: NamespaceDecisionKind
    accept: bool
    reason: str


@dataclass(frozen=True)
class NamespaceDispatchReport:
    decision: NamespaceDecision
    policy: NamespacePolicy | None
    envelope: PayloadEnvelope | None
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision.kind.value.startswith("quarantine_")


def _report(decision: NamespaceDecision, *, policy: NamespacePolicy | None, envelope: PayloadEnvelope | None, frame: WireFrame) -> NamespaceDispatchReport:
    digest = sha256(NAMESPACE_REGISTRY_DOMAIN + b":dispatch-report:" + bencode({
        b"decision": decision.kind.value,
        b"policy": b"" if policy is None else policy.policy_digest,
        b"envelope": b"" if envelope is None else envelope.object_digest,
        b"frame": frame.frame_digest,
    }))
    return NamespaceDispatchReport(decision, policy, envelope, digest)


def validate_namespace_dispatch(registry: NamespaceRegistry, frame: WireFrame, *, payload: bytes, body: bytes, now: int, expected_scope_id: bytes | None = None) -> NamespaceDispatchReport:
    try:
        envelope = PayloadEnvelope.from_bytes(payload)
    except Exception:
        return _report(NamespaceDecision(NamespaceDecisionKind.REJECT_VALIDATOR_WALL, False, "payload envelope could not be parsed before namespace dispatch"), policy=None, envelope=None, frame=frame)
    policy = registry.best_policy(envelope.namespace)
    if policy is None:
        return _report(NamespaceDecision(NamespaceDecisionKind.REJECT_UNKNOWN_NAMESPACE, False, "namespace has no loaded local policy"), policy=None, envelope=envelope, frame=frame)
    pressure = registry.detect_policy_pressure(policy)
    if pressure is not None:
        return _report(NamespaceDecision(pressure, False, "namespace policy conflicts with local monotonic memory"), policy=policy, envelope=envelope, frame=frame)
    if not policy.signature_valid():
        return _report(NamespaceDecision(NamespaceDecisionKind.REJECT_BAD_SIGNATURE, False, "namespace policy signature is invalid"), policy=policy, envelope=envelope, frame=frame)
    if not policy.live(now=now):
        return _report(NamespaceDecision(NamespaceDecisionKind.REJECT_TIME_WINDOW, False, "namespace policy is outside its validity window"), policy=policy, envelope=envelope, frame=frame)
    if envelope.expires_at - envelope.issued_at > policy.max_ttl_seconds or envelope.body_size > policy.max_body_bytes:
        return _report(NamespaceDecision(NamespaceDecisionKind.REJECT_TTL_OR_SIZE, False, "payload ttl or size exceeds namespace policy"), policy=policy, envelope=envelope, frame=frame)
    if not policy.allows_scope(envelope.scope_id):
        return _report(NamespaceDecision(NamespaceDecisionKind.REJECT_SCOPE_PREFIX, False, "payload scope does not match namespace prefix constraints"), policy=policy, envelope=envelope, frame=frame)
    if envelope.role not in policy.allowed_roles_by_kind.get(frame.message_kind, frozenset()):
        return _report(NamespaceDecision(NamespaceDecisionKind.REJECT_KIND_ROLE, False, "wire kind and payload role not allowed by namespace policy"), policy=policy, envelope=envelope, frame=frame)
    wall = validate_payload_wall(frame, payload=payload, body=body, now=now, expected_scope_id=expected_scope_id, policy=policy.wall_policy())
    if not wall.decision.accept:
        return _report(NamespaceDecision(NamespaceDecisionKind.REJECT_VALIDATOR_WALL, False, wall.decision.reason), policy=policy, envelope=envelope, frame=frame)
    return _report(NamespaceDecision(NamespaceDecisionKind.ACCEPT_NAMESPACE, True, "namespace policy and validator wall agree"), policy=policy, envelope=envelope, frame=frame)


def memory_from_policies(policies: Iterable[NamespacePolicy]) -> NamespaceMemory:
    highest: dict[str, int] = {}
    seen: dict[tuple[str, int], set[bytes]] = {}
    for policy in policies:
        highest[policy.namespace] = max(highest.get(policy.namespace, -1), policy.sequence)
        seen.setdefault((policy.namespace, policy.sequence), set()).add(policy.policy_digest)
    return NamespaceMemory(highest_sequence=highest, seen_digests_by_seq={key: frozenset(value) for key, value in seen.items()})
