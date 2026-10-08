from __future__ import annotations

from vhk.system.record_x11 import events_to_steps, load_xmodmap_keysyms, parse_xinput_test_xi2_timed


def test_parse_xinput_test_xi2_and_convert_steps() -> None:
    # Minimal-ish sample inspired by common `xinput test-xi2 --root` output.
    timed_lines = [
        (1000.0, "EVENT type 2 (KeyPress)\n"),
        (1000.1, "    detail: 38\n"),
        (1000.2, "    root: 10.00/20.00\n"),
        (1000.3, "\n"),
        (1020.0, "EVENT type 3 (KeyRelease)\n"),
        (1020.1, "    detail: 38\n"),
        (1020.2, "    root: 10.00/20.00\n"),
        (1020.3, "\n"),
        (2000.0, "EVENT type 4 (ButtonPress)\n"),
        (2000.1, "    detail: 4\n"),
        (2000.2, "    root: 10.00/20.00\n"),
        (2000.3, "\n"),
        (2005.0, "EVENT type 5 (ButtonRelease)\n"),
        (2005.1, "    detail: 4\n"),
        (2005.2, "    root: 10.00/20.00\n"),
        (2005.3, "\n"),
    ]

    events = parse_xinput_test_xi2_timed(timed_lines)
    assert [e.name for e in events] == ["KeyPress", "KeyRelease", "ButtonPress", "ButtonRelease"]

    keysyms = load_xmodmap_keysyms(xmodmap_text="keycode  38 = a A\n")
    steps = events_to_steps(events, keysyms=keysyms, min_delay_ms=40)

    # Key events become KeyDown/KeyUp with normalized key name.
    assert {s.get("type") for s in steps} >= {"KeyDown", "KeyUp"}
    assert any(s.get("type") == "KeyDown" and s.get("key") == "a" for s in steps)
    assert any(s.get("type") == "KeyUp" and s.get("key") == "a" for s in steps)

    # Wheel press becomes MouseWheel; wheel release is ignored.
    wheel_steps = [s for s in steps if s.get("type") == "MouseWheel"]
    assert len(wheel_steps) == 1
    assert wheel_steps[0]["axis"] == "vertical"
    assert wheel_steps[0]["clicks"] == 1
    assert not any(s.get("type") == "MouseClick" and s.get("button") == 4 for s in steps)

    # A delay should be inserted between the key events and the wheel.
    assert any(s.get("type") == "Delay" and int(s.get("ms")) >= 900 for s in steps)
