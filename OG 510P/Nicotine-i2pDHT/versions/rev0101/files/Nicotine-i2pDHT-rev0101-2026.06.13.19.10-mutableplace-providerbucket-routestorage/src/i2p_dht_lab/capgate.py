"""Capability-gated dispatch after namespace validation and admission.

By rev0024 the cube had separate surfaces for canonical wire frames,
validator-wall parsing, namespace policy, capability delegation, and admission
budgets.  The risky part is not any one surface.  The risky part is letting one
successful surface imply the others succeeded.  A valid namespace policy should
not bypass capability revocation.  A valid capability should not bypass local
admission pressure.  A useful refusal should not become authorization.

This module joins those surfaces in one deterministic, transport-neutral gate.
It is still a prototype: no live network, no production authorization scheme,
and no claim that local policy is global truth.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable, Mapping

from .admissionwall import (
    AdmissionBudget,
    AdmissionDecision,
    AdmissionDecisionKind,
    AdmissionPriority,
    AdmissionRequest,
    AdmissionState,
    decide_admission_batch,
)
from .bencode import BValue, bencode
from .capability import CapabilityGrant, CapabilityKind, CapabilityCheck, RevocationSet, validate_capability_chain
from .identity import DhtKeypair
from .ids import DOMAIN, sha256
from .namespaceregistry import NamespaceDispatchReport, NamespaceRegistry, validate_namespace_dispatch
from .validatorwall import PayloadRole
from .wirecanon import WireFrame, WireMessageKind

CAPGATE_DOMAIN = DOMAIN + b":capgate-v1:"


DEFAULT_CAPABILITY_BY_ROLE: Mapping[PayloadRole, CapabilityKind] = {
    PayloadRole.MUTABLE_HEAD: CapabilityKind.WRITE_HEAD,
    PayloadRole.STORE_REQUEST: CapabilityKind.GARDEN_REPROVIDE,
    PayloadRole.STORE_RECEIPT: CapabilityKind.GARDEN_REPROVIDE,
    PayloadRole.CUSTODY_CHALLENGE: CapabilityKind.GARDEN_REPROVIDE,
    PayloadRole.CUSTODY_PROOF: CapabilityKind.GARDEN_REPROVIDE,
    PayloadRole.PROVIDER_CLAIM: CapabilityKind.PUBLISH_SEED,
    PayloadRole.WITNESS_RECEIPT: CapabilityKind.GARDEN_WATCH,
    PayloadRole.USEFUL_REFUSAL: CapabilityKind.GARDEN_WATCH,
    PayloadRole.REPAIR_OFFER: CapabilityKind.GARDEN_REPROVIDE,
}


class CapabilityDispatchDecisionKind(str, Enum):
    ACCEPT_DISPATCH = "accept_dispatch"
    REJECT_NAMESPACE = "reject_namespace"
    REJECT_UNKNOWN_CAPABILITY = "reject_unknown_capability"
    REJECT_CAPABILITY = "reject_capability"
    REJECT_ACTOR_MISMATCH = "reject_actor_mismatch"
    REFUSE_ADMISSION_USEFULLY = "refuse_admission_usefully"
    QUARANTINE_ADMISSION = "quarantine_admission"
    DROP_ADMISSION = "drop_admission"


@dataclass(frozen=True)
class CapabilityDispatchPolicy:
    authority_public_key_by_namespace: Mapping[str, bytes]
    capability_by_role: Mapping[PayloadRole, CapabilityKind] = field(default_factory=lambda: DEFAULT_CAPABILITY_BY_ROLE)
    require_frame_actor: bool = True
    default_priority_by_role: Mapping[PayloadRole, AdmissionPriority] | None = None
    metadata_cost_by_role: Mapping[PayloadRole, int] | None = None

    def __post_init__(self) -> None:
        if self.default_priority_by_role is None:
            object.__setattr__(
                self,
                "default_priority_by_role",
                {
                    PayloadRole.MUTABLE_HEAD: AdmissionPriority.CRITICAL,
                    PayloadRole.WITNESS_RECEIPT: AdmissionPriority.HIGH,
                    PayloadRole.USEFUL_REFUSAL: AdmissionPriority.HIGH,
                    PayloadRole.REPAIR_OFFER: AdmissionPriority.NORMAL,
                    PayloadRole.PROVIDER_CLAIM: AdmissionPriority.NORMAL,
                    PayloadRole.STORE_REQUEST: AdmissionPriority.BULK,
                    PayloadRole.STORE_RECEIPT: AdmissionPriority.NORMAL,
                    PayloadRole.CUSTODY_CHALLENGE: AdmissionPriority.NORMAL,
                    PayloadRole.CUSTODY_PROOF: AdmissionPriority.NORMAL,
                },
            )
        if self.metadata_cost_by_role is None:
            object.__setattr__(
                self,
                "metadata_cost_by_role",
                {
                    PayloadRole.MUTABLE_HEAD: 1,
                    PayloadRole.WITNESS_RECEIPT: 1,
                    PayloadRole.USEFUL_REFUSAL: 1,
                    PayloadRole.REPAIR_OFFER: 2,
                    PayloadRole.PROVIDER_CLAIM: 3,
                    PayloadRole.STORE_REQUEST: 5,
                    PayloadRole.STORE_RECEIPT: 2,
                    PayloadRole.CUSTODY_CHALLENGE: 2,
                    PayloadRole.CUSTODY_PROOF: 2,
                },
            )
        for namespace, key in self.authority_public_key_by_namespace.items():
            if not namespace or len(key) != 32:
                raise ValueError("capability dispatch authorities must be non-empty namespaces mapped to 32-byte keys")


@dataclass(frozen=True)
class CapabilityDispatchDecision:
    kind: CapabilityDispatchDecisionKind
    accept: bool
    reason: str


@dataclass(frozen=True)
class CapabilityDispatchReport:
    namespace_report: NamespaceDispatchReport
    capability_check: CapabilityCheck | None
    admission_decision: AdmissionDecision | None
    decision: CapabilityDispatchDecision
    required_capability: CapabilityKind | None
    resource: bytes
    report_digest: bytes

    @property
    def refused_usefully(self) -> bool:
        return self.decision.kind is CapabilityDispatchDecisionKind.REFUSE_ADMISSION_USEFULLY

    @property
    def quarantined(self) -> bool:
        return self.decision.kind.value.startswith("quarantine_")


def _priority_for(role: PayloadRole, policy: CapabilityDispatchPolicy) -> AdmissionPriority:
    return (policy.default_priority_by_role or {}).get(role, AdmissionPriority.NORMAL)


def _metadata_cost_for(role: PayloadRole, policy: CapabilityDispatchPolicy) -> int:
    return (policy.metadata_cost_by_role or {}).get(role, 1)


def _report(
    *,
    namespace_report: NamespaceDispatchReport,
    capability_check: CapabilityCheck | None,
    admission_decision: AdmissionDecision | None,
    decision: CapabilityDispatchDecision,
    required_capability: CapabilityKind | None,
    resource: bytes,
) -> CapabilityDispatchReport:
    digest = sha256(CAPGATE_DOMAIN + b":report:" + bencode({
        b"namespace": namespace_report.report_digest,
        b"capability": b"" if capability_check is None else capability_check.kind.value,
        b"admission": b"" if admission_decision is None else admission_decision.kind.value,
        b"decision": decision.kind.value,
        b"required": b"" if required_capability is None else required_capability.value,
        b"resource": resource,
    }))
    return CapabilityDispatchReport(namespace_report, capability_check, admission_decision, decision, required_capability, resource, digest)


def evaluate_capability_dispatch(
    *,
    registry: NamespaceRegistry,
    frame: WireFrame,
    payload: bytes,
    body: bytes,
    grants: Iterable[CapabilityGrant],
    revocations: RevocationSet | None,
    dispatch_policy: CapabilityDispatchPolicy,
    admission_budget: AdmissionBudget,
    garden_keypair: DhtKeypair,
    garden_node_id: bytes,
    source_family: str,
    now: int,
    expected_scope_id: bytes | None = None,
    admission_state: AdmissionState | None = None,
    actor_public_key: bytes | None = None,
) -> CapabilityDispatchReport:
    namespace_report = validate_namespace_dispatch(registry, frame, payload=payload, body=body, now=now, expected_scope_id=expected_scope_id)
    if not namespace_report.decision.accept or namespace_report.envelope is None:
        return _report(
            namespace_report=namespace_report,
            capability_check=None,
            admission_decision=None,
            decision=CapabilityDispatchDecision(CapabilityDispatchDecisionKind.REJECT_NAMESPACE, False, namespace_report.decision.reason),
            required_capability=None,
            resource=b"",
        )

    envelope = namespace_report.envelope
    required = dispatch_policy.capability_by_role.get(envelope.role)
    if required is None:
        return _report(
            namespace_report=namespace_report,
            capability_check=None,
            admission_decision=None,
            decision=CapabilityDispatchDecision(CapabilityDispatchDecisionKind.REJECT_UNKNOWN_CAPABILITY, False, "payload role has no local capability mapping"),
            required_capability=None,
            resource=envelope.scope_id,
        )
    authority = dispatch_policy.authority_public_key_by_namespace.get(envelope.namespace)
    if authority is None:
        return _report(
            namespace_report=namespace_report,
            capability_check=None,
            admission_decision=None,
            decision=CapabilityDispatchDecision(CapabilityDispatchDecisionKind.REJECT_CAPABILITY, False, "namespace has no selected capability authority"),
            required_capability=required,
            resource=envelope.scope_id,
        )
    actor = actor_public_key or frame.sender_public_key
    if dispatch_policy.require_frame_actor and actor != frame.sender_public_key:
        return _report(
            namespace_report=namespace_report,
            capability_check=None,
            admission_decision=None,
            decision=CapabilityDispatchDecision(CapabilityDispatchDecisionKind.REJECT_ACTOR_MISMATCH, False, "invocation actor does not match signed wire-frame sender"),
            required_capability=required,
            resource=envelope.scope_id,
        )

    cap_check = validate_capability_chain(
        grants,
        authority_public_key=authority,
        actor_public_key=actor,
        capability=required,
        resource=envelope.scope_id,
        now=now,
        revocations=revocations,
    )
    if not cap_check.valid:
        return _report(
            namespace_report=namespace_report,
            capability_check=cap_check,
            admission_decision=None,
            decision=CapabilityDispatchDecision(CapabilityDispatchDecisionKind.REJECT_CAPABILITY, False, cap_check.reason),
            required_capability=required,
            resource=envelope.scope_id,
        )

    request = AdmissionRequest.from_validated_frame(
        frame,
        source_family=source_family,
        namespace=envelope.namespace,
        role=envelope.role,
        priority=_priority_for(envelope.role, dispatch_policy),
        metadata_cost=_metadata_cost_for(envelope.role, dispatch_policy),
    )
    admission = decide_admission_batch((request,), budget=admission_budget, keypair=garden_keypair, garden_node_id=garden_node_id, now=now, state=admission_state)
    decision = admission.decisions[0]
    if decision.accepted:
        final = CapabilityDispatchDecision(CapabilityDispatchDecisionKind.ACCEPT_DISPATCH, True, "namespace, capability, and admission all accepted")
    elif decision.kind is AdmissionDecisionKind.REFUSE_USEFULLY:
        final = CapabilityDispatchDecision(CapabilityDispatchDecisionKind.REFUSE_ADMISSION_USEFULLY, False, "admission refused usefully after capability validation")
    elif decision.kind.value.startswith("quarantine_"):
        final = CapabilityDispatchDecision(CapabilityDispatchDecisionKind.QUARANTINE_ADMISSION, False, "admission quarantined a valid capability invocation")
    else:
        final = CapabilityDispatchDecision(CapabilityDispatchDecisionKind.DROP_ADMISSION, False, "admission dropped a valid capability invocation")
    return _report(
        namespace_report=namespace_report,
        capability_check=cap_check,
        admission_decision=decision,
        decision=final,
        required_capability=required,
        resource=envelope.scope_id,
    )
