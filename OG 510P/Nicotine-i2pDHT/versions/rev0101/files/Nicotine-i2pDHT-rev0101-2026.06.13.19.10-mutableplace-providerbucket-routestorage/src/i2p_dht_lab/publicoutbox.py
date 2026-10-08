"""No-network publication outbox lane for public bridge side effects.

rev0048 shadow-executed public bridge side effects and collected local audit
receipts before pretending a bridge publication could be written.  rev0049 adds
one more hard boundary: the durable outbox.  A shadow report, audit quorum, and
redress-GC report may all pass, but a future network write must still be staged
as an idempotent, replay-resistant, exact-scope entry before any live SAM/I2P or
DHT side effect exists.

This module is deliberately a toy local judgment surface.  It does not send
anything, does not claim exactly-once network semantics, and does not decide DHT
truth.  It pins the local invariants that should exist before a live publisher is
allowed to be born.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .auditquorum import AuditQuorumReport
from .bencode import BValue, bencode
from .bridgeshadow import BridgeShadowAction, BridgeShadowReport
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .redressgc import RedressGcReport

PUBLIC_OUTBOX_DOMAIN = DOMAIN + b":public-outbox-v1:"


class PublicOutboxAction(str, Enum):
    QUEUE_REFRESH = "queue_refresh"
    QUEUE_WITHDRAW = "queue_withdraw"
    QUEUE_REPAIR = "queue_repair"


SHADOW_TO_OUTBOX_ACTION = {
    BridgeShadowAction.SHADOW_REFRESH: PublicOutboxAction.QUEUE_REFRESH,
    BridgeShadowAction.SHADOW_WITHDRAW: PublicOutboxAction.QUEUE_WITHDRAW,
    BridgeShadowAction.SHADOW_REPAIR: PublicOutboxAction.QUEUE_REPAIR,
}


class PublicOutboxDecisionKind(str, Enum):
    ACCEPT_STAGED = "accept_staged"
    ACCEPT_IDEMPOTENT_REPLAY = "accept_idempotent_replay"
    ACCEPT_WITH_WATCH = "accept_with_watch"
    HOLD_SHADOW_NOT_ACCEPTED = "hold_shadow_not_accepted"
    HOLD_AUDIT_NOT_ACCEPTED = "hold_audit_not_accepted"
    HOLD_REDRESS_NOT_ACCEPTED = "hold_redress_not_accepted"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    HOLD_WATCH_DEBT = "hold_watch_debt"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_EXPIRED_OR_FUTURE = "quarantine_expired_or_future"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_PROFILE_DRIFT = "quarantine_profile_drift"
    QUARANTINE_SERVICE_DRIFT = "quarantine_service_drift"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_REQUEST_DRIFT = "quarantine_request_drift"
    QUARANTINE_ACTION_DRIFT = "quarantine_action_drift"
    QUARANTINE_PAYLOAD_DRIFT = "quarantine_payload_drift"
    QUARANTINE_COMPONENT_DIGEST_DRIFT = "quarantine_component_digest_drift"
    QUARANTINE_IDEMPOTENCY_CONFLICT = "quarantine_idempotency_conflict"
    QUARANTINE_HARD_NEGATIVE_DROPPED = "quarantine_hard_negative_dropped"


@dataclass(frozen=True)
class PublicOutboxEntry:
    action: PublicOutboxAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    bridge_shadow_digest: bytes
    audit_quorum_digest: bytes
    redress_gc_digest: bytes
    outbox_effect_digest: bytes
    idempotency_key: bytes
    sequence: int
    previous_entry_digest: bytes
    issued_at: int
    expires_at: int
    family_id: str
    path_family: str
    signer_public_key: bytes
    signature: bytes = b""

    def __post_init__(self) -> None:
        object.__setattr__(self, "action", PublicOutboxAction(self.action))
        if not self.profile_id or not self.service_name or not self.family_id or not self.path_family:
            raise ValueError("public outbox entry needs profile/service/family/path")
        if self.sequence < 0:
            raise ValueError("sequence must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("expires_at must be after issued_at")
        for name, value in (
            ("scope_digest", self.scope_digest),
            ("request_digest", self.request_digest),
            ("payload_digest", self.payload_digest),
            ("bridge_shadow_digest", self.bridge_shadow_digest),
            ("audit_quorum_digest", self.audit_quorum_digest),
            ("redress_gc_digest", self.redress_gc_digest),
            ("outbox_effect_digest", self.outbox_effect_digest),
            ("idempotency_key", self.idempotency_key),
            ("previous_entry_digest", self.previous_entry_digest),
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
            b"payload": self.payload_digest,
            b"shadow": self.bridge_shadow_digest,
            b"audit": self.audit_quorum_digest,
            b"redress": self.redress_gc_digest,
            b"effect": self.outbox_effect_digest,
            b"idem": self.idempotency_key,
            b"seq": self.sequence,
            b"prev": self.previous_entry_digest,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"family": self.family_id,
            b"path_family": self.path_family,
            b"signer": self.signer_public_key,
        }

    def signature_payload(self) -> bytes:
        return PUBLIC_OUTBOX_DOMAIN + b":entry-sig:" + bencode(self.unsigned_bvalue())

    @property
    def entry_core_digest(self) -> bytes:
        return sha256(PUBLIC_OUTBOX_DOMAIN + b":entry-core:" + bencode(self.unsigned_bvalue()))

    @property
    def entry_digest(self) -> bytes:
        return sha256(PUBLIC_OUTBOX_DOMAIN + b":entry-digest:" + self.signature_payload() + self.signature)

    def verifies(self) -> bool:
        return verify_signature(self.signer_public_key, self.signature_payload(), self.signature)


def make_public_outbox_entry(
    *,
    keypair: DhtKeypair,
    action: PublicOutboxAction,
    profile_id: str,
    service_name: str,
    scope_digest: bytes,
    request_digest: bytes,
    payload_digest: bytes,
    bridge_shadow_digest: bytes,
    audit_quorum_digest: bytes,
    redress_gc_digest: bytes,
    outbox_effect_digest: bytes,
    idempotency_key: bytes,
    sequence: int,
    previous_entry_digest: bytes = ZERO_DIGEST,
    issued_at: int,
    expires_at: int,
    family_id: str,
    path_family: str,
) -> PublicOutboxEntry:
    entry = PublicOutboxEntry(action, profile_id, service_name, scope_digest, request_digest, payload_digest, bridge_shadow_digest, audit_quorum_digest, redress_gc_digest, outbox_effect_digest, idempotency_key, sequence, previous_entry_digest, issued_at, expires_at, family_id, path_family, keypair.public_key_bytes)
    return replace(entry, signature=keypair.sign(entry.signature_payload()))


@dataclass(frozen=True)
class PublicOutboxReport:
    decision_kind: PublicOutboxDecisionKind
    accept: bool
    watch: bool
    reason: str
    profile_id: str
    service_name: str
    action: PublicOutboxAction
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    accepted_entry_digest: bytes
    idempotency_key: bytes
    bridge_shadow_digest: bytes
    audit_quorum_digest: bytes
    redress_gc_digest: bytes
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


def _report(kind: PublicOutboxDecisionKind, accept: bool, watch: bool, reason: str, *, profile_id: str, service_name: str, action: PublicOutboxAction, scope_digest: bytes, request_digest: bytes, payload_digest: bytes, bridge_shadow_digest: bytes, audit_quorum_digest: bytes, redress_gc_digest: bytes, entries: Iterable[PublicOutboxEntry] = (), selected: PublicOutboxEntry | None = None, idempotency_key: bytes = ZERO_DIGEST) -> PublicOutboxReport:
    entry_tuple = tuple(sorted(entries, key=lambda item: (item.sequence, item.entry_digest)))
    families = len({item.family_id for item in entry_tuple})
    paths = len({item.path_family for item in entry_tuple})
    highest = selected.sequence if selected else max((item.sequence for item in entry_tuple), default=-1)
    accepted = selected.entry_digest if selected and accept else ZERO_DIGEST
    if selected is not None:
        idempotency_key = selected.idempotency_key
    digest = sha256(PUBLIC_OUTBOX_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"reason": reason,
        b"profile": profile_id,
        b"service": service_name,
        b"action": action.value,
        b"scope": scope_digest,
        b"request": request_digest,
        b"payload": payload_digest,
        b"accepted": accepted,
        b"idem": idempotency_key,
        b"shadow": bridge_shadow_digest,
        b"audit": audit_quorum_digest,
        b"redress": redress_gc_digest,
        b"families": families,
        b"paths": paths,
        b"highest": highest,
        b"entries": [item.entry_digest for item in entry_tuple],
    }))
    return PublicOutboxReport(kind, accept, watch, reason, profile_id, service_name, action, scope_digest, request_digest, payload_digest, accepted, idempotency_key, bridge_shadow_digest, audit_quorum_digest, redress_gc_digest, families, paths, highest, digest)


def assess_public_outbox(
    entries: Iterable[PublicOutboxEntry],
    *,
    bridge_shadow: BridgeShadowReport,
    audit_quorum: AuditQuorumReport,
    redress_gc: RedressGcReport,
    now: int,
    expected_profile_id: str,
    expected_service_name: str,
    expected_scope_digest: bytes,
    expected_request_digest: bytes,
    expected_payload_digest: bytes,
    expected_action: PublicOutboxAction | None = None,
    previous_entry_digest: bytes = ZERO_DIGEST,
    previously_committed_idempotency: Iterable[bytes] = (),
    committed_idempotency_effects: dict[bytes, bytes] | None = None,
    min_family_diversity: int = 2,
    min_path_diversity: int = 2,
    allow_watch_debt: bool = False,
) -> PublicOutboxReport:
    expected_action = expected_action or SHADOW_TO_OUTBOX_ACTION.get(bridge_shadow.action, PublicOutboxAction.QUEUE_REFRESH)
    committed_effects = committed_idempotency_effects or {}
    previously_committed = set(previously_committed_idempotency) | set(committed_effects)
    component_shadow_digest = bridge_shadow.report_digest
    component_audit_digest = audit_quorum.report_digest
    component_redress_digest = redress_gc.report_digest

    def make_report(kind: PublicOutboxDecisionKind, accept: bool, watch: bool, reason: str, *, selected: PublicOutboxEntry | None = None, candidate_entries: Iterable[PublicOutboxEntry] = (), idem: bytes = ZERO_DIGEST) -> PublicOutboxReport:
        return _report(kind, accept, watch, reason, profile_id=expected_profile_id, service_name=expected_service_name, action=expected_action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, payload_digest=expected_payload_digest, bridge_shadow_digest=component_shadow_digest, audit_quorum_digest=component_audit_digest, redress_gc_digest=component_redress_digest, entries=candidate_entries, selected=selected, idempotency_key=idem)

    if not bridge_shadow.accept:
        return make_report(PublicOutboxDecisionKind.HOLD_SHADOW_NOT_ACCEPTED, False, True, "bridge shadow report not accepted")
    if not audit_quorum.accept:
        return make_report(PublicOutboxDecisionKind.HOLD_AUDIT_NOT_ACCEPTED, False, True, "audit quorum report not accepted")
    if not redress_gc.accept:
        return make_report(PublicOutboxDecisionKind.HOLD_REDRESS_NOT_ACCEPTED, False, True, "redress GC report not accepted")
    if redress_gc.hard_negative_count and not allow_watch_debt:
        return make_report(PublicOutboxDecisionKind.QUARANTINE_HARD_NEGATIVE_DROPPED, False, True, "live hard-negative redress pressure cannot be queued without explicit watch debt")
    if (bridge_shadow.watch or audit_quorum.watch or redress_gc.watch) and not allow_watch_debt:
        return make_report(PublicOutboxDecisionKind.HOLD_WATCH_DEBT, False, True, "component watch debt must be explicitly carried into outbox")

    entry_tuple = tuple(sorted(entries, key=lambda item: (item.sequence, item.entry_digest)))
    if not entry_tuple:
        return make_report(PublicOutboxDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, "no outbox entries")

    core_by_seq: dict[int, bytes] = {}
    idem_to_effect: dict[bytes, bytes] = {}
    for entry in entry_tuple:
        if not entry.verifies():
            return make_report(PublicOutboxDecisionKind.QUARANTINE_BAD_SIGNATURE, False, True, "outbox entry signature failed", candidate_entries=entry_tuple)
        if entry.issued_at > now or entry.expires_at <= now:
            return make_report(PublicOutboxDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, False, True, "outbox entry expired or future-dated", candidate_entries=entry_tuple)
        if entry.profile_id != expected_profile_id:
            return make_report(PublicOutboxDecisionKind.QUARANTINE_PROFILE_DRIFT, False, True, "outbox profile drift", candidate_entries=entry_tuple)
        if entry.service_name != expected_service_name:
            return make_report(PublicOutboxDecisionKind.QUARANTINE_SERVICE_DRIFT, False, True, "outbox service drift", candidate_entries=entry_tuple)
        if entry.scope_digest != expected_scope_digest:
            return make_report(PublicOutboxDecisionKind.QUARANTINE_SCOPE_DRIFT, False, True, "outbox scope drift", candidate_entries=entry_tuple)
        if entry.request_digest != expected_request_digest:
            return make_report(PublicOutboxDecisionKind.QUARANTINE_REQUEST_DRIFT, False, True, "outbox request drift", candidate_entries=entry_tuple)
        if entry.payload_digest != expected_payload_digest:
            return make_report(PublicOutboxDecisionKind.QUARANTINE_PAYLOAD_DRIFT, False, True, "outbox payload drift", candidate_entries=entry_tuple)
        if entry.action is not expected_action:
            return make_report(PublicOutboxDecisionKind.QUARANTINE_ACTION_DRIFT, False, True, "outbox action drift", candidate_entries=entry_tuple)
        if (entry.bridge_shadow_digest != component_shadow_digest or entry.audit_quorum_digest != component_audit_digest or entry.redress_gc_digest != component_redress_digest):
            return make_report(PublicOutboxDecisionKind.QUARANTINE_COMPONENT_DIGEST_DRIFT, False, True, "outbox component digest drift", candidate_entries=entry_tuple)
        if entry.sequence == 0 and entry.previous_entry_digest != ZERO_DIGEST:
            return make_report(PublicOutboxDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, True, "genesis outbox entry has previous digest", candidate_entries=entry_tuple)
        if entry.sequence > 0 and previous_entry_digest != ZERO_DIGEST and entry.previous_entry_digest != previous_entry_digest:
            return make_report(PublicOutboxDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, True, "outbox previous digest mismatch", candidate_entries=entry_tuple)
        prev_core = core_by_seq.setdefault(entry.sequence, entry.entry_core_digest)
        if prev_core != entry.entry_core_digest:
            return make_report(PublicOutboxDecisionKind.QUARANTINE_SEQUENCE_FORK, False, True, "same-sequence outbox fork", candidate_entries=entry_tuple)
        prev_effect = idem_to_effect.setdefault(entry.idempotency_key, entry.outbox_effect_digest)
        if prev_effect != entry.outbox_effect_digest:
            return make_report(PublicOutboxDecisionKind.QUARANTINE_IDEMPOTENCY_CONFLICT, False, True, "same idempotency key maps to different effect", candidate_entries=entry_tuple)
        committed_effect = committed_effects.get(entry.idempotency_key)
        if committed_effect is not None and committed_effect != entry.outbox_effect_digest:
            return make_report(PublicOutboxDecisionKind.QUARANTINE_IDEMPOTENCY_CONFLICT, False, True, "committed idempotency key maps to different effect", candidate_entries=entry_tuple)

    newest = max(entry_tuple, key=lambda item: (item.sequence, item.entry_digest))
    if newest.idempotency_key in previously_committed:
        return make_report(PublicOutboxDecisionKind.ACCEPT_IDEMPOTENT_REPLAY, True, True, "outbox entry already committed with same idempotency key", selected=newest, candidate_entries=entry_tuple)
    if len({entry.family_id for entry in entry_tuple}) < min_family_diversity:
        return make_report(PublicOutboxDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, "outbox lacks family diversity", candidate_entries=entry_tuple)
    if len({entry.path_family for entry in entry_tuple}) < min_path_diversity:
        return make_report(PublicOutboxDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, "outbox lacks path diversity", candidate_entries=entry_tuple)
    watch = bridge_shadow.watch or audit_quorum.watch or redress_gc.watch or bool(redress_gc.hard_negative_count)
    return make_report(PublicOutboxDecisionKind.ACCEPT_WITH_WATCH if watch else PublicOutboxDecisionKind.ACCEPT_STAGED, True, bool(watch), "public outbox entry staged locally", selected=newest, candidate_entries=entry_tuple)
