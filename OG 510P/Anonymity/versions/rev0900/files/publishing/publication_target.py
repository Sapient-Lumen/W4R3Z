#!/usr/bin/env python3
"""Portable published-target naming helpers.

The human title remains ``Anonymity: ...`` in metadata and decisions, but the
filesystem target is deliberately slugged so a future publication cannot create
colon/space-heavy paths that pass planning but fail archive portability once
materialized.
"""

from __future__ import annotations

import argparse
import json
import re

PREFIX = "Anonymity: "
DATE_RE = re.compile(r"^\d{4}\.\d{2}\.\d{2}$")
SLUG_RE = re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)*$")
PORTABLE_DIR_RE = re.compile(r"^\d{4}-\d{2}-\d{2}_[a-z0-9]+(?:_[a-z0-9]+)*$")
MAX_DIRNAME_BYTES = 180


def short_title(title: str) -> str:
    text = title.strip()
    if text.lower().startswith(PREFIX.lower()):
        return text[len(PREFIX):].strip()
    return text


def date_slug(date: str) -> str:
    if not DATE_RE.match(date):
        raise ValueError(f"publication date must be YYYY.MM.DD: {date!r}")
    return date.replace(".", "-")


def title_slug(title: str) -> str:
    text = short_title(title).lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    if not text:
        raise ValueError("publication title slug is empty")
    return text


def portable_published_dirname(date: str, title: str) -> str:
    base = f"{date_slug(date)}_{title_slug(title)}"
    if len(base.encode("utf-8")) > MAX_DIRNAME_BYTES:
        raise ValueError(f"publication dirname exceeds {MAX_DIRNAME_BYTES} bytes: {base!r}")
    return base


def portable_published_path(date: str, title: str) -> str:
    return f"published/{portable_published_dirname(date, title)}"


def display_title(title: str) -> str:
    return PREFIX + short_title(title)


def is_portable_published_dirname(name: str) -> bool:
    return bool(PORTABLE_DIR_RE.match(name)) and len(name.encode("utf-8")) <= MAX_DIRNAME_BYTES


def is_portable_published_path(path: str) -> bool:
    if not path.startswith("published/") or path.count("/") != 1:
        return False
    return is_portable_published_dirname(path.split("/", 1)[1])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True)
    parser.add_argument("--title", required=True)
    args = parser.parse_args()
    out = {
        "published_name": portable_published_dirname(args.date, args.title),
        "published_path": portable_published_path(args.date, args.title),
        "display_title": display_title(args.title),
    }
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
