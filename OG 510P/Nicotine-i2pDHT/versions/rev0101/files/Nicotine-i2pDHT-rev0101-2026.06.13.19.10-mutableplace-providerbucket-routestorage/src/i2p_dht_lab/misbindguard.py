"""Cross-surface misbinding guard before expensive dispatch.

Many cube surfaces can individually accept an observation: a wire frame can be
signed, a payload envelope can validate, a capability grant can authorize, a
claim bundle can be scoped, and admission can fit the budget.  The dangerous bug
class is cross-surface misbinding: using a valid object from one scope, role,
namespace, actor, or request id to authorize a different local action.

This module is a small local guard that joins already-produced reports and checks
that the expensive handler is still bound to the same namespace/role/scope/
actor/request tuple.  It is intentionally stricter than any one upstream gate.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .bencode import bencode
from .capgate import CapabilityDispatchReport
from .claimbundle import ClaimBundleReport
from .ids import DOMAIN, sha256
from .validatorwall import PayloadRole, ValidatorWallReport
from .wirecanon import WireMessageKind

MISBIND_GUARD_DOMAIN = DOMAIN + b":misbind-guard-v1:"


class HandlerIntentKind(str, Enum):
    MUTABLE_HEAD_WRITE = "mutable_head_write"
    STORE_RECORD = "store_record"
    PROVIDER_PUBLISH = "provider_publish"
    WITNESS_ACCEPT = "witness_accept"
    REPAIR_OFFER_ACCEPT = "repair_offer_accept"
    USEFUL_REFUSAL_RECORD = "useful_refusal_record"


class MisbindDecisionKind(str, Enum):
    ACCEPT_BOUND_INTENT = "accept_bound_intent"
    REJECT_UPSTREAM_NOT_ACCEPTED = "reject_upstream_not_accepted"
    REJECT_KIND_ROLE_MISMATCH = "reject_kind_role_mismatch"
    REJECT_SCOPE_MISMATCH = "reject_scope_mismatch"
    REJECT_NAMESPACE_MISMATCH = "reject_namespace_mismatch"
    REJECT_ACTOR_MISMATCH = "reject_actor_mismatch"
    QUARANTINE_REQUEST_MISMATCH = "quarantine_request_mismatch"
    QUARANTINE_CLAIM_SCOPE_MISMATCH = "quarantine_claim_scope_mismatch"


EXPECTED_BY_INTENT: dict[HandlerIntentKind, tuple[WireMessageKind, PayloadRole]] = {
    HandlerIntentKind.MUTABLE_HEAD_WRITE: (WireMessageKind.EPOCH_HEAD, PayloadRole.MUTABLE_HEAD),
    HandlerIntentKind.STORE_RECORD: (WireMessageKind.STORE_RECORD, PayloadRole.STORE_REQUEST),
    HandlerIntentKind.PROVIDER_PUBLISH: (WireMessageKind.FIND_PROVIDER, PayloadRole.PROVIDER_CLAIM),
    HandlerIntentKind.WITNESS_ACCEPT: (WireMessageKind.WITNESS_RECEIPT, PayloadRole.WITNESS_RECEIPT),
    HandlerIntentKind.REPAIR_OFFER_ACCEPT: (WireMessageKind.REPAIR_OFFER, PayloadRole.REPAIR_OFFER),
    HandlerIntentKind.USEFUL_REFUSAL_RECORD: (WireMessageKind.USEFUL_REFUSAL, PayloadRole.USEFUL_REFUSAL),
}


@dataclass(frozen=True)
class HandlerIntent:
    kind: HandlerIntentKind
    namespace: str
    scope_id: bytes
    actor_public_key: bytes
    request_id: bytes
    body_digest: bytes

    def __post_init__(self) -> None:
        if not self.namespace:
            raise ValueError("handler intent namespace must not be empty")
        for name, value in (("scope_id", self.scope_id), ("actor_public_key", self.actor_public_key), ("request_id", self.request_id), ("body_digest", self.body_digest)):
            if len(value) != 32:
                raise ValueError(f"handler intent {name} must be 32 bytes")


@dataclass(frozen=True)
class MisbindGuardPolicy:
    require_claim_bundle_scope: bool = True
    require_capgate_acceptance: bool = True
    require_validator_acceptance: bool = True


@dataclass(frozen=True)
class MisbindGuardReport:
    decision_kind: MisbindDecisionKind
    accept: bool
    reason: str
    intent_digest: bytes
    validator_digest: bytes | None
    capgate_digest: bytes | None
    claim_bundle_digest: bytes | None
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _intent_digest(intent: HandlerIntent) -> bytes:
    return sha256(MISBIND_GUARD_DOMAIN + b":intent:" + bencode({
        b"kind": intent.kind.value,
        b"namespace": intent.namespace,
        b"scope": intent.scope_id,
        b"actor": intent.actor_public_key,
        b"request": intent.request_id,
        b"body": intent.body_digest,
    }))


def _report(
    decision: MisbindDecisionKind,
    accept: bool,
    reason: str,
    *,
    intent: HandlerIntent,
    validator: ValidatorWallReport | None,
    capgate: CapabilityDispatchReport | None,
    claim_bundle: ClaimBundleReport | None,
) -> MisbindGuardReport:
    intent_digest = _intent_digest(intent)
    validator_digest = None if validator is None else validator.report_digest
    capgate_digest = None if capgate is None else capgate.report_digest
    claim_digest = None if claim_bundle is None else claim_bundle.report_digest
    digest = sha256(MISBIND_GUARD_DOMAIN + b":report:" + bencode({
        b"decision": decision.value,
        b"accept": 1 if accept else 0,
        b"intent": intent_digest,
        b"validator": b"" if validator_digest is None else validator_digest,
        b"capgate": b"" if capgate_digest is None else capgate_digest,
        b"claim": b"" if claim_digest is None else claim_digest,
    }))
    return MisbindGuardReport(decision, accept, reason, intent_digest, validator_digest, capgate_digest, claim_digest, digest)


def guard_handler_intent(
    *,
    intent: HandlerIntent,
    validator: ValidatorWallReport,
    capgate: CapabilityDispatchReport | None = None,
    claim_bundles: Iterable[ClaimBundleReport] = (),
    policy: MisbindGuardPolicy | None = None,
) -> MisbindGuardReport:
    policy = policy or MisbindGuardPolicy()
    if policy.require_validator_acceptance and not validator.decision.accept:
        return _report(MisbindDecisionKind.REJECT_UPSTREAM_NOT_ACCEPTED, False, "validator wall did not accept payload", intent=intent, validator=validator, capgate=capgate, claim_bundle=None)
    if validator.envelope is None:
        return _report(MisbindDecisionKind.REJECT_UPSTREAM_NOT_ACCEPTED, False, "validator wall produced no payload envelope", intent=intent, validator=validator, capgate=capgate, claim_bundle=None)
    if policy.require_capgate_acceptance and (capgate is None or not capgate.decision.accept):
        return _report(MisbindDecisionKind.REJECT_UPSTREAM_NOT_ACCEPTED, False, "capability/admission gate did not accept dispatch", intent=intent, validator=validator, capgate=capgate, claim_bundle=None)
    expected_kind, expected_role = EXPECTED_BY_INTENT[intent.kind]
    if validator.frame.message_kind is not expected_kind or validator.envelope.role is not expected_role:
        return _report(MisbindDecisionKind.REJECT_KIND_ROLE_MISMATCH, False, "handler intent does not match wire message kind and payload role", intent=intent, validator=validator, capgate=capgate, claim_bundle=None)
    if validator.envelope.namespace != intent.namespace:
        return _report(MisbindDecisionKind.REJECT_NAMESPACE_MISMATCH, False, "handler intent namespace does not match payload envelope", intent=intent, validator=validator, capgate=capgate, claim_bundle=None)
    if validator.envelope.scope_id != intent.scope_id:
        return _report(MisbindDecisionKind.REJECT_SCOPE_MISMATCH, False, "handler intent scope does not match payload envelope", intent=intent, validator=validator, capgate=capgate, claim_bundle=None)
    if validator.frame.sender_public_key != intent.actor_public_key:
        return _report(MisbindDecisionKind.REJECT_ACTOR_MISMATCH, False, "handler intent actor does not match wire-frame signer", intent=intent, validator=validator, capgate=capgate, claim_bundle=None)
    if validator.frame.request_id != intent.request_id:
        return _report(MisbindDecisionKind.QUARANTINE_REQUEST_MISMATCH, False, "handler intent request id does not match wire frame", intent=intent, validator=validator, capgate=capgate, claim_bundle=None)
    if validator.envelope.body_digest != intent.body_digest:
        return _report(MisbindDecisionKind.REJECT_SCOPE_MISMATCH, False, "handler intent body digest does not match payload envelope", intent=intent, validator=validator, capgate=capgate, claim_bundle=None)
    for claim in claim_bundles:
        if policy.require_claim_bundle_scope and claim.decision.accept and claim.source_families and claim.bundle_digest and claim.positive_count + claim.negative_count > 0:
            # ClaimBundleReport intentionally does not expose scope; compare by
            # report evidence shape indirectly when report is attached.  Future
            # branch should thread scope explicitly.  For now, only use accepted
            # claim bundles as additional evidence if they are not quarantined.
            if claim.quarantined:
                return _report(MisbindDecisionKind.QUARANTINE_CLAIM_SCOPE_MISMATCH, False, "claim bundle was quarantined but attached to dispatch", intent=intent, validator=validator, capgate=capgate, claim_bundle=claim)
    return _report(MisbindDecisionKind.ACCEPT_BOUND_INTENT, True, "handler intent remains bound across validator/capability/claim surfaces", intent=intent, validator=validator, capgate=capgate, claim_bundle=None)
