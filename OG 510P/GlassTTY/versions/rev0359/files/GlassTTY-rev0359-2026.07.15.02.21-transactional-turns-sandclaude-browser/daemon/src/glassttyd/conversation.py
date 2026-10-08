"""Conversation engine for GlassTTY.

This is the layer that turns GlassTTY's low-level bridge primitives
(``prompt.write`` / ``prompt.submit`` / ``state.snapshot`` / ``transcript.latest``)
into an actual commandline conversation: send a prompt, wait for the answer to
*settle*, optionally click "Continue generating", and return the final text.

Design goals
------------
* **No printing.** Everything returns structured results so the CLI, tests, and
  future callers can compose it. (``cli.py`` keeps the print-oriented one-shot
  primitives; this module is the reusable brain behind ``ask`` / ``chat`` / ``run``.)
* **Works against the real extension *and* degrades gracefully.** When the page
  reports a precise ``generation`` lifecycle (streaming / needs-continue /
  settled — added in rev0353) the engine uses it. When it does not (older
  extension builds), the engine falls back to transcript-text stability. Either
  way ``send()`` returns a usable answer.
* **Same wire protocol as the CLI.** One short-lived Unix-socket request per
  bridge call, matched by ``request_id`` — identical to ``cli.py`` so there is
  one broker contract, not two.
"""

from __future__ import annotations

import json
import os
import socket
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

JsonDict = dict[str, Any]


# --------------------------------------------------------------------------- #
# Errors
# --------------------------------------------------------------------------- #
class BrokerError(RuntimeError):
    """Base class for conversation/broker transport failures."""


class BrokerUnavailable(BrokerError):
    """The broker socket does not exist (daemon/extension not running)."""


class BrokerTimeout(BrokerError):
    """A bridge request did not receive a matching reply in time."""


class BridgeRequestError(BrokerError):
    """The bridge replied with an ``error.report`` for a request."""


# --------------------------------------------------------------------------- #
# Envelope helpers (kept local so this module has no import cycle with cli.py)
# --------------------------------------------------------------------------- #
def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def make_envelope(message_type: str, payload: JsonDict | None = None, *, tab_id: int | None = None) -> JsonDict:
    envelope: JsonDict = {
        "version": "0.1",
        "request_id": uuid.uuid4().hex,
        "type": message_type,
        "timestamp": _utc_now(),
        "payload": payload or {},
    }
    if tab_id is not None:
        envelope["tab_id"] = tab_id
    return envelope


@dataclass
class BridgeReply:
    """A parsed reply from the browser bridge for one request."""

    type: str
    request_id: str | None
    payload: JsonDict
    raw: JsonDict

    @property
    def is_error(self) -> bool:
        if self.type == "error.report":
            return True
        ok = self.payload.get("ok")
        return ok is False


# --------------------------------------------------------------------------- #
# Broker client — one request/response round trip over the Unix socket
# --------------------------------------------------------------------------- #
@dataclass
class BrokerClient:
    """Minimal client for the GlassTTY broker socket.

    Each :meth:`request` opens a fresh connection, performs the hello handshake,
    submits one browser request, and blocks for the reply whose ``request_id``
    matches. This mirrors the proven flow in ``cli.py`` (``submit_browser_request``)
    but returns data instead of printing it, and swallows unrelated broadcast
    events that the broker fans out to every connected client.
    """

    socket_path: Path
    default_timeout: float = 20.0

    def ensure_available(self) -> None:
        if not self.socket_path.exists():
            raise BrokerUnavailable(
                f"broker socket not found at {self.socket_path}; start the browser "
                f"with the GlassTTY extension + native host, or run `glassttyd mock-tab` "
                f"for an offline dry run"
            )

    def request(
        self,
        message_type: str,
        payload: JsonDict | None = None,
        *,
        tab_id: int | None = None,
        timeout: float | None = None,
    ) -> BridgeReply:
        self.ensure_available()
        envelope = make_envelope(message_type, payload, tab_id=tab_id)
        request_id = envelope["request_id"]
        deadline = time.monotonic() + (timeout if timeout is not None else self.default_timeout)

        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            sock.settimeout(max(0.1, deadline - time.monotonic()))
            try:
                sock.connect(os.fspath(self.socket_path))
            except (ConnectionRefusedError, FileNotFoundError) as exc:
                # The socket file exists but nothing is listening: a crashed
                # broker / stopped browser leaves the inode behind. Report it as
                # "unavailable" rather than leaking a raw socket traceback.
                raise BrokerUnavailable(
                    f"nothing is listening on {self.socket_path} (stale socket from a stopped "
                    f"browser or mock tab). Restart the browser with the GlassTTY extension, "
                    f"or run `glassttyd mock-tab --force`."
                ) from exc
            except OSError as exc:
                raise BrokerError(f"could not connect to broker socket {self.socket_path}: {exc}") from exc
            reader = sock.makefile("r", encoding="utf-8")
            # hello
            self._read_line(reader, deadline, sock)
            sock.sendall((json.dumps({"op": "submit_browser_request", "message": envelope}) + "\n").encode("utf-8"))
            # ack (server stream) then the matching browser_event
            while True:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise BrokerTimeout(f"timed out after {self.default_timeout if timeout is None else timeout}s waiting for {message_type}")
                sock.settimeout(remaining)
                message = self._read_line(reader, deadline, sock)
                if message.get("stream") == "browser_event":
                    inner = message.get("message", {})
                    if inner.get("request_id") == request_id:
                        return BridgeReply(
                            type=str(inner.get("type") or "unknown"),
                            request_id=inner.get("request_id"),
                            payload=inner.get("payload") if isinstance(inner.get("payload"), dict) else {},
                            raw=message,
                        )
                # server acks / other clients' broadcasts: ignore and keep reading
        finally:
            try:
                sock.close()
            except OSError:
                pass

    @staticmethod
    def _read_line(reader, deadline: float, sock: socket.socket) -> JsonDict:
        try:
            line = reader.readline()
        except (TimeoutError, socket.timeout) as exc:  # noqa: UP041 - socket.timeout alias kept for older runtimes
            raise BrokerTimeout("broker socket read timed out") from exc
        except OSError as exc:
            raise BrokerError(f"broker socket error: {exc}") from exc
        if not line:
            raise BrokerError("broker socket closed before a reply arrived")
        return json.loads(line)


