from __future__ import annotations

from pathlib import Path

from i2p_dht_lab.auditquorum import AuditQuorumDecisionKind, AuditReceiptKind, assess_audit_quorum, make_audit_receipt
from i2p_dht_lab.bridgegovernancefold import audit_bridge_governance_fold
from i2p_dht_lab.bridgeledger import BridgeLedgerAction, BridgeLedgerDecisionKind, BridgeLedgerReport
from i2p_dht_lab.bridgequenchlane import BridgeQuenchDecisionKind, BridgeQuenchReport
from i2p_dht_lab.bridgeshadow import BridgeShadowAction, BridgeShadowDecisionKind, assess_bridge_shadow, make_bridge_shadow_step
from i2p_dht_lab.identity import DhtKeypair
from i2p_dht_lab.ids import DOMAIN, sha256
from i2p_dht_lab.moderationquarantine import ModerationAction, ZERO_DIGEST
from i2p_dht_lab.policyportfolio import PolicyDisposition, PolicyPortfolioDecisionKind, PolicyPortfolioReport
from i2p_dht_lab.publicationfold import audit_publication_fold
from i2p_dht_lab.publicationguard import ExposureClass, PublicationDecisionKind, PublicationIntent, PublicationReport
from i2p_dht_lab.publicationledger import PublicationAction, PublicationLedgerDecisionKind, PublicationLedgerReport
from i2p_dht_lab.redressgc import RedressGcDecisionKind, RedressGcItem, RedressGcItemKind, RedressGcPolicy, assess_redress_gc

NOW = 1_900_000
PROFILE = "profile-alpha"
SERVICE = "public-bridge"
SCOPE = sha256(DOMAIN + b":rev0048:scope")
REQUEST = sha256(DOMAIN + b":rev0048:request")
SUBJECT = sha256(DOMAIN + b":rev0048:subject")
PAYLOAD = sha256(DOMAIN + b":rev0048:payload")


def d(label: str) -> bytes:
    return sha256(DOMAIN + b":rev0048-test:" + label.encode("utf-8"))


def key(n: int) -> DhtKeypair:
    return DhtKeypair.from_seed(bytes([n]) * 32)


K1, K2, K3, K4 = (key(n) for n in range(1, 5))


def bridge_report(*, accept=True, watch=False) -> BridgeLedgerReport:
    kind = BridgeLedgerDecisionKind.ACCEPT_WITH_WATCH if watch else BridgeLedgerDecisionKind.ACCEPT_LEDGER
    if not accept:
        kind = BridgeLedgerDecisionKind.HOLD_REDRESS_NEEDED
    return BridgeLedgerReport(kind, accept, watch, "bridge", PROFILE, SERVICE, BridgeLedgerAction.PUBLIC_REFRESH, d(f"bridge-entry-{accept}-{watch}"), (d("shadow"), d("egress")), 3, 3, 8, d(f"bridge-report-{accept}-{watch}"))


def pub_guard(*, accept=True, watch=False, intent=PublicationIntent.PUBLIC_REFRESH) -> PublicationReport:
    kind = PublicationDecisionKind.ACCEPT_WITH_WATCH if watch else PublicationDecisionKind.ACCEPT_PUBLICATION
    if not accept:
        kind = PublicationDecisionKind.HOLD_LEDGER_NOT_ACCEPTED
    return PublicationReport(kind, accept, watch, "publication guard", PROFILE, SERVICE, intent, ExposureClass.DIGEST_ONLY, d(f"pub-capsule-{accept}-{watch}-{intent.value}"), (d("bridge"), d("policy"), d("egress")), 2, 2, 2, d(f"pubguard-report-{accept}-{watch}-{intent.value}"))


def pub_ledger(*, accept=True, watch=False) -> PublicationLedgerReport:
    kind = PublicationLedgerDecisionKind.ACCEPT_WITH_WATCH if watch else PublicationLedgerDecisionKind.ACCEPT_PUBLICATION
    if not accept:
        kind = PublicationLedgerDecisionKind.HOLD_BRIDGE_LEDGER_NOT_ACCEPTED
    bridge = bridge_report()
    return PublicationLedgerReport(kind, accept, watch, "publication ledger", PROFILE, SERVICE, PublicationAction.PUBLISH_PUBLIC, SCOPE, REQUEST, d(f"publedger-entry-{accept}-{watch}"), bridge.report_digest, ZERO_DIGEST, ZERO_DIGEST, 2, 2, 2, d(f"publedger-report-{accept}-{watch}"))


