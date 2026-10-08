"""Validator-root pressure for public publication namespaces.

The DHT keeps adding local validator surfaces. rev0046 adds a tiny signed root
that binds which validators are allowed to dispatch for a public bridge
publication boundary. This is not a global trust root. It is local policy memory
with rollback, fork, diversity, and scope pressure.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .ids import DOMAIN, sha256
from .identity import DhtKeypair, verify_signature

VALIDATOR_ROOT_DOMAIN = DOMAIN + b":validator-root-v1:"
ZERO_DIGEST = b"\x00" * 32


class ValidatorRootDecisionKind(str, Enum):
    ACCEPT_VALIDATOR_ROOT = "accept_validator_root"
    ACCEPT_WITH_WATCH = "accept_with_watch"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_WATCH_ROOT = "hold_watch_root"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_EXPIRED = "quarantine_expired"
    QUARANTINE_FUTURE = "quarantine_future"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_ROLLBACK = "quarantine_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_PROFILE_DRIFT = "quarantine_profile_drift"
    QUARANTINE_MISSING_REQUIRED_VALIDATOR = "quarantine_missing_required_validator"
    QUARANTINE_FORBIDDEN_VALIDATOR = "quarantine_forbidden_validator"


@dataclass(frozen=True)
class ValidatorRootCapsule:
    profile_id: str
    namespace: str
    scope_digest: bytes
    request_digest: bytes
    validators: tuple[bytes, ...]
    sequence: int
    previous_root_digest: bytes
    issued_at: int
    expires_at: int
    family_id: str
    path_family: str
    signer_public_key: bytes
    watch: bool = False
    signature: bytes = b""

    def __post_init__(self) -> None:
        if not self.profile_id or len(self.profile_id.encode("utf-8")) > 80:
            raise ValueError("profile_id must be short and non-empty")
        if not self.namespace or len(self.namespace.encode("utf-8")) > 96:
            raise ValueError("namespace must be short and non-empty")
        for name, value in (("scope_digest", self.scope_digest), ("request_digest", self.request_digest), ("previous_root_digest", self.previous_root_digest)):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if not self.validators:
            raise ValueError("validators must not be empty")
        for validator in self.validators:
            if len(validator) != 32:
                raise ValueError("validator digests must be 32 bytes")
        object.__setattr__(self, "validators", tuple(sorted(set(self.validators))))
        if len(self.signer_public_key) != 32:
            raise ValueError("signer public key must be 32 bytes")
        if self.sequence < 0:
            raise ValueError("sequence must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("expires_at must be greater than issued_at")
        if not self.family_id or not self.path_family:
            raise ValueError("family_id and path_family must be non-empty")

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"profile": self.profile_id,
            b"namespace": self.namespace,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"validators": self.validators,
            b"seq": self.sequence,
            b"prev": self.previous_root_digest,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"family": self.family_id,
            b"path_family": self.path_family,
            b"signer": self.signer_public_key,
            b"watch": 1 if self.watch else 0,
        }

    def payload(self) -> bytes:
        return VALIDATOR_ROOT_DOMAIN + b":root:" + bencode(self.unsigned_bvalue())

    @property
    def root_digest(self) -> bytes:
        return sha256(VALIDATOR_ROOT_DOMAIN + b":digest:" + self.payload() + self.signature)

    def verify(self) -> bool:
        return verify_signature(self.signer_public_key, self.payload(), self.signature)

    def with_signature(self, signature: bytes) -> "ValidatorRootCapsule":
        return replace(self, signature=signature)


@dataclass(frozen=True)
class ValidatorRootReport:
    decision_kind: ValidatorRootDecisionKind
    accepted: bool
    reason: str
    profile_id: str
    namespace: str
    scope_digest: bytes
    request_digest: bytes
    root_digests: tuple[bytes, ...]
    sequence: int
    family_count: int
    path_count: int
    watch: bool
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def make_validator_root(
    *,
    keypair: DhtKeypair,
    profile_id: str,
    namespace: str,
    scope_digest: bytes,
    request_digest: bytes,
    validators: Iterable[bytes],
    sequence: int,
    previous_root_digest: bytes = ZERO_DIGEST,
    issued_at: int,
    expires_at: int,
    family_id: str,
    path_family: str,
    watch: bool = False,
) -> ValidatorRootCapsule:
    capsule = ValidatorRootCapsule(profile_id, namespace, scope_digest, request_digest, tuple(validators), sequence, previous_root_digest, issued_at, expires_at, family_id, path_family, keypair.public_key_bytes, watch)
    return capsule.with_signature(keypair.sign(capsule.payload()))


def _report(kind: ValidatorRootDecisionKind, accepted: bool, reason: str, *, profile_id: str, namespace: str, scope_digest: bytes, request_digest: bytes, roots: tuple[ValidatorRootCapsule, ...], watch: bool = False) -> ValidatorRootReport:
    root_digests = tuple(sorted(root.root_digest for root in roots))
    families = {root.family_id for root in roots}
    paths = {root.path_family for root in roots}
    sequence = max((root.sequence for root in roots), default=0)
    digest = sha256(VALIDATOR_ROOT_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accepted": 1 if accepted else 0,
        b"reason": reason,
        b"profile": profile_id,
        b"namespace": namespace,
        b"scope": scope_digest,
        b"request": request_digest,
        b"roots": root_digests,
        b"seq": sequence,
        b"families": len(families),
        b"paths": len(paths),
        b"watch": 1 if watch else 0,
    }))
    return ValidatorRootReport(kind, accepted, reason, profile_id, namespace, scope_digest, request_digest, root_digests, sequence, len(families), len(paths), watch, digest)


def assess_validator_roots(
    roots: Iterable[ValidatorRootCapsule],
    *,
    now: int,
    expected_profile_id: str,
    expected_namespace: str,
    expected_scope_digest: bytes,
    expected_request_digest: bytes,
    required_validator_digests: Iterable[bytes] = (),
    forbidden_validator_digests: Iterable[bytes] = (),
    min_family_diversity: int = 2,
    min_path_diversity: int = 1,
    last_sequence: int | None = None,
    last_root_digest: bytes | None = None,
    previously_seen_root_digests: Iterable[bytes] = (),
    allow_watch: bool = False,
) -> ValidatorRootReport:
    if len(expected_scope_digest) != 32 or len(expected_request_digest) != 32:
        raise ValueError("expected digests must be 32 bytes")
    root_tuple = tuple(roots)
    if not root_tuple:
        return _report(ValidatorRootDecisionKind.QUARANTINE_MISSING_REQUIRED_VALIDATOR, False, "no validator root", profile_id=expected_profile_id, namespace=expected_namespace, scope_digest=expected_scope_digest, request_digest=expected_request_digest, roots=())
    for root in root_tuple:
        if not root.verify():
            return _report(ValidatorRootDecisionKind.QUARANTINE_BAD_SIGNATURE, False, "bad validator-root signature", profile_id=expected_profile_id, namespace=expected_namespace, scope_digest=expected_scope_digest, request_digest=expected_request_digest, roots=root_tuple)
        if root.issued_at > now:
            return _report(ValidatorRootDecisionKind.QUARANTINE_FUTURE, False, "validator root issued in future", profile_id=expected_profile_id, namespace=expected_namespace, scope_digest=expected_scope_digest, request_digest=expected_request_digest, roots=root_tuple)
        if root.expires_at <= now:
            return _report(ValidatorRootDecisionKind.QUARANTINE_EXPIRED, False, "validator root expired", profile_id=expected_profile_id, namespace=expected_namespace, scope_digest=expected_scope_digest, request_digest=expected_request_digest, roots=root_tuple)
        if root.profile_id != expected_profile_id:
            return _report(ValidatorRootDecisionKind.QUARANTINE_PROFILE_DRIFT, False, "profile drift in validator roots", profile_id=expected_profile_id, namespace=expected_namespace, scope_digest=expected_scope_digest, request_digest=expected_request_digest, roots=root_tuple)
        if root.namespace != expected_namespace or root.scope_digest != expected_scope_digest or root.request_digest != expected_request_digest:
            return _report(ValidatorRootDecisionKind.QUARANTINE_SCOPE_DRIFT, False, "namespace/scope/request drift in validator roots", profile_id=expected_profile_id, namespace=expected_namespace, scope_digest=expected_scope_digest, request_digest=expected_request_digest, roots=root_tuple)
    root_digests = {root.root_digest for root in root_tuple}
    if root_digests & set(previously_seen_root_digests):
        return _report(ValidatorRootDecisionKind.QUARANTINE_REPLAY, False, "validator root replay", profile_id=expected_profile_id, namespace=expected_namespace, scope_digest=expected_scope_digest, request_digest=expected_request_digest, roots=root_tuple)
    sequences = {root.sequence for root in root_tuple}
    if len(sequences) > 1:
        return _report(ValidatorRootDecisionKind.QUARANTINE_SEQUENCE_FORK, False, "mixed validator-root sequences", profile_id=expected_profile_id, namespace=expected_namespace, scope_digest=expected_scope_digest, request_digest=expected_request_digest, roots=root_tuple)
    sequence = next(iter(sequences))
    if len({tuple(root.validators) for root in root_tuple}) > 1:
        return _report(ValidatorRootDecisionKind.QUARANTINE_SEQUENCE_FORK, False, "same-sequence validator-set fork", profile_id=expected_profile_id, namespace=expected_namespace, scope_digest=expected_scope_digest, request_digest=expected_request_digest, roots=root_tuple)
    if last_sequence is not None:
        if sequence < last_sequence:
            return _report(ValidatorRootDecisionKind.QUARANTINE_ROLLBACK, False, "validator-root rollback", profile_id=expected_profile_id, namespace=expected_namespace, scope_digest=expected_scope_digest, request_digest=expected_request_digest, roots=root_tuple)
        if sequence == last_sequence:
            if last_root_digest is not None and any(root.root_digest != last_root_digest for root in root_tuple):
                return _report(ValidatorRootDecisionKind.QUARANTINE_SEQUENCE_FORK, False, "same-sequence validator-root fork", profile_id=expected_profile_id, namespace=expected_namespace, scope_digest=expected_scope_digest, request_digest=expected_request_digest, roots=root_tuple)
            return _report(ValidatorRootDecisionKind.QUARANTINE_REPLAY, False, "same-sequence validator-root replay", profile_id=expected_profile_id, namespace=expected_namespace, scope_digest=expected_scope_digest, request_digest=expected_request_digest, roots=root_tuple)
        if sequence > last_sequence + 1:
            return _report(ValidatorRootDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, "validator-root sequence gap", profile_id=expected_profile_id, namespace=expected_namespace, scope_digest=expected_scope_digest, request_digest=expected_request_digest, roots=root_tuple)
        if last_root_digest is not None and any(root.previous_root_digest != last_root_digest for root in root_tuple):
            return _report(ValidatorRootDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, "validator-root previous digest mismatch", profile_id=expected_profile_id, namespace=expected_namespace, scope_digest=expected_scope_digest, request_digest=expected_request_digest, roots=root_tuple)
    families = {root.family_id for root in root_tuple}
    paths = {root.path_family for root in root_tuple}
    if len(families) < min_family_diversity:
        return _report(ValidatorRootDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, "validator root lacks family diversity", profile_id=expected_profile_id, namespace=expected_namespace, scope_digest=expected_scope_digest, request_digest=expected_request_digest, roots=root_tuple)
    if len(paths) < min_path_diversity:
        return _report(ValidatorRootDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, "validator root lacks path diversity", profile_id=expected_profile_id, namespace=expected_namespace, scope_digest=expected_scope_digest, request_digest=expected_request_digest, roots=root_tuple)
    validators = set().union(*(set(root.validators) for root in root_tuple))
    missing = set(required_validator_digests) - validators
    if missing:
        return _report(ValidatorRootDecisionKind.QUARANTINE_MISSING_REQUIRED_VALIDATOR, False, "required validator missing", profile_id=expected_profile_id, namespace=expected_namespace, scope_digest=expected_scope_digest, request_digest=expected_request_digest, roots=root_tuple)
    forbidden = set(forbidden_validator_digests) & validators
    if forbidden:
        return _report(ValidatorRootDecisionKind.QUARANTINE_FORBIDDEN_VALIDATOR, False, "forbidden validator present", profile_id=expected_profile_id, namespace=expected_namespace, scope_digest=expected_scope_digest, request_digest=expected_request_digest, roots=root_tuple)
    watch = any(root.watch for root in root_tuple)
    if watch and not allow_watch:
        return _report(ValidatorRootDecisionKind.HOLD_WATCH_ROOT, False, "validator root accepted only with watch", profile_id=expected_profile_id, namespace=expected_namespace, scope_digest=expected_scope_digest, request_digest=expected_request_digest, roots=root_tuple, watch=True)
    return _report(ValidatorRootDecisionKind.ACCEPT_WITH_WATCH if watch else ValidatorRootDecisionKind.ACCEPT_VALIDATOR_ROOT, True, "validator root accepted locally", profile_id=expected_profile_id, namespace=expected_namespace, scope_digest=expected_scope_digest, request_digest=expected_request_digest, roots=root_tuple, watch=watch)
