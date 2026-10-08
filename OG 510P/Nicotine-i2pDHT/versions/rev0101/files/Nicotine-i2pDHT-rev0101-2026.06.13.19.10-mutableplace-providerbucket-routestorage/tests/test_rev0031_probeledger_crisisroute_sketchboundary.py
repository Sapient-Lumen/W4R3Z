from __future__ import annotations

from i2p_dht_lab.contactlease import ContactLease, ContactLeasePurpose
from i2p_dht_lab.crisisroute import CrisisRouteDecisionKind, assess_crisis_route
from i2p_dht_lab.foldmap import audit_fold_map
from i2p_dht_lab.identity import DhtKeypair, NodeIdentity
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.keycrisis import KeyCrisisGateDecisionKind, KeyCrisisGateReport
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
from i2p_dht_lab.succession import SuccessionVerdict, SuccessionVerdictKind


def digest(label: str) -> bytes:
    return sha256(("rev0031-probe:" + label).encode("utf-8"))


def kp(label: str) -> DhtKeypair:
    return DhtKeypair.from_seed(digest("seed:" + label))


def lease(label: str, *, now: int, keypair: DhtKeypair | None = None, family: str = "route-A", sequence: int = 1) -> ContactLease:
    keypair = keypair or kp("lease:" + label)
    identity = NodeIdentity.create(destination=f"rev0031-{label}.b32.i2p", keypair=keypair)
    return ContactLease.create(
        identity=identity,
        keypair=keypair,
        family_id=family,
        purposes=(ContactLeasePurpose.ROUTE, ContactLeasePurpose.SEED_GATE),
        sequence=sequence,
        issued_at=now,
        ttl=900,
    )


def round_(label: str, *, source: str, path: str, now: int, bootstrap: bool = True, live: bool = True, absence: bool = False, positive: bool = False, fast: bool = False, egress: bool = True) -> ProbeLedgerRound:
    return ProbeLedgerRound(
        round_id=digest("round:" + label),
        source_family=source,
        path_family=path,
        issued_at=now,
        expires_at=now + 120,
        bootstrap_digest=digest("bootstrap:" + label),
        bootstrap_accept=bootstrap,
        live_probe_digests=(digest("live:" + label),) if live else (),
        absence_digest=digest("absence:" + label),
        absence_accept=absence,
        egress_digest=digest("egress:" + label),
        egress_accept=egress,
        positive_evidence_digests=(digest("positive:" + label),) if positive else (),
        fast_window_winner=fast,
    )


def gate(kind: KeyCrisisGateDecisionKind, *, subject: bytes, active: bytes | None = None, accept: bool | None = None) -> KeyCrisisGateReport:
    accepted = accept if accept is not None else kind in {
        KeyCrisisGateDecisionKind.ACCEPT_NO_LIVE_CRISIS,
        KeyCrisisGateDecisionKind.ACCEPT_SUCCESSION_RECOVERY,
        KeyCrisisGateDecisionKind.WATCH_DESTINATION_LOST,
    }
    notice = active or digest("notice")
    return KeyCrisisGateReport(kind, accepted, kind.value, subject, notice, digest("gate:" + kind.value))


def test_probeledger_accepts_repeated_diverse_progress_and_rejects_replay() -> None:
    now = 1_766_500_000
    rounds = (
        round_("a", source="source-A", path="path-A", now=now),
        round_("b", source="source-B", path="path-B", now=now),
    )
    report = assess_probe_ledger(rounds, now=now + 1)
    assert report.decision_kind is ProbeLedgerDecisionKind.ACCEPT_REPEATED_DIVERSE_PROGRESS
    assert report.accept
    replay = assess_probe_ledger(rounds, now=now + 1, previously_seen_round_digests=(rounds[0].round_digest,))
    assert replay.decision_kind is ProbeLedgerDecisionKind.QUARANTINE_REPLAYED_ROUND


