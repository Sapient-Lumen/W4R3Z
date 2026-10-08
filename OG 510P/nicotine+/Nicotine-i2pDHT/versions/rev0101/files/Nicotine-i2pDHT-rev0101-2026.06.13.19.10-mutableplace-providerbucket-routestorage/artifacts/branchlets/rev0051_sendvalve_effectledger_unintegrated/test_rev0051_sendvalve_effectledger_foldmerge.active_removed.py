from __future__ import annotations

from types import SimpleNamespace

from i2p_dht_lab.effectledger import (
    EffectLedgerDecisionKind,
    EffectLedgerPhase,
    assess_effect_ledger,
    make_effect_ledger_entry,
)
from i2p_dht_lab.identity import DhtKeypair
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.moderationquarantine import ZERO_DIGEST
from i2p_dht_lab.sendvalve import (
    SendValveAction,
    SendValveDecisionKind,
    assess_send_valve,
    make_send_valve_authorization,
)

NOW = 70_000
PROFILE = "profile-send-valve"
SERVICE = "public-bridge-send-valve"
SESSION = "sam-session-alpha"
DESTINATION = "exampledestination.b32.i2p"
SCOPE = sha256(b"rev0051-send-scope")
REQUEST = sha256(b"rev0051-send-request")
PAYLOAD = sha256(b"rev0051-public-payload")
FRAME = sha256(b"rev0051-public-frame")
IDEM = sha256(b"rev0051-idempotency")
EFFECT = sha256(b"rev0051-public-effect")


def kp(n: int) -> DhtKeypair:
    return DhtKeypair.from_seed(bytes([n]) * 32)


def d(label: str) -> bytes:
    return sha256(label.encode("utf-8"))


def component(label: str, *, accept: bool = True, watch: bool = False, quarantined: bool = False, idem: bytes = IDEM, effect: bytes = EFFECT):
    return SimpleNamespace(
        report_digest=d(f"{label}:{accept}:{watch}:{quarantined}:{idem.hex()}:{effect.hex()}"),
        accept=accept,
        watch=watch,
        quarantined=quarantined,
        idempotency_key=idem,
        drain_effect_digest=effect,
        canary_effect_digest=effect,
    )


def components(*, watch: bool = False):
    commit = component("commit", watch=watch)
    drain = component("drain")
    canary = component("canary")
    compact = component("compact")
    return commit, drain, canary, compact


def auth(keypair, sequence: int, family: str, path: str, commit, drain, canary, compact, *, idem: bytes = IDEM, effect: bytes = EFFECT, frame: bytes = FRAME, previous: bytes = ZERO_DIGEST):
    return make_send_valve_authorization(
        keypair=keypair,
        action=SendValveAction.SEND_REFRESH,
        profile_id=PROFILE,
        service_name=SERVICE,
        session_id=SESSION,
        destination=DESTINATION,
        scope_digest=SCOPE,
        request_digest=REQUEST,
        payload_digest=PAYLOAD,
        commit_barrier_digest=commit.report_digest,
        outbox_drain_digest=drain.report_digest,
        sam_canary_digest=canary.report_digest,
        compact_join_digest=compact.report_digest,
        frame_digest=frame,
        idempotency_key=idem,
        public_effect_digest=effect,
        sequence=sequence,
        previous_authorization_digest=previous,
        issued_at=NOW,
        expires_at=NOW + 300,
        family_id=family,
        path_family=path,
    )


def accepted_send_valve(*, watch: bool = False, allow_watch: bool = False):
    commit, drain, canary, compact = components(watch=watch)
    a = auth(kp(1), 1, "family-a", "path-a", commit, drain, canary, compact)
    b = auth(kp(2), 2, "family-b", "path-b", commit, drain, canary, compact)
    report = assess_send_valve(
        (a, b),
        commit_barrier=commit,
        outbox_drain=drain,
        sam_canary=canary,
        compact_join=compact,
        now=NOW + 1,
        expected_action=SendValveAction.SEND_REFRESH,
        expected_profile_id=PROFILE,
        expected_service_name=SERVICE,
        expected_session_id=SESSION,
        expected_destination=DESTINATION,
        expected_scope_digest=SCOPE,
        expected_request_digest=REQUEST,
        expected_payload_digest=PAYLOAD,
        expected_frame_digest=FRAME,
        allow_watch_debt=allow_watch,
    )
    return report, (a, b), (commit, drain, canary, compact)


def test_send_valve_accepts_joined_public_edge_authorization() -> None:
    report, _, _ = accepted_send_valve()
    assert report.decision_kind is SendValveDecisionKind.ACCEPT_SEND_VALVE
    assert report.accept
    assert report.idempotency_key == IDEM
    assert report.public_effect_digest == EFFECT
    assert report.family_count == 2
    assert report.path_family_count == 2


def test_send_valve_carries_watch_debt_explicitly() -> None:
    held, _, _ = accepted_send_valve(watch=True, allow_watch=False)
    assert held.decision_kind is SendValveDecisionKind.HOLD_WATCH_DEBT
    allowed, _, _ = accepted_send_valve(watch=True, allow_watch=True)
    assert allowed.decision_kind is SendValveDecisionKind.ACCEPT_WITH_WATCH
    assert allowed.watch


