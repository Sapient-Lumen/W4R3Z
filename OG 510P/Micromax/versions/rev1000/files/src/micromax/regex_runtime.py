"""Shared killable execution for backtracking regex operations.

Python's standard :mod:`re` API does not expose a wall-clock match timeout.
Micromax therefore runs caller-authored editor regex matching in a one-shot,
stdlib-only ``python -I -S`` child that can be killed without wedging the editor
process.  Unlike ``spawn``/``forkserver``, the default child does not import the
editor, the VM, site packages, or native extension stacks before matching, so a
250 ms foreground match deadline remains useful in a heavily threaded
cloudtainer.  Child startup has a separate bounded allowance and a ready
handshake; scheduler pressure cannot consume the match clock before the child
is able to read the request.

On Linux, every parent-created worker also receives a finite post-request
virtual-address-space headroom budget.  The fresh child installs ``RLIMIT_AS``
after decoding the owned request and before regex compilation or matching, so
native repeat/backtracking state and replacement/result construction cannot grow
without an operating-system ceiling.  Other platforms retain the killable time
boundary; this is resource containment, not a syscall or crash sandbox.

VM regex hostcalls use the same child by default for every pattern; the legacy
shape classifier remains only as a compatibility/diagnostic helper, not as a
safety boundary.  Callers may inject a multiprocessing context for tests or
unusual embeddings; the default never forks a multithreaded parent.
"""

from __future__ import annotations

import json
import math
import multiprocessing
import subprocess
import sys
import tempfile
import threading
import time
from collections.abc import Iterable
from contextlib import suppress
from pathlib import Path

from .regex_worker_child import (
    HANDSHAKE_ARGUMENT,
    HAYSTACK_FILE_PROTOCOL,
    PROTOCOL,
    execute_worker_request,
)
from .subprocess_start import (
    SubprocessStartError,
    SubprocessStartTimeoutError,
    start_subprocess_with_deadline,
)
from .worker_process import (
    WorkerResultError,
    WorkerResultSender,
    WorkerResultTimeoutError,
    collect_worker_result,
    create_one_shot_worker,
    isolated_worker_context,
)

DEFAULT_REGEX_WORKER_RESULT_MAX_BYTES = 16 * 1024 * 1024
# Keep enough post-request headroom for the existing 16 MiB result budget while
# preventing the regex engine from turning one foreground operation into an
# unbounded native allocation.  The Linux child measures its current virtual
# size after request decoding, then seals RLIMIT_AS at baseline + this amount.
DEFAULT_REGEX_WORKER_MEMORY_HEADROOM_BYTES = 144 * 1024 * 1024
DEFAULT_REGEX_WORKER_STARTUP_TIMEOUT_SECONDS = 2.0
_PROTOCOL_OVERHEAD_BYTES = 64 * 1024
_READY_MAX_BYTES = 1024
_HAYSTACK_FILE_WRITE_CHARS = 256 * 1024


class RegexWorkerError(RuntimeError):
    """Base failure for one contained regex operation."""


class RegexWorkerTimeoutError(RegexWorkerError):
    """Raised after a contained regex exceeds its wall-clock deadline."""


class RegexWorkerStartupTimeoutError(RegexWorkerError):
    """Raised when the isolated child does not become ready in time."""


class RegexWorkerProtocolError(RegexWorkerError):
    """Raised when a regex worker exits or returns malformed data."""


class RegexWorkerOperationError(RegexWorkerError):
    """A stable caller-visible regex, replacement, or result-budget failure."""

    def __init__(self, kind: str, message: str) -> None:
        super().__init__(str(message))
        self.kind = str(kind)


def regex_worker_context() -> multiprocessing.context.BaseContext:
    """Return the legacy/injected multiprocessing context.

    This path is not the interactive default.  It remains available for tests
    and embeddings that explicitly provide a context.  It uses the same
    spawn/forkserver-only policy as every other deadline-owned worker; a helper
    thread cannot safely initiate POSIX ``fork`` even when the caller was
    single-threaded before the operation began.
    """
    return isolated_worker_context()


