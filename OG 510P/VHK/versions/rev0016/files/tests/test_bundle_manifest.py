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