from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from i2p_dht_lab.appealpublicationfold import audit_appeal_publication_fold
from i2p_dht_lab.bridgeledger import BridgeLedgerAction, BridgeLedgerDecisionKind, BridgeLedgerReport
from i2p_dht_lab.bridgequenchlane import (
    BridgeQuenchDecisionKind,
    QuenchObservationKind,
    assess_bridge_quench_window,
    make_quench_observation,
)
from i2p_dht_lab.identity import DhtKeypair
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.moderationquarantine import ModerationAction, ModerationDecisionKind, ModerationQuarantineReport, ZERO_DIGEST
from i2p_dht_lab.publicationledger import (
    PublicationAction,
    PublicationLedgerDecisionKind,
    PublicationLedgerReport,
    assess_publication_ledger,
    make_publication_ledger_entry,
)
from i2p_dht_lab.redresslane import RedressDecisionKind, RedressReport
from i2p_dht_lab.witnessappealmesh import (
    AppealMeshObservationKind,
    WitnessAppealMeshDecisionKind,
    WitnessAppealMeshReport,
    assess_witness_appeal_mesh,
    make_appeal_mesh_observation,
)

NOW = 1_900_000
PROFILE = "profile-alpha"
SERVICE = "public-bridge"
SCOPE = sha256(b"scope-alpha")
REQUEST = sha256(b"request-alpha")
SUBJECT = sha256(b"subject-key")

K1 = DhtKeypair.from_seed(b"A" * 32)
K2 = DhtKeypair.from_seed(b"B" * 32)
K3 = DhtKeypair.from_seed(b"C" * 32)
K4 = DhtKeypair.from_seed(b"D" * 32)
K5 = DhtKeypair.from_seed(b"E" * 32)
K6 = DhtKeypair.from_seed(b"F" * 32)


def d(label: str) -> bytes:
    return sha256(label.encode("utf-8"))


def bridge_report(*, accept=True, watch=False, kind=BridgeLedgerDecisionKind.ACCEPT_LEDGER, action=BridgeLedgerAction.PUBLIC_REFRESH) -> BridgeLedgerReport:
    digest = d(f"bridge-{accept}-{watch}-{kind.value}-{action.value}")
    return BridgeLedgerReport(kind, accept, watch, "bridge fixture", PROFILE, SERVICE, action, d("accepted-entry"), (d("shadow"), d("egress")), 3, 2, 4, digest)


def moderation_report(*, watch=False, blocked=False, kind=None) -> ModerationQuarantineReport:
    if kind is None:
        if blocked:
            kind = ModerationDecisionKind.ACCEPT_DENY
        elif watch:
            kind = ModerationDecisionKind.ACCEPT_WATCH
        else:
            kind = ModerationDecisionKind.CLEAR_NO_ACTIVE_CAPSULE
    digest = d(f"moderation-{watch}-{blocked}-{kind.value}")
    return ModerationQuarantineReport(kind, blocked or watch, blocked, watch, "moderation fixture", PROFILE, SERVICE, ModerationAction.PUBLIC_BRIDGE, SUBJECT, (d("cap-a"),), 2, 2, 3, True, d("accepted-capsule") if (blocked or watch) else ZERO_DIGEST, digest)


def redress_report(*, accept=True, lifted=True, watch=False, kind=RedressDecisionKind.ACCEPT_LIFT, moderation=None) -> RedressReport:
    moderation = moderation or moderation_report(blocked=True)
    digest = d(f"redress-{accept}-{lifted}-{watch}-{kind.value}")
    return RedressReport(kind, accept, lifted, watch, "redress fixture", PROFILE, SERVICE, ModerationAction.PUBLIC_BRIDGE, SUBJECT, moderation.report_digest, (d("receipt-a"), d("receipt-b")), 4, 3, 2, digest)


