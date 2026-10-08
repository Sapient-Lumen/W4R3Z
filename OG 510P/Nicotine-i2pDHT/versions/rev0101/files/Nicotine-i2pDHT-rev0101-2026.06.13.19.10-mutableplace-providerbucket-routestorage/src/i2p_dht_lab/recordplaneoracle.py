"""rev0099 Python-owned DHT record-plane oracle.

The native/GCC branch is now closed as shadow-only.  This module turns that
closure into a positive DHT-substrate rule: record validation, mutable-head
truth, provider semantics, parsing, crypto, transport, and persistence finality
remain Python-owned protocol surfaces.  Native code may not quietly inherit a
record-plane role just because a hot-path branch existed.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .bencode import bencode
from .ids import DOMAIN, sha256

RECORD_PLANE_ORACLE_DOMAIN = DOMAIN + b":record-plane-oracle-v1:"


class RecordPlaneOracleDecisionKind(str, Enum):
    ACCEPT_PYTHON_RECORD_ORACLE = "accept_python_record_oracle"
    HOLD_NATIVE_BRANCH_NOT_CLOSED = "hold_native_branch_not_closed"
    QUARANTINE_FORBIDDEN_NATIVE_SURFACE = "quarantine_forbidden_native_surface"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_MEMORY_DROP = "quarantine_memory_drop"
    QUARANTINE_REPLAY_OR_ROLLBACK = "quarantine_replay_or_rollback"
    QUARANTINE_SAME_SEQUENCE_FORK = "quarantine_same_sequence_fork"
    QUARANTINE_PREVIOUS_LINK_MISMATCH = "quarantine_previous_link_mismatch"
    QUARANTINE_SCOPE_OR_MODE_DRIFT = "quarantine_scope_or_mode_drift"
    QUARANTINE_LOW_DIVERSITY = "quarantine_low_diversity"


@dataclass(frozen=True)
class RecordPlaneOracleCapsule:
    component: str
    profile: str
    operation: str
    request_id: str
    sequence: int
    previous_digest: bytes
    native_branch_close_digest: bytes
    native_policy_digest: bytes
    record_namespace: str
    record_scope: str
    policy_mode: str
    python_validators_own_records: bool
    python_mutable_heads_own_latest: bool
    python_provider_proofs_own_semantics: bool
    python_parser_owns_untrusted_bytes: bool
    python_crypto_owns_signatures: bool
    python_transport_owns_sessions: bool
    python_persistence_owns_finality: bool
    native_record_parser_allowed: bool
    native_record_validator_allowed: bool
    native_mutable_truth_allowed: bool
    native_provider_truth_allowed: bool
    native_transport_allowed: bool
    native_persistence_allowed: bool
    preserve_native_branch_close_memory: bool
    preserve_native_policy_memory: bool
    preserve_mutable_head_memory: bool
    preserve_provider_false_memory: bool
    preserve_tombstone_memory: bool
    preserve_witness_memory: bool
    preserve_garden_refusal_memory: bool
    family_id: str
    path_family_id: str
    note: str = ""

    @property
    def capsule_digest(self) -> bytes:
        return sha256(RECORD_PLANE_ORACLE_DOMAIN + b":capsule:" + bencode({
            b"component": self.component,
            b"profile": self.profile,
            b"operation": self.operation,
            b"request": self.request_id,
            b"seq": self.sequence,
            b"prev": self.previous_digest,
            b"branch_close": self.native_branch_close_digest,
            b"native_policy": self.native_policy_digest,
            b"namespace": self.record_namespace,
            b"scope": self.record_scope,
            b"mode": self.policy_mode,
            b"py_validators": 1 if self.python_validators_own_records else 0,
            b"py_mutable": 1 if self.python_mutable_heads_own_latest else 0,
            b"py_provider": 1 if self.python_provider_proofs_own_semantics else 0,
            b"py_parser": 1 if self.python_parser_owns_untrusted_bytes else 0,
            b"py_crypto": 1 if self.python_crypto_owns_signatures else 0,
            b"py_transport": 1 if self.python_transport_owns_sessions else 0,
            b"py_persistence": 1 if self.python_persistence_owns_finality else 0,
            b"native_parser": 1 if self.native_record_parser_allowed else 0,
            b"native_validator": 1 if self.native_record_validator_allowed else 0,
            b"native_mutable": 1 if self.native_mutable_truth_allowed else 0,
            b"native_provider": 1 if self.native_provider_truth_allowed else 0,
            b"native_transport": 1 if self.native_transport_allowed else 0,
            b"native_persistence": 1 if self.native_persistence_allowed else 0,
            b"preserve_branch": 1 if self.preserve_native_branch_close_memory else 0,
            b"preserve_policy": 1 if self.preserve_native_policy_memory else 0,
            b"preserve_mutable": 1 if self.preserve_mutable_head_memory else 0,
            b"preserve_provider_false": 1 if self.preserve_provider_false_memory else 0,
            b"preserve_tombstone": 1 if self.preserve_tombstone_memory else 0,
            b"preserve_witness": 1 if self.preserve_witness_memory else 0,
            b"preserve_refusal": 1 if self.preserve_garden_refusal_memory else 0,
            b"family": self.family_id,
            b"path_family": self.path_family_id,
            b"note": self.note,
        }))


@dataclass(frozen=True)
class RecordPlaneOracleReport:
    decision_kind: RecordPlaneOracleDecisionKind
    accepted: bool
    python_record_truth: bool
    native_record_permission: bool
    quarantine: bool
    watch: bool
    obligations: tuple[str, ...]
    capsule_digest: bytes
    native_branch_close_digest: bytes
    native_policy_digest: bytes
    record_namespace: str
    record_scope: str
    family_count: int
    path_family_count: int

    @property
    def report_digest(self) -> bytes:
        return sha256(RECORD_PLANE_ORACLE_DOMAIN + b":report:" + bencode({
            b"decision": self.decision_kind.value,
            b"accepted": 1 if self.accepted else 0,
            b"python_record_truth": 1 if self.python_record_truth else 0,
            b"native_record_permission": 1 if self.native_record_permission else 0,
            b"quarantine": 1 if self.quarantine else 0,
            b"watch": 1 if self.watch else 0,
            b"obligations": list(self.obligations),
            b"capsule": self.capsule_digest,
            b"branch_close": self.native_branch_close_digest,
            b"native_policy": self.native_policy_digest,
            b"namespace": self.record_namespace,
            b"scope": self.record_scope,
            b"family_count": self.family_count,
            b"path_family_count": self.path_family_count,
        }))


def assess_record_plane_oracle(
    native_branch_close: object,
    native_policy: object,
    capsule: RecordPlaneOracleCapsule,
    *,
    previous: RecordPlaneOracleCapsule | None = None,
    prior_capsule_digests: tuple[bytes, ...] = (),
    observed_families: tuple[str, ...] = (),
    observed_path_families: tuple[str, ...] = (),
    min_families: int = 2,
    min_path_families: int = 2,
) -> RecordPlaneOracleReport:
    families = set(observed_families or (capsule.family_id,))
    path_families = set(observed_path_families or (capsule.path_family_id,))

    def report(kind: RecordPlaneOracleDecisionKind, accepted: bool, quarantine: bool, watch: bool, obligations: tuple[str, ...]) -> RecordPlaneOracleReport:
        native_permission = any((
            capsule.native_record_parser_allowed,
            capsule.native_record_validator_allowed,
            capsule.native_mutable_truth_allowed,
            capsule.native_provider_truth_allowed,
            capsule.native_transport_allowed,
            capsule.native_persistence_allowed,
        ))
        python_truth = accepted and not native_permission and capsule.policy_mode == "python_record_truth"
        return RecordPlaneOracleReport(
            kind, accepted, python_truth, native_permission, quarantine, watch, obligations,
            capsule.capsule_digest, capsule.native_branch_close_digest, capsule.native_policy_digest,
            capsule.record_namespace, capsule.record_scope, len(families), len(path_families)
        )

    if capsule.capsule_digest in prior_capsule_digests:
        return report(RecordPlaneOracleDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, True, False, ("record-plane-oracle-replay",))
    if previous is not None:
        if capsule.sequence < previous.sequence:
            return report(RecordPlaneOracleDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, True, False, ("record-plane-oracle-rollback",))
        if capsule.sequence == previous.sequence and capsule.capsule_digest != previous.capsule_digest:
            return report(RecordPlaneOracleDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK, False, True, False, ("record-plane-oracle-same-sequence-fork",))
        if capsule.sequence > previous.sequence and capsule.previous_digest != previous.capsule_digest:
            return report(RecordPlaneOracleDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH, False, True, False, ("record-plane-oracle-previous-link-mismatch",))
    if len(families) < min_families or len(path_families) < min_path_families:
        return report(RecordPlaneOracleDecisionKind.QUARANTINE_LOW_DIVERSITY, False, True, False, ("record-plane-oracle-low-diversity",))
    if not getattr(native_branch_close, "accepted", False) or not getattr(native_branch_close, "branch_closed", False):
        return report(RecordPlaneOracleDecisionKind.HOLD_NATIVE_BRANCH_NOT_CLOSED, False, False, True, ("native-branch-close-not-accepted",))
    if getattr(native_branch_close, "native_permission", True):
        return report(RecordPlaneOracleDecisionKind.QUARANTINE_FORBIDDEN_NATIVE_SURFACE, False, True, False, ("native-branch-close-carried-permission",))
    if not getattr(native_policy, "accepted", False) or not getattr(native_policy, "shadow_only", False):
        return report(RecordPlaneOracleDecisionKind.HOLD_NATIVE_BRANCH_NOT_CLOSED, False, False, True, ("native-shadow-policy-not-accepted",))
    if capsule.native_branch_close_digest != getattr(native_branch_close, "report_digest", b"") or capsule.native_policy_digest != getattr(native_policy, "report_digest", b""):
        return report(RecordPlaneOracleDecisionKind.QUARANTINE_DIGEST_DRIFT, False, True, False, ("record-plane-oracle-component-digest-drift",))
    if capsule.policy_mode != "python_record_truth" or capsule.record_namespace not in {"dht.records", "dht.mutable", "dht.providers", "dht.routing"}:
        return report(RecordPlaneOracleDecisionKind.QUARANTINE_SCOPE_OR_MODE_DRIFT, False, True, False, ("record-plane-oracle-scope-or-mode-drift",))
    required_python = (
        capsule.python_validators_own_records,
        capsule.python_mutable_heads_own_latest,
        capsule.python_provider_proofs_own_semantics,
        capsule.python_parser_owns_untrusted_bytes,
        capsule.python_crypto_owns_signatures,
        capsule.python_transport_owns_sessions,
        capsule.python_persistence_owns_finality,
    )
    if not all(required_python):
        return report(RecordPlaneOracleDecisionKind.QUARANTINE_SCOPE_OR_MODE_DRIFT, False, True, False, ("record-plane-python-owner-missing",))
    if any((
        capsule.native_record_parser_allowed,
        capsule.native_record_validator_allowed,
        capsule.native_mutable_truth_allowed,
        capsule.native_provider_truth_allowed,
        capsule.native_transport_allowed,
        capsule.native_persistence_allowed,
    )):
        return report(RecordPlaneOracleDecisionKind.QUARANTINE_FORBIDDEN_NATIVE_SURFACE, False, True, False, ("record-plane-native-permission-attempt",))
    if not all((
        capsule.preserve_native_branch_close_memory,
        capsule.preserve_native_policy_memory,
        capsule.preserve_mutable_head_memory,
        capsule.preserve_provider_false_memory,
        capsule.preserve_tombstone_memory,
        capsule.preserve_witness_memory,
        capsule.preserve_garden_refusal_memory,
    )):
        return report(RecordPlaneOracleDecisionKind.QUARANTINE_MEMORY_DROP, False, True, False, ("record-plane-oracle-memory-drop",))
    return report(RecordPlaneOracleDecisionKind.ACCEPT_PYTHON_RECORD_ORACLE, True, False, False, ("keep-python-record-plane-oracle", "native-branch-remains-shadow-only"))