def _quantifier_end(pattern: str, index: int) -> int:
    """Return the index after a regex quantifier, or the input index."""

    if index >= len(pattern):
        return index
    char = pattern[index]
    if char in "*+?":
        end = index + 1
        if end < len(pattern) and pattern[end] in "?+":
            end += 1
        return end
    if char != "{":
        return index
    end = index + 1
    saw_digit = False
    while end < len(pattern) and pattern[end].isdigit():
        saw_digit = True
        end += 1
    if end < len(pattern) and pattern[end] == ",":
        end += 1
        while end < len(pattern) and pattern[end].isdigit():
            saw_digit = True
            end += 1
    if not saw_digit or end >= len(pattern) or pattern[end] != "}":
        return index
    end += 1
    if end < len(pattern) and pattern[end] in "?+":
        end += 1
    return end


def _skip_group_prefix(pattern: str, index: int) -> int:
    """Return the first content index after a ``(?...)`` group prefix."""

    if index >= len(pattern) or pattern[index] != "?":
        return index
    index += 1
    if index < len(pattern) and pattern[index] == "P":
        if index + 1 < len(pattern) and pattern[index + 1] == "=":
            return -1
        if index + 1 < len(pattern) and pattern[index + 1] == "<":
            end = pattern.find(">", index + 2)
            return len(pattern) if end < 0 else end + 1
    if (
        index < len(pattern)
        and pattern[index] == "<"
        and index + 1 < len(pattern)
        and pattern[index + 1] in "=<!"
    ):
        return index + 2
    if index < len(pattern) and pattern[index] in ":=!#":
        return index + 1
    while index < len(pattern) and (pattern[index].isalpha() or pattern[index] == "-"):
        index += 1
    if index < len(pattern) and pattern[index] == ":":
        return index + 1
    return index


def regex_pattern_needs_containment(pattern: str) -> bool:
    """Recognize common catastrophic-backtracking shapes for VM hostcalls.

    This is a compatibility routing heuristic, not a safety proof.  Direct
    editor regex surfaces do not rely on it: they route every non-literal match
    operation to the bounded worker by default.
    """

    stack: list[dict[str, bool]] = []
    last_group: dict[str, bool] | None = None
    in_class = False
    index = 0
    while index < len(pattern):
        char = pattern[index]
        if char == "\\":
            if index + 1 < len(pattern):
                following = pattern[index + 1]
                if following.isdigit() or following == "g":
                    return True
            index += 2
            last_group = None
            continue
        if in_class:
            if char == "]":
                in_class = False
            index += 1
            last_group = None
            continue
        if char == "[":
            in_class = True
            index += 1
            last_group = None
            continue
        if char == "(":
            stack.append({"has_repeat": False, "has_alt": False})
            index += 1
            if index < len(pattern) and pattern[index] == "?":
                skipped = _skip_group_prefix(pattern, index)
                if skipped < 0:
                    return True
                index = skipped
            last_group = None
            continue
        if char == ")":
            last_group = stack.pop() if stack else {"has_repeat": False, "has_alt": False}
            index += 1
            continue
        if char == "|":
            if stack:
                stack[-1]["has_alt"] = True
            index += 1
            last_group = None
            continue
        quantifier_end = _quantifier_end(pattern, index)
        if quantifier_end != index:
            if last_group is not None and (
                last_group.get("has_repeat") or last_group.get("has_alt")
            ):
                return True
            if stack:
                stack[-1]["has_repeat"] = True
            index = quantifier_end
            last_group = None
            continue
        last_group = None
        index += 1
    return False


def _request(
    *,
    action: str,
    haystack: str,
    pattern: str,
    start: int,
    flags: object,
    replacement: str | None,
    max_matches: int | None,
    replace_all: bool,
    max_result_bytes: int | None,
    max_memory_headroom_bytes: int | None,
) -> dict[str, object]:
    return {
        "protocol": PROTOCOL,
        "action": str(action),
        "haystack": str(haystack),
        "pattern": str(pattern),
        "start": int(start),
        "flags": flags,
        "replacement": replacement,
        "max_matches": max_matches,
        "replace_all": bool(replace_all),
        "max_result_bytes": max_result_bytes,
        "max_memory_headroom_bytes": max_memory_headroom_bytes,
    }