def appeal_observations(bridge=None, moderation=None, redress=None):
    bridge = bridge or bridge_report(watch=True, kind=BridgeLedgerDecisionKind.ACCEPT_WITH_WATCH)
    moderation = moderation or moderation_report(watch=True)
    redress_digest = redress.report_digest if redress else ZERO_DIGEST
    return (
        make_appeal_mesh_observation(keypair=K1, kind=AppealMeshObservationKind.POLICY_WATCH, action=BridgeLedgerAction.PUBLIC_REFRESH, profile_id=PROFILE, service_name=SERVICE, scope_digest=SCOPE, request_digest=REQUEST, bridge_ledger_digest=bridge.report_digest, moderation_digest=moderation.report_digest, redress_digest=redress_digest, evidence_digest=d("appeal-policy"), sequence=1, issued_at=NOW, expires_at=NOW + 100, family_id="fam-a", path_family="path-a", watch=True),
        make_appeal_mesh_observation(keypair=K2, kind=AppealMeshObservationKind.HARD_NEGATIVE_SCAN, action=BridgeLedgerAction.PUBLIC_REFRESH, profile_id=PROFILE, service_name=SERVICE, scope_digest=SCOPE, request_digest=REQUEST, bridge_ledger_digest=bridge.report_digest, moderation_digest=moderation.report_digest, redress_digest=redress_digest, evidence_digest=d("appeal-hard-negative"), sequence=2, issued_at=NOW, expires_at=NOW + 100, family_id="fam-b", path_family="path-b"),
        make_appeal_mesh_observation(keypair=K3, kind=AppealMeshObservationKind.STALE_PUBLIC_SCAN, action=BridgeLedgerAction.PUBLIC_REFRESH, profile_id=PROFILE, service_name=SERVICE, scope_digest=SCOPE, request_digest=REQUEST, bridge_ledger_digest=bridge.report_digest, moderation_digest=moderation.report_digest, redress_digest=redress_digest, evidence_digest=d("appeal-stale"), sequence=3, issued_at=NOW, expires_at=NOW + 100, family_id="fam-c", path_family="path-c"),
    )


def appeal_report(*, bridge=None, moderation=None, redress=None):
    bridge = bridge or bridge_report(watch=True, kind=BridgeLedgerDecisionKind.ACCEPT_WITH_WATCH)
    moderation = moderation or moderation_report(watch=True)
    observations = appeal_observations(bridge=bridge, moderation=moderation, redress=redress)
    return assess_witness_appeal_mesh(observations, bridge_ledger=bridge, moderation=moderation, redress=redress, now=NOW + 1, action=BridgeLedgerAction.PUBLIC_REFRESH, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST)


def publication_entries(bridge=None, appeal=None, *, action=PublicationAction.PUBLISH_PUBLIC):
    bridge = bridge or bridge_report()
    appeal_digest = appeal.report_digest if appeal else ZERO_DIGEST
    return (
        make_publication_ledger_entry(keypair=K4, action=action, profile_id=PROFILE, service_name=SERVICE, scope_digest=SCOPE, request_digest=REQUEST, bridge_ledger_digest=bridge.report_digest, appeal_mesh_digest=appeal_digest, public_record_digest=d("public-record-a"), side_effect_digest=d("publish-a"), sequence=1, issued_at=NOW, expires_at=NOW + 100, family_id="pub-a", path_family="pub-path-a"),
        make_publication_ledger_entry(keypair=K5, action=action, profile_id=PROFILE, service_name=SERVICE, scope_digest=SCOPE, request_digest=REQUEST, bridge_ledger_digest=bridge.report_digest, appeal_mesh_digest=appeal_digest, public_record_digest=d("public-record-b"), side_effect_digest=d("publish-b"), sequence=2, issued_at=NOW, expires_at=NOW + 100, family_id="pub-b", path_family="pub-path-b"),
    )


def publication_report(*, bridge=None, appeal=None, allow_watch=False) -> PublicationLedgerReport:
    bridge = bridge or bridge_report()
    entries = publication_entries(bridge=bridge, appeal=appeal)
    return assess_publication_ledger(entries, bridge_ledger=bridge, appeal_mesh=appeal, now=NOW + 1, action=PublicationAction.PUBLISH_PUBLIC, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, allow_watch=allow_watch)


def test_witness_appeal_mesh_accepts_not_needed_and_watched_mesh() -> None:
    clear_bridge = bridge_report()
    clear_mod = moderation_report()
    not_needed = assess_witness_appeal_mesh((), bridge_ledger=clear_bridge, moderation=clear_mod, redress=None, now=NOW + 1, action=BridgeLedgerAction.PUBLIC_REFRESH, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST)
    assert not_needed.decision_kind is WitnessAppealMeshDecisionKind.ACCEPT_NOT_NEEDED
    assert not_needed.accept and not not_needed.watch

    watched = appeal_report()
    assert watched.decision_kind is WitnessAppealMeshDecisionKind.ACCEPT_WITH_WATCH
    assert watched.accept and watched.watch
    assert watched.family_count == 3


