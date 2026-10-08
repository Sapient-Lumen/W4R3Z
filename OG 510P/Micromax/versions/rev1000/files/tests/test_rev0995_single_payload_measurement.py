from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]


def _load_tool() -> ModuleType:
    path = ROOT / "tools" / "measure_single_payload_save.py"
    spec = importlib.util.spec_from_file_location(
        "test_measure_single_payload_save",
        path,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_single_payload_measurement_exposes_exact_complete_journey() -> None:
    module = _load_tool()
    report = module.build_report(chars=120_000, samples=1)

    assert report["schema"] == module.SCHEMA
    preparation = report["save_preparation"]
    legacy = preparation["legacy_reference"]
    product = preparation["single_payload_product"]
    assert legacy["get_text_calls"] == 3
    assert legacy["recovery_aliases_payload"] is False
    assert legacy["rollback_snapshot_present"] is True
    assert product["get_text_calls"] == 1
    assert product["recovery_aliases_payload"] is True
    assert product["rollback_snapshot_present"] is False
    assert preparation["comparison"]["both_exact"] is True
    assert preparation["comparison"]["product_aliases_recovery"] is True

    journey = report["complete_huge_line_journey"]
    assert journey["viewport_found_needle"] is True
    assert journey["search_found"] is True
    assert journey["search_cursor_exact"] is True
    assert journey["cursor_roundtrip"] is True
    assert journey["edited_fragment"] == "!NEEDLE"
    assert journey["undo_fragment"] == "NEEDLE"
    assert journey["redo_fragment"] == "!NEEDLE"
    assert journey["save_get_text_calls"] == 1
    assert journey["save_current_signature_calls"] == 0
    assert journey["save_undo_snapshot_calls"] == 0
    assert journey["save_state_snapshot_calls"] == 0
    assert journey["save_payload_exact"] is True
    assert journey["save_payload_aliases_recovery"] is True
    assert journey["save_checkpoint_commit_argument_is_none"] is True
    assert journey["save_payload_kind"] == module.PAYLOAD_KIND_EDITOR_TEXT
    assert journey["save_clean_signature_exact"] is True
    assert journey["save_buffer_clean"] is True
    assert journey["save_recovery_checkpointed"] is True

    checkpoint = report["recovery_checkpoint_digest"]
    assert checkpoint["payload_identity_sha256_passes"] == 1
    assert checkpoint["record_written"] is True
