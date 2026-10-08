from __future__ import annotations

import json
import pathlib
import sys


ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools import audit_datacube  # noqa: E402
from tools import plan_test_matrix  # noqa: E402


def check_manifest(root: pathlib.Path) -> None:
    manifest_path = root / "data" / "rules" / "official" / "manifest.json"
    revision_path = root / "REVISION.json"
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    revision = json.loads(revision_path.read_text(encoding="utf-8"))
    assert data["revision"] == revision["revision"]
    assert data["sources"]["comprehensive_rules"]["effective_date"] == "2026-06-19"
    assert data["sources"]["tournament_rules"]["effective_date"] == "2026-02-27"
    for source in data["sources"].values():
        assert source["official"] is True
        assert source["source_url"].startswith("https://")


def check_revision_relations(root: pathlib.Path) -> None:
    issues: list[audit_datacube.AuditIssue] = []
    audit_datacube.audit_revision(root, issues)
    errors = [issue for issue in issues if issue.severity == "error"]
    assert not errors, "revision metadata relation errors: " + "; ".join(
        f"{issue.code}: {issue.detail}" for issue in errors
    )


def check_matrix_planner_uses_auto_cap() -> None:
    previous = {
        "MTGSIM_AUTO_JOBS": plan_test_matrix.os.environ.get("MTGSIM_AUTO_JOBS"),
        "MTGSIM_SANITIZE_AUTO_JOBS": plan_test_matrix.os.environ.get("MTGSIM_SANITIZE_AUTO_JOBS"),
    }
    original_cpu_count = plan_test_matrix.os.cpu_count
    try:
        plan_test_matrix.os.environ["MTGSIM_AUTO_JOBS"] = "3"
        plan_test_matrix.os.environ["MTGSIM_SANITIZE_AUTO_JOBS"] = "2"
        plan_test_matrix.os.cpu_count = lambda: 56  # type: ignore[assignment]
        assert plan_test_matrix.suggested_parallel_shards("release", 500) == 3
        assert plan_test_matrix.suggested_parallel_shards("sanitize", 500) == 2
        assert plan_test_matrix.suggested_parallel_shards("release", 1) == 1
    finally:
        plan_test_matrix.os.cpu_count = original_cpu_count  # type: ignore[assignment]
        for key, value in previous.items():
            if value is None:
                plan_test_matrix.os.environ.pop(key, None)
            else:
                plan_test_matrix.os.environ[key] = value


if __name__ == "__main__":
    check_manifest(ROOT)
    check_revision_relations(ROOT)
    check_matrix_planner_uses_auto_cap()
    print("manifest ok")
