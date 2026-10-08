import zipfile
from pathlib import Path

import yaml

from vhk.project.bundle import bundle_project, verify_bundle


def test_verify_bundle_ok_and_detects_corruption(tmp_path: Path):
    proj = tmp_path / "p"
    (proj / "macros").mkdir(parents=True)
    (proj / "macros" / "m.yaml").write_text(yaml.safe_dump({"name": "m", "steps": [{"type": "Log", "message": "hi"}]}))
    (proj / "project.yaml").write_text(yaml.safe_dump({"name": "p", "macros": {"m": "macros/m.yaml"}}))

    out = tmp_path / "p.zip"
    bundle_project(proj, out)
    ok, errors = verify_bundle(out)
    assert ok
    assert errors == []

    # Corrupt one file while keeping the original manifest.
    bad = tmp_path / "p_bad.zip"
    with zipfile.ZipFile(out, "r") as zin, zipfile.ZipFile(bad, "w", compression=zipfile.ZIP_DEFLATED) as zout:
        for info in zin.infolist():
            data = zin.read(info.filename)
            if info.filename == "macros/m.yaml":
                data = data + b"\n# corrupted\n"
            zout.writestr(info.filename, data)

    ok2, errors2 = verify_bundle(bad)
    assert not ok2
    assert any("sha256 mismatch" in e for e in errors2)
