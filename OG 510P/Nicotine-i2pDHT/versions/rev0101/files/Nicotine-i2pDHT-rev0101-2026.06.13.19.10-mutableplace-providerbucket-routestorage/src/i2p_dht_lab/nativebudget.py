"""rev0084 native optimization budget.

Native code must remain a scarce budgeted optimization surface, not a second
implementation of protocol truth.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .bencode import bencode
from .ids import DOMAIN, sha256
from .parserhold import ParserHoldReport, ParserHoldDecisionKind
from .sanitizerplan import SanitizerPlanReport, SanitizerPlanDecisionKind

NATIVE_BUDGET_DOMAIN = DOMAIN + b":native-budget-v1:"


class NativeBudgetDecisionKind(str, Enum):
    ACCEPT_NATIVE_BUDGET = "accept_native_budget"
    ACCEPT_FALLBACK_ONLY = "accept_fallback_only"
    HOLD_NATIVE_REQUIRED_WITHOUT_BUDGET = "hold_native_required_without_budget"
    QUARANTINE_SEMANTIC_SURFACE = "quarantine_semantic_surface"
    QUARANTINE_UNKNOWN_COMPONENT = "quarantine_unknown_component"
    QUARANTINE_BUDGET_EXCEEDED = "quarantine_budget_exceeded"
    QUARANTINE_MISSING_FALLBACK = "quarantine_missing_fallback"
    QUARANTINE_PARSER_HOLD_NOT_ACCEPTED = "quarantine_parser_hold_not_accepted"
    QUARANTINE_SANITIZER_NOT_ACCEPTED = "quarantine_sanitizer_not_accepted"


@dataclass(frozen=True)
class NativeOptimizationBudget:
    profile: str
    allowed_components: tuple[str, ...]
    max_native_components: int
    max_call_sites: int
    max_estimated_calls: int
    max_input_len: int
    require_python_fallback: bool = True
    allow_native_parsers: bool = False
    allow_native_crypto: bool = False
    allow_native_transport: bool = False

    @property
    def budget_digest(self) -> bytes:
        return sha256(NATIVE_BUDGET_DOMAIN + b":budget:" + bencode({
            b"profile": self.profile,
            b"components": list(self.allowed_components),
            b"max_components": self.max_native_components,
            b"max_call_sites": self.max_call_sites,
            b"max_calls": self.max_estimated_calls,
            b"max_input": self.max_input_len,
            b"fallback": 1 if self.require_python_fallback else 0,
            b"parsers": 1 if self.allow_native_parsers else 0,
            b"crypto": 1 if self.allow_native_crypto else 0,
            b"transport": 1 if self.allow_native_transport else 0,
        }))


@dataclass(frozen=True)
class NativeBudgetDemand:
    component: str
    operation: str
    request_id: str
    call_sites: int
    estimated_calls: int
    max_input_len: int
    native_required: bool
    fallback_available: bool
    touches_parser: bool = False
    touches_crypto: bool = False
    touches_transport: bool = False
    touches_protocol_authority: bool = False
    note: str = ""

    @property
    def demand_digest(self) -> bytes:
        return sha256(NATIVE_BUDGET_DOMAIN + b":demand:" + bencode({
            b"component": self.component,
            b"operation": self.operation,
            b"request": self.request_id,
            b"call_sites": self.call_sites,
            b"estimated_calls": self.estimated_calls,
            b"max_input": self.max_input_len,
            b"required": 1 if self.native_required else 0,
            b"fallback": 1 if self.fallback_available else 0,
            b"parser": 1 if self.touches_parser else 0,
            b"crypto": 1 if self.touches_crypto else 0,
            b"transport": 1 if self.touches_transport else 0,
            b"authority": 1 if self.touches_protocol_authority else 0,
            b"note": self.note,
        }))


@dataclass(frozen=True)
class NativeBudgetReport:
    decision_kind: NativeBudgetDecisionKind
    accepted: bool
    fallback_only: bool
    hold: bool
    quarantine: bool
    budget_digest: bytes
    demand_digest: bytes
    parser_hold_digest: bytes
    sanitizer_report_digest: bytes
    obligations: tuple[str, ...]

    @property
    def report_digest(self) -> bytes:
        return sha256(NATIVE_BUDGET_DOMAIN + b":report:" + bencode({
            b"decision": NativeBudgetDecisionKind(self.decision_kind).value,
            b"accepted": 1 if self.accepted else 0,
            b"fallback_only": 1 if self.fallback_only else 0,
            b"hold": 1 if self.hold else 0,
            b"quarantine": 1 if self.quarantine else 0,
            b"budget": self.budget_digest,
            b"demand": self.demand_digest,
            b"parser": self.parser_hold_digest,
            b"sanitizer": self.sanitizer_report_digest,
            b"obligations": list(self.obligations),
        }))


def assess_native_budget(
    budget: NativeOptimizationBudget,
    demand: NativeBudgetDemand,
    parser_hold: ParserHoldReport,
    sanitizer_report: SanitizerPlanReport,
) -> NativeBudgetReport:
    """Decide whether one native optimization demand may be admitted."""

    def report(kind: NativeBudgetDecisionKind, accepted: bool, fallback_only: bool, hold: bool, quarantine: bool, obligations: tuple[str, ...]) -> NativeBudgetReport:
        return NativeBudgetReport(kind, accepted, fallback_only, hold, quarantine, budget.budget_digest, demand.demand_digest, parser_hold.report_digest, sanitizer_report.report_digest, obligations)

    if parser_hold.decision_kind is not ParserHoldDecisionKind.ACCEPT_PYTHON_PARSER_HOLD:
        return report(NativeBudgetDecisionKind.QUARANTINE_PARSER_HOLD_NOT_ACCEPTED, False, False, False, True, ("parser-hold-must-accept-python-ownership",))
    if sanitizer_report.decision_kind not in (SanitizerPlanDecisionKind.ACCEPT_DEV_SANITIZER_PLAN, SanitizerPlanDecisionKind.ACCEPT_RELEASE_NO_NATIVE_SANITIZER):
        return report(NativeBudgetDecisionKind.QUARANTINE_SANITIZER_NOT_ACCEPTED, False, False, False, True, ("sanitizer-plan-must-accept-before-native-budget",))
    if demand.component not in budget.allowed_components:
        return report(NativeBudgetDecisionKind.QUARANTINE_UNKNOWN_COMPONENT, False, False, False, True, ("component-not-in-native-budget",))
    if budget.require_python_fallback and not demand.fallback_available:
        return report(NativeBudgetDecisionKind.QUARANTINE_MISSING_FALLBACK, False, False, False, True, ("native-demand-lacks-python-fallback",))
    if demand.touches_protocol_authority or (demand.touches_parser and not budget.allow_native_parsers) or (demand.touches_crypto and not budget.allow_native_crypto) or (demand.touches_transport and not budget.allow_native_transport):
        return report(NativeBudgetDecisionKind.QUARANTINE_SEMANTIC_SURFACE, False, False, False, True, ("native-demand-touches-semantic-or-forbidden-surface",))
    if budget.max_native_components < 1 or demand.call_sites > budget.max_call_sites or demand.estimated_calls > budget.max_estimated_calls or demand.max_input_len > budget.max_input_len:
        return report(NativeBudgetDecisionKind.QUARANTINE_BUDGET_EXCEEDED, False, False, False, True, ("native-demand-exceeds-budget",))
    if demand.native_required and budget.max_native_components == 0:
        return report(NativeBudgetDecisionKind.HOLD_NATIVE_REQUIRED_WITHOUT_BUDGET, False, False, True, False, ("native-required-profile-has-no-native-budget",))
    if not demand.native_required and demand.fallback_available:
        return report(NativeBudgetDecisionKind.ACCEPT_FALLBACK_ONLY, True, True, False, False, ("fallback-path-satisfies-demand", "native-optimization-not-required"))
    return report(NativeBudgetDecisionKind.ACCEPT_NATIVE_BUDGET, True, False, False, False, ("native-leaf-budget-admitted", "keep-python-oracle-and-fallback"))
