from __future__ import annotations

import json
import os
import random
import subprocess
import sys
from pathlib import Path
from unittest import mock

from micromax_editor.buffer import Cursor
from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls
from micromax_editor.recovery_journal import RecoveryJournal
from micromax_editor.screen_consumer import validate_screen_contract_v1
from micromax_editor.simultaneous_edits import (
    SimultaneousEditWitness,
    SimultaneousTextEdit,
    line_start_offsets,
    offset_to_cursor,
    plan_simultaneous_edits,
    replay_simultaneous_edit_witness,
)


ROOT = Path(__file__).resolve().parents[1]


def _install_cursors(
    ed: Editor,
    cursors: list[Cursor],
    anchors: list[Cursor | None] | None = None,
) -> None:
    eb = ed.cur()
    eb.cursors[:] = list(cursors)
    eb.sel_anchors[:] = (
        [None for _cursor in cursors] if anchors is None else list(anchors)
    )
    eb.cursor_ids[:] = list(range(1, len(cursors) + 1))
    eb.primary = 0
    ed._normalize_cursor_lists(eb)


def _history_witness(editor: Editor) -> SimultaneousEditWitness:
    edit = editor.undo.peek_undo()
    assert edit is not None
    found: list[SimultaneousEditWitness] = []
    for callback in (edit.undo, edit.redo):
        for cell in callback.__closure__ or ():
            value = cell.cell_contents
            if isinstance(value, SimultaneousEditWitness):
                found.append(value)
    assert found
    assert all(value is found[0] for value in found)
    return found[0]


def test_sparse_witness_roundtrips_seeded_nonoverlapping_edit_plans() -> None:
    rng = random.Random(985)
    alphabet = "ab Ω\n"
    replacement_alphabet = "XY λ\n"

    for _case in range(1_000):
        source = "".join(rng.choice(alphabet) for _ in range(rng.randrange(0, 80)))
        starts = line_start_offsets(source)
        flat: list[tuple[int, int, str]] = []
        source_at = 0
        while source_at <= len(source) and len(flat) < 10:
            source_at += rng.randrange(0, 6)
            if source_at > len(source):
                break
            end = min(len(source), source_at + rng.randrange(0, 6))
            replacement = "".join(
                rng.choice(replacement_alphabet)
                for _ in range(rng.randrange(0, 6))
            )
            flat.append((source_at, end, replacement))
            # Force distinct starts while still allowing adjacent ranges.
            source_at = max(source_at + 1, end)

        requests = [
            SimultaneousTextEdit(
                offset_to_cursor(source, starts, start),
                offset_to_cursor(source, starts, end),
                replacement,
                owner=index,
            )
            for index, (start, end, replacement) in enumerate(flat)
        ]
        plan = plan_simultaneous_edits(source, requests, source_starts=starts)
        witness = plan.compact_history_witness()

        assert replay_simultaneous_edit_witness(
            plan.original_text, witness, undo=False
        ) == plan.new_text
        assert replay_simultaneous_edit_witness(
            plan.new_text, witness, undo=True
        ) == plan.original_text


def test_adjacent_delete_witness_replays_same_offset_inverse_in_source_order() -> None:
    plan = plan_simultaneous_edits(
        "abcd",
        [
            SimultaneousTextEdit(Cursor(0, 1), Cursor(0, 2), "", owner=0),
            SimultaneousTextEdit(Cursor(0, 2), Cursor(0, 3), "", owner=1),
        ],
    )
    witness = plan.compact_history_witness()

    assert plan.new_text == "ad"
    assert [(row.new_start, row.new_end) for row in witness.splices] == [(1, 1), (1, 1)]
    assert replay_simultaneous_edit_witness("ad", witness, undo=True) == "abcd"
    assert replay_simultaneous_edit_witness("abcd", witness, undo=False) == "ad"


def test_sparse_replay_preserves_unrelated_text_after_all_targets() -> None:
    source = "abcdef"
    plan = plan_simultaneous_edits(
        source,
        [
            SimultaneousTextEdit(Cursor(0, 1), Cursor(0, 1), "X", owner=0),
            SimultaneousTextEdit(Cursor(0, 4), Cursor(0, 4), "Y", owner=1),
        ],
    )
    witness = plan.compact_history_witness()

    assert replay_simultaneous_edit_witness(
        source + "!", witness, undo=False
    ) == plan.new_text + "!"
    assert replay_simultaneous_edit_witness(
        plan.new_text + "!", witness, undo=True
    ) == source + "!"


