from __future__ import annotations

from dataclasses import replace
import json
import os
from pathlib import Path
import random
import subprocess
import sys
from typing import Callable

import pytest

from micromax.vm import MicromaxError
from micromax_editor.buffer import Buffer, Cursor
from micromax_editor.editor import Editor, MacroReplaySnapshot
from micromax_editor.micromax_bridge import install_editor_hostcalls
from micromax_editor.undo import UndoSnapshot


ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    "mutate",
    [
        lambda buf: buf.set_text("new\ntext"),
        lambda buf: buf.insert(Cursor(0, 1), "X"),
        lambda buf: buf.delete_range(Cursor(0, 1), Cursor(1, 1)),
        lambda buf: buf.replace_range(Cursor(0, 1), Cursor(1, 1), "Y"),
        lambda buf: buf.replace_lines(("left", "right")),
        lambda buf: buf.delete_line(0),
        lambda buf: buf.duplicate_line(0),
        lambda buf: (buf.lines.__setitem__(slice(None), ["direct"]), buf.touch_external()),
    ],
)
def test_buffer_first_write_observer_precedes_every_owned_mutation(
    mutate: Callable[[Buffer], object],
) -> None:
    buf = Buffer("ab\ncd")
    observed: list[tuple[str, int]] = []

    with buf.observe_before_text_mutation(
        lambda current: observed.append((current.get_text(), int(current.version))),
        once=True,
    ):
        mutate(buf)

    assert observed == [("ab\ncd", 0)]
    assert buf.version == 1


@pytest.mark.parametrize(
    "mutate",
    [
        lambda lines: lines.__setitem__(0, "z"),
        lambda lines: lines.__setitem__(slice(0, 2), ["x", "y"]),
        lambda lines: lines.__delitem__(1),
        lambda lines: lines.insert(1, "x"),
        lambda lines: lines.append("x"),
        lambda lines: lines.extend(["x", "y"]),
        lambda lines: lines.clear(),
        lambda lines: lines.pop(),
        lambda lines: lines.remove("a"),
        lambda lines: lines.reverse(),
        lambda lines: lines.sort(),
        lambda lines: lines.__iadd__(["x"]),
        lambda lines: lines.__imul__(2),
    ],
)
def test_observed_line_view_announces_each_mutating_surface(
    mutate: Callable[[object], object],
) -> None:
    buf = Buffer("b\na\nc")
    observed: list[str] = []

    with buf.observe_before_text_mutation(
        lambda current: observed.append(current.get_text()),
        once=True,
    ):
        view = buf.lines
        mutate(view)

    assert observed == ["b\na\nc"]


@pytest.mark.parametrize("operation", ["delete", "duplicate"])
def test_defensive_empty_line_vector_is_observed_before_canonicalization(
    operation: str,
) -> None:
    buf = Buffer("seed")
    buf.lines.clear()
    observed: list[str] = []

    with buf.observe_before_text_mutation(
        lambda current: observed.append(current.get_text()),
        once=True,
    ):
        if operation == "delete":
            buf.delete_line(0)
        else:
            buf.duplicate_line(0)

    assert observed == [""]
    assert buf.version == 1


def test_buffer_keeps_raw_list_off_transaction_and_one_shot_observer_disarms() -> None:
    buf = Buffer("ab\ncd")
    assert type(buf.lines) is list
    observed: list[str] = []

    with buf.observe_before_text_mutation(
        lambda current: observed.append(current.get_text()),
        once=True,
    ):
        assert type(buf.lines) is not list
        buf.insert(Cursor(0, 1), "X")
        assert type(buf.lines) is list
        buf.insert(Cursor(0, 2), "Y")

    assert observed == ["ab\ncd"]
    assert buf.get_text() == "aXYb\ncd"


def test_failed_first_write_capture_blocks_mutation_and_remains_armed() -> None:
    buf = Buffer("alpha")
    attempts = 0
    captured: list[str] = []

    def capture(current: Buffer) -> None:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise RuntimeError("capture failed")
        captured.append(current.get_text())

    with buf.observe_before_text_mutation(capture, once=True):
        with pytest.raises(RuntimeError, match="capture failed"):
            buf.insert(Cursor(0, 0), "X")
        assert buf.get_text() == "alpha"
        assert buf.version == 0
        buf.insert(Cursor(0, 0), "Y")
        buf.insert(Cursor(0, 1), "Z")

    assert attempts == 2
    assert captured == ["alpha"]
    assert buf.get_text() == "YZalpha"
    assert buf.version == 2


