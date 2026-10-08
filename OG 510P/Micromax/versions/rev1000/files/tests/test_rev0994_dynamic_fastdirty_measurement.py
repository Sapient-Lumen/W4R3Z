from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]


def _load_tool() -> ModuleType:
    path = ROOT / "tools" / "measure_dynamic_fastdirty_longline.py"
    spec = importlib.util.spec_from_file_location(
        "test_measure_dynamic_fastdirty_longline",
        path,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_dynamic_fastdirty_measurement_exposes_policy_and_splice_attribution() -> None:
    module = _load_tool()
    report = module.build_report(
        chars=300_000,
        followup_edits=5,
        samples=1,
    )

    assert report["schema"] == module.SCHEMA

    splice = report["single_line_splice"]
    assert splice["legacy_chained_reference"]["result_exact"] is True
    assert splice["single_join_product"]["result_exact"] is True
    assert splice["comparison"]["both_exact"] is True
    assert (
        splice["legacy_chained_reference"]["result_chars"]
        == splice["single_join_product"]["result_chars"]
    )

    growth = report["live_growth_policy"]
    automatic = growth["automatic_product"]
    exact = growth["explicit_exact_reference"]
    assert automatic["signature_calls_at_crossing"] == 1
    assert automatic["signature_calls_total"] == 1
    assert automatic["fastdirty_after_crossing"] is True
    assert automatic["visible_local_fastdirty"] is True
    assert exact["signature_calls_at_crossing"] == 1
    assert exact["signature_calls_total"] == 6
    assert exact["fastdirty_after_crossing"] is False
    assert exact["visible_local_fastdirty"] is False
    assert growth["comparison"]["automatic_hashes_only_crossing_edit"] is True
    assert growth["comparison"]["explicit_exact_hashes_every_edit"] is True
    assert growth["comparison"]["both_text_lengths_exact"] is True

    cache = report["mark_clean_cache"]
    assert cache["signature_calls_after_exact_mutation"] == 1
    assert cache["signature_calls_after_mark_clean"] == 1
    assert cache["clean_reused_current_signature"] is True
