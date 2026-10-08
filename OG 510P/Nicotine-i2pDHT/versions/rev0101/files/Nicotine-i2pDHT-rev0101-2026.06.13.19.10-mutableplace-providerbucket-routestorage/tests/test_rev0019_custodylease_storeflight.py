from __future__ import annotations

from dataclasses import replace

from i2p_dht_lab.custodyaudit import (
    CustodyAuditChallenge,
    CustodyAuditDecisionKind,
    CustodyAuditPolicy,
    CustodyProof,
    CustodyProofKind,
    assess_custody_proofs,
)
from i2p_dht_lab.identity import DhtKeypair, NodeIdentity
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.storecontract import (
    StoreContractDecisionKind,
    StoreContractPolicy,
    StoreContractReceipt,
    StoreContractRequest,
    StorePurpose,
    StoreReceiptKind,
    assess_store_contracts,
)
from i2p_dht_lab.storerepair import StoreRepairActionKind, StoreRepairPolicy, plan_store_repair
from i2p_dht_lab.surfaceledger import audit_surface_ledger


def kp(n: int) -> DhtKeypair:
    return DhtKeypair.from_seed(bytes([n % 256]) * 32)


def ident(n: int, prefix: str = "store") -> NodeIdentity:
    return NodeIdentity.create(destination=f"{prefix}-{n}.b32.i2p", keypair=kp(n))


def request(*, issued_at: int = 10_000, ttl: int = 10_000) -> StoreContractRequest:
    return StoreContractRequest(
        target=sha256(b"rev0019 store target"),
        record_digest=sha256(b"rev0019 exact record digest"),
        purpose=StorePurpose.MUTABLE_HEAD,
        namespace="heads",
        byte_count=512,
        issued_at=issued_at,
        expires_at=issued_at + ttl,
        slot_digest=sha256(b"rev0019 slot"),
    )


def receipt(n: int, family: str, req: StoreContractRequest, *, kind: StoreReceiptKind = StoreReceiptKind.ACCEPTED, issued_at: int = 10_010, ttl: int = 4_000, rank: int = 0, retry_after: int = 0) -> StoreContractReceipt:
    return StoreContractReceipt.create(
        keypair=kp(n),
        storage_node_id=ident(n).node_id,
        family_id=family,
        request=req,
        kind=kind,
        replica_rank=rank,
        issued_at=issued_at,
        ttl=ttl,
        retry_after_seconds=retry_after,
        note="rev0019 fixture",
    )


def challenge_for(req: StoreContractRequest, *, now: int = 10_100) -> CustodyAuditChallenge:
    return CustodyAuditChallenge.create(target=req.target, record_digest=req.record_digest, nonce=sha256(b"fresh nonce"), issued_at=now, ttl=300)


def proof(n: int, contract: StoreContractReceipt, challenge: CustodyAuditChallenge, *, kind: CustodyProofKind = CustodyProofKind.HAVE_EXACT_DIGEST, observed_at: int = 10_120, digest: bytes | None = None, retry_after: int = 0) -> CustodyProof:
    return CustodyProof.create(
        keypair=kp(n),
        contract=contract,
        challenge=challenge,
        kind=kind,
        observed_at=observed_at,
        response_digest=digest,
        retry_after_seconds=retry_after,
        note="rev0019 proof fixture",
    )


def accepted_contracts(req: StoreContractRequest) -> tuple[StoreContractReceipt, ...]:
    return tuple(receipt(n, family, req, rank=i) for i, (n, family) in enumerate(((1, "east"), (2, "west"), (3, "north"), (4, "south")), start=0))


def test_store_contract_accepts_diverse_exact_leases() -> None:
    req = request()
    report = assess_store_contracts(req, accepted_contracts(req), now=10_100, policy=StoreContractPolicy(min_accepts=4, min_families=3, max_per_family=2))
    assert report.decision.kind is StoreContractDecisionKind.STORED_DIVERSE
    assert report.decision.accept
    assert len(report.accepted_families) >= 3
    assert len(report.transcript_digest) == 32


def test_store_contract_holds_for_useful_refusals_instead_of_flooding() -> None:
    req = request()
    refusals = (
        receipt(10, "east", req, kind=StoreReceiptKind.USEFUL_REFUSAL, retry_after=900),
        receipt(11, "west", req, kind=StoreReceiptKind.OVER_CAPACITY, retry_after=1200),
    )
    report = assess_store_contracts(req, refusals, now=10_100, policy=StoreContractPolicy(min_accepts=3, min_families=2))
    assert report.decision.kind is StoreContractDecisionKind.HOLD_USEFUL_REFUSALS
    assert not report.decision.accept
    assert report.decision.retry_after_seconds >= 1200


def test_store_contract_quarantines_signed_wrong_digest_pressure() -> None:
    req = request()
    receipts = (receipt(20, "east", req), receipt(21, "west", req, kind=StoreReceiptKind.WRONG_DIGEST))
    report = assess_store_contracts(req, receipts, now=10_100)
    assert report.decision.kind is StoreContractDecisionKind.QUARANTINE_CONTRADICTION
    assert not report.decision.accept


def test_store_contract_quarantines_invalid_receipt_pressure() -> None:
    req = request()
    other = request(issued_at=20_000, ttl=10_000)
    bad1 = receipt(30, "east", other)
    bad2 = receipt(31, "west", other)
    report = assess_store_contracts(req, (bad1, bad2), now=10_100, policy=StoreContractPolicy(invalid_pressure_limit=1))
    assert report.decision.kind is StoreContractDecisionKind.QUARANTINE_INVALID_PRESSURE
    assert report.invalid_receipt_count == 2


