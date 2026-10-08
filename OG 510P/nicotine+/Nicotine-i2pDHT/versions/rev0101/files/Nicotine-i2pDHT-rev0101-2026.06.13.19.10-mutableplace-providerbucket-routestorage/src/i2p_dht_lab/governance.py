"""Subjective governance and key-ban scaffolding for an I2P DHT.

The point of this module is not to make a central authority for the DHT.  It is
an explicit trust surface: a client, bridge, seed list, or garden node may choose
to subscribe to signed policy capsules.  A default FLOSS app could ship a
maintainer key and use it to protect official bridges and bootstraps, while
allowing users to disable or replace that policy.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .bencode import bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, key_id
from .sovereignty import ContactCard, ParticipationMode

BANLIST_DOMAIN = DOMAIN + b":subjective-banlist-v1:"
MAX_REASON_BYTES = 96
MAX_BAN_ENTRIES = 100_000


class BanScope(str, Enum):
    OFFICIAL_BOOTSTRAP = "official_bootstrap"
    GARDEN_SERVICE = "garden_service"
    CLASSIC_BRIDGE = "classic_bridge"
    APP_DEFAULT_WARN = "app_default_warn"
    APP_DEFAULT_IGNORE = "app_default_ignore"
    DHT_STORE_DENY = "dht_store_deny"


class BanReason(str, Enum):
    KEY_COMPROMISE = "key_compromise"
    MALWARE_OR_EXPLOIT = "malware_or_exploit"
    FLOODING_OR_DOS = "flooding_or_dos"
    FALSE_PROVIDER_POISONING = "false_provider_poisoning"
    BRIDGE_ABUSE = "bridge_abuse"
    SPAM_OR_HARASSMENT = "spam_or_harassment"
    POLICY_RESERVED = "policy_reserved"


class PolicyAction(str, Enum):
    ALLOW = "allow"
    WARN = "warn"
    DENY_OFFICIAL_SURFACE = "deny_official_surface"
    DENY_BRIDGE = "deny_bridge"
    DENY_GARDEN = "deny_garden"
    DENY_STORE = "deny_store"
    IGNORE = "ignore"


@dataclass(frozen=True)
class BanEntry:
    public_key: bytes
    scopes: tuple[BanScope, ...]
    reason: BanReason
    issued_at: int
    expires_at: int
    note: str = ""
    evidence_hash: bytes = b""

    def validate_shape(self, *, now: int | None = None) -> bool:
        if len(self.public_key) != 32 or not self.scopes:
            return False
        if len(self.note.encode("utf-8")) > MAX_REASON_BYTES:
            return False
        if self.expires_at <= self.issued_at:
            return False
        if now is None:
            now = int(time.time())
        return now < self.expires_at

    def payload(self) -> dict[bytes, object]:
        return {
            b"public_key": self.public_key,
            b"scopes": tuple(scope.value.encode("utf-8") for scope in self.scopes),
            b"reason": self.reason.value.encode("utf-8"),
            b"issued_at": self.issued_at,
            b"expires_at": self.expires_at,
            b"note": self.note.encode("utf-8"),
            b"evidence_hash": self.evidence_hash,
        }


@dataclass(frozen=True)
class PolicyCapsule:
    """Signed list of keys a particular authority asks clients to distrust."""

    authority_name: str
    authority_public_key: bytes
    sequence: int
    issued_at: int
    expires_at: int
    entries: tuple[BanEntry, ...]
    mode_hint: str = "advisory-default"
    signature: bytes = b""

    @classmethod
    def create(
        cls,
        *,
        authority_name: str,
        authority_keypair: DhtKeypair,
        sequence: int,
        issued_at: int | None = None,
        ttl: int = 24 * 3600,
        entries: Iterable[BanEntry] = (),
        mode_hint: str = "advisory-default",
    ) -> "PolicyCapsule":
        if issued_at is None:
            issued_at = int(time.time())
        capsule = cls(
            authority_name=authority_name,
            authority_public_key=authority_keypair.public_key_bytes,
            sequence=sequence,
            issued_at=issued_at,
            expires_at=issued_at + ttl,
            entries=tuple(entries),
            mode_hint=mode_hint,
        )
        return replace(capsule, signature=authority_keypair.sign(capsule.unsigned_payload()))

    def unsigned_payload(self) -> bytes:
        if len(self.entries) > MAX_BAN_ENTRIES:
            raise ValueError("too many policy entries")
        entries = tuple(entry.payload() for entry in self.entries)
        return BANLIST_DOMAIN + bencode({
            b"authority_name": self.authority_name.encode("utf-8"),
            b"authority_public_key": self.authority_public_key,
            b"sequence": self.sequence,
            b"issued_at": self.issued_at,
            b"expires_at": self.expires_at,
            b"mode_hint": self.mode_hint.encode("utf-8"),
            b"entries": entries,
        })

    @property
    def capsule_hash(self) -> bytes:
        return key_id("policy-capsule", self.unsigned_payload() + self.signature)

    def verify(self, *, now: int | None = None, trusted_authority_key: bytes | None = None) -> bool:
        if len(self.authority_public_key) != 32 or self.sequence < 0:
            return False
        if trusted_authority_key is not None and trusted_authority_key != self.authority_public_key:
            return False
        if self.expires_at <= self.issued_at:
            return False
        if now is None:
            now = int(time.time())
        if now >= self.expires_at:
            return False
        if not all(entry.validate_shape(now=now) for entry in self.entries):
            return False
        return verify_signature(self.authority_public_key, self.unsigned_payload(), self.signature)

    def scopes_for_key(self, public_key: bytes, *, now: int | None = None) -> tuple[BanScope, ...]:
        if not self.verify(now=now):
            return ()
        scopes: set[BanScope] = set()
        for entry in self.entries:
            if entry.public_key == public_key and entry.validate_shape(now=now):
                scopes.update(entry.scopes)
        return tuple(sorted(scopes, key=lambda scope: scope.value))


@dataclass(frozen=True)
class PolicyDecision:
    action: PolicyAction
    reason: str
    matched_scopes: tuple[BanScope, ...] = ()
    authority: str = ""

    @property
    def allowed(self) -> bool:
        return self.action in {PolicyAction.ALLOW, PolicyAction.WARN}


def decide_card_policy(
    card: ContactCard,
    *,
    capsules: Iterable[PolicyCapsule],
    mode: ParticipationMode,
    now: int,
    official_surface: bool = False,
) -> PolicyDecision:
    """Apply subscribed policy capsules to a contact card.

    This is intentionally subjective.  The DHT can still carry records from a
    banned key; this function says whether this local app/bridge/garden should
    use the key in a particular surface.
    """

    collected: list[tuple[PolicyCapsule, tuple[BanScope, ...]]] = []
    for capsule in capsules:
        scopes = capsule.scopes_for_key(card.public_key, now=now)
        if scopes:
            collected.append((capsule, scopes))
    if not collected:
        return PolicyDecision(PolicyAction.ALLOW, "no_matching_policy")

    authority, scopes = collected[0]
    scope_set = set(scopes)
    if BanScope.APP_DEFAULT_IGNORE in scope_set:
        return PolicyDecision(PolicyAction.IGNORE, "app_default_ignore_key", scopes, authority.authority_name)
    if BanScope.DHT_STORE_DENY in scope_set:
        return PolicyDecision(PolicyAction.DENY_STORE, "deny_local_dht_store", scopes, authority.authority_name)
    if official_surface and BanScope.OFFICIAL_BOOTSTRAP in scope_set:
        return PolicyDecision(PolicyAction.DENY_OFFICIAL_SURFACE, "deny_official_bootstrap_surface", scopes, authority.authority_name)
    if mode is ParticipationMode.GARDEN and BanScope.GARDEN_SERVICE in scope_set:
        return PolicyDecision(PolicyAction.DENY_GARDEN, "deny_garden_service_selection", scopes, authority.authority_name)
    if BanScope.CLASSIC_BRIDGE in scope_set:
        return PolicyDecision(PolicyAction.DENY_BRIDGE, "deny_classic_bridge_surface", scopes, authority.authority_name)
    if BanScope.APP_DEFAULT_WARN in scope_set:
        return PolicyDecision(PolicyAction.WARN, "warn_for_subscribed_policy", scopes, authority.authority_name)
    return PolicyDecision(PolicyAction.ALLOW, "policy_scoped_elsewhere", scopes, authority.authority_name)


def governance_guardrails() -> tuple[str, ...]:
    return (
        "policy_capsules_are_subjective_not_dht_truth",
        "users_can_disable_or_replace_default_authorities",
        "bans_must_target_keys_not_names",
        "official_surfaces_may_refuse_without_erasing_records",
        "bridges_and_gardens_can_refuse_service",
        "mutable_publishers_keep_signature_authority_over_their_slots",
        "capsules_expire_and_require_monotonic_sequences",
    )
