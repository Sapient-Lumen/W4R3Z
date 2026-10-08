from __future__ import annotations

import io
from typing import Any

import pytest


def test_wait_for_clipboard_change_wayland_prefers_wl_paste_watch(monkeypatch: pytest.MonkeyPatch):
    import vhk.system.watch as watch_mod

    monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")
    monkeypatch.setenv("WAYLAND_DISPLAY", "wayland-1")

    calls: list[list[str]] = []

    def fake_which(cmd: str) -> str | None:
        if cmd == "wl-paste":
            return "/fake/wl-paste"
        return None

    class FakeProc:
        def __init__(self, cmd: list[str], **kwargs: Any):
            calls.append(cmd)
            self.stdout = io.StringIO("__VHK_CLIP_EVENT__\n")

        def terminate(self):
            return None

        def wait(self, timeout: float | None = None):
            return 0

        def kill(self):
            return None

        def communicate(self, timeout: float | None = None):
            return ("", "")

    monkeypatch.setattr(watch_mod, "_which", fake_which)
    monkeypatch.setattr(watch_mod.subprocess, "Popen", lambda cmd, **kw: FakeProc(cmd, **kw))
    monkeypatch.setattr(watch_mod.select, "select", lambda r, w, x, timeout=None: (r, [], []))

    reads = ["one", "one", "two"]

    def read_func(selection: str = "clipboard") -> str:
        return reads.pop(0) if reads else "two"

    out = watch_mod.wait_for_clipboard_change(
        read_func,
        selection="clipboard",
        initial_text="one",
        timeout_ms=200,
        poll_ms=0,
        max_attempts=6,
        jitter_ms=0,
    )
    assert out == "two"
    assert calls
    assert "--watch" in calls[0]


def test_wait_for_clipboard_event_wayland_can_return_unchanged(monkeypatch: pytest.MonkeyPatch):
    import vhk.system.watch as watch_mod

    monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")
    monkeypatch.setenv("WAYLAND_DISPLAY", "wayland-1")

    calls: list[list[str]] = []

    def fake_which(cmd: str) -> str | None:
        if cmd == "wl-paste":
            return "/fake/wl-paste"
        return None

    class FakeProc:
        def __init__(self, cmd: list[str], **kwargs: Any):
            calls.append(cmd)
            self.stdout = io.StringIO("__VHK_CLIP_EVENT__\n")

        def terminate(self):
            return None

        def wait(self, timeout: float | None = None):
            return 0

        def kill(self):
            return None

        def communicate(self, timeout: float | None = None):
            return ("", "")

    monkeypatch.setattr(watch_mod, "_which", fake_which)
    monkeypatch.setattr(watch_mod.subprocess, "Popen", lambda cmd, **kw: FakeProc(cmd, **kw))
    monkeypatch.setattr(watch_mod.select, "select", lambda r, w, x, timeout=None: (r, [], []))

    def read_func(selection: str = "clipboard") -> str:
        return "same"

    txt, changed = watch_mod.wait_for_clipboard_event(
        read_func,
        selection="primary",
        initial_text="same",
        timeout_ms=200,
        poll_ms=0,
        max_attempts=6,
        jitter_ms=0,
    )
    assert txt == "same"
    assert changed is False
    assert calls
    assert "--watch" in calls[0]
    assert "--primary" in calls[0]