def _file_request(
    *,
    action: str,
    haystack_path: Path,
    haystack_bytes: int,
    haystack_chars: int,
    pattern: str,
    start: int,
    flags: object,
    replacement: str | None,
    max_matches: int | None,
    replace_all: bool,
    max_result_bytes: int | None,
    max_memory_headroom_bytes: int | None,
) -> dict[str, object]:
    """Return one small request referring to a private exact-text transport.

    Large editor snapshots should not be joined, JSON-escaped, UTF-8 encoded,
    and then decoded merely to cross the one-shot worker boundary.  The parent
    instead writes bounded chunks into one private temporary file and sends only
    this validated descriptor.  The child still reconstructs the one ``str``
    required by :mod:`re`, but the parent no longer owns a complete flat source
    or a complete JSON/bytes copy at the same time.
    """

    return {
        "protocol": PROTOCOL,
        "action": str(action),
        "haystack_file": {
            "protocol": HAYSTACK_FILE_PROTOCOL,
            "path": str(haystack_path),
            "bytes": int(haystack_bytes),
            "characters": int(haystack_chars),
        },
        "pattern": str(pattern),
        "start": int(start),
        "flags": flags,
        "replacement": replacement,
        "max_matches": max_matches,
        "replace_all": bool(replace_all),
        "max_result_bytes": max_result_bytes,
        "max_memory_headroom_bytes": max_memory_headroom_bytes,
    }


def _write_haystack_chunks(path: Path, chunks: Iterable[str]) -> tuple[int, int]:
    """Write exact source chunks with bounded transient encoding storage.

    ``newline=''`` prevents platform newline translation, and ``surrogatepass``
    preserves every Python string code point accepted by the editor.  Splitting
    each incoming piece bounds the encoder's temporary byte allocation even when
    one logical line is very large.
    """

    characters = 0
    try:
        with path.open(
            "x",
            encoding="utf-8",
            errors="surrogatepass",
            newline="",
        ) as stream:
            for raw_chunk in chunks:
                chunk = str(raw_chunk)
                characters += len(chunk)
                for left in range(0, len(chunk), _HAYSTACK_FILE_WRITE_CHARS):
                    stream.write(chunk[left : left + _HAYSTACK_FILE_WRITE_CHARS])
        byte_count = int(path.stat().st_size)
    except (OSError, UnicodeError, ValueError) as exc:
        raise RegexWorkerProtocolError(
            f"regex worker haystack transport failed: {exc}"
        ) from exc
    return byte_count, int(characters)


def _regex_worker_main(
    request: dict[str, object],
    sender: WorkerResultSender,
) -> None:
    """Multiprocessing adapter around the stdlib-only pure executor."""

    try:
        sender.put(execute_worker_request(request))
    except BaseException as exc:
        with suppress(BaseException):
            sender.put(
                {
                    "protocol": PROTOCOL,
                    "ok": False,
                    "kind": "worker",
                    "message": f"{type(exc).__name__}: {exc}",
                }
            )
    finally:
        sender.close()


def _run_multiprocessing_worker(
    request: dict[str, object],
    *,
    timeout: float,
    context: multiprocessing.context.BaseContext,
    max_result_bytes: int,
) -> dict[str, object]:
    """Run the injected compatibility worker over the shared full-frame channel.

    ``Connection.poll()`` only bounds the wait for the first bytes of a framed
    pickle; ``recv()`` may still block forever after a partial length/payload.
    The shared one-shot transport reads every frame byte under the same absolute
    deadline and owns endpoint/process teardown, matching the filesystem and
    plugin worker families rather than keeping a weaker regex-only exception.
    """

    channel_limit = max(
        _PROTOCOL_OVERHEAD_BYTES,
        int(max_result_bytes) + _PROTOCOL_OVERHEAD_BYTES,
    )
    try:
        process, channel = create_one_shot_worker(
            context,
            target=_regex_worker_main,
            args=(request,),
            max_result_bytes=channel_limit,
        )
        payload = collect_worker_result(
            process,
            channel,
            timeout_seconds=timeout,
            operation="regex",
            join_timeout=0.2,
        )
    except WorkerResultTimeoutError as exc:
        raise RegexWorkerTimeoutError(f"regex timed out after {timeout:g}s") from exc
    except WorkerResultError as exc:
        raise RegexWorkerProtocolError(f"regex worker failed: {exc}") from exc
    except Exception as exc:
        raise RegexWorkerProtocolError(f"regex worker failed: {exc}") from exc

    if not isinstance(payload, dict):
        raise RegexWorkerProtocolError("regex worker returned a malformed result")
    return payload


