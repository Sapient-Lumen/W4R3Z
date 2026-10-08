"""No-network bridge publication shadow lane.

rev0047 made public bridge publication its own final guard, with a publication
ledger and quench lane.  rev0048 adds one more boundary before any future DHT
write, mutable-head update, or SAM-backed public refresh could exist: a shadow
side-effect plan that binds the publication guard, publication ledger, and
quench report to the same profile/service/scope/request/action.

This is deliberately not a live publisher.  It is a typed local judgment surface
for the hardest claim: "all local components passed" is still not permission for
a public side effect unless they pass at the exact same boundary.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .bridgequenchlane import BridgeQuenchReport
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .publicationguard import PublicationIntent, PublicationReport
from .publicationledger import PublicationLedgerReport

BRIDGE_SHADOW_DOMAIN = DOMAIN + b":bridge-shadow-v1:"


class BridgeShadowAction(str, Enum):
    SHADOW_REFRESH = "shadow_refresh"
    SHADOW_WITHDRAW = "shadow_withdraw"
    SHADOW_REPAIR = "shadow_repair"


INTENT_TO_SHADOW_ACTION = {
    PublicationIntent.PUBLIC_REFRESH: BridgeShadowAction.SHADOW_REFRESH,
    PublicationIntent.PUBLIC_WITHDRAW: BridgeShadowAction.SHADOW_WITHDRAW,
    PublicationIntent.PUBLIC_REPAIR: BridgeShadowAction.SHADOW_REPAIR,
}


class BridgeShadowDecisionKind(str, Enum):
    ACCEPT_SHADOW = "accept_shadow"
    ACCEPT_WITH_WATCH = "accept_with_watch"
    HOLD_PUBLICATION_NOT_ACCEPTED = "hold_publication_not_accepted"
    HOLD_LEDGER_NOT_ACCEPTED = "hold_ledger_not_accepted"
    HOLD_QUENCH = "hold_quench"
    HOLD_QUENCH_WATCH = "hold_quench_watch"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    QUARANTINE_PUBLICATION = "quarantine_publication"
    QUARANTINE_LEDGER = "quarantine_ledger"
    QUARANTINE_QUENCH = "quarantine_quench"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_EXPIRED_OR_FUTURE = "quarantine_expired_or_future"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_PROFILE_DRIFT = "quarantine_profile_drift"
    QUARANTINE_SERVICE_DRIFT = "quarantine_service_drift"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_REQUEST_DRIFT = "quarantine_request_drift"
    QUARANTINE_ACTION_DRIFT = "quarantine_action_drift"
    QUARANTINE_COMPONENT_DIGEST_DRIFT = "quarantine_component_digest_drift"
    QUARANTINE_PAYLOAD_DIGEST_DRIFT = "quarantine_payload_digest_drift"


@dataclass(frozen=True)
class BridgeShadowStep:
    action: BridgeShadowAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    publication_report_digest: bytes
    publication_ledger_digest: bytes
    quench_report_digest: bytes
    payload_digest: bytes
    shadow_effect_digest: bytes
    sequence: int
    previous_shadow_digest: bytes
    issued_at: int
    expires_at: int
    family_id: str
    path_family: str
    signer_public_key: bytes
    signature: bytes = b""

    def __post_init__(self) -> None:
        object.__setattr__(self, "action", BridgeShadowAction(self.action))
        if not self.profile_id or not self.service_name or not self.family_id or not self.path_family:
            raise ValueError("bridge shadow step needs profile/service/family/path")
        if self.sequence < 0:
            raise ValueError("sequence must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("expires_at must be after issued_at")
        for name, value in (
            ("scope_digest", self.scope_digest),
            ("request_digest", self.request_digest),
            ("publication_report_digest", self.publication_report_digest),
            ("publication_ledger_digest", self.publication_ledger_digest),
            ("quench_report_digest", self.quench_report_digest),
            ("payload_digest", self.payload_digest),
            ("shadow_effect_digest", self.shadow_effect_digest),
            ("previous_shadow_digest", self.previous_shadow_digest),
            ("signer_public_key", self.signer_public_key),
        ):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if self.signature and len(self.signature) != 64:
            raise ValueError("signature must be Ed25519-sized")

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"action": self.action.value,
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"publication": self.publication_report_digest,
            b"ledger": self.publication_ledger_digest,
            b"quench": self.quench_report_digest,
            b"payload": self.payload_digest,
            b"effect": self.shadow_effect_digest,
            b"seq": self.sequence,
            b"prev": self.previous_shadow_digest,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"family": self.family_id,
            b"path_family": self.path_family,
            b"signer": self.signer_public_key,
        }

    def signature_payload(self) -> bytes:
        return BRIDGE_SHADOW_DOMAIN + b":step-sig:" + bencode(self.unsigned_bvalue())

    @property
    def step_core_digest(self) -> bytes:
        return sha256(BRIDGE_SHADOW_DOMAIN + b":step-core:" + bencode(self.unsigned_bvalue()))

    @property
    def step_digest(self) -> bytes:
        return sha256(BRIDGE_SHADOW_DOMAIN + b":step-digest:" + self.signature_payload() + self.signature)

    def verifies(self) -> bool:
        return verify_signature(self.signer_public_key, self.signature_payload(), self.signature)


@dataclass(frozen=True)
class BridgeShadowReport:
    decision_kind: BridgeShadowDecisionKind
    accept: bool
    watch: bool
    reason: str
    profile_id: str
    service_name: str
    action: BridgeShadowAction
    scope_digest: bytes
    request_digest: bytes
    accepted_step_digest: bytes
    publication_report_digest: bytes
    publication_ledger_digest: bytes
    quench_report_digest: bytes
    payload_digest: bytes
    family_count: int
    path_family_count: int
    highest_sequence: int
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")

    @property
    def allow(self) -> bool:
        return self.accept


def make_bridge_shadow_step(
    *,
    keypair: DhtKeypair,
    action: BridgeShadowAction,
    profile_id: str,
    service_name: str,
    scope_digest: bytes,
    request_digest: bytes,
    publication_report_digest: bytes,
    publication_ledger_digest: bytes,
    quench_report_digest: bytes,
    payload_digest: bytes,
    shadow_effect_digest: bytes,
    sequence: int,
    previous_shadow_digest: bytes = ZERO_DIGEST,
    issued_at: int,
    expires_at: int,
    family_id: str,
    path_family: str,
) -> BridgeShadowStep:
    step = BridgeShadowStep(action, profile_id, service_name, scope_digest, request_digest, publication_report_digest, publication_ledger_digest, quench_report_digest, payload_digest, shadow_effect_digest, sequence, previous_shadow_digest, issued_at, expires_at, family_id, path_family, keypair.public_key_bytes)
    return replace(step, signature=keypair.sign(step.signature_payload()))


def _report(kind: BridgeShadowDecisionKind, accept: bool, watch: bool, reason: str, *, profile_id: str, service_name: str, action: BridgeShadowAction, scope_digest: bytes, request_digest: bytes, publication_report_digest: bytes, publication_ledger_digest: bytes, quench_report_digest: bytes, payload_digest: bytes = ZERO_DIGEST, steps: Iterable[BridgeShadowStep] = (), selected: BridgeShadowStep | None = None) -> BridgeShadowReport:
    step_tuple = tuple(sorted(steps, key=lambda item: (item.sequence, item.step_digest)))
    accepted = selected.step_digest if selected and accept else ZERO_DIGEST
    families = len({item.family_id for item in step_tuple})
    paths = len({item.path_family for item in step_tuple})
    highest = selected.sequence if selected else max((item.sequence for item in step_tuple), default=-1)
    digest = sha256(BRIDGE_SHADOW_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"reason": reason,
        b"profile": profile_id,
        b"service": service_name,
        b"action": action.value,
        b"scope": scope_digest,
        b"request": request_digest,
        b"accepted": accepted,
        b"publication": publication_report_digest,
        b"ledger": publication_ledger_digest,
        b"quench": quench_report_digest,
        b"payload": payload_digest,
        b"steps": [item.step_digest for item in step_tuple],
        b"families": families,
        b"paths": paths,
        b"highest": highest,
    }))
    return BridgeShadowReport(kind, accept, watch, reason, profile_id, service_name, action, scope_digest, request_digest, accepted, publication_report_digest, publication_ledger_digest, quench_report_digest, payload_digest, families, paths, highest, digest)


def assess_bridge_shadow(
    steps: Iterable[BridgeShadowStep],
    *,
    publication: PublicationReport,
    publication_ledger: PublicationLedgerReport,
    quench: BridgeQuenchReport,
    now: int,
    expected_profile_id: str,
    expected_service_name: str,
    expected_scope_digest: bytes,
    expected_request_digest: bytes,
    expected_payload_digest: bytes,
    previous_sequence: int | None = None,
    previous_shadow_digest: bytes | None = None,
    previously_seen_steps: Iterable[bytes] = (),
    min_family_diversity: int = 2,
    min_path_diversity: int = 2,
) -> BridgeShadowReport:
    try:
        action = INTENT_TO_SHADOW_ACTION[publication.intent]
    except KeyError:
        action = BridgeShadowAction.SHADOW_REFRESH
    component_watch = publication.watch or publication_ledger.watch or quench.watch
    if publication.quarantined:
        return _report(BridgeShadowDecisionKind.QUARANTINE_PUBLICATION, False, True, "publication report quarantined", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, publication_report_digest=publication.report_digest, publication_ledger_digest=publication_ledger.report_digest, quench_report_digest=quench.report_digest, payload_digest=expected_payload_digest)
    if publication_ledger.quarantined:
        return _report(BridgeShadowDecisionKind.QUARANTINE_LEDGER, False, True, "publication ledger quarantined", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, publication_report_digest=publication.report_digest, publication_ledger_digest=publication_ledger.report_digest, quench_report_digest=quench.report_digest, payload_digest=expected_payload_digest)
    if quench.quarantined:
        return _report(BridgeShadowDecisionKind.QUARANTINE_QUENCH, False, True, "quench report quarantined", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, publication_report_digest=publication.report_digest, publication_ledger_digest=publication_ledger.report_digest, quench_report_digest=quench.report_digest, payload_digest=expected_payload_digest)
    if not publication.accept:
        return _report(BridgeShadowDecisionKind.HOLD_PUBLICATION_NOT_ACCEPTED, False, publication.watch, "publication guard did not accept", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, publication_report_digest=publication.report_digest, publication_ledger_digest=publication_ledger.report_digest, quench_report_digest=quench.report_digest, payload_digest=expected_payload_digest)
    if not publication_ledger.accept:
        return _report(BridgeShadowDecisionKind.HOLD_LEDGER_NOT_ACCEPTED, False, publication_ledger.watch, "publication ledger did not accept", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, publication_report_digest=publication.report_digest, publication_ledger_digest=publication_ledger.report_digest, quench_report_digest=quench.report_digest, payload_digest=expected_payload_digest)
    if quench.quench:
        return _report(BridgeShadowDecisionKind.HOLD_QUENCH, False, True, "quench lane requested cooldown", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, publication_report_digest=publication.report_digest, publication_ledger_digest=publication_ledger.report_digest, quench_report_digest=quench.report_digest, payload_digest=expected_payload_digest)
    if not quench.continue_publication:
        return _report(BridgeShadowDecisionKind.HOLD_QUENCH_WATCH, False, True, "quench lane did not continue publication", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, publication_report_digest=publication.report_digest, publication_ledger_digest=publication_ledger.report_digest, quench_report_digest=quench.report_digest, payload_digest=expected_payload_digest)

    step_tuple = tuple(sorted(steps, key=lambda item: (item.sequence, item.step_digest)))
    seen = set(previously_seen_steps)
    core_by_sequence: dict[int, bytes] = {}
    for step in step_tuple:
        if not step.verifies():
            return _report(BridgeShadowDecisionKind.QUARANTINE_BAD_SIGNATURE, False, True, "bad bridge shadow signature", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, publication_report_digest=publication.report_digest, publication_ledger_digest=publication_ledger.report_digest, quench_report_digest=quench.report_digest, payload_digest=expected_payload_digest, steps=step_tuple)
        if step.issued_at > now or step.expires_at <= now:
            return _report(BridgeShadowDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, False, True, "bridge shadow step expired or future", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, publication_report_digest=publication.report_digest, publication_ledger_digest=publication_ledger.report_digest, quench_report_digest=quench.report_digest, payload_digest=expected_payload_digest, steps=step_tuple)
        if step.step_digest in seen:
            return _report(BridgeShadowDecisionKind.QUARANTINE_REPLAY, False, True, "bridge shadow step replay", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, publication_report_digest=publication.report_digest, publication_ledger_digest=publication_ledger.report_digest, quench_report_digest=quench.report_digest, payload_digest=expected_payload_digest, steps=step_tuple)
        if previous_sequence is not None and step.sequence < previous_sequence:
            return _report(BridgeShadowDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, True, "bridge shadow sequence rollback", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, publication_report_digest=publication.report_digest, publication_ledger_digest=publication_ledger.report_digest, quench_report_digest=quench.report_digest, payload_digest=expected_payload_digest, steps=step_tuple)
        existing = core_by_sequence.setdefault(step.sequence, step.step_core_digest)
        if existing != step.step_core_digest:
            return _report(BridgeShadowDecisionKind.QUARANTINE_SEQUENCE_FORK, False, True, "bridge shadow same-sequence fork", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, publication_report_digest=publication.report_digest, publication_ledger_digest=publication_ledger.report_digest, quench_report_digest=quench.report_digest, payload_digest=expected_payload_digest, steps=step_tuple)
        if previous_shadow_digest is not None and step.sequence > (previous_sequence or -1) and step.previous_shadow_digest != previous_shadow_digest:
            return _report(BridgeShadowDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, True, "bridge shadow previous digest mismatch", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, publication_report_digest=publication.report_digest, publication_ledger_digest=publication_ledger.report_digest, quench_report_digest=quench.report_digest, payload_digest=expected_payload_digest, steps=step_tuple)
        if step.profile_id != expected_profile_id:
            return _report(BridgeShadowDecisionKind.QUARANTINE_PROFILE_DRIFT, False, True, "bridge shadow profile drift", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, publication_report_digest=publication.report_digest, publication_ledger_digest=publication_ledger.report_digest, quench_report_digest=quench.report_digest, payload_digest=expected_payload_digest, steps=step_tuple)
        if step.service_name != expected_service_name:
            return _report(BridgeShadowDecisionKind.QUARANTINE_SERVICE_DRIFT, False, True, "bridge shadow service drift", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, publication_report_digest=publication.report_digest, publication_ledger_digest=publication_ledger.report_digest, quench_report_digest=quench.report_digest, payload_digest=expected_payload_digest, steps=step_tuple)
        if step.scope_digest != expected_scope_digest:
            return _report(BridgeShadowDecisionKind.QUARANTINE_SCOPE_DRIFT, False, True, "bridge shadow scope drift", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, publication_report_digest=publication.report_digest, publication_ledger_digest=publication_ledger.report_digest, quench_report_digest=quench.report_digest, payload_digest=expected_payload_digest, steps=step_tuple)
        if step.request_digest != expected_request_digest:
            return _report(BridgeShadowDecisionKind.QUARANTINE_REQUEST_DRIFT, False, True, "bridge shadow request drift", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, publication_report_digest=publication.report_digest, publication_ledger_digest=publication_ledger.report_digest, quench_report_digest=quench.report_digest, payload_digest=expected_payload_digest, steps=step_tuple)
        if step.action is not action:
            return _report(BridgeShadowDecisionKind.QUARANTINE_ACTION_DRIFT, False, True, "bridge shadow action drift", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, publication_report_digest=publication.report_digest, publication_ledger_digest=publication_ledger.report_digest, quench_report_digest=quench.report_digest, payload_digest=expected_payload_digest, steps=step_tuple)
        if step.publication_report_digest != publication.report_digest or step.publication_ledger_digest != publication_ledger.report_digest or step.quench_report_digest != quench.report_digest:
            return _report(BridgeShadowDecisionKind.QUARANTINE_COMPONENT_DIGEST_DRIFT, False, True, "bridge shadow component digest drift", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, publication_report_digest=publication.report_digest, publication_ledger_digest=publication_ledger.report_digest, quench_report_digest=quench.report_digest, payload_digest=expected_payload_digest, steps=step_tuple)
        if step.payload_digest != expected_payload_digest:
            return _report(BridgeShadowDecisionKind.QUARANTINE_PAYLOAD_DIGEST_DRIFT, False, True, "bridge shadow payload digest drift", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, publication_report_digest=publication.report_digest, publication_ledger_digest=publication_ledger.report_digest, quench_report_digest=quench.report_digest, payload_digest=expected_payload_digest, steps=step_tuple)
    families = {item.family_id for item in step_tuple}
    paths = {item.path_family for item in step_tuple}
    if len(families) < min_family_diversity:
        return _report(BridgeShadowDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, component_watch, "bridge shadow family diversity too low", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, publication_report_digest=publication.report_digest, publication_ledger_digest=publication_ledger.report_digest, quench_report_digest=quench.report_digest, payload_digest=expected_payload_digest, steps=step_tuple)
    if len(paths) < min_path_diversity:
        return _report(BridgeShadowDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, component_watch, "bridge shadow path diversity too low", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, publication_report_digest=publication.report_digest, publication_ledger_digest=publication_ledger.report_digest, quench_report_digest=quench.report_digest, payload_digest=expected_payload_digest, steps=step_tuple)
    selected = max(step_tuple, key=lambda item: (item.sequence, item.step_digest), default=None)
    if selected is None:
        return _report(BridgeShadowDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, component_watch, "no bridge shadow steps", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, publication_report_digest=publication.report_digest, publication_ledger_digest=publication_ledger.report_digest, quench_report_digest=quench.report_digest, payload_digest=expected_payload_digest, steps=step_tuple)
    kind = BridgeShadowDecisionKind.ACCEPT_WITH_WATCH if component_watch else BridgeShadowDecisionKind.ACCEPT_SHADOW
    return _report(kind, True, component_watch, "bridge shadow accepted", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, publication_report_digest=publication.report_digest, publication_ledger_digest=publication_ledger.report_digest, quench_report_digest=quench.report_digest, payload_digest=expected_payload_digest, steps=step_tuple, selected=selected)
