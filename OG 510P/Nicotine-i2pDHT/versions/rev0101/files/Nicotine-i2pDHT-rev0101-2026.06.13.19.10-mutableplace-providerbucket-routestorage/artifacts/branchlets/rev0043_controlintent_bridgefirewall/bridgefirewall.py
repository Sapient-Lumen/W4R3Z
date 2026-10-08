"""Bridge firewall pressure for public garden/bridge exposure.

rev0043 treats public bridge exposure as a local firewall decision.  A public
announcement, a useful ingress window, and a healthy garden service are still
not enough if a bridge-disable, stale announcement, cooldown, or key-crisis
signal is live.  The firewall is intentionally local and conservative: it can
hold/close public exposure without deciding global truth.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256

BRIDGE_FIREWALL_DOMAIN = DOMAIN + b":bridge-firewall-v1:"


class BridgeFirewallMode(str, Enum):
    PUBLIC_BRIDGE = "public_bridge"
    PRIVATE_GARDEN = "private_garden"
    CLOSED_PUBLIC_BRIDGE = "closed_public_bridge"


class BridgeFirewallSignalKind(str, Enum):
    ANNOUNCEMENT = "announcement"
    INGRESS_GATE = "ingress_gate"
    LOAD_SHEATH = "load_sheath"
    SERVICE_HEALTH = "service_health"
    OPERATOR_KEY = "operator_key"
    BRIDGE_DISABLE = "bridge_disable"
    ANNOUNCEMENT_REPAIR = "announcement_repair"
    PROFILE_COOLDOWN = "profile_cooldown"
    HARD_NEGATIVE_SCAN = "hard_negative_scan"
    STALE_PUBLIC_ANNOUNCEMENT = "stale_public_announcement"


class BridgeFirewallDecisionKind(str, Enum):
    ACCEPT_PUBLIC_BRIDGE_WINDOW = "accept_public_bridge_window"
    ACCEPT_PRIVATE_GARDEN_WINDOW = "accept_private_garden_window"
    ACCEPT_CLOSED_PUBLIC_BRIDGE = "accept_closed_public_bridge"
    HOLD_MISSING_REQUIRED_SIGNAL = "hold_missing_required_signal"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_SIGNAL_NOT_ACCEPTED = "hold_signal_not_accepted"
    HOLD_PUBLIC_BRIDGE_DISABLED = "hold_public_bridge_disabled"
    HOLD_COOLDOWN_OR_HARD_NEGATIVE = "hold_cooldown_or_hard_negative"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_EXPIRED_OR_FUTURE = "quarantine_expired_or_future"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PROFILE_DRIFT = "quarantine_profile_drift"
    QUARANTINE_SERVICE_DRIFT = "quarantine_service_drift"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_PUBLIC_EXPOSURE_AFTER_DISABLE = "quarantine_public_exposure_after_disable"
    QUARANTINE_STALE_PUBLIC_ANNOUNCEMENT = "quarantine_stale_public_announcement"
    QUARANTINE_PUBLIC_EXPOSURE_MISMATCH = "quarantine_public_exposure_mismatch"


@dataclass(frozen=True)
class BridgeFirewallSignal:
    kind: BridgeFirewallSignalKind
    profile_id: str
    service_name: str
    scope_digest: bytes
    sequence: int
    report_digest: bytes
    accepted: bool
    public_exposure: bool
    bridge_disabled: bool
    hard_negative_clear: bool
    family_id: str
    path_family: str
    issued_at: int
    expires_at: int
    signer_public_key: bytes
    signature: bytes = b""

    def __post_init__(self) -> None:
        if not self.profile_id or len(self.profile_id.encode("utf-8")) > 80:
            raise ValueError("profile_id must be short and non-empty")
        if not self.service_name or len(self.service_name.encode("utf-8")) > 80:
            raise ValueError("service_name must be short and non-empty")
        if self.sequence < 0:
            raise ValueError("firewall signal sequence must be non-negative")
        if not self.family_id or not self.path_family:
            raise ValueError("firewall signal needs family/path labels")
        if self.expires_at <= self.issued_at:
            raise ValueError("firewall signal expires_at must be after issued_at")
        for name, value in (("scope_digest", self.scope_digest), ("report_digest", self.report_digest), ("signer_public_key", self.signer_public_key)):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if self.signature and len(self.signature) != 64:
            raise ValueError("firewall signal signature must be Ed25519-sized")

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"kind": self.kind.value,
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"scope": self.scope_digest,
            b"seq": self.sequence,
            b"report": self.report_digest,
            b"accepted": 1 if self.accepted else 0,
            b"public_exposure": 1 if self.public_exposure else 0,
            b"bridge_disabled": 1 if self.bridge_disabled else 0,
            b"hard_negative_clear": 1 if self.hard_negative_clear else 0,
            b"family": self.family_id,
            b"path_family": self.path_family,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"signer": self.signer_public_key,
        }

    @property
    def signal_digest(self) -> bytes:
        return sha256(BRIDGE_FIREWALL_DOMAIN + b":signal:" + bencode(self.unsigned_bvalue()))

    def signature_payload(self) -> bytes:
        return BRIDGE_FIREWALL_DOMAIN + b":sig:" + bencode(self.unsigned_bvalue())

    def verifies(self) -> bool:
        return verify_signature(self.signer_public_key, self.signature_payload(), self.signature)


def make_bridge_firewall_signal(
    *,
    keypair: DhtKeypair,
    kind: BridgeFirewallSignalKind,
    profile_id: str,
    service_name: str,
    scope_digest: bytes,
    sequence: int,
    report_digest: bytes,
    accepted: bool = True,
    public_exposure: bool = False,
    bridge_disabled: bool = False,
    hard_negative_clear: bool = True,
    family_id: str,
    path_family: str,
    issued_at: int,
    expires_at: int,
) -> BridgeFirewallSignal:
    signal = BridgeFirewallSignal(
        kind=kind,
        profile_id=profile_id,
        service_name=service_name,
        scope_digest=scope_digest,
        sequence=sequence,
        report_digest=report_digest,
        accepted=accepted,
        public_exposure=public_exposure,
        bridge_disabled=bridge_disabled,
        hard_negative_clear=hard_negative_clear,
        family_id=family_id,
        path_family=path_family,
        issued_at=issued_at,
        expires_at=expires_at,
        signer_public_key=keypair.public_key_bytes,
    )
    return replace(signal, signature=keypair.sign(signal.signature_payload()))


@dataclass(frozen=True)
class BridgeFirewallPolicy:
    min_family_diversity_public: int = 3
    min_path_diversity_public: int = 2
    min_family_diversity_private: int = 2
    required_public_signals: tuple[BridgeFirewallSignalKind, ...] = (
        BridgeFirewallSignalKind.ANNOUNCEMENT,
        BridgeFirewallSignalKind.INGRESS_GATE,
        BridgeFirewallSignalKind.LOAD_SHEATH,
        BridgeFirewallSignalKind.OPERATOR_KEY,
        BridgeFirewallSignalKind.HARD_NEGATIVE_SCAN,
    )
    required_private_signals: tuple[BridgeFirewallSignalKind, ...] = (
        BridgeFirewallSignalKind.ANNOUNCEMENT,
        BridgeFirewallSignalKind.INGRESS_GATE,
        BridgeFirewallSignalKind.LOAD_SHEATH,
    )
    required_closed_signals: tuple[BridgeFirewallSignalKind, ...] = (
        BridgeFirewallSignalKind.BRIDGE_DISABLE,
        BridgeFirewallSignalKind.ANNOUNCEMENT_REPAIR,
        BridgeFirewallSignalKind.HARD_NEGATIVE_SCAN,
    )


@dataclass(frozen=True)
class BridgeFirewallReport:
    decision_kind: BridgeFirewallDecisionKind
    accept: bool
    reason: str
    mode: BridgeFirewallMode
    profile_id: str
    service_name: str
    scope_digest: bytes
    present_signals: tuple[str, ...]
    signal_digests: tuple[bytes, ...]
    pressure_digests: tuple[bytes, ...]
    public_exposure_seen: bool
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _report(kind: BridgeFirewallDecisionKind, accept: bool, reason: str, *, mode: BridgeFirewallMode, profile_id: str, service_name: str, scope_digest: bytes, signals: Iterable[BridgeFirewallSignal], pressures: Iterable[bytes] = ()) -> BridgeFirewallReport:
    sigs = tuple(sorted(signals, key=lambda item: (item.kind.value, item.sequence, item.signal_digest)))
    digests = tuple(sorted(item.signal_digest for item in sigs))
    present = tuple(sorted({item.kind.value for item in sigs}))
    pressure_t = tuple(sorted(set(pressures)))
    public_seen = any(item.public_exposure for item in sigs)
    digest = sha256(BRIDGE_FIREWALL_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"reason": reason,
        b"mode": mode.value,
        b"profile": profile_id,
        b"service": service_name,
        b"scope": scope_digest,
        b"present": list(present),
        b"signals": list(digests),
        b"pressures": list(pressure_t),
        b"public_seen": 1 if public_seen else 0,
    }))
    return BridgeFirewallReport(kind, accept, reason, mode, profile_id, service_name, scope_digest, present, digests, pressure_t, public_seen, digest)


def assess_bridge_firewall(
    signals: Iterable[BridgeFirewallSignal],
    *,
    now: int,
    mode: BridgeFirewallMode,
    expected_profile_id: str,
    expected_service_name: str,
    expected_scope_digest: bytes,
    policy: BridgeFirewallPolicy = BridgeFirewallPolicy(),
    previously_seen_signals: Iterable[bytes] = (),
) -> BridgeFirewallReport:
    """Classify bridge exposure before public ingress or closure side effects."""
    if len(expected_scope_digest) != 32:
        raise ValueError("expected scope digest must be 32 bytes")
    sigs = tuple(sorted(signals, key=lambda item: (item.kind.value, item.sequence, item.signal_digest)))
    seen = set(previously_seen_signals)
    if any(not item.verifies() for item in sigs):
        return _report(BridgeFirewallDecisionKind.QUARANTINE_BAD_SIGNATURE, False, "firewall signal signature failed", mode=mode, profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, signals=sigs)
    if any(item.issued_at > now or item.expires_at <= now for item in sigs):
        return _report(BridgeFirewallDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, False, "firewall signal outside local time window", mode=mode, profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, signals=sigs)
    if any(item.signal_digest in seen for item in sigs):
        return _report(BridgeFirewallDecisionKind.QUARANTINE_REPLAY, False, "firewall signal replay", mode=mode, profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, signals=sigs)
    if any(item.profile_id != expected_profile_id for item in sigs):
        return _report(BridgeFirewallDecisionKind.QUARANTINE_PROFILE_DRIFT, False, "firewall signal profile drift", mode=mode, profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, signals=sigs)
    if any(item.service_name != expected_service_name for item in sigs):
        return _report(BridgeFirewallDecisionKind.QUARANTINE_SERVICE_DRIFT, False, "firewall signal service drift", mode=mode, profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, signals=sigs)
    if any(item.scope_digest != expected_scope_digest for item in sigs):
        return _report(BridgeFirewallDecisionKind.QUARANTINE_SCOPE_DRIFT, False, "firewall signal scope drift", mode=mode, profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, signals=sigs)
    by_kind_sequence: dict[tuple[BridgeFirewallSignalKind, int], set[bytes]] = {}
    for item in sigs:
        by_kind_sequence.setdefault((item.kind, item.sequence), set()).add(item.signal_digest)
    if any(len(digests) > 1 for digests in by_kind_sequence.values()):
        return _report(BridgeFirewallDecisionKind.QUARANTINE_SEQUENCE_FORK, False, "same-kind same-sequence firewall signal fork", mode=mode, profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, signals=sigs)

    if any(item.kind is BridgeFirewallSignalKind.STALE_PUBLIC_ANNOUNCEMENT and item.accepted and item.public_exposure for item in sigs):
        return _report(BridgeFirewallDecisionKind.QUARANTINE_STALE_PUBLIC_ANNOUNCEMENT, False, "stale public announcement remains visible", mode=mode, profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, signals=sigs)
    bridge_disabled = any(item.kind is BridgeFirewallSignalKind.BRIDGE_DISABLE and item.accepted and item.bridge_disabled for item in sigs)
    dirty = tuple(item for item in sigs if not item.hard_negative_clear)
    if dirty:
        return _report(BridgeFirewallDecisionKind.HOLD_COOLDOWN_OR_HARD_NEGATIVE, False, "firewall sees cooldown or hard-negative pressure", mode=mode, profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, signals=sigs, pressures=(dirty[0].signal_digest,))

    if bridge_disabled and mode is BridgeFirewallMode.PUBLIC_BRIDGE:
        if any(item.public_exposure for item in sigs):
            return _report(BridgeFirewallDecisionKind.QUARANTINE_PUBLIC_EXPOSURE_AFTER_DISABLE, False, "public exposure signal survived bridge-disable", mode=mode, profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, signals=sigs)
        return _report(BridgeFirewallDecisionKind.HOLD_PUBLIC_BRIDGE_DISABLED, False, "public bridge is disabled", mode=mode, profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, signals=sigs)

    required = policy.required_public_signals if mode is BridgeFirewallMode.PUBLIC_BRIDGE else policy.required_private_signals if mode is BridgeFirewallMode.PRIVATE_GARDEN else policy.required_closed_signals
    present = {item.kind for item in sigs}
    missing = tuple(kind for kind in required if kind not in present)
    if missing:
        return _report(BridgeFirewallDecisionKind.HOLD_MISSING_REQUIRED_SIGNAL, False, "firewall missing required signal", mode=mode, profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, signals=sigs, pressures=tuple(kind.value.encode("utf-8") for kind in missing))
    required_sigs = tuple(item for item in sigs if item.kind in set(required))
    rejected = tuple(item for item in required_sigs if not item.accepted)
    if rejected:
        return _report(BridgeFirewallDecisionKind.HOLD_SIGNAL_NOT_ACCEPTED, False, "firewall required signal was not accepted", mode=mode, profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, signals=sigs, pressures=(rejected[0].signal_digest,))

    families = {item.family_id for item in required_sigs}
    path_families = {item.path_family for item in required_sigs}
    if mode is BridgeFirewallMode.PUBLIC_BRIDGE:
        if not any(item.public_exposure and item.kind is BridgeFirewallSignalKind.ANNOUNCEMENT for item in required_sigs) or not any(item.public_exposure and item.kind is BridgeFirewallSignalKind.INGRESS_GATE for item in required_sigs):
            return _report(BridgeFirewallDecisionKind.QUARANTINE_PUBLIC_EXPOSURE_MISMATCH, False, "public bridge mode requires public announcement and ingress", mode=mode, profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, signals=sigs)
        if len(families) < policy.min_family_diversity_public or len(path_families) < policy.min_path_diversity_public:
            return _report(BridgeFirewallDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, "public bridge lacks family/path diversity", mode=mode, profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, signals=sigs)
        return _report(BridgeFirewallDecisionKind.ACCEPT_PUBLIC_BRIDGE_WINDOW, True, "public bridge window accepted through local firewall", mode=mode, profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, signals=sigs)
    if mode is BridgeFirewallMode.PRIVATE_GARDEN:
        if any(item.public_exposure for item in required_sigs):
            return _report(BridgeFirewallDecisionKind.QUARANTINE_PUBLIC_EXPOSURE_MISMATCH, False, "private garden window cannot carry public exposure", mode=mode, profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, signals=sigs)
        if len(families) < policy.min_family_diversity_private:
            return _report(BridgeFirewallDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, "private garden lacks family diversity", mode=mode, profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, signals=sigs)
        return _report(BridgeFirewallDecisionKind.ACCEPT_PRIVATE_GARDEN_WINDOW, True, "private garden window accepted while public bridge policy remains local", mode=mode, profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, signals=sigs)
    if not bridge_disabled:
        return _report(BridgeFirewallDecisionKind.HOLD_MISSING_REQUIRED_SIGNAL, False, "closed mode requires live bridge-disable signal", mode=mode, profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, signals=sigs)
    return _report(BridgeFirewallDecisionKind.ACCEPT_CLOSED_PUBLIC_BRIDGE, True, "closed public bridge accepted with repair and hard-negative scan", mode=mode, profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, signals=sigs)