# --------------------------------------------------------------------------- #
# Generation lifecycle helpers
# --------------------------------------------------------------------------- #
STREAMING = "streaming-or-stoppable"
NEEDS_CONTINUE = "needs-continue"
SETTLED = "settled-or-idle"


def _generation_state(snapshot_payload: JsonDict) -> str | None:
    gen = snapshot_payload.get("generation")
    if isinstance(gen, dict):
        state = gen.get("state")
        if isinstance(state, str):
            return state
    return None


def _latest_output_text(snapshot_payload: JsonDict) -> str:
    text = snapshot_payload.get("latest_output")
    if isinstance(text, str):
        return text
    witness = snapshot_payload.get("latest_output_witness")
    if isinstance(witness, dict) and isinstance(witness.get("text"), str):
        return witness["text"]
    return ""


# --------------------------------------------------------------------------- #
# Attachments
# --------------------------------------------------------------------------- #
# Chrome's native-messaging host->extension limit is 1 MB, so a package cannot
# cross the bridge whole. 384 KB of raw bytes -> ~512 KB of base64 -> comfortably
# under the limit once the JSON envelope is added.
ATTACH_CHUNK_BYTES = 384 * 1024
MAX_ATTACHMENT_BYTES = 512 * 1024 * 1024

# Files at or below this are treated as corrupt rather than small. The userscript
# queuer's v6.44 incident is the reason: a 0-byte zip was truthy, got attached,
# and the failure surfaced downstream as a mystery "Something went wrong" banner
# while the sync baseline quietly advanced past it.
MIN_ATTACHMENT_BYTES = 1


@dataclass
class AttachResult:
    ok: bool
    path: str
    name: str
    bytes: int
    sha256: str
    chunks: int
    chip_present: bool = False
    input_files_before: int | None = None
    known_chip_keys_before: list[str] = field(default_factory=list)
    input_files: int = 0
    composer_keys_before: list[str] = field(default_factory=list)
    added_keys: list[str] = field(default_factory=list)
    added_controls: list[JsonDict] = field(default_factory=list)
    known_chip_keys: list[str] = field(default_factory=list)
    expected_name_visible_before: bool = False
    expected_name_visible: bool = False
    expected_name_newly_visible: bool = False
    error: str | None = None
    warnings: list[str] = field(default_factory=list)

    def to_json(self) -> JsonDict:
        return {
            "ok": self.ok,
            "path": self.path,
            "name": self.name,
            "bytes": self.bytes,
            "sha256": self.sha256,
            "chunks": self.chunks,
            "chip_present": self.chip_present,
            "input_files_before": self.input_files_before,
            "known_chip_keys_before": self.known_chip_keys_before,
            "input_files": self.input_files,
            "composer_keys_before": self.composer_keys_before,
            "added_keys": self.added_keys,
            "added_controls": self.added_controls,
            "known_chip_keys": self.known_chip_keys,
            "expected_name_visible_before": self.expected_name_visible_before,
            "expected_name_visible": self.expected_name_visible,
            "expected_name_newly_visible": self.expected_name_newly_visible,
            "error": self.error,
            "warnings": self.warnings,
        }


@dataclass
class AttachmentClearResult:
    ok: bool
    input_files: int = 0
    added_keys: list[str] = field(default_factory=list)
    added_controls: list[JsonDict] = field(default_factory=list)
    inputs_seen: int = 0
    files_before: int = 0
    files_after: int = 0
    polls: int = 0
    error: str | None = None

    def to_json(self) -> JsonDict:
        return {
            "ok": self.ok,
            "input_files": self.input_files,
            "added_keys": self.added_keys,
            "added_controls": self.added_controls,
            "inputs_seen": self.inputs_seen,
            "files_before": self.files_before,
            "files_after": self.files_after,
            "polls": self.polls,
            "error": self.error,
        }


