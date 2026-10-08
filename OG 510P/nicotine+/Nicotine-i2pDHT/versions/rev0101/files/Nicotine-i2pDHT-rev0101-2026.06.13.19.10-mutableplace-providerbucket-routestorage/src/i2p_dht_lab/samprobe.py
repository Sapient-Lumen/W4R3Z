"""No-network SAM probe planner and transcript classifier.

rev0033 keeps live I2P/SAM out of scope but stops treating the future probe as
plumbing.  The first live probe must be local-only by default, streaming-first,
persistent-destination aware, and explicit about router-unavailable outcomes.
This module builds and classifies deterministic SAM command/reply transcripts
without opening a socket.

It is a harness boundary, not a SAM client.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Mapping

from .bencode import bencode
from .ids import DOMAIN, sha256

SAM_PROBE_DOMAIN = DOMAIN + b":sam-probe-v1:"
LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1"}


class SamProbeCommandKind(str, Enum):
    HELLO = "hello"
    DEST_GENERATE = "dest_generate"
    SESSION_CREATE = "session_create"
    NAMING_LOOKUP = "naming_lookup"
    STREAM_CONNECT = "stream_connect"


class SamProbeDecisionKind(str, Enum):
    ACCEPT_LOCAL_UNAVAILABLE = "accept_local_unavailable"
    ACCEPT_STREAMING_FIRST_PROBE = "accept_streaming_first_probe"
    ACCEPT_SESSION_ONLY = "accept_session_only"
    HOLD_ROUTER_REJECTED = "hold_router_rejected"
    QUARANTINE_EXTERNAL_SAM = "quarantine_external_sam"
    QUARANTINE_DATAGRAM_PRIMARY = "quarantine_datagram_primary"
    QUARANTINE_EPHEMERAL_DESTINATION = "quarantine_ephemeral_destination"
    QUARANTINE_HTTP_PROXY_EXPOSED = "quarantine_http_proxy_exposed"
    QUARANTINE_BAD_ORDER = "quarantine_bad_order"
    QUARANTINE_OPTION_DRIFT = "quarantine_option_drift"
    QUARANTINE_REPLY_PARSE = "quarantine_reply_parse"
    EMPTY_NO_COMMANDS = "empty_no_commands"


@dataclass(frozen=True)
class SamProbeProfile:
    host: str = "127.0.0.1"
    port: int = 7656
    session_id: str = "i2p-dht-probe"
    signature_type: int = 7
    style: str = "STREAM"
    destination_mode: str = "persistent"
    allow_external_sam: bool = False
    datagram_primary: bool = False
    expose_http_proxy: bool = False
    min_version: str = "3.1"

    def validate(self) -> None:
        if self.port <= 0 or self.port > 65535:
            raise ValueError("SAM probe port must be a TCP port")
        if not self.session_id:
            raise ValueError("SAM probe session id cannot be empty")
        if self.signature_type != 7:
            raise ValueError("rev0033 probe profile expects Ed25519 SIGNATURE_TYPE=7")
        if self.style != "STREAM":
            raise ValueError("rev0033 probe profile is streaming-first")
        if self.destination_mode not in {"persistent", "imported"}:
            raise ValueError("SAM probe destination mode must be persistent/imported")


@dataclass(frozen=True)
class SamProbeCommand:
    kind: SamProbeCommandKind
    options: tuple[tuple[str, str], ...]

    @classmethod
    def create(cls, kind: SamProbeCommandKind, **options: object) -> "SamProbeCommand":
        normalized = tuple(sorted((key.upper(), str(value)) for key, value in options.items()))
        return cls(kind, normalized)

    @property
    def command_digest(self) -> bytes:
        return sha256(SAM_PROBE_DOMAIN + b":command:" + self.line().encode("utf-8"))

    def option(self, name: str, default: str = "") -> str:
        wanted = name.upper()
        for key, value in self.options:
            if key == wanted:
                return value
        return default

    def line(self) -> str:
        prefix = {
            SamProbeCommandKind.HELLO: "HELLO VERSION",
            SamProbeCommandKind.DEST_GENERATE: "DEST GENERATE",
            SamProbeCommandKind.SESSION_CREATE: "SESSION CREATE",
            SamProbeCommandKind.NAMING_LOOKUP: "NAMING LOOKUP",
            SamProbeCommandKind.STREAM_CONNECT: "STREAM CONNECT",
        }[self.kind]
        suffix = " ".join(f"{key}={value}" for key, value in self.options)
        return prefix if not suffix else f"{prefix} {suffix}"


@dataclass(frozen=True)
class SamProbeReply:
    status: str
    options: tuple[tuple[str, str], ...]
    raw: str = ""

    @classmethod
    def parse(cls, line: str) -> "SamProbeReply":
        raw = line.strip()
        if not raw:
            raise ValueError("empty SAM reply")
        parts = raw.split()
        status = parts[0].upper()
        options: list[tuple[str, str]] = []
        for item in parts[1:]:
            # SAM replies often have a two-word command prefix such as
            # ``HELLO REPLY`` or ``SESSION STATUS`` before key=value pairs.
            # Unknown bare tokens are prefix words, not payload.
            if "=" not in item:
                continue
            key, value = item.split("=", 1)
            options.append((key.upper(), value))
        return cls(status, tuple(sorted(options)), raw)

    def option(self, name: str, default: str = "") -> str:
        wanted = name.upper()
        for key, value in self.options:
            if key == wanted:
                return value
        return default

    @property
    def ok(self) -> bool:
        result = self.option("RESULT", "OK").upper()
        return result == "OK"

    @property
    def reply_digest(self) -> bytes:
        return sha256(SAM_PROBE_DOMAIN + b":reply:" + self.raw.encode("utf-8"))


@dataclass(frozen=True)
class SamProbeReport:
    decision_kind: SamProbeDecisionKind
    accept: bool
    reason: str
    command_digests: tuple[bytes, ...]
    reply_digests: tuple[bytes, ...]
    endpoint_digest: bytes
    transcript_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def build_sam_probe_plan(profile: SamProbeProfile, *, remote_destination: str = "example.b32.i2p") -> tuple[SamProbeCommand, ...]:
    profile.validate()
    commands = [
        SamProbeCommand.create(SamProbeCommandKind.HELLO, MIN=profile.min_version, MAX="3.3"),
        SamProbeCommand.create(SamProbeCommandKind.DEST_GENERATE, SIGNATURE_TYPE=profile.signature_type),
        SamProbeCommand.create(SamProbeCommandKind.SESSION_CREATE, STYLE=profile.style, ID=profile.session_id, DESTINATION=profile.destination_mode),
    ]
    if remote_destination:
        commands.append(SamProbeCommand.create(SamProbeCommandKind.NAMING_LOOKUP, NAME=remote_destination))
        commands.append(SamProbeCommand.create(SamProbeCommandKind.STREAM_CONNECT, ID=profile.session_id, DESTINATION=remote_destination))
    return tuple(commands)


def _report(kind: SamProbeDecisionKind, accept: bool, reason: str, *, profile: SamProbeProfile, commands: tuple[SamProbeCommand, ...], replies: tuple[SamProbeReply, ...]) -> SamProbeReport:
    command_digests = tuple(command.command_digest for command in commands)
    reply_digests = tuple(reply.reply_digest for reply in replies)
    endpoint_digest = sha256(SAM_PROBE_DOMAIN + b":endpoint:" + f"{profile.host}:{profile.port}".encode("utf-8"))
    transcript_digest = sha256(SAM_PROBE_DOMAIN + b":transcript:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"endpoint": endpoint_digest,
        b"commands": command_digests,
        b"replies": reply_digests,
        b"reason": reason,
    }))
    return SamProbeReport(kind, accept, reason, command_digests, reply_digests, endpoint_digest, transcript_digest)


def classify_sam_probe_transcript(
    profile: SamProbeProfile,
    commands: Iterable[SamProbeCommand],
    reply_lines: Iterable[str],
    *,
    router_unavailable: bool = False,
) -> SamProbeReport:
    """Classify a future SAM probe transcript without touching the network."""
    commands_t = tuple(commands)
    if not commands_t:
        return _report(SamProbeDecisionKind.EMPTY_NO_COMMANDS, False, "no SAM probe commands supplied", profile=profile, commands=commands_t, replies=())
    if profile.host not in LOOPBACK_HOSTS and not profile.allow_external_sam:
        return _report(SamProbeDecisionKind.QUARANTINE_EXTERNAL_SAM, False, "default probe refuses non-loopback SAM endpoint", profile=profile, commands=commands_t, replies=())
    if profile.datagram_primary:
        return _report(SamProbeDecisionKind.QUARANTINE_DATAGRAM_PRIMARY, False, "probe refuses datagram-primary dependence before streaming-first live tests", profile=profile, commands=commands_t, replies=())
    if profile.expose_http_proxy:
        return _report(SamProbeDecisionKind.QUARANTINE_HTTP_PROXY_EXPOSED, False, "probe profile must not expose HTTP proxy surfaces", profile=profile, commands=commands_t, replies=())
    if profile.destination_mode not in {"persistent", "imported"}:
        return _report(SamProbeDecisionKind.QUARANTINE_EPHEMERAL_DESTINATION, False, "probe refuses transient destination mode", profile=profile, commands=commands_t, replies=())
    if router_unavailable:
        return _report(SamProbeDecisionKind.ACCEPT_LOCAL_UNAVAILABLE, True, "local SAM endpoint unavailable; safe no-router probe outcome", profile=profile, commands=commands_t, replies=())
    try:
        replies = tuple(SamProbeReply.parse(line) for line in reply_lines)
    except ValueError as exc:
        return _report(SamProbeDecisionKind.QUARANTINE_REPLY_PARSE, False, f"SAM reply parse failed: {exc}", profile=profile, commands=commands_t, replies=())
    if not replies:
        return _report(SamProbeDecisionKind.HOLD_ROUTER_REJECTED, False, "no SAM replies supplied and router_unavailable was not explicit", profile=profile, commands=commands_t, replies=())
    order = [command.kind for command in commands_t]
    required_prefix = [SamProbeCommandKind.HELLO, SamProbeCommandKind.DEST_GENERATE, SamProbeCommandKind.SESSION_CREATE]
    if order[:3] != required_prefix:
        return _report(SamProbeDecisionKind.QUARANTINE_BAD_ORDER, False, "SAM probe must hello, generate/import destination, then create session", profile=profile, commands=commands_t, replies=replies)
    session = commands_t[2]
    if session.option("STYLE") != "STREAM" or session.option("DESTINATION") in {"", "TRANSIENT"}:
        return _report(SamProbeDecisionKind.QUARANTINE_OPTION_DRIFT, False, "SAM session options drifted away from persistent streaming-first profile", profile=profile, commands=commands_t, replies=replies)
    dest = commands_t[1]
    if dest.option("SIGNATURE_TYPE") != str(profile.signature_type):
        return _report(SamProbeDecisionKind.QUARANTINE_OPTION_DRIFT, False, "SAM destination generation lost Ed25519 signature type", profile=profile, commands=commands_t, replies=replies)
    first_bad = next((reply for reply in replies if not reply.ok), None)
    if first_bad is not None:
        return _report(SamProbeDecisionKind.HOLD_ROUTER_REJECTED, False, "SAM router returned non-OK result before probe completion", profile=profile, commands=commands_t, replies=replies)
    if any(command.kind is SamProbeCommandKind.STREAM_CONNECT for command in commands_t):
        return _report(SamProbeDecisionKind.ACCEPT_STREAMING_FIRST_PROBE, True, "streaming-first SAM probe transcript is local, persistent, ordered, and OK", profile=profile, commands=commands_t, replies=replies)
    return _report(SamProbeDecisionKind.ACCEPT_SESSION_ONLY, True, "SAM probe established hello/destination/session without outbound connect", profile=profile, commands=commands_t, replies=replies)
