from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]


def _load_tool() -> ModuleType:
    path = ROOT / "tools" / "measure_line_vector_replay.py"
    spec = importlib.util.spec_from_file_location(
        "test_measure_line_vector_replay",
        path,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_line_vector_measurement_exposes_replay_and_long_line_attribution() -> None:
    module = _load_tool()

    report = module.build_report(
        line_count=300,
        line_width=60,
        splices=8,
        long_line_chars=30_000,
        long_line_edits=8,
        samples=1,
    )

    assert report["schema"] == module.SCHEMA
    replay = report["sparse_replay"]
    product = replay["line_vector_product"]
    reference = replay["rev0989_flat_reference"]
    comparison = replay["comparison"]

    assert product["roundtrip_exact"] is True
    assert product["full_document_get_text_calls"] == 0
    assert product["full_document_set_text_calls"] == 0
    assert product["complete_result_strings"] == 0
    assert product["line_vector_commits"] == 2

    assert reference["roundtrip_exact"] is True
    assert reference["full_document_get_text_calls"] == 2
    assert reference["full_document_set_text_calls"] == 2
    assert reference["complete_result_strings"] == 2
    assert reference["line_vector_commits"] == 0
    assert comparison["complete_document_string_reduction_percent"] == 100.0
    assert comparison["both_roundtrip_exact"] is True
    assert replay["line_identity_reuse"]["reused_source_line_objects"] >= 290

    for operation in ("insert", "backspace", "delete", "replace"):
        row = report["long_logical_line"][operation]
        fast = row["fastdirty_product_policy"]
        exact = row["exact_dirty_reference_policy"]
        assert fast["action_signature_calls"] == 0
        assert exact["action_signature_calls"] == exact["edits"]
        assert fast["action_text_exact"] is True
        assert fast["undo_text_exact"] is True
        assert fast["redo_text_exact"] is True
        assert exact["action_text_exact"] is True
        assert exact["undo_text_exact"] is True
        assert exact["redo_text_exact"] is True
        assert row["comparison"]["both_roundtrip_exact"] is True
        assert row["comparison"]["signature_pass_reduction_percent"] == 100.0
