from __future__ import annotations

from types import SimpleNamespace

import vhk.system.dialogs as dialogs



def test_prompt_form_prefers_yad_native_form(monkeypatch):
    calls: list[list[str]] = []

    def fake_which(name: str):
        return f"/usr/bin/{name}" if name == "yad" else None

    def fake_run(cmd, capture_output=True, text=True):
        calls.append(list(cmd))
        return SimpleNamespace(returncode=0, stdout="Ada\x1fTRUE\x1fprod\x1f12\n", stderr="")

    monkeypatch.setattr(dialogs.shutil, "which", fake_which)
    monkeypatch.setattr(dialogs.subprocess, "run", fake_run)

    res = dialogs.prompt_form(
        [
            dialogs.FormField(name="name", label="Name", kind="text", default="Grace"),
            dialogs.FormField(name="ok", label="Continue", kind="bool", default=True),
            dialogs.FormField(name="env", label="Environment", kind="choice", default="prod", choices=["dev", "prod"]),
            dialogs.FormField(name="count", label="Count", kind="number", default=12),
        ],
        title="Deploy",
        text="Collect inputs",
    )

    assert res == {"name": "Ada", "ok": True, "env": "prod", "count": 12}
    assert calls and calls[0][0:4] == ["/usr/bin/yad", "--form", "--separator", "\x1f"]
    assert "--title" in calls[0] and "Deploy" in calls[0]
    assert "--text" in calls[0] and "Collect inputs" in calls[0]
    assert "--field=Name" in calls[0]
    assert "--field=Continue:CHK" in calls[0]
    assert "--field=Environment:CB" in calls[0]
    assert "--field=Count:NUM" in calls[0]
    assert calls[0][-4:] == ["Grace", "TRUE", "prod!dev", "12"]



def test_prompt_form_falls_back_to_sequential_prompts(monkeypatch):
    monkeypatch.setattr(dialogs.shutil, "which", lambda name: None)
    shown: list[tuple] = []
    asked: list[tuple] = []
    chosen: list[tuple] = []
    typed: list[tuple] = []
    monkeypatch.setattr(dialogs, "show_message", lambda text, **kw: shown.append((text, kw)))
    monkeypatch.setattr(dialogs, "ask_yes_no", lambda text, **kw: asked.append((text, kw)) or True)
    monkeypatch.setattr(dialogs, "choose_from_list", lambda items, **kw: chosen.append((list(items), kw)) or "prod")
    monkeypatch.setattr(dialogs, "input_text", lambda prompt, **kw: typed.append((prompt, kw)) or ("42" if prompt == "Count" else "Ada"))

    res = dialogs.prompt_form(
        [
            dialogs.FormField(name="name", label="Name", kind="text", default="Grace"),
            dialogs.FormField(name="count", label="Count", kind="number", default=7),
            dialogs.FormField(name="ok", label="Continue", kind="bool", default=False),
            dialogs.FormField(name="env", label="Environment", kind="choice", choices=["dev", "prod"]),
        ],
        title="Deploy",
        text="Collect inputs",
    )

    assert shown == [("Collect inputs", {"title": "Deploy", "level": "info"})]
    assert typed == [
        ("Name", {"title": "Deploy", "default": "Grace", "password": False}),
        ("Count", {"title": "Deploy", "default": "7", "password": False}),
    ]
    assert asked == [("Continue", {"title": "Deploy", "default_yes": False})]
    assert chosen == [(["dev", "prod"], {"title": "Deploy", "text": "Environment", "multiple": False})]
    assert res == {"name": "Ada", "count": 42, "ok": True, "env": "prod"}


def test_choose_from_list_prefers_rofi_on_x11(monkeypatch):
    calls: list[tuple[list[str], str]] = []

    def fake_which(name: str):
        return f"/usr/bin/{name}" if name in {"rofi", "zenity"} else None

    def fake_run(cmd, input=None, capture_output=True, text=True):
        calls.append((list(cmd), input))
        return SimpleNamespace(returncode=0, stdout="beta\n", stderr="")

    monkeypatch.setenv("DISPLAY", ":0")
    monkeypatch.setenv("XDG_SESSION_TYPE", "x11")
    monkeypatch.delenv("WAYLAND_DISPLAY", raising=False)
    monkeypatch.setattr(dialogs.shutil, "which", fake_which)
    monkeypatch.setattr(dialogs.subprocess, "run", fake_run)

    res = dialogs.choose_from_list(["alpha", "beta", "gamma"], text="Pick window")

    assert res == "beta"
    assert calls == [([
        "/usr/bin/rofi",
        "-dmenu",
        "-p",
        "Pick window",
    ], "alpha\nbeta\ngamma\n")]


def test_choose_from_list_prefers_fuzzel_on_wayland(monkeypatch):
    calls: list[tuple[list[str], str]] = []

    def fake_which(name: str):
        return f"/usr/bin/{name}" if name in {"fuzzel", "zenity"} else None

    def fake_run(cmd, input=None, capture_output=True, text=True):
        calls.append((list(cmd), input))
        return SimpleNamespace(returncode=0, stdout="staging\n", stderr="")

    monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")
    monkeypatch.setenv("WAYLAND_DISPLAY", "wayland-1")
    monkeypatch.delenv("DISPLAY", raising=False)
    monkeypatch.setattr(dialogs.shutil, "which", fake_which)
    monkeypatch.setattr(dialogs.subprocess, "run", fake_run)

    res = dialogs.choose_from_list(["dev", "staging", "prod"], title="Deploy", text="Environment")

    assert res == "staging"
    assert calls == [([
        "/usr/bin/fuzzel",
        "--dmenu",
        "--prompt",
        "Environment",
    ], "dev\nstaging\nprod\n")]


def test_choose_from_list_override_can_force_tofi(monkeypatch):
    calls: list[tuple[list[str], str]] = []

    def fake_which(name: str):
        return f"/usr/bin/{name}" if name in {"tofi", "dialog"} else None

    def fake_run(cmd, input=None, capture_output=True, text=True):
        calls.append((list(cmd), input))
        return SimpleNamespace(returncode=0, stdout="prod\n", stderr="")

    monkeypatch.setenv("VHK_CHOOSER_BACKEND", "tofi")
    monkeypatch.setenv("XDG_SESSION_TYPE", "x11")
    monkeypatch.setenv("DISPLAY", ":0")
    monkeypatch.setattr(dialogs.shutil, "which", fake_which)
    monkeypatch.setattr(dialogs.subprocess, "run", fake_run)

    res = dialogs.choose_from_list(["dev", "prod"], text="Environment")

    assert res == "prod"
    assert calls == [([
        "/usr/bin/tofi",
        "--prompt-text=Environment",
    ], "dev\nprod\n")]
