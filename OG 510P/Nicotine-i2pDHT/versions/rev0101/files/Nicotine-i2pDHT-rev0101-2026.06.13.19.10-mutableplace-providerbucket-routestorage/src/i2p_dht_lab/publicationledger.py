"""Public bridge publication ledger.

A bridge ledger says a future public-bridge side effect was locally joined with
shadow-fire, egress, moderation, and redress.  rev0047 adds a stricter boundary:
actually publishing, withdrawing, or repairing public bridge records needs its
own tiny signed ledger because public exposure is sticky and easy to replay.

This is still a no-network lab surface.  It records the exact bridge-ledger and
witness-appeal mesh evidence that would justify a publication-shaped side effect.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .bridgeledger import BridgeLedgerAction, BridgeLedgerReport
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .witnessappealmesh import WitnessAppealMeshReport

PUBLICATION_LEDGER_DOMAIN = DOMAIN + b":publication-ledger-v1:"


class PublicationAction(str, Enum):
    PUBLISH_PUBLIC = "publish_public"
    WITHDRAW_PUBLIC = "withdraw_public"
    REPAIR_PUBLIC = "repair_public"
    QUENCH_NOTICE = "quench_notice"


class PublicationLedgerDecisionKind(str, Enum):
    ACCEPT_PUBLICATION = "accept_publication"
    ACCEPT_WITH_WATCH = "accept_with_watch"
    HOLD_MISSING_ENTRY = "hold_missing_entry"
    HOLD_BRIDGE_LEDGER = "hold_bridge_ledger"
    HOLD_APPEAL_MESH_REQUIRED = "hold_appeal_mesh_required"
    HOLD_APPEAL_MESH_WATCH = "hold_appeal_mesh_watch"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    QUARANTINE_BRIDGE_LEDGER = "quarantine_bridge_ledger"
    QUARANTINE_APPEAL_MESH = "quarantine_appeal_mesh"
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


_ALLOWED_BRIDGE_ACTIONS = {
    PublicationAction.PUBLISH_PUBLIC: {BridgeLedgerAction.PUBLIC_REFRESH},
    PublicationAction.WITHDRAW_PUBLIC: {BridgeLedgerAction.PUBLIC_WITHDRAW},
    PublicationAction.REPAIR_PUBLIC: {BridgeLedgerAction.PUBLIC_REPAIR, BridgeLedgerAction.PUBLIC_REFRESH, BridgeLedgerAction.PUBLIC_WITHDRAW},
    PublicationAction.QUENCH_NOTICE: {BridgeLedgerAction.PUBLIC_REFRESH, BridgeLedgerAction.PUBLIC_WITHDRAW, BridgeLedgerAction.PUBLIC_REPAIR},
}


@dataclass(frozen=True)
class PublicationLedgerEntry:
    action: PublicationAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    bridge_ledger_digest: bytes
    appeal_mesh_digest: bytes
    validator_root_digest: bytes
    public_record_digest: bytes
    side_effect_digest: bytes
    sequence: int
    previous_publication_digest: bytes
    issued_at: int
    expires_at: int
    family_id: str
    path_family: str
    signer_public_key: bytes
    signature: bytes = b""

    def __post_init__(self) -> None:
        object.__setattr__(self, "action", PublicationAction(self.action))
        if not self.profile_id or not self.service_name or not self.family_id or not self.path_family:
            raise ValueError("publication entry needs profile/service/family/path")
        if self.sequence < 0:
            raise ValueError("publication sequence must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("expires_at must be greater than issued_at")
        for name, value in (
            ("scope_digest", self.scope_digest),
            ("request_digest", self.request_digest),
            ("bridge_ledger_digest", self.bridge_ledger_digest),
            ("appeal_mesh_digest", self.appeal_mesh_digest),
            ("validator_root_digest", self.validator_root_digest),
            ("public_record_digest", self.public_record_digest),
            ("side_effect_digest", self.side_effect_digest),
            ("previous_publication_digest", self.previous_publication_digest),
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
            b"bridge": self.bridge_ledger_digest,
            b"appeal": self.appeal_mesh_digest,
            b"validator": self.validator_root_digest,
            b"record": self.public_record_digest,
            b"effect": self.side_effect_digest,
            b"seq": self.sequence,
            b"prev": self.previous_publication_digest,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"family": self.family_id,
            b"path_family": self.path_family,
            b"signer": self.signer_public_key,
        }

    def signature_payload(self) -> bytes:
        return PUBLICATION_LEDGER_DOMAIN + b":entry-sig:" + bencode(self.unsigned_bvalue())

    @property
    def entry_core_digest(self) -> bytes:
        return sha256(PUBLICATION_LEDGER_DOMAIN + b":entry-core:" + bencode(self.unsigned_bvalue()))

    @property
    def entry_digest(self) -> bytes:
        return sha256(PUBLICATION_LEDGER_DOMAIN + b":entry-digest:" + self.signature_payload() + self.signature)

    def verifies(self) -> bool:
        return verify_signature(self.signer_public_key, self.signature_payload(), self.signature)


@dataclass(frozen=True)
class PublicationLedgerReport:
    decision_kind: PublicationLedgerDecisionKind
    accept: bool
    watch: bool
    reason: str
    profile_id: str
    service_name: str
    action: PublicationAction
    scope_digest: bytes
    request_digest: bytes
    accepted_entry_digest: bytes
    bridge_ledger_digest: bytes
    appeal_mesh_digest: bytes
    validator_root_digest: bytes
    family_count: int
    path_family_count: int
    highest_sequence: int
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def make_publication_ledger_entry(
    *,
    keypair: DhtKeypair,
    action: PublicationAction,
    profile_id: str,
    service_name: str,
    scope_digest: bytes,
    request_digest: bytes,
    bridge_ledger_digest: bytes,
    appeal_mesh_digest: bytes = ZERO_DIGEST,
    validator_root_digest: bytes = ZERO_DIGEST,
    public_record_digest: bytes,
    side_effect_digest: bytes,
    sequence: int,
    previous_publication_digest: bytes = ZERO_DIGEST,
    issued_at: int,
    expires_at: int,
    family_id: str,
    path_family: str,
) -> PublicationLedgerEntry:
    entry = PublicationLedgerEntry(action, profile_id, service_name, scope_digest, request_digest, bridge_ledger_digest, appeal_mesh_digest, validator_root_digest, public_record_digest, side_effect_digest, sequence, previous_publication_digest, issued_at, expires_at, family_id, path_family, keypair.public_key_bytes)
    return replace(entry, signature=keypair.sign(entry.signature_payload()))


def _report(kind: PublicationLedgerDecisionKind, accept: bool, watch: bool, reason: str, *, profile_id: str, service_name: str, action: PublicationAction, scope_digest: bytes, request_digest: bytes, bridge_ledger_digest: bytes, appeal_mesh_digest: bytes, validator_root_digest: bytes, entries: Iterable[PublicationLedgerEntry] = (), selected: PublicationLedgerEntry | None = None, family_count: int = 0, path_family_count: int = 0) -> PublicationLedgerReport:
    entry_tuple = tuple(sorted(entries, key=lambda item: (item.sequence, item.entry_digest)))
    accepted = selected.entry_digest if selected and accept else ZERO_DIGEST
    highest = selected.sequence if selected else -1
    digest = sha256(PUBLICATION_LEDGER_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"reason": reason,
        b"profile": profile_id,
        b"service": service_name,
        b"action": action.value,
        b"scope": scope_digest,
        b"request": request_digest,
        b"entry": accepted,
        b"entries": [entry.entry_digest for entry in entry_tuple],
        b"bridge": bridge_ledger_digest,
        b"appeal": appeal_mesh_digest,
        b"validator": validator_root_digest,
        b"families": family_count,
        b"paths": path_family_count,
        b"highest": highest,
    }))
    return PublicationLedgerReport(kind, accept, watch, reason, profile_id, service_name, action, scope_digest, request_digest, accepted, bridge_ledger_digest, appeal_mesh_digest, validator_root_digest, family_count, path_family_count, highest, digest)


def assess_publication_ledger(
    entries: Iterable[PublicationLedgerEntry],
    *,
    bridge_ledger: BridgeLedgerReport,
    appeal_mesh: WitnessAppealMeshReport | None,
    now: int,
    action: PublicationAction,
    expected_profile_id: str,
    expected_service_name: str,
    expected_scope_digest: bytes,
    expected_request_digest: bytes,
    validator_root_digest: bytes = ZERO_DIGEST,
    previous_sequence: int | None = None,
    previous_publication_digest: bytes | None = None,
    previously_seen_entries: Iterable[bytes] = (),
    min_family_diversity: int = 2,
    min_path_diversity: int = 2,
    allow_watch: bool = False,
) -> PublicationLedgerReport:
    action = PublicationAction(action)
    appeal_digest = appeal_mesh.report_digest if appeal_mesh is not None else ZERO_DIGEST
    if bridge_ledger.quarantined:
        return _report(PublicationLedgerDecisionKind.QUARANTINE_BRIDGE_LEDGER, False, bridge_ledger.watch, "bridge ledger quarantined", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, bridge_ledger_digest=bridge_ledger.report_digest, appeal_mesh_digest=appeal_digest, validator_root_digest=validator_root_digest)
    if not bridge_ledger.accept:
        return _report(PublicationLedgerDecisionKind.HOLD_BRIDGE_LEDGER, False, bridge_ledger.watch, "bridge ledger not accepted", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, bridge_ledger_digest=bridge_ledger.report_digest, appeal_mesh_digest=appeal_digest, validator_root_digest=validator_root_digest)
    if bridge_ledger.action not in _ALLOWED_BRIDGE_ACTIONS[action]:
        return _report(PublicationLedgerDecisionKind.QUARANTINE_ACTION_DRIFT, False, bridge_ledger.watch, "publication action does not match bridge-ledger action", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, bridge_ledger_digest=bridge_ledger.report_digest, appeal_mesh_digest=appeal_digest, validator_root_digest=validator_root_digest)
    if bridge_ledger.watch and appeal_mesh is None:
        return _report(PublicationLedgerDecisionKind.HOLD_APPEAL_MESH_REQUIRED, False, True, "watched bridge ledger requires appeal mesh", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, bridge_ledger_digest=bridge_ledger.report_digest, appeal_mesh_digest=appeal_digest, validator_root_digest=validator_root_digest)
    if appeal_mesh is not None:
        if appeal_mesh.quarantined:
            return _report(PublicationLedgerDecisionKind.QUARANTINE_APPEAL_MESH, False, appeal_mesh.watch, "appeal mesh quarantined", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, bridge_ledger_digest=bridge_ledger.report_digest, appeal_mesh_digest=appeal_digest, validator_root_digest=validator_root_digest)
        if not appeal_mesh.accept:
            return _report(PublicationLedgerDecisionKind.HOLD_APPEAL_MESH_REQUIRED, False, appeal_mesh.watch, "appeal mesh not accepted", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, bridge_ledger_digest=bridge_ledger.report_digest, appeal_mesh_digest=appeal_digest, validator_root_digest=validator_root_digest)
        if appeal_mesh.profile_id != expected_profile_id or appeal_mesh.service_name != expected_service_name:
            return _report(PublicationLedgerDecisionKind.QUARANTINE_COMPONENT_DIGEST_DRIFT, False, True, "appeal mesh profile/service drift", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, bridge_ledger_digest=bridge_ledger.report_digest, appeal_mesh_digest=appeal_digest, validator_root_digest=validator_root_digest)
        if appeal_mesh.scope_digest != expected_scope_digest or appeal_mesh.request_digest != expected_request_digest:
            return _report(PublicationLedgerDecisionKind.QUARANTINE_COMPONENT_DIGEST_DRIFT, False, True, "appeal mesh scope/request drift", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, bridge_ledger_digest=bridge_ledger.report_digest, appeal_mesh_digest=appeal_digest, validator_root_digest=validator_root_digest)
        if appeal_mesh.bridge_ledger_digest != bridge_ledger.report_digest:
            return _report(PublicationLedgerDecisionKind.QUARANTINE_COMPONENT_DIGEST_DRIFT, False, True, "appeal mesh bridge digest drift", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, bridge_ledger_digest=bridge_ledger.report_digest, appeal_mesh_digest=appeal_digest, validator_root_digest=validator_root_digest)
        if appeal_mesh.watch and not allow_watch:
            return _report(PublicationLedgerDecisionKind.HOLD_APPEAL_MESH_WATCH, False, True, "appeal mesh has watch pressure", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, bridge_ledger_digest=bridge_ledger.report_digest, appeal_mesh_digest=appeal_digest, validator_root_digest=validator_root_digest)
    entry_tuple = tuple(sorted(entries, key=lambda item: (item.sequence, item.entry_digest)))
    if not entry_tuple:
        return _report(PublicationLedgerDecisionKind.HOLD_MISSING_ENTRY, False, bridge_ledger.watch, "missing publication ledger entry", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, bridge_ledger_digest=bridge_ledger.report_digest, appeal_mesh_digest=appeal_digest, validator_root_digest=validator_root_digest)
    seen = set(previously_seen_entries)
    fork_guard: dict[int, bytes] = {}
    families: set[str] = set()
    paths: set[str] = set()
    latest: PublicationLedgerEntry | None = None
    for entry in entry_tuple:
        if not entry.verifies():
            return _report(PublicationLedgerDecisionKind.QUARANTINE_BAD_SIGNATURE, False, True, "bad publication signature", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, bridge_ledger_digest=bridge_ledger.report_digest, appeal_mesh_digest=appeal_digest, validator_root_digest=validator_root_digest, entries=entry_tuple)
        if entry.issued_at > now or entry.expires_at <= now:
            return _report(PublicationLedgerDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, False, True, "publication entry expired or future", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, bridge_ledger_digest=bridge_ledger.report_digest, appeal_mesh_digest=appeal_digest, validator_root_digest=validator_root_digest, entries=entry_tuple)
        if entry.entry_digest in seen:
            return _report(PublicationLedgerDecisionKind.QUARANTINE_REPLAY, False, True, "publication entry replay", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, bridge_ledger_digest=bridge_ledger.report_digest, appeal_mesh_digest=appeal_digest, validator_root_digest=validator_root_digest, entries=entry_tuple)
        if entry.profile_id != expected_profile_id:
            return _report(PublicationLedgerDecisionKind.QUARANTINE_PROFILE_DRIFT, False, True, "publication profile drift", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, bridge_ledger_digest=bridge_ledger.report_digest, appeal_mesh_digest=appeal_digest, validator_root_digest=validator_root_digest, entries=entry_tuple)
        if entry.service_name != expected_service_name:
            return _report(PublicationLedgerDecisionKind.QUARANTINE_SERVICE_DRIFT, False, True, "publication service drift", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, bridge_ledger_digest=bridge_ledger.report_digest, appeal_mesh_digest=appeal_digest, validator_root_digest=validator_root_digest, entries=entry_tuple)
        if entry.scope_digest != expected_scope_digest:
            return _report(PublicationLedgerDecisionKind.QUARANTINE_SCOPE_DRIFT, False, True, "publication scope drift", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, bridge_ledger_digest=bridge_ledger.report_digest, appeal_mesh_digest=appeal_digest, validator_root_digest=validator_root_digest, entries=entry_tuple)
        if entry.request_digest != expected_request_digest:
            return _report(PublicationLedgerDecisionKind.QUARANTINE_REQUEST_DRIFT, False, True, "publication request drift", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, bridge_ledger_digest=bridge_ledger.report_digest, appeal_mesh_digest=appeal_digest, validator_root_digest=validator_root_digest, entries=entry_tuple)
        if entry.action is not action:
            return _report(PublicationLedgerDecisionKind.QUARANTINE_ACTION_DRIFT, False, True, "publication action drift", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, bridge_ledger_digest=bridge_ledger.report_digest, appeal_mesh_digest=appeal_digest, validator_root_digest=validator_root_digest, entries=entry_tuple)
        if entry.bridge_ledger_digest != bridge_ledger.report_digest or entry.appeal_mesh_digest != appeal_digest or entry.validator_root_digest != validator_root_digest:
            return _report(PublicationLedgerDecisionKind.QUARANTINE_COMPONENT_DIGEST_DRIFT, False, True, "publication component digest drift", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, bridge_ledger_digest=bridge_ledger.report_digest, appeal_mesh_digest=appeal_digest, validator_root_digest=validator_root_digest, entries=entry_tuple)
        if previous_sequence is not None and entry.sequence < previous_sequence:
            return _report(PublicationLedgerDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, True, "publication sequence rollback", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, bridge_ledger_digest=bridge_ledger.report_digest, appeal_mesh_digest=appeal_digest, validator_root_digest=validator_root_digest, entries=entry_tuple)
        prior = fork_guard.get(entry.sequence)
        if prior is not None and prior != entry.entry_core_digest:
            return _report(PublicationLedgerDecisionKind.QUARANTINE_SEQUENCE_FORK, False, True, "same-sequence publication fork", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, bridge_ledger_digest=bridge_ledger.report_digest, appeal_mesh_digest=appeal_digest, validator_root_digest=validator_root_digest, entries=entry_tuple)
        fork_guard[entry.sequence] = entry.entry_core_digest
        families.add(entry.family_id)
        paths.add(entry.path_family)
        if latest is None or entry.sequence > latest.sequence:
            latest = entry
    assert latest is not None
    if previous_sequence is not None and latest.sequence > previous_sequence and previous_publication_digest is not None and latest.previous_publication_digest != previous_publication_digest:
        return _report(PublicationLedgerDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, True, "publication previous-link mismatch", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, bridge_ledger_digest=bridge_ledger.report_digest, appeal_mesh_digest=appeal_digest, validator_root_digest=validator_root_digest, entries=entry_tuple, selected=latest, family_count=len(families), path_family_count=len(paths))
    if len(families) < min_family_diversity:
        return _report(PublicationLedgerDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, bridge_ledger.watch, "publication lacks family diversity", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, bridge_ledger_digest=bridge_ledger.report_digest, appeal_mesh_digest=appeal_digest, validator_root_digest=validator_root_digest, entries=entry_tuple, selected=latest, family_count=len(families), path_family_count=len(paths))
    if len(paths) < min_path_diversity:
        return _report(PublicationLedgerDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, bridge_ledger.watch, "publication lacks path diversity", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, bridge_ledger_digest=bridge_ledger.report_digest, appeal_mesh_digest=appeal_digest, validator_root_digest=validator_root_digest, entries=entry_tuple, selected=latest, family_count=len(families), path_family_count=len(paths))
    watch = bridge_ledger.watch or (appeal_mesh.watch if appeal_mesh is not None else False)
    kind = PublicationLedgerDecisionKind.ACCEPT_WITH_WATCH if watch else PublicationLedgerDecisionKind.ACCEPT_PUBLICATION
    return _report(kind, True, watch, "publication ledger accepted after bridge and appeal boundary", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, bridge_ledger_digest=bridge_ledger.report_digest, appeal_mesh_digest=appeal_digest, validator_root_digest=validator_root_digest, entries=entry_tuple, selected=latest, family_count=len(families), path_family_count=len(paths))
