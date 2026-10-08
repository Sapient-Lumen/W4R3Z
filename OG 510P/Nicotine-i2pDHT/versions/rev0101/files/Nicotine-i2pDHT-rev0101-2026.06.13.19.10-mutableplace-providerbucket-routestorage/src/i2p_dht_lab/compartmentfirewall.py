"""Joined key-compartment and bridge-firewall pressure.

rev0044 folds the two rev0043 branchlets together. Key role separation and
public bridge exposure are not independent chores: a public bridge decision that
passes firewall checks can still be unsafe if its operator/service/router keys
collapse, if the authority split is only partially accepted, or if the control
intent does not bind to the same profile/service/scope/request.

This module is a local reducer. It does not open sockets, publish bridge
announcements, or manage private keys. It makes the exact joined boundary
executable before those side effects exist.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .authoritysplit import AuthoritySplitAssessment, AuthoritySplitDecisionKind
from .bencode import bencode
from .bridgefirewall import BridgeFirewallMode, BridgeFirewallReport
from .controlintent import ControlIntentAction, ControlIntentJoinReport
from .ids import DOMAIN, sha256
from .keycompartment import CompartmentDecisionKind, CompartmentReport, KeyRole

COMPARTMENT_FIREWALL_DOMAIN = DOMAIN + b":compartment-firewall-v1:"
ZERO_DIGEST = b"\x00" * 32


class CompartmentFirewallDecisionKind(str, Enum):
    ACCEPT_COMPARTMENT_FIREWALL = "accept_compartment_firewall"
    ACCEPT_WITH_WATCH = "accept_with_watch"
    HOLD_MISSING_ROLE = "hold_missing_role"
    HOLD_COMPONENT_NOT_ACCEPTED = "hold_component_not_accepted"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_AUTHORITY_WATCH = "hold_authority_watch"
    HOLD_PUBLIC_BRIDGE_NEEDS_PUBLIC_FIREWALL = "hold_public_bridge_needs_public_firewall"
    QUARANTINE_AUTHORITY_REJECTED = "quarantine_authority_rejected"
    QUARANTINE_CONTROL_REJECTED = "quarantine_control_rejected"
    QUARANTINE_FIREWALL_REJECTED = "quarantine_firewall_rejected"
    QUARANTINE_PROFILE_DRIFT = "quarantine_profile_drift"
    QUARANTINE_SERVICE_DRIFT = "quarantine_service_drift"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_REQUEST_DRIFT = "quarantine_request_drift"
    QUARANTINE_MODE_MISMATCH = "quarantine_mode_mismatch"
    QUARANTINE_ACTION_MISMATCH = "quarantine_action_mismatch"
    QUARANTINE_ROLE_REUSE = "quarantine_role_reuse"
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"


_MODE_ACTIONS = {
    BridgeFirewallMode.PUBLIC_BRIDGE: {ControlIntentAction.KEEP_GARDEN_ONLINE, ControlIntentAction.RESUME_PROFILE},
    BridgeFirewallMode.PRIVATE_GARDEN: {ControlIntentAction.KEEP_GARDEN_ONLINE, ControlIntentAction.RESUME_PROFILE},
    BridgeFirewallMode.CLOSED_PUBLIC_BRIDGE: {ControlIntentAction.DISABLE_PUBLIC_BRIDGE},
}


@dataclass(frozen=True)
class CompartmentFirewallReport:
    decision_kind: CompartmentFirewallDecisionKind
    accept: bool
    reason: str
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    mode: BridgeFirewallMode
    action: ControlIntentAction
    role_digests: tuple[bytes, ...]
    component_digests: tuple[bytes, ...]
    family_count: int
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _report(
    kind: CompartmentFirewallDecisionKind,
    accept: bool,
    reason: str,
    *,
    profile_id: str,
    service_name: str,
    scope_digest: bytes,
    request_digest: bytes,
    mode: BridgeFirewallMode,
    action: ControlIntentAction,
    role_reports: Iterable[CompartmentReport] = (),
    component_digests: Iterable[bytes] = (),
    family_count: int = 0,
) -> CompartmentFirewallReport:
    roles = tuple(sorted(item.accepted_binding_digest for item in role_reports if item.accepted_binding_digest != ZERO_DIGEST))
    components = tuple(sorted(set(component_digests)))
    digest = sha256(COMPARTMENT_FIREWALL_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"reason": reason,
        b"profile": profile_id,
        b"service": service_name,
        b"scope": scope_digest,
        b"request": request_digest,
        b"mode": mode.value,
        b"action": action.value,
        b"roles": list(roles),
        b"components": list(components),
        b"families": family_count,
    }))
    return CompartmentFirewallReport(kind, accept, reason, profile_id, service_name, scope_digest, request_digest, mode, action, roles, components, family_count, digest)


def assess_compartment_firewall(
    *,
    authority_split: AuthoritySplitAssessment,
    role_reports: Iterable[CompartmentReport],
    control_intent: ControlIntentJoinReport,
    bridge_firewall: BridgeFirewallReport,
    expected_profile_id: str,
    expected_service_name: str,
    expected_scope_digest: bytes,
    expected_request_digest: bytes,
    mode: BridgeFirewallMode,
    required_roles: Iterable[KeyRole] = (KeyRole.OPERATOR, KeyRole.ROUTER_DESTINATION, KeyRole.SERVICE_SIGNER),
    min_family_diversity: int = 3,
    hard_negative_digests: Iterable[bytes] = (),
    allow_authority_watch: bool = False,
) -> CompartmentFirewallReport:
    if len(expected_scope_digest) != 32 or len(expected_request_digest) != 32:
        raise ValueError("expected digests must be 32 bytes")
    roles = tuple(role_reports)
    required_tuple = tuple(required_roles)
    component_digests = (authority_split.report_digest, control_intent.report_digest, bridge_firewall.report_digest)

    if control_intent.profile_id != expected_profile_id or bridge_firewall.profile_id != expected_profile_id:
        return _report(CompartmentFirewallDecisionKind.QUARANTINE_PROFILE_DRIFT, False, "profile drift across control/firewall", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, mode=mode, action=control_intent.action, role_reports=roles, component_digests=component_digests)
    if control_intent.service_name != expected_service_name or bridge_firewall.service_name != expected_service_name:
        return _report(CompartmentFirewallDecisionKind.QUARANTINE_SERVICE_DRIFT, False, "service drift across control/firewall", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, mode=mode, action=control_intent.action, role_reports=roles, component_digests=component_digests)
    if control_intent.scope_digest != expected_scope_digest or bridge_firewall.scope_digest != expected_scope_digest:
        return _report(CompartmentFirewallDecisionKind.QUARANTINE_SCOPE_DRIFT, False, "scope drift across control/firewall", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, mode=mode, action=control_intent.action, role_reports=roles, component_digests=component_digests)
    if control_intent.request_digest != expected_request_digest:
        return _report(CompartmentFirewallDecisionKind.QUARANTINE_REQUEST_DRIFT, False, "control intent request drift", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, mode=mode, action=control_intent.action, role_reports=roles, component_digests=component_digests)
    if bridge_firewall.mode is not mode:
        return _report(CompartmentFirewallDecisionKind.QUARANTINE_MODE_MISMATCH, False, "bridge firewall mode mismatch", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, mode=mode, action=control_intent.action, role_reports=roles, component_digests=component_digests)
    if control_intent.action not in _MODE_ACTIONS[mode]:
        return _report(CompartmentFirewallDecisionKind.QUARANTINE_ACTION_MISMATCH, False, "control action does not match firewall mode", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, mode=mode, action=control_intent.action, role_reports=roles, component_digests=component_digests)
    hard_negatives = tuple(hard_negative_digests)
    if hard_negatives:
        return _report(CompartmentFirewallDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, "hard-negative pressure survives joined firewall", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, mode=mode, action=control_intent.action, role_reports=roles, component_digests=component_digests + hard_negatives)

    if authority_split.decision_kind.value.startswith("quarantine_"):
        return _report(CompartmentFirewallDecisionKind.QUARANTINE_AUTHORITY_REJECTED, False, "authority split quarantined", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, mode=mode, action=control_intent.action, role_reports=roles, component_digests=component_digests)
    if authority_split.decision_kind not in (AuthoritySplitDecisionKind.ACCEPT_AUTHORITY_SPLIT, AuthoritySplitDecisionKind.ACCEPT_WITH_WATCH):
        return _report(CompartmentFirewallDecisionKind.HOLD_COMPONENT_NOT_ACCEPTED, False, "authority split not accepted", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, mode=mode, action=control_intent.action, role_reports=roles, component_digests=component_digests, family_count=authority_split.family_count)
    if authority_split.decision_kind is AuthoritySplitDecisionKind.ACCEPT_WITH_WATCH and not allow_authority_watch:
        return _report(CompartmentFirewallDecisionKind.HOLD_AUTHORITY_WATCH, False, "authority split has watch components", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, mode=mode, action=control_intent.action, role_reports=roles, component_digests=component_digests, family_count=authority_split.family_count)
    if not control_intent.accept:
        kind = CompartmentFirewallDecisionKind.QUARANTINE_CONTROL_REJECTED if control_intent.quarantined else CompartmentFirewallDecisionKind.HOLD_COMPONENT_NOT_ACCEPTED
        return _report(kind, False, "control intent not accepted", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, mode=mode, action=control_intent.action, role_reports=roles, component_digests=component_digests, family_count=authority_split.family_count)
    if not bridge_firewall.accept:
        kind = CompartmentFirewallDecisionKind.QUARANTINE_FIREWALL_REJECTED if bridge_firewall.quarantined else CompartmentFirewallDecisionKind.HOLD_COMPONENT_NOT_ACCEPTED
        return _report(kind, False, "bridge firewall not accepted", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, mode=mode, action=control_intent.action, role_reports=roles, component_digests=component_digests, family_count=authority_split.family_count)
    if mode is BridgeFirewallMode.PUBLIC_BRIDGE and not bridge_firewall.public_exposure_seen:
        return _report(CompartmentFirewallDecisionKind.HOLD_PUBLIC_BRIDGE_NEEDS_PUBLIC_FIREWALL, False, "public bridge mode lacks public exposure evidence", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, mode=mode, action=control_intent.action, role_reports=roles, component_digests=component_digests, family_count=authority_split.family_count)

    by_role: dict[KeyRole, CompartmentReport] = {}
    for report in roles:
        if report.role is None:
            continue
        if report.decision_kind.value.startswith("quarantine_"):
            return _report(CompartmentFirewallDecisionKind.QUARANTINE_AUTHORITY_REJECTED, False, "role compartment quarantined", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, mode=mode, action=control_intent.action, role_reports=roles, component_digests=component_digests, family_count=authority_split.family_count)
        current = by_role.get(report.role)
        if current is None or report.highest_sequence > current.highest_sequence:
            by_role[report.role] = report
    missing = tuple(role for role in required_tuple if role not in by_role)
    if missing:
        return _report(CompartmentFirewallDecisionKind.HOLD_MISSING_ROLE, False, "missing required key role", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, mode=mode, action=control_intent.action, role_reports=roles, component_digests=component_digests + tuple(role.value.encode("utf-8") for role in missing), family_count=authority_split.family_count)
    selected = tuple(by_role[role] for role in required_tuple)
    not_accepted = tuple(item for item in selected if item.decision_kind is not CompartmentDecisionKind.ACCEPT_COMPARTMENTED_KEY)
    if not_accepted:
        return _report(CompartmentFirewallDecisionKind.HOLD_COMPONENT_NOT_ACCEPTED, False, "role compartment not accepted", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, mode=mode, action=control_intent.action, role_reports=roles, component_digests=component_digests + (not_accepted[0].report_digest,), family_count=authority_split.family_count)
    key_digests = tuple(item.accepted_key_digest for item in selected)
    if ZERO_DIGEST in key_digests or len(set(key_digests)) != len(key_digests):
        return _report(CompartmentFirewallDecisionKind.QUARANTINE_ROLE_REUSE, False, "required roles reuse a key digest", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, mode=mode, action=control_intent.action, role_reports=selected, component_digests=component_digests, family_count=authority_split.family_count)
    family_count = max(authority_split.family_count, max((item.family_count for item in selected), default=0))
    if family_count < min_family_diversity:
        return _report(CompartmentFirewallDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, "joined compartment firewall lacks family diversity", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, mode=mode, action=control_intent.action, role_reports=selected, component_digests=component_digests, family_count=family_count)
    kind = CompartmentFirewallDecisionKind.ACCEPT_WITH_WATCH if authority_split.decision_kind is AuthoritySplitDecisionKind.ACCEPT_WITH_WATCH else CompartmentFirewallDecisionKind.ACCEPT_COMPARTMENT_FIREWALL
    return _report(kind, True, "compartmented authority and bridge firewall agree at exact boundary", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, mode=mode, action=control_intent.action, role_reports=selected, component_digests=component_digests, family_count=family_count)
