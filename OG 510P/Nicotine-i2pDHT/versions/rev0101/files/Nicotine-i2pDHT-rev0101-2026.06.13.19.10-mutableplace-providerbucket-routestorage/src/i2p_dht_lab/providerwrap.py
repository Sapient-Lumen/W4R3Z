"""Provider-plane compatibility facade for the canonical provider_poison module.

The cube still has a historical ``providerpoison`` module.  New rev0018 code
should not import that shadow surface.  This facade gives new callers a tiny
canonical path and keeps migration readiness testable.
"""
from __future__ import annotations

from dataclasses import dataclass

from .provider_poison import ProviderNodeMemory, ProviderProbeAssessment, ProviderProbeAssessmentKind, ProviderProbeReceipt
from .provider_refactor import ProviderMigrationPlan, plan_provider_surface_migration


@dataclass(frozen=True)
class ProviderWrapperDecision:
    provider_node_id: bytes
    selectable: bool
    quarantined: bool
    active_backoff: bool
    score: int
    reason: str


def observe_provider_receipt(memory: ProviderNodeMemory, receipt: ProviderProbeReceipt, *, now: int) -> tuple[ProviderProbeAssessment, ProviderWrapperDecision]:
    if receipt.provider_node_id != memory.provider_node_id:
        raise ValueError("receipt provider_node_id does not match provider memory")
    if not receipt.verify(now=now):
        assessment = ProviderProbeAssessment(ProviderProbeAssessmentKind.INVALID_PROBE_RECEIPT, receipt.receipt_hash, memory.provider_node_id, 0, "receipt failed canonical verification")
        return assessment, ProviderWrapperDecision(memory.provider_node_id, False, memory.quarantined, memory.active_backoff(now=now), memory.score, "invalid canonical receipt")
    assessment = memory.observe(receipt)
    active_backoff = memory.active_backoff(now=now)
    selectable = not memory.quarantined and not active_backoff
    reason = "provider selectable through canonical wrapper" if selectable else "provider blocked by canonical memory quarantine/backoff"
    return assessment, ProviderWrapperDecision(memory.provider_node_id, selectable, memory.quarantined, active_backoff, memory.score, reason)


def provider_wrapper_readiness(root: str) -> ProviderMigrationPlan:
    return plan_provider_surface_migration(root)
