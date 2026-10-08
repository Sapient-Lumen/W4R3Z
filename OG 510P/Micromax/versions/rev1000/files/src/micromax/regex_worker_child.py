"""Stdlib-only one-shot worker for bounded regex matching.

This module is deliberately executable as an absolute script under
``python -I -S``.  It must not import Micromax, site packages, or editor code:
the parent may be multithreaded, and heavy site initialization must not consume
the foreground match deadline.  Handshake mode emits one bounded ready line
before the parent starts that deadline.  The parent owns the request and
communicates over one JSON stdin/stdout exchange; no shell is involved.
"""

from __future__ import annotations

import json
import os
import re
import stat
import sys
from typing import Any, TypeVar

PROTOCOL = "micromax.regex-worker.v1"
HAYSTACK_FILE_PROTOCOL = "micromax.regex-haystack-file.v1"
HANDSHAKE_ARGUMENT = "--handshake"

_RowT = TypeVar("_RowT")
_MEMORY_LIMIT_MESSAGE = "regex worker memory headroom exceeded"


class RegexOperationFailure(RuntimeError):
    """One stable operation failure returned to the owning parent."""

    def __init__(self, kind: str, message: str) -> None:
        super().__init__(str(message))
        self.kind = str(kind)


def _failure_response(kind: str, message: str) -> dict[str, object]:
    return {
        "protocol": PROTOCOL,
        "ok": False,
        "kind": str(kind),
        "message": str(message),
    }


# Build both forms before any request-owned address-space ceiling is installed.
# Returning the prebuilt mapping from a MemoryError handler avoids allocating a
# fresh dict before the already-prebuilt wire envelope can be selected.
_MEMORY_FAILURE_RESPONSE: dict[str, object] = _failure_response(
    "memory-limit", _MEMORY_LIMIT_MESSAGE
)
_MEMORY_FAILURE_RESPONSE_BYTES = json.dumps(
    _MEMORY_FAILURE_RESPONSE,
    ensure_ascii=False,
    separators=(",", ":"),
).encode("utf-8")


