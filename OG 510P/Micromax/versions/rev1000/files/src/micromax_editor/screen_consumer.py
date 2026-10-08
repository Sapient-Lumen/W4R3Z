from __future__ import annotations

"""Strict, bounded consumer for ``micromax.screen.v1`` JSON snapshots."""

import argparse
import json
import sys
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any, BinaryIO

from .screen_budget import (
    SCREEN_CONTRACT_MAX_CUES,
    SCREEN_CONTRACT_MAX_INTEGER,
    SCREEN_CONTRACT_MAX_JSON_DEPTH,
    SCREEN_CONTRACT_MAX_JSON_BYTES,
    SCREEN_CONTRACT_MAX_TAGS_PER_ROW,
    SCREEN_CONTRACT_MAX_TOKEN_CHARS,
    ScreenBudgetError,
    checked_screen_dimensions,
)
from .screen_contract import SCREEN_CONTRACT_SCHEMA


class ScreenContractError(ValueError):
    """Raised when a snapshot is not a strict supported screen contract."""


class UnsupportedScreenContract(ScreenContractError):
    """Raised when the schema discriminator names an unsupported contract."""


def _fail(path: str, message: str) -> ScreenContractError:
    return ScreenContractError(f"{path}: {message}")


def _object(
    value: object,
    path: str,
    *,
    required: set[str],
    optional: set[str] | None = None,
) -> dict[str, Any]:
    # Parsed JSON produces exact dict/list containers. Requiring those concrete
    # shapes keeps direct validator calls finite too: arbitrary Mapping or
    # Sequence implementations cannot hide expensive iteration behind a check.
    if type(value) is not dict:
        raise _fail(path, "expected object")
    allowed = set(required) | set(optional or set())
    missing = sorted(key for key in required if key not in value)
    if missing:
        raise _fail(path, f"missing field(s): {', '.join(missing)}")
    for key in value:
        if type(key) is not str:
            raise _fail(path, "object member name must be a string")
        if key not in allowed:
            raise _fail(path, f"unknown field {key!r}")
    return value


def _array(value: object, path: str) -> list[Any]:
    if type(value) is not list:
        raise _fail(path, "expected array")
    return value


def _integer(
    value: object,
    path: str,
    *,
    minimum: int = 0,
    maximum: int | None = None,
) -> int:
    if type(value) is not int:
        raise _fail(path, "expected integer")
    out = value
    if out < int(minimum):
        raise _fail(path, f"must be >= {int(minimum)}")
    if maximum is not None and out > int(maximum):
        raise _fail(path, f"must be <= {int(maximum)}")
    return out


def _boolean(value: object, path: str) -> bool:
    if type(value) is not bool:
        raise _fail(path, "expected boolean")
    return value


def _text(
    value: object,
    path: str,
    *,
    minimum: int = 0,
    maximum: int | None = None,
) -> str:
    if type(value) is not str:
        raise _fail(path, "expected string")
    if len(value) < int(minimum):
        raise _fail(path, f"must contain at least {int(minimum)} character(s)")
    if maximum is not None and len(value) > int(maximum):
        raise _fail(path, f"exceeds {int(maximum)} character budget")
    return value


def _token(value: object, path: str) -> str:
    text = _text(
        value,
        path,
        minimum=1,
        maximum=SCREEN_CONTRACT_MAX_TOKEN_CHARS,
    )
    previous_dash = False
    for ch in text:
        if ch.isascii() and ch.isalnum():
            previous_dash = False
            continue
        if ch == "-" and not previous_dash:
            previous_dash = True
            continue
        raise _fail(path, "must be an alphanumeric hyphen token")
    if text.startswith("-") or text.endswith("-"):
        raise _fail(path, "must not start or end with a hyphen")
    return text


