"""rev0101 mutable-head placement after Python-owned record ingress.

A mutable DHT record that passed rev0100 ingress is still only a signed
observation.  This module models the next risky seam: placing that observation
into local mutable-head memory without allowing rollback, fork, tombstone, or
native-authority leaks to become local latestness.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .bencode import bencode
from .ids import DOMAIN, sha256

MUTABLE_PLACEMENT_DOMAIN = DOMAIN + b":mutable-placement-v1:"


class MutablePlacementDecisionKind(str, Enum):
    ACCEPT_MUTABLE_PLACEMENT = "accept_mutable_placement"
    HOLD_COMPONENT_NOT_READY = "hold_component_not_ready"
    HOLD_GAP_OR_WATCH = "hold_gap_or_watch"
    QUARANTINE_NOT_MUTABLE_INGRESS = "quarantine_not_mutable_ingress"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_TARGET_OR_SIGNATURE = "quarantine_target_or_signature"
    QUARANTINE_ROLLBACK = "quarantine_rollback"
    QUARANTINE_SAME_SEQUENCE_FORK = "quarantine_same_sequence_fork"
    QUARANTINE_LIVE_TOMBSTONE = "quarantine_live_tombstone"
    QUARANTINE_MEMORY_DROP = "quarantine_memory_drop"
    QUARANTINE_REPLAY_OR_ROLLBACK = "quarantine_replay_or_rollback"
    QUARANTINE_PREVIOUS_LINK_MISMATCH = "quarantine_previous_link_mismatch"
    QUARANTINE_LOW_DIVERSITY = "quarantine_low_diversity"


@dataclass(frozen=True)
class MutablePlacementCapsule:
    component: str
    profile: str
    mutable_key: str
    namespace: str
    request_id: str
    sequence: int
    previous_digest: bytes
    record_ingress_digest: bytes
    mutable_head_digest: bytes
    validator_report_digest: bytes
    witness_digest: bytes
    publisher_key_digest: bytes
    salt_digest: bytes
    computed_target_digest: bytes
    expected_target_digest: bytes
    record_sequence: int
    highest_seen_sequence: int
    previous_head_digest: bytes
    expected_previous_head_digest: bytes
    signature_valid: bool
    cas_ok: bool
    value_digest_matches: bool
    epoch_window_valid: bool
    same_sequence_fork_seen: bool
    rollback_seen: bool
    live_tombstone_seen: bool
    missing_previous_link: bool
    native_mutable_truth_attempted: bool
    preserve_head_memory: bool
    preserve_fork_memory: bool
    preserve_tombstone_memory: bool
    preserve_witness_memory: bool
    preserve_rollback_memory: bool
    family_id: str
    path_family_id: str
    note: str = ""

    @property
    def capsule_digest(self) -> bytes:
        return sha256(MUTABLE_PLACEMENT_DOMAIN + b":capsule:" + bencode({
            b"component": self.component,
            b"profile": self.profile,
            b"key": self.mutable_key,
            b"namespace": self.namespace,
            b"request": self.request_id,
            b"seq": self.sequence,
            b"prev": self.previous_digest,
            b"ingress": self.record_ingress_digest,
            b"head": self.mutable_head_digest,
            b"validator": self.validator_report_digest,
            b"witness": self.witness_digest,
            b"publisher": self.publisher_key_digest,
            b"salt": self.salt_digest,
            b"computed_target": self.computed_target_digest,
            b"expected_target": self.expected_target_digest,
            b"record_seq": self.record_sequence,
            b"highest_seen": self.highest_seen_sequence,
            b"prev_head": self.previous_head_digest,
            b"expected_prev_head": self.expected_previous_head_digest,
            b"signature": 1 if self.signature_valid else 0,
            b"cas": 1 if self.cas_ok else 0,
            b"value_digest": 1 if self.value_digest_matches else 0,
            b"epoch_window": 1 if self.epoch_window_valid else 0,
            b"same_seq_fork": 1 if self.same_sequence_fork_seen else 0,
            b"rollback_seen": 1 if self.rollback_seen else 0,
            b"tombstone": 1 if self.live_tombstone_seen else 0,
            b"missing_prev": 1 if self.missing_previous_link else 0,
            b"native_truth": 1 if self.native_mutable_truth_attempted else 0,
            b"preserve_head": 1 if self.preserve_head_memory else 0,
            b"preserve_fork": 1 if self.preserve_fork_memory else 0,
            b"preserve_tombstone": 1 if self.preserve_tombstone_memory else 0,
            b"preserve_witness": 1 if self.preserve_witness_memory else 0,
            b"preserve_rollback": 1 if self.preserve_rollback_memory else 0,
            b"family": self.family_id,
            b"path_family": self.path_family_id,
            b"note": self.note,
        }))


@dataclass(frozen=True)
class MutablePlacementReport:
    decision_kind: MutablePlacementDecisionKind
    accepted: bool
    mutable_observation_placed: bool
    latestness_claimed: bool
    quarantine: bool
    watch: bool
    obligations: tuple[str, ...]
    capsule_digest: bytes
    record_ingress_digest: bytes
    mutable_head_digest: bytes
    record_sequence: int
    family_count: int
    path_family_count: int

    @property
    def report_digest(self) -> bytes:
        return sha256(MUTABLE_PLACEMENT_DOMAIN + b":report:" + bencode({
            b"decision": self.decision_kind.value,
            b"accepted": 1 if self.accepted else 0,
            b"placed": 1 if self.mutable_observation_placed else 0,
            b"latestness": 1 if self.latestness_claimed else 0,
            b"quarantine": 1 if self.quarantine else 0,
            b"watch": 1 if self.watch else 0,
            b"obligations": list(self.obligations),
            b"capsule": self.capsule_digest,
            b"ingress": self.record_ingress_digest,
            b"head": self.mutable_head_digest,
            b"record_seq": self.record_sequence,
            b"family_count": self.family_count,
            b"path_family_count": self.path_family_count,
        }))


def assess_mutable_placement(
    record_ingress: object,
    validator_report: object,
    witness_report: object,
    capsule: MutablePlacementCapsule,
    *,
    previous: MutablePlacementCapsule | None = None,
    prior_capsule_digests: tuple[bytes, ...] = (),
    observed_families: tuple[str, ...] = (),
    observed_path_families: tuple[str, ...] = (),
    min_families: int = 2,
    min_path_families: int = 2,
) -> MutablePlacementReport:
    families = set(observed_families or (capsule.family_id,))
    path_families = set(observed_path_families or (capsule.path_family_id,))

    def report(kind: MutablePlacementDecisionKind, accepted: bool, quarantine: bool, watch: bool, obligations: tuple[str, ...]) -> MutablePlacementReport:
        return MutablePlacementReport(
            kind, accepted, accepted, False, quarantine, watch, obligations,
            capsule.capsule_digest, capsule.record_ingress_digest, capsule.mutable_head_digest,
            capsule.record_sequence, len(families), len(path_families)
        )

    if capsule.capsule_digest in prior_capsule_digests:
        return report(MutablePlacementDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, True, False, ("mutable-placement-replay",))
    if previous is not None:
        if capsule.sequence < previous.sequence:
            return report(MutablePlacementDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, True, False, ("mutable-placement-rollback",))
        if capsule.sequence == previous.sequence and capsule.capsule_digest != previous.capsule_digest:
            return report(MutablePlacementDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK, False, True, False, ("mutable-placement-same-sequence-fork",))
        if capsule.sequence > previous.sequence and capsule.previous_digest != previous.capsule_digest:
            return report(MutablePlacementDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH, False, True, False, ("mutable-placement-previous-link-mismatch",))
    if len(families) < min_families or len(path_families) < min_path_families:
        return report(MutablePlacementDecisionKind.QUARANTINE_LOW_DIVERSITY, False, True, False, ("mutable-placement-low-diversity",))
    if not getattr(record_ingress, "accepted", False) or not getattr(record_ingress, "record_admitted", False):
        return report(MutablePlacementDecisionKind.HOLD_COMPONENT_NOT_READY, False, False, True, ("mutable-record-ingress-not-ready",))
    if getattr(record_ingress, "record_kind", "") != "mutable":
        return report(MutablePlacementDecisionKind.QUARANTINE_NOT_MUTABLE_INGRESS, False, True, False, ("not-mutable-ingress",))
    if not getattr(validator_report, "accepted", False) or not getattr(witness_report, "accepted", False):
        return report(MutablePlacementDecisionKind.HOLD_COMPONENT_NOT_READY, False, False, True, ("mutable-validator-or-witness-not-ready",))
    if capsule.record_ingress_digest != getattr(record_ingress, "report_digest", b"") or capsule.validator_report_digest != getattr(validator_report, "report_digest", b"") or capsule.witness_digest != getattr(witness_report, "report_digest", b""):
        return report(MutablePlacementDecisionKind.QUARANTINE_DIGEST_DRIFT, False, True, False, ("mutable-placement-component-digest-drift",))
    if capsule.native_mutable_truth_attempted:
        return report(MutablePlacementDecisionKind.QUARANTINE_TARGET_OR_SIGNATURE, False, True, False, ("native-mutable-truth-attempt",))
    if capsule.computed_target_digest != capsule.expected_target_digest or not capsule.signature_valid or not capsule.value_digest_matches or not capsule.epoch_window_valid:
        return report(MutablePlacementDecisionKind.QUARANTINE_TARGET_OR_SIGNATURE, False, True, False, ("mutable-target-signature-or-value-drift",))
    if not capsule.cas_ok or capsule.rollback_seen or capsule.record_sequence < capsule.highest_seen_sequence:
        return report(MutablePlacementDecisionKind.QUARANTINE_ROLLBACK, False, True, False, ("mutable-rollback-or-cas-failure",))
    if capsule.same_sequence_fork_seen:
        return report(MutablePlacementDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK, False, True, False, ("mutable-head-fork",))
    if capsule.live_tombstone_seen:
        return report(MutablePlacementDecisionKind.QUARANTINE_LIVE_TOMBSTONE, False, True, False, ("mutable-live-tombstone",))
    if capsule.missing_previous_link or capsule.previous_head_digest != capsule.expected_previous_head_digest:
        return report(MutablePlacementDecisionKind.HOLD_GAP_OR_WATCH, False, False, True, ("mutable-previous-link-gap",))
    if not all((capsule.preserve_head_memory, capsule.preserve_fork_memory, capsule.preserve_tombstone_memory, capsule.preserve_witness_memory, capsule.preserve_rollback_memory)):
        return report(MutablePlacementDecisionKind.QUARANTINE_MEMORY_DROP, False, True, False, ("mutable-placement-memory-drop",))
    return report(MutablePlacementDecisionKind.ACCEPT_MUTABLE_PLACEMENT, True, False, False, ())
