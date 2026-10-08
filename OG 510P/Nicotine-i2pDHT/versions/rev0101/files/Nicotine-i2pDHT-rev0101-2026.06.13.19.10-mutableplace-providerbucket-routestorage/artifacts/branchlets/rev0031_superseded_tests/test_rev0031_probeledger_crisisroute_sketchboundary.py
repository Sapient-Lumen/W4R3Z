from __future__ import annotations

from pathlib import Path

from i2p_dht_lab.bootstrapjoin import BootstrapJoinDecisionKind, BootstrapJoinReport
from i2p_dht_lab.contactlease import ContactLease, ContactLeasePurpose
from i2p_dht_lab.crisisroute import CrisisRouteDecisionKind, assess_crisis_route
from i2p_dht_lab.foldmap import audit_fold_map
from i2p_dht_lab.identity import DhtKeypair, NodeIdentity
from i2p_dht_lab.ids import key_id, sha256
from i2p_dht_lab.keycrisis import KeyCrisisKind, KeyCrisisMemory, KeyCrisisNotice, gate_keyed_operation
from i2p_dht_lab.probeledger import ProbeLedgerDecisionKind, ProbeLedgerPolicy, ProbeLedgerRound, assess_probe_ledger
from i2p_dht_lab.sketchboundary import (
    SketchAdapterOffer,
    SketchBoundaryDecisionKind,
    SketchContextKind,
    SketchEngineKind,
    SketchRequest,
    assess_sketch_boundary,
    short_reconciliation_id,
)
from i2p_dht_lab.succession import KeySuccessionRecord, SuccessionMemory


def seed(label: str) -> bytes:
    return sha256(("rev0031-seed:" + label).encode("utf-8"))


def kp(label: str) -> DhtKeypair:
    return DhtKeypair.from_seed(seed(label))


def digest(label: str) -> bytes:
    return key_id("rev0031", label)


def identity(label: str, keypair: DhtKeypair | None = None) -> NodeIdentity:
    keypair = keypair or kp("id-" + label)
    return NodeIdentity.create(destination=f"{label}.b32.i2p", keypair=keypair)


def lease(label: str, *, keypair: DhtKeypair, family: str, now: int, seq: int = 1) -> ContactLease:
    return ContactLease.create(identity=identity(label, keypair), keypair=keypair, family_id=family, purposes=(ContactLeasePurpose.ROUTE, ContactLeasePurpose.SEED_GATE), sequence=seq, issued_at=now, ttl=900)


def boot(label: str, *, accept: bool = True) -> BootstrapJoinReport:
    return BootstrapJoinReport(
        BootstrapJoinDecisionKind.ACCEPT_BOOTSTRAP_WINDOW if accept else BootstrapJoinDecisionKind.CONTINUE_NEEDS_LIVE_PROBE,
        accept,
        "test bootstrap",
        3,
        1 if accept else 0,
        0,
        digest("bootstrap-" + label),
        (),
    )


def round_obs(label: str, *, source: str, path: str, now: int, accept: bool = True, absence_only: bool = False, fast: bool = False, positive: bool = False) -> ProbeLedgerRound:
    if absence_only:
        return ProbeLedgerRound(
            round_id=digest("round-" + label),
            source_family=source,
            path_family=path,
            issued_at=now,
            expires_at=now + 120,
            absence_digest=digest("absence-" + label),
            absence_accept=True,
            fast_window_winner=fast,
            positive_evidence_digests=(digest("positive-" + label),) if positive else (),
        )
    return ProbeLedgerRound.from_bootstrap(
        round_id=digest("round-" + label),
        source_family=source,
        path_family=path,
        issued_at=now,
        ttl=120,
        bootstrap=boot(label, accept=accept),
        live_probe_digests=(digest("live-" + label),) if accept else (),
        fast_window_winner=fast,
    )


def test_probeledger_accepts_repeated_diverse_progress_and_rejects_replay() -> None:
    now = 1_766_500_000
    a = round_obs("a", source="seed-A", path="path-A", now=now, fast=True)
    b = round_obs("b", source="seed-B", path="path-B", now=now + 1, fast=True)
    report = assess_probe_ledger((a, b), now=now + 2)
    assert report.decision_kind is ProbeLedgerDecisionKind.ACCEPT_REPEATED_DIVERSE_PROGRESS
    assert report.accept
    replay = assess_probe_ledger((a, b), now=now + 2, previously_seen_round_digests=(a.round_digest,))
    assert replay.decision_kind is ProbeLedgerDecisionKind.QUARANTINE_REPLAYED_ROUND


