from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]


def _load_tool() -> ModuleType:
    path = ROOT / "tools" / "measure_qreplace_history.py"
    spec = importlib.util.spec_from_file_location(
        "test_measure_qreplace_history",
        path,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_qreplace_history_measurement_exposes_broad_reference_shape() -> None:
    module = _load_tool()

    report = module.build_report(chars=30_000, matches=5, samples=1)

    assert report["schema"] == "micromax.qreplace-history-measurement.v1"
    sparse = report["sparse_query_replace"]
    reference = report["rev0988_broad_reference"]
    comparison = report["comparison"]

    assert sparse["matches"] == 5
    assert sparse["answer_full_document_materializations"] == 0
    assert sparse["full_document_callback_generations"] == 0
    assert sparse["simultaneous_witnesses"] == 1
    assert sparse["simultaneous_witness_splices"] == 5
    assert sparse["max_callback_string_chars"] == len(module.TOKEN)

    assert reference["answer_full_document_materializations"] == 23
    assert reference["full_document_callback_generations"] == 2
    assert reference["simultaneous_witnesses"] == 0
    assert reference["max_callback_string_chars"] == reference["document_chars"]
    assert reference["accounted_retained_text_bytes"] > (
        sparse["accounted_retained_text_bytes"] * 100
    )

    assert comparison["reference_materialization_formula_holds"] is True
    assert comparison["product_has_no_answer_materializations"] is True
    assert comparison["both_roundtrip_exact"] is True
    assert comparison["answer_materialization_reduction_percent"] == 100.0
    assert comparison["accounted_retained_text_reduction_percent"] > 99
    assert comparison["traced_current_reduction_percent"] > 50
