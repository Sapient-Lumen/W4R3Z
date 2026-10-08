from __future__ import annotations

from dataclasses import replace

from i2p_dht_lab.bridgeledger import BridgeLedgerAction, BridgeLedgerDecisionKind, BridgeLedgerReport
from i2p_dht_lab.egressmeter import EgressBudget, EgressEvent, EgressEventKind, assess_egress_window
from i2p_dht_lab.identity import DhtKeypair
from i2p_dht_lab.ids import DOMAIN, sha256
from i2p_dht_lab.moderationquarantine import ModerationAction, ZERO_DIGEST
from i2p_dht_lab.policyportfolio import (
    PolicyPortfolioDecisionKind,
    PolicySourceKind,
    PolicyDisposition,
    assess_policy_portfolio,
    make_policy_source_capsule,
)
from i2p_dht_lab.publicationfold import audit_publication_fold
from i2p_dht_lab.publicationguard import (
    ExposureClass,
    PublicationDecisionKind,
    PublicationIntent,
    assess_publication,
    make_publication_capsule,
)

NOW = 1_900_000
PROFILE = "profile-alpha"
SERVICE = "public-bridge"
SCOPE = sha256(DOMAIN + b":rev0047:scope")
REQUEST = sha256(DOMAIN + b":rev0047:request")
SUBJECT = sha256(DOMAIN + b":rev0047:subject")


def d(label: str) -> bytes:
    return sha256(DOMAIN + b":rev0047-test:" + label.encode("utf-8"))


def key(n: int) -> DhtKeypair:
    return DhtKeypair.from_seed(bytes([n]) * 32)


K1 = key(1)
K2 = key(2)
K3 = key(3)
K4 = key(4)
K5 = key(5)
K6 = key(6)
K7 = key(7)
K8 = key(8)


def portfolio_entry(*, keypair=K1, source=PolicySourceKind.MAINTAINER, disposition=PolicyDisposition.ALLOW, sequence=1, family="policy-a", path="path-a", scope=SCOPE, request=REQUEST, subject=SUBJECT, moderation_digest=ZERO_DIGEST, redress_digest=ZERO_DIGEST):
    return make_policy_source_capsule(
        keypair=keypair,
        source_name=source.value,
        source_kind=source,
        disposition=disposition,
        profile_id=PROFILE,
        service_name=SERVICE,
        action=ModerationAction.PUBLIC_BRIDGE,
        subject_key_digest=subject,
        scope_digest=scope,
        request_digest=request,
        policy_head_digest=d(f"policy-{source.value}-{disposition.value}-{sequence}"),
        
        sequence=sequence,
        previous_source_digest=ZERO_DIGEST,
        issued_at=NOW,
        expires_at=NOW + 100,
        family_id=family,
        path_family=path,
    )


def accepted_policy(*, allow_watch=False):
    entries = (
        portfolio_entry(keypair=K1, source=PolicySourceKind.MAINTAINER, family="policy-a", path="path-a"),
        portfolio_entry(keypair=K2, source=PolicySourceKind.GARDEN_SENTINEL, sequence=2, family="policy-b", path="path-b"),
        portfolio_entry(keypair=K3, source=PolicySourceKind.LOCAL_OPERATOR, sequence=3, family="policy-c", path="path-c"),
    )
    return assess_policy_portfolio(
        entries,
        now=NOW + 1,
        expected_profile_id=PROFILE,
        expected_service_name=SERVICE,
        expected_action=ModerationAction.PUBLIC_BRIDGE,
        expected_subject_key_digest=SUBJECT,
        expected_scope_digest=SCOPE,
        expected_request_digest=REQUEST,
        allow_watch=allow_watch,
    )


def ledger_report(*, accept=True, watch=False, action=BridgeLedgerAction.PUBLIC_REFRESH):
    kind = BridgeLedgerDecisionKind.ACCEPT_WITH_WATCH if watch else BridgeLedgerDecisionKind.ACCEPT_LEDGER
    if not accept:
        kind = BridgeLedgerDecisionKind.HOLD_REDRESS_NEEDED
    return BridgeLedgerReport(kind, accept, watch, "test bridge ledger", PROFILE, SERVICE, action, d(f"ledger-entry-{accept}-{watch}-{action.value}"), (d("shadow"), d("egress"), d("moderation")), 3, 3, 7, d(f"ledger-report-{accept}-{watch}-{action.value}"))


