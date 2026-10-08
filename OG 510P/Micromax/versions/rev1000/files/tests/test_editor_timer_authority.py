from __future__ import annotations

import pytest

from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls


def _pop_int(ed: Editor) -> int:
    return ed.vm.pop_int()




def test_ed_after_enforces_pending_timer_budget() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.max_pending_timers = 2

    ed.vm.eval('1000 [ ] "ed.after" hostcall', filename="<timer-budget>")
    first = _pop_int(ed)
    ed.vm.eval('1000 [ ] "ed.after" hostcall', filename="<timer-budget>")
    second = _pop_int(ed)
    assert first != second
    assert ed.timers.pending_count() == 2

    with pytest.raises(Exception, match="ed.after: pending timer budget exceeded"):
        ed.vm.eval('1000 [ ] "ed.after" hostcall', filename="<timer-budget>")
    assert ed.timers.pending_count() == 2

    assert ed.cancel_timer_checked(first) is True
    ed.vm.eval('1000 [ ] "ed.after" hostcall', filename="<timer-budget>")
    third = _pop_int(ed)
    assert third not in {first, second}
    assert ed.timers.pending_count() == 2

def test_script_pump_timers_does_not_fire_trusted_due_timer() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.vm.eval(
        """
        variable ran
        0 ran !
        : bump ( -- ) ran @ 1 + ran ! ;
        0 [ bump ] "ed.after" hostcall drop
        """,
        filename="<trusted-timer>",
    )
    assert ed.timers.pending_count() == 1

    with ed.script_context():
        ed.vm.eval('"ed.pump-timers" hostcall', filename="<script>")
        assert _pop_int(ed) == 0

    assert ed.timers.pending_count() == 1
    ed.vm.eval("ran @")
    assert _pop_int(ed) == 0

    assert ed.pump_timers() == 1
    ed.vm.eval("ran @")
    assert _pop_int(ed) == 1
    assert ed.timers.pending_count() == 0


def test_script_pump_timers_can_fire_same_origin_due_timer() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.vm.eval("variable ran 0 ran ! : bump ( -- ) ran @ 1 + ran ! ;")

    with ed.script_context():
        ed.vm.eval('0 [ bump ] "ed.after" hostcall drop', filename="<script>")
        assert ed.timers.pending_count() == 1
        ed.vm.eval('"ed.pump-timers" hostcall', filename="<script>")
        assert _pop_int(ed) == 1

    ed.vm.eval("ran @")
    assert _pop_int(ed) == 1
    assert ed.timers.pending_count() == 0


def test_cap_timer_fire_allows_script_to_pump_protected_timer_under_script_authority() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line("set cap.timer-fire true") is True
    ed.vm.eval(
        '0 [ set cap.fs-save true ] "ed.after" hostcall drop',
        filename="<trusted-timer>",
    )
    assert ed.timers.pending_count() == 1

    with ed.script_context():
        ed.vm.eval('"ed.pump-timers" hostcall', filename="<script>")
        assert _pop_int(ed) == 1

    assert ed.timers.pending_count() == 0
    assert bool(ed.options.get("cap.fs-save")) is False
    assert any("script context cannot modify capability option: cap.fs-save" in msg for msg in ed.messages)


def test_capability_registry_reports_timer_fire() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.vm.eval('"ed.timer-fire" host.feature?')
    assert _pop_int(ed) == 0

    assert ed.exec_command_line("set cap.timer-fire true") is True
    ed.vm.eval('"ed.timer-fire" host.feature?')
    assert _pop_int(ed) == 1


def test_script_pump_timers_does_not_trigger_autosave_maintenance(tmp_path) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    path = tmp_path / "trusted.txt"
    path.write_text("old", encoding="utf-8")
    ed.open_file(str(path))
    eb = ed.cur()
    eb.buf.set_text("new")
    eb.autosave_dirty_since = 0.0
    ed.options.set("autosave", "1", local=eb.local_options)
    ed._now_fn = lambda: 2.0

    with ed.script_context():
        ed.vm.eval('"ed.pump-timers" hostcall', filename="<script>")
        assert _pop_int(ed) == 0

    assert path.read_text(encoding="utf-8") == "old"
    assert eb.buf.dirty is True

    assert ed.pump_timers() == 0
    assert path.read_text(encoding="utf-8") == "new"
    assert eb.buf.dirty is False


def test_cancel_timer_releases_callback_payload_and_task_row() -> None:
    import gc
    import weakref

    class Payload:
        pass

    ed = Editor()
    install_editor_hostcalls(ed)
    payload = Payload()
    ref = weakref.ref(payload)
    tid = ed.timers.schedule(now=0.0, delay_ms=60_000, xt=payload, group="plugin:leaky")
    del payload

    assert ref() is not None
    assert ed.timers.cancel(tid) is True
    assert ed.timers.get(tid) is None
    assert ed.timers.retained_task_count() == 0
    gc.collect()
    assert ref() is None


def test_repeated_schedule_cancel_keeps_stale_heap_entries_bounded() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    for i in range(200):
        tid = ed.timers.schedule(now=float(i), delay_ms=60_000, xt=[i], group="script:loop")
        assert ed.timers.cancel(tid) is True

    assert ed.timers.pending_count() == 0
    assert ed.timers.retained_task_count() == 0
    assert ed.timers.heap_entry_count() <= 64
