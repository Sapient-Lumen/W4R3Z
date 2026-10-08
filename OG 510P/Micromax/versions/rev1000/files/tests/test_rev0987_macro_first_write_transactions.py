from __future__ import annotations

import json
import os
import random
import subprocess
import sys
from contextlib import ExitStack
from dataclasses import replace
from pathlib import Path

import pytest

from micromax_editor.editor import Editor, MacroReplaySnapshot, MacroStep
from micromax_editor.micromax_bridge import install_editor_hostcalls
from micromax_editor.undo import UndoSnapshot

ROOT = Path(__file__).resolve().parents[1]


def _action(name: str, *, text: str | None = None) -> MacroStep:
    payload: dict[str, object] = {"input": {}}
    if text is not None:
        payload = {"input": {"text": str(text)}}
    return MacroStep(kind="action", name=str(name), payload=payload)


def _command(command: str) -> MacroStep:
    return MacroStep(
        kind="command",
        name="command",
        payload={"cmdline": str(command)},
    )


def _without_history(snapshot: MacroReplaySnapshot) -> MacroReplaySnapshot:
    # Differential editors intentionally own distinct recovery identities.
    # Normalize that nondeterministic authority token while comparing all
    # observable content, policy, cursor, and history state.  Rev0993 added the
    # token to aggregate snapshots; leaving it raw turned every oracle pair into
    # a false failure even when both implementations behaved identically.
    return replace(
        snapshot,
        buffers=tuple(
            replace(row, save_recovery_id="<normalized>")
            for row in snapshot.buffers
        ),
        undo=UndoSnapshot(undo=(), redo=(), suppress=0),
    )


def _state(editor: Editor) -> MacroReplaySnapshot:
    return _without_history(editor._buffer_transaction_snapshot())


def _retained_shape(editor: Editor) -> tuple[tuple[str, int], ...]:
    row = editor.undo.peek_undo()
    assert row is not None
    return tuple((charge.label, int(charge.byte_count)) for charge in row.retained_text)


def _play_macro_eager_oracle(
    editor: Editor,
    steps: list[MacroStep],
    *,
    name: str = "oracle",
    count: int = 1,
) -> bool:
    """Execute the pre-rev0987 eager macro transaction in the current runtime."""

    snapshot = editor._macro_replay_snapshot()
    suppress_step_undo = editor._macro_replay_can_suppress_step_undo(steps)
    editor._macro_playing = True
    editor._macro_play_name = str(name)
    editor._macro_play_steps = len(steps)
    replay_step_index = 0
    try:
        with ExitStack() as stack:
            if suppress_step_undo:
                stack.enter_context(editor.undo.suppress_recording())
            for _ in range(max(1, int(count))):
                for step in steps:
                    replay_step_index += 1
                    ok = False
                    detail = ""
                    try:
                        ok = bool(editor._execute_macro_replay_step(step))
                    except Exception as exc:
                        detail = editor._macro_replay_step_error_detail(step, exc)
                    if not ok:
                        if not detail:
                            detail = editor._macro_replay_step_failure_detail(step)
                        editor._restore_macro_replay_snapshot(snapshot)
                        editor.message(
                            f"macro: aborted at step {replay_step_index}: {detail}"
                        )
                        return False

        try:
            after = editor._macro_replay_snapshot(
                reuse_unchanged_text_from=snapshot,
            )
            editor.undo.restore(snapshot.undo)
            if editor._macro_replay_has_undoable_change(snapshot, after):
                editor._record_buffer_transaction_snapshot(
                    snapshot,
                    after,
                    f"macro {name} x{count}",
                )
        except Exception as exc:
            editor._restore_macro_replay_snapshot(snapshot)
            editor.message(f"macro: aborted during transaction finalization: {exc}")
            return False
    finally:
        editor._macro_playing = False
        editor._macro_play_name = ""
        editor._macro_play_steps = 0
        editor.input = dict(snapshot.input)
    step_word = "step" if len(steps) == 1 else "steps"
    editor.message(f"macro: played {name} x{count} ({len(steps)} {step_word})")
    return True


def _editor_for_differential() -> Editor:
    editor = Editor()
    editor.options.set("undobytes", "0")
    editor.new_buffer("a", "alpha\nbeta\ngamma")
    editor.new_buffer("b", "one\ntwo\nthree")
    assert editor.switch_buffer("a") is True
    editor.input["text"] = "P"
    assert editor.run_action("InsertText") is True
    return editor


