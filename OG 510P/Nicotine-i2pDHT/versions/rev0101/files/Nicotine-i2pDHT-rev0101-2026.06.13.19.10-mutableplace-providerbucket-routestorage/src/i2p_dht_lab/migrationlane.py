"""Persisted-state migration pressure for local DHT memory.

The cube has treated local evidence as protocol memory: tombstones, revocations,
provider-false evidence, crisis notices, and fork evidence must survive restart.
rev0033 adds another boundary: upgrade/migration.  Old state can be parse-safe
and signed while still dropping hard negatives, widening scope, or rolling back
sequence memory.

This is a small deterministic migration seam, not a database migrator.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256

MIGRATION_DOMAIN = DOMAIN + b":migration-lane-v1:"
ZERO_DIGEST = b"\x00" * 32


class StateAtomKind(str, Enum):
    MUTABLE_HEAD = "mutable_head"
    PROVIDER_TRUE = "provider_true"
    PROVIDER_FALSE = "provider_false"
    TOMBSTONE = "tombstone"
    REVOCATION = "revocation"
    KEY_CRISIS = "key_crisis"
    WITNESS_FORK = "witness_fork"
    SOFT_CACHE = "soft_cache"


HARD_NEGATIVE_KINDS = {
    StateAtomKind.PROVIDER_FALSE,
    StateAtomKind.TOMBSTONE,
    StateAtomKind.REVOCATION,
    StateAtomKind.KEY_CRISIS,
    StateAtomKind.WITNESS_FORK,
}


class MigrationDecisionKind(str, Enum):
    ACCEPT_MIGRATION = "accept_migration"
    ACCEPT_WITH_SOFT_DROP = "accept_with_soft_drop"
    HOLD_SCHEMA_WINDOW = "hold_schema_window"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_EXPIRED_MANIFEST = "quarantine_expired_manifest"
    QUARANTINE_INPUT_DIGEST_MISMATCH = "quarantine_input_digest_mismatch"
    QUARANTINE_OUTPUT_DIGEST_MISMATCH = "quarantine_output_digest_mismatch"
    QUARANTINE_DROPPED_HARD_NEGATIVE = "quarantine_dropped_hard_negative"
    QUARANTINE_SCOPE_WIDENING = "quarantine_scope_widening"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_DROPPED_COUNT_MISMATCH = "quarantine_dropped_count_mismatch"
    QUARANTINE_REPLAYED_MANIFEST = "quarantine_replayed_manifest"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"


@dataclass(frozen=True)
class MigrationPolicy:
    expected_from_schema: str = "rev0032-local-state"
    expected_to_schema: str = "rev0033-local-state"
    allow_soft_drop: bool = True
    max_generation_gap: int = 1

    def validate(self) -> None:
        if not self.expected_from_schema or not self.expected_to_schema:
            raise ValueError("migration schema names must not be empty")
        if self.max_generation_gap <= 0:
            raise ValueError("migration generation gap must be positive")


@dataclass(frozen=True)
class StateAtom:
    kind: StateAtomKind
    scope_id: bytes
    object_digest: bytes
    value_digest: bytes
    sequence: int
    issued_at: int
    expires_at: int
    source_family: str = "unknown-source"
    path_family: str = "unknown-path"

    def __post_init__(self) -> None:
        for name, value in (("scope_id", self.scope_id), ("object_digest", self.object_digest), ("value_digest", self.value_digest)):
            if len(value) != 32:
                raise ValueError(f"state atom {name} must be 32 bytes")
        if self.sequence < 0:
            raise ValueError("state atom sequence must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("state atom expiry must follow issue time")
        if not self.source_family or not self.path_family:
            raise ValueError("state atom needs source/path families")

    @property
    def hard_negative(self) -> bool:
        return self.kind in HARD_NEGATIVE_KINDS

    @property
    def identity_key(self) -> tuple[StateAtomKind, bytes, bytes]:
        return (self.kind, self.scope_id, self.object_digest)

    def live(self, *, now: int) -> bool:
        return self.issued_at <= now < self.expires_at

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"kind": self.kind.value,
            b"scope": self.scope_id,
            b"object": self.object_digest,
            b"value": self.value_digest,
            b"sequence": self.sequence,
            b"issued_at": self.issued_at,
            b"expires_at": self.expires_at,
            b"source_family": self.source_family,
            b"path_family": self.path_family,
        }

    @property
    def atom_digest(self) -> bytes:
        return sha256(MIGRATION_DOMAIN + b":atom:" + bencode(self.bvalue()))


def state_digest(atoms: Iterable[StateAtom]) -> bytes:
    atom_digests = sorted(atom.atom_digest for atom in atoms)
    return sha256(MIGRATION_DOMAIN + b":state-digest:" + bencode(atom_digests))


@dataclass(frozen=True)
class MigrationManifest:
    actor_public_key: bytes
    from_schema: str
    to_schema: str
    generation: int
    prev_manifest_digest: bytes
    input_digest: bytes
    output_digest: bytes
    preserved_hard_negative_digests: tuple[bytes, ...]
    dropped_soft_count: int
    sequence: int
    issued_at: int
    expires_at: int
    signature: bytes = b""

    def __post_init__(self) -> None:
        for name, value in (
            ("actor_public_key", self.actor_public_key),
            ("prev_manifest_digest", self.prev_manifest_digest),
            ("input_digest", self.input_digest),
            ("output_digest", self.output_digest),
        ):
            if len(value) != 32:
                raise ValueError(f"migration manifest {name} must be 32 bytes")
        for digest in self.preserved_hard_negative_digests:
            if len(digest) != 32:
                raise ValueError("preserved hard-negative digests must be 32 bytes")
        if not self.from_schema or not self.to_schema:
            raise ValueError("migration manifest schema names must not be empty")
        if self.generation < 0 or self.sequence < 0 or self.dropped_soft_count < 0:
            raise ValueError("migration manifest counters must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("migration manifest expiry must follow issue time")
        if self.signature and len(self.signature) != 64:
            raise ValueError("migration manifest signature must be empty or 64 bytes")

    @classmethod
    def create(
        cls,
        *,
        keypair: DhtKeypair,
        from_schema: str,
        to_schema: str,
        generation: int,
        prev_manifest_digest: bytes,
        input_atoms: Iterable[StateAtom],
        output_atoms: Iterable[StateAtom],
        dropped_soft_count: int,
        sequence: int,
        issued_at: int,
        ttl: int,
    ) -> "MigrationManifest":
        if ttl <= 0:
            raise ValueError("migration manifest ttl must be positive")
        output_t = tuple(output_atoms)
        preserved_hard = tuple(sorted(atom.atom_digest for atom in output_t if atom.hard_negative))
        unsigned = cls(
            actor_public_key=keypair.public_key_bytes,
            from_schema=from_schema,
            to_schema=to_schema,
            generation=generation,
            prev_manifest_digest=prev_manifest_digest,
            input_digest=state_digest(input_atoms),
            output_digest=state_digest(output_t),
            preserved_hard_negative_digests=preserved_hard,
            dropped_soft_count=dropped_soft_count,
            sequence=sequence,
            issued_at=issued_at,
            expires_at=issued_at + ttl,
        )
        return replace(unsigned, signature=keypair.sign(unsigned.unsigned_payload()))

    def live(self, *, now: int) -> bool:
        return self.issued_at <= now < self.expires_at

    @property
    def manifest_digest(self) -> bytes:
        return sha256(MIGRATION_DOMAIN + b":manifest:" + self.unsigned_payload() + self.signature)

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"actor": self.actor_public_key,
            b"from": self.from_schema,
            b"to": self.to_schema,
            b"generation": self.generation,
            b"prev": self.prev_manifest_digest,
            b"input": self.input_digest,
            b"output": self.output_digest,
            b"preserved_hard": list(self.preserved_hard_negative_digests),
            b"dropped_soft": self.dropped_soft_count,
            b"sequence": self.sequence,
            b"issued_at": self.issued_at,
            b"expires_at": self.expires_at,
        }

    def unsigned_payload(self) -> bytes:
        return MIGRATION_DOMAIN + b":manifest-unsigned:" + bencode(self.unsigned_bvalue())

    def verify(self) -> bool:
        return verify_signature(self.actor_public_key, self.unsigned_payload(), self.signature)


@dataclass(frozen=True)
class MigrationReport:
    decision_kind: MigrationDecisionKind
    accept: bool
    reason: str
    manifest_digest: bytes
    hard_negative_count: int
    dropped_soft_count: int
    pressure_digests: tuple[bytes, ...]
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _report(kind: MigrationDecisionKind, accept: bool, reason: str, manifest: MigrationManifest | None, *, hard_count: int = 0, soft_drop: int = 0, pressures: Iterable[bytes] = ()) -> MigrationReport:
    manifest_digest = ZERO_DIGEST if manifest is None else manifest.manifest_digest
    pressure_t = tuple(sorted(set(pressures)))
    digest = sha256(MIGRATION_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"reason": reason,
        b"manifest": manifest_digest,
        b"hard_count": hard_count,
        b"soft_drop": soft_drop,
        b"pressures": list(pressure_t),
    }))
    return MigrationReport(kind, accept, reason, manifest_digest, hard_count, soft_drop, pressure_t, digest)


def _max_sequence_by_identity(atoms: Iterable[StateAtom]) -> dict[tuple[StateAtomKind, bytes, bytes], int]:
    result: dict[tuple[StateAtomKind, bytes, bytes], int] = {}
    for atom in atoms:
        result[atom.identity_key] = max(result.get(atom.identity_key, -1), atom.sequence)
    return result


def assess_state_migration(
    input_atoms: Iterable[StateAtom],
    output_atoms: Iterable[StateAtom],
    manifest: MigrationManifest,
    *,
    now: int,
    previous_manifest: MigrationManifest | None = None,
    policy: MigrationPolicy | None = None,
) -> MigrationReport:
    policy = policy or MigrationPolicy()
    policy.validate()
    in_t = tuple(input_atoms)
    out_t = tuple(output_atoms)

    if not manifest.verify():
        return _report(MigrationDecisionKind.QUARANTINE_BAD_SIGNATURE, False, "bad migration manifest signature", manifest, pressures=(manifest.manifest_digest,))
    if not manifest.live(now=now):
        return _report(MigrationDecisionKind.QUARANTINE_EXPIRED_MANIFEST, False, "expired migration manifest", manifest, pressures=(manifest.manifest_digest,))
    if manifest.from_schema != policy.expected_from_schema or manifest.to_schema != policy.expected_to_schema:
        return _report(MigrationDecisionKind.HOLD_SCHEMA_WINDOW, False, "migration schema window does not match policy", manifest)
    if previous_manifest is not None:
        if manifest.actor_public_key == previous_manifest.actor_public_key and manifest.sequence == previous_manifest.sequence and manifest.manifest_digest == previous_manifest.manifest_digest:
            return _report(MigrationDecisionKind.QUARANTINE_REPLAYED_MANIFEST, False, "migration manifest replay", manifest, pressures=(manifest.manifest_digest,))
        if manifest.actor_public_key == previous_manifest.actor_public_key and manifest.sequence == previous_manifest.sequence and manifest.manifest_digest != previous_manifest.manifest_digest:
            return _report(MigrationDecisionKind.QUARANTINE_SEQUENCE_FORK, False, "same actor sequence forked migration manifest", manifest, pressures=(manifest.manifest_digest, previous_manifest.manifest_digest))
        if manifest.generation - previous_manifest.generation > policy.max_generation_gap:
            return _report(MigrationDecisionKind.HOLD_SCHEMA_WINDOW, False, "migration generation gap requires manual review", manifest)
    if manifest.input_digest != state_digest(in_t):
        return _report(MigrationDecisionKind.QUARANTINE_INPUT_DIGEST_MISMATCH, False, "input state digest mismatch", manifest)
    if manifest.output_digest != state_digest(out_t):
        return _report(MigrationDecisionKind.QUARANTINE_OUTPUT_DIGEST_MISMATCH, False, "output state digest mismatch", manifest)

    out_hard = {atom.atom_digest: atom for atom in out_t if atom.hard_negative}

    # Scope widening: the same object/kind/value reappears under a different scope.
    # Check this before digest-preservation so the report explains the boundary
    # failure rather than only saying the exact old digest disappeared.
    input_scope_by_object = {(atom.kind, atom.object_digest, atom.value_digest): atom.scope_id for atom in in_t}
    for atom in out_t:
        old_scope = input_scope_by_object.get((atom.kind, atom.object_digest, atom.value_digest))
        if old_scope is not None and old_scope != atom.scope_id:
            return _report(MigrationDecisionKind.QUARANTINE_SCOPE_WIDENING, False, "atom moved to a different scope during migration", manifest, hard_count=len(out_hard), pressures=(atom.atom_digest,))

    in_seq = _max_sequence_by_identity(in_t)
    for atom in out_t:
        old_seq = in_seq.get(atom.identity_key)
        if old_seq is not None and atom.sequence < old_seq:
            return _report(MigrationDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, "atom sequence rolled back during migration", manifest, hard_count=len(out_hard), pressures=(atom.atom_digest,))

    in_hard = {atom.atom_digest: atom for atom in in_t if atom.hard_negative}
    missing_hard = sorted(set(in_hard).difference(out_hard))
    if missing_hard:
        return _report(MigrationDecisionKind.QUARANTINE_DROPPED_HARD_NEGATIVE, False, "hard negative disappeared during migration", manifest, hard_count=len(out_hard), pressures=missing_hard)
    if tuple(sorted(out_hard)) != tuple(sorted(manifest.preserved_hard_negative_digests)):
        return _report(MigrationDecisionKind.QUARANTINE_DROPPED_HARD_NEGATIVE, False, "manifest hard-negative preservation list mismatches output", manifest, hard_count=len(out_hard), pressures=tuple(sorted(out_hard)))

    input_soft = {atom.atom_digest for atom in in_t if not atom.hard_negative}
    output_soft = {atom.atom_digest for atom in out_t if not atom.hard_negative}
    dropped_soft = len(input_soft.difference(output_soft))
    if dropped_soft != manifest.dropped_soft_count:
        return _report(MigrationDecisionKind.QUARANTINE_DROPPED_COUNT_MISMATCH, False, "soft drop count mismatch", manifest, hard_count=len(out_hard), soft_drop=dropped_soft)
    if dropped_soft and not policy.allow_soft_drop:
        return _report(MigrationDecisionKind.QUARANTINE_DROPPED_COUNT_MISMATCH, False, "soft drops are disabled by policy", manifest, hard_count=len(out_hard), soft_drop=dropped_soft)
    if dropped_soft:
        return _report(MigrationDecisionKind.ACCEPT_WITH_SOFT_DROP, True, "migration preserved hard negatives while dropping soft evidence", manifest, hard_count=len(out_hard), soft_drop=dropped_soft)
    return _report(MigrationDecisionKind.ACCEPT_MIGRATION, True, "migration preserved state boundaries", manifest, hard_count=len(out_hard), soft_drop=0)