def quench_report(*, active=False, watch=False, cont=True) -> BridgeQuenchReport:
    kind = BridgeQuenchDecisionKind.QUENCH_STALE_PUBLIC_REPLAY if active else BridgeQuenchDecisionKind.ACCEPT_CONTINUE
    return BridgeQuenchReport(kind, cont and not active, active, watch or active, "quench", PROFILE, SERVICE, SCOPE, REQUEST, pub_ledger().report_digest, (), 2, 2, 0, 0, d(f"quench-report-{active}-{watch}-{cont}"))


def policy_report(*, accept=True, watch=False) -> PolicyPortfolioReport:
    kind = PolicyPortfolioDecisionKind.ACCEPT_WARN if watch else PolicyPortfolioDecisionKind.ACCEPT_ALLOW
    if not accept:
        kind = PolicyPortfolioDecisionKind.QUARANTINE_DENY
    return PolicyPortfolioReport(kind, accept, watch, not accept, "policy", PROFILE, SERVICE, ModerationAction.PUBLIC_BRIDGE, SUBJECT, (d("policy-a"), d("policy-b"), d("policy-c")), 3, 3, 3, 3, PolicyDisposition.ALLOW, d("policy-a"), d(f"policy-report-{accept}-{watch}"))


def shadow_step(*, keypair=K1, seq=1, family="shadow-a", path="path-a", payload=PAYLOAD, publication=None, ledger=None, quench=None, action=BridgeShadowAction.SHADOW_REFRESH):
    publication = publication or pub_guard()
    ledger = ledger or pub_ledger()
    quench = quench or quench_report()
    return make_bridge_shadow_step(
        keypair=keypair,
        action=action,
        profile_id=PROFILE,
        service_name=SERVICE,
        scope_digest=SCOPE,
        request_digest=REQUEST,
        publication_report_digest=publication.report_digest,
        publication_ledger_digest=ledger.report_digest,
        quench_report_digest=quench.report_digest,
        payload_digest=payload,
        shadow_effect_digest=d(f"shadow-effect-{seq}-{family}"),
        sequence=seq,
        previous_shadow_digest=ZERO_DIGEST,
        issued_at=NOW,
        expires_at=NOW + 100,
        family_id=family,
        path_family=path,
    )


def accepted_shadow(*, publication=None, ledger=None, quench=None):
    publication = publication or pub_guard()
    ledger = ledger or pub_ledger()
    quench = quench or quench_report()
    steps = (
        shadow_step(keypair=K1, seq=1, family="shadow-a", path="path-a", publication=publication, ledger=ledger, quench=quench),
        shadow_step(keypair=K2, seq=2, family="shadow-b", path="path-b", publication=publication, ledger=ledger, quench=quench),
    )
    return assess_bridge_shadow(steps, publication=publication, publication_ledger=ledger, quench=quench, now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_payload_digest=PAYLOAD)


def audit_receipt(*, keypair=K3, kind=AuditReceiptKind.PUBLICATION_OBSERVED, family="audit-a", path="audit-a", shadow=None, payload=PAYLOAD, accepted=True, watch=False):
    shadow = shadow or accepted_shadow()
    return make_audit_receipt(
        keypair=keypair,
        kind=kind,
        profile_id=PROFILE,
        service_name=SERVICE,
        scope_digest=SCOPE,
        request_digest=REQUEST,
        bridge_shadow_digest=shadow.report_digest,
        public_payload_digest=payload,
        observation_digest=d(f"audit-{kind.value}-{family}-{path}"),
        accepted=accepted,
        watch=watch,
        issued_at=NOW,
        expires_at=NOW + 100,
        family_id=family,
        path_family=path,
    )


def item(kind: RedressGcItemKind, label: str, *, seq=1, expires=100, subject=SUBJECT, family=None, bytes_=1, pinned=False) -> RedressGcItem:
    return RedressGcItem(kind, SCOPE, REQUEST, subject, d(label), seq, NOW, NOW + expires, family or f"family-{label}", bytes_, pinned)