def test_witness_appeal_mesh_catches_bad_signature_missing_and_low_diversity() -> None:
    bridge = bridge_report(watch=True, kind=BridgeLedgerDecisionKind.ACCEPT_WITH_WATCH)
    moderation = moderation_report(watch=True)
    obs = appeal_observations(bridge=bridge, moderation=moderation)
    bad = replace(obs[0], signature=b"0" * 64)
    assert assess_witness_appeal_mesh((bad,) + obs[1:], bridge_ledger=bridge, moderation=moderation, redress=None, now=NOW + 1, action=BridgeLedgerAction.PUBLIC_REFRESH, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST).decision_kind is WitnessAppealMeshDecisionKind.QUARANTINE_BAD_SIGNATURE

    missing = assess_witness_appeal_mesh(obs[:2], bridge_ledger=bridge, moderation=moderation, redress=None, now=NOW + 1, action=BridgeLedgerAction.PUBLIC_REFRESH, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST)
    assert missing.decision_kind is WitnessAppealMeshDecisionKind.HOLD_MISSING_OBSERVATION

    one_family = (
        make_appeal_mesh_observation(keypair=K1, kind=AppealMeshObservationKind.POLICY_WATCH, action=BridgeLedgerAction.PUBLIC_REFRESH, profile_id=PROFILE, service_name=SERVICE, scope_digest=SCOPE, request_digest=REQUEST, bridge_ledger_digest=bridge.report_digest, moderation_digest=moderation.report_digest, evidence_digest=d("appeal-policy-one"), sequence=1, issued_at=NOW, expires_at=NOW + 100, family_id="same-family", path_family="path-a", watch=True),
        make_appeal_mesh_observation(keypair=K2, kind=AppealMeshObservationKind.HARD_NEGATIVE_SCAN, action=BridgeLedgerAction.PUBLIC_REFRESH, profile_id=PROFILE, service_name=SERVICE, scope_digest=SCOPE, request_digest=REQUEST, bridge_ledger_digest=bridge.report_digest, moderation_digest=moderation.report_digest, evidence_digest=d("appeal-hard-one"), sequence=2, issued_at=NOW, expires_at=NOW + 100, family_id="same-family", path_family="path-b"),
        make_appeal_mesh_observation(keypair=K3, kind=AppealMeshObservationKind.STALE_PUBLIC_SCAN, action=BridgeLedgerAction.PUBLIC_REFRESH, profile_id=PROFILE, service_name=SERVICE, scope_digest=SCOPE, request_digest=REQUEST, bridge_ledger_digest=bridge.report_digest, moderation_digest=moderation.report_digest, evidence_digest=d("appeal-stale-one"), sequence=3, issued_at=NOW, expires_at=NOW + 100, family_id="same-family", path_family="path-c"),
    )
    assert assess_witness_appeal_mesh(one_family, bridge_ledger=bridge, moderation=moderation, redress=None, now=NOW + 1, action=BridgeLedgerAction.PUBLIC_REFRESH, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST).decision_kind is WitnessAppealMeshDecisionKind.HOLD_LOW_FAMILY_DIVERSITY


def test_publication_ledger_accepts_clear_and_requires_appeal_for_watch() -> None:
    clear = publication_report()
    assert clear.decision_kind is PublicationLedgerDecisionKind.ACCEPT_PUBLICATION
    assert clear.accept

    watched_bridge = bridge_report(watch=True, kind=BridgeLedgerDecisionKind.ACCEPT_WITH_WATCH)
    held = assess_publication_ledger(publication_entries(bridge=watched_bridge), bridge_ledger=watched_bridge, appeal_mesh=None, now=NOW + 1, action=PublicationAction.PUBLISH_PUBLIC, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST)
    assert held.decision_kind is PublicationLedgerDecisionKind.HOLD_APPEAL_MESH_REQUIRED

    appeal = appeal_report(bridge=watched_bridge, moderation=moderation_report(watch=True))
    held_watch = publication_report(bridge=watched_bridge, appeal=appeal, allow_watch=False)
    assert held_watch.decision_kind is PublicationLedgerDecisionKind.HOLD_APPEAL_MESH_WATCH
    accepted_watch = publication_report(bridge=watched_bridge, appeal=appeal, allow_watch=True)
    assert accepted_watch.decision_kind is PublicationLedgerDecisionKind.ACCEPT_WITH_WATCH
    assert accepted_watch.watch


def test_publication_ledger_catches_replay_fork_and_component_drift() -> None:
    bridge = bridge_report()
    entries = publication_entries(bridge=bridge)
    replay = assess_publication_ledger(entries, bridge_ledger=bridge, appeal_mesh=None, now=NOW + 1, action=PublicationAction.PUBLISH_PUBLIC, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, previously_seen_entries=(entries[0].entry_digest,))
    assert replay.decision_kind is PublicationLedgerDecisionKind.QUARANTINE_REPLAY

    fork = (
        entries[0],
        make_publication_ledger_entry(keypair=K6, action=PublicationAction.PUBLISH_PUBLIC, profile_id=PROFILE, service_name=SERVICE, scope_digest=SCOPE, request_digest=REQUEST, bridge_ledger_digest=bridge.report_digest, public_record_digest=d("different-public-record"), side_effect_digest=d("different-effect"), sequence=1, issued_at=NOW, expires_at=NOW + 100, family_id="pub-c", path_family="pub-path-c"),
    )
    assert assess_publication_ledger(fork, bridge_ledger=bridge, appeal_mesh=None, now=NOW + 1, action=PublicationAction.PUBLISH_PUBLIC, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST).decision_kind is PublicationLedgerDecisionKind.QUARANTINE_SEQUENCE_FORK

    drifted = (replace(entries[0], bridge_ledger_digest=d("other-bridge")), entries[1])
    assert assess_publication_ledger(drifted, bridge_ledger=bridge, appeal_mesh=None, now=NOW + 1, action=PublicationAction.PUBLISH_PUBLIC, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST).decision_kind is PublicationLedgerDecisionKind.QUARANTINE_BAD_SIGNATURE


