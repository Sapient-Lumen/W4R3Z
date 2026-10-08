"""SAM-shadow transcript families for future garden nodes.

This module still does not open a SAM socket.  It expands the SAM shadow lane
from a single outbound streaming-first transcript into families a garden node
will eventually need: inbound accept loops, reconnect after stream close,
naming lookup failure handling, and explicit refusal to rely on datagram-primary
SAM 3.3 features in the i2pd-bundle-first path.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .ids import DOMAIN, sha256
from .samshadow import SamShadowDecisionKind, SamShadowFrame, SamShadowProfile, SamShadowTranscript, SamShadowValidation

SAM_GARDEN_DOMAIN = DOMAIN + b":sam-garden-v1:"


class SamGardenTranscriptKind(str, Enum):
    OUTBOUND_CONNECT = "outbound_connect"
    INBOUND_ACCEPT = "inbound_accept"
    RECONNECT_AFTER_CLOSE = "reconnect_after_close"
    NAMING_FAILURE = "naming_failure"
    DATAGRAM_ASSUMPTION_PROBE = "datagram_assumption_probe"


class SamGardenDecisionKind(str, Enum):
    VALID_GARDEN_STREAMING_FAMILY = "valid_garden_streaming_family"
    INVALID_TRANSCRIPT = "invalid_transcript"
    INVALID_DATAGRAM_PRIMARY_ASSUMPTION = "invalid_datagram_primary_assumption"
    INVALID_NO_PERSISTENT_DESTINATION = "invalid_no_persistent_destination"


@dataclass(frozen=True)
class SamGardenCase:
    kind: SamGardenTranscriptKind
    transcript: SamShadowTranscript
    expected_ok: bool = True
    note: str = ""

    def bvalue(self, validation: SamShadowValidation) -> dict[bytes, BValue]:
        return {
            b"kind": self.kind.value,
            b"transcript_digest": self.transcript.digest,
            b"validation_kind": validation.kind.value,
            b"validation_ok": int(validation.ok),
            b"expected_ok": int(self.expected_ok),
            b"note": self.note[:160],
        }


@dataclass(frozen=True)
class SamGardenProfile:
    shadow_profile: SamShadowProfile
    inbound_accept_slots: int = 1
    reconnect_attempts: int = 2
    require_persistent_destination: bool = True
    allow_datagram_primary_dependency: bool = False

    def validate(self) -> None:
        if self.inbound_accept_slots <= 0 or self.reconnect_attempts <= 0:
            raise ValueError("garden SAM slots/attempts must be positive")

    @classmethod
    def default(cls) -> "SamGardenProfile":
        return cls(SamShadowProfile(session_id="i2pdht-garden", destination_name="/profile/i2pdht-garden.keys"))


@dataclass(frozen=True)
class SamGardenReport:
    cases: tuple[SamGardenCase, ...]
    validations: tuple[SamShadowValidation, ...]
    transcript_digest: bytes
    decision: SamGardenDecisionKind
    ok: bool
    reason: str


def make_sam_garden_cases(profile: SamGardenProfile, *, remote_destination: str) -> tuple[SamGardenCase, ...]:
    profile.validate()
    base = profile.shadow_profile.initial_frames()
    outbound = SamGardenCase(
        SamGardenTranscriptKind.OUTBOUND_CONNECT,
        SamShadowTranscript((*base, profile.shadow_profile.connect_frame(remote_destination))),
        True,
        "garden can initiate streaming peer RPCs",
    )
    inbound_frames = list(base)
    for _ in range(profile.inbound_accept_slots):
        inbound_frames.append(profile.shadow_profile.accept_frame())
    inbound = SamGardenCase(
        SamGardenTranscriptKind.INBOUND_ACCEPT,
        SamShadowTranscript(tuple(inbound_frames)),
        True,
        "garden can accept inbound streaming peers without a second destination",
    )
    reconnect_frames = list(base)
    for attempt in range(profile.reconnect_attempts):
        reconnect_frames.append(profile.shadow_profile.connect_frame(remote_destination, silent=attempt > 0))
        reconnect_frames.append(SamShadowFrame.command("STREAM CLOSED", ID=profile.shadow_profile.session_id, RESULT="I2P_ERROR"))
    reconnect = SamGardenCase(
        SamGardenTranscriptKind.RECONNECT_AFTER_CLOSE,
        SamShadowTranscript(tuple(reconnect_frames)),
        True,
        "garden retry pressure stays inside one persistent stream session",
    )
    naming_failure = SamGardenCase(
        SamGardenTranscriptKind.NAMING_FAILURE,
        SamShadowTranscript((*base, SamShadowFrame.command("NAMING LOOKUP", NAME="missing.example.i2p"), SamShadowFrame.parse("NAMING REPLY RESULT=KEY_NOT_FOUND NAME=missing.example.i2p"))),
        True,
        "naming lookup failure is a recoverable observation, not identity regeneration",
    )
    datagram_probe_profile = SamShadowProfile(
        session_id=profile.shadow_profile.session_id,
        destination_name=profile.shadow_profile.destination_name,
        persistent_destination=profile.shadow_profile.persistent_destination,
        signature_type=profile.shadow_profile.signature_type,
        min_version=profile.shadow_profile.min_version,
        max_version=profile.shadow_profile.max_version,
        require_primary_subsessions=True,
        router_flavor=profile.shadow_profile.router_flavor,
    )
    datagram_frames = (*datagram_probe_profile.initial_frames(), SamShadowFrame.command("DATAGRAM SEND", ID=datagram_probe_profile.session_id, DESTINATION=remote_destination, SIZE=32))
    datagram = SamGardenCase(
        SamGardenTranscriptKind.DATAGRAM_ASSUMPTION_PROBE,
        SamShadowTranscript(datagram_frames),
        profile.allow_datagram_primary_dependency,
        "datagram-primary dependency remains a negative test for bundle-first i2pd path",
    )
    return (outbound, inbound, reconnect, naming_failure, datagram)


def analyze_sam_garden_cases(cases: Iterable[SamGardenCase], *, profile: SamGardenProfile) -> SamGardenReport:
    profile.validate()
    case_tuple = tuple(cases)
    validations: list[SamShadowValidation] = []
    for case in case_tuple:
        validation_profile = profile.shadow_profile
        if case.kind is SamGardenTranscriptKind.DATAGRAM_ASSUMPTION_PROBE and not profile.allow_datagram_primary_dependency:
            validation_profile = SamShadowProfile(
                session_id=profile.shadow_profile.session_id,
                destination_name=profile.shadow_profile.destination_name,
                persistent_destination=profile.shadow_profile.persistent_destination,
                signature_type=profile.shadow_profile.signature_type,
                min_version=profile.shadow_profile.min_version,
                max_version=profile.shadow_profile.max_version,
                require_primary_subsessions=True,
                router_flavor=profile.shadow_profile.router_flavor,
            )
        validations.append(case.transcript.validate(profile=validation_profile))

    if profile.require_persistent_destination and not profile.shadow_profile.persistent_destination:
        decision = SamGardenDecisionKind.INVALID_NO_PERSISTENT_DESTINATION
        ok = False
        reason = "garden SAM profile must preserve destination material"
    elif any(not validation.ok and case.expected_ok for case, validation in zip(case_tuple, validations)):
        decision = SamGardenDecisionKind.INVALID_TRANSCRIPT
        ok = False
        reason = "at least one expected-good SAM shadow transcript failed validation"
    elif any(case.kind is SamGardenTranscriptKind.DATAGRAM_ASSUMPTION_PROBE and not case.expected_ok and validation.ok for case, validation in zip(case_tuple, validations)):
        decision = SamGardenDecisionKind.INVALID_DATAGRAM_PRIMARY_ASSUMPTION
        ok = False
        reason = "datagram-primary dependency unexpectedly validated in bundle-first shadow"
    elif any(case.kind is SamGardenTranscriptKind.DATAGRAM_ASSUMPTION_PROBE and not case.expected_ok and validation.kind is not SamShadowDecisionKind.INVALID_FEATURE_ASSUMPTION for case, validation in zip(case_tuple, validations)):
        decision = SamGardenDecisionKind.INVALID_DATAGRAM_PRIMARY_ASSUMPTION
        ok = False
        reason = "datagram-primary negative test failed for the wrong reason"
    else:
        decision = SamGardenDecisionKind.VALID_GARDEN_STREAMING_FAMILY
        ok = True
        reason = "garden SAM shadow family validates streaming-first and preserves destination material"

    digest = sha256(SAM_GARDEN_DOMAIN + b":report:" + bencode({
        b"cases": [case.bvalue(validation) for case, validation in zip(case_tuple, validations)],
        b"decision": decision.value,
        b"ok": int(ok),
    }))
    return SamGardenReport(case_tuple, tuple(validations), digest, decision, ok, reason)
