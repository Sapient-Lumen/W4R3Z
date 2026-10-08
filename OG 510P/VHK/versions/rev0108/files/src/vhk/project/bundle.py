from __future__ import annotations

import os
import json
import time
import zipfile
import hashlib
from pathlib import Path

from vhk import __version__


def bundle_project(project_dir: Path, out_zip: Path) -> None:
    """Zip a project folder into a shareable bundle.

    Excludes runtime artifacts like logs/ by default.
    """

    project_dir = project_dir.resolve()
    out_zip = out_zip.resolve()
    exclude_prefixes = {"logs/", ".venv/", "__pycache__/"}

    # First pass: discover included files and compute lightweight integrity data.
    #
    # Why: bundles are shared artifacts. Having checksums in the manifest makes it
    # easier to:
    # - detect partial/corrupt transfers
    # - build cache keys for vision assets
    # - implement future "verify bundle" tooling
    files: list[dict[str, object]] = []
    discovered: list[tuple[str, Path]] = []

    for root, dirs, fns in os.walk(project_dir):
        rel_root = Path(root).relative_to(project_dir).as_posix()
        if rel_root == ".":
            rel_root = ""
        if rel_root and not rel_root.endswith('/'):
            rel_root += '/'

        # Prune excluded dirs (stable ordering helps diffability).
        dirs[:] = sorted(
            [d for d in dirs if f"{rel_root}{d}/" not in exclude_prefixes and not d.startswith(".")]
        )
        for fn in sorted(fns):
            if fn.startswith("."):
                continue
            rel_path = f"{rel_root}{fn}" if rel_root else fn
            if any(rel_path.startswith(p) for p in exclude_prefixes):
                continue
            discovered.append((rel_path, Path(root) / fn))

    for rel_path, abs_path in discovered:
        try:
            data = abs_path.read_bytes()
        except Exception:
            # If a file disappears mid-bundle, we still want a helpful error.
            raise FileNotFoundError(f"Bundle input disappeared: {abs_path}")

        sha256 = hashlib.sha256(data).hexdigest()
        files.append(
            {
                "path": rel_path,
                "size": len(data),
                "sha256": sha256,
                "mtime": int(abs_path.stat().st_mtime),
            }
        )

    with zipfile.ZipFile(out_zip, "w", compression=zipfile.ZIP_DEFLATED) as z:
        # Include lightweight metadata so bundles are self-describing.
        manifest = {
            "schema": 1,
            "vhk_version": __version__,
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "project_dir_name": project_dir.name,
            "file_count": len(files),
            "total_bytes": int(sum(int(f["size"]) for f in files)),
            "files": files,
        }
        z.writestr(
            "vhk_bundle_manifest.json",
            json.dumps(manifest, indent=2)
            + "\n",
        )
        for rel_path, abs_path in discovered:
            z.write(abs_path, arcname=rel_path)


def verify_bundle(bundle_zip: Path) -> tuple[bool, list[str]]:
    """Verify a VHK project bundle against its embedded manifest.

    Returns ``(ok, errors)``.

    Notes
    -----
    - This is not a security boundary.
    - It is meant to detect corrupt transfers and provide a future-friendly
      integrity primitive for tooling.
    """

    bundle_zip = bundle_zip.expanduser().resolve()
    errors: list[str] = []

    with zipfile.ZipFile(bundle_zip, "r") as z:
        try:
            manifest = json.loads(z.read("vhk_bundle_manifest.json").decode("utf-8"))
        except KeyError:
            return False, ["Missing vhk_bundle_manifest.json"]
        except Exception as e:
            return False, [f"Failed to parse manifest: {e}"]

        if not isinstance(manifest, dict):
            return False, ["Manifest must be a JSON object"]

        if manifest.get("schema") != 1:
            errors.append(f"Unsupported manifest schema: {manifest.get('schema')!r}")

        files = manifest.get("files")
        if not isinstance(files, list):
            errors.append("Manifest 'files' must be a list")
            return False, errors

        for entry in files:
            if not isinstance(entry, dict):
                errors.append("Manifest file entry must be an object")
                continue
            rel = entry.get("path")
            expected_sha = entry.get("sha256")
            expected_size = entry.get("size")
            if not isinstance(rel, str):
                errors.append("Manifest file entry missing string 'path'")
                continue
            if not isinstance(expected_sha, str) or len(expected_sha) != 64:
                errors.append(f"{rel}: invalid sha256 in manifest")
                continue
            try:
                expected_size_i = int(expected_size)  # type: ignore[arg-type]
            except Exception:
                errors.append(f"{rel}: invalid size in manifest")
                continue

            try:
                data = z.read(rel)
            except KeyError:
                errors.append(f"{rel}: missing from zip")
                continue

            got_sha = hashlib.sha256(data).hexdigest()
            if got_sha != expected_sha:
                errors.append(f"{rel}: sha256 mismatch")
            if len(data) != expected_size_i:
                errors.append(f"{rel}: size mismatch")

    return len(errors) == 0, errors