def test_adjacent_multicursor_backspaces_are_one_exact_compact_history_row() -> None:
    ed = Editor()
    ed.new_buffer("adjacent", "abcd")
    _install_cursors(ed, [Cursor(0, 2), Cursor(0, 3)])
    eb = ed.cur()

    assert ed.run_action("Backspace") is True
    assert eb.buf.get_text() == "ad"
    assert ed.undo.depth() == 1
    assert ed.undo.retained_text_bytes(eb) == 2

    witness = _history_witness(ed)
    assert [(row.old_text, row.new_text) for row in witness.splices] == [
        ("b", ""),
        ("c", ""),
    ]

    assert ed.undo_feedback() is True
    assert eb.buf.get_text() == "abcd"
    assert eb.cursors == [Cursor(0, 2), Cursor(0, 3)]
    assert ed.redo_feedback() is True
    assert eb.buf.get_text() == "ad"


def test_sparse_group_undo_validates_every_target_before_mutating_any_target() -> None:
    ed = Editor()
    source = "abcdefghi"
    ed.new_buffer("atomic", source)
    _install_cursors(ed, [Cursor(0, 1), Cursor(0, 7)])
    eb = ed.cur()

    ed.input["text"] = "X"
    assert ed.run_action("InsertText") is True
    assert eb.buf.get_text() == "aXbcdefgXhi"
    assert ed.undo.depth() == 1

    # Corrupt only the later inverse target outside editor history.  A replay
    # implementation that mutates while validating would already delete the
    # first X before discovering this mismatch.
    eb.buf.replace_range(Cursor(0, 8), Cursor(0, 9), "Q")
    assert eb.buf.get_text() == "aXbcdefgQhi"

    assert ed.undo_feedback() is False
    assert eb.buf.get_text() == "aXbcdefgQhi"
    assert ed.undo.depth() == 1
    assert ed.undo.redo_depth() == 0
    assert ed.messages[-1].startswith("undo: refused stale edit (")

    # The retained row remains useful after the exact target is repaired.
    eb.buf.replace_range(Cursor(0, 8), Cursor(0, 9), "X")
    assert ed.undo_feedback() is True
    assert eb.buf.get_text() == source


def test_sparse_group_redo_validates_every_target_before_mutating_any_target() -> None:
    ed = Editor()
    source = "abcdefghi"
    ed.new_buffer("atomic-redo", source)
    _install_cursors(
        ed,
        [Cursor(0, 2), Cursor(0, 8)],
        [Cursor(0, 1), Cursor(0, 7)],
    )
    eb = ed.cur()

    ed.input["text"] = "X"
    assert ed.run_action("InsertText") is True
    assert eb.buf.get_text() == "aXcdefgXi"
    assert ed.undo_feedback() is True
    assert eb.buf.get_text() == source
    assert ed.undo.depth() == 0
    assert ed.undo.redo_depth() == 1

    # Corrupt only the later forward target.  Redo must not replace the first target
    # before discovering that the second expected old slice is stale.
    eb.buf.replace_range(Cursor(0, 7), Cursor(0, 8), "Q")
    assert eb.buf.get_text() == "abcdefgQi"

    assert ed.redo_feedback() is False
    assert eb.buf.get_text() == "abcdefgQi"
    assert ed.undo.depth() == 0
    assert ed.undo.redo_depth() == 1
    assert ed.messages[-1].startswith("redo: refused stale edit (")

    eb.buf.replace_range(Cursor(0, 7), Cursor(0, 8), "h")
    assert ed.redo_feedback() is True
    assert eb.buf.get_text() == "aXcdefgXi"


def test_large_sparse_multicursor_paste_retains_only_inserted_slices() -> None:
    source = "a" * 1_100_000
    first = 101
    second = 1_000_003
    ed = Editor()
    ed.new_buffer("large", source)
    _install_cursors(ed, [Cursor(0, first), Cursor(0, second)])
    eb = ed.cur()
    ed.set_clipboard_items(["X", "YZ"], kind="items")

    assert ed.run_action("Paste") is True
    expected = (
        source[:first]
        + "X"
        + source[first:second]
        + "YZ"
        + source[second:]
    )
    assert eb.buf.get_text() == expected
    assert ed.undo.depth() == 1
    assert ed.undo.retained_text_bytes(eb) == 3

    witness = _history_witness(ed)
    assert len(witness.splices) == 2
    assert [(row.old_text, row.new_text) for row in witness.splices] == [
        ("", "X"),
        ("", "YZ"),
    ]
    assert max(
        len(text)
        for row in witness.splices
        for text in (row.old_text, row.new_text)
    ) == 2

    assert ed.undo_feedback() is True
    assert eb.buf.get_text() == source
    assert ed.redo_feedback() is True
    assert eb.buf.get_text() == expected