def _encode_worker_response(response: dict[str, object]) -> bytes:
    try:
        return json.dumps(
            response,
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")
    except MemoryError:
        return _MEMORY_FAILURE_RESPONSE_BYTES


def _parse_flags(flags: object) -> int:
    """Parse the portable ``0`` / ``ims`` flag dialect without package imports."""

    if isinstance(flags, bool):
        raise TypeError(
            f"flags must be 0 or a string of ims flags, got boolean {flags!r}"
        )
    if flags in (0, ""):
        return 0
    if flags is None:
        raise TypeError("flags must be 0 or a string of ims flags, got None")
    if isinstance(flags, int):
        raise ValueError(
            "regex flags must be 0 or a string of ims flags, "
            f"got integer {int(flags)}"
        )
    if not isinstance(flags, str):
        raise TypeError("flags must be 0 or a string of ims flags")

    parsed = 0
    for char in flags:
        if char == "i":
            parsed |= re.IGNORECASE
        elif char == "m":
            parsed |= re.MULTILINE
        elif char == "s":
            parsed |= re.DOTALL
        elif char in (" ", "\t", "\n"):
            continue
        else:
            raise ValueError(f"unknown regex flag: {char!r}")
    return parsed


def _capture_value(value: str | None) -> str | int:
    return 0 if value is None else str(value)


def _match_to_map(match: re.Match[str]) -> dict[str, Any]:
    out: dict[str, Any] = {
        "start": int(match.start()),
        "end": int(match.end()),
        "group": str(match.group(0)),
        "groups": [_capture_value(value) for value in match.groups()],
    }
    groupdict = match.groupdict()
    if groupdict:
        out["groupdict"] = {
            str(name): _capture_value(value) for name, value in groupdict.items()
        }
    return out


def _nonnegative_limit(value: object) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool):
        raise RegexOperationFailure("protocol", "invalid regex worker limit")
    try:
        parsed = int(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise RegexOperationFailure("protocol", "invalid regex worker limit") from exc
    return max(0, parsed)


def _positive_limit(value: object) -> int | None:
    parsed = _nonnegative_limit(value)
    return None if parsed is None or parsed <= 0 else parsed


def _exact_nonnegative_integer(value: object, *, label: str) -> int:
    """Return one strict JSON integer coordinate, rejecting coercion and signs."""

    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise RegexOperationFailure(
            "protocol", f"invalid regex worker haystack {label}"
        )
    return int(value)


def _materialize_file_haystack(request: object) -> object:
    """Resolve one validated private-file descriptor to the worker's source str.

    The parent uses this transport only for large immutable editor snapshots.
    Opening the path with ``O_NOFOLLOW`` where available, reading through the
    already-open descriptor, and checking exact byte and character counts keeps
    truncation, replacement, symlink substitution, and newline translation from
    silently changing match coordinates.  The materialized request remains a
    private child object; the caller installs regex-operation memory headroom
    only after this source baseline exists.
    """

    if not isinstance(request, dict) or "haystack_file" not in request:
        return request
    if "haystack" in request:
        raise RegexOperationFailure(
            "protocol", "regex worker request has multiple haystack transports"
        )

    descriptor = request.get("haystack_file")
    if not isinstance(descriptor, dict):
        raise RegexOperationFailure(
            "protocol", "invalid regex worker haystack transport"
        )
    if descriptor.get("protocol") != HAYSTACK_FILE_PROTOCOL:
        raise RegexOperationFailure(
            "protocol", "invalid regex worker haystack transport protocol"
        )
    path = descriptor.get("path")
    if not isinstance(path, str) or not path or "\x00" in path:
        raise RegexOperationFailure(
            "protocol", "invalid regex worker haystack path"
        )
    expected_bytes = _exact_nonnegative_integer(
        descriptor.get("bytes"), label="byte count"
    )
    expected_characters = _exact_nonnegative_integer(
        descriptor.get("characters"), label="character count"
    )

    flags = int(os.O_RDONLY)
    flags |= int(getattr(os, "O_BINARY", 0))
    flags |= int(getattr(os, "O_CLOEXEC", 0))
    flags |= int(getattr(os, "O_NOFOLLOW", 0))
    descriptor_fd = -1
    try:
        descriptor_fd = os.open(path, flags)
        before = os.fstat(descriptor_fd)
        if not stat.S_ISREG(before.st_mode):
            raise RegexOperationFailure(
                "protocol", "regex worker haystack transport is not a regular file"
            )
        if int(before.st_size) != expected_bytes:
            raise RegexOperationFailure(
                "protocol", "regex worker haystack transport size changed"
            )
        with os.fdopen(
            descriptor_fd,
            "r",
            encoding="utf-8",
            errors="surrogatepass",
            newline="",
        ) as stream:
            descriptor_fd = -1
            haystack = stream.read()
            after = os.fstat(stream.fileno())
        if (
            int(after.st_dev) != int(before.st_dev)
            or int(after.st_ino) != int(before.st_ino)
            or int(after.st_size) != expected_bytes
        ):
            raise RegexOperationFailure(
                "protocol", "regex worker haystack transport changed while reading"
            )
    except RegexOperationFailure:
        raise
    except (OSError, UnicodeError, ValueError) as exc:
        raise RegexOperationFailure(
            "protocol", "regex worker haystack transport could not be read"
        ) from exc
    finally:
        if descriptor_fd >= 0:
            try:
                os.close(descriptor_fd)
            except OSError:
                pass

    if len(haystack) != expected_characters:
        raise RegexOperationFailure(
            "protocol", "regex worker haystack character count changed"
        )

    materialized = dict(request)
    materialized.pop("haystack_file", None)
    materialized["haystack"] = haystack
    return materialized


def _utf8_size_range(
    text: str,
    start: int,
    end: int,
    *,
    stop_after: int | None = None,
    ascii_only: bool | None = None,
) -> int:
    """Count replacement-encoded UTF-8 bytes without allocating a byte copy."""

    start_i = max(0, int(start))
    end_i = max(start_i, int(end))
    if ascii_only is True or (ascii_only is None and text.isascii()):
        return end_i - start_i

    total = 0
    for index in range(start_i, end_i):
        codepoint = ord(text[index])
        if codepoint <= 0x7F or 0xD800 <= codepoint <= 0xDFFF:
            total += 1
        elif codepoint <= 0x7FF:
            total += 2
        elif codepoint <= 0xFFFF:
            total += 3
        else:
            total += 4
        if stop_after is not None and total > stop_after:
            return total
    return total


def _install_linux_address_space_headroom(request: object) -> None:
    """Seal one Linux worker to its current VMS plus requested headroom.

    The request has already been decoded, so its haystack and pattern are part
    of the baseline.  The limit constrains native regex state, replacement
    expansion, and protocol materialization that happen after this point.  It
    is intentionally installed inside the fresh child rather than through
    ``subprocess.Popen(preexec_fn=...)``, which is unsafe in threaded parents.

    Other platforms retain the existing killable wall-clock boundary.  Linux
    fails closed when the requested ceiling cannot be installed rather than
    silently running an operation the parent believed was memory-bounded.
    """

    if not isinstance(request, dict):
        return
    headroom = _positive_limit(request.get("max_memory_headroom_bytes"))
    if headroom is None or not sys.platform.startswith("linux"):
        return

    try:
        import resource

        with open("/proc/self/statm", "rb") as statm_file:
            statm = statm_file.read(128).split()
        if not statm:
            raise ValueError("missing /proc/self/statm size")
        page_size = int(os.sysconf("SC_PAGE_SIZE"))
        current_virtual_bytes = int(statm[0]) * page_size
        if current_virtual_bytes <= 0 or page_size <= 0:
            raise ValueError("invalid process address-space measurement")

        requested_cap = current_virtual_bytes + int(headroom)
        soft, hard = resource.getrlimit(resource.RLIMIT_AS)
        cap = requested_cap
        if soft != resource.RLIM_INFINITY:
            cap = min(cap, int(soft))
        if hard != resource.RLIM_INFINITY:
            cap = min(cap, int(hard))
        if cap <= 0:
            raise ValueError("invalid inherited address-space ceiling")

        # Lower both limits.  The one-shot worker has no reason to raise its
        # own soft limit after the boundary is installed.
        resource.setrlimit(resource.RLIMIT_AS, (cap, cap))
    except RegexOperationFailure:
        raise
    except BaseException as exc:
        raise RegexOperationFailure(
            "memory-limit",
            "regex worker memory ceiling unavailable",
        ) from exc


def _encoded_response_size(value: object) -> int:
    """Return the exact UTF-8 protocol size for one successful value."""

    return len(
        json.dumps(
            {"protocol": PROTOCOL, "ok": True, "value": value},
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")
    )


def _append_bounded_list_row(
    rows: list[_RowT],
    row: _RowT,
    *,
    encoded_size: int,
    max_result_bytes: int | None,
) -> int:
    """Append one JSON row only when the final list envelope can still fit.

    ``encoded_size`` is the exact successful-response size for the current list.
    Replacing the closing ``]}`` with a comma (when needed), the encoded row,
    and the same closing bytes adds exactly the row size plus one separator.
    This prevents large match lists from being fully materialized only to fail
    the final protocol budget check.
    """

    row_size = len(
        json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    )
    projected = int(encoded_size) + int(row_size) + (1 if rows else 0)
    if max_result_bytes is not None and projected > max_result_bytes:
        raise RegexOperationFailure(
            "result-limit",
            "regex result budget exceeded: "
            f"more than {max_result_bytes} bytes",
        )
    rows.append(row)
    return projected


def _replacement_rows(
    compiled: re.Pattern[str],
    haystack: str,
    replacement: str,
    *,
    start: int,
    replace_all: bool,
    max_matches: int | None,
    max_result_bytes: int | None,
) -> list[list[object]]:
    try:
        # Pattern.sub validates group references even when the probe has no match.
        compiled.sub(replacement, "", count=0)
    except (re.error, IndexError) as exc:
        raise RegexOperationFailure(
            "invalid-replacement", f"invalid replacement: {exc}"
        ) from exc

    rows: list[list[object]] = []
    result_bytes = _encoded_response_size(rows)
    for match in compiled.finditer(haystack, pos=max(0, int(start))):
        match_start = int(match.start())
        match_end = int(match.end())
        if match_end <= match_start:
            raise RegexOperationFailure(
                "zero-width", "zero-width matches are not supported"
            )
        if max_matches is not None and len(rows) >= max_matches:
            raise RegexOperationFailure(
                "match-limit",
                f"regex match limit exceeded: more than {max_matches} matches",
            )
        try:
            expanded = str(match.expand(replacement))
        except (re.error, IndexError) as exc:
            raise RegexOperationFailure(
                "invalid-replacement", f"invalid replacement: {exc}"
            ) from exc

        row: list[object] = [match_start, match_end, expanded]
        result_bytes = _append_bounded_list_row(
            rows,
            row,
            encoded_size=result_bytes,
            max_result_bytes=max_result_bytes,
        )
        if not replace_all:
            break
    return rows


def _apply_replacement_rows(
    haystack: str,
    rows: list[list[object]],
    *,
    max_result_bytes: int | None,
) -> str:
    # Prove the output budget before creating source slices or the joined result.
    # The old defensive check allocated one UTF-8 bytes object for every prefix
    # and replacement, so a denied operation could spend the very memory the
    # limit was meant to protect.
    source_position = 0
    output_bytes = 0
    haystack_is_ascii = haystack.isascii()
    for row in rows:
        start = int(row[0])
        end = int(row[1])
        replacement = str(row[2])
        remaining = None
        if max_result_bytes is not None:
            remaining = max_result_bytes - output_bytes
        output_bytes += _utf8_size_range(
            haystack,
            source_position,
            start,
            stop_after=remaining,
            ascii_only=haystack_is_ascii,
        )
        if max_result_bytes is not None and output_bytes > max_result_bytes:
            raise RegexOperationFailure(
                "result-limit",
                "regex result budget exceeded: "
                f"more than {max_result_bytes} bytes",
            )
        remaining = None
        if max_result_bytes is not None:
            remaining = max_result_bytes - output_bytes
        output_bytes += _utf8_size_range(
            replacement,
            0,
            len(replacement),
            stop_after=remaining,
            ascii_only=replacement.isascii(),
        )
        if max_result_bytes is not None and output_bytes > max_result_bytes:
            raise RegexOperationFailure(
                "result-limit",
                "regex result budget exceeded: "
                f"more than {max_result_bytes} bytes",
            )
        source_position = end

    remaining = None
    if max_result_bytes is not None:
        remaining = max_result_bytes - output_bytes
    output_bytes += _utf8_size_range(
        haystack,
        source_position,
        len(haystack),
        stop_after=remaining,
        ascii_only=haystack_is_ascii,
    )
    if max_result_bytes is not None and output_bytes > max_result_bytes:
        raise RegexOperationFailure(
            "result-limit",
            f"regex result budget exceeded: more than {max_result_bytes} bytes",
        )

    pieces: list[str] = []
    source_position = 0
    for row in rows:
        start = int(row[0])
        end = int(row[1])
        pieces.extend((haystack[source_position:start], str(row[2])))
        source_position = end
    pieces.append(haystack[source_position:])
    return "".join(pieces)


def execute_request(request: object) -> dict[str, object]:
    """Execute one plain-data request and return one plain-data response."""

    try:
        if not isinstance(request, dict) or request.get("protocol") != PROTOCOL:
            raise RegexOperationFailure("protocol", "invalid regex worker protocol")

        action = str(request.get("action") or "")
        haystack = request.get("haystack")
        pattern = request.get("pattern")
        replacement = request.get("replacement")
        if not isinstance(haystack, str) or not isinstance(pattern, str):
            raise RegexOperationFailure(
                "protocol", "regex worker haystack and pattern must be strings"
            )
        if replacement is not None and not isinstance(replacement, str):
            raise RegexOperationFailure(
                "protocol", "regex worker replacement must be a string"
            )

        try:
            start = int(request.get("start", 0))
        except (TypeError, ValueError, OverflowError) as exc:
            raise RegexOperationFailure(
                "protocol", "invalid regex worker start position"
            ) from exc
        if start < 0:
            raise RegexOperationFailure(
                "protocol", "regex worker start position must be non-negative"
            )

        max_matches = _nonnegative_limit(request.get("max_matches"))
        max_result_bytes = _positive_limit(request.get("max_result_bytes"))
        replace_all = bool(request.get("replace_all", True))

        try:
            compiled = re.compile(pattern, flags=_parse_flags(request.get("flags", "")))
        except re.error as exc:
            raise RegexOperationFailure(
                "invalid-regex", f"invalid regex: {exc}"
            ) from exc
        except RecursionError as exc:
            # CPython's regex parser is recursive.  A pattern can remain well
            # below the public byte ceiling yet exceed that parser depth during
            # compilation.  Keep the failure inside the owned child and expose
            # it as an ordinary invalid-pattern result rather than a generic
            # worker crash or an exception escaping the editor foreground.
            raise RegexOperationFailure(
                "invalid-regex",
                "invalid regex: pattern nesting exceeds engine limit",
            ) from exc
        except (TypeError, ValueError) as exc:
            raise RegexOperationFailure(
                "invalid-flags", f"invalid regex flags: {exc}"
            ) from exc

        if action == "re.search":
            match = compiled.search(haystack, pos=start)
            value: object = 0 if match is None else _match_to_map(match)
        elif action == "re.findall":
            matches: list[dict[str, Any]] = []
            result_bytes = _encoded_response_size(matches)
            for match in compiled.finditer(haystack, pos=start):
                if max_matches is not None and len(matches) >= max_matches:
                    raise RegexOperationFailure(
                        "match-limit",
                        f"regex match limit exceeded: more than {max_matches} matches",
                    )
                result_bytes = _append_bounded_list_row(
                    matches,
                    _match_to_map(match),
                    encoded_size=result_bytes,
                    max_result_bytes=max_result_bytes,
                )
            value = matches
        elif action == "re.spans":
            spans: list[list[int]] = []
            result_bytes = _encoded_response_size(spans)
            for match in compiled.finditer(haystack, pos=start):
                match_start = int(match.start())
                match_end = int(match.end())
                if match_end <= match_start:
                    continue
                if max_matches is not None and len(spans) >= max_matches:
                    raise RegexOperationFailure(
                        "match-limit",
                        f"search match limit exceeded: more than {max_matches} matches",
                    )
                result_bytes = _append_bounded_list_row(
                    spans,
                    [match_start, match_end],
                    encoded_size=result_bytes,
                    max_result_bytes=max_result_bytes,
                )
            value = spans
        elif action == "re.replace-rows":
            if replacement is None:
                raise RegexOperationFailure(
                    "invalid-replacement", "missing replacement"
                )
            value = _replacement_rows(
                compiled,
                haystack,
                replacement,
                start=start,
                replace_all=replace_all,
                max_matches=max_matches,
                max_result_bytes=max_result_bytes,
            )
        elif action in {"re.sub", "re.subn"}:
            if replacement is None:
                raise RegexOperationFailure(
                    "invalid-replacement", "missing replacement"
                )
            rows = _replacement_rows(
                compiled,
                haystack,
                replacement,
                start=0,
                replace_all=True,
                max_matches=max_matches,
                max_result_bytes=max_result_bytes,
            )
            output = _apply_replacement_rows(
                haystack, rows, max_result_bytes=max_result_bytes
            )
            value = output if action == "re.sub" else [output, len(rows)]
        else:
            raise RegexOperationFailure(
                "protocol", f"unknown regex worker action: {action}"
            )

        response: dict[str, object] = {
            "protocol": PROTOCOL,
            "ok": True,
            "value": value,
        }
        if max_result_bytes is not None:
            encoded = json.dumps(
                response,
                ensure_ascii=False,
                separators=(",", ":"),
            ).encode("utf-8")
            if len(encoded) > max_result_bytes:
                raise RegexOperationFailure(
                    "result-limit",
                    "regex result budget exceeded: "
                    f"{len(encoded)} bytes > {max_result_bytes}",
                )
        return response
    except RegexOperationFailure as exc:
        return _failure_response(exc.kind, str(exc))
    except MemoryError:
        return _MEMORY_FAILURE_RESPONSE
    except BaseException as exc:  # keep the owned child failure inspectable
        return _failure_response("worker", f"{type(exc).__name__}: {exc}")


def execute_worker_request(request: object) -> dict[str, object]:
    """Resolve transport, install child-only limits, then execute one request.

    Keeping this wrapper separate preserves :func:`execute_request` as a pure
    in-process test seam; direct tests must never lower the pytest process's
    address-space limit.  File-backed sources are decoded first so the existing
    headroom contract still measures regex state, replacement expansion, and
    response materialization above the worker's fully-owned input baseline.
    """

    try:
        materialized = _materialize_file_haystack(request)
        _install_linux_address_space_headroom(materialized)
    except RegexOperationFailure as exc:
        return _failure_response(exc.kind, str(exc))
    except MemoryError:
        return _MEMORY_FAILURE_RESPONSE
    except BaseException as exc:
        # File transport adds owned filesystem and decoding work ahead of the
        # pure executor.  Keep an unexpected failure inspectable through the
        # same stable worker envelope instead of crashing the one-shot child
        # before it can answer its parent.
        return _failure_response("worker", f"{type(exc).__name__}: {exc}")
    return execute_request(materialized)


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == HANDSHAKE_ARGUMENT:
        ready = json.dumps(
            {"protocol": PROTOCOL, "ready": True},
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")
        sys.stdout.buffer.write(ready + b"\n")
        sys.stdout.buffer.flush()

    try:
        request = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    except BaseException as exc:
        response: dict[str, object] = {
            "protocol": PROTOCOL,
            "ok": False,
            "kind": "protocol",
            "message": f"invalid regex worker request: {exc}",
        }
    else:
        response = execute_worker_request(request)

    data = _encode_worker_response(response)
    sys.stdout.buffer.write(data)
    sys.stdout.buffer.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
