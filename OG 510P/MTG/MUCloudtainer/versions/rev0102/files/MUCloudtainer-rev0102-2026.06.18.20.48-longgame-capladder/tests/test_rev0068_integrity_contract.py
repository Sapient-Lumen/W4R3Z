from __future__ import annotations

import json
from pathlib import Path

from src.muc5.package_contract import (
    audit_package_contract,
    parse_cube_name,
    write_checksum_manifest,
)
from src.muc5.response_matrix import (
    CLOSURE_THREAT_AXIS,
    PRESSURE_THREAT_AXIS,
    SURGE_THREAT_AXIS,
    response_matrix_gate_report,
)


def _minimal_cube(tmp_path: Path) -> Path:
    root = tmp_path / "MUCloudtainer-rev0068-2026.06.17.21.15-missionintegrityaudit-evidencebudget"
    (root / "data").mkdir(parents=True)
    (root / "README.md").write_text(
        "# MUCloudtainer rev0068 — missionintegrityaudit-evidencebudget\n",
        encoding="utf-8",
    )
    manifest = {
        "revision": "rev0068",
        "timestamp": "2026.06.17.21.15",
        "codename": "missionintegrityaudit-evidencebudget",
        "cube_name": root.name,
        "filename": f"{root.name}.zip",
    }
    (root / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    (root / "environment.json").write_text(
        json.dumps({"python": {"version": "test"}, "dependencies": {}}), encoding="utf-8"
    )
    (root / "requirements.txt").write_text("pytest\n", encoding="utf-8")
    (root / ".mucignore").write_text("__pycache__/\n", encoding="utf-8")
    (root / "data/revision_log.json").write_text(
        json.dumps(
            {
                "revisions": [
                    {
                        "revision": "rev0068",
                        "timestamp": "2026.06.17.21.15",
                        "codename": "missionintegrityaudit-evidencebudget",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    write_checksum_manifest(root)
    return root


def test_parse_cube_name_round_trip() -> None:
    identity = parse_cube_name(
        "MUCloudtainer-rev0068-2026.06.17.21.15-missionintegrityaudit-evidencebudget"
    )
    assert identity.revision == "rev0068"
    assert identity.filename.endswith("evidencebudget.zip")


def test_package_contract_detects_stale_manifest(tmp_path: Path) -> None:
    root = _minimal_cube(tmp_path)
    assert audit_package_contract(root).passed
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    manifest["revision"] = "rev0067"
    (root / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    report = audit_package_contract(root, verify_checksums=False)
    assert not report.passed
    assert any("manifest_identity_alignment" in error for error in report.errors)


def test_package_contract_detects_generated_cache(tmp_path: Path) -> None:
    root = _minimal_cube(tmp_path)
    cache = root / "src/__pycache__"
    cache.mkdir(parents=True)
    (cache / "module.pyc").write_bytes(b"cache")
    write_checksum_manifest(root)
    report = audit_package_contract(root)
    assert not report.passed
    assert any("forbidden_generated_artifacts_absent" in error for error in report.errors)


def test_response_gate_requires_complete_cartesian_matrix() -> None:
    size_axes = ("counter40_vs_threat40", "counter60_vs_threat40", "counter60_vs_threat60")
    threat_axes = (CLOSURE_THREAT_AXIS, PRESSURE_THREAT_AXIS, SURGE_THREAT_AXIS)
    rows = [
        {"size_axis": size, "threat_policy_axis": threat, "starting_life": life}
        for size in size_axes
        for threat in threat_axes
        for life in (20, 40)
        if not (size == "counter60_vs_threat60" and threat == SURGE_THREAT_AXIS and life == 40)
    ]
    summary = {
        "games": len(rows),
        "truncations": 0,
        "python_errors": 0,
        "forensic_games": len(rows),
        "closure_feature_games": len(rows),
        "counter_ownership_games": len(rows),
        "cpp_shadow_summary": {"mismatches": 0, "skipped_events": 0},
    }
    report = response_matrix_gate_report(summary, rows, [], min_games=1)
    assert not report["passed"]
    assert report["scope"] == "operational_integrity_only"
    assert any("incomplete" in error for error in report["errors"])
