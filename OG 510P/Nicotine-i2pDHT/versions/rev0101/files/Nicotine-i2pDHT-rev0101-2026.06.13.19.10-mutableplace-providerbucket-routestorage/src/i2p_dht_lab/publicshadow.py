"""rev0048 public-shadow observations for bridge publication side effects.

Publication is not done when a local guard accepts a capsule.  A public bridge
record can be accepted locally, emitted through a future side-effect path, and
then be seen differently by gardens, mirrors, sentinels, or cached peers.  This
module models those post-publication observations without claiming global truth.

The rule is deliberately conservative:

    public shadow observations are evidence about exposure, not proof of truth.

They are signed, scoped, short-lived, sequence/previous-linked, and checked for
family/path diversity before sticky public exposure can be treated as healthy.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .bridgequenchlane import BridgeQuenchReport
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .publicationguard import PublicationReport
from .publicationledger import PublicationLedgerReport

PUBLIC_SHADOW_DOMAIN = DOMAIN + b":public-shadow-v1:"


class PublicShadowKind(str, Enum):
    RECORD_SEEN = "record_seen"
    RECORD_MISSING = "record_missing"
    STALE_RECORD_SEEN = "stale_record_seen"
    WITHDRAWAL_SEEN = "withdrawal_seen"
    REPAIR_SEEN = "repair_seen"
    FALSE_RECORD = "false_record"
    QUENCH_SEEN = "quench_seen"


class PublicShadowDecisionKind(str, Enum):
    ACCEPT_SHADOW = "accept_shadow"
    ACCEPT_WITH_WATCH = "accept_with_watch"
    HOLD_PUBLICATION_GUARD_NOT_ACCEPTED = "hold_publication_guard_not_accepted"
    HOLD_PUBLICATION_LEDGER_NOT_ACCEPTED = "hold_publication_ledger_not_accepted"
    HOLD_QUENCH_ACTIVE = "hold_quench_active"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    HOLD_MISSING_POSITIVE_SHADOW = "hold_missing_positive_shadow"
    HOLD_STALE_SHADOW = "hold_stale_shadow"
    HOLD_WITHDRAWAL_SEEN = "hold_withdrawal_seen"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_EXPIRED_OR_FUTURE = "quarantine_expired_or_future"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_PROFILE_DRIFT = "quarantine_profile_drift"
    QUARANTINE_SERVICE_DRIFT = "quarantine_service_drift"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_REQUEST_DRIFT = "quarantine_request_drift"
    QUARANTINE_PUBLICATION_GUARD_DIGEST_DRIFT = "quarantine_publication_guard_digest_drift"
    QUARANTINE_PUBLICATION_LEDGER_DIGEST_DRIFT = "quarantine_publication_ledger_digest_drift"
    QUARANTINE_QUENCH_DIGEST_DRIFT = "quarantine_quench_digest_drift"
    QUARANTINE_RECORD_DIGEST_DRIFT = "quarantine_record_digest_drift"
    QUARANTINE_FALSE_PUBLIC_RECORD = "quarantine_false_public_record"
    QUARANTINE_CONFLICTING_SHADOW = "quarantine_conflicting_shadow"
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"


@dataclass(frozen=True)
class PublicShadowObservation:
    kind: PublicShadowKind
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    publication_guard_digest: bytes
    publication_ledger_digest: bytes
    quench_digest: bytes
    observed_record_digest: bytes
    sequence: int
    previous_shadow_digest: bytes
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
        if self.sequence < 0:
            raise ValueError("shadow sequence must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("expires_at must be after issued_at")
        if not self.family_id or not self.path_family:
            raise ValueError("family_id and path_family must be non-empty")
        for name, value in (
            ("scope_digest", self.scope_digest),
            ("request_digest", self.request_digest),
            ("publication_guard_digest", self.publication_guard_digest),
            ("publication_ledger_digest", self.publication_ledger_digest),
            ("quench_digest", self.quench_digest),
            ("observed_record_digest", self.observed_record_digest),
            ("previous_shadow_digest", self.previous_shadow_digest),
            ("signer_public_key", self.signer_public_key),
        ):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if self.signature and len(self.signature) != 64:
            raise ValueError("signature must be Ed25519-sized")
        object.__setattr__(self, "kind", PublicShadowKind(self.kind))

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"kind": self.kind.value,
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"pub_guard": self.publication_guard_digest,
            b"pub_ledger": self.publication_ledger_digest,
            b"quench": self.quench_digest,
            b"record": self.observed_record_digest,
            b"seq": self.sequence,
            b"prev": self.previous_shadow_digest,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"family": self.family_id,
            b"path_family": self.path_family,
            b"signer": self.signer_public_key,
        }

    def signature_payload(self) -> bytes:
        return PUBLIC_SHADOW_DOMAIN + b":observation-sig:" + bencode(self.unsigned_bvalue())

    @property
    def observation_core_digest(self) -> bytes:
        return sha256(PUBLIC_SHADOW_DOMAIN + b":observation-core:" + bencode(self.unsigned_bvalue()))

    @property
    def observation_digest(self) -> bytes:
        return sha256(PUBLIC_SHADOW_DOMAIN + b":observation-digest:" + self.signature_payload() + self.signature)

    def verifies(self) -> bool:
        return verify_signature(self.signer_public_key, self.signature_payload(), self.signature)


@dataclass(frozen=True)
class PublicShadowReport:
    decision_kind: PublicShadowDecisionKind
    accept: bool
    watch: bool
    quarantined_flag: bool
    reason: str
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    publication_guard_digest: bytes
    publication_ledger_digest: bytes
    quench_digest: bytes
    accepted_record_digest: bytes
    observation_digests: tuple[bytes, ...]
    family_count: int
    path_family_count: int
    positive_count: int
    stale_count: int
    false_count: int
    highest_sequence: int
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.quarantined_flag or self.decision_kind.value.startswith("quarantine_")


_POSITIVE_KINDS = {PublicShadowKind.RECORD_SEEN, PublicShadowKind.REPAIR_SEEN}
_STALE_KINDS = {PublicShadowKind.STALE_RECORD_SEEN, PublicShadowKind.RECORD_MISSING, PublicShadowKind.WITHDRAWAL_SEEN, PublicShadowKind.QUENCH_SEEN}


def make_public_shadow_observation(
    *,
    keypair: DhtKeypair,
    kind: PublicShadowKind,
    profile_id: str,
    service_name: str,
    scope_digest: bytes,
    request_digest: bytes,
    publication_guard_digest: bytes,
    publication_ledger_digest: bytes,
    quench_digest: bytes,
    observed_record_digest: bytes,
    sequence: int,
    previous_shadow_digest: bytes = ZERO_DIGEST,
    issued_at: int,
    expires_at: int,
    family_id: str,
    path_family: str,
) -> PublicShadowObservation:
    observation = PublicShadowObservation(kind, profile_id, service_name, scope_digest, request_digest, publication_guard_digest, publication_ledger_digest, quench_digest, observed_record_digest, sequence, previous_shadow_digest, issued_at, expires_at, family_id, path_family, keypair.public_key_bytes)
    return replace(observation, signature=keypair.sign(observation.signature_payload()))


def _report(kind: PublicShadowDecisionKind, accept: bool, watch: bool, quarantined: bool, reason: str, *, profile_id: str, service_name: str, scope_digest: bytes, request_digest: bytes, publication_guard_digest: bytes, publication_ledger_digest: bytes, quench_digest: bytes, accepted_record_digest: bytes = ZERO_DIGEST, observations: Iterable[PublicShadowObservation] = (), family_count: int = 0, path_family_count: int = 0, positive_count: int = 0, stale_count: int = 0, false_count: int = 0) -> PublicShadowReport:
    obs_tuple = tuple(sorted(observations, key=lambda item: (item.sequence, item.observation_digest)))
    digests = tuple(obs.observation_digest for obs in obs_tuple)
    highest = max((obs.sequence for obs in obs_tuple), default=-1)
    digest = sha256(PUBLIC_SHADOW_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"quarantine": 1 if quarantined else 0,
        b"reason": reason,
        b"profile": profile_id,
        b"service": service_name,
        b"scope": scope_digest,
        b"request": request_digest,
        b"pub_guard": publication_guard_digest,
        b"pub_ledger": publication_ledger_digest,
        b"quench": quench_digest,
        b"record": accepted_record_digest,
        b"observations": list(digests),
        b"families": family_count,
        b"paths": path_family_count,
        b"positive": positive_count,
        b"stale": stale_count,
        b"false": false_count,
        b"highest": highest,
    }))
    return PublicShadowReport(kind, accept, watch, quarantined, reason, profile_id, service_name, scope_digest, request_digest, publication_guard_digest, publication_ledger_digest, quench_digest, accepted_record_digest, digests, family_count, path_family_count, positive_count, stale_count, false_count, highest, digest)


def assess_public_shadow(
    observations: Iterable[PublicShadowObservation],
    *,
    publication_guard: PublicationReport,
    publication_ledger: PublicationLedgerReport,
    quench: BridgeQuenchReport,
    now: int,
    expected_profile_id: str,
    expected_service_name: str,
    expected_scope_digest: bytes,
    expected_request_digest: bytes,
    expected_public_record_digest: bytes | None = None,
    previous_sequence: int | None = None,
    previous_shadow_digest: bytes | None = None,
    previously_seen_observations: Iterable[bytes] = (),
    live_hard_negative_digests: Iterable[bytes] = (),
    min_family_diversity: int = 2,
    min_path_diversity: int = 2,
    allow_watch: bool = False,
) -> PublicShadowReport:
    if not publication_guard.accept:
        return _report(PublicShadowDecisionKind.HOLD_PUBLICATION_GUARD_NOT_ACCEPTED, False, publication_guard.watch, False, "publication guard not accepted", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, publication_guard_digest=publication_guard.report_digest, publication_ledger_digest=publication_ledger.report_digest, quench_digest=quench.report_digest)
    if not publication_ledger.accept:
        return _report(PublicShadowDecisionKind.HOLD_PUBLICATION_LEDGER_NOT_ACCEPTED, False, publication_guard.watch or publication_ledger.watch, False, "publication ledger not accepted", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, publication_guard_digest=publication_guard.report_digest, publication_ledger_digest=publication_ledger.report_digest, quench_digest=quench.report_digest)
    if quench.quench:
        return _report(PublicShadowDecisionKind.HOLD_QUENCH_ACTIVE, False, True, False, "bridge quench is active", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, publication_guard_digest=publication_guard.report_digest, publication_ledger_digest=publication_ledger.report_digest, quench_digest=quench.report_digest)
    obs_tuple = tuple(sorted(observations, key=lambda item: (item.sequence, item.observation_digest)))
    seen = set(previously_seen_observations)
    hard = set(live_hard_negative_digests)
    if hard:
        return _report(PublicShadowDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, True, True, "live hard negative pressure blocks public shadow acceptance", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, publication_guard_digest=publication_guard.report_digest, publication_ledger_digest=publication_ledger.report_digest, quench_digest=quench.report_digest, observations=obs_tuple)
    if not obs_tuple:
        return _report(PublicShadowDecisionKind.HOLD_MISSING_POSITIVE_SHADOW, False, publication_guard.watch or publication_ledger.watch, False, "no public shadow observations", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, publication_guard_digest=publication_guard.report_digest, publication_ledger_digest=publication_ledger.report_digest, quench_digest=quench.report_digest)

    families: set[str] = set()
    paths: set[str] = set()
    by_sequence: dict[int, PublicShadowObservation] = {}
    positive_records: set[bytes] = set()
    positive_count = 0
    stale_count = 0
    false_count = 0
    for obs in obs_tuple:
        if not obs.verifies():
            return _report(PublicShadowDecisionKind.QUARANTINE_BAD_SIGNATURE, False, True, True, "bad public-shadow signature", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, publication_guard_digest=publication_guard.report_digest, publication_ledger_digest=publication_ledger.report_digest, quench_digest=quench.report_digest, observations=obs_tuple)
        if obs.issued_at > now or obs.expires_at <= now:
            return _report(PublicShadowDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, False, True, True, "public-shadow observation expired or future", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, publication_guard_digest=publication_guard.report_digest, publication_ledger_digest=publication_ledger.report_digest, quench_digest=quench.report_digest, observations=obs_tuple)
        if obs.observation_digest in seen:
            return _report(PublicShadowDecisionKind.QUARANTINE_REPLAY, False, True, True, "public-shadow observation replay", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, publication_guard_digest=publication_guard.report_digest, publication_ledger_digest=publication_ledger.report_digest, quench_digest=quench.report_digest, observations=obs_tuple)
        if obs.profile_id != expected_profile_id:
            return _report(PublicShadowDecisionKind.QUARANTINE_PROFILE_DRIFT, False, True, True, "profile drift", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, publication_guard_digest=publication_guard.report_digest, publication_ledger_digest=publication_ledger.report_digest, quench_digest=quench.report_digest, observations=obs_tuple)
        if obs.service_name != expected_service_name:
            return _report(PublicShadowDecisionKind.QUARANTINE_SERVICE_DRIFT, False, True, True, "service drift", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, publication_guard_digest=publication_guard.report_digest, publication_ledger_digest=publication_ledger.report_digest, quench_digest=quench.report_digest, observations=obs_tuple)
        if obs.scope_digest != expected_scope_digest:
            return _report(PublicShadowDecisionKind.QUARANTINE_SCOPE_DRIFT, False, True, True, "scope drift", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, publication_guard_digest=publication_guard.report_digest, publication_ledger_digest=publication_ledger.report_digest, quench_digest=quench.report_digest, observations=obs_tuple)
        if obs.request_digest != expected_request_digest:
            return _report(PublicShadowDecisionKind.QUARANTINE_REQUEST_DRIFT, False, True, True, "request drift", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, publication_guard_digest=publication_guard.report_digest, publication_ledger_digest=publication_ledger.report_digest, quench_digest=quench.report_digest, observations=obs_tuple)
        if obs.publication_guard_digest != publication_guard.report_digest:
            return _report(PublicShadowDecisionKind.QUARANTINE_PUBLICATION_GUARD_DIGEST_DRIFT, False, True, True, "publication guard digest drift", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, publication_guard_digest=publication_guard.report_digest, publication_ledger_digest=publication_ledger.report_digest, quench_digest=quench.report_digest, observations=obs_tuple)
        if obs.publication_ledger_digest != publication_ledger.report_digest:
            return _report(PublicShadowDecisionKind.QUARANTINE_PUBLICATION_LEDGER_DIGEST_DRIFT, False, True, True, "publication ledger digest drift", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, publication_guard_digest=publication_guard.report_digest, publication_ledger_digest=publication_ledger.report_digest, quench_digest=quench.report_digest, observations=obs_tuple)
        if obs.quench_digest != quench.report_digest:
            return _report(PublicShadowDecisionKind.QUARANTINE_QUENCH_DIGEST_DRIFT, False, True, True, "quench digest drift", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, publication_guard_digest=publication_guard.report_digest, publication_ledger_digest=publication_ledger.report_digest, quench_digest=quench.report_digest, observations=obs_tuple)
        if previous_sequence is not None and obs.sequence < previous_sequence:
            return _report(PublicShadowDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, True, True, "public-shadow rollback", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, publication_guard_digest=publication_guard.report_digest, publication_ledger_digest=publication_ledger.report_digest, quench_digest=quench.report_digest, observations=obs_tuple)
        if previous_sequence is not None and obs.sequence == previous_sequence and previous_shadow_digest is not None and obs.previous_shadow_digest != previous_shadow_digest:
            return _report(PublicShadowDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, True, True, "public-shadow previous mismatch", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, publication_guard_digest=publication_guard.report_digest, publication_ledger_digest=publication_ledger.report_digest, quench_digest=quench.report_digest, observations=obs_tuple)
        existing = by_sequence.get(obs.sequence)
        if existing is not None and existing.observation_core_digest != obs.observation_core_digest:
            return _report(PublicShadowDecisionKind.QUARANTINE_SEQUENCE_FORK, False, True, True, "public-shadow sequence fork", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, publication_guard_digest=publication_guard.report_digest, publication_ledger_digest=publication_ledger.report_digest, quench_digest=quench.report_digest, observations=obs_tuple)
        by_sequence[obs.sequence] = obs
        families.add(obs.family_id)
        paths.add(obs.path_family)
        if obs.kind in _POSITIVE_KINDS:
            positive_count += 1
            positive_records.add(obs.observed_record_digest)
        if obs.kind in _STALE_KINDS:
            stale_count += 1
        if obs.kind is PublicShadowKind.FALSE_RECORD:
            false_count += 1

    if false_count:
        return _report(PublicShadowDecisionKind.QUARANTINE_FALSE_PUBLIC_RECORD, False, True, True, "false public record evidence", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, publication_guard_digest=publication_guard.report_digest, publication_ledger_digest=publication_ledger.report_digest, quench_digest=quench.report_digest, observations=obs_tuple, family_count=len(families), path_family_count=len(paths), positive_count=positive_count, stale_count=stale_count, false_count=false_count)
    if len(positive_records) > 1:
        return _report(PublicShadowDecisionKind.QUARANTINE_CONFLICTING_SHADOW, False, True, True, "conflicting public records observed", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, publication_guard_digest=publication_guard.report_digest, publication_ledger_digest=publication_ledger.report_digest, quench_digest=quench.report_digest, observations=obs_tuple, family_count=len(families), path_family_count=len(paths), positive_count=positive_count, stale_count=stale_count, false_count=false_count)
    if expected_public_record_digest is not None and positive_records and next(iter(positive_records)) != expected_public_record_digest:
        return _report(PublicShadowDecisionKind.QUARANTINE_RECORD_DIGEST_DRIFT, False, True, True, "positive shadow record digest drift", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, publication_guard_digest=publication_guard.report_digest, publication_ledger_digest=publication_ledger.report_digest, quench_digest=quench.report_digest, observations=obs_tuple, family_count=len(families), path_family_count=len(paths), positive_count=positive_count, stale_count=stale_count, false_count=false_count)
    if positive_count == 0:
        if stale_count:
            return _report(PublicShadowDecisionKind.HOLD_STALE_SHADOW, False, True, False, "only stale/negative public shadow observed", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, publication_guard_digest=publication_guard.report_digest, publication_ledger_digest=publication_ledger.report_digest, quench_digest=quench.report_digest, observations=obs_tuple, family_count=len(families), path_family_count=len(paths), positive_count=positive_count, stale_count=stale_count, false_count=false_count)
        return _report(PublicShadowDecisionKind.HOLD_MISSING_POSITIVE_SHADOW, False, publication_guard.watch or publication_ledger.watch, False, "missing positive public shadow", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, publication_guard_digest=publication_guard.report_digest, publication_ledger_digest=publication_ledger.report_digest, quench_digest=quench.report_digest, observations=obs_tuple, family_count=len(families), path_family_count=len(paths), positive_count=positive_count, stale_count=stale_count, false_count=false_count)
    if len(families) < min_family_diversity:
        return _report(PublicShadowDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, False, "low public-shadow family diversity", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, publication_guard_digest=publication_guard.report_digest, publication_ledger_digest=publication_ledger.report_digest, quench_digest=quench.report_digest, observations=obs_tuple, family_count=len(families), path_family_count=len(paths), positive_count=positive_count, stale_count=stale_count, false_count=false_count)
    if len(paths) < min_path_diversity:
        return _report(PublicShadowDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, False, "low public-shadow path diversity", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, publication_guard_digest=publication_guard.report_digest, publication_ledger_digest=publication_ledger.report_digest, quench_digest=quench.report_digest, observations=obs_tuple, family_count=len(families), path_family_count=len(paths), positive_count=positive_count, stale_count=stale_count, false_count=false_count)
    accepted_record = next(iter(positive_records))
    if stale_count:
        if allow_watch:
            return _report(PublicShadowDecisionKind.ACCEPT_WITH_WATCH, True, True, False, "positive public shadow with stale side pressure", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, publication_guard_digest=publication_guard.report_digest, publication_ledger_digest=publication_ledger.report_digest, quench_digest=quench.report_digest, accepted_record_digest=accepted_record, observations=obs_tuple, family_count=len(families), path_family_count=len(paths), positive_count=positive_count, stale_count=stale_count, false_count=false_count)
        return _report(PublicShadowDecisionKind.HOLD_STALE_SHADOW, False, True, False, "stale side pressure requires watch", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, publication_guard_digest=publication_guard.report_digest, publication_ledger_digest=publication_ledger.report_digest, quench_digest=quench.report_digest, accepted_record_digest=accepted_record, observations=obs_tuple, family_count=len(families), path_family_count=len(paths), positive_count=positive_count, stale_count=stale_count, false_count=false_count)
    watch = publication_guard.watch or publication_ledger.watch or quench.watch
    return _report(PublicShadowDecisionKind.ACCEPT_WITH_WATCH if watch else PublicShadowDecisionKind.ACCEPT_SHADOW, True, watch, False, "public shadow accepted", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, publication_guard_digest=publication_guard.report_digest, publication_ledger_digest=publication_ledger.report_digest, quench_digest=quench.report_digest, accepted_record_digest=accepted_record, observations=obs_tuple, family_count=len(families), path_family_count=len(paths), positive_count=positive_count, stale_count=stale_count, false_count=false_count)
