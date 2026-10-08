from __future__ import annotations

from types import SimpleNamespace

from i2p_dht_lab.auditcompact import AuditCompactDecisionKind, assess_audit_compaction, make_audit_compact_bundle
from i2p_dht_lab.auditquorum import AuditReceiptKind, make_audit_receipt
from i2p_dht_lab.identity import DhtKeypair
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.moderationquarantine import ZERO_DIGEST

NOW = 1_956_606
PROFILE = "profile-alpha"
SERVICE = "public-bridge"
SCOPE = sha256(b"scope-alpha")
REQUEST = sha256(b"request-alpha")
PAYLOAD = sha256(b"public-bridge-payload-alpha")
SHADOW = sha256(b"shadow-report")
K1 = DhtKeypair.from_seed(b"a" * 32)
K2 = DhtKeypair.from_seed(b"b" * 32)
K3 = DhtKeypair.from_seed(b"c" * 32)
K4 = DhtKeypair.from_seed(b"d" * 32)


def d(label: str) -> bytes:
    return sha256(label.encode())


def quorum(*, watch: bool = False):
    return SimpleNamespace(
        profile_id=PROFILE,
        service_name=SERVICE,
        scope_digest=SCOPE,
        request_digest=REQUEST,
        bridge_shadow_digest=SHADOW,
        public_payload_digest=PAYLOAD,
        report_digest=d(f"audit-quorum-{watch}"),
        watch=watch,
    )


def receipt(kind: AuditReceiptKind, keypair, fam: str, path: str, *, payload=PAYLOAD, accepted=True, watch=False):
    return make_audit_receipt(
        keypair=keypair,
        kind=kind,
        profile_id=PROFILE,
        service_name=SERVICE,
        scope_digest=SCOPE,
        request_digest=REQUEST,
        bridge_shadow_digest=SHADOW,
        public_payload_digest=payload,
        observation_digest=d(f"receipt-{kind.value}-{fam}-{path}-{payload.hex()[:8]}-{accepted}-{watch}"),
        issued_at=NOW,
        expires_at=NOW + 100,
        family_id=fam,
        path_family=path,
        accepted=accepted,
        watch=watch,
    )


def assess(bundle, raw, q):
    return assess_audit_compaction(
        (bundle,),
        raw_receipts=raw,
        audit_quorum=q,
        now=NOW + 1,
        expected_profile_id=PROFILE,
        expected_service_name=SERVICE,
        expected_scope_digest=SCOPE,
        expected_request_digest=REQUEST,
        expected_public_payload_digest=PAYLOAD,
        min_family_diversity=1,
        min_path_diversity=1,
    )


def test_auditcompact_preserves_refute_evidence_before_summary_acceptance() -> None:
    q = quorum()
    positive = receipt(AuditReceiptKind.PUBLICATION_OBSERVED, K1, "fam-a", "path-a")
    refute = receipt(AuditReceiptKind.REDRESS_GAP, K2, "fam-b", "path-b", watch=True)
    raw = (positive, refute)
    good = make_audit_compact_bundle(keypair=K3, receipts=raw, audit_quorum=q, sequence=1, previous_bundle_digest=ZERO_DIGEST, issued_at=NOW, expires_at=NOW + 100, family_id="compact-a", path_family="compact-path-a")
    result = assess(good, raw, q)
    assert result.decision_kind is AuditCompactDecisionKind.ACCEPT_WITH_WATCH
    assert refute.receipt_digest in result.refute_digests

    bad = make_audit_compact_bundle(keypair=K3, receipts=raw, audit_quorum=q, sequence=2, previous_bundle_digest=ZERO_DIGEST, issued_at=NOW, expires_at=NOW + 100, family_id="compact-a", path_family="compact-path-a", omit_refute_digests=(refute.receipt_digest,))
    assert assess(bad, raw, q).decision_kind is AuditCompactDecisionKind.QUARANTINE_DROPPED_REFUTE_EVIDENCE


def test_auditcompact_preserves_same_family_fork_evidence() -> None:
    q = quorum()
    fork_a = receipt(AuditReceiptKind.PUBLICATION_OBSERVED, K1, "fork-family", "path-a", payload=PAYLOAD)
    fork_b = receipt(AuditReceiptKind.PUBLICATION_OBSERVED, K2, "fork-family", "path-b", payload=d("different-public-payload"))
    raw = (fork_a, fork_b)
    good = make_audit_compact_bundle(keypair=K4, receipts=raw, audit_quorum=q, sequence=1, issued_at=NOW, expires_at=NOW + 100, family_id="compact-b", path_family="compact-path-b")
    assert assess(good, raw, q).decision_kind is AuditCompactDecisionKind.ACCEPT_WITH_WATCH

    bad = make_audit_compact_bundle(keypair=K4, receipts=raw, audit_quorum=q, sequence=2, issued_at=NOW, expires_at=NOW + 100, family_id="compact-b", path_family="compact-path-b", omit_fork_digests=(fork_a.receipt_digest,))
    assert assess(bad, raw, q).decision_kind is AuditCompactDecisionKind.QUARANTINE_DROPPED_FORK_EVIDENCE
