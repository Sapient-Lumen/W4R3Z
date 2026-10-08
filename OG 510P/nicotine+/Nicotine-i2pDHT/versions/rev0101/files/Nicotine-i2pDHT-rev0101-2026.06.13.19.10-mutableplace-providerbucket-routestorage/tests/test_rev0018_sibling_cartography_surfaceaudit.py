from __future__ import annotations

import json
from pathlib import Path

from i2p_dht_lab.identity import DhtKeypair, NodeIdentity
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.keyspacecartography import (
    CartographyDecisionKind,
    CartographyPolicy,
    KeyspaceCartographyBook,
    RegionObservation,
    ScoutReason,
)
from i2p_dht_lab.siblingbroadcast import (
    SiblingBroadcastDecisionKind,
    SiblingBroadcastPolicy,
    SiblingCandidate,
    SiblingReceiptKind,
    SiblingStoreReceipt,
    assess_sibling_broadcast,
    plan_sibling_broadcast,
)
from i2p_dht_lab.surfaceaudit import audit_surface_pointers


def kp(n: int) -> DhtKeypair:
    return DhtKeypair.from_seed(bytes([n % 256]) * 32)


def ident(n: int, prefix: str = "sib") -> NodeIdentity:
    return NodeIdentity.create(destination=f"{prefix}-{n}.b32.i2p", keypair=kp(n))


def candidate(n: int, family: str, *, target: bytes | None = None, score: int = 0, last_seen: int = 1000) -> SiblingCandidate:
    node_id = ident(n).node_id if target is None else target[:-1] + bytes([(target[-1] ^ n) & 0xFF])
    return SiblingCandidate(node_id=node_id, family_id=family, destination_hint=f"node-{n}.b32.i2p", last_seen_at=last_seen, score=score)


def receipt(n: int, family: str, target: bytes, digest: bytes, kind: SiblingReceiptKind, *, rank: int, now: int = 1000) -> SiblingStoreReceipt:
    return SiblingStoreReceipt.create(
        keypair=kp(n),
        storage_node_id=ident(n).node_id,
        family_id=family,
        target=target,
        record_digest=digest,
        sibling_rank=rank,
        kind=kind,
        issued_at=now,
        ttl=1000,
        retry_after=now + 300 if kind is SiblingReceiptKind.USEFUL_REFUSAL else 0,
    )


def key_with_region(region: int, *, prefix_bits: int = 3) -> bytes:
    shift = 256 - prefix_bits
    value = region << shift
    return value.to_bytes(32, "big")


def obs(region: int, family: str, introducer: str, *, at: int, success: int = 1, prefix_bits: int = 3) -> RegionObservation:
    base = int.from_bytes(key_with_region(region, prefix_bits=prefix_bits), "big")
    low = int.from_bytes(sha256(f"{region}:{family}:{introducer}:{at}".encode()), "big") & ((1 << (256 - prefix_bits)) - 1)
    key = (base | low).to_bytes(32, "big")
    return RegionObservation(key=key, family_id=family, introducer_family=introducer, observed_at=at, success_count=success)


def test_sibling_broadcast_plan_family_caps_close_candidates() -> None:
    target = sha256(b"rev0018 sibling target")
    digest = sha256(b"rev0018 record")
    candidates = (
        candidate(1, "captured", target=target, score=20),
        candidate(2, "captured", target=target, score=10),
        candidate(3, "captured", target=target, score=9),
        candidate(4, "east", target=target),
        candidate(5, "west", target=target),
        candidate(6, "north", target=target),
    )
    plan = plan_sibling_broadcast(candidates, target=target, record_digest=digest, policy=SiblingBroadcastPolicy(ask_count=5, max_per_family=2))
    assert len(plan.selected) == 5
    assert sum(1 for item in plan.selected if item.family_id == "captured") == 2
    assert {"east", "west", "north"}.issubset(plan.selected_families)
    assert len(plan.transcript_digest) == 32


def test_sibling_broadcast_accepts_close_family_diverse_receipts() -> None:
    target = sha256(b"rev0018 sibling target 2")
    digest = sha256(b"rev0018 record 2")
    receipts = tuple(
        receipt(i, family, target, digest, SiblingReceiptKind.ACCEPTED, rank=rank)
        for i, family, rank in ((1, "east", 0), (2, "east", 1), (3, "west", 2), (4, "north", 3), (5, "south", 4))
    )
    report = assess_sibling_broadcast(receipts, target=target, record_digest=digest, now=1100, policy=SiblingBroadcastPolicy(min_accept_receipts=5, min_accept_families=3, sibling_window=8))
    assert report.decision.kind is SiblingBroadcastDecisionKind.ACCEPT_REPLICATED
    assert report.accept_family_count == 4
    assert not report.needs_more_siblings


def test_sibling_broadcast_rejects_one_family_replication_even_with_count() -> None:
    target = sha256(b"rev0018 sibling target 3")
    digest = sha256(b"rev0018 record 3")
    receipts = tuple(receipt(i, "captured", target, digest, SiblingReceiptKind.ACCEPTED, rank=i) for i in range(1, 7))
    report = assess_sibling_broadcast(receipts, target=target, record_digest=digest, now=1100, policy=SiblingBroadcastPolicy(min_accept_receipts=5, min_accept_families=3, max_invalid_receipts=0))
    assert report.decision.kind is SiblingBroadcastDecisionKind.CONTINUE_LOW_FAMILY_DIVERSITY
    assert report.accept_family_count == 1