def egress_report(*, raw=False, duplicate=False):
    event_a = EgressEvent(EgressEventKind.SAM_STREAM_SEND, SCOPE, d("publication-object"), d("dest-a"), "dest-a", "path-a", NOW, NOW + 100, 200, 1, raw, "public bridge publication")
    event_b = EgressEvent(EgressEventKind.WITNESS_PUBLISH, SCOPE, d("publication-object"), d("dest-b"), "dest-b", "path-b", NOW, NOW + 100, 100, 1, False, "witness publication")
    events = (event_a, event_a) if duplicate else (event_a, event_b)
    return assess_egress_window(events, budget=EgressBudget(max_total_bytes=1_000, max_total_streams=4, max_raw_key_exposures=1), now=NOW + 1)


def publication_capsule(*, keypair=K4, sequence=1, family="pub-a", path="pub-path-a", exposure=ExposureClass.DIGEST_ONLY, ledger=None, policy=None, egress=None, intent=PublicationIntent.PUBLIC_REFRESH, payload=None, ttl=300, scope=SCOPE, request=REQUEST, subject=SUBJECT):
    ledger = ledger or ledger_report()
    policy = policy or accepted_policy()
    egress = egress or egress_report()
    return make_publication_capsule(
        keypair=keypair,
        intent=intent,
        exposure_class=exposure,
        profile_id=PROFILE,
        service_name=SERVICE,
        subject_key_digest=subject,
        scope_digest=scope,
        request_digest=request,
        bridge_ledger_digest=ledger.report_digest,
        policy_portfolio_digest=policy.report_digest,
        egress_digest=egress.report_digest,
        public_payload_digest=payload or d(f"payload-{sequence}-{exposure.value}"),
        sequence=sequence,
        previous_publication_digest=ZERO_DIGEST,
        issued_at=NOW,
        expires_at=NOW + 100,
        ttl_seconds=ttl,
        family_id=family,
        path_family=path,
    )


def test_policy_portfolio_accepts_diverse_nonblocking_sources() -> None:
    report = accepted_policy()
    assert report.decision_kind is PolicyPortfolioDecisionKind.ACCEPT_ALLOW
    assert report.allow
    assert report.family_count == 3
    assert report.source_kind_count == 3


def test_policy_portfolio_blocks_deny_without_redress_and_catches_fork() -> None:
    deny = (
        portfolio_entry(keypair=K1, source=PolicySourceKind.MAINTAINER, disposition=PolicyDisposition.DENY, family="policy-a", path="path-a"),
        portfolio_entry(keypair=K2, source=PolicySourceKind.GARDEN_SENTINEL, sequence=2, family="policy-b", path="path-b"),
        portfolio_entry(keypair=K3, source=PolicySourceKind.LOCAL_OPERATOR, sequence=3, family="policy-c", path="path-c"),
    )
    blocked = assess_policy_portfolio(deny, now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_action=ModerationAction.PUBLIC_BRIDGE, expected_subject_key_digest=SUBJECT, expected_scope_digest=SCOPE, expected_request_digest=REQUEST)
    assert blocked.decision_kind is PolicyPortfolioDecisionKind.QUARANTINE_DENY
    assert blocked.blocked

    fork = (
        portfolio_entry(keypair=K1, source=PolicySourceKind.MAINTAINER, disposition=PolicyDisposition.ALLOW, sequence=5, family="policy-a", path="path-a"),
        portfolio_entry(keypair=K2, source=PolicySourceKind.MAINTAINER, disposition=PolicyDisposition.WATCH, sequence=5, family="policy-b", path="path-b"),
    )
    assert assess_policy_portfolio(fork, now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_action=ModerationAction.PUBLIC_BRIDGE, expected_subject_key_digest=SUBJECT, expected_scope_digest=SCOPE, expected_request_digest=REQUEST).decision_kind is PolicyPortfolioDecisionKind.QUARANTINE_SEQUENCE_FORK


