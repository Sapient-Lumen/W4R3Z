from __future__ import annotations

import json
from pathlib import Path

from src.muc5.revision_artifacts import audit_revision_artifacts, latest_revision_entry


def test_revision_artifact_audit_reports_missing_and_forbidden(tmp_path: Path):
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "keep.csv").write_text("a\n1\n2\n", encoding="utf-8")
    (tmp_path / "data" / "bad_cpp_transitions.csv").write_text("a\n1\n", encoding="utf-8")
    report = audit_revision_artifacts(
        tmp_path,
        revision="revtest",
        expected_paths=["data/keep.csv", "data/missing.json"],
        forbidden_globs=["data/*_cpp_transitions.csv"],
        max_csv_rows={"data/keep.csv": 1},
    )
    assert report.passed is False
    assert report.missing == ("data/missing.json",)
    assert report.forbidden_present == ("data/bad_cpp_transitions.csv",)
    assert report.row_limit_violations[0]["rows"] == 2


def test_latest_revision_entry_reads_last_revision(tmp_path: Path):
    p = tmp_path / "revision_log.json"
    p.write_text(json.dumps({"revisions": [{"revision": "rev0001"}, {"revision": "rev0002"}]}), encoding="utf-8")
    assert latest_revision_entry(p)["revision"] == "rev0002"