def test_probeledger_catches_absence_loops_positive_contradiction_and_fast_capture() -> None:
    now = 1_766_500_100
    loop = assess_probe_ledger(
        (
            round_obs("neg-a", source="neg-A", path="path-A", now=now, absence_only=True),
            round_obs("neg-b", source="neg-B", path="path-B", now=now + 1, absence_only=True),
        ),
        now=now + 2,
        policy=ProbeLedgerPolicy(max_absence_only_rounds=1),
    )
    assert loop.decision_kind is ProbeLedgerDecisionKind.QUARANTINE_ABSENCE_ONLY_LOOP

    contradiction = assess_probe_ledger((round_obs("neg-c", source="neg-C", path="path-C", now=now, absence_only=True, positive=True),), now=now + 1)
    assert contradiction.decision_kind is ProbeLedgerDecisionKind.QUARANTINE_NEGATIVE_CONTRADICTION

    captured = assess_probe_ledger(
        (
            round_obs("fast-a", source="fam-Z", path="path-A", now=now, fast=True),
            round_obs("fast-b", source="fam-Z", path="path-B", now=now + 1, fast=True),
            round_obs("fast-c", source="fam-Y", path="path-C", now=now + 2, fast=True),
        ),
        now=now + 3,
    )
    assert captured.decision_kind is ProbeLedgerDecisionKind.QUARANTINE_FAST_FAMILY_CAPTURE


def test_crisisroute_blocks_old_key_and_accepts_cosigned_successor_route() -> None:
    now = 1_766_501_000
    old = kp("old")
    successor = kp("successor")
    scope = digest("scope")
    memory = KeyCrisisMemory()
    notice = KeyCrisisNotice.create(issuer_keypair=old, subject_public_key=old.public_key_bytes, kind=KeyCrisisKind.KEY_COMPROMISED, issuer_family="issuer-A", sequence=1, issued_at=now, ttl=3600, scope_digest=scope, successor_public_key=successor.public_key_bytes)
    memory.observe(notice, now=now + 1)

    blocked_gate = gate_keyed_operation(subject_public_key=old.public_key_bytes, memory=memory, now=now + 2)
    old_route = lease("old-route", keypair=old, family="route-old", now=now)
    blocked = assess_crisis_route(gate=blocked_gate, route_lease=old_route, now=now + 2)
    assert blocked.decision_kind is CrisisRouteDecisionKind.BLOCK_CRISIS_GATE
    assert not blocked.accept

    succession = KeySuccessionRecord.create(old_keypair=old, new_keypair=successor, sequence=1, issued_at=now, ttl=3600)
    verdict = SuccessionMemory().observe(succession, now=now + 2)
    successor_gate = gate_keyed_operation(subject_public_key=old.public_key_bytes, memory=memory, now=now + 2, successor_evidence_public_key=successor.public_key_bytes)
    successor_route = lease("successor-route", keypair=successor, family="route-new", now=now)
    accepted = assess_crisis_route(gate=successor_gate, route_lease=successor_route, now=now + 2, successor_public_key=successor.public_key_bytes, succession_verdict=verdict)
    assert accepted.decision_kind is CrisisRouteDecisionKind.ACCEPT_SUCCESSOR_ROUTE
    assert accepted.accept

    revoked = assess_crisis_route(gate=successor_gate, route_lease=successor_route, now=now + 2, successor_public_key=successor.public_key_bytes, succession_verdict=verdict, revocation_digests=(digest("revoked-route"),))
    assert revoked.decision_kind is CrisisRouteDecisionKind.QUARANTINE_REVOCATION_PRESENT


