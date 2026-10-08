from __future__ import annotations

from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls


def test_ed_highlight_spans_for_micromax_lines() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.new_buffer(
        "x",
        ": foo 1 ;\n\"hi\" \\ comment\n( a ) : bar 2 ;\n",
        path="x.mx",
    )

    ed.vm.eval('0 3 "ed.highlight" hostcall')
    spans = ed.vm.pop_list()

    assert spans[0] == [[0, 1, "kw"], [2, 5, "def"], [6, 7, "num"], [8, 9, "kw"]]
    # string + line comment
    assert spans[1][0] == [0, 4, "str"]
    assert spans[1][1][2] == "comment"
    # paren comment + def + num
    assert spans[2][0][2] == "comment"
    assert any(s[2] == "def" and s[0] == 8 for s in spans[2])
    assert any(s[2] == "num" and s[0] == 12 for s in spans[2])


def test_ed_after_and_pump_timers_are_deterministic() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    now = [0.0]
    ed._now_fn = lambda: float(now[0])

    ed.vm.eval(
        """
        variable ran
        0 ran !
        : bump ( -- ) ran @ 1 + ran ! ;

        100 [ bump ] "ed.after" hostcall drop
        "ed.pump-timers" hostcall  ( -- ran-count )
        """
    )
    ran0 = ed.vm.pop_int()
    assert ran0 == 0

    now[0] = 0.11
    ed.vm.eval('"ed.pump-timers" hostcall')
    ran1 = ed.vm.pop_int()
    assert ran1 == 1

    ed.vm.eval('ran @')
    assert ed.vm.pop_int() == 1


def test_ed_cancel_timer_prevents_execution() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    now = [0.0]
    ed._now_fn = lambda: float(now[0])

    ed.vm.eval(
        """
        variable ran
        0 ran !
        variable tid

        : bump ( -- ) ran @ 1 + ran ! ;

        50 [ bump ] "ed.after" hostcall tid !
        tid @ "ed.cancel-timer" hostcall drop
        """
    )

    now[0] = 0.10
    ed.vm.eval('"ed.pump-timers" hostcall drop')

    ed.vm.eval('ran @')
    assert ed.vm.pop_int() == 0
