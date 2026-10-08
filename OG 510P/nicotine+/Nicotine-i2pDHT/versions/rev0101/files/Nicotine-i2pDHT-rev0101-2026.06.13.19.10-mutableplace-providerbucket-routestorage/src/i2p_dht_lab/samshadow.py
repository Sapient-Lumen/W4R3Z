"""Transport-neutral SAM shadow transcripts.

This module does not connect to I2P.  It models the command/response shapes we
expect a future Python DHT transport harness to speak through SAM, then tests
ordering and feature assumptions before a live router is in the loop.

The goal is to keep the DHT core independent of SAM while still preventing a
future integration from accidentally depending on unsupported SAM 3.3 primary
session behavior, ephemeral destinations, or stream connects before session
creation.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .ids import DOMAIN, sha256

SAM_SHADOW_DOMAIN = DOMAIN + b":sam-shadow-v1:"


class SamShadowKind(str, Enum):
    HELLO = "hello"
    HELLO_REPLY = "hello_reply"
    DEST_GENERATE = "dest_generate"
    DEST_REPLY = "dest_reply"
    SESSION_CREATE = "session_create"
    SESSION_STATUS = "session_status"
    STREAM_CONNECT = "stream_connect"
    STREAM_ACCEPT = "stream_accept"
    STREAM_STATUS = "stream_status"
    STREAM_CLOSED = "stream_closed"
    NAMING_LOOKUP = "naming_lookup"
    NAMING_REPLY = "naming_reply"
    DATAGRAM_SEND = "datagram_send"
    NOTE = "note"


class SamShadowDecisionKind(str, Enum):
    VALID_STREAMING_FIRST = "valid_streaming_first"
    INVALID_ORDERING = "invalid_ordering"
    INVALID_FEATURE_ASSUMPTION = "invalid_feature_assumption"
    INVALID_EPHEMERAL_DESTINATION = "invalid_ephemeral_destination"
    INVALID_MISSING_SESSION = "invalid_missing_session"


@dataclass(frozen=True)
class SamShadowFrame:
    kind: SamShadowKind
    tokens: tuple[tuple[str, str], ...]
    raw: str = ""

    @classmethod
    def command(cls, command: str, **kwargs: object) -> "SamShadowFrame":
        parts = command.upper().split()
        if parts == ["HELLO", "VERSION"]:
            kind = SamShadowKind.HELLO
        elif parts == ["DEST", "GENERATE"]:
            kind = SamShadowKind.DEST_GENERATE
        elif parts == ["SESSION", "CREATE"]:
            kind = SamShadowKind.SESSION_CREATE
        elif parts == ["STREAM", "CONNECT"]:
            kind = SamShadowKind.STREAM_CONNECT
        elif parts == ["STREAM", "ACCEPT"]:
            kind = SamShadowKind.STREAM_ACCEPT
        elif parts == ["NAMING", "LOOKUP"]:
            kind = SamShadowKind.NAMING_LOOKUP
        elif parts == ["DATAGRAM", "SEND"]:
            kind = SamShadowKind.DATAGRAM_SEND
        else:
            kind = SamShadowKind.NOTE
        tokens = tuple(sorted((str(key).upper(), str(value)) for key, value in kwargs.items()))
        raw = " ".join([command.upper(), *[f"{key}={value}" for key, value in tokens]]).strip()
        return cls(kind, tokens, raw)

    @classmethod
    def parse(cls, line: str) -> "SamShadowFrame":
        parts = line.strip().split()
        upper = [part.upper() for part in parts[:2]]
        if upper == ["HELLO", "VERSION"]:
            kind = SamShadowKind.HELLO
        elif upper == ["HELLO", "REPLY"]:
            kind = SamShadowKind.HELLO_REPLY
        elif upper == ["DEST", "GENERATE"]:
            kind = SamShadowKind.DEST_GENERATE
        elif upper == ["DEST", "REPLY"]:
            kind = SamShadowKind.DEST_REPLY
        elif upper == ["SESSION", "CREATE"]:
            kind = SamShadowKind.SESSION_CREATE
        elif upper == ["SESSION", "STATUS"]:
            kind = SamShadowKind.SESSION_STATUS
        elif upper == ["STREAM", "CONNECT"]:
            kind = SamShadowKind.STREAM_CONNECT
        elif upper == ["STREAM", "ACCEPT"]:
            kind = SamShadowKind.STREAM_ACCEPT
        elif upper == ["STREAM", "CLOSED"]:
            kind = SamShadowKind.STREAM_CLOSED
        elif upper == ["STREAM", "STATUS"]:
            kind = SamShadowKind.STREAM_STATUS
        elif upper == ["NAMING", "LOOKUP"]:
            kind = SamShadowKind.NAMING_LOOKUP
        elif upper == ["NAMING", "REPLY"]:
            kind = SamShadowKind.NAMING_REPLY
        elif upper == ["DATAGRAM", "SEND"]:
            kind = SamShadowKind.DATAGRAM_SEND
        else:
            kind = SamShadowKind.NOTE
        tokens: list[tuple[str, str]] = []
        for part in parts[2:]:
            if "=" in part:
                key, value = part.split("=", 1)
                tokens.append((key.upper(), value))
        return cls(kind=kind, tokens=tuple(sorted(tokens)), raw=line.strip())

    def get(self, key: str, default: str = "") -> str:
        key = key.upper()
        for token_key, value in self.tokens:
            if token_key == key:
                return value
        return default

    def bvalue(self) -> dict[bytes, BValue]:
        return {b"kind": self.kind.value, b"tokens": [[key, value] for key, value in self.tokens], b"raw": self.raw}


@dataclass(frozen=True)
class SamShadowProfile:
    session_id: str
    destination_name: str
    persistent_destination: bool = True
    signature_type: int = 7
    min_version: str = "3.1"
    max_version: str = "3.3"
    require_primary_subsessions: bool = False
    router_flavor: str = "i2pd-or-java"

    def initial_frames(self) -> tuple[SamShadowFrame, ...]:
        dest_value = self.destination_name if self.persistent_destination else "TRANSIENT"
        return (
            SamShadowFrame.command("HELLO VERSION", MIN=self.min_version, MAX=self.max_version),
            SamShadowFrame.command("DEST GENERATE", SIGNATURE_TYPE=self.signature_type),
            SamShadowFrame.command("SESSION CREATE", STYLE="STREAM", ID=self.session_id, DESTINATION=dest_value, **{"inbound.length": 2, "outbound.length": 2}),
        )

    def connect_frame(self, remote_destination: str, *, silent: bool = False) -> SamShadowFrame:
        return SamShadowFrame.command("STREAM CONNECT", ID=self.session_id, DESTINATION=remote_destination, SILENT=str(silent).lower())

    def accept_frame(self, *, silent: bool = False) -> SamShadowFrame:
        return SamShadowFrame.command("STREAM ACCEPT", ID=self.session_id, SILENT=str(silent).lower())


@dataclass(frozen=True)
class SamShadowValidation:
    kind: SamShadowDecisionKind
    ok: bool
    reason: str
    transcript_digest: bytes


@dataclass(frozen=True)
class SamShadowTranscript:
    frames: tuple[SamShadowFrame, ...]

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> "SamShadowTranscript":
        return cls(tuple(SamShadowFrame.parse(line) for line in lines if line.strip()))

    @property
    def digest(self) -> bytes:
        return sha256(SAM_SHADOW_DOMAIN + b":transcript:" + bencode([frame.bvalue() for frame in self.frames]))

    def validate(self, *, profile: SamShadowProfile | None = None) -> SamShadowValidation:
        profile = profile or SamShadowProfile(session_id="dht", destination_name="dht.keys")
        saw_hello = False
        saw_session = False
        saw_dest = False
        for frame in self.frames:
            if frame.kind is SamShadowKind.HELLO:
                saw_hello = True
                continue
            if frame.kind is SamShadowKind.DEST_GENERATE:
                if not saw_hello:
                    return SamShadowValidation(SamShadowDecisionKind.INVALID_ORDERING, False, "DEST GENERATE before HELLO VERSION", self.digest)
                saw_dest = True
                if frame.get("SIGNATURE_TYPE") and int(frame.get("SIGNATURE_TYPE")) != profile.signature_type:
                    return SamShadowValidation(SamShadowDecisionKind.INVALID_FEATURE_ASSUMPTION, False, "unexpected destination signature type", self.digest)
                continue
            if frame.kind is SamShadowKind.SESSION_CREATE:
                if not saw_hello:
                    return SamShadowValidation(SamShadowDecisionKind.INVALID_ORDERING, False, "SESSION CREATE before HELLO VERSION", self.digest)
                if profile.persistent_destination and frame.get("DESTINATION", "TRANSIENT") == "TRANSIENT":
                    return SamShadowValidation(SamShadowDecisionKind.INVALID_EPHEMERAL_DESTINATION, False, "DHT profile requires persistent destination material", self.digest)
                if frame.get("STYLE") != "STREAM":
                    return SamShadowValidation(SamShadowDecisionKind.INVALID_FEATURE_ASSUMPTION, False, "rev0015 shadow expects streaming-first session", self.digest)
                saw_session = True
                continue
            if frame.kind in {SamShadowKind.STREAM_CONNECT, SamShadowKind.STREAM_ACCEPT}:
                if not saw_session:
                    return SamShadowValidation(SamShadowDecisionKind.INVALID_MISSING_SESSION, False, f"{frame.kind.value.upper()} before SESSION CREATE", self.digest)
                if frame.get("ID") and frame.get("ID") != profile.session_id:
                    return SamShadowValidation(SamShadowDecisionKind.INVALID_MISSING_SESSION, False, f"{frame.kind.value.upper()} used an unexpected session id", self.digest)
                continue
            if frame.kind is SamShadowKind.DATAGRAM_SEND and profile.require_primary_subsessions:
                return SamShadowValidation(SamShadowDecisionKind.INVALID_FEATURE_ASSUMPTION, False, "do not require SAM 3.3 datagram subsession support in the bundle-first i2pd path yet", self.digest)
        if not saw_hello or not saw_session:
            return SamShadowValidation(SamShadowDecisionKind.INVALID_MISSING_SESSION, False, "transcript lacks hello or session create", self.digest)
        if profile.persistent_destination and not saw_dest:
            return SamShadowValidation(SamShadowDecisionKind.INVALID_EPHEMERAL_DESTINATION, False, "transcript did not show destination generation/import shadow", self.digest)
        return SamShadowValidation(SamShadowDecisionKind.VALID_STREAMING_FIRST, True, "valid streaming-first SAM shadow transcript", self.digest)


def make_streaming_first_shadow(profile: SamShadowProfile, remote_destination: str) -> SamShadowTranscript:
    return SamShadowTranscript((*profile.initial_frames(), profile.connect_frame(remote_destination)))