def _seeded_steps(seed: int) -> list[MacroStep]:
    rng = random.Random(seed)
    steps: list[MacroStep] = [_action("InsertText", text=chr(65 + seed % 26))]
    for index in range(11):
        choice = rng.randrange(8)
        if choice == 0:
            steps.append(_action("InsertText", text=chr(97 + (seed + index) % 26)))
        elif choice == 1:
            steps.append(_action("InsertNewline"))
        elif choice == 2:
            steps.append(_action("CursorLeft"))
        elif choice == 3:
            steps.append(_action("CursorRight"))
        elif choice == 4:
            steps.append(_action("StartOfLine"))
        elif choice == 5:
            steps.append(_action("EndOfLine"))
        elif choice == 6:
            steps.append(_action("DuplicateLine"))
        else:
            steps.append(_command("buffer b" if (seed + index) % 2 else "buffer a"))
    return steps


@pytest.mark.parametrize("seed", range(40))
def test_macro_first_write_success_matches_eager_oracle(seed: int) -> None:
    eager = _editor_for_differential()
    product = _editor_for_differential()
    steps = _seeded_steps(seed)
    eager.set_macro("seeded", steps)
    product.set_macro("seeded", steps)

    assert _play_macro_eager_oracle(eager, steps, name="seeded") is True
    assert product.play_macro("seeded") is True

    assert _state(product) == _state(eager)
    assert product.undo.depth() == eager.undo.depth()
    assert product.undo.redo_depth() == eager.undo.redo_depth()
    product_retained = _retained_shape(product)
    eager_retained = _retained_shape(eager)
    assert tuple(label for label, _ in product_retained) == tuple(
        label for label, _ in eager_retained
    )
    assert all(
        product_bytes <= eager_bytes
        for (_label, product_bytes), (_other, eager_bytes) in zip(
            product_retained, eager_retained, strict=True
        )
    )

    eager_row = eager.undo.peek_undo()
    product_row = product.undo.peek_undo()
    assert eager_row is not None and product_row is not None
    assert product_row.description == eager_row.description
    assert product._undo_redo_entry_authority(product_row) == eager._undo_redo_entry_authority(
        eager_row
    )

    assert product.undo.undo() is eager.undo.undo() is True
    assert _state(product) == _state(eager)
    assert product.undo.redo() is eager.undo.redo() is True
    assert _state(product) == _state(eager)


@pytest.mark.parametrize("seed", range(20))
def test_macro_first_write_failure_matches_eager_oracle(seed: int) -> None:
    eager = _editor_for_differential()
    product = _editor_for_differential()
    initial = _state(eager)
    steps = [
        *_seeded_steps(seed)[:5],
        _action("rev0987-missing-action"),
    ]
    eager.set_macro("fail", steps)
    product.set_macro("fail", steps)

    assert _play_macro_eager_oracle(eager, steps, name="fail") is False
    assert product.play_macro("fail") is False

    assert _state(eager) == initial
    assert _state(product) == initial
    assert product.undo.depth() == eager.undo.depth() == 1
    assert product.undo.redo_depth() == eager.undo.redo_depth() == 0
    assert product.messages[-1] == eager.messages[-1]


def _large_editor(buffer_count: int = 4, chars: int = 250_000) -> Editor:
    editor = Editor()
    editor.options.set("undobytes", "0")
    for index in range(buffer_count):
        name = f"buffer-{index + 1}"
        editor.new_buffer(name, chr(97 + index) * chars)
        editor.buffers[name].buf.fastdirty = True
        editor.buffers[name].buf.dirty = False
    assert editor.switch_buffer("buffer-1") is True
    return editor


def _forbid_get_text(editor: Editor, names: list[str], monkeypatch: pytest.MonkeyPatch) -> None:
    for name in names:
        def forbidden(*, _name: str = name) -> str:
            raise AssertionError(f"untouched buffer joined: {_name}")

        monkeypatch.setattr(editor.buffers[name].buf, "get_text", forbidden)


def test_successful_macro_never_joins_untouched_open_buffers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    editor = _large_editor()
    _forbid_get_text(editor, ["buffer-2", "buffer-3", "buffer-4"], monkeypatch)
    editor.set_macro("one", [_action("InsertText", text="X")])

    assert editor.play_macro("one") is True
    assert editor.undo.depth() == 1
    assert editor.undo.undo() is True
    assert editor.undo.redo() is True