def _subprocess_worker_command() -> list[str]:
    executable = str(sys.executable or "").strip()
    child = Path(__file__).with_name("regex_worker_child.py")
    if not executable:
        raise RegexWorkerProtocolError("regex worker unavailable: no Python executable")
    if not child.is_file():
        raise RegexWorkerProtocolError(
            f"regex worker unavailable: child script not found: {child}"
        )
    # -I ignores caller environment and user site; -S skips site initialization.
    return [executable, "-I", "-S", str(child), HANDSHAKE_ARGUMENT]


def _kill_and_collect_subprocess(
    process: subprocess.Popen[bytes],
    *,
    reader: threading.Thread | None = None,
) -> tuple[bytes, bytes]:
    """Kill one owned child and finish its pipes without leaking a reader."""

    with suppress(BaseException):
        process.kill()
    if reader is not None:
        with suppress(BaseException):
            reader.join(timeout=1.0)
        # ``Thread.start`` may fail before the reader becomes joinable, or
        # teardown itself may be interrupted.  Process ownership is more
        # important than propagating a second failure from best-effort reader
        # drainage; the original exception remains authoritative.
    try:
        return process.communicate(timeout=1.0)
    except BaseException:
        with suppress(BaseException):
            process.wait(timeout=0.2)
        return (b"", b"")