def test_equal_multicursor_replacements_record_zero_text_sidecar_history() -> None:
    ed = Editor()
    ed.new_buffer("sidecars", "foo foo")
    _install_cursors(
        ed,
        [Cursor(0, 3), Cursor(0, 7)],
        [Cursor(0, 0), Cursor(0, 4)],
    )
    eb = ed.cur()
    version_before = int(eb.buf.version)

    ed.input["text"] = "foo"
    assert ed.run_action("InsertText") is True
    assert eb.buf.get_text() == "foo foo"
    assert int(eb.buf.version) == version_before
    assert eb.sel_anchors == [None, None]
    assert ed.undo.retained_text_bytes(eb) == 0
    assert _history_witness(ed).splices == ()

    assert ed.undo_feedback() is True
    assert eb.sel_anchors == [Cursor(0, 0), Cursor(0, 4)]
    assert int(eb.buf.version) == version_before
    assert ed.redo_feedback() is True
    assert eb.sel_anchors == [None, None]
    assert int(eb.buf.version) == version_before


def test_suppressed_cursor_edits_skip_redundant_local_snapshot_helpers(
    monkeypatch,
) -> None:
    source = "a" * 600_000
    ed = Editor()
    ed.new_buffer("aggregate", source)
    _install_cursors(ed, [Cursor(0, 10), Cursor(0, 500_000)])
    eb = ed.cur()
    snapshot_calls = 0
    original_snapshot = ed._snapshot_undo_buffer_state

    def counted_snapshot(target):
        nonlocal snapshot_calls
        snapshot_calls += 1
        return original_snapshot(target)

    monkeypatch.setattr(ed, "_snapshot_undo_buffer_state", counted_snapshot)
    with ed.undo.suppress_recording():
        for char in "XYZ":
            ed.input["text"] = char
            assert ed.run_action("InsertText") is True

    assert snapshot_calls == 0
    assert ed.undo.depth() == 0
    assert eb.buf.get_text() == (
        source[:10]
        + "XYZ"
        + source[10:500_000]
        + "XYZ"
        + source[500_000:]
    )


def test_suppressed_direct_edit_still_finalizes_live_qreplace_boundary() -> None:
    """The suppression fast path must not bypass qreplace session ownership."""

    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("qreplace-owner", "one one")
    eb = ed.cur()

    assert ed.begin_query_replace("one", "X", literal=True) is True
    assert ed.qreplace_yes() is True
    assert eb.buf.get_text() == "X one"
    assert ed.qreplace is not None

    # Direct hostcalls finalize qreplace post-hoc through the broad fallback.
    # ed.with-undo and eligible macro replay suppress their local rows while an
    # outer transaction remains responsible for rollback and aggregate undo.
    with ed.undo.suppress_recording():
        ed.vm.stack.extend([0, len("X one"), 0, len("X one"), "!", "ed.replace-range"])
        ed.vm.eval("hostcall")
        assert ed.vm.pop_int() == len("X one!")
        assert ed.vm.pop_int() == 0

    assert eb.buf.get_text() == "X one!"
    assert ed.qreplace is None
    assert ed.current_capture_key_mode() is None
    assert ed.undo.depth() == 0


def test_cut_and_replace_selections_share_sparse_undo_seam(monkeypatch) -> None:
    def no_broad_snapshot(_eb):
        raise AssertionError("immediate simultaneous edit used a broad snapshot")

    source = "AA" + ("x" * 250_000) + "BB"
    ed = Editor()
    ed.new_buffer("cut", source)
    _install_cursors(
        ed,
        [Cursor(0, 2), Cursor(0, len(source))],
        [Cursor(0, 0), Cursor(0, len(source) - 2)],
    )
    eb = ed.cur()
    monkeypatch.setattr(ed, "_snapshot_undo_buffer_state", no_broad_snapshot)

    assert ed.run_action("Cut") is True
    assert eb.buf.get_text() == "x" * 250_000
    assert ed.clipboard_items == ["AA", "BB"]
    assert ed.undo.retained_text_bytes(eb) == 4
    assert ed.undo_feedback() is True
    assert eb.buf.get_text() == source

    host = Editor()
    install_editor_hostcalls(host)
    host.new_buffer("host", "foo foo")
    _install_cursors(
        host,
        [Cursor(0, 3), Cursor(0, 7)],
        [Cursor(0, 0), Cursor(0, 4)],
    )
    host_eb = host.cur()
    monkeypatch.setattr(host, "_snapshot_undo_buffer_state", no_broad_snapshot)
    host.vm.stack.extend([["A", "BBBB"], "ed.replace-selections"])

    host.vm.eval("hostcall")
    assert host.vm.pop_int() == 1
    assert host.vm.pop_int() == 0
    assert host_eb.buf.get_text() == "A BBBB"
    assert host.undo.retained_text_bytes(host_eb) == len("foo") * 2 + len("A") + len("BBBB")
    assert host.undo_feedback() is True
    assert host_eb.buf.get_text() == "foo foo"


