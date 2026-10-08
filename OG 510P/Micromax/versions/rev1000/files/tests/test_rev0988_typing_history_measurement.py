from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]


def _load_tool() -> ModuleType:
    path = ROOT / "tools" / "measure_typing_history.py"
    spec = importlib.util.spec_from_file_location(
        "test_measure_typing_history",
        path,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_typing_history_measurement_compares_exact_current_paths() -> None:
    module = _load_tool()

    report = module.build_report(chars=513, samples=1)

    assert report["schema"] == "micromax.typing-history-measurement.v1"
    reference = report["independent_rows_reference"]
    product = report["bounded_typing_groups"]
    comparison = report["comparison"]
    assert reference["undo_rows"] == 513
    assert product["undo_rows"] == 3
    assert product["max_typing_group_chars"] == 256
    assert reference["logical_retained_text_bytes"] == 513
    assert product["logical_retained_text_bytes"] == 513
    assert reference["roundtrip_exact"] is True
    assert product["roundtrip_exact"] is True
    assert comparison["logical_retained_text_bytes_equal"] is True
    assert comparison["both_roundtrip_exact"] is True
    assert comparison["undo_row_reduction_percent"] > 99
    assert comparison["traced_current_reduction_percent"] > 90
