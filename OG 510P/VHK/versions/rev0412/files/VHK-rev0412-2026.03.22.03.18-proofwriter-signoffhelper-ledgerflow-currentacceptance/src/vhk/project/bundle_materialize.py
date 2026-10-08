from __future__ import annotations

import json
import os
import shutil
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any

from vhk.project.bundle import inspect_bundle, verify_bundle


class BundleMaterializeError(ValueError):
    """Raised when a VHK bundle cannot be materialized safely."""


def _safe_member_path(name: str) -> tuple[str, ...]:
    member = PurePosixPath(name)
    if member.is_absolute():
        raise BundleMaterializeError(f"Bundle member uses an absolute path: {name}")
    parts = tuple(part for part in member.parts if part not in {"", "."})
    if not parts:
        return tuple()
    if any(part == ".." for part in parts):
        raise BundleMaterializeError(f"Bundle member escapes the target root: {name}")
    return parts


def materialize_bundle(
    bundle_zip: Path,
    target_root: Path,
    *,
    verify: bool = True,
    force: bool = True,
) -> dict[str, Any]:
    """Safely extract a verified VHK bundle into ``target_root``.

    Returns a small metadata dictionary that includes the extracted project root.
    """

    bundle_zip = bundle_zip.expanduser().resolve()
    target_root = target_root.expanduser().resolve()
    if verify:
        ok, errors = verify_bundle(bundle_zip)
        if not ok:
            joined = "; ".join(str(err) for err in errors)
            raise BundleMaterializeError(f"Bundle verification failed: {joined}")

    info = inspect_bundle(bundle_zip)
    bundle_root_name = str(info.get("bundle_root_name") or "").strip()
    tmp_root = target_root.parent / f".{target_root.name}.tmp"
    if tmp_root.exists():
        shutil.rmtree(tmp_root)
    tmp_root.mkdir(parents=True, exist_ok=True)

    try:
        root_names: set[str] = set()
        extract_parent = tmp_root / bundle_root_name if bundle_root_name else tmp_root
        with zipfile.ZipFile(bundle_zip, "r") as zf:
            for zinfo in zf.infolist():
                parts = _safe_member_path(zinfo.filename)
                if not parts:
                    continue
                root_names.add(parts[0])
                out_path = extract_parent.joinpath(*parts)
                if zinfo.is_dir() or zinfo.filename.endswith("/"):
                    out_path.mkdir(parents=True, exist_ok=True)
                    continue
                out_path.parent.mkdir(parents=True, exist_ok=True)
                with zf.open(zinfo, "r") as src, out_path.open("wb") as dst:
                    shutil.copyfileobj(src, dst)
                mode = (int(zinfo.external_attr) >> 16) & 0o777
                if mode:
                    try:
                        out_path.chmod(mode)
                    except OSError:
                        pass

        if not root_names:
            raise BundleMaterializeError("Bundle did not contain any extractable files")
        if not bundle_root_name:
            if len(root_names) != 1:
                raise BundleMaterializeError(
                    "Bundle root is ambiguous; inspect-bundle did not expose one distinct root directory"
                )
            bundle_root_name = next(iter(root_names))
            project_root = tmp_root / bundle_root_name
        else:
            project_root = extract_parent
        if not project_root.is_dir():
            raise BundleMaterializeError(f"Extracted bundle root is not a directory: {project_root}")

        metadata = {
            "bundle": str(bundle_zip),
            "bundle_kind": str(info.get("bundle_kind") or "project"),
            "bundle_root_name": bundle_root_name,
            "project_root": str(project_root),
            "extract_root": str(tmp_root),
            "verified": bool(verify),
        }
        (tmp_root / ".vhk_bundle_materialized.json").write_text(
            json.dumps(metadata, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        if target_root.exists():
            if not force:
                raise BundleMaterializeError(f"Target root already exists: {target_root}")
            shutil.rmtree(target_root)
        target_root.parent.mkdir(parents=True, exist_ok=True)
        os.replace(tmp_root, target_root)
        metadata["extract_root"] = str(target_root)
        metadata["project_root"] = str(target_root / bundle_root_name)
        metadata_path = target_root / ".vhk_bundle_materialized.json"
        metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return metadata
    finally:
        if tmp_root.exists():
            shutil.rmtree(tmp_root, ignore_errors=True)
