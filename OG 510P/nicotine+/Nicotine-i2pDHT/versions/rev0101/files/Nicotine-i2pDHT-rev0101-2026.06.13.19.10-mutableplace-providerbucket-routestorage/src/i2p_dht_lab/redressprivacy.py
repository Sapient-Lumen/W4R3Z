"""Privacy and minimization guard for redress/appeal evidence.

Appeal/redress should not turn a subjective policy system into a raw metadata
publishing machine.  rev0047 models redress disclosure as a bounded, redacted,
short-lived lane that can support a local lift/narrow/watch decision without
exposing raw subject keys, raw evidence, or I2P destinations by default.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .redresslane import RedressReport

REDRESS_PRIVACY_DOMAIN = DOMAIN + b":redress-privacy-v1:"
_ALLOWED_FIELDS = frozenset({"quarantine_digest", "redress_digest", "remedy_kind", "redacted_summary", "hard_negative_scan", "witness_statement_digest", "decoy_commitment"})


class RedressPrivacyDecisionKind(str, Enum):
    ACCEPT_MINIMIZED = "accept_minimized"
    ACCEPT_WITH_WATCH = "accept_with_watch"
    HOLD_REDRESS_NOT_ACCEPTED = "hold_redress_not_accepted"
    HOLD_MISSING_DISCLOSURE = "hold_missing_disclosure"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    HOLD_LOW_DECOY_BUDGET = "hold_low_decoy_budget"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_EXPIRED_OR_FUTURE = "quarantine_expired_or_future"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_PROFILE_DRIFT = "quarantine_profile_drift"
    QUARANTINE_SERVICE_DRIFT = "quarantine_service_drift"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_REQUEST_DRIFT = "quarantine_request_drift"
    QUARANTINE_REDRESS_DIGEST_DRIFT = "quarantine_redress_digest_drift"
    QUARANTINE_QUARANTINE_DIGEST_DRIFT = "quarantine_quarantine_digest_drift"
    QUARANTINE_RAW_SUBJECT_EXPOSED = "quarantine_raw_subject_exposed"
    QUARANTINE_RAW_EVIDENCE_EXPOSED = "quarantine_raw_evidence_exposed"
    QUARANTINE_RAW_DESTINATION_EXPOSED = "quarantine_raw_destination_exposed"
    QUARANTINE_UNKNOWN_FIELD = "quarantine_unknown_field"
    QUARANTINE_BYTE_BUDGET = "quarantine_byte_budget"
    QUARANTINE_RETENTION_EXCESS = "quarantine_retention_excess"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"


@dataclass(frozen=True)
class RedressDisclosure:
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    redress_report_digest: bytes
    quarantine_report_digest: bytes
    subject_blind_digest: bytes
    disclosed_fields: tuple[str, ...]
    raw_subject_exposed: bool
    raw_evidence_exposed: bool
    raw_destination_exposed: bool
    byte_count: int
    decoy_count: int
    retained_until: int
    sequence: int
    previous_disclosure_digest: bytes
    issued_at: int
    expires_at: int
    family_id: str
    path_family: str
    signer_public_key: bytes
    note_code: str = ""
    signature: bytes = b""

    def __post_init__(self) -> None:
        if not self.profile_id or len(self.profile_id.encode("utf-8")) > 80:
            raise ValueError("profile_id must be short and non-empty")
        if not self.service_name or len(self.service_name.encode("utf-8")) > 96:
            raise ValueError("service_name must be short and non-empty")
        if self.byte_count < 0 or self.byte_count > 1_000_000:
            raise ValueError("byte_count out of prototype bounds")
        if self.decoy_count < 0 or self.decoy_count > 10_000:
            raise ValueError("decoy_count out of prototype bounds")
        if self.sequence < 0:
            raise ValueError("disclosure sequence must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("expires_at must be after issued_at")
        if len(self.note_code.encode("utf-8")) > 160:
            raise ValueError("note_code must be short")
        if not self.family_id or not self.path_family:
            raise ValueError("family_id and path_family must be non-empty")
        for name, value in (
            ("scope_digest", self.scope_digest),
            ("request_digest", self.request_digest),
            ("redress_report_digest", self.redress_report_digest),
            ("quarantine_report_digest", self.quarantine_report_digest),
            ("subject_blind_digest", self.subject_blind_digest),
            ("previous_disclosure_digest", self.previous_disclosure_digest),
            ("signer_public_key", self.signer_public_key),
        ):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if self.signature and len(self.signature) != 64:
            raise ValueError("signature must be Ed25519-sized")
        object.__setattr__(self, "disclosed_fields", tuple(self.disclosed_fields))

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"redress": self.redress_report_digest,
            b"quarantine": self.quarantine_report_digest,
            b"subject_blind": self.subject_blind_digest,
            b"fields": list(self.disclosed_fields),
            b"raw_subject": 1 if self.raw_subject_exposed else 0,
            b"raw_evidence": 1 if self.raw_evidence_exposed else 0,
            b"raw_destination": 1 if self.raw_destination_exposed else 0,
            b"bytes": self.byte_count,
            b"decoys": self.decoy_count,
            b"retained_until": self.retained_until,
            b"seq": self.sequence,
            b"prev": self.previous_disclosure_digest,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"family": self.family_id,
            b"path_family": self.path_family,
            b"signer": self.signer_public_key,
            b"note": self.note_code,
        }

    def signature_payload(self) -> bytes:
        return REDRESS_PRIVACY_DOMAIN + b":disclosure-sig:" + bencode(self.unsigned_bvalue())

    @property
    def disclosure_core_digest(self) -> bytes:
        return sha256(REDRESS_PRIVACY_DOMAIN + b":disclosure-core:" + bencode({
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"redress": self.redress_report_digest,
            b"quarantine": self.quarantine_report_digest,
            b"subject_blind": self.subject_blind_digest,
            b"fields": list(self.disclosed_fields),
            b"raw_subject": 1 if self.raw_subject_exposed else 0,
            b"raw_evidence": 1 if self.raw_evidence_exposed else 0,
            b"raw_destination": 1 if self.raw_destination_exposed else 0,
            b"bytes": self.byte_count,
            b"decoys": self.decoy_count,
            b"retained_until": self.retained_until,
            b"seq": self.sequence,
            b"prev": self.previous_disclosure_digest,
            b"note": self.note_code,
        }))

    @property
    def disclosure_digest(self) -> bytes:
        return sha256(REDRESS_PRIVACY_DOMAIN + b":disclosure-digest:" + self.signature_payload() + self.signature)

    def verifies(self) -> bool:
        return verify_signature(self.signer_public_key, self.signature_payload(), self.signature)


@dataclass(frozen=True)
class RedressPrivacyReport:
    decision_kind: RedressPrivacyDecisionKind
    accept: bool
    watch: bool
    reason: str
    profile_id: str
    service_name: str
    redress_report_digest: bytes
    disclosure_digests: tuple[bytes, ...]
    family_count: int
    path_family_count: int
    total_bytes: int
    total_decoys: int
    highest_sequence: int
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")



def make_redress_disclosure(
    *,
    keypair: DhtKeypair,
    profile_id: str,
    service_name: str,
    scope_digest: bytes,
    request_digest: bytes,
    redress_report_digest: bytes,
    quarantine_report_digest: bytes,
    subject_blind_digest: bytes,
    disclosed_fields: Iterable[str],
    raw_subject_exposed: bool = False,
    raw_evidence_exposed: bool = False,
    raw_destination_exposed: bool = False,
    byte_count: int,
    decoy_count: int,
    retained_until: int,
    sequence: int,
    previous_disclosure_digest: bytes = ZERO_DIGEST,
    issued_at: int,
    expires_at: int,
    family_id: str,
    path_family: str,
    note_code: str = "",
) -> RedressDisclosure:
    disclosure = RedressDisclosure(profile_id, service_name, scope_digest, request_digest, redress_report_digest, quarantine_report_digest, subject_blind_digest, tuple(disclosed_fields), raw_subject_exposed, raw_evidence_exposed, raw_destination_exposed, byte_count, decoy_count, retained_until, sequence, previous_disclosure_digest, issued_at, expires_at, family_id, path_family, keypair.public_key_bytes, note_code)
    return replace(disclosure, signature=keypair.sign(disclosure.signature_payload()))



def _report(kind: RedressPrivacyDecisionKind, accept: bool, watch: bool, reason: str, *, redress: RedressReport, disclosures: Iterable[RedressDisclosure] = (), family_count: int = 0, path_family_count: int = 0, total_bytes: int = 0, total_decoys: int = 0, highest_sequence: int = -1) -> RedressPrivacyReport:
    disclosure_tuple = tuple(sorted(disclosures, key=lambda item: (item.sequence, item.disclosure_digest)))
    digests = tuple(sorted(item.disclosure_digest for item in disclosure_tuple if accept or watch or kind.value.startswith("hold_")))
    digest = sha256(REDRESS_PRIVACY_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"reason": reason,
        b"profile": redress.profile_id,
        b"service": redress.service_name,
        b"redress": redress.report_digest,
        b"disclosures": list(digests),
        b"families": family_count,
        b"paths": path_family_count,
        b"bytes": total_bytes,
        b"decoys": total_decoys,
        b"highest": highest_sequence,
    }))
    return RedressPrivacyReport(kind, accept, watch, reason, redress.profile_id, redress.service_name, redress.report_digest, digests, family_count, path_family_count, total_bytes, total_decoys, highest_sequence, digest)



def assess_redress_privacy(
    disclosures: Iterable[RedressDisclosure],
    *,
    redress: RedressReport,
    now: int,
    expected_scope_digest: bytes,
    expected_request_digest: bytes,
    previous_sequence: int | None = None,
    previous_disclosure_digest: bytes | None = None,
    previously_seen_disclosures: Iterable[bytes] = (),
    min_family_diversity: int = 2,
    min_path_diversity: int = 2,
    min_decoy_count: int = 1,
    max_total_bytes: int = 4096,
    max_retention_seconds: int = 86_400,
    allow_watch: bool = False,
) -> RedressPrivacyReport:
    disclosure_tuple = tuple(sorted(disclosures, key=lambda item: (item.sequence, item.disclosure_digest)))
    if not redress.accept and not redress.watch:
        return _report(RedressPrivacyDecisionKind.HOLD_REDRESS_NOT_ACCEPTED, False, False, "redress report is not accepted or watchable", redress=redress)
    if not disclosure_tuple:
        return _report(RedressPrivacyDecisionKind.HOLD_MISSING_DISCLOSURE, False, False, "missing redress disclosure", redress=redress)
    seen = set(previously_seen_disclosures)
    fork_guard: dict[tuple[bytes, int], bytes] = {}
    for disclosure in disclosure_tuple:
        if not disclosure.verifies():
            return _report(RedressPrivacyDecisionKind.QUARANTINE_BAD_SIGNATURE, False, False, "bad redress disclosure signature", redress=redress, disclosures=disclosure_tuple)
        if disclosure.issued_at > now or disclosure.expires_at <= now:
            return _report(RedressPrivacyDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, False, False, "redress disclosure expired or future", redress=redress, disclosures=disclosure_tuple)
        if disclosure.disclosure_digest in seen:
            return _report(RedressPrivacyDecisionKind.QUARANTINE_REPLAY, False, False, "redress disclosure replay", redress=redress, disclosures=disclosure_tuple)
        if disclosure.profile_id != redress.profile_id:
            return _report(RedressPrivacyDecisionKind.QUARANTINE_PROFILE_DRIFT, False, False, "redress disclosure profile drift", redress=redress, disclosures=disclosure_tuple)
        if disclosure.service_name != redress.service_name:
            return _report(RedressPrivacyDecisionKind.QUARANTINE_SERVICE_DRIFT, False, False, "redress disclosure service drift", redress=redress, disclosures=disclosure_tuple)
        if disclosure.scope_digest != expected_scope_digest:
            return _report(RedressPrivacyDecisionKind.QUARANTINE_SCOPE_DRIFT, False, False, "redress disclosure scope drift", redress=redress, disclosures=disclosure_tuple)
        if disclosure.request_digest != expected_request_digest:
            return _report(RedressPrivacyDecisionKind.QUARANTINE_REQUEST_DRIFT, False, False, "redress disclosure request drift", redress=redress, disclosures=disclosure_tuple)
        if disclosure.redress_report_digest != redress.report_digest:
            return _report(RedressPrivacyDecisionKind.QUARANTINE_REDRESS_DIGEST_DRIFT, False, False, "redress disclosure digest drift", redress=redress, disclosures=disclosure_tuple)
        if disclosure.quarantine_report_digest != redress.quarantine_report_digest:
            return _report(RedressPrivacyDecisionKind.QUARANTINE_QUARANTINE_DIGEST_DRIFT, False, False, "quarantine digest drift", redress=redress, disclosures=disclosure_tuple)
        if disclosure.raw_subject_exposed:
            return _report(RedressPrivacyDecisionKind.QUARANTINE_RAW_SUBJECT_EXPOSED, False, False, "raw subject exposure", redress=redress, disclosures=disclosure_tuple)
        if disclosure.raw_evidence_exposed:
            return _report(RedressPrivacyDecisionKind.QUARANTINE_RAW_EVIDENCE_EXPOSED, False, False, "raw evidence exposure", redress=redress, disclosures=disclosure_tuple)
        if disclosure.raw_destination_exposed:
            return _report(RedressPrivacyDecisionKind.QUARANTINE_RAW_DESTINATION_EXPOSED, False, False, "raw destination exposure", redress=redress, disclosures=disclosure_tuple)
        if any(field not in _ALLOWED_FIELDS for field in disclosure.disclosed_fields):
            return _report(RedressPrivacyDecisionKind.QUARANTINE_UNKNOWN_FIELD, False, False, "unknown redress disclosure field", redress=redress, disclosures=disclosure_tuple)
        if disclosure.retained_until - now > max_retention_seconds:
            return _report(RedressPrivacyDecisionKind.QUARANTINE_RETENTION_EXCESS, False, False, "redress disclosure retained too long", redress=redress, disclosures=disclosure_tuple)
        if previous_sequence is not None:
            if disclosure.sequence <= previous_sequence:
                return _report(RedressPrivacyDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, False, "redress disclosure sequence rollback", redress=redress, disclosures=disclosure_tuple)
            if previous_disclosure_digest is not None and disclosure.previous_disclosure_digest != previous_disclosure_digest:
                return _report(RedressPrivacyDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, False, "redress disclosure previous digest mismatch", redress=redress, disclosures=disclosure_tuple)
        key = (disclosure.signer_public_key, disclosure.sequence)
        old = fork_guard.get(key)
        if old is not None and old != disclosure.disclosure_core_digest:
            return _report(RedressPrivacyDecisionKind.QUARANTINE_SEQUENCE_FORK, False, False, "redress disclosure same-signer fork", redress=redress, disclosures=disclosure_tuple)
        fork_guard[key] = disclosure.disclosure_core_digest
    highest = max(disclosure.sequence for disclosure in disclosure_tuple)
    active = tuple(disclosure for disclosure in disclosure_tuple if disclosure.sequence == highest)
    families = {disclosure.family_id for disclosure in active}
    paths = {disclosure.path_family for disclosure in active}
    total_bytes = sum(disclosure.byte_count for disclosure in active)
    total_decoys = sum(disclosure.decoy_count for disclosure in active)
    if total_bytes > max_total_bytes:
        return _report(RedressPrivacyDecisionKind.QUARANTINE_BYTE_BUDGET, False, False, "redress disclosure byte budget exceeded", redress=redress, disclosures=active, family_count=len(families), path_family_count=len(paths), total_bytes=total_bytes, total_decoys=total_decoys, highest_sequence=highest)
    if len(families) < min_family_diversity:
        return _report(RedressPrivacyDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, False, "low redress disclosure family diversity", redress=redress, disclosures=active, family_count=len(families), path_family_count=len(paths), total_bytes=total_bytes, total_decoys=total_decoys, highest_sequence=highest)
    if len(paths) < min_path_diversity:
        return _report(RedressPrivacyDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, False, "low redress disclosure path diversity", redress=redress, disclosures=active, family_count=len(families), path_family_count=len(paths), total_bytes=total_bytes, total_decoys=total_decoys, highest_sequence=highest)
    if total_decoys < min_decoy_count:
        return _report(RedressPrivacyDecisionKind.HOLD_LOW_DECOY_BUDGET, False, True, "redress disclosure has too little decoy cover", redress=redress, disclosures=active, family_count=len(families), path_family_count=len(paths), total_bytes=total_bytes, total_decoys=total_decoys, highest_sequence=highest)
    if redress.watch and not allow_watch:
        return _report(RedressPrivacyDecisionKind.ACCEPT_WITH_WATCH, True, True, "redress disclosure accepted with watch pressure", redress=redress, disclosures=active, family_count=len(families), path_family_count=len(paths), total_bytes=total_bytes, total_decoys=total_decoys, highest_sequence=highest)
    return _report(RedressPrivacyDecisionKind.ACCEPT_MINIMIZED, True, redress.watch, "redress disclosure minimized", redress=redress, disclosures=active, family_count=len(families), path_family_count=len(paths), total_bytes=total_bytes, total_decoys=total_decoys, highest_sequence=highest)