def test_with_undo_never_joins_untouched_open_buffers(monkeypatch) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    source = ("payload-" * 40 + "\n") * 2_000
    ed.new_buffer("active", source)
    ed.new_buffer("cold-a", source.replace("p", "q"))
    ed.new_buffer("cold-b", source.replace("p", "r"))
    ed.new_buffer("cold-c", source.replace("p", "s"))
    assert ed.switch_buffer("active") is True

    def forbidden_join() -> str:
        raise AssertionError("untouched transaction buffer text was joined")

    for name in ("cold-a", "cold-b", "cold-c"):
        monkeypatch.setattr(ed.buffers[name].buf, "get_text", forbidden_join)

    ed.vm.eval(
        '"first-write" [ "X" "ed.insert" hostcall ] "ed.with-undo" hostcall',
        filename="<test>",
    )

    row = ed.undo.peek_undo()
    assert row is not None
    assert row.description == "first-write"
    assert [charge.owner for charge in row.retained_text] == [ed.buffers["active"]]
    assert ed.buffers["active"].buf.get_text() == "X" + source

    assert ed.undo.undo() is True
    assert ed.buffers["active"].buf.get_text() == source
    assert ed.undo.redo() is True
    assert ed.buffers["active"].buf.get_text() == "X" + source


def test_mark_only_with_undo_joins_no_buffer_text(monkeypatch) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("a", "alpha\nbeta")
    ed.new_buffer("b", "one\ntwo")
    assert ed.switch_buffer("a") is True

    def forbidden_join() -> str:
        raise AssertionError("mark-only transaction joined buffer text")

    for eb in ed.buffers.values():
        monkeypatch.setattr(eb.buf, "get_text", forbidden_join)

    ed.vm.eval(
        '"mark-only" [ "new" "ed.mark-set" hostcall drop ] "ed.with-undo" hostcall',
        filename="<test>",
    )

    row = ed.undo.peek_undo()
    assert row is not None
    assert row.retained_text == ()
    assert "new" in ed.marks
    assert ed.undo.undo() is True
    assert "new" not in ed.marks
    assert ed.undo.redo() is True
    assert "new" in ed.marks


def _without_history(snapshot: MacroReplaySnapshot) -> MacroReplaySnapshot:
    # Independent differential editors intentionally own distinct recovery IDs.
    # Normalize the random identity token while retaining every observable text,
    # option, cursor, dirty, and transaction field in the oracle comparison.
    return replace(
        snapshot,
        buffers=tuple(
            replace(row, save_recovery_id="<normalized>")
            for row in snapshot.buffers
        ),
        undo=UndoSnapshot(undo=(), redo=(), suppress=0),
    )


def _state(ed: Editor) -> MacroReplaySnapshot:
    return _without_history(ed._buffer_transaction_snapshot())


def _record_eager_transaction(
    ed: Editor,
    operation: Callable[[Editor], None],
    *,
    description: str,
) -> None:
    before = ed._buffer_transaction_snapshot()
    try:
        with ed.undo.suppress_recording():
            operation(ed)
    except Exception:
        ed._restore_macro_replay_snapshot(before)
        raise
    after = ed._buffer_transaction_snapshot(reuse_unchanged_text_from=before)
    if ed._buffer_transaction_changed(before, after):
        ed._record_buffer_transaction_snapshot(before, after, description)


def _record_first_write_transaction(
    ed: Editor,
    operation: Callable[[Editor], None],
    *,
    description: str,
) -> None:
    journal = None
    try:
        with ed._first_write_buffer_transaction() as journal:
            with ed.undo.suppress_recording():
                operation(ed)
    except Exception:
        assert journal is not None
        ed._restore_macro_replay_snapshot(
            ed._first_write_transaction_rollback_snapshot(journal)
        )
        raise
    assert journal is not None
    before, after = ed._finish_first_write_buffer_transaction(journal)
    if ed._buffer_transaction_changed(before, after):
        ed._record_buffer_transaction_snapshot(before, after, description)