def validate_screen_contract_v1(value: object) -> dict[str, Any]:
    """Validate structural, relational, ordering, and finite-size invariants."""

    root = _object(
        value,
        "$",
        required={"schema", "size", "cursor", "rows", "cues"},
    )
    schema = _text(root["schema"], "$.schema", minimum=1, maximum=96)
    if schema != SCREEN_CONTRACT_SCHEMA:
        raise UnsupportedScreenContract(
            f"$.schema: unsupported screen contract {schema!r}; "
            f"supported: {SCREEN_CONTRACT_SCHEMA}"
        )

    size = _object(root["size"], "$.size", required={"lines", "cols"})
    lines = _integer(size["lines"], "$.size.lines", minimum=1)
    cols = _integer(size["cols"], "$.size.cols", minimum=1)
    try:
        checked_screen_dimensions(lines, cols, label="screen contract")
    except ScreenBudgetError as exc:
        raise ScreenContractError(str(exc)) from exc

    cursor = _object(
        root["cursor"],
        "$.cursor",
        required={"visible", "mode"},
        optional={"y", "x"},
    )
    visible = _boolean(cursor["visible"], "$.cursor.visible")
    _token(cursor["mode"], "$.cursor.mode")
    if visible:
        if "y" not in cursor or "x" not in cursor:
            raise _fail("$.cursor", "visible cursor requires y and x")
        _integer(cursor["y"], "$.cursor.y", minimum=0, maximum=lines - 1)
        _integer(cursor["x"], "$.cursor.x", minimum=0, maximum=cols - 1)
    elif "y" in cursor or "x" in cursor:
        raise _fail("$.cursor", "hidden cursor must omit y and x")

    rows = _array(root["rows"], "$.rows")
    if len(rows) != lines:
        raise _fail("$.rows", f"row count {len(rows)} must equal size.lines {lines}")
    for index, raw_row in enumerate(rows):
        path = f"$.rows[{index}]"
        row = _object(
            raw_row,
            path,
            required={"y", "kind", "text"},
            optional={"source", "tags"},
        )
        y = _integer(row["y"], f"{path}.y", minimum=0, maximum=lines - 1)
        if y != index:
            raise _fail(f"{path}.y", f"expected contiguous screen row {index}, got {y}")
        _token(row["kind"], f"{path}.kind")
        _text(row["text"], f"{path}.text", maximum=cols)

        if "source" in row:
            source = _object(
                row["source"],
                f"{path}.source",
                required={"line", "column", "screen_x"},
                optional={"continuation"},
            )
            _integer(
                source["line"],
                f"{path}.source.line",
                minimum=0,
                maximum=SCREEN_CONTRACT_MAX_INTEGER,
            )
            _integer(
                source["column"],
                f"{path}.source.column",
                minimum=0,
                maximum=SCREEN_CONTRACT_MAX_INTEGER,
            )
            _integer(source["screen_x"], f"{path}.source.screen_x", minimum=0, maximum=cols)
            if "continuation" in source:
                _boolean(source["continuation"], f"{path}.source.continuation")

        if "tags" in row:
            tags = _array(row["tags"], f"{path}.tags")
            if not tags:
                raise _fail(f"{path}.tags", "must not be empty when present")
            if len(tags) > SCREEN_CONTRACT_MAX_TAGS_PER_ROW:
                raise _fail(
                    f"{path}.tags",
                    f"count {len(tags)} exceeds budget {SCREEN_CONTRACT_MAX_TAGS_PER_ROW}",
                )
            seen: set[str] = set()
            for tag_index, raw_tag in enumerate(tags):
                tag = _token(raw_tag, f"{path}.tags[{tag_index}]")
                if tag in seen:
                    raise _fail(f"{path}.tags[{tag_index}]", f"duplicate tag {tag!r}")
                seen.add(tag)

    cues = _array(root["cues"], "$.cues")
    if len(cues) > SCREEN_CONTRACT_MAX_CUES:
        raise _fail(
            "$.cues",
            f"count {len(cues)} exceeds budget {SCREEN_CONTRACT_MAX_CUES}",
        )
    previous: tuple[int, int, int, str] | None = None
    for index, raw_cue in enumerate(cues):
        path = f"$.cues[{index}]"
        cue = _object(raw_cue, path, required={"y", "x", "end", "kind"})
        y = _integer(cue["y"], f"{path}.y", minimum=0, maximum=lines - 1)
        x = _integer(cue["x"], f"{path}.x", minimum=0, maximum=cols - 1)
        end = _integer(cue["end"], f"{path}.end", minimum=1, maximum=cols)
        if end <= x:
            raise _fail(f"{path}.end", f"must be greater than x ({x})")
        kind = _token(cue["kind"], f"{path}.kind")
        key = (y, x, end, kind)
        if previous is not None and key <= previous:
            relation = "duplicate" if key == previous else "out of order"
            raise _fail(path, f"cue is {relation}; cues must be strictly sorted")
        previous = key

    return root


