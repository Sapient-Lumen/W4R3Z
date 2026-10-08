"""Repeated bridge-ledger chaos pressure.

rev0047 joins the moderation/redress bridge ledger with policy portfolios and
privacy budgets across restart windows.  The aim is not to produce global truth;
it is to stop a valid one-shot bridge ledger from becoming a sticky public bridge
side effect after replay, flapping, stale policy, or privacy leakage.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .bridgeledger import BridgeLedgerAction, BridgeLedgerReport
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .moderationquarantine import ModerationQuarantineReport, ZERO_DIGEST
from .policyportfolio import PolicyPortfolioReport
from .redresslane import RedressReport
from .redressprivacy import RedressPrivacyReport

BRIDGE_CHAOS_DOMAIN = DOMAIN + b":bridge-chaos-v1:"


class BridgeChaosDecisionKind(str, Enum):
    ACCEPT_STABLE_WINDOW = "accept_stable_window"
    ACCEPT_WITH_WATCH = "accept_with_watch"
    HOLD_MISSING_OBSERVATION = "hold_missing_observation"
    HOLD_BRIDGE_LEDGER = "hold_bridge_ledger"
    HOLD_POLICY_PORTFOLIO = "hold_policy_portfolio"
    HOLD_REDRESS_PRIVACY = "hold_redress_privacy"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    HOLD_NEEDS_MORE_WINDOWS = "hold_needs_more_windows"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_EXPIRED_OR_FUTURE = "quarantine_expired_or_future"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_PROFILE_DRIFT = "quarantine_profile_drift"
    QUARANTINE_SERVICE_DRIFT = "quarantine_service_drift"
    QUARANTINE_ACTION_DRIFT = "quarantine_action_drift"
    QUARANTINE_COMPONENT_DIGEST_DRIFT = "quarantine_component_digest_drift"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_RESTART_REPLAY = "quarantine_restart_replay"
    QUARANTINE_SIDE_EFFECT_COLLISION = "quarantine_side_effect_collision"
    QUARANTINE_POLICY_BLOCK_UNREDRESSED = "quarantine_policy_block_unredressed"
    QUARANTINE_MODERATION_BLOCK_UNREDRESSED = "quarantine_moderation_block_unredressed"
    QUARANTINE_PRIVACY_LEAK = "quarantine_privacy_leak"
    QUARANTINE_FLAPPING_LOOP = "quarantine_flapping_loop"


@dataclass(frozen=True)
class BridgeChaosObservation:
    profile_id: str
    service_name: str
    action: BridgeLedgerAction
    bridge_ledger_digest: bytes
    policy_portfolio_digest: bytes
    redress_privacy_digest: bytes
    moderation_digest: bytes
    redress_digest: bytes
    side_effect_digest: bytes
    restart_id: str
    sequence: int
    previous_observation_digest: bytes
    issued_at: int
    expires_at: int
    family_id: str
    path_family: str
    signer_public_key: bytes
    signature: bytes = b""

    def __post_init__(self) -> None:
        if not self.profile_id or len(self.profile_id.encode("utf-8")) > 80:
            raise ValueError("profile_id must be short and non-empty")
        if not self.service_name or len(self.service_name.encode("utf-8")) > 96:
            raise ValueError("service_name must be short and non-empty")
        if not self.restart_id or len(self.restart_id.encode("utf-8")) > 96:
            raise ValueError("restart_id must be short and non-empty")
        if self.sequence < 0:
            raise ValueError("bridge chaos observation sequence must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("expires_at must be after issued_at")
        if not self.family_id or not self.path_family:
            raise ValueError("family_id and path_family must be non-empty")
        for name, value in (
            ("bridge_ledger_digest", self.bridge_ledger_digest),
            ("policy_portfolio_digest", self.policy_portfolio_digest),
            ("redress_privacy_digest", self.redress_privacy_digest),
            ("moderation_digest", self.moderation_digest),
            ("redress_digest", self.redress_digest),
            ("side_effect_digest", self.side_effect_digest),
            ("previous_observation_digest", self.previous_observation_digest),
            ("signer_public_key", self.signer_public_key),
        ):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if self.signature and len(self.signature) != 64:
            raise ValueError("signature must be Ed25519-sized")
        object.__setattr__(self, "action", BridgeLedgerAction(self.action))

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"action": self.action.value,
            b"ledger": self.bridge_ledger_digest,
            b"policy": self.policy_portfolio_digest,
            b"privacy": self.redress_privacy_digest,
            b"moderation": self.moderation_digest,
            b"redress": self.redress_digest,
            b"effect": self.side_effect_digest,
            b"restart": self.restart_id,
            b"seq": self.sequence,
            b"prev": self.previous_observation_digest,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"family": self.family_id,
            b"path_family": self.path_family,
            b"signer": self.signer_public_key,
        }

    def signature_payload(self) -> bytes:
        return BRIDGE_CHAOS_DOMAIN + b":observation-sig:" + bencode(self.unsigned_bvalue())

    @property
    def observation_core_digest(self) -> bytes:
        return sha256(BRIDGE_CHAOS_DOMAIN + b":observation-core:" + bencode({
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"action": self.action.value,
            b"ledger": self.bridge_ledger_digest,
            b"policy": self.policy_portfolio_digest,
            b"privacy": self.redress_privacy_digest,
            b"moderation": self.moderation_digest,
            b"redress": self.redress_digest,
            b"effect": self.side_effect_digest,
            b"restart": self.restart_id,
            b"seq": self.sequence,
            b"prev": self.previous_observation_digest,
        }))

    @property
    def observation_digest(self) -> bytes:
        return sha256(BRIDGE_CHAOS_DOMAIN + b":observation-digest:" + self.signature_payload() + self.signature)

    def verifies(self) -> bool:
        return verify_signature(self.signer_public_key, self.signature_payload(), self.signature)


@dataclass(frozen=True)
class BridgeChaosReport:
    decision_kind: BridgeChaosDecisionKind
    accept: bool
    watch: bool
    reason: str
    profile_id: str
    service_name: str
    action: BridgeLedgerAction
    observation_digests: tuple[bytes, ...]
    component_digests: tuple[bytes, ...]
    family_count: int
    path_family_count: int
    restart_count: int
    highest_sequence: int
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")



def make_bridge_chaos_observation(
    *,
    keypair: DhtKeypair,
    profile_id: str,
    service_name: str,
    action: BridgeLedgerAction,
    bridge_ledger_digest: bytes,
    policy_portfolio_digest: bytes,
    redress_privacy_digest: bytes = ZERO_DIGEST,
    moderation_digest: bytes = ZERO_DIGEST,
    redress_digest: bytes = ZERO_DIGEST,
    side_effect_digest: bytes,
    restart_id: str,
    sequence: int,
    previous_observation_digest: bytes = ZERO_DIGEST,
    issued_at: int,
    expires_at: int,
    family_id: str,
    path_family: str,
) -> BridgeChaosObservation:
    observation = BridgeChaosObservation(profile_id, service_name, action, bridge_ledger_digest, policy_portfolio_digest, redress_privacy_digest, moderation_digest, redress_digest, side_effect_digest, restart_id, sequence, previous_observation_digest, issued_at, expires_at, family_id, path_family, keypair.public_key_bytes)
    return replace(observation, signature=keypair.sign(observation.signature_payload()))



def _report(kind: BridgeChaosDecisionKind, accept: bool, watch: bool, reason: str, *, profile_id: str, service_name: str, action: BridgeLedgerAction, observations: Iterable[BridgeChaosObservation] = (), components: Iterable[bytes] = (), family_count: int = 0, path_family_count: int = 0, restart_count: int = 0, highest_sequence: int = -1) -> BridgeChaosReport:
    observation_tuple = tuple(sorted(observations, key=lambda item: (item.sequence, item.observation_digest)))
    observation_digests = tuple(sorted(item.observation_digest for item in observation_tuple if accept or watch or kind.value.startswith("hold_")))
    component_tuple = tuple(sorted(set(components)))
    digest = sha256(BRIDGE_CHAOS_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"reason": reason,
        b"profile": profile_id,
        b"service": service_name,
        b"action": action.value,
        b"observations": list(observation_digests),
        b"components": list(component_tuple),
        b"families": family_count,
        b"paths": path_family_count,
        b"restarts": restart_count,
        b"highest": highest_sequence,
    }))
    return BridgeChaosReport(kind, accept, watch, reason, profile_id, service_name, action, observation_digests, component_tuple, family_count, path_family_count, restart_count, highest_sequence, digest)



def assess_bridge_chaos_window(
    observations: Iterable[BridgeChaosObservation],
    *,
    bridge_ledger: BridgeLedgerReport,
    policy_portfolio: PolicyPortfolioReport,
    redress_privacy: RedressPrivacyReport | None,
    moderation: ModerationQuarantineReport | None,
    redress: RedressReport | None,
    now: int,
    expected_profile_id: str,
    expected_service_name: str,
    action: BridgeLedgerAction,
    previous_sequence: int | None = None,
    previous_observation_digest: bytes | None = None,
    previously_seen_observations: Iterable[bytes] = (),
    recent_actions: Iterable[BridgeLedgerAction] = (),
    min_family_diversity: int = 2,
    min_path_diversity: int = 2,
    min_restart_windows: int = 1,
    allow_watch: bool = False,
) -> BridgeChaosReport:
    action = BridgeLedgerAction(action)
    privacy_digest = redress_privacy.report_digest if redress_privacy is not None else ZERO_DIGEST
    moderation_digest = moderation.report_digest if moderation is not None else ZERO_DIGEST
    redress_digest = redress.report_digest if redress is not None else ZERO_DIGEST
    components = [bridge_ledger.report_digest, policy_portfolio.report_digest, privacy_digest, moderation_digest, redress_digest]
    if not bridge_ledger.accept:
        return _report(BridgeChaosDecisionKind.HOLD_BRIDGE_LEDGER, False, False, "bridge ledger has not accepted", profile_id=expected_profile_id, service_name=expected_service_name, action=action, components=components)
    if not policy_portfolio.accept:
        # Ordinary holds remain holds.  A subjective DENY/FREEZE can be lifted
        # only when a scoped redress report and privacy report survive their
        # own gates.  Other portfolio quarantines stay quarantines.
        if policy_portfolio.blocked:
            has_lift = redress is not None and redress.lifted and (redress_privacy is None or redress_privacy.accept)
            if not has_lift:
                return _report(BridgeChaosDecisionKind.QUARANTINE_POLICY_BLOCK_UNREDRESSED, False, policy_portfolio.watch, "blocking policy pressure lacks lifted redress", profile_id=expected_profile_id, service_name=expected_service_name, action=action, components=components)
        elif policy_portfolio.quarantined:
            return _report(BridgeChaosDecisionKind.QUARANTINE_POLICY_BLOCK_UNREDRESSED, False, policy_portfolio.watch, "policy portfolio quarantined", profile_id=expected_profile_id, service_name=expected_service_name, action=action, components=components)
        else:
            return _report(BridgeChaosDecisionKind.HOLD_POLICY_PORTFOLIO, False, policy_portfolio.watch, "policy portfolio not locally acceptable", profile_id=expected_profile_id, service_name=expected_service_name, action=action, components=components)
    if redress_privacy is not None and not redress_privacy.accept:
        kind = BridgeChaosDecisionKind.QUARANTINE_PRIVACY_LEAK if redress_privacy.quarantined else BridgeChaosDecisionKind.HOLD_REDRESS_PRIVACY
        return _report(kind, False, redress_privacy.watch, "redress privacy gate not acceptable", profile_id=expected_profile_id, service_name=expected_service_name, action=action, components=components)
    if policy_portfolio.blocked and (redress is None or not redress.lifted):
        return _report(BridgeChaosDecisionKind.QUARANTINE_POLICY_BLOCK_UNREDRESSED, False, True, "blocking policy pressure lacks lifted redress", profile_id=expected_profile_id, service_name=expected_service_name, action=action, components=components)
    if moderation is not None and moderation.blocked and (redress is None or not redress.lifted):
        return _report(BridgeChaosDecisionKind.QUARANTINE_MODERATION_BLOCK_UNREDRESSED, False, True, "blocking moderation pressure lacks lifted redress", profile_id=expected_profile_id, service_name=expected_service_name, action=action, components=components)
    action_tuple = tuple(BridgeLedgerAction(item) for item in recent_actions)
    if len(action_tuple) >= 3 and len(set(action_tuple[-3:] + (action,))) > 1:
        return _report(BridgeChaosDecisionKind.QUARANTINE_FLAPPING_LOOP, False, True, "bridge action flapping across recent windows", profile_id=expected_profile_id, service_name=expected_service_name, action=action, components=components)
    observation_tuple = tuple(sorted(observations, key=lambda item: (item.sequence, item.observation_digest)))
    if not observation_tuple:
        return _report(BridgeChaosDecisionKind.HOLD_MISSING_OBSERVATION, False, False, "missing bridge chaos observation", profile_id=expected_profile_id, service_name=expected_service_name, action=action, components=components)
    seen = set(previously_seen_observations)
    fork_guard: dict[tuple[bytes, int], bytes] = {}
    restart_effects: dict[str, bytes] = {}
    for observation in observation_tuple:
        if not observation.verifies():
            return _report(BridgeChaosDecisionKind.QUARANTINE_BAD_SIGNATURE, False, False, "bad bridge chaos observation signature", profile_id=expected_profile_id, service_name=expected_service_name, action=action, observations=observation_tuple, components=components)
        if observation.issued_at > now or observation.expires_at <= now:
            return _report(BridgeChaosDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, False, False, "bridge chaos observation expired or future", profile_id=expected_profile_id, service_name=expected_service_name, action=action, observations=observation_tuple, components=components)
        if observation.observation_digest in seen:
            return _report(BridgeChaosDecisionKind.QUARANTINE_REPLAY, False, False, "bridge chaos observation replay", profile_id=expected_profile_id, service_name=expected_service_name, action=action, observations=observation_tuple, components=components)
        if observation.profile_id != expected_profile_id or bridge_ledger.profile_id != expected_profile_id or policy_portfolio.profile_id != expected_profile_id:
            return _report(BridgeChaosDecisionKind.QUARANTINE_PROFILE_DRIFT, False, False, "bridge chaos profile drift", profile_id=expected_profile_id, service_name=expected_service_name, action=action, observations=observation_tuple, components=components)
        if observation.service_name != expected_service_name or bridge_ledger.service_name != expected_service_name or policy_portfolio.service_name != expected_service_name:
            return _report(BridgeChaosDecisionKind.QUARANTINE_SERVICE_DRIFT, False, False, "bridge chaos service drift", profile_id=expected_profile_id, service_name=expected_service_name, action=action, observations=observation_tuple, components=components)
        if observation.action is not action or bridge_ledger.action is not action:
            return _report(BridgeChaosDecisionKind.QUARANTINE_ACTION_DRIFT, False, False, "bridge chaos action drift", profile_id=expected_profile_id, service_name=expected_service_name, action=action, observations=observation_tuple, components=components)
        if observation.bridge_ledger_digest != bridge_ledger.report_digest or observation.policy_portfolio_digest != policy_portfolio.report_digest or observation.redress_privacy_digest != privacy_digest or observation.moderation_digest != moderation_digest or observation.redress_digest != redress_digest:
            return _report(BridgeChaosDecisionKind.QUARANTINE_COMPONENT_DIGEST_DRIFT, False, False, "bridge chaos component digest drift", profile_id=expected_profile_id, service_name=expected_service_name, action=action, observations=observation_tuple, components=components)
        if previous_sequence is not None:
            if observation.sequence <= previous_sequence:
                return _report(BridgeChaosDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, False, "bridge chaos sequence rollback", profile_id=expected_profile_id, service_name=expected_service_name, action=action, observations=observation_tuple, components=components)
            if previous_observation_digest is not None and observation.previous_observation_digest != previous_observation_digest:
                return _report(BridgeChaosDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, False, "bridge chaos previous digest mismatch", profile_id=expected_profile_id, service_name=expected_service_name, action=action, observations=observation_tuple, components=components)
        key = (observation.signer_public_key, observation.sequence)
        old = fork_guard.get(key)
        if old is not None and old != observation.observation_core_digest:
            return _report(BridgeChaosDecisionKind.QUARANTINE_SEQUENCE_FORK, False, False, "bridge chaos same-signer fork", profile_id=expected_profile_id, service_name=expected_service_name, action=action, observations=observation_tuple, components=components)
        fork_guard[key] = observation.observation_core_digest
        old_effect = restart_effects.get(observation.restart_id)
        if old_effect is not None and old_effect != observation.side_effect_digest:
            return _report(BridgeChaosDecisionKind.QUARANTINE_RESTART_REPLAY, False, False, "same restart window produced conflicting side effects", profile_id=expected_profile_id, service_name=expected_service_name, action=action, observations=observation_tuple, components=components)
        restart_effects[observation.restart_id] = observation.side_effect_digest
    highest = max(observation.sequence for observation in observation_tuple)
    active = tuple(observation for observation in observation_tuple if observation.sequence == highest)
    families = {observation.family_id for observation in active}
    paths = {observation.path_family for observation in active}
    restart_count = len({observation.restart_id for observation in active})
    if restart_count < min_restart_windows:
        return _report(BridgeChaosDecisionKind.HOLD_NEEDS_MORE_WINDOWS, False, True, "more restart windows needed before sticky public side effect", profile_id=expected_profile_id, service_name=expected_service_name, action=action, observations=active, components=components, family_count=len(families), path_family_count=len(paths), restart_count=restart_count, highest_sequence=highest)
    if len(families) < min_family_diversity:
        return _report(BridgeChaosDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, "low bridge chaos family diversity", profile_id=expected_profile_id, service_name=expected_service_name, action=action, observations=active, components=components, family_count=len(families), path_family_count=len(paths), restart_count=restart_count, highest_sequence=highest)
    if len(paths) < min_path_diversity:
        return _report(BridgeChaosDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, "low bridge chaos path diversity", profile_id=expected_profile_id, service_name=expected_service_name, action=action, observations=active, components=components, family_count=len(families), path_family_count=len(paths), restart_count=restart_count, highest_sequence=highest)
    watch = bridge_ledger.watch or policy_portfolio.watch or bool(redress_privacy and redress_privacy.watch)
    if watch and not allow_watch:
        return _report(BridgeChaosDecisionKind.ACCEPT_WITH_WATCH, True, True, "bridge chaos window accepted with watch pressure", profile_id=expected_profile_id, service_name=expected_service_name, action=action, observations=active, components=components, family_count=len(families), path_family_count=len(paths), restart_count=restart_count, highest_sequence=highest)
    return _report(BridgeChaosDecisionKind.ACCEPT_STABLE_WINDOW, True, watch, "bridge chaos window accepted", profile_id=expected_profile_id, service_name=expected_service_name, action=action, observations=active, components=components, family_count=len(families), path_family_count=len(paths), restart_count=restart_count, highest_sequence=highest)
