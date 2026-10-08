from __future__ import annotations

import copy
import importlib.util
import random
import sys
from pathlib import Path
from types import ModuleType

from micromax_editor.buffer import Cursor
from micromax_editor.editor import Editor
from micromax_editor.query_replace import (
    QueryReplaceSourceSnapshot,
    advance_cursor_through_source_span,
    advance_cursor_through_text_span,
)
from micromax_editor.replace_plan import (
    scan_literal_replacement_edits_lines,
    scan_replacement_edits,
)
from micromax_editor.search import PackedOffsets as SearchPackedOffsets
from micromax_editor.textpos import PackedOffsets

ROOT = Path(__file__).resolve().parents[1]


def _scan_signature(scan: object) -> tuple[object, ...]:
    return (
        getattr(scan, "ok"),
        getattr(scan, "error"),
        getattr(scan, "edits"),
        getattr(scan, "worker_routed"),
        getattr(scan, "timed_out"),
    )


def _load_measurement_tool() -> ModuleType:
    path = ROOT / "tools" / "measure_qreplace_source.py"
    spec = importlib.util.spec_from_file_location(
        "test_measure_qreplace_source",
        path,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_source_snapshot_shares_lines_and_deepcopy_generation() -> None:
    lines = ("alpha", "beta", "", "omega")
    snapshot = QueryReplaceSourceSnapshot.capture(lines)

    assert snapshot.lines is lines
    assert all(snapshot.lines[index] is lines[index] for index in range(len(lines)))
    assert snapshot.length == len("\n".join(lines))
    assert snapshot.coordinate_bytes == 8 * len(lines)
    assert snapshot.range_text_offsets(3, 11) == "ha\nbeta\n"
    assert copy.deepcopy(snapshot) is snapshot


def test_source_snapshot_detaches_mutable_line_vector() -> None:
    first = "alpha"
    second = "beta"
    lines = [first, second]
    snapshot = QueryReplaceSourceSnapshot.capture(lines)

    lines[0] = "changed"
    lines.append("later")

    assert snapshot.lines == ("alpha", "beta")
    assert snapshot.lines[0] is first
    assert snapshot.lines[1] is second
    assert snapshot.materialize_text() == "alpha\nbeta"


def test_source_coordinate_advance_matches_flat_oracle() -> None:
    text = "zero\none two\nthree\nfour"
    snapshot = QueryReplaceSourceSnapshot.capture(tuple(text.split("\n")))
    origin = Cursor(7, 11)

    for left in range(len(text) + 1):
        for right in range(left, len(text) + 1):
            assert advance_cursor_through_source_span(
                origin,
                snapshot.cursor_at(left),
                snapshot.cursor_at(right),
            ) == advance_cursor_through_text_span(origin, text, left, right)


def test_segmented_literal_scan_matches_flat_oracle_at_every_boundary() -> None:
    rng = random.Random(997)
    alphabet = "abAB.[]\\\nİıſKiIsSkK"

    for _ in range(300):
        text = "".join(rng.choice(alphabet) for _ in range(rng.randrange(0, 90)))
        search = "".join(rng.choice(alphabet) for _ in range(rng.randrange(1, 11)))
        value = "".join(rng.choice("xy\n") for _ in range(rng.randrange(0, 5)))
        start = rng.randrange(0, len(text) + 4)
        replace_all = bool(rng.randrange(2))
        case_sensitive = bool(rng.randrange(2))
        expected = scan_replacement_edits(
            text,
            search,
            value,
            start_index=start,
            replace_all=replace_all,
            literal=True,
            case_sensitive=case_sensitive,
        )
        lines = tuple(text.split("\n"))
        snapshot = QueryReplaceSourceSnapshot.capture(lines)
        for chunk_chars in (1, 2, 3, 7, 16):
            for starts in (None, snapshot.line_starts):
                actual = scan_literal_replacement_edits_lines(
                    lines,
                    search,
                    value,
                    start_index=start,
                    replace_all=replace_all,
                    case_sensitive=case_sensitive,
                    chunk_chars=chunk_chars,
                    line_starts=starts,
                )
                assert _scan_signature(actual) == _scan_signature(expected)


def test_segmented_literal_scan_spans_many_chunks_and_line_breaks() -> None:
    text = "prefix-ABCDEFGHIJ\nKLMNOPQRST-suffix"
    search = "GHIJ\nKLMNOP"
    lines = tuple(text.split("\n"))
    snapshot = QueryReplaceSourceSnapshot.capture(lines)

    expected = scan_replacement_edits(
        text,
        search,
        "X",
        literal=True,
        replace_all=True,
    )
    actual = scan_literal_replacement_edits_lines(
        lines,
        search,
        "X",
        replace_all=True,
        chunk_chars=2,
        line_starts=snapshot.line_starts,
    )

    assert _scan_signature(actual) == _scan_signature(expected)


def test_packed_offsets_are_shared_read_only_coordinate_primitive() -> None:
    offsets = PackedOffsets((0, 4, 9))

    assert SearchPackedOffsets is PackedOffsets
    assert tuple(offsets) == (0, 4, 9)
    assert offsets[1:] == (4, 9)
    assert offsets.storage_bytes == 24
    assert not hasattr(offsets, "append")


def test_segmented_literal_scan_preserves_budget_failures() -> None:
    text = "a\n" * 20
    lines = tuple(text.split("\n"))
    snapshot = QueryReplaceSourceSnapshot.capture(lines)

    for raw_kwargs in (
        {"max_matches": 3},
        {"max_result_bytes": 100},
        {"max_pattern_bytes": 1, "search": "aa"},
    ):
        kwargs = dict(raw_kwargs)
        search = str(kwargs.pop("search", "a"))
        expected = scan_replacement_edits(
            text,
            search,
            "X",
            literal=True,
            replace_all=True,
            **kwargs,
        )
        actual = scan_literal_replacement_edits_lines(
            lines,
            search,
            "X",
            replace_all=True,
            chunk_chars=1,
            line_starts=snapshot.line_starts,
            **kwargs,
        )
        assert _scan_signature(actual) == _scan_signature(expected)


def test_regex_query_replace_retains_only_line_source() -> None:
    editor = Editor()
    editor.new_buffer("*regex-snapshot*", "before\nneedle-42\nafter")

    assert editor.begin_query_replace(r"needle-([0-9]+)", r"value-$1", literal=False)
    assert editor.qreplace is not None
    assert isinstance(editor.qreplace.source_snapshot, QueryReplaceSourceSnapshot)
    assert not hasattr(editor.qreplace, "source_text")
    assert editor.qreplace.match_old == "needle-42"
    assert editor.qreplace.match_repl == "value-42"


def test_regex_query_replace_never_materializes_snapshot_text(
    monkeypatch: object,
) -> None:
    editor = Editor()
    editor.new_buffer("*regex-segmented*", "before\nneedle-42\nafter")

    def forbidden_materialization(self: QueryReplaceSourceSnapshot) -> str:
        raise AssertionError("regex query-replace flattened its source")

    monkeypatch.setattr(  # type: ignore[attr-defined]
        QueryReplaceSourceSnapshot,
        "materialize_text",
        forbidden_materialization,
    )
    assert editor.begin_query_replace(
        r"needle-([0-9]+)",
        r"value-$1",
        literal=False,
    )
    assert editor.qreplace is not None
    assert editor.qreplace.match_old == "needle-42"
    assert editor.qreplace.match_repl == "value-42"


def test_literal_query_replace_never_materializes_snapshot_text(monkeypatch: object) -> None:
    editor = Editor()
    editor.new_buffer("*literal-segmented*", "before\nneedle\nafter")

    def forbidden_materialization(self: QueryReplaceSourceSnapshot) -> str:
        raise AssertionError("literal query-replace flattened its source")

    monkeypatch.setattr(  # type: ignore[attr-defined]
        QueryReplaceSourceSnapshot,
        "materialize_text",
        forbidden_materialization,
    )
    assert editor.begin_query_replace("needle", "X", literal=True)
    assert editor.qreplace is not None
    assert editor.qreplace.match_old == "needle"


def test_stale_boundary_authentication_does_not_call_buffer_get_text() -> None:
    editor = Editor()
    editor.new_buffer("*stale-lines*", "needle then needle")
    eb = editor.cur()
    eb.buf.fastdirty = True
    assert editor.begin_query_replace("needle", "X", literal=True)
    assert editor.qreplace_yes()
    assert editor.qreplace is not None

    eb.buf.insert(Cursor(0, 0), "outside ")

    def forbidden_get_text() -> str:
        raise AssertionError("stale query-replace flattened the live buffer")

    eb.buf.get_text = forbidden_get_text  # type: ignore[method-assign]
    assert editor.qreplace_yes() is False
    assert editor.qreplace is None


def test_qreplace_source_measurement_exposes_retained_shape() -> None:
    module = _load_measurement_tool()
    report = module.build_report(chars=250_000, line_chars=64, samples=1)

    assert report["schema"] == "micromax.qreplace-source-measurement.v1"
    reference = report["rev0996_complete_string_reference"]
    product = report["shallow_line_source_product"]
    comparison = report["comparison"]

    assert comparison["plans_exactly_equal"] is True
    assert comparison["product_avoids_buffer_get_text"] is True
    assert comparison["all_source_line_objects_shared"] is True
    assert reference["retained_complete_source_chars"] == reference["document_chars"]
    assert product["retained_complete_source_chars"] == 0
    assert product["source_coordinate_bytes"] == 8 * product["line_count"]
    assert comparison["retained_complete_source_reduction_percent"] == 100.0
    assert comparison["traced_current_reduction_percent"] > 50
