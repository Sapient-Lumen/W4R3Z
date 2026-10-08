"""Typed claim bundles for joining evidence without blurring evidence roles.

A DHT client will often receive a convenient packet of "proof": provider
proofs, witness receipts, tombstones, custody facts, and mutable-head facts.
Bundling is useful for latency and garden service, but it is also dangerous:
valid evidence from unrelated scopes can be mixed together, one family can flood
a bundle, and positive availability can be paired with a live tombstone.

This module keeps bundles local and typed.  A valid signed bundle is still not
truth; it is a compact observation container that must pass scope, family,
conflict, freshness, and role checks before downstream code may spend work on it.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .evidencegc import EvidenceItem, EvidenceKind
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256

CLAIM_BUNDLE_DOMAIN = DOMAIN + b":claim-bundle-v1:"


class ClaimBundleDecisionKind(str, Enum):
    ACCEPT_BUNDLE = "accept_bundle"
    REJECT_BAD_SIGNATURE = "reject_bad_signature"
    REJECT_TIME_WINDOW = "reject_time_window"
    QUARANTINE_SCOPE_MIX = "quarantine_scope_mix"
    QUARANTINE_FAMILY_MONOCULTURE = "quarantine_family_monoculture"
    QUARANTINE_CONFLICTING_CLAIMS = "quarantine_conflicting_claims"
    CONTINUE_EMPTY_BUNDLE = "continue_empty_bundle"


POSITIVE_KINDS = frozenset({
    EvidenceKind.PROVIDER_TRUE,
    EvidenceKind.MUTABLE_LATEST,
    EvidenceKind.CUSTODY_PROOF,
})

NEGATIVE_KINDS = frozenset({
    EvidenceKind.PROVIDER_FALSE,
    EvidenceKind.MUTABLE_STALE,
    EvidenceKind.MUTABLE_FORK,
    EvidenceKind.TOMBSTONE,
    EvidenceKind.CAPABILITY_REVOCATION,
})


@dataclass(frozen=True)
class ClaimBundlePolicy:
    min_source_families: int = 2
    min_path_families: int = 2
    allow_positive_with_useful_refusal: bool = True
    max_items: int = 32

    def validate(self) -> None:
        if self.min_source_families <= 0 or self.min_path_families <= 0 or self.max_items <= 0:
            raise ValueError("claim bundle policy invalid")


@dataclass(frozen=True)
class ClaimBundle:
    scope_id: bytes
    bundle_sequence: int
    issued_at: int
    expires_at: int
    bundler_public_key: bytes
    evidence: tuple[EvidenceItem, ...]
    signature: bytes = b""

    def __post_init__(self) -> None:
        if len(self.scope_id) != 32 or len(self.bundler_public_key) != 32:
            raise ValueError("claim bundle scope/bundler key must be 32 bytes")
        if self.bundle_sequence < 0 or self.expires_at <= self.issued_at:
            raise ValueError("claim bundle counters invalid")

    @classmethod
    def create(
        cls,
        *,
        bundler: DhtKeypair,
        scope_id: bytes,
        bundle_sequence: int,
        evidence: Iterable[EvidenceItem],
        issued_at: int,
        ttl: int = 600,
    ) -> "ClaimBundle":
        if ttl <= 0:
            raise ValueError("claim bundle ttl must be positive")
        unsigned = cls(
            scope_id=scope_id,
            bundle_sequence=bundle_sequence,
            issued_at=issued_at,
            expires_at=issued_at + ttl,
            bundler_public_key=bundler.public_key_bytes,
            evidence=tuple(evidence),
        )
        return replace(unsigned, signature=bundler.sign(unsigned.unsigned_payload()))

    @property
    def bundle_digest(self) -> bytes:
        return sha256(CLAIM_BUNDLE_DOMAIN + b":bundle:" + self.unsigned_payload() + self.signature)

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"scope_id": self.scope_id,
            b"bundle_sequence": self.bundle_sequence,
            b"issued_at": self.issued_at,
            b"expires_at": self.expires_at,
            b"bundler_public_key": self.bundler_public_key,
            b"evidence": [item.digest for item in self.evidence],
        }

    def unsigned_payload(self) -> bytes:
        return CLAIM_BUNDLE_DOMAIN + b":bundle-unsigned:" + bencode(self.unsigned_bvalue())

    def verify(self, *, now: int) -> bool:
        if now < self.issued_at or now >= self.expires_at:
            return False
        return verify_signature(self.bundler_public_key, self.unsigned_payload(), self.signature)


@dataclass(frozen=True)
class ClaimBundleDecision:
    kind: ClaimBundleDecisionKind
    accept: bool
    reason: str


@dataclass(frozen=True)
class ClaimBundleReport:
    bundle_digest: bytes
    decision: ClaimBundleDecision
    source_families: tuple[str, ...]
    path_families: tuple[str, ...]
    positive_count: int
    negative_count: int
    quarantine_evidence: tuple[bytes, ...]
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision.kind.value.startswith("quarantine_")


def _report(bundle: ClaimBundle, decision: ClaimBundleDecision, *, quarantine: Iterable[bytes] = ()) -> ClaimBundleReport:
    source_families = tuple(sorted({item.source_family for item in bundle.evidence}))
    path_families = tuple(sorted({item.path_family for item in bundle.evidence}))
    positive_count = sum(1 for item in bundle.evidence if item.kind in POSITIVE_KINDS)
    negative_count = sum(1 for item in bundle.evidence if item.kind in NEGATIVE_KINDS)
    quarantine_tuple = tuple(sorted(quarantine))
    digest = sha256(CLAIM_BUNDLE_DOMAIN + b":report:" + bencode({
        b"bundle": bundle.bundle_digest,
        b"decision": decision.kind.value,
        b"source_families": list(source_families),
        b"path_families": list(path_families),
        b"positive_count": positive_count,
        b"negative_count": negative_count,
        b"quarantine": quarantine_tuple,
    }))
    return ClaimBundleReport(bundle.bundle_digest, decision, source_families, path_families, positive_count, negative_count, quarantine_tuple, digest)


def assess_claim_bundle(bundle: ClaimBundle, *, policy: ClaimBundlePolicy | None = None, now: int) -> ClaimBundleReport:
    policy = policy or ClaimBundlePolicy()
    policy.validate()
    if not bundle.verify(now=now):
        # Distinguish expired from bad signature for tests and future UI.
        if not (bundle.issued_at <= now < bundle.expires_at):
            return _report(bundle, ClaimBundleDecision(ClaimBundleDecisionKind.REJECT_TIME_WINDOW, False, "claim bundle is outside its validity window"))
        return _report(bundle, ClaimBundleDecision(ClaimBundleDecisionKind.REJECT_BAD_SIGNATURE, False, "claim bundle signature is invalid"))
    if not bundle.evidence:
        return _report(bundle, ClaimBundleDecision(ClaimBundleDecisionKind.CONTINUE_EMPTY_BUNDLE, False, "bundle contained no evidence"))
    if len(bundle.evidence) > policy.max_items:
        return _report(bundle, ClaimBundleDecision(ClaimBundleDecisionKind.QUARANTINE_CONFLICTING_CLAIMS, False, "bundle exceeded local item cap"), quarantine=(item.digest for item in bundle.evidence[policy.max_items:]))

    scope_mix = [item for item in bundle.evidence if item.scope_id != bundle.scope_id]
    if scope_mix:
        return _report(bundle, ClaimBundleDecision(ClaimBundleDecisionKind.QUARANTINE_SCOPE_MIX, False, "bundle mixed evidence from multiple scopes"), quarantine=(item.digest for item in scope_mix))

    source_families = {item.source_family for item in bundle.evidence}
    path_families = {item.path_family for item in bundle.evidence}
    if len(source_families) < policy.min_source_families or len(path_families) < policy.min_path_families:
        return _report(bundle, ClaimBundleDecision(ClaimBundleDecisionKind.QUARANTINE_FAMILY_MONOCULTURE, False, "bundle evidence is dominated by too few source/path families"), quarantine=(item.digest for item in bundle.evidence))

    positive = [item for item in bundle.evidence if item.kind in POSITIVE_KINDS]
    negative = [item for item in bundle.evidence if item.kind in NEGATIVE_KINDS]
    live_tombs = [item for item in negative if item.kind in {EvidenceKind.TOMBSTONE, EvidenceKind.CAPABILITY_REVOCATION} and item.issued_at <= now < item.expires_at]
    if positive and live_tombs:
        return _report(bundle, ClaimBundleDecision(ClaimBundleDecisionKind.QUARANTINE_CONFLICTING_CLAIMS, False, "positive availability was bundled with live tombstone/revocation evidence"), quarantine=tuple(item.digest for item in positive + live_tombs))

    seen_by_kind_seq: dict[tuple[EvidenceKind, int], bytes] = {}
    conflicts: list[EvidenceItem] = []
    for item in bundle.evidence:
        key = (item.kind, item.sequence)
        prior = seen_by_kind_seq.get(key)
        if prior is not None and prior != item.object_digest and item.kind in {EvidenceKind.MUTABLE_LATEST, EvidenceKind.MUTABLE_FORK, EvidenceKind.TOMBSTONE, EvidenceKind.CAPABILITY_REVOCATION}:
            conflicts.append(item)
        else:
            seen_by_kind_seq.setdefault(key, item.object_digest)
    if conflicts:
        return _report(bundle, ClaimBundleDecision(ClaimBundleDecisionKind.QUARANTINE_CONFLICTING_CLAIMS, False, "same kind/sequence carried conflicting digests inside bundle"), quarantine=(item.digest for item in conflicts))

    return _report(bundle, ClaimBundleDecision(ClaimBundleDecisionKind.ACCEPT_BUNDLE, True, "bundle is signed, scoped, diverse, and non-conflicting"))
