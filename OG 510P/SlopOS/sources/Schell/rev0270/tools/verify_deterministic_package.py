#!/usr/bin/env python3
"""Verify deterministic Schell zip metadata and file content.

This verifies bounded package-byte custody only. It does not prove erasure,
sanitization, compliance, host trust, helper authority, policy permission, receiver
sync, public proof permission, or SlopOS append authority.
"""
import argparse
import hashlib
import json
import stat
import zipfile
from pathlib import Path

DANGEROUS_EFFECTS = "policy/helper/public-export/receiver-sync/SlopOS-append remain blocked"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("zip_path")
    ns = ap.parse_args()
    zip_path = Path(ns.zip_path)
    root_name = zip_path.name[:-4]
    with zipfile.ZipFile(zip_path) as zf:
        names = zf.namelist()
        if names != sorted(names):
            raise SystemExit("deterministic zip entries are not sorted")
        if zf.comment:
            raise SystemExit("zip comment must be empty")
        if any(n.endswith("/") for n in names):
            raise SystemExit("deterministic package must not include directory entries")
        manifest_name = f"{root_name}/ENVIRONMENT-DETERMINISM-MANIFEST.json"
        pcm_name = f"{root_name}/PACKAGE-CONTENTS-MANIFEST.json"
        if manifest_name not in names:
            raise SystemExit("environment determinism manifest missing from zip")
        if pcm_name not in names:
            raise SystemExit("package contents manifest missing from zip")
        env = json.loads(zf.read(manifest_name).decode())
        pcm = json.loads(zf.read(pcm_name).decode())
        fixed = tuple(env["normalized_environment"]["fixed_zip_datetime_utc"])
        if env.get("package_root") != root_name or pcm.get("package_root") != root_name:
            raise SystemExit("package root mismatch inside deterministic zip")
        expected = {f"{root_name}/PACKAGE-CONTENTS-MANIFEST.json"}
        expected.update(f"{root_name}/{item['path']}" for item in pcm["files"])
        if set(names) != expected:
            raise SystemExit("deterministic zip file set mismatch")
        by_path = {item["path"]: item for item in pcm["files"]}
        for info in zf.infolist():
            if info.date_time != fixed:
                raise SystemExit(f"timestamp drift: {info.filename}")
            if info.compress_type != zipfile.ZIP_STORED:
                raise SystemExit(f"compression drift: {info.filename}")
            if info.extra or info.comment:
                raise SystemExit(f"zip metadata residue: {info.filename}")
            if info.compress_size != info.file_size:
                raise SystemExit(f"stored entry size mismatch: {info.filename}")
            mode = (info.external_attr >> 16) & 0o777777
            if (mode & 0o170000) != stat.S_IFREG:
                raise SystemExit(f"non-regular entry: {info.filename}")
            rel = info.filename[len(root_name)+1:]
            if rel == "PACKAGE-CONTENTS-MANIFEST.json":
                continue
            expected_item = by_path[rel]
            data = zf.read(info.filename)
            if len(data) != expected_item["bytes"]:
                raise SystemExit(f"byte count mismatch: {rel}")
            if hashlib.sha256(data).hexdigest() != expected_item["sha256"]:
                raise SystemExit(f"sha256 mismatch: {rel}")
            if oct(mode & 0o777) != expected_item["mode"]:
                raise SystemExit(f"mode mismatch: {rel}")
    print(f"verify_deterministic_package: zip ok ({DANGEROUS_EFFECTS})")

if __name__ == "__main__":
    main()