def test_custody_audit_accepts_fresh_challenge_bound_family_diverse_proofs() -> None:
    req = request()
    contracts = accepted_contracts(req)
    challenge = challenge_for(req)
    proofs = tuple(proof(n, contract, challenge) for n, contract in zip((1, 2, 3, 4), contracts))
    report = assess_custody_proofs(challenge, contracts=contracts, proofs=proofs, now=10_130, policy=CustodyAuditPolicy(min_proofs=3, min_families=3, max_per_family=1))
    assert report.decision.kind is CustodyAuditDecisionKind.PROVEN_DIVERSE
    assert report.decision.accept
    assert len(report.proof_families) >= 3


def test_custody_audit_quarantines_replayed_old_challenge_proof() -> None:
    req = request()
    contracts = accepted_contracts(req)
    old_challenge = CustodyAuditChallenge.create(target=req.target, record_digest=req.record_digest, nonce=sha256(b"old nonce"), issued_at=10_090, ttl=300)
    fresh_challenge = challenge_for(req, now=10_100)
    replayed = proof(1, contracts[0], old_challenge, observed_at=10_110)
    report = assess_custody_proofs(fresh_challenge, contracts=contracts, proofs=(replayed,), now=10_130)
    assert report.decision.kind is CustodyAuditDecisionKind.QUARANTINE_REPLAY_PRESSURE
    assert report.replay_pressure_count == 1


def test_custody_audit_quarantines_wrong_digest_proof() -> None:
    req = request()
    contracts = accepted_contracts(req)
    challenge = challenge_for(req)
    bad = proof(1, contracts[0], challenge, kind=CustodyProofKind.WRONG_DIGEST, digest=sha256(b"wrong bytes"))
    report = assess_custody_proofs(challenge, contracts=contracts, proofs=(bad,), now=10_130)
    assert report.decision.kind is CustodyAuditDecisionKind.QUARANTINE_FALSE_PROOF
    assert report.false_proof_count == 1


def test_custody_audit_refusal_is_backoff_not_proof() -> None:
    req = request()
    contracts = accepted_contracts(req)
    challenge = challenge_for(req)
    refusal = proof(1, contracts[0], challenge, kind=CustodyProofKind.USEFUL_REFUSAL, retry_after=800)
    report = assess_custody_proofs(challenge, contracts=contracts, proofs=(refusal,), now=10_130)
    assert report.decision.kind is CustodyAuditDecisionKind.HOLD_USEFUL_REFUSALS
    assert not report.decision.accept
    assert report.decision.retry_after_seconds >= 800


def test_store_repair_no_action_after_proven_custody_and_long_leases() -> None:
    req = request()
    contracts = accepted_contracts(req)
    store_report = assess_store_contracts(req, contracts, now=10_100)
    challenge = challenge_for(req)
    proofs = tuple(proof(n, contract, challenge) for n, contract in zip((1, 2, 3, 4), contracts))
    custody_report = assess_custody_proofs(challenge, contracts=contracts, proofs=proofs, now=10_130)
    plan = plan_store_repair(store_report=store_report, custody_report=custody_report, now=10_130, policy=StoreRepairPolicy(renew_within_seconds=500))
    assert plan.action is StoreRepairActionKind.NO_ACTION
    assert len(plan.digest) == 32


def test_store_repair_renews_near_expiry_even_after_good_audit() -> None:
    req = request(ttl=1_000)
    contracts = tuple(receipt(n, family, req, ttl=250, rank=i) for i, (n, family) in enumerate(((1, "east"), (2, "west"), (3, "north"), (4, "south")), start=0))
    store_report = assess_store_contracts(req, contracts, now=10_100)
    challenge = challenge_for(req)
    proofs = tuple(proof(n, contract, challenge) for n, contract in zip((1, 2, 3, 4), contracts))
    custody_report = assess_custody_proofs(challenge, contracts=contracts, proofs=proofs, now=10_130)
    plan = plan_store_repair(store_report=store_report, custody_report=custody_report, now=10_130, policy=StoreRepairPolicy(renew_within_seconds=200))
    assert plan.action is StoreRepairActionKind.RENEW_SOON


def test_store_repair_quarantines_false_custody_even_if_store_leases_look_good() -> None:
    req = request()
    contracts = accepted_contracts(req)
    store_report = assess_store_contracts(req, contracts, now=10_100)
    challenge = challenge_for(req)
    bad = proof(1, contracts[0], challenge, kind=CustodyProofKind.WRONG_DIGEST, digest=sha256(b"wrong"))
    custody_report = assess_custody_proofs(challenge, contracts=contracts, proofs=(bad,), now=10_130)
    plan = plan_store_repair(store_report=store_report, custody_report=custody_report, now=10_130)
    assert plan.action is StoreRepairActionKind.QUARANTINE_RECORD
    assert plan.quarantine


def test_custody_proof_signature_is_over_challenge_hash() -> None:
    req = request()
    contracts = accepted_contracts(req)
    challenge = challenge_for(req)
    original = proof(1, contracts[0], challenge)
    tampered = replace(original, challenge_hash=sha256(b"tampered challenge"))
    report = assess_custody_proofs(challenge, contracts=contracts, proofs=(tampered,), now=10_130)
    assert report.decision.kind is CustodyAuditDecisionKind.QUARANTINE_FALSE_PROOF


def test_surface_ledger_still_accepts_rev0019_active_surface() -> None:
    report = audit_surface_ledger(__import__("pathlib").Path(__file__).resolve().parents[1])
    assert report.ok
    assert report.error_count == 0
