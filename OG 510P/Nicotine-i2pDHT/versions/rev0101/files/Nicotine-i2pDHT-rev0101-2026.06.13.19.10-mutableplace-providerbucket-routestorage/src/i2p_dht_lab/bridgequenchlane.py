"""Bridge quench lane for repeated public-exposure pressure.

The uncomfortable public-bridge failure mode is not only a single bad publish.
It is repeated plausible refreshes that keep stale public entrances alive while
witnesses, withdrawals, hard negatives, and refusal loops are trying to slow the
node down.  rev0047 treats quench/cooldown as a typed local side effect.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .publicationledger import PublicationLedgerReport

BRIDGE_QUENCH_DOMAIN = DOMAIN + b":bridge-quench-lane-v1:"


class QuenchObservationKind(str, Enum):
    PUBLICATION_ACCEPTED = "publication_accepted"
    PUBLICATION_WATCH = "publication_watch"
    STALE_PUBLIC_REPLAY = "stale_public_replay"
    FALSE_SERVICE_PROOF = "false_service_proof"
    HARD_NEGATIVE = "hard_negative"
    APPEAL_WATCH_LOOP = "appeal_watch_loop"
    REFUSAL_ONLY = "refusal_only"
    WITHDRAWAL_CONFIRMED = "withdrawal_confirmed"


class BridgeQuenchDecisionKind(str, Enum):
    ACCEPT_CONTINUE = "accept_continue"
    ACCEPT_WITH_WATCH = "accept_with_watch"
    ACCEPT_QUENCH = "accept_quench"
    QUENCH_STALE_PUBLIC_REPLAY = "accept_quench"
    HOLD_PUBLICATION_NOT_ACCEPTED = "hold_publication_not_accepted"
    HOLD_COOLDOWN = "hold_cooldown"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    QUARANTINE_PUBLICATION = "quarantine_publication"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_EXPIRED_OR_FUTURE = "quarantine_expired_or_future"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_PROFILE_DRIFT = "quarantine_profile_drift"
    QUARANTINE_SERVICE_DRIFT = "quarantine_service_drift"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_REQUEST_DRIFT = "quarantine_request_drift"
    QUARANTINE_PUBLICATION_DIGEST_DRIFT = "quarantine_publication_digest_drift"
    QUARANTINE_FAMILY_CAPTURE = "quarantine_family_capture"


@dataclass(frozen=True)
class QuenchObservation:
    kind: QuenchObservationKind
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    publication_digest: bytes
    evidence_digest: bytes
    window_id: str
    accepted: bool
    watch: bool
    issued_at: int
    expires_at: int
    family_id: str
    path_family: str
    signer_public_key: bytes
    signature: bytes = b""

    def __post_init__(self) -> None:
        object.__setattr__(self, "kind", QuenchObservationKind(self.kind))
        if not self.profile_id or not self.service_name or not self.window_id or not self.family_id or not self.path_family:
            raise ValueError("quench observation needs profile/service/window/family/path")
        if self.expires_at <= self.issued_at:
            raise ValueError("expires_at must be greater than issued_at")
        for name, value in (
            ("scope_digest", self.scope_digest),
            ("request_digest", self.request_digest),
            ("publication_digest", self.publication_digest),
            ("evidence_digest", self.evidence_digest),
            ("signer_public_key", self.signer_public_key),
        ):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if self.signature and len(self.signature) != 64:
            raise ValueError("signature must be Ed25519-sized")

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"kind": self.kind.value,
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"publication": self.publication_digest,
            b"evidence": self.evidence_digest,
            b"window": self.window_id,
            b"accepted": 1 if self.accepted else 0,
            b"watch": 1 if self.watch else 0,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"family": self.family_id,
            b"path_family": self.path_family,
            b"signer": self.signer_public_key,
        }

    def signature_payload(self) -> bytes:
        return BRIDGE_QUENCH_DOMAIN + b":observation-sig:" + bencode(self.unsigned_bvalue())

    @property
    def observation_digest(self) -> bytes:
        return sha256(BRIDGE_QUENCH_DOMAIN + b":observation-digest:" + self.signature_payload() + self.signature)

    def verifies(self) -> bool:
        return verify_signature(self.signer_public_key, self.signature_payload(), self.signature)


@dataclass(frozen=True)
class BridgeQuenchReport:
    decision_kind: BridgeQuenchDecisionKind
    continue_publication: bool
    quench: bool
    watch: bool
    reason: str
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    publication_digest: bytes
    observation_digests: tuple[bytes, ...]
    family_count: int
    path_family_count: int
    stale_replay_count: int
    watch_loop_count: int
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def make_quench_observation(
    *,
    keypair: DhtKeypair,
    kind: QuenchObservationKind,
    profile_id: str,
    service_name: str,
    scope_digest: bytes,
    request_digest: bytes,
    publication_digest: bytes,
    evidence_digest: bytes,
    window_id: str,
    issued_at: int,
    expires_at: int,
    family_id: str,
    path_family: str,
    accepted: bool = True,
    watch: bool = False,
) -> QuenchObservation:
    observation = QuenchObservation(kind, profile_id, service_name, scope_digest, request_digest, publication_digest, evidence_digest, window_id, accepted, watch, issued_at, expires_at, family_id, path_family, keypair.public_key_bytes)
    return replace(observation, signature=keypair.sign(observation.signature_payload()))


def _report(kind: BridgeQuenchDecisionKind, continue_publication: bool, quench: bool, watch: bool, reason: str, *, profile_id: str, service_name: str, scope_digest: bytes, request_digest: bytes, publication_digest: bytes, observations: Iterable[QuenchObservation] = (), family_count: int = 0, path_family_count: int = 0, stale_replay_count: int = 0, watch_loop_count: int = 0) -> BridgeQuenchReport:
    obs_tuple = tuple(sorted(observations, key=lambda item: (item.window_id, item.observation_digest)))
    digests = tuple(obs.observation_digest for obs in obs_tuple)
    digest = sha256(BRIDGE_QUENCH_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"continue": 1 if continue_publication else 0,
        b"quench": 1 if quench else 0,
        b"watch": 1 if watch else 0,
        b"reason": reason,
        b"profile": profile_id,
        b"service": service_name,
        b"scope": scope_digest,
        b"request": request_digest,
        b"publication": publication_digest,
        b"observations": list(digests),
        b"families": family_count,
        b"paths": path_family_count,
        b"stale": stale_replay_count,
        b"watch_loop": watch_loop_count,
    }))
    return BridgeQuenchReport(kind, continue_publication, quench, watch, reason, profile_id, service_name, scope_digest, request_digest, publication_digest, digests, family_count, path_family_count, stale_replay_count, watch_loop_count, digest)


def assess_bridge_quench_window(
    observations: Iterable[QuenchObservation],
    *,
    publication: PublicationLedgerReport,
    now: int,
    expected_profile_id: str,
    expected_service_name: str,
    expected_scope_digest: bytes,
    expected_request_digest: bytes,
    previously_seen_observations: Iterable[bytes] = (),
    min_family_diversity: int = 2,
    min_path_diversity: int = 2,
    stale_replay_threshold: int = 1,
    watch_loop_threshold: int = 2,
) -> BridgeQuenchReport:
    if publication.quarantined:
        return _report(BridgeQuenchDecisionKind.QUARANTINE_PUBLICATION, False, False, publication.watch, "publication ledger quarantined", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, publication_digest=publication.report_digest)
    if not publication.accept:
        return _report(BridgeQuenchDecisionKind.HOLD_PUBLICATION_NOT_ACCEPTED, False, False, publication.watch, "publication ledger not accepted", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, publication_digest=publication.report_digest)
    obs_tuple = tuple(sorted(observations, key=lambda item: (item.window_id, item.observation_digest)))
    seen = set(previously_seen_observations)
    families: set[str] = set()
    paths: set[str] = set()
    windows_by_family: dict[str, set[str]] = {}
    for obs in obs_tuple:
        if not obs.verifies():
            return _report(BridgeQuenchDecisionKind.QUARANTINE_BAD_SIGNATURE, False, False, True, "bad quench observation signature", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, publication_digest=publication.report_digest, observations=obs_tuple)
        if obs.issued_at > now or obs.expires_at <= now:
            return _report(BridgeQuenchDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, False, False, True, "quench observation expired or future", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, publication_digest=publication.report_digest, observations=obs_tuple)
        if obs.observation_digest in seen:
            return _report(BridgeQuenchDecisionKind.QUARANTINE_REPLAY, False, False, True, "quench observation replay", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, publication_digest=publication.report_digest, observations=obs_tuple)
        if obs.profile_id != expected_profile_id:
            return _report(BridgeQuenchDecisionKind.QUARANTINE_PROFILE_DRIFT, False, False, True, "quench profile drift", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, publication_digest=publication.report_digest, observations=obs_tuple)
        if obs.service_name != expected_service_name:
            return _report(BridgeQuenchDecisionKind.QUARANTINE_SERVICE_DRIFT, False, False, True, "quench service drift", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, publication_digest=publication.report_digest, observations=obs_tuple)
        if obs.scope_digest != expected_scope_digest:
            return _report(BridgeQuenchDecisionKind.QUARANTINE_SCOPE_DRIFT, False, False, True, "quench scope drift", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, publication_digest=publication.report_digest, observations=obs_tuple)
        if obs.request_digest != expected_request_digest:
            return _report(BridgeQuenchDecisionKind.QUARANTINE_REQUEST_DRIFT, False, False, True, "quench request drift", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, publication_digest=publication.report_digest, observations=obs_tuple)
        if obs.publication_digest != publication.report_digest:
            return _report(BridgeQuenchDecisionKind.QUARANTINE_PUBLICATION_DIGEST_DRIFT, False, False, True, "quench publication digest drift", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, publication_digest=publication.report_digest, observations=obs_tuple)
        families.add(obs.family_id)
        paths.add(obs.path_family)
        windows_by_family.setdefault(obs.family_id, set()).add(obs.window_id)
    stale_count = sum(1 for obs in obs_tuple if obs.kind is QuenchObservationKind.STALE_PUBLIC_REPLAY)
    watch_loop_count = sum(1 for obs in obs_tuple if obs.kind in (QuenchObservationKind.APPEAL_WATCH_LOOP, QuenchObservationKind.REFUSAL_ONLY))
    if obs_tuple and len(families) == 1 and len({obs.window_id for obs in obs_tuple}) > 1:
        return _report(BridgeQuenchDecisionKind.QUARANTINE_FAMILY_CAPTURE, False, False, True, "one family controls repeated quench observations", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, publication_digest=publication.report_digest, observations=obs_tuple, family_count=len(families), path_family_count=len(paths), stale_replay_count=stale_count, watch_loop_count=watch_loop_count)
    if any(obs.kind in (QuenchObservationKind.HARD_NEGATIVE, QuenchObservationKind.FALSE_SERVICE_PROOF) for obs in obs_tuple):
        if len(families) < min_family_diversity:
            return _report(BridgeQuenchDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, False, True, "hard negative lacks family diversity", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, publication_digest=publication.report_digest, observations=obs_tuple, family_count=len(families), path_family_count=len(paths), stale_replay_count=stale_count, watch_loop_count=watch_loop_count)
        return _report(BridgeQuenchDecisionKind.ACCEPT_QUENCH, False, True, True, "hard negative or false service quenches bridge publication", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, publication_digest=publication.report_digest, observations=obs_tuple, family_count=len(families), path_family_count=len(paths), stale_replay_count=stale_count, watch_loop_count=watch_loop_count)
    if stale_count > stale_replay_threshold:
        if len(families) < min_family_diversity:
            return _report(BridgeQuenchDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, False, True, "stale replay lacks family diversity", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, publication_digest=publication.report_digest, observations=obs_tuple, family_count=len(families), path_family_count=len(paths), stale_replay_count=stale_count, watch_loop_count=watch_loop_count)
        return _report(BridgeQuenchDecisionKind.ACCEPT_QUENCH, False, True, True, "repeated stale public announcements quench bridge publication", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, publication_digest=publication.report_digest, observations=obs_tuple, family_count=len(families), path_family_count=len(paths), stale_replay_count=stale_count, watch_loop_count=watch_loop_count)
    if watch_loop_count >= watch_loop_threshold:
        return _report(BridgeQuenchDecisionKind.HOLD_COOLDOWN, False, False, True, "appeal/refusal watch loop requires cooldown", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, publication_digest=publication.report_digest, observations=obs_tuple, family_count=len(families), path_family_count=len(paths), stale_replay_count=stale_count, watch_loop_count=watch_loop_count)
    if obs_tuple and len(families) < min_family_diversity:
        return _report(BridgeQuenchDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, False, publication.watch, "quench window lacks family diversity", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, publication_digest=publication.report_digest, observations=obs_tuple, family_count=len(families), path_family_count=len(paths), stale_replay_count=stale_count, watch_loop_count=watch_loop_count)
    if obs_tuple and len(paths) < min_path_diversity:
        return _report(BridgeQuenchDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, False, publication.watch, "quench window lacks path diversity", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, publication_digest=publication.report_digest, observations=obs_tuple, family_count=len(families), path_family_count=len(paths), stale_replay_count=stale_count, watch_loop_count=watch_loop_count)
    kind = BridgeQuenchDecisionKind.ACCEPT_WITH_WATCH if publication.watch else BridgeQuenchDecisionKind.ACCEPT_CONTINUE
    return _report(kind, True, False, publication.watch, "bridge publication may continue under quench monitoring", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, publication_digest=publication.report_digest, observations=obs_tuple, family_count=len(families), path_family_count=len(paths), stale_replay_count=stale_count, watch_loop_count=watch_loop_count)
