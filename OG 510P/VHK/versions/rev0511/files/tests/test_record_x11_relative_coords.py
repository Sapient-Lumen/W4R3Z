from __future__ import annotations

from vhk.system.record_x11 import relativize_pointer_steps


def test_relativize_pointer_steps_window_mode() -> None:
    steps = [
        {"type": "MouseMove", "x": 110, "y": 220},
        {"type": "MouseDrag", "x1": 110, "y1": 220, "x2": 135, "y2": 255, "button": 1},
        {"type": "MouseClickAt", "x": 125, "y": 240, "button": 1},
        {"type": "Log", "message": "keep"},
    ]

    out = relativize_pointer_steps(
        steps,
        rect={"x": 100, "y": 200, "w": 300, "h": 300},
        client={"x": 102, "y": 205, "w": 296, "h": 290},
        mode="window",
    )

    assert out == [
        {"type": "MouseMove", "x": 10, "y": 20},
        {"type": "MouseDrag", "x1": 10, "y1": 20, "x2": 35, "y2": 55, "button": 1},
        {"type": "MouseClickAt", "x": 25, "y": 40, "button": 1},
        {"type": "Log", "message": "keep"},
    ]


def test_relativize_pointer_steps_client_mode_falls_back_to_rect() -> None:
    steps = [{"type": "MouseClickAt", "x": 110, "y": 220, "button": 1}]

    out = relativize_pointer_steps(
        steps,
        rect={"x": 100, "y": 200, "w": 300, "h": 300},
        client=None,
        mode="client",
    )

    assert out == [{"type": "MouseClickAt", "x": 10, "y": 20, "button": 1}]
