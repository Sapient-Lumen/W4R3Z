from __future__ import annotations

import json
from pathlib import Path

from i2p_dht_lab.surfaceclean import SurfaceCleanReport, audit_surface_clean


def test_surfaceclean_real_cube_has_no_errors_after_revision_surfaces_update() -> None:
    root = Path(__file__).resolve().parents[1]
    current_revision = (root / "VERSION").read_text(encoding="utf-8").strip()
    report = audit_surface_clean(root, revision=current_revision)
    assert isinstance(report, SurfaceCleanReport)
    assert report.error_count == 0
    assert report.digest.hex()


def test_surfaceclean_detects_version_revision_mismatch(tmp_path: Path) -> None:
    (tmp_path / "src" / "i2p_dht_lab").mkdir(parents=True)
    (tmp_path / "tests").mkdir()
    (tmp_path / "VERSION").write_text("rev0000\n", encoding="utf-8")
    (tmp_path / "PUBLIC_SURFACE.json").write_text(json.dumps({"revision": "rev0000"}), encoding="utf-8")
    report = audit_surface_clean(tmp_path, revision="rev0019")
    assert report.error_count >= 1
    assert any(finding.code == "version_revision_mismatch" for finding in report.findings)


def test_surfaceclean_can_escalate_historical_legacy_test_imports(tmp_path: Path) -> None:
    (tmp_path / "src" / "i2p_dht_lab").mkdir(parents=True)
    (tmp_path / "tests").mkdir()
    (tmp_path / "VERSION").write_text("rev0019\n", encoding="utf-8")
    (tmp_path / "tests" / "test_legacy.py").write_text("from i2p_dht_lab.providerpoison import x\n", encoding="utf-8")
    report = audit_surface_clean(tmp_path, revision="rev0019", allow_historical_tests=False)
    assert any(finding.code == "legacy_test_import" for finding in report.findings)
