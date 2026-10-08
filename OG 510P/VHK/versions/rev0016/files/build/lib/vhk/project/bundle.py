from __future__ import annotations

import os
import json
import time
import zipfile
from pathlib import Path

from vhk import __version__


def bundle_project(project_dir: Path, out_zip: Path) -> None:
    """Zip a project folder into a shareable bundle.

    Excludes runtime artifacts like logs/ by default.
    """

    project_dir = project_dir.resolve()
    out_zip = out_zip.resolve()
    exclude_prefixes = {"logs/", ".venv/", "__pycache__/"}

    with zipfile.ZipFile(out_zip, "w", compression=zipfile.ZIP_DEFLATED) as z:
        # Include lightweight metadata so bundles are self-describing.
        z.writestr(
            "vhk_bundle_manifest.json",
            json.dumps(
                {
                    "vhk_version": __version__,
                    "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "project_dir_name": project_dir.name,
                },
                indent=2,
            )
            + "\n",
        )
        for root, dirs, files in os.walk(project_dir):
            rel_root = Path(root).relative_to(project_dir).as_posix()
            if rel_root and not rel_root.endswith('/'):
                rel_root += '/'
            # prune excluded dirs
            dirs[:] = [d for d in dirs if f"{rel_root}{d}/" not in exclude_prefixes and not d.startswith(".")]
            for fn in files:
                if fn.startswith("."):
                    continue
                rel_path = f"{rel_root}{fn}" if rel_root else fn
                if any(rel_path.startswith(p) for p in exclude_prefixes):
                    continue
                z.write(Path(root) / fn, arcname=rel_path)