def test_sibling_broadcast_quarantines_contradictory_valid_receipts() -> None:
    target = sha256(b"rev0018 sibling target 4")
    digest_a = sha256(b"rev0018 record 4a")
    digest_b = sha256(b"rev0018 record 4b")
    good = [receipt(i, f"family-{i}", target, digest_a, SiblingReceiptKind.ACCEPTED, rank=i) for i in range(1, 5)]
    first = receipt(9, "forky", target, digest_a, SiblingReceiptKind.ACCEPTED, rank=5)
    second = receipt(9, "forky", target, digest_b, SiblingReceiptKind.ACCEPTED, rank=5)
    report = assess_sibling_broadcast(tuple(good + [first, second]), target=target, record_digest=digest_a, now=1100)
    assert report.decision.kind is SiblingBroadcastDecisionKind.QUARANTINE_CONTRADICTORY_RECEIPTS
    assert first.storage_node_id in report.contradiction_node_ids


def test_sibling_broadcast_useful_refusals_are_not_success() -> None:
    target = sha256(b"rev0018 sibling target 5")
    digest = sha256(b"rev0018 record 5")
    receipts = tuple(receipt(i, f"family-{i}", target, digest, SiblingReceiptKind.USEFUL_REFUSAL, rank=i) for i in range(1, 6))
    report = assess_sibling_broadcast(receipts, target=target, record_digest=digest, now=1100, policy=SiblingBroadcastPolicy(useful_refusal_pressure=4))
    assert report.decision.kind is SiblingBroadcastDecisionKind.CONTINUE_USEFUL_REFUSAL_PRESSURE
    assert len(report.useful_refusals) == 5
    assert len(report.accepted_receipts) == 0


def test_keyspace_cartography_scouts_holes_and_monoculture() -> None:
    policy = CartographyPolicy(prefix_bits=3, min_covered_regions=4, min_families_per_region=2, max_family_fraction=0.70, scout_limit=6)
    book = KeyspaceCartographyBook()
    book.ingest((
        obs(0, "captured", "garden-a", at=1000),
        obs(0, "captured", "garden-a", at=1001),
        obs(0, "captured", "garden-a", at=1002),
        obs(1, "east", "garden-b", at=1000),
        obs(1, "west", "garden-c", at=1000),
    ), policy=policy)
    report = book.analyze(now=1100, policy=policy)
    assert report.decision.kind is CartographyDecisionKind.SCOUT_MONOCULTURE
    assert any(action.reason is ScoutReason.MONOCULTURE and action.region == 0 for action in report.scouts)
    assert any(action.reason is ScoutReason.HOLE for action in report.scouts)
    assert len(report.transcript_digest) == 32


def test_keyspace_cartography_prunes_stale_before_scouting() -> None:
    policy = CartographyPolicy(prefix_bits=3, min_covered_regions=2, stale_after_seconds=50, scout_limit=4)
    book = KeyspaceCartographyBook()
    book.ingest((obs(0, "east", "seed", at=100), obs(1, "west", "seed", at=101)), policy=policy)
    report = book.analyze(now=1000, policy=policy, prune_stale=True)
    assert report.decision.kind is CartographyDecisionKind.PRUNE_STALE_THEN_SCOUT
    assert report.stale_pruned == 2
    assert report.covered_regions == 0


def test_keyspace_cartography_accepts_minimal_diverse_coverage() -> None:
    policy = CartographyPolicy(prefix_bits=2, min_covered_regions=4, min_families_per_region=2, max_family_fraction=0.75, scout_limit=4)
    book = KeyspaceCartographyBook()
    observations = []
    for region in range(4):
        observations.append(obs(region, f"east-{region}", f"intro-{region}-a", at=1000, prefix_bits=2))
        observations.append(obs(region, f"west-{region}", f"intro-{region}-b", at=1001, prefix_bits=2))
    book.ingest(observations, policy=policy)
    report = book.analyze(now=1100, policy=policy)
    assert report.decision.kind is CartographyDecisionKind.ACCEPT_COVERAGE
    assert not report.scouts


def test_surface_pointer_audit_finds_missing_public_and_registry_paths(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "001-present.md").write_text("ok", encoding="utf-8")
    (tmp_path / "PUBLIC_SURFACE.json").write_text(json.dumps({"revision": "rev0018", "entry_points": [{"path": "docs/001-present.md"}, {"path": "docs/missing.md"}]}), encoding="utf-8")
    (tmp_path / "HEAD_REGISTRY.json").write_text(json.dumps({"revision": "rev0018", "heads": {"present": "docs/001-present.md", "missing": "docs/also-missing.md"}}), encoding="utf-8")
    for surface in ("CLAIM_SURFACE.json", "NEXT_REVISION.json", "REVISION_RECEIPT.json", "PROOF_OBLIGATION_SURFACE.json"):
        (tmp_path / surface).write_text(json.dumps({"revision": "rev0018"}), encoding="utf-8")
    report = audit_surface_pointers(tmp_path, revision="rev0018")
    assert report.status == "warn"
    missing = [finding for finding in report.findings if finding.code == "missing_pointer"]
    assert {item.pointer for item in missing} == {"docs/missing.md", "docs/also-missing.md"}