def test_probeledger_catches_absence_loops_positive_contradiction_and_fast_capture() -> None:
    now = 1_766_500_100
    contradiction = assess_probe_ledger((round_("contradict", source="A", path="P", now=now, bootstrap=False, live=False, absence=True, positive=True),), now=now + 1)
    assert contradiction.decision_kind is ProbeLedgerDecisionKind.QUARANTINE_NEGATIVE_CONTRADICTION

    absence_loop = assess_probe_ledger(
        (
            round_("empty-a", source="A", path="P1", now=now, bootstrap=False, live=False, absence=True),
            round_("empty-b", source="B", path="P2", now=now, bootstrap=False, live=False, absence=True),
        ),
        now=now + 1,
    )
    assert absence_loop.decision_kind is ProbeLedgerDecisionKind.QUARANTINE_ABSENCE_ONLY_LOOP

    fast = assess_probe_ledger(
        tuple(round_(f"fast-{idx}", source="captured", path=f"P{idx}", now=now, fast=True) for idx in range(3)),
        now=now + 1,
    )
    assert fast.decision_kind is ProbeLedgerDecisionKind.QUARANTINE_FAST_FAMILY_CAPTURE


def test_probeledger_allows_watch_when_one_progress_round_is_clean_skip() -> None:
    now = 1_766_500_150
    report = assess_probe_ledger(
        (
            round_("live", source="A", path="P1", now=now),
            round_("skip", source="B", path="P2", now=now, live=False),
        ),
        now=now + 1,
        policy=ProbeLedgerPolicy(accept_with_watch_on_clean_skip=True),
    )
    assert report.decision_kind is ProbeLedgerDecisionKind.ACCEPT_WITH_WATCH
    assert report.accept


def test_crisisroute_blocks_old_key_and_accepts_cosigned_successor_route() -> None:
    now = 1_766_501_000
    old = kp("old")
    new = kp("new")
    old_route = lease("old", now=now, keypair=old, family="old-family")
    blocked = assess_crisis_route(gate=gate(KeyCrisisGateDecisionKind.BLOCK_KEY_COMPROMISED, subject=old.public_key_bytes), route_lease=old_route, now=now + 1)
    assert blocked.decision_kind is CrisisRouteDecisionKind.BLOCK_CRISIS_GATE
    assert not blocked.accept

    new_route = lease("new", now=now, keypair=new, family="new-family")
    succession = SuccessionVerdict(SuccessionVerdictKind.ACCEPT_FIRST, old.public_key_bytes, 1, None, new.public_key_bytes, "co-signed")
    accepted = assess_crisis_route(
        gate=gate(KeyCrisisGateDecisionKind.ACCEPT_SUCCESSION_RECOVERY, subject=old.public_key_bytes),
        route_lease=new_route,
        successor_public_key=new.public_key_bytes,
        succession_verdict=succession,
        now=now + 1,
    )
    assert accepted.decision_kind is CrisisRouteDecisionKind.ACCEPT_SUCCESSOR_ROUTE
    assert accepted.accept


def test_crisisroute_rejects_successor_without_matching_succession_or_under_tombstone() -> None:
    now = 1_766_501_100
    old = kp("old-2")
    new = kp("new-2")
    other = kp("other-2")
    new_route = lease("new-2", now=now, keypair=new, family="new-family")
    bad_succession = SuccessionVerdict(SuccessionVerdictKind.ACCEPT_FIRST, old.public_key_bytes, 1, None, other.public_key_bytes, "wrong successor")
    rejected = assess_crisis_route(
        gate=gate(KeyCrisisGateDecisionKind.ACCEPT_SUCCESSION_RECOVERY, subject=old.public_key_bytes),
        route_lease=new_route,
        successor_public_key=new.public_key_bytes,
        succession_verdict=bad_succession,
        now=now + 1,
    )
    assert rejected.decision_kind is CrisisRouteDecisionKind.QUARANTINE_SUCCESSION_MISMATCH

    tombstoned = assess_crisis_route(
        gate=gate(KeyCrisisGateDecisionKind.ACCEPT_SUCCESSION_RECOVERY, subject=old.public_key_bytes),
        route_lease=new_route,
        successor_public_key=new.public_key_bytes,
        succession_verdict=SuccessionVerdict(SuccessionVerdictKind.ACCEPT_FIRST, old.public_key_bytes, 1, None, new.public_key_bytes, "co-signed"),
        tombstone_digests=(digest("live-tombstone"),),
        now=now + 1,
    )
    assert tombstoned.decision_kind is CrisisRouteDecisionKind.QUARANTINE_TOMBSTONE_PRESENT