def test_crisisroute_rejects_successor_without_matching_succession() -> None:
    now = 1_766_501_100
    old = kp("old2")
    successor = kp("successor2")
    wrong_successor = kp("wrong-successor")
    memory = KeyCrisisMemory()
    notice = KeyCrisisNotice.create(issuer_keypair=old, subject_public_key=old.public_key_bytes, kind=KeyCrisisKind.SUCCESSION_REQUIRED, issuer_family="issuer-B", sequence=1, issued_at=now, ttl=3600, scope_digest=digest("scope2"), successor_public_key=successor.public_key_bytes)
    memory.observe(notice, now=now + 1)
    gate = gate_keyed_operation(subject_public_key=old.public_key_bytes, memory=memory, now=now + 2, successor_evidence_public_key=successor.public_key_bytes)
    wrong_succession = KeySuccessionRecord.create(old_keypair=old, new_keypair=wrong_successor, sequence=1, issued_at=now, ttl=3600)
    wrong_verdict = SuccessionMemory().observe(wrong_succession, now=now + 2)
    route = lease("succession-route", keypair=successor, family="route-B", now=now)
    report = assess_crisis_route(gate=gate, route_lease=route, now=now + 2, successor_public_key=successor.public_key_bytes, succession_verdict=wrong_verdict)
    assert report.decision_kind is CrisisRouteDecisionKind.QUARANTINE_SUCCESSION_MISMATCH


def test_sketchboundary_keeps_exact_toy_sketches_in_lab_and_requires_native_adapter_elsewhere() -> None:
    request = SketchRequest(range_id=digest("range"), engine=SketchEngineKind.EXACT_DEBUG, context=SketchContextKind.LAB, expected_difference=2, capacity=4, element_bits=32, session_salt=b"fresh-salt-000000", allow_exact_debug=True)
    lab = assess_sketch_boundary(request)
    assert lab.decision_kind is SketchBoundaryDecisionKind.ACCEPT_EXACT_DEBUG_LAB
    production = assess_sketch_boundary(SketchRequest(range_id=digest("range"), engine=SketchEngineKind.EXACT_DEBUG, context=SketchContextKind.PRODUCTION, expected_difference=2, capacity=4, element_bits=32, session_salt=b"fresh-salt-111111"))
    assert production.decision_kind is SketchBoundaryDecisionKind.QUARANTINE_EXACT_DEBUG_OUTSIDE_LAB

    native_request = SketchRequest(range_id=digest("native-range"), engine=SketchEngineKind.MINISKETCH, context=SketchContextKind.GARDEN_SERVICE, expected_difference=3, capacity=4, element_bits=32, session_salt=b"fresh-salt-222222")
    missing = assess_sketch_boundary(native_request)
    assert missing.decision_kind is SketchBoundaryDecisionKind.CONTINUE_NEED_NATIVE_ADAPTER
    offer = SketchAdapterOffer(SketchEngineKind.MINISKETCH, "adapter-v0", "garden-A", max_capacity=64, element_bits=32, supports_extension=True)
    accepted = assess_sketch_boundary(native_request, offer=offer)
    assert accepted.decision_kind is SketchBoundaryDecisionKind.ACCEPT_NATIVE_ADAPTER_BOUNDARY


def test_sketchboundary_capacity_extension_salt_replay_and_short_ids() -> None:
    offer = SketchAdapterOffer(SketchEngineKind.MINISKETCH, "adapter-v0", "garden-A", max_capacity=32, element_bits=32, supports_extension=True)
    request = SketchRequest(range_id=digest("too-small"), engine=SketchEngineKind.MINISKETCH, context=SketchContextKind.GARDEN_SERVICE, expected_difference=12, capacity=4, element_bits=32, session_salt=b"fresh-salt-333333")
    extension = assess_sketch_boundary(request, offer=offer)
    assert extension.decision_kind is SketchBoundaryDecisionKind.REQUEST_SKETCH_EXTENSION

    replay = assess_sketch_boundary(request, offer=offer, previously_used_salts=(b"fresh-salt-333333",))
    assert replay.decision_kind is SketchBoundaryDecisionKind.QUARANTINE_SALT_REPLAY

    a = short_reconciliation_id(digest("item-a"), salt=b"fresh-salt-444444", bits=32)
    b = short_reconciliation_id(digest("item-a"), salt=b"fresh-salt-555555", bits=32)
    assert a != b
    assert 1 <= a < 2**32


def test_foldmap_current_path_is_visible() -> None:
    root = Path(__file__).resolve().parents[1]
    report = audit_fold_map(root, revision="rev0031", artifact_stem=root.name)
    assert report.status == "pass"
    assert report.current_entry_count >= 10
