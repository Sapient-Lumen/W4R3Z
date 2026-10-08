"""rev0100 record-ingress gate for the returned Python-owned DHT substrate.

rev0099 re-entered the generic substrate and reasserted that Python owns record
truth.  rev0100 starts using that promise: a valid-looking incoming DHT record
is only admitted after substrate re-entry, the record-plane oracle, parsing,
validation, admission, native-closure memory, and exact-boundary evidence agree.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .bencode import bencode
from .ids import DOMAIN, sha256

RECORD_INGRESS_DOMAIN = DOMAIN + b":record-ingress-v1:"
ALLOWED_RECORD_KINDS = {"immutable", "mutable", "provider", "routing", "garden_seed", "tombstone"}
ALLOWED_NAMESPACES = {"dht.records", "dht.mutable", "dht.providers", "dht.routing", "dht.garden"}


class RecordIngressDecisionKind(str, Enum):
    ACCEPT_RECORD_INGRESS = "accept_record_ingress"
    HOLD_COMPONENT_NOT_READY = "hold_component_not_ready"
    QUARANTINE_NATIVE_PERMISSION_LEAK = "quarantine_native_permission_leak"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_PARSE_NOT_CANONICAL = "quarantine_parse_not_canonical"
    QUARANTINE_VALIDATOR_REJECTED = "quarantine_validator_rejected"
    QUARANTINE_ADMISSION_REJECTED = "quarantine_admission_rejected"
    QUARANTINE_SCOPE_OR_KIND_DRIFT = "quarantine_scope_or_kind_drift"
    QUARANTINE_SIZE_OR_TTL = "quarantine_size_or_ttl"
    QUARANTINE_MEMORY_DROP = "quarantine_memory_drop"
    QUARANTINE_REPLAY_OR_ROLLBACK = "quarantine_replay_or_rollback"
    QUARANTINE_SAME_SEQUENCE_FORK = "quarantine_same_sequence_fork"
    QUARANTINE_PREVIOUS_LINK_MISMATCH = "quarantine_previous_link_mismatch"
    QUARANTINE_LOW_DIVERSITY = "quarantine_low_diversity"


@dataclass(frozen=True)
class RecordIngressCapsule:
    component: str
    profile: str
    namespace: str
    record_kind: str
    record_key: str
    request_id: str
    sequence: int
    previous_digest: bytes
    substrate_reentry_digest: bytes
    record_plane_oracle_digest: bytes
    parse_report_digest: bytes
    validator_report_digest: bytes
    admission_report_digest: bytes
    payload_digest: bytes
    value_size: int
    max_value_size: int
    ttl_seconds: int
    max_ttl_seconds: int
    canonical_wire: bool
    untrusted_bytes_parsed_by_python: bool
    python_validator_accepted: bool
    admission_accepted: bool
    native_validation_attempted: bool
    native_parser_attempted: bool
    signature_checked_by_python: bool
    preserve_record_plane_oracle_memory: bool
    preserve_substrate_reentry_memory: bool
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
        return sha256(RECORD_INGRESS_DOMAIN + b":capsule:" + bencode({
            b"component": self.component,
            b"profile": self.profile,
            b"namespace": self.namespace,
            b"kind": self.record_kind,
            b"key": self.record_key,
            b"request": self.request_id,
            b"seq": self.sequence,
            b"prev": self.previous_digest,
            b"substrate": self.substrate_reentry_digest,
            b"oracle": self.record_plane_oracle_digest,
            b"parse": self.parse_report_digest,
            b"validator": self.validator_report_digest,
            b"admission": self.admission_report_digest,
            b"payload": self.payload_digest,
            b"value_size": self.value_size,
            b"max_value_size": self.max_value_size,
            b"ttl": self.ttl_seconds,
            b"max_ttl": self.max_ttl_seconds,
            b"canonical": 1 if self.canonical_wire else 0,
            b"py_parse": 1 if self.untrusted_bytes_parsed_by_python else 0,
            b"py_validator": 1 if self.python_validator_accepted else 0,
            b"admission_ok": 1 if self.admission_accepted else 0,
            b"native_validation": 1 if self.native_validation_attempted else 0,
            b"native_parser": 1 if self.native_parser_attempted else 0,
            b"py_sig": 1 if self.signature_checked_by_python else 0,
            b"preserve_oracle": 1 if self.preserve_record_plane_oracle_memory else 0,
            b"preserve_substrate": 1 if self.preserve_substrate_reentry_memory else 0,
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
class RecordIngressReport:
    decision_kind: RecordIngressDecisionKind
    accepted: bool
    record_admitted: bool
    record_kind: str
    namespace: str
    record_key: str
    quarantine: bool
    watch: bool
    obligations: tuple[str, ...]
    capsule_digest: bytes
    substrate_reentry_digest: bytes
    record_plane_oracle_digest: bytes
    payload_digest: bytes
    family_count: int
    path_family_count: int

    @property
    def report_digest(self) -> bytes:
        return sha256(RECORD_INGRESS_DOMAIN + b":report:" + bencode({
            b"decision": self.decision_kind.value,
            b"accepted": 1 if self.accepted else 0,
            b"admitted": 1 if self.record_admitted else 0,
            b"kind": self.record_kind,
            b"namespace": self.namespace,
            b"key": self.record_key,
            b"quarantine": 1 if self.quarantine else 0,
            b"watch": 1 if self.watch else 0,
            b"obligations": list(self.obligations),
            b"capsule": self.capsule_digest,
            b"substrate": self.substrate_reentry_digest,
            b"oracle": self.record_plane_oracle_digest,
            b"payload": self.payload_digest,
            b"family_count": self.family_count,
            b"path_family_count": self.path_family_count,
        }))


def assess_record_ingress(
    substrate_reentry: object,
    record_plane_oracle: object,
    parse_report: object,
    validator_report: object,
    admission_report: object,
    capsule: RecordIngressCapsule,
    *,
    previous: RecordIngressCapsule | None = None,
    prior_capsule_digests: tuple[bytes, ...] = (),
    observed_families: tuple[str, ...] = (),
    observed_path_families: tuple[str, ...] = (),
    min_families: int = 2,
    min_path_families: int = 2,
) -> RecordIngressReport:
    families = set(observed_families or (capsule.family_id,))
    path_families = set(observed_path_families or (capsule.path_family_id,))

    def report(kind: RecordIngressDecisionKind, accepted: bool, quarantine: bool, watch: bool, obligations: tuple[str, ...]) -> RecordIngressReport:
        return RecordIngressReport(
            kind, accepted, accepted, capsule.record_kind, capsule.namespace, capsule.record_key,
            quarantine, watch, obligations, capsule.capsule_digest, capsule.substrate_reentry_digest,
            capsule.record_plane_oracle_digest, capsule.payload_digest, len(families), len(path_families)
        )

    if capsule.capsule_digest in prior_capsule_digests:
        return report(RecordIngressDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, True, False, ("record-ingress-replay",))
    if previous is not None:
        if capsule.sequence < previous.sequence:
            return report(RecordIngressDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, True, False, ("record-ingress-rollback",))
        if capsule.sequence == previous.sequence and capsule.capsule_digest != previous.capsule_digest:
            return report(RecordIngressDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK, False, True, False, ("record-ingress-same-sequence-fork",))
        if capsule.sequence > previous.sequence and capsule.previous_digest != previous.capsule_digest:
            return report(RecordIngressDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH, False, True, False, ("record-ingress-previous-link-mismatch",))
    if len(families) < min_families or len(path_families) < min_path_families:
        return report(RecordIngressDecisionKind.QUARANTINE_LOW_DIVERSITY, False, True, False, ("record-ingress-low-diversity",))
    if not getattr(substrate_reentry, "accepted", False) or not getattr(substrate_reentry, "substrate_reentered", False):
        return report(RecordIngressDecisionKind.HOLD_COMPONENT_NOT_READY, False, False, True, ("substrate-reentry-not-accepted",))
    if not getattr(record_plane_oracle, "accepted", False) or not getattr(record_plane_oracle, "python_record_truth", False):
        return report(RecordIngressDecisionKind.HOLD_COMPONENT_NOT_READY, False, False, True, ("record-plane-oracle-not-accepted",))
    if getattr(record_plane_oracle, "native_record_permission", False) or getattr(substrate_reentry, "native_permission_leak", False):
        return report(RecordIngressDecisionKind.QUARANTINE_NATIVE_PERMISSION_LEAK, False, True, False, ("native-record-permission-leak",))
    expected = (
        capsule.substrate_reentry_digest == getattr(substrate_reentry, "report_digest", b""),
        capsule.record_plane_oracle_digest == getattr(record_plane_oracle, "report_digest", b""),
        capsule.parse_report_digest == getattr(parse_report, "report_digest", b""),
        capsule.validator_report_digest == getattr(validator_report, "report_digest", b""),
        capsule.admission_report_digest == getattr(admission_report, "report_digest", b""),
    )
    if not all(expected):
        return report(RecordIngressDecisionKind.QUARANTINE_DIGEST_DRIFT, False, True, False, ("record-ingress-component-digest-drift",))
    if capsule.namespace not in ALLOWED_NAMESPACES or capsule.record_kind not in ALLOWED_RECORD_KINDS:
        return report(RecordIngressDecisionKind.QUARANTINE_SCOPE_OR_KIND_DRIFT, False, True, False, ("record-ingress-scope-or-kind-drift",))
    if capsule.value_size < 0 or capsule.value_size > capsule.max_value_size or capsule.ttl_seconds <= 0 or capsule.ttl_seconds > capsule.max_ttl_seconds:
        return report(RecordIngressDecisionKind.QUARANTINE_SIZE_OR_TTL, False, True, False, ("record-ingress-size-or-ttl",))
    if not capsule.canonical_wire or not capsule.untrusted_bytes_parsed_by_python or not getattr(parse_report, "accepted", False):
        return report(RecordIngressDecisionKind.QUARANTINE_PARSE_NOT_CANONICAL, False, True, False, ("record-ingress-parse-not-canonical",))
    if not capsule.python_validator_accepted or not getattr(validator_report, "accepted", False) or not capsule.signature_checked_by_python:
        return report(RecordIngressDecisionKind.QUARANTINE_VALIDATOR_REJECTED, False, True, False, ("record-ingress-validator-rejected",))
    if not capsule.admission_accepted or not getattr(admission_report, "accepted", False):
        return report(RecordIngressDecisionKind.QUARANTINE_ADMISSION_REJECTED, False, True, False, ("record-ingress-admission-rejected",))
    if capsule.native_validation_attempted or capsule.native_parser_attempted:
        return report(RecordIngressDecisionKind.QUARANTINE_NATIVE_PERMISSION_LEAK, False, True, False, ("record-ingress-native-attempt",))
    if not all((
        capsule.preserve_record_plane_oracle_memory,
        capsule.preserve_substrate_reentry_memory,
        capsule.preserve_mutable_head_memory,
        capsule.preserve_provider_false_memory,
        capsule.preserve_tombstone_memory,
        capsule.preserve_witness_memory,
        capsule.preserve_garden_refusal_memory,
    )):
        return report(RecordIngressDecisionKind.QUARANTINE_MEMORY_DROP, False, True, False, ("record-ingress-memory-drop",))
    return report(RecordIngressDecisionKind.ACCEPT_RECORD_INGRESS, True, False, False, ())