def test_policy_portfolio_catches_low_source_diversity_replay_and_scope_drift() -> None:
    one_source = (
        portfolio_entry(keypair=K1, source=PolicySourceKind.GARDEN_SENTINEL, family="policy-a", path="path-a"),
        portfolio_entry(keypair=K2, source=PolicySourceKind.GARDEN_SENTINEL, sequence=2, family="policy-b", path="path-b"),
    )
    assert assess_policy_portfolio(one_source, now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_action=ModerationAction.PUBLIC_BRIDGE, expected_subject_key_digest=SUBJECT, expected_scope_digest=SCOPE, expected_request_digest=REQUEST).decision_kind is PolicyPortfolioDecisionKind.HOLD_LOW_SOURCE_DIVERSITY

    entry = portfolio_entry()
    assert assess_policy_portfolio((entry,), now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_action=ModerationAction.PUBLIC_BRIDGE, expected_subject_key_digest=SUBJECT, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, previously_seen_sources=(entry.source_digest,)).decision_kind is PolicyPortfolioDecisionKind.QUARANTINE_REPLAY

    drift = portfolio_entry(scope=d("other-scope"))
    assert assess_policy_portfolio((drift,), now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_action=ModerationAction.PUBLIC_BRIDGE, expected_subject_key_digest=SUBJECT, expected_scope_digest=SCOPE, expected_request_digest=REQUEST).decision_kind is PolicyPortfolioDecisionKind.QUARANTINE_SCOPE_DRIFT


def test_publication_guard_accepts_final_digest_only_publication() -> None:
    ledger = ledger_report()
    policy = accepted_policy()
    egress = egress_report()
    capsules = (
        publication_capsule(keypair=K4, sequence=1, family="pub-a", path="path-a", ledger=ledger, policy=policy, egress=egress),
        publication_capsule(keypair=K5, sequence=2, family="pub-b", path="path-b", ledger=ledger, policy=policy, egress=egress),
    )
    report = assess_publication(capsules, bridge_ledger=ledger, policy_portfolio=policy, egress=egress, now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_action=BridgeLedgerAction.PUBLIC_REFRESH, expected_subject_key_digest=SUBJECT, expected_scope_digest=SCOPE, expected_request_digest=REQUEST)
    assert report.decision_kind is PublicationDecisionKind.ACCEPT_PUBLICATION
    assert report.accept
    assert report.family_count == 2


def test_publication_guard_holds_public_hint_until_explicitly_allowed() -> None:
    ledger = ledger_report()
    policy = accepted_policy()
    egress = egress_report()
    capsules = (
        publication_capsule(keypair=K4, sequence=1, family="pub-a", path="path-a", ledger=ledger, policy=policy, egress=egress, exposure=ExposureClass.PUBLIC_B32_HINT),
        publication_capsule(keypair=K5, sequence=2, family="pub-b", path="path-b", ledger=ledger, policy=policy, egress=egress, exposure=ExposureClass.PUBLIC_B32_HINT),
    )
    held = assess_publication(capsules, bridge_ledger=ledger, policy_portfolio=policy, egress=egress, now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_action=BridgeLedgerAction.PUBLIC_REFRESH, expected_subject_key_digest=SUBJECT, expected_scope_digest=SCOPE, expected_request_digest=REQUEST)
    assert held.decision_kind is PublicationDecisionKind.HOLD_PUBLIC_CONTACT_NOT_ALLOWED
    allowed = assess_publication(capsules, bridge_ledger=ledger, policy_portfolio=policy, egress=egress, now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_action=BridgeLedgerAction.PUBLIC_REFRESH, expected_subject_key_digest=SUBJECT, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, allow_public_contact=True)
    assert allowed.decision_kind is PublicationDecisionKind.ACCEPT_PUBLICATION