def _check_json_nesting(data: bytes) -> None:
    """Reject excessive container depth before invoking the recursive decoder."""

    depth = 0
    in_string = False
    escaped = False
    for offset, byte in enumerate(data):
        if in_string:
            if escaped:
                escaped = False
            elif byte == 0x5C:  # backslash
                escaped = True
            elif byte == 0x22:  # quote
                in_string = False
            continue
        if byte == 0x22:
            in_string = True
        elif byte in (0x5B, 0x7B):  # [ {
            depth += 1
            if depth > SCREEN_CONTRACT_MAX_JSON_DEPTH:
                raise ScreenContractError(
                    f"$: JSON nesting exceeds depth budget "
                    f"{SCREEN_CONTRACT_MAX_JSON_DEPTH} at byte {offset}"
                )
        elif byte in (0x5D, 0x7D):  # ] }
            depth -= 1
            if depth < 0:
                raise ScreenContractError(
                    f"$: invalid JSON: unmatched closing container at byte {offset}"
                )


def _reject_constant(raw: str) -> object:
    raise ScreenContractError(f"$: non-standard JSON number {raw!r} is not allowed")


def _reject_float(raw: str) -> object:
    raise ScreenContractError(
        f"$: non-integer JSON number {raw!r} is not allowed by {SCREEN_CONTRACT_SCHEMA}"
    )


def _parse_integer(raw: str) -> int:
    try:
        value = int(raw)
    except ValueError as exc:
        raise ScreenContractError(f"$: invalid JSON integer {raw!r}") from exc
    if abs(value) > SCREEN_CONTRACT_MAX_INTEGER:
        raise ScreenContractError(
            f"$: JSON integer exceeds interoperable magnitude "
            f"{SCREEN_CONTRACT_MAX_INTEGER}"
        )
    return value


def _reject_unpaired_surrogates(value: object) -> None:
    """Require Unicode scalar strings, including object member names."""

    pending = [value]
    while pending:
        item = pending.pop()
        if isinstance(item, str):
            for char in item:
                codepoint = ord(char)
                if 0xD800 <= codepoint <= 0xDFFF:
                    raise ScreenContractError(
                        f"$: JSON string contains unpaired UTF-16 surrogate "
                        f"U+{codepoint:04X}"
                    )
        elif type(item) is dict:
            pending.extend(item.keys())
            pending.extend(item.values())
        elif type(item) is list:
            pending.extend(item)


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in pairs:
        if key in out:
            raise ScreenContractError(f"$: duplicate JSON object name {key!r}")
        out[key] = value
    return out


def parse_screen_contract_v1(data: bytes) -> dict[str, Any]:
    """Decode one bounded UTF-8 JSON document and validate contract v1."""

    if len(data) > SCREEN_CONTRACT_MAX_JSON_BYTES:
        raise ScreenContractError(
            f"$: JSON input {len(data)} bytes exceeds budget "
            f"{SCREEN_CONTRACT_MAX_JSON_BYTES}"
        )
    _check_json_nesting(data)
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ScreenContractError(f"$: input is not valid UTF-8: {exc}") from exc
    try:
        value = json.loads(
            text,
            object_pairs_hook=_unique_object,
            parse_constant=_reject_constant,
            parse_float=_reject_float,
            parse_int=_parse_integer,
        )
    except ScreenContractError:
        raise
    except json.JSONDecodeError as exc:
        raise ScreenContractError(
            f"$: invalid JSON at line {exc.lineno} column {exc.colno}: {exc.msg}"
        ) from exc
    except RecursionError as exc:
        raise ScreenContractError("$: JSON nesting exceeded decoder safety limit") from exc
    except ValueError as exc:
        raise ScreenContractError(f"$: invalid JSON numeric value: {exc}") from exc
    _reject_unpaired_surrogates(value)
    return validate_screen_contract_v1(value)