def test_bridge_shadow_accepts_and_rejects_risky_steps() -> None:
    report = accepted_shadow()
    assert report.decision_kind is BridgeShadowDecisionKind.ACCEPT_SHADOW
    assert report.accept
    assert report.payload_digest == PAYLOAD

    publication = pub_guard()
    ledger = pub_ledger()
    quench = quench_report(active=True)
    assert assess_bridge_shadow((shadow_step(publication=publication, ledger=ledger, quench=quench),), publication=publication, publication_ledger=ledger, quench=quench, now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_payload_digest=PAYLOAD).decision_kind is BridgeShadowDecisionKind.HOLD_QUENCH

    quench_ok = quench_report()
    step = shadow_step(publication=publication, ledger=ledger, quench=quench_ok)
    assert assess_bridge_shadow((step,), publication=publication, publication_ledger=ledger, quench=quench_ok, now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_payload_digest=PAYLOAD, previously_seen_steps=(step.step_digest,)).decision_kind is BridgeShadowDecisionKind.QUARANTINE_REPLAY

    fork = shadow_step(keypair=K2, seq=1, family="shadow-b", path="path-b", payload=d("other"), publication=publication, ledger=ledger, quench=quench_ok)
    assert assess_bridge_shadow((step, fork), publication=publication, publication_ledger=ledger, quench=quench_ok, now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_payload_digest=PAYLOAD).decision_kind is BridgeShadowDecisionKind.QUARANTINE_PAYLOAD_DIGEST_DRIFT


def test_audit_quorum_accepts_diverse_receipts_and_blocks_negative_observations() -> None:
    shadow = accepted_shadow()
    good = (
        audit_receipt(keypair=K3, family="audit-a", path="path-a", shadow=shadow),
        audit_receipt(keypair=K4, family="audit-b", path="path-b", shadow=shadow),
    )
    report = assess_audit_quorum(good, bridge_shadow=shadow, now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_public_payload_digest=PAYLOAD)
    assert report.decision_kind is AuditQuorumDecisionKind.ACCEPT_AUDITED
    assert report.accept

    stale = (audit_receipt(keypair=K3, kind=AuditReceiptKind.STALE_PUBLIC_RECORD, family="a", path="a", shadow=shadow), audit_receipt(keypair=K4, family="b", path="b", shadow=shadow))
    assert assess_audit_quorum(stale, bridge_shadow=shadow, now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_public_payload_digest=PAYLOAD).decision_kind is AuditQuorumDecisionKind.QUARANTINE_STALE_PUBLIC_RECORD

    receipt = audit_receipt(shadow=shadow)
    assert assess_audit_quorum((receipt,), bridge_shadow=shadow, now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_public_payload_digest=PAYLOAD, previously_seen_receipts=(receipt.receipt_digest,)).decision_kind is AuditQuorumDecisionKind.QUARANTINE_REPLAY


def test_redress_gc_preserves_hard_negative_memory_under_cleanup() -> None:
    expired_soft = item(RedressGcItemKind.SOFT_EXPIRED, "soft", seq=1, expires=1)
    hard = item(RedressGcItemKind.HARD_NEGATIVE, "hard", seq=2, pinned=True)
    lift = item(RedressGcItemKind.REDRESS_LIFT, "lift", seq=3)
    report = assess_redress_gc((expired_soft, hard, lift), now=NOW + 2, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, live_hard_negative_digests=(hard.item_digest,), active_redress_digests=(lift.item_digest,))
    assert report.decision_kind is RedressGcDecisionKind.ACCEPT_WITH_WATCH
    assert expired_soft.item_digest in report.dropped_digests
    assert hard.item_digest in report.retained_digests
    assert lift.item_digest in report.retained_digests

    old_hard = item(RedressGcItemKind.HARD_NEGATIVE, "old-hard", seq=4, expires=1, pinned=False)
    assert assess_redress_gc((old_hard,), now=NOW + 2, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, live_hard_negative_digests=(old_hard.item_digest,)).decision_kind is RedressGcDecisionKind.QUARANTINE_LIVE_HARD_NEGATIVE_DROP

    fork_a = item(RedressGcItemKind.APPEAL_OBSERVATION, "fork-a", seq=7)
    fork_b = item(RedressGcItemKind.APPEAL_OBSERVATION, "fork-b", seq=7)
    assert assess_redress_gc((fork_a, fork_b), now=NOW + 1, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, policy=RedressGcPolicy(preserve_fork_evidence=True)).decision_kind is RedressGcDecisionKind.QUARANTINE_SAME_SEQUENCE_CONFLICT


def test_bridge_governance_fold_pins_current_revision_path() -> None:
    root = Path(__file__).resolve().parents[1]
    assert audit_publication_fold(root, revision="rev0047").status == "pass"
    report = audit_bridge_governance_fold(root, revision="rev0048")
    assert report.status == "pass"
    assert report.predecessor_status == "pass"
