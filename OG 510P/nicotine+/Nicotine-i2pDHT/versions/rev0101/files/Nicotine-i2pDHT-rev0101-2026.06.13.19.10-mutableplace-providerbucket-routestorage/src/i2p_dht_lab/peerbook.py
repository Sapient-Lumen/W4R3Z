"""Peer/address book pressure for entrance growth.

A DHT over I2P needs sticky entrances without letting one seed channel, garden,
or bridge family become the new center.  The peer book here stores observations
of signed contact leases together with the channel that delivered them, then
builds local entrance views only after channel/family/purpose pressure passes.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .bencode import bencode
from .contactlease import ContactLease, ContactLeaseBook, ContactLeasePurpose, ContactLeaseVerdictKind
from .ids import DOMAIN, sha256, xor_distance

PEERBOOK_DOMAIN = DOMAIN + b":peerbook-v1:"


class PeerBookDecisionKind(str, Enum):
    ACCEPT_ENTRANCE_VIEW = "accept_entrance_view"
    ACCEPT_DIVERSE_BOOK = "accept_entrance_view"
    ACCEPT_PEER_BOOK = "accept_entrance_view"
    ACCEPT_WITH_WATCH = "accept_with_watch"
    CONTINUE_NO_VALID_LEASES = "continue_no_valid_leases"
    CONTINUE_LOW_CHANNEL_DIVERSITY = "continue_low_channel_diversity"
    CONTINUE_LOW_FAMILY_DIVERSITY = "continue_low_family_diversity"
    CONTINUE_LOW_PURPOSE_COVERAGE = "continue_low_purpose_coverage"
    QUARANTINE_FORK_PRESSURE = "quarantine_fork_pressure"
    QUARANTINE_LEASE_FORK_PRESSURE = "quarantine_fork_pressure"
    QUARANTINE_LEASE_FORK = "quarantine_fork_pressure"
    QUARANTINE_CHANNEL_MONOCULTURE = "quarantine_channel_monoculture"
    QUARANTINE_INTRODUCER_CAPTURE = "quarantine_channel_monoculture"
    QUARANTINE_SAM_DESTINATION_DRIFT = "quarantine_sam_destination_drift"
    QUARANTINE_SAM_SCRIPT = "quarantine_sam_script"


@dataclass(frozen=True)
class PeerLeaseObservation:
    lease: ContactLease
    channel_id: str
    channel_family: str
    observed_at: int
    observer_note: str = ""

    def __post_init__(self) -> None:
        if not self.channel_id or not self.channel_family:
            raise ValueError("peer lease observation needs channel id/family")
        if self.observed_at < 0:
            raise ValueError("observed_at must be non-negative")

    @property
    def observation_digest(self) -> bytes:
        return sha256(PEERBOOK_DOMAIN + b":observation:" + bencode({
            b"lease": self.lease.lease_hash,
            b"channel_id": self.channel_id,
            b"channel_family": self.channel_family,
            b"observed_at": self.observed_at,
            b"note": self.observer_note[:96],
        }))


@dataclass(frozen=True)
class PeerBookObservation:
    """Compatibility observation shape used by rev0030 join tests.

    ``introducer_family`` maps to the newer ``channel_family``; ``channel`` maps
    to ``channel_id``.  ``path_family`` is kept as typed evidence for callers
    that still distinguish path from channel, but the peer-book view only uses
    the channel family and signed lease family.
    """
    lease: ContactLease
    introducer_family: str
    path_family: str
    channel: str
    observed_at: int
    sam_report: object | None = None

    def as_peer_lease_observation(self) -> PeerLeaseObservation:
        note = self.path_family if self.sam_report is None else f"{self.path_family}:sam"
        return PeerLeaseObservation(self.lease, self.channel, self.introducer_family, self.observed_at, note)

    @property
    def observation_digest(self) -> bytes:
        return self.as_peer_lease_observation().observation_digest


@dataclass(frozen=True)
class PeerBookPolicy:
    min_peer_families: int = 2
    min_channel_families: int = 2
    min_channels: int = 2
    max_per_channel_family: int = 4
    required_purposes: tuple[ContactLeasePurpose, ...] = (ContactLeasePurpose.ROUTE, ContactLeasePurpose.SEED_GATE)
    min_work_bits: int = 0

    def validate(self) -> None:
        if self.min_peer_families <= 0 or self.min_channel_families <= 0 or self.min_channels <= 0 or self.max_per_channel_family <= 0:
            raise ValueError("peerbook diversity thresholds must be positive")


@dataclass(frozen=True)
class PeerBookView:
    decision_kind: PeerBookDecisionKind
    accept: bool
    reason: str
    selected_node_ids: tuple[bytes, ...]
    lease_hashes: tuple[bytes, ...]
    peer_families: tuple[str, ...]
    channel_families: tuple[str, ...]
    purpose_coverage: tuple[str, ...]
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _view(kind: PeerBookDecisionKind, accept: bool, reason: str, selected: Iterable[PeerLeaseObservation]) -> PeerBookView:
    observations = tuple(selected)
    node_ids = tuple(sorted(obs.lease.node_id for obs in observations))
    lease_hashes = tuple(sorted(obs.lease.lease_hash for obs in observations))
    peer_families = tuple(sorted({obs.lease.family_id for obs in observations}))
    channel_families = tuple(sorted({obs.channel_family for obs in observations}))
    purposes = tuple(sorted({purpose.value for obs in observations for purpose in obs.lease.purposes}))
    digest = sha256(PEERBOOK_DOMAIN + b":view:" + bencode({
        b"decision": kind.value,
        b"accept": 1 if accept else 0,
        b"nodes": node_ids,
        b"leases": lease_hashes,
        b"peer_families": peer_families,
        b"channel_families": channel_families,
        b"purposes": purposes,
    }))
    return PeerBookView(kind, accept, reason, node_ids, lease_hashes, peer_families, channel_families, purposes, digest)


def build_peerbook_view(
    observations: Iterable[PeerLeaseObservation],
    *,
    now: int,
    target_id: bytes | None = None,
    policy: PeerBookPolicy | None = None,
) -> PeerBookView:
    policy = policy or PeerBookPolicy()
    policy.validate()
    if target_id is not None and len(target_id) != 32:
        raise ValueError("target_id must be 32 bytes")
    book = ContactLeaseBook()
    valid: list[PeerLeaseObservation] = []
    saw_fork = False
    for observation in sorted(observations, key=lambda obs: (xor_distance(obs.lease.node_id, target_id) if target_id else 0, obs.observed_at, obs.lease.lease_hash)):
        verdict = book.observe(observation.lease, now=now, min_work_bits=policy.min_work_bits)
        if verdict.kind is ContactLeaseVerdictKind.QUARANTINE_SAME_SEQ_FORK:
            saw_fork = True
        if verdict.accepted:
            valid.append(observation)
    if saw_fork:
        return _view(PeerBookDecisionKind.QUARANTINE_FORK_PRESSURE, False, "same-sequence contact lease fork seen while building entrance view", valid)
    if not valid:
        return _view(PeerBookDecisionKind.CONTINUE_NO_VALID_LEASES, False, "no fresh valid signed contact leases", ())
    channel_counts: dict[str, int] = {}
    for obs in valid:
        channel_counts[obs.channel_family] = channel_counts.get(obs.channel_family, 0) + 1
    if any(count > policy.max_per_channel_family for count in channel_counts.values()) and len(channel_counts) < policy.min_channel_families:
        return _view(PeerBookDecisionKind.QUARANTINE_CHANNEL_MONOCULTURE, False, "one entrance channel family dominates the view", valid)
    if len({obs.channel_id for obs in valid}) < policy.min_channels or len(channel_counts) < policy.min_channel_families:
        return _view(PeerBookDecisionKind.CONTINUE_LOW_CHANNEL_DIVERSITY, False, "not enough independent entrance channels", valid)
    if len({obs.lease.family_id for obs in valid}) < policy.min_peer_families:
        return _view(PeerBookDecisionKind.CONTINUE_LOW_FAMILY_DIVERSITY, False, "not enough peer-family diversity", valid)
    covered = {purpose for obs in valid for purpose in obs.lease.purposes}
    missing = [purpose.value for purpose in policy.required_purposes if purpose not in covered]
    if missing:
        return _view(PeerBookDecisionKind.CONTINUE_LOW_PURPOSE_COVERAGE, False, f"missing required purposes: {', '.join(missing)}", valid)
    decision = PeerBookDecisionKind.ACCEPT_ENTRANCE_VIEW if len(valid) >= policy.min_channels + 1 else PeerBookDecisionKind.ACCEPT_WITH_WATCH
    return _view(decision, True, "fresh contact leases have enough local entrance diversity", valid)


# rev0030 compatibility names used by joined bootstrap branchlets.
PeerBookReport = PeerBookView
PeerBookView.selected_count = property(lambda self: len(self.selected_node_ids))  # type: ignore[attr-defined]


def assess_peer_book(
    observations: Iterable[PeerLeaseObservation | PeerBookObservation],
    *,
    target: bytes | None = None,
    target_id: bytes | None = None,
    now: int,
    policy: PeerBookPolicy | None = None,
    min_work_bits: int = 0,
) -> PeerBookView:
    normalized = tuple(obs.as_peer_lease_observation() if isinstance(obs, PeerBookObservation) else obs for obs in observations)
    effective = policy or PeerBookPolicy()
    if min_work_bits and effective.min_work_bits != min_work_bits:
        from dataclasses import replace as _replace
        effective = _replace(effective, min_work_bits=min_work_bits)
    return build_peerbook_view(normalized, now=now, target_id=target_id or target, policy=effective)
