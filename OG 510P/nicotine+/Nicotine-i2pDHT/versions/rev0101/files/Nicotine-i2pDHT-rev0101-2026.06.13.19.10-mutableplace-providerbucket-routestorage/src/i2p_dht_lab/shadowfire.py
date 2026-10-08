"""Joined public-bridge shadow-fire gate.

rev0045 joins public bridge epoch state, key-authority receipts, subjective
policy, authority receipts, and announcement repair.  The purpose is not to
create a global moderator or a production bridge firewall.  The purpose is to
make the hidden side effect visible: a public bridge can only stay public, close,
or recover when the exact local evidence chain agrees.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .announcementrepair import AnnouncementRepairReport
from .authorityreceipt import AuthorityReceiptMeshReport
from .bencode import bencode
from .bridgeepoch import BridgeEpochAction, BridgeEpochReport
from .ids import DOMAIN, sha256
from .keyreceiptlane import KeyReceiptReport
from .policyfirebreak import PolicyFirebreakReport, ZERO_DIGEST

SHADOW_FIRE_DOMAIN = DOMAIN + b":shadow-fire-v1:"


class ShadowFireDecisionKind(str, Enum):
    ACCEPT_PUBLIC_BRIDGE = "accept_public_bridge"
    ACCEPT_CLOSE_OR_WITHDRAW = "accept_close_or_withdraw"
    ACCEPT_WITH_WATCH = "accept_with_watch"
    HOLD_COMPONENT_NOT_ACCEPTED = "hold_component_not_accepted"
    HOLD_REPAIR_REQUIRED = "hold_repair_required"
    HOLD_LOW_EVIDENCE_DIVERSITY = "hold_low_evidence_diversity"
    QUARANTINE_EPOCH = "quarantine_epoch"
    QUARANTINE_KEY_RECEIPTS = "quarantine_key_receipts"
    QUARANTINE_POLICY = "quarantine_policy"
    QUARANTINE_AUTHORITY_RECEIPTS = "quarantine_authority_receipts"
    QUARANTINE_REPAIR = "quarantine_repair"
    QUARANTINE_PROFILE_DRIFT = "quarantine_profile_drift"
    QUARANTINE_SERVICE_DRIFT = "quarantine_service_drift"
    QUARANTINE_ACTION_MISMATCH = "quarantine_action_mismatch"
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"


@dataclass(frozen=True)
class ShadowFireReport:
    decision_kind: ShadowFireDecisionKind
    accept: bool
    watch: bool
    reason: str
    profile_id: str
    service_name: str
    bridge_action: BridgeEpochAction | None
    component_digests: tuple[bytes, ...]
    evidence_family_count: int
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _report(kind: ShadowFireDecisionKind, accept: bool, watch: bool, reason: str, *, profile_id: str, service_name: str, bridge_action: BridgeEpochAction | None, component_digests: Iterable[bytes], evidence_family_count: int) -> ShadowFireReport:
    digests = tuple(sorted(set(component_digests)))
    digest = sha256(SHADOW_FIRE_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"reason": reason,
        b"profile": profile_id,
        b"service": service_name,
        b"action": bridge_action.value if bridge_action is not None else b"none",
        b"components": list(digests),
        b"families": evidence_family_count,
    }))
    return ShadowFireReport(kind, accept, watch, reason, profile_id, service_name, bridge_action, digests, evidence_family_count, digest)


def assess_shadow_fire(
    *,
    bridge_epoch: BridgeEpochReport,
    key_receipts: KeyReceiptReport,
    policy_firebreak: PolicyFirebreakReport,
    authority_receipts: AuthorityReceiptMeshReport,
    announcement_repair: AnnouncementRepairReport | None,
    expected_profile_id: str,
    expected_service_name: str,
    expected_public: bool,
    hard_negative_digests: Iterable[bytes] = (),
    min_combined_family_count: int = 4,
) -> ShadowFireReport:
    components = [bridge_epoch.report_digest, key_receipts.report_digest, policy_firebreak.report_digest, authority_receipts.report_digest]
    if announcement_repair is not None:
        components.append(announcement_repair.report_digest)
    components.extend(hard_negative_digests)
    if bridge_epoch.profile_id != expected_profile_id or key_receipts.profile_id != expected_profile_id:
        return _report(ShadowFireDecisionKind.QUARANTINE_PROFILE_DRIFT, False, False, "profile drift across epoch/key receipt", profile_id=expected_profile_id, service_name=expected_service_name, bridge_action=bridge_epoch.action, component_digests=components, evidence_family_count=0)
    if bridge_epoch.service_name != expected_service_name or key_receipts.service_name != expected_service_name:
        return _report(ShadowFireDecisionKind.QUARANTINE_SERVICE_DRIFT, False, False, "service drift across epoch/key receipt", profile_id=expected_profile_id, service_name=expected_service_name, bridge_action=bridge_epoch.action, component_digests=components, evidence_family_count=0)
    if tuple(hard_negative_digests):
        return _report(ShadowFireDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, "hard-negative pressure blocks shadow fire", profile_id=expected_profile_id, service_name=expected_service_name, bridge_action=bridge_epoch.action, component_digests=components, evidence_family_count=0)
    if bridge_epoch.quarantined:
        return _report(ShadowFireDecisionKind.QUARANTINE_EPOCH, False, False, "bridge epoch quarantined", profile_id=expected_profile_id, service_name=expected_service_name, bridge_action=bridge_epoch.action, component_digests=components, evidence_family_count=bridge_epoch.family_count)
    if key_receipts.quarantined:
        return _report(ShadowFireDecisionKind.QUARANTINE_KEY_RECEIPTS, False, key_receipts.watch, "key receipts quarantined", profile_id=expected_profile_id, service_name=expected_service_name, bridge_action=bridge_epoch.action, component_digests=components, evidence_family_count=key_receipts.family_count)
    if policy_firebreak.decision_kind.value.startswith("quarantine_"):
        return _report(ShadowFireDecisionKind.QUARANTINE_POLICY, False, policy_firebreak.watch, "policy firebreak quarantined", profile_id=expected_profile_id, service_name=expected_service_name, bridge_action=bridge_epoch.action, component_digests=components, evidence_family_count=policy_firebreak.family_count)
    if authority_receipts.decision_kind.value.startswith("quarantine_"):
        return _report(ShadowFireDecisionKind.QUARANTINE_AUTHORITY_RECEIPTS, False, authority_receipts.watch, "authority receipt mesh quarantined", profile_id=expected_profile_id, service_name=expected_service_name, bridge_action=bridge_epoch.action, component_digests=components, evidence_family_count=authority_receipts.family_count)
    if announcement_repair is not None and announcement_repair.quarantined:
        return _report(ShadowFireDecisionKind.QUARANTINE_REPAIR, False, False, "announcement repair quarantined", profile_id=expected_profile_id, service_name=expected_service_name, bridge_action=bridge_epoch.action, component_digests=components, evidence_family_count=0)
    if not (bridge_epoch.accept and key_receipts.accept and policy_firebreak.accepted and authority_receipts.accepted):
        return _report(ShadowFireDecisionKind.HOLD_COMPONENT_NOT_ACCEPTED, False, policy_firebreak.watch or key_receipts.watch or authority_receipts.watch, "component has not accepted", profile_id=expected_profile_id, service_name=expected_service_name, bridge_action=bridge_epoch.action, component_digests=components, evidence_family_count=max(bridge_epoch.family_count, key_receipts.family_count, policy_firebreak.family_count, authority_receipts.family_count))
    is_public_epoch = bridge_epoch.action in (BridgeEpochAction.OPEN_PUBLIC, BridgeEpochAction.RENEW_PUBLIC)
    if expected_public and not is_public_epoch:
        return _report(ShadowFireDecisionKind.QUARANTINE_ACTION_MISMATCH, False, False, "expected public bridge but epoch is closed", profile_id=expected_profile_id, service_name=expected_service_name, bridge_action=bridge_epoch.action, component_digests=components, evidence_family_count=bridge_epoch.family_count)
    if not expected_public and is_public_epoch:
        return _report(ShadowFireDecisionKind.QUARANTINE_ACTION_MISMATCH, False, False, "expected closed/withdrawn bridge but epoch is public", profile_id=expected_profile_id, service_name=expected_service_name, bridge_action=bridge_epoch.action, component_digests=components, evidence_family_count=bridge_epoch.family_count)
    if not expected_public and (announcement_repair is None or not announcement_repair.accept):
        return _report(ShadowFireDecisionKind.HOLD_REPAIR_REQUIRED, False, False, "closed bridge requires announcement repair", profile_id=expected_profile_id, service_name=expected_service_name, bridge_action=bridge_epoch.action, component_digests=components, evidence_family_count=bridge_epoch.family_count)
    combined_family_count = max(bridge_epoch.family_count, key_receipts.family_count, policy_firebreak.family_count, authority_receipts.family_count)
    if combined_family_count < min_combined_family_count:
        return _report(ShadowFireDecisionKind.HOLD_LOW_EVIDENCE_DIVERSITY, False, key_receipts.watch or policy_firebreak.watch or authority_receipts.watch, "joined shadow fire lacks evidence diversity", profile_id=expected_profile_id, service_name=expected_service_name, bridge_action=bridge_epoch.action, component_digests=components, evidence_family_count=combined_family_count)
    watch = key_receipts.watch or policy_firebreak.watch or authority_receipts.watch
    if watch:
        return _report(ShadowFireDecisionKind.ACCEPT_WITH_WATCH, True, True, "shadow fire accepted with watch pressure", profile_id=expected_profile_id, service_name=expected_service_name, bridge_action=bridge_epoch.action, component_digests=components, evidence_family_count=combined_family_count)
    kind = ShadowFireDecisionKind.ACCEPT_PUBLIC_BRIDGE if expected_public else ShadowFireDecisionKind.ACCEPT_CLOSE_OR_WITHDRAW
    return _report(kind, True, False, "shadow fire accepted at public bridge boundary", profile_id=expected_profile_id, service_name=expected_service_name, bridge_action=bridge_epoch.action, component_digests=components, evidence_family_count=combined_family_count)
