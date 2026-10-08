import json
import zipfile
from pathlib import Path

import yaml

from vhk.project.bundle import bundle_project


def test_bundle_includes_manifest(tmp_path: Path):
    proj = tmp_path / "p"
    (proj / "macros").mkdir(parents=True)
    (proj / "macros" / "m.yaml").write_text(yaml.safe_dump({"name": "m", "steps": [{"type": "Log", "message": "hi"}]}))
    (proj / "project.yaml").write_text(yaml.safe_dump({"name": "p", "macros": {"m": "macros/m.yaml"}}))

    out = tmp_path / "p.zip"
    bundle_project(proj, out)

    with zipfile.ZipFile(out, "r") as z:
        data = json.loads(z.read("vhk_bundle_manifest.json").decode("utf-8"))
        assert "vhk_version" in data
        assert data["project_dir_name"] == "p"

        # Integrity inventory.
        assert data["schema"] == 1
        assert data["file_count"] >= 2
        assert data["total_bytes"] > 0

        files = {f["path"]: f for f in data["files"]}
        assert "project.yaml" in files
        assert "macros/m.yaml" in files
        assert len(files["project.yaml"]["sha256"]) == 64