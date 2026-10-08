"""Lease/live-probe join pressure for sticky DHT entrances.

A signed contact lease is entrance memory, not reachability.  rev0031 keeps two
prototype surfaces in one module: a joined entrance judgment over peerbook,
live-probe, SAM-smoke, and negative-space evidence, plus a small no-network
challenge/response transcript for future transport experiments.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Any, Iterable

from .bencode import BValue, bencode
from .contactlease import ContactLease, ContactLeasePurpose
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, destination_hash, sha256
from .liveprobe import LiveProbeDecisionKind, LiveProbeReport
from .livesmoke import SamLiveSmokeReport, SamSmokeDecisionKind
from .negspace import NegspaceReport
from .peerbook import PeerBookView

LEASE_PROBE_DOMAIN = DOMAIN + b":lease-probe-v1:"


class LeaseProbeDecisionKind(str, Enum):
    # Joined lease/liveness surface.
    ACCEPT_PROBED_ENTRANCE = "accept_probed_entrance"
    ACCEPT_CLEAN_SKIP_WITH_WATCH = "accept_clean_skip_with_watch"
    WATCH_UNPROBED_CONTACT = "watch_unprobed_contact"
    CONTINUE_PEERBOOK_NOT_READY = "continue_peerbook_not_ready"
    CONTINUE_NEGATIVE_ABSENCE = "continue_negative_absence"
    QUARANTINE_LEASE_INVALID = "quarantine_lease_invalid"
    QUARANTINE_LIVE_PROBE = "quarantine_live_probe"
    QUARANTINE_SAM_SMOKE = "quarantine_sam_smoke"
    QUARANTINE_NEGATIVE_CONTRADICTION = "quarantine_negative_contradiction"
    QUARANTINE_PEERBOOK_CAPTURE = "quarantine_peerbook_capture"
    QUARANTINE_DESTINATION_DRIFT = "quarantine_destination_drift"
    # No-network challenge/response surface.
    ACCEPT_REACHABLE_LEASE = "accept_reachable_lease"
    ACCEPT_WITH_WATCH = "accept_with_watch"
    CONTINUE_NO_VALID_RESPONSE = "continue_no_valid_response"
    CONTINUE_LOW_PATH_DIVERSITY = "continue_low_path_diversity"
    CONTINUE_LOW_RESPONDER_DIVERSITY = "continue_low_responder_diversity"
    REJECT_STALE_LEASE = "reject_stale_lease"
    REJECT_PURPOSE_MISMATCH = "reject_purpose_mismatch"
    REJECT_BAD_CHALLENGE = "reject_bad_challenge"
    REJECT_EXPIRED_RESPONSE = "reject_expired_response"
    QUARANTINE_REPLAYED_RESPONSE = "quarantine_replayed_response"
    QUARANTINE_FAMILY_MONOCULTURE = "quarantine_family_monoculture"


@dataclass(frozen=True)
class LeaseProbePolicy:
    require_peerbook_acceptance: bool = True
    allow_clean_skip_watch: bool = True
    require_live_probe_for_accept: bool = True
    required_purpose: ContactLeasePurpose = ContactLeasePurpose.ROUTE
    min_path_families: int = 2
    min_responder_families: int = 1
    max_per_responder_family: int = 3
    min_work_bits: int = 0

    def validate(self) -> None:
        if self.min_path_families <= 0 or self.min_responder_families <= 0 or self.max_per_responder_family <= 0:
            raise ValueError("lease-probe diversity limits must be positive")


@dataclass(frozen=True)
class LeaseProbeReport:
    decision_kind: LeaseProbeDecisionKind
    accept: bool
    watch: bool
    reason: str
    lease_hash: bytes = b""
    peerbook_digest: bytes = b""
    live_digest: bytes = b""
    smoke_digest: bytes = b""
    negspace_digest: bytes = b""
    valid_response_digests: tuple[bytes, ...] = ()
    path_families: tuple[str, ...] = ()
    responder_families: tuple[str, ...] = ()
    bad_response_digests: tuple[bytes, ...] = ()
    report_digest: bytes = b""

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")

    @property
    def needs_more_work(self) -> bool:
        return self.decision_kind.value.startswith("continue_") or self.watch


def _maybe_digest(obj: Any, *attrs: str) -> bytes:
    if obj is None:
        return b""
    for attr in attrs:
        value = getattr(obj, attr, None)
        if isinstance(value, bytes):
            return value
    return sha256(repr(obj).encode("utf-8"))


def _join_report(
    *,
    kind: LeaseProbeDecisionKind,
    accept: bool,
    watch: bool,
    reason: str,
    lease: ContactLease,
    peerbook: PeerBookView | None,
    live: LiveProbeReport | None,
    smoke: SamLiveSmokeReport | None,
    negspace: NegspaceReport | None,
) -> LeaseProbeReport:
    peerbook_digest = _maybe_digest(peerbook, "report_digest")
    live_digest = _maybe_digest(live, "report_digest", "transcript_digest")
    smoke_digest = _maybe_digest(smoke, "transcript_digest", "report_digest")
    negspace_digest = _maybe_digest(negspace, "report_digest")
    digest = sha256(LEASE_PROBE_DOMAIN + b":join-report:" + bencode({
        b"decision": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"lease_hash": lease.lease_hash,
        b"peerbook": peerbook_digest,
        b"live": live_digest,
        b"smoke": smoke_digest,
        b"negspace": negspace_digest,
        b"reason": reason,
    }))
    return LeaseProbeReport(kind, accept, watch, reason, lease.lease_hash, peerbook_digest, live_digest, smoke_digest, negspace_digest, report_digest=digest)


def assess_lease_probe_join(
    *,
    lease: ContactLease,
    now: int,
    peerbook: PeerBookView | None = None,
    live: LiveProbeReport | None = None,
    smoke: SamLiveSmokeReport | None = None,
    negspace: NegspaceReport | None = None,
    policy: LeaseProbePolicy | None = None,
) -> LeaseProbeReport:
    policy = policy or LeaseProbePolicy()
    if not lease.verify(now=now):
        return _join_report(kind=LeaseProbeDecisionKind.QUARANTINE_LEASE_INVALID, accept=False, watch=False, reason="contact lease is not fresh/signature-valid/identity-bound", lease=lease, peerbook=peerbook, live=live, smoke=smoke, negspace=negspace)
    if peerbook is not None and peerbook.quarantined:
        return _join_report(kind=LeaseProbeDecisionKind.QUARANTINE_PEERBOOK_CAPTURE, accept=False, watch=False, reason=f"peerbook quarantined selected contact: {peerbook.reason}", lease=lease, peerbook=peerbook, live=live, smoke=smoke, negspace=negspace)
    if policy.require_peerbook_acceptance and peerbook is not None and not peerbook.accept:
        return _join_report(kind=LeaseProbeDecisionKind.CONTINUE_PEERBOOK_NOT_READY, accept=False, watch=True, reason=f"peerbook has not accepted this entrance view: {peerbook.reason}", lease=lease, peerbook=peerbook, live=live, smoke=smoke, negspace=negspace)
    if peerbook is not None and peerbook.accept and lease.node_id not in set(peerbook.selected_node_ids):
        return _join_report(kind=LeaseProbeDecisionKind.CONTINUE_PEERBOOK_NOT_READY, accept=False, watch=True, reason="peerbook accepted a view, but not this exact lease node", lease=lease, peerbook=peerbook, live=live, smoke=smoke, negspace=negspace)
    if negspace is not None and negspace.quarantined:
        return _join_report(kind=LeaseProbeDecisionKind.QUARANTINE_NEGATIVE_CONTRADICTION, accept=False, watch=False, reason=f"negative-space evidence is contradictory/quarantined: {negspace.reason}", lease=lease, peerbook=peerbook, live=live, smoke=smoke, negspace=negspace)
    if live is not None and live.quarantined:
        kind = LeaseProbeDecisionKind.QUARANTINE_DESTINATION_DRIFT if live.decision_kind is LiveProbeDecisionKind.QUARANTINE_DESTINATION_DRIFT else LeaseProbeDecisionKind.QUARANTINE_LIVE_PROBE
        return _join_report(kind=kind, accept=False, watch=False, reason=f"live probe quarantined: {live.reason}", lease=lease, peerbook=peerbook, live=live, smoke=smoke, negspace=negspace)
    if smoke is not None and smoke.quarantined:
        kind = LeaseProbeDecisionKind.QUARANTINE_DESTINATION_DRIFT if smoke.decision_kind is SamSmokeDecisionKind.QUARANTINE_DESTINATION_DRIFT else LeaseProbeDecisionKind.QUARANTINE_SAM_SMOKE
        return _join_report(kind=kind, accept=False, watch=False, reason=f"SAM smoke quarantined: {smoke.reason}", lease=lease, peerbook=peerbook, live=live, smoke=smoke, negspace=negspace)
    live_positive = live is not None and live.ok and not live.clean_skip
    smoke_positive = smoke is not None and smoke.accept and not smoke.skipped
    positive_liveness = live_positive or smoke_positive
    clean_skip = (live is not None and live.clean_skip and live.ok) or (smoke is not None and smoke.skipped and smoke.accept)
    if negspace is not None and negspace.accept:
        if positive_liveness:
            return _join_report(kind=LeaseProbeDecisionKind.QUARANTINE_NEGATIVE_CONTRADICTION, accept=False, watch=False, reason="positive liveness and accepted absence were seen for the same lease window", lease=lease, peerbook=peerbook, live=live, smoke=smoke, negspace=negspace)
        return _join_report(kind=LeaseProbeDecisionKind.CONTINUE_NEGATIVE_ABSENCE, accept=False, watch=True, reason="diverse absence slows this entrance but does not prove it dead", lease=lease, peerbook=peerbook, live=live, smoke=smoke, negspace=negspace)
    if positive_liveness:
        return _join_report(kind=LeaseProbeDecisionKind.ACCEPT_PROBED_ENTRANCE, accept=True, watch=False, reason="fresh lease has coherent positive liveness evidence", lease=lease, peerbook=peerbook, live=live, smoke=smoke, negspace=negspace)
    if clean_skip and policy.allow_clean_skip_watch:
        return _join_report(kind=LeaseProbeDecisionKind.ACCEPT_CLEAN_SKIP_WITH_WATCH, accept=True, watch=True, reason="router absence/session skip is clean; keep entrance sticky but watched", lease=lease, peerbook=peerbook, live=live, smoke=smoke, negspace=negspace)
    if policy.require_live_probe_for_accept:
        return _join_report(kind=LeaseProbeDecisionKind.WATCH_UNPROBED_CONTACT, accept=False, watch=True, reason="fresh lease has not yet been probed at the joined boundary", lease=lease, peerbook=peerbook, live=live, smoke=smoke, negspace=negspace)
    return _join_report(kind=LeaseProbeDecisionKind.ACCEPT_CLEAN_SKIP_WITH_WATCH, accept=True, watch=True, reason="policy allows lease-only sticky watch", lease=lease, peerbook=peerbook, live=live, smoke=smoke, negspace=negspace)


@dataclass(frozen=True)
class LeaseProbeChallenge:
    requester_public_key: bytes
    lease_hash: bytes
    node_id: bytes
    purpose: ContactLeasePurpose
    nonce: bytes
    requester_family: str
    issued_at: int
    expires_at: int
    signature: bytes = b""

    @classmethod
    def create(cls, *, requester_keypair: DhtKeypair, lease: ContactLease, purpose: ContactLeasePurpose, nonce: bytes, requester_family: str, issued_at: int, ttl: int = 120) -> "LeaseProbeChallenge":
        unsigned = cls(requester_keypair.public_key_bytes, lease.lease_hash, lease.node_id, purpose, nonce, requester_family, issued_at, issued_at + ttl)
        return replace(unsigned, signature=requester_keypair.sign(unsigned.unsigned_payload()))

    def unsigned_bvalue(self) -> dict[bytes, object]:
        return {b"requester_public_key": self.requester_public_key, b"lease_hash": self.lease_hash, b"node_id": self.node_id, b"purpose": self.purpose.value, b"nonce": self.nonce, b"requester_family": self.requester_family, b"issued_at": self.issued_at, b"expires_at": self.expires_at}

    def unsigned_payload(self) -> bytes:
        return LEASE_PROBE_DOMAIN + b":challenge-unsigned:" + bencode(self.unsigned_bvalue())

    @property
    def challenge_digest(self) -> bytes:
        return sha256(LEASE_PROBE_DOMAIN + b":challenge:" + self.unsigned_payload() + self.signature)

    def verify(self, *, now: int) -> bool:
        return self.issued_at <= now < self.expires_at and verify_signature(self.requester_public_key, self.unsigned_payload(), self.signature)


@dataclass(frozen=True)
class LeaseProbeResponse:
    lease_hash: bytes
    challenge_digest: bytes
    node_id: bytes
    destination_digest: bytes
    public_key: bytes
    responder_family: str
    path_family: str
    observed_at: int
    expires_at: int
    transcript_digest: bytes
    signature: bytes = b""

    @classmethod
    def create(cls, *, keypair: DhtKeypair, lease: ContactLease, challenge: LeaseProbeChallenge, responder_family: str, path_family: str, observed_at: int, transcript_digest: bytes | None = None, ttl: int = 120) -> "LeaseProbeResponse":
        unsigned = cls(lease.lease_hash, challenge.challenge_digest, lease.node_id, destination_hash(lease.destination), lease.public_key, responder_family, path_family, observed_at, observed_at + ttl, transcript_digest or sha256(LEASE_PROBE_DOMAIN + b":transcript:" + challenge.challenge_digest + lease.lease_hash))
        return replace(unsigned, signature=keypair.sign(unsigned.unsigned_payload()))

    def unsigned_bvalue(self) -> dict[bytes, object]:
        return {b"lease_hash": self.lease_hash, b"challenge_digest": self.challenge_digest, b"node_id": self.node_id, b"destination_digest": self.destination_digest, b"public_key": self.public_key, b"responder_family": self.responder_family, b"path_family": self.path_family, b"observed_at": self.observed_at, b"expires_at": self.expires_at, b"transcript_digest": self.transcript_digest}

    def unsigned_payload(self) -> bytes:
        return LEASE_PROBE_DOMAIN + b":response-unsigned:" + bencode(self.unsigned_bvalue())

    @property
    def response_digest(self) -> bytes:
        return sha256(LEASE_PROBE_DOMAIN + b":response:" + self.unsigned_payload() + self.signature)

    def verify_for(self, *, lease: ContactLease, challenge: LeaseProbeChallenge, now: int) -> bool:
        if not (self.observed_at <= now < self.expires_at):
            return False
        if self.lease_hash != lease.lease_hash or self.challenge_digest != challenge.challenge_digest:
            return False
        if self.node_id != lease.node_id or self.public_key != lease.public_key or self.destination_digest != destination_hash(lease.destination):
            return False
        return verify_signature(self.public_key, self.unsigned_payload(), self.signature)


def assess_lease_probe(*, lease: ContactLease, challenge: LeaseProbeChallenge, responses: Iterable[LeaseProbeResponse], now: int, policy: LeaseProbePolicy | None = None) -> LeaseProbeReport:
    policy = policy or LeaseProbePolicy()
    policy.validate()
    if not lease.verify(now=now, min_work_bits=policy.min_work_bits):
        return LeaseProbeReport(LeaseProbeDecisionKind.REJECT_STALE_LEASE, False, False, "lease is stale, invalid, or below work threshold", lease_hash=lease.lease_hash)
    if not lease.has_purpose(policy.required_purpose) or challenge.purpose is not policy.required_purpose:
        return LeaseProbeReport(LeaseProbeDecisionKind.REJECT_PURPOSE_MISMATCH, False, False, "lease or challenge does not bind the required purpose", lease_hash=lease.lease_hash)
    if challenge.lease_hash != lease.lease_hash or challenge.node_id != lease.node_id or not challenge.verify(now=now):
        return LeaseProbeReport(LeaseProbeDecisionKind.REJECT_BAD_CHALLENGE, False, False, "challenge is not fresh, signed, and lease-bound", lease_hash=lease.lease_hash)
    seen: set[bytes] = set()
    valid: list[LeaseProbeResponse] = []
    bad: list[LeaseProbeResponse] = []
    replay = False
    drift = False
    for response in responses:
        if response.response_digest in seen:
            replay = True
        seen.add(response.response_digest)
        if response.lease_hash == lease.lease_hash and response.challenge_digest == challenge.challenge_digest and (response.node_id != lease.node_id or response.public_key != lease.public_key or response.destination_digest != destination_hash(lease.destination)):
            drift = True
            bad.append(response)
        elif response.verify_for(lease=lease, challenge=challenge, now=now):
            valid.append(response)
        else:
            bad.append(response)
    valid_digests = tuple(sorted(r.response_digest for r in valid))
    bad_digests = tuple(sorted(r.response_digest for r in bad))
    paths = tuple(sorted({r.path_family for r in valid}))
    responders = tuple(sorted({r.responder_family for r in valid}))
    if replay:
        kind, accept, reason = LeaseProbeDecisionKind.QUARANTINE_REPLAYED_RESPONSE, False, "same response digest replayed inside window"
    elif drift:
        kind, accept, reason = LeaseProbeDecisionKind.QUARANTINE_DESTINATION_DRIFT, False, "response did not bind advertised destination"
    elif not valid:
        kind, accept, reason = LeaseProbeDecisionKind.CONTINUE_NO_VALID_RESPONSE, False, "no fresh lease-key response proved reachability"
    elif len(paths) < policy.min_path_families:
        kind, accept, reason = LeaseProbeDecisionKind.CONTINUE_LOW_PATH_DIVERSITY, False, "reachability proof has too little path diversity"
    else:
        kind, accept, reason = (LeaseProbeDecisionKind.ACCEPT_REACHABLE_LEASE if len(valid) >= policy.min_path_families + 1 else LeaseProbeDecisionKind.ACCEPT_WITH_WATCH), True, "lease reached through enough local path pressure"
    digest = sha256(LEASE_PROBE_DOMAIN + b":response-report:" + bencode({b"decision": kind.value, b"valid": valid_digests, b"bad": bad_digests, b"paths": paths, b"responders": responders}))
    return LeaseProbeReport(kind, accept, kind is LeaseProbeDecisionKind.ACCEPT_WITH_WATCH, reason, lease_hash=lease.lease_hash, valid_response_digests=valid_digests, path_families=paths, responder_families=responders, bad_response_digests=bad_digests, report_digest=digest)
