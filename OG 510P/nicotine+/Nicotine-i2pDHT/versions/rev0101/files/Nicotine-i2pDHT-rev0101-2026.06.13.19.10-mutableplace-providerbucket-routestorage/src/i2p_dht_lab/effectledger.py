"""Durable no-network public-effect ledger.

The public send seal says a future live writer may consider one exact public side
effect.  The effect ledger is the next local boundary: restartable memory of
prepare/send-shadow/commit/abort observations keyed by idempotency and exact
scope.  It is not a publisher and does not open SAM.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Any, Iterable, Mapping

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sendseal import SendSealReport

EFFECT_LEDGER_DOMAIN = DOMAIN + b":effect-ledger-v1:"


class EffectLedgerPhase(str, Enum):
    PREPARE = "prepare"
    SEND_SHADOW = "send_shadow"
    COMMIT = "commit"
    ABORT = "abort"


PHASE_ORDER = {
    EffectLedgerPhase.PREPARE: 1,
    EffectLedgerPhase.SEND_SHADOW: 2,
    EffectLedgerPhase.COMMIT: 3,
    EffectLedgerPhase.ABORT: 4,
}


class EffectLedgerDecisionKind(str, Enum):
    ACCEPT_COMMITTED = "accept_committed"
    ACCEPT_ABORTED = "accept_aborted"
    ACCEPT_PREPARED_WITH_WATCH = "accept_prepared_with_watch"
    EMPTY_NO_ENTRIES = "empty_no_entries"
    HOLD_SEND_SEAL = "hold_send_seal"
    HOLD_SAM_CANARY = "hold_sam_canary"
    HOLD_OUTBOX_DRAIN = "hold_outbox_drain"
    HOLD_NOT_COMMITTED = "hold_not_committed"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    QUARANTINE_SEND_SEAL = "quarantine_send_seal"
    QUARANTINE_SAM_CANARY = "quarantine_sam_canary"
    QUARANTINE_OUTBOX_DRAIN = "quarantine_outbox_drain"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_EXPIRED_OR_FUTURE = "quarantine_expired_or_future"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_PHASE_REGRESSION = "quarantine_phase_regression"
    QUARANTINE_PROFILE_DRIFT = "quarantine_profile_drift"
    QUARANTINE_SERVICE_DRIFT = "quarantine_service_drift"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_REQUEST_DRIFT = "quarantine_request_drift"
    QUARANTINE_PAYLOAD_DRIFT = "quarantine_payload_drift"
    QUARANTINE_COMPONENT_DIGEST_DRIFT = "quarantine_component_digest_drift"
    QUARANTINE_IDEMPOTENCY_CONFLICT = "quarantine_idempotency_conflict"
    QUARANTINE_EFFECT_CONFLICT = "quarantine_effect_conflict"


@dataclass(frozen=True)
class EffectLedgerEntry:
    phase: EffectLedgerPhase
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    public_payload_digest: bytes
    idempotency_key: bytes
    public_effect_digest: bytes
    send_seal_digest: bytes
    sam_canary_digest: bytes
    outbox_drain_digest: bytes
    sequence: int
    previous_entry_digest: bytes
    issued_at: int
    expires_at: int
    family_id: str
    path_family: str
    signer_public_key: bytes
    signature: bytes = b""

    def __post_init__(self) -> None:
        object.__setattr__(self, "phase", EffectLedgerPhase(self.phase))
        if not self.profile_id or not self.service_name or not self.family_id or not self.path_family:
            raise ValueError("effect ledger entry requires profile/service/family/path")
        if self.sequence < 0:
            raise ValueError("sequence must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("expires_at must follow issued_at")
        for name, value in (
            ("scope_digest", self.scope_digest),
            ("request_digest", self.request_digest),
            ("public_payload_digest", self.public_payload_digest),
            ("idempotency_key", self.idempotency_key),
            ("public_effect_digest", self.public_effect_digest),
            ("send_seal_digest", self.send_seal_digest),
            ("sam_canary_digest", self.sam_canary_digest),
            ("outbox_drain_digest", self.outbox_drain_digest),
            ("previous_entry_digest", self.previous_entry_digest),
            ("signer_public_key", self.signer_public_key),
        ):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if self.signature and len(self.signature) != 64:
            raise ValueError("signature must be empty or Ed25519-sized")

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"phase": self.phase.value,
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"payload": self.public_payload_digest,
            b"idem": self.idempotency_key,
            b"effect": self.public_effect_digest,
            b"send_seal": self.send_seal_digest,
            b"canary": self.sam_canary_digest,
            b"drain": self.outbox_drain_digest,
            b"seq": self.sequence,
            b"prev": self.previous_entry_digest,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"family": self.family_id,
            b"path_family": self.path_family,
            b"signer": self.signer_public_key,
        }

    def signature_payload(self) -> bytes:
        return EFFECT_LEDGER_DOMAIN + b":entry-sig:" + bencode(self.unsigned_bvalue())

    @property
    def core_digest(self) -> bytes:
        return sha256(EFFECT_LEDGER_DOMAIN + b":entry-core:" + bencode(self.unsigned_bvalue()))

    @property
    def entry_digest(self) -> bytes:
        return sha256(EFFECT_LEDGER_DOMAIN + b":entry-digest:" + self.signature_payload() + self.signature)

    def verifies(self) -> bool:
        return verify_signature(self.signer_public_key, self.signature_payload(), self.signature)

    def live(self, now: int) -> bool:
        return self.issued_at <= now < self.expires_at


def make_effect_ledger_entry(
    *,
    keypair: DhtKeypair,
    phase: EffectLedgerPhase,
    profile_id: str,
    service_name: str,
    scope_digest: bytes,
    request_digest: bytes,
    public_payload_digest: bytes,
    idempotency_key: bytes,
    public_effect_digest: bytes,
    send_seal: Any,
    sam_canary: Any,
    outbox_drain: Any,
    sequence: int,
    previous_entry_digest: bytes = ZERO_DIGEST,
    issued_at: int,
    expires_at: int,
    family_id: str,
    path_family: str,
) -> EffectLedgerEntry:
    unsigned = EffectLedgerEntry(
        phase=phase,
        profile_id=profile_id,
        service_name=service_name,
        scope_digest=scope_digest,
        request_digest=request_digest,
        public_payload_digest=public_payload_digest,
        idempotency_key=idempotency_key,
        public_effect_digest=public_effect_digest,
        send_seal_digest=_digest(send_seal),
        sam_canary_digest=_digest(sam_canary),
        outbox_drain_digest=_digest(outbox_drain),
        sequence=sequence,
        previous_entry_digest=previous_entry_digest,
        issued_at=issued_at,
        expires_at=expires_at,
        family_id=family_id,
        path_family=path_family,
        signer_public_key=keypair.public_key_bytes,
    )
    return replace(unsigned, signature=keypair.sign(unsigned.signature_payload()))


@dataclass(frozen=True)
class EffectLedgerReport:
    decision_kind: EffectLedgerDecisionKind
    accept: bool
    watch: bool
    reason: str
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    public_payload_digest: bytes
    idempotency_key: bytes
    public_effect_digest: bytes
    selected_phase: EffectLedgerPhase | None
    accepted_entry_digest: bytes
    entry_digests: tuple[bytes, ...]
    component_digests: tuple[bytes, ...]
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


def _digest(report: Any) -> bytes:
    for attr in ("report_digest", "seal_digest", "canary_digest", "accepted_canary_digest", "accepted_seal_digest", "accepted_receipt_digest", "entry_digest"):
        value = getattr(report, attr, None)
        if isinstance(value, bytes) and len(value) == 32:
            return value
    raise ValueError("component lacks 32-byte digest")


def _accept(report: Any) -> bool:
    return bool(getattr(report, "accept", False))


def _watch(report: Any) -> bool:
    return bool(getattr(report, "watch", False))


def _quarantined(report: Any) -> bool:
    return bool(getattr(report, "quarantined", False))


def _report(
    kind: EffectLedgerDecisionKind,
    accept: bool,
    watch: bool,
    reason: str,
    *,
    profile_id: str,
    service_name: str,
    scope_digest: bytes,
    request_digest: bytes,
    public_payload_digest: bytes,
    idempotency_key: bytes = ZERO_DIGEST,
    public_effect_digest: bytes = ZERO_DIGEST,
    selected: EffectLedgerEntry | None = None,
    entries: Iterable[EffectLedgerEntry] = (),
    components: Iterable[bytes] = (),
) -> EffectLedgerReport:
    entry_tuple = tuple(sorted(entries, key=lambda item: (item.sequence, PHASE_ORDER[item.phase], item.entry_digest)))
    digests = tuple(item.entry_digest for item in entry_tuple)
    families = len({item.family_id for item in entry_tuple})
    paths = len({item.path_family for item in entry_tuple})
    highest = selected.sequence if selected else max((item.sequence for item in entry_tuple), default=-1)
    phase = selected.phase if selected else None
    accepted = selected.entry_digest if selected and accept else ZERO_DIGEST
    idem = selected.idempotency_key if selected else idempotency_key
    effect = selected.public_effect_digest if selected else public_effect_digest
    component_tuple = tuple(sorted(set(components)))
    digest = sha256(EFFECT_LEDGER_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"reason": reason,
        b"profile": profile_id,
        b"service": service_name,
        b"scope": scope_digest,
        b"request": request_digest,
        b"payload": public_payload_digest,
        b"idem": idem,
        b"effect": effect,
        b"phase": phase.value if phase else b"",
        b"accepted": accepted,
        b"entries": list(digests),
        b"components": list(component_tuple),
        b"families": families,
        b"paths": paths,
        b"highest": highest,
    }))
    return EffectLedgerReport(kind, accept, watch, reason, profile_id, service_name, scope_digest, request_digest, public_payload_digest, idem, effect, phase, accepted, digests, component_tuple, families, paths, highest, digest)


def assess_effect_ledger(
    entries: Iterable[EffectLedgerEntry],
    *,
    send_seal: SendSealReport,
    sam_canary: Any,
    outbox_drain: Any,
    now: int,
    expected_profile_id: str,
    expected_service_name: str,
    expected_scope_digest: bytes,
    expected_request_digest: bytes,
    expected_public_payload_digest: bytes,
    expected_idempotency_key: bytes,
    expected_public_effect_digest: bytes,
    committed_idempotency_effects: Mapping[bytes, bytes] | None = None,
    last_sequence: int = -1,
    last_entry_digest: bytes = ZERO_DIGEST,
    min_family_diversity: int = 2,
    min_path_diversity: int = 2,
) -> EffectLedgerReport:
    components = (_digest(send_seal), _digest(sam_canary), _digest(outbox_drain))
    for report, hold, quarantine, label in (
        (send_seal, EffectLedgerDecisionKind.HOLD_SEND_SEAL, EffectLedgerDecisionKind.QUARANTINE_SEND_SEAL, "send seal"),
        (sam_canary, EffectLedgerDecisionKind.HOLD_SAM_CANARY, EffectLedgerDecisionKind.QUARANTINE_SAM_CANARY, "SAM canary"),
        (outbox_drain, EffectLedgerDecisionKind.HOLD_OUTBOX_DRAIN, EffectLedgerDecisionKind.QUARANTINE_OUTBOX_DRAIN, "outbox drain"),
    ):
        if _quarantined(report):
            return _report(quarantine, False, True, f"{label} quarantined", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, public_payload_digest=expected_public_payload_digest, idempotency_key=expected_idempotency_key, public_effect_digest=expected_public_effect_digest, components=components)
        if not _accept(report):
            return _report(hold, False, _watch(report), f"{label} did not accept", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, public_payload_digest=expected_public_payload_digest, idempotency_key=expected_idempotency_key, public_effect_digest=expected_public_effect_digest, components=components)
    entry_tuple = tuple(sorted(entries, key=lambda item: (item.sequence, PHASE_ORDER[item.phase], item.entry_digest)))
    if not entry_tuple:
        return _report(EffectLedgerDecisionKind.EMPTY_NO_ENTRIES, False, False, "no ledger entries", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, public_payload_digest=expected_public_payload_digest, idempotency_key=expected_idempotency_key, public_effect_digest=expected_public_effect_digest, components=components)
    seen_by_seq: dict[int, bytes] = {}
    previous_digest = last_entry_digest
    highest_phase_order = 0
    selected: EffectLedgerEntry | None = None
    for entry in entry_tuple:
        if not entry.verifies():
            return _report(EffectLedgerDecisionKind.QUARANTINE_BAD_SIGNATURE, False, True, "bad ledger signature", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, public_payload_digest=expected_public_payload_digest, entries=entry_tuple, components=components)
        if not entry.live(now):
            return _report(EffectLedgerDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, False, True, "ledger entry expired or future", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, public_payload_digest=expected_public_payload_digest, entries=entry_tuple, components=components)
        previous_core = seen_by_seq.get(entry.sequence)
        if previous_core and previous_core != entry.core_digest:
            return _report(EffectLedgerDecisionKind.QUARANTINE_SEQUENCE_FORK, False, True, "same-sequence ledger fork", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, public_payload_digest=expected_public_payload_digest, entries=entry_tuple, components=components)
        seen_by_seq[entry.sequence] = entry.core_digest
        if entry.sequence < last_sequence:
            return _report(EffectLedgerDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, True, "ledger sequence rollback", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, public_payload_digest=expected_public_payload_digest, entries=entry_tuple, components=components)
        if entry.sequence == last_sequence and entry.entry_digest == last_entry_digest:
            return _report(EffectLedgerDecisionKind.QUARANTINE_REPLAY, False, True, "ledger replay", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, public_payload_digest=expected_public_payload_digest, entries=entry_tuple, components=components)
        if previous_digest != ZERO_DIGEST and entry.previous_entry_digest != previous_digest:
            return _report(EffectLedgerDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, True, "ledger previous link mismatch", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, public_payload_digest=expected_public_payload_digest, entries=entry_tuple, components=components)
        if PHASE_ORDER[entry.phase] < highest_phase_order:
            return _report(EffectLedgerDecisionKind.QUARANTINE_PHASE_REGRESSION, False, True, "ledger phase regression", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, public_payload_digest=expected_public_payload_digest, entries=entry_tuple, components=components)
        highest_phase_order = PHASE_ORDER[entry.phase]
        if entry.profile_id != expected_profile_id:
            return _report(EffectLedgerDecisionKind.QUARANTINE_PROFILE_DRIFT, False, True, "profile drift", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, public_payload_digest=expected_public_payload_digest, entries=entry_tuple, components=components)
        if entry.service_name != expected_service_name:
            return _report(EffectLedgerDecisionKind.QUARANTINE_SERVICE_DRIFT, False, True, "service drift", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, public_payload_digest=expected_public_payload_digest, entries=entry_tuple, components=components)
        if entry.scope_digest != expected_scope_digest:
            return _report(EffectLedgerDecisionKind.QUARANTINE_SCOPE_DRIFT, False, True, "scope drift", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, public_payload_digest=expected_public_payload_digest, entries=entry_tuple, components=components)
        if entry.request_digest != expected_request_digest:
            return _report(EffectLedgerDecisionKind.QUARANTINE_REQUEST_DRIFT, False, True, "request drift", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, public_payload_digest=expected_public_payload_digest, entries=entry_tuple, components=components)
        if entry.public_payload_digest != expected_public_payload_digest:
            return _report(EffectLedgerDecisionKind.QUARANTINE_PAYLOAD_DRIFT, False, True, "payload drift", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, public_payload_digest=expected_public_payload_digest, entries=entry_tuple, components=components)
        if entry.idempotency_key != expected_idempotency_key:
            return _report(EffectLedgerDecisionKind.QUARANTINE_IDEMPOTENCY_CONFLICT, False, True, "idempotency drift", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, public_payload_digest=expected_public_payload_digest, entries=entry_tuple, components=components)
        if entry.public_effect_digest != expected_public_effect_digest:
            return _report(EffectLedgerDecisionKind.QUARANTINE_EFFECT_CONFLICT, False, True, "effect drift", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, public_payload_digest=expected_public_payload_digest, entries=entry_tuple, components=components)
        if entry.send_seal_digest != components[0] or entry.sam_canary_digest != components[1] or entry.outbox_drain_digest != components[2]:
            return _report(EffectLedgerDecisionKind.QUARANTINE_COMPONENT_DIGEST_DRIFT, False, True, "component digest drift", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, public_payload_digest=expected_public_payload_digest, entries=entry_tuple, components=components)
        committed = (committed_idempotency_effects or {}).get(entry.idempotency_key)
        if committed is not None and committed != entry.public_effect_digest:
            return _report(EffectLedgerDecisionKind.QUARANTINE_IDEMPOTENCY_CONFLICT, False, True, "known idempotency conflict", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, public_payload_digest=expected_public_payload_digest, entries=entry_tuple, components=components)
        previous_digest = entry.entry_digest
        selected = entry
    if len({entry.family_id for entry in entry_tuple}) < min_family_diversity:
        return _report(EffectLedgerDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, "ledger family diversity too low", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, public_payload_digest=expected_public_payload_digest, entries=entry_tuple, components=components)
    if len({entry.path_family for entry in entry_tuple}) < min_path_diversity:
        return _report(EffectLedgerDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, "ledger path diversity too low", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, public_payload_digest=expected_public_payload_digest, entries=entry_tuple, components=components)
    assert selected is not None
    if selected.phase is EffectLedgerPhase.COMMIT:
        return _report(EffectLedgerDecisionKind.ACCEPT_COMMITTED, True, False, "effect ledger committed at exact public edge", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, public_payload_digest=expected_public_payload_digest, selected=selected, entries=entry_tuple, components=components)
    if selected.phase is EffectLedgerPhase.ABORT:
        return _report(EffectLedgerDecisionKind.ACCEPT_ABORTED, True, True, "effect ledger aborted at exact public edge", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, public_payload_digest=expected_public_payload_digest, selected=selected, entries=entry_tuple, components=components)
    return _report(EffectLedgerDecisionKind.HOLD_NOT_COMMITTED if selected.phase is EffectLedgerPhase.SEND_SHADOW else EffectLedgerDecisionKind.ACCEPT_PREPARED_WITH_WATCH, selected.phase is EffectLedgerPhase.PREPARE, True, "effect ledger has not reached commit", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, public_payload_digest=expected_public_payload_digest, selected=selected, entries=entry_tuple, components=components)