def quench_observations(publication=None, kinds=(QuenchObservationKind.PUBLICATION_ACCEPTED, QuenchObservationKind.WITHDRAWAL_CONFIRMED)):
    publication = publication or publication_report()
    keys = (K1, K2, K3, K4)
    return tuple(
        make_quench_observation(keypair=keys[index], kind=kind, profile_id=PROFILE, service_name=SERVICE, scope_digest=SCOPE, request_digest=REQUEST, publication_digest=publication.report_digest, evidence_digest=d(f"quench-{kind.value}-{index}"), window_id=f"window-{index}", issued_at=NOW, expires_at=NOW + 100, family_id=f"quench-fam-{index}", path_family=f"quench-path-{index}", watch=kind in (QuenchObservationKind.APPEAL_WATCH_LOOP, QuenchObservationKind.REFUSAL_ONLY))
        for index, kind in enumerate(kinds)
    )


def test_bridge_quench_continue_and_quench_on_hard_negative_or_stale_replay() -> None:
    publication = publication_report()
    healthy = assess_bridge_quench_window(quench_observations(publication), publication=publication, now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST)
    assert healthy.decision_kind is BridgeQuenchDecisionKind.ACCEPT_CONTINUE
    assert healthy.continue_publication and not healthy.quench

    hard = assess_bridge_quench_window(quench_observations(publication, kinds=(QuenchObservationKind.HARD_NEGATIVE, QuenchObservationKind.FALSE_SERVICE_PROOF)), publication=publication, now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST)
    assert hard.decision_kind is BridgeQuenchDecisionKind.ACCEPT_QUENCH
    assert hard.quench

    stale = assess_bridge_quench_window(quench_observations(publication, kinds=(QuenchObservationKind.STALE_PUBLIC_REPLAY, QuenchObservationKind.STALE_PUBLIC_REPLAY)), publication=publication, now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST)
    assert stale.decision_kind is BridgeQuenchDecisionKind.ACCEPT_QUENCH
    assert stale.stale_replay_count == 2


def test_bridge_quench_catches_watch_loop_family_capture_and_replay() -> None:
    publication = publication_report()
    watch_loop = assess_bridge_quench_window(quench_observations(publication, kinds=(QuenchObservationKind.APPEAL_WATCH_LOOP, QuenchObservationKind.REFUSAL_ONLY)), publication=publication, now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST)
    assert watch_loop.decision_kind is BridgeQuenchDecisionKind.HOLD_COOLDOWN

    obs = quench_observations(publication, kinds=(QuenchObservationKind.PUBLICATION_ACCEPTED, QuenchObservationKind.WITHDRAWAL_CONFIRMED))
    replay = assess_bridge_quench_window(obs, publication=publication, now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST, previously_seen_observations=(obs[0].observation_digest,))
    assert replay.decision_kind is BridgeQuenchDecisionKind.QUARANTINE_REPLAY

    captured = (
        make_quench_observation(keypair=K1, kind=QuenchObservationKind.PUBLICATION_ACCEPTED, profile_id=PROFILE, service_name=SERVICE, scope_digest=SCOPE, request_digest=REQUEST, publication_digest=publication.report_digest, evidence_digest=d("captured-a"), window_id="window-a", issued_at=NOW, expires_at=NOW + 100, family_id="same-family", path_family="path-a"),
        make_quench_observation(keypair=K2, kind=QuenchObservationKind.WITHDRAWAL_CONFIRMED, profile_id=PROFILE, service_name=SERVICE, scope_digest=SCOPE, request_digest=REQUEST, publication_digest=publication.report_digest, evidence_digest=d("captured-b"), window_id="window-b", issued_at=NOW, expires_at=NOW + 100, family_id="same-family", path_family="path-b"),
    )
    captured_report = assess_bridge_quench_window(captured, publication=publication, now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE, expected_request_digest=REQUEST)
    assert captured_report.decision_kind is BridgeQuenchDecisionKind.QUARANTINE_FAMILY_CAPTURE


def test_rev0047_fold_audit() -> None:
    root = Path(__file__).resolve().parents[1]
    report = audit_appeal_publication_fold(root, revision="rev0047", artifact_stem=root.name)
    assert report.status == "pass"
    assert report.error_count == 0
    assert report.branchlet_count >= 6