def _seeded_operation(seed: int) -> Callable[[Editor], None]:
    def operation(ed: Editor) -> None:
        rng = random.Random(seed)
        for step in range(12):
            choice = rng.randrange(8)
            if choice == 0:
                names = sorted(ed.buffers)
                assert ed.switch_buffer(names[rng.randrange(len(names))]) is True
                continue
            if choice == 1:
                eb = ed.cur()
                line = rng.randrange(len(eb.buf.lines))
                col = rng.randrange(len(eb.buf.lines[line]) + 1)
                eb.cursors[eb.primary] = Cursor(line, col)
                continue
            if choice == 2:
                ed.input["text"] = chr(ord("a") + ((seed + step) % 26))
                ed.run_action("InsertText")
                continue
            if choice == 3:
                ed.input["text"] = "\n"
                ed.run_action("InsertText")
                continue
            if choice == 4:
                ed.run_action("Delete")
                continue
            if choice == 5:
                ed.run_action("DuplicateLine")
                continue
            if choice == 6:
                ed.mark_set(f"m{step % 3}")
                continue
            if "scratch" in ed.buffers:
                ed.close_buffer("scratch", force=True)
            else:
                ed.new_buffer("scratch", f"scratch-{seed}-{step}\n")

    return operation


def _editor_for_differential() -> Editor:
    ed = Editor()
    ed.new_buffer("a", "alpha\nbeta\ngamma")
    ed.new_buffer("b", "one\ntwo\nthree")
    ed.new_buffer("c", "red\ngreen\nblue")
    assert ed.switch_buffer("a") is True
    ed.input["text"] = "P"
    assert ed.run_action("InsertText") is True
    return ed


def _retained_shape(ed: Editor) -> tuple[tuple[str, int], ...]:
    row = ed.undo.peek_undo()
    assert row is not None
    return tuple((charge.label, int(charge.byte_count)) for charge in row.retained_text)


@pytest.mark.parametrize("seed", range(40))
def test_first_write_success_matches_broad_snapshot_oracle(seed: int) -> None:
    eager = _editor_for_differential()
    lazy = _editor_for_differential()
    operation = _seeded_operation(seed)

    _record_eager_transaction(eager, operation, description=f"seed {seed}")
    _record_first_write_transaction(lazy, operation, description=f"seed {seed}")

    assert _state(lazy) == _state(eager)
    assert lazy.undo.depth() == eager.undo.depth()
    lazy_retained = _retained_shape(lazy)
    eager_retained = _retained_shape(eager)
    assert tuple(label for label, _ in lazy_retained) == tuple(
        label for label, _ in eager_retained
    )
    assert all(
        lazy_bytes <= eager_bytes
        for (_label, lazy_bytes), (_other, eager_bytes) in zip(
            lazy_retained, eager_retained, strict=True
        )
    )

    assert lazy.undo.undo() is eager.undo.undo() is True
    assert _state(lazy) == _state(eager)
    assert lazy.undo.redo() is eager.undo.redo() is True
    assert _state(lazy) == _state(eager)


@pytest.mark.parametrize("seed", range(20))
def test_first_write_failure_matches_broad_snapshot_oracle(seed: int) -> None:
    eager = _editor_for_differential()
    lazy = _editor_for_differential()
    initial = _state(eager)
    operation = _seeded_operation(seed)

    def fail_after(editor: Editor) -> None:
        operation(editor)
        raise RuntimeError("stop")

    with pytest.raises(RuntimeError, match="stop"):
        _record_eager_transaction(eager, fail_after, description="never")
    with pytest.raises(RuntimeError, match="stop"):
        _record_first_write_transaction(lazy, fail_after, description="never")

    assert _state(eager) == initial
    assert _state(lazy) == initial
    assert lazy.undo.depth() == eager.undo.depth() == 1


def test_direct_line_view_mutation_without_touch_is_still_transactional() -> None:
    ed = Editor()
    ed.new_buffer("main", "alpha\nbeta")

    _record_first_write_transaction(
        ed,
        lambda current: current.cur().buf.lines.__setitem__(slice(None), ["direct"]),
        description="direct",
    )

    assert ed.cur().buf.get_text() == "direct"
    assert ed.undo.undo() is True
    assert ed.cur().buf.get_text() == "alpha\nbeta"
    assert ed.undo.redo() is True
    assert ed.cur().buf.get_text() == "direct"


def test_nested_with_undo_has_one_outer_row_and_exact_replay() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("main", "seed")

    ed.vm.eval(
        '"outer" [ '
        '"inner" [ "A" "ed.insert" hostcall ] "ed.with-undo" hostcall drop '
        '"B" "ed.insert" hostcall '
        '] "ed.with-undo" hostcall',
        filename="<test>",
    )

    assert ed.cur().buf.get_text() == "ABseed"
    assert ed.undo.depth() == 1
    row = ed.undo.peek_undo()
    assert row is not None and row.description == "outer"
    assert ed.undo.undo() is True
    assert ed.cur().buf.get_text() == "seed"
    assert ed.undo.redo() is True
    assert ed.cur().buf.get_text() == "ABseed"


