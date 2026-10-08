"""Effect-seal join after restart replay, quench, journal, and fuzz evidence.

rev0055 adds a final no-network seal before a handler or public-edge side effect
can become sticky after restart.  The seal joins handler replay, handler quench,
side-effect journal, restart-chaos cuts, fuzz-ledger persistence, and fuzz-shrink
coverage at one exact scope/request/payload/idempotency boundary.  It is a local
receipt, not a live network write and not production persistence.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Any, Iterable

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectAction, SideEffectPhase

EFFECT_SEAL_DOMAIN = DOMAIN + b":effect-seal-v1:"


class EffectSealDecisionKind(str, Enum):
    ACCEPT_EFFECT_COMMITTED = "accept_effect_committed"
    ACCEPT_EFFECT_ABORTED = "accept_effect_aborted"
    ACCEPT_WITH_WATCH = "accept_with_watch"
    EMPTY_NO_SEALS = "empty_no_seals"
    HOLD_COMPONENT_WATCH = "hold_component_watch"
    HOLD_PREPARE_ONLY = "hold_prepare_only"
    HOLD_QUENCH_COOLDOWN = "hold_quench_cooldown"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    QUARANTINE_COMPONENT_NOT_ACCEPTED = "quarantine_component_not_accepted"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_EXPIRED_OR_FUTURE = "quarantine_expired_or_future"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_PROFILE_DRIFT = "quarantine_profile_drift"
    QUARANTINE_SERVICE_DRIFT = "quarantine_service_drift"
    QUARANTINE_ACTION_DRIFT = "quarantine_action_drift"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_REQUEST_DRIFT = "quarantine_request_drift"
    QUARANTINE_PAYLOAD_DRIFT = "quarantine_payload_drift"
    QUARANTINE_IDEMPOTENCY_DRIFT = "quarantine_idempotency_drift"
    QUARANTINE_COMPONENT_DIGEST_DRIFT = "quarantine_component_digest_drift"
    QUARANTINE_PHASE_DRIFT = "quarantine_phase_drift"
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"


@dataclass(frozen=True)
class EffectSealCapsule:
    action: SideEffectAction
    final_phase: SideEffectPhase
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    handler_replay_digest: bytes
    handler_quench_digest: bytes
    side_effect_journal_digest: bytes
    restart_chaos_digest: bytes
    fuzz_ledger_digest: bytes
    fuzz_shrink_digest: bytes
    hard_negative_count: int
    sequence: int
    previous_seal_digest: bytes
    issued_at: int
    expires_at: int
    family_id: str
    path_family: str
    signer_public_key: bytes
    signature: bytes = b""

    def __post_init__(self) -> None:
        object.__setattr__(self, "action", SideEffectAction(self.action))
        object.__setattr__(self, "final_phase", SideEffectPhase(self.final_phase))
        if not self.profile_id or not self.service_name or not self.family_id or not self.path_family:
            raise ValueError("effect seal requires profile/service/family/path")
        if self.sequence < 0 or self.hard_negative_count < 0:
            raise ValueError("sequence and hard_negative_count must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("expires_at must follow issued_at")
        for name, value in (
            ("scope_digest", self.scope_digest),
            ("request_digest", self.request_digest),
            ("payload_digest", self.payload_digest),
            ("idempotency_key", self.idempotency_key),
            ("handler_replay_digest", self.handler_replay_digest),
            ("handler_quench_digest", self.handler_quench_digest),
            ("side_effect_journal_digest", self.side_effect_journal_digest),
            ("restart_chaos_digest", self.restart_chaos_digest),
            ("fuzz_ledger_digest", self.fuzz_ledger_digest),
            ("fuzz_shrink_digest", self.fuzz_shrink_digest),
            ("previous_seal_digest", self.previous_seal_digest),
            ("signer_public_key", self.signer_public_key),
        ):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if self.signature and len(self.signature) != 64:
            raise ValueError("signature must be empty or Ed25519-sized")

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"action": self.action.value,
            b"phase": self.final_phase.value,
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"payload": self.payload_digest,
            b"idem": self.idempotency_key,
            b"handler_replay": self.handler_replay_digest,
            b"handler_quench": self.handler_quench_digest,
            b"journal": self.side_effect_journal_digest,
            b"restart": self.restart_chaos_digest,
            b"fuzz_ledger": self.fuzz_ledger_digest,
            b"fuzz_shrink": self.fuzz_shrink_digest,
            b"hard": self.hard_negative_count,
            b"seq": self.sequence,
            b"prev": self.previous_seal_digest,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"family": self.family_id,
            b"path_family": self.path_family,
            b"signer": self.signer_public_key,
        }

    def signature_payload(self) -> bytes:
        return EFFECT_SEAL_DOMAIN + b":seal-sig:" + bencode(self.unsigned_bvalue())

    @property
    def seal_core_digest(self) -> bytes:
        return sha256(EFFECT_SEAL_DOMAIN + b":seal-core:" + bencode(self.unsigned_bvalue()))

    @property
    def seal_digest(self) -> bytes:
        return sha256(EFFECT_SEAL_DOMAIN + b":seal-digest:" + self.signature_payload() + self.signature)

    def verifies(self) -> bool:
        return verify_signature(self.signer_public_key, self.signature_payload(), self.signature)

    def live(self, now: int) -> bool:
        return self.issued_at <= now < self.expires_at


@dataclass(frozen=True)
class EffectSealReport:
    decision_kind: EffectSealDecisionKind
    accept: bool
    watch: bool
    reason: str
    action: SideEffectAction
    final_phase: SideEffectPhase | None
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    accepted_seal_digest: bytes
    seal_digests: tuple[bytes, ...]
    component_digests: tuple[bytes, ...]
    highest_sequence: int
    family_count: int
    path_family_count: int
    hard_negative_count: int
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _digest(report: Any | None) -> bytes:
    if report is None:
        return ZERO_DIGEST
    for attr in ("report_digest", "transcript_digest", "canary_digest"):
        value = getattr(report, attr, None)
        if isinstance(value, bytes) and len(value) == 32:
            return value
    raise ValueError("component lacks 32-byte digest")


def _accept(report: Any | None) -> bool:
    return bool(getattr(report, "accept", False)) if report is not None else False


def _watch(report: Any | None) -> bool:
    return bool(getattr(report, "watch", False)) if report is not None else False


def _quarantined(report: Any | None) -> bool:
    return bool(getattr(report, "quarantined", False)) if report is not None else False


def make_effect_seal_capsule(
    *,
    keypair: DhtKeypair,
    side_effect_journal_report: Any,
    handler_replay_report: Any,
    handler_quench_report: Any,
    restart_chaos_report: Any,
    fuzz_ledger_report: Any,
    fuzz_shrink_report: Any,
    sequence: int,
    previous_seal_digest: bytes = ZERO_DIGEST,
    issued_at: int,
    expires_at: int,
    hard_negative_count: int = 0,
    family_id: str,
    path_family: str,
) -> EffectSealCapsule:
    phase = getattr(side_effect_journal_report, "final_phase", None)
    if phase is None:
        phase = SideEffectPhase.PREPARE
    unsigned = EffectSealCapsule(
        action=getattr(side_effect_journal_report, "action"),
        final_phase=phase,
        profile_id=getattr(side_effect_journal_report, "profile_id"),
        service_name=getattr(side_effect_journal_report, "service_name"),
        scope_digest=getattr(side_effect_journal_report, "scope_digest"),
        request_digest=getattr(side_effect_journal_report, "request_digest"),
        payload_digest=getattr(side_effect_journal_report, "payload_digest"),
        idempotency_key=getattr(side_effect_journal_report, "idempotency_key"),
        handler_replay_digest=_digest(handler_replay_report),
        handler_quench_digest=_digest(handler_quench_report),
        side_effect_journal_digest=_digest(side_effect_journal_report),
        restart_chaos_digest=_digest(restart_chaos_report),
        fuzz_ledger_digest=_digest(fuzz_ledger_report),
        fuzz_shrink_digest=_digest(fuzz_shrink_report),
        hard_negative_count=hard_negative_count,
        sequence=sequence,
        previous_seal_digest=previous_seal_digest,
        issued_at=issued_at,
        expires_at=expires_at,
        family_id=family_id,
        path_family=path_family,
        signer_public_key=keypair.public_key_bytes,
    )
    return replace(unsigned, signature=keypair.sign(unsigned.signature_payload()))


def assess_effect_seal(
    seals: Iterable[EffectSealCapsule],
    *,
    handler_replay_report: Any,
    handler_quench_report: Any,
    side_effect_journal_report: Any,
    restart_chaos_report: Any,
    fuzz_ledger_report: Any,
    fuzz_shrink_report: Any,
    now: int,
    previous_seen_seal_digests: Iterable[bytes] = (),
    highest_seen_sequence: int | None = None,
    allow_component_watch: bool = False,
    min_family_count: int = 2,
    min_path_family_count: int = 2,
) -> EffectSealReport:
    seal_t = tuple(seals)
    action = SideEffectAction(getattr(side_effect_journal_report, "action"))
    phase_raw = getattr(side_effect_journal_report, "final_phase", None)
    final_phase = SideEffectPhase(phase_raw) if phase_raw is not None else None
    profile_id = getattr(side_effect_journal_report, "profile_id")
    service_name = getattr(side_effect_journal_report, "service_name")
    scope_digest = getattr(side_effect_journal_report, "scope_digest")
    request_digest = getattr(side_effect_journal_report, "request_digest")
    payload_digest = getattr(side_effect_journal_report, "payload_digest")
    idempotency_key = getattr(side_effect_journal_report, "idempotency_key")
    components = (handler_replay_report, handler_quench_report, side_effect_journal_report, restart_chaos_report, fuzz_ledger_report, fuzz_shrink_report)
    component_digests = tuple(_digest(component) for component in components)
    common = dict(action=action, final_phase=final_phase, profile_id=profile_id, service_name=service_name, scope_digest=scope_digest, request_digest=request_digest, payload_digest=payload_digest, idempotency_key=idempotency_key, component_digests=component_digests)
    if not seal_t:
        return _report(EffectSealDecisionKind.EMPTY_NO_SEALS, False, False, "effect seal needs capsules", seals=seal_t, **common)
    for component in components:
        if not _accept(component) or _quarantined(component):
            return _report(EffectSealDecisionKind.QUARANTINE_COMPONENT_NOT_ACCEPTED, False, False, "component did not accept", seals=seal_t, **common)
    if final_phase is SideEffectPhase.PREPARE:
        return _report(EffectSealDecisionKind.HOLD_PREPARE_ONLY, False, True, "prepared side effect cannot be effect-sealed", seals=seal_t, **common)
    if getattr(handler_quench_report, "cooldown_until", 0) > now:
        return _report(EffectSealDecisionKind.HOLD_QUENCH_COOLDOWN, False, True, "handler quench cooldown still active", seals=seal_t, **common)
    if any(_watch(component) for component in components) and not allow_component_watch:
        return _report(EffectSealDecisionKind.HOLD_COMPONENT_WATCH, False, True, "component watch pressure must be carried into seal", seals=seal_t, **common)
    restart_phase = getattr(restart_chaos_report, "final_phase", None)
    if restart_phase is not None and final_phase is not None and SideEffectPhase(restart_phase) is not final_phase:
        return _report(EffectSealDecisionKind.QUARANTINE_PHASE_DRIFT, False, False, "restart chaos phase and journal phase disagree", seals=seal_t, **common)

    seen = set(previous_seen_seal_digests)
    by_sequence: dict[int, EffectSealCapsule] = {}
    for seal in seal_t:
        if not seal.verifies():
            return _report(EffectSealDecisionKind.QUARANTINE_BAD_SIGNATURE, False, False, "bad effect-seal signature", seals=seal_t, **common)
        if not seal.live(now):
            return _report(EffectSealDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, False, False, "expired or future effect seal", seals=seal_t, **common)
        if seal.seal_digest in seen:
            return _report(EffectSealDecisionKind.QUARANTINE_REPLAY, False, False, "replayed effect seal", seals=seal_t, **common)
        if highest_seen_sequence is not None and seal.sequence < highest_seen_sequence:
            return _report(EffectSealDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, False, "effect-seal sequence rollback", seals=seal_t, **common)
        prior = by_sequence.get(seal.sequence)
        if prior is not None and prior.seal_core_digest != seal.seal_core_digest:
            return _report(EffectSealDecisionKind.QUARANTINE_SEQUENCE_FORK, False, False, "same-sequence effect-seal fork", seals=seal_t, **common)
        by_sequence[seal.sequence] = seal
        if seal.profile_id != profile_id:
            return _report(EffectSealDecisionKind.QUARANTINE_PROFILE_DRIFT, False, False, "profile drift", seals=seal_t, **common)
        if seal.service_name != service_name:
            return _report(EffectSealDecisionKind.QUARANTINE_SERVICE_DRIFT, False, False, "service drift", seals=seal_t, **common)
        if seal.action is not action:
            return _report(EffectSealDecisionKind.QUARANTINE_ACTION_DRIFT, False, False, "action drift", seals=seal_t, **common)
        if final_phase is not None and seal.final_phase is not final_phase:
            return _report(EffectSealDecisionKind.QUARANTINE_PHASE_DRIFT, False, False, "seal phase drift", seals=seal_t, **common)
        if seal.scope_digest != scope_digest:
            return _report(EffectSealDecisionKind.QUARANTINE_SCOPE_DRIFT, False, False, "scope drift", seals=seal_t, **common)
        if seal.request_digest != request_digest:
            return _report(EffectSealDecisionKind.QUARANTINE_REQUEST_DRIFT, False, False, "request drift", seals=seal_t, **common)
        if seal.payload_digest != payload_digest:
            return _report(EffectSealDecisionKind.QUARANTINE_PAYLOAD_DRIFT, False, False, "payload drift", seals=seal_t, **common)
        if seal.idempotency_key != idempotency_key:
            return _report(EffectSealDecisionKind.QUARANTINE_IDEMPOTENCY_DRIFT, False, False, "idempotency drift", seals=seal_t, **common)
        if (seal.handler_replay_digest, seal.handler_quench_digest, seal.side_effect_journal_digest, seal.restart_chaos_digest, seal.fuzz_ledger_digest, seal.fuzz_shrink_digest) != component_digests:
            return _report(EffectSealDecisionKind.QUARANTINE_COMPONENT_DIGEST_DRIFT, False, False, "effect-seal component digest drift", seals=seal_t, **common)
        if seal.hard_negative_count:
            return _report(EffectSealDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, "hard negatives block effect seal", seals=seal_t, **common)
    ordered = sorted(by_sequence.values(), key=lambda item: item.sequence)
    for left, right in zip(ordered, ordered[1:]):
        if right.sequence == left.sequence + 1 and right.previous_seal_digest != left.seal_digest:
            return _report(EffectSealDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, False, "effect-seal previous-link mismatch", seals=seal_t, **common)
    families = {seal.family_id for seal in seal_t}
    paths = {seal.path_family for seal in seal_t}
    if len(families) < min_family_count:
        return _report(EffectSealDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, "effect seal needs family diversity", seals=seal_t, **common)
    if len(paths) < min_path_family_count:
        return _report(EffectSealDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, "effect seal needs path diversity", seals=seal_t, **common)
    accepted = ordered[-1]
    if any(_watch(component) for component in components):
        return _report(EffectSealDecisionKind.ACCEPT_WITH_WATCH, True, True, "effect seal accepted with watch", seals=seal_t, accepted=accepted, **common)
    if final_phase is SideEffectPhase.ABORT:
        return _report(EffectSealDecisionKind.ACCEPT_EFFECT_ABORTED, True, False, "effect seal accepted aborted effect", seals=seal_t, accepted=accepted, **common)
    return _report(EffectSealDecisionKind.ACCEPT_EFFECT_COMMITTED, True, False, "effect seal accepted committed effect", seals=seal_t, accepted=accepted, **common)


def _report(kind: EffectSealDecisionKind, accept: bool, watch: bool, reason: str, *, action: SideEffectAction, final_phase: SideEffectPhase | None, profile_id: str, service_name: str, scope_digest: bytes, request_digest: bytes, payload_digest: bytes, idempotency_key: bytes, component_digests: tuple[bytes, ...], seals: Iterable[EffectSealCapsule], accepted: EffectSealCapsule | None = None) -> EffectSealReport:
    seal_t = tuple(seals)
    digests = tuple(seal.seal_digest for seal in seal_t)
    highest = max((seal.sequence for seal in seal_t), default=-1)
    families = {seal.family_id for seal in seal_t}
    paths = {seal.path_family for seal in seal_t}
    hard = sum(seal.hard_negative_count for seal in seal_t)
    accepted_digest = accepted.seal_digest if accepted else ZERO_DIGEST
    digest = sha256(EFFECT_SEAL_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"reason": reason,
        b"action": action.value,
        b"phase": final_phase.value if final_phase else "none",
        b"profile": profile_id,
        b"service": service_name,
        b"scope": scope_digest,
        b"request": request_digest,
        b"payload": payload_digest,
        b"idem": idempotency_key,
        b"accepted": accepted_digest,
        b"seals": list(digests),
        b"components": list(component_digests),
        b"highest": highest,
        b"families": len(families),
        b"paths": len(paths),
        b"hard": hard,
    }))
    return EffectSealReport(kind, accept, watch, reason, action, final_phase, profile_id, service_name, scope_digest, request_digest, payload_digest, idempotency_key, accepted_digest, digests, component_digests, highest, len(families), len(paths), hard, digest)
