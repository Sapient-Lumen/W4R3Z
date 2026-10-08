"""rev0091 native Python-oracle seal.

A cold-start/relaunch candidate may only move toward native reconsideration if the
Python oracle remains explicitly bound.  This seal is not native load permission
and not dispatch permission; it is a compact exact-boundary reminder that the
Python reference, fallback route, and fault memories are still the authority.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .bencode import bencode
from .ids import DOMAIN, sha256
from .loaderseal import NativeLoaderSealReport

NATIVE_ORACLE_SEAL_DOMAIN = DOMAIN + b":native-oracle-seal-v1:"


class NativeOracleSealDecisionKind(str, Enum):
    ACCEPT_PYTHON_ORACLE_SEAL = "accept_python_oracle_seal"
    HOLD_LOADER_SEAL_NOT_READY = "hold_loader_seal_not_ready"
    HOLD_NATIVE_EVAL_DISABLED = "hold_native_eval_disabled"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_FORBIDDEN_SURFACE = "quarantine_forbidden_surface"
    QUARANTINE_MEMORY_DROP = "quarantine_memory_drop"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_REPLAY_OR_ROLLBACK = "quarantine_replay_or_rollback"
    QUARANTINE_SAME_SEQUENCE_FORK = "quarantine_same_sequence_fork"
    QUARANTINE_PREVIOUS_LINK_MISMATCH = "quarantine_previous_link_mismatch"
    QUARANTINE_LOW_DIVERSITY = "quarantine_low_diversity"


@dataclass(frozen=True)
class NativeOracleSealCapsule:
    component: str
    profile: str
    operation: str
    request_id: str
    sequence: int
    previous_digest: bytes
    loader_seal_digest: bytes
    artifact_digest: bytes
    source_digest: bytes
    fallback_digest: bytes
    python_oracle_digest: bytes
    differential_corpus_digest: bytes
    allow_native_eval: bool
    parser_bytes_touched: bool
    crypto_or_secret_touched: bool
    transport_touched: bool
    persistence_touched: bool
    python_fallback_active: bool
    preserve_loader_seal_memory: bool
    preserve_fallback_memory: bool
    preserve_tombstone_memory: bool
    preserve_quarantine_memory: bool
    preserve_crash_memory: bool
    family_id: str
    path_family_id: str
    note: str = ""

    @property
    def capsule_digest(self) -> bytes:
        return sha256(NATIVE_ORACLE_SEAL_DOMAIN + b":capsule:" + bencode({
            b"component": self.component,
            b"profile": self.profile,
            b"operation": self.operation,
            b"request": self.request_id,
            b"seq": self.sequence,
            b"prev": self.previous_digest,
            b"loader_seal": self.loader_seal_digest,
            b"artifact": self.artifact_digest,
            b"source": self.source_digest,
            b"fallback": self.fallback_digest,
            b"oracle": self.python_oracle_digest,
            b"corpus": self.differential_corpus_digest,
            b"allow_native_eval": 1 if self.allow_native_eval else 0,
            b"parser": 1 if self.parser_bytes_touched else 0,
            b"crypto": 1 if self.crypto_or_secret_touched else 0,
            b"transport": 1 if self.transport_touched else 0,
            b"persistence": 1 if self.persistence_touched else 0,
            b"fallback_active": 1 if self.python_fallback_active else 0,
            b"preserve_loader": 1 if self.preserve_loader_seal_memory else 0,
            b"preserve_fallback": 1 if self.preserve_fallback_memory else 0,
            b"preserve_tombstone": 1 if self.preserve_tombstone_memory else 0,
            b"preserve_quarantine": 1 if self.preserve_quarantine_memory else 0,
            b"preserve_crash": 1 if self.preserve_crash_memory else 0,
            b"family": self.family_id,
            b"path_family": self.path_family_id,
            b"note": self.note,
        }))


@dataclass(frozen=True)
class NativeOracleSealReport:
    decision_kind: NativeOracleSealDecisionKind
    accepted: bool
    python_oracle_sealed: bool
    native_eval_allowed: bool
    native_load_forbidden: bool
    dispatch_forbidden: bool
    fallback_active: bool
    quarantine: bool
    watch: bool
    obligations: tuple[str, ...]
    capsule_digest: bytes
    loader_seal_digest: bytes
    artifact_digest: bytes
    source_digest: bytes
    fallback_digest: bytes
    python_oracle_digest: bytes
    differential_corpus_digest: bytes
    tombstone_memory: bool
    fault_memory: bool
    family_count: int
    path_family_count: int

    @property
    def report_digest(self) -> bytes:
        return sha256(NATIVE_ORACLE_SEAL_DOMAIN + b":report:" + bencode({
            b"decision": NativeOracleSealDecisionKind(self.decision_kind).value,
            b"accepted": 1 if self.accepted else 0,
            b"oracle_sealed": 1 if self.python_oracle_sealed else 0,
            b"native_eval_allowed": 1 if self.native_eval_allowed else 0,
            b"load_forbidden": 1 if self.native_load_forbidden else 0,
            b"dispatch_forbidden": 1 if self.dispatch_forbidden else 0,
            b"fallback_active": 1 if self.fallback_active else 0,
            b"quarantine": 1 if self.quarantine else 0,
            b"watch": 1 if self.watch else 0,
            b"obligations": list(self.obligations),
            b"capsule": self.capsule_digest,
            b"loader_seal": self.loader_seal_digest,
            b"artifact": self.artifact_digest,
            b"source": self.source_digest,
            b"fallback": self.fallback_digest,
            b"oracle": self.python_oracle_digest,
            b"corpus": self.differential_corpus_digest,
            b"tombstone": 1 if self.tombstone_memory else 0,
            b"fault_memory": 1 if self.fault_memory else 0,
            b"family_count": self.family_count,
            b"path_family_count": self.path_family_count,
        }))


def assess_native_oracle_seal(
    loader_seal: NativeLoaderSealReport,
    capsule: NativeOracleSealCapsule,
    *,
    previous: NativeOracleSealCapsule | None = None,
    prior_capsule_digests: tuple[bytes, ...] = (),
    observed_families: tuple[str, ...] = (),
    observed_path_families: tuple[str, ...] = (),
    min_families: int = 2,
    min_path_families: int = 2,
) -> NativeOracleSealReport:
    families = set(observed_families or (capsule.family_id,))
    path_families = set(observed_path_families or (capsule.path_family_id,))
    tombstone_memory = bool(loader_seal.tombstone_memory and capsule.preserve_tombstone_memory)
    fault_memory = bool(loader_seal.fault_memory and capsule.preserve_quarantine_memory and capsule.preserve_crash_memory)

    def report(kind: NativeOracleSealDecisionKind, accepted: bool, sealed: bool, native_eval: bool, fallback: bool, quarantine: bool, watch: bool, obligations: tuple[str, ...]) -> NativeOracleSealReport:
        return NativeOracleSealReport(kind, accepted, sealed, native_eval, True, True, fallback, quarantine, watch, obligations, capsule.capsule_digest, loader_seal.report_digest, capsule.artifact_digest, capsule.source_digest, capsule.fallback_digest, capsule.python_oracle_digest, capsule.differential_corpus_digest, tombstone_memory, fault_memory, len(families), len(path_families))

    if capsule.capsule_digest in prior_capsule_digests:
        return report(NativeOracleSealDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, False, False, True, True, False, ("native-oracle-seal-replay",))
    if previous is not None:
        if capsule.sequence < previous.sequence:
            return report(NativeOracleSealDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, False, False, True, True, False, ("native-oracle-seal-rollback",))
        if capsule.sequence == previous.sequence and capsule.capsule_digest != previous.capsule_digest:
            return report(NativeOracleSealDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK, False, False, False, True, True, False, ("native-oracle-seal-same-sequence-fork",))
        if capsule.sequence > previous.sequence and capsule.previous_digest != previous.capsule_digest:
            return report(NativeOracleSealDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH, False, False, False, True, True, False, ("native-oracle-seal-previous-link-mismatch",))
    if len(families) < min_families or len(path_families) < min_path_families:
        return report(NativeOracleSealDecisionKind.QUARANTINE_LOW_DIVERSITY, False, False, False, True, True, False, ("native-oracle-seal-low-diversity",))
    if not all((capsule.component, capsule.profile, capsule.operation, capsule.request_id)):
        return report(NativeOracleSealDecisionKind.QUARANTINE_SCOPE_DRIFT, False, False, False, True, True, False, ("native-oracle-seal-missing-boundary",))
    if not loader_seal.accepted or not loader_seal.sealed:
        return report(NativeOracleSealDecisionKind.HOLD_LOADER_SEAL_NOT_READY, False, False, False, True, loader_seal.quarantine, True, ("loader-seal-not-ready", "python-fallback-only"))
    if capsule.loader_seal_digest != loader_seal.report_digest:
        return report(NativeOracleSealDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, False, True, True, False, ("native-oracle-seal-loader-digest-drift",))
    if capsule.artifact_digest != loader_seal.artifact_digest or capsule.source_digest != loader_seal.source_digest or capsule.fallback_digest != loader_seal.fallback_digest or capsule.python_oracle_digest != loader_seal.python_oracle_digest:
        return report(NativeOracleSealDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, False, True, True, False, ("native-oracle-seal-artifact-source-fallback-oracle-drift",))
    if capsule.parser_bytes_touched or capsule.crypto_or_secret_touched or capsule.transport_touched or capsule.persistence_touched:
        return report(NativeOracleSealDecisionKind.QUARANTINE_FORBIDDEN_SURFACE, False, False, False, True, True, False, ("native-oracle-seal-forbidden-semantic-surface", "python-owns-parser-crypto-transport-persistence"))
    if not capsule.python_fallback_active or not capsule.preserve_loader_seal_memory or not capsule.preserve_fallback_memory or not tombstone_memory or not fault_memory:
        return report(NativeOracleSealDecisionKind.QUARANTINE_MEMORY_DROP, False, False, False, True, True, False, ("native-oracle-seal-memory-drop", "fallback-or-fault-memory-required"))
    if not capsule.allow_native_eval:
        return report(NativeOracleSealDecisionKind.HOLD_NATIVE_EVAL_DISABLED, False, True, False, True, False, True, ("native-eval-disabled", "python-fallback-active"))
    return report(NativeOracleSealDecisionKind.ACCEPT_PYTHON_ORACLE_SEAL, True, True, True, True, False, loader_seal.watch, ("python-oracle-sealed", "native-load-and-dispatch-still-forbidden"))