def _wait_for_subprocess_ready(
    process: subprocess.Popen[bytes],
    *,
    startup_timeout: float,
    deadline: float,
) -> None:
    """Wait portably for one newline-delimited ready envelope.

    ``selectors`` cannot monitor anonymous subprocess pipes uniformly on all
    supported platforms. A one-shot reader thread is safe here because the
    parent owns both the process and pipe, and killing the process closes the
    writer so the thread can be joined before the operation returns.
    """

    reader: threading.Thread | None = None
    try:
        if process.stdout is None:
            raise RegexWorkerProtocolError("regex worker stdout pipe is unavailable")

        lines: list[bytes] = []
        failures: list[BaseException] = []
        completed_at: list[float] = []

        def read_ready() -> None:
            try:
                lines.append(process.stdout.readline(_READY_MAX_BYTES + 1))
            except BaseException as exc:
                failures.append(exc)
            finally:
                completed_at.append(time.monotonic())

        reader = threading.Thread(
            target=read_ready,
            name="micromax-regex-ready",
            daemon=True,
        )
        reader.start()
        reader.join(timeout=max(0.0, deadline - time.monotonic()))
        if reader.is_alive():
            raise RegexWorkerStartupTimeoutError(
                f"regex worker startup timed out after {startup_timeout:g}s"
            )
        if failures:
            failure = failures[0]
            raise RegexWorkerProtocolError(
                f"regex worker readiness failed: {failure}"
            ) from failure
        if not completed_at or completed_at[0] > deadline:
            raise RegexWorkerStartupTimeoutError(
                f"regex worker startup timed out after {startup_timeout:g}s"
            )

        line = lines[0] if lines else b""
        if len(line) > _READY_MAX_BYTES or not line.endswith(b"\n"):
            raise RegexWorkerProtocolError(
                "regex worker returned an oversized or unterminated "
                "readiness envelope"
            )
        try:
            ready = json.loads(line.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise RegexWorkerProtocolError(
                f"regex worker returned malformed readiness JSON: {exc}"
            ) from exc
        if not isinstance(ready, dict) or ready != {
            "protocol": PROTOCOL,
            "ready": True,
        }:
            raise RegexWorkerProtocolError(
                "regex worker returned the wrong readiness protocol"
            )
    except BaseException:
        # Ownership begins when ``Popen`` returns, not when the ready line has
        # been decoded.  This one exit path covers reader construction/start,
        # asynchronous interruption, deadline expiry, and protocol rejection.
        _kill_and_collect_subprocess(process, reader=reader)
        raise


def _run_stdlib_subprocess_worker(
    request: dict[str, object],
    *,
    timeout: float,
    startup_timeout: float,
    max_result_bytes: int,
) -> dict[str, object]:
    try:
        # File-backed requests may contain a temporary-directory path decoded
        # with the filesystem ``surrogateescape`` handler.  Escaping that small
        # descriptor keeps every path code point JSON-safe without expanding
        # ordinary flat haystacks, whose established wire-size behavior remains
        # unchanged.
        encoded_request = json.dumps(
            request,
            ensure_ascii="haystack_file" in request,
            separators=(",", ":"),
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise RegexWorkerProtocolError(
            f"regex worker request is not serializable: {exc}"
        ) from exc

    startup_deadline = time.monotonic() + startup_timeout
    try:
        process = start_subprocess_with_deadline(
            lambda: subprocess.Popen(
                _subprocess_worker_command(),
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                close_fds=True,
            ),
            cleanup=lambda late: _kill_and_collect_subprocess(late),
            deadline=startup_deadline,
            timeout_seconds=startup_timeout,
            operation="regex worker",
        )
    except SubprocessStartTimeoutError as exc:
        raise RegexWorkerStartupTimeoutError(
            f"regex worker startup timed out after {startup_timeout:g}s"
        ) from exc
    except SubprocessStartError as exc:
        raise RegexWorkerProtocolError(f"regex worker unavailable: {exc}") from exc

    completed_at_deadline = False
    stdout = b""
    stderr = b""
    try:
        _wait_for_subprocess_ready(
            process,
            startup_timeout=startup_timeout,
            deadline=startup_deadline,
        )
        stdout, stderr = process.communicate(input=encoded_request, timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        # ``communicate`` waits for both protocol output and process exit.  A
        # child can finish matching, flush one complete response, and then lose
        # its final scheduling slice before interpreter teardown.  Kill the
        # owned one-shot child either way, but accept only a complete valid
        # protocol envelope that was already emitted by the deadline; partial
        # output remains a real timeout.
        # ``TimeoutExpired.output`` is the data communicate had already read at
        # the deadline.  Decode only that snapshot: output raced out after the
        # deadline but before ``kill()`` must not convert a timeout into success.
        deadline_stdout = exc.output if isinstance(exc.output, bytes) else b""
        _kill_and_collect_subprocess(process)
        try:
            payload = _decode_subprocess_payload(
                deadline_stdout,
                max_result_bytes=max_result_bytes,
            )
        except RegexWorkerProtocolError:
            raise RegexWorkerTimeoutError(
                f"regex timed out after {timeout:g}s"
            ) from exc
        if payload.get("protocol") != PROTOCOL or (
            payload.get("ok") is not True and payload.get("ok") is not False
        ):
            raise RegexWorkerTimeoutError(
                f"regex timed out after {timeout:g}s"
            ) from exc
        completed_at_deadline = True
    except BaseException:
        _kill_and_collect_subprocess(process)
        raise

    if process.returncode != 0 and not completed_at_deadline:
        detail = stderr.decode("utf-8", errors="replace").strip()
        if len(detail) > 512:
            detail = detail[:509] + "..."
        suffix = f": {detail}" if detail else ""
        raise RegexWorkerProtocolError(
            f"regex worker exited with status {process.returncode}{suffix}"
        )

    if completed_at_deadline:
        return payload
    return _decode_subprocess_payload(stdout, max_result_bytes=max_result_bytes)


def _decode_subprocess_payload(
    stdout: bytes,
    *,
    max_result_bytes: int,
) -> dict[str, object]:
    """Decode one bounded child response without trusting process exit status."""

    output_ceiling = max(
        _PROTOCOL_OVERHEAD_BYTES,
        int(max_result_bytes) + _PROTOCOL_OVERHEAD_BYTES,
    )
    if len(stdout) > output_ceiling:
        raise RegexWorkerProtocolError(
            "regex worker protocol output exceeded budget: "
            f"{len(stdout)} bytes > {output_ceiling}"
        )
    try:
        payload = json.loads(stdout.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RegexWorkerProtocolError(
            f"regex worker returned malformed JSON: {exc}"
        ) from exc
    if not isinstance(payload, dict):
        raise RegexWorkerProtocolError("regex worker returned a malformed result")
    return payload


def _validated_value(payload: dict[str, object]) -> object:
    if payload.get("protocol") != PROTOCOL:
        raise RegexWorkerProtocolError("regex worker returned the wrong protocol")
    if payload.get("ok") is not True:
        kind = str(payload.get("kind") or "worker")
        message = str(payload.get("message") or "regex worker failed")
        if kind == "worker":
            raise RegexWorkerError(f"regex worker failed: {message}")
        if kind == "protocol":
            raise RegexWorkerProtocolError(message)
        raise RegexWorkerOperationError(kind, message)
    return payload.get("value")


def _positive_worker_budget(value: object, *, default: int, label: str) -> int:
    """Return one finite positive child budget or the guarded default.

    Python booleans are integers at the host level, but accepting ``True`` as a
    one-byte result or memory lease is never an intentional Micromax spelling.
    Keep malformed numeric configuration visible before a worker is spawned.
    """

    if isinstance(value, bool):
        raise RegexWorkerError(f"invalid regex worker {label}")
    try:
        parsed = int(default if value is None else value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise RegexWorkerError(f"invalid regex worker {label}") from exc
    return int(default) if parsed <= 0 else int(parsed)


def _worker_execution_policy(
    *,
    timeout_seconds: float,
    startup_timeout_seconds: float,
    max_result_bytes: int | None,
    max_memory_headroom_bytes: int | None,
    worker_context: multiprocessing.context.BaseContext | None,
) -> tuple[float, float, int, int]:
    """Normalize the shared one-shot worker deadlines and finite budgets."""

    try:
        timeout = float(timeout_seconds)
    except (TypeError, ValueError, OverflowError) as exc:
        raise RegexWorkerError("invalid regex worker timeout") from exc
    if not math.isfinite(timeout) or timeout <= 0:
        raise RegexWorkerError("regex worker timeout is disabled")

    startup_timeout = float(DEFAULT_REGEX_WORKER_STARTUP_TIMEOUT_SECONDS)
    if worker_context is None:
        try:
            startup_timeout = float(startup_timeout_seconds)
        except (TypeError, ValueError, OverflowError) as exc:
            raise RegexWorkerError("invalid regex worker startup timeout") from exc
        if not math.isfinite(startup_timeout) or startup_timeout <= 0:
            raise RegexWorkerError("regex worker startup timeout is disabled")

    result_limit = _positive_worker_budget(
        max_result_bytes,
        default=DEFAULT_REGEX_WORKER_RESULT_MAX_BYTES,
        label="result budget",
    )
    memory_headroom = _positive_worker_budget(
        max_memory_headroom_bytes,
        default=DEFAULT_REGEX_WORKER_MEMORY_HEADROOM_BYTES,
        label="memory headroom",
    )
    return timeout, startup_timeout, result_limit, memory_headroom


def _run_prepared_regex_request(
    request: dict[str, object],
    *,
    timeout: float,
    startup_timeout: float,
    result_limit: int,
    worker_context: multiprocessing.context.BaseContext | None,
) -> object:
    """Execute one already-owned request through the selected worker adapter."""

    if worker_context is not None:
        payload = _run_multiprocessing_worker(
            request,
            timeout=timeout,
            context=worker_context,
            max_result_bytes=result_limit,
        )
    else:
        payload = _run_stdlib_subprocess_worker(
            request,
            timeout=timeout,
            startup_timeout=startup_timeout,
            max_result_bytes=result_limit,
        )
    return _validated_value(payload)


def run_regex_worker(
    *,
    action: str,
    haystack: str,
    pattern: str,
    timeout_seconds: float,
    startup_timeout_seconds: float = DEFAULT_REGEX_WORKER_STARTUP_TIMEOUT_SECONDS,
    start: int = 0,
    flags: object = "",
    replacement: str | None = None,
    max_matches: int | None = None,
    replace_all: bool = True,
    max_result_bytes: int | None = DEFAULT_REGEX_WORKER_RESULT_MAX_BYTES,
    max_memory_headroom_bytes: int | None = (
        DEFAULT_REGEX_WORKER_MEMORY_HEADROOM_BYTES
    ),
    worker_context: multiprocessing.context.BaseContext | None = None,
) -> object:
    """Run one regex action in a killable child and return plain data.

    The default is a minimal fresh interpreter, not multiprocessing.  Supplying
    ``worker_context`` explicitly selects the compatibility/test adapter.
    """

    timeout, startup_timeout, result_limit, memory_headroom = (
        _worker_execution_policy(
            timeout_seconds=timeout_seconds,
            startup_timeout_seconds=startup_timeout_seconds,
            max_result_bytes=max_result_bytes,
            max_memory_headroom_bytes=max_memory_headroom_bytes,
            worker_context=worker_context,
        )
    )

    request = _request(
        action=action,
        haystack=haystack,
        pattern=pattern,
        start=start,
        flags=flags,
        replacement=replacement,
        max_matches=max_matches,
        replace_all=replace_all,
        max_result_bytes=result_limit,
        max_memory_headroom_bytes=memory_headroom,
    )

    return _run_prepared_regex_request(
        request,
        timeout=timeout,
        startup_timeout=startup_timeout,
        result_limit=result_limit,
        worker_context=worker_context,
    )


def _cleanup_haystack_directory(
    directory: tempfile.TemporaryDirectory[str],
    *,
    primary: BaseException | None = None,
) -> None:
    """Release one file-backed source owner without hiding primary failure.

    A cleanup error after a successful scan is still an operation failure: the
    editor must not enter capture mode while plaintext source residue is known to
    remain.  During timeout, interruption, or another primary failure, preserve
    that authoritative exception and attach the cleanup problem as a diagnostic
    note instead of replacing it.
    """

    try:
        directory.cleanup()
    except OSError as exc:
        message = f"regex worker haystack transport cleanup failed: {exc}"
        if primary is not None:
            # ``BaseException.add_note`` arrived in Python 3.11, while Micromax
            # still supports Python 3.10.  Preserve the primary failure on both
            # runtimes; attach the diagnostic only where that API exists.
            add_note = getattr(primary, "add_note", None)
            if callable(add_note):
                add_note(message)
            return
        raise RegexWorkerProtocolError(message) from exc


def run_regex_worker_from_chunks(
    *,
    action: str,
    haystack_chunks: Iterable[str],
    pattern: str,
    timeout_seconds: float,
    startup_timeout_seconds: float = DEFAULT_REGEX_WORKER_STARTUP_TIMEOUT_SECONDS,
    expected_haystack_chars: int | None = None,
    start: int = 0,
    flags: object = "",
    replacement: str | None = None,
    max_matches: int | None = None,
    replace_all: bool = True,
    max_result_bytes: int | None = DEFAULT_REGEX_WORKER_RESULT_MAX_BYTES,
    max_memory_headroom_bytes: int | None = (
        DEFAULT_REGEX_WORKER_MEMORY_HEADROOM_BYTES
    ),
    worker_context: multiprocessing.context.BaseContext | None = None,
) -> object:
    """Run one regex action without retaining a complete parent source string.

    The source iterator is consumed exactly once into a securely-created private
    temporary directory.  Only a small descriptor crosses the worker's JSON or
    multiprocessing channel; the directory is removed after success, timeout,
    startup failure, protocol rejection, or interruption.
    """

    timeout, startup_timeout, result_limit, memory_headroom = (
        _worker_execution_policy(
            timeout_seconds=timeout_seconds,
            startup_timeout_seconds=startup_timeout_seconds,
            max_result_bytes=max_result_bytes,
            max_memory_headroom_bytes=max_memory_headroom_bytes,
            worker_context=worker_context,
        )
    )

    expected: int | None = None
    if expected_haystack_chars is not None:
        if (
            isinstance(expected_haystack_chars, bool)
            or not isinstance(expected_haystack_chars, int)
            or expected_haystack_chars < 0
        ):
            raise RegexWorkerProtocolError(
                "invalid regex worker expected haystack length"
            )
        expected = int(expected_haystack_chars)

    directory: tempfile.TemporaryDirectory[str]
    try:
        directory = tempfile.TemporaryDirectory(prefix="micromax-regex-")
    except OSError as exc:
        raise RegexWorkerProtocolError(
            f"regex worker haystack transport setup failed: {exc}"
        ) from exc

    try:
        path = Path(directory.name) / "haystack.utf8"
        byte_count, character_count = _write_haystack_chunks(
            path,
            haystack_chunks,
        )
        if expected is not None and expected != character_count:
            raise RegexWorkerProtocolError(
                "regex worker haystack length changed while staging: "
                f"{character_count} characters != {expected}"
            )

        request = _file_request(
            action=action,
            haystack_path=path,
            haystack_bytes=byte_count,
            haystack_chars=character_count,
            pattern=pattern,
            start=start,
            flags=flags,
            replacement=replacement,
            max_matches=max_matches,
            replace_all=replace_all,
            max_result_bytes=result_limit,
            max_memory_headroom_bytes=memory_headroom,
        )
        result = _run_prepared_regex_request(
            request,
            timeout=timeout,
            startup_timeout=startup_timeout,
            result_limit=result_limit,
            worker_context=worker_context,
        )
    except BaseException as exc:
        _cleanup_haystack_directory(directory, primary=exc)
        raise

    _cleanup_haystack_directory(directory)
    return result


def bounded_regex_spans(
    haystack: str,
    pattern: str,
    *,
    start: int = 0,
    flags: object = "",
    timeout_seconds: float,
    max_matches: int,
    max_result_bytes: int = DEFAULT_REGEX_WORKER_RESULT_MAX_BYTES,
    worker_context: multiprocessing.context.BaseContext | None = None,
) -> tuple[tuple[int, int], ...]:
    """Return bounded non-empty spans from one contained regex scan."""

    value = run_regex_worker(
        action="re.spans",
        haystack=haystack,
        pattern=pattern,
        timeout_seconds=timeout_seconds,
        start=start,
        flags=flags,
        max_matches=max_matches,
        max_result_bytes=max_result_bytes,
        worker_context=worker_context,
    )
    if not isinstance(value, list):
        raise RegexWorkerProtocolError("regex span worker returned a malformed result")
    spans: list[tuple[int, int]] = []
    for row in value:
        if not isinstance(row, (list, tuple)) or len(row) != 2:
            raise RegexWorkerProtocolError("regex span worker returned a malformed span")
        start_i, end_i = row
        if isinstance(start_i, bool) or isinstance(end_i, bool):
            raise RegexWorkerProtocolError(
                "regex span worker returned boolean coordinates"
            )
        spans.append((int(start_i), int(end_i)))
    return tuple(spans)


def bounded_regex_replacement_rows(
    haystack: str,
    pattern: str,
    replacement: str,
    *,
    start: int = 0,
    replace_all: bool = True,
    flags: object = "",
    timeout_seconds: float,
    max_matches: int,
    max_result_bytes: int = DEFAULT_REGEX_WORKER_RESULT_MAX_BYTES,
    worker_context: multiprocessing.context.BaseContext | None = None,
) -> tuple[tuple[int, int, str], ...]:
    """Return concrete replacement rows from one bounded regex scan."""

    value = run_regex_worker(
        action="re.replace-rows",
        haystack=haystack,
        pattern=pattern,
        replacement=replacement,
        timeout_seconds=timeout_seconds,
        start=start,
        flags=flags,
        max_matches=max_matches,
        replace_all=replace_all,
        max_result_bytes=max_result_bytes,
        worker_context=worker_context,
    )
    return _validated_replacement_rows(value)


def bounded_regex_replacement_rows_from_chunks(
    haystack_chunks: Iterable[str],
    pattern: str,
    replacement: str,
    *,
    expected_haystack_chars: int | None = None,
    start: int = 0,
    replace_all: bool = True,
    flags: object = "",
    timeout_seconds: float,
    max_matches: int,
    max_result_bytes: int = DEFAULT_REGEX_WORKER_RESULT_MAX_BYTES,
    worker_context: multiprocessing.context.BaseContext | None = None,
) -> tuple[tuple[int, int, str], ...]:
    """Return replacement rows while staging source chunks outside JSON.

    This is intended for immutable editor snapshots that already expose bounded
    canonical chunks.  It preserves the ordinary worker's regex, timeout,
    capture-expansion, match-limit, and result-budget semantics.
    """

    value = run_regex_worker_from_chunks(
        action="re.replace-rows",
        haystack_chunks=haystack_chunks,
        expected_haystack_chars=expected_haystack_chars,
        pattern=pattern,
        replacement=replacement,
        timeout_seconds=timeout_seconds,
        start=start,
        flags=flags,
        max_matches=max_matches,
        replace_all=replace_all,
        max_result_bytes=max_result_bytes,
        worker_context=worker_context,
    )
    return _validated_replacement_rows(value)


def _validated_replacement_rows(
    value: object,
) -> tuple[tuple[int, int, str], ...]:
    """Validate the shared plain-data replacement-row response."""

    if not isinstance(value, list):
        raise RegexWorkerProtocolError(
            "regex replacement worker returned a malformed result"
        )
    rows: list[tuple[int, int, str]] = []
    for row in value:
        if not isinstance(row, (list, tuple)) or len(row) != 3:
            raise RegexWorkerProtocolError(
                "regex replacement worker returned a malformed row"
            )
        start_i, end_i, expanded = row
        if isinstance(start_i, bool) or isinstance(end_i, bool):
            raise RegexWorkerProtocolError(
                "regex replacement worker returned boolean coordinates"
            )
        if not isinstance(expanded, str):
            raise RegexWorkerProtocolError(
                "regex replacement worker returned a non-string replacement"
            )
        rows.append((int(start_i), int(end_i), expanded))
    return tuple(rows)
