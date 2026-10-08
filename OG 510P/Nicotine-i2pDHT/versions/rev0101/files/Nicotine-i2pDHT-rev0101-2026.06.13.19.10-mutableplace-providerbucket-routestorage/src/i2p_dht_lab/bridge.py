"""Classic-client bridge sketches for an I2P DHT.

A future DHT may need to serve people who only have an old protocol client.  The
bridge is a giving garden service: it can accept classic-style requests and
translate them into DHT lookups, but it must not become a new root of truth.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .governance import PolicyAction, PolicyDecision
from .sovereignty import MetadataPosture, ParticipationMode


class BridgeMode(str, Enum):
    OFF = "off"
    LOCALHOST_COMPAT_SHIM = "localhost_compat_shim"
    PRIVATE_INVITE_GATEWAY = "private_invite_gateway"
    PUBLIC_GARDEN_GATEWAY = "public_garden_gateway"


class ClassicOperation(str, Enum):
    LOGIN_COMPAT = "login_compat"
    SEARCH = "search"
    BROWSE = "browse"
    PEER_CONNECT = "peer_connect"
    CHAT_RELAY = "chat_relay"
    PROVIDER_ANNOUNCE = "provider_announce"


class BridgeRisk(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    REFUSE = "refuse"


@dataclass(frozen=True)
class BridgeBudget:
    mode: BridgeMode
    max_classic_clients: int
    upload_kib_s: int
    max_queries_per_minute: int
    max_provider_announces_per_hour: int
    metadata_posture: MetadataPosture = MetadataPosture.CONNECTIVE
    require_invite_for_write: bool = True
    accept_policy_capsules: bool = True


@dataclass(frozen=True)
class BridgeServiceOffer:
    mode: BridgeMode
    operations: tuple[ClassicOperation, ...]
    risk: BridgeRisk
    warnings: tuple[str, ...]
    contribution_tags: tuple[str, ...]

    def supports(self, operation: ClassicOperation) -> bool:
        return operation in self.operations


@dataclass(frozen=True)
class BridgeDecision:
    allowed: bool
    reason: str
    risk: BridgeRisk


def plan_bridge_service(budget: BridgeBudget) -> BridgeServiceOffer:
    if budget.mode is BridgeMode.OFF or budget.max_classic_clients <= 0:
        return BridgeServiceOffer(BridgeMode.OFF, (), BridgeRisk.REFUSE, ("bridge_disabled",), ())

    operations = {ClassicOperation.LOGIN_COMPAT, ClassicOperation.SEARCH, ClassicOperation.BROWSE, ClassicOperation.PEER_CONNECT}
    warnings = ["bridge_answers_are_gateway_results_not_dht_truth"]
    tags = ["classic_entrance", "mutual_aid_gateway"]
    risk = BridgeRisk.MEDIUM

    if budget.mode is BridgeMode.PUBLIC_GARDEN_GATEWAY:
        warnings.append("public_gateway_needs_rate_limits_and_policy_capsules")
        tags.append("public_garden")
        risk = BridgeRisk.HIGH
    if budget.metadata_posture is MetadataPosture.BRIDGE_HELPER:
        operations.add(ClassicOperation.CHAT_RELAY)
        warnings.append("chat_relay_is_metadata_heavy")
        risk = BridgeRisk.HIGH
    if budget.require_invite_for_write:
        warnings.append("write_surfaces_require_invite_or_local_trust")
    else:
        operations.add(ClassicOperation.PROVIDER_ANNOUNCE)
        warnings.append("open_provider_announces_are_poisoning_risk")
        risk = BridgeRisk.HIGH

    if budget.max_queries_per_minute < 10 or budget.upload_kib_s < 256:
        warnings.append("budget_too_low_for_public_bridge")
        risk = BridgeRisk.MEDIUM if budget.mode is BridgeMode.LOCALHOST_COMPAT_SHIM else BridgeRisk.HIGH

    return BridgeServiceOffer(
        budget.mode,
        tuple(sorted(operations, key=lambda operation: operation.value)),
        risk,
        tuple(warnings),
        tuple(sorted(tags)),
    )


def decide_bridge_operation(
    offer: BridgeServiceOffer,
    operation: ClassicOperation,
    *,
    policy_decision: PolicyDecision | None = None,
    authenticated_invite: bool = False,
) -> BridgeDecision:
    if offer.mode is BridgeMode.OFF:
        return BridgeDecision(False, "bridge_disabled", BridgeRisk.REFUSE)
    if policy_decision is not None and policy_decision.action in {
        PolicyAction.DENY_BRIDGE,
        PolicyAction.IGNORE,
        PolicyAction.DENY_STORE,
        PolicyAction.DENY_OFFICIAL_SURFACE,
    }:
        return BridgeDecision(False, f"policy_refused:{policy_decision.reason}", BridgeRisk.REFUSE)
    if not offer.supports(operation):
        return BridgeDecision(False, "operation_not_supported_by_bridge_offer", BridgeRisk.REFUSE)
    if operation is ClassicOperation.PROVIDER_ANNOUNCE and not authenticated_invite:
        return BridgeDecision(False, "provider_announces_need_invite", BridgeRisk.HIGH)
    if operation is ClassicOperation.CHAT_RELAY and offer.risk is BridgeRisk.HIGH and not authenticated_invite:
        return BridgeDecision(False, "chat_relay_needs_invite", BridgeRisk.HIGH)
    return BridgeDecision(True, "accepted_by_bridge_offer", offer.risk)


def bridge_guardrails() -> tuple[str, ...]:
    return (
        "classic_bridge_is_optional_default_off",
        "classic_bridge_is_a_gateway_not_an_authority",
        "public_write_surfaces_need_invites_or_rate_limits",
        "bridge_results_must_be_labeled_as_translated",
        "bridges_should_never_require_central_server_login",
        "bridges_may_subscribe_to_policy_capsules",
        "i2p_only_mode_must_not_silently_connect_to_classic_servers",
    )


def mode_buys_sovereignty(mode: ParticipationMode, bridge: BridgeMode) -> bool:
    return mode is ParticipationMode.I2P_ONLY and bridge in {
        BridgeMode.OFF,
        BridgeMode.LOCALHOST_COMPAT_SHIM,
        BridgeMode.PRIVATE_INVITE_GATEWAY,
        BridgeMode.PUBLIC_GARDEN_GATEWAY,
    }