def read_screen_contract_v1(stream: BinaryIO) -> dict[str, Any]:
    """Read through short reads, stopping at the budget plus one witness byte."""

    limit = SCREEN_CONTRACT_MAX_JSON_BYTES + 1
    chunks: list[bytes] = []
    total = 0
    while total < limit:
        chunk = stream.read(min(64 * 1024, limit - total))
        if chunk is None:
            raise ScreenContractError("$: JSON input stream returned no read result")
        if not isinstance(chunk, bytes):
            raise ScreenContractError("$: JSON input stream must produce bytes")
        if not chunk:
            break
        chunks.append(chunk)
        total += len(chunk)
    if total > SCREEN_CONTRACT_MAX_JSON_BYTES:
        raise ScreenContractError(
            f"$: JSON input exceeds budget {SCREEN_CONTRACT_MAX_JSON_BYTES} bytes"
        )
    return parse_screen_contract_v1(b"".join(chunks))


_TERMINAL_CONTROL_CATEGORIES = frozenset({"Cc", "Cf", "Zl", "Zp"})
_NAMED_CONTROL_ESCAPES = {
    "\b": r"\b",
    "\t": r"\t",
    "\n": r"\n",
    "\f": r"\f",
    "\r": r"\r",
}


def _escape_terminal_text(text: str, *, escape_backslash: bool = True) -> str:
    """Escape controls and format characters before writing text to a terminal."""

    out: list[str] = []
    for char in text:
        if char == "\\" and escape_backslash:
            out.append(r"\\")
            continue
        named = _NAMED_CONTROL_ESCAPES.get(char)
        if named is not None:
            out.append(named)
            continue
        if unicodedata.category(char) not in _TERMINAL_CONTROL_CATEGORIES:
            out.append(char)
            continue
        codepoint = ord(char)
        if codepoint <= 0xFF:
            out.append(f"\\x{codepoint:02x}")
        elif codepoint <= 0xFFFF:
            out.append(f"\\u{codepoint:04x}")
        else:
            out.append(f"\\U{codepoint:08x}")
    return "".join(out)


def screen_contract_text(contract: object) -> str:
    """Return one terminal-safe escaped line for each validated screen row."""

    checked = validate_screen_contract_v1(contract)
    return "\n".join(_escape_terminal_text(str(row["text"])) for row in checked["rows"])


def screen_contract_summary(contract: object) -> dict[str, Any]:
    checked = validate_screen_contract_v1(contract)
    row_kinds = Counter(str(row["kind"]) for row in checked["rows"])
    cue_kinds = Counter(str(cue["kind"]) for cue in checked["cues"])
    return {
        "schema": checked["schema"],
        "size": dict(checked["size"]),
        "cursor": dict(checked["cursor"]),
        "rows": len(checked["rows"]),
        "source_rows": sum(1 for row in checked["rows"] if "source" in row),
        "row_kinds": dict(sorted(row_kinds.items())),
        "cues": len(checked["cues"]),
        "cue_kinds": dict(sorted(cue_kinds.items())),
    }


def _open_input(path: str) -> tuple[BinaryIO, bool]:
    if path == "-":
        return sys.stdin.buffer, False
    return Path(path).open("rb"), True


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="micromax-screen",
        description="strict bounded consumer for micromax.screen.v1 JSON",
    )
    ap.add_argument("path", nargs="?", default="-", help="JSON file (default: stdin)")
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="validate silently")
    mode.add_argument(
        "--text",
        action="store_true",
        help="print terminal-safe escaped visible row text",
    )
    mode.add_argument(
        "--summary",
        action="store_true",
        help="print deterministic summary JSON (default)",
    )
    args = ap.parse_args(argv)

    stream: BinaryIO | None = None
    close_stream = False
    try:
        stream, close_stream = _open_input(str(args.path))
        contract = read_screen_contract_v1(stream)
        if args.check:
            return 0
        if args.text:
            print(screen_contract_text(contract))
            return 0
        print(json.dumps(screen_contract_summary(contract), indent=2, sort_keys=True))
        return 0
    except (OSError, ScreenContractError) as exc:
        message = _escape_terminal_text(str(exc), escape_backslash=False)
        print(f"micromax-screen: {message}", file=sys.stderr)
        return 2
    finally:
        if close_stream and stream is not None:
            stream.close()


if __name__ == "__main__":
    raise SystemExit(main())
