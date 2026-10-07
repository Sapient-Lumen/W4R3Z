#!/usr/bin/env python3
"""Render human/hash companion files for compared datacube transfer sources."""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from collections import Counter


def load_json(path: pathlib.Path):
    return json.loads(path.read_text(encoding="utf-8"))


def normalize(root: pathlib.Path, data: dict) -> dict:
    release_manifest = load_json(root / "RELEASE_MANIFEST.json")
    archive_index = load_json(root / "ARCHIVE_INDEX.json")
    entries = list(data.get("source_bundles", []))
    counts = Counter(entry.get("transfer_status", "") for entry in entries)
    data["generated_for_revision"] = release_manifest["revision"]
    previous_revision = release_manifest["revision"]
    revisions = archive_index.get("revisions", [])
    if len(revisions) > 1:
        previous_revision = revisions[1]["revision"]
    data["compared_against_primary_revision"] = previous_revision
    data["source_bundle_count"] = len(entries)
    data["status_counts"] = {
        "adopted_pattern": counts.get("adopted_pattern", 0),
        "reviewed_no_strong_transfer": counts.get("reviewed_no_strong_transfer", 0),
    }
    return data


def render(root: pathlib.Path) -> dict:
    path = root / "TRANSFER_SOURCES.json"
    data = normalize(root, load_json(path))
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    entries = list(data.get("source_bundles", []))
    entries.sort(key=lambda e: (e["project"].lower(), e["bundle"].lower()))

    md_lines = [
        "# Transfer Sources",
        "",
        "These are the exact uploaded non-primary datacube bundles compared against this primary archive during transfer-review passes.",
        "Use this file when you need the precise comparison inputs rather than only the higher-level adoption summary in `DATACUBE_TRANSFER_LEDGER.md`.",
        "",
        f"- Generated for revision: `{data['generated_for_revision']}`",
        f"- Compared against primary revision: `{data['compared_against_primary_revision']}`",
        f"- Source bundle count: {data['source_bundle_count']}",
        f"- Adopted-pattern sources: {data['status_counts']['adopted_pattern']}",
        f"- Reviewed-without-strong-transfer sources: {data['status_counts']['reviewed_no_strong_transfer']}",
        "",
        "| Project | Revision | Status | Bundle | SHA-256 |",
        "| --- | --- | --- | --- | --- |",
    ]
    for e in entries:
        md_lines.append(f"| {e['project']} | {e['source_revision']} | {e['transfer_status']} | `{e['bundle']}` | `{e['sha256']}` |")
    md_lines.extend([
        "",
        "The machine-readable companion is `TRANSFER_SOURCES.json`; the exact filename/hash receipt is `TRANSFER_INPUTS.sha256`.",
        "",
    ])
    (root / "TRANSFER_SOURCES.md").write_text("\n".join(md_lines), encoding="utf-8")

    sha_lines = [f"{e['sha256']}  {e['bundle']}" for e in entries]
    (root / "TRANSFER_INPUTS.sha256").write_text("\n".join(sha_lines) + "\n", encoding="utf-8")
    return {
        "rendered_markdown": "TRANSFER_SOURCES.md",
        "rendered_sha_receipt": "TRANSFER_INPUTS.sha256",
        "entry_count": len(entries),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    root = pathlib.Path(args.root).resolve()
    sys.stdout.write(json.dumps(render(root), indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
