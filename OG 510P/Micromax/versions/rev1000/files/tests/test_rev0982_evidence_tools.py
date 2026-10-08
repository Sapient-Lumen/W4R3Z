from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]


def _load_tool(name: str) -> ModuleType:
    path = ROOT / "tools" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"test_{name}", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_hotpath_measurement_tool_reports_small_semantic_witnesses() -> None:
    module = _load_tool("measure_hotpath_allocations")

    report = module.build_report(
        cases=("wordwrap", "search", "replace"),
        wordwrap_chars=1_000,
        wordwrap_width=10,
        search_matches=200,
        replace_matches=100,
    )

    assert report["schema"] == "micromax.hotpath-allocation-witness.v1"
    assert "not RSS" in report["measurement_scope"]
    rows = {row["case"]: row for row in report["cases"]}
    assert rows["true-wordwrap"]["visual_rows"] == 100
    assert rows["true-wordwrap"]["retained_coordinate_bytes"] <= 256 * 1024
    assert rows["cold-literal-search"]["matches"] == 200
    assert rows["cold-literal-search"]["retained_coordinate_bytes"] == 3_208
    assert rows["complete-replace-plan"]["matches"] == 100
    assert rows["complete-replace-plan"]["sample_rows"] == 3
    assert all(row["traced_peak_bytes"] >= row["traced_current_bytes"] for row in rows.values())


def test_subprocess_start_stall_tool_proves_one_pending_late_handoff() -> None:
    module = _load_tool("reproduce_subprocess_start_stall")

    result = module.run_witness(
        observation_seconds=0.02,
        deadline_seconds=0.02,
    )

    assert result["schema"] == "micromax.subprocess-start-stall-witness.v1"
    assert result["raw_constructor_still_blocked"] is True
    assert result["first_caller_timed_out"] is True
    assert result["second_caller_timed_out"] is True
    assert result["second_factory_calls"] == 0
    assert result["cleaned_labels"] == ["late-first"]
    assert result["late_cleanup_finished"] is True
    assert result["later_start_recovered"] is True
