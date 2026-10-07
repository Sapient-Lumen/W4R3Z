#!/usr/bin/env python3
"""Check text surfaces for hidden Unicode/control-character hazards.

Text normalization proves that files decode as UTF-8 and use LF endings.  This
companion guard rejects characters that can hide edits, reorder displayed text,
or smuggle terminal/control behavior into otherwise readable surfaces.  Findings
record code point metadata but never echo the matched character or nearby text.

The scanner uses an ASCII fast path because most archive surfaces are ordinary
ASCII/UTF-8 text.  Files that contain only allowed ASCII controls are accepted
without a per-character unicodedata lookup; non-ASCII files are still decoded and
checked for bidi, invisible-format, C1, surrogate, and noncharacter hazards.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import unicodedata
from typing import Any

TEXT_SUFFIXES = {
    ".cff",
    ".csv",
    ".json",
    ".jsonl",
    ".md",
    ".paths",
    ".py",
    ".sha256",
    ".tex",
    ".txt",
    ".yaml",
    ".yml",
}
TEXT_NAMES = {"LICENSE", "Makefile", "NOTICE", "VERSION"}
ALLOWED_ASCII_CONTROL_BYTES = {0x09, 0x0A}
ALLOWED_ASCII_CONTROLS = {"\n", "\t"}
BIDI_CONTROL_RANGES = ((0x202A, 0x202E), (0x2066, 0x2069))
INVISIBLE_FORMAT_CONTROLS = {
    0x00AD,  # SOFT HYPHEN
    0x061C,  # ARABIC LETTER MARK
    0x180E,  # MONGOLIAN VOWEL SEPARATOR (historic format control)
    0x200B,  # ZERO WIDTH SPACE
    0x200C,  # ZERO WIDTH NON-JOINER
    0x200D,  # ZERO WIDTH JOINER
    0x200E,  # LEFT-TO-RIGHT MARK
    0x200F,  # RIGHT-TO-LEFT MARK
    0x2060,  # WORD JOINER
    0x2061,  # FUNCTION APPLICATION
    0x2062,  # INVISIBLE TIMES
    0x2063,  # INVISIBLE SEPARATOR
    0x2064,  # INVISIBLE PLUS
    0x206A,
    0x206B,
    0x206C,
    0x206D,
    0x206E,
    0x206F,
    0xFEFF,  # ZERO WIDTH NO-BREAK SPACE / BOM
}


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def is_text_surface(path: pathlib.Path) -> bool:
    return path.suffix in TEXT_SUFFIXES or path.name in TEXT_NAMES


def codepoint_name(ch: str) -> str:
    return unicodedata.name(ch, "<unnamed>")


def is_bidi_control(cp: int) -> bool:
    return any(start <= cp <= end for start, end in BIDI_CONTROL_RANGES)


def is_noncharacter(cp: int) -> bool:
    return 0xFDD0 <= cp <= 0xFDEF or ((cp & 0xFFFE) == 0xFFFE and cp <= 0x10FFFF)


def classify_forbidden(ch: str) -> str | None:
    cp = ord(ch)
    if ch in ALLOWED_ASCII_CONTROLS:
        return None
    if cp < 0x20 or cp == 0x7F:
        return "c0_or_del_control"
    if 0x80 <= cp <= 0x9F:
        return "c1_control"
    if is_bidi_control(cp):
        return "bidi_control"
    if cp in INVISIBLE_FORMAT_CONTROLS:
        return "invisible_format_control"
    if is_noncharacter(cp):
        return "unicode_noncharacter"
    # Valid UTF-8 cannot decode surrogate code points, but keep this guard for
    # defensive completeness if Python ever receives a non-standard str object.
    category = unicodedata.category(ch)
    if category in {"Cc", "Cs"}:
        return "unicode_control_or_surrogate"
    return None


def line_and_column(text: str, offset: int) -> tuple[int, int]:
    line = text.count("\n", 0, offset) + 1
    last_lf = text.rfind("\n", 0, offset)
    column = offset + 1 if last_lf == -1 else offset - last_lf
    return line, column


def has_forbidden_ascii_byte(data: bytes) -> bool:
    return any((b < 0x20 and b not in ALLOWED_ASCII_CONTROL_BYTES) or b == 0x7F for b in data)


def scan_text(text: str, ascii_only: bool) -> list[tuple[int, str, str]]:
    """Return (offset, character, category) findings without echoing context."""
    findings: list[tuple[int, str, str]] = []
    if ascii_only:
        iterator = enumerate(text)
    else:
        # Non-ASCII files still tend to be mostly ASCII.  Avoid unicodedata work
        # for ordinary printable ASCII and allowed LF/TAB characters.
        iterator = ((offset, ch) for offset, ch in enumerate(text) if ord(ch) >= 0x80 or ord(ch) < 0x20 or ord(ch) == 0x7F)
    for offset, ch in iterator:
        category = classify_forbidden(ch)
        if category is not None:
            findings.append((offset, ch, category))
    return findings


def check(root: pathlib.Path) -> dict[str, Any]:
    release = load_json(root / "RELEASE_MANIFEST.json")
    findings: list[dict[str, Any]] = []
    text_count = 0
    codepoints_scanned = 0
    ascii_fast_path_files = 0
    non_ascii_files = 0
    category_counts: dict[str, int] = {}

    paths = sorted(
        (p for p in root.rglob("*") if p.is_file() and is_text_surface(p)),
        key=lambda p: p.relative_to(root).as_posix(),
    )
    for path in paths:
        rel = path.relative_to(root).as_posix()
        text_count += 1
        data = path.read_bytes()
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError as exc:
            findings.append({"path": rel, "category": "utf8_decode_failed", "detail": str(exc)})
            category_counts["utf8_decode_failed"] = category_counts.get("utf8_decode_failed", 0) + 1
            continue
        codepoints_scanned += len(text)
        ascii_only = data.isascii()
        if ascii_only and not has_forbidden_ascii_byte(data):
            ascii_fast_path_files += 1
            continue
        if not ascii_only:
            non_ascii_files += 1
        for offset, ch, category in scan_text(text, ascii_only):
            cp = ord(ch)
            line, column = line_and_column(text, offset)
            findings.append(
                {
                    "path": rel,
                    "line": line,
                    "column": column,
                    "offset": offset,
                    "category": category,
                    "codepoint": f"U+{cp:04X}",
                    "unicode_category": unicodedata.category(ch),
                    "unicode_name": codepoint_name(ch),
                }
            )
            category_counts[category] = category_counts.get(category, 0) + 1

    summary = {
        "checks_failed": len(findings),
        "text_surface_count": text_count,
        "codepoints_scanned": codepoints_scanned,
        "ascii_fast_path_file_count": ascii_fast_path_files,
        "non_ascii_file_count": non_ascii_files,
        "finding_count": len(findings),
        "c0_or_del_control_count": category_counts.get("c0_or_del_control", 0),
        "c1_control_count": category_counts.get("c1_control", 0),
        "bidi_control_count": category_counts.get("bidi_control", 0),
        "invisible_format_control_count": category_counts.get("invisible_format_control", 0),
        "unicode_noncharacter_count": category_counts.get("unicode_noncharacter", 0),
        "category_counts": category_counts,
    }
    return {
        "status": "pass" if not findings else "fail",
        "generated_for_revision": release["revision"],
        "checked_bundle": release["bundle"],
        "publication_authorized": False,
        "unicode_control_policy": {
            "allowed_ascii_controls": ["LF", "TAB"],
            "forbidden_categories": [
                "C0 controls except LF/TAB",
                "DEL",
                "C1 controls",
                "bidirectional override/embed/isolate controls",
                "zero-width and invisible format controls",
                "Unicode noncharacters",
                "surrogate code points",
            ],
            "findings_do_not_echo_matched_text": True,
            "ascii_fast_path": True,
        },
        "text_suffixes": sorted(TEXT_SUFFIXES),
        "text_names": sorted(TEXT_NAMES),
        "findings": findings[:100],
        "summary": summary,
        "fail_closed_rule": "If hidden control, bidi, invisible-format, or noncharacter code points are found in text surfaces, default to no publication and repair the affected file before packaging.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--write-report", default="")
    args = parser.parse_args()
    root = pathlib.Path(args.root).resolve()
    report = check(root)
    text = json.dumps(report, indent=2) + "\n"
    if args.write_report:
        out = root / args.write_report
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