def test_with_undo_failure_restores_first_write_text_and_vm_stack() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    source = ("0123456789\n" * 20_000).rstrip("\n")
    ed.new_buffer("main", source)
    before_version = ed.cur().buf.version

    with pytest.raises(MicromaxError):
        ed.vm.eval(
            '"rollback" [ "X" "ed.insert" hostcall nope ] "ed.with-undo" hostcall',
            filename="<test>",
        )

    assert ed.cur().buf.get_text() == source
    assert ed.cur().buf.version == before_version
    assert ed.cur().buf.dirty is False
    assert ed.undo.depth() == 0
    assert ed.vm.stack == []


def test_with_undo_record_failure_rolls_back_editor_history_and_vm_stack(monkeypatch) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("main", "seed")
    ed.input["text"] = "P"
    assert ed.run_action("InsertText") is True
    before = _state(ed)
    before_depth = ed.undo.depth()
    original = ed._record_buffer_transaction_snapshot

    def record_then_fail(*args: object, **kwargs: object) -> None:
        original(*args, **kwargs)  # type: ignore[arg-type]
        raise RuntimeError("record failed")

    monkeypatch.setattr(ed, "_record_buffer_transaction_snapshot", record_then_fail)

    with pytest.raises(MicromaxError, match="record failed"):
        ed.vm.eval(
            '"atomic finalization" [ "X" "ed.insert" hostcall ] '
            '"ed.with-undo" hostcall',
            filename="<test>",
        )

    assert _state(ed) == before
    assert ed.undo.depth() == before_depth
    assert ed.vm.stack == []


def test_first_write_measurement_compares_product_and_eager_capture() -> None:
    env = dict(os.environ)
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(ROOT / "src") + (os.pathsep + existing if existing else "")
    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / "tools" / "measure_first_write_transactions.py"),
            "--chars",
            "200000",
            "--buffers",
            "4",
            "--samples",
            "1",
            "--mutation-cycles",
            "5000",
            "--mutation-samples",
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
    assert payload["schema"] == "micromax.first-write-transaction-witness.v2"
    success_reference = payload["success"]["eager_snapshot_reference"]
    success_product = payload["success"]["first_write_product"]
    failure_reference = payload["failure"]["eager_snapshot_reference"]
    failure_product = payload["failure"]["first_write_product"]

    document_chars = success_product["document_chars_per_buffer"]
    assert success_reference["joined_text_calls"] == 5
    assert success_product["joined_text_calls"] == 0
    assert success_reference["joined_text_chars"] == document_chars * 5 + 1
    assert success_product["joined_text_chars"] == 0
    assert success_reference["old_content_capture_rows"] == 4
    assert success_product["old_content_capture_rows"] == 1
    assert success_reference["accounted_retained_text_bytes"] == document_chars * 2 + 1
    assert 0 < success_product["accounted_retained_text_bytes"]
    assert (
        success_product["accounted_retained_text_bytes"]
        < success_reference["accounted_retained_text_bytes"]
    )
    assert success_reference["capture_representation"] == "joined-text"
    assert success_product["capture_representation"] == "line-vector"
    assert success_product["traced_peak_bytes_median"] < success_reference["traced_peak_bytes_median"]

    assert failure_reference["joined_text_calls"] == 4
    assert failure_product["joined_text_calls"] == 0
    assert failure_reference["joined_text_chars"] == document_chars * 4
    assert failure_product["joined_text_chars"] == 0
    assert failure_reference["old_content_capture_rows"] == 4
    assert failure_product["old_content_capture_rows"] == 1
    assert failure_product["traced_peak_bytes_median"] < failure_reference["traced_peak_bytes_median"]

    for case in (success_reference, success_product, failure_reference, failure_product):
        assert case["forward_or_rollback_exact"] is True
        assert case["undo_exact"] is True
        assert case["redo_exact"] is True
    hotpath = payload["ordinary_mutation_hotpath"]
    assert hotpath["cycles"] == 5000
    assert hotpath["mutations_per_cycle"] == 2
    assert hotpath["product_to_control_ratio"] > 0
