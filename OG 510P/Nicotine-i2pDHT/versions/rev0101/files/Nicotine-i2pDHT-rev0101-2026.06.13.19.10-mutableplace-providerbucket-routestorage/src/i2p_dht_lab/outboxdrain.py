"""No-network outbox drain and commit receipts before public publication.

rev0049 staged public bridge side effects in a durable outbox and dry-ran the
publication boundary.  rev0050 adds the next seam: draining the outbox must not
be confused with committing a network write.  A drain receipt binds the accepted
outbox report, publish dry-run, SAM trace, scope journal, idempotency key, and
exact profile/service/scope/request/payload before a future live writer exists.

This module deliberately does not send anything and does not claim exactly-once
network semantics.  It pins local replay/fork/idempotency pressure first.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Any, Iterable

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .publicoutbox import PublicOutboxAction, PublicOutboxReport

OUTBOX_DRAIN_DOMAIN = DOMAIN + b":outbox-drain-v1:"


class OutboxDrainPhase(str, Enum):
    PREPARE = "prepare"
    COMMIT = "commit"


class OutboxDrainAction(str, Enum):
    DRAIN_REFRESH = "drain_refresh"
    DRAIN_WITHDRAW = "drain_withdraw"
    DRAIN_REPAIR = "drain_repair"


OUTBOX_TO_DRAIN_ACTION = {
    PublicOutboxAction.QUEUE_REFRESH: OutboxDrainAction.DRAIN_REFRESH,
    PublicOutboxAction.QUEUE_WITHDRAW: OutboxDrainAction.DRAIN_WITHDRAW,
    PublicOutboxAction.QUEUE_REPAIR: OutboxDrainAction.DRAIN_REPAIR,
}


class OutboxDrainDecisionKind(str, Enum):
    ACCEPT_PREPARED_DRAIN = "accept_prepared_drain"
    ACCEPT_COMMIT_RECEIPT = "accept_commit_receipt"
    ACCEPT_IDEMPOTENT_COMMIT_REPLAY = "accept_idempotent_commit_replay"
    ACCEPT_WITH_WATCH = "accept_with_watch"
    HOLD_OUTBOX = "hold_outbox"
    HOLD_DRY_RUN = "hold_dry_run"
    HOLD_SAM_TRACE = "hold_sam_trace"
    HOLD_SCOPE_JOURNAL = "hold_scope_journal"
    HOLD_COMPONENT_WATCH = "hold_component_watch"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    EMPTY_NO_RECEIPTS = "empty_no_receipts"
    QUARANTINE_OUTBOX = "quarantine_outbox"
    QUARANTINE_DRY_RUN = "quarantine_dry_run"
    QUARANTINE_SAM_TRACE = "quarantine_sam_trace"
    QUARANTINE_SCOPE_JOURNAL = "quarantine_scope_journal"
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
    QUARANTINE_PAYLOAD_DRIFT = "quarantine_payload_drift"
    QUARANTINE_ACTION_DRIFT = "quarantine_action_drift"
    QUARANTINE_COMPONENT_DIGEST_DRIFT = "quarantine_component_digest_drift"
    QUARANTINE_IDEMPOTENCY_CONFLICT = "quarantine_idempotency_conflict"
    QUARANTINE_PHASE_REGRESSION = "quarantine_phase_regression"


@dataclass(frozen=True)
class OutboxDrainReceipt:
    phase: OutboxDrainPhase
    action: OutboxDrainAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    outbox_report_digest: bytes
    outbox_entry_digest: bytes
    dry_run_report_digest: bytes
    sam_trace_digest: bytes
    scope_journal_digest: bytes
    idempotency_key: bytes
    drain_effect_digest: bytes
    sequence: int
    previous_receipt_digest: bytes
    issued_at: int
    expires_at: int
    family_id: str
    path_family: str
    signer_public_key: bytes
    signature: bytes = b""

    def __post_init__(self) -> None:
        object.__setattr__(self, "phase", OutboxDrainPhase(self.phase))
        object.__setattr__(self, "action", OutboxDrainAction(self.action))
        if not self.profile_id or not self.service_name or not self.family_id or not self.path_family:
            raise ValueError("outbox drain receipt needs profile/service/family/path")
        if self.sequence < 0:
            raise ValueError("sequence must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("expires_at must follow issued_at")
        for name, value in (
            ("scope_digest", self.scope_digest),
            ("request_digest", self.request_digest),
            ("payload_digest", self.payload_digest),
            ("outbox_report_digest", self.outbox_report_digest),
            ("outbox_entry_digest", self.outbox_entry_digest),
            ("dry_run_report_digest", self.dry_run_report_digest),
            ("sam_trace_digest", self.sam_trace_digest),
            ("scope_journal_digest", self.scope_journal_digest),
            ("idempotency_key", self.idempotency_key),
            ("drain_effect_digest", self.drain_effect_digest),
            ("previous_receipt_digest", self.previous_receipt_digest),
            ("signer_public_key", self.signer_public_key),
        ):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if self.signature and len(self.signature) != 64:
            raise ValueError("signature must be empty or Ed25519-sized")

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"phase": self.phase.value,
            b"action": self.action.value,
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"payload": self.payload_digest,
            b"outbox_report": self.outbox_report_digest,
            b"outbox_entry": self.outbox_entry_digest,
            b"dry_run": self.dry_run_report_digest,
            b"sam_trace": self.sam_trace_digest,
            b"journal": self.scope_journal_digest,
            b"idem": self.idempotency_key,
            b"effect": self.drain_effect_digest,
            b"seq": self.sequence,
            b"prev": self.previous_receipt_digest,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"family": self.family_id,
            b"path_family": self.path_family,
            b"signer": self.signer_public_key,
        }

    def signature_payload(self) -> bytes:
        return OUTBOX_DRAIN_DOMAIN + b":receipt-sig:" + bencode(self.unsigned_bvalue())

    @property
    def receipt_core_digest(self) -> bytes:
        return sha256(OUTBOX_DRAIN_DOMAIN + b":receipt-core:" + bencode(self.unsigned_bvalue()))

    @property
    def receipt_digest(self) -> bytes:
        return sha256(OUTBOX_DRAIN_DOMAIN + b":receipt-digest:" + self.signature_payload() + self.signature)

    def verifies(self) -> bool:
        return verify_signature(self.signer_public_key, self.signature_payload(), self.signature)

    def live(self, now: int) -> bool:
        return self.issued_at <= now < self.expires_at


@dataclass(frozen=True)
class OutboxDrainReport:
    decision_kind: OutboxDrainDecisionKind
    accept: bool
    watch: bool
    reason: str
    profile_id: str
    service_name: str
    action: OutboxDrainAction
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    accepted_receipt_digest: bytes
    idempotency_key: bytes
    drain_effect_digest: bytes
    receipt_digests: tuple[bytes, ...]
    component_digests: tuple[bytes, ...]
    family_count: int
    path_family_count: int
    highest_sequence: int
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _component_digest(report: Any) -> bytes:
    for attr in ("report_digest", "transcript_digest"):
        value = getattr(report, attr, None)
        if isinstance(value, bytes) and len(value) == 32:
            return value
    raise ValueError("component report lacks 32-byte digest")


def _component_accept(report: Any) -> bool:
    return bool(getattr(report, "accept", False))


def _component_watch(report: Any) -> bool:
    return bool(getattr(report, "watch", False))


def _component_quarantined(report: Any) -> bool:
    return bool(getattr(report, "quarantined", False))


def make_outbox_drain_receipt(
    *,
    keypair: DhtKeypair,
    phase: OutboxDrainPhase,
    action: OutboxDrainAction,
    profile_id: str,
    service_name: str,
    scope_digest: bytes,
    request_digest: bytes,
    payload_digest: bytes,
    outbox_report_digest: bytes,
    outbox_entry_digest: bytes,
    dry_run_report_digest: bytes,
    sam_trace_digest: bytes,
    scope_journal_digest: bytes,
    idempotency_key: bytes,
    drain_effect_digest: bytes,
    sequence: int,
    previous_receipt_digest: bytes = ZERO_DIGEST,
    issued_at: int,
    expires_at: int,
    family_id: str,
    path_family: str,
) -> OutboxDrainReceipt:
    receipt = OutboxDrainReceipt(
        phase,
        action,
        profile_id,
        service_name,
        scope_digest,
        request_digest,
        payload_digest,
        outbox_report_digest,
        outbox_entry_digest,
        dry_run_report_digest,
        sam_trace_digest,
        scope_journal_digest,
        idempotency_key,
        drain_effect_digest,
        sequence,
        previous_receipt_digest,
        issued_at,
        expires_at,
        family_id,
        path_family,
        keypair.public_key_bytes,
    )
    return replace(receipt, signature=keypair.sign(receipt.signature_payload()))


def _report(
    kind: OutboxDrainDecisionKind,
    accept: bool,
    watch: bool,
    reason: str,
    *,
    profile_id: str,
    service_name: str,
    action: OutboxDrainAction,
    scope_digest: bytes,
    request_digest: bytes,
    payload_digest: bytes,
    receipts: Iterable[OutboxDrainReceipt] = (),
    selected: OutboxDrainReceipt | None = None,
    components: Iterable[bytes] = (),
    idempotency_key: bytes = ZERO_DIGEST,
    drain_effect_digest: bytes = ZERO_DIGEST,
) -> OutboxDrainReport:
    receipt_tuple = tuple(sorted(receipts, key=lambda item: (item.sequence, item.receipt_digest)))
    receipt_digests = tuple(item.receipt_digest for item in receipt_tuple)
    component_digests = tuple(sorted(set(components)))
    families = len({item.family_id for item in receipt_tuple})
    paths = len({item.path_family for item in receipt_tuple})
    highest = selected.sequence if selected else max((item.sequence for item in receipt_tuple), default=-1)
    accepted = selected.receipt_digest if selected and accept else ZERO_DIGEST
    if selected is not None:
        idempotency_key = selected.idempotency_key
        drain_effect_digest = selected.drain_effect_digest
    digest = sha256(OUTBOX_DRAIN_DOMAIN + b":report:" + bencode({
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
        b"effect": drain_effect_digest,
        b"receipts": list(receipt_digests),
        b"components": list(component_digests),
        b"families": families,
        b"paths": paths,
        b"highest": highest,
    }))
    return OutboxDrainReport(kind, accept, watch, reason, profile_id, service_name, action, scope_digest, request_digest, payload_digest, accepted, idempotency_key, drain_effect_digest, receipt_digests, component_digests, families, paths, highest, digest)


def assess_outbox_drain(
    receipts: Iterable[OutboxDrainReceipt],
    *,
    outbox_report: PublicOutboxReport,
    dry_run_report: Any,
    sam_trace_report: Any,
    scope_journal_report: Any,
    now: int,
    expected_profile_id: str,
    expected_service_name: str,
    expected_scope_digest: bytes,
    expected_request_digest: bytes,
    expected_payload_digest: bytes,
    expected_action: OutboxDrainAction | None = None,
    previous_highest_sequence: int = -1,
    previous_receipt_digest: bytes = ZERO_DIGEST,
    previously_seen_receipts: Iterable[bytes] = (),
    previously_committed_idempotency: Iterable[bytes] = (),
    committed_idempotency_effects: dict[bytes, bytes] | None = None,
    min_family_diversity: int = 2,
    min_path_diversity: int = 2,
    allow_component_watch: bool = False,
) -> OutboxDrainReport:
    expected_action = expected_action or OUTBOX_TO_DRAIN_ACTION.get(outbox_report.action, OutboxDrainAction.DRAIN_REFRESH)
    components = (
        outbox_report.report_digest,
        _component_digest(dry_run_report),
        _component_digest(sam_trace_report),
        _component_digest(scope_journal_report),
    )

    def make_report(kind: OutboxDrainDecisionKind, accept: bool, watch: bool, reason: str, *, selected: OutboxDrainReceipt | None = None, candidate_receipts: Iterable[OutboxDrainReceipt] = ()) -> OutboxDrainReport:
        return _report(kind, accept, watch, reason, profile_id=expected_profile_id, service_name=expected_service_name, action=expected_action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, payload_digest=expected_payload_digest, receipts=candidate_receipts, selected=selected, components=components)

    component_checks = (
        (outbox_report, OutboxDrainDecisionKind.HOLD_OUTBOX, OutboxDrainDecisionKind.QUARANTINE_OUTBOX, "outbox"),
        (dry_run_report, OutboxDrainDecisionKind.HOLD_DRY_RUN, OutboxDrainDecisionKind.QUARANTINE_DRY_RUN, "dry-run"),
        (sam_trace_report, OutboxDrainDecisionKind.HOLD_SAM_TRACE, OutboxDrainDecisionKind.QUARANTINE_SAM_TRACE, "SAM trace"),
        (scope_journal_report, OutboxDrainDecisionKind.HOLD_SCOPE_JOURNAL, OutboxDrainDecisionKind.QUARANTINE_SCOPE_JOURNAL, "scope journal"),
    )
    for component, hold_kind, quarantine_kind, label in component_checks:
        if _component_quarantined(component):
            return make_report(quarantine_kind, False, True, f"{label} quarantined")
        if not _component_accept(component):
            return make_report(hold_kind, False, _component_watch(component), f"{label} did not accept")
    if any(_component_watch(component) for component, *_ in component_checks) and not allow_component_watch:
        return make_report(OutboxDrainDecisionKind.HOLD_COMPONENT_WATCH, False, True, "component watch debt must be explicitly carried into drain")

    receipt_tuple = tuple(sorted(receipts, key=lambda item: (item.sequence, item.receipt_digest)))
    if not receipt_tuple:
        return make_report(OutboxDrainDecisionKind.EMPTY_NO_RECEIPTS, False, True, "no drain receipts supplied")

    seen = set(previously_seen_receipts)
    committed_effects = committed_idempotency_effects or {}
    committed_ids = set(previously_committed_idempotency) | set(committed_effects)
    core_by_seq: dict[int, bytes] = {}
    idem_to_effect: dict[bytes, bytes] = {}
    phases_by_seq: dict[int, OutboxDrainPhase] = {}
    for receipt in receipt_tuple:
        if not receipt.verifies():
            return make_report(OutboxDrainDecisionKind.QUARANTINE_BAD_SIGNATURE, False, True, "drain receipt signature failed", candidate_receipts=receipt_tuple)
        if not receipt.live(now):
            return make_report(OutboxDrainDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, False, True, "drain receipt expired or future", candidate_receipts=receipt_tuple)
        if receipt.receipt_digest in seen:
            return make_report(OutboxDrainDecisionKind.QUARANTINE_REPLAY, False, True, "drain receipt replay", candidate_receipts=receipt_tuple)
        if receipt.sequence <= previous_highest_sequence:
            return make_report(OutboxDrainDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, True, "drain receipt sequence rollback", candidate_receipts=receipt_tuple)
        if previous_highest_sequence >= 0 and receipt.previous_receipt_digest != previous_receipt_digest:
            return make_report(OutboxDrainDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, True, "drain previous digest mismatch", candidate_receipts=receipt_tuple)
        if receipt.profile_id != expected_profile_id:
            return make_report(OutboxDrainDecisionKind.QUARANTINE_PROFILE_DRIFT, False, True, "drain profile drift", candidate_receipts=receipt_tuple)
        if receipt.service_name != expected_service_name:
            return make_report(OutboxDrainDecisionKind.QUARANTINE_SERVICE_DRIFT, False, True, "drain service drift", candidate_receipts=receipt_tuple)
        if receipt.scope_digest != expected_scope_digest:
            return make_report(OutboxDrainDecisionKind.QUARANTINE_SCOPE_DRIFT, False, True, "drain scope drift", candidate_receipts=receipt_tuple)
        if receipt.request_digest != expected_request_digest:
            return make_report(OutboxDrainDecisionKind.QUARANTINE_REQUEST_DRIFT, False, True, "drain request drift", candidate_receipts=receipt_tuple)
        if receipt.payload_digest != expected_payload_digest:
            return make_report(OutboxDrainDecisionKind.QUARANTINE_PAYLOAD_DRIFT, False, True, "drain payload drift", candidate_receipts=receipt_tuple)
        if receipt.action is not expected_action:
            return make_report(OutboxDrainDecisionKind.QUARANTINE_ACTION_DRIFT, False, True, "drain action drift", candidate_receipts=receipt_tuple)
        if receipt.outbox_report_digest != outbox_report.report_digest or receipt.outbox_entry_digest != outbox_report.accepted_entry_digest or receipt.dry_run_report_digest != _component_digest(dry_run_report) or receipt.sam_trace_digest != _component_digest(sam_trace_report) or receipt.scope_journal_digest != _component_digest(scope_journal_report):
            return make_report(OutboxDrainDecisionKind.QUARANTINE_COMPONENT_DIGEST_DRIFT, False, True, "drain component digest drift", candidate_receipts=receipt_tuple)
        if receipt.idempotency_key != outbox_report.idempotency_key:
            return make_report(OutboxDrainDecisionKind.QUARANTINE_IDEMPOTENCY_CONFLICT, False, True, "drain idempotency key drift", candidate_receipts=receipt_tuple)
        prior_core = core_by_seq.setdefault(receipt.sequence, receipt.receipt_core_digest)
        if prior_core != receipt.receipt_core_digest:
            return make_report(OutboxDrainDecisionKind.QUARANTINE_SEQUENCE_FORK, False, True, "same-sequence drain fork", candidate_receipts=receipt_tuple)
        prior_effect = idem_to_effect.setdefault(receipt.idempotency_key, receipt.drain_effect_digest)
        if prior_effect != receipt.drain_effect_digest:
            return make_report(OutboxDrainDecisionKind.QUARANTINE_IDEMPOTENCY_CONFLICT, False, True, "same idempotency key maps to different drain effect", candidate_receipts=receipt_tuple)
        committed_effect = committed_effects.get(receipt.idempotency_key)
        if committed_effect is not None and committed_effect != receipt.drain_effect_digest:
            return make_report(OutboxDrainDecisionKind.QUARANTINE_IDEMPOTENCY_CONFLICT, False, True, "committed idempotency maps to different effect", candidate_receipts=receipt_tuple)
        old_phase = phases_by_seq.setdefault(receipt.sequence, receipt.phase)
        if old_phase is not receipt.phase:
            return make_report(OutboxDrainDecisionKind.QUARANTINE_PHASE_REGRESSION, False, True, "same sequence carries both prepare and commit phases", candidate_receipts=receipt_tuple)

    newest = max(receipt_tuple, key=lambda item: (item.sequence, item.receipt_digest))
    if newest.idempotency_key in committed_ids:
        return make_report(OutboxDrainDecisionKind.ACCEPT_IDEMPOTENT_COMMIT_REPLAY, True, True, "drain commit already observed with same idempotency key", selected=newest, candidate_receipts=receipt_tuple)
    if len({item.family_id for item in receipt_tuple}) < min_family_diversity:
        return make_report(OutboxDrainDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, "drain receipts lack family diversity", candidate_receipts=receipt_tuple)
    if len({item.path_family for item in receipt_tuple}) < min_path_diversity:
        return make_report(OutboxDrainDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, "drain receipts lack path diversity", candidate_receipts=receipt_tuple)
    watch = any(_component_watch(component) for component, *_ in component_checks)
    if newest.phase is OutboxDrainPhase.PREPARE:
        return make_report(OutboxDrainDecisionKind.ACCEPT_PREPARED_DRAIN, True, True, "outbox drain is prepared but not committed", selected=newest, candidate_receipts=receipt_tuple)
    return make_report(OutboxDrainDecisionKind.ACCEPT_WITH_WATCH if watch else OutboxDrainDecisionKind.ACCEPT_COMMIT_RECEIPT, True, watch, "outbox drain commit receipt is exact-scope, idempotent, and no-network", selected=newest, candidate_receipts=receipt_tuple)
