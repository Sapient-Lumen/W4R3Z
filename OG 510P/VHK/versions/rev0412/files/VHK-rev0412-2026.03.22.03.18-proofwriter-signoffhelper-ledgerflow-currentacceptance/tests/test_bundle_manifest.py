import json
import zipfile
from pathlib import Path

import yaml

from vhk.project.bundle import bundle_project, bundle_release_stage, inspect_bundle, verify_bundle
from vhk.project.release_stage_pack import write_release_stage_pack


def _make_project(proj: Path) -> None:
    (proj / "macros").mkdir(parents=True)
    (proj / "macros" / "m.yaml").write_text(yaml.safe_dump({"name": "m", "steps": [{"type": "Log", "message": "hi"}]}))
    (proj / "project.yaml").write_text(yaml.safe_dump({"name": "p", "macros": {"m": "macros/m.yaml"}}))



def test_bundle_includes_manifest(tmp_path: Path):
    proj = tmp_path / "p"
    _make_project(proj)

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



def test_deterministic_bundle_reuses_fixed_timestamp_and_bytes(tmp_path: Path) -> None:
    proj = tmp_path / "p"
    _make_project(proj)

    out1 = tmp_path / "p1.zip"
    out2 = tmp_path / "p2.zip"
    epoch = 1_700_000_000

    bundle_project(proj, out1, deterministic=True, source_date_epoch=epoch)
    bundle_project(proj, out2, deterministic=True, source_date_epoch=epoch)

    assert out1.read_bytes() == out2.read_bytes()

    with zipfile.ZipFile(out1, "r") as z:
        manifest = json.loads(z.read("vhk_bundle_manifest.json").decode("utf-8"))
        assert manifest["deterministic"] is True
        assert manifest["source_date_epoch"] == epoch
        assert manifest["created_at"] == "2023-11-14T22:13:20Z"
        assert all(int(f["mtime"]) == epoch for f in manifest["files"])
        info = z.getinfo("project.yaml")
        assert info.date_time == (2023, 11, 14, 22, 13, 20)


def test_release_stage_bundle_uses_stage_root_and_embeds_lane_metadata(tmp_path: Path) -> None:
    proj = tmp_path / "p"
    _make_project(proj)

    # Ensure the staged lane contains some copied docs as well as lane scripts.
    (proj / "docs").mkdir(parents=True, exist_ok=True)
    (proj / "docs" / "VHK_PUBLIC_SUPPORT.md").write_text("# public support\n")
    write_release_stage_pack(proj, force=True, target_profiles=["x11-desktop"])

    out = tmp_path / "x11-stage.zip"
    bundle_release_stage(proj, out, profile_id="x11-desktop")

    ok, errors = verify_bundle(out)
    assert ok is True, errors

    payload = inspect_bundle(out)
    assert payload["bundle_kind"] == "release-stage"
    assert payload["project_dir_name"] == "p"
    assert payload["bundle_root_name"] == "x11-desktop"
    assert payload["release_stage"]["profile_id"] == "x11-desktop"
    assert payload["release_stage"]["deploy_style"]

    with zipfile.ZipFile(out, "r") as z:
        names = set(z.namelist())
        assert "README.md" in names
        assert "install.sh" in names
        assert "verify.sh" in names
        assert "assemble_payload.sh" in names
        assert "vhk_release_stage.json" in names
        assert "payload/docs/VHK_PUBLIC_SUPPORT.md" in names
        manifest = json.loads(z.read("vhk_bundle_manifest.json").decode("utf-8"))
        assert manifest["bundle_kind"] == "release-stage"
        assert manifest["release_stage_metadata"]["profile_id"] == "x11-desktop"
