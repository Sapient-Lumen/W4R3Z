from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from i2p_dht_lab.ackarchive import AckArchiveDecisionKind, assess_ack_archive, make_ack_archive_entry
from i2p_dht_lab.ackfold import audit_ack_fold
from i2p_dht_lab.ackprunejoin import AckPruneJoinDecisionKind, assess_ack_prune_join
from i2p_dht_lab.deliverysettlement import DeliverySettlementDecisionKind, assess_delivery_settlement, expected_settlement_ack_digest, make_delivery_settlement_marker
from i2p_dht_lab.deliverywitness import assess_delivery_witness, make_delivery_receipt
from i2p_dht_lab.ids import DOMAIN, sha256
from i2p_dht_lab.livesendgate import assess_live_send_gate
from i2p_dht_lab.sendfence import assess_send_fence, make_send_fence_marker
from i2p_dht_lab.sideeffectjournal import SideEffectAction

PROFILE = "rev0061-profile"
SERVICE = "rev0061-public-edge"
ACTION = SideEffectAction.OUTBOUND_PUBLIC_SEND
SCOPE = sha256(DOMAIN + b":rev0061:scope")
REQUEST = sha256(DOMAIN + b":rev0061:request")
PAYLOAD = sha256(DOMAIN + b":rev0061:payload")
IDEM = sha256(DOMAIN + b":rev0061:idem")
SESSION = sha256(DOMAIN + b":rev0061:session")
DESTINATION = sha256(DOMAIN + b":rev0061:destination")
ENDPOINT = sha256(DOMAIN + b":rev0061:endpoint")


def d(label: str) -> bytes:
    return sha256(DOMAIN + b":rev0061-test:" + label.encode())


def report(label: str, **kw):
    base = dict(
        report_digest=d(label),
        accept=True,
        watch=False,
        quarantined=False,
        action=ACTION,
        profile_id=PROFILE,
        service_name=SERVICE,
        scope_digest=SCOPE,
        request_digest=REQUEST,
        payload_digest=PAYLOAD,
        idempotency_key=IDEM,
        session_digest=SESSION,
        destination_digest=DESTINATION,
        endpoint_digest=ENDPOINT,
        family_count=2,
        path_family_count=2,
        hard_negative_count=0,
        terminal=True,
        retry_required=False,
    )
    base.update(kw)
    return SimpleNamespace(**base)


def accepted_gate():
    return assess_live_send_gate(
        canary_join_report=report("canary"),
        settlement_store_report=report("settlement-store"),
        tomb_repair_join_report=report("tomb-repair"),
        side_effect_journal_report=report("side-effect-journal"),
        outbox_drain_report=report("outbox-drain"),
        public_payload_bytes=512,
    )


def accepted_witness_and_fence():
    gate = accepted_gate()
    r1 = make_delivery_receipt(live_send_gate_report=gate, sequence=1, family_id="a", path_family_id="pa")
    r2 = make_delivery_receipt(live_send_gate_report=gate, sequence=2, previous_digest=r1.receipt_digest, family_id="b", path_family_id="pb")
    witness = assess_delivery_witness(live_send_gate_report=gate, receipts=(r1, r2), previous_digest=r1.previous_digest)
    m1 = make_send_fence_marker(live_send_gate_report=gate, delivery_witness_report=witness, sequence=1, family_id="a", path_family_id="pa")
    m2 = make_send_fence_marker(live_send_gate_report=gate, delivery_witness_report=witness, sequence=2, previous_digest=m1.marker_digest, family_id="b", path_family_id="pb")
    fence = assess_send_fence(live_send_gate_report=gate, delivery_witness_report=witness, markers=(m1, m2), previous_digest=m1.previous_digest)
    return gate, witness, fence


def accepted_settlement():
    _, witness, fence = accepted_witness_and_fence()
    s1 = make_delivery_settlement_marker(send_fence_report=fence, delivery_witness_report=witness, sequence=1, family_id="a", path_family_id="pa")
    s2 = make_delivery_settlement_marker(send_fence_report=fence, delivery_witness_report=witness, sequence=2, previous_digest=s1.marker_digest, family_id="b", path_family_id="pb")
    settlement = assess_delivery_settlement(send_fence_report=fence, delivery_witness_report=witness, markers=(s1, s2), previous_digest=s1.previous_digest)
    return witness, fence, settlement


def accepted_archive():
    witness, fence, settlement = accepted_settlement()
    a1 = make_ack_archive_entry(delivery_settlement_report=settlement, sequence=1, family_id="a", path_family_id="pa")
    a2 = make_ack_archive_entry(delivery_settlement_report=settlement, sequence=2, previous_digest=a1.entry_digest, family_id="b", path_family_id="pb")
    archive = assess_ack_archive(delivery_settlement_report=settlement, entries=(a1, a2), previous_digest=a1.previous_digest)
    return witness, fence, settlement, archive


def test_delivery_settlement_accepts_diverse_exact_boundary() -> None:
    _, witness, fence = accepted_witness_and_fence()
    s1 = make_delivery_settlement_marker(send_fence_report=fence, delivery_witness_report=witness, sequence=1, family_id="a", path_family_id="pa")
    s2 = make_delivery_settlement_marker(send_fence_report=fence, delivery_witness_report=witness, sequence=2, previous_digest=s1.marker_digest, family_id="b", path_family_id="pb")
    settlement = assess_delivery_settlement(send_fence_report=fence, delivery_witness_report=witness, markers=(s1, s2), previous_digest=s1.previous_digest)
    assert settlement.decision_kind is DeliverySettlementDecisionKind.ACCEPT_DELIVERY_SETTLED
    assert settlement.accept and settlement.terminal
    assert settlement.accepted_marker_digest == s2.marker_digest
    assert expected_settlement_ack_digest(witness) == s1.ack_digest


