#!/usr/bin/env python3
"""Shared strict parsers for release control files.

Release control files are intentionally byte-canonical rather than merely
semantic.  Verifiers should reject CRLF, trailing spaces, multi-line VERSION
values, uppercase digests, and other tolerant text-decoding variants so the ZIP
artifact and extracted-tree checks agree about exactly what was released.
"""

from __future__ import annotations

import re
from collections.abc import Mapping

import release_path_policy

MANIFEST_NAME = "MANIFEST.sha256"
VERSION_NAME = "VERSION"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
VERSION_RE = re.compile(r"^v(?P<num>0|[1-9]\d*)$")
VERSION_BYTES_RE = re.compile(rb"^v(?P<num>0|[1-9]\d*)\n$")


def format_manifest_text(entries: Mapping[str, str]) -> str:
    """Return the canonical MANIFEST.sha256 text for ``entries``."""

    return "".join(f"{sha}  {rel}\n" for rel, sha in sorted(entries.items()))


def parse_manifest_bytes(raw: bytes) -> tuple[dict[str, str], list[str]]:
    """Parse MANIFEST.sha256 bytes with strict canonical-text checks.

    The parser is deliberately byte-first.  ``str.splitlines()`` would accept
    CRLF transparently, but the release manifest is part of the canonical release
    surface and must use LF-only records.
    """

    problems: list[str] = []
    if b"\r" in raw:
        problems.append(f"{MANIFEST_NAME} must use LF line endings only; CR bytes are not allowed")
    if raw and not raw.endswith(b"\n"):
        problems.append(f"{MANIFEST_NAME} must end with a newline")

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        return {}, [f"{MANIFEST_NAME} is not valid UTF-8: {exc}"] + problems

    entries: dict[str, str] = {}
    seen_paths: set[str] = set()
    for lineno, line in enumerate(text.split("\n"), 1):
        if line == "":
            if lineno == text.count("\n") + 1 and text.endswith("\n"):
                continue
            problems.append(f"{MANIFEST_NAME} line {lineno}: blank lines are not allowed")
            continue
        if "\r" in line:
            problems.append(f"{MANIFEST_NAME} line {lineno}: CR bytes are not allowed")
        try:
            digest, rel = line.split("  ", 1)
        except ValueError:
            problems.append(f"{MANIFEST_NAME} line {lineno}: expected '<sha256>  <path>'")
            continue

        if not SHA256_RE.fullmatch(digest):
            problems.append(f"{MANIFEST_NAME} line {lineno}: digest must be lowercase 64-hex SHA-256")
        if rel == MANIFEST_NAME:
            problems.append(f"{MANIFEST_NAME} line {lineno}: manifest must not hash itself")
        path_problem = release_path_policy.release_path_problem(rel)
        if path_problem:
            problems.append(f"{MANIFEST_NAME} line {lineno}: unsafe path {rel!r}: {path_problem}")
        if rel in seen_paths:
            problems.append(f"{MANIFEST_NAME} line {lineno}: duplicate path {rel!r}")
        seen_paths.add(rel)
        entries[rel] = digest

    if list(entries) != sorted(entries):
        problems.append(f"{MANIFEST_NAME} entries must be sorted by path")

    collisions = release_path_policy.find_portable_path_collisions(entries)
    for key, vals in sorted(collisions.items()):
        problems.append(f"{MANIFEST_NAME} portable path collision for {key!r}: {', '.join(vals)}")

    shape_conflicts = release_path_policy.find_extraction_shape_conflicts(entries)
    for prefix, children in sorted(shape_conflicts.items()):
        problems.append(
            f"{MANIFEST_NAME} extraction shape conflict: file path {prefix!r} also prefixes {', '.join(children)}"
        )

    if entries:
        canonical = format_manifest_text(entries).encode("utf-8")
        if raw != canonical:
            problems.append(f"{MANIFEST_NAME} bytes are not canonical '<sha256>  <path>\\n' records sorted by path")

    return entries, problems


def parse_version_bytes(raw: bytes) -> tuple[str | None, list[str]]:
    """Parse VERSION bytes and require the canonical single-line LF form."""

    problems: list[str] = []
    if b"\r" in raw:
        problems.append(f"{VERSION_NAME} must use LF line endings only; CR bytes are not allowed")
    if raw.count(b"\n") != 1 or not raw.endswith(b"\n"):
        problems.append(f"{VERSION_NAME} must contain exactly one LF-terminated line")
    if raw != raw.strip() + b"\n":
        # Catches leading/trailing spaces and extra blank lines while keeping the
        # more specific newline diagnostic above.
        problems.append(f"{VERSION_NAME} must not contain surrounding whitespace or extra blank lines")
    if not VERSION_BYTES_RE.fullmatch(raw):
        problems.append(f"{VERSION_NAME} must be canonical bytes b'vNNN\\n' with no leading zeroes")
        return None, problems

    text = raw[:-1].decode("ascii")
    if not VERSION_RE.fullmatch(text):
        problems.append(f"{VERSION_NAME} must be like vNNN with no leading zeroes, got {text!r}")
        return None, problems
    return text, problems
