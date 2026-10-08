from __future__ import annotations

from types import SimpleNamespace

from i2p_dht_lab.commitbarrier import PublicCommitAction
from i2p_dht_lab.effectledger import (
    EffectLedgerDecisionKind,
    EffectLedgerPhase,
    assess_effect_ledger,
    make_effect_ledger_entry,
)
from i2p_dht_lab.identity import DhtKeypair
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.moderationquarantine import ZERO_DIGEST
from i2p_dht_lab.sendseal import (
    SendSealDecisionKind,
    assess_send_seal,
    make_public_send_seal,
)

NOW = 70_000
PROFILE = "profile-send-seal"
SERVICE = "public-bridge-send-seal"
SESSION = "sam-session-alpha"
DESTINATION = "exampledestination.b32.i2p"
SCOPE = sha256(b"rev0051-send-scope")
REQUEST = sha256(b"rev0051-send-request")
PAYLOAD = sha256(b"rev0051-public-payload")
IDEM = sha256(b"rev0051-idempotency")
EFFECT = sha256(b"rev0051-public-effect")


def kp(n: int) -> DhtKeypair:
    return DhtKeypair.from_seed(bytes([n]) * 32)


def d(label: str) -> bytes:
    return sha256(label.encode("utf-8"))


def component(label: str, *, accept: bool = True, watch: bool = False, quarantined: bool = False):
    return SimpleNamespace(
        report_digest=d(f"{label}:{accept}:{watch}:{quarantined}"),
        accept=accept,
        watch=watch,
        quarantined=quarantined,
        idempotency_key=IDEM,
        drain_effect_digest=EFFECT,
        canary_effect_digest=EFFECT,
    )


def components(*, watch: bool = False):
    commit = component("commit", watch=watch)
    drain = component("drain")
    canary = component("canary")
    compact = component("compact")
    return commit, drain, canary, compact


def seal(keypair, sequence: int, family: str, path: str, commit, drain, canary, compact, *, effect: bytes = EFFECT, previous: bytes = ZERO_DIGEST):
    return make_public_send_seal(
        keypair=keypair,
        action=PublicCommitAction.COMMIT_REFRESH,
        profile_id=PROFILE,
        service_name=SERVICE,
        session_id=SESSION,
        destination=DESTINATION,
        scope_digest=SCOPE,
        request_digest=REQUEST,
        public_payload_digest=PAYLOAD,
        commit_report=commit,
        outbox_drain=drain,
        sam_canary=canary,
        compact_join=compact,
        idempotency_key=IDEM,
        public_effect_digest=effect,
        sequence=sequence,
        previous_send_seal_digest=previous,
        issued_at=NOW,
        expires_at=NOW + 300,
        family_id=family,
        path_family=path,
    )


def accepted_send_seal(*, watch: bool = False, allow_watch: bool = False):
    commit, drain, canary, compact = components(watch=watch)
    first = seal(kp(1), 1, "family-a", "path-a", commit, drain, canary, compact)
    second = seal(kp(2), 2, "family-b", "path-b", commit, drain, canary, compact)
    report = assess_send_seal(
        (first, second),
        commit_report=commit,
        outbox_drain=drain,
        sam_canary=canary,
        compact_join=compact,
        now=NOW + 1,
        expected_profile_id=PROFILE,
        expected_service_name=SERVICE,
        expected_action=PublicCommitAction.COMMIT_REFRESH,
        expected_destination=DESTINATION,
        expected_scope_digest=SCOPE,
        expected_request_digest=REQUEST,
        expected_public_payload_digest=PAYLOAD,
        expected_idempotency_key=IDEM,
        expected_public_effect_digest=EFFECT,
        allow_watch_debt=allow_watch,
    )
    return report, (first, second), (commit, drain, canary, compact)


def test_send_seal_accepts_joined_public_edge_authorization() -> None:
    report, _, _ = accepted_send_seal()
    assert report.decision_kind is SendSealDecisionKind.ACCEPT_SEND_SEAL
    assert report.accept
    assert report.idempotency_key == IDEM
    assert report.public_effect_digest == EFFECT
    assert report.family_count == 2
    assert report.path_family_count == 2


def test_send_seal_carries_watch_debt_explicitly() -> None:
    held, _, _ = accepted_send_seal(watch=True, allow_watch=False)
    assert held.decision_kind is SendSealDecisionKind.HOLD_WATCH_DEBT
    allowed, _, _ = accepted_send_seal(watch=True, allow_watch=True)
    assert allowed.decision_kind is SendSealDecisionKind.ACCEPT_WITH_WATCH
    assert allowed.watch