def test_publication_guard_blocks_unaccepted_components_and_raw_destination() -> None:
    policy = accepted_policy()
    egress = egress_report()
    bad_ledger = ledger_report(accept=False)
    capsule = publication_capsule(ledger=bad_ledger, policy=policy, egress=egress)
    assert assess_publication((capsule,), bridge_ledger=bad_ledger, policy_portfolio=policy, egress=egress, now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_action=BridgeLedgerAction.PUBLIC_REFRESH, expected_subject_key_digest=SUBJECT, expected_scope_digest=SCOPE, expected_request_digest=REQUEST).decision_kind is PublicationDecisionKind.HOLD_LEDGER_NOT_ACCEPTED

    ledger = ledger_report()
    raw = (
        publication_capsule(keypair=K4, sequence=1, family="pub-a", path="path-a", ledger=ledger, policy=policy, egress=egress, exposure=ExposureClass.RAW_DESTINATION),
        publication_capsule(keypair=K5, sequence=2, family="pub-b", path="path-b", ledger=ledger, policy=policy, egress=egress, exposure=ExposureClass.RAW_DESTINATION),
    )
    assert assess_publication(raw, bridge_ledger=ledger, policy_portfolio=policy, egress=egress, now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_action=BridgeLedgerAction.PUBLIC_REFRESH, expected_subject_key_digest=SUBJECT, expected_scope_digest=SCOPE, expected_request_digest=REQUEST).decision_kind is PublicationDecisionKind.QUARANTINE_RAW_DESTINATION_EXPOSURE


def test_publication_guard_catches_replay_fork_stale_payload_and_digest_drift() -> None:
    ledger = ledger_report()
    policy = accepted_policy()
    egress = egress_report()
    cap = publication_capsule(ledger=ledger, policy=policy, egress=egress)
    assert assess_publication((cap,), bridge_ledger=ledger, policy_portfolio=policy, egress=egress, now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_action=BridgeLedgerAction.PUBLIC_REFRESH, expected_subject_key_digest=SUBJECT, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, previously_seen_capsules=(cap.capsule_digest,)).decision_kind is PublicationDecisionKind.QUARANTINE_REPLAY

    fork = (
        publication_capsule(keypair=K4, sequence=4, family="pub-a", path="path-a", ledger=ledger, policy=policy, egress=egress, payload=d("payload-a")),
        publication_capsule(keypair=K5, sequence=4, family="pub-b", path="path-b", ledger=ledger, policy=policy, egress=egress, payload=d("payload-b")),
    )
    assert assess_publication(fork, bridge_ledger=ledger, policy_portfolio=policy, egress=egress, now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_action=BridgeLedgerAction.PUBLIC_REFRESH, expected_subject_key_digest=SUBJECT, expected_scope_digest=SCOPE, expected_request_digest=REQUEST).decision_kind is PublicationDecisionKind.QUARANTINE_SEQUENCE_FORK

    stale_payload = d("old-public")
    stale = (
        publication_capsule(keypair=K4, sequence=1, family="pub-a", path="path-a", ledger=ledger, policy=policy, egress=egress, payload=stale_payload),
        publication_capsule(keypair=K5, sequence=2, family="pub-b", path="path-b", ledger=ledger, policy=policy, egress=egress, payload=d("new-public")),
    )
    assert assess_publication(stale, bridge_ledger=ledger, policy_portfolio=policy, egress=egress, now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_action=BridgeLedgerAction.PUBLIC_REFRESH, expected_subject_key_digest=SUBJECT, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, stale_public_payload_digests=(stale_payload,)).decision_kind is PublicationDecisionKind.QUARANTINE_STALE_PUBLIC_REPLAY

    drift = replace(cap, policy_portfolio_digest=d("other-policy"))
    assert assess_publication((drift,), bridge_ledger=ledger, policy_portfolio=policy, egress=egress, now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_action=BridgeLedgerAction.PUBLIC_REFRESH, expected_subject_key_digest=SUBJECT, expected_scope_digest=SCOPE, expected_request_digest=REQUEST).decision_kind is PublicationDecisionKind.QUARANTINE_BAD_SIGNATURE


def test_publicationfold_current_revision_path_passes() -> None:
    report = audit_publication_fold(".", revision="rev0047")
    assert report.status == "pass"
    assert report.predecessor_status == "pass"
    assert report.foldmap_status == "pass"
    assert report.registry_status == "pass"
    assert report.surface_ledger_status == "pass"
    assert report.branchlet_status == "pass"
