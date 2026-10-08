"""Explicit provider-plane compatibility/refactor plan.

The cube accumulated two provider-poison surfaces while behavior was still
moving quickly: ``providerpoison.py`` from rev0011 and ``provider_poison.py`` as
the later canonical local-memory/refusal/quarantine surface.  Deleting the old
file would damage wake-from-amnesia history; leaving the split undocumented would
make future maintainers trip.

rev0018 adds an explicit compatibility plan.  It does not yet rewrite the legacy
module.  It classifies legacy-only public names into: already superseded,
adapter-worthy, or intentionally historical.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from importlib import import_module

from .ids import DOMAIN, sha256
from .provider_refactor import ProviderMigrationPlan, plan_provider_surface_migration

PROVIDER_COMPAT_DOMAIN = DOMAIN + b":provider-compat-v1:"


class ProviderCompatActionKind(str, Enum):
    REEXPORT_CANONICAL = "reexport_canonical"
    ADAPT_LEGACY_NAME = "adapt_legacy_name"
    KEEP_HISTORICAL_ONLY = "keep_historical_only"
    NEEDS_MANUAL_DECISION = "needs_manual_decision"


@dataclass(frozen=True)
class ProviderCompatAction:
    name: str
    kind: ProviderCompatActionKind
    target: str
    reason: str


@dataclass(frozen=True)
class ProviderCompatReport:
    migration: ProviderMigrationPlan
    actions: tuple[ProviderCompatAction, ...]
    safe_to_replace_legacy_module: bool
    transcript_digest: bytes

    @property
    def unresolved_names(self) -> tuple[str, ...]:
        return tuple(action.name for action in self.actions if action.kind is ProviderCompatActionKind.NEEDS_MANUAL_DECISION)

    @property
    def adapter_count(self) -> int:
        return sum(1 for action in self.actions if action.kind is ProviderCompatActionKind.ADAPT_LEGACY_NAME)


ADAPTER_TARGETS = {
    "ProviderPoisonAnalysis": "provider_poison.ProviderPoisonBook + probe assessment summary",
    "ProviderPoisonDecision": "provider_poison.ProviderRecordAssessment / ProviderProbeAssessment",
    "ProviderPoisonDecisionKind": "provider_poison.ProviderRecordAssessmentKind / ProviderProbeAssessmentKind",
    "ProviderPoisonPolicy": "provider_poison.ProviderPoisonBook policy wrapper, not a direct alias",
    "ProviderPressureObservation": "provider_poison.ProviderProbeReceipt plus ProviderNodeMemory",
    "ProviderProbeChallenge": "proofhandshake.ProviderProofChallenge for challenge-bound proofs",
    "ProviderProbeKind": "provider_poison.ProviderProbeOutcome",
    "ProviderProbePlan": "privateprovider.PrivateProviderProbePlan or proofhandshake challenge plan",
    "analyze_provider_poisoning": "provider_poison.ProviderPoisonBook.ingest_receipts plus proofprobe analysis",
    "make_provider_probe_plan": "privateprovider.plan_private_provider_probes plus proofhandshake challenges",
}

HISTORICAL_ONLY = {
    "DEFAULT_PROBE_TTL": "legacy timeout constant; callers should choose explicit policy ttl",
    "PROVIDER_PROBE_DOMAIN": "legacy transcript domain; keep only for old evidence digests",
}


def build_provider_compat_report(root: str) -> ProviderCompatReport:
    migration = plan_provider_surface_migration(root)
    canonical_module = import_module(migration.audit.canonical_module)
    actions: list[ProviderCompatAction] = []

    for name in migration.audit.shared_public_names:
        if hasattr(canonical_module, name):
            actions.append(ProviderCompatAction(name, ProviderCompatActionKind.REEXPORT_CANONICAL, f"{migration.audit.canonical_module}.{name}", "shared name can come from canonical surface"))

    for name in migration.audit.legacy_only_names:
        if name in ADAPTER_TARGETS:
            actions.append(ProviderCompatAction(name, ProviderCompatActionKind.ADAPT_LEGACY_NAME, ADAPTER_TARGETS[name], "legacy behavior needs an explicit adapter rather than silent aliasing"))
        elif name in HISTORICAL_ONLY:
            actions.append(ProviderCompatAction(name, ProviderCompatActionKind.KEEP_HISTORICAL_ONLY, "legacy-only", HISTORICAL_ONLY[name]))
        else:
            actions.append(ProviderCompatAction(name, ProviderCompatActionKind.NEEDS_MANUAL_DECISION, "", "legacy-only name has no explicit compatibility target"))

    unresolved = [action for action in actions if action.kind is ProviderCompatActionKind.NEEDS_MANUAL_DECISION]
    safe = migration.active_legacy_import_count == 0 and not unresolved and all(
        action.kind is not ProviderCompatActionKind.ADAPT_LEGACY_NAME for action in actions
    )
    digest = sha256(PROVIDER_COMPAT_DOMAIN + b":" + "|".join(f"{action.name}:{action.kind.value}:{action.target}" for action in sorted(actions, key=lambda item: item.name)).encode("utf-8"))
    return ProviderCompatReport(migration, tuple(actions), safe, digest)