def test_send_seal_quarantines_component_drift_and_effect_conflict() -> None:
    commit, drain, canary, compact = components()
    wrong_compact = component("compact-wrong")
    candidate = seal(kp(1), 1, "family-a", "path-a", commit, drain, canary, wrong_compact)
    report = assess_send_seal(
        (candidate,), commit_report=commit, outbox_drain=drain, sam_canary=canary, compact_join=compact,
        now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE,
        expected_action=PublicCommitAction.COMMIT_REFRESH, expected_destination=DESTINATION,
        expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_public_payload_digest=PAYLOAD,
        min_family_diversity=1, min_path_diversity=1,
    )
    assert report.decision_kind is SendSealDecisionKind.QUARANTINE_COMPONENT_DIGEST_DRIFT

    conflict_candidate = seal(kp(2), 1, "family-b", "path-b", commit, drain, canary, compact, effect=d("other-effect"))
    conflict = assess_send_seal(
        (conflict_candidate,), commit_report=commit, outbox_drain=drain, sam_canary=canary, compact_join=compact,
        now=NOW + 1, expected_profile_id=PROFILE, expected_service_name=SERVICE,
        expected_action=PublicCommitAction.COMMIT_REFRESH, expected_destination=DESTINATION,
        expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_public_payload_digest=PAYLOAD,
        expected_public_effect_digest=EFFECT, min_family_diversity=1, min_path_diversity=1,
    )
    assert conflict.decision_kind is SendSealDecisionKind.QUARANTINE_EFFECT_CONFLICT


def test_effect_ledger_accepts_linked_commit_after_send_seal() -> None:
    send, _, (_, drain, canary, _) = accepted_send_seal()
    first = make_effect_ledger_entry(
        keypair=kp(3), phase=EffectLedgerPhase.PREPARE, profile_id=PROFILE, service_name=SERVICE,
        scope_digest=SCOPE, request_digest=REQUEST, public_payload_digest=PAYLOAD, idempotency_key=IDEM,
        public_effect_digest=EFFECT, send_seal=send, sam_canary=canary, outbox_drain=drain,
        sequence=1, issued_at=NOW, expires_at=NOW + 300, family_id="ledger-a", path_family="ledger-path-a",
    )
    second = make_effect_ledger_entry(
        keypair=kp(4), phase=EffectLedgerPhase.COMMIT, profile_id=PROFILE, service_name=SERVICE,
        scope_digest=SCOPE, request_digest=REQUEST, public_payload_digest=PAYLOAD, idempotency_key=IDEM,
        public_effect_digest=EFFECT, send_seal=send, sam_canary=canary, outbox_drain=drain,
        sequence=2, previous_entry_digest=first.entry_digest, issued_at=NOW + 1, expires_at=NOW + 301,
        family_id="ledger-b", path_family="ledger-path-b",
    )
    report = assess_effect_ledger(
        (first, second), send_seal=send, sam_canary=canary, outbox_drain=drain, now=NOW + 2,
        expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE,
        expected_request_digest=REQUEST, expected_public_payload_digest=PAYLOAD,
        expected_idempotency_key=IDEM, expected_public_effect_digest=EFFECT,
    )
    assert report.decision_kind is EffectLedgerDecisionKind.ACCEPT_COMMITTED
    assert report.accept
    assert report.selected_phase is EffectLedgerPhase.COMMIT


def test_effect_ledger_rejects_phase_regression_and_component_drift() -> None:
    send, _, (_, drain, canary, _) = accepted_send_seal()
    committed = make_effect_ledger_entry(
        keypair=kp(5), phase=EffectLedgerPhase.COMMIT, profile_id=PROFILE, service_name=SERVICE,
        scope_digest=SCOPE, request_digest=REQUEST, public_payload_digest=PAYLOAD, idempotency_key=IDEM,
        public_effect_digest=EFFECT, send_seal=send, sam_canary=canary, outbox_drain=drain,
        sequence=1, issued_at=NOW, expires_at=NOW + 300, family_id="ledger-a", path_family="ledger-path-a",
    )
    prepare = make_effect_ledger_entry(
        keypair=kp(6), phase=EffectLedgerPhase.PREPARE, profile_id=PROFILE, service_name=SERVICE,
        scope_digest=SCOPE, request_digest=REQUEST, public_payload_digest=PAYLOAD, idempotency_key=IDEM,
        public_effect_digest=EFFECT, send_seal=send, sam_canary=canary, outbox_drain=drain,
        sequence=2, previous_entry_digest=committed.entry_digest, issued_at=NOW + 1, expires_at=NOW + 301,
        family_id="ledger-b", path_family="ledger-path-b",
    )
    report = assess_effect_ledger(
        (committed, prepare), send_seal=send, sam_canary=canary, outbox_drain=drain, now=NOW + 2,
        expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE,
        expected_request_digest=REQUEST, expected_public_payload_digest=PAYLOAD,
        expected_idempotency_key=IDEM, expected_public_effect_digest=EFFECT,
    )
    assert report.decision_kind is EffectLedgerDecisionKind.QUARANTINE_PHASE_REGRESSION

    wrong_canary = component("canary-wrong")
    drift = assess_effect_ledger(
        (committed,), send_seal=send, sam_canary=wrong_canary, outbox_drain=drain, now=NOW + 2,
        expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE,
        expected_request_digest=REQUEST, expected_public_payload_digest=PAYLOAD,
        expected_idempotency_key=IDEM, expected_public_effect_digest=EFFECT,
        min_family_diversity=1, min_path_diversity=1,
    )
    assert drift.decision_kind is EffectLedgerDecisionKind.QUARANTINE_COMPONENT_DIGEST_DRIFT