def test_bounded_large_history_journey_crosses_edit_search_render_save_and_cancel(
    tmp_path: Path,
) -> None:
    """One product-level witness for the retention work, not a microbenchmark."""

    path = tmp_path / "history-journey.txt"
    source = "one BEGIN " + ("x" * 350_000) + " one END\n"
    path.write_text(source, encoding="utf-8")

    journal = RecoveryJournal(tmp_path / "recovery")
    ed = Editor()
    ed.configure_recovery_journal(journal)
    ed.new_buffer(str(path), source, path=str(path))
    eb = ed.cur()
    second_one = source.rfind("one")
    _install_cursors(ed, [Cursor(0, 0), Cursor(0, second_one)])
    ed.set_clipboard_items(["ONE", "TWO"], kind="items")

    assert ed.run_action("Paste") is True
    pasted = "ONE" + source[:second_one] + "TWO" + source[second_one:]
    assert eb.buf.get_text() == pasted
    sparse_charge = ed.undo.retained_text_bytes(eb)
    assert sparse_charge == 6

    contract = ed.screen_contract(8, 64)
    assert validate_screen_contract_v1(contract) == contract
    assert any(row["kind"] == "viewport" and row["text"] for row in contract["rows"])

    # Enter and then cancel a search/replace interaction without changing text.
    assert ed.begin_query_replace("BEGIN", "START", literal=True) is True
    assert ed.qreplace_quit() is True
    assert eb.buf.get_text() == pasted
    assert ed.undo.retained_text_bytes(eb) == sparse_charge

    ed.save()
    assert path.read_text(encoding="utf-8") == pasted
    assert eb.buf.dirty is False

    assert ed.undo_feedback() is True
    assert eb.buf.get_text() == source
    assert eb.buf.dirty is True
    assert ed.redo_feedback() is True
    assert eb.buf.get_text() == pasted
    assert eb.buf.dirty is False

    # The same lived loop crosses an interrupted explicit save and restart
    # recovery.  The journal must own the exact post-history editor text while
    # disk remains at the last successful generation.
    _install_cursors(ed, [Cursor(0, 3)])
    ed.input["text"] = "!"
    assert ed.run_action("InsertText") is True
    failed_text = pasted[:3] + "!" + pasted[3:]
    assert eb.buf.get_text() == failed_text
    with mock.patch(
        "micromax_editor.editor.write_file_bytes",
        side_effect=OSError("simulated disk full"),
    ):
        assert ed.exec_command_line("save") is False

    assert path.read_text(encoding="utf-8") == pasted
    [candidate] = journal.discover()
    assert journal.load(candidate.entry_id).editor_text() == failed_text

    restarted = Editor()
    restarted.configure_recovery_journal(journal)
    restarted.new_buffer("*restart*", "")
    assert restarted.exec_command_line("recover #1") is True
    assert restarted.cur().buf.get_text() == failed_text
    assert restarted.cur().buf.dirty is True
    assert path.read_text(encoding="utf-8") == pasted
    assert restarted.exec_command_line("save") is True
    assert path.read_text(encoding="utf-8") == failed_text
    assert journal.discover() == []


def test_simultaneous_history_measurement_compares_product_and_rev0984_shapes() -> None:
    env = dict(os.environ)
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(ROOT / "src") + (os.pathsep + existing if existing else "")
    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / "tools" / "measure_simultaneous_history.py"),
            "--chars",
            "400000",
            "--cursors",
            "4",
            "--edits",
            "5",
            "--samples",
            "1",
        ],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
        timeout=60,
    )

    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["schema"] == "micromax.simultaneous-history-retention-witness.v1"
    compact = payload["sparse_simultaneous_history"]
    reference = payload["rev0984_snapshot_reference"]
    comparison = payload["comparison"]
    suppressed = payload["suppressed_aggregate_owner"]

    assert compact["undo_exact"] is True
    assert compact["redo_exact"] is True
    assert reference["undo_exact"] is True
    assert reference["redo_exact"] is True
    assert compact["simultaneous_witness_splices"] == 20
    assert compact["max_callback_string_chars"] <= 7
    assert reference["max_callback_string_chars"] >= 400_000
    assert comparison["accounted_retained_text_reduction_percent"] > 99
    assert comparison["traced_current_reduction_percent"] > 50
    assert suppressed["local_snapshot_helper_calls"] == 0
    assert suppressed["rev0984_reference_local_snapshot_helper_calls"] == 10
    assert suppressed["undo_rows_recorded_inside_owner"] == 0
    assert suppressed["text_changed"] is True