def test_sketchboundary_keeps_exact_toy_sketches_in_lab_and_requires_native_adapter_elsewhere() -> None:
    lab = SketchRequest(range_id=digest("range-lab"), engine=SketchEngineKind.EXACT_DEBUG, context=SketchContextKind.LAB, expected_difference=2, capacity=4, element_bits=32, session_salt=b"fresh-salt-lab-0001", allow_exact_debug=True)
    lab_report = assess_sketch_boundary(lab)
    assert lab_report.decision_kind is SketchBoundaryDecisionKind.ACCEPT_EXACT_DEBUG_LAB
    assert lab_report.accept

    prod_exact = SketchRequest(range_id=digest("range-prod"), engine=SketchEngineKind.EXACT_DEBUG, context=SketchContextKind.PRODUCTION, expected_difference=2, capacity=4, element_bits=32, session_salt=b"fresh-salt-prod-001")
    assert assess_sketch_boundary(prod_exact).decision_kind is SketchBoundaryDecisionKind.QUARANTINE_EXACT_DEBUG_OUTSIDE_LAB

    prod_mini = SketchRequest(range_id=digest("range-mini"), engine=SketchEngineKind.MINISKETCH, context=SketchContextKind.PRODUCTION, expected_difference=2, capacity=4, element_bits=32, session_salt=b"fresh-salt-mini-001")
    assert assess_sketch_boundary(prod_mini).decision_kind is SketchBoundaryDecisionKind.CONTINUE_NEED_NATIVE_ADAPTER
    offer = SketchAdapterOffer(SketchEngineKind.MINISKETCH, "0.1-boundary", "adapter-A", max_capacity=8, element_bits=32, supports_extension=True)
    native = assess_sketch_boundary(prod_mini, offer=offer)
    assert native.decision_kind is SketchBoundaryDecisionKind.ACCEPT_NATIVE_ADAPTER_BOUNDARY
    assert native.accept


def test_sketchboundary_capacity_extension_salt_replay_and_short_ids() -> None:
    salt = b"fresh-salt-cap-001"
    request = SketchRequest(range_id=digest("range-cap"), engine=SketchEngineKind.MINISKETCH, context=SketchContextKind.GARDEN_SERVICE, expected_difference=7, capacity=3, element_bits=32, session_salt=salt)
    offer = SketchAdapterOffer(SketchEngineKind.MINISKETCH, "0.1-boundary", "adapter-B", max_capacity=12, element_bits=32, supports_extension=True)
    extension = assess_sketch_boundary(request, offer=offer)
    assert extension.decision_kind is SketchBoundaryDecisionKind.REQUEST_SKETCH_EXTENSION

    replay = assess_sketch_boundary(request, offer=offer, previously_used_salts=(salt,))
    assert replay.decision_kind is SketchBoundaryDecisionKind.QUARANTINE_SALT_REPLAY

    too_raw = SketchRequest(range_id=digest("range-raw"), engine=SketchEngineKind.MINISKETCH, context=SketchContextKind.PRODUCTION, expected_difference=1, capacity=2, element_bits=32, session_salt=b"fresh-salt-raw-0001", raw_element_count=100, privacy_budget_bytes=32)
    assert assess_sketch_boundary(too_raw, offer=offer).decision_kind is SketchBoundaryDecisionKind.REJECT_PRIVACY_BUDGET
    assert short_reconciliation_id(digest("element"), salt=b"fresh-salt-short-01", bits=20) > 0


def test_foldmap_current_path_is_visible() -> None:
    report = audit_fold_map(".")
    assert report.status == "pass"
    assert report.error_count == 0
    assert report.current_entry_count >= 10