def test_send_valve_quarantines_component_drift_and_effect_conflict() -> None:
    commit, drain, canary, compact = components()
    wrong_compact = component("compact-wrong")
    a = auth(kp(1), 1, "family-a", "path-a", commit, drain, canary, wrong_compact)
    report = assess_send_valve(
        (a,), commit_barrier=commit, outbox_drain=drain, sam_canary=canary, compact_join=compact,
        now=NOW + 1, expected_action=SendValveAction.SEND_REFRESH, expected_profile_id=PROFILE,
        expected_service_name=SERVICE, expected_session_id=SESSION, expected_destination=DESTINATION,
        expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_payload_digest=PAYLOAD,
        expected_frame_digest=FRAME, min_family_diversity=1, min_path_diversity=1,
    )
    assert report.decision_kind is SendValveDecisionKind.QUARANTINE_COMPONENT_DIGEST_DRIFT

    b = auth(kp(2), 1, "family-b", "path-b", commit, drain, canary, compact, effect=d("other-effect"))
    conflict = assess_send_valve(
        (b,), commit_barrier=commit, outbox_drain=drain, sam_canary=canary, compact_join=compact,
        now=NOW + 1, expected_action=SendValveAction.SEND_REFRESH, expected_profile_id=PROFILE,
        expected_service_name=SERVICE, expected_session_id=SESSION, expected_destination=DESTINATION,
        expected_scope_digest=SCOPE, expected_request_digest=REQUEST, expected_payload_digest=PAYLOAD,
        expected_frame_digest=FRAME, min_family_diversity=1, min_path_diversity=1,
    )
    assert conflict.decision_kind is SendValveDecisionKind.QUARANTINE_EFFECT_DRIFT


def test_effect_ledger_accepts_linked_commit_after_send_valve() -> None:
    send, _, (_, drain, canary, _) = accepted_send_valve()
    e1 = make_effect_ledger_entry(
        keypair=kp(3), phase=EffectLedgerPhase.PREPARE, profile_id=PROFILE, service_name=SERVICE,
        scope_digest=SCOPE, request_digest=REQUEST, public_payload_digest=PAYLOAD, idempotency_key=IDEM,
        public_effect_digest=EFFECT, send_seal=send, sam_canary=canary, outbox_drain=drain,
        sequence=1, issued_at=NOW, expires_at=NOW + 300, family_id="ledger-a", path_family="ledger-path-a",
    )
    e2 = make_effect_ledger_entry(
        keypair=kp(4), phase=EffectLedgerPhase.COMMIT, profile_id=PROFILE, service_name=SERVICE,
        scope_digest=SCOPE, request_digest=REQUEST, public_payload_digest=PAYLOAD, idempotency_key=IDEM,
        public_effect_digest=EFFECT, send_seal=send, sam_canary=canary, outbox_drain=drain,
        sequence=2, previous_entry_digest=e1.entry_digest, issued_at=NOW + 1, expires_at=NOW + 301,
        family_id="ledger-b", path_family="ledger-path-b",
    )
    report = assess_effect_ledger(
        (e1, e2), send_seal=send, sam_canary=canary, outbox_drain=drain, now=NOW + 2,
        expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE,
        expected_request_digest=REQUEST, expected_public_payload_digest=PAYLOAD,
        expected_idempotency_key=IDEM, expected_public_effect_digest=EFFECT,
    )
    assert report.decision_kind is EffectLedgerDecisionKind.ACCEPT_COMMITTED
    assert report.accept
    assert report.selected_phase is EffectLedgerPhase.COMMIT


def test_effect_ledger_rejects_phase_regression_and_component_drift() -> None:
    send, _, (_, drain, canary, _) = accepted_send_valve()
    commit = make_effect_ledger_entry(
        keypair=kp(5), phase=EffectLedgerPhase.COMMIT, profile_id=PROFILE, service_name=SERVICE,
        scope_digest=SCOPE, request_digest=REQUEST, public_payload_digest=PAYLOAD, idempotency_key=IDEM,
        public_effect_digest=EFFECT, send_seal=send, sam_canary=canary, outbox_drain=drain,
        sequence=1, issued_at=NOW, expires_at=NOW + 300, family_id="ledger-a", path_family="ledger-path-a",
    )
    prepare = make_effect_ledger_entry(
        keypair=kp(6), phase=EffectLedgerPhase.PREPARE, profile_id=PROFILE, service_name=SERVICE,
        scope_digest=SCOPE, request_digest=REQUEST, public_payload_digest=PAYLOAD, idempotency_key=IDEM,
        public_effect_digest=EFFECT, send_seal=send, sam_canary=canary, outbox_drain=drain,
        sequence=2, previous_entry_digest=commit.entry_digest, issued_at=NOW + 1, expires_at=NOW + 301,
        family_id="ledger-b", path_family="ledger-path-b",
    )
    report = assess_effect_ledger(
        (commit, prepare), send_seal=send, sam_canary=canary, outbox_drain=drain, now=NOW + 2,
        expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE,
        expected_request_digest=REQUEST, expected_public_payload_digest=PAYLOAD,
        expected_idempotency_key=IDEM, expected_public_effect_digest=EFFECT,
    )
    assert report.decision_kind is EffectLedgerDecisionKind.QUARANTINE_PHASE_REGRESSION

    wrong_canary = component("canary-wrong")
    drift = assess_effect_ledger(
        (commit,), send_seal=send, sam_canary=wrong_canary, outbox_drain=drain, now=NOW + 2,
        expected_profile_id=PROFILE, expected_service_name=SERVICE, expected_scope_digest=SCOPE,
        expected_request_digest=REQUEST, expected_public_payload_digest=PAYLOAD,
        expected_idempotency_key=IDEM, expected_public_effect_digest=EFFECT,
        min_family_diversity=1, min_path_diversity=1,
    )
    assert drift.decision_kind is EffectLedgerDecisionKind.QUARANTINE_COMPONENT_DIGEST_DRIFT
