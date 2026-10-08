#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INLINE_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
REF_DEF_RE = re.compile(r"^\[([^\]]+)\]:\s+(\S+)\s*$", re.MULTILINE)

def iter_markdown_files() -> list[Path]:
    return sorted(ROOT.rglob("*.md"))

def is_external(target: str) -> bool:
    return target.startswith("http://") or target.startswith("https://") or target.startswith("mailto:")

def normalize_local_target(source: Path, target: str) -> Path | None:
    target = target.strip()
    if target.startswith("#"):
        return None
    if "#" in target:
        target = target.split("#", 1)[0]
    if not target:
        return None
    return (source.parent / target).resolve()

def check_markdown_links() -> list[str]:
    errors: list[str] = []
    for path in iter_markdown_files():
        text = path.read_text(encoding="utf-8")
        for target in INLINE_LINK_RE.findall(text):
            if is_external(target):
                continue
            resolved = normalize_local_target(path, target)
            if resolved is None:
                continue
            if not resolved.exists():
                errors.append(f"{path.relative_to(ROOT)} -> missing link target: {target}")
        for _, target in REF_DEF_RE.findall(text):
            if is_external(target):
                continue
            resolved = normalize_local_target(path, target)
            if resolved is None:
                continue
            if not resolved.exists():
                errors.append(f"{path.relative_to(ROOT)} -> missing ref target: {target}")
    return errors

def check_registry() -> list[str]:
    errors: list[str] = []
    registry_path = ROOT / "metadata" / "link-registry.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    seen_ids: set[str] = set()
    seen_urls: set[str] = set()
    for item in registry["links"]:
        if item["id"] in seen_ids:
            errors.append(f"duplicate link id: {item['id']}")
        seen_ids.add(item["id"])
        if item["url"] in seen_urls:
            errors.append(f"duplicate link url: {item['url']}")
        seen_urls.add(item["url"])
        if not item["url"].startswith("https://"):
            errors.append(f"non-https url: {item['url']}")
    return errors

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="print errors as json")
    args = parser.parse_args()

    errors = check_markdown_links() + check_registry()

    if args.json:
        print(json.dumps({"errors": errors}, indent=2))
    else:
        if errors:
            for error in errors:
                print(f"ERROR: {error}")
        else:
            print("Link checks passed.")

    return 1 if errors else 0

if __name__ == "__main__":
    raise SystemExit(main())
