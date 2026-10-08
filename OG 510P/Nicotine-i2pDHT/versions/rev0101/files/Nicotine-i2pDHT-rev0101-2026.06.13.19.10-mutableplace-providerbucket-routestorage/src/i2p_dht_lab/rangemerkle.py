"""Merkle-ish range repair fixtures for anti-entropy.

Range sketches are cheap roots.  The next risky boundary is exact repair: a
node must ask for smaller evidence without treating a signed root as truth.
This module implements a tiny deterministic Merkle tree with inclusion proofs,
signed range summaries, source-family pressure, tombstone-first repair, and
stale/root-fork quarantine.

It is deliberately small and not a production storage tree.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .familydiversity import FamilyDiversityPolicy, analyze_family_diversity
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256

RANGE_MERKLE_DOMAIN = DOMAIN + b":range-merkle-v1:"
MAX_REGION_BITS = 16
EMPTY_RANGE_ROOT = sha256(RANGE_MERKLE_DOMAIN + b":empty-root:")


class RangeMerkleLeafKind(str, Enum):
    MUTABLE_HEAD = "mutable_head"
    PROVIDER_RECORD = "provider_record"
    TOMBSTONE = "tombstone"
    CUSTODY_FACT = "custody_fact"
    NAMESPACE_POLICY = "namespace_policy"


class RangeMerkleDecisionKind(str, Enum):
    ACCEPT_IN_SYNC = "accept_in_sync"
    REQUEST_CHILD_RANGE_REPAIR = "request_child_range_repair"
    ACCEPT_VERIFIED_EXACT_REPAIR = "accept_verified_exact_repair"
    REQUEST_TOMBSTONE_FIRST = "request_tombstone_first"
    CONTINUE_NO_VALID_SUMMARIES = "continue_no_valid_summaries"
    CONTINUE_NEED_FAMILY_DIVERSITY = "continue_need_family_diversity"
    REJECT_BAD_SIGNATURE_OR_TIME = "reject_bad_signature_or_time"
    REJECT_BAD_PROOF = "reject_bad_proof"
    QUARANTINE_ROOT_FORK = "quarantine_root_fork"
    QUARANTINE_STALE_REPLAY = "quarantine_stale_replay"


@dataclass(frozen=True)
class RangeMerkleLeaf:
    key_digest: bytes
    object_digest: bytes
    kind: RangeMerkleLeafKind
    sequence: int = 0
    tombstone: bool = False

    def __post_init__(self) -> None:
        if len(self.key_digest) != 32 or len(self.object_digest) != 32:
            raise ValueError("range Merkle leaf digests must be 32 bytes")
        if self.sequence < 0:
            raise ValueError("range Merkle leaf sequence must be non-negative")

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"key_digest": self.key_digest,
            b"object_digest": self.object_digest,
            b"kind": self.kind.value,
            b"sequence": self.sequence,
            b"tombstone": 1 if self.tombstone else 0,
        }

    @property
    def leaf_digest(self) -> bytes:
        return sha256(RANGE_MERKLE_DOMAIN + b":leaf:" + bencode(self.bvalue()))


@dataclass(frozen=True)
class MerkleSibling:
    side: str
    digest: bytes

    def __post_init__(self) -> None:
        if self.side not in {"left", "right"}:
            raise ValueError("Merkle sibling side must be left/right")
        if len(self.digest) != 32:
            raise ValueError("Merkle sibling digest must be 32 bytes")

    def bvalue(self) -> dict[bytes, BValue]:
        return {b"side": self.side, b"digest": self.digest}


@dataclass(frozen=True)
class RangeMerkleProof:
    leaf: RangeMerkleLeaf
    branch: tuple[MerkleSibling, ...]

    def compute_root(self) -> bytes:
        current = self.leaf.leaf_digest
        for sibling in self.branch:
            if sibling.side == "left":
                current = sha256(RANGE_MERKLE_DOMAIN + b":node:" + sibling.digest + current)
            else:
                current = sha256(RANGE_MERKLE_DOMAIN + b":node:" + current + sibling.digest)
        return current

    def verify(self, root_digest: bytes) -> bool:
        return len(root_digest) == 32 and self.compute_root() == root_digest

    def bvalue(self) -> dict[bytes, BValue]:
        return {b"leaf": self.leaf.bvalue(), b"branch": [item.bvalue() for item in self.branch]}


@dataclass(frozen=True)
class RangeMerkleTree:
    leaves: tuple[RangeMerkleLeaf, ...]
    root_digest: bytes
    proofs: tuple[RangeMerkleProof, ...]

    def proof_for_leaf(self, leaf: RangeMerkleLeaf) -> RangeMerkleProof:
        for proof in self.proofs:
            if proof.leaf == leaf:
                return proof
        raise KeyError("leaf proof not found")


def _parent(left: bytes, right: bytes) -> bytes:
    return sha256(RANGE_MERKLE_DOMAIN + b":node:" + left + right)


def build_range_merkle_tree(leaves: Iterable[RangeMerkleLeaf]) -> RangeMerkleTree:
    ordered = tuple(sorted(leaves, key=lambda leaf: (leaf.key_digest, leaf.kind.value, leaf.sequence, leaf.object_digest)))
    if not ordered:
        return RangeMerkleTree((), EMPTY_RANGE_ROOT, ())
    levels: list[list[bytes]] = [[leaf.leaf_digest for leaf in ordered]]
    width = len(levels[0])
    while width > 1:
        prev = levels[-1]
        nxt: list[bytes] = []
        for idx in range(0, len(prev), 2):
            left = prev[idx]
            right = prev[idx + 1] if idx + 1 < len(prev) else left
            nxt.append(_parent(left, right))
        levels.append(nxt)
        width = len(nxt)
    proofs: list[RangeMerkleProof] = []
    for leaf_index, leaf in enumerate(ordered):
        idx = leaf_index
        branch: list[MerkleSibling] = []
        for level in levels[:-1]:
            if idx % 2 == 0:
                sib_idx = idx + 1 if idx + 1 < len(level) else idx
                branch.append(MerkleSibling("right", level[sib_idx]))
            else:
                branch.append(MerkleSibling("left", level[idx - 1]))
            idx //= 2
        proofs.append(RangeMerkleProof(leaf, tuple(branch)))
    return RangeMerkleTree(ordered, levels[-1][0], tuple(proofs))


@dataclass(frozen=True)
class RangeMerkleSummary:
    region_prefix: int
    region_bits: int
    sequence: int
    root_digest: bytes
    leaf_count: int
    source_node_id: bytes
    source_family: str
    public_key: bytes
    issued_at: int
    expires_at: int
    signature: bytes = b""

    def __post_init__(self) -> None:
        if self.region_bits < 0 or self.region_bits > MAX_REGION_BITS:
            raise ValueError("range Merkle region bits out of range")
        if self.region_prefix < 0 or self.region_prefix >= (1 << self.region_bits if self.region_bits else 1):
            raise ValueError("range Merkle region prefix invalid")
        if self.sequence < 0 or self.leaf_count < 0:
            raise ValueError("range Merkle counters invalid")
        if len(self.root_digest) != 32 or len(self.source_node_id) != 32 or len(self.public_key) != 32:
            raise ValueError("range Merkle summary digests/keys must be 32 bytes")
        if not self.source_family or self.expires_at <= self.issued_at:
            raise ValueError("range Merkle summary family/time invalid")

    @classmethod
    def create(
        cls,
        *,
        keypair: DhtKeypair,
        source_node_id: bytes,
        source_family: str,
        region_prefix: int,
        region_bits: int,
        sequence: int,
        tree: RangeMerkleTree,
        issued_at: int,
        ttl: int,
    ) -> "RangeMerkleSummary":
        if ttl <= 0:
            raise ValueError("range Merkle summary ttl must be positive")
        unsigned = cls(region_prefix=region_prefix, region_bits=region_bits, sequence=sequence, root_digest=tree.root_digest, leaf_count=len(tree.leaves), source_node_id=source_node_id, source_family=source_family, public_key=keypair.public_key_bytes, issued_at=issued_at, expires_at=issued_at + ttl)
        return replace(unsigned, signature=keypair.sign(unsigned.unsigned_payload()))

    @property
    def key(self) -> tuple[int, int]:
        return (self.region_bits, self.region_prefix)

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"region_prefix": self.region_prefix,
            b"region_bits": self.region_bits,
            b"sequence": self.sequence,
            b"root_digest": self.root_digest,
            b"leaf_count": self.leaf_count,
            b"source_node_id": self.source_node_id,
            b"source_family": self.source_family,
            b"public_key": self.public_key,
            b"issued_at": self.issued_at,
            b"expires_at": self.expires_at,
        }

    def unsigned_payload(self) -> bytes:
        return RANGE_MERKLE_DOMAIN + b":summary-unsigned:" + bencode(self.unsigned_bvalue())

    @property
    def summary_digest(self) -> bytes:
        return sha256(RANGE_MERKLE_DOMAIN + b":summary:" + self.unsigned_payload() + self.signature)

    def signature_valid(self) -> bool:
        return verify_signature(self.public_key, self.unsigned_payload(), self.signature)

    def live(self, *, now: int, max_future_skew: int = 300) -> bool:
        return self.issued_at - max_future_skew <= now < self.expires_at + max_future_skew


@dataclass(frozen=True)
class RangeMerklePolicy:
    min_families: int = 2
    max_per_family: int = 1
    max_future_skew: int = 300

    def family_policy(self) -> FamilyDiversityPolicy:
        return FamilyDiversityPolicy(min_families=self.min_families, max_per_family=self.max_per_family)


@dataclass(frozen=True)
class RangeMerklePlan:
    decision: RangeMerkleDecisionKind
    accept: bool
    reason: str
    chosen_summary: RangeMerkleSummary | None
    repair_proofs: tuple[RangeMerkleProof, ...]
    valid_summaries: tuple[RangeMerkleSummary, ...]
    invalid_summaries: tuple[RangeMerkleSummary, ...]
    family_counts: dict[str, int]
    digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision.value.startswith("quarantine_")


def _plan(
    decision: RangeMerkleDecisionKind,
    accept: bool,
    reason: str,
    *,
    chosen_summary: RangeMerkleSummary | None = None,
    repair_proofs: Iterable[RangeMerkleProof] = (),
    valid_summaries: Iterable[RangeMerkleSummary] = (),
    invalid_summaries: Iterable[RangeMerkleSummary] = (),
    family_counts: dict[str, int] | None = None,
) -> RangeMerklePlan:
    proofs = tuple(repair_proofs)
    valid = tuple(valid_summaries)
    invalid = tuple(invalid_summaries)
    counts = dict(sorted((family_counts or {}).items()))
    digest = sha256(RANGE_MERKLE_DOMAIN + b":plan:" + bencode({
        b"decision": decision.value,
        b"accept": 1 if accept else 0,
        b"chosen": b"" if chosen_summary is None else chosen_summary.summary_digest,
        b"proofs": [proof.compute_root() + proof.leaf.leaf_digest for proof in proofs],
        b"valid": [summary.summary_digest for summary in valid],
        b"invalid": [summary.summary_digest for summary in invalid],
        b"families": counts,
    }))
    return RangeMerklePlan(decision, accept, reason, chosen_summary, proofs, valid, invalid, counts, digest)


def plan_range_merkle_repair(
    local_summary: RangeMerkleSummary | None,
    remote_summaries: Iterable[RangeMerkleSummary],
    *,
    proofs: Iterable[RangeMerkleProof] = (),
    now: int,
    policy: RangeMerklePolicy | None = None,
) -> RangeMerklePlan:
    policy = policy or RangeMerklePolicy()
    incoming = tuple(remote_summaries)
    valid: list[RangeMerkleSummary] = []
    invalid: list[RangeMerkleSummary] = []
    for summary in incoming:
        if summary.signature_valid() and summary.live(now=now, max_future_skew=policy.max_future_skew):
            valid.append(summary)
        else:
            invalid.append(summary)
    if not valid:
        kind = RangeMerkleDecisionKind.REJECT_BAD_SIGNATURE_OR_TIME if invalid else RangeMerkleDecisionKind.CONTINUE_NO_VALID_SUMMARIES
        return _plan(kind, False, "no valid live range Merkle summaries", invalid_summaries=invalid)

    diversity = analyze_family_diversity(valid, family_of=lambda summary: summary.source_family, policy=policy.family_policy())
    if not diversity.passes(policy.family_policy()):
        return _plan(RangeMerkleDecisionKind.CONTINUE_NEED_FAMILY_DIVERSITY, False, "range Merkle summaries need source-family diversity", valid_summaries=valid, invalid_summaries=invalid, family_counts=diversity.family_counts)

    max_seq = max(summary.sequence for summary in valid)
    top = [summary for summary in valid if summary.sequence == max_seq]
    top_roots = {summary.root_digest for summary in top}
    if len(top_roots) > 1:
        return _plan(RangeMerkleDecisionKind.QUARANTINE_ROOT_FORK, False, "same-sequence range Merkle root fork", chosen_summary=top[0], valid_summaries=valid, invalid_summaries=invalid, family_counts=diversity.family_counts)
    chosen = top[0]
    if local_summary is not None:
        if chosen.key != local_summary.key:
            return _plan(RangeMerkleDecisionKind.REJECT_BAD_PROOF, False, "remote summary covers a different region", chosen_summary=chosen, valid_summaries=valid, invalid_summaries=invalid, family_counts=diversity.family_counts)
        if chosen.sequence < local_summary.sequence:
            return _plan(RangeMerkleDecisionKind.QUARANTINE_STALE_REPLAY, False, "remote range Merkle root replays a stale sequence", chosen_summary=chosen, valid_summaries=valid, invalid_summaries=invalid, family_counts=diversity.family_counts)
        if chosen.sequence == local_summary.sequence and chosen.root_digest == local_summary.root_digest:
            return _plan(RangeMerkleDecisionKind.ACCEPT_IN_SYNC, True, "range Merkle root matches local memory", chosen_summary=chosen, valid_summaries=valid, invalid_summaries=invalid, family_counts=diversity.family_counts)
        if chosen.sequence == local_summary.sequence and chosen.root_digest != local_summary.root_digest:
            return _plan(RangeMerkleDecisionKind.QUARANTINE_ROOT_FORK, False, "local and remote disagree at same range sequence", chosen_summary=chosen, valid_summaries=valid, invalid_summaries=invalid, family_counts=diversity.family_counts)

    proof_tuple = tuple(proofs)
    if not proof_tuple:
        return _plan(RangeMerkleDecisionKind.REQUEST_CHILD_RANGE_REPAIR, False, "newer range root needs child/proof repair", chosen_summary=chosen, valid_summaries=valid, invalid_summaries=invalid, family_counts=diversity.family_counts)
    if any(not proof.verify(chosen.root_digest) for proof in proof_tuple):
        return _plan(RangeMerkleDecisionKind.REJECT_BAD_PROOF, False, "range Merkle proof does not verify against chosen root", chosen_summary=chosen, repair_proofs=proof_tuple, valid_summaries=valid, invalid_summaries=invalid, family_counts=diversity.family_counts)
    if any(proof.leaf.tombstone or proof.leaf.kind is RangeMerkleLeafKind.TOMBSTONE for proof in proof_tuple):
        return _plan(RangeMerkleDecisionKind.REQUEST_TOMBSTONE_FIRST, False, "verified range proof contains tombstone pressure", chosen_summary=chosen, repair_proofs=proof_tuple, valid_summaries=valid, invalid_summaries=invalid, family_counts=diversity.family_counts)
    return _plan(RangeMerkleDecisionKind.ACCEPT_VERIFIED_EXACT_REPAIR, True, "verified range proofs identify exact repair leaves", chosen_summary=chosen, repair_proofs=proof_tuple, valid_summaries=valid, invalid_summaries=invalid, family_counts=diversity.family_counts)