def test_delivery_settlement_rejects_ack_conflict_boundary_drift_and_fork() -> None:
    _, witness, fence = accepted_witness_and_fence()
    good = make_delivery_settlement_marker(send_fence_report=fence, delivery_witness_report=witness, sequence=1, family_id="a", path_family_id="pa")
    bad_ack = make_delivery_settlement_marker(send_fence_report=fence, delivery_witness_report=witness, sequence=1, family_id="a", path_family_id="pa", ack_digest=d("bad-ack"))
    assert assess_delivery_settlement(send_fence_report=fence, delivery_witness_report=witness, markers=(bad_ack,)).decision_kind is DeliverySettlementDecisionKind.QUARANTINE_ACK_CONFLICT

    drift = make_delivery_settlement_marker(send_fence_report=report("other-fence", live_send_gate_digest=fence.live_send_gate_digest), delivery_witness_report=witness, sequence=1, family_id="a", path_family_id="pa")
    assert assess_delivery_settlement(send_fence_report=fence, delivery_witness_report=witness, markers=(drift,)).decision_kind is DeliverySettlementDecisionKind.QUARANTINE_BOUNDARY_DRIFT

    fork = make_delivery_settlement_marker(send_fence_report=fence, delivery_witness_report=witness, sequence=1, family_id="b", path_family_id="pb")
    assert assess_delivery_settlement(send_fence_report=fence, delivery_witness_report=witness, markers=(good, fork)).decision_kind is DeliverySettlementDecisionKind.QUARANTINE_SEQUENCE_FORK


def test_ack_archive_accepts_and_rejects_idempotency_conflict() -> None:
    _, _, settlement = accepted_settlement()
    a1 = make_ack_archive_entry(delivery_settlement_report=settlement, sequence=1, family_id="a", path_family_id="pa")
    a2 = make_ack_archive_entry(delivery_settlement_report=settlement, sequence=2, previous_digest=a1.entry_digest, family_id="b", path_family_id="pb")
    archive = assess_ack_archive(delivery_settlement_report=settlement, entries=(a1, a2), previous_digest=a1.previous_digest)
    assert archive.decision_kind is AckArchiveDecisionKind.ACCEPT_ARCHIVED_DELIVERY
    assert archive.accept and archive.terminal

    conflict = assess_ack_archive(delivery_settlement_report=settlement, entries=(a1, a2), prior_payload_digests_for_idempotency=(d("other-payload"),))
    assert conflict.decision_kind is AckArchiveDecisionKind.QUARANTINE_IDEMPOTENCY_CONFLICT


def test_ack_archive_rejects_replay_previous_and_low_diversity() -> None:
    _, _, settlement = accepted_settlement()
    a1 = make_ack_archive_entry(delivery_settlement_report=settlement, sequence=1, family_id="a", path_family_id="pa")
    assert assess_ack_archive(delivery_settlement_report=settlement, entries=(a1,), seen_entry_digests=(a1.entry_digest,)).decision_kind is AckArchiveDecisionKind.QUARANTINE_REPLAY
    assert assess_ack_archive(delivery_settlement_report=settlement, entries=(a1,), previous_digest=d("wrong-prev")).decision_kind is AckArchiveDecisionKind.QUARANTINE_PREVIOUS_MISMATCH
    assert assess_ack_archive(delivery_settlement_report=settlement, entries=(a1,), previous_digest=a1.previous_digest, min_family_count=2).decision_kind is AckArchiveDecisionKind.HOLD_LOW_FAMILY_DIVERSITY


def test_ack_prune_join_accepts_only_after_archive_and_rejects_drift() -> None:
    witness, fence, settlement, archive = accepted_archive()
    joined = assess_ack_prune_join(delivery_settlement_report=settlement, ack_archive_report=archive, send_fence_report=fence, delivery_witness_report=witness)
    assert joined.decision_kind is AckPruneJoinDecisionKind.ACCEPT_PRUNE_AFTER_ARCHIVE
    assert joined.accept and joined.prune_allowed

    pending = assess_ack_prune_join(delivery_settlement_report=settlement, ack_archive_report=None, send_fence_report=fence, delivery_witness_report=witness)
    assert pending.decision_kind is AckPruneJoinDecisionKind.HOLD_PENDING_ARCHIVE

    drift_archive = SimpleNamespace(**{**archive.__dict__, "request_digest": d("other-request")})
    assert assess_ack_prune_join(delivery_settlement_report=settlement, ack_archive_report=drift_archive, send_fence_report=fence, delivery_witness_report=witness).decision_kind is AckPruneJoinDecisionKind.QUARANTINE_BOUNDARY_DRIFT


def test_ack_prune_join_rejects_digest_drift_and_hard_negative() -> None:
    witness, fence, settlement, archive = accepted_archive()
    bad_archive = SimpleNamespace(**{**archive.__dict__, "delivery_settlement_digest": d("wrong-settlement")})
    assert assess_ack_prune_join(delivery_settlement_report=settlement, ack_archive_report=bad_archive, send_fence_report=fence, delivery_witness_report=witness).decision_kind is AckPruneJoinDecisionKind.QUARANTINE_DIGEST_DRIFT

    bad_settlement = SimpleNamespace(**{**settlement.__dict__, "hard_negative_count": 1})
    assert assess_ack_prune_join(delivery_settlement_report=bad_settlement, ack_archive_report=archive, send_fence_report=fence, delivery_witness_report=witness).decision_kind is AckPruneJoinDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE


def test_ackfold_current_revision_audit_passes() -> None:
    root = Path(__file__).resolve().parents[1]
    fold = audit_ack_fold(root, revision="rev0061", artifact_stem=root.name)
    assert fold.status == "pass", fold.findings
