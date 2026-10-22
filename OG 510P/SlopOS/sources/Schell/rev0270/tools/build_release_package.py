#!/usr/bin/env python3
"""Build a deterministic Schell release zip from the checked source tree.

This is a bounded custody helper, not SLSA/in-toto provenance, host attestation,
truth proof, deletion proof, policy permission, helper authority, or SlopOS append authority.
"""
import json
import stat
import sys
import zipfile
from pathlib import Path

DANGEROUS_EFFECTS = "policy/helper/public-export/receiver-sync/SlopOS-append remain blocked"

def load_json(root, rel):
    return json.loads((root / rel).read_text())

def zip_mode(mode_text):
    return int(mode_text, 8) | stat.S_IFREG

def main():
    root = Path(__file__).resolve().parents[1]
    release = load_json(root, "RELEASE-MANIFEST.json")
    env = load_json(root, "ENVIRONMENT-DETERMINISM-MANIFEST.json")
    pcm = load_json(root, "PACKAGE-CONTENTS-MANIFEST.json")
    if env.get("package_root") != root.name:
        raise SystemExit("environment package_root mismatch")
    if pcm.get("package_root") != root.name:
        raise SystemExit("package manifest package_root mismatch")
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else root.parent / release["bundle"]
    if target.is_dir():
        target = target / release["bundle"]
    fixed = tuple(env["normalized_environment"]["fixed_zip_datetime_utc"])
    entries = []
    for item in pcm["files"]:
        entries.append((f"{root.name}/{item['path']}", root / item["path"], item["mode"]))
    entries.append((f"{root.name}/PACKAGE-CONTENTS-MANIFEST.json", root / "PACKAGE-CONTENTS-MANIFEST.json", "0o644"))
    entries.sort(key=lambda x: x[0])
    if target.exists():
        target.unlink()
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_STORED, allowZip64=False) as zf:
        zf.comment = b""
        for arc, src, mode_text in entries:
            info = zipfile.ZipInfo(arc, fixed)
            info.compress_type = zipfile.ZIP_STORED
            info.create_system = 3
            info.external_attr = (zip_mode(mode_text) & 0xFFFF) << 16
            info.extra = b""
            info.comment = b""
            zf.writestr(info, src.read_bytes())
    print(f"build_release_package: wrote {target} ({DANGEROUS_EFFECTS})")

if __name__ == "__main__":
    main()
