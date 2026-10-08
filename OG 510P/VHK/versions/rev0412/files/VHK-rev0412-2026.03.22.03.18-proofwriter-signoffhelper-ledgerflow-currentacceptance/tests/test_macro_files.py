from __future__ import annotations

from pathlib import Path

import yaml

from vhk.project.init_project import init_project
from vhk.project.macro_files import resolve_macro_path, resolve_macro_recording_sidecar_path, write_macro_steps


def test_resolve_macro_path_prefers_manifest_mapping(tmp_path: Path):
    init_project(tmp_path, template="minimal")

    manifest = tmp_path / "project.yaml"
    doc = yaml.safe_load(manifest.read_text())
    doc.setdefault("macros", {})
    doc["macros"]["foo"] = "custom/foo.yaml"
    manifest.write_text(yaml.safe_dump(doc, sort_keys=False))

    abs_path, rel = resolve_macro_path(tmp_path, "foo")
    assert rel == "custom/foo.yaml"
    assert abs_path == (tmp_path / "custom/foo.yaml").resolve()


def test_write_macro_steps_creates_and_registers(tmp_path: Path):
    init_project(tmp_path, template="minimal")

    steps = [{"type": "Log", "message": "hi"}]
    res = write_macro_steps(tmp_path, macro_name="rec", steps=steps, register=True)

    assert res.macro_path.exists()
    doc = yaml.safe_load(res.macro_path.read_text())
    assert doc["name"] == "rec"
    assert doc["steps"] == steps

    manifest = yaml.safe_load((tmp_path / "project.yaml").read_text())
    assert manifest["macros"]["rec"] == "macros/rec.yaml"


def test_write_macro_steps_preserves_other_fields_and_appends(tmp_path: Path):
    init_project(tmp_path, template="minimal")

    macro_path = tmp_path / "macros" / "m.yaml"
    macro_path.write_text(
        yaml.safe_dump(
            {
                "name": "m",
                "comment": "keep",
                "steps": [{"type": "Log", "message": "a"}],
            },
            sort_keys=False,
        )
    )

    # Explicitly map name -> custom path to ensure resolve respects it.
    manifest = tmp_path / "project.yaml"
    doc = yaml.safe_load(manifest.read_text())
    doc.setdefault("macros", {})
    doc["macros"]["m"] = "macros/m.yaml"
    manifest.write_text(yaml.safe_dump(doc, sort_keys=False))

    res = write_macro_steps(
        tmp_path,
        macro_name="m",
        steps=[{"type": "Log", "message": "b"}],
        register=True,
        append=True,
    )
    assert res.appended
    doc2 = yaml.safe_load(macro_path.read_text())
    assert doc2["comment"] == "keep"
    assert [s["message"] for s in doc2["steps"] if s.get("type") == "Log"] == ["a", "b"]


def test_write_macro_steps_can_set_when_selector(tmp_path: Path):
    init_project(tmp_path, template="minimal")

    res = write_macro_steps(
        tmp_path,
        macro_name="scoped",
        steps=[{"type": "Log", "message": "scoped"}],
        register=True,
        when={"class": "Firefox"},
    )

    doc = yaml.safe_load(res.macro_path.read_text())
    assert doc["when"] == {"class": "Firefox"}
    assert doc["steps"] == [{"type": "Log", "message": "scoped"}]


def test_resolve_macro_recording_sidecar_path_tracks_macro_location(tmp_path: Path):
    init_project(tmp_path, template="minimal")

    manifest = tmp_path / "project.yaml"
    doc = yaml.safe_load(manifest.read_text())
    doc.setdefault("macros", {})
    doc["macros"]["foo"] = "custom/foo.yaml"
    manifest.write_text(yaml.safe_dump(doc, sort_keys=False))

    abs_path, rel = resolve_macro_recording_sidecar_path(tmp_path, "foo")
    assert rel == "custom/foo.window-context.yaml"
    assert abs_path == (tmp_path / "custom/foo.window-context.yaml").resolve()
