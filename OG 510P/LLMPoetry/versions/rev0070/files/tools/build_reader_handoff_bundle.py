#!/usr/bin/env python3
"""Build the portable P0002-D010 reader handoff bundle.

The bundle is deliberately reader-facing only. It excludes evaluator rubric files,
source packets, cube registries, reports, and tools. The ZIP is not evidence of a
reader response; it is a transfer surface for the next real disclosed-reader pass.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from pathlib import Path

FIXED_DT = (1980, 1, 1, 0, 0, 0)
HANDOFF_DIR = Path("anthology/candidates/P0002-D010_reader_handoff")
BUNDLE_PATH = Path("anthology/candidates/P0002-D010_reader_handoff_bundle.zip")
SIDE_PATH = Path("anthology/candidates/P0002-D010_reader_handoff_bundle.zip.sha256")
PAYLOAD_FILES = [
    "README.md",
    "reader_one_sheet.md",
    "reader_one_sheet.html",
    "reader_response_form.html",
    "response_intake_template.json",
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, obj: dict) -> None:
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def file_entry(root: Path, rel: str) -> dict:
    p = root / HANDOFF_DIR / rel
    return {"path": rel, "size": p.stat().st_size, "sha256": sha256_file(p)}


def build(root: Path, revision: str | None = None, created_at: str | None = None) -> dict:
    state = load_json(root / "STATE.json")
    rev = revision or state.get("revision")
    timestamp = created_at or state.get("updated_at") or state.get("timestamp")
    handoff = root / HANDOFF_DIR
    handoff.mkdir(parents=True, exist_ok=True)

    missing = [rel for rel in PAYLOAD_FILES if not (handoff / rel).exists()]
    if missing:
        raise FileNotFoundError(f"missing handoff payload files: {missing}")

    manifest_path = handoff / "HANDOFF_MANIFEST.json"
    manifest = load_json(manifest_path) if manifest_path.exists() else {}
    manifest.update({
        "schema": "llmpoetry-reader-handoff-manifest-v2",
        "revision": rev,
        "updated_at": timestamp,
        "draft_id": "P0002-D010",
        "candidate_id": "CAND-P0002-D010-001",
        "status": "portable_reader_handoff_bundle_built_not_run",
        "bundle_path": BUNDLE_PATH.as_posix(),
        "bundle_sidecar": SIDE_PATH.as_posix(),
        "bundle_includes_evaluator_rubric": False,
        "bundle_includes_source_packet": False,
        "bundle_includes_tools_or_registries": False,
        "evaluator_rubric_included": False,
        "source_packet_included": False,
        "cube_paths_in_reader_files": False,
        "no_live_water_level_claim": True,
        "files": [file_entry(root, rel) for rel in PAYLOAD_FILES],
        "non_claim": "Portable handoff bundle readiness is not a reader response, admission, or evidence status."
    })
    # Keep original created fields if present, but current revision/timestamp must be fresh.
    manifest.setdefault("created_turn", state.get("turn", {}).get("last_completed"))
    manifest.setdefault("created_at", timestamp)
    write_json(manifest_path, manifest)

    out = root / BUNDLE_PATH
    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for rel in ["HANDOFF_MANIFEST.json", *PAYLOAD_FILES]:
            p = handoff / rel
            info = zipfile.ZipInfo(rel, FIXED_DT)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, p.read_bytes())
    side = root / SIDE_PATH
    side.write_text(f"{sha256_file(out)}  {BUNDLE_PATH.name}\n", encoding="utf-8")
    return {"ok": True, "bundle": BUNDLE_PATH.as_posix(), "sidecar": SIDE_PATH.as_posix(), "sha256": sha256_file(out)}


def main() -> int:
    ap = argparse.ArgumentParser(description="Build reader-only P0002-D010 handoff bundle")
    ap.add_argument("--root", default=".")
    ap.add_argument("--revision")
    ap.add_argument("--created-at")
    args = ap.parse_args()
    report = build(Path(args.root), args.revision, args.created_at)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
