"""rev0101 provider-index bucket admission after provider semantics.

Provider semantics prove only that a claim survived a local challenge.  This
module decides whether that claim may enter a local provider-index bucket without
becoming content truth or unbounded storage pressure.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .bencode import bencode
from .ids import DOMAIN, sha256

PROVIDER_BUCKET_DOMAIN = DOMAIN + b":provider-bucket-v1:"
ALLOWED_BUCKET_PURPOSES = {"provider_index", "garden_reprovide", "hot_cache"}


class ProviderBucketDecisionKind(str, Enum):
    ACCEPT_PROVIDER_BUCKET = "accept_provider_bucket"
    HOLD_COMPONENT_NOT_READY = "hold_component_not_ready"
    HOLD_BUCKET_FULL_TO_SWEEP = "hold_bucket_full_to_sweep"
    HOLD_USEFUL_REFUSAL_BACKOFF = "hold_useful_refusal_backoff"
    QUARANTINE_FALSE_OR_UNPROVEN_PROVIDER = "quarantine_false_or_unproven_provider"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_TTL_OR_REGION = "quarantine_ttl_or_region"
    QUARANTINE_CONTENT_STORAGE_ATTEMPT = "quarantine_content_storage_attempt"
    QUARANTINE_MEMORY_DROP = "quarantine_memory_drop"
    QUARANTINE_REPLAY_OR_ROLLBACK = "quarantine_replay_or_rollback"
    QUARANTINE_SAME_SEQUENCE_FORK = "quarantine_same_sequence_fork"
    QUARANTINE_PREVIOUS_LINK_MISMATCH = "quarantine_previous_link_mismatch"
    QUARANTINE_LOW_DIVERSITY = "quarantine_low_diversity"


@dataclass(frozen=True)
class ProviderBucketCapsule:
    component: str
    profile: str
    bucket_id: str
    purpose: str
    request_id: str
    sequence: int
    previous_digest: bytes
    provider_semantics_digest: bytes
    region_digest: bytes
    content_key_digest: bytes
    provider_destination_digest: bytes
    index_entry_digest: bytes
    ttl_seconds: int
    max_ttl_seconds: int
    now: int
    expires_at: int
    current_bucket_count: int
    bucket_capacity: int
    semantic_result: str
    useful_refusal_seen: bool
    false_provider_seen: bool
    live_tombstone_seen: bool
    content_payload_stored: bool
    provider_claim_only: bool
    preserve_provider_false_memory: bool
    preserve_tombstone_memory: bool
    preserve_metadata_budget_memory: bool
    preserve_region_ledger_memory: bool
    source_family_id: str
    provider_family_id: str
    path_family_id: str
    note: str = ""

    @property
    def capsule_digest(self) -> bytes:
        return sha256(PROVIDER_BUCKET_DOMAIN + b":capsule:" + bencode({
            b"component": self.component,
            b"profile": self.profile,
            b"bucket": self.bucket_id,
            b"purpose": self.purpose,
            b"request": self.request_id,
            b"seq": self.sequence,
            b"prev": self.previous_digest,
            b"semantics": self.provider_semantics_digest,
            b"region": self.region_digest,
            b"content_key": self.content_key_digest,
            b"destination": self.provider_destination_digest,
            b"entry": self.index_entry_digest,
            b"ttl": self.ttl_seconds,
            b"max_ttl": self.max_ttl_seconds,
            b"now": self.now,
            b"expires": self.expires_at,
            b"count": self.current_bucket_count,
            b"capacity": self.bucket_capacity,
            b"semantic_result": self.semantic_result,
            b"useful_refusal": 1 if self.useful_refusal_seen else 0,
            b"false_provider": 1 if self.false_provider_seen else 0,
            b"tombstone": 1 if self.live_tombstone_seen else 0,
            b"payload_stored": 1 if self.content_payload_stored else 0,
            b"claim_only": 1 if self.provider_claim_only else 0,
            b"preserve_false": 1 if self.preserve_provider_false_memory else 0,
            b"preserve_tombstone": 1 if self.preserve_tombstone_memory else 0,
            b"preserve_budget": 1 if self.preserve_metadata_budget_memory else 0,
            b"preserve_region": 1 if self.preserve_region_ledger_memory else 0,
            b"source_family": self.source_family_id,
            b"provider_family": self.provider_family_id,
            b"path_family": self.path_family_id,
            b"note": self.note,
        }))


@dataclass(frozen=True)
class ProviderBucketReport:
    decision_kind: ProviderBucketDecisionKind
    accepted: bool
    provider_indexed: bool
    content_truth_claimed: bool
    quarantine: bool
    watch: bool
    obligations: tuple[str, ...]
    capsule_digest: bytes
    provider_semantics_digest: bytes
    region_digest: bytes
    index_entry_digest: bytes
    source_family_count: int
    provider_family_count: int
    path_family_count: int

    @property
    def report_digest(self) -> bytes:
        return sha256(PROVIDER_BUCKET_DOMAIN + b":report:" + bencode({
            b"decision": self.decision_kind.value,
            b"accepted": 1 if self.accepted else 0,
            b"indexed": 1 if self.provider_indexed else 0,
            b"truth": 1 if self.content_truth_claimed else 0,
            b"quarantine": 1 if self.quarantine else 0,
            b"watch": 1 if self.watch else 0,
            b"obligations": list(self.obligations),
            b"capsule": self.capsule_digest,
            b"semantics": self.provider_semantics_digest,
            b"region": self.region_digest,
            b"entry": self.index_entry_digest,
            b"source_families": self.source_family_count,
            b"provider_families": self.provider_family_count,
            b"path_families": self.path_family_count,
        }))


def assess_provider_bucket(
    provider_semantics: object,
    capsule: ProviderBucketCapsule,
    *,
    previous: ProviderBucketCapsule | None = None,
    prior_capsule_digests: tuple[bytes, ...] = (),
    observed_source_families: tuple[str, ...] = (),
    observed_provider_families: tuple[str, ...] = (),
    observed_path_families: tuple[str, ...] = (),
    min_source_families: int = 2,
    min_provider_families: int = 2,
    min_path_families: int = 2,
) -> ProviderBucketReport:
    source_families = set(observed_source_families or (capsule.source_family_id,))
    provider_families = set(observed_provider_families or (capsule.provider_family_id,))
    path_families = set(observed_path_families or (capsule.path_family_id,))

    def report(kind: ProviderBucketDecisionKind, accepted: bool, quarantine: bool, watch: bool, obligations: tuple[str, ...]) -> ProviderBucketReport:
        return ProviderBucketReport(
            kind, accepted, accepted, False, quarantine, watch, obligations,
            capsule.capsule_digest, capsule.provider_semantics_digest, capsule.region_digest,
            capsule.index_entry_digest, len(source_families), len(provider_families), len(path_families)
        )

    if capsule.capsule_digest in prior_capsule_digests:
        return report(ProviderBucketDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, True, False, ("provider-bucket-replay",))
    if previous is not None:
        if capsule.sequence < previous.sequence:
            return report(ProviderBucketDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, True, False, ("provider-bucket-rollback",))
        if capsule.sequence == previous.sequence and capsule.capsule_digest != previous.capsule_digest:
            return report(ProviderBucketDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK, False, True, False, ("provider-bucket-same-sequence-fork",))
        if capsule.sequence > previous.sequence and capsule.previous_digest != previous.capsule_digest:
            return report(ProviderBucketDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH, False, True, False, ("provider-bucket-previous-link-mismatch",))
    if len(source_families) < min_source_families or len(provider_families) < min_provider_families or len(path_families) < min_path_families:
        return report(ProviderBucketDecisionKind.QUARANTINE_LOW_DIVERSITY, False, True, False, ("provider-bucket-low-diversity",))
    if not getattr(provider_semantics, "accepted", False):
        return report(ProviderBucketDecisionKind.HOLD_COMPONENT_NOT_READY, False, False, True, ("provider-semantics-not-ready",))
    if capsule.provider_semantics_digest != getattr(provider_semantics, "report_digest", b""):
        return report(ProviderBucketDecisionKind.QUARANTINE_DIGEST_DRIFT, False, True, False, ("provider-bucket-semantics-digest-drift",))
    if capsule.semantic_result != "true" or capsule.false_provider_seen or capsule.live_tombstone_seen:
        return report(ProviderBucketDecisionKind.QUARANTINE_FALSE_OR_UNPROVEN_PROVIDER, False, True, False, ("provider-false-unproven-or-tombstoned",))
    if capsule.useful_refusal_seen:
        return report(ProviderBucketDecisionKind.HOLD_USEFUL_REFUSAL_BACKOFF, False, False, True, ("provider-useful-refusal-backoff",))
    if capsule.purpose not in ALLOWED_BUCKET_PURPOSES or capsule.ttl_seconds <= 0 or capsule.ttl_seconds > capsule.max_ttl_seconds or capsule.expires_at <= capsule.now:
        return report(ProviderBucketDecisionKind.QUARANTINE_TTL_OR_REGION, False, True, False, ("provider-bucket-ttl-or-purpose-drift",))
    if len(capsule.region_digest) != 32 or len(capsule.content_key_digest) != 32 or len(capsule.provider_destination_digest) != 32:
        return report(ProviderBucketDecisionKind.QUARANTINE_TTL_OR_REGION, False, True, False, ("provider-bucket-region-or-digest-drift",))
    if capsule.content_payload_stored or not capsule.provider_claim_only:
        return report(ProviderBucketDecisionKind.QUARANTINE_CONTENT_STORAGE_ATTEMPT, False, True, False, ("provider-bucket-content-storage-attempt",))
    if capsule.current_bucket_count >= capsule.bucket_capacity:
        return report(ProviderBucketDecisionKind.HOLD_BUCKET_FULL_TO_SWEEP, False, False, True, ("provider-bucket-sweep-required",))
    if not all((capsule.preserve_provider_false_memory, capsule.preserve_tombstone_memory, capsule.preserve_metadata_budget_memory, capsule.preserve_region_ledger_memory)):
        return report(ProviderBucketDecisionKind.QUARANTINE_MEMORY_DROP, False, True, False, ("provider-bucket-memory-drop",))
    return report(ProviderBucketDecisionKind.ACCEPT_PROVIDER_BUCKET, True, False, False, ())
