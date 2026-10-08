from __future__ import annotations

import json
import zipfile
from pathlib import Path

import yaml
from typer.testing import CliRunner

from vhk.cli import app
from vhk.project.bundle_materialize import materialize_bundle, BundleMaterializeError


runner = CliRunner()


def _make_project(tmp_path: Path) -> Path:
    project_dir = tmp_path / "proj"
    (project_dir / "macros").mkdir(parents=True)
    (project_dir / "macros" / "hello.yaml").write_text(
        yaml.safe_dump({"name": "hello", "steps": [{"type": "TypeText", "text": "hi"}]}, sort_keys=False)
    )
    (project_dir / "project.yaml").write_text(
        yaml.safe_dump({"name": "proj", "bindings": [{"keys": "Mod4+H", "macro": "hello"}]}, sort_keys=False)
    )
    return project_dir



def test_materialize_bundle_cli_extracts_verified_bundle(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)
    bundle_zip = tmp_path / "proj.zip"
    target = tmp_path / "materialized"

    res = runner.invoke(app, ["bundle", str(project_dir), str(bundle_zip)])
    assert res.exit_code == 0, res.output

    res = runner.invoke(app, ["materialize-bundle", str(bundle_zip), str(target), "--json"])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.stdout)
    assert payload["ok"] is True
    assert payload["bundle_kind"] == "project"
    assert payload["bundle_root_name"] == "proj"
    assert Path(payload["extract_root"]) == target.resolve()
    assert Path(payload["project_root"]) == target.resolve() / "proj"
    assert (target / "proj" / "project.yaml").exists()
    assert (target / ".vhk_bundle_materialized.json").exists()



def test_materialize_bundle_rejects_escaping_members(tmp_path: Path) -> None:
    bundle_zip = tmp_path / "evil.zip"
    with zipfile.ZipFile(bundle_zip, "w") as zf:
        zf.writestr("vhk_bundle_manifest.json", json.dumps({
            "schema": 1,
            "bundle_kind": "project",
            "project_dir_name": "proj",
            "bundle_root_name": "proj",
            "file_count": 1,
            "total_bytes": 4,
            "files": [{"path": "../escape.txt", "size": 4, "sha256": "deadbeef" * 8, "mtime": 0}],
        }))
        zf.writestr("../escape.txt", "oops")

    try:
        materialize_bundle(bundle_zip, tmp_path / "out", verify=False)
    except BundleMaterializeError as exc:
        assert "escapes the target root" in str(exc)
    else:
        raise AssertionError("expected BundleMaterializeError")
