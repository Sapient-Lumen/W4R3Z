"""Router harness capsule for bundle-first / external-SAM startup.

rev0035 keeps live I2P/SAM out of scope, but treats router configuration as a
security boundary.  A future node should not turn a successful launch quorum
into network side effects unless the router harness says the local assumptions
are explicit: persistent destination, local SAM endpoint unless explicitly
allowed, no accidental HTTP/SOCKS proxy exposure, and bundle-first transit
participation rather than a default notransit island.

This module is a no-network classifier, not a router manager.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .bencode import bencode
from .ids import DOMAIN, sha256
from .samprobe import SAM_PROBE_DOMAIN, SamProbeDecisionKind, SamProbeReport

ROUTER_HARNESS_DOMAIN = DOMAIN + b":router-harness-v1:"
LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1"}
ZERO_DIGEST = b"\x00" * 32


class RouterHarnessMode(str, Enum):
    BUNDLED_I2PD = "bundled_i2pd"
    EXTERNAL_SAM = "external_sam"
    OFFLINE_NO_ROUTER = "offline_no_router"


class RouterHarnessDecisionKind(str, Enum):
    ACCEPT_BUNDLED_I2PD_HARNESS = "accept_bundled_i2pd_harness"
    ACCEPT_EXTERNAL_SAM_HARNESS = "accept_external_sam_harness"
    ACCEPT_OFFLINE_DESIGN_HARNESS = "accept_offline_design_harness"
    HOLD_ROUTER_UNAVAILABLE = "hold_router_unavailable"
    HOLD_SESSION_ONLY = "hold_session_only"
    QUARANTINE_SAM_PROBE = "quarantine_sam_probe"
    QUARANTINE_CONFIG_DIGEST_MISMATCH = "quarantine_config_digest_mismatch"
    QUARANTINE_EPHEMERAL_DESTINATION = "quarantine_ephemeral_destination"
    QUARANTINE_PROXY_EXPOSURE = "quarantine_proxy_exposure"
    QUARANTINE_NOTRANSIT_BUNDLE = "quarantine_notransit_bundle"
    QUARANTINE_EXTERNAL_ENDPOINT = "quarantine_external_endpoint"
    QUARANTINE_MODE_ENDPOINT_DRIFT = "quarantine_mode_endpoint_drift"


@dataclass(frozen=True)
class RouterHarnessConfig:
    mode: RouterHarnessMode
    host: str = "127.0.0.1"
    port: int = 7656
    datadir_digest: bytes = ZERO_DIGEST
    destination_digest: bytes = ZERO_DIGEST
    generated_config_digest: bytes = ZERO_DIGEST
    expected_config_digest: bytes = ZERO_DIGEST
    transit_enabled: bool = True
    http_proxy_disabled: bool = True
    socks_proxy_disabled: bool = True
    allow_external_endpoint: bool = False
    allow_session_only: bool = False

    def __post_init__(self) -> None:
        if self.port <= 0 or self.port > 65535:
            raise ValueError("router harness port must be a TCP port")
        for name, value in (
            ("datadir_digest", self.datadir_digest),
            ("destination_digest", self.destination_digest),
            ("generated_config_digest", self.generated_config_digest),
            ("expected_config_digest", self.expected_config_digest),
        ):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")

    @property
    def endpoint_digest(self) -> bytes:
        return sha256(SAM_PROBE_DOMAIN + b":endpoint:" + f"{self.host}:{self.port}".encode("utf-8"))

    @property
    def profile_digest(self) -> bytes:
        return sha256(ROUTER_HARNESS_DOMAIN + b":profile:" + bencode({
            b"mode": self.mode.value,
            b"endpoint": self.endpoint_digest,
            b"datadir": self.datadir_digest,
            b"destination": self.destination_digest,
            b"generated_config": self.generated_config_digest,
            b"expected_config": self.expected_config_digest,
            b"transit_enabled": 1 if self.transit_enabled else 0,
            b"http_proxy_disabled": 1 if self.http_proxy_disabled else 0,
            b"socks_proxy_disabled": 1 if self.socks_proxy_disabled else 0,
            b"allow_external_endpoint": 1 if self.allow_external_endpoint else 0,
            b"allow_session_only": 1 if self.allow_session_only else 0,
        }))


@dataclass(frozen=True)
class RouterHarnessReport:
    decision_kind: RouterHarnessDecisionKind
    accept: bool
    reason: str
    profile_digest: bytes
    endpoint_digest: bytes
    sam_probe_transcript_digest: bytes
    pressure_digests: tuple[bytes, ...]
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _report(kind: RouterHarnessDecisionKind, accept: bool, reason: str, *, config: RouterHarnessConfig, sam_probe: SamProbeReport, pressures: Iterable[bytes] = ()) -> RouterHarnessReport:
    pressure_t = tuple(sorted(set(pressures)))
    digest = sha256(ROUTER_HARNESS_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"reason": reason,
        b"profile": config.profile_digest,
        b"endpoint": config.endpoint_digest,
        b"sam": sam_probe.transcript_digest,
        b"pressures": pressure_t,
    }))
    return RouterHarnessReport(kind, accept, reason, config.profile_digest, config.endpoint_digest, sam_probe.transcript_digest, pressure_t, digest)


def assess_router_harness(config: RouterHarnessConfig, sam_probe: SamProbeReport, *, previously_seen_reports: Iterable[bytes] = ()) -> RouterHarnessReport:
    """Classify router assumptions before a future launch can touch I2P."""
    prior = set(previously_seen_reports)
    if sam_probe.transcript_digest in prior:
        return _report(RouterHarnessDecisionKind.QUARANTINE_SAM_PROBE, False, "SAM probe transcript was replayed at router harness boundary", config=config, sam_probe=sam_probe, pressures=(sam_probe.transcript_digest,))
    if config.expected_config_digest != ZERO_DIGEST and config.generated_config_digest != config.expected_config_digest:
        return _report(RouterHarnessDecisionKind.QUARANTINE_CONFIG_DIGEST_MISMATCH, False, "generated router config does not match expected capsule digest", config=config, sam_probe=sam_probe, pressures=(config.generated_config_digest, config.expected_config_digest))
    if config.mode is not RouterHarnessMode.OFFLINE_NO_ROUTER:
        if config.datadir_digest == ZERO_DIGEST or config.destination_digest == ZERO_DIGEST:
            return _report(RouterHarnessDecisionKind.QUARANTINE_EPHEMERAL_DESTINATION, False, "router harness requires persistent datadir and destination before live launch", config=config, sam_probe=sam_probe, pressures=(config.datadir_digest, config.destination_digest))
        if not config.http_proxy_disabled or not config.socks_proxy_disabled:
            return _report(RouterHarnessDecisionKind.QUARANTINE_PROXY_EXPOSURE, False, "router harness refuses accidental HTTP/SOCKS proxy exposure", config=config, sam_probe=sam_probe, pressures=(config.profile_digest,))
        if config.host not in LOOPBACK_HOSTS and not config.allow_external_endpoint:
            return _report(RouterHarnessDecisionKind.QUARANTINE_EXTERNAL_ENDPOINT, False, "router harness refuses non-loopback SAM endpoint unless explicitly allowed", config=config, sam_probe=sam_probe, pressures=(config.endpoint_digest,))
    if config.mode is RouterHarnessMode.BUNDLED_I2PD and not config.transit_enabled:
        return _report(RouterHarnessDecisionKind.QUARANTINE_NOTRANSIT_BUNDLE, False, "bundle-first router must not default to notransit island mode", config=config, sam_probe=sam_probe, pressures=(config.profile_digest,))
    if sam_probe.endpoint_digest != config.endpoint_digest:
        return _report(RouterHarnessDecisionKind.QUARANTINE_MODE_ENDPOINT_DRIFT, False, "SAM probe endpoint does not match router harness endpoint", config=config, sam_probe=sam_probe, pressures=(sam_probe.endpoint_digest, config.endpoint_digest))
    if not sam_probe.accept or sam_probe.quarantined:
        return _report(RouterHarnessDecisionKind.QUARANTINE_SAM_PROBE, False, "SAM probe was not locally acceptable before router harness", config=config, sam_probe=sam_probe, pressures=(sam_probe.transcript_digest,))
    if sam_probe.decision_kind is SamProbeDecisionKind.ACCEPT_LOCAL_UNAVAILABLE:
        if config.mode is RouterHarnessMode.OFFLINE_NO_ROUTER:
            return _report(RouterHarnessDecisionKind.ACCEPT_OFFLINE_DESIGN_HARNESS, True, "offline design harness accepted explicit local-unavailable router outcome", config=config, sam_probe=sam_probe)
        return _report(RouterHarnessDecisionKind.HOLD_ROUTER_UNAVAILABLE, False, "router unavailable is explicit but not accepted for live harness mode", config=config, sam_probe=sam_probe, pressures=(sam_probe.transcript_digest,))
    if sam_probe.decision_kind is SamProbeDecisionKind.ACCEPT_SESSION_ONLY and not config.allow_session_only:
        return _report(RouterHarnessDecisionKind.HOLD_SESSION_ONLY, False, "router harness requires streaming proof unless session-only is explicit", config=config, sam_probe=sam_probe, pressures=(sam_probe.transcript_digest,))
    if config.mode is RouterHarnessMode.BUNDLED_I2PD:
        return _report(RouterHarnessDecisionKind.ACCEPT_BUNDLED_I2PD_HARNESS, True, "bundle-first router harness accepted persistent streaming-first profile", config=config, sam_probe=sam_probe)
    if config.mode is RouterHarnessMode.EXTERNAL_SAM:
        return _report(RouterHarnessDecisionKind.ACCEPT_EXTERNAL_SAM_HARNESS, True, "external SAM router harness accepted under explicit endpoint policy", config=config, sam_probe=sam_probe)
    return _report(RouterHarnessDecisionKind.ACCEPT_OFFLINE_DESIGN_HARNESS, True, "offline design harness accepted non-live startup", config=config, sam_probe=sam_probe)
