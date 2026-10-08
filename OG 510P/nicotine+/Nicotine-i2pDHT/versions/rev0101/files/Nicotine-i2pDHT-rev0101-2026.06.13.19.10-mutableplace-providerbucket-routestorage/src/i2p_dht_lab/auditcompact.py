"""Compact audit statements without dropping refute/fork evidence.

rev0048 created local audit receipts for public bridge shadow side effects.  A
future node cannot keep every receipt forever or ship every receipt with every
publication dry-run.  rev0049 therefore adds a compact audit bundle, but treats
compaction as a dangerous boundary: a compact statement is only useful if it
preserves the receipt digests that carry negative/refuting evidence and any
same-family fork evidence.

This module is intentionally small and local.  It does not create a global audit
log, quorum, or transparency system.  It only makes the "summary did not erase
bad news" claim executable.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .auditquorum import AuditReceipt, AuditReceiptKind, AuditQuorumReport
from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST

AUDIT_COMPACT_DOMAIN = DOMAIN + b":audit-compact-v1:"

NEGATIVE_RECEIPT_KINDS = frozenset({
    AuditReceiptKind.STALE_PUBLIC_RECORD,
    AuditReceiptKind.PAYLOAD_MISMATCH,
    AuditReceiptKind.REDRESS_GAP,
})


class AuditCompactDecisionKind(str, Enum):
    ACCEPT_COMPACT = "accept_compact"
    ACCEPT_WITH_WATCH = "accept_with_watch"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    EMPTY_NO_RECEIPTS = "empty_no_receipts"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_EXPIRED_OR_FUTURE = "quarantine_expired_or_future"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_PROFILE_DRIFT = "quarantine_profile_drift"
    QUARANTINE_SERVICE_DRIFT = "quarantine_service_drift"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_REQUEST_DRIFT = "quarantine_request_drift"
    QUARANTINE_SHADOW_DIGEST_DRIFT = "quarantine_shadow_digest_drift"
    QUARANTINE_PAYLOAD_DIGEST_DRIFT = "quarantine_payload_digest_drift"
    QUARANTINE_QUORUM_DIGEST_DRIFT = "quarantine_quorum_digest_drift"
    QUARANTINE_RECEIPT_DIGEST_DRIFT = "quarantine_receipt_digest_drift"
    QUARANTINE_DROPPED_REFUTE_EVIDENCE = "quarantine_dropped_refute_evidence"
    QUARANTINE_DROPPED_FORK_EVIDENCE = "quarantine_dropped_fork_evidence"


@dataclass(frozen=True)
class AuditCompactBundle:
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    bridge_shadow_digest: bytes
    public_payload_digest: bytes
    audit_quorum_digest: bytes
    positive_receipt_digests: tuple[bytes, ...]
    watch_receipt_digests: tuple[bytes, ...]
    refute_receipt_digests: tuple[bytes, ...]
    fork_evidence_digests: tuple[bytes, ...]
    family_count: int
    path_family_count: int
    sequence: int
    previous_bundle_digest: bytes
    issued_at: int
    expires_at: int
    family_id: str
    path_family: str
    signer_public_key: bytes
    signature: bytes = b""

    def __post_init__(self) -> None:
        if not self.profile_id or not self.service_name or not self.family_id or not self.path_family:
            raise ValueError("audit compact bundle needs profile/service/family/path")
        if self.sequence < 0:
            raise ValueError("sequence must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("expires_at must follow issued_at")
        for name, value in (
            ("scope_digest", self.scope_digest),
            ("request_digest", self.request_digest),
            ("bridge_shadow_digest", self.bridge_shadow_digest),
            ("public_payload_digest", self.public_payload_digest),
            ("audit_quorum_digest", self.audit_quorum_digest),
            ("previous_bundle_digest", self.previous_bundle_digest),
            ("signer_public_key", self.signer_public_key),
        ):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        for seq_name in ("positive_receipt_digests", "watch_receipt_digests", "refute_receipt_digests", "fork_evidence_digests"):
            for digest in getattr(self, seq_name):
                if len(digest) != 32:
                    raise ValueError(f"{seq_name} must contain 32-byte digests")
        if self.signature and len(self.signature) != 64:
            raise ValueError("signature must be empty or Ed25519-sized")

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"shadow": self.bridge_shadow_digest,
            b"payload": self.public_payload_digest,
            b"quorum": self.audit_quorum_digest,
            b"positive": list(self.positive_receipt_digests),
            b"watch": list(self.watch_receipt_digests),
            b"refute": list(self.refute_receipt_digests),
            b"fork": list(self.fork_evidence_digests),
            b"family_count": self.family_count,
            b"path_count": self.path_family_count,
            b"seq": self.sequence,
            b"prev": self.previous_bundle_digest,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"family": self.family_id,
            b"path_family": self.path_family,
            b"signer": self.signer_public_key,
        }

    def signature_payload(self) -> bytes:
        return AUDIT_COMPACT_DOMAIN + b":bundle-sig:" + bencode(self.unsigned_bvalue())

    @property
    def bundle_core_digest(self) -> bytes:
        return sha256(AUDIT_COMPACT_DOMAIN + b":bundle-core:" + bencode(self.unsigned_bvalue()))

    @property
    def bundle_digest(self) -> bytes:
        return sha256(AUDIT_COMPACT_DOMAIN + b":bundle-digest:" + self.signature_payload() + self.signature)

    def verifies(self) -> bool:
        return verify_signature(self.signer_public_key, self.signature_payload(), self.signature)

    def live(self, now: int) -> bool:
        return self.issued_at <= now < self.expires_at


@dataclass(frozen=True)
class AuditCompactReport:
    decision_kind: AuditCompactDecisionKind
    accept: bool
    watch: bool
    reason: str
    accepted_bundle_digest: bytes
    bundle_digests: tuple[bytes, ...]
    refute_digests: tuple[bytes, ...]
    fork_evidence_digests: tuple[bytes, ...]
    family_count: int
    path_family_count: int
    highest_sequence: int
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _receipt_sets(receipts: Iterable[AuditReceipt]) -> tuple[tuple[bytes, ...], tuple[bytes, ...], tuple[bytes, ...], tuple[bytes, ...], int, int]:
    receipt_tuple = tuple(sorted(receipts, key=lambda item: item.receipt_digest))
    positive: list[bytes] = []
    watch: list[bytes] = []
    refute: list[bytes] = []
    family_to_payloads: dict[str, set[bytes]] = {}
    family_to_digests: dict[str, list[bytes]] = {}
    for receipt in receipt_tuple:
        digest = receipt.receipt_digest
        if receipt.accepted and receipt.kind not in NEGATIVE_RECEIPT_KINDS:
            positive.append(digest)
        if receipt.watch:
            watch.append(digest)
        if not receipt.accepted or receipt.kind in NEGATIVE_RECEIPT_KINDS:
            refute.append(digest)
        family_to_payloads.setdefault(receipt.family_id, set()).add(receipt.public_payload_digest)
        family_to_digests.setdefault(receipt.family_id, []).append(digest)
    fork: list[bytes] = []
    for family, payloads in family_to_payloads.items():
        if len(payloads) > 1:
            fork.extend(family_to_digests[family])
    return (
        tuple(sorted(set(positive))),
        tuple(sorted(set(watch))),
        tuple(sorted(set(refute))),
        tuple(sorted(set(fork))),
        len({item.family_id for item in receipt_tuple}),
        len({item.path_family for item in receipt_tuple}),
    )


def make_audit_compact_bundle(
    *,
    keypair: DhtKeypair,
    receipts: Iterable[AuditReceipt],
    audit_quorum: AuditQuorumReport,
    sequence: int,
    previous_bundle_digest: bytes = ZERO_DIGEST,
    issued_at: int,
    expires_at: int,
    family_id: str,
    path_family: str,
    omit_refute_digests: Iterable[bytes] = (),
    omit_fork_digests: Iterable[bytes] = (),
) -> AuditCompactBundle:
    positive, watch, refute, fork, families, paths = _receipt_sets(receipts)
    omit_refute = set(omit_refute_digests)
    omit_fork = set(omit_fork_digests)
    unsigned = AuditCompactBundle(
        profile_id=audit_quorum.profile_id,
        service_name=audit_quorum.service_name,
        scope_digest=audit_quorum.scope_digest,
        request_digest=audit_quorum.request_digest,
        bridge_shadow_digest=audit_quorum.bridge_shadow_digest,
        public_payload_digest=audit_quorum.public_payload_digest,
        audit_quorum_digest=audit_quorum.report_digest,
        positive_receipt_digests=positive,
        watch_receipt_digests=watch,
        refute_receipt_digests=tuple(item for item in refute if item not in omit_refute),
        fork_evidence_digests=tuple(item for item in fork if item not in omit_fork),
        family_count=families,
        path_family_count=paths,
        sequence=sequence,
        previous_bundle_digest=previous_bundle_digest,
        issued_at=issued_at,
        expires_at=expires_at,
        family_id=family_id,
        path_family=path_family,
        signer_public_key=keypair.public_key_bytes,
    )
    return replace(unsigned, signature=keypair.sign(unsigned.signature_payload()))


def _report(kind: AuditCompactDecisionKind, accept: bool, watch: bool, reason: str, *, bundles: Iterable[AuditCompactBundle], selected: AuditCompactBundle | None = None, refutes: Iterable[bytes] = (), forks: Iterable[bytes] = ()) -> AuditCompactReport:
    bundle_tuple = tuple(sorted(bundles, key=lambda item: (item.sequence, item.bundle_digest)))
    bundle_digests = tuple(item.bundle_digest for item in bundle_tuple)
    refute_tuple = tuple(sorted(set(refutes)))
    fork_tuple = tuple(sorted(set(forks)))
    accepted = selected.bundle_digest if selected and accept else ZERO_DIGEST
    families = len({item.family_id for item in bundle_tuple})
    paths = len({item.path_family for item in bundle_tuple})
    highest = selected.sequence if selected else max((item.sequence for item in bundle_tuple), default=-1)
    digest = sha256(AUDIT_COMPACT_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"reason": reason,
        b"accepted": accepted,
        b"bundles": list(bundle_digests),
        b"refutes": list(refute_tuple),
        b"forks": list(fork_tuple),
        b"families": families,
        b"paths": paths,
        b"highest": highest,
    }))
    return AuditCompactReport(kind, accept, watch, reason, accepted, bundle_digests, refute_tuple, fork_tuple, families, paths, highest, digest)


def assess_audit_compaction(
    bundles: Iterable[AuditCompactBundle],
    *,
    raw_receipts: Iterable[AuditReceipt],
    audit_quorum: AuditQuorumReport,
    now: int,
    expected_profile_id: str,
    expected_service_name: str,
    expected_scope_digest: bytes,
    expected_request_digest: bytes,
    expected_public_payload_digest: bytes,
    previous_highest_sequence: int = -1,
    previous_bundle_digest: bytes = ZERO_DIGEST,
    previously_seen_bundles: Iterable[bytes] = (),
    min_family_diversity: int = 1,
    min_path_diversity: int = 1,
) -> AuditCompactReport:
    bundle_tuple = tuple(sorted(bundles, key=lambda item: (item.sequence, item.bundle_digest)))
    if not bundle_tuple:
        return _report(AuditCompactDecisionKind.EMPTY_NO_RECEIPTS, False, True, "no compact audit bundles supplied", bundles=())
    expected_positive, expected_watch, expected_refute, expected_fork, _, _ = _receipt_sets(raw_receipts)
    seen = set(previously_seen_bundles)
    core_by_seq: dict[int, bytes] = {}
    for bundle in bundle_tuple:
        if not bundle.verifies():
            return _report(AuditCompactDecisionKind.QUARANTINE_BAD_SIGNATURE, False, True, "bad compact bundle signature", bundles=bundle_tuple, refutes=expected_refute, forks=expected_fork)
        if not bundle.live(now):
            return _report(AuditCompactDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, False, True, "compact bundle expired or future", bundles=bundle_tuple, refutes=expected_refute, forks=expected_fork)
        if bundle.bundle_digest in seen:
            return _report(AuditCompactDecisionKind.QUARANTINE_REPLAY, False, True, "compact bundle replay", bundles=bundle_tuple, refutes=expected_refute, forks=expected_fork)
        if bundle.sequence <= previous_highest_sequence:
            return _report(AuditCompactDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, True, "compact bundle sequence rollback", bundles=bundle_tuple, refutes=expected_refute, forks=expected_fork)
        if previous_highest_sequence >= 0 and bundle.previous_bundle_digest != previous_bundle_digest:
            return _report(AuditCompactDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, True, "compact bundle previous digest mismatch", bundles=bundle_tuple, refutes=expected_refute, forks=expected_fork)
        previous = core_by_seq.setdefault(bundle.sequence, bundle.bundle_core_digest)
        if previous != bundle.bundle_core_digest:
            return _report(AuditCompactDecisionKind.QUARANTINE_SEQUENCE_FORK, False, True, "compact bundle same-sequence fork", bundles=bundle_tuple, refutes=expected_refute, forks=expected_fork)
        if bundle.profile_id != expected_profile_id:
            return _report(AuditCompactDecisionKind.QUARANTINE_PROFILE_DRIFT, False, True, "compact bundle profile drift", bundles=bundle_tuple, refutes=expected_refute, forks=expected_fork)
        if bundle.service_name != expected_service_name:
            return _report(AuditCompactDecisionKind.QUARANTINE_SERVICE_DRIFT, False, True, "compact bundle service drift", bundles=bundle_tuple, refutes=expected_refute, forks=expected_fork)
        if bundle.scope_digest != expected_scope_digest:
            return _report(AuditCompactDecisionKind.QUARANTINE_SCOPE_DRIFT, False, True, "compact bundle scope drift", bundles=bundle_tuple, refutes=expected_refute, forks=expected_fork)
        if bundle.request_digest != expected_request_digest:
            return _report(AuditCompactDecisionKind.QUARANTINE_REQUEST_DRIFT, False, True, "compact bundle request drift", bundles=bundle_tuple, refutes=expected_refute, forks=expected_fork)
        if bundle.bridge_shadow_digest != audit_quorum.bridge_shadow_digest:
            return _report(AuditCompactDecisionKind.QUARANTINE_SHADOW_DIGEST_DRIFT, False, True, "compact bundle shadow digest drift", bundles=bundle_tuple, refutes=expected_refute, forks=expected_fork)
        if bundle.public_payload_digest != expected_public_payload_digest:
            return _report(AuditCompactDecisionKind.QUARANTINE_PAYLOAD_DIGEST_DRIFT, False, True, "compact bundle payload digest drift", bundles=bundle_tuple, refutes=expected_refute, forks=expected_fork)
        if bundle.audit_quorum_digest != audit_quorum.report_digest:
            return _report(AuditCompactDecisionKind.QUARANTINE_QUORUM_DIGEST_DRIFT, False, True, "compact bundle quorum digest drift", bundles=bundle_tuple, refutes=expected_refute, forks=expected_fork)
        bundle_receipts = set(bundle.positive_receipt_digests) | set(bundle.watch_receipt_digests) | set(bundle.refute_receipt_digests) | set(bundle.fork_evidence_digests)
        raw_receipt_set = set(expected_positive) | set(expected_watch) | set(expected_refute) | set(expected_fork)
        if not bundle_receipts.issubset(raw_receipt_set):
            return _report(AuditCompactDecisionKind.QUARANTINE_RECEIPT_DIGEST_DRIFT, False, True, "compact bundle contains receipt digest not present in raw receipt window", bundles=bundle_tuple, refutes=expected_refute, forks=expected_fork)
        if not set(expected_refute).issubset(set(bundle.refute_receipt_digests)):
            return _report(AuditCompactDecisionKind.QUARANTINE_DROPPED_REFUTE_EVIDENCE, False, True, "compact bundle dropped refuting audit evidence", bundles=bundle_tuple, refutes=expected_refute, forks=expected_fork)
        if not set(expected_fork).issubset(set(bundle.fork_evidence_digests)):
            return _report(AuditCompactDecisionKind.QUARANTINE_DROPPED_FORK_EVIDENCE, False, True, "compact bundle dropped same-family fork evidence", bundles=bundle_tuple, refutes=expected_refute, forks=expected_fork)
    if len({item.family_id for item in bundle_tuple}) < min_family_diversity:
        return _report(AuditCompactDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, "compact bundle source-family diversity too low", bundles=bundle_tuple, refutes=expected_refute, forks=expected_fork)
    if len({item.path_family for item in bundle_tuple}) < min_path_diversity:
        return _report(AuditCompactDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, "compact bundle path-family diversity too low", bundles=bundle_tuple, refutes=expected_refute, forks=expected_fork)
    selected = max(bundle_tuple, key=lambda item: (item.sequence, item.bundle_digest))
    watch = audit_quorum.watch or bool(expected_watch or expected_refute or expected_fork)
    kind = AuditCompactDecisionKind.ACCEPT_WITH_WATCH if watch else AuditCompactDecisionKind.ACCEPT_COMPACT
    return _report(kind, True, watch, "compact audit bundle preserves positive, watch, refute, and fork evidence", bundles=bundle_tuple, selected=selected, refutes=expected_refute, forks=expected_fork)