# --------------------------------------------------------------------------- #
# Engine configuration and result types
# --------------------------------------------------------------------------- #
@dataclass
class EngineConfig:
    poll_interval: float = 1.0          # seconds between state polls
    max_wait: float = 180.0             # hard ceiling for one answer
    settle_polls: int = 2               # consecutive stable+settled polls to accept
    start_grace: float = 15.0           # how long to wait for generation to *begin*
    auto_continue: bool = True          # click "Continue generating" automatically
    max_continues: int = 12             # safety cap on continue clicks
    request_timeout: float = 20.0       # per bridge request
    require_readback: bool = False      # fail if composer readback != prompt
    keep_snapshots: bool = False        # attach raw poll snapshots to the result
    attach_timeout: float = 180.0       # per-file upload ceiling (70MB packages are slow)
    chip_wait: float = 30.0             # how long to wait for the attachment chip to render
    require_attachment: bool = True     # refuse to submit if an attachment cannot be witnessed


@dataclass
class TurnResult:
    ok: bool
    prompt: str
    text: str | None
    submitted: bool
    settle_reason: str
    submission_outcome: str = "not-attempted"  # "not-attempted" | "submitted" | "unknown"
    continues: int = 0
    polls: int = 0
    elapsed_s: float = 0.0
    baseline_output: str | None = None
    final_generation: str | None = None
    detection: str = "unknown"           # "generation" | "text-stability"
    readback_ok: bool | None = None
    started_at: str = ""
    finished_at: str = ""
    error: str | None = None
    warnings: list[str] = field(default_factory=list)
    attachments: list[JsonDict] = field(default_factory=list)
    attachment_cleanup: JsonDict | None = None
    composer_cleanup: JsonDict | None = None
    snapshots: list[JsonDict] | None = None

    def to_json(self) -> JsonDict:
        data = {
            "ok": self.ok,
            "prompt": self.prompt,
            "text": self.text,
            "submitted": self.submitted,
            "settle_reason": self.settle_reason,
            "submission_outcome": self.submission_outcome,
            "continues": self.continues,
            "polls": self.polls,
            "elapsed_s": round(self.elapsed_s, 3),
            "baseline_output_len": len(self.baseline_output) if self.baseline_output is not None else None,
            "final_generation": self.final_generation,
            "detection": self.detection,
            "readback_ok": self.readback_ok,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "error": self.error,
            "warnings": self.warnings,
            "attachments": self.attachments,
            "attachment_cleanup": self.attachment_cleanup,
            "composer_cleanup": self.composer_cleanup,
        }
        if self.snapshots is not None:
            data["snapshots"] = self.snapshots
        return data


