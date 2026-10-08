from __future__ import annotations

import json
from pathlib import Path

import pytest

from micromax_editor import Editor
from micromax_editor.buffer import Cursor
from micromax_editor.screen_consumer import validate_screen_contract_v1
from micromax_editor.screen_budget import ScreenBudgetError
from micromax_editor.screen_contract import (
    SCREEN_CONTRACT_SCHEMA,
    load_screen_contract_schema,
    screen_contract_from_diagnostic,
)


def _key_count(value: object) -> int:
    if isinstance(value, dict):
        return len(value) + sum(_key_count(item) for item in value.values())
    if isinstance(value, list):
        return sum(_key_count(item) for item in value)
    return 0


def test_blank_screen_contract_is_small_versioned_and_bounded() -> None:
    ed = Editor()
    ed.new_buffer("*scratch*", "")

    contract = ed.screen_contract(24, 80)
    compact = json.dumps(
        contract,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    pretty = json.dumps(contract, indent=2, sort_keys=True).encode("utf-8")
    assert validate_screen_contract_v1(contract) == contract

    assert set(contract) == {"schema", "size", "cursor", "rows", "cues"}
    assert contract["schema"] == SCREEN_CONTRACT_SCHEMA
    assert contract["size"] == {"lines": 24, "cols": 80}
    assert contract["cursor"] == {
        "visible": True,
        "mode": "edit",
        "y": 0,
        "x": 0,
    }
    assert len(contract["rows"]) == 24
    assert contract["rows"][0]["source"] == {
        "line": 0,
        "column": 0,
        "screen_x": 0,
    }
    assert contract["cues"] == []

    # These are product budgets, not merely compression ratios. A blank 24x80
    # contract should remain legible and safely below the former ~214 KiB graph.
    assert len(compact) <= 1536
    assert len(pretty) <= 3072
    assert _key_count(contract) <= 96
    assert max(len(row) for row in contract["rows"]) <= 5


def test_screen_contract_projects_only_visible_rows_and_nonempty_cues() -> None:
    diagnostic = {
        "lines": 3,
        "cols": 20,
        "layout": {"viewport_x": 4},
        "display_rows": {
            "rows": [
                {
                    "screen_y": 0,
                    "kind": "viewport",
                    "text": "  3 title",
                    "has_line": 1,
                    "line": 2,
                    "start_col": 5,
                    "continuation": 1,
                    "current": 1,
                    "overflow_cells": [[0, "<"]],
                },
                {
                    "screen_y": 1,
                    "kind": "prompt-panel",
                    "text": "> result",
                    "selected": 1,
                    "type": "sticky",
                    "row_kind": "heading",
                },
                {
                    "screen_y": 2,
                    "kind": "statusline",
                    "text": "status",
                },
            ]
        },
        "viewport_cues": {
            "rows": [
                {
                    "screen_y": 0,
                    "cursorline": 1,
                    "search_spans": [[1, 4]],
                    "current_search_spans": [[2, 3]],
                    "colorcolumn_blank": 1,
                    "colorcolumn_x": 10,
                    "brace_spans": [],
                }
            ]
        },
        "docs_cues": {
            "rows": [
                {
                    "screen_y": 0,
                    "line_role": "heading-title",
                    "link_spans": [[0, 5]],
                    "bold_spans": [[1, 5]],
                    "dim_spans": [],
                    "italic_spans": [],
                }
            ]
        },
        "cursor": {
            "visible": 1,
            "mode": "edit",
            "screen_y": 0,
            "screen_x": 7,
        },
    }

    contract = screen_contract_from_diagnostic(diagnostic)
    assert validate_screen_contract_v1(contract) == contract

    assert contract["rows"][0] == {
        "y": 0,
        "kind": "viewport",
        "text": "  3 title",
        "source": {
            "line": 2,
            "column": 5,
            "screen_x": 4,
            "continuation": True,
        },
        "tags": ["cursor-line", "docs-heading-title", "gutter-current"],
    }
    assert contract["rows"][1]["tags"] == [
        "prompt-selected",
        "prompt-sticky",
        "prompt-heading",
    ]
    assert contract["cursor"] == {
        "visible": True,
        "mode": "edit",
        "y": 0,
        "x": 7,
    }
    assert {
        (cue["y"], cue["x"], cue["end"], cue["kind"])
        for cue in contract["cues"]
    } == {
        (0, 4, 5, "overflow-marker"),
        (0, 4, 9, "docs-link"),
        (0, 5, 8, "search"),
        (0, 5, 9, "docs-bold"),
        (0, 6, 7, "search-current"),
        (0, 14, 15, "color-column"),
    }


def test_screen_contract_exposes_syntax_and_selection_cues() -> None:
    ed = Editor()
    ed.new_buffer("t.mx", ": foo 12 ;\nalpha\n\n", path="t.mx")
    eb = ed.cur()
    ed.options.set("statusline", "false", local=eb.local_options)
    ed.options.set("infobar", "false", local=eb.local_options)
    ed.options.set("cursorline", "false", local=eb.local_options)
    eb.cursors[:] = [Cursor(0, 5), Cursor(2, 0)]
    eb.sel_anchors[:] = [Cursor(0, 2), Cursor(1, 1)]
    eb.cursor_ids[:] = [1, 2]
    eb.primary = 0

    contract = ed.screen_contract(6, 20)
    assert validate_screen_contract_v1(contract) == contract

    cues = {
        (cue["y"], cue["x"], cue["end"], cue["kind"])
        for cue in contract["cues"]
    }
    assert (0, 0, 1, "syntax-kw") in cues
    assert (0, 2, 5, "syntax-def") in cues
    assert (0, 2, 5, "selection-primary") in cues
    assert (0, 6, 8, "syntax-num") in cues
    assert (1, 1, 5, "selection-secondary") in cues
    assert (1, 5, 6, "selection-secondary") in cues


def test_screen_contract_softwrap_source_starts_after_display_indent() -> None:
    ed = Editor()
    ed.new_buffer("wrap.mx", ": abcdefgh  ;", path="wrap.mx")
    eb = ed.cur()
    ed.options.set("statusline", "false", local=eb.local_options)
    ed.options.set("infobar", "false", local=eb.local_options)
    ed.options.set("softwrap", "true", local=eb.local_options)
    ed.options.set("softwrap.contindent", "2", local=eb.local_options)

    contract = ed.screen_contract(4, 8)
    assert validate_screen_contract_v1(contract) == contract

    continuation = contract["rows"][1]
    assert continuation["text"] == "  gh  ;"
    assert continuation["source"] == {
        "line": 0,
        "column": 8,
        "screen_x": 2,
        "continuation": True,
    }
    continuation_cues = [
        cue for cue in contract["cues"] if int(cue["y"]) == 1
    ]
    assert continuation_cues
    assert min(int(cue["x"]) for cue in continuation_cues) >= 2


def test_screen_model_materializes_stateful_screen_parts_once(monkeypatch) -> None:
    ed = Editor()
    ed.new_buffer("*scratch*", "alpha\nbeta")
    original_window = ed._edit_window_model_from_layout
    original_bottom = ed.bottom_rows_model
    window_calls = 0
    bottom_calls = 0

    def counted_window(*args, **kwargs):  # type: ignore[no-untyped-def]
        nonlocal window_calls
        window_calls += 1
        return original_window(*args, **kwargs)

    def counted_bottom(*args, **kwargs):  # type: ignore[no-untyped-def]
        nonlocal bottom_calls
        bottom_calls += 1
        return original_bottom(*args, **kwargs)

    monkeypatch.setattr(ed, "_edit_window_model_from_layout", counted_window)
    monkeypatch.setattr(ed, "bottom_rows_model", counted_bottom)

    diagnostic = ed.screen_model(8, 40)

    assert window_calls == 1
    assert bottom_calls == 1
    assert diagnostic["screen_rows"]["row_count"] == 8
    assert diagnostic["screen_rows"]["rows"][0]["text"].startswith("alpha")


def test_compact_screen_contract_does_not_construct_diagnostic_graph(monkeypatch) -> None:
    ed = Editor()
    ed.new_buffer("*scratch*", "alpha\nbeta")

    def forbidden(*args, **kwargs):  # type: ignore[no-untyped-def]
        raise AssertionError("compact screen path must not call screen_model")

    monkeypatch.setattr(ed, "screen_model", forbidden)

    contract = ed.screen_contract(8, 40)

    assert contract["schema"] == SCREEN_CONTRACT_SCHEMA
    assert contract["rows"][0]["text"].startswith("alpha")


def test_active_help_contract_uses_open_buffer_title_without_catalog_scan(
    tmp_path: Path,
    monkeypatch,
) -> None:
    doc = tmp_path / "outside-help.md"
    doc.write_text("# Local Help\n\nSee [this](#local-help).\n", encoding="utf-8")
    ed = Editor()
    ed.new_buffer("*scratch*", "")
    assert ed.open_help_doc(str(doc), allow_outside_root=True) is True

    def forbidden_catalog():  # type: ignore[no-untyped-def]
        raise AssertionError("active help rendering must not rescan the docs catalog")

    monkeypatch.setattr(ed, "_docs_catalog", forbidden_catalog)
    contract = ed.screen_contract(8, 60)

    assert contract["rows"][0]["text"].endswith("# Local Help")
    assert any(cue["kind"] == "docs-link" for cue in contract["cues"])


def test_packaged_screen_contract_schema_matches_runtime_identity() -> None:
    schema = load_screen_contract_schema()

    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["$id"] == "urn:micromax:schema:screen:v1"
    assert schema["properties"]["schema"]["const"] == SCREEN_CONTRACT_SCHEMA
    assert schema["additionalProperties"] is False
    assert schema["$defs"]["row"]["additionalProperties"] is False
    assert schema["$defs"]["cue"]["additionalProperties"] is False
    assert schema["properties"]["rows"]["maxItems"] == 256
    assert schema["properties"]["cues"]["maxItems"] == 65_536
    assert schema["$defs"]["token"]["pattern"] == (
        "^[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*$"
    )
    assert schema["$defs"]["row"]["properties"]["kind"] == {
        "$ref": "#/$defs/token"
    }
    assert schema["$defs"]["source"]["properties"]["line"]["maximum"] == (2**53) - 1
    hidden_cursor_else = schema["$defs"]["cursor"]["allOf"][0]["else"]
    assert hidden_cursor_else == {
        "not": {
            "anyOf": [
                {"required": ["y"]},
                {"required": ["x"]},
            ]
        }
    }


def test_projection_sanitizes_public_tokens_and_unpaired_surrogates() -> None:
    diagnostic = {
        "lines": 1,
        "cols": 8,
        "display_rows": {
            "rows": [
                {
                    "screen_y": 0,
                    "kind": "Bad_kind " + ("x" * 200),
                    "text": "A\ud800BCDEFGH",
                }
            ]
        },
        "cursor": {
            "visible": 1,
            "mode": "Visual_mode",
            "screen_y": 0,
            "screen_x": 0,
        },
    }

    contract = screen_contract_from_diagnostic(diagnostic)

    assert len(contract["rows"][0]["kind"]) == 96
    assert contract["rows"][0]["kind"].startswith("bad-kind-")
    assert contract["rows"][0]["text"] == "A\ufffdBCDEFG"
    assert contract["cursor"]["mode"] == "visual-mode"
    assert validate_screen_contract_v1(contract) == contract

    diagnostic["display_rows"]["rows"][0]["kind"] = "É_kind"  # type: ignore[index]
    assert screen_contract_from_diagnostic(diagnostic)["rows"][0]["kind"] == "kind"


def test_projection_refuses_noninteroperable_source_coordinates() -> None:
    diagnostic = {
        "lines": 1,
        "cols": 8,
        "display_rows": {
            "rows": [
                {
                    "screen_y": 0,
                    "kind": "viewport",
                    "text": "alpha",
                    "has_line": 1,
                    "line": 2**53,
                    "start_col": 0,
                }
            ]
        },
        "cursor": {"visible": 0, "mode": "edit"},
    }

    with pytest.raises(ScreenBudgetError, match="source line.*interoperable coordinate"):
        screen_contract_from_diagnostic(diagnostic)


def test_projection_refuses_oversized_or_ambiguous_source_rows() -> None:
    diagnostic = {
        "lines": 1,
        "cols": 8,
        "display_rows": {
            "rows": [
                {"screen_y": 0, "kind": "viewport", "text": "alpha"},
                {"screen_y": 0, "kind": "viewport", "text": "beta"},
            ]
        },
        "cursor": {"visible": 0, "mode": "edit"},
    }

    with pytest.raises(ScreenBudgetError, match="display rows row count 2.*budget 1"):
        screen_contract_from_diagnostic(diagnostic)

    diagnostic["lines"] = 2
    with pytest.raises(ScreenBudgetError, match="duplicate screen row 0"):
        screen_contract_from_diagnostic(diagnostic)


def test_projection_budgets_source_cue_entries_before_deduplication(
    monkeypatch,
) -> None:
    import micromax_editor.screen_contract as contract_module

    monkeypatch.setattr(contract_module, "SCREEN_CONTRACT_MAX_CUES", 2)
    diagnostic = {
        "lines": 1,
        "cols": 8,
        "display_rows": {
            "rows": [{"screen_y": 0, "kind": "viewport", "text": "alpha"}]
        },
        "viewport_cues": {
            "rows": [
                {
                    "screen_y": 0,
                    "search_spans": [[0, 1], [0, 1], [0, 1]],
                }
            ]
        },
        "cursor": {"visible": 0, "mode": "edit"},
    }

    with pytest.raises(ScreenBudgetError, match="source cue entry count.*budget 2"):
        screen_contract_from_diagnostic(diagnostic)
