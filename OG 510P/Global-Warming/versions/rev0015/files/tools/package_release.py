#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT = json.loads((ROOT / "PROJECT.json").read_text(encoding="utf-8"))

parser = argparse.ArgumentParser()
parser.add_argument("--timestamp", required=True)
parser.add_argument("--slug", required=True)
args = parser.parse_args()

rev = PROJECT["revision"]
project_slug = PROJECT["project"].replace(" ", "-")
bundle_name = f"{project_slug}-{rev}-{args.timestamp}-{args.slug}.zip"
bundle_path = ROOT.parent / bundle_name
manifest = {
    "project": PROJECT["project"],
    "revision": rev,
    "timestamp": args.timestamp,
    "slug": args.slug,
    "bundle": bundle_name,
}
(ROOT / "RELEASE-MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

exclude = {bundle_name, "__pycache__"}
with zipfile.ZipFile(bundle_path, "w", zipfile.ZIP_DEFLATED) as zf:
    for path in ROOT.rglob("*"):
        if path.is_dir():
            continue
        if any(part in exclude for part in path.parts):
            continue
        zf.write(path, path.relative_to(ROOT).as_posix())

print(bundle_path)
