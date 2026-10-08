"""Bridge side-effect ledger joined to moderation and egress pressure.

rev0045's shadow-fire gate asks whether a public bridge side effect is locally
allowed.  rev0046 adds the uncomfortable next question: can the node actually
spend outbound metadata and publish/withdraw/repair when subjective moderation
and redress evidence are in play?

A bridge ledger entry is not a network operation.  It is a signed local record
that the exact shadow-fire, egress, moderation, and optional redress reports were
joined before a future side effect would happen.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .bridgeepoch import BridgeEpochAction
from .egressmeter import EgressWindowReport
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .moderationquarantine import ModerationDecisionKind, ModerationQuarantineReport, ZERO_DIGEST
from .redresslane import RedressReport
from .shadowfire import ShadowFireReport

BRIDGE_LEDGER_DOMAIN = DOMAIN + b":bridge-ledger-v1:"


class BridgeLedgerAction(str, Enum):
    PUBLIC_REFRESH = "public_refresh"
    PUBLIC_WITHDRAW = "public_withdraw"
    PUBLIC_REPAIR = "public_repair"


class BridgeLedgerDecisionKind(str, Enum):
    ACCEPT_LEDGER = "accept_ledger"
    ACCEPT_WITH_WATCH = "accept_with_watch"
    HOLD_MISSING_ENTRY = "hold_missing_entry"
    HOLD_SHADOW_FIRE = "hold_shadow_fire"
    HOLD_EGRESS = "hold_egress"
    HOLD_MODERATION_WATCH = "hold_moderation_watch"
    HOLD_REDRESS_NEEDED = "hold_redress_needed"
    HOLD_REDRESS_WATCH = "hold_redress_watch"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_EXPIRED_OR_FUTURE = "quarantine_expired_or_future"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_PROFILE_DRIFT = "quarantine_profile_drift"
    QUARANTINE_SERVICE_DRIFT = "quarantine_service_drift"
    QUARANTINE_ACTION_DRIFT = "quarantine_action_drift"
    QUARANTINE_COMPONENT_DIGEST_DRIFT = "quarantine_component_digest_drift"
    QUARANTINE_SHADOW_FIRE = "quarantine_shadow_fire"
    QUARANTINE_EGRESS = "quarantine_egress"
    QUARANTINE_MODERATION_BLOCK = "quarantine_moderation_block"
    QUARANTINE_REDRESS = "quarantine_redress"


_ACTION_TO_EPOCH = {
    BridgeLedgerAction.PUBLIC_REFRESH: {BridgeEpochAction.OPEN_PUBLIC, BridgeEpochAction.RENEW_PUBLIC},
    BridgeLedgerAction.PUBLIC_WITHDRAW: {BridgeEpochAction.CLOSE_PUBLIC, BridgeEpochAction.WITHDRAW_PUBLIC},
    BridgeLedgerAction.PUBLIC_REPAIR: {BridgeEpochAction.CLOSE_PUBLIC, BridgeEpochAction.WITHDRAW_PUBLIC, BridgeEpochAction.RENEW_PUBLIC},
}


@dataclass(frozen=True)
class BridgeLedgerEntry:
    action: BridgeLedgerAction
    profile_id: str
    service_name: str
    shadow_fire_digest: bytes
    egress_digest: bytes
    moderation_digest: bytes
    redress_digest: bytes
    side_effect_digest: bytes
    sequence: int
    previous_ledger_digest: bytes
    issued_at: int
    expires_at: int
    family_id: str
    path_family: str
    signer_public_key: bytes
    signature: bytes = b""

    def __post_init__(self) -> None:
        if not self.profile_id or len(self.profile_id.encode("utf-8")) > 80:
            raise ValueError("profile_id must be short and non-empty")
        if not self.service_name or len(self.service_name.encode("utf-8")) > 96:
            raise ValueError("service_name must be short and non-empty")
        if self.sequence < 0:
            raise ValueError("bridge ledger sequence must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("expires_at must be after issued_at")
        if not self.family_id or not self.path_family:
            raise ValueError("family_id and path_family must be non-empty")
        for name, value in (
            ("shadow_fire_digest", self.shadow_fire_digest),
            ("egress_digest", self.egress_digest),
            ("moderation_digest", self.moderation_digest),
            ("redress_digest", self.redress_digest),
            ("side_effect_digest", self.side_effect_digest),
            ("previous_ledger_digest", self.previous_ledger_digest),
            ("signer_public_key", self.signer_public_key),
        ):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if self.signature and len(self.signature) != 64:
            raise ValueError("signature must be Ed25519-sized")
        object.__setattr__(self, "action", BridgeLedgerAction(self.action))

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"action": self.action.value,
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"shadow": self.shadow_fire_digest,
            b"egress": self.egress_digest,
            b"moderation": self.moderation_digest,
            b"redress": self.redress_digest,
            b"effect": self.side_effect_digest,
            b"seq": self.sequence,
            b"prev": self.previous_ledger_digest,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"family": self.family_id,
            b"path_family": self.path_family,
            b"signer": self.signer_public_key,
        }

    def signature_payload(self) -> bytes:
        return BRIDGE_LEDGER_DOMAIN + b":entry-sig:" + bencode(self.unsigned_bvalue())

    @property
    def entry_core_digest(self) -> bytes:
        return sha256(BRIDGE_LEDGER_DOMAIN + b":entry-core:" + bencode(self.unsigned_bvalue()))

    @property
    def entry_digest(self) -> bytes:
        return sha256(BRIDGE_LEDGER_DOMAIN + b":entry-digest:" + self.signature_payload() + self.signature)

    def verifies(self) -> bool:
        return verify_signature(self.signer_public_key, self.signature_payload(), self.signature)


@dataclass(frozen=True)
class BridgeLedgerReport:
    decision_kind: BridgeLedgerDecisionKind
    accept: bool
    watch: bool
    reason: str
    profile_id: str
    service_name: str
    action: BridgeLedgerAction
    accepted_entry_digest: bytes
    component_digests: tuple[bytes, ...]
    family_count: int
    path_family_count: int
    highest_sequence: int
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")



def make_bridge_ledger_entry(
    *,
    keypair: DhtKeypair,
    action: BridgeLedgerAction,
    profile_id: str,
    service_name: str,
    shadow_fire_digest: bytes,
    egress_digest: bytes,
    moderation_digest: bytes,
    redress_digest: bytes = ZERO_DIGEST,
    side_effect_digest: bytes,
    sequence: int,
    previous_ledger_digest: bytes = ZERO_DIGEST,
    issued_at: int,
    expires_at: int,
    family_id: str,
    path_family: str,
) -> BridgeLedgerEntry:
    entry = BridgeLedgerEntry(action, profile_id, service_name, shadow_fire_digest, egress_digest, moderation_digest, redress_digest, side_effect_digest, sequence, previous_ledger_digest, issued_at, expires_at, family_id, path_family, keypair.public_key_bytes)
    return replace(entry, signature=keypair.sign(entry.signature_payload()))



def _report(kind: BridgeLedgerDecisionKind, accept: bool, watch: bool, reason: str, *, profile_id: str, service_name: str, action: BridgeLedgerAction, entries: Iterable[BridgeLedgerEntry] = (), selected: BridgeLedgerEntry | None = None, components: Iterable[bytes] = (), family_count: int = 0, path_family_count: int = 0) -> BridgeLedgerReport:
    entry_tuple = tuple(sorted(entries, key=lambda item: (item.sequence, item.entry_digest)))
    component_tuple = tuple(sorted(set(components)))
    accepted = selected.entry_digest if selected and accept else ZERO_DIGEST
    highest = selected.sequence if selected else -1
    digest = sha256(BRIDGE_LEDGER_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"reason": reason,
        b"profile": profile_id,
        b"service": service_name,
        b"action": action.value,
        b"entry": accepted,
        b"entries": [entry.entry_digest for entry in entry_tuple],
        b"components": list(component_tuple),
        b"families": family_count,
        b"paths": path_family_count,
        b"highest": highest,
    }))
    return BridgeLedgerReport(kind, accept, watch, reason, profile_id, service_name, action, accepted, component_tuple, family_count, path_family_count, highest, digest)



def assess_bridge_ledger(
    entries: Iterable[BridgeLedgerEntry],
    *,
    shadow_fire: ShadowFireReport,
    egress: EgressWindowReport,
    moderation: ModerationQuarantineReport,
    redress: RedressReport | None,
    now: int,
    action: BridgeLedgerAction,
    expected_profile_id: str,
    expected_service_name: str,
    previous_sequence: int | None = None,
    previous_ledger_digest: bytes | None = None,
    previously_seen_entries: Iterable[bytes] = (),
    min_family_diversity: int = 2,
    min_path_diversity: int = 2,
    allow_watch: bool = False,
) -> BridgeLedgerReport:
    action = BridgeLedgerAction(action)
    components = [shadow_fire.report_digest, egress.report_digest, moderation.report_digest]
    redress_digest = redress.report_digest if redress is not None else ZERO_DIGEST
    if redress is not None:
        components.append(redress.report_digest)
    entry_tuple = tuple(sorted(entries, key=lambda item: (item.sequence, item.entry_digest)))
    if not entry_tuple:
        return _report(BridgeLedgerDecisionKind.HOLD_MISSING_ENTRY, False, False, "missing bridge ledger entry", profile_id=expected_profile_id, service_name=expected_service_name, action=action, components=components)
    seen = set(previously_seen_entries)
    fork_guard: dict[int, bytes] = {}
    families: set[str] = set()
    paths: set[str] = set()
    latest: BridgeLedgerEntry | None = None
    for entry in entry_tuple:
        if not entry.verifies():
            return _report(BridgeLedgerDecisionKind.QUARANTINE_BAD_SIGNATURE, False, False, "bad bridge ledger signature", profile_id=expected_profile_id, service_name=expected_service_name, action=action, entries=entry_tuple, components=components)
        if entry.issued_at > now or entry.expires_at <= now:
            return _report(BridgeLedgerDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, False, False, "bridge ledger entry expired or future", profile_id=expected_profile_id, service_name=expected_service_name, action=action, entries=entry_tuple, components=components)
        if entry.entry_digest in seen:
            return _report(BridgeLedgerDecisionKind.QUARANTINE_REPLAY, False, False, "bridge ledger replay", profile_id=expected_profile_id, service_name=expected_service_name, action=action, entries=entry_tuple, components=components)
        if entry.profile_id != expected_profile_id or shadow_fire.profile_id != expected_profile_id or moderation.profile_id != expected_profile_id:
            return _report(BridgeLedgerDecisionKind.QUARANTINE_PROFILE_DRIFT, False, False, "bridge ledger profile drift", profile_id=expected_profile_id, service_name=expected_service_name, action=action, entries=entry_tuple, components=components)
        if entry.service_name != expected_service_name or shadow_fire.service_name != expected_service_name or moderation.service_name != expected_service_name:
            return _report(BridgeLedgerDecisionKind.QUARANTINE_SERVICE_DRIFT, False, False, "bridge ledger service drift", profile_id=expected_profile_id, service_name=expected_service_name, action=action, entries=entry_tuple, components=components)
        if entry.action is not action:
            return _report(BridgeLedgerDecisionKind.QUARANTINE_ACTION_DRIFT, False, False, "bridge ledger action drift", profile_id=expected_profile_id, service_name=expected_service_name, action=action, entries=entry_tuple, components=components)
        if entry.shadow_fire_digest != shadow_fire.report_digest or entry.egress_digest != egress.report_digest or entry.moderation_digest != moderation.report_digest or entry.redress_digest != redress_digest:
            return _report(BridgeLedgerDecisionKind.QUARANTINE_COMPONENT_DIGEST_DRIFT, False, False, "bridge ledger component digest drift", profile_id=expected_profile_id, service_name=expected_service_name, action=action, entries=entry_tuple, components=components)
        if previous_sequence is not None and entry.sequence < previous_sequence:
            return _report(BridgeLedgerDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, False, "bridge ledger sequence rollback", profile_id=expected_profile_id, service_name=expected_service_name, action=action, entries=entry_tuple, components=components)
        prior = fork_guard.get(entry.sequence)
        if prior is not None and prior != entry.entry_core_digest:
            return _report(BridgeLedgerDecisionKind.QUARANTINE_SEQUENCE_FORK, False, False, "same-sequence bridge ledger fork", profile_id=expected_profile_id, service_name=expected_service_name, action=action, entries=entry_tuple, components=components)
        fork_guard[entry.sequence] = entry.entry_core_digest
        families.add(entry.family_id)
        paths.add(entry.path_family)
        if latest is None or entry.sequence > latest.sequence:
            latest = entry
    assert latest is not None
    if previous_sequence is not None and latest.sequence > previous_sequence and previous_ledger_digest is not None and latest.previous_ledger_digest != previous_ledger_digest:
        return _report(BridgeLedgerDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, False, "bridge ledger previous-link mismatch", profile_id=expected_profile_id, service_name=expected_service_name, action=action, entries=entry_tuple, selected=latest, components=components, family_count=len(families), path_family_count=len(paths))
    if shadow_fire.quarantined:
        return _report(BridgeLedgerDecisionKind.QUARANTINE_SHADOW_FIRE, False, shadow_fire.watch, "shadow fire quarantined", profile_id=expected_profile_id, service_name=expected_service_name, action=action, entries=entry_tuple, selected=latest, components=components, family_count=len(families), path_family_count=len(paths))
    if not shadow_fire.accept:
        return _report(BridgeLedgerDecisionKind.HOLD_SHADOW_FIRE, False, shadow_fire.watch, "shadow fire not accepted", profile_id=expected_profile_id, service_name=expected_service_name, action=action, entries=entry_tuple, selected=latest, components=components, family_count=len(families), path_family_count=len(paths))
    if shadow_fire.bridge_action not in _ACTION_TO_EPOCH[action]:
        return _report(BridgeLedgerDecisionKind.QUARANTINE_ACTION_DRIFT, False, shadow_fire.watch, "shadow fire bridge action does not match ledger action", profile_id=expected_profile_id, service_name=expected_service_name, action=action, entries=entry_tuple, selected=latest, components=components, family_count=len(families), path_family_count=len(paths))
    if egress.quarantined:
        return _report(BridgeLedgerDecisionKind.QUARANTINE_EGRESS, False, shadow_fire.watch, "egress quarantined", profile_id=expected_profile_id, service_name=expected_service_name, action=action, entries=entry_tuple, selected=latest, components=components, family_count=len(families), path_family_count=len(paths))
    if not egress.accept:
        return _report(BridgeLedgerDecisionKind.HOLD_EGRESS, False, shadow_fire.watch, "egress window not accepted", profile_id=expected_profile_id, service_name=expected_service_name, action=action, entries=entry_tuple, selected=latest, components=components, family_count=len(families), path_family_count=len(paths))
    if moderation.quarantined:
        return _report(BridgeLedgerDecisionKind.QUARANTINE_MODERATION_BLOCK, False, moderation.watch, "moderation lane quarantined", profile_id=expected_profile_id, service_name=expected_service_name, action=action, entries=entry_tuple, selected=latest, components=components, family_count=len(families), path_family_count=len(paths))
    if moderation.blocked:
        if redress is None or not redress.accept or not redress.lifted:
            return _report(BridgeLedgerDecisionKind.HOLD_REDRESS_NEEDED, False, moderation.watch, "moderation block needs accepted lifting redress", profile_id=expected_profile_id, service_name=expected_service_name, action=action, entries=entry_tuple, selected=latest, components=components, family_count=len(families), path_family_count=len(paths))
        if redress.quarantined:
            return _report(BridgeLedgerDecisionKind.QUARANTINE_REDRESS, False, redress.watch, "redress lane quarantined", profile_id=expected_profile_id, service_name=expected_service_name, action=action, entries=entry_tuple, selected=latest, components=components, family_count=len(families), path_family_count=len(paths))
    if moderation.watch and not allow_watch:
        return _report(BridgeLedgerDecisionKind.HOLD_MODERATION_WATCH, False, True, "moderation watch requires explicit allowance", profile_id=expected_profile_id, service_name=expected_service_name, action=action, entries=entry_tuple, selected=latest, components=components, family_count=len(families), path_family_count=len(paths))
    watch = shadow_fire.watch or moderation.watch or (redress.watch if redress is not None else False) or egress.decision_kind.value == "accept_with_watch"
    if watch and not allow_watch:
        return _report(BridgeLedgerDecisionKind.HOLD_REDRESS_WATCH, False, True, "joined bridge ledger contains watch pressure", profile_id=expected_profile_id, service_name=expected_service_name, action=action, entries=entry_tuple, selected=latest, components=components, family_count=len(families), path_family_count=len(paths))
    if len(families) < min_family_diversity:
        return _report(BridgeLedgerDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, watch, "bridge ledger lacks family diversity", profile_id=expected_profile_id, service_name=expected_service_name, action=action, entries=entry_tuple, selected=latest, components=components, family_count=len(families), path_family_count=len(paths))
    if len(paths) < min_path_diversity:
        return _report(BridgeLedgerDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, watch, "bridge ledger lacks path diversity", profile_id=expected_profile_id, service_name=expected_service_name, action=action, entries=entry_tuple, selected=latest, components=components, family_count=len(families), path_family_count=len(paths))
    kind = BridgeLedgerDecisionKind.ACCEPT_WITH_WATCH if watch else BridgeLedgerDecisionKind.ACCEPT_LEDGER
    return _report(kind, True, watch, "bridge ledger accepted after shadowfire, egress, moderation, and redress join", profile_id=expected_profile_id, service_name=expected_service_name, action=action, entries=entry_tuple, selected=latest, components=components, family_count=len(families), path_family_count=len(paths))
