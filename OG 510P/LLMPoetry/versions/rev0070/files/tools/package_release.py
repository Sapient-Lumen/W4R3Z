#!/usr/bin/env python3
"""Create and immediately verify a deterministic LLMPoetry release zip."""
from __future__ import annotations

import argparse
import json
import stat
import zipfile
from pathlib import Path

from release_tree import FIXED_DT, PACKAGE_EXCLUDE, collect_files, sha256_file, verify_release_zip


def package(root: Path, out: Path):
    files = collect_files(root, exclude=PACKAGE_EXCLUDE)
    expected = {rel: sha256_file(path) for path, rel in files}
    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path, rel in files:
            info = zipfile.ZipInfo(rel, FIXED_DT)
            info.create_system = 3
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            archive.writestr(info, path.read_bytes())
    verification = verify_release_zip(out, expected)
    if not verification["ok"]:
        out.unlink(missing_ok=True)
        raise ValueError("release zip verification failed: " + "; ".join(verification["failures"]))
    sidecar = out.with_suffix(out.suffix + ".sha256")
    sidecar.write_text(f"{sha256_file(out)}  {out.name}\n", encoding="utf-8")
    return out, sidecar, verification


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    try:
        out, sidecar, verification = package(Path(args.root), Path(args.out))
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2))
        return 1
    print(json.dumps({"ok": True, "zip": str(out), "sidecar": str(sidecar), **verification}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