# --------------------------------------------------------------------------- #
# The turn engine
# --------------------------------------------------------------------------- #
class ConversationEngine:
    """Drive a single ChatGPT tab as a conversation over the broker."""

    def __init__(
        self,
        client: BrokerClient,
        *,
        tab_id: int | None = None,
        config: EngineConfig | None = None,
        sleep: Callable[[float], None] = time.sleep,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.client = client
        self.tab_id = tab_id
        self.config = config or EngineConfig()
        self._sleep = sleep
        self._clock = clock

    # -- primitives -------------------------------------------------------- #
    def snapshot(self) -> JsonDict:
        reply = self.client.request("state.snapshot", {}, tab_id=self.tab_id, timeout=self.config.request_timeout)
        if reply.is_error:
            raise BridgeRequestError(str(reply.payload.get("error") or "state.snapshot failed"))
        return reply.payload

    def read_prompt(self) -> str | None:
        reply = self.client.request("prompt.read", {}, tab_id=self.tab_id, timeout=self.config.request_timeout)
        text = reply.payload.get("text")
        return text if isinstance(text, str) else None

    def read_latest(self) -> JsonDict:
        reply = self.client.request("transcript.latest", {}, tab_id=self.tab_id, timeout=self.config.request_timeout)
        return reply.payload

    def write_prompt(self, text: str) -> tuple[bool, bool]:
        """Write the composer text. Returns (write_ok, readback_matches)."""
        reply = self.client.request("prompt.write", {"text": text}, tab_id=self.tab_id, timeout=self.config.request_timeout)
        write_ok = bool(reply.payload.get("ok"))
        readback = reply.payload.get("readback")
        readback_ok = isinstance(readback, str) and readback.strip() == text.strip()
        return write_ok, readback_ok

    def submit(self) -> JsonDict:
        reply = self.client.request("prompt.submit", {}, tab_id=self.tab_id, timeout=self.config.request_timeout)
        return reply.payload

    # -- attachments ------------------------------------------------------- #
    def attach(self, path: Path, *, require_empty_baseline: bool = False) -> AttachResult:
        """Stream a file into the composer's hidden file input, in chunks."""
        import base64
        import hashlib
        import mimetypes

        path = Path(path)
        warnings: list[str] = []
        try:
            if not path.exists():
                return AttachResult(False, str(path), path.name, 0, "", 0, error=f"file not found: {path}")
            if not path.is_file():
                return AttachResult(False, str(path), path.name, 0, "", 0,
                                    error=f"attachment is not a regular file: {path}")
            size = path.stat().st_size
        except OSError as exc:
            return AttachResult(False, str(path), path.name, 0, "", 0,
                                error=f"could not inspect attachment {path}: {exc}")

        if size < MIN_ATTACHMENT_BYTES:
            # Refuse, do not warn. An empty attachment is worse than a missing one:
            # it looks like it worked.
            return AttachResult(False, str(path), path.name, size, hashlib.sha256(b"").hexdigest(), 0,
                                error=f"refusing to attach a zero-byte file: {path}")
        if size > MAX_ATTACHMENT_BYTES:
            return AttachResult(
                False, str(path), path.name, size, "", 0,
                error=f"refusing attachment larger than {MAX_ATTACHMENT_BYTES} bytes: {path}",
            )
        if size < 1024:
            warnings.append(f"{path.name} is only {size} bytes — is that really the file you meant?")

        chunk_count = (size + ATTACH_CHUNK_BYTES - 1) // ATTACH_CHUNK_BYTES
        transfer_id = uuid.uuid4().hex
        mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        transfer_deadline = self._clock() + self.config.attach_timeout

        def transfer_request_timeout() -> float:
            remaining = transfer_deadline - self._clock()
            if remaining <= 0:
                raise BrokerTimeout(
                    f"attachment exceeded the {self.config.attach_timeout}s per-file upload ceiling"
                )
            return max(0.1, min(self.config.request_timeout, remaining))

        def abort_transfer() -> None:
            try:
                self.client.request(
                    "attach.abort", {"transfer_id": transfer_id},
                    tab_id=self.tab_id, timeout=self.config.request_timeout,
                )
            except BrokerError:
                pass

        try:
            begin = self.client.request(
                "attach.begin",
                {"transfer_id": transfer_id, "name": path.name, "mime": mime, "size": size, "chunks": chunk_count},
                tab_id=self.tab_id, timeout=transfer_request_timeout(),
            )
        except BrokerError as exc:
            abort_transfer()
            return AttachResult(False, str(path), path.name, size, "", chunk_count,
                                error=f"attach.begin failed: {exc}", warnings=warnings)
        except BaseException:
            abort_transfer()
            raise
        if not begin.payload.get("ok"):
            return AttachResult(False, str(path), path.name, size, "", chunk_count,
                                error=str(begin.payload.get("error") or "attach.begin was refused"),
                                warnings=warnings)
        keys_before = list(begin.payload.get("composer_keys_before") or [])
        expected_name_visible_before = bool(begin.payload.get("expected_name_visible_before"))
        raw_input_files_before = begin.payload.get("input_files_before")
        input_files_before = (
            raw_input_files_before
            if isinstance(raw_input_files_before, int) and not isinstance(raw_input_files_before, bool)
            and raw_input_files_before >= 0
            else None
        )
        known_chip_keys_before = [
            key for key in (begin.payload.get("known_chip_keys_before") or [])
            if isinstance(key, str)
        ]
        if require_empty_baseline and input_files_before is None:
            abort_transfer()
            return AttachResult(
                False, str(path), path.name, size, "", chunk_count,
                composer_keys_before=keys_before,
                expected_name_visible_before=expected_name_visible_before,
                error="the extension did not report the pre-transfer attachment count; refusing an unsafe send",
                warnings=warnings,
            )
        if require_empty_baseline and (input_files_before != 0 or known_chip_keys_before):
            abort_transfer()
            return AttachResult(
                False, str(path), path.name, size, "", chunk_count,
                input_files_before=input_files_before,
                known_chip_keys_before=known_chip_keys_before,
                composer_keys_before=keys_before,
                expected_name_visible_before=expected_name_visible_before,
                error=(
                    f"the composer already contains attachment evidence "
                    f"({input_files_before} input file(s), {len(known_chip_keys_before)} known chip(s)); refusing to mix "
                    "operator-staged attachments into this send"
                ),
                warnings=warnings,
            )
        digest = hashlib.sha256()
        sent = 0

        try:
            with path.open("rb") as handle:
                for index in range(chunk_count):
                    chunk = handle.read(ATTACH_CHUNK_BYTES)
                    if not chunk:
                        abort_transfer()
                        return AttachResult(
                            False, str(path), path.name, size, digest.hexdigest(), chunk_count,
                            input_files_before=input_files_before,
                            known_chip_keys_before=known_chip_keys_before,
                            composer_keys_before=keys_before,
                            expected_name_visible_before=expected_name_visible_before,
                            error=f"attachment changed or truncated while reading at chunk {index}",
                            warnings=warnings,
                        )
                    digest.update(chunk)
                    sent += len(chunk)
                    reply = self.client.request(
                        "attach.chunk",
                        {"transfer_id": transfer_id, "index": index,
                         "data": base64.b64encode(chunk).decode("ascii")},
                        tab_id=self.tab_id, timeout=transfer_request_timeout(),
                    )
                    if not reply.payload.get("ok"):
                        abort_transfer()
                        return AttachResult(
                            False, str(path), path.name, size, digest.hexdigest(), chunk_count,
                            input_files_before=input_files_before,
                            known_chip_keys_before=known_chip_keys_before,
                            composer_keys_before=keys_before,
                            expected_name_visible_before=expected_name_visible_before,
                            error=f"chunk {index} failed: {reply.payload.get('error')}",
                            warnings=warnings,
                        )
                if handle.read(1) or sent != size:
                    abort_transfer()
                    return AttachResult(
                        False, str(path), path.name, size, digest.hexdigest(), chunk_count,
                        input_files_before=input_files_before,
                        known_chip_keys_before=known_chip_keys_before,
                        composer_keys_before=keys_before,
                        expected_name_visible_before=expected_name_visible_before,
                        error=f"attachment changed size while reading (declared {size}, read {sent})",
                        warnings=warnings,
                    )
        except (OSError, BrokerError) as exc:
            abort_transfer()
            return AttachResult(
                False, str(path), path.name, size, digest.hexdigest(), chunk_count,
                input_files_before=input_files_before,
                known_chip_keys_before=known_chip_keys_before,
                composer_keys_before=keys_before,
                expected_name_visible_before=expected_name_visible_before,
                error=f"attachment transfer failed: {exc}", warnings=warnings,
            )
        except BaseException:
            abort_transfer()
            raise

        try:
            commit = self.client.request(
                "attach.commit", {"transfer_id": transfer_id},
                tab_id=self.tab_id, timeout=transfer_request_timeout(),
            )
        except BrokerError as exc:
            abort_transfer()
            warnings.append("attachment commit outcome is unknown; inspect the composer before sending")
            return AttachResult(
                False, str(path), path.name, size, digest.hexdigest(), chunk_count,
                input_files_before=input_files_before,
                known_chip_keys_before=known_chip_keys_before,
                composer_keys_before=keys_before,
                expected_name_visible_before=expected_name_visible_before,
                error=f"attach.commit failed: {exc}", warnings=warnings,
            )
        except BaseException:
            abort_transfer()
            raise
        payload = commit.payload
        if not payload.get("ok"):
            abort_transfer()
            return AttachResult(
                False, str(path), path.name, size, digest.hexdigest(), chunk_count,
                input_files_before=input_files_before,
                known_chip_keys_before=known_chip_keys_before,
                composer_keys_before=keys_before,
                expected_name_visible_before=expected_name_visible_before,
                error=str(payload.get("error") or "attach.commit failed"), warnings=warnings,
            )

        keys_before = list(payload.get("composer_keys_before") or keys_before)
        expected_name_visible_before = bool(
            payload.get("expected_name_visible_before", expected_name_visible_before)
        )
        witness = payload.get("witness") or {}

        # Poll for the chip. ChatGPT uploads asynchronously: input.files is set the
        # instant we write it, but the file is not really *attached* until the page
        # renders it. Submitting in between is how you send a fileless prompt.
        deadline = self._clock() + self.config.chip_wait
        while not witness.get("chip_present") and self._clock() < deadline:
            self._sleep(0.5)
            try:
                status = self.client.request(
                    "attach.status", {
                        "composer_keys_before": keys_before,
                        "expected_name": path.name,
                        "expected_name_visible_before": expected_name_visible_before,
                    },
                    tab_id=self.tab_id, timeout=self.config.request_timeout,
                )
            except BrokerError as exc:
                warnings.append(f"attachment witness check failed: {exc}")
                break
            witness = status.payload.get("witness") or witness

        if not witness.get("chip_present"):
            warnings.append(
                "no attachment chip appeared in the composer; the file is in the input but the page "
                "may not have accepted it"
            )

        return AttachResult(
            ok=True, path=str(path), name=path.name, bytes=size, sha256=digest.hexdigest(), chunks=chunk_count,
            chip_present=bool(witness.get("chip_present")),
            input_files_before=input_files_before,
            known_chip_keys_before=known_chip_keys_before,
            input_files=int(witness.get("input_files") or 0),
            composer_keys_before=keys_before,
            added_keys=list(witness.get("added_keys") or []),
            added_controls=list(witness.get("added_controls") or []),
            known_chip_keys=list(witness.get("known_chip_keys") or []),
            expected_name_visible_before=expected_name_visible_before,
            expected_name_visible=bool(witness.get("expected_name_visible")),
            expected_name_newly_visible=bool(witness.get("expected_name_newly_visible")),
            warnings=warnings,
        )

    def clear_attachments(
        self,
        composer_keys_before: list[str],
        *,
        expected_name: str = "",
        expected_name_visible_before: bool = False,
    ) -> AttachmentClearResult:
        """Clear file inputs and prove that no attachment controls remain."""
        payload = {
            "composer_keys_before": list(composer_keys_before),
            "expected_name": expected_name,
            "expected_name_visible_before": expected_name_visible_before,
        }
        try:
            reply = self.client.request(
                "attach.clear", payload,
                tab_id=self.tab_id, timeout=self.config.request_timeout,
            )
        except BrokerError as exc:
            return AttachmentClearResult(False, error=f"attach.clear failed: {exc}")

        clear_payload = reply.payload
        if not clear_payload.get("ok"):
            return AttachmentClearResult(
                False,
                inputs_seen=int(clear_payload.get("inputs_seen") or 0),
                files_before=int(clear_payload.get("files_before") or 0),
                files_after=int(clear_payload.get("files_after") or 0),
                error=str(clear_payload.get("error") or "attach.clear was refused"),
            )

        witness = clear_payload.get("witness")
        if not (
            isinstance(witness, dict)
            and "input_files" in witness
            and isinstance(witness.get("added_keys"), list)
        ):
            return AttachmentClearResult(
                False,
                inputs_seen=int(clear_payload.get("inputs_seen") or 0),
                files_before=int(clear_payload.get("files_before") or 0),
                files_after=int(clear_payload.get("files_after") or 0),
                error="the extension did not return a cleanup witness",
            )
        polls = 0
        deadline = self._clock() + self.config.chip_wait
        while (
            (int(witness.get("input_files") or 0) > 0 or bool(witness.get("added_keys")))
            and self._clock() < deadline
        ):
            self._sleep(0.25)
            polls += 1
            try:
                status = self.client.request(
                    "attach.status", payload,
                    tab_id=self.tab_id, timeout=self.config.request_timeout,
                )
            except BrokerError as exc:
                return AttachmentClearResult(False, polls=polls, error=f"attachment cleanup check failed: {exc}")
            next_witness = status.payload.get("witness")
            if not (
                isinstance(next_witness, dict)
                and "input_files" in next_witness
                and isinstance(next_witness.get("added_keys"), list)
            ):
                return AttachmentClearResult(
                    False, polls=polls, error="the extension returned an invalid cleanup witness"
                )
            witness = next_witness

        input_files = int(witness.get("input_files") or 0)
        added_keys = list(witness.get("added_keys") or [])
        clean = input_files == 0 and not added_keys
        return AttachmentClearResult(
            clean,
            input_files=input_files,
            added_keys=added_keys,
            added_controls=list(witness.get("added_controls") or []),
            inputs_seen=int(clear_payload.get("inputs_seen") or 0),
            files_before=int(clear_payload.get("files_before") or 0),
            files_after=int(clear_payload.get("files_after") or 0),
            polls=polls,
            error=None if clean else "attachment input or chip remained after clear",
        )

    def stop(self) -> bool:
        reply = self.client.request("prompt.stop", {}, tab_id=self.tab_id, timeout=self.config.request_timeout)
        return bool(reply.payload.get("ok"))

    def new_chat(self) -> bool:
        reply = self.client.request("chat.new", {}, tab_id=self.tab_id, timeout=self.config.request_timeout)
        return bool(reply.payload.get("ok"))

    def click_continue(self) -> bool:
        reply = self.client.request("prompt.continue", {}, tab_id=self.tab_id, timeout=self.config.request_timeout)
        return bool(reply.payload.get("ok"))

    # -- the send/settle loop --------------------------------------------- #
    def send(self, prompt: str, *, submit: bool = True, attach: list[Path] | None = None) -> TurnResult:
        cfg = self.config
        started_at = _utc_now()
        t0 = self._clock()
        warnings: list[str] = []
        snapshots: list[JsonDict] | None = [] if cfg.keep_snapshots else None
        attachments: list[JsonDict] = []
        rollback_baseline: tuple[list[str], str, bool] | None = None
        readback_ok: bool | None = None

        # 1) baseline: what is the latest assistant text *before* we ask?
        try:
            baseline = _latest_output_text(self.snapshot())
        except BrokerError as exc:
            return self._fail(prompt, f"baseline snapshot failed: {exc}", started_at, t0, submitted=False, warnings=warnings)

        # 2) preserve operator-owned composer state before writing anything.
        try:
            composer_before = self.read_prompt()
        except BrokerError as exc:
            return self._fail(
                prompt, f"prompt.read preflight failed: {exc}", started_at, t0,
                submitted=False, warnings=warnings,
            )
        if composer_before is None:
            return self._fail(
                prompt, "the extension did not return a composer preflight; refusing to overwrite unknown state",
                started_at, t0, submitted=False, warnings=warnings,
            )
        if composer_before:
            return self._fail(
                prompt, "the composer already contains an operator draft; refusing to overwrite it",
                started_at, t0, submitted=False, warnings=warnings,
            )

        def fail_after_staging(error: str, *, submission_outcome: str = "not-attempted") -> TurnResult:
            cleanup_json: JsonDict | None = None
            composer_cleanup: JsonDict | None = None
            if rollback_baseline is not None:
                keys_before, expected_name, expected_name_visible_before = rollback_baseline
                cleanup = self.clear_attachments(
                    keys_before,
                    expected_name=expected_name,
                    expected_name_visible_before=expected_name_visible_before,
                )
                cleanup_json = cleanup.to_json()
                if cleanup.ok:
                    warnings.append("staged attachments were cleared after the failed turn")
                else:
                    detail = cleanup.error or "cleanup witness was not clean"
                    error = (
                        f"{error}; attachment rollback was not verified ({detail}); "
                        "inspect and clear the composer before sending anything else"
                    )
            try:
                restore_ok, restore_readback_ok = self.write_prompt(composer_before)
                composer_cleanup = {
                    "ok": restore_ok and restore_readback_ok,
                    "write_ok": restore_ok,
                    "readback_ok": restore_readback_ok,
                    "restored_text_length": len(composer_before),
                    "error": None,
                }
            except BrokerError as exc:
                composer_cleanup = {
                    "ok": False,
                    "write_ok": False,
                    "readback_ok": False,
                    "restored_text_length": len(composer_before),
                    "error": f"composer restore failed: {exc}",
                }
            if composer_cleanup["ok"]:
                warnings.append("composer text was restored after the failed turn")
            else:
                detail = composer_cleanup.get("error") or "composer restore readback did not match"
                error = (
                    f"{error}; composer text rollback was not verified ({detail}); "
                    "inspect the composer before sending anything else"
                )
            return self._fail(
                prompt, error, started_at, t0,
                submitted=submission_outcome == "submitted",
                submission_outcome=submission_outcome,
                warnings=warnings,
                readback_ok=readback_ok,
                attachments=attachments,
                attachment_cleanup=cleanup_json,
                composer_cleanup=composer_cleanup,
            )

        # 3) write the prompt into the composer.
        try:
            write_ok, readback_ok = self.write_prompt(prompt)
        except BrokerError as exc:
            return fail_after_staging(f"prompt.write failed: {exc}")
        if not write_ok:
            return fail_after_staging("composer rejected the prompt (prompt.write ok=false)")
        if not readback_ok:
            msg = "composer readback did not match the prompt exactly"
            if cfg.require_readback:
                return fail_after_staging(msg)
            warnings.append(msg)

        # 4) attach files BEFORE submit, and refuse to submit if we cannot witness them.
        #
        # This is the fileless-prompt guard. The queuer learned it the hard way: an
        # attachment that silently fails does not look like a failure, it looks like
        # ChatGPT ignoring your request — and you debug the wrong thing for a day.
        for file_index, file_path in enumerate(attach or []):
            result = self.attach(Path(file_path), require_empty_baseline=file_index == 0)
            attachments.append(result.to_json())
            warnings.extend(result.warnings)
            if (
                rollback_baseline is None
                and result.input_files_before == 0
                and not result.known_chip_keys_before
            ):
                rollback_baseline = (
                    list(result.composer_keys_before),
                    result.name,
                    result.expected_name_visible_before,
                )
            if not result.ok:
                return fail_after_staging(f"attachment failed: {result.error}")
            if not result.chip_present and cfg.require_attachment:
                return fail_after_staging(
                    f"attached {result.name} but no attachment chip rendered in the composer; "
                    f"refusing to send a possibly fileless prompt (use --no-require-attachment to override)",
                )

        # 5) optionally stop here (stage-only)
        if not submit:
            elapsed = self._clock() - t0
            return TurnResult(
                ok=True, prompt=prompt, text=None, submitted=False, settle_reason="staged-not-submitted",
                submission_outcome="not-attempted",
                elapsed_s=elapsed, baseline_output=baseline, readback_ok=readback_ok,
                started_at=started_at, finished_at=_utc_now(), warnings=warnings,
                attachments=attachments, snapshots=snapshots,
            )

        # 6) submit
        try:
            submit_payload = self.submit()
        except BrokerError as exc:
            return fail_after_staging(
                f"prompt.submit outcome is unknown: {exc}",
                submission_outcome="unknown",
            )
        if not submit_payload.get("ok"):
            return fail_after_staging(
                "submit was blocked (no send control, wrong route, or empty composer)",
            )

        # 7) poll until the answer settles
        result = self._await_settled(
            prompt=prompt,
            baseline=baseline,
            started_at=started_at,
            t0=t0,
            warnings=warnings,
            snapshots=snapshots,
            readback_ok=readback_ok,
        )
        result.attachments = attachments
        return result

    def _await_settled(
        self,
        *,
        prompt: str,
        baseline: str,
        started_at: str,
        t0: float,
        warnings: list[str],
        snapshots: list[JsonDict] | None,
        readback_ok: bool | None,
    ) -> TurnResult:
        cfg = self.config
        deadline = t0 + cfg.max_wait
        start_deadline = t0 + cfg.start_grace

        polls = 0
        continues = 0
        stable_ticks = 0
        last_text = baseline
        current_text = baseline
        started_observed = False
        detection = "unknown"
        final_generation: str | None = None

        while True:
            now = self._clock()
            if now >= deadline:
                return TurnResult(
                    ok=False, prompt=prompt, text=(current_text or None), submitted=True,
                    settle_reason="timeout", continues=continues, polls=polls,
                    submission_outcome="submitted",
                    elapsed_s=now - t0, baseline_output=baseline, final_generation=final_generation,
                    detection=detection, readback_ok=readback_ok, started_at=started_at,
                    finished_at=_utc_now(), error=f"answer did not settle within {cfg.max_wait}s",
                    warnings=warnings, snapshots=snapshots,
                )

            try:
                snap = self.snapshot()
            except BrokerError as exc:
                # transient bridge hiccup; keep trying until the deadline
                warnings.append(f"snapshot error (retrying): {exc}")
                self._sleep(cfg.poll_interval)
                continue

            polls += 1
            if snapshots is not None:
                snapshots.append(snap)

            gen_state = _generation_state(snap)
            current_text = _latest_output_text(snap)
            changed = bool(current_text) and current_text != baseline
            final_generation = gen_state

            if gen_state is not None:
                detection = "generation"
                if gen_state == STREAMING:
                    started_observed = True
                    stable_ticks = 0
                    last_text = current_text
                elif gen_state == NEEDS_CONTINUE:
                    started_observed = True
                    if cfg.auto_continue and continues < cfg.max_continues:
                        try:
                            self.click_continue()
                        except BrokerError as exc:
                            warnings.append(f"continue click failed: {exc}")
                        continues += 1
                        stable_ticks = 0
                        last_text = current_text
                    else:
                        # not continuing: treat the current text as the answer
                        return self._settle(
                            prompt, current_text, "needs-continue-not-followed", continues, polls,
                            self._clock() - t0, baseline, gen_state, detection, readback_ok, started_at,
                            warnings, snapshots,
                        )
                else:  # SETTLED
                    if started_observed or changed:
                        if current_text == last_text:
                            stable_ticks += 1
                        else:
                            stable_ticks = 1
                            last_text = current_text
                        if stable_ticks >= cfg.settle_polls:
                            return self._settle(
                                prompt, current_text, "generation-settled", continues, polls,
                                self._clock() - t0, baseline, gen_state, detection, readback_ok,
                                started_at, warnings, snapshots,
                            )
                    else:
                        # awaiting start: settled but nothing has happened yet
                        if now >= start_deadline:
                            reason = "no-generation-detected" if not changed else "settled-no-stream"
                            ok = changed
                            result = self._settle(
                                prompt, current_text if changed else None, reason, continues, polls,
                                self._clock() - t0, baseline, gen_state, detection, readback_ok,
                                started_at, warnings, snapshots,
                            )
                            result.ok = ok
                            if not ok:
                                result.error = "submit succeeded but no generation started (page may have drifted)"
                            return result
            else:
                # Fallback: no generation lifecycle exposed; use text stability.
                detection = "text-stability"
                if changed:
                    started_observed = True
                    if current_text == last_text:
                        stable_ticks += 1
                    else:
                        stable_ticks = 1
                        last_text = current_text
                    if stable_ticks >= cfg.settle_polls:
                        return self._settle(
                            prompt, current_text, "output-stable", continues, polls,
                            self._clock() - t0, baseline, None, detection, readback_ok,
                            started_at, warnings, snapshots,
                        )
                elif now >= start_deadline:
                    result = self._settle(
                        prompt, None, "no-output-change", continues, polls,
                        self._clock() - t0, baseline, None, detection, readback_ok,
                        started_at, warnings, snapshots,
                    )
                    result.ok = False
                    result.error = "no new assistant text appeared (no generation signal available)"
                    return result

            self._sleep(cfg.poll_interval)

    # -- result builders --------------------------------------------------- #
    def _settle(
        self, prompt, text, reason, continues, polls, elapsed, baseline, gen, detection,
        readback_ok, started_at, warnings, snapshots,
    ) -> TurnResult:
        return TurnResult(
            ok=True, prompt=prompt, text=(text or None), submitted=True, settle_reason=reason,
            submission_outcome="submitted",
            continues=continues, polls=polls, elapsed_s=elapsed, baseline_output=baseline,
            final_generation=gen, detection=detection, readback_ok=readback_ok,
            started_at=started_at, finished_at=_utc_now(), warnings=warnings, snapshots=snapshots,
        )

    def _fail(
        self, prompt, error, started_at, t0, *, submitted, warnings, readback_ok=None,
        attachments=None, attachment_cleanup=None, composer_cleanup=None, submission_outcome=None,
    ) -> TurnResult:
        return TurnResult(
            ok=False, prompt=prompt, text=None, submitted=submitted, settle_reason="error",
            submission_outcome=submission_outcome or ("submitted" if submitted else "not-attempted"),
            elapsed_s=self._clock() - t0, readback_ok=readback_ok, started_at=started_at,
            finished_at=_utc_now(), error=error, warnings=warnings, attachments=attachments or [],
            attachment_cleanup=attachment_cleanup, composer_cleanup=composer_cleanup,
        )