def test_failed_macro_never_joins_or_rebuilds_untouched_open_buffers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    editor = _large_editor()
    original = editor.buffers["buffer-1"].buf.get_text
    expected = original()
    _forbid_get_text(editor, ["buffer-2", "buffer-3", "buffer-4"], monkeypatch)
    editor.set_macro(
        "fail",
        [
            _action("InsertText", text="X"),
            _action("rev0987-missing-action"),
        ],
    )

    assert editor.play_macro("fail") is False
    assert original() == expected
    assert editor.undo.depth() == 0
    assert editor.undo.redo_depth() == 0


def test_navigation_only_macro_joins_no_buffer_text(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    editor = _large_editor()
    originals = {
        name: eb.buf.get_text
        for name, eb in editor.buffers.items()
    }
    _forbid_get_text(editor, list(editor.buffers), monkeypatch)
    editor.set_macro(
        "navigate",
        [
            _action("CursorRight"),
            _action("CursorRight"),
            _action("CursorLeft"),
        ],
    )

    assert editor.play_macro("navigate") is True
    assert editor.primary_cursor().col == 1
    assert editor.undo.depth() == 0
    assert all(originals[name]() for name in originals)


def test_register_only_macro_joins_no_buffer_text_and_replays_exactly(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    editor = _large_editor()

    def set_mark(current: Editor) -> bool:
        current.mark_set("m")
        return True

    editor.actions.register("Rev0987SetMark", set_mark)
    _forbid_get_text(editor, list(editor.buffers), monkeypatch)
    editor.set_macro("mark", [_action("Rev0987SetMark")])

    assert editor.play_macro("mark") is True
    assert "m" in editor.marks
    assert editor.undo.depth() == 1
    assert editor.undo.undo() is True
    assert "m" not in editor.marks
    assert editor.undo.redo() is True
    assert "m" in editor.marks


def test_macro_tracks_direct_observed_line_mutation_without_late_touch() -> None:
    editor = Editor()
    editor.new_buffer("main", "alpha\nbeta")

    def mutate_lines(current: Editor) -> bool:
        current.cur().buf.lines[:] = ["direct"]
        return True

    editor.actions.register("Rev0987DirectLines", mutate_lines)
    editor.set_macro("direct", [_action("Rev0987DirectLines")])

    assert editor.play_macro("direct") is True
    assert editor.cur().buf.get_text() == "direct"
    assert editor.undo.undo() is True
    assert editor.cur().buf.get_text() == "alpha\nbeta"
    assert editor.undo.redo() is True
    assert editor.cur().buf.get_text() == "direct"


def test_macro_finalization_failure_restores_text_history_and_input(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    editor = Editor()
    editor.new_buffer("main", "seed")
    editor.input["text"] = "before"
    editor.set_macro("write", [_action("InsertText", text="X")])
    before = _state(editor)
    before_depth = editor.undo.depth()
    original = editor._record_buffer_transaction_snapshot

    def record_then_fail(*args: object, **kwargs: object) -> None:
        original(*args, **kwargs)  # type: ignore[arg-type]
        raise RuntimeError("record failed")

    monkeypatch.setattr(editor, "_record_buffer_transaction_snapshot", record_then_fail)

    assert editor.play_macro("write") is False
    assert editor.messages[-1] == (
        "macro: aborted during transaction finalization: record failed"
    )
    assert _state(editor) == before
    assert editor.undo.depth() == before_depth
    assert editor.undo.redo_depth() == 0
    assert editor.input == {"text": "before"}
    assert editor._macro_playing is False
    assert editor._macro_play_name == ""
    assert editor._macro_play_steps == 0


def test_script_started_macro_keeps_caller_authority_after_first_write_refactor() -> None:
    eager = _editor_for_differential()
    product = _editor_for_differential()
    steps = [_action("InsertText", text="s"), _action("InsertText", text="t")]

    with eager.script_context(origin_id="script-a"):
        eager.set_macro("owned", steps)
        assert _play_macro_eager_oracle(eager, steps, name="owned") is True
    with product.script_context(origin_id="script-a"):
        product.set_macro("owned", steps)
        assert product.play_macro("owned") is True

    eager_row = eager.undo.peek_undo()
    product_row = product.undo.peek_undo()
    assert eager_row is not None and product_row is not None
    eager_authority = eager._undo_redo_entry_authority(eager_row)
    product_authority = product._undo_redo_entry_authority(product_row)
    assert product_authority == eager_authority
    assert product_authority.script_context is True
    assert product_authority.script_origin_id == "script-a"



def test_failed_safe_macro_preserves_outer_history_suppression() -> None:
    """Rollback must not consume an enclosing aggregate transaction guard."""

    editor = Editor()
    editor.new_buffer("main", "abc")
    editor.set_macro(
        "fail-safe",
        [
            _action("InsertText", text="X"),
            _action("StartOfLine"),
            _action("Backspace"),
        ],
    )
    assert editor._macro_replay_can_suppress_step_undo(
        editor.macros["fail-safe"]
    ) is True

    with editor.undo.suppress_recording():
        assert editor.undo.snapshot().suppress == 1
        assert editor.play_macro("fail-safe") is False
        assert editor.messages[-1] == (
            "macro: aborted at step 3: action Backspace failed"
        )
        assert editor.cur().buf.get_text() == "abc"
        assert editor.undo.snapshot().suppress == 1

        editor.input["text"] = "Q"
        assert editor.run_action("InsertText") is True
        assert editor.cur().buf.get_text() == "Qabc"
        assert editor.undo.depth() == 0

    assert editor.undo.snapshot().suppress == 0



def test_failed_macro_inside_with_undo_keeps_one_outer_history_row() -> None:
    """A failed nested replay must not re-enable per-step recording."""

    editor = Editor()
    install_editor_hostcalls(editor)
    editor.new_buffer("main", "abc")
    editor.set_macro(
        "fail-safe",
        [
            _action("InsertText", text="X"),
            _action("StartOfLine"),
            _action("Backspace"),
        ],
    )
    editor.options.set("cap.macro-play", "true")

    editor.vm.eval(
        '"outer" [ '
        '"fail-safe" 1 "ed.macro-play" hostcall drop '
        '"Q" "ed.insert" hostcall '
        '] "ed.with-undo" hostcall',
        filename="<test>",
    )

    assert editor.vm.stack == [1]
    assert editor.cur().buf.get_text() == "Qabc"
    assert editor.undo.snapshot().suppress == 0
    assert editor.undo.depth() == 1
    row = editor.undo.peek_undo()
    assert row is not None and row.description == "outer"

    assert editor.undo.undo() is True
    assert editor.cur().buf.get_text() == "abc"
    assert editor.undo.redo() is True
    assert editor.cur().buf.get_text() == "Qabc"

def test_failed_safe_macro_preserves_nested_suppression_depth() -> None:
    editor = Editor()
    editor.new_buffer("main", "abc")
    editor.set_macro(
        "fail-safe",
        [_action("InsertText", text="X"), _action("StartOfLine"), _action("Backspace")],
    )

    with editor.undo.suppress_recording():
        with editor.undo.suppress_recording():
            assert editor.undo.snapshot().suppress == 2
            assert editor.play_macro("fail-safe") is False
            assert editor.undo.snapshot().suppress == 2
        assert editor.undo.snapshot().suppress == 1
    assert editor.undo.snapshot().suppress == 0

def test_macro_first_write_measurement_compares_product_and_eager_capture(
    tmp_path: Path,
) -> None:
    output = tmp_path / "macro-first-write.json"
    env = dict(os.environ)
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(ROOT / "src") + (
        os.pathsep + existing if existing else ""
    )
    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / "tools" / "measure_macro_first_write.py"),
            "--chars",
            "100000",
            "--buffers",
            "4",
            "--samples",
            "1",
            "--output",
            str(output),
        ],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        timeout=60,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["schema"] == "micromax.macro-first-write-witness.v2"

    success_reference = payload["success"]["eager_snapshot_reference"]
    success_product = payload["success"]["first_write_product"]
    failure_reference = payload["failure"]["eager_snapshot_reference"]
    failure_product = payload["failure"]["first_write_product"]
    nav_reference = payload["navigation_only"]["eager_snapshot_reference"]
    nav_product = payload["navigation_only"]["first_write_product"]

    assert success_reference["joined_text_calls"] == 5
    assert success_product["joined_text_calls"] == 0
    assert failure_reference["joined_text_calls"] == 4
    assert failure_product["joined_text_calls"] == 0
    assert nav_reference["joined_text_calls"] == 4
    assert nav_product["joined_text_calls"] == 0
    assert (
        0
        < success_product["accounted_retained_text_bytes"]
        < success_reference["accounted_retained_text_bytes"]
    )
    assert success_reference["capture_representation"] == "joined-text"
    assert success_product["capture_representation"] == "line-vector"
    for row in (
        success_reference,
        success_product,
        failure_reference,
        failure_product,
        nav_reference,
        nav_product,
    ):
        assert row["return_value_exact"] is True
        assert row["forward_or_rollback_exact"] is True
        assert row["undo_exact"] is True
        assert row["redo_exact"] is True
