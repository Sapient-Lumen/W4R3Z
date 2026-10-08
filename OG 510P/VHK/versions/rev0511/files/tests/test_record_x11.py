from __future__ import annotations

from vhk.system.record_x11 import (
    events_to_steps,
    load_xmodmap_keysyms,
    parse_xinput_test_xi2_timed,
    resolve_recording_smoothing,
)


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


def test_motion_thinning_keeps_final_position() -> None:
    timed_lines = [
        (1000.0, "EVENT type 6 (Motion)\n"),
        (1000.1, "    root: 10.00/10.00\n"),
        (1000.2, "\n"),
        (1005.0, "EVENT type 6 (Motion)\n"),
        (1005.1, "    root: 11.00/10.00\n"),
        (1005.2, "\n"),
        (1008.0, "EVENT type 2 (KeyPress)\n"),
        (1008.1, "    detail: 38\n"),
        (1008.2, "    root: 11.00/10.00\n"),
        (1008.3, "\n"),
    ]
    events = parse_xinput_test_xi2_timed(timed_lines)
    keysyms = load_xmodmap_keysyms(xmodmap_text="keycode  38 = a A\n")

    steps = events_to_steps(
        events,
        keysyms=keysyms,
        min_delay_ms=0,
        mouse_sample_ms=25,
        mouse_min_delta=4,
    )

    mouse_moves = [s for s in steps if s.get("type") == "MouseMove"]
    assert mouse_moves == [{"type": "MouseMove", "x": 10, "y": 10}, {"type": "MouseMove", "x": 11, "y": 10}]
    assert steps[-1] == {"type": "KeyDown", "key": "a"}


def test_drag_collapse_survives_intermediate_motion() -> None:
    timed_lines = [
        (1000.0, "EVENT type 4 (ButtonPress)\n"),
        (1000.1, "    detail: 1\n"),
        (1000.2, "    root: 10.00/10.00\n"),
        (1000.3, "\n"),
        (1035.0, "EVENT type 6 (Motion)\n"),
        (1035.1, "    root: 30.00/45.00\n"),
        (1035.2, "\n"),
        (1065.0, "EVENT type 5 (ButtonRelease)\n"),
        (1065.1, "    detail: 1\n"),
        (1065.2, "    root: 30.00/45.00\n"),
        (1065.3, "\n"),
    ]
    events = parse_xinput_test_xi2_timed(timed_lines)

    steps = events_to_steps(
        events,
        keysyms={},
        min_delay_ms=0,
        mouse_sample_ms=10,
        mouse_min_delta=1,
        drag_min_dist=3,
    )

    drags = [s for s in steps if s.get("type") == "MouseDrag"]
    assert drags == [{"type": "MouseDrag", "x1": 10, "y1": 10, "x2": 30, "y2": 45, "button": 1}]
    assert not any(s.get("type") == "MouseClick" and s.get("down") for s in steps)
    assert not any(s.get("type") == "MouseClick" and s.get("up") for s in steps)


def test_resolve_recording_smoothing_presets_and_overrides() -> None:
    assert resolve_recording_smoothing("normal") == (25, 4)
    assert resolve_recording_smoothing("compact") == (50, 10)
    assert resolve_recording_smoothing("compact", mouse_min_delta=3) == (50, 3)
