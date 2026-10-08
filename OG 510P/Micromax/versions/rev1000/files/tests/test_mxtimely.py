from __future__ import annotations

import importlib.util
import json
import os
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]


def _load_mxtimely_module():
    tools_path = str(ROOT / "tools")
    if tools_path not in sys.path:
        sys.path.insert(0, tools_path)
    spec = importlib.util.spec_from_file_location("mxtimely_test_module", ROOT / "tools" / "mxtimely.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_build_steps_default_is_quiet_handoff_lane() -> None:
    module = _load_mxtimely_module()

    steps = module.build_steps(manifest=".artifacts/demo.json")

    assert [step.name for step in steps] == ["context", "audit", "lint", "portable", "doctor"]
    assert steps[3].argv[-1] == "--quiet"
    assert all(step.partial_manifest == "" for step in steps)


def test_build_steps_can_append_bounded_mxtest_slice() -> None:
    module = _load_mxtimely_module()

    steps = module.build_steps(manifest=".artifacts/demo.json", include_tests=True, include_doctor=False)

    assert [step.name for step in steps] == ["context", "audit", "lint", "portable", "mxtest-slice"]
    test_step = steps[-1]
    assert test_step.partial_manifest == ".artifacts/demo.json"
    assert "tools/mxtest.py" in test_step.argv
    assert "--max-runtime-seconds" in test_step.argv
    assert "14.0" in test_step.argv
    assert "--max-new-tests" in test_step.argv
    assert "12" in test_step.argv


def test_parse_skip_tests_wins_over_with_tests() -> None:
    module = _load_mxtimely_module()
    args = module.parse_args(["--with-tests", "--skip-tests"])

    steps = module.build_steps(include_tests=bool(args.with_tests) and not bool(args.skip_tests))

    assert "mxtest-slice" not in [step.name for step in steps]


def test_mxtest_budgeted_partial_ok_accepts_clean_progress(tmp_path: Path) -> None:
    module = _load_mxtimely_module()
    manifest = tmp_path / "mxtest.json"
    manifest.write_text(
        json.dumps(
            {
                "status": "partial",
                "complete": False,
                "chunk_status_counts": {"passed": 1, "partial": 1},
                "test_status_counts": {"passed": 3},
                "chunk_results": [
                    {"status": "passed"},
                    {"status": "not_run", "skip_reason": "max-runtime-seconds-reached+max-new-tests-reached"},
                ],
            }
        ),
        encoding="utf-8",
    )

    ok, note = module.mxtest_budgeted_partial_ok(manifest)

    assert ok is True
    assert "clean" in note


def test_mxtest_budgeted_partial_rejects_failed_tests(tmp_path: Path) -> None:
    module = _load_mxtimely_module()
    manifest = tmp_path / "mxtest.json"
    manifest.write_text(
        json.dumps(
            {
                "status": "partial",
                "complete": False,
                "chunk_status_counts": {"passed": 1},
                "test_status_counts": {"passed": 2, "failed": 1},
                "chunk_results": [],
            }
        ),
        encoding="utf-8",
    )

    ok, note = module.mxtest_budgeted_partial_ok(manifest)

    assert ok is False
    assert "failed" in note


def test_result_for_returncode_uses_partial_manifest_on_mxtest_failure(tmp_path: Path) -> None:
    module = _load_mxtimely_module()
    manifest = tmp_path / "mxtest.json"
    manifest.write_text(
        json.dumps(
            {
                "status": "partial",
                "complete": False,
                "chunk_status_counts": {"passed": 1},
                "test_status_counts": {"passed": 1},
                "chunk_results": [{"status": "not_run", "skip_reason": "max-new-tests-reached"}],
            }
        ),
        encoding="utf-8",
    )
    step = module.TimelyStep("mxtest-slice", ["python"], 1, partial_manifest=str(manifest))

    result = module.result_for_returncode(step, 1, 0.2)

    assert result.ok is True
    assert result.returncode == 1
    assert "clean" in result.note


def test_bounded_env_disables_pytest_autoload_and_prepends_src(monkeypatch) -> None:
    module = _load_mxtimely_module()
    monkeypatch.delenv("PYTEST_DISABLE_PLUGIN_AUTOLOAD", raising=False)
    monkeypatch.delenv("PYTHONDONTWRITEBYTECODE", raising=False)
    monkeypatch.setenv("PYTHONPATH", os.pathsep.join(["/elsewhere"]))

    env = module.bounded_env()

    assert env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] == "1"
    assert env["PYTHONDONTWRITEBYTECODE"] == "1"
    assert env["PYTHONPATH"].split(os.pathsep)[0] == str(ROOT / "src")


def test_write_summary_records_total_timing_and_completion(tmp_path: Path) -> None:
    module = _load_mxtimely_module()
    out = tmp_path / "summary.json"
    results = [
        module.TimelyResult("context", 0, 0.5, True, note="ok"),
        module.TimelyResult("audit", 0, 1.25, True, note="ok"),
    ]

    module.write_summary(out, results, planned_steps=["context", "audit"])
    payload = json.loads(out.read_text(encoding="utf-8"))

    assert payload["schema"] == "micromax.mxtimely.summary.v3"
    assert payload["ok"] is True
    assert payload["status"] == "passed"
    assert payload["complete"] is True
    assert payload["planned_steps"] == ["context", "audit"]
    assert payload["pending_steps"] == []
    assert payload["total_elapsed_seconds"] == 1.75
    assert payload["slowest_step"] == "audit"


def test_write_summary_marks_incomplete_prefix_partial(tmp_path: Path) -> None:
    module = _load_mxtimely_module()
    out = tmp_path / "summary.json"
    results = [module.TimelyResult("context", 0, 0.5, True, note="ok")]

    module.write_summary(out, results, planned_steps=["context", "audit"])
    payload = json.loads(out.read_text(encoding="utf-8"))

    assert payload["ok"] is False
    assert payload["status"] == "partial"
    assert payload["complete"] is False
    assert payload["completed_steps"] == 1
    assert payload["planned_step_count"] == 2
    assert payload["pending_steps"] == ["audit"]


def test_main_writes_summary_after_each_step_before_interruption(tmp_path: Path, monkeypatch) -> None:
    module = _load_mxtimely_module()
    summary = tmp_path / "summary.json"
    steps = [
        module.TimelyStep("context", ["python"], 1),
        module.TimelyStep("audit", ["python"], 1),
    ]
    monkeypatch.setattr(module, "build_steps", lambda **kwargs: steps)

    def fake_run_step(step, *, verbose_children: bool = False):  # noqa: ARG001
        if step.name == "context":
            return module.TimelyResult("context", 0, 0.25, True, note="Rev: 925")
        raise KeyboardInterrupt

    monkeypatch.setattr(module, "run_step", fake_run_step)

    with pytest.raises(KeyboardInterrupt):
        module.main(["--summary-json", str(summary), "--skip-doctor"])

    payload = json.loads(summary.read_text(encoding="utf-8"))
    assert payload["ok"] is False
    assert payload["status"] == "partial"
    assert payload["complete"] is False
    assert payload["planned_steps"] == ["context", "audit"]
    assert payload["pending_steps"] == ["audit"]
    assert [row["name"] for row in payload["results"]] == ["context"]
    assert payload["results"][0]["note"] == "Rev: 925"

