"""rev0100 provider semantic proof join.

Provider records are routing claims.  This module keeps that distinction hard:
record ingress may accept a provider record, but provider truth requires a
challenge-bound, metadata-budgeted semantic proof and typed witness memory.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .bencode import bencode
from .ids import DOMAIN, sha256

PROVIDER_SEMANTICS_DOMAIN = DOMAIN + b":provider-semantics-v1:"


class ProviderSemanticsDecisionKind(str, Enum):
    ACCEPT_PROVIDER_SEMANTICS = "accept_provider_semantics"
    WATCH_USEFUL_REFUSAL = "watch_useful_refusal"
    HOLD_COMPONENT_NOT_READY = "hold_component_not_ready"
    QUARANTINE_NOT_PROVIDER_INGRESS = "quarantine_not_provider_ingress"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_METADATA_LEAK = "quarantine_metadata_leak"
    QUARANTINE_FALSE_PROVIDER = "quarantine_false_provider"
    QUARANTINE_STALE_OR_MISSING_PROOF = "quarantine_stale_or_missing_proof"
    QUARANTINE_MEMORY_DROP = "quarantine_memory_drop"
    QUARANTINE_REPLAY_OR_ROLLBACK = "quarantine_replay_or_rollback"
    QUARANTINE_SAME_SEQUENCE_FORK = "quarantine_same_sequence_fork"
    QUARANTINE_PREVIOUS_LINK_MISMATCH = "quarantine_previous_link_mismatch"
    QUARANTINE_LOW_DIVERSITY = "quarantine_low_diversity"


@dataclass(frozen=True)
class ProviderSemanticsCapsule:
    component: str
    profile: str
    namespace: str
    content_key_digest: bytes
    provider_destination_digest: bytes
    request_id: str
    sequence: int
    previous_digest: bytes
    record_ingress_digest: bytes
    provider_claim_digest: bytes
    proof_challenge_digest: bytes
    metadata_budget_digest: bytes
    witness_digest: bytes
    proof_result: str  # true, false, refused, stale, missing
    challenge_bound: bool
    digest_matches: bool
    signed_provider_claim: bool
    semantic_confirmation_required: bool
    metadata_budget_accepted: bool
    decoy_budget_accepted: bool
    raw_content_key_exposed: bool
    witness_preserved: bool
    preserve_provider_false_memory: bool
    preserve_witness_memory: bool
    preserve_metadata_budget_memory: bool
    preserve_tombstone_memory: bool
    family_id: str
    path_family_id: str
    note: str = ""

    @property
    def capsule_digest(self) -> bytes:
        return sha256(PROVIDER_SEMANTICS_DOMAIN + b":capsule:" + bencode({
            b"component": self.component,
            b"profile": self.profile,
            b"namespace": self.namespace,
            b"content_key": self.content_key_digest,
            b"destination": self.provider_destination_digest,
            b"request": self.request_id,
            b"seq": self.sequence,
            b"prev": self.previous_digest,
            b"ingress": self.record_ingress_digest,
            b"claim": self.provider_claim_digest,
            b"challenge": self.proof_challenge_digest,
            b"budget": self.metadata_budget_digest,
            b"witness": self.witness_digest,
            b"proof": self.proof_result,
            b"challenge_bound": 1 if self.challenge_bound else 0,
            b"digest_matches": 1 if self.digest_matches else 0,
            b"signed_claim": 1 if self.signed_provider_claim else 0,
            b"semantic_required": 1 if self.semantic_confirmation_required else 0,
            b"budget_ok": 1 if self.metadata_budget_accepted else 0,
            b"decoy_ok": 1 if self.decoy_budget_accepted else 0,
            b"raw_key": 1 if self.raw_content_key_exposed else 0,
            b"witness_preserved": 1 if self.witness_preserved else 0,
            b"preserve_false": 1 if self.preserve_provider_false_memory else 0,
            b"preserve_witness": 1 if self.preserve_witness_memory else 0,
            b"preserve_budget": 1 if self.preserve_metadata_budget_memory else 0,
            b"preserve_tombstone": 1 if self.preserve_tombstone_memory else 0,
            b"family": self.family_id,
            b"path_family": self.path_family_id,
            b"note": self.note,
        }))


@dataclass(frozen=True)
class ProviderSemanticsReport:
    decision_kind: ProviderSemanticsDecisionKind
    accepted: bool
    provider_semantically_confirmed: bool
    false_provider_pressure: bool
    useful_refusal: bool
    quarantine: bool
    watch: bool
    obligations: tuple[str, ...]
    capsule_digest: bytes
    record_ingress_digest: bytes
    content_key_digest: bytes
    provider_destination_digest: bytes
    family_count: int
    path_family_count: int

    @property
    def report_digest(self) -> bytes:
        return sha256(PROVIDER_SEMANTICS_DOMAIN + b":report:" + bencode({
            b"decision": self.decision_kind.value,
            b"accepted": 1 if self.accepted else 0,
            b"confirmed": 1 if self.provider_semantically_confirmed else 0,
            b"false_pressure": 1 if self.false_provider_pressure else 0,
            b"useful_refusal": 1 if self.useful_refusal else 0,
            b"quarantine": 1 if self.quarantine else 0,
            b"watch": 1 if self.watch else 0,
            b"obligations": list(self.obligations),
            b"capsule": self.capsule_digest,
            b"ingress": self.record_ingress_digest,
            b"content_key": self.content_key_digest,
            b"destination": self.provider_destination_digest,
            b"family_count": self.family_count,
            b"path_family_count": self.path_family_count,
        }))


def assess_provider_semantics(
    record_ingress: object,
    proof_challenge: object,
    metadata_budget: object,
    witness_report: object,
    capsule: ProviderSemanticsCapsule,
    *,
    previous: ProviderSemanticsCapsule | None = None,
    prior_capsule_digests: tuple[bytes, ...] = (),
    observed_families: tuple[str, ...] = (),
    observed_path_families: tuple[str, ...] = (),
    min_families: int = 2,
    min_path_families: int = 2,
) -> ProviderSemanticsReport:
    families = set(observed_families or (capsule.family_id,))
    path_families = set(observed_path_families or (capsule.path_family_id,))

    def report(kind: ProviderSemanticsDecisionKind, accepted: bool, false_pressure: bool, useful_refusal: bool, quarantine: bool, watch: bool, obligations: tuple[str, ...]) -> ProviderSemanticsReport:
        return ProviderSemanticsReport(
            kind, accepted, accepted, false_pressure, useful_refusal, quarantine, watch, obligations,
            capsule.capsule_digest, capsule.record_ingress_digest, capsule.content_key_digest,
            capsule.provider_destination_digest, len(families), len(path_families)
        )

    if capsule.capsule_digest in prior_capsule_digests:
        return report(ProviderSemanticsDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, False, False, True, False, ("provider-semantics-replay",))
    if previous is not None:
        if capsule.sequence < previous.sequence:
            return report(ProviderSemanticsDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, False, False, True, False, ("provider-semantics-rollback",))
        if capsule.sequence == previous.sequence and capsule.capsule_digest != previous.capsule_digest:
            return report(ProviderSemanticsDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK, False, False, False, True, False, ("provider-semantics-same-sequence-fork",))
        if capsule.sequence > previous.sequence and capsule.previous_digest != previous.capsule_digest:
            return report(ProviderSemanticsDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH, False, False, False, True, False, ("provider-semantics-prev-link",))
    if len(families) < min_families or len(path_families) < min_path_families:
        return report(ProviderSemanticsDecisionKind.QUARANTINE_LOW_DIVERSITY, False, False, False, True, False, ("provider-semantics-low-diversity",))
    if not getattr(record_ingress, "accepted", False) or not getattr(record_ingress, "record_admitted", False):
        return report(ProviderSemanticsDecisionKind.HOLD_COMPONENT_NOT_READY, False, False, False, False, True, ("provider-ingress-not-ready",))
    if getattr(record_ingress, "record_kind", "") != "provider":
        return report(ProviderSemanticsDecisionKind.QUARANTINE_NOT_PROVIDER_INGRESS, False, False, False, True, False, ("not-provider-ingress",))
    if not getattr(proof_challenge, "accepted", False) or not getattr(metadata_budget, "accepted", False) or not getattr(witness_report, "accepted", False):
        return report(ProviderSemanticsDecisionKind.HOLD_COMPONENT_NOT_READY, False, False, False, False, True, ("provider-proof-components-not-ready",))
    if (
        capsule.record_ingress_digest != getattr(record_ingress, "report_digest", b"") or
        capsule.proof_challenge_digest != getattr(proof_challenge, "report_digest", b"") or
        capsule.metadata_budget_digest != getattr(metadata_budget, "report_digest", b"") or
        capsule.witness_digest != getattr(witness_report, "report_digest", b"")
    ):
        return report(ProviderSemanticsDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, False, True, False, ("provider-semantics-digest-drift",))
    if capsule.raw_content_key_exposed or not capsule.metadata_budget_accepted or not capsule.decoy_budget_accepted:
        return report(ProviderSemanticsDecisionKind.QUARANTINE_METADATA_LEAK, False, False, False, True, False, ("provider-metadata-budget-or-raw-key",))
    if not all((capsule.witness_preserved, capsule.preserve_provider_false_memory, capsule.preserve_witness_memory, capsule.preserve_metadata_budget_memory, capsule.preserve_tombstone_memory)):
        return report(ProviderSemanticsDecisionKind.QUARANTINE_MEMORY_DROP, False, False, False, True, False, ("provider-semantics-memory-drop",))
    if capsule.proof_result == "refused":
        return report(ProviderSemanticsDecisionKind.WATCH_USEFUL_REFUSAL, False, False, True, False, True, ("provider-useful-refusal-backoff",))
    if capsule.proof_result in {"stale", "missing"} or not capsule.challenge_bound or not capsule.signed_provider_claim:
        return report(ProviderSemanticsDecisionKind.QUARANTINE_STALE_OR_MISSING_PROOF, False, False, False, True, False, ("provider-proof-stale-or-missing",))
    if capsule.proof_result == "false" or not capsule.digest_matches:
        return report(ProviderSemanticsDecisionKind.QUARANTINE_FALSE_PROVIDER, False, True, False, True, False, ("provider-semantic-false",))
    if capsule.proof_result != "true" or not capsule.semantic_confirmation_required:
        return report(ProviderSemanticsDecisionKind.QUARANTINE_STALE_OR_MISSING_PROOF, False, False, False, True, False, ("provider-semantic-proof-incomplete",))
    return report(ProviderSemanticsDecisionKind.ACCEPT_PROVIDER_SEMANTICS, True, False, False, False, False, ())
